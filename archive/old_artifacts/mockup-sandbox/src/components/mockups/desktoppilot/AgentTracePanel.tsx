import { useState, useEffect, useRef, useCallback } from "react";
import "./_group.css";

// ── Types ─────────────────────────────────────────────────────────────────────

type AgentId =
  | "supervisor" | "req_analyzer" | "planning"
  | "doc_agent" | "browser_agent" | "desktop_agent" | "validation";

type AgentStatus = "idle" | "active" | "done" | "failed" | "unavailable" | "retrying";
type BackendMode = "groq" | "ollama";

interface Agent {
  id: AgentId;
  name: string;
  layer: "orchestration" | "reasoning" | "execution";
  color: string;
  status: AgentStatus;
  detail?: string;
}

// ── Palette ───────────────────────────────────────────────────────────────────

const COLOR = {
  navy:       "#1F3A5F",
  teal:       "#2E7D6B",
  slateBlue:  "#3E6B8A",
  amber:      "#C9891A",
  redMuted:   "#B84040",
  bg:         "#F4F8FC",
  panel:      "#EAF0F6",
  sidebarBg:  "#162A42",
  sidebarText:"#C8D8E8",
  sidebarDim: "#4E6E8E",
  border:     "#2A4468",
};

// ── Simulation ────────────────────────────────────────────────────────────────

type SimStep = {
  updates: Partial<Record<AgentId, { status: AgentStatus; detail?: string }>>;
  retryActive?: boolean;
  ms: number;
};

const SIM: SimStep[] = [
  { updates: {}, ms: 600 },
  { updates: { supervisor: { status: "active", detail: "Classifying request…" } }, ms: 900 },
  { updates: { supervisor: { status: "done", detail: "document_generation" } }, ms: 500 },
  { updates: { req_analyzer: { status: "active", detail: "Checking requirements…" } }, ms: 1000 },
  { updates: { req_analyzer: { status: "done", detail: "All info present" } }, ms: 500 },
  { updates: { planning: { status: "active", detail: "Generating 3-step plan…" } }, ms: 1100 },
  { updates: { planning: { status: "done", detail: "3 steps ready" } }, ms: 500 },
  { updates: { doc_agent: { status: "active", detail: "Generating attendance_sheet.xlsx…" } }, ms: 1300 },
  { updates: { doc_agent: { status: "done", detail: "Generated (0 bytes — corrupt)" } }, ms: 500 },
  { updates: { validation: { status: "active", detail: "Verifying file…" } }, ms: 900 },
  { updates: { validation: { status: "failed", detail: "File empty — execution failed" } }, ms: 800 },
  // cyclic edge fires: validation → planning
  { updates: { planning: { status: "retrying" }, doc_agent: { status: "idle", detail: undefined }, validation: { status: "idle", detail: undefined } }, retryActive: true, ms: 1600 },
  { updates: { planning: { status: "active", detail: "Replanning…" } }, retryActive: false, ms: 1000 },
  { updates: { planning: { status: "done", detail: "Revised plan ready" } }, ms: 500 },
  { updates: { doc_agent: { status: "active", detail: "Retrying with corrected params…" } }, ms: 1300 },
  { updates: { doc_agent: { status: "done", detail: "attendance_sheet.xlsx — 2.4 KB" } }, ms: 500 },
  { updates: { validation: { status: "active", detail: "Verifying file…" } }, ms: 800 },
  { updates: { validation: { status: "done", detail: "✓ Valid — 2.4 KB, readable" } }, ms: 3000 },
  // reset
  {
    updates: {
      supervisor: { status: "idle" }, req_analyzer: { status: "idle" },
      planning: { status: "idle" }, doc_agent: { status: "idle" },
      validation: { status: "idle" },
    }, ms: 400,
  },
];

