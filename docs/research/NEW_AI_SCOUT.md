# NEW_AI_SCOUT — SGH (Grok research), live web 2026-08-27

**Scout:** SGH (Grok research). **Written:** 2026-08-27. **Present-day sources only.**
**Consumer:** COSMOS / COW. **P10:** this file is the assigned research artifact. Part B
`COMPETENCY.toml` rows are **PROPOSE-ONLY** — COW files them, or not.
**No COSMOS core / COMPETENCY.toml / makers.toml was edited this pass.**

**Assignment (WISHLIST 2026-08-27):**
- **(A)** NEW-AI DISCOVERY: products/models/agents COSMOS does **not** already have.
- **(B)** MAP THE UNMAPPED: GrokBOT, Aider, Groq, Ollama, GitHub/GitLab, MS Copilot,
  Browser-Use, Firecrawl — synchro level + proposed competency rows.

**Exclusion (do not re-add):** anything already a COMPETENCY node (G46, GEM, OA, SGH,
Cursor, DOM/Playwright), already a live rail (`sgh-api` / `gem-api` / `gw-api` /
`oa-api` / `playwright-dom` / `firecrawl-web` satellite), already a HANDS file, or
already a MESH_ADDITIONS / MESH_ADDITIONS_grok row (OpenCode, Goose, Pi, Cline,
whisper.cpp, Piper, Kokoro, llama.cpp, LM Studio/vLLM, Crawl4AI, Chrome DevTools
MCP, Windows-MCP, Qwen Code, Crush, …). `cosmos_discover.py` inventories known
hands; this scout is the open-ended pass.

**Filter:** a chatbot with no hands is rejected. Every candidate has a dispatchable
CLI / MCP / API / DOM surface. Free / already-prepaid first. Chat-only = out.

---

## A. NEW-AI DISCOVERY

Ranked by COSMOS power × free-first. CVM (voice) is the wishlist **top priority**,
so voice orchestration leads. Browser Stagehand v4 shipped **2026-08-10** and is
absent from MESH_ADDITIONS. Antigravity CLI replaced Gemini CLI on **2026-06-18**.

### A.1 Ranked new candidates (not already in the tree)

