# OPENAI HANDS — G46 scout return (OpenAI Platform + Codex CLI)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25 (docs fetched live).
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim except where a COSMOS artifact is named.
**No COSMOS core code was edited.** Maker-docs sweep (DHx assignment log): each maker's hands → `docs/research/<MAKER>_HANDS.md`.

**Already on the mesh (do not re-add as "new"):** Dispatcher rail **`oa-api`** (`bts_oa_api`) — OpenAI API, spend-gated **$0.05/call, $5 cap** (`cosmos/cosmos_node_rails.py`, `docs/MESH_ADDITIONS.md`, `docs/SELFTEST_2026-08-25.md`: `SPEND_SETTLED` measured). This file inventories every OpenAI **hand** COSMOS could fire, including the ones already wired.

**Filter:** a surface with no hands is rejected. Every row is an **action** COSMOS could fire: REST endpoint, CLI flag, SDK call, MCP tool, GitHub Action, or DOM fallback. ChatGPT chat-only chrome is out unless it is a dispatchable CLI/API (Codex) or the DOM fallback (billing, key mint, first OAuth).

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks. Equal power, cheaper wins. Metered Platform API sits **below** the Codex CLI / ChatGPT-plan cluster even when the model is the same family — ChatGPT login draws a **different wallet** from `oa-api` prepaid credits.

