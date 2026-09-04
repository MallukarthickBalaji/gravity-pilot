import { useState, useEffect, useMemo, useRef } from "react";
import { QueryClient, QueryClientProvider, useQueryClient } from "@tanstack/react-query";
import { C } from "./theme";
import { StatusBar } from "./components/StatusBar";
import { ChatPanel } from "./components/ChatPanel";
import { TracePanel } from "./components/TracePanel";
import { Sidebar } from "./components/Sidebar";
import { useChatStream, buildAgents } from "./hooks/use-chat-stream";
import { Mic, AlertCircle } from "lucide-react";
import { 
  useGetChatStatus, 
  useListChatSessions, 
  useCreateChatSession, 
  useGetSessionMessages,
  getGetSessionMessagesQueryKey,
  getListChatSessionsQueryKey,
  ChatSessionInputMode,
  ChatMessage
} from "@workspace/api-client-react";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    }
  }
});

function DesktopPilotApp() {
  const qc = useQueryClient();
  const [mode, setMode] = useState<ChatSessionInputMode>("groq");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [optimisticMessages, setOptimisticMessages] = useState<ChatMessage[]>([]);
  const [isNewChat, setIsNewChat] = useState(false);
  
  // Voice State
  const [voiceState, setVoiceState] = useState<"IDLE" | "LISTENING" | "PROCESSING" | "ERROR">("IDLE");
  const [voiceErrorMsg, setVoiceErrorMsg] = useState("");
  const recognitionRef = useRef<any>(null);

  const { data: status } = useGetChatStatus();
  
  useEffect(() => {
    if (status?.mode && status.mode !== "none") {
      setMode(status.mode as ChatSessionInputMode);
    }
  }, [status?.mode]);

  const { data: sessions = [] } = useListChatSessions();
  const mostRecentSession = sessions[0];

  useEffect(() => {
    if (mostRecentSession && !sessionId && !isNewChat) {
      setSessionId(mostRecentSession.id);
      setMode(mostRecentSession.mode as ChatSessionInputMode);
    }
  }, [mostRecentSession, sessionId, isNewChat]);

  const { data: history = [] } = useGetSessionMessages(sessionId!, { 
    query: { 
      enabled: !!sessionId,
      queryKey: getGetSessionMessagesQueryKey(sessionId!) 
    } 
  });
  
  const createSession = useCreateChatSession();
  const { agents, streamingMessages, isStreaming, send, retryActive, setAgents } = useChatStream(mode);

  // When session changes or history arrives, clear optimistic messages
  useEffect(() => {
    setOptimisticMessages([]);
  }, [history.length, sessionId]);

  const combinedMessages = useMemo(() => {
    return [...history, ...optimisticMessages, ...streamingMessages];
  }, [history, optimisticMessages, streamingMessages]);

  const handleSend = async (text: string) => {
    if (!text.trim() || isStreaming) return;
    
    setInput("");
    
    let activeSessionId = sessionId;
    if (!activeSessionId) {
      try {
        const newSession = await createSession.mutateAsync({ data: { mode } });
        activeSessionId = newSession.id;
        setSessionId(newSession.id);
        setIsNewChat(false);
        qc.invalidateQueries({ queryKey: getListChatSessionsQueryKey() });
      } catch (e) {
        console.error("Failed to create session", e);
        return;
      }
    }
    
    setOptimisticMessages(prev => [...prev, {
      id: Date.now().toString(),
      sessionId: activeSessionId!,
      role: "user",
      text,
      createdAt: new Date().toISOString()
    }]);

    await send(text, activeSessionId, () => {
      qc.invalidateQueries({ queryKey: getGetSessionMessagesQueryKey(activeSessionId!) });
      qc.invalidateQueries({ queryKey: getListChatSessionsQueryKey() }); // Refresh title
    });
  };

  const handleNewChat = () => {
    setSessionId(null);
    setIsNewChat(true);
    setAgents(buildAgents(mode));
  };

  const handleSelectSession = (id: string) => {
    setSessionId(id);
    setIsNewChat(false);
    setAgents(buildAgents(mode)); // Clear Agent Trace
  };

  const toggleVoice = () => {
    if (isStreaming) return;

    if (voiceState === "LISTENING") {
      recognitionRef.current?.stop();
      setVoiceState("IDLE");
      return;
    }

    setVoiceErrorMsg("");
    
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceState("ERROR");
      setVoiceErrorMsg("Speech recognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setVoiceState("LISTENING");
    };

    recognition.onresult = (event: any) => {
      setVoiceState("PROCESSING");
      const transcript = event.results[0][0].transcript;
      if (transcript) {
        // We set input just for visual, but send immediately
        setInput(transcript);
        handleSend(transcript);
        setVoiceState("IDLE");
      }
    };

    recognition.onerror = (event: any) => {
      setVoiceState("ERROR");
      if (event.error === "not-allowed") {
        setVoiceErrorMsg("Microphone access was denied. You can still type your request.");
      } else if (event.error === "no-speech") {
        setVoiceErrorMsg("No speech detected. Please try again.");
      } else {
        setVoiceErrorMsg(`Microphone error: ${event.error}`);
      }
      setTimeout(() => setVoiceState("IDLE"), 4000); // Clear error after 4s
    };

    recognition.onend = () => {
      // If we didn't explicitly transition to PROCESSING/ERROR
      setVoiceState(prev => prev === "LISTENING" ? "IDLE" : prev);
    };

    recognitionRef.current = recognition;
    
    try {
      recognition.start();
    } catch (e) {
      console.error(e);
      setVoiceState("ERROR");
      setVoiceErrorMsg("Could not start microphone.");
    }
  };

  return (
    <div style={{ width: "100vw", height: "100vh", display: "flex", flexDirection: "column", background: C.bg, fontFamily: "var(--dp-font-ui)", overflow: "hidden" }}>
      <StatusBar mode={mode} setMode={(m) => setMode(m as ChatSessionInputMode)} />
      
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Sidebar Pane */}
        <Sidebar 
          sessions={sessions}
          activeSessionId={sessionId}
          onSelectSession={handleSelectSession}
          onNewChat={handleNewChat}
        />

        {/* Conversation Pane */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", borderRight: `1px solid ${C.panelBorder}`, minWidth: 0 }}>
          <ChatPanel msgs={combinedMessages} mode={mode} onSuggestion={(t) => {
            setInput(t);
          }} />
          
          <div style={{ padding: "12px 16px", borderTop: `1px solid ${C.panelBorder}`, background: "white", display: "flex", flexDirection: "column", flexShrink: 0 }}>
            {voiceState === "ERROR" && (
              <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "6px 10px", marginBottom: 8, background: `${C.redMuted}1A`, borderRadius: 6, color: C.redMuted, fontSize: 12 }}>
                <AlertCircle size={14} />
                <span>{voiceErrorMsg}</span>
              </div>
            )}
            
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <button
                onClick={toggleVoice}
                disabled={isStreaming}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: 44,
                  height: 44,
                  borderRadius: "50%",
                  border: voiceState === "LISTENING" ? `2px solid ${C.redMuted}` : `1px solid ${C.panelBorder}`,
                  background: voiceState === "LISTENING" ? `${C.redMuted}1A` : C.bg,
                  color: voiceState === "LISTENING" ? C.redMuted : C.textSec,
                  cursor: isStreaming ? "not-allowed" : "pointer",
                  transition: "all 0.2s",
                  flexShrink: 0
                }}
                title="Voice Input"
              >
                <Mic size={20} style={{ opacity: voiceState === "LISTENING" ? 1 : 0.7 }} />
              </button>

              <div style={{ flex: 1, display: "flex", alignItems: "center", position: "relative" }}>
                <input
                  value={voiceState === "LISTENING" ? "Listening..." : voiceState === "PROCESSING" ? "Processing..." : input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && handleSend(input)}
                  placeholder="Type a request…"
                  style={{ flex: 1, padding: "10px 14px", border: `1px solid ${C.panelBorder}`, borderRadius: 8, fontFamily: "var(--dp-font-ui)", fontSize: 13, color: (voiceState === "LISTENING" || voiceState === "PROCESSING") ? C.textSec : C.textPrim, outline: "none", background: C.bg }}
                  disabled={isStreaming || voiceState === "LISTENING" || voiceState === "PROCESSING"}
                />
              </div>

              <button 
                onClick={() => handleSend(input)}
                disabled={isStreaming || !input.trim() || voiceState === "LISTENING" || voiceState === "PROCESSING"}
                style={{ padding: "10px 18px", height: 44, borderRadius: 8, border: "none", background: (isStreaming || !input.trim() || voiceState === "LISTENING" || voiceState === "PROCESSING") ? `${C.navy}88` : C.navy, color: "white", fontFamily: "var(--dp-font-ui)", fontSize: 13, fontWeight: 600, cursor: (isStreaming || !input.trim() || voiceState === "LISTENING" || voiceState === "PROCESSING") ? "not-allowed" : "pointer", flexShrink: 0 }}>
                Send
              </button>
            </div>
          </div>
        </div>
        
        {/* Trace Pane */}
        <div style={{ width: 280, flexShrink: 0, display: "flex", flexDirection: "column" }}>
          <TracePanel agents={agents} retryActive={retryActive} mode={mode} />
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <DesktopPilotApp />
    </QueryClientProvider>
  );
}

export default App;
