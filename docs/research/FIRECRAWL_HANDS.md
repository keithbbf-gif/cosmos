# FIRECRAWL HANDS — G46 scout return (Firecrawl Cloud + OSS)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25 (docs fetched live).
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim. **No COSMOS core code was edited.**
**Assignment:** maker-docs sweep (DHx) — every Firecrawl hand COSMOS could fire.

**Already on the mesh (do not re-add as "new"):** MESH_ADDITIONS row 9 named Firecrawl as an UNVERIFIED MCP connector (`directoryUuid: 8bedbd43-e074-4a82-8bc3-53ef89afc032`, url `https://mcp.firecrawl.dev/v2/mcp-search`) with `firecrawl_search`, paper tools, and GitHub/code search. MESH_ADDITIONS_grok row 35 preferred **keyless hosted MCP first**, then self-host if Keith wants crawl/map without a bill. This file inventories **every official hand**, including Cloud-only and paid, so COW can decide. Playwright MCP remains the preferred *deterministic* a11y-tree lane; Firecrawl is the *web-context* lane (search → scrape → structured JSON / papers).

**Filter:** a surface is a HAND only if COSMOS can **do** something with it (scrape, crawl, map, search, extract, parse, dispatch an agent, poll a job, mint a browser session, read remaining credits). Chat-only dashboard chrome is out unless it is the DOM fallback (playground / login).

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks (web-context worker, citation Chapter 4, fenced commit of scraped artifacts, spend-gate). Equal power, cheaper wins. Cloud credits sit **below** self-host and keyless even when the hosted agent is more accurate — credits can run out; a local scrape cannot.

