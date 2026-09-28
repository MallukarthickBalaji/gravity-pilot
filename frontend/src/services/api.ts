/**
 * api.ts — Centralized API service layer for DesktopPilot AI frontend.
 */
import { HealthStatus, OllamaInfo, SessionItem, ChatMessage } from "../types";

export async function fetchHealth(): Promise<{ backendOnline: boolean; groqAvailable: boolean }> {
  try {
    const res = await fetch("/health");
    if (res.ok) {
      const data: HealthStatus = await res.json();
      return {
        backendOnline: data.backend === true,
        groqAvailable: data.groq_available === true,
      };
    }
  } catch (err) {
    console.warn("fetchHealth error:", err);
  }
  return { backendOnline: false, groqAvailable: false };
}

export async function fetchOllamaHealth(): Promise<OllamaInfo> {
  try {
    const res = await fetch("/api/ollama/health");
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn("fetchOllamaHealth error:", err);
  }
  return {
    available: false,
    error: "Could not connect to Ollama on http://127.0.0.1:11434",
  };
}

export async function fetchSessions(): Promise<SessionItem[]> {
  try {
    const res = await fetch("/sessions");
    if (res.ok) {
      const data = await res.json();
      return data.sessions || [];
    }
  } catch (err) {
    console.error("fetchSessions error:", err);
  }
  return [];
}

export async function createSession(title?: string): Promise<string | null> {
  try {
    const res = await fetch("/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: title || "New Chat" }),
    });
    if (res.ok) {
      const data = await res.json();
      return data.id || null;
    }
  } catch (err) {
    console.error("createSession error:", err);
  }
  return null;
}

export async function deleteSessionApi(sessionId: string): Promise<boolean> {
  try {
    const res = await fetch(`/session/${sessionId}`, { method: "DELETE" });
    return res.ok;
  } catch (err) {
    console.error("deleteSessionApi error:", err);
    return false;
  }
}

export async function fetchSessionHistory(sessionId: string): Promise<ChatMessage[]> {
  try {
    const res = await fetch(`/session/${sessionId}/history`);
    if (res.ok) {
      const data = await res.json();
      return (data.messages || []).map((m: any, idx: number) => ({
        id: m.id || `${sessionId}-${idx}`,
        sessionId,
        taskId: m.task_id,
        role: m.role as "user" | "assistant" | "agent",
        agentName: m.agent_name || (m.role === "user" ? undefined : "GravityPilot"),
        agentColor: m.agent_color || (m.role === "user" ? undefined : "#2E7D6B"),
        kind: m.kind || "normal",
        text: m.content || "",
        createdAt: m.timestamp,
        generatedFiles: (m.generated_files || []).map((gf: any) => ({
          fileName: gf.filename || gf.fileName || "file",
          filePath: gf.path || gf.filePath || "",
          fileType: gf.doc_type || gf.fileType || "document",
          taskId: gf.taskId,
          sessionId: gf.sessionId,
          status: gf.status,
        })),
      }));
    }
  } catch (err) {
    console.error("fetchSessionHistory error:", err);
  }
  return [];
}
