import { drizzle } from "drizzle-orm/libsql";
import { createClient } from "@libsql/client";
import * as schema from "./schema";
import path from "path";

if (!process.env.DATABASE_URL) {
  throw new Error(
    "DATABASE_URL must be set (e.g., api.db)",
  );
}

// Ensure the URL uses the file: protocol for local SQLite
const dbUrl = process.env.DATABASE_URL.startsWith("file:") 
  ? process.env.DATABASE_URL 
  : `file:${process.env.DATABASE_URL}`;

const client = createClient({ url: dbUrl });
export const db = drizzle(client, { schema });

export * from "./schema";
