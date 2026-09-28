import { useState, useEffect, useRef, useCallback } from "react";
import "./_group.css";

// ── Palette ───────────────────────────────────────────────────────────────────
const C = {
  navy:       "#1F3A5F",
  teal:       "#2E7D6B",
  slateBlue:  "#3E6B8A",
  amber:      "#C9891A",
  redMuted:   "#B84040",
  bg:         "#F4F8FC",
  panel:      "#EAF0F6",
  panelBorder:"#CBD5E0",
  sidebarBg:  "#162A42",
  sidebarText:"#C8D8E8",
  sidebarDim: "#4E6E8E",
  border:     "#2A4468",
  textPrim:   "#1A2B3C",
  textSec:    "#5A6472",
};

// ── Types ─────────────────────────────────────────────────────────────────────
type AgentId = "supervisor"|"req_analyzer"|"planning"|"doc_agent"|"browser_agent"|"desktop_agent"|"validation";
type AgentStatus = "idle"|"active"|"done"|"failed"|"unavailable"|"retrying";
type BackendMode = "groq"|"ollama";

interface Agent { id: AgentId; name: string; color: string; status: AgentStatus; detail?: string; }

interface ChatMsg {
  id: number;
  role: "user"|"agent";
  agentName?: string;
  agentColor?: string;
  kind?: "normal"|"clarification"|"error"|"plan";
  text: string;
  items?: string[];
}

// ── Simulation data ───────────────────────────────────────────────────────────
type SimStep = {
  agentUpdates?: Partial<Record<AgentId, { status: AgentStatus; detail?: string }>>;
  addMsg?: ChatMsg;
  retryActive?: boolean;
  ms: number;
};

const GROQ_SIM: SimStep[] = [
  { ms: 400 },
  { agentUpdates: { supervisor: { status:"active", detail:"Classifying…" } }, ms: 900 },
  { agentUpdates: { supervisor: { status:"done", detail:"document_generation" } }, ms: 400 },
  { agentUpdates: { req_analyzer: { status:"active", detail:"Checking requirements…" } }, ms: 900 },
  { agentUpdates: { req_analyzer: { status:"done", detail:"All info present" } }, ms: 400 },
  {
    addMsg: { id:2, role:"agent", agentName:"Requirement Analyzer", agentColor:C.teal, kind:"normal",
      text:"Got everything I need. Planning the steps now." },
    ms: 500,
  },
  { agentUpdates: { planning: { status:"active", detail:"Generating plan…" } }, ms: 1100 },
  { agentUpdates: { planning: { status:"done", detail:"3 steps ready" } }, ms: 400 },
  {
    addMsg: { id:3, role:"agent", agentName:"Planning Agent", agentColor:C.amber, kind:"plan",
      text:"Plan ready — 3 steps:",
      items:["Generate Excel (.xlsx) via Document Agent","Verify file exists and is non-empty","Report result to user"] },
    ms: 600,
  },
  { agentUpdates: { doc_agent: { status:"active", detail:"Writing attendance_sheet.xlsx…" } }, ms: 1300 },
  { agentUpdates: { doc_agent: { status:"done", detail:"Generated (0 bytes — corrupt)" } }, ms: 400 },
  { agentUpdates: { validation: { status:"active", detail:"Verifying…" } }, ms: 800 },
  { agentUpdates: { validation: { status:"failed", detail:"File empty — 0 bytes" } }, ms: 600 },
  {
    addMsg: { id:4, role:"agent", agentName:"Validation Agent", agentColor:C.teal, kind:"error",
      text:"Couldn't verify the spreadsheet — file was empty after generation. Retried once. Routing back to Planning Agent to replan." },
    ms: 500,
  },
  {
    agentUpdates: { planning:{status:"retrying"}, doc_agent:{status:"idle",detail:undefined}, validation:{status:"idle",detail:undefined} },
    retryActive: true, ms: 1600,
  },
  { agentUpdates: { planning: { status:"active", detail:"Replanning…" } }, retryActive: false, ms: 900 },
  { agentUpdates: { planning: { status:"done", detail:"Revised plan" } }, ms: 400 },
  { agentUpdates: { doc_agent: { status:"active", detail:"Retrying with corrected params…" } }, ms: 1300 },
  { agentUpdates: { doc_agent: { status:"done", detail:"attendance_sheet.xlsx — 2.4 KB" } }, ms: 400 },
  { agentUpdates: { validation: { status:"active", detail:"Verifying…" } }, ms: 700 },
  { agentUpdates: { validation: { status:"done", detail:"✓ Valid, 2.4 KB" } }, ms: 400 },
  {
    addMsg: { id:5, role:"agent", agentName:"Document Agent", agentColor:C.slateBlue, kind:"normal",
      text:"Done. attendance_sheet.xlsx saved to your Desktop (2.4 KB). 20 student rows × 10 date columns, P/A marked." },
    ms: 3500,
  },
  {
    agentUpdates: {
      supervisor:{status:"idle"}, req_analyzer:{status:"idle"}, planning:{status:"idle"},
      doc_agent:{status:"idle"}, validation:{status:"idle"},
    }, ms: 400,
  },
];

