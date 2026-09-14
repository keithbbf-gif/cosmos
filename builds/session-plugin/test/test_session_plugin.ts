// Hermetic pins for the session plugin skeleton.
//
// Transcript tools run against fixtures the real session_tools wrote
// (test/fixtures/make_fixtures.py). Core tools run against a throwaway loopback
// HTTP server, so the URL, the query and the bearer header are measured, not
// asserted. No network, no live tree, no credential.
//
//     node --experimental-strip-types builds/session-plugin/test/test_session_plugin.ts

import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import type { Server } from "node:http";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { loadConfig } from "../src/config.ts";
import { RECENTS_SCHEMA } from "../src/core.ts";
import { esc } from "../src/esc.ts";
import { readVerified } from "../src/transcript.ts";
import {
  mcpCallTool, mcpListTools, RESULT_SCHEMA, runTool, SESSION_TOOLS, TRANSCRIPT_SCHEMA,
} from "../src/tools.ts";
import type { ToolResult } from "../src/tools.ts";
import { CosmosSessionsPlugin } from "../.opencode/plugins/cosmos_sessions.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const TRANSCRIPTS = join(HERE, "fixtures", "transcripts");
const TAMPERED = join(HERE, "fixtures", "tampered");
const ROLLED = join(HERE, "fixtures", "rolled", "cosmos.rolled.jsonl");
const GROK = "grok-aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee";

const RESULTS: Array<[string, boolean, string]> = [];

async function check(label: string, fn: () => unknown | Promise<unknown>): Promise<void> {
  try {
    RESULTS.push([label, Boolean(await fn()), ""]);
  } catch (e) {
    RESULTS.push([label, false, `${(e as Error).name}: ${(e as Error).message}`]);
  }
}

// ---- stand-in Core ------------------------------------------------------

type Seen = { path: string; auth: string | undefined };

