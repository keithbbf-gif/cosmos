# MESH ADDITIONS — running, dynamically ranked (free first)

**Consumer:** COSMOS / COW. Live discovery backlog. Agents APPEND candidates; COW verifies.
Ranked by **increase in MESH power**, **free options first**. Every entry needs HANDS
(actionable: CLI / MCP / API / DOM / connector / skill / extension / plugin / tool) — not
chat-only. Started 2026-08-25. **This pass:** Cowork orchestration subagent, 2026-08-25 —
MCP registry sweep (8 keyword sets) + web research. Companion candidate list:
`docs/MESH_ADDITIONS_grok.md`. Maker-hands: `docs/research/*_HANDS.md`.

**Stage-2 ARCH (2026-08-25T23:09-05, G46 `motif_meshadditions_s2`):** decision rubric +
wiring design → `docs/arch/meshadditions_ARCH.md`. Git `56fa423`. Core not edited.
`rc=0` is not complete.

**Stage-3 (2026-08-26, `docs/critique/meshadditions_STAGE3.md`):** CONVERGE with
locks. Same-family as the ARCH (gem/oa still owed). Satellite `--gate` shape, not
Kernel compose. HIGH/MED applied additively in slice-1 (no stage-5 file existed).

**Stage-6 satellite `--gate` (2026-08-26T10:53-05, G46 `motif_meshadditions_s6`):**
slice-1 built and run. Kernel/ledger/sched/service **not** edited.
`kernel_attached=false` is a PASS predicate. Proof is the probe JSON, not `rc=0`.

| rail | proof artifact | live-tree / vendor value |
|---|---|---|
| **firecrawl-web** | `live/config/firecrawl_rail_probe.json` | `gate=PASS` `gated_at=2026-08-26T10:53:54-05:00` `primaryId=arxiv:physics/0103087` `http=200` `success=true` `title=Thoughtful comments on 'Bessel beams and signal propagation'` `tree_id=KMesh-COSMOS-live` `route=core->papers` `attach_refused=true` `kernel_attached=false` |
| **playwright-dom** | `live/config/playwright_rail_probe.json` | `gate=PASS` `gated_at=2026-08-26T10:53:58-05:00` `tools/list n=24` including `browser_navigate`+`browser_snapshot` (`browser_run_code_unsafe` listed, client-denied) `server=Playwright version=1.63.0-alpha-2026-08-05` snapshot a11y: `paragraph [ref=e3]: tree_id=KMesh-COSMOS-live` via `http://127.0.0.1:59571/` (not `file://`) `route=core->interact` `attach_refused=true` `kernel_attached=false` |

Code (additive satellites, cursor-rail shape): `cosmos/cosmos_mcp_client.py`,
`cosmos/cosmos_playwright_rail.py`, `cosmos/cosmos_firecrawl_rail.py`. Ollama /
Groq remain HOLD. Production Kernel still does not attach rails (BACKLOG).

### Hands verification (this host, 2026-08-25T23:09-05)

Quoted artifacts, not intentions. Full rubric and slice plan in the ARCH.

| candidate | live packet | class |
|---|---|---|
| **Playwright MCP** | Stage-6 `--gate` spawned 0.0.79, `tools/list` 24 names, `browser_snapshot` of loopback page contains `tree_id=KMesh-COSMOS-live`. Probe JSON `gate=PASS`. | **WIRED** satellite (`playwright-dom`) |
| **Firecrawl keyless scrape** | POST `/v2/scrape` HTTP 200 `success:true` markdown of docs.firecrawl.dev | **WIRE** slice 1 (`firecrawl-web`) |
| **Firecrawl keyless search** | POST `/v2/search` HTTP 200 first hit `https://github.com/microsoft/playwright-mcp` | **WIRE** |
| **Firecrawl papers** | Stage-6 `--gate` GET papers HTTP 200 `primaryId=arxiv:physics/0103087` (do **not** send `limit` — 400 `unrecognized_keys`). Probe JSON `gate=PASS`. | **WIRED** satellite (`firecrawl-web`, Chapter 4) |
| **Groq** | GET `api.groq.com/openai/v1/models` HTTP 401 `invalid_api_key` — endpoint live, no `gsk_` in `live/config/` | **HOLD** Keith key; default model `openai/gpt-oss-20b` (not Llama-3-70B) |
| **Ollama** | GET `127.0.0.1:11434/api/version` WinError 10061; binary/paths missing. GPU `RTX 3070 8192 MiB` via nvidia-smi | **HOLD** Keith install; 8 GiB → 8B-class models, not 30B-coder |
| **browser-use / aider / uvx / groq+firecrawl Python pkgs** | imports NO; `uvx` ABSENT; `aider` ABSENT | **HOLD** slice 3 |
| **n8n / Zapier / OpenRouter rotating `free` / Mixtral** | — | **REJECT** (see ARCH §4.5) |