**What Firecrawl is (one sentence):** the web-context API that turns a URL or a query into LLM-ready markdown / HTML / structured JSON (schema or prompt), plus a paper index (~43M abstracts), a developer index, a hosted MCP server, official SDKs, a CLI, and an AGPL-3.0 self-host of the core scrape/crawl/map/search stack. Official docs home: [docs.firecrawl.dev](https://docs.firecrawl.dev). Machine index: [docs.firecrawl.dev/llms.txt](https://docs.firecrawl.dev/llms.txt).

**Repo in play:** `keithbbf-gif/cosmos`. Firecrawl is a **web-context worker**, never a second ledger writer. It runs in an attempt-private workspace (or as an MCP tool the agent brains call); fenced commit still owns the live tree. Artifacts go into the content-addressed store; the ledger holds the pointer.

---

## Official documentation URLs (fetched 2026-08-25)

These are the real vendor pages this scout used. Prefer the machine indexes (`llms.txt`, `pricing.md`) over blog roundups.

| what | URL |
|------|-----|
| **Docs machine index** | https://docs.firecrawl.dev/llms.txt |
| Human docs home | https://docs.firecrawl.dev |
| Introduction | https://docs.firecrawl.dev/introduction |
| **v2 API introduction** | https://docs.firecrawl.dev/api-reference/v2-introduction |
| **v2 OpenAPI** | https://docs.firecrawl.dev/api-reference/v2-openapi.json |
| Errors | https://docs.firecrawl.dev/api-reference/errors |
| **Pricing (authoritative markdown)** | https://www.firecrawl.dev/pricing.md |
| Human pricing | https://www.firecrawl.dev/pricing |
| **Billing / credits** | https://docs.firecrawl.dev/billing |
| **Rate limits (incl. keyless)** | https://docs.firecrawl.dev/rate-limits |
| `/scrape` feature | https://docs.firecrawl.dev/features/scrape |
| `/scrape` API ref | https://docs.firecrawl.dev/api-reference/endpoint/scrape |
| JSON mode (schema) | https://docs.firecrawl.dev/features/llm-extract |
| Batch scrape | https://docs.firecrawl.dev/features/batch-scrape |
| `/crawl` feature | https://docs.firecrawl.dev/features/crawl |
| `/crawl` API ref | https://docs.firecrawl.dev/api-reference/endpoint/crawl-post |
| `/map` feature | https://docs.firecrawl.dev/features/map |
| `/map` API ref | https://docs.firecrawl.dev/api-reference/endpoint/map |
| `/search` feature | https://docs.firecrawl.dev/features/search |
| `/search` API ref | https://docs.firecrawl.dev/api-reference/endpoint/search |
| `/extract` (legacy; successor is `/agent`) | https://docs.firecrawl.dev/features/extract |
| Choosing extractor (`/agent` vs `/extract` vs scrape-JSON) | https://docs.firecrawl.dev/developer-guides/usage-guides/choosing-the-data-extractor |
| `/agent` | https://docs.firecrawl.dev/features/agent |
| `/parse` (PDFs, DOCX, …) | https://docs.firecrawl.dev/features/parse |
| `/parse` API ref | https://docs.firecrawl.dev/api-reference/endpoint/parse |
| Interact / browser sandbox | https://docs.firecrawl.dev/features/interact |
| Research Index (papers) | https://docs.firecrawl.dev/features/research |
| Search papers API | https://docs.firecrawl.dev/api-reference/endpoint/research-search-papers |
| Inspect / read paper API | https://docs.firecrawl.dev/api-reference/endpoint/research-paper |
| Related papers API | https://docs.firecrawl.dev/api-reference/endpoint/research-related-papers |
| Developer Index | https://docs.firecrawl.dev/features/developer |
| Developer search API | https://docs.firecrawl.dev/api-reference/endpoint/developer-search |
| Monitoring | https://docs.firecrawl.dev/features/monitoring |
| Credit usage API | https://docs.firecrawl.dev/api-reference/endpoint/credit-usage |
| **MCP get started** | https://docs.firecrawl.dev/mcp-server |
| MCP keyless (agents) | https://docs.firecrawl.dev/mcp-server/keyless |
| MCP OAuth (humans) | https://docs.firecrawl.dev/mcp-server/oauth |
| MCP connect / modes | https://docs.firecrawl.dev/mcp-server/connect |
| **MCP tools inventory** | https://docs.firecrawl.dev/mcp-server/tools |
| **MCP local / self-host** | https://docs.firecrawl.dev/mcp-server/local |
| MCP clients (Cursor, etc.) | https://docs.firecrawl.dev/mcp-server/clients |
| SDKs overview | https://docs.firecrawl.dev/sdks/overview |
| **Python SDK** | https://docs.firecrawl.dev/sdks/python |
| **Node / JS SDK** | https://docs.firecrawl.dev/sdks/node |
| CLI | https://docs.firecrawl.dev/sdks/cli |
| Open source vs Cloud | https://docs.firecrawl.dev/contributing/open-source-or-cloud |
| **Self-host (Docker Compose)** | https://docs.firecrawl.dev/contributing/self-host |
| GitHub (AGPL-3.0 core) | https://github.com/firecrawl/firecrawl |
| LICENSE (AGPL-3.0) | https://github.com/firecrawl/firecrawl/blob/main/LICENSE |
| Official MCP server repo | https://github.com/firecrawl/firecrawl-mcp-server |
| Python SDK repo | https://github.com/firecrawl/firecrawl-py |
| CLI repo | https://github.com/firecrawl/cli |
| Agent onboarding skill | https://www.firecrawl.dev/agent-onboarding/SKILL.md |
| Playground (DOM fallback) | https://www.firecrawl.dev/playground |
| Dashboard / API keys | https://www.firecrawl.dev/app · https://www.firecrawl.dev/app/api-keys |

v1 still exists (`https://api.firecrawl.dev/v1/scrape`) but v2 is current. New COSMOS work should use **v2**.

---

## Licensing / cost floor

| fact | official source | COSMOS implication |
|------|-----------------|--------------------|
| Core repo is **GNU AGPL v3** (Sideguide Technologies Inc., 2024) | [LICENSE](https://github.com/firecrawl/firecrawl/blob/main/LICENSE) | Self-hosting unmodified on a trusted network is $0. **Modifying** it and exposing it as a network service triggers AGPL §13 (offer corresponding source). Do not fold Firecrawl source into COSMOS core; keep it a **separate process**. |
| Firecrawl Cloud is a **credit subscription**, not pay-per-use | [pricing.md](https://www.firecrawl.dev/pricing.md), [billing](https://docs.firecrawl.dev/billing) | No PAYG. Unused self-serve credits **do not roll over**. 402 when empty unless Smart Upgrade is on. |
| **Free plan:** 1,000 credits / month, $0, no card, 2 concurrent browsers | [pricing.md](https://www.firecrawl.dev/pricing.md) | Signed-up key. Distinct from keyless. |
| **Keyless (no account):** Search, Scrape, Parse on hosted MCP; Search, Scrape, Interact on SDK/CLI/REST; Research + Developer indexes also keyless. Per-IP daily request cap **and** credit cap (exact numbers **not published** on the rate-limits page). 429 when either trips. | [rate-limits § Keyless](https://docs.firecrawl.dev/rate-limits) | First COSMOS probe. Spend-gate still sees "nothing that can run out" until the IP daily cap. |
| Research Index paper endpoints are **free** on every plan (including AI/ML and life sciences) | [pricing.md](https://www.firecrawl.dev/pricing.md) | Chapter 4 citation hunting. Highest-ranked *hosted* hand. |
| Agent: **5 free daily runs**, then dynamic credits. Default `maxCredits` = 2,500. | [agent](https://docs.firecrawl.dev/features/agent), [pricing.md](https://www.firecrawl.dev/pricing.md) | Cap every COSMOS agent job with `maxCredits`. Failed runs: reasoning unbilled, tool-call credits refunded, `creditsUsed: 0`. |
| Hobby **$19/mo** or **$16/mo** yearly (5k credits, 5 concurrent). Standard **$99 / $83** (100k). Growth **$399 / $333** (500k). Scale **$749 / $599** (1M). | [pricing.md](https://www.firecrawl.dev/pricing.md) | Keith buys; COSMOS spend-gates. |
| Credit table (Cloud): scrape/crawl/monitor **1 / page**; map **1 / call** (not per URL); search **2 / 10 results** (round up); JSON format **+4 / page**; PDF parse **1 / PDF page**; Interact **2 / browser-minute** (Playwright code) or **7 / minute** (NL prompt); ZDR **+1 / page**. | [pricing.md](https://www.firecrawl.dev/pricing.md), [billing](https://docs.firecrawl.dev/billing) | JSON schema extraction is 5 credits/page (1+4), not 1. |
| `/extract` billing: **1 credit = 15 tokens** | [extract](https://docs.firecrawl.dev/features/extract) | Prefer scrape-JSON (predictable 5 cr) or `/agent` (5 free/day). |
| x.com / twitter.com scrapes: **1 + 29 = 30 credits** (Grok X Query). JSON on top → 34. | [billing § X](https://docs.firecrawl.dev/billing) | Do not loop X URLs on the free 1k. |
| Failed *Firecrawl* requests are not billed; HTTP 403/404 **from the target** still consume credits (the browser ran). | [billing](https://docs.firecrawl.dev/billing), [pricing FAQ](https://www.firecrawl.dev/pricing.md) | Check `metadata.statusCode` before retry. |
| Crawl pre-flight: default `limit` is **10,000**. If remaining credits < `limit`, **402 even if the site is small**. | [billing](https://docs.firecrawl.dev/billing), [crawl](https://docs.firecrawl.dev/features/crawl) | Always pass an explicit `limit`. |
| Self-host: core scrape/crawl/map/search included; LLM JSON needs BYO OpenAI-compat or Ollama; Agent, Interact, dashboard, enhanced anti-bot, screenshots/actions **not** in the default stack. | [open-source-or-cloud](https://docs.firecrawl.dev/contributing/open-source-or-cloud), [self-host](https://docs.firecrawl.dev/contributing/self-host) | Self-host for bulk markdown. Cloud for Agent / Interact / stealth. |
| Smart Upgrade (since 2026-06-01) auto-steps the credit ladder when balance hits zero. Disable in billing settings. | [billing](https://docs.firecrawl.dev/billing) | **COSMOS default: off** until Keith opts in. Fail-closed 402 is correct. |
| No charge for polling job status. | [billing](https://docs.firecrawl.dev/billing) | Poll `/crawl/{id}` freely. |

**Install (official):**

- Python: `pip install firecrawl-py` → `from firecrawl import Firecrawl`
- Node/JS: `npm install firecrawl` → `import { Firecrawl } from 'firecrawl'`
- CLI: `npm install -g firecrawl-cli` or `npx -y firecrawl-cli@latest init --all --browser`
- Local MCP: `npx -y firecrawl-mcp@3.23.7` (Node 22+)
- Self-host: pin `v2.11.162`, `docker compose up --build -d`, API at `http://localhost:3002`

Older Node examples still show `@mendable/firecrawl-js`. Current official package name is **`firecrawl`**.

---

## Auth (all rows inherit this unless overridden)

Keith owns credentials. Store under `live/config/` (git-ignored). Never hard-code. Never print a key in full (redact to `fc-…last4`).

| method | credential | how | COSMOS use |
|--------|------------|-----|------------|
| **none (keyless Cloud)** | — | Omit `Authorization`. SDK: `Firecrawl()` with no key. MCP: `https://mcp.firecrawl.dev/v2/mcp` with no Bearer. | First probe: search / scrape / parse / interact / papers / developer. Rate-limited per IP. |
| **Free/paid API key** | `fc-…` | Header `Authorization: Bearer fc-…`. Env `FIRECRAWL_API_KEY`. Mint at [app/api-keys](https://www.firecrawl.dev/app/api-keys). | Unlocks crawl, map, batch, extract, agent-beyond-free, higher RPM. |
| **MCP hosted OAuth** | browser session | Client → `https://mcp.firecrawl.dev/v2/mcp-oauth`. Leave Client ID/Secret blank. | Interactive Cursor / Claude Code. Bills the selected team. |
| **MCP hosted unattended** | `fc-…` as Bearer | `https://mcp.firecrawl.dev/v2/mcp` + `Authorization: Bearer <key>`. **Do not put the key in the URL.** | COSMOS MCP-client / CI. Full tool surface. |
| **MCP registry search URL** | none or same key | `https://mcp.firecrawl.dev/v2/mcp-search` (MESH_ADDITIONS row 9; **not** in the current MCP get-started page) | Search-weighted connector already listed. Confirm against `/v2/mcp` before treating as a second server. |
| **Self-host (eval Compose)** | none | `USE_DB_AUTHENTICATION=false`. No `Authorization` header. Trusted network only. | Local `http://localhost:3002`. Do not expose. |
| **Self-host (production)** | your identity layer | Docs: "one env var is not enough"; put TLS + auth at a reverse proxy. | Only after Keith designs it. |
| **CLI login** | browser or `--api-key` | `firecrawl login --browser` or `FIRECRAWL_API_KEY`. `--api-url` for self-host skips Cloud auth. | Queue-runner CLI jobs. |
| **WorkOS ID-JAG (agent mint)** | platform-minted | [auth.md](https://www.firecrawl.dev/auth.md) | Only if a COSMOS client can mint ID-JAG. Otherwise the SKILL.md keyless/signup path. |

**Keyless vs Free plan (do not conflate):**

| | Keyless | Free plan (signed-up `fc-` key) |
|--|---------|----------------------------------|
| Account | none | yes, no card |
| MCP tools | `firecrawl_search`, `firecrawl_scrape`, `firecrawl_parse` | full surface (plan-gated) |
| SDK/REST | `scrape`, `search`, `interact` | all methods |
| Crawl / map / batch / extract | **no** | yes, burns the 1,000 credits |
| Cap | per-IP daily requests **and** credits (numbers unpublished) | 1,000 credits / month, 2 concurrent, 10 `/scrape` RPM |
| Papers / developer search | yes | yes |

---

## How COSMOS reaches Firecrawl (one pattern)

Core stays sole ledger writer. Firecrawl is a **web-context worker**. Scraped markdown / JSON is an artifact; hash it, pointer in the ledger.

| Lane | Mechanism | When |
|------|-----------|------|
| **A. Hosted MCP keyless (preferred first probe)** | MCP client → `https://mcp.firecrawl.dev/v2/mcp` (no auth). Tools: search, scrape, parse. | Agent brains (Cursor / G46 / COW) need a page or a query **now**, no key. |
| **B. REST v2 keyless / Python SDK** | `POST https://api.firecrawl.dev/v2/scrape` (and `/search`) with no Bearer, or `Firecrawl().scrape(...)`. | Queue job that must return markdown/JSON without MCP. |
| **C. Research Index HTTP (keyless, $0)** | `GET https://api.firecrawl.dev/v2/search/research/papers?query=…` then inspect/read/similar. | Chapter 4 DOI / citation / related-work. |
| **D. Free-plan key in `live/config/`** | `Authorization: Bearer $FIRECRAWL_API_KEY`. SDK `Firecrawl(api_key=…)`. | Crawl, map, batch, JSON-at-volume, once Keith mints a key. Spend-gate via `/v2/team/credit-usage`. |
| **E. Self-host Docker** | `POST http://localhost:3002/v2/scrape`. MCP: `FIRECRAWL_API_URL=http://localhost:3002 npx firecrawl-mcp`. CLI: `firecrawl --api-url http://localhost:3002`. | Bulk site → markdown with **no Cloud credit**. AGPL process boundary. |
| **F. Hosted MCP full (OAuth or Bearer)** | `/v2/mcp-oauth` or `/v2/mcp` + Bearer. | Need crawl / map / agent / research_* / developer / monitor from an MCP host. |
| **G. DOM playground / dashboard** | https://www.firecrawl.dev/playground · `/app` | AUTH_REQUIRED, first signup, or when the API depends on something that can run out. Canon: DOM is the floor. |

**Default COSMOS flags for unattended Cloud jobs:**

```
FIRECRAWL_API_KEY from live/config/ (git-ignored)
explicit crawl limit  (never the default 10_000)
maxCredits on every /agent call
GET /v2/team/credit-usage before a pour  → 402 is success (fail-closed)
Smart Upgrade OFF
FIRECRAWL_NO_TELEMETRY=1 on CLI
```

Never let Firecrawl write the live tree. Never put `fc-` in a tracked MCP JSON URL.

---

## Output formats (what a scrape/parse can return)

Formats are requested in `formats: [...]` on `/scrape`, `/crawl` (`scrapeOptions`), `/search` (`scrapeOptions`), and `/parse`. Multiple formats in one call.

| format | what it DOES | extra Cloud credits | notes |
|--------|--------------|---------------------|-------|
| `markdown` | Clean LLM-ready page text (default) | 0 (base 1/page) | Primary COSMOS ingest. |
| `html` | Cleaned HTML | 0 | |
| `rawHtml` | Unmodified HTML | 0 | |
| `summary` | Page summary | 0 | |
| `links` | Outbound URLs | 0 | |
| `images` | Image URLs | 0 | |
| `screenshot` | PNG (fullPage / quality / viewport). URLs expire **24h**. | 0 (Cloud). **Not** in default self-host. | Incompatible with ZDR. |
| **`json`** | Structured object via **JSON Schema** and/or **prompt**. Pydantic / Zod in SDKs. Prompt-only → model chooses shape. | **+4 / page** (5 total) | This is the "structured JSON via schema" hand. Sync on `/scrape`. |
| `question` | NL question → `answer` field | +4 / page | Also on `/search` via scrapeOptions. |
| `highlights` | Query-relevant source passages | +4 / page | Search has highlights **on by default** (snippets). |
| `branding` | Colors, fonts, spacing, components | (not separately itemized; treat as scrape) | Design-system extract. |
| `product` | Deterministic product fields (title, price, availability, variants). **No LLM, no schema.** | base scrape (cheaper than json) | Self-host needs `PRODUCT_EXTRACTION_SERVICE_URL`. |
| `audio` / `video` | Signed GCS URL (YouTube etc.), expires **1h** | +4 / page (5 total) | Cloud-only service. |
| `changeTracking` | Diff vs prior scrape | bypasses cache | |
| Parse extras (`pages`, `blocks`, `pageMarkers`) | Per-page markdown, layout bboxes, `<!-- page N -->` | **no extra** on top of 1 cr / PDF page | Grounding: `markdownSpan` → bbox. Max file **50 MB**. |

`/extract` and `/agent` return **one structured `data` object** (schema or prompt), not a formats array.

---

## Ranking table

| # | name | kind | HANDS (what it DOES) | auth | cost | power | how COSMOS reaches it | source |
|---|------|------|----------------------|------|------|-------|------------------------|--------|
| 1 | **Self-host OSS API** (`POST /v2/scrape` · `/crawl` · `/map` · `/search`) | local HTTP, AGPL-3.0 | Recursively crawl / scrape / map / search **on Keith's hardware**. Default stack includes Fetch + Playwright. Eval Compose: pin `v2.11.162`, API `http://localhost:3002`, `USE_DB_AUTHENTICATION=false`. Smoke: `POST /v2/scrape` `{url, formats:["markdown"]}` → `success: true`. | none on eval; TLS+auth before any untrusted net | **free** (electricity + disk). LLM-JSON needs BYO Ollama/OpenAI-compat. | **highest** | Docker Compose worker. Point SDK/CLI/MCP via `FIRECRAWL_API_URL` / `--api-url`. Separate process — do not vendor the AGPL tree into `cosmos/`. | [self-host](https://docs.firecrawl.dev/contributing/self-host), [OSS vs Cloud](https://docs.firecrawl.dev/contributing/open-source-or-cloud), [LICENSE](https://github.com/firecrawl/firecrawl/blob/main/LICENSE) |
| 2 | **Research Index — search papers** | REST `GET /v2/search/research/papers` | Search ~**43M** abstracts (PubMed, bioRxiv, medRxiv, arXiv) → ranked `paperId` / `primaryId` (`pmid:` `pmcid:` `doi:` `arxiv:`), title, full abstract, score. Filters: authors, categories, from/to dates. | **none** (keyless) or Bearer for higher RPM | **free** (every plan, every category) | **highest** | HTTP from a queue job or MCP `firecrawl_research_*`. This is Chapter 4's citation workflow as an API. | [research](https://docs.firecrawl.dev/features/research), [API](https://docs.firecrawl.dev/api-reference/endpoint/research-search-papers), [pricing.md](https://www.firecrawl.dev/pricing.md) |
| 3 | **Research Index — inspect / read passages** | REST `GET /v2/search/research/papers/{id}` | Canonical metadata, or add `query` + `k` to pull **full-text passages** that answer a question (verify method/dataset before citing). | none or Bearer | **free** | **highest** | Same as #2. `read_paper` in MCP / CLI `firecrawl research read-paper`. | [research](https://docs.firecrawl.dev/features/research), [API](https://docs.firecrawl.dev/api-reference/endpoint/research-paper) |
| 4 | **Research Index — related papers** | REST `GET /v2/search/research/papers/{id}/similar` | Expand a seed via `mode=similar` (co-citation / bibliographic coupling), `citers`, or `references`, ranked against an `intent`. | none or Bearer | **free** | **highest** | Citation-graph walk without Semantic Scholar/Crossref glue. | [research](https://docs.firecrawl.dev/features/research), [API](https://docs.firecrawl.dev/api-reference/endpoint/research-related-papers) |
| 5 | **Hosted MCP keyless** | MCP HTTP | Hosted server exposes **exactly** `firecrawl_search`, `firecrawl_scrape`, `firecrawl_parse` with no account. | none | **free**, per-IP daily caps (unpublished numbers), 429 | **highest** | COSMOS / Cursor MCP config `"url": "https://mcp.firecrawl.dev/v2/mcp"`. First live probe. | [MCP](https://docs.firecrawl.dev/mcp-server), [tools](https://docs.firecrawl.dev/mcp-server/tools), [rate-limits](https://docs.firecrawl.dev/rate-limits) |
| 6 | **Keyless REST `/v2/scrape`** | REST | One URL → markdown / html / json / … JS-rendered, proxies, PDFs-by-URL. No key. | none | **free** keyless cap | **highest** | `curl POST https://api.firecrawl.dev/v2/scrape` or `Firecrawl().scrape(url, formats=["markdown"])`. | [scrape](https://docs.firecrawl.dev/features/scrape), [API](https://docs.firecrawl.dev/api-reference/endpoint/scrape) |
| 7 | **Keyless REST `/v2/search`** | REST | Web / news / images search. Optional `scrapeOptions` to pull full markdown of hits. Categories: `github`, `research` (**website filter**, not the paper index), `pdf`, `developer`. | none | **free** keyless; signed-up: **2 credits / 10 results** (+ scrape costs if scraping) | **highest** | `Firecrawl().search(query, limit=n)`. Prefer two-step (search then scrape chosen URLs) when filtering. | [search](https://docs.firecrawl.dev/features/search), [API](https://docs.firecrawl.dev/api-reference/endpoint/search) |
| 8 | **Keyless Interact (SDK / CLI / REST)** | browser sandbox | Stateful session after a scrape: NL prompt **or** Playwright / agent-browser code. MCP keyless does **not** include Interact. | none on SDK/CLI/REST keyless | **free** keyless cap; signed-up: **2 cr / browser-min** (code) or **7** (prompt), 1-minute minimum | **high** | `firecrawl.interact(scrape_id, …)` after a scrape. Close with `stop_interaction`. Complements Playwright MCP (vendor-plural DOM). | [interact](https://docs.firecrawl.dev/features/interact), [rate-limits](https://docs.firecrawl.dev/rate-limits) |
| 9 | **Free-plan API key (1,000 credits / month)** | Cloud account | Unlocks **crawl, map, batch, extract, agent-beyond-5**, higher RPM (10 `/scrape` RPM, 2 concurrent). No card. | `fc-` Bearer | **$0**. Credits reset monthly, **no rollover**. | **highest** (Cloud) | Keith mints at `/app/api-keys`; store `live/config/firecrawl_api_key.txt`. Probe `GET /v2/team/credit-usage` before claiming remaining. | [pricing.md](https://www.firecrawl.dev/pricing.md), [rate-limits](https://docs.firecrawl.dev/rate-limits) |
| 10 | **`/agent` 5 free daily runs** | REST `POST /v2/agent` | Autonomous web research. **No URL required** — prompt (+ optional JSON schema). Models: `spark-1-pro` (default), `spark-1-mini` (60% cheaper), `spark-2` (cheapest/fastest). Official successor to `/extract`. | `fc-` (not keyless) | **5 runs/day free**, then dynamic credits (often "a few hundred"). `maxCredits` default 2500. | **high** | `app.agent(prompt=…, schema=…, max_credits=100)`. Poll `GET /v2/agent/{id}`. Always set `maxCredits`. | [agent](https://docs.firecrawl.dev/features/agent), [chooser](https://docs.firecrawl.dev/developer-guides/usage-guides/choosing-the-data-extractor) |
| 11 | **Developer Index** | REST `GET/POST /v2/search/developer` | Issues, merged PRs, READMEs, curated docs → ranked hits with markdown **passages**. Filters: types, repos, sources, language, stars, `skills=only`. | none or Bearer | **2 credits / 10 results** (keyless allowed). Python/Node SDKs have **no dedicated method** — HTTP / CLI / MCP. | **high** | `GET /v2/search/developer?query=…` or MCP `firecrawl_developer_search`. Coding-agent lookup without general web junk. | [developer](https://docs.firecrawl.dev/features/developer), [API](https://docs.firecrawl.dev/api-reference/endpoint/developer-search) |
| 12 | **Python SDK `firecrawl-py`** | SDK | Idiomatic wrapper: `scrape` `crawl` `map` `search` `extract` `agent` `parse` `batch_scrape` `browser` + waiters, pagination, `AsyncFirecrawl`. Snake-cases response fields. Keyless: only scrape/search/interact. | `FIRECRAWL_API_KEY` or none | **free** wrapper; Cloud credits as used. Point `api_url=` at self-host. | **highest** (shape) | Preferred COSMOS in-process client for queue jobs. `pip install firecrawl-py`. | [Python SDK](https://docs.firecrawl.dev/sdks/python), [repo](https://github.com/firecrawl/firecrawl-py) |
| 13 | **Node / JS SDK `firecrawl`** | SDK | Same surface for Node/TS. Waiters, watcher (WS + HTTP fallback), `browser()` CDP URL. | `apiKey` or none | **free** wrapper | **high** | KDash-adjacent / Node workers. `npm install firecrawl`. | [Node SDK](https://docs.firecrawl.dev/sdks/node) |
| 14 | **Official CLI `firecrawl-cli`** | CLI | `firecrawl <url>` scrape; `search` `map` `crawl` `interact` `agent` `developer` `monitor` `credit-usage` `login`. `--schema` for JSON extract. `--api-url` for self-host. | login / env / keyless fallback | **free** tool | **high** | Queue argv. `FIRECRAWL_NO_TELEMETRY=1`. Never a `.bat`. | [CLI](https://docs.firecrawl.dev/sdks/cli) |
| 15 | **Local MCP server `firecrawl-mcp`** | MCP stdio / Streamable HTTP | Same tool surface as hosted, launched as `npx -y firecrawl-mcp@3.23.7`. `HTTP_STREAMABLE_SERVER=true` → `http://localhost:3000/mcp`. | `FIRECRAWL_API_KEY` and/or `FIRECRAWL_API_URL` | **free** process; backend bills as Cloud or $0 self-host | **high** | Cursor / COSMOS MCP when the host cannot reach the remote URL, **or** when talking to localhost:3002. Direct local-file `firecrawl_parse` **requires** self-host `FIRECRAWL_API_URL`. | [local MCP](https://docs.firecrawl.dev/mcp-server/local) |
| 16 | **Hosted MCP full (OAuth or Bearer)** | MCP HTTP | Full tool list (plan-gated): scrape (incl. JSON schema), map, search, parse, crawl + status, agent + status, interact + stop, `firecrawl_research_*`, `firecrawl_developer_search`, `firecrawl_monitor_*`, optional feedback tools. **Extract MCP tool is deprecated** — use scrape-JSON or agent. | OAuth at `/v2/mcp-oauth` **or** Bearer at `/v2/mcp` | Cloud credits | **high** | Production MCP once a key exists. Unattended: Bearer header, key **not** in the URL. | [connect](https://docs.firecrawl.dev/mcp-server/connect), [tools](https://docs.firecrawl.dev/mcp-server/tools) |
| 17 | **`POST /v2/scrape` (authenticated)** | REST | Full scrape: actions (wait/click/write/press/scroll/screenshot/JS/PDF), location, proxy, `maxAge` cache (default **2 days**), `redactPII`, ZDR, enhanced mode. Cached results still cost 1 credit (speed, not savings). | Bearer | **1 cr / page** + modifiers | **high** | Core REST hand. Default COSMOS format: `markdown`. Force fresh: `maxAge: 0`. | [scrape](https://docs.firecrawl.dev/features/scrape), [API](https://docs.firecrawl.dev/api-reference/endpoint/scrape) |
| 18 | **`/scrape` JSON schema mode** | REST format | LLM extracts a **JSON Schema** (or prompt-only) from one known URL. Sync. Combine with markdown in the same call. | none (keyless) or Bearer | **5 cr / page** (1+4) | **high** | Cheapest *structured* path when the URL is known. Pydantic `model_json_schema()` / Zod. Prefer `product` format for product pages (no LLM). | [JSON mode](https://docs.firecrawl.dev/features/llm-extract), [chooser](https://docs.firecrawl.dev/developer-guides/usage-guides/choosing-the-data-extractor) |
| 19 | **`POST /v2/map`** | REST | Fast sitemap + SERP + cache URL inventory. Optional `search` ranks links. `sitemap`: include/skip/only. **1 credit per call**, even at `limit` 100,000. May miss pages — crawl is the thorough path. | Bearer (not keyless) | **1 cr / call** | **high** | Site reconnaissance before a bounded crawl. `firecrawl.map(url, limit=50)`. | [map](https://docs.firecrawl.dev/features/map), [API](https://docs.firecrawl.dev/api-reference/endpoint/map) |
| 20 | **`POST /v2/crawl`** | REST async | Recursive scrape from a start URL. Job ID → poll `GET /v2/crawl/{id}` (or webhook / watcher). Path regex, depth, subdomains, `scrapeOptions` (incl. JSON schema on every page). Results expire **24h** on the API. | Bearer | **1 cr / page** (+ JSON/PDF). Pre-flight 402 if credits < `limit` (default 10k). | **high** | `firecrawl.crawl(url, limit=100, scrape_options={formats:["markdown"]})`. Always set `limit`. Errors endpoint for robots/timeouts. | [crawl](https://docs.firecrawl.dev/features/crawl), [API](https://docs.firecrawl.dev/api-reference/endpoint/crawl-post) |
| 21 | **`POST /v2/batch/scrape`** | REST async | Scrape a **known URL list** in parallel. Same scrape options. Poll / cancel / errors endpoints. Shares crawl RPM. | Bearer | **1 cr / successful page** (+ modifiers). Billed as pages complete, not at submit. | **high** | Search-then-scrape, or a map → batch. SDK `batch_scrape(urls, formats=["markdown"])`. | [batch](https://docs.firecrawl.dev/features/batch-scrape) |
| 22 | **`POST /v2/parse`** | REST multipart | Upload a local file (PDF/DOCX/XLSX/PPTX/ODT/EPUB/CSV/HTML, max 50 MB) → markdown, per-page, layout blocks, or JSON schema. Public URL documents use `/scrape` instead (auto-detect). | MCP keyless includes parse; REST typically keyed. Hosted MCP parse uses a **signed upload handoff** (two calls). | **1 cr / PDF page**. `pages`/`blocks`/`pageMarkers` add $0. JSON format +4. | **high** | Dissertation PDFs / exhibit bundles. Self-host MCP can read `filePath` directly. | [parse](https://docs.firecrawl.dev/features/parse), [API](https://docs.firecrawl.dev/api-reference/endpoint/parse) |
| 23 | **`POST /v2/extract` (legacy)** | REST async | Multi-URL / wildcard-domain LLM extract. Prompt and/or schema. Optional `enableWebSearch`. Job ID, 24h results. Official docs: **use `/agent` instead**. FIRE-1 agent still attachable via `"agent": {"model": "FIRE-1"}`. | Bearer (not keyless) | **token-based**, 1 credit = 15 tokens | **med** | Only if an incumbent integration already calls extract. New work → scrape-JSON or agent. | [extract](https://docs.firecrawl.dev/features/extract) |
| 24 | **`POST /v2/agent` (paid beyond free)** | REST async | Same as #10 after the 5 daily frees. Optional `urls` to focus. Cooperative cancel; in-flight steps can still accrue credits. | Bearer | dynamic; set `maxCredits` | **med-high** | Overflow research. Prefer scrape-JSON when the URL is known (~5 cr vs hundreds). | [agent](https://docs.firecrawl.dev/features/agent) |
| 25 | **Cloud browser / Interact (paid)** | REST `/v2/browser` family + scrape-bound interact | Launch a Cloud browser: `cdp_url` (`wss://cdp-proxy.firecrawl.dev/…`), live view, profiles (cookies), execute Python/Node/bash. Connect Playwright `connect_over_cdp`. | Bearer | 2 or 7 cr / minute | **med** | When Playwright-local is blocked and stealth/geo is needed. **Must delete the session** — same class of leak as Browser-Use Cloud CDP. Cloud-only (not default self-host). | [Python browser](https://docs.firecrawl.dev/sdks/python), [interact](https://docs.firecrawl.dev/features/interact) |
| 26 | **Monitor (recurring scrape/crawl + diff)** | REST `/v2/monitor*` | Cron / NL schedule, goal-judged "meaningful change", webhook or email. Page, website, or web-scale. | Bearer | **1 cr / page / check** | **med** | Watch a competitor docs page or a regulation URL. `firecrawl_monitor_*` on full MCP. Delete is destructive. | [monitoring](https://docs.firecrawl.dev/features/monitoring) |
| 27 | **`GET /v2/team/credit-usage`** | REST | Remaining credits, plan credits, billing window. Historical sibling exists. | Bearer | **0** | **high** (gate) | COSMOS spend-gate probe. Bind any "we have headroom" claim to this JSON. CLI: `firecrawl credit-usage`. | [credit-usage](https://docs.firecrawl.dev/api-reference/endpoint/credit-usage) |
| 28 | **Webhooks (crawl / batch / monitor)** | HTTP callback | `crawl.started/page/completed/failed`, batch equivalents. HMAC `X-Firecrawl-Signature`. | webhook secret in dashboard Advanced | 0 extra | **med** | Return-watcher: process pages as they finish instead of blocking the queue. Verify signature. | [webhooks](https://docs.firecrawl.dev/webhooks/overview) |
| 29 | **Ask / docs-search (debug)** | REST `/v2/support/ask` | Agentic support over Firecrawl jobs + public docs corpus. | Bearer | (support surface; not a scrape) | **low** | Debug a 402/429/empty extract. Not a general web hand. | [ask](https://docs.firecrawl.dev/features/ask) |
| 30 | **Paid Cloud plans (Hobby → Scale)** | subscription | More credits + RPM + concurrent browsers. Hobby 5k / 5 conc / 100 scrape RPM. Standard 100k. Growth 500k. Scale 1M. Enterprise: ZDR, SSO, ignore-robots, custom. | Stripe (Keith) | **$19–$749/mo** (yearly discount on pricing.md) | **low until needed** | Only after free 1k + self-host are proven insufficient. Smart Upgrade OFF. | [pricing.md](https://www.firecrawl.dev/pricing.md), [rate-limits](https://docs.firecrawl.dev/rate-limits) |
| 31 | **Playground + dashboard (DOM)** | browser | Interactive scrape/search/crawl/agent; mint keys; billing; logs after 24h API expiry. | account cookie | $0 to look | **floor** | Canon DOM path for signup / AUTH_REQUIRED / when the key lapses. | [playground](https://www.firecrawl.dev/playground), [dashboard](https://docs.firecrawl.dev/dashboard) |

---

## MCP tool inventory (official, 2026-08-25)

From [MCP tools](https://docs.firecrawl.dev/mcp-server/tools). Client receives live input schemas on connect.

| job | tool | keyless hosted? |
|-----|------|-----------------|
| Read one page / JSON schema extract | `firecrawl_scrape` (JSON format on the scrape tool) | yes |
| Discover site URLs | `firecrawl_map` | no |
| Search the web | `firecrawl_search` | yes |
| Parse a file | `firecrawl_parse` | yes (upload handoff on hosted) |
| Crawl a site | `firecrawl_crawl` + `firecrawl_check_crawl_status` | no |
| Autonomous research | `firecrawl_agent` + `firecrawl_agent_status` | no |
| Live page | `firecrawl_interact` + `firecrawl_interact_stop` | no (SDK keyless yes; MCP keyless no) |
| Papers | `firecrawl_research_*` | full MCP (plan); papers REST is keyless |
| Coding sources | `firecrawl_developer_search` | full MCP; REST keyless |
| Recurring diffs | `firecrawl_monitor_*` | no |
| Feedback | `firecrawl_search_feedback`, `firecrawl_feedback` | optional; disable with `FIRECRAWL_NO_*_FEEDBACK=1` |

Former **Extract MCP tool is gone**. MESH_ADDITIONS names `firecrawl_research_search_papers` / `read_paper` / `related_papers` / `firecrawl_research_search_github` — those map onto `firecrawl_research_*` and `firecrawl_developer_search` / search category `github` on the current tool surface.

---

## REST v2 endpoint map (Cloud base `https://api.firecrawl.dev`)

Auth unless noted: `Authorization: Bearer fc-…`. Keyless allowed where marked.

| method | path | does | keyless? | credits |
|--------|------|------|----------|---------|
| POST | `/v2/scrape` | one URL → formats | yes | 1/page + modifiers |
| POST | `/v2/batch/scrape` | many known URLs | no | 1/page |
| GET | `/v2/batch/scrape/{id}` | batch status | no | 0 |
| DELETE | `/v2/batch/scrape/{id}` | cancel batch | no | 0 |
| GET | `/v2/batch/scrape/{id}/errors` | batch errors | no | 0 |
| POST | `/v2/crawl` | start crawl | no | 1/page as pages finish |
| GET | `/v2/crawl/{id}` | crawl status | no | 0 |
| DELETE | `/v2/crawl/{id}` | cancel | no | 0 |
| GET | `/v2/crawl/{id}/errors` | crawl errors | no | 0 |
| GET | `/v2/crawl/active` | active crawls | no | 0 |
| POST | `/v2/map` | URL inventory | no | 1/call |
| POST | `/v2/search` | web/news/images | yes | 2/10 results + scrape |
| GET/POST | `/v2/search/developer` | developer index | yes | 2/10 |
| GET | `/v2/search/research/papers` | paper search | yes | **free** |
| GET | `/v2/search/research/papers/{id}` | inspect / read | yes | **free** |
| GET | `/v2/search/research/papers/{id}/similar` | related | yes | **free** |
| POST | `/v2/extract` | legacy multi-URL LLM extract | no | tokens (1 cr = 15 tok) |
| GET | `/v2/extract/{id}` | extract status | no | 0 |
| POST | `/v2/agent` | autonomous gather | no | 5/day free then dynamic |
| GET | `/v2/agent/{id}` | agent status | no | 0 |
| POST | `/v2/parse` | upload file | (MCP keyless yes) | 1/PDF page |
| POST | `/v2/browser` (create) + execute/list/delete | Cloud browser | no | interact rates |
| POST | `/v2/scrape/{id}/interact` | scrape-bound interact | SDK keyless | interact rates |
| GET | `/v2/team/credit-usage` | remaining credits | no | 0 |
| POST | `/v2/monitor` family | recurring checks | no | 1/page/check |

Self-host base: `http://localhost:3002` (same `/v2/scrape` shape). Health heartbeat `GET /v0/health/readiness` is **not** an end-to-end test — the docs require a real scrape.

---

## Cloud vs self-host (operating model)

| decision | Open source (self-host) | Firecrawl Cloud |
|----------|-------------------------|-----------------|
| Core scrape, crawl, map, search | included | included + managed |
| Fetch + Playwright | default stack | managed |
| LLM JSON / schema | BYO OpenAI-compat or Ollama | managed |
| Screenshots, page actions, enhanced anti-bot | **not** in default stack (needs Fire-engine, separate) | managed where the product supports it |
| Agent, Interact, dashboard, enterprise ZDR/SSO | **not** in default stack | Cloud-only |
| Auth | you (eval Compose = **off**) | `fc-` / OAuth |
| Cost | infra | plan credits |
| License | **AGPL-3.0** | commercial ToS |

Official recommendation: Cloud unless source/infra control is worth the ops. For COSMOS: **self-host for bulk markdown that must not depend on credits**; **keyless Cloud for papers + first search/scrape**; **free 1k key for map/crawl**.

---

## Rate limits (Cloud, requests per minute)

From [rate-limits](https://docs.firecrawl.dev/rate-limits). Concurrent **browsers** (not the marketing "concurrent requests" on the HTML pricing page):

| plan | browsers | `/scrape` | `/map` | `/crawl` | `/search` | `/agent` | `/interact` |
|------|----------|-----------|--------|----------|-----------|----------|-------------|
| Free | 2 | 10 | 10 | 2 | 10 | 2 | 2 |
| Hobby | 5 | 100 | 100 | 20 | 100 | 20 | 20 |
| Standard | 50 | 500 | 500 | 100 | 500 | 100 | 100 |
| Growth | 100 | 5000 | 5000 | 1000 | 5000 | 1000 | 1000 |
| Scale | 150+ | 10000 | 10000 | 2000 | 10000 | 2000 | 1500 |

Extract RPM shares `/agent`. Batch scrape RPM shares `/crawl`. Exceed → **429**. Empty credits → **402**.

**Discrepancy (do not flatten):** HTML [pricing](https://www.firecrawl.dev/pricing) lists Standard **25** / Growth **50** / Scale **100** "concurrent requests". [rate-limits.md](https://docs.firecrawl.dev/rate-limits) and [billing.md](https://docs.firecrawl.dev/billing) list **50 / 100 / 150 concurrent browsers**. Operational authority is the rate-limits page; probe live `firecrawl --status` / queue-status before a pour.

---

## COSMOS mapping (what to fire first)

1. **Papers (Chapter 4)** — Research Index, $0, keyless. Replaces "prompt SGH to hunt a DOI."
2. **Keyless MCP search+scrape** — agent brains, no key, no bats.
3. **Self-host scrape/crawl** — bulk site → markdown when Cloud credits would lapse. AGPL process boundary.
4. **Free 1k `fc-` key** — map + bounded crawl (`limit: 100`) + JSON schema on known URLs.
5. **Agent** — only when URLs are unknown; always `maxCredits`.
6. **Spend-gate** — `GET /v2/team/credit-usage`; Smart Upgrade off; 402 is correct.

Do **not** treat `/search` `categories: ["research"]` as the paper index — that is a **website filter** (arxiv.org, nature.com, … snippets). Papers are `/v2/search/research/papers`.

---

## What is not a HAND (out of table on purpose)

- Marketing blog posts, testimonials, Launch Week banners.
- Partner Integration API (approved resellers minting keys for *their* users).
- Enterprise IP/key restrictions, SIEM, threat-protection policy — real, but Keith-gated Cloud add-ons, not a first scout fire.
- Putting `fc-` in `https://mcp.firecrawl.dev/{KEY}/v2/mcp` (old blog pattern; current docs forbid key-in-URL).
- Claiming MESH_ADDITIONS row 9 is "connected" — registry entry confirmed, **not yet connected**.

---

## Unverified against a live artifact (scout honesty)

This return is documentation-bound. Not yet proven on this machine:

- A keyless `POST /v2/scrape` from the COSMOS host (IP daily cap unknown until 429).
- A Research Index query returning a real `pmid:` / `arxiv:` record.
- Presence of `https://mcp.firecrawl.dev/v2/mcp-search` as a distinct server vs `/v2/mcp` (registry vs current docs).
- Self-host Compose on Windows / Docker Desktop (docs pin Linux-style `docker compose`).
- Remaining Free-plan credits (no key minted in this scout).

Bind any later "Firecrawl works" claim to the JSON the API actually returned (`success`, `data.markdown` / `data.json`, `remainingCredits`, MCP tool list).

---

## Host bind (additive, 2026-08-27 s6) — D3 satellite `--probe`

RAN (no kernel/ledger/sched/service edit; `--probe` does **not** overwrite `live/config/firecrawl_rail_probe.json`):

`py -3.14 cosmos\cosmos_firecrawl_rail.py --root V:\A\Ai\COSMOS\live --probe`

Live emit this process (a value only this tree + the keyless papers endpoint can produce today):

- `ok=true`
- `link_id=firecrawl-web`
- **`primaryId=pmid:11089135`**
- `http=200`
- `date=Thu, 27 Aug 2026 06:55:06 GMT`
- `detail=firecrawl-web papers primaryId=pmid:11089135 http=200 success=True date=Thu, 27 Aug 2026 06:55:06 GMT`

Prior `--gate` (2026-08-26T10:53:54-05): `primaryId=arxiv:physics/0103087` (different record; keyless papers live). Direct GET with `limit` still HTTP **400** `unrecognized_keys` — do not send `limit`. U9 remaining cap unpublished; this call was **200 not 429**. No `fc-` in `live/config/`. Kernel attach BACKLOG. Core `:8770` **DOWN** this pass.
