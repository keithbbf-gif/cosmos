// rolled-event/1 projection.
//
// PROPOSED SCHEMA — nothing in this tree emits the ROLLED feed yet. The projection
// is proven against a fixture; against a live root with no feed configured it says
// NO_SOURCE. It does not invent a timeline out of the transcript.

import { readFileSync, statSync } from "node:fs";
import { refuse } from "./refusals.ts";

export const ROLLED_SCHEMA = "rolled-event/1";

export type RolledEvent = {
  schema?: string;
  id?: string;
  seq?: number;
  t?: number;
  kind?: string;
  actor?: string;
  detail?: unknown;
};

export type TimelineEntry = {
  seq: number | null;
  t: number | null;
  kind: string;
  actor: string | null;
  detail: unknown;
};

export type TimelineResult = {
  kind: "OK";
  id: string | null;
  feed: string;
  n_events: number;
  n_skipped: number;
  entries: TimelineEntry[];
};

function parseFeed(path: string): RolledEvent[] {
  try {
    statSync(path);
  } catch (e) {
    refuse("NO_SOURCE", `${path}: ${(e as Error).message}`);
  }
  const lines = readFileSync(path, "utf8").split("\n").filter((l) => l.trim() !== "");
  const out: RolledEvent[] = [];
  for (const line of lines) {
    let rec: RolledEvent;
    try {
      rec = JSON.parse(line) as RolledEvent;
    } catch (e) {
      refuse("SCHEMA_UNKNOWN", `${path}: ${(e as Error).message}`);
    }
    if (rec.schema !== ROLLED_SCHEMA) {
      refuse("SCHEMA_UNKNOWN", `${path}: line schema is ${String(rec.schema)}`);
    }
    out.push(rec);
  }
  return out;
}

/**
 * Order by (t, seq) and filter to one session id when given. Unknown `kind`
 * values pass through untouched — the projection orders, it does not interpret.
 */
export function timeline(
  feedPath: string,
  id: string | undefined,
  limit = 100,
): TimelineResult {
  const events = parseFeed(feedPath);
  const wanted = id ? events.filter((e) => e.id === id) : events;
  if (id && wanted.length === 0) refuse("NOT_FOUND", `${id} has no ${ROLLED_SCHEMA} events`);
  const ordered = wanted.slice().sort((a, b) => {
    const dt = (a.t ?? 0) - (b.t ?? 0);
    return dt !== 0 ? dt : (a.seq ?? 0) - (b.seq ?? 0);
  });
  const kept = ordered.slice(0, Math.max(0, limit));
  return {
    kind: "OK",
    id: id ?? null,
    feed: feedPath,
    n_events: ordered.length,
    n_skipped: events.length - wanted.length,
    entries: kept.map((e) => ({
      seq: e.seq ?? null,
      t: e.t ?? null,
      kind: String(e.kind || "unknown"),
      actor: e.actor ?? null,
      detail: e.detail ?? null,
    })),
  };
}