PowerShell `npm.ps1` is execution-policy blocked; spawn via `cmd /c`. No Groq / Firecrawl
paid / Ollama / Anthropic keys in `live/config/`.

## Ranking key
`POWER` = capability added × reliability × how many nodes/surfaces it unlocks. `COST` = free /
free-tier(rate-limited) / prepaid(already-paid quota) / metered / paid. Free + high-power
sorts to the top. **UNVERIFIED** = found by one source (usually a web search summary), not
independently confirmed against the vendor's own docs by this pass.

## Rails COSMOS already has (baseline — do NOT re-add these)
Confirmed by reading `cosmos/cosmos_node_rails.py` (`register_node_rails` specs) and
`docs/MOTIF.md`: **`sgh-api`** (Grok, via `bts_sgh`, $0.02/call budget) · **`gem-api`**
(Gemini, via `bts_gem`, draws the $300 Vertex credit expiring 2026-10-13, budget $300) ·
**`gw-api`** (Grok-Build, via `bts_gw`, $0.001/call) · **`oa-api`** (OpenAI, via
`bts_oa_api`, $0.05/call). Wider mesh (outside COSMOS's rail registry, per `CLAUDE.md`):
Copilot (DOM, m365.cloud.microsoft), Claude Code/Cowork (F5, `claude -p`), GrokBot/GBt
(file-mailbox only — confirmed **no synchronous team/agent API exists**, see
`research_grok.md`).

## Candidates

| # | name | kind | HANDS (what it can DO) | cost | power | how COSMOS reaches it | found by | verified |
|---|------|------|--------|------|-------|----------|----------|----------|
| 1 | **Ollama** | CLI + local HTTP API | Runs Llama, Mistral, Gemma, Qwen, DeepSeek-distill etc. **fully offline** on Keith's own hardware; local server on `http://localhost:11434` is OpenAI-chat-compatible, so it drops into COSMOS's existing `ApiRail` shape with zero cloud dependency, zero spend-gate risk, and no vendor quota to run out — the one rail immune to every other row's "credit expires" problem | **free**, MIT license, no key, no cap | **5** — a whole model class with no external failure mode (no billing, no quota, no consent-to-lapse — matches canon "DOM first... depends on nothing that can run out") | new `ApiRail`/CLI adapter, `link_id="ollama-local"`, no spend_gate budget needed | web search + OLLAMA_HANDS.md; host probe 2026-08-25 | HANDS-DOCS yes; LIVE daemon **UNREACHABLE** (WinError 10061, binary missing). GPU RTX 3070 **8192 MiB**. HOLD Keith install. See ARCH §4.3 D. |
| 2 | **Groq API** | API (OpenAI-compatible) | Open-weight inference on LPU silicon (GPT-OSS / Qwen / Whisper) at hundreds–1000 tok/s — a different vendor from xAI **Grok**. **Not** Llama-3-70B on Free/Dev (shutdown 2026-08-16). Default id `openai/gpt-oss-20b`. Mixtral is dead. Cookbook [github.com/groq/groq-api-cookbook](https://github.com/groq/groq-api-cookbook) is a **research pointer**, not a rewrite (Batch/Flex still dark; Llama-3 tutorials stale vs ContactSales; Firecrawl MCP recipe ≠ composed `firecrawl-web`). | **free tier** (no card; 429 when over); Developer is card-on-file | **4** — speed unlocks bulk/agentic loops that are impractical on slower rails | new `ApiRail`, `link_id="groq-api"`, budget $0 | GROQ_HANDS.md + live GET /models + cookbook 2026-09-04 | HANDS-DOCS yes; **GATE PASS 2026-09-04** `response_model=openai/gpt-oss-20b` `chat_http=200`. Kernel compose live after bounce. See ARCH §4.3 E. |
| 3 | **Playwright MCP** (Microsoft, official) | MCP server | Real Playwright-controlled browser exposed as MCP tools — structured accessibility-tree navigation, not screenshots. Pin **`@playwright/mcp@0.0.79`**. | free, Apache-2.0 (Microsoft) | **4** — the canonical DOM-automation surface; upgrades `cosmos_browser` `--dump-dom` (READ only) to INTERACT | MCP-client stdio (`cosmos_mcp_client.py`); satellite `link_id="playwright-dom"` `kind=DOM` `core->interact` | PLAYWRIGHT_MCP_HANDS.md + live `--gate` | **WIRED satellite 2026-08-26T10:53:58-05:** `tools/list` 24 names + snapshot `tree_id=KMesh-COSMOS-live`. `--help` is not the gate. Kernel attach BACKLOG. |
| 4 | **browser-use** | Python library / CLI / hosted API | Open-source LLM-driven browser agent — natural-language task → autonomous multi-step browsing (fills forms, clicks, extracts) instead of hand-written selectors. Cloud trains on inputs — **do not wire Cloud MCP**. | free (MIT) self-hosted; hosted cloud API also offered | **4** — a second, independent DOM-automation lane (vendor-plural: Playwright = a11y-tree, this = open-ended) | OSS `Agent` in attempt workspace; `ANONYMIZED_TELEMETRY=false`; LLM = Ollama or existing rails | BROWSER_USE_HANDS.md | HANDS-DOCS yes; Python pkg **NO** on 3.14. HOLD slice 3 behind Ollama. Cloud MCP REJECT. |
| 5 | **Official MCP reference servers** — Filesystem, Git, Fetch, Memory, Sequential Thinking, Time, Everything | MCP servers | Filesystem: sandboxed file read/write with configurable ACLs. Git: read/search/manipulate repos. Fetch: web page retrieval. These are the maintained core of `modelcontextprotocol/servers` — the GitHub/GitLab/Postgres/Puppeteer/Slack/Redis/Sentry variants were archived in late 2025/early 2026 | free, open source, MCP-steering-group maintained | **3** — standards-based local hands COSMOS could use instead of custom file/git glue, if any module wants MCP-shaped access rather than direct `pathlib`/`git` calls | MCP registration, local stdio servers | web search (github.com/modelcontextprotocol/servers) | UNVERIFIED — confirm current archive/active split against `registry.modelcontextprotocol.io` before relying on this |
| 6 | **Aider** | CLI | Open-source terminal AI pair-programmer: edits code directly in a git repo, atomic commits per change, model-agnostic (works with Claude, DeepSeek, GPT-4o, o1/o3-mini, and local models) | free (tool itself); pay only the LLM provider it calls | **4** — a fourth independent coding-agent lane (alongside Claude Code/F5, Grok-Build, Copilot CLI) that can point at whichever model rail has quota headroom that day — fits `ROUTING.md`'s per-task, per-quota dispatch exactly | native worker `--yes-always --no-auto-commits` so Core fences; never the live tree | AIDER_HANDS.md | HANDS-DOCS yes; `aider` **ABSENT** on PATH. HOLD slice 3. |
| 7 | **GitHub Copilot CLI** | CLI (agent) | Terminal-native coding agent: review code, generate tests, debug, PR/issue-aware, parallelized subagents | **free tier**: 2,000 completions + 50 chat + 50 agent-mode requests/month, no card | **3** — another coding-agent lane, free-tier-capped so best as overflow/experiment rather than a daily driver | CLI install; queue-runner job | web search (github.com/features/copilot/cli, multiple pricing summaries) | UNVERIFIED |
| 8 | **OpenAI Codex CLI** | CLI (agent) | OpenAI's terminal coding agent; borrows ChatGPT sign-in (Free/Go/Plus/Pro) or a metered API key — no separate paywall | free on ChatGPT Free plan (low cap); metered via API key | **3** — a fifth coding-agent lane; low-value while `oa-api` already covers OpenAI, but the ChatGPT-plan login path is a *free* quota separate from the metered `oa-api` budget | CLI install, `codex` binary, queue-runner job | web search (morphllm.com, inventivehq.com, Wikipedia) | UNVERIFIED |
| 9 | **Firecrawl** | REST v2 (keyless) + MCP | Keyless: scrape, search, Research Index papers (~43M). Crawl/map need `fc-` key. Papers path is `/v2/search/research/papers` (not search category `research`). | **keyless free** (per-IP cap) then Free plan 1k credits/mo; paid after | **5** after live probe — Chapter 4 citation workflow as an API | satellite `ApiRail` `link_id="firecrawl-web"` `kind=API` `core->papers` (not ROUTING default for search/READ) | FIRECRAWL_HANDS.md + live `--gate` | **WIRED satellite 2026-08-26T10:53:54-05:** papers `primaryId=arxiv:physics/0103087` http=200. scrape/search overflow of dump-dom / SGH DOM. 402/429=`BROKE`. Kernel attach BACKLOG. |
| 10 | **Exa** | MCP connector (registry: not yet connected) | `web_search_exa`, `get_code_context_exa` — semantic web search + code-doc search | metered (exact pricing UNVERIFIED) | **3** — overlaps Firecrawl for web search but adds code-context search; useful as a second, disagreeing search lane (vendor-plural canon) | MCP connector, `directoryUuid: 91408932-1110-4350-97c7-2d6b3a6d9694`, url `https://mcp.exa.ai/mcp` | MCP registry search (keywords: code/github/deploy) | registry entry confirmed live; pricing UNVERIFIED |
| 11 | **LlamaParse** | MCP connector (registry: not yet connected) | Turns PDFs/documents into agent-ready structured context: `extractFile`, `classifyFile`, `estimateFileComplexity` — relevant to the dissertation's OCR'd corpus and PDF digitization work (Lindau1976, PJLA certs, exhibit bundles) | free tier + metered (exact numbers UNVERIFIED) | **3** — narrow but genuinely useful for the `chapter`/`legal` streams' recurring PDF-to-structured-text problem | MCP connector, `directoryUuid: d0585e82-4190-4588-ab31-b1afd254cf0f`, url `https://mcp.llamaindex.ai/mcp` | MCP registry search (keywords: files/storage/drive) | registry entry confirmed live; pricing UNVERIFIED |
| 12 | **Mistral API** ("La Plateforme") | API | Chat + Codestral coding model, OpenAI-ish REST; free "Experiment" tier is rate-limited but covers all models including Codestral | **free tier** (~1B tok/month cap per one source, exact number not published by Mistral, check console) | **3** — closes a real gap: adds a genuinely different model family (European, non-US-Big-Tech) to the vendor-plural roster, which the canon explicitly values ("the value is that members can disagree") | new `ApiRail`, `link_id="mistral-api"` | web search (cloudzero.com, pricepertoken.com, mistral.ai docs referenced) | UNVERIFIED |
| 13 | **DeepSeek API** | API (OpenAI-compatible) | Strong reasoning/coding model (V4-Flash / V4-Pro); one-time 5M-token free grant (30 days) then cheap metered (peak/off-peak billing, $0.22–$1.32/M in depending on time of day) | free trial grant, then **very cheap** metered (no perpetual free tier) | **4** — cheap+strong enough to be a real overflow/bulk-reasoning rail once the free grant is used; also runnable locally-adjacent via distilled models through Ollama (row 1) | new `ApiRail`, `link_id="deepseek-api"` | web search (multiple pricing trackers) | UNVERIFIED |
| 14 | **Perplexity Sonar API** | API | Web-grounded chat with inline citations — search + synthesis in one call, unlike a bare chat model | free: 5 Pro searches/day consumer; API gets $25–50 trial credit for new accounts, then $1–15/M tok+request fee tiers | **3** — a genuinely different capability (cited, grounded answers) that could shortcut some of SGH's DOM-search-then-synthesize workflow for quick fact-checks | new `ApiRail`, `link_id="pplx-api"` | web search (multiple pricing summaries) | UNVERIFIED |
| 15 | **Hugging Face Inference API** | API | Serverless inference across 100,000+ open models (under ~10B params on free tier) | free tier: a few hundred requests/hour, rate-limited, cold starts; PRO $9/mo raises limits + adds ZeroGPU compute | **2** — broad but weak per-model reliability on free tier; mainly useful for one-off niche/open-model experiments, not a daily rail | new `ApiRail`, `link_id="hf-api"` | web search | UNVERIFIED |
| 16 | **OpenRouter "free models router"** | API (OpenAI-compatible) | `model: openrouter/free` load-balances across ~20-27 rotating free open models (Qwen3-Coder, Gemma, gpt-oss, etc.) behind one endpoint | free, no card; rate-limited ~20 RPM/200 RPD, models rotate without warning | **2** — convenient single endpoint for casual free-model access, but the rotation-without-warning behavior is a bad fit for anything COSMOS needs to depend on (contradicts "no silent fallback" canon) | new `ApiRail`, `link_id="openrouter-free"`, flagged low-reliability | web search | **REJECT** H3/H4 (silent model swap). Named-model pin only if Keith asks. |
| 17 | **Anthropic API (direct, metered)** | API | Direct `api.anthropic.com` access to Opus/Sonnet/Haiku outside the Claude Code/Cowork subscription — a metered fallback path when the Claude Code weekly quota (currently 61-80% used per `ROUTING.md`) runs dry | $5 free credit for new accounts only; otherwise fully metered ($3-25/M input depending on model) | **3** — closes the one real gap in the "missing models" ask: COSMOS currently reaches Claude ONLY through Cowork/Claude Code (F5), never as a rail the Dispatcher can route to on its own; a metered `oa`-shaped rail would let COSMOS fall back to Claude without spending the scarce Claude Code weekly allotment | new `ApiRail`, `link_id="anthropic-api"`, budget-gated (it is real money, not prepaid quota) | web search (platform.claude.com/docs/pricing, multiple trackers) | pricing figures UNVERIFIED against the live pricing page this pass |
| 18 | **GitHub CLI (`gh`)** | CLI | Official GitHub CLI: issues, PRs, Actions, gists, releases — real repo hands | free, official (GitHub/Microsoft) | **2** — COSMOS's CI is currently GitLab (`ROUTING.md`); this only matters if/when a GitHub mirror or a GitHub-hosted dependency enters the picture | CLI job via queue runner | general knowledge, not independently re-verified this pass | UNVERIFIED |
| 19 | **Zapier MCP** | MCP connector (registry: not yet connected) | One MCP endpoint that can act across 9,000+ SaaS apps (Gmail, Slack, Salesforce, etc.) — broad but shallow, and costs Zapier task quota per call | runs on Zapier Free plan but **metered against task quota** (2 tasks/tool call) — not truly free | **2** — huge nominal reach, but 9,000 apps of which almost none matter to this dissertation/plumbing/legal mesh; useful only if a specific SaaS integration is ever needed that nothing else covers | MCP connector | web search (zapier.com/mcp) | **REJECT** H4 (meter for no COSMOS consumer). |
| 20 | **n8n** (self-hosted Community edition) | tool / workflow orchestrator with native MCP support | Open-source workflow automation, 400+ integrations, native MCP nodes, AI-agent nodes that can reason/branch — a second scheduler/orchestrator layer | free self-hosted (only cost = a small VPS, $5-20/mo) | **2** — COSMOS already has its own scheduler/queue-runner per the ratified architecture; n8n would be a redundant second orchestration layer unless used narrowly as a SaaS-integration bridge (then it's really competing with Zapier MCP, row 19, for the same narrow job) | would require a small always-on host; not native to `V:\A\Ai\COSMOS\live` | web search | **REJECT** as scheduler (H2/H8). Revisit only as a named SaaS-bridge. |

## Missing AI model rails — summary
COSMOS's `cosmos_node_rails.py` currently registers exactly four API links: **Grok**
(`sgh-api`), **Gemini** (`gem-api`, Vertex-backed), **Grok-Build** (`gw-api`), **OpenAI**
(`oa-api`). Wider mesh (not in the rail registry): Copilot (DOM), Claude Code/Cowork (F5),
GrokBot/GBt (file mailbox only, no sync API — confirmed by `research_grok.md`).

**Notable model-family gaps, ranked by how much they'd change what COSMOS can do:**
1. **Anthropic API direct** (row 17) — real gap: Claude is reachable only through the
   Cowork/Claude-Code subscription channel, never as a Dispatcher-routable metered rail.
2. **Local/offline via Ollama** (row 1) — real gap: zero rails today survive a
   quota/billing/consent outage; Ollama is the only candidate immune to that class of
   failure by construction, which is exactly what the DOM-first canon values.
3. **Mistral, DeepSeek** (rows 12-13) — real gap: no non-US-hyperscaler model family in
   the mesh at all; both are cheap-to-free and would add genuine vendor-plurality.
4. **Perplexity** (row 14) — different capability class (grounded/cited search-synthesis),
   not just another chat model — gap is capability, not redundancy.
5. **Groq** (row 2) — LPU speed (gpt-oss-20b), **not** a Grok twin and **not** Llama-3-70B
   on Free/Dev (shutdown 2026-08-16). Gap is latency/throughput. HOLD until Keith mints `gsk_`.

## MCP registry sweep — scope note
Searched 8 keyword sets (automation/tasks, code/github/deploy, browser/web, database/data,
files/storage, search/research, email/calendar, ai/llm/agent) against
`mcp__mcp-registry__search_mcp_registry`. ~90 distinct connectors returned. The large
majority (monday.com, Wrike, Process Street, Sprinto, Zoho Desk, Frontify, Runway, Roboflow,
Datadog, FactSet, Fitch, ZoomInfo, Semrush, Sprouts, Bigdata.com, DataGrail, Adobe Marketing
Agent, Gainsight, Webull, Alpha Vantage, Remote.com, Pushwoosh, OneSignal, MailerLite,
Padlet, AdWhispr, Circleback, Grain, Superhuman Mail, Intapp Celeste, LawVu, Jus AI, Midpage,
EDEN, WeWeb, Webflow, Similarweb, Webex, B12, Cloudinary, Pinegap, DataHub, Neon, Crustdata,
Files.com, Roam Research, Egnyte) are enterprise SaaS (CRM, finance data, marketing,
biotech, legal-research-for-firms) with **no plausible fit** to this mesh's actual mission
(dissertation physics, plumbing/legal/chapter streams, KMesh coordination) and were dropped
rather than padding the table. Two connectors already show `connected: true` in this Cowork
session and are worth noting as already-live surfaces COSMOS itself doesn't yet route
through directly: **Google Drive** (`b89f7865-...`, matches the existing GDX/BTS_SGH_Handoff
channel) and **Cloudflare Developer Platform** (`2d60210c-...`, Workers/KV/D1/R2 — relevant
since R2 already hosts the `GrokDex.csv` publish surface; COSMOS could get direct
bucket/worker hands instead of only the desktop `Publish-to-R2_KEYED.bat` route).

## Notes
- A chatbot with no hands is NOT an addition — reject unless it gains hands (a connector/CLI/API).
- Free/prepaid outranks metered at equal power.
- Stage-2 verification (G46, 2026-08-25T23:09-05) bound Playwright MCP `--help`, Firecrawl
  keyless scrape/search/papers, Groq 401, and Ollama 10061 to real packets. Architecture:
  `docs/arch/meshadditions_ARCH.md`. Remaining UNVERIFIED rows still need a live probe
  before WIRE.
- Stage-6 (G46, 2026-08-26T10:53-05) bound slice-1 as **satellites**:
  `live/config/firecrawl_rail_probe.json` `primaryId=arxiv:physics/0103087`;
  `live/config/playwright_rail_probe.json` snapshot `tree_id=KMesh-COSMOS-live`.
  Kernel still does not call `register_node_rails` (BACKLOG). `kernel_attached=false`
  is the honest PASS. Ollama/Groq HOLD. This is not Dispatcher-on-boot.
