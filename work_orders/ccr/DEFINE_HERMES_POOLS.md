# DEFINE — Hermes credential pools + provider routing

Keith: *We need this.* URLs: hermes-agent credential-pools, provider-routing, MCP.

**Not occupancy.** Do not `curl|bash` Ori. Do not `hermes auth add` from this TUI (Keith pastes keys). Do not write `~/.hermes/auth.json` from orch. Gitur later if CORE must know the pool.

## Why

GLM Flash **429 DeepInfra** is same-provider exhaustion, not “wrong model.” Naked `OpenRouterRail` has **one** key and `allow_fallbacks: false` — first 429 dies. Hermes **credential pools** rotate **same provider** (OR keys `_2`, `_3`) before fallback. **Provider routing** `ignore: ["deepinfra"]` is the GLM pin we already needed.

**Not** fallback-to-Anthropic. ANTHROPIC_OFF. Pools first, then named fallback only if Keith lists one.

## What we need (Hermes, when bound)

`~/.hermes/config.yaml`:

```yaml
provider_routing:
  sort: "price"
  ignore: ["deepinfra"]
  require_parameters: true
  data_collection: "deny"
  models:
    "z-ai/glm-5.3-flash":
      ignore: ["deepinfra"]
      order: ["z-ai"]   # if OR slug exists; else drop order and keep ignore
    "openai/gpt-5.6-luna":
      only: ["openai"]

credential_pool_strategies:
  openrouter: fill_first   # keep PREFIX cache on one key until 429
```

Env (Keith): `OPENROUTER_API_KEY`, `OPENROUTER_API_KEY_2`, … — Hermes auto-discovers numbered siblings. **fill_first** so we do **not** round-robin every call (that **busts prompt cache** — Hermes docs: rotation = full-price re-read).

429 plan-cap: rotate immediately. Transient 429: retry same key once, then rotate. 402: rotate, 1h cooldown.

## GLM Judge harness (corrected)

Not a naked OR chat as the *named* via once Hermes is on PATH (`cosmos_cred_kit` already probes `hermes` / `~/.hermes/.env`).

| Until `hermes` bound | After bound |
|---|---|
| `mouth:openrouter` degenerate (CALL_GLM_587.py) | via **`cli:hermes`** — Hermes is the harness; GLM is the **model**; OR is the **pool** |
| one key, 429 = FAIL | pool rotate; `ignore: deepinfra` |
| ITEM in prompt (no tools) | MCP tools **kind-gated**: JUDGE = read-only servers only; no `apply_patch` |

Hermes does **not** mean we call Codex/Claude/Cursor consumer UIs. MCP: `hermes mcp add codex --preset codex` is optional **stdio to Codex MCP**, not Luna’s Judge seat. Luna Judge stays `codex exec`. GLM Judge stays Hermes+OR **or** mouth until Hermes is installed.

## Cache vs rotate

fill_first + one OR key until exhausted = PREFIX cache lives. round_robin every call = **cache die**. Do not round_robin GLM Judge.

## Gitur later

CORE: `cosmos_cred_kit` already lists hermes. Optional: read pool health, never write secrets. WO HOLD until Judge.

Keith: keys in env/Bitwarden, not chat. Not this TUI.

## xAI Grok OAuth (wishlist)

https://hermes-agent.nousresearch.com/docs/guides/xai-grok-oauth  
Provider `xai-oauth`. Device code at `accounts.x.ai`. SuperGrok **or** X Premium+. **No `XAI_API_KEY` required** for that path. Transport = Responses-style (`codex_responses`) — reasoning, tools, **prompt cache**. Default model **`grok-4.6`**. Also `grok-build-0.1`. Tokens in `~/.hermes/auth.json`.

**Not extra `grok.exe`.** Not Coder-6 Cursor Gitur (that DUD stays Cursor BUILD). This is a **future via** if Hermes is the harness and Keith logs in (`hermes auth add xai-oauth`). Keith does the browser. Orch does not.

**403 after login:** xAI may gate OAuth API (`#26847`). Fallback `XAI_API_KEY` + `provider: xai` — Keith’s money.

**OAuth over SSH:** https://hermes-agent.nousresearch.com/docs/guides/oauth-over-ssh  
`xai-oauth` = **device code, no tunnel**. Loopback tunnel (`ssh -L`) is for Spotify / remote MCP only. OpenRouter over SSH = paste-the-code, no tunnel.

## Worktree UI (wishlist / analog)

https://hermes-agent.nousresearch.com/docs/developer-guide/worktree-ui-dev  
`htui`/`hgui` = Hermes **own-repo** worktrees sharing `node_modules`. Analog to our **isolated DUDs worktrees** (`live/work/codex/hero-*`). Do not install Hermes desktop from this TUI. `HERMES_HOME` shared across slots = **don’t dual-write** the same session (one-writer).

## Architecture analog (parked 2026-09-18 TidyUP — do not install)

Mapped from Hermes architecture + agent-loop + prompt-assembly + provider-runtime + tools-runtime + context-compression + session-storage + acp-internals. **No install. No spawn. No `hermes auth add`.** Compaction is not TidyUP.

| Hermes | COSMOS analog |
|---|---|
| Prompt assembly **stable → context → volatile** | P11: legend PREFIX (Role→Enviro) vs Mission tail. Exact byte match on prefix. No dates/UUIDs in PREFIX. |
| API modes `chat_completions` / `codex_responses` / `anthropic_messages` | GLM/OR = `chat_completions` (mouth until `cli:hermes`). Luna/Codex = **`codex_responses`** (`codex exec` Flex). **anthropic_messages OFF.** |
| 70+ tools; Daytona as a Hermes terminal backend | COSMOS Daytona is HOLD. Kind-gate (JUDGE read-only; ORC no coding-write) — do not dump 70 tools into a Judge. |
| Compression 50% / 85% | Do not bind COSMOS TidyUP / SEED / WD2 to Hermes compression. |
| Compaction archives `active=0` (not delete) | Same as `_delme` never-unlink. |
| Credential pools before fallback | This DEFINE. `fill_first`. `ignore: ["deepinfra"]`. |
| SQLite `state.db` WAL; `HERMES_HOME` not HOME | Named profiles. One writer. Dual-write the same `HERMES_HOME` = two-writer scar. |
| ACP = sync AIAgent in async JSON-RPC stdio | Do not make a COSMOS ACP. Optional later. |
| Hermes cron | **Do not bind COSMOS WD2 / 15s clock to Hermes cron.** Windows clocks stay COSMOS-native. |

Kelly Vertex today = `apikey` `region: global` (`orders.ggn`, `project-10b3a132`). Hermes Vertex later = OAuth2 / SA JSON, same `global`. Not this TUI.
