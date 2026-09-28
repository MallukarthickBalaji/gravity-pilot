/**
 * Chat routes — DesktopPilot AI
 *
 * REST:  GET /chat/status
 *        GET /chat/sessions
 *        POST /chat/sessions
 *        GET /chat/sessions/:sessionId
 *        GET /chat/sessions/:sessionId/messages
 *
 * SSE:   POST /chat/sessions/:sessionId/stream
 *          body: { message: string }
 *          streams newline-delimited JSON from the Python subprocess as SSE
 */

import { Router, type IRouter } from "express";
import { spawn } from "child_process";
import * as path from "path";
import { desc, eq } from "drizzle-orm";
import { v4 as uuidv4 } from "uuid";
import { db, chatSessionsTable, chatMessagesTable } from "@workspace/db";
import {
  GetChatStatusResponse,
  ListChatSessionsResponse,
  CreateChatSessionBody,
  CreateChatSessionResponse,
  GetChatSessionParams,
  GetChatSessionResponse,
  GetSessionMessagesParams,
  GetSessionMessagesResponse,
} from "@workspace/api-zod";
import { logger } from "../lib/logger";

const router: IRouter = Router();

// ── Paths ─────────────────────────────────────────────────────────────────────

// import.meta.dirname resolves to artifacts/api-server/dist/ in the esbuild bundle.
// 3 levels up: dist/ → api-server/ → artifacts/ → workspace root
const WORKSPACE_ROOT = path.resolve(import.meta.dirname, "..", "..", "..");
const PYTHON_BIN     = process.env.PYTHON_BIN || "python";
const RUN_TASK_PY    = path.join(WORKSPACE_ROOT, "desktop_pilot", "run_task.py");

// ── Capability probe ──────────────────────────────────────────────────────────

interface DetectedStatus {
  mode: "groq" | "ollama" | "none";
  browserAutomation: boolean;
  desktopAutomation: boolean;
  documentGeneration: boolean;
}

let cachedStatus: DetectedStatus | null = null;
let cacheExpiry = 0;

async function probeBackend(): Promise<DetectedStatus> {
  const now = Date.now();
  if (cachedStatus && now < cacheExpiry) return cachedStatus;

  // Try Groq key first
  const groqKey = process.env["GROQ_API_KEY"] || process.env["Groq_API_KEY"] || "";
  let mode: DetectedStatus["mode"] = "none";

  if (groqKey && groqKey.trim().length > 0) {
    try {
      const res = await fetch("https://api.groq.com/openai/v1/models", {
        method: "GET",
        headers: { Authorization: `Bearer ${groqKey.trim()}` },
        signal: AbortSignal.timeout(3000),
      });
      if (res.ok) mode = "groq";
    } catch {
      // fall through
    }
  }

  if (mode === "none") {
    // Try Ollama
    const host = process.env["OLLAMA_HOST"] || "http://localhost:11434";
    try {
      const res = await fetch(`${host}/api/tags`, { signal: AbortSignal.timeout(2000) });
      if (res.ok) mode = "ollama";
    } catch {
      // no backend
    }
  }

  cachedStatus = {
    mode,
    browserAutomation: mode === "groq",
    desktopAutomation:  mode !== "none",
    documentGeneration: mode !== "none",
  };
  cacheExpiry = now + 30_000; // cache 30s
  return cachedStatus;
}

// ── GET /chat/status ──────────────────────────────────────────────────────────

router.get("/chat/status", async (_req, res): Promise<void> => {
  const status = await probeBackend();
  res.json(GetChatStatusResponse.parse(status));
});

// ── GET /chat/sessions ────────────────────────────────────────────────────────

router.get("/chat/sessions", async (_req, res): Promise<void> => {
  const sessions = await db
    .select()
    .from(chatSessionsTable)
    .orderBy(desc(chatSessionsTable.createdAt))
    .limit(50);
  res.json(ListChatSessionsResponse.parse(sessions));
});

// ── POST /chat/sessions ───────────────────────────────────────────────────────

router.post("/chat/sessions", async (req, res): Promise<void> => {
  const parsed = CreateChatSessionBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  const [session] = await db
    .insert(chatSessionsTable)
    .values({ id: uuidv4(), mode: parsed.data.mode })
    .returning();
  res.status(201).json(CreateChatSessionResponse.parse(session));
});

// ── GET /chat/sessions/:sessionId ─────────────────────────────────────────────

router.get("/chat/sessions/:sessionId", async (req, res): Promise<void> => {
  const params = GetChatSessionParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const [session] = await db
    .select()
    .from(chatSessionsTable)
    .where(eq(chatSessionsTable.id, params.data.sessionId));
  if (!session) {
    res.status(404).json({ error: "Session not found" });
    return;
  }
  res.json(GetChatSessionResponse.parse(session));
});

// ── DELETE /chat/sessions/:sessionId ──────────────────────────────────────────

