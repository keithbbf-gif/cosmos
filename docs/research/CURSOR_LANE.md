# CURSOR_LANE — COSMOS-own-key Cloud Agent dispatch recipe

**Researcher:** G46 (Grok Build), local disk. **Written:** 2026-08-26 (API `Date` header `Wed, 26 Aug 2026 02:36:56 GMT`).
**Scope:** Verify **COSMOS's own** Cursor API key and write the Cloud Agent launch + poll recipe for GitHub repo `keithbbf-gif/cosmos`. **No COSMOS core code was edited.**
**Rule:** every claim is bound to a live HTTP response from this session, a file on this machine, or an official Cursor URL. **UNKNOWN** where not bound.

This is a dispatch recipe, not a DONE claim that COSMOS already dispatches through this lane.

**Stage-4 follow-up (2026-08-25, G46):** the COSMOS rail adapter is
`cosmos/cosmos_cursor_rail.py` (`link_id=cursor-api`). Canonical wiring + the
live-tree probe value live in `docs/CURSOR_LANE.md` and
`live/config/cursor_rail_probe.json`. Kernel boot still does not attach rails.

---

## 1. Verdict

**The COSMOS key authenticates.** One cheap GET to the Cloud Agents API returned **HTTP 200**. Display name on the wire is **`Cursor COSMOS 2`**.

