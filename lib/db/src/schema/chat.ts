import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";
import { sql } from "drizzle-orm";

// ── Chat Sessions ─────────────────────────────────────────────────────────────

export const chatSessionsTable = sqliteTable("chat_sessions", {
  id:        text("id").primaryKey(),
  mode:      text("mode").notNull().default("groq"),
  title:     text("title"),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull().default(sql`(strftime('%s', 'now'))`),
});

export const insertChatSessionSchema = createInsertSchema(chatSessionsTable).omit({ createdAt: true });
export type InsertChatSession = z.infer<typeof insertChatSessionSchema>;
export type ChatSession       = typeof chatSessionsTable.$inferSelect;

// ── Chat Messages ─────────────────────────────────────────────────────────────

export const chatMessagesTable = sqliteTable("chat_messages", {
  id:         text("id").primaryKey(),
  sessionId:  text("session_id").notNull().references(() => chatSessionsTable.id, { onDelete: "cascade" }),
  role:       text("role").notNull(),          // "user" | "agent"
  agentName:  text("agent_name"),
  agentColor: text("agent_color"),
  kind:       text("kind"),                    // "normal" | "clarification" | "error" | "plan"
  text:       text("text").notNull(),
  items:      text("items", { mode: "json" }).$type<string[]>(),
  createdAt:  integer("created_at", { mode: "timestamp" }).notNull().default(sql`(strftime('%s', 'now'))`),
});

export const insertChatMessageSchema = createInsertSchema(chatMessagesTable).omit({ createdAt: true });
export type InsertChatMessage = z.infer<typeof insertChatMessageSchema>;
export type ChatMessage       = typeof chatMessagesTable.$inferSelect;
