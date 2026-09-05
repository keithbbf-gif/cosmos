# ANTHROPIC HANDS — G46 scout return (Claude / Anthropic platform)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25 (docs fetched live).
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim except where a COSMOS artifact is named.
**No COSMOS core code was edited.** Maker-docs sweep (DHx assignment log): each maker's hands → `docs/research/<MAKER>_HANDS.md`.

**Already on the mesh (do not re-add as "new"):** native `claude -p` is the Opus brain (`cosmos/cosmos_brain.py`) and Keith's standing coding default (`docs/ROUTING.md`: **CC/F5 — Claude Code**). Maker map seeds `claude-agent-tool`. Claude is **not** a Dispatcher `ApiRail` today — MESH_ADDITIONS row 17 named that gap. This file inventories every Anthropic **hand** COSMOS could fire, including the ones already wired.

**Filter:** a surface with no hands is rejected. Every row is an **action** COSMOS could fire: REST endpoint, CLI flag, SDK call, MCP tool, hook, skill/slash command, GitHub Action / GitLab CI job, or DOM fallback. Chat-only is out.

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks. Equal power, cheaper wins. Metered Messages API sits **below** the prepaid Claude Code / free MCP cluster even when the model is the same family.

---

## How COSMOS reaches Anthropic (reach column, one pattern)

Core stays sole ledger writer. Anthropic is reached as:

| Lane | Mechanism | When |
|------|-----------|------|
| **A. Native Claude Code CLI** | `claude -p` / `--print` inside an attempt-private workspace. Already the Opus brain. JSON via `--output-format json`. | Default. Prepaid subscription quota. Matches "no bats — in-app / COSMOS action." |
| **B. Agent SDK (Python)** | `claude_agent_sdk.query()` / `ClaudeSDKClient` — same agent loop as the CLI, in-process. Bundles the Claude Code binary. | When COSMOS needs structured messages, permission callbacks, MCP servers as objects — not subprocess text. |
| **C. HTTP through spend-gate** | `POST https://api.anthropic.com/v1/messages` (+ batches, files, skills, sessions). Header `x-api-key` + `anthropic-version: 2023-06-01`. | Metered fallback when Claude Code weekly quota is dry. Real money. |
| **D. MCP-client / MCP-server** | Claude Code is an MCP **host**. COSMOS can also be a host (official Python/TS SDKs) or expose Core as an MCP **server**. Messages API MCP connector talks to remote HTTP MCP without a local client. | Agent brains get forge/browser/search tools. Core should prefer native `claude`/`gh`/`glab` over giving itself a shell via MCP. |
| **E. Forge CI** | `anthropics/claude-code-action` (GitHub) or Claude Code GitLab CI. Trigger `@claude` or `prompt:` automation. | Overflow coding on `keithbbf-gif/cosmos`. Lease so it does not double-write with Cursor Cloud Agents. |
| **F. DOM** | claude.ai / Console billing, App install consent, first OAuth — everything the API cannot do when AUTH_REQUIRED. | Fallback only. Canon: DOM first when the API depends on something that can run out (weekly quota, key expiry). |

Keith owns credentials. Store under `live/config/` (git-ignored). Never hard-code. Never print a key in full. Fenced commit still gates any tree write.

---

## Auth primer (all API/CLI rows inherit this unless overridden)

Base: `https://api.anthropic.com`. Required header on every API call: `anthropic-version: 2023-06-01`.

| method | credential | header | COSMOS use |
|--------|------------|--------|------------|
| **Claude Code `/login`** (Pro/Max/Team/Enterprise) | OAuth in `%USERPROFILE%\.claude\.credentials.json` (Windows) | CLI manages it | Default for `claude -p`. Draws **seat allowance**, not Console API spend. |
| **`claude setup-token`** | One-year `CLAUDE_CODE_OAUTH_TOKEN` | CLI env | CI / headless where browser login is unavailable. Model requests only. **`--bare` does not read this.** |
| **API key** | `sk-ant-api…` | `x-api-key` | Metered Messages / Files / Batches / Skills. Env `ANTHROPIC_API_KEY`. In `-p` mode the key is **always used when present** (outranks subscription). |
| **Admin API key** | `sk-ant-admin…` | `x-api-key` | Org members, workspaces, usage/cost, API-key inventory. **Org accounts only** — not individual. |
| **`org:admin` OAuth** | Bearer from `ant auth login --scope org:admin` | `Authorization: Bearer` | WIF / service accounts / federation rules. Required for those Admin endpoints; Admin API keys are **rejected** there. |
| **Workload Identity Federation** | Short-lived token from `POST /v1/oauth/token` | `Authorization: Bearer` | Production / GitHub Actions OIDC. No long-lived `sk-ant-api` in the environment. |
| **MCP OAuth** | Per-server access token (`claude mcp login`, or `/mcp` in session) | MCP transport | Remote MCP (GitHub, Sentry, Notion, …). `-p` cannot complete the browser flow — sign in interactively first. |

**Precedence inside Claude Code** (official, highest first): cloud-provider flags → `ANTHROPIC_AUTH_TOKEN` → `ANTHROPIC_API_KEY` → `apiKeyHelper` → `CLAUDE_CODE_OAUTH_TOKEN` → Anthropic profiles / WIF → `/login` subscription. A leftover `ANTHROPIC_API_KEY` **steals** the session off the prepaid seat. `/status` is ground truth for which method is live.

