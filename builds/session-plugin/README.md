# session-plugin

Open Sessions reached from **inside** OpenWork — and from any other MCP host. Product on COSMOS,
not CORE. Same Core endpoints, same `cosmos-transcript/1` files, no second kernel and no second
writer.

**Stage: SKELETON.** ARCH: `docs/arch/SESSION_PLUGIN_ARCH.md`. Product: `builds/open_sessions/`.
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
legal_omitted}`. A refusal is a typed `kind`, not a thrown string: `NO_SOURCE`, `NOT_FOUND`,
`LEGAL_OMITTED`, `LEN_MISMATCH`, `HASH_MISMATCH`, `SCHEMA_UNKNOWN`, `NO_TOKEN`,
`CORE_UNREACHABLE`, `HTTP_<code>`, `BAD_ARGS`, `UNMEASURED`.

## Configuration — host environment only

No credential is in this repo and none is cached to disk.

| Env | Meaning |
|---|---|
| `COSMOS_CORE_URL` | Core base URL (default `http://127.0.0.1:8770`) |
| `COSMOS_API_TOKEN` | bearer value |
| `COSMOS_API_TOKEN_FILE` | path to `live\config\api_token.txt`, read at call time |
| `COSMOS_TRANSCRIPT_DIR` | canonical `*.ctr.jsonl` store; unset is `NO_SOURCE`, never a guess |
| `COSMOS_ROLLED_FEED` | `rolled-event/1` JSONL; unset is `NO_SOURCE` |

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

`src/mcp.ts` exposes JSON-RPC 2.0 `tools/list` + `tools/call` (`mcpHandleRequest` /
`mcpHandleLine`); it reshapes the same table via `mcpListTools()` / `mcpCallTool()`.
Host ids are underscored because some hosts reject `.` in a tool name; both spellings resolve.

## Tests

```
node --experimental-strip-types builds/session-plugin/test/test_session_plugin.ts
node --experimental-strip-types builds/session-plugin/test/test_mcp_adapter.ts
node --experimental-strip-types builds/session-plugin/test/test_opencode_adapter.ts
py -3.14 tests/test_session_plugin.py
```

Fixtures are written by the real producer — `test/fixtures/make_fixtures.py` runs
`session_tools load --out` and then derives the legal, tampered and truncated cases. The Core
tools are pinned against a throwaway loopback HTTP server, so the URL, the query string and the
`Authorization` header are measured rather than asserted.

**No dependencies.** Zero `node_modules`, no npm install on the host, no vendor SDK import: Node
runs the TypeScript by stripping types. The one dependency this would ever want is
`@opencode-ai/plugin`, and only if OpenWork starts requiring zod-typed tool args instead of JSON
Schema — it is not needed for the skeleton, so it is not here.