function buildInitialAgents(mode: BackendMode): Agent[] {
  return [
    { id: "supervisor",    name: "Supervisor",            layer: "orchestration", color: COLOR.navy,      status: "idle" },
    { id: "req_analyzer",  name: "Requirement Analyzer",  layer: "reasoning",     color: COLOR.teal,      status: "idle" },
    { id: "planning",      name: "Planning Agent",         layer: "reasoning",     color: COLOR.amber,     status: "idle" },
    { id: "doc_agent",     name: "Document Agent",         layer: "execution",     color: COLOR.slateBlue, status: "idle" },
    { id: "browser_agent", name: "Browser Agent",          layer: "execution",     color: COLOR.slateBlue, status: mode === "ollama" ? "unavailable" : "idle" },
    { id: "desktop_agent", name: "Desktop Agent",          layer: "execution",     color: COLOR.slateBlue, status: "idle" },
    { id: "validation",    name: "Validation Agent",       layer: "reasoning",     color: COLOR.teal,      status: "idle" },
  ];
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function StatusIcon({ status }: { status: AgentStatus }) {
  const base: React.CSSProperties = {
    fontFamily: "var(--dp-font-mono)",
    fontSize: 12,
    fontWeight: 600,
    width: 20,
    textAlign: "center",
    flexShrink: 0,
  };
  if (status === "done")        return <span style={{ ...base, color: "#5AC994" }}>✓</span>;
  if (status === "failed")      return <span style={{ ...base, color: COLOR.redMuted }}>✗</span>;
  if (status === "active")      return <span style={{ ...base, color: COLOR.amber, animation: "dp-spin 1.2s linear infinite" }}>⟳</span>;
  if (status === "retrying")    return <span style={{ ...base, color: COLOR.amber }}>↺</span>;
  if (status === "unavailable") return <span style={{ ...base, color: COLOR.sidebarDim }}>⊘</span>;
  return <span style={{ ...base, color: COLOR.sidebarDim }}>·</span>;
}

function NodeDot({ color, status }: { color: string; status: AgentStatus }) {
  const isActive = status === "active" || status === "retrying";
  const isDone = status === "done";
  const isFailed = status === "failed";
  const isUnavail = status === "unavailable";

  const pulseRgb =
    color === COLOR.amber      ? "201,137,26"
    : color === COLOR.teal     ? "46,125,107"
    : color === COLOR.navy     ? "31,58,95"
    : "62,107,138";

  return (
    <div style={{
      width: 10, height: 10, borderRadius: "50%", flexShrink: 0, marginTop: 2,
      background:
        isActive  ? color :
        isDone    ? color :
        isFailed  ? "transparent" :
        isUnavail ? "transparent" : "transparent",
      border:
        isActive  ? `2px solid ${color}` :
        isDone    ? `2px solid ${color}` :
        isFailed  ? `2px solid ${COLOR.redMuted}` :
        isUnavail ? `2px solid ${COLOR.sidebarDim}` :
                    `2px solid ${color}44`,
      opacity: isUnavail ? 0.45 : 1,
      animation: isActive
        ? `dp-pulse 1.5s ease-in-out infinite`
        : "none",
      ["--dp-pulse-color" as string]: `rgba(${pulseRgb}, 0.55)`,
      transition: "all 0.25s ease",
    }} />
  );
}

interface AgentRowProps {
  agent: Agent;
  isLast: boolean;
  showConnector: boolean;
  rowRef?: React.Ref<HTMLDivElement>;
}

function AgentRow({ agent, isLast, showConnector, rowRef }: AgentRowProps) {
  const [expanded, setExpanded] = useState(false);
  const isUnavail = agent.status === "unavailable";
  const isDone    = agent.status === "done";
  const isFailed  = agent.status === "failed";
  const isActive  = agent.status === "active" || agent.status === "retrying";

  const rowBg =
    isActive  ? `${agent.color}18` :
    isDone    ? `${agent.color}0F` :
    isFailed  ? `${COLOR.redMuted}15` :
    "transparent";

  const borderLeft =
    isActive  ? `3px solid ${agent.color}` :
    isDone    ? `3px solid ${agent.color}88` :
    isFailed  ? `3px solid ${COLOR.redMuted}` :
    isUnavail ? `3px solid ${COLOR.sidebarDim}44` :
                `3px solid ${agent.color}22`;

  return (
    <div ref={rowRef} style={{ position: "relative" }}>
      {/* Vertical connector line to next node */}
      {showConnector && (
        <div style={{
          position: "absolute", left: 23, top: 44, width: 1, height: "calc(100% - 8px)",
          background: `${agent.color}33`, zIndex: 0,
        }} />
      )}

      <div
        onClick={() => agent.detail && setExpanded(e => !e)}
        style={{
          display: "flex", alignItems: "flex-start", gap: 10,
          padding: "10px 16px 10px 20px",
          cursor: agent.detail ? "pointer" : "default",
          borderLeft, borderRadius: 6,
          background: rowBg,
          opacity: isUnavail ? 0.55 : 1,
          transition: "background 0.3s ease, border-left 0.3s ease, opacity 0.3s ease",
          position: "relative", zIndex: 1,
        }}
      >
        <NodeDot color={agent.color} status={agent.status} />

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
          }}>
            <span style={{
              fontFamily: "var(--dp-font-ui)", fontSize: 13, fontWeight: 500,
              color: isUnavail ? COLOR.sidebarDim : COLOR.sidebarText,
              letterSpacing: 0.1,
            }}>
              {agent.name}
              {isUnavail && (
                <span style={{
                  marginLeft: 8, fontSize: 10, fontWeight: 400,
                  color: COLOR.sidebarDim, fontFamily: "var(--dp-font-mono)",
                  background: `${COLOR.sidebarDim}22`, padding: "1px 6px", borderRadius: 3,
                }}>
                  offline
                </span>
              )}
            </span>
            <StatusIcon status={agent.status} />
          </div>

          {/* Detail text — mono, shows on active/done/failed or when expanded */}
          {agent.detail && (isActive || isDone || isFailed || expanded) && (
            <div style={{
              fontFamily: "var(--dp-font-mono)", fontSize: 11,
              color: isFailed ? `${COLOR.redMuted}CC` : `${COLOR.sidebarText}88`,
              marginTop: 3, letterSpacing: 0.1,
              overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
            }}>
              {agent.detail}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Retry Arc SVG ──────────────────────────────────────────────────────────────

function RetryArc({ active, fromY, toY }: { active: boolean; fromY: number; toY: number }) {
  if (!active) return null;
  const x = 14;   // left edge x of the panel
  const curveX = -28;  // control point x (outside panel)
  const midY = (fromY + toY) / 2;

  const d = `M ${x},${fromY} C ${curveX},${fromY - 30} ${curveX},${toY + 30} ${x},${toY}`;
  const pathLen = 260;

  return (
    <svg
      style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none", overflow: "visible" }}
    >
      <defs>
        <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
          <path d="M 0,0 L 6,3 L 0,6 Z" fill={COLOR.amber} />
        </marker>
      </defs>
      {/* Glow track */}
      <path d={d} fill="none" stroke={`${COLOR.amber}33`} strokeWidth={3} strokeLinecap="round" />
      {/* Animated draw */}
      <path
        d={d} fill="none" stroke={COLOR.amber} strokeWidth={2} strokeLinecap="round"
        markerEnd="url(#arrowhead)"
        strokeDasharray={pathLen} strokeDashoffset={pathLen}
        style={{ animation: `dp-retry-draw 1.2s cubic-bezier(0.4,0,0.2,1) forwards` }}
      />
    </svg>
  );
}

// ── Main Component ─────────────────────────────────────────────────────────────

export function AgentTracePanel() {
  const [mode, setMode] = useState<BackendMode>("groq");
  const [agents, setAgents] = useState<Agent[]>(() => buildInitialAgents("groq"));
  const [retryActive, setRetryActive] = useState(false);
  const [simRunning, setSim] = useState(false);
  const [step, setStep] = useState(0);

  // Node refs for retry arc positioning
  const planningRef = useRef<HTMLDivElement>(null);
  const validationRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const [arcCoords, setArcCoords] = useState({ fromY: 0, toY: 0 });

  // Reset agents when mode changes
  useEffect(() => {
    setAgents(buildInitialAgents(mode));
    setRetryActive(false);
    setSim(false);
    setStep(0);
  }, [mode]);

  // Compute retry arc coordinates
  useEffect(() => {
    if (retryActive && planningRef.current && validationRef.current && panelRef.current) {
      const panelRect = panelRef.current.getBoundingClientRect();
      const planRect  = planningRef.current.getBoundingClientRect();
      const valRect   = validationRef.current.getBoundingClientRect();
      setArcCoords({
        fromY: valRect.top  + valRect.height / 2 - panelRect.top,
        toY:   planRect.top + planRect.height / 2 - panelRect.top,
      });
    }
  }, [retryActive]);

  // Simulation stepper
  useEffect(() => {
    if (!simRunning) return;
    if (step >= SIM.length) { setSim(false); setStep(0); return; }

    const current = SIM[step];
    const timer = setTimeout(() => {
      setAgents(prev =>
        prev.map(a =>
          current.updates[a.id]
            ? { ...a, status: current.updates[a.id]!.status, detail: current.updates[a.id]!.detail ?? a.detail }
            : a
        )
      );
      setRetryActive(!!current.retryActive);
      setStep(s => s + 1);
    }, current.ms);

    return () => clearTimeout(timer);
  }, [simRunning, step]);

  const startSim = useCallback(() => {
    setAgents(buildInitialAgents(mode));
    setRetryActive(false);
    setStep(0);
    setSim(true);
  }, [mode]);

  // Split agents: main flow vs unavailable
  const mainAgents = agents.filter(a => a.id !== "browser_agent" && a.id !== "desktop_agent");
  const sideAgents = agents.filter(a => a.id === "browser_agent" || a.id === "desktop_agent");

  const activeCount = agents.filter(a => a.status === "active" || a.status === "retrying").length;
  const doneCount   = agents.filter(a => a.status === "done").length;

  return (
    <div style={{
      minHeight: "100vh", background: COLOR.bg,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontFamily: "var(--dp-font-ui)", padding: "32px 24px",
    }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 20, width: "100%", maxWidth: 420 }}>

        {/* Controls row */}
        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: COLOR.navy, flex: 1 }}>
            Agent Trace Panel — Isolated
          </span>
          {/* Mode toggle */}
          <div style={{
            display: "flex", borderRadius: 6, overflow: "hidden",
            border: `1px solid ${COLOR.border}44`, fontSize: 12,
          }}>
            {(["groq", "ollama"] as BackendMode[]).map(m => (
              <button key={m} onClick={() => setMode(m)} style={{
                padding: "5px 14px", border: "none", cursor: "pointer",
                fontFamily: "var(--dp-font-ui)", fontSize: 12, fontWeight: 500,
                background: mode === m ? COLOR.navy : "white",
                color: mode === m ? "white" : COLOR.sidebarDim,
                transition: "all 0.15s",
              }}>
                {m === "groq" ? "☁ Cloud" : "⊙ Local"}
              </button>
            ))}
          </div>
          <button onClick={startSim} disabled={simRunning} style={{
            padding: "5px 16px", borderRadius: 6, border: "none", cursor: simRunning ? "default" : "pointer",
            background: simRunning ? COLOR.sidebarDim : COLOR.amber,
            color: "white", fontFamily: "var(--dp-font-ui)", fontSize: 12, fontWeight: 600,
            opacity: simRunning ? 0.6 : 1, transition: "all 0.15s",
          }}>
            {simRunning ? "Running…" : "▶ Play Demo"}
          </button>
        </div>

        {/* Panel */}
        <div ref={panelRef} style={{
          background: COLOR.sidebarBg, borderRadius: 12,
          border: `1px solid ${COLOR.border}`,
          boxShadow: "0 4px 24px rgba(0,0,0,0.18)",
          overflow: "hidden", position: "relative",
        }}>
          {/* Panel header */}
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            padding: "14px 20px 12px",
            borderBottom: `1px solid ${COLOR.border}`,
            background: `${COLOR.navy}99`,
          }}>
            <span style={{
              fontFamily: "var(--dp-font-mono)", fontSize: 11, fontWeight: 600,
              letterSpacing: 1.2, textTransform: "uppercase", color: COLOR.sidebarDim,
            }}>
              Agent Trace
            </span>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              {activeCount > 0 && (
                <span style={{
                  fontFamily: "var(--dp-font-mono)", fontSize: 10,
                  color: COLOR.amber, background: `${COLOR.amber}22`,
                  padding: "2px 8px", borderRadius: 10,
                  border: `1px solid ${COLOR.amber}44`,
                }}>
                  {activeCount} running
                </span>
              )}
              {doneCount > 0 && activeCount === 0 && (
                <span style={{
                  fontFamily: "var(--dp-font-mono)", fontSize: 10,
                  color: "#5AC994", background: "#5AC99422",
                  padding: "2px 8px", borderRadius: 10,
                  border: "1px solid #5AC99444",
                }}>
                  {doneCount}/{mainAgents.length + sideAgents.filter(a => a.status !== "unavailable").length} done
                </span>
              )}
            </div>
          </div>

          {/* Retry arc overlay (positioned relative to panel) */}
          <RetryArc active={retryActive} fromY={arcCoords.fromY - 48} toY={arcCoords.toY - 48} />

          {/* Main flow agents */}
          <div style={{ padding: "10px 0 6px" }}>
            {mainAgents.map((agent, i) => (
              <AgentRow
                key={agent.id}
                agent={agent}
                isLast={i === mainAgents.length - 1}
                showConnector={i < mainAgents.length - 1}
                rowRef={
                  agent.id === "planning"   ? planningRef :
                  agent.id === "validation" ? validationRef :
                  undefined
                }
              />
            ))}
          </div>

          {/* Separator */}
          <div style={{
            margin: "4px 20px",
            borderTop: `1px dashed ${COLOR.border}`,
            display: "flex", alignItems: "center", gap: 8,
          }}>
            <span style={{
              fontFamily: "var(--dp-font-mono)", fontSize: 10,
              color: COLOR.sidebarDim, padding: "4px 0",
              letterSpacing: 0.5,
            }}>
              {mode === "ollama" ? "offline — restricted" : "online"}
            </span>
          </div>

          {/* Side agents */}
          <div style={{ padding: "4px 0 12px" }}>
            {sideAgents.map((agent, i) => (
              <AgentRow
                key={agent.id}
                agent={agent}
                isLast={i === sideAgents.length - 1}
                showConnector={false}
              />
            ))}
          </div>
        </div>

        {/* Legend */}
        <div style={{
          display: "flex", gap: 16, flexWrap: "wrap",
          padding: "12px 16px", background: "white",
          borderRadius: 8, border: `1px solid ${COLOR.panel}`,
        }}>
          {[
            { label: "Idle",        color: COLOR.slateBlue, style: "outline" },
            { label: "Active",      color: COLOR.amber,     style: "filled" },
            { label: "Done",        color: COLOR.teal,      style: "filled" },
            { label: "Failed",      color: COLOR.redMuted,  style: "outline" },
            { label: "Unavailable", color: "#888",          style: "outline" },
          ].map(({ label, color, style }) => (
            <div key={label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{
                width: 9, height: 9, borderRadius: "50%", flexShrink: 0,
                background: style === "filled" ? color : "transparent",
                border: `2px solid ${color}`,
                opacity: label === "Unavailable" ? 0.55 : 1,
              }} />
              <span style={{ fontSize: 11, color: COLOR.sidebarDim, fontFamily: "var(--dp-font-mono)" }}>
                {label}
              </span>
            </div>
          ))}
        </div>

        <p style={{ margin: 0, fontSize: 11, color: COLOR.sidebarDim, fontFamily: "var(--dp-font-mono)", textAlign: "center" }}>
          Click "▶ Play Demo" to see the full execution flow, including the cyclic retry-loop animation.
        </p>
      </div>

      {/* Spin keyframe via style tag */}
      <style>{`
        @keyframes dp-spin {
          from { display: inline-block; transform: rotate(0deg); }
          to   { display: inline-block; transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