**Docs home (URL map):** `https://platform.openai.com/docs` now **redirects** to `https://developers.openai.com/api/docs`. Codex product docs live at `https://learn.chatgpt.com/docs` (and still answer at `developers.openai.com/codex/…` with another redirect). Both families are cited below. Markdown twins: append `.md`. Combined dump: [llms-full.txt](https://developers.openai.com/api/docs/llms-full.txt). Index: [llms.txt](https://developers.openai.com/api/docs/llms.txt).

---

## How COSMOS reaches OpenAI (reach column, one pattern)

Core stays sole ledger writer. OpenAI is reached as:

| Lane | Mechanism | When |
|------|-----------|------|
| **A. Native Codex CLI** | `codex exec "…"` inside an attempt-private workspace. JSON via `--json`. Schema via `--output-schema`. Sandbox `--sandbox workspace-write`. Apache-2.0 OSS ([github.com/openai/codex](https://github.com/openai/codex)). | Preferred OpenAI **coding-agent** lane. Draws ChatGPT plan quota **or** a metered API key. Matches "no bats — in-app / COSMOS action." |
| **B. HTTP Platform API (Responses)** | `POST https://api.openai.com/v1/responses`. Header `Authorization: Bearer $OPENAI_API_KEY`. Official Python/TS SDKs default to this. | **Already `oa-api`.** Recommended for all new API work. Built-in tools, MCP, structured outputs, stateful `previous_response_id`. |
| **C. HTTP Chat Completions** | `POST https://api.openai.com/v1/chat/completions`. Still supported; **not** recommended for new work. | Compat for workers that already speak Chat Completions (Aider, LiteLLM). Same key, same spend-gate. |
| **D. Batch API** | JSONL upload `purpose=batch` → `POST /v1/batches` → poll → download results. 50% of list. 24h window. | Overnight bulk eval / critique. Return-watcher on `completed`. |
| **E. MCP-client / MCP-server** | Codex CLI is an MCP **host**. Responses API talks to remote Streamable-HTTP MCP (`type: mcp`). OpenAI hosts a **docs MCP** at `https://developers.openai.com/mcp`. | Agent brains get forge/browser/docs tools. Core should prefer native `codex`/`gh`/`glab` over giving itself a shell via MCP. |
| **F. Forge CI** | `openai/codex-action` — CI autofix, review, `codex exec` on a runner via a Responses API **proxy** (key never in the job env of untrusted code). | Overflow coding on `keithbbf-gif/cosmos`. Lease so it does not double-write with Cursor Cloud Agents. |
| **G. DOM** | [platform.openai.com](https://platform.openai.com) billing / keys / spend limits; [chatgpt.com/codex](https://chatgpt.com/codex) cloud agent; first OAuth. | Fallback only. Canon: DOM first when the API depends on something that can run out (prepaid balance, ChatGPT weekly window, key expiry). |

Keith owns credentials. Store under `live/config/` (git-ignored). Never hard-code. Never print a key in full. Fenced commit still gates any tree write.

---

## Auth primer (all API/CLI rows inherit this unless overridden)

Base: `https://api.openai.com`. Required header: `Authorization: Bearer <key-or-token>`. Optional: `OpenAI-Organization`, `OpenAI-Project`. Header budget **&lt; 64 KiB**. Log `x-request-id` (and optional `X-Client-Request-Id`) for support.

| method | credential | header / env | COSMOS use |
|--------|------------|--------------|------------|
| **Platform API key** | `sk-…` from [API keys](https://platform.openai.com/settings/organization/api-keys) | `Authorization: Bearer`. Env `OPENAI_API_KEY` | Default for `oa-api`. Spend-gated. **Secret — server only.** |
| **Admin API key** | separate key from [admin keys](https://platform.openai.com/settings/organization/admin-keys) | same Bearer | Org users, invites, audit logs, spend. **Not** for inference. |
| **Workload identity federation** | short-lived token from IdP (GitHub Actions, GCP, AWS, Azure, K8s, SPIFFE, X.509) | Bearer access token | CI / production. No long-lived `sk-` in the environment. Official: [WIF](https://developers.openai.com/api/docs/guides/workload-identity-federation). |
| **Codex CLI ChatGPT login** | OAuth via `codex login` → `~/.codex/auth.json` | CLI manages it | Default for interactive + `codex exec` on a machine Keith signed in. Draws **ChatGPT plan Codex allowance**, not Platform credits. Treat `auth.json` like a password. |
| **Codex API key (automation)** | `CODEX_API_KEY` (preferred over job-level `OPENAI_API_KEY`) | CLI env, **scoped to the invocation** | CI. Official GitHub Action uses a **proxy** so the key never sits in the job env of repo-controlled code. |
| **Realtime ephemeral client secret** | `POST /v1/realtime/client_secrets` | browser/mobile WebRTC | Phone/voice clients. Mint on the **server** (COSMOS), hand the short-lived secret to the client. |
| **Remote MCP** | per-server token in `tools[].headers` / Codex `codex mcp login` | MCP transport | Streamable HTTP. |

**Two wallets — do not conflate them.** A leftover `OPENAI_API_KEY` in the environment of a Codex CLI job **bills the Platform org** instead of the ChatGPT seat. `/status` (Codex TUI) and the [usage dashboard](https://chatgpt.com/codex/settings/usage) are ground truth for which method is live.

---

## ARCH env isolation (additive, 2026-08-25) — H5 / A5 / B2

Two-wallet theft: leftover `OPENAI_API_KEY` steals Codex off the ChatGPT seat onto `oa-api`. `live/config/` this pass has **no** `OPENAI_API_KEY` file.

**ARCH rule:** `codex exec` queue jobs that should draw a ChatGPT seat **unset** `OPENAI_API_KEY` (prefer ChatGPT login / `CODEX_API_KEY` scoped to the invocation). `oa-api` HTTP jobs **set** the Platform key in an isolated env. Do not mix. `--sandbox workspace-write` for unattended jobs. ChatGPT Plus/Pro seat existence: **UNKNOWN** (B2; `codex login status` not run). Assistants API shuts **2026-08-26** — do not add an Assistants client.

**WAVE A5:** point MCP hosts at **`https://developers.openai.com/mcp`** (no key). Already-on-mesh `oa-api` speaks **Responses**, not Chat Completions, for new work. Dispatcher new rails wait on Kernel attach. This is **not** a stage-6 pass.

---

## Host bind (additive, 2026-08-27 s6 re-probe) — U3 closed / A5 not configured

This process (`cmd /c "codex login status"` — PowerShell `codex.ps1` is execution-policy blocked):

- **`Logged in using ChatGPT`** — U3 **closed**. B2 is a **distinct ChatGPT-seat wallet**, not `oa-api`. Unset `OPENAI_API_KEY` in that job env still (H5).
- Assistants API sunset was **2026-08-26**; do not add an Assistants client.
- WAVE A5 OpenAI Docs MCP (`https://developers.openai.com/mcp`): **not** in Grok Build / Cursor / Gemini MCP lists this pass (Grok=`BFast` only; Cursor=`bts` only; Gemini=`BFast` only). Not a wired COSMOS hand.

---

## Cost floor (two wallets — do not mix)

Mixing ChatGPT-plan Codex quota with Platform prepaid credits is how `oa-api` gets burned by accident. Official: **ChatGPT and the API are separate billing containers** (same login can own both).

| Wallet | What official docs say | COSMOS note |
|--------|------------------------|-------------|
| **ChatGPT Free / Go / Plus / Pro seat** | Codex is **included** on Free, Go ($8), Plus ($20), Pro ($100 5× / $200 20×), Business, Enterprise. Shared **5-hour rolling window** + weekly cap. Free = try-it, not a workhorse. Plus local 5h window (official estimates): GPT-5.6 Sol 10–100 msgs, Terra 25–200, Luna 250–2,000. After included limits, buy **credits**. [Codex pricing](https://learn.chatgpt.com/docs/pricing.md) · [Help: Codex + ChatGPT plan](https://help.openai.com/articles/11369540). | Highest-ranked OpenAI **coding** lane. Keith's SuperGrok Heavy / Cursor Ultra is **not** this wallet — probe whether a ChatGPT Plus/Pro seat exists before treating Codex as prepaid. |
| **Codex credits (after included)** | Token-based credit rate card (credits / 1M tok). GPT-5.6 Sol 100/10/500; Terra 50/5/300; Luna 5/0.5/30. Fast mode costs more. Image gen 3–5× a text turn. | Real money on the ChatGPT bill, **not** `oa-api`. |
| **Platform API prepaid credits** | New accounts: **prepaid**. Min purchase **$5** (default $10). Free credits in the account (if any) spend **first**. Purchased credits **expire 1 year, non-refundable**. Auto-recharge min $5. $0 balance → requests fail (`credit_balance_exhausted`). [Help: prepaid](https://help.openai.com/en/articles/8264778-what-is-prepaid-billing). Quickstart still says "Congrats on running a **free test** API request" then "Add credits." | This is `oa-api`. **No standing $5 trial for new orgs** (phased out ~mid-2025; confirmed by Platform billing docs + community FAQ). Budget-gate it. MESH cap **$5**. |
| **Moderation** | `omni-moderation-latest` is **free of charge**. | Always-on safety gate. |
| **File search storage** | **1 GB free**, then **$0.10 / GB / day**. Tool call **$2.50 / 1k** (Responses API only). | Cheap RAG until 1 GB. |
| **Web search (Responses tool)** | **$10 / 1k calls** + search-content tokens at model rates (preview non-reasoning: $25 / 1k, content tokens free). | Do not enable on a COSMOS loop without a spend cap. |
| **Containers (hosted Shell / Code Interpreter)** | 1 GB $0.03 · 4 GB $0.12 · 16 GB $0.48 · 64 GB $1.92 **per 20-min session**. Eligible sessions billed by the minute, **5-min minimum**. | Tokens also bill at model rates. |
| **Batch API** | **50% of Standard** list. Separate rate-limit pool. Completes within 24 h. Results deleted 30 days after complete. | Bulk eval. |
| **Flex processing** | ~50% of Standard, higher latency. | Async jobs that are not Batch. |
| **Fast mode** (was "priority") | ~2× Standard (`service_tier: "fast"` or `"priority"`). Renamed 2026-07-30. | Only if latency is the product. |
| **Embeddings** | `text-embedding-3-small` **$0.02 / 1M**; large $0.13; ada-002 $0.10. Batch 50%. | Collector / RAG. |
| **Fine-tuning** | Platform **winding down**. New orgs cannot create jobs (since 2026-05-07). Existing customers: last new jobs **2027-01-06**. Inference until the **base model** is deprecated. | Do **not** start a new COSMOS fine-tune. |
| **SDKs / Codex CLI binary / Agents SDK / Docs MCP** | **$0** to install (Apache/MIT OSS). | Inference still bills. |
| **Admin / spend-limit / models list** | **Free** to call (Admin key where required). | Hygiene + spend-gate. |

**List rates fetched 2026-08-25** from [Pricing](https://developers.openai.com/api/docs/pricing.md) (USD / million tokens, **Standard**). Flagship family as of this fetch: **GPT-5.6 Sol / Terra / Luna**. GPT-5.6 Sol promotional pricing holds **at least through 2026-11-21**. Regional processing: **+10%** for models released on/after 2026-03-05.

| Model | Input | Cached in | Output | Batch in / out |
|-------|-------|-----------|--------|----------------|
| gpt-5.6-sol (short) | $4.00 | $0.40 | $20.00 | $2.00 / $10.00 |
| gpt-5.6-terra (short) | $2.00 | $0.20 | $12.00 | $1.00 / $6.00 |
| gpt-5.6-luna (short) | $0.20 | $0.02 | $1.20 | $0.10 / $0.60 |
| gpt-5.5 (&lt;272k) | $5.00 | $0.50 | $30.00 | $2.50 / $15.00 |
| gpt-5.4 (&lt;272k) | $2.50 | $0.25 | $15.00 | $1.25 / $7.50 |
| gpt-5.4-mini | $0.75 | $0.075 | $4.50 | $0.375 / $2.25 |
| gpt-5.2 | $1.75 | $0.175 | $14.00 | $0.875 / $7.00 |
| gpt-5-mini | $0.25 | $0.025 | $2.00 | $0.125 / $1.00 |
| gpt-5-nano | $0.05 | $0.005 | $0.40 | $0.025 / $0.20 |
| gpt-4o-mini | $0.15 | $0.075 | $0.60 | $0.075 / $0.30 |
| gpt-5.3-codex (specialized) | $1.75 | $0.175 | $14.00 | — |
| text-embedding-3-small | $0.02 | — | — | $0.01 |
| omni-moderation-latest | **Free** | — | — | Free |

Realtime audio (gpt-realtime-2.1): **$32 / 1M audio in**, $64 audio out; text $4 / $24. Whisper-class file transcribe ~$0.0045–$0.006 / min. Sora-2 video **shuts down 2026-09-24** — do not build on it.

---

## Ranking table

| # | name | kind | HANDS (what it DOES) | auth | cost | power | how COSMOS reaches it |
|---|------|------|----------------------|------|------|-------|------------------------|
| 1 | **Codex CLI `codex exec` (headless)** | CLI + agent | Open-source **terminal agent** (Apache-2.0): inspects/edits the attempt workspace, runs shell under a sandbox, web-search, MCP, skills, review. `codex exec "…"` non-interactive; progress on stderr, final message on stdout. `--json` JSONL events (`thread.started` / `turn.*` / `item.*` with `usage`). `--output-schema` JSON Schema. `--sandbox workspace-write`. `--ephemeral`. `codex exec resume --last`. Must run inside a git repo (override `--skip-git-repo-check`). | `codex login` ChatGPT **or** `CODEX_API_KEY` for one invocation. CI: prefer `openai/codex-action` proxy. | **Tool free.** Inference: ChatGPT Free (tiny) / Plus–Pro **prepaid seat** / API key = Platform list rates. | **highest** | Native worker: Windows install `irm https://chatgpt.com/codex/install.ps1 \| iex` (Keith runs once) or `npm i -g @openai/codex`. Queue: `codex exec --json --sandbox workspace-write --output-schema schema.json "…"`. Bind DONE to JSONL `turn.completed` + `usage`. Never a `.bat`. Prefer ChatGPT login so it does **not** burn `oa-api`. | [CLI](https://learn.chatgpt.com/docs/codex/cli.md) · [non-interactive](https://learn.chatgpt.com/docs/non-interactive-mode.md) · [flags](https://learn.chatgpt.com/docs/developer-commands.md?surface=cli) · [repo](https://github.com/openai/codex) |
| 2 | **`--json` / `--output-schema` / `-o`** | CLI | Machine-readable COSMOS return: JSONL event stream + schema-validated final JSON + last-message file. `turn.completed.usage` has input / cached / output / reasoning tokens. | same as row 1 | **included** | **highest** | Runtime binding: ledger the `thread_id` + `usage` + schema JSON. Pair `--json` with `--output-last-message` in CI. | [non-interactive](https://learn.chatgpt.com/docs/non-interactive-mode.md) |
| 3 | **Codex as MCP host** (`codex mcp`) | MCP client | `codex mcp add <name> -- <stdio>` or `--url`. STDIO + Streamable HTTP. `codex mcp login` OAuth. `/mcp` lists tools. Connects GitHub, Playwright, Context7, OpenAI Docs MCP. | MCP OAuth or `--env` secrets | **free** protocol; tokens when used | **highest** | Point at GitHub MCP / Playwright / COSMOS MCP **from the Codex worker**, not from Core. `required = true` on a server → `codex exec` **exits** if it fails to init (fail-closed). | [MCP](https://developers.openai.com/codex/mcp) · [learn MCP](https://learn.chatgpt.com/docs/extend/mcp) |
| 4 | **OpenAI Docs MCP** | MCP server (hosted) | Read-only search + page content for `developers.openai.com`, `platform.openai.com`, `learn.chatgpt.com`. **Does not** call the API on your behalf. URL: `https://developers.openai.com/mcp`. | none | **free** | **high** | `codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp`. Also usable from Cursor / Claude Code. Grounds OpenAI-hand research without scraping. | [docs MCP](https://developers.openai.com/learn/docs-mcp.md) |
| 5 | **Official Python / TS SDKs** | SDK (OSS) | `pip install openai` / `npm i openai`. Default primitive is **Responses**. Auto-reads `OPENAI_API_KEY`. Helpers: `responses.parse` (Pydantic/Zod), streaming, files, batches, realtime, vector stores. | API key | **free** SDK; inference metered | **highest** (programmatic) | COSMOS Python worker. `from openai import OpenAI; client.responses.create(...)`. This is the **shape** of `oa-api`. Do not invent a second client. | [libraries](https://developers.openai.com/api/docs/libraries.md) · [quickstart](https://developers.openai.com/api/docs/quickstart.md) |
| 6 | **OpenAI CLI (`openai`)** | CLI | Generated official CLI: `openai responses create --model gpt-5.6 --input "…"`. YAML stdin, `--transform` GJSON, files, speech, batches. Distinct from `codex`. | `OPENAI_API_KEY` | **free** CLI; API bills | **high** | Native worker alternative to curl for the metered rail. `brew install openai/tools/openai`. | [OpenAI CLI](https://developers.openai.com/api/docs/libraries/openai-cli.md) |
| 7 | **Agents SDK** (Python / TS) | SDK + agent | Code-first orchestration: tools, handoffs, guardrails, tracing, sandboxes. Wraps Responses. `@function_tool` / `tool()`. Can call **Codex as MCP** (`codex mcp-server` is deprecated — use app-server). | API key | **OSS free**; tokens metered | **highest** (orchestration) | `pip install openai-agents`. Optional COSMOS-external agent runtime. Overlaps Core scheduler — use when a worker needs an agent loop, not as a second OS. | [Agents](https://developers.openai.com/api/docs/guides/agents.md) · [Py](https://github.com/openai/openai-agents-python) · [JS](https://github.com/openai/openai-agents-js) |
| 8 | **Moderation API** (`omni-moderation-latest`) | REST | `POST /v1/moderations`. Text + images (20 MB). Categories: harassment, hate, illicit, self-harm, sexual, violence (+ graphic/minors variants). Also inline `moderation: {model:…}` on Responses. | API key | **FREE** | **high** (safety) | Spend-gate-adjacent: classify queue prompts / returned artifacts before they hit the ledger or KDash. Not a substitute for COSMOS fail-closed. | [moderation](https://developers.openai.com/api/docs/guides/moderation.md) · [pricing](https://developers.openai.com/api/docs/pricing.md) |
| 9 | **Responses API** (`POST /v1/responses`) | REST + SDK | **The** Platform hand. Input items → output items. Built-in tools (web_search, file_search, code_interpreter, computer_use, image_gen, MCP, shell, skills, apply_patch). Stateful `previous_response_id` / Conversations. Streaming SSE. Structured `text.format`. Background mode. Stored by default (`store: false` to opt out). Official: **recommended for all new projects.** 3% SWE-bench lift vs Chat Completions on same prompt; 40–80% better cache util. | API key / WIF | **metered** list rates. No extra "Responses fee." | **highest** (already `oa-api`) | **Existing rail.** Prefer this over Chat Completions for new `oa-api` work. `client.responses.create(model="gpt-5.6-luna", input=…)`. Fail-closed on 429 / `credit_balance_exhausted`. | [migrate](https://developers.openai.com/api/docs/guides/migrate-to-responses.md) · [create](https://developers.openai.com/api/reference/resources/responses/methods/create) · [platform twin](https://platform.openai.com/docs/guides/migrate-to-responses) |
| 10 | **Function calling / tool calling** | API feature | Model emits `function_call` items (`name`, JSON `arguments`, `call_id`); **COSMOS executes**; send `function_call_output`. Strict mode = Structured Outputs on the schema. Parallel calls. `tool_choice` auto/required/none/forced. Namespaces. Custom tools (free-form + CFG grammar). | API key | **$0 extra** (tokens; function defs count as input) | **highest** | Declare COSMOS verbs (ledger-read, queue-submit, collector) as `strict: true` functions. Do **not** give Core a shell; give the worker scoped functions. Reasoning models: round-trip reasoning items with tool outputs. | [function calling](https://developers.openai.com/api/docs/guides/function-calling.md) |
| 11 | **Structured Outputs** (`text.format` / `json_schema`) | API feature | Guaranteed JSON Schema adherence (`strict: true`). SDK `responses.parse` → Pydantic/Zod. Refusals detectable. Available on Responses, Chat Completions, Batch, (legacy) Assistants. Prefer this over JSON mode. | API key | tokens | **highest** (reliability) | Always on for COSMOS machine-readable returns (critique JSON, collector records). CLI twin: `codex exec --output-schema`. | [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs.md) |
| 12 | **Token counting** (`POST /v1/responses/input_tokens`) | REST | Count input tokens **before** send. Same shape as Responses (text, images, files, tools). Includes formatting tokens tiktoken misses. | API key | count-only (use as spend-gate preflight; not a generation) | **high** (infra) | Spend-gate calls this before `oa-api` generate. Pair with remaining credit + ChatGPT `/status`. | [token counting](https://developers.openai.com/api/docs/guides/token-counting.md) |
| 13 | **Chat Completions + tools** (`POST /v1/chat/completions`) | REST | Stateless messages array. Function calling (`tools[].function`), `response_format` JSON schema, vision, streaming. **Still supported.** Missing native web_search / file_search / MCP / computer_use / code_interpreter. GPT-5.4+: tool calling with `reasoning_effort` other than `none` is Responses-only. | API key | same model prices | **high** (compat) | Keep for Aider / LiteLLM / OpenAI-shaped workers. New COSMOS code should emit Responses. Same `oa-api` spend-gate — **one ledger**. | [migrate table](https://developers.openai.com/api/docs/guides/migrate-to-responses.md) · [Chat ref](https://developers.openai.com/api/reference/resources/chat) |
| 14 | **Prompt caching** | API feature | Automatic prefix cache. Cached input ~**0.1×**. Put stable COSMOS canon **first**. | API key | cache-read column on pricing | **high** (cost) | Always-on for repeated system prompts. Check `input_tokens_details.cached_tokens`. | [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching.md) |
| 15 | **Files API** | REST | `POST /v1/files` multipart. Purposes: `user_data`, `assistants` (vector stores), `batch`, `vision`. Then pass `file_id` into Responses (`input_file`). | API key | upload **$0**; tokens when used as input | **high** | Upload a dissertation PDF / exhibit once, pass `file_id` across turns. Hash locally; pointer in ledger. | [file inputs](https://developers.openai.com/api/docs/guides/file-inputs.md) · [Files ref](https://developers.openai.com/api/reference/resources/files) |
| 16 | **Vector stores + File Search** | REST + hosted tool | Create store → attach files (`purpose=assistants`) → `tools: [{type:"file_search", vector_store_ids:[…]}]`. Semantic + keyword. Citations. `max_num_results`, metadata filters. Hosted — OpenAI runs retrieval. | API key | **1 GB storage free**, then $0.10/GB-day; **$2.50 / 1k tool calls** + tokens | **high** | Managed RAG for chapter/legal corpus. Alternative to local embeddings+SQLite. Poll file status=`completed` before search. | [file search](https://developers.openai.com/api/docs/guides/tools-file-search.md) · [retrieval](https://developers.openai.com/api/docs/guides/retrieval.md) |
| 17 | **Embeddings** | REST | `POST /v1/embeddings`. `text-embedding-3-small` / `large` / `ada-002`. Batch 50%. | API key | $0.02 / $0.13 / $0.10 per 1M | **high** | Collector / duplicate detection / local RAG. Prefer File Search (row 16) if managed RAG is enough. | [embeddings](https://developers.openai.com/api/docs/guides/embeddings.md) |
| 18 | **Batch API** | REST | JSONL of `/v1/responses` **or** chat **or** embeddings **or** images **or** videos **or** moderations. 50k req, 200 MB, 24 h, separate RPM/TPM pool. `custom_id` to join results (order **not** preserved). Cancel supported. | API key | **50%** of Standard | **high** (bulk) | Overnight Motif/critique/port-backlog. COSMOS submit → batch → return-watcher on `completed`. Match by `custom_id`. | [batch](https://developers.openai.com/api/docs/guides/batch.md) · [ref](https://developers.openai.com/api/reference/resources/batches) |
| 19 | **Web search (hosted tool)** | API built-in tool | `tools: [{type:"web_search"}]`. Model searches, synthesizes, cites. | API key | **$10 / 1k calls** + content tokens | **high** (cited web) | Vendor-plural with Firecrawl/SGH DOM. Spend-cap it. Prefer `input_file` / URL for known docs. | [web search](https://developers.openai.com/api/docs/guides/tools-web-search.md) |
| 20 | **Code Interpreter (hosted container)** | API built-in tool | `tools: [{type:"code_interpreter", container:{type:"auto"}}]`. Model writes Python; OpenAI runs it. | API key | container session SKU + tokens | **high** | Math/CSV/plots **without** Keith's shell. Not a replacement for attempt-private workspaces. | [code interpreter](https://developers.openai.com/api/docs/guides/tools-code-interpreter.md) |
| 21 | **Remote MCP in Responses** | API tool | `tools: [{type:"mcp", server_label, server_url, require_approval, allowed_tools}]`. OpenAI is the MCP client. Streamable HTTP (or legacy SSE). | API key + MCP bearer | tokens + MCP server | **high** | Cloud-agent path: `oa-api` talks to GitHub/Playwright MCP without COSMOS hosting the loop. Local stdio stays on Codex CLI. | [MCP / connectors](https://developers.openai.com/api/docs/guides/tools-connectors-mcp.md) |
| 22 | **Tool search + namespaces** | API feature | Defer large tool surfaces (`defer_loading: true`); model loads what it needs. **gpt-5.4+ only.** | API key | tokens (deferred tools not in every prompt) | **high** | When COSMOS grows 20+ function tools. Keep start-of-turn &lt;20 live. | [tool search](https://developers.openai.com/api/docs/guides/tools-tool-search.md) |
| 23 | **Streaming Responses** | API feature | SSE typed events: `response.output_text.delta`, `response.function_call_arguments.delta`, `response.completed`. | API key | same as Responses | **med-high** | KDash live token view on `oa-api`. | [streaming](https://developers.openai.com/api/docs/guides/streaming-responses.md) |
| 24 | **Conversations API / `previous_response_id`** | REST | Server-side item streams (not just messages). Chain turns without resending the transcript. `store: true` default. ZDR orgs: `store: false` + encrypted reasoning items. | API key | prior-chain tokens **still billed** as input | **high** | Multi-turn `oa-api` jobs. Capture `response.id`, pass `previous_response_id`. Resend `instructions` each turn (they do **not** carry). | [conversation state](https://developers.openai.com/api/docs/guides/conversation-state.md) |
| 25 | **Background mode + webhooks** | REST | Long Responses run async; webhook on complete. | API key | tokens | **high** (infra) | Point at Core return-watcher (`cosmos up` / Tailscale). | [background](https://developers.openai.com/api/docs/guides/background.md) · [webhooks](https://developers.openai.com/api/docs/guides/webhooks.md) |
| 26 | **`codex review` / `/review`** | CLI | Non-interactive working-tree / commit / base-branch review. Does **not** modify files. | same as Codex | ChatGPT quota or API | **high** | Queue a review job before fenced commit. GitHub `@Codex` reviews are a **separate** Code Review allowance (cloud only). | [review](https://learn.chatgpt.com/docs/code-review) |
| 27 | **Codex GitHub Action** (`openai/codex-action`) | Actions | Installs Codex, starts a Responses **proxy**, runs `codex exec` without putting `OPENAI_API_KEY` in the job env of repo-controlled code. Official autofix-on-CI-failure recipe. | repo secret `OPENAI_API_KEY` → action input only | API tokens + Actions minutes (public = $0 minutes) | **high** | Workflow on `keithbbf-gif/cosmos`. Lease vs Cursor Cloud Agents. Prefer this over a raw `codex exec` step. | [non-interactive CI](https://learn.chatgpt.com/docs/non-interactive-mode.md) · [action](https://github.com/openai/codex-action) |
| 28 | **Codex cloud + `codex cloud exec`** | cloud agent | Browser/phone sessions against a GitHub repo; CLI `codex cloud` picker / `codex cloud exec` submit / `codex apply` to pull the diff locally. Slack, Linear, `@codex` on issues/PRs. **Not available with API-key auth.** | ChatGPT login | **prepaid seat** | **med-high** | Deep URL for Keith: [chatgpt.com/codex](https://chatgpt.com/codex). Do not use as the Motif runtime-binding gate — that's Keith's machine. Cloud chats unavailable on API-key path. | [cloud](https://learn.chatgpt.com/docs/cloud) · [pricing matrix](https://learn.chatgpt.com/docs/pricing.md) |
| 29 | **Codex skills / plugins / AGENTS.md** | config | `.` skills, plugin marketplaces, nested `AGENTS.md`. `/init` scaffolds. | Codex session | **included** (tokens) | **high** | Commit COSMOS `AGENTS.md` + skills (`/cosmos-fence-check`). Keep it short — injected every turn. | [skills](https://learn.chatgpt.com/docs/skills-and-plugins) · [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) |
| 30 | **Codex sandbox + permissions** | CLI | `--sandbox read-only` (exec default) / `workspace-write` / `danger-full-access`. `/permissions`. Windows elevated sandbox `/setup-default-sandbox`. | local | **included** | **high** (safety) | Headless COSMOS: `--sandbox workspace-write` in the attempt workspace. Never `danger-full-access` on the live tree. | [approvals](https://learn.chatgpt.com/docs/agent-approvals-security) |
| 31 | **Models API** (`GET /v1/models`) | REST | List + retrieve. Ground-truth model IDs. | API key | **free** | **med** | Probe before dispatch so COSMOS never hard-codes a retired snapshot (`gpt-5-2025-08-07` dies 2026-12-11). | [models](https://developers.openai.com/api/docs/models.md) · [deprecations](https://developers.openai.com/api/docs/deprecations.md) |
| 32 | **Spend limits + usage dashboard** | Admin + DOM | Org/project monthly hard cap → `429 organization_spend_limit_exceeded` / `project_spend_limit_exceeded`. Alerts do **not** stop traffic. Separate from OpenAI-assigned usage-tier limit. | org/project admin | **free** to set | **high** (hygiene) | Mirror COSMOS spend-gate. Keith sets the Platform hard cap; Core still reserves/settles. | [spend limits](https://developers.openai.com/api/docs/guides/spend-limits.md) · [org limits](https://platform.openai.com/settings/organization/limits) |
| 33 | **Admin APIs** | Admin REST | Users, invites, projects, API keys, audit logs. Admin key **or** WIF. | Admin key | **free** | **med-high** | Inventory keys, expire unused. Keith does money/credentials; COSMOS can *report*. | [admin](https://developers.openai.com/api/docs/guides/admin-apis.md) · [RBAC](https://developers.openai.com/api/docs/guides/rbac.md) |
| 34 | **Flex / Fast service tiers** | API config | `service_tier: "flex"` (~50%) or `"fast"`/`"priority"` (~2×). | API key | Flex 50%; Fast ~2× | **med** | Spend-gate `serviceTier`. Default Standard. Batch is the other 50% path (24 h). | [flex](https://developers.openai.com/api/docs/guides/flex-processing.md) · [fast](https://developers.openai.com/api/docs/guides/fast-mode.md) |
| 35 | **Realtime API (GA)** | WS / WebRTC / SIP | Speech-to-speech agents. `gpt-realtime-2.1` (+ mini). Transcription `gpt-live-transcribe`. Translation dedicated endpoint. Tools + MCP in-session. Ephemeral `POST /v1/realtime/client_secrets`. Beta header **removed** (beta died 2026-05-12). | API key (server) → ephemeral secret (client) | audio **$32/$64 per 1M** (2.1); mini cheaper | **med** (voice) | Phone/voice clients. Mint secrets in COSMOS Core; never ship `sk-` to the APK. Safety identifier header recommended. | [realtime](https://developers.openai.com/api/docs/guides/realtime.md) · [voice agents](https://developers.openai.com/api/docs/guides/voice-agents.md) · [WebRTC](https://developers.openai.com/api/docs/guides/realtime-webrtc.md) |
| 36 | **Audio file APIs** (TTS / STT) | REST | `gpt-4o-mini-tts`, `tts-1`/`tts-1-hd` (char-priced), `gpt-transcribe` / `gpt-4o-transcribe` / Whisper. | API key | TTS $12/1M audio out (4o-mini) or $15–$30 / 1M chars; STT ~$0.003–$0.006/min | **med** | Voice surface / meeting minutes. Not coding. | [TTS](https://developers.openai.com/api/docs/guides/text-to-speech.md) · [STT](https://developers.openai.com/api/docs/guides/speech-to-text.md) |
| 37 | **Image generation** (`gpt-image-2`) | REST + tool | Generate/edit. Also `tools: [{type:"image_generation"}]` on Responses. DALL·E 2/3 **already shut down 2026-05-12**. `gpt-image-1*` die 2026-12-01. | API key | image $8 in / $30 out per 1M tok (gpt-image-2); Batch 50% | **med** | KDash/docs figures. Not a coding rail. | [image gen](https://developers.openai.com/api/docs/guides/image-generation.md) |
| 38 | **Computer use** | API tool | `computer` tool: click/type/scroll/screenshot. Client or hosted. Preview models can be retired with 2-week notice. | API key + COSMOS supplies the desktop | tokens + image tokens | **med** | Vendor-plural with Playwright / browser-use. **Not default.** Contained worker VM only. | [computer use](https://developers.openai.com/api/docs/guides/tools-computer-use.md) |
| 39 | **Deep research** | API tool / models | Multi-step web research reports. Older `o3-deep-research` snapshots **already shut 2026-07-23**; use current GPT-5.6 family + tools. | API key | expensive (many search calls + tokens) | **med-high** | Chapter-4 citation sweeps — cap it. SGH DOM remains the prepaid search rail. | [deep research](https://developers.openai.com/api/docs/guides/deep-research.md) |
| 40 | **Shell / apply_patch / skills (hosted)** | API tools | Hosted shell container, structured diffs, reusable skill bundles. | API key | container SKU + tokens | **med** | Only if COSMOS is implementing its own agent loop on Responses. Codex CLI already has Read/Edit/Bash. | [shell](https://developers.openai.com/api/docs/guides/tools-shell.md) · [apply_patch](https://developers.openai.com/api/docs/guides/tools-apply-patch.md) · [skills](https://developers.openai.com/api/docs/guides/tools-skills.md) |
| 41 | **tiktoken** | OSS lib | Local BPE token count. Incomplete for images/tools. | none | **free** | **med** (approx) | Fast local estimate; **authoritative** count is row 12. | [tiktoken](https://github.com/openai/tiktoken) |
| 42 | **ChatKit** | embed | Embeddable chat widget. Agent Builder is **deprecated** (shutdown 2026-11-30); ChatKit **stays**. 1 GB/mo file upload free then $0.10/GB-day. | API | tokens + storage | **low-med** | KDash already exists. Skip unless Keith wants an OpenAI-hosted chat chrome. | [ChatKit](https://developers.openai.com/api/docs/guides/chatkit.md) |
| 43 | **Azure OpenAI / Bedrock** | cloud API | Same models, cloud IAM + invoice. Feature lag vs first-party. Bedrock billed through AWS. | Azure/AWS creds | cloud invoice | **med** | Only if Keith already has Azure OpenAI. Don't split `oa-api` across two bills without a reason. | [Bedrock](https://developers.openai.com/api/docs/guides/amazon-bedrock.md) |
| 44 | **GPT Actions / Custom GPTs** | ChatGPT product | Natural-language → REST against a 3rd-party OpenAPI. OAuth/API-key. **ChatGPT**, not the Platform agent loop. | ChatGPT login + action auth | ChatGPT plan | **low** | Not a COSMOS worker. DOM only. | [GPT Actions](https://developers.openai.com/api/docs/actions/introduction.md) |
| 45 | **Platform DOM** (keys, billing, limits) | DOM | Mint/restrict keys, add prepaid credits (min $5), auto-recharge, hard spend cap, rate-limit dashboard, Playground. | Keith's OpenAI login | console **free**; credits bill | **high as fallback** | `cosmos_browser` when AUTH_REQUIRED / `credit_balance_exhausted` / key create (Admin API cannot mint inference keys the way Keith clicks). Canon: DOM first when quota/billing can run out. | [billing](https://platform.openai.com/settings/organization/billing) · [keys](https://platform.openai.com/api-keys) |
| 46 | **Assistants API** (`/v1/assistants`, threads, runs) | REST (**deprecated**) | Persistent assistants + threads + runs + `code_interpreter` / `file_search` / functions. Header `OpenAI-Beta: assistants=v2`. | API key | tokens + tool SKUs | **do not use** | **Shuts down 2026-08-26** (tomorrow relative to this scout). Map: Assistants→Prompts (also being deprecated), Threads→Conversations, Runs→Responses. New COSMOS work: Responses only. | [migration](https://developers.openai.com/api/docs/assistants/migration.md) · [platform twin](https://platform.openai.com/docs/assistants/migration) · [deprecations](https://developers.openai.com/api/docs/deprecations.md) |
| 47 | **Fine-tuning** (`/v1/fine_tuning/jobs`) | REST (**winding down**) | SFT / DPO / RFT / vision FT. **Closed to new orgs since 2026-05-07.** Existing customers: last new jobs **2027-01-06**. Inference until base-model sunset. | API key | training $ + higher inference | **do not start** | Do not open a COSMOS fine-tune. If a legacy `ft-` model exists, run it until its base dies (many `ft-` snapshots shut 2026-10-23). | [SFT](https://developers.openai.com/api/docs/guides/supervised-fine-tuning.md) · [deprecations § FT](https://developers.openai.com/api/docs/deprecations.md) |
| 48 | **Completions API** (`/v1/completions`) | REST (legacy) | Old prompt-completion. Still in Batch's endpoint list. | API key | metered | **do not use** | Chat Completions replaced it; Responses replaced *that* for new work. | [completions](https://developers.openai.com/api/docs/guides/completions.md) |
| 49 | **Evals platform / Agent Builder / reusable prompts** | dashboard (**deprecated**) | Evals read-only 2026-10-31, gone 2026-11-30. Agent Builder gone 2026-11-30 (migrate to Agents SDK). `v1/prompts` gone 2026-11-30. | API / dashboard | n/a | **do not build on** | Promptfoo / COSMOS collector instead of OpenAI Evals. | [deprecations](https://developers.openai.com/api/docs/deprecations.md) |
| 50 | **Sora / Videos API** | REST (**deprecated**) | `sora-2` / `sora-2-pro`. Batch supported. | API key | $0.10–$0.70 / s | **do not build on** | **Shutdown 2026-09-24.** | [video](https://developers.openai.com/api/docs/guides/video-generation.md) |

---

## Assistants API — deprecation path (clock)

Official: [Assistants migration](https://developers.openai.com/api/docs/assistants/migration.md) · [Deprecations](https://developers.openai.com/api/docs/deprecations.md) · platform twin [platform.openai.com/docs/assistants/migration](https://platform.openai.com/docs/assistants/migration).

| When | What |
|------|------|
| 2025-03 | Responses API launched; Assistants sunset announced for 2026. |
| **2025-08-26** | Assistants API **deprecated**. |
| **2026-08-26** | Assistants API **shuts down.** This scout date is **2026-08-25 — one day left.** |
| 2026-11-30 | Reusable **prompt objects** (`v1/prompts`) also shut down — do not migrate Assistants *into* dashboard prompts as a long-lived home. Put instructions in application code. |

| Assistants object | Responses replacement | Why |
|-------------------|----------------------|-----|
| Assistant | Instructions + tools in **code** (not dashboard prompts) | Versioned in git |
| Thread | **Conversation** (items, not just messages) | Tool calls live in the stream |
| Run | **Response** | Input items → output items; COSMOS owns the tool loop |
| Run step | **Item** | message / function_call / function_call_output / reasoning |

**COSMOS rule:** do not add an Assistants client. If anything on the mesh still holds `asst_` / `thread_` IDs, backfill threads → conversations (recipe in the migration guide) **today**, then cut over to `POST /v1/responses`.

---

## Codex CLI flags COSMOS actually scripts

Official: [CLI reference](https://learn.chatgpt.com/docs/developer-commands.md?surface=cli), [non-interactive](https://learn.chatgpt.com/docs/non-interactive-mode.md).

| flag / command | COSMOS use |
|----------------|------------|
| `codex exec "…"` / `codex e` | The hand. Non-interactive. |
| `--json` | JSONL events for the ledger / collector. |
| `--output-schema FILE` | Structured JSON COSMOS can parse without regex. |
| `-o` / `--output-last-message` | Final natural-language summary file. |
| `--sandbox workspace-write` | Allow edits inside the attempt workspace. Default exec = **read-only**. |
| `--ephemeral` | Do not persist session files. |
| `--ignore-user-config` | CI: do not inherit Keith's `~/.codex/config.toml`. |
| `codex exec resume --last` | Multi-step jobs (review → fix). |
| `CODEX_API_KEY=…` **inline** | Metered fallback; never a job-level env next to untrusted checkout. |
| `codex login status` | Probe: exit 0 iff creds present. |
| `codex mcp add` / `list` | Register MCP servers for the worker. |
| `codex review --uncommitted` | Pre-commit review, no writes. |
| `/status` `/usage` | Human/Keith; remaining ChatGPT window. |

Windows install (Keith runs once, not a COSMOS bat):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

---

## Responses vs Chat Completions (one-page)

Official comparison: [Migrate to Responses](https://developers.openai.com/api/docs/guides/migrate-to-responses.md).

| Capability | Chat Completions | Responses |
|------------|------------------|-----------|
| Text / vision / structured / function calling | yes | yes |
| Web search, file search, computer use, code interpreter, MCP, image gen tool | no (you wrap it) | **yes, hosted** |
| Agentic loop in one request | no | **yes** |
| State | you send `messages[]` | `previous_response_id` / Conversations |
| Schema field | `response_format` | `text.format` |
| Function shape | `{type:function, function:{name,…}}` | `{type:function, name,…}` (internally tagged) |
| New work | supported | **recommended** |

COSMOS `oa-api` should speak **Responses**. Keep Completions only as a compatibility adapter.

---

## Free vs paid — what "free" actually is (2026-08-25)

| Claim | Official fact |
|-------|----------------|
| "OpenAI API free tier" | **No standing trial credit** for new Platform orgs. Prepaid min **$5**. Quickstart's "free test request" is a first-call courtesy, not a budget. |
| "Codex is free" | The **CLI is free** (Apache-2.0). ChatGPT **Free includes a small Codex allowance** (try, not work). Real work = Plus/Pro seat **or** API key. |
| "Moderation is free" | **Yes** — `omni-moderation-latest`. |
| "File search is free" | **1 GB storage** free; retrieval calls are **$2.50 / 1k**. |
| "Batch is free" | **No** — 50% off list. |
| "Assistants is included" | Irrelevant: **dead 2026-08-26**. |

---

## Source URLs (official, fetched 2026-08-25)

**Platform / API** (live host `developers.openai.com`; `platform.openai.com/docs/…` still advertised and redirects):

- Docs index — https://developers.openai.com/api/docs/llms.txt
- Full dump — https://developers.openai.com/api/docs/llms-full.txt
- Quickstart — https://developers.openai.com/api/docs/quickstart.md · https://platform.openai.com/docs
- Pricing — https://developers.openai.com/api/docs/pricing.md · https://platform.openai.com/docs/pricing
- Responses / migrate — https://developers.openai.com/api/docs/guides/migrate-to-responses.md
- Assistants migration — https://developers.openai.com/api/docs/assistants/migration.md · https://platform.openai.com/docs/assistants/migration
- Function calling — https://developers.openai.com/api/docs/guides/function-calling.md
- Structured outputs — https://developers.openai.com/api/docs/guides/structured-outputs.md
- Tools overview — https://developers.openai.com/api/docs/guides/tools.md
- File search — https://developers.openai.com/api/docs/guides/tools-file-search.md
- Batch — https://developers.openai.com/api/docs/guides/batch.md
- Realtime — https://developers.openai.com/api/docs/guides/realtime.md
- Token counting — https://developers.openai.com/api/docs/guides/token-counting.md
- Moderation — https://developers.openai.com/api/docs/guides/moderation.md
- Spend limits — https://developers.openai.com/api/docs/guides/spend-limits.md
- Deprecations — https://developers.openai.com/api/docs/deprecations.md
- Auth / overview — https://developers.openai.com/api/reference/overview.md
- Libraries — https://developers.openai.com/api/docs/libraries.md
- Agents SDK — https://developers.openai.com/api/docs/guides/agents.md
- Prepaid billing (Help) — https://help.openai.com/en/articles/8264778-what-is-prepaid-billing

**Codex CLI / ChatGPT plan:**

- CLI — https://learn.chatgpt.com/docs/codex/cli.md
- Non-interactive `codex exec` — https://learn.chatgpt.com/docs/non-interactive-mode.md
- Flag reference — https://learn.chatgpt.com/docs/developer-commands.md?surface=cli
- Codex pricing (ChatGPT plans) — https://learn.chatgpt.com/docs/pricing.md · https://developers.openai.com/codex/pricing
- Using Codex with ChatGPT plan — https://help.openai.com/articles/11369540
- GitHub — https://github.com/openai/codex (Apache-2.0)
- GitHub Action — https://github.com/openai/codex-action
- Docs MCP — https://developers.openai.com/mcp

---

## COSMOS takeaway (one paragraph)

Two OpenAI hands matter tomorrow morning: **(1) Codex CLI `codex exec`** as a fifth coding-agent lane that can ride a ChatGPT seat (free/Plus) *or* the existing `oa-api` key — probe which wallet Keith actually has before pouring work; **(2) Responses API** as what `oa-api` should speak, with function calling + structured outputs + Batch 50% as the metered cluster. **Assistants API dies 2026-08-26.** Fine-tuning is closed to new orgs. There is **no** standing Platform free credit — $5 prepaid is the floor. Moderation is the one genuinely free API. Do not double-dispatch Codex cloud and Cursor Cloud Agents onto the same issue without a lease.