const OLLAMA_SIM: SimStep[] = [
  { ms: 400 },
  { agentUpdates: { supervisor: { status:"active", detail:"Classifying…" } }, ms: 900 },
  { agentUpdates: { supervisor: { status:"done", detail:"browser_automation — unavailable" } }, ms: 500 },
  {
    addMsg: { id:2, role:"agent", agentName:"Supervisor", agentColor:C.navy, kind:"error",
      text:"I can't run a browser automation task right now — that capability is unavailable in offline (Local) mode. I can help with document generation and desktop file operations instead. Try: \"Create an attendance sheet for my AI class\"." },
    ms: 3500,
  },
  {
    agentUpdates: { supervisor:{status:"idle"} }, ms: 400,
  },
];

function buildAgents(mode: BackendMode): Agent[] {
  return [
    { id:"supervisor",    name:"Supervisor",           color:C.navy,      status:"idle" },
    { id:"req_analyzer",  name:"Requirement Analyzer", color:C.teal,      status:"idle" },
    { id:"planning",      name:"Planning Agent",        color:C.amber,     status:"idle" },
    { id:"doc_agent",     name:"Document Agent",        color:C.slateBlue, status:"idle" },
    { id:"browser_agent", name:"Browser Agent",         color:C.slateBlue, status:mode==="ollama"?"unavailable":"idle" },
    { id:"desktop_agent", name:"Desktop Agent",         color:C.slateBlue, status:"idle" },
    { id:"validation",    name:"Validation Agent",      color:C.teal,      status:"idle" },
  ];
}

const INITIAL_MSGS: Record<BackendMode, ChatMsg[]> = {
  groq: [
    { id:1, role:"user", text:"Create an attendance sheet for my AI class — 20 students, 10 dates, mark with P or A" },
  ],
  ollama: [
    { id:1, role:"user", text:"Search the web for the top 5 Python AI libraries in 2025 and summarise them" },
  ],
};

// ── Small UI atoms ────────────────────────────────────────────────────────────
function NodeDot({ color, status }: { color: string; status: AgentStatus }) {
  const active  = status==="active"||status==="retrying";
  const done    = status==="done";
  const failed  = status==="failed";
  const unavail = status==="unavailable";
  const pulseRgb = color===C.amber?"201,137,26":color===C.teal?"46,125,107":color===C.navy?"31,58,95":"62,107,138";
  return (
    <div style={{
      width:9,height:9,borderRadius:"50%",flexShrink:0,marginTop:3,
      background: active||done ? color : "transparent",
      border: failed?`2px solid ${C.redMuted}`:unavail?`2px solid ${C.sidebarDim}44`:active||done?`2px solid ${color}`:`2px solid ${color}44`,
      opacity: unavail?0.4:1,
      animation: active?`dp-pulse 1.5s ease-in-out infinite`:"none",
      ["--dp-pulse-color" as string]:`rgba(${pulseRgb},0.55)`,
      transition:"all 0.25s ease",
    }} />
  );
}

function StatusIcon({ s }: { s: AgentStatus }) {
  const st: React.CSSProperties = { fontFamily:"var(--dp-font-mono)",fontSize:11,fontWeight:600,width:18,textAlign:"center",flexShrink:0 };
  if(s==="done")        return <span style={{...st,color:"#5AC994"}}>✓</span>;
  if(s==="failed")      return <span style={{...st,color:C.redMuted}}>✗</span>;
  if(s==="active"||s==="retrying") return <span style={{...st,color:C.amber,display:"inline-block",animation:"dp-spin 1.2s linear infinite"}}>⟳</span>;
  if(s==="unavailable") return <span style={{...st,color:C.sidebarDim}}>⊘</span>;
  return <span style={{...st,color:C.sidebarDim}}>·</span>;
}

