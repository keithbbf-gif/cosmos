// MCP adapter — JSON-RPC 2.0 tools/list + tools/call. Adapter only; every
// behaviour lives in tools.ts (runTool + SESSION_TOOLS).

import { runTool, SESSION_TOOLS } from "./tools.ts";
import type { JsonSchema, ToolContext } from "./tools.ts";

export const MCP_PROTOCOL = "2024-11-05";

export function mcpListTools(): Array<{
  name: string;
  description: string;
  inputSchema: JsonSchema;
}> {
  return SESSION_TOOLS.map((t) => ({
    name: t.id,
    description: t.description,
    inputSchema: t.inputSchema,
  }));
}

export async function mcpCallTool(
  name: string,
  args: Record<string, unknown>,
  ctx: ToolContext,
): Promise<{ content: Array<{ type: "text"; text: string }>; isError: boolean }> {
  const rec = await runTool(name, args, ctx);
  return {
    content: [{ type: "text", text: JSON.stringify(rec, null, 2) }],
    isError: !rec.ok,
  };
}

type JsonRpcRequest = {
  jsonrpc?: string;
  id?: unknown;
  method?: string;
  params?: Record<string, unknown>;
};

function rpcError(id: unknown, code: number, message: string): Record<string, unknown> {
  return { jsonrpc: "2.0", id: id ?? null, error: { code, message } };
}

function rpcResult(id: unknown, result: unknown): Record<string, unknown> {
  return { jsonrpc: "2.0", id, result };
}

/** One parsed JSON-RPC request → one response object, or null for notifications. */
export async function mcpHandleRequest(
  req: JsonRpcRequest,
  ctx: ToolContext,
): Promise<Record<string, unknown> | null> {
  const rid = req.id;
  const method = req.method;

  if (method === "notifications/initialized" || method === "initialized") {
    return null;
  }

  try {
    if (method === "initialize") {
      return rpcResult(rid, {
        protocolVersion: MCP_PROTOCOL,
        capabilities: { tools: {} },
        serverInfo: { name: "cosmos-sessions", version: "1" },
      });
    }
    if (method === "tools/list") {
      return rpcResult(rid, { tools: mcpListTools() });
    }
    if (method === "tools/call") {
      const p = req.params || {};
      const name = typeof p.name === "string" ? p.name : "";
      const raw = p.arguments;
      const args =
        raw && typeof raw === "object" && !Array.isArray(raw)
          ? (raw as Record<string, unknown>)
          : {};
      const out = await mcpCallTool(name, args, ctx);
      return rpcResult(rid, out);
    }
    return rpcError(rid, -32601, `method not found: ${method}`);
  } catch (e) {
    return rpcError(rid, -32603, `${(e as Error).name}: ${(e as Error).message}`);
  }
}

/** One JSON-RPC line (stdio transport) → one response line, or null. */
export async function mcpHandleLine(line: string, ctx: ToolContext): Promise<string | null> {
  let req: JsonRpcRequest;
  try {
    req = JSON.parse(line) as JsonRpcRequest;
  } catch {
    return JSON.stringify(rpcError(null, -32700, "parse error"));
  }
  const resp = await mcpHandleRequest(req, ctx);
  return resp === null ? null : JSON.stringify(resp);
}
