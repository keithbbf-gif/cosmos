# T1 sync Gbot↔COW — domain map (GitHub / Cursor / GitLab / OTHER)

**Author:** G46 (Grok Build). **Date:** 2026-08-25.  
**Target:** SYNCHRONOUS programmatic control (request → response; COW blocks for the reply) of a **persistent GrokBot agent team** from COW. Today that team is **async file-mailbox only**.  
**Inputs:** `research_{grok,openai,gemini}.md`, `docs/T1_ARCH.md`, `builds/gbridge/`, plus live vendor docs fetched 2026-08-25.  
**Rule:** write **UNKNOWN** rather than guess. No code. No cookie/browser automation of grok.com.

---

## 0. Identity split — do not conflate these products

xAI shipped several similarly named surfaces. Only one of them is the T1 target.

| Product | Where | Persistent named team? | Programmable? | Addresses the T1 team? |
|---|---|---|---|---|
| **GrokBot / GBt team** (T1 target) | grok.com mailbox today; COSMOS `gbridge` `to_gbot/`/`from_gbot/` | Yes — the team COW already talks to | File mailbox only | **This is the target** |
| **Grok Bot** (app, launched 11 Aug 2026) | Desktop/iOS app; Cursor account required; persistent **shared** cloud VM | Yes — named Bots, group chats, up to 50 Bots+chats | **No public API / webhook** in [docs.x.ai/grok-bot](https://docs.x.ai/grok-bot/overview) | **UNKNOWN** whether this *is* the T1 team. Different product surface than grok.com chat. |
| **Grok Automations** (ex-Tasks) | grok.com/automations | Saved automations, not a named teammate | Webhook **starts** a run (`202 Accepted`, async) | No — fire-and-forget automation, not the team |
| **Grok Build** (`grok` CLI) | Local terminal / CI | Sessions under `~/.grok/sessions`, not grok.com team memory | **Yes** — headless `-p`, JSON, ACP stdio | No — local coding agent, same *model family* |
| **xAI API** | `https://api.x.ai/v1` | No (client-managed messages) | **Yes** — HTTP request/response | No — model, not team |
| **Cursor Cloud Agents** | `https://api.cursor.com/v1/agents` (`bc-*` IDs) | Durable agent + runs | **Yes** — REST + SDK `wait()` | No — Cursor coding agent, not a Grok Bot teammate ID |

Grok Bot (the app) is Cursor-account-backed: eligible plans are SuperGrok Plus/Heavy **or** Cursor Pro+/Ultra/Teams; sign-in is “Sign In with Cursor”; admin settings live on the Cursor dashboard; a team toggle controls whether Grok Bot Bots may *launch* Cursor cloud agents. That does **not** document that a Grok Bot teammate is addressable as `POST /v1/agents`. Treat them as different objects until xAI/Cursor document an ID mapping.

---

## Rubric (same as `docs/T1_ARCH.md`)

A domain is useful for T1 only if it can satisfy, in order:

1. **R1 Identity** — the call reaches the *actual* persistent team (memory, files, config), not a fresh Grok/Cursor/Copilot/Duo session.
2. **R2 Sync at COW** — one blocking call returns a structured answer **or a typed refusal**.
3. **R3 Supported surface** — documented endpoints. No guessed `team_id`, no cookie replay.
4. **R4 Canon** — DOM-first; nothing that must run out as the *primary* path; fail-closed.
5. **R5 Buildable today**.
6. **R6 Swap-ready** — COW’s call site stays `ask()`; transport is injected (`gbridge`).

**Consensus from prior vendor research (unchanged for grok.com team identity):** there is still **no documented public API that addresses a persistent grok.com / Grok Bot named team by ID**. The domains below are evaluated as *candidate channels*, not assumed to be that API.

---

## 1. GitHub (Actions, Apps, API dispatch)

### 1.1 Does GitHub expose a synchronous channel to the GrokBot team?

**No.** GitHub has no documented endpoint that takes a grok.com / Grok Bot team ID. Nothing in Actions, Apps, or Copilot agent-tasks talks to grok.com.

GitHub *does* expose several **dispatch-then-poll** agent/CI surfaces. Those can be made **blocking at the caller** by polling. They still run **GitHub’s** agents or **your** workflow, not GBt.

### 1.2 Exact surfaces

#### A. Actions `workflow_dispatch` (fire, then poll)

- **Endpoint:** `POST https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches`
- **Auth:** `Authorization: Bearer <token>` + `Accept: application/vnd.github+json` + `X-GitHub-Api-Version: 2026-03-10`. PAT/OAuth: `repo` (classic) or Actions **write** (fine-grained / App). `GITHUB_TOKEN` cannot dispatch a workflow in another repo.
- **Body:** `{ "ref": "<branch|tag>", "inputs": { ... } }` — max 25 input keys; workflow must declare `on: workflow_dispatch`.
- **Response (current REST docs):** **200** with `{ workflow_run_id, run_url, html_url }`. Changelog 2026-02-19: historically **204 No Content**; optional `return_run_details` was added so the 200 body is opt-in. **Confirm** which of “always 200” vs “200 only with `return_run_details: true`” the live API applies before coding — do not assume.
- **Wait (not a native blocking RPC):**
  - REST: poll `GET /repos/{owner}/{repo}/actions/runs/{run_id}` until `status == completed`.
  - CLI: `gh workflow run <workflow>` (prints run URL when available) then `gh run watch <run-id> [--exit-status] [-i 3]`. Watch **polls** (default 3s). Then `gh run view <run-id> --json ...` / `gh run download <run-id>` for artifacts.
- **Sync?** Dispatch is **async**. `gh run watch` is **sync at the CLI process**. HTTP itself never blocks for the workflow.
- **GBt?** Only if the *workflow* on a **self-hosted runner that can see the mail root** writes `to_gbot/` and waits on `from_gbot/` — that is mailbox-over-Actions, worse than local `gbridge`. A GitHub-hosted runner **cannot** see `V:\A\Ai\COSMOS\live`.

#### B. `repository_dispatch` (external event)

- **Endpoint:** `POST https://api.github.com/repos/{owner}/{repo}/dispatches`
- **Auth:** same Bearer; classic PAT needs `repo`.
- **Body:** `{ "event_type": "<≤100 chars>", "client_payload": { ... } }` — max 10 top-level payload keys, **< 64 KB**.
- **Response:** **204 No Content** — **no run ID**. Mapping dispatch → run requires listing runs by event and heuristics (race-prone).
- **Sync?** No. Worse than `workflow_dispatch` for a blocking caller.

#### C. GitHub Apps

- **Auth:** App JWT (`iss` = app id, RS256) → `POST /app/installations/{id}/access_tokens` → installation token. Webhooks: HMAC `X-Hub-Signature-256`.
- **What they can do:** receive GitHub events (async), call REST/GraphQL, dispatch Actions, open issues/PRs, post check runs.
- **What they cannot do (documented):** GitHub App **installation (server-to-server) tokens are not supported** on the Copilot agent-tasks API (user-to-server only). Apps have **no grok.com/Grok Bot API**.
- **Sync?** Webhook inbound is async. An App that then polls something else is a shim you own, not a GitHub feature.

#### D. Copilot cloud agent / Agent tasks API (public preview)

- **Start:** `POST https://api.github.com/agents/repos/{owner}/{repo}/tasks`
- **List repo:** `GET https://api.github.com/agents/repos/{owner}/{repo}/tasks`
- **List all:** `GET https://api.github.com/agents/tasks`
- **Status:** `GET https://api.github.com/agents/repos/{owner}/{repo}/tasks/{task-id}`
- **Auth:** user-to-server only — PAT, OAuth, or GitHub App **user-to-server**. Header `X-GitHub-Api-Version: 2022-11-28` in the how-to (REST versioning page also cites `2026-03-10` — use the agent-tasks reference live).
- **Body:** required `prompt`; optional `base_ref`, `model`, `create_pull_request`.
- **States:** `queued | in_progress | completed | failed | idle | waiting_for_user | timed_out | cancelled`.
- **Issue assign path:** REST `POST /repos/{owner}/{repo}/issues/{n}/assignees` with `"assignees": ["copilot-swe-agent[bot]"]` + `agent_assignment`; or GraphQL `createIssue` / `replaceActorsForAssignable` with `GraphQL-Features: issues_copilot_assignment_api_support,coding_agent_model_selection`.
- **Sync?** **No.** POST returns a task; caller polls GET. No documented blocking “run until result” RPC.
- **GBt?** No — this is Copilot’s cloud coding agent (Actions-backed VM, PR-oriented).

### 1.3 Concrete GitHub path (if forced to use this domain)

```
COW  --(block on poll)-->  POST workflow_dispatch (return run id)
                         -->  GET run / gh run watch
                         -->  GET artifacts or job logs
```

That path is a **CI job**, not GBt. To reach GBt you’d still drop a mailbox file from a self-hosted runner — extra hops, runner quota, GitHub auth, no identity gain.

**Verdict:** GitHub is a **documented dispatch+poll fabric**, not a GBt RPC. Do not pick it as the T1 primary.

---

## 2. Cursor (Cloud Agent API / SDK)

### 2.1 Does Cursor expose a synchronous channel to the GrokBot team?

**Not documented.** Cursor has a **real, documented agent RPC** (closest thing in these four domains to “block for an agent reply”), but the documented resource is a **Cursor Cloud Agent** (`bc-<uuid>`), not a Grok Bot teammate and not the grok.com mailbox team.

Grok Bot *uses* a Cursor account and *may launch* Cloud Agents (dashboard toggle “Cloud Agents”, on by default). Official Cloud Agents API pages do **not** list a `grokBotId`, Bot name, or grok.com team handle. **UNKNOWN** whether any existing Grok Bot teammate is a `bc-*` you can `GET`/`POST /runs` against. Do not assume `Agent.resume("the QA bot")` works.

### 2.2 Exact surfaces

**Base:** `https://api.cursor.com`  
**Auth (Cloud Agents):** Basic (`-u YOUR_API_KEY:`) **or** `Authorization: Bearer <key>`. Keys from [Cursor Dashboard → API Keys](https://cursor.com/dashboard/api) (`crsr_…`) or a **service account** key. Team Admin API keys are **not** supported for the SDK. Env: `CURSOR_API_KEY`.  
**Status:** Cloud Agents API **v1 public beta**. v1 webhooks: “coming soon”; legacy **v0 still has webhooks**.

#### REST v1 (async create, poll or SSE)

| Action | Method / path |
|---|---|
| Create agent + first run | `POST /v1/agents` |
| List agents | `GET /v1/agents` |
| Get agent | `GET /v1/agents/{id}` |
| Follow-up run | `POST /v1/agents/{id}/runs` |
| List / get run | `GET /v1/agents/{id}/runs` · `GET /v1/agents/{id}/runs/{runId}` |
| Stream run (SSE) | `GET /v1/agents/{id}/runs/{runId}/stream` (`Accept: text/event-stream`) |
| Cancel run | `POST /v1/agents/{id}/runs/{runId}/cancel` |
| Usage / artifacts / lifecycle | `GET /v1/agents/{id}/usage` · artifacts list/download · `POST .../archive` · `DELETE /v1/agents/{id}` |
| Me / models / GitHub repos | `GET /v1/me` · `GET /v1/models` · `GET /v1/repositories` (strict: **1/user/min**, **30/user/hour**) |

Create body (required): `prompt.text`. Optional: `model.id`/`params`, `repos[]` (GitHub URL + `startingRef`/`prUrl`), `autoCreatePR`, `mcpServers[]`, `env` (`cloud`\|`pool`\|`machine`), `mode` (`agent`\|`plan`), client `agentId` (`bc-<uuid>`). Omit `repos` and `env` for a **no-repo** agent (must be enabled; repo-scoped keys cannot create them).

Create **response:** `{ agent, run }` with `run.status` typically `CREATING` — **not** the final answer. Terminal run `GET` includes `result` (assistant text), `durationMs`, `git`. Run statuses include `CREATING` / `RUNNING` / `FINISHED` / `ERROR` / `CANCELLED` / `EXPIRED`. Follow-up while busy: **409 `agent_busy`**.

SSE events: `status`, `assistant`, `thinking`, `tool_call`, `interaction_update`, `heartbeat`, `result`, `error`, `done`. Resume with `Last-Event-ID`. Retention: `X-Cursor-Stream-Retention-Seconds`; after expiry **410 `stream_expired`** — fall back to GET run.

**REST itself is not a single blocking HTTP RPC.** Blocking is: hold the SSE stream until `result`/`done`, or poll GET.

#### Python / TypeScript SDK (sync *at the caller*)

- PyPI `cursor-sdk` / npm `@cursor/sdk` (aligned ~1.0.28 as of 2026-08-13).
- Sync Python: `Agent.create(...)` → `agent.send(prompt)` → `run.wait()` / `run.text()` / `Agent.prompt(...)` (create+send+wait+dispose).
- Cloud example: `CloudAgentOptions(repos=[CloudRepository(url=..., starting_ref="main")], auto_create_pr=True)`.
- Resume: `Agent.resume("bc-...")` then `send`+`wait`.
- Docs: [cursor.com/docs/sdk/python](https://cursor.com/docs/sdk/python), [cursor.com/docs/cloud-agent/api/endpoints](https://cursor.com/docs/cloud-agent/api/endpoints).

This is the **only first-party SDK in these four domains** that documents a process-blocking `wait()` on a durable agent.

### 2.3 Concrete Cursor path

**If the goal is “block for a Cursor agent reply” (R2 yes, R1 no for GBt):**

```
COW  --(block)--  cursor-sdk Agent.prompt(...) / run.wait()
               or POST /v1/agents + GET .../stream until result
Auth: CURSOR_API_KEY
```

**If the goal is the T1 GrokBot team:** Cursor does not document that path. Using Cloud Agents would **replace** the team with a new Cursor agent (optional MCP servers, repo VM, PR). That is a substitute, not a bridge.

**Verdict:** Best **documented blocking agent API** of the four domains. **Not** a GBt identity channel unless a later Cursor/xAI doc maps Bot IDs → `bc-*`. Watch item, not a build.

---

## 3. GitLab (CI triggers, API)

COSMOS already uses GitLab CI (`ROUTING.md` / mesh notes). That does not make GitLab a GBt RPC.

### 3.1 Does GitLab expose a synchronous channel to the GrokBot team?

**No.** Same as GitHub: pipelines and Duo flows are GitLab’s agents/jobs. No grok.com team ID.

### 3.2 Exact surfaces

#### A. Create pipeline (user token)

- **Endpoint:** `POST https://gitlab.example.com/api/v4/projects/:id/pipeline?ref=<branch>`
- **Auth:** `PRIVATE-TOKEN: <PAT>` (or job token where documented).
- **Optional JSON:** `{ "variables": [...], "inputs": { ... } }` (`inputs` GA in GitLab 18.1).
- **Response:** **201** pipeline object, `status: pending` — **immediate**, not finished.
- **Wait:** poll `GET /projects/:id/pipelines/:pipeline_id` until `status` ∈ `{success, failed, canceled, skipped, ...}`. Job logs/artifacts via Jobs API / `glab job artifact`.
- **CLI:** `glab ci run [-b ref] [--variables ...] [--input key:value]` then `glab ci status --wait` (blocks until finished, non-interactive) or `--live`.

#### B. Trigger token

- **Endpoint:** `POST /projects/:id/trigger/pipeline`
- **Auth:** form `token=<trigger token or CI_JOB_TOKEN>` + `ref=` + optional `variables[KEY]=` / `inputs`.
- **Docs:** [Pipeline trigger tokens API](https://docs.gitlab.com/api/pipeline_triggers/), [CI triggers](https://docs.gitlab.com/ci/triggers/).
- **Response:** pipeline object, not a final result.
- **`$CI_PIPELINE_SOURCE`:** `trigger` (trigger token) vs `pipeline` (`$CI_JOB_TOKEN` / `trigger:` keyword).

#### C. YAML `trigger: strategy: depend`

Waits for a **downstream GitLab pipeline from inside another GitLab job**. Not a COW-callable blocking HTTP API.

#### D. GitLab Duo Agent Platform — Flows API (Premium/Ultimate; trigger is **Experiment**)

- **Start:** `POST /api/v4/ai/duo_workflows/workflows`
- **Auth:** `PRIVATE-TOKEN`.
- **Body (typical):** `{ "project_id", "goal", "workflow_definition": "developer/v1", "start_workflow": true }` or `ai_catalog_item_consumer_id`. Optional `allow_agent_to_request_user` (default true — may **pause** for input).
- **Response:** **201** with `id`, `status` (`created|running|paused|finished|failed|stopped|input_required|plan_approval_required|tool_call_approval_required`), `workload`.
- **Trace:** `GET /ai/duo_workflows/workflows/:workflow_id/trace.jsonl` (experiment) — JSONL chat log, **not** a blocking create.
- **Callbacks:** `POST /ai/duo_workflows/flow_callbacks` registers HTTPS for `flow.started` / `flow.completed` / `flow.failed` (org Owner). Then pass `callback_hook_id` when triggering — **async notify**, not request/response.
- **Mentions/assign:** Duo **triggers** (Mention / Assign / Assign reviewer / Pipeline events) are inbound GitLab events, async.

**Sync?** Create is async. Caller polls status or waits on a callback. `glab ci status --wait` is sync **for CI pipelines**, not for Duo flows (no documented `glab duo wait`).

**GBt?** No. Duo is GitLab’s agent platform (CI-backed remote flows). External-agent docs describe *your* model key inside GitLab, not grok.com teams.

### 3.3 Concrete GitLab path (if forced)

```
COW  --(block on poll)--  POST /projects/:id/pipeline
                       -->  GET pipeline until terminal
                       -->  job artifacts / trace
or: glab ci run … ; glab ci status --wait
```

Same objection as GitHub: extra hop, runner must see the mail root to reach GBt, no identity.

**Verdict:** GitLab is COSMOS’s **CI** home, not the GBt control plane. Duo Flows are a second Copilot-like async agent API. Do not pick for T1.

---

## 4. OTHER — xAI Agents/Assistants, MCP wrap, grok CLI, Automations

### 4.1 xAI Agents / Teams / Assistants API

**Finding: no documented public Agents/Teams/Assistants API that addresses a grok.com or Grok Bot named team.**

What *is* documented (model inference, **synchronous HTTP**):

| Item | Value |
|---|---|
| Base | `https://api.x.ai/v1` |
| Auth | `Authorization: Bearer $XAI_API_KEY` (prefix `xai-`; console.x.ai) |
| Primary (current quickstart) | `POST /v1/responses` — `{ "model": "grok-4.6", "input": "..." }` |
| Also supported | `POST /v1/chat/completions` (OpenAI-compatible `messages`) |
| SDK | `pip install xai-sdk` · `Client(api_key=...).chat.create(model=...).sample()` |
| OpenAI compat | `OpenAI(api_key=..., base_url="https://api.x.ai/v1")` |
| Structured outputs | documented under text generation — **verify current model support** at [docs.x.ai](https://docs.x.ai) rather than guessing schema fields |
| Remote MCP (Grok as **client**) | tools `type: "mcp"`, `server_url` on Responses / xAI SDK `mcp(server_url=...)` |
| Batch | `POST /v1/batches` — **async**, not T1 |
| Management | `api.x.ai` gRPC + REST team API-key admin — **not** Bot/team runs |

**Not documented:** `POST /v1/agents/{id}/runs`, `/v1/teams/{id}/messages`, `/v1/assistants`, `bot_id`, `team_id`, grok.com session continuity.

**Sync?** **Yes** for chat/responses (HTTP blocks until completion or client timeout). **R1:** no — fresh model session, not GBt.

Rate/token numbers are **account-tiered** (docs describe spend tiers since 2026-01-01). Do not hard-code RPM/TPM; read the console / current rate-limit page.

### 4.2 Grok Bot app (docs.x.ai/grok-bot)

- Create/edit/share/delete Bots in the **app UI**. Share link is a **public config copy**, not an RPC handle.
- Memory, routines, group chats, shared computer, connectors/MCP **consumed by the Bot**, computer-use for sites without APIs.
- **No** public API, webhook, or “message this Bot” endpoint in the Bot docs (overview, get-started, bots, teams-and-enterprises).
- **UNKNOWN:** undocumented private UI API behind the app. R3 forbids building on it.

### 4.3 Grok Automations webhook (grok.com, not the team)

- **Docs:** [docs.x.ai/grok/automations/webhooks](https://docs.x.ai/grok/automations/webhooks)
- **How:** save an automation → add Webhook trigger → unique URL + `whsec_…` secret (shown once).
- **Call:** `POST <copied endpoint>` with Standard Webhooks headers: `webhook-id`, `webhook-timestamp`, `webhook-signature: v1,<b64 HMAC-SHA256>` over `{id}.{timestamp}.{raw-body}`. Body ≤ **1 MiB**. Timestamp skew > 5 min rejected.
- **Response:** **202 Accepted** — “confirms that the delivery was accepted **rather than that the automation has finished**.”
- **Sync?** **No.** Inbound fire-and-forget. No documented GET-result or callback of the run’s text to the caller.
- **GBt?** No. A saved automation, not the persistent team.

### 4.4 Grok Build CLI (`grok`) — official, **synchronous process**

- **Install:** `curl -fsSL https://x.ai/cli/install.sh | bash` · Windows: `irm https://x.ai/cli/install.ps1 | iex` · npm: `@xai-official/grok` also exists — **prefer the x.ai installer** as the vendor path.
- **Docs:** [docs.x.ai/build/overview](https://docs.x.ai/build/overview), [headless](https://docs.x.ai/build/cli/headless-scripting), [CLI reference](https://docs.x.ai/build/cli/reference).
- **Auth:** browser `grok login` (SuperGrok / X Premium+) **or** `XAI_API_KEY` (bills API). CI/headless: API key. `--device-auth` for remote login.
- **Blocking one-shot:**

  ```
  grok --no-auto-update -p "PROMPT" --output-format json
  ```

  Flags: `-p/--single`, `-m model`, `-s/--session-id`, `-r/--resume`, `-c/--continue`, `--cwd`, `--output-format plain|json|streaming-json`, `--always-approve`. Sessions: `~/.grok/sessions`.

- **ACP (JSON-RPC over stdio, request/response):** `grok agent stdio`  
  Flow documented: `initialize` → `authenticate` (`xai.api_key` or `cached_token`) → `session/new` → `session/prompt`. Assistant text arrives as `session/update` chunks; `session/prompt` returns completion metadata (`stopReason`). This is **sync at the JSON-RPC call** if the client waits for the prompt result (the vendor JS sample also polls text-length stability — treat that sample as illustrative, not a second protocol).

- **MCP:** `grok mcp add|list|remove|doctor` — Grok Build as **MCP client**, not as an MCP server wrapping GBt.
- **GBt?** No. Local/CI coding agent. Named grok.com team state is not a CLI flag (`--bot-id` / `--team-id` **not documented**).

**Name collision:** community `superagent-ai/grok-cli` is a **different** tool. Do not mix.

### 4.5 Wrap GrokBot as an MCP server so COW calls a native tool

MCP can wrap **any function you can implement**. It cannot invent an upstream API.

| Backend behind `grokbot_ask` | Sync at COW? | Hits T1 team? |
|---|---|---|
| xAI `POST /v1/responses` or `/v1/chat/completions` | Yes | No |
| `grok -p --output-format json` / `grok agent stdio` | Yes (process/JSON-RPC) | No |
| Cursor `run.wait()` | Yes (SDK) | No (unless Bot ID mapping is later documented) |
| Poll `from_gbot/<id>.json` (gbridge MailboxTransport) | Yes (blocking poll) | **Yes** |
| Grok Automations webhook | No (202) | No |
| Undocumented grok.com UI API | UNKNOWN / R3 fail | UNKNOWN |

**Direction trap:** xAI “Remote MCP Tools” means **Grok calls your MCP server**. That is the opposite of COW calling Grok as a tool.

**Smallest MCP slice that preserves identity:** stdio MCP tool `gbridge_ask` over existing `GBridge.ask()` (already deferred in `builds/gbridge/README.md`). Transport stays injected.

---

## Comparison (honest)

| Domain | Native blocking RPC? | Documented auth + endpoint? | Reaches T1 GBt identity? | Fit for T1 primary? |
|---|---|---|---|---|
| **GitHub Actions** | No (poll / `gh run watch`) | Yes | No (unless self-hosted mailbox) | No — extra hop |
| **GitHub Apps** | No | Yes (JWT/install) | No | No |
| **GitHub Copilot tasks** | No (poll task state) | Yes (user-to-server) | No | No — wrong agent |
| **Cursor Cloud Agents REST** | No (poll/SSE) | Yes | UNKNOWN / almost certainly no | Watch only |
| **Cursor SDK `wait()`** | **Yes at process** | Yes | UNKNOWN / almost certainly no | Best *Cursor-agent* path; not GBt |
| **GitLab pipeline API** | No (poll / `glab ci status --wait`) | Yes | No | No — extra hop |
| **GitLab Duo Flows** | No (poll / callback) | Yes (experiment) | No | No |
| **xAI chat/responses** | **Yes HTTP** | Yes | No | API-second fallback (already in T1_ARCH) |
| **Grok Build `grok -p` / ACP** | **Yes process / JSON-RPC** | Yes | No | Best *Grok-agent* path; not GBt |
| **Grok Automations webhook** | No (`202`) | Yes | No | Inbound only |
| **Grok Bot app** | No public channel | UI only | UNKNOWN if it *is* T1 | Cannot call it |
| **MCP wrap of mailbox/gbridge** | Yes (your server blocks) | MCP stdio/HTTP you host | **Yes** | Matches T1_ARCH slice 2 |
| **Mailbox / gbridge** | Yes (blocking poll) | Filesystem, handed-in root | **Yes** | **Primary today** |

---

## RECOMMENDED single best path

**Keep `gbridge` MailboxTransport as the primary T1 channel. Do not route COW→GBt through GitHub, GitLab, or Cursor.**

Reason, against the rubric:

- **R1.** Only the mailbox (or a future documented Teams/Bot API) reaches the team that already reads/writes files. GitHub Copilot tasks, Cursor `bc-*` agents, GitLab Duo flows, `grok -p`, and `api.x.ai` are **different identities**.
- **R2.** `GBridge.ask()` already blocks until `from_gbot/<id>.json` or a typed refusal (`TIMEOUT`, `TORN_REPLY`, …). That is the COW contract. MCP `gbridge_ask` is a thin wrapper over the same call — next slice, already named in T1_ARCH.
- **R3.** GitHub/GitLab/Cursor APIs are real, but they are **not** GBt APIs. Using them as a GBt channel would be a fabricated compliance story (a CI green that never touched the team).
- **R4.** Files on the native volume do not require Actions minutes, Copilot seats, Duo Premium, or Cursor API credits. API-second remains `XaiApiTransport`.
- **R5.** `builds/gbridge` already exists.
- **R6.** If xAI ships a Bot/Teams run API, it becomes a third injected transport; COW still calls `ask()`.

**Do not** add GitHub Actions or GitLab CI as a “sync” layer in front of the mailbox. That is mailbox-plus-poll-plus-runner, strictly worse.

### What to use from each domain *instead* (if the goal slips from “that team” to “a Grok/agent reply”)

These are **substitutes**, not T1 identity:

1. **Grok reasoning, documented, blocking, no grok.com team:** `grok --no-auto-update -p "…" --output-format json` **or** `POST https://api.x.ai/v1/responses` with `Authorization: Bearer $XAI_API_KEY`. Prefer Responses as the HTTP shape (current xAI quickstart). Keep Chat Completions if an existing OpenAI-compatible client is already wired (`gw-api` / `sgh-api` rails).
2. **Durable agent + blocking wait, not GBt:** Cursor Python SDK `Agent.prompt` / `run.wait()`, auth `CURSOR_API_KEY`. Only if Keith explicitly accepts a **Cursor** agent in place of GBt.
3. **Inbound ping of a grok.com *automation* (not a reply to COW):** Automations webhook `POST` → `202`. Useless for T1’s request/response unless xAI later documents a result fetch.

### Smallest next build (still no new vendor)

1. Keep mailbox as primary (`gbridge ask --root <handed-in>`).
2. Add the deferred **MCP stdio tool** `gbridge_ask` so COW blocks on a native tool that is still the team.
3. Leave `XaiApiTransport` as the documented HTTP fallback when the key is present — model, not team.
4. Re-check on a cadence (see sources): Grok Bot API, Cloud Agents ↔ Bot ID mapping, Teams/Assistants on docs.x.ai.

---

## UNKNOWN / do not invent

- Any REST path of the form `/v1/bots/{id}/messages` or `/v1/teams/{id}/runs` on `api.x.ai` or grok.com.
- Whether a Grok Bot teammate ID is a Cursor `bc-*` Cloud Agent.
- Whether grok.com custom “GrokBot QA” (mailbox team) is the same product as Grok Bot (Cursor app). Treat as **separate** until a vendor sentence says otherwise.
- Numeric rate limits for xAI / Cursor Cloud Agents / Copilot tasks (account-specific).
- Whether `workflow_dispatch` **always** returns 200+`workflow_run_id` or only with `return_run_details`.
- A first-party MCP **server** that *is* Grok Bot (xAI documents MCP in the other direction).
- Automations webhook returning the automation’s output in the HTTP response (docs say 202 + async start).
- Linux Grok Bot desktop app (docs say none; anecdotal .deb reports are not evidence).

---

## Sources (fetched 2026-08-25)

**Prior T1 packets:** `docs/research/T1_SYNC_GBOT_COW/research_{grok,openai,gemini}.md` · `docs/T1_ARCH.md` · `builds/gbridge/README.md`

**xAI / Grok**  
- https://docs.x.ai/grok-bot/overview · https://docs.x.ai/grok-bot/get-started · https://docs.x.ai/grok-bot/bots · https://docs.x.ai/grok-bot/teams-and-enterprises  
- https://docs.x.ai/developers/quickstart · https://docs.x.ai/  
- https://docs.x.ai/build/overview · https://docs.x.ai/build/cli/headless-scripting · https://docs.x.ai/build/cli/reference  
- https://docs.x.ai/grok/automations/webhooks  
- https://docs.x.ai/developers/tools/remote-mcp  

**Cursor**  
- https://cursor.com/docs/api  
- https://cursor.com/docs/cloud-agent/api/endpoints  
- https://cursor.com/docs/sdk/python  

**GitHub**  
- https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event  
- https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event  
- https://github.blog/changelog/2026-02-19-workflow-dispatch-api-now-returns-run-ids/  
- https://cli.github.com/manual/gh_workflow_run · https://cli.github.com/manual/gh_run_watch  
- https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-via-the-api  
- https://github.blog/changelog/2026-06-04-agent-tasks-rest-api-now-available-for-copilot-pro-pro-and-max/  

**GitLab**  
- https://docs.gitlab.com/api/pipelines/  
- https://docs.gitlab.com/api/pipeline_triggers/ · https://docs.gitlab.com/ci/triggers/  
- https://docs.gitlab.com/cli/ci/run/ · https://docs.gitlab.com/cli/ci/status/  
- https://docs.gitlab.com/api/duo_agent_platform_flows/  

Re-check those URLs before any implementation; beta surfaces (Cursor v1, Copilot tasks, Duo Flows) can move.
