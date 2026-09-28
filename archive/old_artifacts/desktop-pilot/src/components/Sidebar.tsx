import { useState, useMemo } from "react";
import { ChatSession } from "@workspace/api-client-react";
import { MessageSquare, Plus, Trash2, MoreVertical } from "lucide-react";
import { C } from "../theme";
import { useDeleteChatSession } from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { getListChatSessionsQueryKey } from "@workspace/api-client-react";

interface SidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
}

export function Sidebar({ sessions, activeSessionId, onSelectSession, onNewChat }: SidebarProps) {
  const qc = useQueryClient();
  const deleteSession = useDeleteChatSession();
  const [menuOpenId, setMenuOpenId] = useState<string | null>(null);

  const { today, yesterday, older } = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const grouped = {
      today: [] as ChatSession[],
      yesterday: [] as ChatSession[],
      older: [] as ChatSession[],
    };

    sessions.forEach(s => {
      const d = new Date(s.createdAt);
      if (d >= today) {
        grouped.today.push(s);
      } else if (d >= yesterday) {
        grouped.yesterday.push(s);
      } else {
        grouped.older.push(s);
      }
    });

    return grouped;
  }, [sessions]);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await deleteSession.mutateAsync({ sessionId: id });
      qc.invalidateQueries({ queryKey: getListChatSessionsQueryKey() });
      if (activeSessionId === id) {
        onNewChat();
      }
    } catch (err) {
      console.error("Failed to delete session", err);
    }
    setMenuOpenId(null);
  };

  const renderGroup = (title: string, list: ChatSession[]) => {
    if (list.length === 0) return null;
    return (
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: C.textSec, textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 8, padding: "0 12px" }}>
          {title}
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {list.map(s => (
            <div 
              key={s.id} 
              onClick={() => {
                setMenuOpenId(null);
                onSelectSession(s.id);
              }}
              style={{
                display: "flex",
                alignItems: "center",
                padding: "8px 12px",
                borderRadius: 8,
                cursor: "pointer",
                background: activeSessionId === s.id ? `${C.navy}15` : "transparent",
                color: activeSessionId === s.id ? C.navy : C.textPrim,
                position: "relative"
              }}
              onMouseLeave={() => setMenuOpenId(null)}
            >
              <MessageSquare size={16} style={{ marginRight: 10, flexShrink: 0, opacity: 0.7 }} />
              <div style={{ flex: 1, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", fontSize: 13, fontWeight: activeSessionId === s.id ? 600 : 400 }}>
                {s.title || "New Chat"}
              </div>
              
              <div 
                style={{ cursor: "pointer", padding: 4, opacity: 0.6 }}
                onClick={(e) => {
                  e.stopPropagation();
                  setMenuOpenId(menuOpenId === s.id ? null : s.id);
                }}
              >
                <MoreVertical size={14} />
              </div>

              {menuOpenId === s.id && (
                <div style={{
                  position: "absolute",
                  right: 12,
                  top: 32,
                  background: "white",
                  border: `1px solid ${C.panelBorder}`,
                  borderRadius: 6,
                  boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                  zIndex: 10,
                  display: "flex",
                  flexDirection: "column",
                  minWidth: 100,
                  overflow: "hidden"
                }}>
                  <div 
                    onClick={(e) => handleDelete(e, s.id)}
                    style={{ padding: "8px 12px", fontSize: 13, color: C.redMuted, display: "flex", alignItems: "center", gap: 8, cursor: "pointer", background: "white" }}
                  >
                    <Trash2 size={14} /> Delete
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
    <div style={{ width: 260, borderRight: `1px solid ${C.panelBorder}`, background: C.panel, display: "flex", flexDirection: "column", flexShrink: 0 }}>
      <div style={{ padding: 16 }}>
        <button
          onClick={() => {
            setMenuOpenId(null);
            onNewChat();
          }}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            width: "100%",
            background: "white",
            border: `1px solid ${C.panelBorder}`,
            padding: "10px 16px",
            borderRadius: 8,
            color: C.navy,
            fontWeight: 600,
            fontSize: 13,
            cursor: "pointer",
            boxShadow: "0 1px 2px rgba(0,0,0,0.03)"
          }}
        >
          <Plus size={16} /> New Chat
        </button>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "8px 8px 24px" }}>
        {renderGroup("Today", today)}
        {renderGroup("Yesterday", yesterday)}
        {renderGroup("Older", older)}
      </div>
    </div>
  );
}
