import React, { useMemo, useState } from "react";
import { MessageSquare, MoreVertical, Plus, Trash2 } from "lucide-react";
import { C } from "../theme";

export interface SessionItem {
  id: string;
  title: string;
  created_at?: string;
  updated_at?: string;
}

interface SidebarProps {
  sessions: SessionItem[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onDeleteSession: (id: string) => void;
}

export function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
}: SidebarProps) {
  const [menuOpenId, setMenuOpenId] = useState<string | null>(null);

  const { today, yesterday, older } = useMemo(() => {
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterdayStart = new Date(todayStart);
    yesterdayStart.setDate(yesterdayStart.getDate() - 1);

    const grouped = {
      today: [] as SessionItem[],
      yesterday: [] as SessionItem[],
      older: [] as SessionItem[],
    };

    sessions.forEach((s) => {
      const d = s.updated_at ? new Date(s.updated_at) : new Date();
      if (d >= todayStart) {
        grouped.today.push(s);
      } else if (d >= yesterdayStart) {
        grouped.yesterday.push(s);
      } else {
        grouped.older.push(s);
      }
    });

    return grouped;
  }, [sessions]);

  const renderGroup = (title: string, list: SessionItem[]) => {
    if (list.length === 0) return null;
    return (
      <div style={{ marginBottom: 18 }}>
        <div
          style={{
            fontSize: 10.5,
            fontWeight: 700,
            color: C.textSec,
            textTransform: "uppercase",
            letterSpacing: 0.8,
            marginBottom: 6,
            padding: "0 10px",
          }}
        >
          {title}
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
          {list.map((s) => (
            <div
              key={s.id}
              onClick={() => {
                setMenuOpenId(null);
                onSelectSession(s.id);
              }}
              style={{
                display: "flex",
                alignItems: "center",
                padding: "8px 10px",
                borderRadius: 7,
                cursor: "pointer",
                background:
                  activeSessionId === s.id ? `${C.navy}14` : "transparent",
                color: activeSessionId === s.id ? C.navy : C.textPrim,
                position: "relative",
                transition: "background 0.15s ease",
              }}
              onMouseLeave={() => setMenuOpenId(null)}
            >
              <MessageSquare
                size={15}
                style={{
                  marginRight: 8,
                  flexShrink: 0,
                  opacity: activeSessionId === s.id ? 1 : 0.6,
                }}
              />
              <div
                style={{
                  flex: 1,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  fontSize: 12.5,
                  fontWeight: activeSessionId === s.id ? 600 : 400,
                }}
              >
                {s.title || "New Chat"}
              </div>

              <div
                style={{ cursor: "pointer", padding: "2px 4px", opacity: 0.6 }}
                onClick={(e) => {
                  e.stopPropagation();
                  setMenuOpenId(menuOpenId === s.id ? null : s.id);
                }}
              >
                <MoreVertical size={13} />
              </div>

              {menuOpenId === s.id && (
                <div
                  style={{
                    position: "absolute",
                    right: 8,
                    top: 28,
                    background: "white",
                    border: `1px solid ${C.panelBorder}`,
                    borderRadius: 6,
                    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                    zIndex: 20,
                    minWidth: 90,
                    overflow: "hidden",
                  }}
                >
                  <div
                    onClick={(e) => {
                      e.stopPropagation();
                      setMenuOpenId(null);
                      onDeleteSession(s.id);
                    }}
                    style={{
                      padding: "7px 10px",
                      fontSize: 12,
                      color: C.redMuted,
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                      cursor: "pointer",
                      background: "white",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = `${C.redMuted}10`;
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "white";
                    }}
                  >
                    <Trash2 size={13} /> Delete
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div
      style={{
        width: 250,
        borderRight: `1px solid ${C.panelBorder}`,
        background: C.panel,
        display: "flex",
        flexDirection: "column",
        flexShrink: 0,
      }}
    >
      <div style={{ padding: "14px 14px 8px" }}>
        <button
          onClick={() => {
            setMenuOpenId(null);
            onNewChat();
          }}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 8,
            width: "100%",
            background: "white",
            border: `1px solid ${C.panelBorder}`,
            padding: "9px 14px",
            borderRadius: 7,
            color: C.navy,
            fontWeight: 600,
            fontSize: 13,
            cursor: "pointer",
            boxShadow: "0 1px 2px rgba(0,0,0,0.03)",
            transition: "all 0.15s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = C.slateBlue;
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = C.panelBorder;
          }}
        >
          <Plus size={15} /> New Chat
        </button>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "10px 10px 20px" }}>
        {sessions.length === 0 ? (
          <div
            style={{
              padding: "16px 8px",
              textAlign: "center",
              fontSize: 12,
              color: C.textSec,
            }}
          >
            No past chats
          </div>
        ) : (
          <>
            {renderGroup("Today", today)}
            {renderGroup("Yesterday", yesterday)}
            {renderGroup("Older", older)}
          </>
        )}
      </div>
    </div>
  );
}
