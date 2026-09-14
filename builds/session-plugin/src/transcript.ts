// cosmos-transcript/1 reader. The sidecar is checked BEFORE the bytes are parsed:
// a transcript that disagrees with its declaration is refused, never repaired and
// never half-read. Same fail-closed contract as cosmos_validate.read_verified.

import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { esc } from "./esc.ts";
import { refuse } from "./refusals.ts";

export const TRANSCRIPT_SCHEMA = "cosmos-transcript/1";
export const DECL_SCHEMA = "cosmos-transcript-decl/1";
const JSONL_SUFFIX = ".ctr.jsonl";
const DECL_SUFFIX = ".ctr.decl.json";

export type TranscriptHead = {
  schema?: string;
  id?: string;
  family?: string;
  title?: string;
  stream?: string;
  legal?: boolean;
  n_turns?: number;
  aliases?: Record<string, unknown>;
  [k: string]: unknown;
};

export type Turn = {
  seq?: number;
  role?: string;
  text?: string | null;
  [k: string]: unknown;
};

export type Transcript = {
  id: string;
  head: TranscriptHead;
  turns: Turn[];
  sha: string;
  len: number;
};

function sha256(data: Buffer): string {
  return createHash("sha256").update(data).digest("hex");
}

export function listIds(dir: string): string[] {
  let names: string[];
  try {
    names = readdirSync(dir);
  } catch (e) {
    refuse("NO_SOURCE", `${dir}: ${(e as Error).message}`);
  }
  return names
    .filter((n) => n.endsWith(JSONL_SUFFIX))
    .map((n) => n.slice(0, -JSONL_SUFFIX.length))
    .sort();
}

/** Read {id}.ctr.jsonl only after its .ctr.decl.json len+sha agree with the bytes. */
export function readVerified(dir: string, id: string): Transcript {
  const jsonl = join(dir, `${id}${JSONL_SUFFIX}`);
  const declPath = join(dir, `${id}${DECL_SUFFIX}`);
  try {
    statSync(jsonl);
  } catch {
    refuse("NOT_FOUND", `${id} has no ${JSONL_SUFFIX} in ${dir}`);
  }
  let decl: Record<string, unknown>;
  try {
    decl = JSON.parse(readFileSync(declPath, "utf8")) as Record<string, unknown>;
  } catch (e) {
    // A transcript without its declaration is unverifiable, so it is not read.
    refuse("NO_SOURCE", `${id} has no readable sidecar: ${(e as Error).message}`);
  }
  const payload = readFileSync(jsonl);
  if (Number(decl.len) !== payload.length) {
    refuse("LEN_MISMATCH", `${id}: declared ${decl.len}, on disk ${payload.length}`);
  }
  const sha = sha256(payload);
  if (String(decl.sha) !== sha) {
    refuse("HASH_MISMATCH", `${id}: declared ${decl.sha}, on disk ${sha}`);
  }
  const lines = payload.toString("utf8").split("\n").filter((l) => l.trim() !== "");
  if (lines.length === 0) refuse("SCHEMA_UNKNOWN", `${id}: empty transcript`);
  let head: TranscriptHead;
  let turns: Turn[];
  try {
    head = JSON.parse(lines[0]) as TranscriptHead;
    turns = lines.slice(1).map((l) => JSON.parse(l) as Turn);
  } catch (e) {
    refuse("SCHEMA_UNKNOWN", `${id}: ${(e as Error).message}`);
  }
  if (head.schema !== TRANSCRIPT_SCHEMA) {
    refuse("SCHEMA_UNKNOWN", `${id}: head.schema is ${String(head.schema)}`);
  }
  return { id, head, turns, sha, len: payload.length };
}

export type ReadResult = {
  kind: "OK";
  id: string;
  sha: string;
  head: TranscriptHead;
  n_turns: number;
  offset: number;
  turns: Turn[];
};

export function readSession(
  dir: string,
  id: string,
  offset = 0,
  limit = 50,
): ReadResult {
  const t = readVerified(dir, id);
  // The file store has no Core in front of it, so the legal check happens here.
  if (t.head.legal === true) refuse("LEGAL_OMITTED", id);
  const from = Math.max(0, offset);
  return {
    kind: "OK",
    id: t.id,
    sha: t.sha,
    head: t.head,
    n_turns: t.turns.length,
    offset: from,
    turns: t.turns.slice(from, from + Math.max(0, limit)).map((turn) => ({
      ...turn,
      text: typeof turn.text === "string" ? esc(turn.text) : turn.text,
    })),
  };
}

export type Hit = {
  id: string;
  seq: unknown;
  role: unknown;
  excerpt: string;
};

export type SearchResult = {
  kind: "OK";
  query: string;
  n_scanned: number;
  n_hits: number;
  legal_omitted: number;
  refused: Array<{ id: string; kind: string }>;
  hits: Hit[];
};

function excerpt(text: string, at: number, span = 80): string {
  const from = Math.max(0, at - span);
  const to = Math.min(text.length, at + span);
  return (from > 0 ? "…" : "") + text.slice(from, to).replace(/\s+/g, " ") + (to < text.length ? "…" : "");
}

export function searchSessions(
  dir: string,
  query: string,
  limit = 20,
  ids?: string[],
): SearchResult {
  if (!query) refuse("BAD_ARGS", "session.search requires a query");
  const needle = query.toLowerCase();
  const candidates = ids && ids.length ? ids : listIds(dir);
  const hits: Hit[] = [];
  const refused: Array<{ id: string; kind: string }> = [];
  let legalOmitted = 0;
  let scanned = 0;
  for (const id of candidates) {
    let t: Transcript;
    try {
      t = readVerified(dir, id);
    } catch (e) {
      // One corrupt transcript refuses itself; it does not blind the search.
      refused.push({ id, kind: (e as { kind?: string }).kind || "UNMEASURED" });
      continue;
    }
    if (t.head.legal === true) {
      legalOmitted += 1;
      continue;
    }
    scanned += 1;
    for (const turn of t.turns) {
      if (hits.length >= limit) break;
      const text = typeof turn.text === "string" ? turn.text : "";
      const at = text.toLowerCase().indexOf(needle);
      if (at < 0) continue;
      hits.push({
        id: t.id,
        seq: turn.seq,
        role: turn.role,
        excerpt: esc(excerpt(text, at)),
      });
    }
    if (hits.length >= limit) break;
  }
  return {
    kind: "OK",
    query,
    n_scanned: scanned,
    n_hits: hits.length,
    legal_omitted: legalOmitted,
    refused,
    hits,
  };
}
