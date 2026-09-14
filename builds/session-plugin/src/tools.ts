// The tool table. One definition per surface, host-agnostic on purpose: the
// OpenWork plugin entry and the MCP adapter below are both pure re-shaping of
// this array, so neither host gets behaviour the other one lacks.

import { loadConfig, requireRolledFeed, requireTranscriptDir } from "./config.ts";
import type { Env } from "./config.ts";
import type { FetchLike } from "./core.ts";
import { listSessions, openSession } from "./core.ts";
import { SessionPluginRefusal } from "./refusals.ts";
import { timeline } from "./rolled.ts";
import { readSession, searchSessions } from "./transcript.ts";

export const RESULT_SCHEMA = "cosmos-session-plugin-result/1";

export type ToolContext = { env: Env; fetchImpl?: FetchLike };

export type JsonSchema = {
  type: "object";
  properties: Record<string, { type: string; description: string; default?: unknown }>;
  required?: string[];
  additionalProperties: false;
};

export type ToolDef = {
  /** Canonical, dotted. The name the product is specified with. */
  name: string;
  /** Host-safe alias for hosts that reject "." in a tool name. */
  id: string;
  description: string;
  inputSchema: JsonSchema;
  run: (args: Record<string, unknown>, ctx: ToolContext) => Promise<Record<string, unknown>>;
};

export type ToolResult = {
  schema: typeof RESULT_SCHEMA;
  tool: string;
  ok: boolean;
  kind: string;
  gate: Record<string, unknown>;
  legal_omitted: unknown;
};

function str(args: Record<string, unknown>, key: string): string | undefined {
  const v = args[key];
  return typeof v === "string" && v.trim() !== "" ? v.trim() : undefined;
}

function num(args: Record<string, unknown>, key: string, fallback: number): number {
  const v = args[key];
  const n = typeof v === "number" ? v : Number(v);
  return Number.isFinite(n) && n >= 0 ? Math.floor(n) : fallback;
}

export const SESSION_TOOLS: ToolDef[] = [
  {
    name: "session.list",
    id: "session_list",
    description:
      "List recent AI sessions from COSMOS Core (GET /api/v1/recents). Legal rows are " +
      "omitted upstream; the omitted count is reported.",
    inputSchema: {
      type: "object",
      properties: {
        limit: { type: "integer", description: "Max rows to return.", default: 20 },
      },
      additionalProperties: false,
    },
    async run(args, ctx) {
      const cfg = loadConfig(ctx.env);
      const rec = await listSessions(cfg, num(args, "limit", 20), ctx.fetchImpl);
      return { ...rec, core: cfg.coreUrl };
    },
  },
  {
    name: "session.open",
    id: "session_open",
    description:
      "Open one session by id (GET /api/v1/recents?open=1&id=). Returns the transcript " +
      "text plus the OpenWork focus target.",
    inputSchema: {
      type: "object",
      properties: {
        id: { type: "string", description: "Session id, e.g. cow-abc." },
      },
      required: ["id"],
      additionalProperties: false,
    },
    async run(args, ctx) {
      const cfg = loadConfig(ctx.env);
      const rec = await openSession(cfg, str(args, "id") || "", ctx.fetchImpl);
      return { ...rec, core: cfg.coreUrl };
    },
  },
  {
    name: "session.read",
    id: "session_read",
    description:
      "Read a canonical cosmos-transcript/1 session from the transcript store. The " +
      "declared length and sha are verified before the bytes are parsed.",
    inputSchema: {
      type: "object",
      properties: {
        id: { type: "string", description: "Transcript id (file stem of {id}.ctr.jsonl)." },
        offset: { type: "integer", description: "First turn index to return.", default: 0 },
        limit: { type: "integer", description: "Max turns to return.", default: 50 },
      },
      required: ["id"],
      additionalProperties: false,
    },
    async run(args, ctx) {
      const dir = requireTranscriptDir(loadConfig(ctx.env));
      return readSession(dir, str(args, "id") || "", num(args, "offset", 0), num(args, "limit", 50));
    },
  },
  {
    name: "session.search",
    id: "session_search",
    description:
      "Search turn text across verified cosmos-transcript/1 files. Legal transcripts are " +
      "skipped and counted; a transcript that fails verification is refused by id, not read.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Case-insensitive substring to find." },
        limit: { type: "integer", description: "Max hits to return.", default: 20 },
        ids: { type: "array", description: "Restrict the scan to these transcript ids." },
      },
      required: ["query"],
      additionalProperties: false,
    },
    async run(args, ctx) {
      const dir = requireTranscriptDir(loadConfig(ctx.env));
      const ids = Array.isArray(args.ids) ? (args.ids as unknown[]).map(String) : undefined;
      return searchSessions(dir, str(args, "query") || "", num(args, "limit", 20), ids);
    },
  },
  {
    name: "session.timeline",
    id: "session_timeline",
    description:
      "Project the ROLLED rolled-event/1 feed into an ordered timeline. The feed is not " +
      "emitted by Core yet, so this returns NO_SOURCE until COSMOS_ROLLED_FEED points at one.",
    inputSchema: {
      type: "object",
      properties: {
        id: { type: "string", description: "Session id to filter to. Omit for the whole feed." },
        limit: { type: "integer", description: "Max entries to return.", default: 100 },
      },
      additionalProperties: false,
    },
    async run(args, ctx) {
      const feed = requireRolledFeed(loadConfig(ctx.env));
      return timeline(feed, str(args, "id"), num(args, "limit", 100));
    },
  },
];

export function findTool(name: string): ToolDef | undefined {
  return SESSION_TOOLS.find((t) => t.name === name || t.id === name);
}

/**
 * Always returns an envelope. A refusal is a typed result an agent can read, not
 * an exception string it has to guess at.
 */
export async function runTool(
  name: string,
  args: Record<string, unknown>,
  ctx: ToolContext,
): Promise<ToolResult> {
  const tool = findTool(name);
  if (!tool) {
    return {
      schema: RESULT_SCHEMA,
      tool: name,
      ok: false,
      kind: "NOT_FOUND",
      gate: { detail: `no such tool: ${name}` },
      legal_omitted: null,
    };
  }
  for (const req of tool.inputSchema.required || []) {
    if (args[req] === undefined || args[req] === null || args[req] === "") {
      return {
        schema: RESULT_SCHEMA,
        tool: tool.name,
        ok: false,
        kind: "BAD_ARGS",
        gate: { detail: `${tool.name} requires ${req}` },
        legal_omitted: null,
      };
    }
  }
  try {
    const gate = await tool.run(args, ctx);
    return {
      schema: RESULT_SCHEMA,
      tool: tool.name,
      ok: true,
      kind: String(gate.kind || "OK"),
      gate,
      legal_omitted: gate.legal_omitted ?? null,
    };
  } catch (e) {
    const kind = e instanceof SessionPluginRefusal ? e.kind : "UNMEASURED";
    return {
      schema: RESULT_SCHEMA,
      tool: tool.name,
      ok: false,
      kind: String(kind),
      gate: { detail: (e as Error).message },
      legal_omitted: kind === "LEGAL_OMITTED" ? 1 : null,
    };
  }
}

// ---- MCP adapter: tools/list + tools/call, for any host that is not OpenWork ----

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
