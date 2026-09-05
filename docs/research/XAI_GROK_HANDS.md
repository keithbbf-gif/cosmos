# XAI / GROK HANDS — G46 scout return (xAI API + Grok Build CLI + Grok Bot)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25 (docs fetched live from `docs.x.ai`).
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim except where a COSMOS artifact is named.
**No COSMOS core code was edited.** Maker-docs sweep (DHx assignment log): each maker's hands → `docs/research/<MAKER>_HANDS.md`.

**Already on the mesh (do not re-add as "new"):** Dispatcher rails **`sgh-api`** (`bts_sgh`, Grok, $0.02/call, cap $10) and **`gw-api`** (`bts_gw`, Grok-Build, $0.001/call, cap $5) — both spend-gated, live-probed 2026-08-25 (`docs/SELFTEST_2026-08-25.md`, `cosmos/cosmos_node_rails.py`). Grok Build CLI (`grok -p`) is already the overflow coding lane (`docs/ROUTING.md`). GrokBot/GBt is a **file mailbox only** — there is still **no public REST to address a named grok.com / Grok Bot teammate** (confirmed against current docs; see Grok Bot rows). This file inventories every xAI **hand** COSMOS could fire, including the ones already wired.

**Filter:** a surface with no hands is rejected. Every row is an **action** COSMOS could fire: REST endpoint, CLI flag, SDK call, MCP tool, ACP, or DOM fallback. grok.com chat-only chrome is out except as the DOM fallback (billing, key mint, first OAuth, connectors).

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks. Equal power, cheaper wins. Metered Console API (`api.x.ai`) sits **below** the SuperGrok Heavy / Grok Build CLI cluster even when the model slug is the same — `grok login` draws a **different wallet** from `XAI_API_KEY`.

