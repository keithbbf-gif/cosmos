# GitHub / OpenAI Codex as a COSMOS coder+vetter rail — research + proposal

Source: SSA research 2026-08-26 (present-day GitHub/OpenAI docs). Vendor-plural: an
OpenAI-family coder/vetter that can DISAGREE with G46/Grok + Cursor.

## What it is
GitHub **Agent HQ** (public preview → GA'ing to Business/Pro through H1 2026): assign a
GitHub issue to **OpenAI Codex** (or Claude, or Copilot's own agent) from the Assignees
dropdown + pick the model. The OpenAI agent runs in a GitHub Actions sandbox on a branch
and opens a PR — the same shape COSMOS already uses for Cursor Cloud Agents.

## Headless-assignable? YES (public preview — probe before binding)
- **Agent Tasks API:** `POST https://api.github.com/agents/repos/{owner}/{repo}/tasks`
  body `{"prompt","base_ref":"main","model":"<openai-model>","create_pull_request":true}`;
  poll `GET /agents/repos/{owner}/{repo}/tasks/{id}`; list `GET /agents/tasks`.
  Headers: `Accept: application/vnd.github+json`, `X-GitHub-Api-Version: 2022-11-28`,
  `Authorization: Bearer <token>`.
- **Auth constraint:** USER-to-server token only (PAT / OAuth / GitHub App *user* token).
  App *installation* tokens are REJECTED (Copilot bills per user).
- **Assign-issue path (GraphQL):** `suggestedActors(capabilities:[CAN_BE_ASSIGNED])` →
  bot login `copilot-swe-agent`, node id → `replaceActorsForAssignable`/`addAssignees…`
  with optional `agentAssignment{baseRef,customInstructions,model,customAgent}`.
  Header `GraphQL-Features: issues_copilot_assignment_api_support,coding_agent_model_selection`.

## Vetter
- PR-reviewer API does NOT accept Copilot/Codex as a reviewer. Use a **ruleset**
  ("Automatically request Copilot code review") so every G46/Cursor PR auto-gets a
  cross-vendor review; read comments back via the PR-reviews API.
- Cleaner for the "disagreeing reviewer" canon: **Codex CLI** `codex exec --sandbox
  read-only --output-schema <schema.json>` (diff on stdin) → machine-readable
  approve/request-changes + findings for the critics/consensus stage.

## Access + cost
- GitHub-embedded Codex agent: **requires a Copilot seat** (Pro/Pro+/Business/Enterprise);
  "Codex included with your Copilot subscription" (no separate OpenAI bill). Since
  2026-06-01 metered via GitHub AI Credits; coding-agent runs also burn Actions minutes.
  **Not confirmed Keith holds a Copilot seat** — gate-zero probe pending.
- Direct Codex fallback: ChatGPT Plus/Pro OR OpenAI API key (`OPENAI_API_KEY`),
  independent of Copilot.

## Proposal (two small rails, mirror cosmos_cursor_rail.py; key in runtime-root file,
## never hard-coded/printed; both terminate at COSMOS's GitHub PR/approval gate)
- **SECONDARY (matches what Keith saw) — `--agent github-agent` in `cosmos_dispatch.py`:**
  dispatch via the Agent Tasks API (user PAT from `live\config\github_agent_token.txt`) →
  poll → PR into the existing GitHub gate. Needs a Copilot seat. API is public-preview: add
  a live probe as gate-zero, pin nothing.
- **PRIMARY (lowest dependency, buildable now) — `cosmos_codex_rail.py`:** drive the Codex
  CLI headless — coder `codex exec --sandbox workspace-write "<task>"` in an attempt-private
  clone → fenced commit → PR; vetter `codex exec --sandbox read-only --output-schema …`.
  Auth `OPENAI_API_KEY` from `live\config\openai_api_key.txt` (add to .gitignore deny-list).
- **Runtime-binding proof:** bind "done" to the emitted artifact — Codex `--output-last-message`
  final message + real model field; GitHub agent → the `task` object status + created PR URL.

## Disposition (COW)
1. Probe (gate-zero): is `copilot-swe-agent`/Codex assignable on `keithbbf-gif/cosmos`?
   → confirms the Copilot path via artifact.
2. If Copilot seat present → hand G46 the `github-agent` rail (closest to what Keith saw).
   If not → build `cosmos_codex_rail.py` now (Codex CLI); it needs only an OpenAI key Keith
   drops at runtime.
