// Client for the one Core. Read-only: GET, never POST. The plugin is a client of
// the single authority, not a second writer.

import type { Config } from "./config.ts";
import { esc } from "./esc.ts";
import { refuse, scrub, SessionPluginRefusal } from "./refusals.ts";

export const RECENTS_PATH = "/api/v1/recents";
export const RECENTS_SCHEMA = "cdeck-recents/1";

export type FetchLike = (url: string, init?: { headers?: Record<string, string> }) => Promise<{
  status: number;
  json: () => Promise<unknown>;
  text: () => Promise<string>;
}>;

export type CoreResponse = { status: number; body: Record<string, unknown> };

function headers(cfg: Config): Record<string, string> {
  const h: Record<string, string> = { Accept: "application/json" };
  // Core lets a loopback peer skip the bearer; we still send it when configured.
  if (cfg.token) h.Authorization = `Bearer ${cfg.token}`;
  return h;
}

export async function coreGet(
  cfg: Config,
  path: string,
  query: Record<string, string> = {},
  fetchImpl: FetchLike = globalThis.fetch as unknown as FetchLike,
): Promise<CoreResponse> {
  // A non-loopback base URL without a bearer is refused before the socket opens:
  // Core would 401 it, and an unauthenticated request off the machine is a leak.
  if (!cfg.loopback && !cfg.token) {
    refuse("NO_TOKEN", `${cfg.coreUrl} is not loopback and no COSMOS_API_TOKEN is set`);
  }
  const qs = new URLSearchParams(query).toString();
  const url = `${cfg.coreUrl}${path}${qs ? `?${qs}` : ""}`;
  let res: Awaited<ReturnType<FetchLike>>;
  try {
    res = await fetchImpl(url, { headers: headers(cfg) });
  } catch (e) {
    refuse("CORE_UNREACHABLE", scrub(`${url}: ${(e as Error).message}`, [cfg.token]));
  }
  let body: unknown;
  try {
    body = await res.json();
  } catch {
    body = {};
  }
  const obj = (body && typeof body === "object" ? body : {}) as Record<string, unknown>;
  if (res.status !== 200) {
    const detail = String(obj.error || obj.detail || "no detail");
    throw new SessionPluginRefusal(`HTTP_${res.status}`, scrub(detail, [cfg.token]));
  }
  return { status: res.status, body: obj };
}

export type SessionRow = {
  id: unknown;
  date: unknown;
  stream: unknown;
  title: unknown;
};

export type ListResult = {
  kind: string;
  tree_id: unknown;
  available: boolean;
  n: number;
  /** Legal rows are omitted by Core. The plugin surfaces the count, never the row. */
  legal_omitted: unknown;
  rows: SessionRow[];
};

function rowsOf(body: Record<string, unknown>): SessionRow[] {
  const raw = (body.rows ?? body.sessions ?? []) as unknown;
  if (!Array.isArray(raw)) return [];
  return raw
    .filter((r): r is Record<string, unknown> => !!r && typeof r === "object")
    .map((r) => ({ id: r.id, date: r.date, stream: r.stream, title: r.title }));
}

export async function listSessions(
  cfg: Config,
  limit: number | undefined,
  fetchImpl?: FetchLike,
): Promise<ListResult> {
  const { body } = await coreGet(cfg, RECENTS_PATH, {}, fetchImpl);
  const kind = String(body.kind || (body.schema === RECENTS_SCHEMA ? "OK" : ""));
  if (body.schema !== RECENTS_SCHEMA && !kind) {
    // Neither the pinned schema nor a typed kind: do not guess field names.
    refuse("SCHEMA_UNKNOWN", `${RECENTS_PATH} returned ${JSON.stringify(body).slice(0, 200)}`);
  }
  const available = body.available !== false && kind !== "NO_SOURCE";
  const rows = available ? rowsOf(body) : [];
  return {
    kind: available ? "OK" : kind || "NO_SOURCE",
    tree_id: body.tree_id,
    available,
    n: rows.length,
    legal_omitted: body.n_omitted_legal ?? null,
    rows: typeof limit === "number" ? rows.slice(0, limit) : rows,
  };
}

export type OpenResult = {
  kind: string;
  id: unknown;
  opencode_id: unknown;
  title: unknown;
  text: string;
  openwork: unknown;
};

export async function openSession(
  cfg: Config,
  id: string,
  fetchImpl?: FetchLike,
): Promise<OpenResult> {
  if (!id) refuse("BAD_ARGS", "session.open requires an id");
  const { body } = await coreGet(cfg, RECENTS_PATH, { open: "1", id }, fetchImpl);
  const kind = String(body.kind || (body.ok ? "OK" : ""));
  if (body.ok !== true) {
    // Core's own kind is the refusal — LEGAL_OMITTED and NOT_FOUND both arrive here.
    throw new SessionPluginRefusal(kind || "NOT_FOUND", String(body.detail || id));
  }
  return {
    kind: kind || "OK",
    id: body.id ?? id,
    opencode_id: body.opencode_id ?? null,
    title: body.title ?? null,
    text: esc(body.text || ""),
    openwork: body.openwork ?? null,
  };
}
