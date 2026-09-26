import { loadConfig } from "./config.ts";
import type { Env } from "./config.ts";
import type { FetchLike } from "./core.ts";
import { XTALK_PATH, coreCall } from "./core.ts";
import { XTalkPluginRefusal } from "./refusals.ts";

export const RESULT_SCHEMA = "cosmos-xtalk-plugin-result/1";
export type ToolContext = { env: Env; fetchImpl?: FetchLike };

export type JsonSchema = {
  type: "object";
  properties: Record<string, { type: string; description: string; default?: unknown }>;
  required?: string[];
  additionalProperties: false;
};

export type ToolDef = {
  name: string;
  id: string;
  description: string;
  inputSchema: JsonSchema;
  run: (args: Record<string, unknown>, ctx: ToolContext) => Promise<Record<string, unknown>>;
};

function str(args: Record<string, unknown>, key: string): string | undefined {
  const v = args[key];
  return typeof v === "string" && v.trim() !== "" ? v.trim() : undefined;
}

export const XTALK_TOOLS: ToolDef[] = [
  {
    name: "xtalk.get",
    id: "xtalk_get",
    description:
      "GET /api/v1/xtalk — peek the agent stream (never mkdir, never consumes a cursor).",
    inputSchema: {
      type: "object",
      properties: {
        role: { type: "string", description: "Inbox filter (to == role)." },
        bind: { type: "string", description: "local (default) or openwork (read-only)." },
        verify: { type: "string", description: "1 to walk the hash chain.", default: "1" },
      },
      additionalProperties: false,
    },
    async run(args, ctx) {
      const cfg = loadConfig(ctx.env);
      const q = new URLSearchParams();
      q.set("tail", "80");
      q.set("verify", str(args, "verify") || "1");
      const role = str(args, "role");
      const bind = str(args, "bind");
      if (role) q.set("role", role);
      if (bind) q.set("bind", bind);
      const rec = await coreCall(cfg, `${XTALK_PATH}?${q.toString()}`, {}, ctx.fetchImpl);
      return rec.body;
    },
  },
  {
    name: "xtalk.send",
    id: "xtalk_send",
    description:
      "POST /api/v1/xtalk — Transport B append. Transport A is NOT_COMPOSED (no fake inject).",
    inputSchema: {
      type: "object",
      properties: {
        to: { type: "string", description: "Target role (must be a live owner for B)." },
        body: { type: "string", description: "Message text." },
        from: { type: "string", description: "Sender id.", default: "plugin" },
      },
      required: ["to", "body"],
      additionalProperties: false,
    },
    async run(args, ctx) {
      const cfg = loadConfig(ctx.env);
      const to = str(args, "to");
      const body = str(args, "body");
      if (!to || !body) throw new XTalkPluginRefusal("BAD_ARGS", "to and body required");
      const rec = await coreCall(
        cfg,
        XTALK_PATH,
        { method: "POST", body: { to, body, from: str(args, "from") || "plugin" } },
        ctx.fetchImpl,
      );
      return rec.body;
    },
  },
  {
    name: "xtalk.roles",
    id: "xtalk_roles",
    description: "Fence projection from GET /api/v1/xtalk (no session ids).",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
    async run(_args, ctx) {
      const cfg = loadConfig(ctx.env);
      const rec = await coreCall(cfg, `${XTALK_PATH}?tail=1`, {}, ctx.fetchImpl);
      return { kind: rec.body.kind, roles: rec.body.roles, bind: rec.body.bind };
    },
  },
];

export async function runTool(
  name: string,
  args: Record<string, unknown>,
  ctx: ToolContext,
): Promise<Record<string, unknown>> {
  const tool = XTALK_TOOLS.find((t) => t.name === name || t.id === name);
  if (!tool) {
    return {
      schema: RESULT_SCHEMA,
      tool: name,
      ok: false,
      kind: "BAD_ARGS",
      gate: { detail: `unknown tool ${name}` },
    };
  }
  try {
    const gate = await tool.run(args || {}, ctx);
    return {
      schema: RESULT_SCHEMA,
      tool: tool.name,
      ok: true,
      kind: String(gate.kind || "OK"),
      gate,
    };
  } catch (e) {
    const kind = e instanceof XTalkPluginRefusal ? e.kind : "UNMEASURED";
    return {
      schema: RESULT_SCHEMA,
      tool: tool.name,
      ok: false,
      kind: String(kind),
      gate: { detail: (e as Error).message },
    };
  }
}

export function mcpListTools() {
  return XTALK_TOOLS.map((t) => ({
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
