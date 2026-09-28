/**
 * index.ts — Shared TypeScript interfaces and types for DesktopPilot AI frontend.
 */

export type VoiceState = "idle" | "listening" | "processing" | "unsupported" | "denied";

export interface SessionItem {
  id: string;
  title: string;
  created_at?: string;
  updated_at: string;
}

export interface GeneratedFile {
  taskId?: string;
  sessionId?: string;
  filePath: string;
  fileName: string;
  fileType: string;
  status?: string;
}

export interface ChatMessage {
  id: string;
  sessionId: string;
  taskId?: string;
  role: "user" | "assistant" | "agent";
  agentName?: string;
  agentColor?: string;
  kind?: "normal" | "clarification" | "error";
  text: string;
  items?: string[];
  generatedFiles?: GeneratedFile[];
  createdAt?: string;
}

export interface OllamaInfo {
  available: boolean;
  base_url?: string;
  models?: string[];
  active_model?: string;
  error?: string | null;
}

export interface HealthStatus {
  backend: boolean;
  groq_available: boolean;
  model_backend: string;
}

export type AgentId =
  | "model_router"
  | "supervisor"
  | "requirement_analyzer"
  | "memory_agent"
  | "planning_agent"
  | "task_coordinator"
  | "document_agent"
  | "desktop_agent"
  | "browser_agent"
  | "validation_agent";

export type AgentStatus = "idle" | "active" | "done" | "failed" | "unavailable" | "retrying";

export interface Agent {
  id: AgentId;
  name: string;
  color: string;
  status: AgentStatus;
  detail?: string;
}
