# GROQ HANDS — G46 scout return (GroqCloud / Groq LPU, **not** xAI Grok)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25 (docs fetched live).
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim except where a COSMOS artifact is named.
**No COSMOS core code was edited.** Maker-docs sweep (DHx assignment log): each maker's hands → `docs/research/<MAKER>_HANDS.md`.

**Name collision (do not mix wallets or APIs):** this file is **Groq** the inference-chip company (GroqCloud, LPUs, `api.groq.com`, keys `gsk_…`). It is **not** xAI **Grok**. COSMOS already has Grok on `sgh-api` / `gw-api`. A Groq rail is a *different* vendor, different silicon, different open-weight models, different key.

**Already on the mesh (do not re-add as "new"):** MESH_ADDITIONS row 2 named **Groq API** as an UNVERIFIED candidate (`link_id="groq-api"`, budget $0 free-tier, spend-gate ceiling once paid). It is **not** a live `ApiRail` in `cosmos_node_rails.py`. This file inventories every Groq **hand** COSMOS could fire, including the ones MESH already named.

**Filter:** a surface with no hands is rejected. Every row is an **action** COSMOS could fire: REST endpoint, SDK call, CLI (none official — Groq has SDKs, not a coding CLI), MCP tool Groq hosts, or DOM fallback. Chat-only playground chrome is out except as the DOM fallback.

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks. Equal power, cheaper wins. Metered Developer-tier Batch / Flex / TTS sit **below** free-tier chat + Whisper even when the model is the same family.

