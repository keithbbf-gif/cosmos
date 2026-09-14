// Shared fixture paths and stand-in Core for per-tool pins.

import { createServer } from "node:http";
import type { Server } from "node:http";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { RECENTS_SCHEMA } from "../src/core.ts";
import { runTool } from "../src/tools.ts";

export const HERE = dirname(fileURLToPath(import.meta.url));
export const TRANSCRIPTS = join(HERE, "fixtures", "transcripts");
export const TAMPERED = join(HERE, "fixtures", "tampered");
export const ROLLED = join(HERE, "fixtures", "rolled", "cosmos.rolled.jsonl");
export const GROK = "grok-aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee";

export const fileEnv = {
  COSMOS_TRANSCRIPT_DIR: TRANSCRIPTS,
  COSMOS_ROLLED_FEED: ROLLED,
};

export async function run(name: string, args: Record<string, unknown>, env: Record<string, string>) {
  return runTool(name, args, { env });
}

export function fakeCore(): Promise<{ server: Server; url: string }> {
  const server = createServer((req, res) => {
    const url = new URL(req.url || "/", "http://127.0.0.1");
    res.setHeader("Content-Type", "application/json");
    if (url.pathname !== "/api/v1/recents") {
      res.statusCode = 404;
      return res.end(JSON.stringify({ error: "NOT_FOUND" }));
    }
    if (url.searchParams.get("open") === "1") {
      const id = url.searchParams.get("id");
      if (id === "cow-abc") {
        return res.end(JSON.stringify({
          ok: true,
          kind: "OK",
          id,
          opencode_id: "ses_cow_001",
          title: "clocks",
          text: "# clocks\n\nhello from plumbing\n",
          openwork: "focus: COSMOS 2",
        }));
      }
      if (id === "cow-leg1") {
        return res.end(JSON.stringify({ ok: false, kind: "LEGAL_OMITTED", detail: id }));
      }
      return res.end(JSON.stringify({ ok: false, kind: "NOT_FOUND", detail: id }));
    }
    res.end(JSON.stringify({
      ok: true,
      schema: RECENTS_SCHEMA,
      tree_id: "KMesh-COSMOS-live",
      available: true,
      n_shown: 2,
      n_omitted_legal: 1,
      rows: [
        { id: "cow-abc", date: "2026-09-01", stream: "plumbing", title: "clocks" },
        { id: GROK, date: "2026-09-05", stream: "cm", title: "grok tui" },
      ],
    }));
  });
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => {
      const addr = server.address();
      const port = typeof addr === "object" && addr ? addr.port : 0;
      resolve({ server, url: `http://127.0.0.1:${port}` });
    });
  });
}