// ── Trace Panel ───────────────────────────────────────────────────────────────
function TracePanel({ agents, retryActive, mode }: { agents:Agent[]; retryActive:boolean; mode:BackendMode }) {
  const planRef = useRef<HTMLDivElement>(null);
  const valRef  = useRef<HTMLDivElement>(null);
  const panelRef= useRef<HTMLDivElement>(null);
  const [arc, setArc] = useState({from:0,to:0});

  useEffect(() => {
    if(retryActive && planRef.current && valRef.current && panelRef.current) {
      const pr = panelRef.current.getBoundingClientRect();
      const pl = planRef.current.getBoundingClientRect();
      const vl = valRef.current.getBoundingClientRect();
      setArc({ from: vl.top+vl.height/2-pr.top, to: pl.top+pl.height/2-pr.top });
    }
  }, [retryActive]);

  const main = agents.filter(a=>a.id!=="browser_agent"&&a.id!=="desktop_agent");
  const side = agents.filter(a=>a.id==="browser_agent"||a.id==="desktop_agent");
  const active = agents.filter(a=>a.status==="active"||a.status==="retrying").length;
  const done   = agents.filter(a=>a.status==="done").length;

  return (
    <div ref={panelRef} style={{ position:"relative", height:"100%", display:"flex", flexDirection:"column", background:C.sidebarBg, overflow:"hidden" }}>
      {/* Header */}
      <div style={{ padding:"12px 16px 10px", borderBottom:`1px solid ${C.border}`, background:`${C.navy}88`, flexShrink:0, display:"flex", alignItems:"center", justifyContent:"space-between" }}>
        <span style={{ fontFamily:"var(--dp-font-mono)",fontSize:10,fontWeight:600,letterSpacing:1.2,textTransform:"uppercase",color:C.sidebarDim }}>
          Agent Trace
        </span>
        <div style={{ display:"flex",gap:6 }}>
          {active>0&&<span style={{ fontFamily:"var(--dp-font-mono)",fontSize:10,color:C.amber,background:`${C.amber}22`,padding:"2px 7px",borderRadius:10,border:`1px solid ${C.amber}44` }}>{active} running</span>}
          {done>0&&active===0&&<span style={{ fontFamily:"var(--dp-font-mono)",fontSize:10,color:"#5AC994",background:"#5AC99422",padding:"2px 7px",borderRadius:10,border:"1px solid #5AC99444" }}>{done} done</span>}
        </div>
      </div>

      {/* Retry SVG arc */}
      {retryActive && (
        <svg style={{ position:"absolute",top:0,left:0,width:"100%",height:"100%",pointerEvents:"none",overflow:"visible",zIndex:10 }}>
          <defs>
            <marker id="ah2" markerWidth="5" markerHeight="5" refX="2.5" refY="2.5" orient="auto">
              <path d="M 0,0 L 5,2.5 L 0,5 Z" fill={C.amber}/>
            </marker>
          </defs>
          <path d={`M 12,${arc.from} C -20,${arc.from-25} -20,${arc.to+25} 12,${arc.to}`}
            fill="none" stroke={`${C.amber}33`} strokeWidth={3} strokeLinecap="round"/>
          <path d={`M 12,${arc.from} C -20,${arc.from-25} -20,${arc.to+25} 12,${arc.to}`}
            fill="none" stroke={C.amber} strokeWidth={2} strokeLinecap="round"
            markerEnd="url(#ah2)"
            strokeDasharray="240" strokeDashoffset="240"
            style={{ animation:"dp-retry-draw 1.2s cubic-bezier(0.4,0,0.2,1) forwards" }}/>
        </svg>
      )}

      {/* Nodes */}
      <div style={{ flex:1, overflowY:"auto", padding:"8px 0 4px" }}>
        {main.map((a,i) => {
          const active2=a.status==="active"||a.status==="retrying";
          const rowBg = active2?`${a.color}18`:a.status==="done"?`${a.color}0F`:a.status==="failed"?`${C.redMuted}15`:"transparent";
          const bl    = active2?`3px solid ${a.color}`:a.status==="done"?`3px solid ${a.color}88`:a.status==="failed"?`3px solid ${C.redMuted}`:`3px solid ${a.color}22`;
          return (
            <div key={a.id} style={{ position:"relative" }}>
              {i<main.length-1 && <div style={{ position:"absolute",left:21,top:40,width:1,height:"100%",background:`${a.color}33`,zIndex:0 }}/>}
              <div ref={a.id==="planning"?planRef:a.id==="validation"?valRef:undefined}
                style={{ display:"flex",alignItems:"flex-start",gap:9,padding:"8px 14px 8px 18px",borderLeft:bl,background:rowBg,opacity:a.status==="unavailable"?0.5:1,transition:"all 0.25s ease",position:"relative",zIndex:1 }}>
                <NodeDot color={a.color} status={a.status}/>
                <div style={{ flex:1,minWidth:0 }}>
                  <div style={{ display:"flex",alignItems:"center",justifyContent:"space-between" }}>
                    <span style={{ fontFamily:"var(--dp-font-ui)",fontSize:12,fontWeight:500,color:a.status==="unavailable"?C.sidebarDim:C.sidebarText }}>
                      {a.name}
                    </span>
                    <StatusIcon s={a.status}/>
                  </div>
                  {a.detail && (active2||a.status==="done"||a.status==="failed") && (
                    <div style={{ fontFamily:"var(--dp-font-mono)",fontSize:10,color:a.status==="failed"?`${C.redMuted}CC`:`${C.sidebarText}77`,marginTop:2,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap" }}>
                      {a.detail}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        <div style={{ margin:"6px 18px 4px",borderTop:`1px dashed ${C.border}`,display:"flex",alignItems:"center" }}>
          <span style={{ fontFamily:"var(--dp-font-mono)",fontSize:10,color:C.sidebarDim,padding:"4px 0",letterSpacing:0.5 }}>
            {mode==="ollama"?"offline — restricted":"online"}
          </span>
        </div>

        {side.map(a => (
          <div key={a.id} style={{ display:"flex",alignItems:"center",gap:9,padding:"6px 14px 6px 18px",opacity:a.status==="unavailable"?0.4:1,borderLeft:`3px solid ${a.status==="unavailable"?C.sidebarDim+"33":a.color+"22"}`,transition:"all 0.25s ease" }}>
            <NodeDot color={a.color} status={a.status}/>
            <span style={{ fontFamily:"var(--dp-font-ui)",fontSize:12,color:a.status==="unavailable"?C.sidebarDim:C.sidebarText }}>
              {a.name}
            </span>
            {a.status==="unavailable"&&<span style={{ fontFamily:"var(--dp-font-mono)",fontSize:9,color:C.sidebarDim,background:`${C.sidebarDim}22`,padding:"1px 5px",borderRadius:3,marginLeft:"auto" }}>offline</span>}
            <StatusIcon s={a.status}/>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Chat Panel ────────────────────────────────────────────────────────────────
function ChatPanel({ msgs, mode }: { msgs:ChatMsg[]; mode:BackendMode }) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior:"smooth" }); }, [msgs]);

  return (
    <div style={{ flex:1,overflowY:"auto",padding:"20px 20px 8px",display:"flex",flexDirection:"column",gap:14 }}>
      {msgs.length===0&&(
        <div style={{ flex:1,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",gap:12,paddingBottom:60 }}>
          <div style={{ width:48,height:48,borderRadius:12,background:C.navy,display:"flex",alignItems:"center",justifyContent:"center",fontSize:22 }}>🤖</div>
          <p style={{ margin:0,fontFamily:"var(--dp-font-ui)",fontSize:14,fontWeight:600,color:C.textPrim }}>DesktopPilot AI</p>
          <p style={{ margin:0,fontFamily:"var(--dp-font-ui)",fontSize:13,color:C.textSec,textAlign:"center",maxWidth:280 }}>
            I can generate documents, automate desktop tasks, and search the web.
          </p>
          <div style={{ marginTop:4,padding:"10px 16px",background:C.panel,border:`1px solid ${C.panelBorder}`,borderRadius:8,cursor:"pointer" }}>
            <span style={{ fontFamily:"var(--dp-font-ui)",fontSize:12,color:C.textSec }}>
              Try: "Create an attendance sheet for my AI class"
            </span>
          </div>
        </div>
      )}
      {msgs.map(m => (
        <div key={m.id} style={{ display:"flex",flexDirection:"column",alignItems:m.role==="user"?"flex-end":"flex-start",gap:4 }}>
          {m.role==="agent"&&m.agentName&&(
            <div style={{ display:"flex",alignItems:"center",gap:6,paddingLeft:2 }}>
              <div style={{ width:8,height:8,borderRadius:"50%",background:m.agentColor,flexShrink:0 }}/>
              <span style={{ fontFamily:"var(--dp-font-mono)",fontSize:10,fontWeight:600,color:m.agentColor,letterSpacing:0.3 }}>
                {m.agentName}
              </span>
            </div>
          )}
          <div style={{
            maxWidth:"80%",padding:"10px 14px",borderRadius:m.role==="user"?"12px 12px 4px 12px":"12px 12px 12px 4px",
            background:
              m.role==="user"?C.navy:
              m.kind==="error"?`${C.redMuted}12`:
              m.kind==="clarification"?`${C.amber}12`:
              "white",
            border: m.role==="agent"?(m.kind==="error"?`1px solid ${C.redMuted}33`:m.kind==="clarification"?`1px solid ${C.amber}33`:`1px solid ${C.panelBorder}`):"none",
            boxShadow: m.role==="user"?"none":"0 1px 4px rgba(0,0,0,0.06)",
          }}>
            {m.kind==="clarification"&&(
              <div style={{ display:"flex",alignItems:"center",gap:6,marginBottom:6 }}>
                <span style={{ fontSize:10,background:`${C.amber}22`,color:C.amber,padding:"2px 8px",borderRadius:10,fontFamily:"var(--dp-font-mono)",fontWeight:600,border:`1px solid ${C.amber}44` }}>
                  clarification needed
                </span>
              </div>
            )}
            <p style={{ margin:0,fontFamily:"var(--dp-font-ui)",fontSize:13,lineHeight:1.5,color:m.role==="user"?"white":C.textPrim }}>
              {m.text}
            </p>
            {m.items&&(
              <ul style={{ margin:"8px 0 0",padding:"0 0 0 16px",display:"flex",flexDirection:"column",gap:3 }}>
                {m.items.map((it,i)=>(
                  <li key={i} style={{ fontFamily:"var(--dp-font-mono)",fontSize:11,color:C.textSec,lineHeight:1.5 }}>{it}</li>
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

// ── Full App ──────────────────────────────────────────────────────────────────
export function FullApp() {
  const [mode, setMode]       = useState<BackendMode>("groq");
  const [agents, setAgents]   = useState<Agent[]>(()=>buildAgents("groq"));
  const [msgs, setMsgs]       = useState<ChatMsg[]>(()=>[...INITIAL_MSGS.groq]);
  const [retry, setRetry]     = useState(false);
  const [simRunning, setSim]  = useState(false);
  const [step, setStep]       = useState(0);
  const [input, setInput]     = useState("");

  useEffect(() => {
    setAgents(buildAgents(mode));
    setMsgs([...INITIAL_MSGS[mode]]);
    setRetry(false);
    setSim(false);
    setStep(0);
  }, [mode]);

  const sim = mode==="groq"?GROQ_SIM:OLLAMA_SIM;

  useEffect(() => {
    if(!simRunning) return;
    if(step>=sim.length){ setSim(false); setStep(0); return; }
    const cur = sim[step];
    const t = setTimeout(()=>{
      if(cur.agentUpdates) setAgents(prev=>prev.map(a=>cur.agentUpdates![a.id]?{...a,...cur.agentUpdates![a.id]}:a));
      if(cur.addMsg)        setMsgs(prev=>[...prev,cur.addMsg!]);
      setRetry(!!cur.retryActive);
      setStep(s=>s+1);
    }, cur.ms);
    return ()=>clearTimeout(t);
  }, [simRunning, step, sim]);

  const startSim = useCallback(()=>{
    setAgents(buildAgents(mode));
    setMsgs([...INITIAL_MSGS[mode]]);
    setRetry(false);
    setStep(0);
    setSim(true);
  },[mode]);

  return (
    <div style={{ width:"100vw",height:"100vh",display:"flex",flexDirection:"column",background:C.bg,fontFamily:"var(--dp-font-ui)",overflow:"hidden" }}>
      {/* Status Bar */}
      <div style={{ height:44,display:"flex",alignItems:"center",justifyContent:"space-between",padding:"0 20px",background:C.navy,flexShrink:0,gap:16 }}>
        <div style={{ display:"flex",alignItems:"center",gap:10 }}>
          <div style={{ width:28,height:28,borderRadius:8,background:`${C.slateBlue}88`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:14 }}>🤖</div>
          <span style={{ fontFamily:"var(--dp-font-ui)",fontSize:14,fontWeight:700,color:"white",letterSpacing:0.2 }}>DesktopPilot AI</span>
        </div>

        <div style={{ display:"flex",alignItems:"center",gap:12 }}>
          {/* Mode toggle */}
          <div style={{ display:"flex",borderRadius:6,overflow:"hidden",border:`1px solid ${C.border}`,fontSize:12 }}>
            {(["groq","ollama"] as BackendMode[]).map(m=>(
              <button key={m} onClick={()=>setMode(m)} style={{ padding:"5px 14px",border:"none",cursor:"pointer",fontFamily:"var(--dp-font-ui)",fontSize:11,fontWeight:500,background:mode===m?C.slateBlue:`${C.navy}88`,color:"white",transition:"all 0.15s" }}>
                {m==="groq"?"☁ Cloud (Groq)":"⊙ Local (Ollama)"}
              </button>
            ))}
          </div>

          {/* Connectivity pill */}
          <div style={{ display:"flex",gap:8 }}>
            <span style={{ display:"flex",alignItems:"center",gap:5,fontFamily:"var(--dp-font-mono)",fontSize:11,color:mode==="groq"?"#5AC994":"#F0A040",background:"rgba(255,255,255,0.08)",padding:"4px 10px",borderRadius:20 }}>
              <span style={{ width:7,height:7,borderRadius:"50%",background:mode==="groq"?"#5AC994":"#F0A040",display:"inline-block",boxShadow:mode==="groq"?"0 0 6px #5AC99488":"none" }}/>
              {mode==="groq"?"Online":"Offline"}
            </span>
            <span style={{ display:"flex",alignItems:"center",gap:5,fontFamily:"var(--dp-font-mono)",fontSize:11,color:mode==="ollama"?"#5AC994":C.sidebarDim,background:"rgba(255,255,255,0.08)",padding:"4px 10px",borderRadius:20 }}>
              <span style={{ width:7,height:7,borderRadius:"50%",background:mode==="ollama"?"#5AC994":C.sidebarDim,display:"inline-block" }}/>
              Local
            </span>
          </div>

          <button onClick={startSim} disabled={simRunning} style={{ padding:"5px 14px",borderRadius:6,border:"none",cursor:simRunning?"default":"pointer",background:simRunning?C.sidebarDim:C.amber,color:"white",fontFamily:"var(--dp-font-ui)",fontSize:11,fontWeight:600,opacity:simRunning?0.6:1,flexShrink:0 }}>
            {simRunning?"Running…":"▶ Demo"}
          </button>
        </div>
      </div>

      {/* Main content */}
      <div style={{ flex:1,display:"flex",overflow:"hidden" }}>
        {/* Conversation — left */}
        <div style={{ flex:1,display:"flex",flexDirection:"column",borderRight:`1px solid ${C.panelBorder}`,minWidth:0 }}>
          <ChatPanel msgs={msgs} mode={mode}/>

          {/* Input bar */}
          <div style={{ padding:"12px 16px",borderTop:`1px solid ${C.panelBorder}`,background:"white",display:"flex",gap:10,flexShrink:0 }}>
            <input
              value={input}
              onChange={e=>setInput(e.target.value)}
              placeholder="Type a request…"
              style={{ flex:1,padding:"10px 14px",border:`1px solid ${C.panelBorder}`,borderRadius:8,fontFamily:"var(--dp-font-ui)",fontSize:13,color:C.textPrim,outline:"none",background:C.bg }}
            />
            <button style={{ padding:"10px 18px",borderRadius:8,border:"none",background:C.navy,color:"white",fontFamily:"var(--dp-font-ui)",fontSize:13,fontWeight:600,cursor:"pointer",flexShrink:0 }}>
              Send
            </button>
          </div>
        </div>

        {/* Trace panel — right */}
        <div style={{ width:280,flexShrink:0,display:"flex",flexDirection:"column" }}>
          <TracePanel agents={agents} retryActive={retry} mode={mode}/>
        </div>
      </div>

      <style>{`@keyframes dp-spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }`}</style>
    </div>
  );
}
