# ARCH — Sessions as an OpenWork plugin (B8-002)

**Product:** Open Sessions (`builds/open_sessions/`) + session-tools (`builds/session-tools/`).
**This ARCH:** the same product reached from **inside** OpenWork — and from any other MCP host —
without a second kernel, a second ledger writer, or a second copy of the transcript schema.

**Stage:** SKELETON. Tool surfaces + auth boundary are decided here; one shape of them is built and
fixture-bound. What is not measured is named UNMEASURED, not shipped green.

## Shape

One host-agnostic tool table; two thin adapters over it.

```
builds/session-plugin/src/tools.ts        SESSION_TOOLS[]  (name, description, JSON Schema, run)
  ├─ .opencode/plugins/cosmos_sessions.ts  OpenWork / opencode plugin entry
  └─ src/mcp.ts  mcpHandleRequest/mcpHandleLine  any MCP host (JSON-RPC tools/list + tools/call)
```

The adapters carry no logic. A behaviour that lives in an adapter is a behaviour the other host
does not get, so both are pure re-shaping of the same table.

## Tool surfaces

| Tool | Reaches | Returns | Refuses |
|---|---|---|---|
| `session.list` | `GET /api/v1/recents` | rows + `n_omitted_legal` (legal is **omitted upstream**, the count still shows) | `CORE_UNREACHABLE` · `NO_TOKEN` · `HTTP_<code>` |
| `session.open` | `GET /api/v1/recents?open=1&id=<id>` | `{id, opencode_id, title, text, openwork}` — DISPLAY + OpenWork focus | `NOT_FOUND` · `LEGAL_OMITTED` (Core's kind, passed through) |
| `session.read` | `{id}.ctr.jsonl` + `{id}.ctr.decl.json` | `cosmos-transcript/1` head + a turn window | `NO_SOURCE` · `LEN_MISMATCH` · `HASH_MISMATCH` · `LEGAL_OMITTED` |
| `session.search` | every verified `*.ctr.jsonl` in the store | `{id, seq, role, excerpt}` hits | same as read, per file, plus `legal_omitted` count |
| `session.timeline` | `rolled-event/1` JSONL feed | ordered `{t, seq, kind, actor, detail}` projection | `NO_SOURCE` (**the feed is not emitted yet — see risks**) |

`session.read` / `session.search` verify **declared length and sha before parsing**. A transcript
whose bytes disagree with its sidecar is refused, never repaired and never partially read — the
same fail-closed contract `cosmos_validate.read_verified` already holds on the Python side.

Legal has two different mechanics and the plugin keeps both: `session.list`/`session.open` inherit
Core's omission (the plugin only surfaces the count), while `session.read`/`session.search` do
their own `head.legal` check on disk, because the file store has no Core in front of it.

## Auth boundary

**The plugin holds no credential and the repo contains none.** Everything comes from the host
environment at call time:

| Env | Meaning | Default |
|---|---|---|
| `COSMOS_CORE_URL` | Core base URL | `http://127.0.0.1:8770` |
| `COSMOS_API_TOKEN` | bearer value | unset |
| `COSMOS_API_TOKEN_FILE` | path to `live/config/api_token.txt` — read at call time, never cached to disk | unset |
| `COSMOS_TRANSCRIPT_DIR` | canonical `*.ctr.jsonl` store | unset → `NO_SOURCE` |
| `COSMOS_ROLLED_FEED` | `rolled-event/1` JSONL | unset → `NO_SOURCE` |

Rules that are tested, not just stated:

1. **No guessed root.** No transcript dir configured is `NO_SOURCE`, never a walk up the tree.
   Same scar as `cosmos_paths`: existence is not identity.
2. **Non-loopback without a token is `NO_TOKEN`, refused before the socket opens.** Core lets
   loopback peers skip the bearer (`_request_authed`); a Tailscale/LAN/phone base URL does not,
   and the plugin refuses locally rather than leaking an unauthenticated request.
3. **The token never enters a result, a log line, or an error string.** Refusal details are
   scrubbed of the token value.
4. **Read-only.** No tool writes the live tree, the ledger, or the transcript store. The plugin is
   a client of the one authority; it is not a second writer (P10 — agents propose, CCr disposes).

## Risks

- **`rolled-event/1` does not exist yet.** Nothing in this repo emits it. `session.timeline` is
  written against the schema declared below and proven against a fixture; against a live tree it
  returns `NO_SOURCE` until Core actually emits the feed. That is the honest state, not a stub
  that invents a timeline.
- **`builds/cdeck` is a bare gitlink in this repo** (mode 160000, no `.gitmodules`), so
  `cosmos_recents_panel` — the thing behind `/api/v1/recents` — is not checkable here. The plugin
  therefore binds to the **wire shape** asserted by `tests/test_cdeck_routes.py`
  (`schema: cdeck-recents/1`, or a typed `kind`) and refuses an unrecognised body as
  `SCHEMA_UNKNOWN` rather than guessing field names out of it.
- **Dotted tool names.** `session.list` is the canonical name, but some hosts reject `.` in a tool
  name. Each tool therefore carries a host-safe `id` (`session_list`) as well, and both spellings
  resolve to the same entry. If OpenWork ever rejects one of the two, the table still holds.
- **Vendor plugin API drift.** OpenWork/opencode can change the plugin contract. The entry point
  is structurally typed against a local minimal interface and imports nothing from the vendor, so
  drift breaks one adapter file, not the tool table.
- **Type stripping, not a build.** `node --experimental-strip-types` runs the `.ts` directly and
  is experimental in Node 22; it is also why there is no `tsconfig`, no bundler, and no
  `node_modules`. If OpenWork's own loader compiles the plugin instead, the same files work.

## rolled-event/1 (PROPOSED — not yet emitted)

```jsonc
{"schema":"rolled-event/1","id":"cow-abc","seq":1,"t":1757000000.0,
 "kind":"session.opened","actor":"open-sessions","detail":{}}
```

`id` joins to the transcript id. `seq` is monotonic per id. `t` is epoch seconds. Unknown `kind`
values pass through — the projection orders and filters, it does not interpret.

## Dependencies

**None added.** Zero `node_modules`, zero npm install on the host. Node runs the TypeScript by
stripping types; tests are one `.ts` script in the repo's PASS/FAIL convention, wrapped by
`tests/test_session_plugin.py` so the existing Python suite still drives it.

## Not this ARCH

A second Core. A second ledger. Writing sessions from the plugin. Bundling a vendor SDK. Shipping
a token. Re-ingesting the 666 pack. Replacing Open Sessions — this is the same product, reachable
from the orch seat.
