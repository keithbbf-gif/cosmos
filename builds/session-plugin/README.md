# session-plugin

Open Sessions reached from **inside** OpenWork — and from any other MCP host. Product on COSMOS,
not CORE. Same Core endpoints, same `cosmos-transcript/1` files, no second kernel and no second
writer.

**Stage: fixture-bound.** ARCH: `docs/arch/SESSION_PLUGIN_ARCH.md`. Product: `builds/open_sessions/`.
Suite: `builds/session-tools/`.

## Tools

| Tool | Host id | Reaches |
|---|---|---|
| `session.list` | `session_list` | `GET /api/v1/recents` — rows + `n_omitted_legal` |
| `session.open` | `session_open` | `GET /api/v1/recents?open=1&id=` — text + OpenWork focus |
| `session.read` | `session_read` | `{id}.ctr.jsonl` verified against `{id}.ctr.decl.json` |
| `session.search` | `session_search` | turn text across every verified transcript |
| `session.timeline` | `session_timeline` | `rolled-event/1` projection (**feed not emitted yet**) |

Every call returns one `cosmos-session-plugin-result/1` envelope — `{schema, tool, ok, kind, gate,
legal_omitted}`. A refusal is a typed `kind`, not a thrown string.

**Empty is explicit.** A measured-empty feed is `n: 0` and empty `rows`. A missing source is a
typed refusal, never an empty list dressed as "no sessions". **UNMEASURED is `null`, never `0`.**
Data text (titles, turn text, excerpts) goes through `esc()` before it enters a result.

## Refusal kinds

| Kind | When |
|---|---|
| `NO_SOURCE` | Transcript dir / rolled feed unset or unreadable. No guessed root. |
| `NOT_FOUND` | Unknown tool, session id, or timeline id. |
| `LEGAL_OMITTED` | Legal session omitted (Core kind, or `head.legal` on disk). |
| `LEN_MISMATCH` | Transcript bytes disagree with sidecar `len` — refused before parse. |
| `HASH_MISMATCH` | Transcript bytes disagree with sidecar `sha` — refused before parse. |
| `SCHEMA_UNKNOWN` | Body / head schema is not the exact pinned string. |
| `NO_TOKEN` | Non-loopback Core with no bearer, or empty `COSMOS_API_TOKEN_FILE`. |
| `CORE_UNREACHABLE` | Core socket failed. Not an empty list. |
| `HTTP_<code>` | Core returned a non-200. Bearer material is scrubbed from the detail. |
| `BAD_ARGS` | Required argument missing. |
| `UNMEASURED` | Failure that was not a typed refusal. Never used as a count of `0`. |

## Configuration — host environment only

No credential is in this repo and none is cached to disk.

| Env | Meaning | Default |
|---|---|---|
| `COSMOS_CORE_URL` | Core base URL | `http://127.0.0.1:8770` |
| `COSMOS_API_TOKEN` | bearer value | unset |
| `COSMOS_API_TOKEN_FILE` | path to `live\config\api_token.txt`, read at call time | unset |
| `COSMOS_TRANSCRIPT_DIR` | canonical `*.ctr.jsonl` store; unset is `NO_SOURCE`, never a guess | unset |
| `COSMOS_ROLLED_FEED` | `rolled-event/1` JSONL; unset is `NO_SOURCE` | unset |

Core lets a loopback peer skip the bearer. A **non-loopback** `COSMOS_CORE_URL` with no token is
refused `NO_TOKEN` before the socket opens, and the token value never reaches a result or an
error string.

## Install into OpenWork

Copy this directory into the grant (`V:\OPENWORK\COSMOS 2\`) so the relative layout survives, then
point `opencode.json` at the entry — the bundled `opencode.json` is that registration:

```json
{ "plugin": [".opencode/plugins/cosmos_sessions.ts"] }
```

Do **not** grant OpenWork the COSMOS tree to make this work. The plugin talks to Core over
loopback and reads the transcript store it is pointed at.

## Other MCP hosts

`mcpListTools()` / `mcpCallTool()` in `src/tools.ts` are the `tools/list` + `tools/call` shapes.
Host ids are underscored because some hosts reject `.` in a tool name; both spellings resolve.
`tools/call` always wraps a `cosmos-session-plugin-result/1` envelope and sets `isError` on a
typed refusal.

## Tests

```
node --experimental-strip-types builds/session-plugin/test/test_session_plugin.ts
py -3.14 tests/test_session_plugin.py
```

Fixtures are written by the real producer — `test/fixtures/make_fixtures.py` runs
`session_tools load --out` and then derives the legal, tampered and truncated cases. The Core
tools are pinned against a throwaway loopback HTTP server, so the URL, the query string and the
`Authorization` header are measured rather than asserted.

**No dependencies.** Zero `node_modules`, no npm install on the host, no vendor SDK import: Node
runs the TypeScript by stripping types. The one dependency this would ever want is
`@opencode-ai/plugin`, and only if OpenWork starts requiring zod-typed tool args instead of JSON
Schema — it is not needed here, so it is not here.
