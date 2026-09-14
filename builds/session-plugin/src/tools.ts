// The tool table. One definition per surface, host-agnostic on purpose: the
// OpenWork plugin entry and the MCP adapter below are both pure re-shaping of
// this array, so neither host gets behaviour the other one lacks.

import { loadConfig, requireRolledFeed, requireTranscriptDir } from "./config.ts";
import type { Env } from "./config.ts";
import type { FetchLike } from "./core.ts";
import { listSessions, openSession } from "./core.ts";
import { scrub, SessionPluginRefusal } from "./refusals.ts";
import { timeline } from "./rolled.ts";
import { TRANSCRIPT_SCHEMA, readSession, searchSessions } from "./transcript.ts";

export const RESULT_SCHEMA = "cosmos-session-plugin-result/1";
export { TRANSCRIPT_SCHEMA };

const REFUSAL_KINDS = new Set<string>([
  "NO_SOURCE",
  "NOT_FOUND",
  "LEGAL_OMITTED",
  "LEN_MISMATCH",
  "HASH_MISMATCH",
  "SCHEMA_UNKNOWN",
  "NO_TOKEN",
  "CORE_UNREACHABLE",
  "BAD_ARGS",
  "UNMEASURED",
]);

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

function isRefusalKind(kind: string): boolean {
  return REFUSAL_KINDS.has(kind) || /^HTTP_\d{3}$/.test(kind);
}

/** Bearer material from the host env. Never logged; used only to scrub. */
function secretsOf(ctx: ToolContext): Array<string | undefined> {
  const inline = (ctx.env.COSMOS_API_TOKEN || "").trim() || undefined;
  let resolved: string | undefined;
  try {
    resolved = loadConfig(ctx.env).token;
  } catch {
    resolved = undefined;
  }
  return [inline, resolved];
}

function scrubUnknown(value: unknown, secrets: Array<string | undefined>): unknown {
  if (typeof value === "string") return scrub(value, secrets);
  if (Array.isArray(value)) return value.map((v) => scrubUnknown(v, secrets));
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      out[k] = scrubUnknown(v, secrets);
    }
    return out;
  }
  return value;
}

function envelope(
  tool: string,
  ok: boolean,
  kind: string,
  gate: Record<string, unknown>,
  legalOmitted: unknown,
  ctx?: ToolContext,
): ToolResult {
  const secrets = ctx ? secretsOf(ctx) : [];
  return {
    schema: RESULT_SCHEMA,
    tool,
    ok,
    kind,
    gate: scrubUnknown(gate, secrets) as Record<string, unknown>,
    legal_omitted: legalOmitted,
  };
}

function refuseEnvelope(
  tool: string,
  kind: string,
  detail: string,
  ctx?: ToolContext,
): ToolResult {
  return envelope(
    tool,
    false,
    kind,
    { detail },
    kind === "LEGAL_OMITTED" ? 1 : null,
    ctx,
  );
}

/**
 * Fail-closed wrap of a tool.run gate. Schema strings are exact (`===`),
 * LEGAL_OMITTED is honoured on both mechanics, and a typed refusal kind is
 * never reported as ok.
 */
function wrapGate(
  tool: string,
  gate: Record<string, unknown>,
  ctx: ToolContext,
): ToolResult {
  const kind = String(gate.kind || "OK");
  const head = gate.head && typeof gate.head === "object"
    ? gate.head as { schema?: unknown; legal?: unknown }
    : undefined;

  // File-store mechanic: head.legal is omitted here, not repaired into a row.
  if (head?.legal === true) {
    return refuseEnvelope(tool, "LEGAL_OMITTED", String(gate.id || tool), ctx);
  }

  // cosmos-transcript/1 is exact. A suffix, prefix, or v2 is SCHEMA_UNKNOWN.
  if (head && head.schema !== TRANSCRIPT_SCHEMA) {
    return refuseEnvelope(
      tool,
      "SCHEMA_UNKNOWN",
      `${String(gate.id || tool)}: head.schema is ${String(head.schema)}`,
      ctx,
    );
  }

  // Core mechanic: Core's own kind is the refusal (open LEGAL_OMITTED).
  if (kind === "LEGAL_OMITTED") {
    return envelope(tool, false, "LEGAL_OMITTED", gate, gate.legal_omitted ?? 1, ctx);
  }

  return envelope(
    tool,
    !isRefusalKind(kind),
    kind,
    gate,
    gate.legal_omitted ?? null,
    ctx,
  );
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
      // No local parse. readSession -> readVerified (len+sha, then JSON.parse).
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
      // No local parse and no unverified scan. searchSessions calls readVerified
      // per id (len+sha before JSON.parse); a failed file is refused by id.
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
 * Always returns a cosmos-session-plugin-result/1 envelope. A refusal is a
 * typed kind an agent can read, not an exception string it has to guess at.
 * Every failure path below mints a kind; nothing falls out as a throw.
 */
export async function runTool(
  name: string,
  args: Record<string, unknown>,
  ctx: ToolContext,
): Promise<ToolResult> {
  const tool = findTool(name);
  if (!tool) {
    return refuseEnvelope(name, "NOT_FOUND", `no such tool: ${name}`, ctx);
  }
  for (const req of tool.inputSchema.required || []) {
    if (args[req] === undefined || args[req] === null || args[req] === "") {
      return refuseEnvelope(tool.name, "BAD_ARGS", `${tool.name} requires ${req}`, ctx);
    }
  }
  try {
    const gate = await tool.run(args, ctx);
    return wrapGate(tool.name, gate, ctx);
  } catch (e) {
    const kind = e instanceof SessionPluginRefusal ? String(e.kind) : "UNMEASURED";
    const detail = e instanceof Error ? e.message : String(e);
    return refuseEnvelope(tool.name, kind, detail, ctx);
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
