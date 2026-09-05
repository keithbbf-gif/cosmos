# BROWSER-USE HANDS — G46 scout return (browser-use OSS + Cloud)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25 (docs fetched live).
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim. **No COSMOS core code was edited.**
**Assignment:** maker-docs sweep (DHx) — every Browser-Use hand COSMOS could fire.

**Already on the mesh (do not re-add as "new"):** MESH_ADDITIONS row 4 named browser-use as an UNVERIFIED `DomRail`-shaped worker. MESH_ADDITIONS_grok row 10 preferred **local OSS** and said **do not use Cloud MCP** (trains on inputs). This file inventories every official hand, including Cloud, so COW can decide. Playwright MCP remains the preferred *deterministic* a11y-tree lane; Browser-Use is the *open-ended* "figure out this site" lane (vendor-plural: two DOM members that can disagree).

**Filter:** a surface is a HAND only if COSMOS can **do** something with it (drive a browser, extract, dispatch an agent, poll a run, mint a CDP session). Chat-only dashboard chrome is out unless it is the DOM fallback.

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks (DOM worker, fenced commit, spend-gate, vendor-plural). Equal power, cheaper wins. Cloud token/browser bills sit **below** the MIT local library even when the hosted agent is more accurate.

**What Browser-Use is (one sentence):** an MIT-licensed Python library that turns a natural-language task into autonomous multi-step Chromium control (click/type/scroll/extract, with an indexed DOM plus optional screenshots), plus a separate commercial Cloud (hosted Agents + managed browsers). Official product map: [browser-use.com/llms.txt](https://browser-use.com/llms.txt). **Do not mix** the OSS package `browser-use` with the Cloud SDK `browser-use-sdk` — official docs say the APIs are different.

**Repo in play:** `keithbbf-gif/cosmos`. Browser-Use is a **DOM worker**, never a second ledger writer. It runs in an attempt-private workspace; fenced commit still owns the live tree.

---

## Official documentation URLs (fetched 2026-08-25)

These are the real vendor pages this scout used. Prefer the machine indexes (`llms.txt`) over blog roundups.

| what | URL |
|------|-----|
| GitHub (OSS library, MIT) | https://github.com/browser-use/browser-use |
| LICENSE | https://github.com/browser-use/browser-use/blob/main/LICENSE |
| Human docs home | https://docs.browser-use.com |
| **OSS machine index** | https://docs.browser-use.com/open-source/llms.txt |
| OSS full dump | https://docs.browser-use.com/open-source/llms-full.txt |
| **Cloud machine index** | https://docs.browser-use.com/cloud/llms.txt |
| Cloud full dump | https://docs.browser-use.com/cloud/llms-full.txt |
| Top-level docs index (Cloud-weighted) | https://docs.browser-use.com/llms.txt |
| Product map | https://browser-use.com/llms.txt |
| **Pricing (authoritative, dated 2026-08-17)** | https://browser-use.com/pricing.md |
| Human pricing | https://browser-use.com/pricing |
| OSS intro / quickstart | https://docs.browser-use.com/open-source/introduction · https://docs.browser-use.com/open-source/quickstart |
| Supported LLM backends | https://docs.browser-use.com/open-source/supported-models |
| Agent class params | https://docs.browser-use.com/open-source/customize/agent/all-parameters |
| Agent basics / `run()` | https://docs.browser-use.com/open-source/customize/agent/basics |
| Agent history / structured output | https://docs.browser-use.com/open-source/customize/agent/output-format |
| Browser / `BrowserSession` params | https://docs.browser-use.com/open-source/customize/browser/all-parameters |
| Real Chrome / auth / remote CDP | https://docs.browser-use.com/open-source/customize/browser/real-browser · https://docs.browser-use.com/open-source/customize/browser/authentication · https://docs.browser-use.com/open-source/customize/browser/remote |
| Built-in tools | https://docs.browser-use.com/open-source/customize/tools/available |
| Actor (Page/Element/Mouse) | https://docs.browser-use.com/open-source/legacy/actor/all-parameters |
| Local MCP | https://docs.browser-use.com/open-source/customize/integrations/mcp-server |
| CLI (Harness-backed) | https://docs.browser-use.com/open-source/browser-use-cli |
| Terminal TUI | https://docs.browser-use.com/open-source/browser-use-terminal |
| Telemetry (opt-out) | https://docs.browser-use.com/open-source/development/monitoring/telemetry |
| Cloud quickstart | https://docs.browser-use.com/cloud/quickstart |
| Cloud V4 REST | https://docs.browser-use.com/cloud/api-v4-overview |
| **V4 OpenAPI** | https://docs.browser-use.com/cloud/openapi/v4.json |
| V4 models | https://docs.browser-use.com/cloud/agent/models |
| Cloud MCP | https://docs.browser-use.com/cloud/guides/mcp-server |
| Cloud dashboard / key mint | https://cloud.browser-use.com · https://cloud.browser-use.com/settings?tab=api-keys&new=1 |
| Cloud SDK repo | https://github.com/browser-use/sdk |
| Skills | https://docs.browser-use.com/open-source/examples/skills/overview |
| Privacy / ToS | https://browser-use.com/privacy/ · https://browser-use.com/legal/terms-of-service |

---

## Licensing / cost floor

| fact | official source | COSMOS implication |
|------|-----------------|--------------------|
| OSS library is **MIT** | [LICENSE](https://github.com/browser-use/browser-use/blob/main/LICENSE) (Copyright 2024 Gregor Zunic) | Tool cost = **$0**. Install, copy, wrap. |
| FAQ: "Can I use this for free? **Yes.** You only need an LLM provider (or Ollama)." | [GitHub README](https://github.com/browser-use/browser-use) | Spend-gate the **LLM**, not the library. |
| Two commercial products on the same managed infra: **Agents** (NL goal → result) and **Browser Infrastructure** (raw CDP). | [product map](https://browser-use.com/llms.txt) | Cloud is optional. Local Chromium is the default. |
| Cloud **Free** plan: **$0**, 10 agent tasks/month, 3 concurrent sessions, no card. | [pricing.md](https://browser-use.com/pricing.md) (verified 2026-08-17) | Tiny overflow only. Not a daily driver. |
| Pay-as-you-go: buy credits ($5–$100k), no subscription; first top-up raises concurrency 3 → 10. Credits never expire. | same | Keith buys; COSMOS spend-gates. |
| Dev $29 / Business $299 / Scaleup $999 per month (credits = plan price). Annual = 10 months' price, full year of credits up front. | same | Real money. |
| Cloud browser: **$0.02 / browser-hour**, metered by the minute, 1-minute minimum. Unused reserved time refunded. | same | Cheap infra if Keith wants stealth/CAPTCHA. |
| Managed residential proxy **$5/GB** (Scaleup $4/GB); direct/BYO-proxy egress **$0.20/GB**. | same | Do not leave proxy on for bulk scrapes. |
| ChatBrowserUse OSS gateway (`bu-2-0` / `bu-latest`): **$0.60 / $0.06 / $3.50** per 1M in/cached/out. Signup docs also say **5 free tasks** (supported-models) *or* **$10** trial (human quickstart) — **do not treat those two figures as one fact.** Plan floor is the 10 tasks/month in pricing.md. | [supported-models](https://docs.browser-use.com/open-source/supported-models), [quickstart](https://docs.browser-use.com/open-source/quickstart), [pricing.md](https://browser-use.com/pricing.md) | Probe the live dashboard before quoting remaining credit. |
| Cloud V4 default model GPT-5.6 Luna: **$0.24 / $0.024 / $1.44** per 1M. Grok 4.5: $2.40 / $0.36 / $7.20. Claude Opus 5: $6 / $0.60 / $30. | [V4 models](https://docs.browser-use.com/cloud/agent/models) | Cloud Agents burn **Browser Use credits** plus browser-hour + network. |
| BYOK (Dev+): provider bills tokens; Browser Use adds **0.2× orchestration fee**. Browser/network still billed. Free/PAYG: **no BYOK**. | [pricing.md](https://browser-use.com/pricing.md) | Prefer pointing the **OSS Agent** at COSMOS rails over Cloud BYOK. |
| V2 agent (legacy): **$0.01 / task init** + from **$0.006 / step**. | [pricing.md](https://browser-use.com/pricing.md), [V2](https://docs.browser-use.com/cloud/api-v2-overview) | Cheap and less accurate (54% hard-task vs V4 76%). New work → V4 or local. |
| V3: 1.2× provider token rates (hosted) or provider + 0.2× (BYOK). | [pricing.md](https://browser-use.com/pricing.md) | Fastest Cloud agent; still metered. |
| Typical Cloud task (their 30-day production, Claude Opus 4.7): V2 ~$0.70 / V3 ~$0.87 / V4 ~$1.64. | [choosing an agent](https://docs.browser-use.com/cloud/choosing-an-agent) | Order-of-magnitude vs local+Ollama = $0. |
| Default OSS telemetry (PostHog) may include **task instructions, URLs, action traces, errors, final results**. Opt out: `ANONYMIZED_TELEMETRY=false`. | [Telemetry](https://docs.browser-use.com/open-source/development/monitoring/telemetry) | **Required COSMOS default: opt out.** This is the measured basis for MESH_ADDITIONS_grok's "cloud trains on inputs" caution — OSS telemetry is already task-level unless disabled. |

**Install (official, Python ≥ 3.11):** `uv add browser-use` or `pip install browser-use`, then `uvx browser-use install` (Chromium). CLI extras: `uv tool install browser-use` or `uvx --from 'browser-use[cli]' browser-use --mcp`. Cloud SDK (separate): `pip install browser-use-sdk`. COSMOS runtime is Python 3.14 — above the documented floor.

---

## Auth (all rows inherit this unless overridden)

Keith owns credentials. Store under `live/config/` (git-ignored). Never hard-code. Never print a key in full.

| method | credential | how | COSMOS use |
|--------|------------|-----|------------|
| **none (local Chromium + Ollama)** | — | `ChatOllama(model=…)` against `http://127.0.0.1:11434` | Highest-ranked: nothing that can run out. |
| **BYO provider key into OSS Agent** | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` (not the deprecated `GEMINI_API_KEY`), `GROQ_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `CEREBRAS_API_KEY`, `XAI_API_KEY` via OpenAI-compat/LiteLLM, Azure/AWS/OCI as documented | env / `.env` in the **attempt** workspace | Point at existing rails `oa-api` / `gem-api` / F5 / Groq / DeepSeek. Spend-gate the provider. |
| **Browser Use Cloud API key** | `bu_…` | header `X-Browser-Use-API-Key` **or** env `BROWSER_USE_API_KEY`. Mint at cloud.browser-use.com. | Cloud Agents, Cloud browsers, ChatBrowserUse(), Cloud MCP, `@sandbox()`. |
| **CLI `browser-use auth login`** | same `bu_` key, or stdin `--api-key-stdin` | stores in `~/.config/browser-use/config.json` | Remote CLI daemons. |
| **x402 (USDC on Base)** | crypto wallet, no API key | Cloud pay-per-request | Keith-only money path. Not a COSMOS default. |
| **Cloud BYOK (Dev+)** | Anthropic / OpenAI / Google key in Cloud Settings | V4 uses it automatically for matching models | Avoid: second copy of keys outside COSMOS spend-gate. |
| **Chrome profile / storage_state / TOTP** | local profile, `auth.json`, authenticator seed | `Browser.from_system_chrome()`, `storage_state=`, sensitive_data | Authenticated DOM without sending passwords to the LLM. |

**Package split (official):** OSS `from browser_use import Agent, Browser, ChatOllama`. Cloud `from browser_use_sdk.v4 import BrowserUse` (or `.v3`). Mixing examples is a documented footgun.

---

## How COSMOS reaches Browser-Use (one pattern)

Core stays sole ledger writer. Browser-Use is a **DOM worker** in an attempt-private workspace.

| Lane | Mechanism | When |
|------|-----------|------|
| **A. Python OSS Agent (preferred for "figure it out")** | `Agent(task=…, llm=ChatOllama(…) or ChatGoogle/ChatOpenAI, browser=Browser(allowed_domains=[…]))` then `await agent.run(max_steps=N)` | Open-ended site with no API. Spend-gate the LLM. `ANONYMIZED_TELEMETRY=false`. |
| **B. Python Actor / CLI Python stdin (preferred for scripted DOM)** | `Browser()` + Page/Element **or** `browser-use <<'PY' …` (PowerShell here-string on Windows) | Known clicks/extracts; no LLM required. Complements Playwright MCP. |
| **C. Local MCP stdio** | `uvx --from 'browser-use[cli]' browser-use --mcp` | Agent brains (Claude Code / Cursor / COSMOS MCP-client) need browser tools. **Local only.** |
| **D. HTTP Cloud (overflow, spend-gated)** | `POST https://api.browser-use.com/api/v4/runs` + poll `/status`. Header `X-Browser-Use-API-Key`. | Stealth / CAPTCHA / geo / parallel isolated browsers. Keith has minted a `bu_` key. |
| **E. Cloud CDP into OSS or Playwright** | `POST /api/v4/browsers` → `cdpUrl` → `Browser(cdp_url=…)` or Playwright `connect_over_cdp`. **Must** `PATCH … {"action":"stop"}` — disconnect does **not** stop billing. | Want our agent + their stealth browser. |
| **F. DOM on cloud.browser-use.com** | Dashboard: keys, billing, live view, human takeover. | AUTH_REQUIRED / first signup. Canon: DOM when the API depends on something that can run out. |

**Default COSMOS flags for unattended OSS jobs:**

```
ANONYMIZED_TELEMETRY=false
Agent(..., use_vision="auto",
      browser=Browser(allowed_domains=[...], headless=True),
      sensitive_data={...} if secrets else None)
history = await agent.run(max_steps=<cap>)
# ledger: history.final_result(), history.urls(), history.is_done(), history.has_errors()
```

Never let the agent write the live tree. Downloads go into the attempt workspace / GEM.

---

## Ranking table

| # | name | kind | HANDS (what it DOES) | auth | cost | power | how COSMOS reaches it | source |
|---|------|------|----------------------|------|------|-------|------------------------|--------|
| 1 | **`Agent` + `await agent.run()` (OSS)** | Python library | The core hand: NL `task` → loop of DOM snapshot → LLM decides tools → click/type/scroll/extract until `done`. Returns `AgentHistoryList`. `max_steps` default **100**. `run_sync()` also exists. | BYO LLM (or none if you only use Actor) | **free** MIT; inference = LLM | **highest** | Native worker in attempt workspace after Keith `pip/uv install browser-use`. Preferred COSMOS queue verb for open-ended DOM. | [basics](https://docs.browser-use.com/open-source/customize/agent/basics), [README](https://github.com/browser-use/browser-use) |
| 2 | **`Browser` / `BrowserSession` (same class)** | Python + CDP | Launch or attach Chromium; `start`/`stop`; `new_page`/`get_pages`/`get_current_page`/`close_page`. Alias: `Browser is BrowserSession`. All Actor methods hang off it. | none (local) | **free** | **highest** | Same process as the Agent, or standalone scripted control with **no LLM**. | [browser params](https://docs.browser-use.com/open-source/customize/browser/all-parameters) |
| 3 | **Actor: Page / Element / Mouse (direct CDP)** | Python | Playwright-shaped control **without** the Agent loop: `goto`, CSS/`get_element_by_prompt`, `evaluate`, `screenshot`, `extract_content`, `click`/`fill`/`select_option`/`drag_to`, coordinate mouse. This is the "hands without a brain" surface. | none, or LLM only for `*_by_prompt` / `extract_content` | **free** | **highest** | Scripted DOM jobs that must not spend tokens. Pair with Playwright MCP when selectors are known. | [Actor params](https://docs.browser-use.com/open-source/legacy/actor/all-parameters) |
| 4 | **Vision + indexed DOM (the perception stack)** | Agent params + tools | `use_vision` `"auto"` (default: screenshot **tool** present, used on request) / `True` (always) / `False` (never, tool removed). `vision_detail_level` `low`/`high`/`auto`. `highlight_elements` (default True) paints interactive nodes for the model. `paint_order_filtering` drops occluded nodes. `include_attributes` controls which HTML attrs enter the text DOM. This **is** the vision-based DOM extraction the brief named. | LLM must accept images if vision=True | **free** tool; vision tokens extra | **highest** | Default `"auto"` for COSMOS. Force `False` on login/PII pages (see sensitive_data). | [agent params](https://docs.browser-use.com/open-source/customize/agent/all-parameters), [tools](https://docs.browser-use.com/open-source/customize/tools/available) |
| 5 | **`extract` tool + `page_extraction_llm` + `Page.extract_content`** | extraction | LLM-backed structured scrape of the current page. Separate small/fast `page_extraction_llm` so the main brain is not used for "read this table." Actor: `page.extract_content(prompt, structured_output, llm)`. History: `history.extracted_content()`. | extractor LLM key | **free** tool; cheap-model inference | **highest** | Point `page_extraction_llm` at Ollama / Gemini Flash / Groq. Runtime-binding: the extract **is** the artifact. | [tools](https://docs.browser-use.com/open-source/customize/tools/available), [output](https://docs.browser-use.com/open-source/customize/agent/output-format) |
| 6 | **Built-in tool registry (default actions)** | tools | Navigation: `search` (DDG/Google/Bing), `navigate`, `go_back`, `wait`. Interaction: `click` (by **index**), `input`, `upload_file`, `scroll`, `find_text`, `send_keys`. JS: `evaluate` (shadow DOM / custom selectors). Tabs: `switch`, `close`. Visual: `screenshot`. Forms: `dropdown_options`, `select_dropdown`. Files: `write_file`/`read_file`/`replace_file`. Always: `done`. | none | **free** | **highest** | COSMOS allowlists tools per job (`Remove Tools` docs) — drop `evaluate`/`write_file` on untrusted sites. | [available tools](https://docs.browser-use.com/open-source/customize/tools/available) |
| 7 | **Local CLI `browser-use` (Python stdin)** | CLI | Direct browser control for coding agents. Unix: `uvx browser-use <<'PY' …`. **Windows PowerShell:** pipe a here-string. Helpers: `new_tab`, `page_info`, click/type/scroll/screenshot. Three modes: local Chrome/Chromium (existing tabs/cookies), Cloud, any CDP (`BU_CDP_URL` / `BU_CDP_WS`). `browser-use --doctor`. | none local; `bu_` for remote | **free** local | **highest** | Native worker. Matches "no bats — in-app / COSMOS action." Preferred over Cloud CLI for Keith's desktop Chrome. | [CLI](https://docs.browser-use.com/open-source/browser-use-cli) |
| 8 | **Local MCP server (`browser-use --mcp`)** | MCP stdio | Free OSS MCP: `uvx --from 'browser-use[cli]' browser-use --mcp`. Tools: `browser_navigate/click/type/get_state/scroll/go_back`, tab list/switch/close, `browser_extract_content`, session list/close, plus last-resort `retry_with_browser_use_agent`. `browser_get_state` takes `include_screenshot`. Claude Code / Cursor / Windsurf recipes documented, **including Windows** `%APPDATA%\Claude\…`. | `OPENAI_API_KEY` **or** `ANTHROPIC_API_KEY` (for the agent-retry tool). Env `BROWSER_USE_HEADLESS`, `BROWSER_USE_DISABLE_SECURITY`. | **free** OSS; LLM = provider | **highest** | COSMOS MCP-client **or** `claude mcp add`. **Not** the Cloud MCP URL. | [OSS MCP](https://docs.browser-use.com/open-source/customize/integrations/mcp-server) |
| 9 | **`ChatOllama` local backend** | LLM backend | `ChatOllama(model="llama3.1:8b")` after `ollama serve` + `ollama pull`. Documented first-class. Completes the "nothing that can run out" canon. | none | **free** ($0 inference) | **highest** | Point Agent at the Ollama rail (MESH_ADDITIONS #1). Weak models may need `extend_system_message` with a concrete action-schema example (Qwen docs warn about this class of failure). | [supported models — Ollama](https://docs.browser-use.com/open-source/supported-models) |
| 10 | **`ChatOpenAI` + custom `base_url` (OpenAI-compat)** | LLM adapter | Any OpenAI-shaped endpoint: COSMOS `oa-api`, xAI/Grok (`XAI_API_KEY` + xAI base), vLLM, llama.cpp, LiteLLM sidecar, Novita, Moonshot, Qwen DashScope, ModelScope. This is how Grok reaches the Agent **without** a native `ChatXAI` class (none is documented in OSS supported-models). | endpoint key | **free** adapter; inference = backend | **highest** | Preferred *shape*: one compat URL so the Agent does not learn every vendor SDK. Spend-gate still sits in front of the real provider (`sgh-api` / `gw-api` / `oa-api`). | [supported models](https://docs.browser-use.com/open-source/supported-models), [novita.py](https://github.com/browser-use/browser-use/blob/main/examples/models/novita.py), [moonshot.py](https://github.com/browser-use/browser-use/blob/main/examples/models/moonshot.py) |
| 11 | **`output_model_schema` (Pydantic structured output)** | Agent param | Pass a Pydantic class; `history.structured_output` is the parsed object. Cloud V4 has the same idea. | same | **free** | **highest** | COSMOS queue jobs that must return typed JSON (prices, citations, form status) rather than prose. | [output format](https://docs.browser-use.com/open-source/customize/agent/output-format) |
| 12 | **`AgentHistoryList` (the result artifact)** | Python result | `urls()`, `screenshots()` / `screenshot_paths()`, `action_names()`, `extracted_content()`, `errors()`, `model_actions()`, `model_thoughts()`, `final_result()`, `is_done()`, `is_successful()`, `has_errors()`, `number_of_steps()`, `total_duration_seconds()`. | none | **free** | **highest** | This is the runtime-binding evidence. Ledger the real fields (`final_result`, `urls`, `has_errors`) — never a green log. | [output format](https://docs.browser-use.com/open-source/customize/agent/output-format) |
| 13 | **`allowed_domains` / `prohibited_domains`** | Browser param | Navigation allow/deny lists. Patterns: `example.com`, `*.example.com`, `http*://example.com`, `chrome-extension://*`. TLD wildcards (`example.*`) **forbidden**. 100+ entries auto-optimize to O(1) sets. `allowed` wins if both set. | none | **free** | **highest** | Required on every unattended COSMOS job. Prevents the agent wandering onto billing/admin hosts. | [browser params](https://docs.browser-use.com/open-source/customize/browser/all-parameters) |
| 14 | **`sensitive_data` placeholders** | Agent param | LLM sees `x_user` / `x_pass`; real values inject into DOM **after** the model call. Domain-scoped dicts supported. Docs: also set `use_vision=False` so screenshots cannot leak the typed password. Example sets `ANONYMIZED_TELEMETRY=false`. | secrets in process memory, not in prompts | **free** | **highest** | Login jobs. Prefer `storage_state` cookies over passwords when possible. | [sensitive data](https://docs.browser-use.com/open-source/examples/templates/sensitive-data) |
| 15 | **`Browser.from_system_chrome()` + storage_state** | auth | Reuse Keith's real Chrome profile (cookies, extensions, logged-in sessions). `list_chrome_profiles()`. Export `auth.json` then reload headless. May need Chrome fully closed first (debug-mode conflict). | local Chrome profile | **free** | **highest** | Authenticated DOM (Gmail, vendor portals) without sending passwords to any LLM. Contained profile — not the live personal session if isolation is required. | [auth](https://docs.browser-use.com/open-source/customize/browser/authentication), [real browser](https://docs.browser-use.com/open-source/customize/browser/real-browser) |
| 16 | **Custom tools (`Tools` + `@tools.action`)** | Python | Register arbitrary Python (HTTP to Core, file ops, mesh lookups) as agent tools. `controller=` is the legacy alias. | same | **free** | **high** | Give the DOM agent a `ledger_note` / `queue_return` tool instead of scraping COSMOS itself. | [README custom tools](https://github.com/browser-use/browser-use), [add tools](https://docs.browser-use.com/open-source/customize/tools/add) |
| 17 | **Remove / restrict tools** | tools | Drop defaults (`evaluate`, `write_file`, `search`) so a job cannot shell out via page JS or write the workspace. | none | **free** | **high** | Least-privilege per queue job. | [remove tools](https://docs.browser-use.com/open-source/customize/tools/remove) |
| 18 | **`fallback_llm`** | Agent param | Primary LLM retries (~5, exponential backoff) then switches for the rest of the run on 429/401/402/5xx. | two providers | **free** adapter | **high** | Vendor-plural inside one job: Grok → Gemini → Ollama. | [agent params](https://docs.browser-use.com/open-source/customize/agent/all-parameters) |
| 19 | **`ChatGoogle` (Gemini / Vertex / Gemma)** | LLM backend | `ChatGoogle(model='gemini-2.5-flash')`. `GOOGLE_API_KEY` (**`GEMINI_API_KEY` deprecated 2025-05**). `vertexai=True` for Vertex. | `GOOGLE_API_KEY` / ADC | **metered** (`gem-api` already budgeted; Vertex $300 credit to 2026-10-13) | **high** | Point at existing `gem-api`. Fast/cheap vision for `page_extraction_llm`. | [supported models](https://docs.browser-use.com/open-source/supported-models) |
| 20 | **`ChatAnthropic`** | LLM backend | `ChatAnthropic(model='claude-sonnet-4-6')`. Coordinate clicking auto-enabled for `claude-sonnet-4-*` and `claude-opus-4-*`. | `ANTHROPIC_API_KEY` | **metered** (distinct from F5 Claude Code weekly quota) | **high** | Use as Dispatcher rail so F5 allotment is not the only Claude path (MESH_ADDITIONS #17). | [supported models](https://docs.browser-use.com/open-source/supported-models) |
| 21 | **`ChatGroq`** | LLM backend | e.g. `meta-llama/llama-4-maverick-17b-128e-instruct`. | `GROQ_API_KEY` | **free-tier** then metered | **high** | Fast bulk DOM loops. Probe remaining Groq quota first. | [supported models](https://docs.browser-use.com/open-source/supported-models) |
| 22 | **`ChatDeepSeek` / `ChatMistral` / `ChatCerebras` / `ChatOpenRouter` / `ChatLiteLLM`** | LLM backends | First-class classes. OpenRouter = 300+ models. LiteLLM = `pip install litellm` then any LiteLLM name. | per-provider | **free** adapter; inference varies (OpenRouter has free models — **pin a named model**, do not use a rotating `free` router) | **high** | Overflow / vendor-plural. LiteLLM is the catch-all when a native class is missing (xAI, HuggingFace, …). | [supported models](https://docs.browser-use.com/open-source/supported-models) |
| 23 | **`ChatAzureOpenAI` / `ChatAWSBedrock` / `ChatAnthropicBedrock` / `ChatVercel` / `ChatOCIRaw`** | LLM backends | Azure (incl. Responses API auto-detect for gpt-5.1-codex / computer-use-preview). Bedrock `pip install "browser-use[aws]"`. Vercel AI Gateway with provider `order`. OCI `pip install "browser-use[oci]"`. | cloud-vendor creds | **metered** | **med-high** | Only if Keith already has those clouds. Do not mint a fourth wallet. | [supported models](https://docs.browser-use.com/open-source/supported-models) |
| 24 | **Langchain adapter `ChatLangchain`** | LLM adapter | Wrap an existing LangChain chat model. Marked **legacy** in the examples README. | underlying key | **free** adapter | **med** | Skip unless a worker already speaks LangChain. Prefer native Chat* classes. | [examples/models/langchain](https://github.com/browser-use/browser-use/tree/main/examples/models/langchain) |
| 25 | **CDP attach (`cdp_url`) + remote Browser** | Browser param | Connect to any Chrome that exposes DevTools: local debug port, Playwright-launched, Browserbase, **or** Browser-Use Cloud. `is_local=False` for remote (changes download behavior). | none, or Cloud key if `use_cloud=True` | **free** local CDP; Cloud browser $0.02/hr | **high** | COSMOS already running Chrome for another DOM rail can be reused. `use_cloud=True` needs `BROWSER_USE_API_KEY`. | [remote](https://docs.browser-use.com/open-source/customize/browser/remote) |
| 26 | **`keep_alive` + follow-up tasks (same session)** | Browser + Agent | Keep Chromium up after `run()`; send another task against the same cookies/tabs. Template: follow-up tasks. | same | **free** (local process) | **high** | Multi-turn portal work (login once, then N extracts). | [follow-up](https://docs.browser-use.com/open-source/examples/templates/follow-up-tasks), `keep_alive` in [browser params](https://docs.browser-use.com/open-source/customize/browser/all-parameters) |
| 27 | **Parallel agents (separate browsers)** | template | One Agent per Browser instance, `asyncio.gather`. | per-agent LLM | **free** tool; N× inference + RAM | **high** | Bulk extract. Chrome is memory-heavy — official FAQ says use Cloud for production fan-out. Cap concurrency. | [parallel](https://docs.browser-use.com/open-source/examples/templates/parallel-browser) |
| 28 | **Playwright + Browser-Use hybrid** | template | Drive Playwright yourself, then hand the same browser to Agent (or the reverse). | same | **free** | **high** | Deterministic setup (Playwright) + open-ended finish (Agent). Aligns with Playwright MCP as sibling lane. | [Playwright integration](https://docs.browser-use.com/open-source/examples/templates/playwright-integration) |
| 29 | **`initial_actions` (no LLM)** | Agent param | Run a list of actions *before* the model loop (open URL, accept cookies). `directly_open_url` default True if the task contains a URL. | none | **free** (saves tokens) | **high** | Skip the "how do I get to the page" tax. | [agent params](https://docs.browser-use.com/open-source/customize/agent/all-parameters) |
| 30 | **`flash_mode` / Fast Agent** | Agent param | Skip evaluation, next-goal, and thinking; memory only. Faster/cheaper, less reliable. Overrides `use_thinking`. | same | **saves** tokens | **med-high** | Cheap watchers / "is this in stock." Not for authenticated money moves. | [agent params](https://docs.browser-use.com/open-source/customize/agent/all-parameters), [fast agent](https://docs.browser-use.com/open-source/examples/templates/fast-agent) |
| 31 | **Lifecycle hooks `on_step_start` / `on_step_end`** | Python callbacks | Inspect/modify Agent mid-run: `pause`/`resume`/`add_new_task`, raw CDP `DOM.getOuterHTML`, screenshot events, URL log. Docs: most needs are better as custom tools. | same | **free** | **high** | COSMOS step-cap / domain-violation kill switch. Increase `step_timeout` if the hook is slow. | [hooks](https://docs.browser-use.com/open-source/customize/hooks) |
| 32 | **TOTP / email-SMS 2FA / 1Password (OSS + Cloud)** | auth | OSS: authenticator-app TOTP. Cloud: 2FA guide + 1Password autofill + domain-scoped Secrets. Terminal: `/secrets` with `--totp` seed (not the current 6 digits). | 1Password `op` CLI / TOTP seed | **free** local TOTP; 1Password is Keith's seat | **high** | Prefer TOTP seed in `live/config/` over SMS. Never put the seed in the task prompt. | [auth](https://docs.browser-use.com/open-source/customize/browser/authentication), [Cloud 2FA](https://docs.browser-use.com/cloud/guides/2fa), [1Password](https://docs.browser-use.com/cloud/guides/1password) |
| 33 | **Downloads, PDFs, video, HAR, traces, GIF** | Browser + Agent | `accept_downloads` (default True), `downloads_path`, `auto_download_pdfs` (default True). Optional `pip install "browser-use[video]"` for mp4. HAR + traces dirs. `generate_gif`. | none | **free** (disk) | **high** | Attempt-workspace downloads → GEM (hash-named). Video extra is optional. | [browser params](https://docs.browser-use.com/open-source/customize/browser/all-parameters) |
| 34 | **Cost tracking `calculate_cost=True`** | Agent param | Token/API cost accounting for the run. | same | **free** (observability) | **high** | Feed spend-gate evidence. Pair with [Costs](https://docs.browser-use.com/open-source/development/monitoring/costs). | [agent params](https://docs.browser-use.com/open-source/customize/agent/all-parameters) |
| 35 | **Telemetry opt-out `ANONYMIZED_TELEMETRY=false`** | env | Disables PostHog. Default **on**, and may include the **task text and URLs**. | none | **free** | **highest (hygiene)** | **Required** on every COSMOS process. Also `BROWSER_USE_LOGGING_LEVEL=DEBUG` for doctoring. | [telemetry](https://docs.browser-use.com/open-source/development/monitoring/telemetry) |
| 36 | **SKILL.md pack (`browser-use`, `open-source`, `qa`, `remote-browser`, `cloud`, `x402`)** | skills | `npx skills add https://github.com/browser-use/browser-use --skill <name>` or `browser-use skill install`. Teaches Claude Code / Cursor / Codex / OpenClaw how to call the CLI. QA skill returns a 1–5 score with evidence. | none for local skills | **free** | **high** | Install into G46/Cursor skills dir so coding agents drive the browser instead of inventing Playwright. | [skills overview](https://docs.browser-use.com/open-source/examples/skills/overview) |
| 37 | **Cloud Free plan (10 tasks/mo, 3 sessions)** | Cloud plan | $0, no card. Free browsers + 10 hosted-agent tasks/month. CAPTCHA + webhooks included even on Free. No BYOK, no scheduled jobs, no auto-recharge. | `bu_` key | **free-tier** | **med-high** (capped) | Signup overflow only. Probe remaining tasks on the dashboard — do not treat as unlimited. | [pricing.md](https://browser-use.com/pricing.md) |
| 38 | **`ChatBrowserUse()` OSS gateway** | hosted LLM from OSS Agent | In-house `bu-2-0` / `bu-latest` (default) claimed 3–5× faster than frontier on browser tasks. Also accepts provider-prefixed ids (`anthropic/claude-sonnet-4-6`, `openai/gpt-5.5`, `google/gemini-3-pro`) on **one** `BROWSER_USE_API_KEY`. Preview OSS weights: `browser-use/bu-30b-a3b-preview`. | `BROWSER_USE_API_KEY` | **metered** ($0.60/$3.50 per 1M on bu-2-0) + 5-task or $10 signup (docs disagree) | **high** | Only after local Ollama/Gemini/Grok are exhausted. Do not make this the default brain — it is a Cloud bill. | [supported models](https://docs.browser-use.com/open-source/supported-models), [bu_oss.py](https://github.com/browser-use/browser-use/blob/main/examples/models/bu_oss.py) |
| 39 | **Cloud V4 hosted Agent (`POST /api/v4/runs`)** | Cloud REST + SDK | Give a goal, get `result`. Implicit session + workspace. Poll cheap `GET /runs/{id}/status` until terminal, then `GET /runs/{id}`. Cancel: `POST /runs/{id}/cancel` (stops further token billing). Events: `GET /runs/{id}/events` (`browser.ready` → `live_view_url`). Default model `gpt-5.6-luna`; Grok 4.5 / Opus 5 / MiniMax M3 documented. Python: `browser_use_sdk.v4.BrowserUse`. | `X-Browser-Use-API-Key: bu_…` | **credits** + $0.02/hr + network. Free = 10 tasks/mo | **high** (accuracy; costs real $) | Spend-gate HTTP. Return-watcher polls `/status`. Do **not** use if ZDR is on (V4 returns 403). | [V4 overview](https://docs.browser-use.com/cloud/api-v4-overview), [OpenAPI](https://docs.browser-use.com/cloud/openapi/v4.json), [models](https://docs.browser-use.com/cloud/agent/models) |
| 40 | **V4 sessions + follow-ups (`POST /sessions/{id}/queue`)** | Cloud REST | Conversation across runs in the same browser context. `interrupt: true` cancels the current turn. Queue list/get/delete. `POST /sessions/{id}/purge` is **ZDR-only**. | `bu_` | **credits** | **high** | Multi-turn Cloud jobs. Prefer local `keep_alive` when stealth is not required. | [sessions](https://docs.browser-use.com/cloud/agent/sessions), OpenAPI |
| 41 | **V4 workspaces + files** | Cloud REST | `POST /workspaces`, presigned upload under `uploads/`, list/delete files, size/quota. Persist scripts/CSVs across runs. | `bu_` | **credits** + storage quota | **high** | Cloud-side GEM analogue. Pull artifacts into local GEM; ledger holds the hash, not the Cloud URL as authority. | [workspaces](https://docs.browser-use.com/cloud/agent/workspaces), OpenAPI |
| 42 | **Rerunnable Cloud scripts (self-heal)** | Cloud pattern | First V4 run writes `scripts/*.py` into a workspace; later runs execute + repair if the site changed. Still starts a model (token cost remains). | `bu_` | **credits** (often less than a full agent replay) | **high** | Repeated extracts (HN, dockets, price tables). Compare first-run vs later-run cost before claiming savings (official caveat). | [scripts](https://docs.browser-use.com/cloud/agent/scripts) |
| 43 | **Cloud Browser Infrastructure (`POST /api/v4/browsers`)** | Cloud REST + CDP | Stealth Chromium + proxies + live view + recording. Returns `id` + `cdpUrl`. Connect OSS Agent / Playwright / Puppeteer / Selenium. **Stop with `PATCH /browsers/{id} {"action":"stop"}`** — `close()` / dropped CDP does **not** stop billing. Also `wss://connect.browser-use.com?apiKey=…&proxyCountryCode=us` (no SDK). List/get, downloads. | `bu_` | **$0.02/hr** + proxy/egress | **high** | When local Chrome is blocked (Cloudflare) or the worker is headless. Pair with OSS Agent so COSMOS still owns the brain. | [browser quickstart](https://docs.browser-use.com/cloud/browser/quickstart), [CDP](https://docs.browser-use.com/cloud/guides/browser-api), [Playwright](https://docs.browser-use.com/cloud/browser/playwright-puppeteer-selenium) |
| 44 | **Cloud profiles (cookies/localStorage)** | Cloud REST | `GET/POST/PATCH/DELETE /profiles`. Persist login **without storing passwords**. Local→Cloud cookie sync (`profile-use` / profile-sync guide). `cloud_profile_id` on OSS `Browser(use_cloud=True, …)`. Free: 10 profiles; Dev 20; Business+ unlimited. | `bu_` | **included** in plan | **high** | Authenticated Cloud runs. Still Keith's cookies — treat as a secret. | [profiles](https://docs.browser-use.com/cloud/guides/authentication), OpenAPI `/profiles` |
| 45 | **Stealth / CAPTCHA / residential proxies** | Cloud browser feature | Hardened Chromium fork, fingerprint randomization, cookie-banner blocking, Cloudflare/PerimeterX bypass, residential proxies in 195+ countries. `cloud_proxy_country_code`. Official: local OSS **cannot** reliably solve CAPTCHAs — use Cloud. | `bu_` | browser-hour + **$5/GB** managed proxy | **high** (sites that block Playwright) | Last resort after local fails. Spend-cap the GB. | [stealth](https://docs.browser-use.com/cloud/browser/stealth), [proxies](https://docs.browser-use.com/cloud/browser/proxies), README FAQ |
| 46 | **Human-in-the-loop + live preview + recording** | Cloud | `browser.ready` event → `live_view_url` (iframe). Take over for auth/payments, then continue. Session recordings. | `bu_` | **included** (recording storage on plan) | **high** | Keith-in-the-loop for money/credentials (canon: Keith does money). COSMOS must not auto-complete checkouts. | [HITL](https://docs.browser-use.com/cloud/agent/human-in-the-loop), [live preview](https://docs.browser-use.com/cloud/browser/live-preview) |
| 47 | **`@sandbox()` (legacy OSS→Cloud wrapper)** | Python decorator | `@sandbox(cloud_profile_id=…, cloud_proxy_country_code=…, cloud_timeout=…)` injects a Cloud `Browser` into an OSS `Agent`. Docs: "easiest production path." Timeout: official remote.md says **max free 15 min, paid 240 min**. | `bu_` | Cloud rates | **high** | Thin wrapper; prefer explicit `Browser(use_cloud=True)` so stop/billing is visible. | [sandbox](https://docs.browser-use.com/open-source/legacy/sandbox/quickstart), [remote](https://docs.browser-use.com/open-source/customize/browser/remote) |
| 48 | **Cloud MCP `https://api.browser-use.com/v3/mcp`** | MCP HTTP | Hosted tools: `run_session`, `get_session`, `send_task`, `stop_session`, `get_session_messages`, `list_sessions`, `list_browser_profiles`. Header `x-browser-use-api-key`. Cursor/Claude/Windsurf snippets. | `bu_` | **credits** per session | **med-high** | MESH_ADDITIONS_grok: **do not** use for COSMOS (task text leaves the box). Prefer local `--mcp`. If used, spend-gate + opt-out still does not cover Cloud training ToS — treat as a Keith decision. | [Cloud MCP](https://docs.browser-use.com/cloud/guides/mcp-server) |
| 49 | **Cloud V3 / V2 agents (legacy)** | Cloud REST | V3 = fastest, 67% hard-task. V2 = step-priced (`browser-use-2.0` $0.006/step, Gemini Flash Lite $0.005, O3 $0.03, Sonnet 4.6 $0.05) + $0.01 init; files 10 MB; streaming steps. Base `https://api.browser-use.com/api/v2`. Official: new work → **V4**. | `bu_` | **cheapest Cloud**, lowest accuracy | **med** | Only to finish an old integration. COSMOS should not start on V2. | [choosing](https://docs.browser-use.com/cloud/choosing-an-agent), [V2 agent](https://docs.browser-use.com/cloud/legacy/agent) |
| 50 | **V2 Cloud Skills ("turn a site into an API")** | Cloud legacy | Record a workflow once, call it as a deterministic endpoint. | `bu_` | **credits** | **med** | Overlaps V4 rerunnable scripts (row 42), which is the current path. | [legacy skills](https://docs.browser-use.com/cloud/legacy/skills) |
| 51 | **Webhooks** | Cloud | Plan table: webhook events on Free+. Return-watcher ingress instead of polling. | webhook secret + `bu_` to register | **included** | **high** (infra) | HMAC-verify, ledger delivery id, fail-closed on bad sig. Prefer over `/status` spin. | [pricing plan features](https://browser-use.com/pricing.md), [webhooks product URL](https://browser-use.com/webhooks) |
| 52 | **Browser Use Terminal (`browser` TUI + `browser-use-terminal`)** | TUI + CLI + `browser_use.beta.Agent` | Codex-style browser assistant (Rust runtime). TUI: `/task /model /auth /browser /profile /secrets /domains`. One-shot: `browser-use-terminal run-openai\|run-anthropic\|run-openrouter\|run-deepseek`. Python: `from browser_use.beta import Agent`. **Separate binary from `browser-use` CLI.** Installer: `curl -fsSL https://browser-use.com/terminal/install.sh \| sh` (Unix; Windows path not in this page — treat as **unverified on this host**). | provider keys or `bu_` | **free** TUI; inference = provider | **med-high** | Human/Keith interactive. COSMOS unattended jobs should use OSS `Agent` or Cloud V4, not a TUI. | [Terminal](https://docs.browser-use.com/open-source/browser-use-terminal) |
| 53 | **x402 crypto pay-per-request** | Cloud payments | USDC on Base, no signup/API key. Skill walks wallet setup + ~$1 test run. | wallet | **metered crypto** | **low-med** | Keith-only. COSMOS does not hold wallets. | [x402 skill](https://docs.browser-use.com/open-source/examples/skills/x402) |
| 54 | **Claude Code / Managed Agents / OpenClaw / Hermes integrations** | Cloud tutorials | Official recipes to give those agents a Browser-Use browser (CLI skill or CDP). | `bu_` + that agent's login | **credits** | **med** | Overlaps COSMOS's own DOM worker. Use only if Keith wants *those* agents to browse, not Core. | [Claude Code](https://docs.browser-use.com/cloud/tutorials/integrations/claude-code), [OpenClaw](https://docs.browser-use.com/cloud/tutorials/integrations/openclaw), [Hermes](https://docs.browser-use.com/cloud/tutorials/integrations/hermes-agent) |
| 55 | **Cloud V4 structured output + thinking levels + cost caps + judgement** | Cloud Agent | JSON schema on V4 runs; `modelParams` / thinkingLevel across V2/V3/V4; per-run cost totals and caps; optional judgement. SDK types may lag REST (official: use `POST /runs` for `modelParams` until SDK regen). | `bu_` | **credits** | **high** | Spend **cap on the request** is the Cloud-side cousin of COSMOS spend-gate. Still ledger the returned cost fields as evidence. | [FAQ](https://docs.browser-use.com/cloud/faq), [thinking](https://docs.browser-use.com/cloud/agent/thinking-levels), [structured](https://docs.browser-use.com/cloud/agent/structured-output) |
| 56 | **OSS Agent `skills=` (Cloud skill UUIDs)** | Agent param | `skills=['skill-uuid']` or `['*']`. **Requires `BROWSER_USE_API_KEY`.** Distinct from SKILL.md (row 36). | `bu_` | **credits** | **med** | Skip until Cloud is adopted. Local custom tools (row 16) cover the same job without a Cloud skill id. | [agent params](https://docs.browser-use.com/open-source/customize/agent/all-parameters) |
| 57 | **Search API (BETA, Cloud examples)** | Cloud example | `examples/cloud/05_search_api.py` — content extraction Search API. Not in the V4 OpenAPI path list fetched today. | `bu_` | **UNVERIFIED** rate | **low-med** | Do not build on BETA. Prefer `extract` locally or V4 Agent. | [examples/cloud](https://github.com/browser-use/browser-use/tree/main/examples/cloud) |
| 58 | **DOM fallback on cloud.browser-use.com** | DOM | Mint keys, billing, live view, HITL takeover, first OAuth — everything the API cannot do when AUTH_REQUIRED. | Keith's browser session | **free** UI | **high as fallback** | Existing `cosmos_browser` / Playwright MCP. Not the daily dispatch path. | dashboard URLs above |
| 59 | **Timeout env knobs (`TIMEOUT_*`)** | env | Per-event timeouts: Navigate 15s, Type 60s, BrowserStateRequest 30s, etc. Raise on slow portals. | none | **free** | **infra** | Job-local env in the attempt workspace. | [agent params — env](https://docs.browser-use.com/open-source/customize/agent/all-parameters) |
| 60 | **ProxySettings (local OSS)** | Browser param | `ProxySettings(server=…, bypass=…, username=…, password=…)`. Local path; Cloud has its own proxy product. | proxy creds | **free** adapter; proxy may be paid | **med** | Only if Keith already has a proxy. Cloud residential is the documented CAPTCHA path. | [browser params](https://docs.browser-use.com/open-source/customize/browser/all-parameters) |

---

## LLM backends the vendor actually names (OSS `Chat*` classes)

Native classes on [supported-models](https://docs.browser-use.com/open-source/supported-models) (15+ providers). xAI/Grok is **not** a native OSS class; reach it via ChatOpenAI-compat, ChatLiteLLM, ChatOpenRouter, ChatBrowserUse provider prefix, or Cloud V4 `grok-4.5`.

| class | vendor | env | COSMOS rail to reuse |
|-------|--------|-----|----------------------|
| `ChatOllama` | local Ollama | none | new local rail (MESH_ADDITIONS #1) |
| `ChatGoogle` | Gemini / Vertex / Gemma | `GOOGLE_API_KEY` | `gem-api` |
| `ChatOpenAI` | OpenAI **or any compat URL** | `OPENAI_API_KEY` (+ `base_url`) | `oa-api`; also **Grok/xAI** via xAI base |
| `ChatAnthropic` | Claude | `ANTHROPIC_API_KEY` | missing Dispatcher rail (#17) |
| `ChatAzureOpenAI` | Azure OpenAI | `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY` | only if Azure exists |
| `ChatAWSBedrock` / `ChatAnthropicBedrock` | Bedrock | AWS keys / profile / IAM / SSO | only if AWS exists |
| `ChatVercel` | Vercel AI Gateway | `VERCEL_API_KEY` | router; avoid silent fallback |
| `ChatGroq` | Groq | `GROQ_API_KEY` | MESH_ADDITIONS #2 |
| `ChatOCIRaw` | Oracle GenAI | `~/.oci/config` | unlikely |
| `ChatDeepSeek` | DeepSeek | `DEEPSEEK_API_KEY` | MESH_ADDITIONS #13 |
| `ChatMistral` | Mistral | `MISTRAL_API_KEY` | MESH_ADDITIONS #12 |
| `ChatCerebras` | Cerebras | `CEREBRAS_API_KEY` | overflow speed |
| `ChatOpenRouter` | OpenRouter | `OPENROUTER_API_KEY` | pin a **named** model |
| `ChatLiteLLM` | 100+ via LiteLLM | provider-specific | catch-all (incl. xAI) |
| `ChatBrowserUse` | Browser Use Cloud | `BROWSER_USE_API_KEY` | metered; also `anthropic/` `openai/` `google/` prefixes |
| `ChatLangchain` | LangChain wrap | underlying | legacy |

**Cloud V4 hosted model IDs** ([models](https://docs.browser-use.com/cloud/agent/models)): Anthropic `claude-opus-4.7/4.8/5`, `claude-fable-5`, `claude-sonnet-5`; OpenAI `gpt-5.5`, `gpt-5.6`, `gpt-5.6-sol/terra/luna`; Google `gemini-3-flash`, `gemini-3.1-pro`, `gemini-3.5-flash`, `gemini-3.6-flash`; xAI **`grok-4.5`** (BYOK column "—"); Z.ai `glm-5.2`; Moonshot `kimi-k3`; MiniMax `minimax-m3`. BYOK only for Anthropic/OpenAI/Google on Dev+.

---

## Cloud V4 REST surface (complete path list from OpenAPI 2026-08-25)

Base `https://api.browser-use.com/api/v4`. Auth: `X-Browser-Use-API-Key`. Spec: [openapi/v4.json](https://docs.browser-use.com/cloud/openapi/v4.json).

| method | path | HAND |
|--------|------|------|
| POST | `/runs` | create hosted agent run (402 = no credits) |
| GET | `/runs` | list (cursor) |
| GET | `/runs/{id}` | full result (after terminal) |
| GET | `/runs/{id}/status` | **cheap poll** |
| POST | `/runs/{id}/cancel` | stop token billing |
| GET | `/runs/{id}/events` | incremental events / live URL |
| GET | `/runs/{id}/attachments` | files attached to the run |
| GET | `/sessions` | list conversations |
| GET | `/sessions/{id}` | session detail / idle poll |
| POST | `/sessions/{id}/queue` | follow-up / interrupt |
| GET | `/sessions/{id}/queue` | list queue |
| GET/DELETE | `/sessions/{id}/queue/{message_id}` | get / cancel queued |
| POST | `/sessions/{id}/purge` | ZDR-only hard delete |
| POST | `/workspaces` | mint workspace |
| GET/PATCH/DELETE | `/workspaces/{id}` | get / rename / archive |
| GET | `/workspaces/{id}/size` | quota |
| POST | `/workspaces/{id}/files/upload` | presigned PUT |
| GET/DELETE | `/workspaces/{id}/files` | list / delete |
| GET/POST | `/browsers` | list / **create CDP session** |
| GET/PATCH | `/browsers/{id}` | get / **`{"action":"stop"}`** |
| GET | `/browsers/{id}/downloads` | downloads |
| GET/POST | `/profiles` | list / create cookie profile |
| GET/PATCH/DELETE | `/profiles/{id}` | get / update / delete |

V2 base `https://api.browser-use.com/api/v2` remains for simple step-priced tasks. Cloud MCP is V3: `https://api.browser-use.com/v3/mcp`.

---

## Hazards (carry with the scout return)

- **Two packages, two APIs.** `pip install browser-use` ≠ `pip install browser-use-sdk`. Official: do not mix Cloud SDK examples with the OSS library.
- **Telemetry default-on** includes task text and URLs. Set `ANONYMIZED_TELEMETRY=false`. Cloud ToS/privacy is a separate training surface; local MCP is the COSMOS default.
- **CAPTCHA:** official README — local fingerprint is not enough; Cloud stealth is the documented path.
- **Chrome memory / parallel agents:** official production FAQ points at Cloud infra. Cap local fan-out.
- **Stop billing:** Cloud browsers keep charging until `PATCH … stop`. Disconnect is not stop.
- **V4 + Zero Data Retention:** OpenAPI 403 — V4 unsupported when ZDR is enabled.
- **Windows CLI:** PowerShell here-string, not bash `<<'PY'`.
- **`GEMINI_API_KEY` renamed** to `GOOGLE_API_KEY`.
- **Qwen/small local models** often emit the wrong action schema — add a concrete example to the prompt or use a stronger model.
- **Never a second ledger writer.** Browser-Use publishes artifacts into the attempt workspace; Core fences.

---

## COSMOS recommendation (one paragraph)

Ship **lane A+B+C first**: OSS `Agent` with `ChatOllama` or existing `gem-api`/`sgh-api` as `page_extraction_llm`/`llm`, `Browser(allowed_domains=…, headless=True)`, `ANONYMIZED_TELEMETRY=false`, local `--mcp` for agent brains, Actor/CLI Python for scripted steps. Keep Playwright MCP as the deterministic sibling. Treat Cloud V4 + $0.02/hr browsers as a **spend-gated overflow** for Cloudflare/CAPTCHA/geo, with explicit stop and a request-level cost cap. Do not wire Cloud MCP into COSMOS by default.

---

## Host bind (additive, 2026-08-27 s6) — D4 still dark / M5 default holds

WAVE D4 (OSS Agent, not Cloud MCP) stays behind C1 Ollama or an existing rail. Default DOM worker remains Playwright MCP (M5); this file is the vendor-plural overflow, not a second authority. Cloud MCP stays **out**. Not a stage-6 pass.
