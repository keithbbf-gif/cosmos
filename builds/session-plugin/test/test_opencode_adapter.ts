// Focused pin: OpenWork / opencode plugin entry (tool factory).
//
//     node --experimental-strip-types builds/session-plugin/test/test_opencode_adapter.ts

import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { CosmosSessionsPlugin } from "../.opencode/plugins/cosmos_sessions.ts";
import { SESSION_TOOLS } from "../src/tools.ts";
import type { ToolResult } from "../src/tools.ts";

const TRANSCRIPTS = join(dirname(fileURLToPath(import.meta.url)), "fixtures", "transcripts");

const hooks = await CosmosSessionsPlugin({});
const expected = SESSION_TOOLS.map((t) => t.id).sort().join(",");
const listed = SESSION_TOOLS.map((t) => t.id).every((id) => hooks.tool[id] !== undefined);

const prev = process.env.COSMOS_TRANSCRIPT_DIR;
process.env.COSMOS_TRANSCRIPT_DIR = TRANSCRIPTS;
let parsed: ToolResult;
try {
  parsed = JSON.parse(await hooks.tool.session_read.execute({ id: "cow-abc" })) as ToolResult;
} finally {
  if (prev === undefined) delete process.env.COSMOS_TRANSCRIPT_DIR;
  else process.env.COSMOS_TRANSCRIPT_DIR = prev;
}

const ok =
  listed &&
  expected === "session_list,session_open,session_read,session_search,session_timeline" &&
  parsed.ok &&
  parsed.tool === "session.read";

console.log(ok ? "PASS opencode adapter discovery + call" : "FAIL opencode adapter discovery + call");
process.exitCode = ok ? 0 : 1;
