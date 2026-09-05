# Cursor Cloud Agents API v1 — COSMOS dispatch reference (from official docs, 2026-08-25)

**Base:** `https://api.cursor.com`  ·  **Auth:** Basic (`-u "$KEY:"`) or Bearer.
**COSMOS key:** read from `V:\A\Ai\COSMOS\live\config\cursor_cosmos_key.txt` (`Cursor COSMOS 2`,
Admin, never-expires). Never hard-code; redact to `crsr_…last4`. Repo: `keithbbf-gif/cosmos`.
Public beta — API may change. Full OpenAPI: `/docs-static/cloud-agents-openapi.yaml`.

## The dispatch loop COSMOS uses
1. **Verify key:** `GET /v1/me` → `{apiKeyName, userId, userEmail}`. 200 = key good.
2. **List models:** `GET /v1/models` → valid `model.id`s (e.g. `composer-2`, `claude-4.6-sonnet-thinking`). Omit `model` to use default.
3. **Launch agent + first run:** `POST /v1/agents`
   body: `{"prompt":{"text":"..."},"repos":[{"url":"https://github.com/keithbbf-gif/cosmos","startingRef":"main"}],"autoCreatePR":true}`
   → returns `agent.id` (`bc-…`) + `run.id` (`run-…`), `run.status:"CREATING"`. Default pushes to a new `cursor/…` branch.
   Optional: `model.id`, `mcpServers[]`, `customSubagents[]`, `mode:"plan"|"agent"`, `agentId:"bc-<uuid>"` (idempotent), `env.type:"pool"`.
4. **Poll result:** `GET /v1/agents/{id}/runs/{runId}` → on terminal `status:"FINISHED"` returns `result` (final text), `durationMs`, `git.branches[]` (`{repoUrl,branch,prUrl?}`). Or **stream** `GET /v1/agents/{id}/runs/{runId}/stream` (SSE: status/assistant/tool_call/result/done).
5. **Follow-up:** `POST /v1/agents/{id}/runs` (one active run per agent; `409 agent_busy` otherwise). **Cancel:** `POST .../runs/{runId}/cancel`.
6. **Usage:** `GET /v1/agents/{id}/usage` → per-run token counts. **Artifacts:** `GET /v1/agents/{id}/artifacts` + `/download`.
7. **Lifecycle:** `POST /v1/agents/{id}/archive` | `/unarchive`; `DELETE /v1/agents/{id}` (irreversible).

## Minimal launch (curl)
```
curl -s -X POST https://api.cursor.com/v1/agents -u "$(cat live/config/cursor_cosmos_key.txt):" \
  -H 'Content-Type: application/json' \
  -d '{"prompt":{"text":"<task>"},"repos":[{"url":"https://github.com/keithbbf-gif/cosmos","startingRef":"main"}],"autoCreatePR":true}'
```
Then poll `GET /v1/agents/{agent.id}/runs/{run.id}` until `status:"FINISHED"`; read `result` + `git.branches[].prUrl`.

## Notes / gotchas
- `GET /v1/repositories` is rate-limited hard (1/min, 30/hr) — don't poll it.
- `repoUrl` in run responses drops the scheme (`github.com/...`) vs request `repos[].url` (`https://...`).
- Worker pools / BYO-machine + fleet mgmt: `/v0/private-workers*` (needs a service-account key).
- Cloud Agent runs on branches → also triggers GitLab CI on push. Two free lanes at once.
