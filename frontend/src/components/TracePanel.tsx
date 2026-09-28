import React, { useEffect, useRef, useState } from "react";
import { Agent, AgentStatus } from "../hooks/use-chat-stream";
import { C } from "../theme";

function NodeDot({ color, status }: { color: string; status: AgentStatus }) {
  const active = status === "active" || status === "retrying";
  const done = status === "done";
  const failed = status === "failed";
  const unavail = status === "unavailable";
  const pulseRgb =
    color === C.amber
      ? "201,137,26"
      : color === C.teal
      ? "46,125,107"
      : color === C.navy
      ? "31,58,95"
      : "62,107,138";

  return (
    <div
      style={{
        width: 10,
        height: 10,
        borderRadius: "50%",
        flexShrink: 0,
        marginTop: 4,
        background: active || done ? color : "transparent",
        border: failed
          ? `2px solid ${C.redMuted}`
          : unavail
          ? `2px solid ${C.sidebarDim}44`
          : active || done
          ? `2px solid ${color}`
          : `2px solid ${color}44`,
        opacity: unavail ? 0.4 : 1,
        animation: active ? `dp-pulse 1.4s ease-in-out infinite` : "none",
        ["--dp-pulse-color" as string]: `rgba(${pulseRgb},0.65)`,
        transition: "all 0.25s ease",
      }}
    />
  );
}

function StatusIcon({ s }: { s: AgentStatus }) {
  const st: React.CSSProperties = {
    fontFamily: "var(--dp-font-mono)",
    fontSize: 12,
    fontWeight: 700,
    width: 20,
    textAlign: "center",
    flexShrink: 0,
  };
  if (s === "done") return <span style={{ ...st, color: "#5AC994" }}>✓</span>;
  if (s === "failed") return <span style={{ ...st, color: C.redMuted }}>✗</span>;
  if (s === "active" || s === "retrying")
    return (
      <span
        style={{
          ...st,
          color: C.amber,
          display: "inline-block",
          animation: "dp-spin 1.2s linear infinite",
        }}
      >
        ⟳
      </span>
    );
  if (s === "unavailable") return <span style={{ ...st, color: C.sidebarDim }}>⊘</span>;
  return <span style={{ ...st, color: C.sidebarDim }}>·</span>;
}

