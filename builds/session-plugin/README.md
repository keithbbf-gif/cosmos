# session-plugin

Open Sessions reached from **inside** OpenWork — and from any other MCP host. Product on COSMOS,
not CORE. Same Core endpoints, same `cosmos-transcript/1` files, no second kernel and no second
writer.

**Stage: FIXTURE-BOUND.** ARCH: `docs/arch/SESSION_PLUGIN_ARCH.md`. Product: `builds/open_sessions/`.
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
legal_omitted}`. A refusal is a typed `kind`, not a thrown string. User-derived text in the
envelope is passed through `esc()` (HTML-safe encoding, same contract as KDash) before it leaves
the plugin.

## Refusal kinds

| Kind | When |
|---|---|
| `OK` | Tool completed; `gate` holds the payload |
| `NO_SOURCE` | Required path unset or unreadable (`COSMOS_TRANSCRIPT_DIR`, `COSMOS_ROLLED_FEED`, missing sidecar) — never a guessed root |
| `NOT_FOUND` | Named session, tool, or rolled events absent — not an empty success |
| `LEGAL_OMITTED` | Legal transcript or Core row withheld; count surfaced, row never returned |
| `LEN_MISMATCH` | Transcript bytes length disagrees with `.ctr.decl.json` before parse |
| `HASH_MISMATCH` | Transcript sha disagrees with sidecar before parse |
| `SCHEMA_UNKNOWN` | Unrecognised Core or transcript schema |
| `NO_TOKEN` | Non-loopback `COSMOS_CORE_URL` with no bearer, or empty `COSMOS_API_TOKEN_FILE` |
| `CORE_UNREACHABLE` | Core socket failed — not an empty list |
| `HTTP_<code>` | Core returned non-200 |
| `BAD_ARGS` | Required tool argument missing |
| `UNMEASURED` | Unexpected failure class — never reported as `0` hits or a green suite tally |

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

Copy this directory into the grant (for example `V:\OPENWORK\COSMOS 2\`) so the relative layout
survives. Set the host environment variables above in the OpenWork process (or its service wrapper).

**Registration — `opencode.json`** at the grant root (bundled copy ships beside this README):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [".opencode/plugins/cosmos_sessions.ts"]
}
```

**Wiring — `.opencode/plugins/cosmos_sessions.ts`** imports the host-agnostic tool table and
registers one OpenWork tool per entry (canonical dotted name and host-safe `id` alias):

```typescript
import { runTool, SESSION_TOOLS } from "../../src/tools.ts";

export const CosmosSessionsPlugin = async () => {
  const tool = {};
  for (const def of SESSION_TOOLS) {
    const entry = {
      description: def.description,
      args: def.inputSchema,
      parameters: def.inputSchema,
      execute: async (args) =>
        JSON.stringify(await runTool(def.name, args, { env: process.env }), null, 2),
    };
    tool[def.id] = entry;
    if (def.name !== def.id) tool[def.name] = entry;
  }
  return { tool };
};
export default CosmosSessionsPlugin;
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
node --experimental-strip-types builds/session-plugin/test/test_tool_session_list.ts
node --experimental-strip-types builds/session-plugin/test/test_tool_session_open.ts
node --experimental-strip-types builds/session-plugin/test/test_tool_session_read.ts
node --experimental-strip-types builds/session-plugin/test/test_tool_session_search.ts
node --experimental-strip-types builds/session-plugin/test/test_tool_session_timeline.ts
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