router.delete("/chat/sessions/:sessionId", async (req, res): Promise<void> => {
  const sessionId = req.params["sessionId"];
  if (!sessionId) {
    res.status(400).json({ error: "sessionId required" });
    return;
  }
  
  // Delete messages first (foreign key cascades aren't implicitly handled here if not configured)
  await db.delete(chatMessagesTable).where(eq(chatMessagesTable.sessionId, sessionId));
  
  const deleted = await db.delete(chatSessionsTable).where(eq(chatSessionsTable.id, sessionId)).returning();
  
  if (deleted.length === 0) {
    res.status(404).json({ error: "Session not found" });
    return;
  }
  
  res.status(204).end();
});

// ── GET /chat/sessions/:sessionId/messages ────────────────────────────────────

router.get("/chat/sessions/:sessionId/messages", async (req, res): Promise<void> => {
  const params = GetSessionMessagesParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const messages = await db
    .select()
    .from(chatMessagesTable)
    .where(eq(chatMessagesTable.sessionId, params.data.sessionId))
    .orderBy(chatMessagesTable.createdAt);
  res.json(GetSessionMessagesResponse.parse(messages));
});

// ── POST /chat/sessions/:sessionId/stream (SSE) ───────────────────────────────
//
// Not in OpenAPI (SSE not representable cleanly). The frontend calls this with
// fetch() + ReadableStream and parses newline-delimited JSON lines from the
// response body.

router.post("/chat/sessions/:sessionId/stream", async (req, res): Promise<void> => {
  const sessionIdRaw = Array.isArray(req.params["sessionId"])
    ? req.params["sessionId"][0]
    : req.params["sessionId"];
  const sessionId = sessionIdRaw ?? "";

  const { message } = req.body as { message?: string };
  if (!message || typeof message !== "string") {
    res.status(400).json({ error: "message is required" });
    return;
  }

  // Verify session exists
  const [session] = await db
    .select()
    .from(chatSessionsTable)
    .where(eq(chatSessionsTable.id, sessionId));
  if (!session) {
    res.status(404).json({ error: "Session not found" });
    return;
  }

  // Persist user message
  await db.insert(chatMessagesTable).values({
    id:        uuidv4(),
    sessionId,
    role:      "user",
    agentName: null,
    agentColor:null,
    kind:      null,
    text:      message,
    items:     null,
  });

  // Set up SSE headers
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control",  "no-cache");
  res.setHeader("Connection",     "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");
  res.flushHeaders();

  const sendEvent = (data: object) => {
    res.write(`data: ${JSON.stringify(data)}\n\n`);
  };

  // Spawn Python subprocess
  const proc = spawn(PYTHON_BIN, [
    RUN_TASK_PY,
    "--input",      message,
    "--session-id", sessionId,
  ], {
    env: { ...process.env, PYTHONUNBUFFERED: "1" },
    cwd: path.join(WORKSPACE_ROOT, "desktop_pilot"),
  });

  let buffer = "";
  const pendingMessages: Array<{
    agentName: string | null;
    agentColor: string | null;
    kind: string | null;
    text: string;
    items: string[] | null;
  }> = [];

  proc.stdout.on("data", (chunk: Buffer) => {
    buffer += chunk.toString("utf8");
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      try {
        const event = JSON.parse(trimmed) as Record<string, unknown>;
        sendEvent(event);

        // Collect agent messages to persist later
        if (event["type"] === "message") {
          pendingMessages.push({
            agentName:  (event["agentName"]  as string | null) ?? null,
            agentColor: (event["agentColor"] as string | null) ?? null,
            kind:       (event["kind"]       as string | null) ?? null,
            text:       (event["text"]       as string)       ?? "",
            items:      (event["items"]      as string[] | null) ?? null,
          });
        }
      } catch {
        logger.warn({ line }, "non-JSON line from Python subprocess");
      }
    }
  });

  proc.stderr.on("data", (chunk: Buffer) => {
    logger.debug({ stderr: chunk.toString("utf8") }, "python subprocess stderr");
  });

  proc.on("error", (err) => {
    logger.error({ err }, "failed to spawn python subprocess");
    sendEvent({ type: "error", message: `Failed to start AI backend: ${err.message}` });
    res.end();
  });

  proc.on("close", async (code) => {
    // Flush remaining buffer
    if (buffer.trim()) {
      try {
        const event = JSON.parse(buffer.trim()) as Record<string, unknown>;
        sendEvent(event);
      } catch { /* ignore */ }
    }

    // Persist all collected agent messages
    try {
      for (const m of pendingMessages) {
        await db.insert(chatMessagesTable).values({
          id:        uuidv4(),
          sessionId,
          role:      "agent",
          agentName:  m.agentName,
          agentColor: m.agentColor,
          kind:       m.kind,
          text:       m.text,
          items:      m.items ?? undefined,
        });
      }
      // Update session title from first user message
      await db
        .update(chatSessionsTable)
        .set({ title: message.slice(0, 80) })
        .where(eq(chatSessionsTable.id, sessionId));
    } catch (err) {
      logger.error({ err }, "failed to persist messages");
    }

    if (code !== 0) {
      sendEvent({ type: "error", message: `Process exited with code ${code}` });
    }
    res.end();
  });

  // Clean up on client disconnect
  req.on("close", () => { proc.kill(); });
});

export default router;