**Name collisions (do not mix):**
- **xAI Grok** (this file) ≠ **Groq** LPUs (`docs/research/GROQ_HANDS.md`, `api.groq.com`, keys `gsk_…`).
- **Grok Build CLI** (`grok` binary, `cli-chat-proxy.grok.com`) ≠ **Grok Bot** (Cursor-auth desktop teammate on a cloud VM) ≠ **GrokBot/GBt** (Keith's grok.com team mailbox).
- **Live Search** is **not** a separate 2026 product. Realtime grounding is the server-side tools **`web_search`** + **`x_search`**.

There is **no** official xAI PDF spec. The live HTML + markdown twins (`https://docs.x.ai/<path>.md`) + machine dump [`https://docs.x.ai/llms.txt`](https://docs.x.ai/llms.txt) + OpenAPI at [`https://api.x.ai/docs`](https://api.x.ai/docs) **are** the docs.

---

## Official documentation URLs (fetched 2026-08-25)

Prefer these over blogs. Markdown twin: append `.md` to any `docs.x.ai` path (some fetchers 404 the twin; HTML + `llms.txt` still hold).

| what | URL |
|------|-----|
| **Docs home / overview** | https://docs.x.ai/overview |
| **Machine dump (all pages)** | https://docs.x.ai/llms.txt |
| **Quickstart + key mint** | https://docs.x.ai/developers/quickstart |
| **Models** | https://docs.x.ai/developers/models |
| **Pricing (tokens, tools, batch, storage)** | https://docs.x.ai/developers/pricing |
| **Rate limits + tiers** | https://docs.x.ai/developers/rate-limits |
| **Grok 4.6 (flagship)** | https://docs.x.ai/developers/grok-4-6 |
| **Responses API (preferred text)** | https://docs.x.ai/developers/model-capabilities/text/generate-text |
| **Chat Completions (legacy)** | https://docs.x.ai/developers/model-capabilities/legacy/chat-completions |
| **Chat vs Responses comparison** | https://docs.x.ai/developers/model-capabilities/text/comparison |
| **Structured outputs** | https://docs.x.ai/developers/model-capabilities/text/structured-outputs |
| **Reasoning / `reasoning_effort`** | https://docs.x.ai/developers/model-capabilities/text/reasoning |
| **Streaming** | https://docs.x.ai/developers/model-capabilities/text/streaming |
| **Multi-agent (beta)** | https://docs.x.ai/developers/model-capabilities/text/multi-agent |
| **Vision / image understanding** | https://docs.x.ai/developers/model-capabilities/images/understanding |
| **Tools overview (agentic)** | https://docs.x.ai/developers/tools/overview |
| **Function calling (client tools)** | https://docs.x.ai/developers/tools/function-calling |
| **Web Search** (was Live Search web half) | https://docs.x.ai/developers/tools/web-search |
| **X Search** (was Live Search X half) | https://docs.x.ai/developers/tools/x-search |
| **Code execution** | https://docs.x.ai/developers/tools/code-execution |
| **Collections search (RAG tool)** | https://docs.x.ai/developers/tools/collections-search |
| **Remote MCP (server-side)** | https://docs.x.ai/developers/tools/remote-mcp |
| **Image generation tool** | https://docs.x.ai/developers/tools/image-generation |
| **Citations** | https://docs.x.ai/developers/tools/citations |
| **Streaming & sync (agentic)** | https://docs.x.ai/developers/tools/streaming-and-sync |
| **Batch API** | https://docs.x.ai/developers/advanced-api-usage/batch-api |
| **Deferred chat completions** | https://docs.x.ai/developers/advanced-api-usage/deferred-chat-completions |
| **Async client concurrency** | https://docs.x.ai/developers/advanced-api-usage/async |
| **WebSocket Responses** | https://docs.x.ai/developers/advanced-api-usage/websocket-mode |
| **Priority processing (2×)** | https://docs.x.ai/developers/advanced-api-usage/priority-processing |
| **Prompt caching** | https://docs.x.ai/developers/advanced-api-usage/prompt-caching |
| **Context compaction** | https://docs.x.ai/developers/advanced-api-usage/context-compaction |
| **mTLS** | https://docs.x.ai/developers/advanced-api-usage/mtls |
| **Files** | https://docs.x.ai/developers/files |
| **Collections (RAG store)** | https://docs.x.ai/developers/files/collections |
| **Cost tracking (`cost_in_usd_ticks`)** | https://docs.x.ai/developers/cost-tracking |
| **Management API** | https://docs.x.ai/developers/management-api-guide |
| **REST inference reference** | https://docs.x.ai/developers/rest-api-reference/inference |
| **OpenAPI / Swagger** | https://api.x.ai/docs |
| **gRPC + protobuf** | https://docs.x.ai/developers/grpc-api-reference · https://github.com/xai-org/xai-proto |
| **Docs MCP** | https://docs.x.ai/developers/docs-mcp · endpoint `https://docs.x.ai/api/mcp` |
| **Console billing** | https://docs.x.ai/console/billing · https://console.x.ai |
| **Grok Build CLI** | https://docs.x.ai/build/overview |
| **Headless / ACP** | https://docs.x.ai/build/cli/headless-scripting |
| **CLI reference** | https://docs.x.ai/build/cli/reference |
| **Grok Build MCP / hooks / skills / worktrees** | https://docs.x.ai/build/features/mcp-servers · hooks · skills-plugins-marketplaces · worktrees |
| **Enterprise Grok Build (auth, ZDR, MDM)** | https://docs.x.ai/build/enterprise |
| **Grok Bot (teammates, no public RPC)** | https://docs.x.ai/grok-bot/overview |
| **Grok Bot cost / eligible plans** | https://docs.x.ai/grok-bot/faq |
| **Imagine image gen / edit** | https://docs.x.ai/developers/model-capabilities/images/generation · editing |
| **Imagine video** | https://docs.x.ai/developers/model-capabilities/video/generation |
| **TTS / STT / speech-to-speech** | https://docs.x.ai/developers/model-capabilities/audio/text-to-speech · speech-to-text · speech-to-speech |
| **Voice realtime WS** | `wss://api.x.ai/v1/realtime` |
| **Consumer grok.com FAQ (weekly pool)** | https://docs.x.ai/grok/faq |
| **grok.com connectors** | https://docs.x.ai/grok/connectors · https://grok.com/connectors |
| **Vertex AI (Grok as partner model)** | https://docs.x.ai/developers/community/google-cloud-vertex-ai |
| **Microsoft Foundry** | https://docs.x.ai/developers/community/microsoft-foundry |
| **Release notes** | https://docs.x.ai/developers/release-notes |
| **May 15 2026 model retirement** | https://docs.x.ai/developers/migration/may-15-retirement |
| **Python SDK** | https://github.com/xai-org/xai-sdk-python · `pip install xai-sdk` |
| **CLI installer** | `curl -fsSL https://x.ai/cli/install.sh \| bash` · Windows: `irm https://x.ai/cli/install.ps1 \| iex` · `npm i -g @xai-official/grok` |
| **Grok 4.6 announcement** | https://x.ai/news/grok-4-6 |
| **Marketing API page** | https://x.ai/api |

---

## How COSMOS reaches xAI (reach column, one pattern)

Core stays sole ledger writer. xAI is reached as:

| Lane | Mechanism | When |
|------|-----------|------|
| **A. Native Grok Build CLI** | `grok -p "…"` inside an attempt-private workspace. JSON via `--output-format json`. Stream-json, `--always-approve`, `--sandbox`, `--session-id` / `-r` / `-c`, `--worktree`, ACP `grok agent stdio`. | **Preferred coding-agent lane.** Draws SuperGrok Heavy weekly pool when authenticated via `grok login`. Matches "no bats — in-app / COSMOS action." **Already the overflow coding default** (`ROUTING.md`). |
| **B. HTTP Responses API** | `POST https://api.x.ai/v1/responses`. Header `Authorization: Bearer $XAI_API_KEY`. Official Python/TS SDKs + OpenAI SDK with `base_url="https://api.x.ai/v1"`. Stateful `previous_response_id`, built-in tools, MCP, structured outputs. | **Preferred new API work.** This is the shape `sgh-api` / `gw-api` should grow into. Metered Console credits. |
| **C. HTTP Chat Completions (legacy)** | `POST https://api.x.ai/v1/chat/completions`. Still supported; new features land on Responses first. | Compat for workers that already speak Chat Completions (Aider, LiteLLM). Same key, same spend-gate. **Already the likely shape of `bts_sgh`.** |
| **D. Batch + deferred** | `POST /v1/batches` (async, 24h, separate rate-limit pool) or `deferred: true` on chat completions (`GET /v1/chat/deferred-completion/{id}`). | Overnight bulk eval / critique. Return-watcher on batch complete. |
| **E. MCP-client / MCP-server** | Grok Build is an MCP **host** (`grok mcp add`). Responses API is an MCP **client** (`tools: [{type:"mcp", server_url}]`). xAI hosts **docs MCP** at `https://docs.x.ai/api/mcp` (no key). | Agent brains get forge/browser/docs tools. Core should prefer native `grok`/`gh`/`glab` over giving itself a shell via MCP. |
| **F. Grok Bot desktop / iOS** | Cursor-auth app on a persistent cloud VM. Skills, routines, connectors, computer-use. **No documented REST to a named Bot.** | Prepaid teammate overflow. Handoff is still mailbox / file / human. Do not invent a `team_id` RPC. |
| **G. Vertex / Foundry** | Grok as partner model on GCP Model Garden or Azure AI Foundry. OpenAI-compat. | Only if Keith wants Grok on the **Vertex $300 credit** (expires 2026-10-13, already `gem-api`) or an Azure bill. Two wallets, one model family. |
| **H. DOM** | [console.x.ai](https://console.x.ai) keys/billing/rate-limits; [grok.com](https://grok.com) usage/connectors; first OAuth. | Fallback only. Canon: DOM first when the API depends on something that can run out (prepaid balance, weekly pool, key expiry). |

Keith owns credentials. Store under `live/config/` (git-ignored). Never hard-code. Never print a key in full (redact `xai-…last4`). Fenced commit still gates any tree write.

---

## Auth primer (all API/CLI rows inherit this unless overridden)

**Inference base:** `https://api.x.ai/v1` (mTLS twin `https://mtls.api.x.ai`). Header: `Authorization: Bearer <XAI_API_KEY>`.
**Management base:** `https://management-api.x.ai` — **separate management key**, not the inference key.
**Grok Build proxy:** `cli-chat-proxy.grok.com` + `auth.x.ai` (OAuth). Direct `api.x.ai` only when using `XAI_API_KEY`.

| method | credential | header / env | COSMOS use |
|--------|------------|--------------|------------|
| **Console API key** | `xai-…` from [API Keys](https://console.x.ai/team/default/api-keys) | `Authorization: Bearer`. Env `XAI_API_KEY` | Default for `sgh-api` / `gw-api` HTTP. Spend-gated. **Secret — server only.** |
| **Management key** | Console → Settings → Management Keys | Bearer on `management-api.x.ai` | Key inventory, ACLs, QPS/QPM/TPM caps, audit. **Not** for inference. |
| **Grok Build browser OIDC** | `grok login` → cached session | CLI manages it (`~/.grok/`) | Default interactive + `grok -p` on a machine Keith signed in. Draws **SuperGrok weekly pool**, not Console credits. |
| **Grok Build device-code** | `grok login --device-auth` (RFC 8628) | CLI | SSH / container / headless host without a browser. Still SuperGrok pool. |
| **Grok Build API key** | `XAI_API_KEY` or `[model.…] api_key` in `~/.grok/config.toml` | CLI env | CI. **Bills Console prepaid credits**, not the weekly pool. A leftover key **steals** the session off SuperGrok. |
| **Enterprise OIDC / `auth_provider_command`** | IdP token | CLI | MDM. `disable_api_key_auth` + `force_login_team_uuid` in `/etc/grok/requirements.toml`. |
| **Grok Bot** | **Cursor account** (SSO). Eligible: SuperGrok Plus/Heavy, Cursor Pro+/Ultra/Teams. | App OAuth | Desktop/iOS only. Uses whichever of Cursor vs SuperGrok has **more** remaining usage. |
| **Remote MCP** | `authorization` / `headers` on `tools[].type=mcp` | MCP transport | Streamable HTTP or SSE. xAI is the MCP client. |
| **Docs MCP** | none | Streamable HTTP | `https://docs.x.ai/api/mcp` — public, stateless. |
| **Vertex ADC / Foundry Entra** | GCP ADC or Azure identity | provider IAM | Partner-model path. Different bill. |

**Credential precedence inside Grok Build** (official, per model): `model.api_key` → `model.env_key` → active session token (`grok login`) → `XAI_API_KEY`. A leftover `XAI_API_KEY` on a SuperGrok-signed workstation **bills Console** instead of the prepaid seat.

---

## ARCH env isolation (additive, 2026-08-25) — H5 / A5

Two-wallet theft: leftover `XAI_API_KEY` steals SuperGrok pool onto Console. `live/config/` this pass has **no** xAI key file (Cursor key is a different wallet).

**ARCH rule:** `grok -p` queue jobs **unset** `XAI_API_KEY` so SuperGrok is used. `sgh-api` / `gw-api` HTTP jobs **set** the Console key in an isolated env. Do not mix. `--sandbox workspace` / `--bare` for unattended jobs.

**WAVE A5:** point Grok Build / Claude Code / Cursor MCP hosts at **`https://docs.x.ai/api/mcp`** (no key). Already-on-mesh `sgh-api`/`gw-api` stay; settle `cost_in_usd_ticks` as a delta, not a new maker. Dispatcher new rails wait on Kernel attach. Grok Bot REST remains **not documented** — do not invent it. This is **not** a stage-6 pass.

---

## Host bind (additive, 2026-08-27 s6 re-probe) — A5 / U11

This process (`grok` 1.0.5 (5115b46bc9) [stable]):

- `grok mcp list` → **`BFast`** only (`bts_fs_mcp.py`). **No** `https://docs.x.ai/api/mcp`.
- Cursor `~/.cursor/mcp.json` server names → **`bts`** only.
- Claude Code `claude mcp list` → Gmail/Slack/Box/Cloudflare/GDrive connected; M365 needs auth; **no** xAI Docs MCP.

WAVE A5 is still a config drop, not a wired COSMOS hand. Grok Bot REST remains **not documented**.

**Two wallets — do not conflate them.** Official consumer FAQ + Console billing: SuperGrok subscription and Console API prepaid credits are **separate**. Heavy **does not** feed API credits. API spend does not count against the weekly pool except as a display category when the same xAI login owns both.

---

## Cost floor (two wallets — do not mix)

Mixing SuperGrok weekly pool with Console prepaid credits is how `sgh-api` / `gw-api` get burned by accident while Grok Build still shows 96% headroom.

| Wallet | What official docs say | COSMOS note |
|--------|------------------------|-------------|
| **SuperGrok / SuperGrok Plus / SuperGrok Heavy seat** | One **shared weekly usage pool** across Chat, Imagine, Voice, **Build**, (and an "API" breakdown row when the same login also uses Console). Resets on a schedule shown in grok.com Settings → Usage. Free-tier Chat/Voice remain after the pool is empty. Extra Usage Credits from $5 on web, expire 1 year, **standard (higher) rates**. Auto Top Up available. | Live number lives in `docs/ROUTING.md`. Keith **2026-09-05:** **25% used** (18% on Sep 4 is stale; morning 7% is stale). Reset **Sep 10, 2026 5:35 PM**. Last 2% of the bar is reserve. One-time Usage Limit Reset (Redeem) expires Sep 12 — do not Redeem. **This is the prepaid orch/WO lane.** Re-read Settings → Usage — do not quote those numbers stale. (2026-08-25 4% / Aug 31 38% / Sep 3 reset / Sep 4 18% are STALE.) |
| **Cursor Ultra** | **Included with SuperGrok Heavy → $0 marginal.** Grok Bot eligible. DHx: cycle Aug 14–Sep 14, Cursor Models 4.6% used, on-demand DISABLED. | Separate from Console API. Cloud Agents already proven. Do not double-write the live tree. |
| **Grok Bot weekly** | Included on eligible plans. Overage = on-demand at model/token cost. If both Cursor and SuperGrok exist, Bot uses whichever has **more** remaining usage. | DHx: GrokBot weekly **0%**, resets Aug 30. App, not an API. |
| **Console API prepaid credits** | Buy in Console (Guest Checkout). Auto top-up min **$25**, max 5 top-ups / 24h. $0 invoiced limit (default) → requests **rejected** when credits hit $0. Credits **non-refundable**. Usage calculated at request time. | This is `sgh-api` / `gw-api`. MESH caps $10 / $5. Bind settle to `usage.cost_in_usd_ticks` (1 USD = 10^10 ticks). |
| **Function calling (client tools)** | **$0 extra** — tokens only. Args always schema-strict (`strict` implicitly true). Max 128 tools. | COSMOS executes; model does not. |
| **Web Search / X Search / Code execution** | **$5 / 1k calls** each + tokens. Errors: check `server_side_tool_usage` (that is what bills). | Do not enable on a COSMOS loop without a spend cap. SGH DOM remains the prepaid search rail. |
| **Collections search / `file_search`** | **$2.50 / 1k calls** + tokens. Storage: files **$0.025 / GiB / day**, collections **$0.10 / GiB / day**. Downloads **$0.20 / GiB**. | RAG. Need credits on the account to upload. |
| **File attachments / `attachment_search`** | **$10 / 1k calls** + tokens. Implicitly added when files are attached. | Prefer Collections for persistent corpora; Files for one-shot chat. |
| **Remote MCP** | Token-based only (no per-call tool fee). | |
| **View image / view X video** | Token-based only (images/videos **found by search**, not user-supplied). | User-supplied images = vision input tokens. |
| **Image generation tool** | Imagine API rates (not the $5/1k table). | |
| **Batch API** | **20% off** tokens on `grok-4.3` and `grok-4.20-*` only. **grok-4.6 has no batch discount.** Image/video batch = **standard** rates. Requests **do not** count toward RPS/TPM. Most finish &lt;24h (best-effort, not guaranteed). | Bulk eval. Prefer 4.3/4.20 if the discount matters. |
| **Priority processing** | **2×** all token types. Only billed 2× when response `service_tier: "priority"`. Chat Completions + Responses only. Not Batch, not Imagine. | Only if latency is the product. |
| **Prompt cache** | grok-4.6 cached in **$0.50 / 1M** (short) / **$1.00** (long). Set `prompt_cache_key` (Responses) or `x-grok-conv-id` (Chat Completions) or cache misses. | Required on any repeated COSMOS system prompt. |
| **Context compaction** | `POST /v1/responses/compact` — pay to shrink, then cheaper follow-ups. | Long agent loops. |
| **Docs MCP / CLI binary / xai-sdk** | **$0** to install (OSS / hosted docs). | Inference still bills. |
| **Tokenizer / GET /v1/models / GET /v1/api-key** | **Not billed** as inference (estimate only; live requests add extra control tokens). | Spend-gate preflight. |
| **Usage-guideline violation (Responses, pre-gen)** | **$0.05 / request** if caught before generation. | Fail-closed; still charged. |
| **Voice** | STS `grok-voice-think-fast-2.0` **$0.08 / min** audio + $0.004 text in. STT **$0.10 / hr REST**, **$0.20 / hr streaming**. TTS **$15 / 1M chars**. | Phone/voice clients. |
| **Imagine** | Image 2.0 from **$0.04 / img** (1K low) to $0.08 (2K medium). Video 1.5 from **$0.08 / sec** (480p) to **$0.25 / sec** (1080p). | Not a COSMOS default. |
| **Vertex / Foundry Grok** | GCP / Azure invoice, not Console credits. | Could theoretically burn remaining Vertex $300 — **gem-api already owns that credit.** Don't split it without Keith. |

**List rates fetched 2026-08-25** from [Pricing](https://docs.x.ai/developers/pricing) (USD / million tokens). Long-context threshold = **200k prompt tokens**; once crossed, **the whole request** bills at the long rate.

| Model | Context | Input / cached / out (&lt;200k) | Input / cached / out (≥200k) | Batch |
|-------|---------|----------------------------------|------------------------------|-------|
| **grok-4.6** (flagship, default Build) | 500k | $2.00 / $0.50 / $6.00 | $4.00 / $1.00 / $12.00 | **no discount** |
| grok-4.5 | 500k | $2.00 / $0.30 / $6.00 | $4.00 / $0.60 / $12.00 | no discount |
| **grok-4.3** | 1M | **$1.25 / $0.20 / $2.50** | $2.50 / $0.40 / $5.00 | **20% off** |
| grok-4.20-0309-reasoning | 1M | $1.25 / $0.20 / $2.50 | $2.50 / $0.40 / $5.00 | 20% off |
| grok-4.20-0309-non-reasoning | 1M | $1.25 / $0.20 / $2.50 | $2.50 / $0.40 / $5.00 | 20% off |
| grok-4.20-multi-agent-0309 | 1M | $1.25 / $0.20 / $2.50 | $2.50 / $0.40 / $5.00 | 20% off |
| **grok-build-0.1** (ex `grok-code-fast-1`) | 256k | **$1.00 / $0.20 / $2.00** | $2.00 / $0.40 / $4.00 | no discount |

Knowledge cutoff for grok-4.6: **1 Feb 2026** (models page; grok-4-6 page also says January 2026). No realtime without search tools.

**Retired 2026-05-15** (already past): `grok-3`, `grok-4-0709`, `grok-4-fast-*`, `grok-4-1-fast-*`, `grok-code-fast-1`, `grok-imagine-image-pro`. Those slugs **redirect** to grok-4.3 / grok-build-0.1 / imagine-image-quality and **bill at the new rates**. Do not send retired slugs on purpose.

---

## Rate limits (Console API)

Official: [Rate Limits](https://docs.x.ai/developers/rate-limits). Per **team**, per **model**, two axes: **RPS** and **TPM**. RPS is RPM/60 (cannot dump a minute of requests in one second). 429 + exponential backoff. Tiers from **cumulative API spend since 2026-01-01**; once earned, **never downgrade**. Ground truth: [Console Rate Limits](https://console.x.ai/team/default/rate-limits).

| Tier | Spend threshold |
|------|-----------------|
| T0 | $0 (default) |
| T1 | $50 |
| T2 | $250 |
| T3 | $1,000 |
| T4 | $5,000 |
| Enterprise | on request |

| Model | RPS T0→T4 | TPM T0→T4 |
|-------|-----------|-----------|
| grok-4.6 / grok-4.5 | 150 / 172 / 208 / 312 / 500 | 50M / 53M / 60M / 74M / 100M |
| grok-4.3 / grok-4.20-*- / grok-build-0.1 | 37 / 50 / 75 / 125 / 208 | 10M / 15M / 25M / 45M / 85M |
| grok-4.20-multi-agent-0309 | 9 / 12 / 18 / 31 / 56 | 2.5M / 3.7M / 6.2M / 11M / 21M |
| grok-imagine-image* | 6 / 12 / 25 / 50 / 100 | — |
| grok-imagine-video* | 10 / 20 / 39 / 79 / 158 | — |

TPM counts prompt + completion + reasoning + **cached** tokens. Voice/Imagine raises: email sales@x.ai. Batch requests **do not** consume this pool.

---

## Ranking table

| # | name | kind | HANDS (what it DOES) | auth | cost | power | how COSMOS reaches it |
|---|------|------|----------------------|------|------|-------|------------------------|
| 1 | **`grok -p` / `--single` (Grok Build CLI)** | CLI + agent | Headless coding agent on this machine: Read/Edit/Bash, MCP, web, subagents, worktrees, sessions. `grok -p "…" --output-format json\|streaming-json\|plain`. `--always-approve` / `--yolo`, `--sandbox workspace\|strict`, `--allow`/`--deny`, `--max-turns`, `--effort`, `-m`, `-s`/`-r`/`-c`, `--cwd`, `--no-auto-update`. Claude Code flag aliases accepted. **This is the prepaid coding hand.** | `grok login` (SuperGrok pool) **or** `XAI_API_KEY` (Console). Device-code for headless. | **prepaid** SuperGrok Heavy weekly pool when OAuth. **Metered** if a key is in env. | **highest** | Native worker, already the overflow coding default. Queue: `grok --no-auto-update -p "…" --output-format json --always-approve --sandbox workspace --cwd <attempt>`. Capture `sessionId` for `-r`. Never a `.bat`. Install: `irm https://x.ai/cli/install.ps1 \| iex` or `npm i -g @xai-official/grok`. |
| 2 | **`--output-format json` / `streaming-json`** | CLI | Structured result COSMOS can ledger. JSON object at end (includes session id). Streaming-json = NDJSON events for KDash live. | same as row 1 | **included** | **highest** | Bind every DONE claim to the JSON (`sessionId`, stop reason, text). Runtime binding / SCAR_PLACATION. |
| 3 | **Grok Build as MCP host** | MCP client | `grok mcp add\|list\|remove\|doctor`. stdio (`npx …`) and HTTP (OAuth auto). Namespaced tools `<server>__<tool>`. Also reads `~/.claude.json`, `.cursor/mcp.json`, project `.mcp.json`. | MCP OAuth → `~/.grok/mcp_credentials.json` or `--header` | **free** protocol; model tokens still bill | **highest** | Project `.grok/config.toml` or `--scope project`. GitLab/GitHub MCP so G46 gets forge hands without Core growing a client. `grok inspect --json` is ground truth for what loaded. |
| 4 | **ACP `grok agent stdio`** | CLI + JSON-RPC | Agent Client Protocol over stdin/stdout. IDE/tool integration. `initialize` → `authenticate` (`xai.api_key` or `cached_token`) → `session/new` → `session/prompt`. Text arrives as `session/update` chunks. | same as row 1 | same as row 1 | **highest** (programmatic) | COSMOS Python worker can spawn `grok agent stdio` instead of scraping TUI. Prefer `-p` JSON for one-shot jobs; ACP for multi-turn IDE-shaped loops. |
| 5 | **Grok Build hooks** | hooks + CLI | JSON hooks in `~/.grok/hooks/` and `<project>/.grok/hooks/`. Events: `PreToolUse` (only blocking), `PostToolUse`, `Stop`, `SessionStart/End`, `Subagent*`, `PreCompact`. `type: command` or `http`. Exit 2 / `{"decision":"deny"}` blocks. Fail-open on crash/timeout. Also reads Claude/Cursor hook files. | local files. Project hooks need `/hooks-trust` or `--trust`. | **included** | **highest** | Format after Edit; block `.env` writes; `Stop` HTTP hook → Core URL so the return-watcher sees the turn. `--trust` only inside attempt workspaces. |
| 6 | **Skills / plugins / marketplaces / AGENTS.md** | skill + CLI | `.grok/skills/`, `~/.grok/skills/`, plugins, marketplaces. Slash commands. Reads `AGENTS.md` / `CLAUDE.md` / `.claude/rules/` / `.cursor/rules/` with **zero extra setup** (Claude Code compatible). | same as row 1 | **included** (tokens when invoked) | **highest** | Repo already has `CLAUDE.md` — every `grok -p` in this tree inherits it. Park procedures in skills, not a 200-line dump. `grok inspect` lists loaded rules + token counts. |
| 7 | **Permissions + sandbox + worktrees + subagents** | CLI | Modes: ask / auto / always-approve / headless `dontAsk`. Sandbox profiles: off / workspace / read-only / **strict** (Landlock/Seatbelt). `grok -w` git worktrees under `~/.grok/worktrees/`. Built-in subagents: `general-purpose`, `explore` (no shell/edits), `plan`. | same | **included** | **highest** | Headless COSMOS: `--permission-mode dontAsk --allow 'Read' --allow 'Grep' --sandbox strict` for review; `--always-approve --sandbox workspace` only inside fenced attempt dirs. Subagents inherit permission mode, **not** the parent's plan-mode edit gate. |
| 8 | **xAI Docs MCP** | MCP server (hosted) | Public Streamable-HTTP MCP. Tools include `list_doc_pages`. Stateless, no session, **no API key**. | none | **free** | **highest** (docs) | Point Claude Code / Grok Build / Cursor at `https://docs.x.ai/api/mcp`. COSMOS agents pull live xAI docs instead of stale copies. |
| 9 | **Sessions / resume / export / compact** | CLI | Auto-saved under `~/.grok/sessions/`. `-r` resume, `-c` continue, `--fork-session`, `/rewind` (restores files), `/compact`, `grok export` markdown, `grok import` from Claude Code. | same | **included** | **high** | Capture `sessionId` from JSON; multi-step jobs (review → fix → commit) via `-r`. Rewind **mutates disk** — only in attempt workspaces. |
| 10 | **Grok Bot (desktop/iOS teammate)** | app + cloud VM | Persistent named Bot on a **shared cloud computer** (browser, FS, terminal, connectors). Skills, routines (`/loop`-like schedules), approvals, parallel Bots (max 50 Bots+group chats). Continues when the laptop is closed. | **Cursor login.** Eligible: SuperGrok Plus/Heavy, Cursor Pro+/Ultra/Teams. | **prepaid** weekly Bot allowance; overage on-demand | **high** (but **no API**) | Keith runs the app. COSMOS does **not** get a `POST /bots/{id}/run`. Handoff remains file mailbox / human. Official: [overview](https://docs.x.ai/grok-bot/overview), [FAQ](https://docs.x.ai/grok-bot/faq). Treat "call that GBt synchronously" as **unavailable**. |
| 11 | **GET `/v1/models`** | REST | List models + aliases + live prices (cents per 100M tokens) + context length + long-context threshold. | API key | **free** | **high** (infra) | Probe before dispatch so COSMOS never hard-codes a retired slug. |
| 12 | **POST `/v1/tokenize-text`** | REST | Tokenize with a named model. Returns token ids/bytes/strings. Console Tokenizer twin. | API key | **free** (estimate; live inference adds extra control tokens) | **high** (spend-gate) | Preflight: refuse a job that would blow remaining Console headroom. Pair with `cost_in_usd_ticks` after the fact. |
| 13 | **GET `/v1/api-key`** | REST | Key name, ACLs, blocked/disabled, redacted key, team. | API key | **free** | **high** (hygiene) | Liveness probe cheaper than a chat call. Fail-closed if `api_key_blocked` / `team_blocked`. |
| 14 | **Responses API `POST /v1/responses`** | REST | Preferred text/agent endpoint. Stateful 30-day store (`previous_response_id`). Tools, structured outputs, reasoning, images in, streaming, `service_tier`. `store=false` to keep history local. | API key | **metered** list rates | **high** (fallback rail) | Grow `sgh-api`/`gw-api` onto this. Official SDKs: `xai-sdk` (gRPC+REST), `openai` with `base_url=https://api.x.ai/v1`, Vercel `ai` + `@ai-sdk/xai`. |
| 15 | **Chat Completions `POST /v1/chat/completions` (legacy)** | REST | OpenAI-shaped chat. Still live; **new features land on Responses first**. `deferred: true` lives here. | API key | **metered** | **high** (compat) | Keep for Aider / LiteLLM / incumbent `bts_sgh`. Migrate new work to Responses. |
| 16 | **Function calling (client tools)** | API feature | Model returns `tool_call` / Responses `function_call`; COSMOS executes; send `tool` / `function_call_output`. Parallel by default (`parallel_tool_calls: false` to serialize). `tool_choice` auto / required / named. Max **128**. Streaming: whole call in **one chunk**. Args **always schema-strict**. | API key | **tokens only** | **high** | Wire COSMOS tools (lock/ledger/queue **read-only first**) as JSON Schema. Prefer Grok Build CLI when the tools are filesystem/bash — don't reimplement that loop on HTTP. |
| 17 | **Structured outputs** | API feature | `response_format.type = json_schema \| json_object \| text`. Guaranteed match when using supported JSON Schema subset (Draft 2020-12 best). Combinable with tools on Grok 4 family. | API key | tokens | **high** | Batch critique / collector results as JSON COSMOS can ledger without regex. CLI twin: none first-party (use API or prompt+validate). |
| 18 | **Vision / image understanding** | API feature | jpg/png, ≤20 MiB, **no count cap**. `input_image` + `image_url` (URL or data URL). `detail: high`. grok-4.6: text+image in → text out. | API key | image tokens at input rate | **high** | Exhibit photos, Lindau plates, KDash / CI screenshots. Do not store image-chat history on server (docs warn requests fail). |
| 19 | **Web Search (`web_search`) — Live Search web half** | server tool | xAI searches + browses. Citations returned. Filters: `allowed_domains` / `excluded_domains` (max 5, mutually exclusive). `enable_image_understanding`, `enable_image_search`. Server runs the agent loop until a final answer. | API key | **$5 / 1k calls** + tokens (reasoning+completion) | **high** | Responses `tools: [{type:"web_search"}]` or SDK `web_search()`. **Spend-cap it.** SGH DOM remains prepaid search. This **is** the documented replacement for "Live Search." |
| 20 | **X Search (`x_search`) — Live Search X half** | server tool | Keyword + semantic + user + thread fetch on X. Filters: `allowed_x_handles` / `excluded_x_handles` (max 20), `from_date` / `to_date` ISO8601, image/video understanding. | API key | **$5 / 1k calls** + tokens | **high** | Grounded mesh-scout / "what is being said on X" without DOM. Same spend-cap rule. |
| 21 | **Code execution (`code_execution` / `code_interpreter`)** | server tool | Python sandbox on xAI. Math, data, verification. Responses name `code_interpreter`; xAI SDK `code_execution`. | API key | **$5 / 1k calls** + tokens | **high** | Spreadsheet / stats without giving Grok Keith's shell. Not a replacement for attempt-private workspaces. |
| 22 | **Remote MCP (API is the client)** | server tool | `tools: [{type:"mcp", server_url, server_label, authorization, headers, allowed_tools}]`. xAI talks to **your** Streamable-HTTP/SSE MCP. `require_approval` / `connector_id` **not** supported. Also on Speech-to-Speech. | API key + MCP bearer | tokens only | **high** | Cloud-agent path: Responses rail talks to GitLab/GitHub/Firecrawl MCP without COSMOS hosting a client. Local stdio stays on Grok Build CLI. |
| 23 | **Prompt cache + `prompt_cache_key`** | API feature | Cached input at ¼–⅙ list. **Highly recommended** on grok-4.6: `prompt_cache_key` (Responses) or `x-grok-conv-id` (Chat Completions) pins the conversation to one server. Without it, multi-turn often cache-misses. | API key | cached in $0.20–$1.00 / 1M | **high** (cost) | Required on any repeated COSMOS system prompt / SEED facts. Check usage cached tokens. |
| 24 | **Cost tracking `cost_in_usd_ticks`** | API field | Every inference response includes actual billed cost (tokens + tools, after cache). 1 USD = 10,000,000,000 ticks. SDK: `response.cost_usd`. | API key | **free** field | **high** (spend-gate) | **This is how `sgh-api` should settle** instead of UNPRICED estimates. Ledger `SPEND_SETTLED` from ticks, not `metered_usd` guesses. |
| 25 | **Reasoning / `reasoning_effort`** | API feature | grok-4.6: `low \| medium \| high` (default) \| **`xhigh`**. Cannot disable. Encrypted CoT via `include: ["reasoning.encrypted_content"]` for round-trip. `presencePenalty`/`frequencyPenalty`/`stop` **error** on reasoning models. | API key | reasoning tokens bill as output | **high** | Default high for hard review. `low` for latency-sensitive tool loops. `xhigh` only when quality ≫ time. |
| 26 | **Batch API** | REST | `POST /v1/batches` → add requests (SDK objects or JSONL upload) → poll → results. Chat, Responses, tools, MCP, images, videos. Unique `batch_request_id` / JSONL `custom_id`. Unlimited batches; **2 creates/s**; JSONL **200 MB / 50k lines**; per-request **25 MB**; **1000 add-calls / 30s**. Image/video result URLs expire **1 hour**. Console UI exists. | API key | **20% off** on 4.3/4.20 only; 4.6 = list; Imagine = list. **No RPS/TPM.** | **high** (bulk) | Overnight 135-tool backlog critique. Return-watcher on complete. Match by `custom_id`. Prefer `grok-4.3` if the 20% matters. |
| 27 | **Deferred chat completions** | REST | Chat Completions `deferred: true` → `{request_id}` → poll `GET /v1/chat/deferred-completion/{id}`. 202 until ready. Result **once**, discarded after **24h**. Same rate limit as chat. REST or xAI SDK only. | API key | same as chat | **med-high** | Single long reasoning job without holding an HTTP connection. Batch is better for N≫1. |
| 28 | **Async client (`AsyncClient`)** | SDK | Concurrent in-flight requests with a semaphore. Not a server queue — still counts against RPS/TPM. | API key | same as live | **med-high** | Fan-out short jobs. Cap `max_concurrent` to the team's RPS. |
| 29 | **WebSocket Responses `wss://api.x.ai/v1/responses`** | WS | Long-lived socket; `response.create` per turn; server keeps state on the socket. Works with ZDR / `store=false`. ~20% lower E2E latency on tool-heavy loops (vendor benchmark). | API key | same as Responses | **med-high** | Agentic worker that would otherwise re-POST the whole history. |
| 30 | **Context compaction `POST /v1/responses/compact`** | REST | Shrink a long conversation into an opaque `encrypted_content` item. Next turn pays for the compact blob, not the full history. | API key | compact call + cheaper follow-ups | **med-high** | Multi-hour agent loops under 500k. Treat blob as opaque. |
| 31 | **Files API + `attachment_search`** | REST + tool | Upload / list / get / delete (`POST /v1/files`). Attach by URL or file id; API **implicitly** adds `attachment_search` and runs an agentic loop over the docs. | API key | **$10 / 1k searches** + tokens. Storage $0.025/GiB/day. | **high** | One-shot dissertation PDF / exhibit in a chat. Persistent corpora → Collections instead. |
| 32 | **Collections API + `collections_search` / `file_search`** | REST + tool | Persistent RAG: collections, files, embeddings, metadata filters, chunking. Search tool in Responses. Need credits on the account to upload. Max file **100 MB**. | API key | **$2.50 / 1k searches** + storage $0.10/GiB/day | **high** | Chapter corpus / exhibit bundle as a collection. Do not train-on (docs: user Collection data not used for training). |
| 33 | **Multi-agent `grok-4.20-multi-agent`** | model (beta) | Server-side team: leader + specialists, built-in tools (`web_search`, `x_search`, `code_execution`, `collections_search`) + remote MCP. **No client-side function calling. No Chat Completions — Responses / xAI SDK only.** Only tool calls + leader final answer are returned. | API key | $1.25/$2.50 + tool fees. Tight RPS (T0: 9). | **high** (research) | Deep multi-source research jobs. Beta — interface may break. Don't use for COSMOS tool-calling to Core. |
| 34 | **Streaming SSE** | API feature | `stream: true` on Responses/Chat. Agentic: **strongly recommended** (tool visibility + reasoning token counts). Opt-in tool outputs via `include` (`web_search_call_output`, etc.). | API key | same as non-stream | **high** | KDash live token view. Default for any tool-enabled request. |
| 35 | **Management API** | REST (separate host) | Create/list/update/delete API keys; ACLs (`api-key:model:*`, `api-key:endpoint:chat\|image`); per-key QPS/QPM/TPM; audit events. Base `https://management-api.x.ai`. | **Management key** | **free** to call | **high** (hygiene) | Mint a COSMOS-scoped key with endpoint+model ACL + low QPS. Keith does money; COSMOS can *report* and fail-closed on blocked keys. |
| 36 | **xAI Python SDK (`xai-sdk`)** | SDK | Official. Chat, tools helpers (`web_search()`, `x_search()`, `code_execution()`, `mcp()`, `image_generation()`), files, collections, batch, image/video, management. gRPC under the hood. `AsyncClient`. | `XAI_API_KEY` + optional `XAI_MANAGEMENT_API_KEY` | **free** lib; inference bills | **high** | `pip install xai-sdk`. Prefer this over hand-rolled curl for tool loops / batch / files. |
| 37 | **OpenAI-compat drop-in** | SDK shape | `OpenAI(base_url="https://api.x.ai/v1", api_key=…)`. Chat Completions **and** Responses. Vercel AI SDK `@ai-sdk/xai`. | API key | same | **high** | LiteLLM sidecar / Aider / any OpenAI-client worker pointed at xAI without a second adapter. Spend-gate still in front. |
| 38 | **Image generation / edit API** | REST | `POST /v1/images/generations` + `/v1/images/edits`. Models `grok-imagine-image-2.0` (current tool default), `grok-imagine-image`, `grok-imagine-image-quality`. Also a **conversation tool** so Grok can chain gen→edit in one request. | API key | from **$0.02–$0.08 / image** (see pricing table) | **med** | Not a COSMOS default. KDash assets / exhibit figures if Keith asks. Signed URLs expire (batch: 1h). |
| 39 | **Video generation / edit / extend** | REST | `POST /v1/videos/generations` (also `/v1/videos`), `/edits`, `/extensions`. `grok-imagine-video-1.5` (native 1080p T2V), `grok-imagine-video`. Async poll; SDK hides it. | API key | from **$0.05–$0.25 / sec** | **med** | Same "only if asked." Heavy weekly-pool consumer on grok.com; API is Console credits. |
| 40 | **TTS `POST /v1/tts`** | REST | Text → MP3 (and telephony formats). Voices e.g. `eve`. Inline speech tags. | API key | **$15 / 1M chars** | **med** | Phone/desktop voice out. COSMOS voice path already exists — vendor-plural, not default. |
| 41 | **STT `POST /v1/stt` + streaming** | REST / WS | File transcribe (12 formats, word timestamps, keyterms) or streaming. | API key | **$0.10 / hr REST**, **$0.20 / hr stream** | **med** | Voice in. Cheap vs STS. |
| 42 | **Speech-to-speech / Voice API** | WS | `wss://api.x.ai/v1/realtime?model=grok-voice-latest`. Server VAD, function calling (client executes), remote MCP. Ephemeral tokens for browsers. Custom voices. SIP for phone. | API key; ephemeral token for clients | **$0.08 / min** (2.0) + $0.004 text in | **med-high** (voice) | Phone clients. Mint secret **on COSMOS**, never ship `XAI_API_KEY` to the browser. |
| 43 | **Priority processing `service_tier: "priority"`** | API feature | Higher scheduling priority. Response echoes actual tier; only bill 2× if granted. | API key | **2× tokens** | **low-med** | Skip unless a live user is blocked on TTFT. |
| 44 | **gRPC API** | gRPC | Same products, protobuf at `xai-org/xai-proto`. Base `api.x.ai`. Bearer. | API key | same | **med** | `xai-sdk` already wraps this. Don't dual-implement. |
| 45 | **mTLS `https://mtls.api.x.ai`** | transport | Same paths, mutual TLS. | API key + client cert | same | **med** (enterprise) | Only if Keith requires it. |
| 46 | **Vertex AI partner Grok** | cloud API | Grok on GCP Model Garden. OpenAI-compat Responses + Chat Completions. ADC. | GCP ADC / Vertex | **GCP invoice** (not Console) | **med** | Only if leftover **$300 Vertex credit** should buy Grok instead of Gemini. `gem-api` already owns that credit — don't split without Keith. |
| 47 | **Microsoft Foundry Grok** | cloud API | Grok on Azure AI Foundry. Entra ID, Marketplace bill, optional Content Safety. | Azure identity | Azure invoice | **low-med** | No Azure rail today. Skip unless a Foundry credit appears. |
| 48 | **grok.com connectors (Gmail, Drive, Outlook, …)** | consumer + OAuth | Built-in OAuth connectors + catalog + custom MCP. Search mail/files/calendar **inside grok.com chat**. Team admin must provision for Business/Enterprise. | grok.com login + per-app OAuth | **prepaid SuperGrok pool** | **med** | DOM / Keith-owned. Not an API COSMOS can fire. Custom MCP on grok.com is a cousin of API remote-MCP (row 22). |
| 49 | **Grok Build background tasks / `/loop` / monitors / dashboard** | CLI TUI | Recurring prompts (`/loop 5m …`, max 50, expire 7d, min 60s), log monitors, `grok dashboard`. | `grok login` | **prepaid pool** | **med** | COSMOS already has OS scheduled tasks + collector. Do **not** use `/loop` as the mesh clock (Claude.md: Windows clock, not vendor app loops). |
| 50 | **Chat Completions deferred vs Batch vs Async** | (map) | Async SDK = parallel live calls (rate-limited). Deferred = one parked completion, 24h, retrieve once. Batch = many parked, discount on some models, 24h best-effort. | API key | see rows 26–28 | — | Use Batch for bulk; deferred for one long job; async for interactive fan-out. |
| 51 | **Standalone `/v1/embeddings`** | REST (thin) | Mentioned on the mTLS page as a path that exists. **No first-class docs page** in `llms.txt`. Collections generate embeddings internally for RAG. | API key | UNKNOWN (not on pricing page) | **low** until documented | Do not build a COSMOS embeddings rail on a one-line mention. Use Collections search. |
| 52 | **Agents / Teams / "invoke GBt" REST** | — | **Not documented.** No `team_id` / `bot_id` / Assistants-style threads targeting grok.com or Grok Bot. | — | — | **none** | Confirmed against 2026-08-25 `docs.x.ai` (Grok Bot is an app; API is stateless/stateful Responses). Mailbox remains the GBt path. Re-check this page if xAI ships a Bots API. |
| 53 | **DOM on console.x.ai / grok.com** | DOM | Billing, prepaid top-up, key mint (Management API **cannot** replace the first human checkout), rate-limit page, Collections UI, Batches UI, first OAuth, usage %. | Keith's browser | **free** | **high as fallback** | Existing `cosmos_browser` / Playwright MCP. Canon: DOM when the API depends on something that can run out (credits, weekly pool UI, card, key create). |

---

## Grok Build CLI flags COSMOS actually scripts

Official: [Headless](https://docs.x.ai/build/cli/headless-scripting), [CLI reference](https://docs.x.ai/build/cli/reference).

| flag | COSMOS use |
|------|------------|
| `-p` / `--single <PROMPT>` | non-interactive. The hand. |
| `--output-format plain\|json\|streaming-json` | ledger vs live |
| `--always-approve` / `--yolo` | auto-approve tools (deny rules + hooks still apply) |
| `--permission-mode dontAsk` | CI lock — deny unless `--allow` |
| `--allow` / `--deny` | fence (`Bash(git *)`, `Read`, `Grep`) |
| `--sandbox workspace\|strict\|read-only` | Landlock/Seatbelt |
| `-m` / `--model` | pin `grok-4.6` vs `grok-build-0.1` |
| `--effort low\|medium\|high\|xhigh` | reasoning |
| `-s` / `--session-id` | named new session |
| `-r` / `--resume` | continue |
| `-c` / `--continue` | last session in this cwd |
| `--cwd` | attempt-private workspace |
| `-w` / `--worktree` | isolated git checkout |
| `--max-turns` | hard stop |
| `--no-auto-update` | CI/scripts (also `[cli] auto_update = false`) |
| `--no-alt-screen` | no TUI takeover |
| `--tools` / `--disallowed-tools` | allowlist built-ins |
| `--no-plan` / `--no-subagents` / `--no-memory` / `--disable-web-search` | shrink blast radius |
| `--rules` / `--system-prompt-override` | inject COSMOS canon without editing CLAUDE.md |
| `grok agent stdio` | ACP |
| `grok inspect --json` | what loaded (rules/MCP/skills) — fail CI if a server did not |

Windows config: `%USERPROFILE%\.grok\config.toml`. Sessions: `%USERPROFILE%\.grok\sessions`.

---

## REST endpoints COSMOS might call (inference)

Base `https://api.x.ai/v1`. Bearer `XAI_API_KEY`.

| method | path | notes |
|--------|------|-------|
| POST | `/responses` | preferred |
| GET/POST | `/responses` (WS upgrade to `wss://…/v1/responses`) | websocket mode |
| POST | `/responses/compact` | compaction |
| POST | `/chat/completions` | legacy; `deferred: true` |
| GET | `/chat/deferred-completion/{request_id}` | 202 until ready |
| GET | `/models` | list + prices |
| GET | `/api-key` | this key's ACLs |
| POST | `/tokenize-text` | estimate |
| POST | `/batches` | create |
| POST | `/batches/{id}/requests` | add |
| GET | `/batches/{id}` | status |
| GET | `/batches/{id}/results` | page |
| POST | `/batches/{id}:cancel` | cancel |
| POST | `/files` | upload |
| POST | `/images/generations` · `/images/edits` | Imagine still |
| POST | `/videos` · `/videos/generations` · `/videos/edits` · `/videos/extensions` | Imagine motion |
| POST | `/tts` | speech out |
| POST | `/stt` | speech in |
| WS | `wss://api.x.ai/v1/realtime` | voice agent |
| — | Collections REST under `/developers/rest-api-reference/collections` | RAG CRUD + search |

---

## What COSMOS should actually turn on (scout recommendation, not a dispatch)

1. **Keep pouring coding into `grok -p` on SuperGrok Heavy** (96% headroom at last snapshot) + Cursor Ultra. Do **not** put `XAI_API_KEY` in that environment.
2. **Settle `sgh-api` / `gw-api` from `cost_in_usd_ticks`** — the UNPRICED estimates in the collector are the gap.
3. **Add Responses + `web_search`/`x_search` as an explicit spend-gated tool flag**, not the default on every chat. Live Search **is** those two tools.
4. **Batch + `grok-4.3`** for the 135-tool critique (20% off, 1M context, $1.25/$2.50).
5. **Do not build a Grok Bot RPC.** The docs still do not have one.
6. **Docs MCP** is free and should be in Grok Build / Claude Code MCP lists.

---

## Sources (this fetch)

Primary: [`https://docs.x.ai/llms.txt`](https://docs.x.ai/llms.txt) (full dump, 2026-08-25), plus the HTML pages listed in the URL map (pricing, models, rate limits, Grok Build overview, Grok Bot FAQ, consumer FAQ). Cross-checked against COSMOS artifacts: `docs/AGENT_BRIEF.md`, `docs/ROUTING.md`, `docs/MESH_ADDITIONS.md`, `cosmos/cosmos_node_rails.py`, `docs/SELFTEST_2026-08-25.md`, prior GBt note `docs/research/T1_SYNC_GBOT_COW/research_grok.md` (the "no team RPC" finding still holds).