| # | name | vendor | reach | cost + free tier | credential | COSMOS fit |
|---|------|--------|-------|------------------|------------|------------|
| 1 | **Pipecat** | Daily (BSD-2 OSS) | **CLI** (`pipecat` scaffold/deploy) + **Python library** (pipeline) + **API** (self-host or Pipecat Cloud) + Android/iOS/JS **client SDKs**. Not MCP-first. | Framework **$0** (BSD-2). Pay only the STT/LLM/TTS you plug in. Cloud hosting is optional/metered. | None for self-host. Provider keys only for the services in the pipeline (or point STT/TTS at local VOSK/Piper/whisper.cpp already on the CVM path). | **Highest.** CVM needs a real-time STT→LLM→TTS loop on the PC, thin phone. Pipecat *is* that loop, swappable per stage, 500–800 ms round-trip claimed. Client SDKs cover phone + DT. |
| 2 | **LiveKit Agents** | LiveKit (Apache-2.0) | **CLI** (`agents.cli.run_app` / console) + **Python/Node SDK** + **API** (self-host LiveKit server **or** LiveKit Cloud) + WebRTC to phone/DT. Plugins for Deepgram/Groq/OpenAI/Cartesia/ElevenLabs/Silero. **MCP extra** exists. | Framework **$0**. Self-host media server **$0**. Cloud is optional. Plugins bill their vendors. | `LIVEKIT_URL` + API key/secret **only if Cloud**; self-host needs none beyond the STT/LLM/TTS plugins. | **Highest** sibling of Pipecat. Phone/DT already need a realtime transport; LiveKit *is* WebRTC. Python 3.10–&lt;3.15 (COSMOS is 3.14 — inside the band). Prefer **self-host** so voice does not depend on a vendor that can run out. |
| 3 | **Stagehand v4** | Browserbase (MIT) | **Python/TS/Go SDK** (local Chromium via CDP — **no Playwright dependency**) + **API** to Browserbase hosted browsers. `act` / `extract` / `observe` + Playwright-style `page`. **Not** an MCP server of its own; pair with an existing agent brain. | SDK **$0** (MIT). Local browser = electricity. Hosted Browserbase = metered session-minutes (free-tier exists on Browserbase; probe dashboard). LLM tokens = the model you pass (`OPENAI_API_KEY` etc.). | None for local. `BROWSERBASE_API_KEY` only if hosted. BYO model key. | **Highest browser add.** COSMOS already has Playwright MCP (deterministic a11y) and Browser-Use (open-ended LLM driver). Stagehand is the missing **hybrid**: NL `act` that drops to locators. v4.0.0 **2026-08-10**, v4.0.2 **2026-08-20** on PyPI. Python example uses `local_browser.launch`. |
| 4 | **Google Antigravity CLI (`agy`)** | Google | **CLI** (`agy`) + **IDE** (Antigravity 2.0) + **Gemini API** “Antigravity Agent” programmatic path. MCP (added after launch). Closed-source Go binary. | **$0 Individual** plan: Gemini 3.5 Flash / 3.1 Pro / 3 Flash, Claude Sonnet & Opus 4.6, gpt-oss-120b, unlimited tab/command, **basic weekly rate limits**. Google AI Pro/Ultra = higher limits + credit pool. Gemini CLI **consumer free serving died 2026-06-18**. | Google account login (Individual). Or Gemini API / Vertex / Gemini Enterprise Agent Platform keys for the programmatic agent. | **High.** A second Google-family **coding CLI** COSMOS does not have (GEM is API, not a harness). Fills the hole MESH_ADDITIONS_grok closed by rejecting unpaid Gemini CLI. Use as overflow coding lane; do not make it a second ledger writer. Pin it to attempt workspaces. |
| 5 | **Skyvern** | Skyvern AI (AGPL-3.0 OSS + cloud) | **API** + **Python/workflow UI** + self-host. Vision+LLM RPA: forms, CAPTCHA, 2FA. | OSS self-host **$0** (AGPL — keep as a **separate process**, same rule as Firecrawl). Cloud: free credits then paid (one 2026 roundup cited 1k credits / $29/mo — **probe** [skyvern.com](https://www.skyvern.com) before quoting). | None self-host (BYO LLM). Cloud API key if hosted. | **High** for hostile sites Playwright a11y-tree cannot see (CAPTCHA/2FA). Vendor-plural DOM: Playwright = structure, Browser-Use = open-ended, Skyvern = vision-RPA. AGPL = sidecar, never inlined into Core. |
| 6 | **Steel** | Steel.dev (Apache-2.0) | **API** (CDP URL → Playwright / Browser-Use) + **self-host** Docker. Cloud browser fleet, CAPTCHA/proxy optional. | OSS self-host **$0**. Cloud: free tier reported (one 2026 infra roundup: 100 hrs then $29/mo — **probe** [steel.dev](https://steel.dev) before quoting). | None self-host. Cloud API key if hosted. | **High infra.** If CVM/DOM jobs outgrow local Chromium, Steel is the **open** cloud-browser (Browserbase is closed). COSMOS-shaped: self-host first. |
| 7 | **PydanticAI** | Pydantic (MIT) | **Python library** (typed `Agent`, `run_sync`, tools, structured `output_type`) + optional **Gateway** (one key, failover). Not a CLI coding agent. Model-agnostic: OpenAI, Anthropic, Gemini, Grok/xAI, Groq, Ollama, Cerebras, … | Library **$0**. Gateway/metered models = those vendors. | Provider keys already on COSMOS rails, **or** Ollama (none). | **High orchestration.** COSMOS is Python 3.14 + structured outputs + spend-gate. PydanticAI is the typed agent loop that can sit **in a worker** and call existing rails without inventing a second orchestrator (n8n already REJECT). PyPI `pydantic-ai` **2.35.0** dated **2026-08-26**. |
| 8 | **Google ADK** (`google-adk`) | Google (Apache-2.0) | **CLI** (`adk eval`, web UI) + **Python/Go/Java/Kotlin/TS SDK**. Tools, code executor, live/voice agents, eval sets. PyPI **2.8.0** **2026-08-26**. | Framework **$0**. Gemini inference = Vertex/`gem-api` or AI Studio. | Existing `GOOGLE_API_KEY` / Vertex ADC. | **High** for CVM live-voice eval + a second Python agent harness that is **not** LangGraph. Complements GEM rail; do not duplicate Dispatcher. |
| 9 | **Continue.dev** | Continue (OSS, Apache-ish) | **IDE extension** (VS Code/JetBrains) + **CLI/agent**. BYO model (Ollama, any OpenAI-compat). MCP. | Tool **$0**. Inference = provider / local. | None for local Ollama. Else existing keys. | **Med-high.** A configurable assistant, not a hands-off agent (AgentsCamp 2026). Useful as a Keith-facing editor agent; COSMOS queue still prefers Aider/OpenCode/`grok -p`. ~35.6k stars, last push **2026-08-25**. |
| 10 | **Kilo Code** | Kilo-Org (MIT) | **VS Code extension + CLI** (Cline-lineage). BYO, 500+ models, MCP. | Tool **$0**. | BYO keys / Ollama. | **Med-high** OSS coding overflow. 27.0k stars, last push **2026-08-25**. Probe vs Cline (already MESH_ADDITIONS_grok row 43) — pick **one**. |
| 11 | **Tabby** | TabbyML (Apache-2.0) | **Self-hosted** coding assistant: REST + IDE plugins. Local models. | **$0** self-host. | None (local weights). | **Med-high** local-first completion rail that cannot run out. 33.8k stars; last push **2026-06-30** (slower). RTX 3070 8 GiB → 7–8B coder, same VRAM ceiling as Ollama. |
| 12 | **OpenAI Agents SDK** | OpenAI | **Python/TS SDK** (agent loop, handoffs, guardrails, **sandbox agents**, Codex-shaped filesystem tools). Not a CLI. | SDK **$0**. Inference = `oa-api` token meters. | Existing `OPENAI_API_KEY`. | **Med.** COSMOS already has Codex CLI + `oa-api`. The SDK’s **sandbox harness** (2026-04 evolution: files, shell, long jobs) is the new piece — a worker-shaped OpenAI agent without burning ChatGPT Codex CLI quota. |
| 13 | **Amazon Kiro** | Amazon (AWS) | **IDE** (spec-driven) + AWS-tied agents. Replacing Q Developer (EOL Apr 2027 per Zylos Q2 2026 landscape). | Free → paid AWS; **probe** [kiro.dev](https://kiro.dev) / AWS pricing before a spend-gate. | AWS account. | **HOLD.** Spec-driven is interesting; no COSMOS AWS consumer today. MESH_ADDITIONS_grok already skips AWS Labs MCP for the same reason. |
| 14 | **Google Jules** | Google | **Cloud agent**: GitHub issue → VM → PR. Async, not a local CLI. | Public beta **free with limits** (AgentsCamp / CodemySpec 2026). Confirm at [jules.google](https://jules.google). | Google + GitHub OAuth. | **HOLD overflow.** Overlaps Cursor Cloud Agents + Copilot cloud agent. Do not double-dispatch without a lease. |
| 15 | **Factory (Droid)** | Factory AI | **CLI + desktop + cloud “Missions”.** Full-SDLC Droids. | Enterprise; Series C $150M Apr 2026 at $1.5B (CodemySpec). No meaningful free tier found this pass. | Factory account. | **REJECT for now** (meter, no COSMOS consumer). Revisit only if Keith wants an enterprise SDLC vendor. |
| 16 | **Amp** | Amp Inc. (ex-Sourcegraph) | **CLI + web + mobile**, remote workers, subagent messaging. | Closed; paid. CLI-only pivot Feb 2026 (Tech Stackups). | Amp account. | **REJECT for now** (paid closed harness; OpenCode/Pi/Aider cover BYOK CLI). |

**Sources (Part A, fetched 2026-08-27):**
- Coding-agent ranking (updated **2026-08-26 01:24 UTC**): https://github.com/tiennm99/awesome-coding-agents
- Terminal-Bench / price table (updated 2026-08-21): https://www.morphllm.com/ai-coding-agent
- CLI landscape: https://agentscamp.com/guides/prompting/ai-coding-agents-cli-2026 · https://www.testmuai.com/blog/agentic-coding-cli-tools/ · https://zylos.ai/research/2026-06-25-agentic-coding-tools-q2-2026-landscape/
- Stagehand v4: https://docs.stagehand.dev · https://pypi.org/project/stagehand/ (4.0.0 on 2026-08-10, 4.0.2 on 2026-08-20) · X launch https://x.com/Stagehanddev/status/2089450961152655729
- Browser comparison: https://agentscamp.com/guides/comparisons/browser-agents-compared-2026 · Skyvern vs Steel https://openalternative.co/compare/skyvern/vs/steel · Browserbase/Steel infra https://www.pkgpulse.com/guides/browserbase-vs-hyperbrowser-vs-steel-cloud-browsers-ai-2026
- Antigravity pricing: https://antigravity.google/pricing · cutover https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/ (2026-05-19; consumer cutoff 2026-06-18)
- Pipecat: https://docs.pipecat.ai/overview/introduction · https://docs.pipecat.ai/overview/pipecat (BSD-2, 150+ services, 500–800 ms)
- LiveKit Agents: https://docs.livekit.io/agents/ · https://pypi.org/project/livekit-agents/ (1.7.1, Apache-2.0, Py &lt;3.15, verified 2026-08-27)
- PydanticAI: https://pypi.org/project/pydantic-ai/ (2.35.0, 2026-08-26) · https://pydantic.dev/docs/pydantic-ai/overview/
- Google ADK: https://pypi.org/project/google-adk/ (2.8.0, 2026-08-26) · https://google.github.io/adk-docs/
- OpenAI Agents SDK: https://developers.openai.com/api/docs/guides/agents · https://openai.github.io/openai-agents-python/agents · sandbox evolution https://openai.com/zh-Hans-CN/index/the-next-evolution-of-the-agents-sdk/

### A.2 Suggested first slice (COW verify, then maybe HANDS + rail)

Probe in this order — each is free or already-prepaid, each closes a hole the live mesh actually has:

1. **Pipecat self-host** (or LiveKit Agents self-host) against **local** STT/TTS (VOSK/whisper.cpp + Piper/Kokoro already on MESH_ADDITIONS_grok). CVM top priority. Proof = a PC round-trip transcript+wav hash, not `rc=0`.
2. **Stagehand v4 local** (`pip install stagehand` + `local_browser.launch`) as a third DOM member. Proof = `extract` JSON from a loopback page containing `tree_id=KMesh-COSMOS-live`.
3. **Antigravity CLI Individual $0** (`agy`) as a Google-family coding harness overflow. Proof = `agy` version + one attempt-workspace edit, never the live tree.
4. **PydanticAI worker** pointed at existing `sgh-api`/`oa-api`/`gem-api` (and later Ollama). Proof = structured `output_type` JSON the spend-gate logged.

Do **not** stand up Factory/Amp/Jules/Kiro until the free slice is bound.

### A.3 Explicitly not-new (already inventoried)

OpenCode, Goose, Pi, Cline, Aider, Codex CLI, Copilot CLI, Firecrawl, Browser-Use, Playwright MCP, Ollama, Groq, llama.cpp, LM Studio, vLLM, whisper.cpp, FunASR, Piper, Kokoro, WhisperX, Crawl4AI, Chrome DevTools MCP, n8n (REJECT as scheduler), Zapier (REJECT), OpenRouter rotating free (REJECT silent swap). See `docs/MESH_ADDITIONS.md` and `docs/MESH_ADDITIONS_grok.md`.

---

## B. MAP THE UNMAPPED

These products have `docs/research/*_HANDS.md` (or T1/gbridge for GrokBOT) but **no**
`[nodes.*]` row in `docs/COMPETENCY.toml` (researched_at 2026-08-26, six nodes:
G46, GEM, OA, SGH, Cursor, DOM). Wishlist 2026-08-27 named them.

### B.1 Synchro level (CLI / MCP / API / DOM)

| product | primary synchro | also | COSMOS status now | source of the level |
|---|---|---|---|---|
| **GrokBOT / Grok Bot** | **DOM** (Windows/macOS desktop app + iOS). File-mailbox (`to_gbot/` / `from_gbot/`, `builds/gbridge`) is the only COSMOS-owned **sync** path. | MCP **as a consumer** (Bot uses connectors/MCP on its cloud VM). **No** documented public REST/CLI that addresses a *named* grok.com Bot. xAI API (`POST /v1/chat/completions`) is a **different identity** (stateless Grok model, not that teammate). | Maker `grokbot-team` in `cosmos/makers.toml`. Sync job `grok_syncgrokbot` **FAILED rc=3221225786** (NTSTATUS `0xC0000005` ACCESS_VIOLATION — native crash, not a Python exception). Retry `grok_syncgrokbot_retry` later `ok rc=0`. | https://docs.x.ai/grok-bot/overview · https://docs.x.ai/grok-bot/get-started · https://x.ai/news/introducing-grok-bot (2026-08-11) · https://x.ai/news/grok-bot-more-plans (2026-08-26) · `docs/research/T1_SYNC_GBOT_COW/research_grok.md` · `docs/COLLECTOR.md` |
| **Aider** | **CLI** (`aider --yes-always --message …`). | Community MCP only. Python `Coder` API **unsupported**. DOM = optional `--browser` / copy-paste web-chat fallback. | HANDS yes. Binary **ABSENT** on PATH (MESH_ADDITIONS 2026-08-25). HOLD slice 3. | https://aider.chat/docs/scripting.html · `docs/research/AIDER_HANDS.md` |
| **Groq** | **API** (`https://api.groq.com/openai/v1`, OpenAI-compat). | Groq is an MCP **client** (remote MCP + Google connectors). **No official coding CLI.** DOM = console.groq.com (keys/limits). | HANDS yes. Live GET `/models` **HTTP 401** `invalid_api_key` — endpoint up, no `gsk_` in `live/config/`. HOLD Keith key. Default model `openai/gpt-oss-20b` (Llama-3-70B Free/Dev **shutdown 2026-08-16**). | https://console.groq.com/docs/overview · https://console.groq.com/docs/models · `docs/research/GROQ_HANDS.md` |
| **Ollama** | **CLI** (`ollama run/pull/serve`) **+ local HTTP API** (`http://127.0.0.1:11434`, OpenAI + Anthropic shims). | MCP wrappers (community). DOM = ollama.com download/library/signin. Cloud `ollama.com/api` is a **second wallet**. | HANDS yes. Live GET `:11434/api/version` **WinError 10061**; binary missing. GPU RTX 3070 **8192 MiB** → 8B-class, not 30B-coder. HOLD Keith install. | https://docs.ollama.com/api/introduction · https://ollama.com/pricing · `docs/research/OLLAMA_HANDS.md` |
| **GitHub** | **CLI** (`gh`) **+ REST/GraphQL API** + **official MCP** (`https://api.githubcopilot.com/mcp/`) + **DOM** (github.com fallback). Copilot CLI `copilot -p` and cloud agent `POST /agents/repos/{o}/{r}/tasks` ride the same wallet. | — | HANDS yes. GitHub is the **second forge** (`keithbbf-gif/cosmos`). Copilot cloud agent **pending** a seat (`docs/MODEL_ACCESS.md`). | https://cli.github.com/manual/gh · https://github.com/github/github-mcp-server · `docs/research/GITHUB_HANDS.md` |
| **GitLab** | **CLI** (`glab`) **+ REST/GraphQL API** + **MCP** (`https://gitlab.com/api/v4/mcp`, Free as of 19.2, beta) + **DOM**. Self-hosted runner = unlimited CI minutes. | `glab mcp serve` stdio is **experimental**. | HANDS yes. Named executable gate in FINAL_ARCHITECTURE. Hosted minutes = **400/mo Free**, not a $200 grant. | https://docs.gitlab.com/cli/ · https://docs.gitlab.com/user/model_context_protocol/mcp_server/ · `docs/research/GITLAB_HANDS.md` |
| **MS Copilot** | **DOM first** (`https://m365.cloud.microsoft/chat`, web-grounded, $0 extra on eligible M365). **API** = Graph Copilot + Work IQ A2A (license/credits). **MCP** = Work IQ MCP (10 generic M365 tools). Direct Line for Studio agents. | GitHub Copilot is a **different product/wallet** (`GITHUB_HANDS.md`). | HANDS yes. No Microsoft rail in `cosmos_node_rails.py`. | https://www.microsoft.com/en-us/microsoft-365/copilot · `docs/research/MICROSOFT_COPILOT_HANDS.md` |
| **Browser-Use** | **CLI** (`browser-use --mcp`) **+ Python OSS library** (local Chromium) **+ local MCP**. Cloud **API** (`api.browser-use.com/v4`) is overflow. | Cloud MCP **REJECT** (trains on inputs — MESH_ADDITIONS_grok). | HANDS yes. Python pkg **NO** on 3.14 this host. HOLD slice 3 behind Ollama. | https://docs.browser-use.com/open-source/llms.txt · https://browser-use.com/pricing.md · `docs/research/BROWSER_USE_HANDS.md` |
| **Firecrawl** | **API** (REST v2; keyless scrape/search/papers) **+ MCP** (`https://mcp.firecrawl.dev/v2/mcp`) **+ CLI** (`firecrawl-cli`). DOM = playground/keys. | Crawl/map need `fc-` key. Self-host AGPL core. | **WIRED satellite** `firecrawl-web` 2026-08-26T10:53:54-05. Probe `primaryId=arxiv:physics/0103087` http=200. Kernel still does **not** attach (`kernel_attached=false`). | https://docs.firecrawl.dev · https://www.firecrawl.dev/pricing.md · `docs/research/FIRECRAWL_HANDS.md` · `live/config/firecrawl_rail_probe.json` |

**GrokBOT extra (post-T1, live 2026-08-27):** official product is **Grok Bot** (SpaceXAI / xAI + Cursor). Each Bot is a persistent named teammate on a **shared per-user cloud VM** (browser, filesystem, terminal, computer-use, connectors/MCP). Messaging is the desktop/iOS app, Cursor-account login. Eligible plans expanded **2026-08-26** to SuperGrok, SuperGrok Plus/Heavy, Cursor Pro/Pro+/Ultra, Cursor Teams Standard/Premium — usage **separate** from Grok/Cursor quotas. Get-started still lists a slightly narrower set (Plus/Heavy/Pro+/Ultra/Teams) — **treat the Aug 26 news post as the expansion, the get-started page as possibly stale.** There is still **no** public `team_id` / `bot_id` RPC. COSMOS synchro remains: **mailbox / gbridge** (sync facade) + **DOM** of the desktop app. Do not claim `grok -p` addresses Grok Bot — that is Grok Build (G46).

**rc=3221225786:** Windows `STATUS_ACCESS_VIOLATION`. The T1 sync job crashed the process; it is **not** evidence that “no API exists” (that conclusion is separately true from xAI docs). Fix = stop running an in-process crashy wrapper; keep gbridge mailbox + fail-closed timeout. ACCESS_VIOLATION is a native-code bug, not a vendor 404.

### B.2 Proposed `docs/COMPETENCY.toml` additions (COW files)

Schema stays `competency/1`. Ratings = real hands, not slogans. `possessed=false` and `rating=0` if the host cannot fire it **today** (Ollama daemon down, no `gsk_`, Aider/Browser-Use not installed) — but the **node still exists** so ROUTING can pick it the day the probe goes green. Alternative: set `possessed=true` for “we have the HANDS and a path” even if HOLD; **this proposal uses possessed=true for documented hands, rating reflects live reachability caveats in `hands`.** Firecrawl is the one already gated live.

**Also propose two new `task_types`** (CVM is top priority; the current 8 types cannot route STT/TTS):

```toml
# --- PROPOSE: append to [router] ---
# nodes_order add (after DOM, vendor-plural / local-first):
#   "Ollama", "Firecrawl", "BrowserUse", "Aider", "Groq",
#   "GitHub", "GitLab", "MSCopilot", "GrokBOT"
# task_types add:
#   "voice-STT",
#   "voice-TTS",
```

#### Proposed node blocks

```toml
# === PROPOSE-ONLY (P10). COW files into docs/COMPETENCY.toml or not. ===
# SGH 2026-08-27. Do not treat this as live ROUTING until COW merges.

[nodes.GrokBOT]
id = "GrokBOT"
family = "xai"
product = "Grok Bot (persistent cloud-VM teammates)"
model = "grok-family (Bot-managed; not grok-4.6 API identity)"
context_tokens = 0
cosmos_lane = "gbridge mailbox + Grok Bot desktop DOM; makers.toml grokbot-team"
hands = "Named persistent Bots on a shared per-user cloud Linux VM: browser, filesystem, terminal, computer-use, connectors/MCP. App (Win/macOS/iOS), Cursor-account login. NO public bot_id REST/CLI. COSMOS sync = to_gbot/from_gbot files (gbridge). grok -p is G46, not this node."

[nodes.Aider]
id = "Aider"
family = "aider"
product = "Aider CLI pair-programmer"
model = "BYO (LiteLLM: OpenAI/Anthropic/Gemini/xAI/Groq/Ollama/…)"
context_tokens = 0
cosmos_lane = "native CLI worker in attempt workspace (not installed this host 2026-08-25)"
hands = "Headless aider --yes-always --message/--message-file, repo-map, SEARCH/REPLACE, auto-commit per edit, --auto-test. Apache-2.0. Last upstream push 2026-05-22 (slower than OpenCode/Pi). Never write the live tree."

[nodes.Groq]
id = "Groq"
family = "groq"
product = "GroqCloud LPU inference"
model = "openai/gpt-oss-20b (default; Llama-3-70B Free/Dev dead 2026-08-16)"
context_tokens = 131072
cosmos_lane = "proposed ApiRail groq-api; HOLD Keith gsk_ (live 401)"
hands = "OpenAI-compat POST api.groq.com/openai/v1; ~1000 t/s gpt-oss-20b; Whisper STT; Orpheus TTS (expensive); Compound + browser_search/code; remote MCP client. NOT xAI Grok. No official coding CLI."

[nodes.Ollama]
id = "Ollama"
family = "local"
product = "Ollama local (and optional Cloud) open-model runtime"
model = "local GGUF (8B-class on RTX 3070 8 GiB)"
context_tokens = 0
cosmos_lane = "proposed ApiRail ollama-local; HOLD Keith install (WinError 10061)"
hands = "CLI + HTTP :11434 native/OpenAI/Anthropic shims. $0 local, no key. Cloud is a different wallet ($0 light / $20 Pro). Default num_ctx 2k is a silent-truncation footgun."

[nodes.GitHub]
id = "GitHub"
family = "github"
product = "GitHub forge + Copilot agents"
model = "Copilot auto / BYOK into Copilot CLI"
context_tokens = 0
cosmos_lane = "gh CLI + REST/GraphQL + github-mcp-server; Copilot cloud agent pending seat"
hands = "gh issues/PRs/Actions/dispatches; official MCP; Copilot CLI copilot -p; cloud SWE agent POST /agents/repos/{o}/{r}/tasks (user-to-server token only). Free REST 5k/hr. Copilot credits are a separate wallet from gh."

[nodes.GitLab]
id = "GitLab"
family = "gitlab"
product = "GitLab.com forge + CI gate"
model = "none (forge). Duo is Credits-metered on Free — not the coding lane."
context_tokens = 0
cosmos_lane = "glab + REST/GraphQL + /api/v4/mcp; named Motif executable gate"
hands = "glab ci/mr/issue/api; pipelines REST + trigger tokens + webhooks; MCP on Free (19.2, beta); self-hosted runner burns 0 hosted minutes. Free hosted = 400 min/mo, not $200."

[nodes.MSCopilot]
id = "MSCopilot"
family = "microsoft"
product = "Microsoft Copilot Chat / Graph Copilot / Work IQ"
model = "M365 Copilot stack (web-grounded Chat; work-grounded needs $30 add-on)"
context_tokens = 0
cosmos_lane = "DOM m365.cloud.microsoft/chat; Graph/Work IQ after Entra app"
hands = "Free web-grounded Chat on eligible M365. Graph Search included. Retrieval/Chat API need Copilot add-on or PAYG. Work IQ A2A/MCP = Copilot Credits, no add-on. NOT GitHub Copilot."

[nodes.BrowserUse]
id = "BrowserUse"
family = "browser-use"
product = "browser-use OSS (local) + optional Cloud"
model = "BYO LLM (Ollama preferred) or Cloud V4 hosted"
context_tokens = 0
cosmos_lane = "DOM worker OSS Agent; HOLD pkg missing on 3.14; Cloud MCP REJECT"
hands = "MIT Python Agent: NL task → Chromium click/type/extract. Local MCP uvx browser-use --mcp. ANONYMIZED_TELEMETRY=false required. Cloud Free = 10 tasks/mo. Do not mix browser-use vs browser-use-sdk."

[nodes.Firecrawl]
id = "Firecrawl"
family = "firecrawl"
product = "Firecrawl v2 web-context API + MCP"
model = "none (extractor); Agent uses vendor LLMs on paid path"
context_tokens = 0
cosmos_lane = "satellite firecrawl-web (wired 2026-08-26); Kernel attach BACKLOG"
hands = "Keyless scrape/search/papers; papers ~43M. Crawl/map need fc- key. MCP hosted. AGPL self-host for bulk markdown. Probe gate=PASS primaryId=arxiv:physics/0103087."
```

#### Proposed skill rows

Rating scale unchanged: `0=absent/unverified 1=weak 2=usable-with-caveats 3=competent 4=strong 5=best-among-listed`.

```toml
# --- code-build ---
[skills.code-build.GrokBOT]
possessed = true
rating = 3
source = "https://docs.x.ai/grok-bot/overview (cloud VM with terminal/filesystem/browser; app-dispatch only — no grok -p / no bot_id API). COSMOS cannot queue it like G46."

[skills.code-build.Aider]
possessed = true
rating = 4
source = "https://aider.chat/docs/scripting.html + https://github.com/tiennm99/awesome-coding-agents (48.5k stars; --yes-always --message --auto-test). Host binary ABSENT 2026-08-25 — rating is product, probe before ROUTING."

[skills.code-build.Groq]
possessed = true
rating = 2
source = "https://console.groq.com/docs/models (gpt-oss-20b is fast inference, not a coding harness). Pair with Aider --model groq/… once gsk_ exists."

[skills.code-build.Ollama]
possessed = true
rating = 3
source = "https://docs.ollama.com/integrations/claude-code + aider ollama_chat/ (local coder 8B on 8 GiB). Daemon UNREACHABLE this host."

[skills.code-build.GitHub]
possessed = true
rating = 4
source = "https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli (copilot -p) + https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-via-the-api (POST /agents/repos/…/tasks). Cloud agent pending seat."

[skills.code-build.GitLab]
possessed = true
rating = 2
source = "https://docs.gitlab.com/ci/pipelines/ (CI is the *gate*, not the coder). Duo Agent Platform on Free needs GitLab Credits — do not route Motif coding here while G46/Cursor have headroom. docs/research/GITLAB_HANDS.md row 36."

[skills.code-build.MSCopilot]
possessed = false
rating = 0
source = "docs/research/MICROSOFT_COPILOT_HANDS.md (M365 Copilot is work-chat/RAG, not a coding agent). GitHub Copilot ≠ this node."

[skills.code-build.BrowserUse]
possessed = false
rating = 0
source = "https://docs.browser-use.com/open-source/introduction (browser agent, not a repo coding loop)"

[skills.code-build.Firecrawl]
possessed = false
rating = 0
source = "https://docs.firecrawl.dev (web-context API, not a coding agent)"

# --- code-review-critique ---
[skills.code-review-critique.GrokBOT]
possessed = true
rating = 3
source = "https://docs.x.ai/grok-bot/overview (can review in its VM / apps). Same xAI family as G46 — cannot supply *other-family* critique of a G46 build."

[skills.code-review-critique.Aider]
possessed = true
rating = 4
source = "https://aider.chat/docs/usage/modes.html (`--chat-mode ask` never edits; --auto-test is a real gate)"

[skills.code-review-critique.Groq]
possessed = true
rating = 2
source = "https://console.groq.com/docs/openai (fast token dump of a diff; no repo harness)"

[skills.code-review-critique.Ollama]
possessed = true
rating = 2
source = "https://docs.ollama.com/api/chat (local review, quality = the pulled model; 8B-class on this GPU)"

[skills.code-review-critique.GitHub]
possessed = true
rating = 4
source = "https://docs.github.com/en/rest/pulls/reviews (PR reviews) + Copilot CLI/cloud review jobs. Checks API for runtime-binding evidence on the merge UI."

[skills.code-review-critique.GitLab]
possessed = true
rating = 4
source = "https://docs.gitlab.com/api/merge_requests/ + MCP save_merge_request_review (notes on the SHA-pinned MR — Motif stage-5 landing zone)"

[skills.code-review-critique.MSCopilot]
possessed = true
rating = 2
source = "https://m365.cloud.microsoft/chat (can read a pasted diff in DOM). Not a repo-native reviewer."

[skills.code-review-critique.BrowserUse]
possessed = false
rating = 0
source = "browser agent, not a critic"

[skills.code-review-critique.Firecrawl]
possessed = false
rating = 0
source = "extractor, not a critic"

# --- web-research ---
[skills.web-research.GrokBOT]
possessed = true
rating = 4
source = "https://docs.x.ai/grok-bot/overview (own browser + computer-use + connectors). App-dispatch, not SGH web_search."

[skills.web-research.Aider]
possessed = true
rating = 2
source = "https://aider.chat/docs/usage/images-urls.html (`/web` Playwright scrape into chat — ingest, not a search index)"

[skills.web-research.Groq]
possessed = true
rating = 3
source = "https://console.groq.com/docs/tool-use/built-in-tools/browser-search (Compound / gpt-oss + browser_search; tool fees on Developer). Free-tier Compound 250 RPD."

[skills.web-research.Ollama]
possessed = true
rating = 2
source = "https://docs.ollama.com/capabilities/web-search (web search/fetch need ollama.com account + API key = Cloud wallet, not local)"

[skills.web-research.GitHub]
possessed = true
rating = 2
source = "https://docs.github.com/en/rest/search/search (code/issues/commits search, 30 req/min). Not a web index."

[skills.web-research.GitLab]
possessed = true
rating = 1
source = "https://docs.gitlab.com/user/gitlab_com/#rate-limits-on-gitlabcom (project search 10 req/min/IP). Local rg is faster on the live tree."

[skills.web-research.MSCopilot]
possessed = true
rating = 4
source = "https://m365.cloud.microsoft/chat (web-grounded Copilot Chat included on eligible M365 — DOM-first free LLM+search)"

[skills.web-research.BrowserUse]
possessed = true
rating = 3
source = "https://docs.browser-use.com/open-source/introduction (can *use* the live web; no search index of its own)"

[skills.web-research.Firecrawl]
possessed = true
rating = 5
source = "https://docs.firecrawl.dev/features/search + https://docs.firecrawl.dev/features/research (keyless search + ~43M-paper index). Live gate 2026-08-26 primaryId=arxiv:physics/0103087."

# --- docs-authoring ---
[skills.docs-authoring.GrokBOT]
possessed = true
rating = 3
source = "https://docs.x.ai/grok-bot/overview (durable teammate writes in its VM / connected apps). Not in-repo markdown like G46."

[skills.docs-authoring.Aider]
possessed = true
rating = 3
source = "https://aider.chat/docs/usage/not-code.html (edits README/YAML/text in git with the same pipeline)"

[skills.docs-authoring.Groq]
possessed = true
rating = 2
source = "https://console.groq.com/docs/text-chat (fast draft tokens; no doc harness)"

[skills.docs-authoring.Ollama]
possessed = true
rating = 2
source = "https://docs.ollama.com/api/generate (local draft; quality = pulled model)"

[skills.docs-authoring.GitHub]
possessed = true
rating = 2
source = "https://docs.github.com/en/rest/repos/contents (Contents API / gh can commit docs). Author is the agent that calls it."

[skills.docs-authoring.GitLab]
possessed = true
rating = 2
source = "https://docs.gitlab.com/api/repository_files/ (file API) + Pages for publish. Wiki is not COSMOS docs/."

[skills.docs-authoring.MSCopilot]
possessed = true
rating = 4
source = "https://www.microsoft.com/en-us/microsoft-365/copilot (in-app Word/Excel/Pages with $30 add-on; web Chat can draft without it)"

[skills.docs-authoring.BrowserUse]
possessed = false
rating = 0
source = "no document authoring hands"

[skills.docs-authoring.Firecrawl]
possessed = true
rating = 2
source = "https://docs.firecrawl.dev/features/scrape (URL→markdown is ingest, not authoring)"

# --- DOM-automation ---
[skills.DOM-automation.GrokBOT]
possessed = true
rating = 4
source = "https://docs.x.ai/grok-bot/overview (computer-use on a persistent cloud VM; human takeover for 2FA). App-dispatch only."

[skills.DOM-automation.Aider]
possessed = true
rating = 1
source = "https://aider.chat/docs/usage/copypaste.html (copy-paste web-chat fallback). Not a browser driver."

[skills.DOM-automation.Groq]
possessed = true
rating = 1
source = "https://console.groq.com/docs/tool-use/built-in-tools/browser-search (server-side browse, not COSMOS DOM control)"

[skills.DOM-automation.Ollama]
possessed = false
rating = 0
source = "https://docs.ollama.com (inference runtime, no browser)"

[skills.DOM-automation.GitHub]
possessed = true
rating = 1
source = "docs/research/GITHUB_HANDS.md row 41 (github.com DOM fallback when API AUTH_REQUIRED). Prefer gh/API."

[skills.DOM-automation.GitLab]
possessed = true
rating = 1
source = "docs/research/GITLAB_HANDS.md (gitlab.com DOM fallback). Prefer glab/API."

[skills.DOM-automation.MSCopilot]
possessed = true
rating = 3
source = "https://m365.cloud.microsoft/chat (Playwright MCP drives the composer — the free Copilot hand). Studio computer-use is credits-heavy overlap."

[skills.DOM-automation.BrowserUse]
possessed = true
rating = 5
source = "https://docs.browser-use.com/open-source/introduction (NL→autonomous Chromium; vendor-plural vs Playwright a11y-tree). Local only; Cloud MCP REJECT."

[skills.DOM-automation.Firecrawl]
possessed = true
rating = 2
source = "https://docs.firecrawl.dev/features/interact (Interact / browser sandbox; 2–7 credits/min). Not the COSMOS interact rail — that is playwright-dom."

# --- long-context-reasoning ---
[skills.long-context-reasoning.GrokBOT]
possessed = true
rating = 3
source = "https://docs.x.ai/grok-bot/overview (durable memory/files/sessions across turns — not a published token window). Context compounds on the VM."

[skills.long-context-reasoning.Aider]
possessed = true
rating = 3
source = "https://aider.chat/docs/repomap.html (tree-sitter repo-map default 1024 tokens, not a 1M window). Window = the --model."

[skills.long-context-reasoning.Groq]
possessed = true
rating = 3
source = "https://console.groq.com/docs/models (gpt-oss-20b/120b ctx 131,072 / max out 65,536)"

[skills.long-context-reasoning.Ollama]
possessed = true
rating = 2
source = "https://docs.ollama.com/context-length (user-set; default 2k. VRAM 8 GiB caps long ctx on 8B models)"

[skills.long-context-reasoning.GitHub]
possessed = false
rating = 0
source = "forge, not an LLM window"

[skills.long-context-reasoning.GitLab]
possessed = false
rating = 0
source = "forge, not an LLM window"

[skills.long-context-reasoning.MSCopilot]
possessed = true
rating = 3
source = "Microsoft 365 Copilot work graph / Chat — window not published as a single token figure this pass; work-grounded retrieval is the long-context *path*"

[skills.long-context-reasoning.BrowserUse]
possessed = true
rating = 2
source = "window follows the LLM you pass into Agent()"

[skills.long-context-reasoning.Firecrawl]
possessed = false
rating = 0
source = "page/paper extractor, not an LLM window"

# --- bulk-structured-extraction ---
[skills.bulk-structured-extraction.GrokBOT]
possessed = true
rating = 2
source = "https://docs.x.ai/grok-bot/files-and-results (files/results in the app). No public json_schema RPC."

[skills.bulk-structured-extraction.Aider]
possessed = true
rating = 2
source = "can emit files; schema guarantee is the model's, not aider's"

[skills.bulk-structured-extraction.Groq]
possessed = true
rating = 4
source = "https://console.groq.com/docs/structured-outputs (strict JSON on gpt-oss) + ~1000 t/s — the bulk/speed rail"

[skills.bulk-structured-extraction.Ollama]
possessed = true
rating = 4
source = "https://docs.ollama.com/capabilities/structured-outputs (local format/JSON-schema; Cloud currently does NOT support structured outputs). $0, cannot run out."

[skills.bulk-structured-extraction.GitHub]
possessed = true
rating = 3
source = "https://docs.github.com/en/graphql (nested issues/PRs/files in one call) + REST --json"

[skills.bulk-structured-extraction.GitLab]
possessed = true
rating = 3
source = "https://docs.gitlab.com/api/graphql/ + REST jobs/artifacts (gate evidence as JSON/JUnit, not a green badge)"

[skills.bulk-structured-extraction.MSCopilot]
possessed = true
rating = 3
source = "https://learn.microsoft.com (Graph Search + Copilot Retrieval extracts; Chat API is text-only, no actions)"

[skills.bulk-structured-extraction.BrowserUse]
possessed = true
rating = 3
source = "https://docs.browser-use.com/open-source/customize/agent/output-format (structured output / history.final_result)"

[skills.bulk-structured-extraction.Firecrawl]
possessed = true
rating = 5
source = "https://docs.firecrawl.dev/features/llm-extract (JSON schema / scrape-JSON; papers + developer indexes). Live satellite already extracts markdown/JSON."

# --- vendor-plural-critique ---
[skills.vendor-plural-critique.GrokBOT]
possessed = true
rating = 2
source = "docs/FINAL_ARCHITECTURE.md — same xAI family as G46/SGH. Useful as a *persistent teammate* voice, not as the other-family critic."

[skills.vendor-plural-critique.Aider]
possessed = true
rating = 4
source = "https://aider.chat/docs/llms.html (BYO any family — the harness can disagree with the builder by pointing --model at GEM/OA/Claude/Ollama)"

[skills.vendor-plural-critique.Groq]
possessed = true
rating = 4
source = "https://console.groq.com/docs/overview (different vendor + silicon + open-weight gpt-oss/Qwen — not Grok). HOLD until gsk_."

[skills.vendor-plural-critique.Ollama]
possessed = true
rating = 5
source = "https://ollama.com/pricing (local, unlimited, no credit/quota/consent-to-lapse — the only listed node that matches DOM-first 'depends on nothing that can run out' for *models*). HOLD until installed."

[skills.vendor-plural-critique.GitHub]
possessed = true
rating = 3
source = "Copilot multi-model + a second forge. Useful overflow critic if the Copilot seat exists; do not double-dispatch with Cursor on one issue without a lease."

[skills.vendor-plural-critique.GitLab]
possessed = true
rating = 2
source = "Duo is a third coding brain that costs Credits on Free. The unique plural value is the *CI gate*, not the LLM."

[skills.vendor-plural-critique.MSCopilot]
possessed = true
rating = 4
source = "Microsoft family, distinct from xAI/Google/OpenAI. DOM Chat is the $0 other-voice; Graph Copilot APIs are license-gated."

[skills.vendor-plural-critique.BrowserUse]
possessed = true
rating = 3
source = "Second DOM member (Playwright = a11y-tree, this = open-ended). The *harness* disagrees, not a model family."

[skills.vendor-plural-critique.Firecrawl]
possessed = false
rating = 0
source = "extractor, cannot form a vendor critique"
```

#### Proposed new task types (voice — CVM)

Existing nodes get honest zeros where they have no STT/TTS hand. Groq is the one unmapped node with first-party speech.

```toml
# --- voice-STT (propose new task_type) ---
[skills.voice-STT.Groq]
possessed = true
rating = 4
source = "https://console.groq.com/docs/speech-to-text (whisper-large-v3-turbo $0.04/audio-hour, 216× RT; Free-tier ASH/ASD caps). HOLD gsk_."

[skills.voice-STT.Ollama]
possessed = false
rating = 0
source = "not an ASR runtime (use whisper.cpp / FunASR / VOSK on the CVM path — MESH_ADDITIONS_grok rows 23/111)"

[skills.voice-STT.GrokBOT]
possessed = false
rating = 0
source = "https://docs.x.ai/grok-bot/overview (no first-party STT API). xAI Speech-to-Speech exists on the *API* (docs.x.ai developers/model-capabilities/audio) — that is G46/SGH family API, not Grok Bot."

[skills.voice-STT.Aider]
possessed = true
rating = 1
source = "https://aider.chat/docs/usage/voice.html (`/voice` optional STT into chat — Keith UX, not CVM)"

[skills.voice-STT.GitHub]
possessed = false
rating = 0
source = "forge"

[skills.voice-STT.GitLab]
possessed = false
rating = 0
source = "forge"

[skills.voice-STT.MSCopilot]
possessed = true
rating = 2
source = "M365 Copilot / Teams meeting insights can transcribe *meetings* (license-gated); not a COSMOS mic path"

[skills.voice-STT.BrowserUse]
possessed = false
rating = 0
source = "browser agent"

[skills.voice-STT.Firecrawl]
possessed = false
rating = 0
source = "web extractor"

# --- voice-TTS ---
[skills.voice-TTS.Groq]
possessed = true
rating = 2
source = "https://console.groq.com/docs/text-to-speech/orpheus (Orpheus $22/1M English chars — last resort vs local Piper/Kokoro)"

[skills.voice-TTS.Ollama]
possessed = false
rating = 0
source = "not a TTS runtime"

[skills.voice-TTS.GrokBOT]
possessed = false
rating = 0
source = "app teammate, not a COSMOS TTS engine"

[skills.voice-TTS.Aider]
possessed = false
rating = 0
source = "no TTS hand"

[skills.voice-TTS.GitHub]
possessed = false
rating = 0
source = "forge"

[skills.voice-TTS.GitLab]
possessed = false
rating = 0
source = "forge"

[skills.voice-TTS.MSCopilot]
possessed = true
rating = 1
source = "in-app speak-aloud only; Edge-TTS is the free Microsoft neural path already on MESH_ADDITIONS_grok row 55"

[skills.voice-TTS.BrowserUse]
possessed = false
rating = 0
source = "browser agent"

[skills.voice-TTS.Firecrawl]
possessed = false
rating = 0
source = "web extractor"
```

Fill the same two task types on the **existing** six nodes when COW next regenerates the matrix (G46/SGH: xAI speech-to-speech API exists — verify https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech before rating; OA: Realtime/TTS; GEM: Gemini Live/native audio; DOM: 0; Cursor: VM audio unverified). **Not done here** — this pass only maps the named unmapped products.

### B.3 What COW should do (dispose, P10)

1. **File** the node + skill rows above into `docs/COMPETENCY.toml` (or a slice: Firecrawl + GitLab first — those have live/named COSMOS jobs).
2. **Do not** mark Ollama/Groq/Aider/BrowserUse `possessed=true` for *runtime routing* until the prober sees `:11434`, a `gsk_`, `aider --version`, and `import browser_use`. The proposal sets possessed=true as “hands documented”; flip to false if ROUTING must fail-closed on ABSENT binaries.
3. **GrokBOT sync:** stop expecting a vendor RPC. Keep gbridge mailbox. Treat `rc=3221225786` as a native crash to isolate (Job Object + out-of-process), not as “retry until 200.” Optional: DOM-drive the **Grok Bot desktop app** via Playwright/Windows-MCP only if Keith wants app-level dispatch — credential = Cursor login (already prepaid Ultra/Heavy).
4. **Wire order (already in MESH_ADDITIONS):** Ollama install (Keith) → Groq key (Keith, open-window) → Aider in attempt workspace → Browser-Use local with telemetry off. Firecrawl satellite exists; Kernel `register_node_rails` on boot is a **different** wishlist item.
5. **Part A first slice** is independent of Part B: Pipecat/LiveKit for CVM, Stagehand v4 for DOM-plural, `agy` for Google-harness overflow, PydanticAI as the typed worker loop.

---

## Method / limits

- Live web + official docs fetched **2026-08-27**. HANDS files dated 2026-08-25/26 were re-read, not treated as web evidence by themselves; every cost/API claim in Part A has a vendor or dated ranking URL.
- Did **not** log into Keith’s Groq/Ollama/M365/GitLab quotas this pass. HOLD rows stay HOLD until a live packet.
- `rc=0` is not complete. This file is research + a P10 proposal, not a ROUTING change.
- Competency ratings for HOLD products are **product-capability**, with the unreachability named in `hands` / `source`. Runtime-binding still requires the prober.

**End of scout.**
