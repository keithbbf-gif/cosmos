// Focused pin: MCP adapter (JSON-RPC tools/list + tools/call).
//
//     node --experimental-strip-types builds/session-plugin/test/test_mcp_adapter.ts

import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { mcpHandleRequest } from "../src/mcp.ts";
import type { ToolResult } from "../src/tools.ts";

const TRANSCRIPTS = join(dirname(fileURLToPath(import.meta.url)), "fixtures", "transcripts");
const ctx = { env: { COSMOS_TRANSCRIPT_DIR: TRANSCRIPTS } };

const list = await mcpHandleRequest({ jsonrpc: "2.0", id: 1, method: "tools/list" }, ctx);
const tools = (list?.result as { tools: unknown[] })?.tools ?? [];
const call = await mcpHandleRequest({
  jsonrpc: "2.0",
  id: 2,
  method: "tools/call",
  params: { name: "session_read", arguments: { id: "cow-abc" } },
}, ctx);
const body = (call?.result as { content: Array<{ text: string }>; isError: boolean }) ?? {};
const parsed = JSON.parse(body.content?.[0]?.text ?? "{}") as ToolResult;

const ok =
  list?.jsonrpc === "2.0" &&
  tools.length === 5 &&
  call?.jsonrpc === "2.0" &&
  body.isError === false &&
  parsed.ok &&
  parsed.tool === "session.read";

console.log(ok ? "PASS mcp adapter discovery + call" : "FAIL mcp adapter discovery + call");
process.exitCode = ok ? 0 : 1;