function fakeCore(seen: Seen[]): Promise<{ server: Server; url: string }> {
  const server = createServer((req, res) => {
    const url = new URL(req.url || "/", "http://127.0.0.1");
    seen.push({ path: req.url || "", auth: req.headers.authorization });
    res.setHeader("Content-Type", "application/json");
    if (url.pathname !== "/api/v1/recents") {
      res.statusCode = 404;
      return res.end(JSON.stringify({ error: "NOT_FOUND" }));
    }
    if (url.searchParams.get("open") === "1") {
      const id = url.searchParams.get("id");
      if (id === "cow-abc") {
        return res.end(JSON.stringify({
          ok: true, kind: "OK", id, opencode_id: "ses_cow_001", title: "clocks",
          text: "# clocks\n\nhello from plumbing\n", openwork: "focus: COSMOS 2",
        }));
      }
      if (id === "cow-leg1") {
        res.statusCode = 200;
        return res.end(JSON.stringify({ ok: false, kind: "LEGAL_OMITTED", detail: id }));
      }
      res.statusCode = 200;
      return res.end(JSON.stringify({ ok: false, kind: "NOT_FOUND", detail: id }));
    }
    res.end(JSON.stringify({
      ok: true, schema: RECENTS_SCHEMA, tree_id: "KMesh-COSMOS-live", available: true,
      n_shown: 2, n_omitted_legal: 1,
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

// ---- pins ---------------------------------------------------------------

const fileEnv = { COSMOS_TRANSCRIPT_DIR: TRANSCRIPTS, COSMOS_ROLLED_FEED: ROLLED };

async function run(name: string, args: Record<string, unknown>, env: Record<string, string>) {
  return runTool(name, args, { env });
}

async function main(): Promise<number> {
  const seen: Seen[] = [];
  const { server, url } = await fakeCore(seen);
  const coreEnv = { ...fileEnv, COSMOS_CORE_URL: url };

  try {
    // --- surface ---
    await check("five tool surfaces, canonical dotted names", () =>
      SESSION_TOOLS.map((t) => t.name).join(",") ===
        "session.list,session.open,session.read,session.search,session.timeline");
    await check("every tool has a host-safe id and a JSON Schema", () =>
      SESSION_TOOLS.every((t) => /^[a-z0-9_]+$/.test(t.id) &&
        t.inputSchema.type === "object" && t.inputSchema.additionalProperties === false));

    // --- session.list ---
    const list = await run("session.list", {}, coreEnv);
    await check("session.list returns both rows off GET /api/v1/recents", () =>
      list.ok && list.kind === "OK" && (list.gate.rows as unknown[]).length === 2);
    await check("session.list carries the legal omitted count, never the row", () =>
      list.legal_omitted === 1 &&
      !JSON.stringify(list.gate.rows).includes("legal"));
    await check("session.list honours limit", async () =>
      ((await run("session.list", { limit: 1 }, coreEnv)).gate.rows as unknown[]).length === 1);
    await check("session.list unavailable feed is NO_SOURCE with n null, not 0", async () => {
      const r = await runTool("session.list", {}, {
        env: coreEnv,
        fetchImpl: async () => ({
          status: 200,
          json: async () => ({ schema: RECENTS_SCHEMA, kind: "NO_SOURCE", available: false }),
          text: async () => "",
        }),
      });
      return r.kind === "NO_SOURCE" && r.ok === false && r.gate.n === null;
    });
    await check("session.list measured empty is n 0, not UNMEASURED", async () => {
      const r = await runTool("session.list", {}, {
        env: coreEnv,
        fetchImpl: async () => ({
          status: 200,
          json: async () => ({
            schema: RECENTS_SCHEMA, available: true, n_omitted_legal: 0, rows: [],
          }),
          text: async () => "",
        }),
      });
      return r.ok && r.kind === "OK" && r.gate.n === 0 &&
        (r.gate.rows as unknown[]).length === 0 && r.legal_omitted === 0;
    });
    await check("session.list with no n_omitted_legal is null, never 0", async () => {
      const r = await runTool("session.list", {}, {
        env: coreEnv,
        fetchImpl: async () => ({
          status: 200,
          json: async () => ({ schema: RECENTS_SCHEMA, available: true, rows: [] }),
          text: async () => "",
        }),
      });
      return r.ok && r.legal_omitted === null && r.gate.legal_omitted === null;
    });

    // --- session.open ---
    const open = await run("session.open", { id: "cow-abc" }, coreEnv);
    await check("session.open hits ?open=1&id= and returns transcript + openwork focus", () =>
      open.ok && String(open.gate.text).includes("hello from plumbing") &&
      open.gate.opencode_id === "ses_cow_001" &&
      seen.some((s) => s.path.includes("open=1") && s.path.includes("id=cow-abc")));
    await check("session.open passes Core's LEGAL_OMITTED through as the kind", async () => {
      const r = await run("session.open", { id: "cow-leg1" }, coreEnv);
      return r.kind === "LEGAL_OMITTED" && r.ok === false && r.legal_omitted === 1 &&
        r.schema === RESULT_SCHEMA && !("text" in r.gate);
    });
    await check("session.open on an unknown id is NOT_FOUND, not an empty session", async () =>
      (await run("session.open", { id: "nope" }, coreEnv)).kind === "NOT_FOUND");
    await check("session.open without an id is BAD_ARGS before any request", async () =>
      (await run("session.open", {}, coreEnv)).kind === "BAD_ARGS");
    await check("session.open missing text is null, not an empty string", async () => {
      const r = await runTool("session.open", { id: "cow-abc" }, {
        env: coreEnv,
        fetchImpl: async () => ({
          status: 200,
          json: async () => ({ ok: true, kind: "OK", id: "cow-abc" }),
          text: async () => "",
        }),
      });
      return r.ok && r.gate.text === null && r.gate.title === null;
    });

    // --- auth boundary ---
    await check("loopback Core needs no bearer (Core skips it for 127.0.0.1)", () =>
      seen.length > 0 && seen.every((s) => s.auth === undefined));
    const remote = await run("session.list", {}, { COSMOS_CORE_URL: "http://10.0.0.9:8770" });
    await check("non-loopback Core without a token is NO_TOKEN, refused locally", () =>
      remote.kind === "NO_TOKEN" && !remote.ok);
    await check("a configured bearer is sent as Authorization", async () => {
      const before = seen.length;
      await run("session.list", {}, { ...coreEnv, COSMOS_API_TOKEN: "tok-abc123" });
      return seen.slice(before).every((s) => s.auth === "Bearer tok-abc123");
    });
    await check("an empty COSMOS_API_TOKEN_FILE is NO_TOKEN, not an open door", () => {
      try {
        loadConfig({ COSMOS_API_TOKEN_FILE: join(HERE, "fixtures", "empty_bearer.txt") });
        return false;
      } catch (e) {
        return (e as { kind?: string }).kind === "NO_TOKEN";
      }
    });
    await check("a dead Core is CORE_UNREACHABLE, not an empty list", async () =>
      (await run("session.list", {}, { COSMOS_CORE_URL: "http://127.0.0.1:1" })).kind ===
        "CORE_UNREACHABLE");

    // --- session.read ---
    const read = await run("session.read", { id: "cow-abc" }, fileEnv);
    await check("session.read returns the verified cosmos-transcript/1 head + turns", () =>
      read.ok && (read.gate.head as { schema: string }).schema === "cosmos-transcript/1" &&
      read.gate.n_turns === 1 &&
      read.gate.sha === readVerified(TRANSCRIPTS, "cow-abc").sha);
    await check("session.read windows turns with offset/limit", async () => {
      const r = await run("session.read", { id: GROK, offset: 1, limit: 1 }, fileEnv);
      return (r.gate.turns as Array<{ seq: number }>).length === 1 &&
        (r.gate.turns as Array<{ seq: number }>)[0].seq === 2 && r.gate.n_turns === 2;
    });
    await check("session.read refuses a legal transcript", async () => {
      const r = await run("session.read", { id: "cow-leg1" }, fileEnv);
      return r.kind === "LEGAL_OMITTED" && r.ok === false && r.legal_omitted === 1 &&
        r.schema === RESULT_SCHEMA && !("turns" in r.gate) && !("head" in r.gate);
    });
    await check("session.read of an unknown id is NOT_FOUND", async () =>
      (await run("session.read", { id: "cow-nope" }, fileEnv)).kind === "NOT_FOUND");
    await check("mutated bytes under a good sidecar refuse HASH_MISMATCH", async () => {
      const r = await run("session.read", { id: "cow-tamper" },
        { COSMOS_TRANSCRIPT_DIR: TAMPERED });
      return r.kind === "HASH_MISMATCH" && !r.ok && !("turns" in r.gate);
    });
    await check("truncated bytes refuse LEN_MISMATCH before any parse", async () => {
      const r = await run("session.read", { id: "cow-short" },
        { COSMOS_TRANSCRIPT_DIR: TAMPERED });
      return r.kind === "LEN_MISMATCH" && !r.ok && !("turns" in r.gate);
    });
    await check("no COSMOS_TRANSCRIPT_DIR is NO_SOURCE, never a guessed root", async () =>
      (await run("session.read", { id: "cow-abc" }, {})).kind === "NO_SOURCE");

    // --- session.search ---
    const hit = await run("session.search", { query: "plumbing" }, fileEnv);
    await check("session.search finds the turn and quotes an excerpt", () =>
      hit.ok && hit.gate.n_hits === 1 &&
      (hit.gate.hits as Array<{ id: string; excerpt: string }>)[0].id === "cow-abc" &&
      (hit.gate.hits as Array<{ excerpt: string }>)[0].excerpt.includes("hello from plumbing"));
    await check("session.search skips legal and reports the omitted count", () =>
      hit.gate.legal_omitted === 1 && hit.gate.n_scanned === 2 &&
      !JSON.stringify(hit.gate.hits).includes("cow-leg1"));
    await check("session.search misses cleanly (zero hits is not an error)", async () => {
      const miss = await run("session.search", { query: "zzz-no-such-token" }, fileEnv);
      return miss.ok && miss.gate.n_hits === 0;
    });
    await check("session.search refuses one corrupt file by id, keeps scanning", async () => {
      const r = await run("session.search", { query: "hello" },
        { COSMOS_TRANSCRIPT_DIR: TAMPERED });
      const refused = r.gate.refused as Array<{ id: string; kind: string }>;
      return r.ok && refused.length === 2 &&
        refused.some((x) => x.kind === "HASH_MISMATCH") &&
        refused.some((x) => x.kind === "LEN_MISMATCH");
    });
    await check("session.search without a query is BAD_ARGS", async () =>
      (await run("session.search", {}, fileEnv)).kind === "BAD_ARGS");

    // --- session.timeline ---
    const tl = await run("session.timeline", { id: "cow-abc" }, fileEnv);
    await check("session.timeline orders rolled-event/1 by (t, seq) for one id", () =>
      tl.ok && tl.gate.n_events === 2 &&
      (tl.gate.entries as Array<{ seq: number }>).map((e) => e.seq).join(",") === "1,2" &&
      (tl.gate.entries as Array<{ kind: string }>)[0].kind === "session.opened");
    await check("session.timeline filters other sessions out and counts them skipped", () =>
      tl.gate.n_skipped === 1);
    await check("no COSMOS_ROLLED_FEED is NO_SOURCE - the feed is not emitted yet", async () =>
      (await run("session.timeline", {}, { COSMOS_TRANSCRIPT_DIR: TRANSCRIPTS })).kind ===
        "NO_SOURCE");
    await check("session.timeline for an id with no events is NOT_FOUND, not empty", async () =>
      (await run("session.timeline", { id: "cow-nope" }, fileEnv)).kind === "NOT_FOUND");

    // --- host adapters ---
    await check("an unknown tool name is NOT_FOUND, not a throw", async () =>
      (await run("session.nope", {}, fileEnv)).kind === "NOT_FOUND");

    // --- envelope hardening (WO-F) ---------------------------------------
    await check("every result schema is exactly cosmos-session-plugin-result/1", async () => {
      const samples = [
        list, open, read, hit, tl,
        await run("session.open", { id: "cow-leg1" }, coreEnv),
        await run("session.read", { id: "cow-nope" }, fileEnv),
        await run("session.nope", {}, fileEnv),
      ];
      return samples.every((r) => r.schema === RESULT_SCHEMA && r.schema ===
        "cosmos-session-plugin-result/1");
    });
    await check("session.read head.schema is exactly cosmos-transcript/1", () =>
      (read.gate.head as { schema: string }).schema === TRANSCRIPT_SCHEMA &&
      TRANSCRIPT_SCHEMA === "cosmos-transcript/1");
    await check("a suffixed transcript schema is SCHEMA_UNKNOWN, not a prefix match", async () => {
      const dir = join(tmpdir(), `ctr-schema-${process.pid}`);
      mkdirSync(dir, { recursive: true });
      const head = {
        schema: "cosmos-transcript/1-beta", id: "cow-schema", family: "cowork",
        legal: false, n_turns: 1,
      };
      const payload = Buffer.from(`${JSON.stringify(head)}\n${JSON.stringify({
        seq: 1, role: "user", text: "hello",
      })}\n`);
      writeFileSync(join(dir, "cow-schema.ctr.jsonl"), payload);
      writeFileSync(join(dir, "cow-schema.ctr.decl.json"), JSON.stringify({
        schema: "cosmos-transcript-decl/1",
        len: payload.length,
        sha: createHash("sha256").update(payload).digest("hex"),
      }));
      const r = await run("session.read", { id: "cow-schema" }, { COSMOS_TRANSCRIPT_DIR: dir });
      return r.kind === "SCHEMA_UNKNOWN" && !r.ok && !("turns" in r.gate);
    });
    await check("token in a Core body never reaches the envelope", async () => {
      const token = "tok-must-never-leak-9f3a";
      const r = await runTool("session.list", {}, {
        env: { COSMOS_CORE_URL: url, COSMOS_API_TOKEN: token },
        fetchImpl: async () => ({
          status: 200,
          json: async () => ({ leaked: token }),
          text: async () => "",
        }),
      });
      const dumped = JSON.stringify(r);
      return r.kind === "SCHEMA_UNKNOWN" && !r.ok &&
        !dumped.includes(token) && dumped.includes("<redacted>");
    });
    await check("HTTP_401 is a typed refusal and the bearer is scrubbed", async () => {
      const token = "tok-http-401-secret";
      const r = await runTool("session.list", {}, {
        env: { COSMOS_CORE_URL: url, COSMOS_API_TOKEN: token },
        fetchImpl: async () => ({
          status: 401,
          json: async () => ({ error: `bad bearer ${token}` }),
          text: async () => "",
        }),
      });
      const dumped = JSON.stringify(r);
      return r.kind === "HTTP_401" && !r.ok && !dumped.includes(token) &&
        String(r.gate.detail).includes("<redacted>");
    });
    await check("MCP tools/list advertises all five with JSON Schema", () => {
      const listed = mcpListTools();
      return listed.length === 5 && listed.every((t) => t.inputSchema.type === "object");
    });
    await check("MCP tools/call wraps the envelope and flags isError on a refusal", async () => {
      const ok = await mcpCallTool("session_read", { id: "cow-abc" }, { env: fileEnv });
      const bad = await mcpCallTool("session_read", { id: "cow-leg1" }, { env: fileEnv });
      const parsed = JSON.parse(ok.content[0].text) as ToolResult;
      return ok.isError === false && bad.isError === true &&
        parsed.schema === "cosmos-session-plugin-result/1";
    });
    await check("esc() encodes data text, not structural fields", () =>
      esc("<a & 'b'>") === "&lt;a &amp; &#39;b&#39;&gt;" &&
      esc("hello from plumbing") === "hello from plumbing");
    await check("session.list and session.open run data text through esc()", async () => {
      const title = 'say <b>hi</b> & "go"';
      const body = { ok: true, schema: RECENTS_SCHEMA, available: true, rows: [
        { id: "cow-esc", date: "2026-09-14", stream: "cm", title },
      ]};
      const listed = await runTool("session.list", {}, {
        env: coreEnv,
        fetchImpl: async () => ({ status: 200, json: async () => body, text: async () => "" }),
      });
      const opened = await runTool("session.open", { id: "cow-esc" }, {
        env: coreEnv,
        fetchImpl: async () => ({
          status: 200,
          json: async () => ({ ok: true, kind: "OK", id: "cow-esc", title, text: title }),
          text: async () => "",
        }),
      });
      const wanted = esc(title);
      const row = (listed.gate.rows as Array<{ title: string }>)[0];
      return listed.ok && row.title === wanted && !JSON.stringify(listed).includes("<b>") &&
        opened.ok && opened.gate.title === wanted && opened.gate.text === wanted;
    });
    await check("OpenWork plugin entry exposes the same five, executing the same table", async () => {
      const hooks = await CosmosSessionsPlugin({});
      const names = Object.keys(hooks.tool).sort().join(",");
      const prev = process.env.COSMOS_TRANSCRIPT_DIR;
      process.env.COSMOS_TRANSCRIPT_DIR = TRANSCRIPTS;
      try {
        const out = JSON.parse(await hooks.tool.session_read.execute({ id: "cow-abc" })) as ToolResult;
        return names ===
          "session_list,session_open,session_read,session_search,session_timeline" &&
          out.ok && out.tool === "session.read";
      } finally {
        if (prev === undefined) delete process.env.COSMOS_TRANSCRIPT_DIR;
        else process.env.COSMOS_TRANSCRIPT_DIR = prev;
      }
    });
  } finally {
    server.close();
  }

  let passed = 0;
  for (const [label, ok, err] of RESULTS) {
    console.log(`${ok ? "PASS" : "FAIL"} ${label}${err ? `  ${err}` : ""}`);
    if (ok) passed += 1;
  }
  console.log(`${passed}/${RESULTS.length}`);
  return passed === RESULTS.length ? 0 : 1;
}

process.exitCode = await main();
