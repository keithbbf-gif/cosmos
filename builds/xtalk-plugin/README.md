# xtalk-plugin

OpenWork / MCP plugin for the COSMOS XTalk stream. Same Core endpoints as the
standalone page (`/xtalk/`) and the cDeck XTalk tab. No second writer.

## Tools

| Tool | Host id | Reaches |
|---|---|---|
| `xtalk.get` | `xtalk_get` | `GET /api/v1/xtalk` peek (never mkdir) |
| `xtalk.send` | `xtalk_send` | `POST /api/v1/xtalk` Transport B |
| `xtalk.roles` | `xtalk_roles` | fence projection (no session ids) |

Transport A is `NOT_COMPOSED` — the plugin does not fake inject.

## Config (host env only)

| Env | Meaning |
|---|---|
| `COSMOS_CORE_URL` | default `http://127.0.0.1:8770` |
| `COSMOS_API_TOKEN` | bearer |
| `COSMOS_API_TOKEN_FILE` | path to `api_token.txt` |

## Install

Point OpenWork at this directory's `opencode.json`:

```json
{ "plugin": [".opencode/plugins/cosmos_xtalk.ts"] }
```

## Tests

```
node --experimental-strip-types builds/xtalk-plugin/test/test_xtalk_plugin.ts
py -3.14 tests/test_xtalk.py
```
