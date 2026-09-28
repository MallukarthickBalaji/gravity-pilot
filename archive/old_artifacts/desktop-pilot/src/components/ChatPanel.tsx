import { useEffect, useRef } from "react";
import { ChatMessage } from "@workspace/api-client-react";
import { C } from "../theme";

export function ChatPanel({ msgs, mode, onSuggestion }: { msgs: ChatMessage[]; mode: string; onSuggestion: (text: string) => void }) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs]);

  return (
    <div style={{ flex: 1, overflowY: "auto", padding: "20px 20px 8px", display: "flex", flexDirection: "column", gap: 14 }}>
      {msgs.length === 0 && (
        <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 12, paddingBottom: 60 }}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: C.navy, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22 }}>🤖</div>
          <p style={{ margin: 0, fontFamily: "var(--dp-font-ui)", fontSize: 14, fontWeight: 600, color: C.textPrim }}>DesktopPilot AI</p>
          <p style={{ margin: 0, fontFamily: "var(--dp-font-ui)", fontSize: 13, color: C.textSec, textAlign: "center", maxWidth: 280 }}>
            I can generate documents, automate desktop tasks, and search the web.
          </p>
          <div 
            onClick={() => onSuggestion("Create an attendance sheet for my AI class")}
            style={{ marginTop: 4, padding: "10px 16px", background: C.panel, border: `1px solid ${C.panelBorder}`, borderRadius: 8, cursor: "pointer" }}>
            <span style={{ fontFamily: "var(--dp-font-ui)", fontSize: 12, color: C.textSec }}>
              Try: "Create an attendance sheet for my AI class"
            </span>
          </div>
        </div>
      )}
      {msgs.map((m, i) => (
        <div key={m.id || i} style={{ display: "flex", flexDirection: "column", alignItems: m.role === "user" ? "flex-end" : "flex-start", gap: 4 }}>
          {m.role === "agent" && m.agentName && (
            <div style={{ display: "flex", alignItems: "center", gap: 6, paddingLeft: 2 }}>
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: m.agentColor || C.slateBlue, flexShrink: 0 }}/>
              <span style={{ fontFamily: "var(--dp-font-mono)", fontSize: 10, fontWeight: 600, color: m.agentColor || C.slateBlue, letterSpacing: 0.3 }}>
                {m.agentName}
              </span>
            </div>
          )}
          <div style={{
            maxWidth: "80%", padding: "10px 14px", borderRadius: m.role === "user" ? "12px 12px 4px 12px" : "12px 12px 12px 4px",
            background:
              m.role === "user" ? C.navy :
              m.kind === "error" ? `${C.redMuted}12` :
              m.kind === "clarification" ? `${C.amber}12` :
              "white",
            border: m.role === "agent" ? (m.kind === "error" ? `1px solid ${C.redMuted}33` : m.kind === "clarification" ? `1px solid ${C.amber}33` : `1px solid ${C.panelBorder}`) : "none",
            boxShadow: m.role === "user" ? "none" : "0 1px 4px rgba(0,0,0,0.06)",
          }}>
            {m.kind === "clarification" && (
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                <span style={{ fontSize: 10, background: `${C.amber}22`, color: C.amber, padding: "2px 8px", borderRadius: 10, fontFamily: "var(--dp-font-mono)", fontWeight: 600, border: `1px solid ${C.amber}44` }}>
                  clarification needed
                </span>
              </div>
            )}
            <p style={{ margin: 0, fontFamily: "var(--dp-font-ui)", fontSize: 13, lineHeight: 1.5, color: m.role === "user" ? "white" : C.textPrim, whiteSpace: "pre-wrap" }}>
              {m.text}
            </p>
            {m.items && m.items.length > 0 && (
              <ul style={{ margin: "8px 0 0", padding: "0 0 0 16px", display: "flex", flexDirection: "column", gap: 3 }}>
                {m.items.map((it, idx) => (
                  <li key={idx} style={{ fontFamily: "var(--dp-font-mono)", fontSize: 11, color: C.textSec, lineHeight: 1.5 }}>{it}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      ))}
      <div ref={bottomRef}/>
    </div>
  );
}