- Base: `https://api.cursor.com` ([API overview](https://cursor.com/docs/api), OpenAPI `servers[0].url`, and every official Cloud Agents curl).
- Auth used: `Authorization: Bearer <key>` ([API overview § Bearer Authentication](https://cursor.com/docs/api#authentication); OpenAPI `bearerAuth`).
- Probe: `GET /v1/me` ([API key info](https://cursor.com/docs/cloud-agent/api/endpoints#api-key-info)).
- **No launch this session.** `POST /v1/agents` creates a billed/quota Cloud Agent run. Create/poll bodies below are bound to official docs + OpenAPI, not a live POST.

---

## 2. Live call this session (one cheap GET — no launch)

| # | Method / path | HTTP | What it proved |
|---|---|---|---|
| 1 | `GET /v1/me` | **200** | COSMOS key is valid. Cloud Agents Bearer auth works. Key display name is **`Cursor COSMOS 2`**. |

No `GET /v1/agents`. No `GET /v1/models`. No `POST /v1/agents`. No v0 calls. No SDK `Agent.create`.

### Actual request

```http
GET https://api.cursor.com/v1/me
Authorization: Bearer <key from live/config/cursor_cosmos_key.txt>
```

### Actual response

- **HTTP status:** `200`
- **Date header:** `Wed, 26 Aug 2026 02:36:56 GMT`
- **Content-Type:** `application/json; charset=utf-8`
- **Body:**

```json
{
  "apiKeyName": "Cursor COSMOS 2",
  "userId": 405041965,
  "createdAt": "2026-08-26T02:33:32.166Z",
  "userEmail": "keith.bbf@gmail.com",
  "userFirstName": "Keith",
  "userLastName": "BBF"
}
```

`userId` / `userEmail` / names are present. Official docs: those fields are for **user-scoped keys** and are omitted for service-account / team keys ([API key info](https://cursor.com/docs/cloud-agent/api/endpoints#api-key-info), OpenAPI `ApiKeyInfo`). So this key, live, is a **user API key**, not a service-account key.

---

## 3. Auth + key on this machine

### Official contract

- Docs: [Cursor APIs Overview](https://cursor.com/docs/api) · [Cloud Agents API v1](https://cursor.com/docs/cloud-agent/api/endpoints)
- OpenAPI: https://cursor.com/docs-static/cloud-agents-openapi.yaml (`servers[0].url` = `https://api.cursor.com`; `securitySchemes.bearerAuth` + `basicAuth`)
- Cloud Agents API v1 is **public beta** ([endpoints](https://cursor.com/docs/cloud-agent/api/endpoints)).
- Auth (Cloud Agents): **Basic** (`-u YOUR_API_KEY:` empty password) **or** `Authorization: Bearer <key>`. Both documented as identical. ([API overview § Authentication](https://cursor.com/docs/api#authentication))
- Key mint: [Cursor Dashboard → API Keys](https://cursor.com/dashboard/api). Format documented as `crsr_` + 64 hex. User API key or [service account](https://cursor.com/docs/account/enterprise/service-accounts) key.

### Key on this machine (redacted)

| Fact | Bound to |
|---|---|
| Path | `V:\A\Ai\COSMOS\live\config\cursor_cosmos_key.txt` (host `Get-Item` this session) |
| Git | Ignored by `.gitignore` line `/live/` (`git check-ignore` this session) |
| File length | **69** bytes (`Get-Item.Length`; `Trim()` length **69**; no whitespace) |
| LastWriteTime | 2026-08-25 21:34:54 local |
| Prefix / last 4 | `crsr_` / `31ab` (computed this session; secret not printed) |
| Live identity | `GET /v1/me` body above |
| Do **not** use | BTS keys (`Cursor BTS`, `Cursor BTS 2`). Those are a different secret. |

**The secret itself is not in this file and must stay under `live/config/` (git-ignored runtime root).**

### Name / Admin / expiry — do not paper over

| Local claim | Live / API |
|---|---|
| `docs/AGENT_BRIEF.md`: key name **`Cursor COSMOS 2`**, Admin, never-expires | `/v1/me.apiKeyName` = **`Cursor COSMOS 2`** (match). `/v1/me` has **no expiry field** and **no scope/admin field**. |
| “Admin-scope key” | `/v1/me` shape is **user-scoped** (email + userId present). Official Admin API keys are a different product (`admin:*`, [API overview](https://cursor.com/docs/api#creating-api-keys)). Whether the dashboard UI labeled this key Admin is **UNKNOWN** from the API. |
| “never-expires” | **UNKNOWN from the API.** `/v1/me` does not return expiry. |

---

## 4. Endpoints (v1 current; v0 legacy)

Official: [Cloud Agents API v1](https://cursor.com/docs/cloud-agent/api/endpoints) · [v0 (legacy)](https://cursor.com/docs/cloud-agent/api/v0) · OpenAPI: `https://cursor.com/docs-static/cloud-agents-openapi.yaml`

v1 splits a **durable agent** (`bc-<uuid>`) from **per-prompt runs** (`run-<uuid>`). New integrations should use v1 (vendor: “Migrating from v0?”).

### v1 — launch and read (the COSMOS lane)

| Action | Method | Path | Verified this session? |
|---|---|---|---|
| Create agent + first run | `POST` | `/v1/agents` | **No** (would launch) — schema from official docs + OpenAPI |
| List agents | `GET` | `/v1/agents?limit=20` | **Not called** |
| Get agent | `GET` | `/v1/agents/{id}` | **Not called** — poll recipe from docs |
| Follow-up run | `POST` | `/v1/agents/{id}/runs` | No — docs only |
| List runs | `GET` | `/v1/agents/{id}/runs` | No — docs only |
| Get run (status + result) | `GET` | `/v1/agents/{id}/runs/{runId}` | **Not called** — poll recipe from docs |
| Stream run (SSE) | `GET` | `/v1/agents/{id}/runs/{runId}/stream` | No — docs only |
| Who am I | `GET` | `/v1/me` | **Yes, 200** |
| Models | `GET` | `/v1/models` | **Not called** |
| GitHub repos | `GET` | `/v1/repositories` | **Not called** (docs: **1 / user / minute**, **30 / user / hour**) |

Create returns **201** with `{ agent, run }` (OpenAPI `CreateAgentResponse`). List/get return **200**.

### v0 — still documented; not used this session

Legacy [v0](https://cursor.com/docs/cloud-agent/api/v0): `POST /v0/agents` (launch), `GET /v0/agents/{id}` (status). v0 curls in the vendor docs use Basic (`-u YOUR_API_KEY:`). Prefer v1.

v1 webhooks: official text is “Webhooks are coming soon.” v0 still documents them. **UNKNOWN** whether v1 webhooks work today — not probed.

---

## 5. Launch recipe (v1, `keithbbf-gif/cosmos`, a prompt)

Bound to: [Create An Agent](https://cursor.com/docs/cloud-agent/api/endpoints#create-an-agent) + OpenAPI `POST /v1/agents` / `CreateAgentRequest`. **Not POSTed this session.**

### Target repo / branch

| Item | Value | Bound to |
|---|---|---|
| GitHub repo URL | `https://github.com/keithbbf-gif/cosmos` | This tree `git remote origin` = `https://github.com/keithbbf-gif/cosmos.git`; official `repos[].url` is a GitHub URL |
| Local branch now | `main` @ `56fa423` | `git branch --show-current` / `git log -1` this session |
| `startingRef` to pass | `main` (or the branch you mean) | Official `repos[0].startingRef` — branch name or commit SHA. What Cursor uses if omitted is **UNKNOWN** (not tested). |

Cloud Agents source is **GitHub**. GitLab `keithbbf-gif/cosmos` is a separate remote on this tree; whether GitLab URLs are accepted as `repos[].url` is **UNKNOWN** (docs say GitHub).

`workOnCurrentBranch` (docs, default `false`): when false, Cursor pushes to a new `cursor/...` branch off `startingRef`. When true, commits land on the starting ref.

### Create request (official v1)

```http
POST https://api.cursor.com/v1/agents
Authorization: Bearer <key from V:\A\Ai\COSMOS\live\config\cursor_cosmos_key.txt>
Content-Type: application/json
```

```json
{
  "prompt": {
    "text": "<the COSMOS task prompt>"
  },
  "name": "optional display name, max 100 chars",
  "repos": [
    {
      "url": "https://github.com/keithbbf-gif/cosmos",
      "startingRef": "main"
    }
  ],
  "workOnCurrentBranch": false,
  "autoCreatePR": true
}
```

Equivalent curl (key never in the repo; inject at run time from the live config file):

```bash
CURSOR_API_KEY="$(tr -d '[:space:]' < /path/to/live/config/cursor_cosmos_key.txt)"
curl --request POST \
  --url https://api.cursor.com/v1/agents \
  --header "Authorization: Bearer ${CURSOR_API_KEY}" \
  --header "Content-Type: application/json" \
  --data '{
    "prompt": { "text": "YOUR TASK" },
    "repos": [
      { "url": "https://github.com/keithbbf-gif/cosmos", "startingRef": "main" }
    ],
    "workOnCurrentBranch": false,
    "autoCreatePR": true
  }'
```

Basic-auth equivalent (official): `-u "${CURSOR_API_KEY}:"` instead of the Bearer header.

`model` is optional. Official: omit → user default, then team default, then system default. To pin a model, pass `model.id` from `GET /v1/models` ([List Models](https://cursor.com/docs/cloud-agent/api/endpoints#list-models)). **This session did not call `/v1/models`**, so a live catalog for this key is **UNKNOWN**.

### Documented create response (not live — no POST this session)

From [Create An Agent](https://cursor.com/docs/cloud-agent/api/endpoints#create-an-agent) / OpenAPI `201`:

```json
{
  "agent": {
    "id": "bc-…",
    "status": "ACTIVE",
    "latestRunId": "run-…"
  },
  "run": {
    "id": "run-…",
    "agentId": "bc-…",
    "status": "CREATING"
  }
}
```

`run.status` on create is typically `CREATING` — **not** the final answer. Poll or SSE.

### Fields that matter

| Field | Required? | Notes (docs / OpenAPI, unless marked live) |
|---|---|---|
| `prompt.text` | yes | Instruction text |
| `model` | no | Omit → configured default. Pin with `model.id` from `GET /v1/models` (not called this session). |
| `repos[].url` | if using repos | GitHub URL. Pass `https://github.com/keithbbf-gif/cosmos`. |
| `repos[].startingRef` | no | Branch or SHA. Pass `main` (or the branch you mean). |
| `workOnCurrentBranch` | no, default false | `false` → new `cursor/…` branch. `true` → push to `startingRef`. |
| `autoCreatePR` | no, default false (OpenAPI) | Official optional. |
| `env` | no | Mutually exclusive with explicit `repos` when selecting a named cloud environment. |
| `mode` | no, default `agent` | `plan` or `agent`. |
| Follow-up while busy | — | `POST .../runs` while a run is `CREATING`/`RUNNING` → `409 agent_busy` (docs). |

---

## 6. Poll the result

Official: execution status lives on **runs**, not on the durable agent. Agent `status` is lifecycle: `ACTIVE` | `IDLE` | `ARCHIVED` ([Get An Agent](https://cursor.com/docs/cloud-agent/api/endpoints#get-an-agent)). A recoverable error also reports agent `IDLE`; the run object holds the error.

Bound to: [Get An Agent](https://cursor.com/docs/cloud-agent/api/endpoints#get-an-agent) · [Get A Run](https://cursor.com/docs/cloud-agent/api/endpoints#get-a-run) · OpenAPI `GET /v1/agents/{id}` and `GET /v1/agents/{id}/runs/{runId}`. **Not GETed this session** (would require an agent id from a launch).

### 6.1 Keep ids from create, then GET the run

```bash
# durable agent + latestRunId
curl --request GET \
  --url "https://api.cursor.com/v1/agents/${AGENT_ID}" \
  --header "Authorization: Bearer ${CURSOR_API_KEY}"

# run status + (when terminal) result + git
curl --request GET \
  --url "https://api.cursor.com/v1/agents/${AGENT_ID}/runs/${RUN_ID}" \
  --header "Authorization: Bearer ${CURSOR_API_KEY}"
```

### 6.2 Run statuses (docs / OpenAPI `Run.status`)

`CREATING` · `RUNNING` · `FINISHED` · `ERROR` · `CANCELLED` · `EXPIRED`

Terminal: `FINISHED`, `ERROR`, `CANCELLED`, `EXPIRED`. Then `result` (final assistant text) and `durationMs` are populated. `git.branches[]` is populated once a branch has been pushed. `git.repoUrl` is returned **without** `https://` (docs).

### 6.3 Documented GET-run body (docs example, not live)

From [Get A Run](https://cursor.com/docs/cloud-agent/api/endpoints#get-a-run):

```json
{
  "id": "run-…",
  "agentId": "bc-…",
  "status": "FINISHED",
  "createdAt": "2026-04-13T18:30:00.000Z",
  "updatedAt": "2026-04-13T18:45:00.000Z",
  "durationMs": 12357,
  "result": "Added README.md with installation instructions and usage examples.",
  "git": {
    "branches": [
      {
        "repoUrl": "github.com/your-org/your-repo",
        "branch": "cursor/add-readme-a1b2",
        "prUrl": "https://github.com/your-org/your-repo/pull/123"
      }
    ]
  }
}
```

### 6.4 Poll loop (derived from docs; not executed this session)

1. `POST /v1/agents` → keep `agent.id` and `run.id` (or `agent.latestRunId`). Expect **201**.
2. Poll `GET /v1/agents/{id}/runs/{runId}` until `status` ∈ `{FINISHED, ERROR, CANCELLED, EXPIRED}`.
3. Read `result` and `git.branches[]`.
4. Optional: SSE `GET /v1/agents/{id}/runs/{runId}/stream` with `Accept: text/event-stream` ([Stream A Run](https://cursor.com/docs/cloud-agent/api/endpoints#stream-a-run)). After retention, `410 stream_expired` → fall back to GET run.
5. Optional: `GET /v1/agents/{id}/usage?runId=...` for tokens (docs; may `403 feature_unavailable`).

Do not treat agent `IDLE` as success.

OpenAPI notes that **list** run items may omit `result`; the per-run GET is the one that carries the answer. This session did not observe list-vs-get live.

---

## 7. UNKNOWN / not claimed

- Whether `POST /v1/agents` with the body above succeeds for **this** key / repo **right now**. Schema is documented; create was not sent.
- Model catalog for this key (`GET /v1/models` not called). Do not assume `grok-4.6` is accepted without listing it on this key.
- Key expiry / “never-expires” (not in `/v1/me`).
- Dashboard “Admin” label (not in `/v1/me`). Live shape is user-scoped.
- Default `startingRef` when omitted.
- v1 webhook delivery.
- Whether GitLab URLs work as Cloud Agents `repos[].url`. Docs and OpenAPI say **GitHub**.
- Numeric Cloud Agents rate limit. Docs table: “Standard rate limiting.” No number. `GET /v1/repositories` **is** 1/min, 30/hour — not called.
- `$0` remaining Cursor allowance **today**. `docs/AGENT_BRIEF.md` has a dashboard snapshot; this session did not re-read the dashboard.
- Python/TS SDK against this key. REST `GET /v1/me` is the verified path.

---

## 8. COSMOS integration notes (research only — no core edits)

- One authority, one ledger: a Cursor dispatch still needs a COSMOS ledger event even if the lane is $0-marginal.
- The cloud VM cannot see `V:`. Acceptance of **behavior** stays on Keith’s machine (runtime binding). Cloud output is **code** (branch / PR / `result` text).
- Key path is the runtime root (`live/config/cursor_cosmos_key.txt`), never the git tree. Resolve, do not paste.
- Prefer v1 over v0. v0 remains available during vendor migration ([v0](https://cursor.com/docs/cloud-agent/api/v0)).

---

## 9. Official URLs

- https://cursor.com/docs/cloud-agent/api/endpoints
- https://cursor.com/docs/cloud-agent/api/v0
- https://cursor.com/docs/api
- https://cursor.com/dashboard/api
- OpenAPI: https://cursor.com/docs-static/cloud-agents-openapi.yaml
