import { useState, useCallback } from "react";
import { ChatMessage } from "@workspace/api-client-react";
import { C } from "../theme";

export type AgentId = "supervisor"|"requirement_analyzer"|"planning_agent"|"document_agent"|"browser_agent"|"desktop_agent"|"validation_agent";
export type AgentStatus = "idle"|"active"|"done"|"failed"|"unavailable"|"retrying";

export interface Agent {
  id: AgentId;
  name: string;
  color: string;
  status: AgentStatus;
  detail?: string;
}

export function buildAgents(mode: string): Agent[] {
  return [
    { id: "supervisor",           name: "Supervisor",           color: C.navy,      status: "idle" },
    { id: "requirement_analyzer", name: "Requirement Analyzer", color: C.teal,      status: "idle" },
    { id: "planning_agent",       name: "Planning Agent",       color: C.amber,     status: "idle" },
    { id: "document_agent",       name: "Document Agent",       color: C.slateBlue, status: "idle" },
    { id: "browser_agent",        name: "Browser Agent",        color: C.slateBlue, status: mode === "ollama" ? "unavailable" : "idle" },
    { id: "desktop_agent",        name: "Desktop Agent",        color: C.slateBlue, status: "idle" },
    { id: "validation_agent",     name: "Validation Agent",     color: C.teal,      status: "idle" },
  ];
}

const BASE_URL = import.meta.env.BASE_URL ?? "/";

export function useChatStream(mode: string) {
  const [agents, setAgents] = useState<Agent[]>(() => buildAgents(mode));
  const [streamingMessages, setStreamingMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [retryActive, setRetryActive] = useState(false);

  const send = useCallback(async (text: string, targetSessionId: string, onDone: () => void) => {
    if (!targetSessionId) return;
    setIsStreaming(true);
    setStreamingMessages([]);
    setAgents(buildAgents(mode));
    setRetryActive(false);

    try {
      const response = await fetch(`${BASE_URL.replace(/\/$/, '')}/api/chat/sessions/${targetSessionId}/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      
      if (!response.body) return;
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";
        
        for (const part of parts) {
          if (part.startsWith("data: ")) {
            const dataStr = part.slice(6).trim();
            if (!dataStr) continue;
            try {
              const data = JSON.parse(dataStr);
              if (data.type === "agent_update") {
                setAgents(prev => prev.map(a => a.id === data.agent ? { ...a, status: data.status, detail: data.detail } : a));
                if (data.agent === "planning_agent" && data.status === "retrying") {
                  setRetryActive(true);
                } else if (data.agent === "planning_agent" && (data.status === "active" || data.status === "idle")) {
                  setRetryActive(false);
                }
              } else if (data.type === "message") {
                setStreamingMessages(prev => [...prev, {
                  id: Date.now().toString() + Math.random().toString(),
                  sessionId: targetSessionId,
                  role: "agent",
                  agentName: data.agentName,
                  agentColor: data.agentColor,
                  kind: data.kind,
                  text: data.text,
                  items: data.items,
                  createdAt: new Date().toISOString()
                }]);
              } else if (data.type === "done") {
                // Stream is done
              }
            } catch (e) {
              console.error("Failed to parse SSE event", e, "Data:", dataStr);
            }
          }
        }
      }
    } catch (e) {
      console.error("Stream error", e);
    } finally {
      setIsStreaming(false);
      onDone();
    }
  }, [mode]);

  return { agents, setAgents, streamingMessages, isStreaming, send, retryActive };
}
