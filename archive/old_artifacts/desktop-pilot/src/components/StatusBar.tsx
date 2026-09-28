import { C } from "../theme";

export function StatusBar({ mode, setMode }: { mode: string; setMode: (m: string) => void }) {
  return (
    <div style={{ height: 44, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 20px", background: C.navy, flexShrink: 0, gap: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{ width: 28, height: 28, borderRadius: 8, background: `${C.slateBlue}88`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14 }}>🤖</div>
        <span style={{ fontFamily: "var(--dp-font-ui)", fontSize: 14, fontWeight: 700, color: "white", letterSpacing: 0.2 }}>DesktopPilot AI</span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        {/* Mode toggle */}
        <div style={{ display: "flex", borderRadius: 6, overflow: "hidden", border: `1px solid ${C.border}`, fontSize: 12 }}>
          {(["groq", "ollama"] as const).map(m => (
            <button key={m} onClick={() => setMode(m)} style={{ padding: "5px 14px", border: "none", cursor: "pointer", fontFamily: "var(--dp-font-ui)", fontSize: 11, fontWeight: 500, background: mode === m ? C.slateBlue : `${C.navy}88`, color: "white", transition: "all 0.15s" }}>
              {m === "groq" ? "☁ Cloud (Groq)" : "⊙ Local (Ollama)"}
            </button>
          ))}
        </div>

        {/* Connectivity pill */}
        <div style={{ display: "flex", gap: 8 }}>
          <span style={{ display: "flex", alignItems: "center", gap: 5, fontFamily: "var(--dp-font-mono)", fontSize: 11, color: mode === "groq" ? "#5AC994" : "#F0A040", background: "rgba(255,255,255,0.08)", padding: "4px 10px", borderRadius: 20 }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: mode === "groq" ? "#5AC994" : "#F0A040", display: "inline-block", boxShadow: mode === "groq" ? "0 0 6px #5AC99488" : "none" }}/>
            {mode === "groq" ? "Online" : "Offline"}
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: 5, fontFamily: "var(--dp-font-mono)", fontSize: 11, color: mode === "ollama" ? "#5AC994" : C.sidebarDim, background: "rgba(255,255,255,0.08)", padding: "4px 10px", borderRadius: 20 }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: mode === "ollama" ? "#5AC994" : C.sidebarDim, display: "inline-block" }}/>
            Local
          </span>
        </div>
      </div>
    </div>
  );
}
