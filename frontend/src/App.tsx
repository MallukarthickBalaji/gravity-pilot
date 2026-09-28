import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Mic, MicOff, Send, AlertCircle } from "lucide-react";
import { StatusBar } from "./components/StatusBar";
import { Sidebar } from "./components/Sidebar";
import { ChatPanel } from "./components/ChatPanel";
import { TracePanel } from "./components/TracePanel";
import { useChatStream, ChatMessage } from "./hooks/use-chat-stream";
import { C } from "./theme";
import { SessionItem, OllamaInfo, VoiceState } from "./types";
import {
  fetchHealth,
  fetchOllamaHealth,
  fetchSessions,
  createSession,
  deleteSessionApi,
  fetchSessionHistory,
} from "./services/api";

export default function App() {
  const [mode, setMode] = useState<string>("groq");
  const [ollamaInfo, setOllamaInfo] = useState<OllamaInfo | null>(null);
  const [groqAvailable, setGroqAvailable] = useState<boolean>(true);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [historyMessages, setHistoryMessages] = useState<ChatMessage[]>([]);
  const [optimisticMessages, setOptimisticMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isBackendOnline, setIsBackendOnline] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState<VoiceState>("idle");
  const [voiceMessage, setVoiceMessage] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);

  const {
    agents,
    streamingMessages,
    isStreaming,
    send,
    retryActive,
    abortCurrentStream,
  } = useChatStream(mode);

  // Health check
  const checkHealth = useCallback(async () => {
    const health = await fetchHealth();
    setIsBackendOnline(health.backendOnline);
    setGroqAvailable(health.groqAvailable);

    const oinfo = await fetchOllamaHealth();
    setOllamaInfo(oinfo);
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  // Load sessions
  const loadSessions = useCallback(async () => {
    const list = await fetchSessions();
    setSessions(list);
    if (!sessionId && list.length > 0) {
      setSessionId(list[0].id);
    }
  }, [sessionId]);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  // Load history messages when active session changes
  const loadHistory = useCallback(async (sid: string) => {
    const msgs = await fetchSessionHistory(sid);
    setHistoryMessages(msgs);
    setOptimisticMessages([]);
  }, []);

  useEffect(() => {
    if (sessionId) {
      loadHistory(sessionId);
    } else {
      setHistoryMessages([]);
      setOptimisticMessages([]);
    }
  }, [sessionId, loadHistory]);

  const combinedMessages = useMemo(() => {
    return [...historyMessages, ...optimisticMessages, ...streamingMessages];
  }, [historyMessages, optimisticMessages, streamingMessages]);

  const handleSend = async (text: string) => {
    if (!text.trim() || isStreaming) return;

    if (mode === "ollama" && ollamaInfo && !ollamaInfo.available) {
      alert(`Local Ollama is unavailable: ${ollamaInfo.error || "Please start Ollama on http://127.0.0.1:11434"}`);
      return;
    }

    let targetSid = sessionId;
    if (!targetSid) {
      targetSid = Date.now().toString() + Math.random().toString(36).substring(2, 8);
      setSessionId(targetSid);
      setSessions((prev) => [
        { id: targetSid!, title: text.slice(0, 35), updated_at: new Date().toISOString() },
        ...prev,
      ]);
    }

    setOptimisticMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        sessionId: targetSid!,
        role: "user",
        text,
        createdAt: new Date().toISOString(),
      },
    ]);

    setInput("");

    await send(text, targetSid, () => {
      loadHistory(targetSid!);
      loadSessions();
    });
  };

  // Proper New Chat session lifecycle (Requirement 5)
  const handleNewChat = async () => {
    abortCurrentStream();
    setHistoryMessages([]);
    setOptimisticMessages([]);
    setInput("");
    setVoiceStatus("idle");
    setVoiceMessage(null);

    const newId = await createSession("New Chat");
    const activeId = newId || (Date.now().toString() + Math.random().toString(36).substring(2, 8));
    setSessionId(activeId);
    setSessions((prev) => [
      { id: activeId, title: "New Chat", created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
      ...prev,
    ]);
  };

  const handleSelectSession = (id: string) => {
    if (id === sessionId) return;
    abortCurrentStream();
    setSessionId(id);
  };

  const handleDeleteSession = async (id: string) => {
    await deleteSessionApi(id);
    setSessions((prev) => prev.filter((s) => s.id !== id));
    if (sessionId === id) {
      handleNewChat();
    }
  };

  // Web Speech API Voice Recognition (Requirement 1)
  const toggleVoiceInput = () => {
    if (voiceStatus === "listening") {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setVoiceStatus("idle");
      setVoiceMessage(null);
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setVoiceStatus("unsupported");
      setVoiceMessage("Speech recognition unavailable in this browser.");
      setTimeout(() => {
        setVoiceStatus("idle");
        setVoiceMessage(null);
      }, 4000);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setVoiceStatus("listening");
        setVoiceMessage("Listening... Speak naturally.");
      };

      recognition.onresult = (event: any) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        if (transcript) {
          setInput((prev) => {
            const trimmed = prev.trim();
            return trimmed ? `${trimmed} ${transcript}` : transcript;
          });
        }
      };

      recognition.onerror = (event: any) => {
        if (event.error === "not-allowed" || event.error === "service-not-allowed") {
          setVoiceStatus("denied");
          setVoiceMessage("Microphone permission denied. Please allow microphone access.");
        } else {
          setVoiceStatus("idle");
          setVoiceMessage(null);
        }
        setTimeout(() => {
          setVoiceStatus("idle");
          setVoiceMessage(null);
        }, 5000);
      };

      recognition.onend = () => {
        setVoiceStatus("idle");
        setVoiceMessage(null);
      };

      recognition.start();
    } catch (err: any) {
      console.error("Speech recognition start failed:", err);
      setVoiceStatus("idle");
      setVoiceMessage(null);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100vw",
        height: "100vh",
        background: C.bg,
        overflow: "hidden",
      }}
    >
      {/* Top Status Bar */}
      <StatusBar
        mode={mode}
        setMode={setMode}
        isBackendOnline={isBackendOnline}
        ollamaInfo={ollamaInfo}
        groqAvailable={groqAvailable}
      />

      {/* Offline Alert Banner */}
      {!isBackendOnline && (
        <div
          style={{
            background: "#FFF1F0",
            borderBottom: "1px solid #FFCCC7",
            padding: "8px 20px",
            color: "#CF1322",
            fontSize: 12.5,
            fontFamily: "var(--dp-font-ui)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <span>
            ⚠️ <strong>Backend is not running.</strong> Please run <code>START.bat</code> to launch the FastAPI engine on port 8000.
          </span>
          <button
            onClick={checkHealth}
            style={{
              background: "white",
              border: "1px solid #FFA39E",
              borderRadius: 4,
              padding: "2px 8px",
              cursor: "pointer",
              fontSize: 11,
              fontWeight: 600,
            }}
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Main Workspace Area */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Left Sidebar */}
        <Sidebar
          sessions={sessions}
          activeSessionId={sessionId}
          onSelectSession={handleSelectSession}
          onNewChat={handleNewChat}
          onDeleteSession={handleDeleteSession}
        />

        {/* Center Chat Area */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            position: "relative",
          }}
        >
          <ChatPanel
            msgs={combinedMessages}
            mode={mode}
            onSuggestion={(suggestion) => handleSend(suggestion)}
          />

          {/* Voice Feedback Banner */}
          {voiceMessage && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "6px 20px",
                background: voiceStatus === "listening" ? "#ECFDF5" : "#FFF1F0",
                color: voiceStatus === "listening" ? "#065F46" : "#CF1322",
                borderTop: `1px solid ${voiceStatus === "listening" ? "#A7F3D0" : "#FFCCC7"}`,
                fontSize: 12,
                fontFamily: "var(--dp-font-ui)",
              }}
            >
              <AlertCircle size={14} />
              <span>{voiceMessage}</span>
            </div>
          )}

          {/* Input Area */}
          <div
            style={{
              padding: "14px 20px 18px",
              background: "white",
              borderTop: `1px solid ${C.panelBorder}`,
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            {/* Microphone / Speech-to-Text Button (Requirement 1) */}
            <button
              onClick={toggleVoiceInput}
              disabled={isStreaming}
              title={
                voiceStatus === "listening"
                  ? "Stop listening"
                  : voiceStatus === "denied"
                  ? "Microphone permission denied"
                  : "Click to speak naturally"
              }
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: 42,
                height: 42,
                borderRadius: 8,
                background:
                  voiceStatus === "listening"
                    ? "#DC2626"
                    : voiceStatus === "denied"
                    ? "#FEE2E2"
                    : "#F1F5F9",
                color:
                  voiceStatus === "listening"
                    ? "white"
                    : voiceStatus === "denied"
                    ? "#DC2626"
                    : C.textPrim,
                border: `1px solid ${
                  voiceStatus === "listening"
                    ? "#DC2626"
                    : voiceStatus === "denied"
                    ? "#FCA5A5"
                    : C.panelBorder
                }`,
                cursor: isStreaming ? "not-allowed" : "pointer",
                transition: "all 0.2s ease",
                animation: voiceStatus === "listening" ? "dp-pulse 1.2s infinite" : "none",
                flexShrink: 0,
              }}
            >
              {voiceStatus === "listening" ? <Mic size={18} /> : voiceStatus === "denied" ? <MicOff size={18} /> : <Mic size={18} />}
            </button>

            <input
              type="text"
              placeholder={
                isStreaming
                  ? "GravityPilot is working on your request..."
                  : voiceStatus === "listening"
                  ? "Listening to speech... speak your task naturally"
                  : "Type your request... (e.g. 'Create an Excel attendance sheet for 10 students' or 'Create a leave letter')"
              }
              value={input}
              disabled={isStreaming}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(input);
                }
              }}
              style={{
                flex: 1,
                padding: "11px 16px",
                border: `1px solid ${voiceStatus === "listening" ? "#DC2626" : C.panelBorder}`,
                borderRadius: 8,
                fontSize: 13.5,
                fontFamily: "var(--dp-font-ui)",
                color: C.textPrim,
                outline: "none",
                transition: "border-color 0.15s ease",
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = C.navy;
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = C.panelBorder;
              }}
            />

            <button
              onClick={() => handleSend(input)}
              disabled={isStreaming || !input.trim()}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 6,
                padding: "11px 18px",
                borderRadius: 8,
                background: isStreaming || !input.trim() ? `${C.navy}66` : C.navy,
                color: "white",
                border: "none",
                fontWeight: 600,
                fontSize: 13,
                cursor: isStreaming || !input.trim() ? "not-allowed" : "pointer",
                transition: "all 0.15s ease",
                boxShadow: "0 1px 3px rgba(31,58,95,0.2)",
                flexShrink: 0,
              }}
            >
              <Send size={15} /> Send
            </button>
          </div>
        </div>

        {/* Right Trace Panel */}
        <TracePanel agents={agents} retryActive={retryActive} mode={mode} />
      </div>
    </div>
  );
}