**`--bare`:** recommended for scripted `-p`. Skips hooks/skills/MCP/CLAUDE.md auto-discovery. **Does not** read OAuth / keychain / `CLAUDE_CODE_OAUTH_TOKEN`. Set `ANTHROPIC_API_KEY` or an `apiKeyHelper`.

---

## ARCH env isolation (additive, 2026-08-25) — H5

Two-wallet theft is documented: a leftover `ANTHROPIC_API_KEY` in the `claude -p` environment **steals** the prepaid seat. `live/config/` this pass has **no** `ANTHROPIC_API_KEY` (safer for the seat; means there is also **no** COSMOS-owned metered Messages credential).

**ARCH rule:** queue jobs that should draw the seat **unset** `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN`. Metered `anthropic-api` (WAVE D1 / MESH #17) is a **different** job env that **sets** a workspace-scoped key. Do not mix. Dispatcher `ApiRail` waits on Kernel attach. `--bare` for unattended jobs. This is **not** a stage-6 pass.

---

## Host bind (additive, 2026-08-27 s6 re-probe) — H5 still holds

This process: `claude` **2.1.220** on PATH. `live/config/` still has **no** Anthropic key file. Seat-path jobs still unset `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN`. WAVE D1 `anthropic-api` stays dark (Keith mints `sk-ant-api`; different job env). Not a stage-6 pass.

---

## Cost floor (subscription vs API — do not conflate)

Two wallets. Mixing them in a spend plan is how F5 gets burned by accident (`ROUTING.md`: F5 = Claude Code, **not** Cowork).

| Wallet | What official docs say | COSMOS note |
|--------|------------------------|-------------|
| **Claude Pro / Max / Team / Enterprise seat** | Claude Code usage draws a **per-seat allowance** that resets on a rolling **5-hour window** and a **weekly window**, shared with Claude chat and Cowork. Size depends on seat tier. Usage **inside** the allowance is not metered in dollars. | This is the prepaid coding lane. Keith's 2026-08-25 snapshot (DHx / ROUTING): Fable **80%**, all-models **61%**, resets Sun 6:59 AM; usage credits **$58.06 / $78**. Re-read `/usage` — do not quote those numbers stale. |
| **Usage credits** | Extra spend past the seat ceiling. Pro/Max: `/usage-credits` → claude.ai Settings > Usage. Team/Enterprise: admin. | Already on. Auto-reload. Real money after the seat is gone. |
| **Claude Console API** | Per-token list rates at [platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing). New users: "a small amount of free credits." Then fully metered. | The missing Dispatcher rail (MESH_ADDITIONS #17). Budget-gate it. |
| **Claude Code workspace (Console)** | Auto-created on first Console sign-in to Claude Code. Per-user keys; you cannot mint keys in it by hand. Isolated rate limits. | If Keith ever points `claude` at Console billing, this workspace is the spend bucket. Archiving it **disables Console-billed Claude Code for the whole org**. |
| **Batches API** | **50% off** input and output vs list. Most batches finish &lt;1 hour; expire at 24h. Results live 29 days. | Bulk eval / port-backlog critique. Stacks with prompt-cache discounts. |
| **Prompt cache** | Write 1.25× (5 min) or 2× (1 h); **read 0.1×**. | Claude Code manages this automatically. API must set `cache_control`. |
| **Web search (server tool)** | **$10 / 1,000 searches** + tokens. Errors not billed. | Do not enable on a COSMOS loop without a spend cap. |
| **Web fetch (server tool)** | **$0 extra** — tokens only. | Prefer this over search for known URLs. |
| **Code execution** | **Free** when `web_search` or `web_fetch` is in the same request. Else: 1,550 free container-hours/org/month, then **$0.05 / hour / container**. | Files preloaded onto the container start the clock even if the tool is not called. |
| **Managed Agents session runtime** | Tokens at list + **$0.08 / session-hour** while status is `running`. Idle does not count. | Replaces code-execution container-hour billing for that product. |
| **Files API ops** | Upload / list / metadata / delete / download = **$0**. Content used in Messages = input tokens. 500 MB/file, 1 TB/org. ~500 req/min. | Storage is free; inference is not. |
| **MCP protocol / official SDKs** | **Free** (Apache/MIT OSS). | Tokens still bill when a model *uses* a tool. |
| **Admin API** | **Free** to call. Does not create API keys (Console only). | Org accounts. Individual Console accounts: unavailable. |

**List rates fetched 2026-08-25** from [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) (USD / million tokens). Sonnet 5 introductory $2/$10 is now the **standard** price (the Sep 1, 2026 bump to $3/$15 **will not occur**).

| Model | Input | Cache hit | Output | Batch in / out |
|-------|-------|-----------|--------|----------------|
| Fable 5 | $10 | $1 | $50 | $5 / $25 |
| Opus 5 / 4.8 / 4.7 / 4.6 / 4.5 | $5 | $0.50 | $25 | $2.50 / $12.50 |
| Sonnet 5 | $2 | $0.20 | $10 | $1 / $5 |
| Sonnet 4.6 / 4.5 | $3 | $0.30 | $15 | $1.50 / $7.50 |
| Haiku 4.5 | $1 | $0.10 | $5 | $0.50 / $2.50 |

Opus 5 / 4.8 **fast mode** (research preview, first-party API only): $10 / $50. Not available with Batches.

---

## Ranking table

| # | name | kind | HANDS (what it DOES) | auth | cost | power | how COSMOS reaches it |
|---|------|------|----------------------|------|------|-------|------------------------|
| 1 | **`claude -p` / `--print` (Claude Code CLI)** | CLI + agent | Headless agent loop on this machine: Read/Edit/Bash, multi-turn, resume, JSON/stream-json, `--json-schema`, `--allowedTools`, `--permission-mode`, `--bare`, `--continue`/`--resume`. Exit 0 on success. JSON envelope includes `result`, `session_id`, `total_cost_usd` (client estimate). **This is the coding hand Keith ordered.** Piped stdin cap 10 MB. | `/login` subscription (default) or `ANTHROPIC_API_KEY` (`-p` always uses the key if set). `--bare` needs the API key. | **prepaid** on Pro/Max/Team (seat + weekly window). Metered if an API key is in env. | **highest** | Native worker, already live: `cosmos_brain.py` runs `claude -p --output-format text --model opus`. Queue jobs: `claude --bare -p "…" --output-format json --allowedTools Read,Edit,Bash --permission-mode acceptEdits`. Capture `session_id` for `--resume`. Never a `.bat`. |
| 2 | **`--output-format json` / `stream-json`** | CLI | Structured result COSMOS can ledger: `type/subtype`, `result`, `session_id`, `is_error`, durations, `total_cost_usd`, per-model breakdown. `stream-json --verbose --include-partial-messages` emits token deltas + `system/init` (plugins, MCP servers, `plugin_errors`, `mcp_server_errors`) — **fail CI when a plugin/MCP did not load.** `--json-schema` puts validated JSON in `structured_output`. | same as row 1 | **included** | **highest** | `claude -p --output-format json "…" \| jq`. Bind every DONE claim to `result` + `session_id` + `is_error` (runtime binding / SCAR_PLACATION). Stream-json for KDash live. |
| 3 | **Claude Code as MCP host** | MCP client | `claude mcp add --transport http\|stdio\|sse\|ws`. Connects GitHub, GitLab, Notion, Sentry, Postgres, … Official transports: HTTP (preferred), stdio (local), SSE (deprecated), WebSocket. OAuth via `/mcp` or `claude mcp login`. Tool search deferred by default. Channels push CI/alerts into a running session. | MCP OAuth or `--header` / `--env` secrets. Workspace-trust dialog for project `.mcp.json` (skipped in `-p` — loads without asking). | **free** protocol; model tokens still bill | **highest** | Project `.mcp.json` committed (GitLab MCP `https://gitlab.com/api/v4/mcp`, GitHub `https://api.githubcopilot.com/mcp/`). For `-p`/CI, disable untrusted project servers via `disabledMcpjsonServers` or `--bare` + `--mcp-config`. COSMOS agents get forge hands without Core growing a GitHub client. |
| 4 | **MCP spec + official SDKs** | spec + SDK (OSS) | Open JSON-RPC protocol. Latest spec **2026-07-28**. Server features: tools, resources, prompts. Client features: elicitation, sampling, roots. Transports: **stdio** (SHOULD) and **Streamable HTTP**. Official SDKs: TypeScript/Python/C#/Go/Rust **Tier 1**; Java/Ruby Tier 2. COSMOS can be a **host** (talk to servers) or a **server** (expose ledger/queue/status as tools). | none for the spec. Server auth is per-server (OAuth 2.1 for HTTP). | **free** (OSS) | **highest** | Python: `pip install mcp`. COSMOS MCP-client worker for agent brains; optional Core MCP **server** so Claude Code / Cursor / G46 can call `cosmos_status` / `submit` without scraping KDash. Fail-closed: never let an untrusted server write the live tree. |
| 5 | **Claude Code hooks** | hooks + CLI | Deterministic shell (or HTTP / prompt / agent) at lifecycle points: `PreToolUse`, `PostToolUse`, `PermissionRequest`, `Stop`, `SessionStart`/`SessionEnd`, `Notification`, `PreCompact`, `FileChanged`, … Exit 2 blocks. JSON `permissionDecision: allow\|deny\|ask`. Matcher on tool name (`Bash`, `Edit\|Write`, `mcp__.*`). **This is a gate that executes.** | local settings (`.claude/settings.json`, `~/.claude/settings.json`). `-p` **runs project hooks with no trust dialog** unless `--bare`. | **included** | **highest** | Project hooks: format after Edit; block `.env` writes; `Stop` hook posts a JSONL line COSMOS's return-watcher can ingest; `PreToolUse` deny `Bash(rm *)`. `--bare` for CI that must not inherit a teammate's `~/.claude`. HTTP hooks → Core URL (Tailscale / `cosmos up`). |
| 6 | **Skills / slash commands** | skill + CLI | `.claude/skills/<name>/SKILL.md` (Agent Skills standard) or `.claude/commands/*.md`. Invoke `/name` in a prompt — **works in `-p`**. Frontmatter: `allowed-tools`, `disable-model-invocation`, `context: fork`, `$ARGUMENTS`. Bundled: `/code-review`, `/doctor`, `/debug`, `/verify`, `/loop`. Dynamic `` !`cmd` `` injection. | same as Claude Code. `-p` expands `/skill-name` before the run. | **included** (tokens when invoked) | **highest** | Commit COSMOS skills: `/cosmos-py-compile`, `/cosmos-fence-check`, `/chapter-citation`. Dispatch: `claude -p "/code-review $PR"`. Keep CLAUDE.md &lt;200 lines; park procedures in skills (loads on demand). |
| 7 | **Agent SDK — Python** (`claude-agent-sdk`) | SDK + agent | Same tools, agent loop, and context management as Claude Code, in-process. `query()` async iterator; `ClaudeSDKClient` for bidirectional sessions. Bundles a native Claude Code binary (Windows: `claude.exe`). Options: `allowed_tools`, `permission_mode`, `mcp_servers`, `cwd`, hooks, subagents, structured output (Pydantic). | API key **required for third-party products** (Anthropic does not allow offering claude.ai login through the SDK). Env `ANTHROPIC_API_KEY`. | **metered API** if key; same as Claude Code if you violate that and use `/login` (not allowed for shipped products) | **highest** (programmatic) | `pip install claude-agent-sdk`. COSMOS Python worker. Prefer this over scraping CLI text when COSMOS needs tool-approval callbacks or typed `ResultMessage`. Do **not** expose Keith's `/login` through a COSMOS-shipped agent. |
| 8 | **Agent SDK — TypeScript** (`@anthropic-ai/claude-agent-sdk`) | SDK + agent | Same loop as row 7. `query()` async generator. In-process MCP servers, tool search, plugins, OpenTelemetry. | API key | same as row 7 | **high** | `npm i @anthropic-ai/claude-agent-sdk`. Use if a TS worker exists; Python is the COSMOS default. |
| 9 | **`--continue` / `--resume` / sessions** | CLI | Continue last conversation or a specific `session_id`. Sessions are findable **by ID across directories** (v2.1.223+). `--from-pr` picks the session that opened a PR. Checkpoints / `/rewind`. | same as row 1 | **included** (tokens per turn) | **high** | `cosmos_brain.py` already maps COSMOS sid → deterministic Claude session UUID. Queue: capture `session_id` from JSON, `--resume` for multi-step jobs (review → fix → commit). |
| 10 | **`--allowedTools` + permission modes** | CLI | Auto-approve named tools. Modes: `auto` (classifier), `dontAsk` (deny unless allowlisted — **CI lock**), `acceptEdits` (files + common fs cmds). Rule syntax: `Bash(git diff *)`. | same | **included** | **high** | Headless COSMOS jobs: `--permission-mode dontAsk --allowedTools "Read,Bash(git status *),Bash(git diff *)"` for read-only review; `acceptEdits` for fenced attempt workspaces only. |
| 11 | **Claude Code GitHub Action** (`anthropics/claude-code-action@v1`) | Actions + agent | `@claude` on issues/PRs → clone, edit, push, comment. Automation `prompt:` on any event (cron, `pull_request`, `workflow_dispatch`). Skills, plugins, `claude_args`. OIDC WIF so **no long-lived key**. | `ANTHROPIC_API_KEY` **or** `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`) **or** WIF (`anthropic_federation_rule_id`). Actor must have write access; bots blocked unless `allowed_bots`. | **prepaid** if OAuth token (Keith's seat); **metered** if API key. Plus GitHub Actions minutes (public = $0). | **high** | Workflow on `keithbbf-gif/cosmos`. Prefer WIF. Lease vs Cursor Cloud Agents — do not double-dispatch the same issue. `/install-github-app` is Keith's one-time setup (he runs it). |
| 12 | **Claude Code GitLab CI** | CI + agent | Official GitLab CI integration: Claude Code in a pipeline job (MR comment / `CI_JOB` prompt). Same agent loop on a runner. | job env `ANTHROPIC_API_KEY` or OAuth token | same as row 11 + GitLab minutes (400 hosted; **0** on a project runner) | **high** | `.gitlab-ci.yml` job on a **self-hosted project runner** (GITLAB_HANDS #1) so it does not burn the 400. Pair with GitLab MCP. |
| 13 | **CLAUDE.md / memory** | config | Persistent project instructions loaded every session. Auto-memory. Nested files in monorepos. | none | **included** (tokens every turn — keep it short) | **high** | Repo already has `CLAUDE.md` (BootUP + canon). That **is** a hand: every `claude -p` in this tree inherits it unless `--bare` / `--system-prompt`. Do not dump the 135-tool backlog into it — use skills. |
| 14 | **Files API** | REST | `POST /v1/files` upload (multipart, ≤500 MB) → `file_id`. Reference in Messages as `image` / `document` / `container_upload`. List / metadata / delete. Download **only** files Claude generated (skills / code execution). Workspace-scoped — **any key in the workspace can read any file.** | API key | **ops free**; content in Messages = input tokens. 1 TB/org. | **high** | Spend-gate HTTP. Upload a dissertation PDF / exhibit once, pass `file_id` across turns (avoids re-sending base64 every turn). One workspace per tenant if COSMOS ever serves more than Keith. Never accept a user-supplied `file_id`. |
| 15 | **Messages API** (`POST /v1/messages`) | REST | Stateless conversational inference. Full history each call. Content blocks: text, image, document, tool_use/tool_result, thinking. Streaming. Structured outputs. Token counting sibling `POST /v1/messages/count_tokens`. Request cap 32 MB. | API key or WIF. Headers: `x-api-key`, `anthropic-version: 2023-06-01`. | **metered** list rates. Small new-account credits only. | **high** (fallback rail) | New `ApiRail` `link_id="anthropic-api"`, spend-gated. Use when Claude Code weekly quota is dry **and** the task is not a coding-agent loop (that's still Cursor/Grok Build). Official SDKs: `anthropic` (Python), `@anthropic-ai/sdk` (TS), plus Go/Java/C#/PHP/Ruby, and `ant` CLI. |
| 16 | **Tool use / function calling** | API feature | Claude returns `stop_reason: "tool_use"` + `tool_use` blocks; COSMOS executes client tools and sends `tool_result`. Server tools (web_search, web_fetch, code_execution, MCP connector, advisor, tool_search) run on Anthropic. `tool_choice` auto/any/tool/none. `strict: true` schema conformance. Parallel tools. Tool Runner in the SDK executes the loop for you. | API key | tokens + optional server-tool fees | **high** | Messages rail with COSMOS-defined tools wrapping `cosmos_lock` / ledger / queue (read-only first). Prefer Claude Code/Agent SDK when the tools are filesystem/bash — don't reimplement that loop. |
| 17 | **Prompt caching** | API feature | `cache_control: {type: "ephemeral"}` top-level (automatic) or on blocks (explicit, max 4 breakpoints). 5 min TTL default; `ttl: "1h"` at 2× write. Automatic prefix lookback of 20 blocks. Min cacheable length model-dependent (512–4096 tokens). Workspace-isolated. `max_tokens: 0` pre-warms. | API key | write 1.25×/2×, **read 0.1×**. Stacks with Batches 50%. | **high** (cost) | Required on any repeated COSMOS system prompt (canon, SEED facts, CLAUDE.md-shaped instructions). Check `usage.cache_read_input_tokens`. Claude Code already caches for free on the CLI path. |
| 18 | **Vision + PDF** | API feature | Images: JPEG/PNG/GIF/WebP as base64, URL, or `file_id`. Up to 600 images/request (100 on 200k-context models); 20 on claude.ai. PDFs as `document` blocks (text + vision of pages). Citations optional. | API key | image tokens = `⌈w/28⌉×⌈h/28⌉` visual tokens × model input rate | **high** | Files API + Messages. Exhibit photos, Lindau plates, KDash screenshots, CI failure screenshots. Prefer `file_id` in multi-turn. Claude **cannot generate/edit** images. |
| 19 | **Thinking / extended thinking** | API feature | Adaptive thinking on current models (on by default on Opus 5 / Sonnet 5 / Fable 5). `thinking: {type: "adaptive", display: "summarized"\|"omitted"}`. Manual extended thinking: `type: "enabled"` + `budget_tokens`. Effort levels. Interleaved thinking between tool calls. Encrypted `signature` must be round-tripped with tool results. Tokens billed as output even when display is omitted. | API key | output-token rates for full thinking, not the summary | **high** | Default on for hard review. `display: "omitted"` for COSMOS workers that don't surface CoT (faster TTFT, same bill). Pass thinking blocks back unmodified in tool loops. Fable 5 **cannot disable** thinking. |
| 20 | **Message Batches API** | REST | `POST /v1/messages/batches` up to 100k requests or 256 MB. Async, most &lt;1h, hard 24h. Poll `processing_status`; stream `.jsonl` results keyed by `custom_id`. Cancel supported. Almost every Messages feature works (vision, tools, thinking, MCP, cache). No streaming, no fast mode, no `max_tokens: 0`. | API key (workspace-scoped) | **50% off** in+out | **high** (bulk) | Overnight eval of the 135-tool port backlog / stage-5 critiques. COSMOS submit → batch → return-watcher on `ended`. Match results by `custom_id`, not order. |
| 21 | **Token Counting API** | REST | `POST /v1/messages/count_tokens` — count before send. Same shape as Messages. | API key | **free** (count only) | **high** (infra) | Spend-gate preflight: refuse a job that would blow the remaining Claude Code window or the API budget. Complements `usage` on live responses. |
| 22 | **Web fetch (server tool)** | server tool | Anthropic fetches a URL / PDF into context. `web_fetch_20260209`. `max_content_tokens` cap. | API key | **$0 extra** + tokens (~2.5k tok / 10 kB page) | **high** | Grounded Opus without SGH DOM when the URL is known (docs.anthropic.com, a DOI landing page). Safer than web_search on cost. |
| 23 | **Web search (server tool)** | server tool | Live web search with citations. `web_search_20260209`. | API key | **$10 / 1k searches** + tokens | **med-high** | Only with a hard cap. SGH DOM remains the prepaid search rail. Batches throttle search per org automatically. |
| 24 | **Code execution (server tool)** | server tool | Python + bash in an Anthropic container. Generate files → Files API download. | API key | free with web_search/fetch; else 1,550 h/mo then $0.05/h | **high** | Spreadsheet/PDF skills, data plots, running a snippet **without** giving the model Keith's shell. Not a replacement for attempt-private workspaces. |
| 25 | **MCP connector (Messages API)** | API beta | `mcp_servers: [{type: url, url, name, authorization_token}]` + `tools: [{type: mcp_toolset, mcp_server_name}]`. Anthropic is the MCP client. Allowlist/denylist per tool. Multiple servers per request. Beta header `mcp-client-2025-11-20`. **Tools only** (no prompts/resources). Server must be public HTTPS (Streamable HTTP or SSE). No local stdio. | API key + MCP bearer. Header `anthropic-beta: mcp-client-2025-11-20`. | tokens; **not ZDR-eligible** | **high** | Cloud-agent path: Messages rail talks to GitLab/GitHub MCP without COSMOS hosting an MCP client. Local stdio servers stay on Claude Code / Agent SDK. |
| 26 | **Client-side MCP helpers** | SDK | `anthropic[mcp]` / `@anthropic-ai/sdk/helpers/beta/mcp`: convert MCP tools/prompts/resources ↔ Claude types; Tool Runner executes them. | API key + local MCP session | tokens | **high** | COSMOS Python worker already speaking MCP (Playwright, GitLab) can feed those tools into Messages without hand-rolling converters. |
| 27 | **Skills API** | REST | `POST /v1/skills`, versions, list, delete. Upload Agent Skills for the API / Managed Agents (frontmatter restricted to spec fields). | API key | tokens when used | **med-high** | Promote a proven Claude Code skill to the API rail so Cowork-less workers share it. Not needed until the Messages rail exists. |
| 28 | **`ant` CLI (Claude Platform CLI)** | CLI | Official Console CLI: `ant messages create`, `ant files upload`, `ant messages:batches`, `--format jsonl`, `--transform` GJSON. Profiles, `ant auth login --scope org:admin`. | API key / OAuth profile | **free** CLI; API usage bills | **med-high** | Native worker alternative to curl for the metered rail. Distinct from `claude` (Claude Code). |
| 29 | **Models API** | REST | `GET /v1/models` list + retrieve. Ground-truth model IDs. | API key | **free** | **med** | Probe before dispatch so COSMOS never hard-codes a retired ID (`claude-opus-4-1` etc.). |
| 30 | **Workspaces + Admin Workspaces API** | Admin REST | Create/list/archive workspaces; members; spend + rate limits per workspace. IDs `wrkspc_…`. Max 100/org. Default workspace cannot be renamed. Response header `anthropic-workspace-id`. | Admin API key `sk-ant-admin…` | **free** to call | **high** (hygiene) | Isolate `anthropic-api` spend from Claude Code Console workspace. Cap the metered rail so it cannot starve production. |
| 31 | **Admin API (members, invites, keys)** | Admin REST | List/update/remove org users; invite by email (21-day expiry); list/update API keys (`expires_at`); **cannot create keys** (Console only); cannot remove admins. | Admin key or `org:admin` bearer. **Org accounts only.** | **free** | **med-high** | Inventory keys, expire unused, offboard. Keith does money/credentials; COSMOS can *report*. |
| 32 | **Usage and Cost API** | Admin REST | `GET /v1/organizations/usage_report/messages` + cost report. Bucket by day, workspace, model. | Admin key | **free** | **high** (spend-gate) | Feed COSMOS spend-gate / KDash. Default workspace reports `workspace_id: null`. Bind claims to this, not `/usage` client estimates. |
| 33 | **Claude Code Analytics API** | Admin REST | Per-user Claude Code metrics (spend, accepted lines) for Console-billed orgs. | Admin key | **free** | **med** | Only if Claude Code is Console-billed. Seat-based Pro/Max: use claude.ai analytics / `/usage` instead. |
| 34 | **Rate Limits API + Spend Limits API** | Admin REST | Read org/workspace RPM/TPM; set spend limits; approve/deny increase requests. | Admin key | **free** | **med-high** | Fail-closed when remaining TPM is below a job's estimate (pair with token counting). |
| 35 | **Managed Agents (Agents + Sessions + Environments APIs)** | REST beta | Hosted agent harness: define a versioned agent, start a stateful session in Anthropic's sandbox, stream events, attach files, MCP, GitHub, scheduled deployments, webhooks. Anthropic runs the loop **and** the sandbox. | API key. Beta. First-party + Claude Platform on AWS. | tokens + **$0.08 / running hour**. No batch discount. | **med-high** | Overflow when COSMOS must not host the sandbox (untrusted prompt). Overlaps Claude Code — do not run both on the same tree write. Webhook → return-watcher. |
| 36 | **Computer use / browser use (API toolsets)** | API tools | `computer_toolset_20260801` / `browser_toolset_20260801`: screenshots, mouse, keyboard, a11y tree. Client executes; Anthropic publishes the schema. ~4.5k–6.6k extra input tokens for the toolset definition. | API key + COSMOS supplies the desktop/browser | tokens + image tokens | **med** | DOM-canon cousin. COSMOS already has SGH chrome-bridge / Playwright MCP — vendor-plural, not default. Claude Code CLI also has computer-use (macOS) and Chrome. |
| 37 | **Bash / text-editor / memory tools (API)** | API tools | Anthropic-schema client tools: persistent bash, file editor, cross-conversation memory files **you** host. | API key + COSMOS executes | tokens (bash +244–325, text_editor +700) | **med** | Only if COSMOS is implementing its own agent loop on Messages. Agent SDK already has Read/Edit/Bash. |
| 38 | **Claude Code on the web / `--cloud` / routines** | cloud agent | Browser/phone sessions against a GitHub repo; `--teleport` between web and terminal; **routines** (schedule, API trigger, GitHub events) on Anthropic cloud. `POST` trigger-a-routine API. | claude.ai login | **prepaid seat** | **med-high** | Deep URL for Keith. `claude --cloud` from CLI queues into a cloud session (with `-p` + session ID). Do not use as the Motif runtime-binding gate — that's Keith's machine. |
| 39 | **Self-hosted environments** | runner | Cloud-shaped Claude Code sessions on **Keith's compute**. Runner CLI, identity JWT `CLAUDE_CODE_SESSION_ACCESS_TOKEN`. | runner token | **prepaid** tokens + electricity | **med** | Only if cloud sessions must stay on-box (dissertation / live tree). Heavy ops. |
| 40 | **Plugins + marketplaces** | plugin | Package skills + agents + hooks + MCP. Official marketplace `anthropics/claude-plugins-official` (`mcp-server-dev`, `code-review`, security-guidance, Claude Security). | Claude Code session | **included**; tokens when used | **med** | `/plugin install code-review@claude-code-plugins`. Pin versions in managed settings for CI. |
| 41 | **Channels (MCP push)** | MCP extension | MCP server declares `claude/channel` and pushes CI/alerts into a live session (`--channels`). | MCP + Claude Code | **included** | **med** | GitLab pipeline webhook → channel → Claude Code session, as an alternative to Core's return-watcher. Don't build two authorities. |
| 42 | **Subagents / agent teams / worktrees** | CLI feature | Isolated subagents, `--worktree` git isolation, experimental agent teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, ~7× tokens). | same | tokens × N | **med** | Useful inside one `claude -p` for "review vs implement." Teams are expensive — leave off by default. |
| 43 | **Structured outputs + citations** | API feature | Schema-validated JSON; document citations with location. | API key | tokens | **med-high** | Batch critique results as JSON COSMOS can ledger without regex. CLI twin: `--json-schema`. |
| 44 | **Streaming Messages** | API feature | SSE event stream; required by SDKs when `max_tokens` &gt; 21,333. | API key | same as Messages | **med** | KDash live token view on the metered rail. |
| 45 | **PDF / document blocks** | API feature | Native PDF in Messages (not just Files). Citations. | API key | tokens (pages as images + text) | **med-high** | Dissertation / exhibit PDFs. Convert .docx→PDF for images; plain-text for .xlsx unless code execution. |
| 46 | **Bedrock / Vertex / Foundry / Claude Platform on AWS** | cloud API | Same models, provider IAM + billing. Feature lag vs first-party (no Files/MCP connector on Bedrock/Vertex). 10% regional premium on 4.5+. | AWS/GCP/Azure creds | cloud invoice (CCUs at $0.01 on Anthropic-operated marketplaces) | **med** | Only if Keith wants Claude on the existing Vertex $300 credit or AWS bill. Gemini already occupies Vertex. Don't split Claude across two bills without a reason. |
| 47 | **Compliance API / Activity Feed** | Admin REST | Audit chats, files, Claude Code artifacts; delete. Files API ops appear as `platform_file_*` activities when enabled. | Compliance setup + Admin key (Activity Feed only on Admin keys) | **Enterprise** | **low-med** | Skip until an Enterprise org exists. |
| 48 | **Inference hooks** | Admin | Org HTTP hooks on inference (pre/post). | org admin | Enterprise | **low** | Overlaps COSMOS spend-gate. Skip. |
| 49 | **App Attest** | auth | iOS/macOS apps call Messages without shipping a key. 1-hour tokens, Messages only. | Apple App Attest | tokens | **low** | Phone client would use Tailscale → COSMOS API, not App Attest. |
| 50 | **Completions API** | REST (legacy) | Old text-completion endpoint. | API key | metered | **do not use** | Messages replaced it. |
| 51 | **DOM on claude.ai / Console** | DOM | Billing, usage credits toggle, invite members, create API keys (Admin API **cannot** mint keys), first OAuth, App install. | Keith's browser session | **free** | **high as fallback** | Existing `cosmos_browser` / Playwright MCP. Canon: DOM when the API depends on something that can run out (weekly limit UI, credit-card, key create). |

---

## Claude Code CLI flags COSMOS actually scripts

Official: [CLI reference](https://code.claude.com/docs/en/cli-reference), [headless](https://code.claude.com/docs/en/headless).

| flag | COSMOS use |
|------|------------|
| `-p` / `--print` | non-interactive. The hand. |
| `--bare` | CI/scripts; will become default for `-p`. Needs `ANTHROPIC_API_KEY`. |
| `--output-format text\|json\|stream-json` | ledger vs live |
| `--json-schema '{…}'` | typed worker output |
| `--input-format stream-json` | multi-turn stdin protocol |
| `--include-partial-messages` | token stream |
| `--allowedTools` / `--disallowedTools` | fence |
| `--permission-mode auto\|dontAsk\|acceptEdits` | CI lock vs edit |
| `--append-system-prompt` / `--system-prompt-file` | inject COSMOS canon without editing CLAUDE.md |
| `--max-turns` / `--max-budget-usd` | hard stop |
| `--continue` / `--resume <id>` | session |
| `--mcp-config` | explicit servers under `--bare` |
| `--settings '{…}'` | inline permissions JSON |
| `--add-dir` | extra stream roots (cosmos_brain already does this) |
| `--model` | opus / sonnet / haiku / fable |
| `--plugin-dir` / `--plugin-url` | one-off plugin |

Rejected with `-p`: `--bg`; `--cloud` with a task description (session-id + `-p` queues a follow-up into a cloud session instead).

SIGTERM → exit 143, unfinished turn, `SessionEnd` hooks still run. Prefer SIGINT / SDK `interrupt()`.

---

## MCP — what COSMOS should and should not host

| Role | Do | Don't |
|------|----|-------|
| **Claude Code as host** | Add GitLab + GitHub MCP; maybe Playwright. Project `.mcp.json`. | `enableAllProjectMcpServers` on untrusted clones. |
| **COSMOS as host** | Official Python SDK talking to local stdio servers (filesystem with ACL, time, fetch). | Give Core a general Bash MCP. |
| **COSMOS as server** | Read-only tools: `status`, `ledger_tail`, `queue_list`. Write tools fenced (submit → attempt workspace). | Expose `live/config` secrets or `install_key.bin`. |
| **Messages MCP connector** | Remote HTTPS MCP when the worker is HTTP-only. | Local stdio — not supported. |

Official SDK index: [modelcontextprotocol.io/docs/2026-07-28/sdk](https://modelcontextprotocol.io/docs/2026-07-28/sdk). Spec: [specification/2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28). Schema: `schema/2026-07-28/schema.ts`.

---

## Recommended COSMOS Anthropic stack (research, not a DONE claim)

Nothing below is claimed live except row 1's existing `cosmos_brain.py` path.

1. **Keep `claude -p` as the prepaid coding / hard-review hand.** `--output-format json`, capture `session_id`, bind DONE to `result` + `is_error`. `--bare` for queue jobs so a random `~/.claude` hook cannot run. **Unset `ANTHROPIC_API_KEY` in that environment** so the seat allowance is used, not Console spend.
2. **Commit skills + a tight CLAUDE.md** (already present). Skills for repeatable COSMOS procedures; hooks for the gates (py_compile, no-delete-without-`_delme`, block `.env`).
3. **Project MCP:** GitLab HTTP MCP + GitHub MCP, allowlisted tools. Approve once in an interactive session so `-p` is not the first to load them blindly — or pass `--mcp-config` under `--bare`.
4. **Agent SDK Python** only if COSMOS needs callbacks / typed messages. Auth with a **workspace-scoped API key**, spend-gated — do not ship `/login`.
5. **Metered Messages rail** (`anthropic-api`) as overflow when the weekly Claude Code window is dry. Haiku for cheap structured; Sonnet 5 default; Opus/Fable reserved. Prompt cache + Batches for bulk. Files API for PDFs. **This closes MESH_ADDITIONS #17.**
6. **Do not** turn on web_search in a loop ($10/1k). Prefer web_fetch or SGH DOM.
7. **Forge overflow:** GitHub Action `@claude` **or** GitLab CI job on a project runner — leased against Cursor Cloud Agents.
8. **Admin/Usage APIs** once an org Admin key exists — feed the spend-gate. Individual accounts cannot call Admin API.
9. **DOM:** billing, key create, first OAuth only.
10. Fail-closed on 401/403/429 and on `stop_reason: "refusal"`. Never invent a green Claude log.

---

## Explicitly not hands / do not build

- **Cowork in-session subagent as F5.** Burns the Cowork allotment; the +50% boost is Claude Code only (`ROUTING.md`).
- **Completions API.** Dead.
- **Offering claude.ai login inside a COSMOS-shipped Agent SDK product.** Anthropic forbids it unless pre-approved.
- **Treating `/usage` dollar figures as the bill.** Client-side list-rate estimates; Console Usage page / Usage API are authority.
- **Accepting `file_id` from anyone.** Workspace-wide readable.
- **`--dangerously-skip-permissions` / `--yolo`.** Not a COSMOS permission mode.
- **Agent teams** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`) as default — ~7× tokens.
- **A second orchestrator** (Managed Agents + Claude Code + COSMOS scheduler all writing the tree). One authority.

---

## Official documentation (fetched 2026-08-25)

Indexes (LLM-complete; treat as the "PDF"):

- https://platform.claude.com/docs/llms.txt — Claude API / Admin / Files / Batches / MCP connector
- https://code.claude.com/docs/llms.txt — Claude Code CLI, Agent SDK, hooks, MCP, Actions
- https://modelcontextprotocol.io/llms.txt — MCP spec + SDKs

Platform (API):

- https://platform.claude.com/docs/en/home
- https://platform.claude.com/docs/en/api/overview
- https://platform.claude.com/docs/en/api/messages/create
- https://platform.claude.com/docs/en/build-with-claude/working-with-messages
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
- https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- https://platform.claude.com/docs/en/build-with-claude/batch-processing
- https://platform.claude.com/docs/en/build-with-claude/vision
- https://platform.claude.com/docs/en/build-with-claude/thinking
- https://platform.claude.com/docs/en/build-with-claude/files
- https://platform.claude.com/docs/en/build-with-claude/pdf-support
- https://platform.claude.com/docs/en/agents-and-tools/mcp-connector
- https://platform.claude.com/docs/en/manage-claude/admin-api
- https://platform.claude.com/docs/en/manage-claude/workspaces
- https://platform.claude.com/docs/en/manage-claude/authentication
- https://platform.claude.com/docs/en/manage-claude/usage-cost-api
- https://platform.claude.com/docs/en/about-claude/pricing
- https://platform.claude.com/docs/en/models/overview
- https://platform.claude.com/docs/en/managed-agents/overview
- https://platform.claude.com/docs/en/cli-sdks-libraries/overview
- https://claude.com/pricing — consumer / seat plans

Claude Code:

- https://code.claude.com/docs/en/headless
- https://code.claude.com/docs/en/cli-reference
- https://code.claude.com/docs/en/authentication
- https://code.claude.com/docs/en/hooks-guide · https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/mcp
- https://code.claude.com/docs/en/agent-sdk/overview
- https://code.claude.com/docs/en/agent-sdk/python · https://code.claude.com/docs/en/agent-sdk/typescript
- https://code.claude.com/docs/en/github-actions
- https://code.claude.com/docs/en/gitlab-ci-cd
- https://code.claude.com/docs/en/costs
- https://github.com/anthropics/claude-agent-sdk-python
- https://github.com/anthropics/claude-agent-sdk-typescript
- https://github.com/anthropics/claude-code-action

MCP:

- https://modelcontextprotocol.io/specification/2026-07-28
- https://modelcontextprotocol.io/docs/2026-07-28/sdk
- https://github.com/modelcontextprotocol/python-sdk
- https://github.com/modelcontextprotocol/typescript-sdk
- https://github.com/modelcontextprotocol/specification/blob/main/schema/2026-07-28/schema.ts