**What Groq is (one sentence):** OpenAI-compatible HTTP inference on custom **LPU** silicon — Llama / GPT-OSS / Qwen / Whisper / Orpheus at hundreds of tokens per second — plus server-side tools (Compound, browser search, code execution), remote MCP, a 50%-off Batch API (paid), and Flex 10× rate limits (paid). Official docs home: [console.groq.com/docs/overview](https://console.groq.com/docs/overview). Machine dump: [console.groq.com/llms-full.txt](https://console.groq.com/llms-full.txt).

---

## Official documentation URLs (fetched 2026-08-25)

These are the real vendor pages this scout used. Prefer these over blog roundups. There is **no** official Groq PDF spec; the live HTML + `llms-full.txt` + OpenAPI-shaped API reference **are** the docs.

| what | URL |
|------|-----|
| **Docs home / overview** | https://console.groq.com/docs/overview |
| **Docs machine dump** | https://console.groq.com/llms-full.txt |
| Quickstart | https://console.groq.com/docs/quickstart |
| **Supported models + list prices** | https://console.groq.com/docs/models · https://console.groq.com/docs/models.md |
| **OpenAI compatibility** | https://console.groq.com/docs/openai |
| **API reference** | https://console.groq.com/docs/api-reference |
| **Rate limits** | https://console.groq.com/docs/rate-limits |
| **Billing FAQs** (Free vs Developer) | https://console.groq.com/docs/billing-faqs |
| List-price marketing page (sparse HTML; use models.md) | https://groq.com/pricing |
| Chat / text generation | https://console.groq.com/docs/text-chat |
| **Speech-to-text (Whisper)** | https://console.groq.com/docs/speech-to-text |
| **Text-to-speech (Orpheus)** | https://console.groq.com/docs/text-to-speech · https://console.groq.com/docs/text-to-speech/orpheus |
| Vision / OCR | https://console.groq.com/docs/vision |
| Reasoning | https://console.groq.com/docs/reasoning |
| Content moderation | https://console.groq.com/docs/content-moderation |
| Structured outputs | https://console.groq.com/docs/structured-outputs |
| Prompt caching | https://console.groq.com/docs/prompt-caching |
| **Tool use overview** | https://console.groq.com/docs/tool-use/overview |
| Built-in tools | https://console.groq.com/docs/tool-use/built-in-tools |
| Web search / visit / code / Wolfram / browser search | https://console.groq.com/docs/tool-use/built-in-tools/web-search · visit-website · code-execution · wolfram-alpha · browser-search |
| **Remote MCP** | https://console.groq.com/docs/tool-use/remote-mcp |
| **Google Workspace connectors** | https://console.groq.com/docs/tool-use/remote-mcp/connectors |
| Local / function calling | https://console.groq.com/docs/tool-use/local-tool-calling |
| **Responses API (beta)** | https://console.groq.com/docs/responses-api |
| **Compound** | https://console.groq.com/docs/compound · systems · built-in-tools |
| Service tiers | https://console.groq.com/docs/service-tiers |
| Performance tier (enterprise) | https://console.groq.com/docs/performance-tier |
| **Flex processing** | https://console.groq.com/docs/flex-processing |
| **Batch API** | https://console.groq.com/docs/batch |
| LoRA inference (enterprise) | https://console.groq.com/docs/lora |
| Spend limits | https://console.groq.com/docs/spend-limits |
| Projects | https://console.groq.com/docs/projects |
| Your data / ZDR | https://console.groq.com/docs/your-data |
| Deprecations (Mixtral, Llama 4, Gemma, …) | https://console.groq.com/docs/deprecations |
| SDKs | https://console.groq.com/docs/libraries |
| Cookbook | https://github.com/groq/groq-api-cookbook |
| Keys (DOM) | https://console.groq.com/keys |
| Org limits (ground truth) | https://console.groq.com/settings/limits |
| Plans / billing | https://console.groq.com/settings/billing/plans |
| Playground | https://console.groq.com/playground |
| Python SDK | https://pypi.org/project/groq |
| JS SDK | https://www.npmjs.com/package/groq-sdk |

---

## Cookbook as COSMOS research pointer (Keith 2026-09-04)

Vendor repo [github.com/groq/groq-api-cookbook](https://github.com/groq/groq-api-cookbook)
fetched 2026-09-04 (README + tutorials 01–10). **Pointer, not a rewrite.**
COSMOS already has chat-create + Kernel `compose_rails` `groq-api`. CCr still
writes COSMOS. Do not import cookbook frameworks as Core.

| tutorial | what the vendor shows | COSMOS bind |
|----------|----------------------|-------------|
| 01 Quickstart / batch | Chatbot, chat history, **Batch APIs** | Chat-create is the rail. **Batch stays dark.** |
| 02 Tool use | Function calling, SQL, stock, parallel tools | Compound / tools are not the cheap-reasoning default. |
| 03 MCP | Box, Browser Use, BrowserBase, **Firecrawl**, Exa, E2B, Tavily, HF, Parallel | Firecrawl MCP is a **recipe**. COSMOS already has composed `firecrawl-web`. Do not dual-wire. |
| 04 RAG | LangChain / Pinecone / Whisper-podcast | Overflow research. Not a Core RAG rewrite. |
| 05 JSON mode | Structured outputs / Instructor | Vendor recipe. Rail is still chat-create. |
| 06 Multimodal | Vision + Whisper + Batch image | Whisper is STT (rail refuses on chat-create). Batch dark. |
| 07 Agents | Mixture-of-agents, CrewAI, Langroid, Minions | Do **not** vendor-lock COSMOS into CrewAI. MOTIF is dual-lane CCr + Cursor. |
| 08 Integrations | Gradio, Streamlit, LangChain, LlamaIndex, Portkey, **LiteLLM** | ARCH already parks LiteLLM proxy (second spend surface). |
| 09 Observability | OpenTelemetry, Arize Phoenix | Optional later. Not a Core rewrite. |
| 10 Guardrails | Llama Guard, image moderation | Llama still **Bedrock-later**. Rail refuses Llama 3.x Free/Dev IDs. Catalog Llama 3.1/3.3 is Enterprise ContactSales. |

Llama-3 stock tutorials in this repo are **stale** vs the 2026-09-04 catalog.
Cookbook Batch / Flex examples do **not** lift `service_tier=flex`.

---

## How COSMOS reaches Groq (reach column, one pattern)

Core stays sole ledger writer. Groq is reached as:

| Lane | Mechanism | When |
|------|-----------|------|
| **A. HTTP OpenAI-compat** | `POST https://api.groq.com/openai/v1/chat/completions` (also `/responses`, `/audio/*`, `/batches`, `/files`, `/models`). Header `Authorization: Bearer $GROQ_API_KEY`. Drop-in: `openai.OpenAI(base_url="https://api.groq.com/openai/v1", api_key=…)`. | Default. Matches existing `ApiRail` shape (`oa-api`). **This is the Groq hand.** |
| **B. Official SDKs** | `pip install groq` → `from groq import Groq`. `npm i groq-sdk`. Same REST under the hood. | Python worker (COSMOS default). Prefer this over hand-rolled curl when tool-call loops / files / batches are involved. |
| **C. Compound / built-in tools** | Same chat endpoint, `model="groq/compound"` or `openai/gpt-oss-120b` + `tools=[{type:"browser_search"}]`. Groq runs the agent loop **server-side**. | When COSMOS wants web/code without hosting the loop. Not HIPAA. |
| **D. Remote MCP + connectors** | Responses API `tools: [{type:"mcp", server_url, headers}]` or `connector_id: connector_gmail\|googlecalendar\|googledrive`. Groq is the MCP **client**. | Firecrawl / GitHub / Hugging Face / Gmail without COSMOS hosting an MCP client. |
| **E. DOM** | [console.groq.com](https://console.groq.com) — sign-up, key mint, limits, billing, playground, data-controls / ZDR. | Fallback only. Canon: DOM first when the API depends on something that can run out (free RPD, card, org block). |

Keith owns credentials. Store under `live/config/` (git-ignored). Never hard-code. Never print a key in full (`gsk_…last4`). Fenced commit still gates any tree write. There is **no official Groq CLI** and **no bats**.

---

## Auth primer (all API rows inherit this unless overridden)

Base: `https://api.groq.com/openai/v1`. OpenAI-compat drop-in. Keys minted at [console.groq.com/keys](https://console.groq.com/keys); prefix **`gsk_`**. Shown **once**.

| method | credential | header / env | COSMOS use |
|--------|------------|--------------|------------|
| **API key (Free or Developer)** | `gsk_…` | `Authorization: Bearer` · env `GROQ_API_KEY` | Every Groq hand. Project-scoped once Projects are used. Org-level rate limits — **all keys share one budget**. |
| **Project key** | same shape, bound to a Console project | same | Isolate `groq-api` logs / batch jobs from experiments. Project limits can only go **down** from org ceiling. |
| **Google OAuth (connectors)** | Google access token (`ya29.…`) in the MCP tool's `authorization` field | Groq forwards to Google | Gmail / Calendar / Drive connectors. Keith does consent. Read-only scopes. Tokens ~1 h. |
| **MCP server headers** | per-server token in `tools[].headers` | Groq redacts from logs; HTTPS required | Firecrawl, Stripe, Parallel, Hugging Face, GitHub. Only trusted servers — they see the prompt. |

TLS 1.2+. Never embed `gsk_` in frontend / KDash. Route through Core. Rotate on suspicion; revoke in Console.

---

## Cost floor (two wallets — do not conflate)

Mixing "the console shows a dollar figure" with "we were billed" is how a Free-tier scout report lies. Official: **Free = no payment method, no charge, 429 when over**. Developer = card on file, pay-as-you-go at list, billed in arrears (progressive $1 / $10 / $100 / $500 / $1,000 then monthly; India: $1 / $10 then every $100). No charge under **$0.50**.

| Wallet | What official docs say | COSMOS note |
|--------|------------------------|-------------|
| **Free tier** | Sign up, no card. Rate-limited (org-wide RPM/RPD/TPM/TPD/ASH). Console Usage may show **what the same traffic would have cost on Developer** — that is **not a bill**. Over = HTTP **429**. Community staff (2025-07, still the documented behavior): "as long as you're on Free you don't owe us a thing." | Highest-ranked Groq inference. MESH proposed `budget $0`. Probe live numbers at [settings/limits](https://console.groq.com/settings/limits) — **do not treat this file's table as the org's live cap**. |
| **Developer (paid)** | Card / US bank / SEPA. No immediate charge on upgrade. Unlocks: **higher rate limits, Batch, Flex, Spend Limits, chat support**. Downgrade anytime (final invoice first). | Spend-gate as `groq-api` sibling once a card exists. Keith does money. |
| **Enterprise / committed spend** | Contact sales. Llama 3.1/3.3 and MiniMax M2.7 list as **Enterprise · Contact Sales**. LoRA, Performance tier, dedicated instances. Free/Developer deprecations **do not apply** to committed-spend contracts. | Out of scope until Keith signs. |
| **Batch API** | **50% off** vs sync list. Separate rate limits (does not burn sync TPM). 24h–7d window. Files ≤50k lines / 200 MB. Results 30 days. **Developer+.** Cache discount **does not stack** (batch tokens all at 50%). | Overnight eval. Paid. |
| **Flex** | Same **on-demand prices**, **10×** rate limits, fail-fast **498 `capacity_exceeded`**. **Paid only.** | Burst overflow, not a realtime SLA. |
| **Prompt cache** | Automatic on GPT-OSS family. **50% off cached input**. 2 h volatile TTL. Exact prefix match. Cached tokens **do not count toward rate limits** (subtracted after). No extra fee. Does **not** stack with Batch 50%. | Put COSMOS system prompt + tool schemas first. |
| **Compound tools (list, Developer)** | Tokens of underlying models **plus** tool fees: Basic web search **$5 / 1,000**, Advanced **$8 / 1,000**, Visit website **$1 / 1,000**, Code execution **$0.18 / hour**, Wolfram = Wolfram's key (not Groq). Compound model ID itself has no list price (`-` on models page). | Cap Compound on a loop. Prefer `gpt-oss-20b` + local tools when the URL is known. **Not HIPAA.** |
| **Function calling / JSON / structured outputs / Models API / Files ops** | **$0 extra** — tokens (or free for list/retrieve). | |
| **Whisper** | Turbo **$0.04 / audio-hour**, Large v3 **$0.111 / hour**. Min billed length **10 s**. | Free-tier still rate-limited in ASH/ASD. |
| **Orpheus TTS** | English **$22 / 1M characters**, Arabic **$40 / 1M**. | Expensive. Last resort vs local / prepaid TTS. |
| **Spend Limits** | Org-wide monthly USD cap. **Paid only**, owner role. 10–15 min tracking lag. Hit → 400 `blocked_api_access`. | Required the day a card is on file. |
| **Failed 429/5xx** | Not billed as successful tokens. | Retry with `retry-after`. |

**List rates fetched 2026-08-25** from [Supported Models](https://console.groq.com/docs/models) (USD). Llama 3.x no longer publish a public $/M on Free/Developer.

| Model ID | Free-tier usable? | Speed | Input / 1M | Output / 1M | Ctx / max out | Notes |
|----------|-------------------|-------|------------|-------------|---------------|-------|
| `openai/gpt-oss-20b` | **yes** (rate-limited) | ~1000 t/s | $0.075 | $0.30 | 131,072 / 65,536 | **Default COSMOS Groq brain.** Tools, built-in browser+code, reasoning, strict JSON, prompt cache. |
| `openai/gpt-oss-120b` | **yes** | ~500 t/s | $0.15 | $0.60 | 131,072 / 65,536 | Higher quality same family. |
| `openai/gpt-oss-safeguard-20b` | **yes** | ~1000 t/s | $0.075 | $0.30 | 131,072 / 65,536 | BYO-policy moderator. Preview. |
| `qwen/qwen3.6-27b` | **yes** | ~500 t/s | $0.60 | $3.00 | 131,072 / 16,384 | **Vision** (5 images, 20 MB). Preview. |
| `groq/compound` | **yes** | ~450 t/s | underlying models + tools | — | 131,072 / 8,192 | Up to **10** server tool calls. |
| `groq/compound-mini` | **yes** | ~450 t/s | same | — | 131,072 / 8,192 | **1** tool call, ~3× lower latency. |
| `whisper-large-v3-turbo` | **yes** | 216× RT | $0.04 / hour | — | — | STT only (no translation). |
| `whisper-large-v3` | **yes** | 189× RT | $0.111 / hour | — | 100 MB (dev) | STT + **translation to EN**. |
| `meta-llama/llama-prompt-guard-2-22m` | **yes** | — | $0.03 | $0.03 | 512 | Prompt-injection classifier. |
| `meta-llama/llama-prompt-guard-2-86m` | **yes** | — | $0.04 | $0.04 | 512 | Same, slightly heavier. |
| `canopylabs/orpheus-v1-english` | rate-limited | — | $22 / 1M chars | — | 4k in / 50k out | TTS. Preview. |
| `llama-3.1-8b-instant` | **Enterprise only** after 2026-08-16 | 560 t/s | Contact Sales | — | 131,072 | Free/Dev **shutdown 2026-08-16**. Replacement: `openai/gpt-oss-20b`. |
| `llama-3.3-70b-versatile` | **Enterprise only** after 2026-08-16 | 280 t/s | Contact Sales | — | 131,072 / 32,768 | Free/Dev **shutdown 2026-08-16**. Replacement: `openai/gpt-oss-120b` or `qwen/qwen3.6-27b`. |
| `minimaxai/minimax-m2.7` | Enterprise | 260 t/s | Contact Sales | — | 196,608 | Preview. |
| **`mixtral-8x7b-32768`** | **DEAD** | — | — | — | — | **Shutdown 2026-03-20.** Do not dispatch. |

Batch = **50%** of the sync column. Cache hits on GPT-OSS = **50%** of input.

---

## Free-tier vs Developer rate limits (probe live)

Limits are **organization-wide**, not per-key. First of RPM / RPD / TPM / TPD / ASH / ASD wins. Some orgs also have **ITPM / OTPM** (hover the TPM cell on the Console limits page for an "X in / Y out" split; no hover = combined TPM only). Cached tokens do not count toward limits. Ground truth: [console.groq.com/settings/limits](https://console.groq.com/settings/limits) and response headers. Docs page: [console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits).

**COSMOS bind (Keith 2026-09-04):** `cosmos_groq_rail.py` pins `vendor_limits` to that docs URL. Persist `x-ratelimit-*` + `retry-after`. 429 is **BROKE** (do not hammer). Do **not** treat the public table as the live org cap. Do **not** lift Batch/Flex for 10×. Keith does money; budget $0 Free.

**Docs conflict to flag, not paper over:** [Rate Limits](https://console.groq.com/docs/rate-limits) says both "upgrade to Developer for higher limits" **and** "the limits shown below are the base limits for the Developer plan." The **table on that page** (re-fetched **2026-09-04**, same numbers as 2026-08-25 for gpt-oss) matches historical **Free** numbers. The **models page** labels a **much higher** column "RATE LIMITS (DEVELOPER PLAN)". Treat the two tables as Free-shaped vs Developer-shaped until the org page is probed.

### Public table on `/docs/rate-limits` (fetched 2026-09-04; likely Free / current public default)

| MODEL ID | RPM | RPD | TPM | TPD | ASH | ASD |
|----------|-----|-----|-----|-----|-----|-----|
| `openai/gpt-oss-20b` / `120b` / `safeguard-20b` | 30 | 1K | 8K | 200K | — | — |
| `qwen/qwen3.6-27b` / `qwen/qwen3.8-27b` | 30 | 1K | 8K | 200K | — | — |
| `groq/compound` / `compound-mini` | 30 | 250 | 70K | — | — | — |
| `whisper-large-v3` / `-turbo` | 20 | 2K | — | — | 7.2K | 28.8K |
| `meta-llama/llama-prompt-guard-2-*` | 30 | 14.4K | 15K | 500K | — | — |
| `canopylabs/orpheus-*` | 10 | 100 | 1.2K | 3.6K | — | — |

Whisper **file size:** Free **25 MB**, Developer **100 MB**. Attachment cap 25 MB either way — larger audio via `url`.

### Developer (models page, 2026-08-25)

| MODEL ID | Developer RPM | Developer TPM (or ASH) |
|----------|---------------|------------------------|
| `openai/gpt-oss-20b` / `120b` | 1K | 250K TPM |
| `groq/compound` / `mini` | 200 | 200K TPM |
| `whisper-large-v3` | 300 | 200K ASH |
| `whisper-large-v3-turbo` | 400 | 400K ASH |
| Orpheus | 250 | 50K TPM |
| Prompt Guard | 100 | 30K TPM |

**Flex (paid):** 10× those on-demand limits; 498 when no capacity. **Batch (paid):** separate pool.

**Headers (always present except `retry-after` only on 429):**

| Header | Means |
|--------|--------|
| `x-ratelimit-limit-requests` / `remaining-requests` / `reset-requests` | **RPD** |
| `x-ratelimit-limit-tokens` / `remaining-tokens` / `reset-tokens` | **TPM** |
| `retry-after` | seconds (429 only) |

Bind every Groq 429 to those headers, not to this markdown.

---

## Ranking table

| # | name | kind | HANDS (what it DOES) | auth | cost | power | how COSMOS reaches it |
|---|------|------|----------------------|------|------|-------|------------------------|
| 1 | **Chat Completions — `openai/gpt-oss-20b`** | REST + SDK | OpenAI-compatible `POST /openai/v1/chat/completions`. ~**1000 tok/s** LPU. 131k context. Streaming SSE. Tools, JSON mode, reasoning (`reasoning_effort` low/medium/high, `include_reasoning`). Built-in `browser_search` + `code_interpreter` optional. **This is the Groq coding/bulk-reasoning hand.** `n` must be 1. `temperature` 0 → `1e-8`. | `GROQ_API_KEY` Bearer | **free** on Free tier (30 RPM / 8K TPM / 200K TPD public table); Developer list $0.075 / $0.30 per 1M | **highest** | New `ApiRail` `link_id="groq-api"`. `from groq import Groq` **or** existing OpenAI client with `base_url=https://api.groq.com/openai/v1`. Default model for Groq jobs. Bind DONE to `choices[0].message` + `usage` + `x-groq` request id. Never a `.bat`. |
| 2 | **Chat Completions — `openai/gpt-oss-120b`** | REST + SDK | Same endpoint, bigger open-weight (~500 t/s). Same tool / MCP / structured-output / cache surface. Prefer when 20B quality is not enough. | same | **free**-tier eligible; list $0.15 / $0.60 | **highest** | Same rail, `model="openai/gpt-oss-120b"`. Overflow from 20B, not a second wallet. |
| 3 | **Local tool / function calling** | API feature | COSMOS declares JSON-schema functions; model returns `tool_calls`; COSMOS executes **in the attempt workspace** and sends `role: tool`. `tool_choice` auto/required/none/named. Parallel tools on Llama 3.x / Qwen / MiniMax (**not** on GPT-OSS). GPT-OSS **can** mix local tools with built-in + remote MCP in one request. Compound **cannot**. | API key | **tokens only** | **highest** | Wrap `cosmos_status` / queue / ledger **read-only** first. Speed is the point: multi-hop tool loops that are painful at 30 t/s are instant at 300–1000 t/s. Fail-closed: never let the model write the live tree. |
| 4 | **`groq/compound-mini`** | REST system | Server-side agent, **one** tool call, ~3× lower latency than Compound. Tools: `web_search`, `code_interpreter`, `visit_website`, `wolfram_alpha`. Single chat call returns the final answer + `executed_tools` + `usage_breakdown`. | API key | **free**-tier eligible; Developer = underlying tokens + tool list fees | **highest** (grounded, one hop) | `model="groq/compound-mini"`. Fast "what's the weather / fetch this URL / run this Python" without COSMOS hosting tools. **Not HIPAA. Not on sovereign endpoints.** Restrict with `compound_custom.tools.enabled_tools`. |
| 5 | **`groq/compound`** | REST system | Same tools, up to **10** server-side calls per request. Version pin via `Groq-Model-Version: latest` (stable default `2025-08-16`). | API key | same as row 4 (more tool calls → more $) | **highest** (research) | Multi-step search+code. Cap it. Check `executed_tools` before claiming a source. Underlying models historically include `gpt-oss-120b` and Llama 3.3 — Llama 3.3 is Enterprise-only after 2026-08-16; probe `usage_breakdown`. |
| 6 | **Built-in `browser_search` + `code_interpreter` on GPT-OSS** | server tools | GPT-OSS runs Groq-hosted browser search and a code sandbox **in one call** (`tools: [{type:"browser_search"},{type:"code_interpreter"}]`). Also on Responses API. No Visit Website / Wolfram on this path (those are Compound). | API key | tokens; tool fees when billed | **highest** | Prefer this over Compound when COSMOS already wants GPT-OSS + optional local tools in the same request. |
| 7 | **Whisper Large V3 Turbo STT** | REST | `POST /openai/v1/audio/transcriptions`. `whisper-large-v3-turbo`. Multilingual transcribe, **no** translate. 216× realtime. Formats: flac/mp3/mp4/mpeg/mpga/m4a/ogg/wav/webm. `file` or `url`. `verbose_json` + word/segment timestamps. **Not** `vtt`/`srt`. | API key | **free**-tier ASH; list **$0.04/hour**; min bill 10 s | **highest** (voice) | Phone / meeting / dissertation-audio → text in the attempt workspace. Pre-downmix 16 kHz mono FLAC. Chunk >25 MB (free) / >100 MB (dev). |
| 8 | **Models API** | REST | `GET /openai/v1/models` list + `GET /openai/v1/models/{id}` retrieve. Live IDs, not this markdown. | API key | **free** | **highest** (infra) | Probe **before** dispatch so COSMOS never hard-codes a retired ID (`mixtral-8x7b-32768`, Llama 4 Scout, Llama 3.3 on Free). Cache the JSON; refresh on 400 unknown model. |
| 9 | **Streaming** | API feature | `stream: true` SSE token deltas. Required for KDash-live / perceived latency. | API key | **included** | **high** | Default on interactive Groq jobs. Capture `usage` on the last chunk. |
| 10 | **Structured outputs / JSON mode** | API feature | `response_format.json_schema` with `strict: true` (constrained decoding, GPT-OSS only) or `strict: false`. Broader JSON object mode. **No streaming + no tool use** while structured-outputs is on. | API key | **tokens only** | **high** | Collector / critique envelopes. Strict mode for production parsers. Retry + lower temperature on 400 schema mismatch (`strict: false`). |
| 11 | **Prompt caching (GPT-OSS)** | API feature | Automatic prefix cache, 50% input discount, 2 h TTL, exact match, min length 128–1024 tok. `usage.prompt_tokens_details.cached_tokens`. | API key | **included**; 50% on hits | **high** (cost) | Static COSMOS canon + tool schemas **first**, user text last. Check `cached_tokens` in the ledger. |
| 12 | **Reasoning controls** | API feature | GPT-OSS: `reasoning_effort` low/medium/high, `include_reasoning` true/false (no `reasoning_format`). Qwen: `reasoning_format` parsed/raw/hidden; `reasoning_effort` none/default. Tokens billed as output. | API key | output tokens | **high** | `include_reasoning: false` / `hidden` for workers that don't surface CoT (faster TTFT, same thinking). `high` only on hard review. |
| 13 | **Responses API (beta)** | REST | `POST /openai/v1/responses`. OpenAI Responses-shaped. Text+image in, text out. Built-in tools, MCP, structured outputs, reasoning. **Not stateful** on Groq (`previous_response_id` unsupported — COSMOS must thread `output` itself). Also missing: `store`, `truncation`, reusable `prompt`. Header `Groq-Beta: inference-metrics` adds `metadata.{prompt,completion,queue,total}_time`. | API key | **tokens** (same models) | **high** | Prefer for MCP / connector workflows. Chat Completions remains the workhorse. |
| 14 | **Remote MCP (Groq as host)** | API beta | Groq discovers `tools/list`, runs `tools/call` server-side, loops until a final message. `type: "mcp"` + `server_url` + headers. Also Chat Completions. Approval flow `require_approval: never\|always`. Multiple servers per request. 424 `external_connector_error` on bad MCP auth. | API key + MCP bearer | tokens; MCP vendor may bill | **high** | Point Groq at Firecrawl / Hugging Face / GitHub MCP **without** COSMOS running an MCP client. Only trusted HTTPS servers (they see context). |
| 15 | **Whisper Large V3 (accuracy + translation)** | REST | `POST /audio/transcriptions` **and** `/audio/translations` (to English only). Better WER (10.3% vs turbo 12%). | API key | **$0.111/hour** | **high** | Use when turbo error-rate is too high or the job is "translate this audio to EN". |
| 16 | **Vision — `qwen/qwen3.6-27b`** | REST | Image URL or base64 in chat (or Responses `input_image`). Max 5 images, 20 MB/request. Tool use + JSON mode with images. Preview — may vanish on short notice. | API key | $0.60 / $3.00 per 1M | **high** | KDash screenshots, exhibit plates, Lindau figures. Prefer Files/URL over re-sending base64. Llama 4 Scout **dead** (shutdown 2026-07-17) — Qwen is the live vision ID. |
| 17 | **Safety — Prompt Guard 2 (22M / 86M)** | REST | Tiny classifiers, 512-token window, ~$0.03–0.04 / 1M. High RPD (14.4K public table). | API key | **cheap** / free-tier | **high** (gate) | Pre-filter untrusted prompts before they hit gpt-oss. Fail-closed on `violation`. |
| 18 | **Safety — `openai/gpt-oss-safeguard-20b`** | REST | Policy-following moderator. Put the taxonomy in `system`; get JSON `{violation, category, rationale}`. | API key | same $ as gpt-oss-20b | **high** | BYO COSMOS policy (never-destroy-mesh, no-fabricated-compliance). Complements Guard 2. |
| 19 | **OpenAI-compat drop-in** | adapter | Any code already on `oa-api` can point at Groq by changing **base URL + key + model id**. Unsupported OpenAI fields 400: `logprobs`, `logit_bias`, `top_logprobs`, `messages[].name`, `n≠1`. | Groq key (not OpenAI) | **free** adapter | **high** | Do **not** invent a second spend ledger. Core spend-gate remains authority. LiteLLM `groq/<model>` is optional glue (AIDER_HANDS already notes it). |
| 20 | **Python SDK `groq` / JS `groq-sdk`** | SDK | Typed chat, audio, files, batches, async client. Reads `GROQ_API_KEY`. | API key | **free** libs; usage bills | **high** | `pip install groq` in the attempt venv. Community C#/PHP/Ruby/Dart = use-at-own-risk. |
| 21 | **Rate-limit headers + 429 handling** | HTTP | Every response carries remaining RPD/TPM. 429 + `retry-after`. | none extra | **included** | **high** (infra) | Return-watcher / collector: persist headers. Exponential backoff. Do not hammer. |
| 22 | **Files API** | REST | `POST /openai/v1/files` (`purpose=batch` or `fine_tuning`), list, retrieve, `GET /files/{id}/content`. JSONL ≤50k lines / 200 MB for batch. | API key | **ops free**; batch inference bills | **high** (bulk) | Upload overnight eval JSONL; never accept a user-supplied `file_id`. 30-day retention unless deleted. |
| 23 | **Google Workspace connectors** | MCP connector (beta) | Read-only **Gmail / Calendar / Drive** without standing up an MCP server. IDs: `connector_gmail`, `connector_googlecalendar`, `connector_googledrive`. OAuth token in `authorization`. | Groq key + Google OAuth | tokens; Google quota | **high** (if Keith consents) | Responses API. DOM: Google OAuth Playground for a test token; production = proper refresh. Keith does consent. |
| 24 | **JSON object mode / prefilling / stop** | API feature | `response_format: {type: json_object}`, assistant prefilling, `stop` sequences. Documented on text-chat / prefilling pages. | API key | tokens | **med-high** | Schema-lite structured jobs when `json_schema` is unavailable on a model. |
| 25 | **Service tier `auto` / `on_demand`** | API param | `service_tier`: `on_demand` (default), `auto` (best available), `flex` (paid), `performance` (enterprise). Batch **ignores** this param. | API key | **included** on Free (`on_demand`) | **med-high** | Leave default on Free. `auto` once Developer exists. |
| 26 | **Playground + Console DOM** | DOM | Try models, mint keys, read live limits, usage, logs, data-controls (ZDR), billing. | Google / email login | **free** UI | **med-high** (bootstrap) | Keith signs up, drops `gsk_` into `live/config/`. COSMOS does not scrape the playground. |
| 27 | **Projects** | Console + keys | Isolate API keys, logs, batch jobs, optional **lower** per-project RPM. Org ceiling still wins. | owner | **free** | **med** | `cosmos-live` vs `cosmos-dev` projects so experiment 429s don't starve a future production key. |
| 28 | **Data controls / ZDR** | Console | Default: inference **not** retained. Batch/fine-tune files retained up to 30 days / until delete. ZDR disables retention **and** those features. US GCP. | owner | **free** | **med** (hygiene) | Turn ZDR on if dissertation audio/text must not sit on Groq disk; then **no Batch**. |
| 29 | **Batch API** | REST (paid) | JSONL of `/v1/chat/completions` or `/v1/audio/transcriptions|translations`. 24h–7d window. 50% off. Separate limits. Status: validating → in_progress → completed / expired. Match results by `custom_id`. Audio in batch = **URL**, not upload. | API key, **Developer+** | **50% list**; **not** on Free | **high** (bulk, paid) | Unlock only after a card + Spend Limit. Overnight port-backlog / STT corpus. Split to ~1k-line files. |
| 30 | **Flex processing** | API param (paid) | `service_tier: "flex"`. 10× RPM/TPM, same $. Fail 498 `capacity_exceeded`. | Developer+ | **same $ as on-demand** | **med-high** (paid burst) | Queue jobs that can retry. Not for KDash-interactive. |
| 31 | **Spend Limits + alerts** | Console (paid) | Monthly USD cap, email at 50/75/90%. Org-wide. 10–15 min lag. | owner, paid | **free to set**; blocks at cap | **high** (hygiene, paid) | Mandatory the day Groq is no longer $0. |
| 32 | **Orpheus TTS** | REST | `POST /openai/v1/audio/speech`. English + Saudi Arabic. Vocal directions e.g. `[cheerful]`. `wav` default. | API key | **$22–40 / 1M chars** | **med** | Voice replies / accessibility. Expensive vs Whisper-in. Preview. |
| 33 | **Prometheus metrics** | REST | `https://api.groq.com/v1/metrics/prometheus` Bearer key. | API key | **free** to scrape | **med** | Optional KDash / collector scrape. Not a substitute for the ledger. |
| 34 | **LoRA inference** | REST (enterprise) | Upload PEFT adapter ZIP → `ft:` model id on `llama-3.1-8b-instant`. Groq does **not** train. Ranks 8/16/32/64. | enterprise | **contact sales** | **low** (until signed) | Ignore until Keith is enterprise. Llama 3.1 8B itself is already off Free/Dev. |
| 35 | **Performance tier** | API param (enterprise) | `service_tier: "performance"` — reserved low-latency. | enterprise | **contact sales** | **low** | Ignore. |
| 36 | **Mixtral 8x7B** | — | **Shutdown 2026-03-20.** Replacement was `mistral-saba-24b` (also later deprecated) or Llama 3.3. | — | **n/a** | **none** | **Not a hand.** Any leftover `mixtral-8x7b-32768` in Aider/LiteLLM recipes is stale. Use `openai/gpt-oss-20b`. |
| 37 | **Llama 4 Scout / Maverick, Gemma, PlayAI TTS, Distil-Whisper, Kimi K2, Llama Guard 4, …** | — | All **deprecated** on Free/Dev (see deprecations page). Scout 2026-07-17, Maverick 2026-03-09, Gemma2 2025-10-08, PlayAI TTS 2025-12-31, Llama Guard 4 2026-03-05. | — | **n/a** | **none** | Probe `/models`. Do not copy MESH_ADDITIONS' older "Llama/Qwen/GPT-OSS/Whisper" blurb as if Llama 4 were still public. |

---

## Mixtral, Llama, Whisper — what is actually live

User asked specifically. Official deprecation page + models page, 2026-08-25:

| Family | Status on Free / Developer (2026-08-25) | Live replacement |
|--------|------------------------------------------|------------------|
| **Mixtral** `mixtral-8x7b-32768` | **Dead** since 2026-03-20 | `openai/gpt-oss-20b` or `120b` |
| **Llama 3.1 8B Instant** | Free/Dev shutdown **2026-08-16**; still listed **Enterprise · Contact Sales** | `openai/gpt-oss-20b` |
| **Llama 3.3 70B Versatile** | same | `openai/gpt-oss-120b` or `qwen/qwen3.6-27b` |
| **Llama 4 Scout / Maverick** | Dead (2026-07-17 / 2026-03-09) | `qwen/qwen3.6-27b` (vision) or gpt-oss (text) |
| **Whisper Large v3 / Turbo** | **Live**, production | turbo for price/speed; v3 for accuracy + EN translation |
| **GPT-OSS 20B / 120B** | **Live**, production | — |
| **Qwen 3.6 27B** | **Live**, preview (vision) | — |

Do not advertise Mixtral as a COSMOS hand.

---

## COSMOS wiring sketch (not implemented this pass)

MESH already proposed it. This scout only names the contract:

1. Keith mints a key at [console.groq.com/keys](https://console.groq.com/keys) (Free, no card). Stores `live/config/groq_api_key.txt` (git-ignored).
2. New `ApiRail` `link_id="groq-api"`, budget **$0**, spend-gate refuses if a Developer invoice appears without a new budget.
3. Default model **`openai/gpt-oss-20b`**. Probe `GET /models` at process start; fail-closed on missing ID.
4. Persist `x-ratelimit-*` + `usage` (and `cached_tokens` / `executed_tools` when present) into the ledger. Runtime binding: the model string in the **response**, not the one in the prompt.
5. Batch / Flex / Spend Limits stay dark until a card exists.
6. Compound / MCP / Gmail connectors are **optional workers**, not Core.

---

## What this scout did **not** do

- Did not mint a Groq key or call `api.groq.com` (no COSMOS Groq credential in `live/config/` was used).
- Did not edit COSMOS core, rails, or KDash.
- Did not treat MESH_ADDITIONS row 2 as verified — this file **is** the vendor-doc verification that row asked for.
- `groq.com/pricing` HTML is a marketing shell; **models.md is the price table**.

---

## ARCH pick (additive, 2026-08-25) — M3 / C3

This file is **authority** over `docs/MESH_ADDITIONS.md` row 2 prose. Llama 4 / Mixtral are **dead** on Free/Dev. Default model **`openai/gpt-oss-20b`**. Live IDs: Whisper turbo/v3, `qwen/qwen3.6-27b` (vision). Do not copy MESH's older "Llama/Qwen/GPT-OSS/Whisper" blurb.

**WAVE C3 (ARCH):** designed-but-dark until Keith mints `gsk_` at console.groq.com/keys into `live/config/groq_api_key.txt` (git-ignored). Worker HTTP through spend-gate budget **$0**; persist `x-ratelimit-*`. Dispatcher `ApiRail` `groq-api` waits on Kernel attach (BACKLOG). `live/config/` this pass has **no** `groq_api_key`. Probe `GET /models` after the key exists. Live org limits: **UNKNOWN**. This is **not** a stage-6 pass.

---

## Host bind (additive, 2026-08-27 s6 re-probe) — M3 / C3

This process (no `gsk_` in `live/config/`):

`GET https://api.groq.com/openai/v1/models` → HTTP **401** body `{"error":{"message":"Invalid API Key","type":"invalid_request_error","code":"invalid_api_key"}}`

Endpoint is live. COSMOS has **no** Groq credential. Default model remains **`openai/gpt-oss-20b`**. WAVE C3 stays designed-but-dark.

---

## Sources (primary)

- https://console.groq.com/docs/overview
- https://console.groq.com/docs/models · https://console.groq.com/docs/models.md
- https://console.groq.com/docs/openai
- https://console.groq.com/docs/api-reference
- https://console.groq.com/docs/rate-limits
- https://console.groq.com/docs/billing-faqs
- https://console.groq.com/docs/batch
- https://console.groq.com/docs/flex-processing
- https://console.groq.com/docs/service-tiers
- https://console.groq.com/docs/tool-use/overview
- https://console.groq.com/docs/tool-use/built-in-tools
- https://console.groq.com/docs/tool-use/remote-mcp
- https://console.groq.com/docs/tool-use/remote-mcp/connectors
- https://console.groq.com/docs/tool-use/local-tool-calling
- https://console.groq.com/docs/compound
- https://console.groq.com/docs/speech-to-text
- https://console.groq.com/docs/text-to-speech
- https://console.groq.com/docs/vision
- https://console.groq.com/docs/reasoning
- https://console.groq.com/docs/structured-outputs
- https://console.groq.com/docs/prompt-caching
- https://console.groq.com/docs/responses-api
- https://console.groq.com/docs/content-moderation
- https://console.groq.com/docs/deprecations
- https://console.groq.com/docs/spend-limits
- https://console.groq.com/docs/projects
- https://console.groq.com/docs/your-data
- https://console.groq.com/docs/libraries
- https://console.groq.com/docs/lora
- https://console.groq.com/llms-full.txt
- Compound list tool prices: https://console.groq.com/docs/agentic-tooling/compound-beta (underlying + web search $5–8/1k, visit $1/1k, code $0.18/h)
- Free-tier billing behavior (staff): https://community.groq.com/t/free-tier/419