export function TracePanel({
  agents,
  retryActive,
  mode,
}: {
  agents: Agent[];
  retryActive: boolean;
  mode: string;
}) {
  const planRef = useRef<HTMLDivElement>(null);
  const valRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const [arc, setArc] = useState({ from: 0, to: 0 });

  useEffect(() => {
    if (retryActive && planRef.current && valRef.current && panelRef.current) {
      const pr = panelRef.current.getBoundingClientRect();
      const pl = planRef.current.getBoundingClientRect();
      const vl = valRef.current.getBoundingClientRect();
      setArc({
        from: vl.top + vl.height / 2 - pr.top,
        to: pl.top + pl.height / 2 - pr.top,
      });
    }
  }, [retryActive, agents]);

  const activeCount = agents.filter(
    (a) => a.status === "active" || a.status === "retrying"
  ).length;
  const doneCount = agents.filter((a) => a.status === "done").length;

  return (
    <div
      ref={panelRef}
      style={{
        position: "relative",
        height: "100%",
        width: 280,
        display: "flex",
        flexDirection: "column",
        background: C.sidebarBg,
        borderLeft: `1px solid ${C.border}`,
        overflow: "hidden",
        flexShrink: 0,
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "12px 16px",
          borderBottom: `1px solid ${C.border}`,
          background: `${C.navy}99`,
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <span
          style={{
            fontFamily: "var(--dp-font-mono)",
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: 1.2,
            textTransform: "uppercase",
            color: C.sidebarText,
          }}
        >
          Agent Trace
        </span>
        <div style={{ display: "flex", gap: 6 }}>
          {activeCount > 0 && (
            <span
              style={{
                fontFamily: "var(--dp-font-mono)",
                fontSize: 10,
                color: C.amber,
                background: `${C.amber}22`,
                padding: "2px 7px",
                borderRadius: 10,
                border: `1px solid ${C.amber}44`,
              }}
            >
              {activeCount} active
            </span>
          )}
          {doneCount > 0 && activeCount === 0 && (
            <span
              style={{
                fontFamily: "var(--dp-font-mono)",
                fontSize: 10,
                color: "#5AC994",
                background: "#5AC99422",
                padding: "2px 7px",
                borderRadius: 10,
                border: "1px solid #5AC99444",
              }}
            >
              {doneCount} done
            </span>
          )}
        </div>
      </div>

      {/* Retry SVG Arc between Validation and Planning Agent */}
      {retryActive && arc.from > 0 && (
        <svg
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            pointerEvents: "none",
            overflow: "visible",
            zIndex: 10,
          }}
        >
          <defs>
            <marker id="arrow" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
              <path d="M 0,0 L 6,3 L 0,6 Z" fill={C.amber} />
            </marker>
          </defs>
          <path
            d={`M 14,${arc.from} C -15,${arc.from - 20} -15,${arc.to + 20} 14,${arc.to}`}
            fill="none"
            stroke={`${C.amber}33`}
            strokeWidth={3}
            strokeLinecap="round"
          />
          <path
            d={`M 14,${arc.from} C -15,${arc.from - 20} -15,${arc.to + 20} 14,${arc.to}`}
            fill="none"
            stroke={C.amber}
            strokeWidth={2}
            strokeLinecap="round"
            markerEnd="url(#arrow)"
            strokeDasharray="240"
            strokeDashoffset="240"
            style={{ animation: "dp-retry-draw 1.2s cubic-bezier(0.4, 0, 0.2, 1) forwards" }}
          />
        </svg>
      )}

      {/* Agent Nodes */}
      <div style={{ flex: 1, overflowY: "auto", padding: "8px 0 16px" }}>
        {agents.map((a, i) => {
          const isActive = a.status === "active" || a.status === "retrying";
          const rowBg = isActive
            ? `${a.color}22`
            : a.status === "done"
            ? `${a.color}11`
            : a.status === "failed"
            ? `${C.redMuted}18`
            : "transparent";
          const borderLeft = isActive
            ? `3px solid ${a.color}`
            : a.status === "done"
            ? `3px solid ${a.color}88`
            : a.status === "failed"
            ? `3px solid ${C.redMuted}`
            : `3px solid ${a.color}22`;

          return (
            <div key={a.id} style={{ position: "relative" }}>
              {i < agents.length - 1 && (
                <div
                  style={{
                    position: "absolute",
                    left: 23,
                    top: 24,
                    width: 1,
                    height: "100%",
                    background: `${a.color}33`,
                    zIndex: 0,
                  }}
                />
              )}

              <div
                ref={
                  a.id === "planning_agent"
                    ? planRef
                    : a.id === "validation_agent"
                    ? valRef
                    : undefined
                }
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 10,
                  padding: "8px 14px 8px 18px",
                  borderLeft,
                  background: rowBg,
                  opacity: a.status === "unavailable" ? 0.45 : 1,
                  transition: "all 0.2s ease",
                  position: "relative",
                  zIndex: 1,
                }}
              >
                <NodeDot color={a.color} status={a.status} />

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <span
                      style={{
                        fontFamily: "var(--dp-font-ui)",
                        fontSize: 12.5,
                        fontWeight: 600,
                        color:
                          a.status === "unavailable" ? C.sidebarDim : C.sidebarText,
                      }}
                    >
                      {a.name}
                    </span>
                    <StatusIcon s={a.status} />
                  </div>

                  {a.detail && (isActive || a.status === "done" || a.status === "failed") && (
                    <div
                      style={{
                        fontFamily: "var(--dp-font-mono)",
                        fontSize: 10,
                        color:
                          a.status === "failed"
                            ? `${C.redMuted}EE`
                            : `${C.sidebarText}88`,
                        marginTop: 2,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                      title={a.detail}
                    >
                      {a.detail}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
