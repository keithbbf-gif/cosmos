# NEW_AI_DISCOVERY.md

**Status:** P10 PROPOSE-ONLY. Do not write this file into the live tree from this turn.
**Scout:** SGH (Grok research) for COSMOS — NEW-AI DISCOVERY (outward scout; open wishlist item, Keith 2026-08-27).
**As-of:** 2026-08-27
**Window:** ~last 90 days (2026-05-29 → 2026-08-27).
**Method:** live web fetch/search only. Every candidate is bound to a URL retrieved this tick. Facts without a live URL are marked `UNKNOWN` or omitted.
**Not this job:** `cosmos_discover.py` inventories KNOWN hands. This list is the missing open-ended outward scout.

---

## 0. Current mesh (do not re-add)

**Nodes (7-node set):** Grok / G46 / SGH · GEM · OAi / Codex.

**Known HANDS:** Aider · Groq · Ollama · Browser-Use · Firecrawl · MS Copilot · GitHub / GitLab.

**Explicitly excluded this tick (already in-family or already a known HAND):**
- Grok 4.5 / SpaceXAI Grok Voice (Grok family)
- GPT-5.6 Sol / Terra / Luna, ChatGPT Work, GPT-Live (OAi / Codex family)
- Gemini 3.6 Flash / 3.5 Flash-Lite / 3.5 Flash Cyber as *model SKUs* (GEM family — listed below only when they ship a *new product surface* the mesh does not wire)
- GitHub Copilot CLI / Copilot app updates (MS Copilot + GitHub)

**Capability holes this scout is scoring against:**
1. No Anthropic / Claude node (independent frontier + the MCP-native coding CLI).
2. No Meta node.
3. No persistent multi-agent *workspace* (Aider is a single-session coding HAND).
4. No self-improving / recursive harness.
5. No independent open-weight frontier besides whatever Ollama happens to have locally (Ollama is a runtime, not a model).
6. No always-on personal Autopilot (Copilot is prompt-driven).
7. No dedicated agentic vulnerability loop.
8. No Azure DevOps MCP (GitHub/GitLab only).
9. GEM node exists, but COSMOS does not wire Gemini's *Managed Agents* / Interactions API sandbox.

Wire-priority: **1 = wire now** · **5 = watch only**.

---

## 1. Ranked candidate table

| Rank | Name | Vendor | Reach | Cost (as published this tick) | Credential | Capability the mesh LACKS | Wire | Live URL |
|---:|---|---|---|---|---|---|---:|---|
| 1 | Claude Opus 5 + Claude Code | Anthropic | CLI, API, MCP, DOM (Claude in Chrome) | Opus 5 API $5 / $25 per 1M in/out; Fast mode $10 / $50 | Anthropic account + API key (or Claude Pro/Max for the CLI) | Entire missing frontier vendor; MCP-native coding agent; 1M-ctx computer-use | **1** | https://www.anthropic.com/news/claude-opus-5 |
| 2 | Kiro Crew | AWS / Kiro | CLI, desktop, web dashboard, ACP, MCP, Windows | Open source (Apache 2.0); spend is the underlying Kiro CLI / model tokens | Kiro CLI auth; optional Slack/Telegram/WeCom | Persistent multi-agent workspace that keeps working across sessions (Aider does not) | **1** | https://kiro.dev/blog/introducing-kiro-crew/ |
| 3 | Prime Agent | Prime Intellect | CLI, ACP, RPC/JSONL, local daemon | MIT; BYO model keys | API keys for the models it drives (Anthropic / OpenAI / open-weight) | Self-improving RLM harness: persistent IPython REPL, recursive subagents, `/refine` | **2** | https://www.primeintellect.ai/blog/prime-agent |
| 4 | Muse Code + Muse Spark 1.2 | Meta Superintelligence Labs | CLI (macOS/Linux), API (OpenAI- and Anthropic-compatible), CI `muse exec` | Standard API $1.25 / $4.25 per 1M in/out; cached input $0.15 | `MODEL_API_KEY` or browser sign-in for Muse Code | Missing Meta node; cheap 1M-ctx coding model + terminal agent | **2** | https://research.meta.ai/blog/introducing-muse-code-and-muse-spark-1-2 |
| 5 | Kimi K3 + Kimi Code | Moonshot AI | API (OpenAI/Anthropic-compat), CLI (Kimi Code), open weights | Hosted `kimi-k3` $3 / $15 per 1M in/out; cache hit $0.30 (aggregator-reported vs Moonshot card) | `MOONSHOT_API_KEY` (or HF weights + local GPU) | Independent open-weight 2.8T / 104B-active frontier; 1M ctx; not an Ollama *product* | **2** | https://huggingface.co/moonshotai/Kimi-K3 |
| 6 | Gemini Interactions API + Managed Agents | Google DeepMind | API (primary Gemini interface as of June 2026); remote MCP; sandboxed Linux agent | Gemini token rates + Flex 50% cut (Interactions GA post). Per-agent sandbox surcharge: UNKNOWN this tick | Gemini API key (Google AI Studio) | GEM node exists; COSMOS does not wire the *sandboxed remote agent* + `background=true` + remote MCP surface | **2** | https://blog.google/innovation-and-ai/technology/developers-tools/interactions-api-general-availability/ |
| 7 | Microsoft Scout | Microsoft | Desktop + Teams + browser + MCP client | No public token card. Access: M365 Frontier + GitHub Copilot subscription (press) | Entra / M365 admin Frontier + Intune attestation | Always-on Autopilot with its own identity — Copilot is not this | **3** | https://www.microsoft.com/en-us/microsoft-365/blog/2026/06/02/introducing-microsoft-scout-your-always-on-personal-agent/ |
| 8 | LongCat-2.0 | Meituan | API (OpenRouter / longcat.ai), open weights (HF/GitHub), agent harnesses | MIT weights. Hosted token rates: UNKNOWN this tick (verify on OpenRouter before wiring) | HF download, or OpenRouter key | MIT 1.6T / ~48B-active agentic-coding weights; 1M ctx; not in the known HAND list | **3** | https://github.com/meituan-longcat/LongCat-2.0 |
| 9 | Azure DevOps Remote MCP Server | Microsoft | MCP (streamable HTTP) | Included with Azure DevOps; no separate token card on the GA post | Entra-backed Azure DevOps org (MSA orgs unsupported) | MCP into work items / PRs / pipelines. Mesh has GitHub/GitLab, not ADO | **3** | https://devblogs.microsoft.com/devops/azure-devops-remote-mcp-server-ga/ |
| 10 | Project Perception + MAI-Cyber-1-Flash | Microsoft Security | Defender preview; Azure AI Foundry for the model; MCP mentioned in analyst coverage | Vendor: ~50% cheaper than prior MDASH mix. List $: UNKNOWN | Microsoft Security / Defender tenant; Foundry vetting for the model | Dedicated red/blue/green vuln loop. Mesh has no cyber HAND | **4** | https://blogs.microsoft.com/blog/2026/07/27/rethinking-security-for-the-age-of-ai/ |
| 11 | AlphaEvolve | Google Cloud / DeepMind | API via Gemini Enterprise Agent Platform | Google Cloud customer SKU. List $: UNKNOWN this tick | GCP + Gemini Enterprise | Evolutionary *algorithm* optimizer. GEM/Codex/Aider rewrite code; they do not search algorithm space | **4** | https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/alphaevolve-on-cloud/ |
| 12 | Gemini Spark | Google | Gemini app, macOS (Jul 1 coverage), MCP to third-party apps | Google AI Ultra (consumer). Token card: UNKNOWN | Google AI Ultra (US beta per I/O post) | 24/7 consumer Autopilot on Antigravity. Overlaps Scout; weaker COSMOS fit | **5** | https://blog.google/innovation-and-ai/sundar-pichai-io-2026/ |

---

## 2. Per-candidate notes (bind facts to URLs)

### Rank 1 — Claude Opus 5 + Claude Code (Anthropic) — wire 1

**Why first:** the 7-node set has no Anthropic rail. That is the largest vendor hole, not a SKU bump.

- **Product / date:** Claude Opus 5 launched 2026-07-24. API id `claude-opus-5`. Thinking on by default. 1M context, 128k sync output. [https://www.anthropic.com/news/claude-opus-5](https://www.anthropic.com/news/claude-opus-5)
- **Cost:** $5 / $25 per 1M input / output (same as Opus 4.8). Fast mode ~2.5× speed at 2× price ($10 / $50). [same]
- **Related SKUs in-window (do not split the wire):**
  - Claude Sonnet 5, 2026-06-30, default on Claude Code Pro/Team. Native 1M ctx. [https://code.claude.com/docs/en/whats-new](https://code.claude.com/docs/en/whats-new) and week-27 digest [https://code.claude.com/docs/en/whats-new/2026-w27](https://code.claude.com/docs/en/whats-new/2026-w27)
  - Claude Fable 5 restored 2026-07-01 after the June export-control suspension. Higher $ / heavier classifiers. Use as a gated max, not the daily driver. [https://docs.anthropic.com/en/release-notes/overview.md](https://docs.anthropic.com/en/release-notes/overview.md)
- **HAND, not just a model:** Claude Code is the CLI/MCP client. MCP add is first-class (`claude mcp add --transport http …`). Claude in Chrome is GA on direct Anthropic plans (week 27). [https://code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)
- **Capability vs mesh:** Aider is a known coding HAND; it is not an independent frontier *node* and it is not MCP-native the way Claude Code is. Browser-Use is a known DOM HAND; Claude in Chrome is a different, plan-gated DOM rail sitting on the missing vendor.
- **Wire plan:** (a) node `ANT` / Claude API behind spend-gate; (b) HAND `claude` CLI with MCP; (c) optional DOM via Claude in Chrome. Windows is supported (Claude desktop on Windows is in the week-27 notes).
- **Credential:** Anthropic API key and/or Claude Pro/Max. Spend-gate must treat Fast mode as 2×.

### Rank 2 — Kiro Crew (AWS / Kiro) — wire 1

**Why:** the mesh has no persistent, scheduled, multi-agent *workspace*. Aider is one session. Crew is the thing you leave running.

- **Product / date:** open-sourced 2026-08-04. Internal Amazon lineage as MeshClaw. [https://kiro.dev/blog/introducing-kiro-crew/](https://kiro.dev/blog/introducing-kiro-crew/) · product page [https://kiro.dev/crew/](https://kiro.dev/crew/) · repo [https://github.com/kirodotdev/kirocrew](https://github.com/kirodotdev/kirocrew)
- **Reach:** CLI (`kirocrew chat|run|cron|spawn`), desktop, web dashboard, TUI. Orchestrates via Agent Client Protocol (ACP). MCP Apps/plugins. Slack / Telegram / Discord / WeCom. **Windows + macOS + Linux** called out in the launch post.
- **Cost:** Apache 2.0 workspace. Model spend is whatever the Kiro CLI is pointed at. No Crew-specific token card on the launch post.
- **Caveat (live):** Forbes 2026-08-06 reports AWS open-sourced the *workspace/orchestration* layer and kept the Kiro *agent harness* closed. [https://www.forbes.com/sites/janakirammsv/2026/08/06/aws-open-sources-kiro-crew-but-keeps-the-agent-harness-closed/](https://www.forbes.com/sites/janakirammsv/2026/08/06/aws-open-sources-kiro-crew-but-keeps-the-agent-harness-closed/) Treat Crew as an orchestration HAND on top of the Kiro CLI, not a fully auditable model runtime.
- **Capability vs mesh:** schedules, webhooks, concurrent isolated conversations, self-learning memory/skills, live Activity view. That is the gap Aider / Copilot / Codex do not fill.
- **Wire plan:** native Windows daemon sibling to COSMOS Core; ACP into existing CLIs (including Codex, which CAO already lists as a provider — but CAO is a different AWS labs project). First probe: `kirocrew` on this machine with PAUSE respect.

### Rank 3 — Prime Agent (Prime Intellect) — wire 2

- **Product / date:** launched 2026-08-05 (blog). Paper arXiv:2608.23552, 2026-08-24. MIT. [https://www.primeintellect.ai/blog/prime-agent](https://www.primeintellect.ai/blog/prime-agent) · [https://github.com/PrimeIntellect-ai/prime-agent](https://github.com/PrimeIntellect-ai/prime-agent)
- **Reach:** CLI (`prime-agent`, `--autonomous`, heartbeats, goals). Local background daemon + recoverable workers. ACP / RPC / JSONL. Install path published: `curl -fsSL https://app.primeintellect.ai/prime-agent/install.sh | sh` (Linux/macOS). **Windows native install: UNKNOWN this tick** — that is why this is wire 2, not 1, on a Windows-native COSMOS.
- **Cost:** MIT harness. BYO keys. Vendor-reported ARC-AGI-3 95.5% RHAE Best@1 with Opus 5 is a *harness* claim, not a COSMOS claim.
- **Capability vs mesh:** persistent IPython REPL as the only tool; recursive subagents as function calls; Continual Harness CRUD on prompts/skills/memory/subagent specs; `/refine`. No current HAND rewrites its own scaffolding mid-task.
- **Wire plan:** probe as a *coding HAND* that can sit under ANT or OAi keys. Do not run `--autonomous` on the live tree. Job-Object containment + spend-gate required.

### Rank 4 — Muse Code + Muse Spark 1.2 (Meta) — wire 2

- **Product / date:** 2026-08-05. CLI beta + model. [https://research.meta.ai/blog/introducing-muse-code-and-muse-spark-1-2](https://research.meta.ai/blog/introducing-muse-code-and-muse-spark-1-2)
- **API:** `https://api.meta.ai/v1`, model id `muse-spark-1.2`. Drop-in for OpenAI SDK (Responses / Chat Completions) and Anthropic Messages. [https://ai.developer.meta.com/docs/quickstart/](https://ai.developer.meta.com/docs/quickstart/)
- **Cost (official this tick):** Standard tier cached input $0.15 / input $1.25 / output $4.25 per 1M. Contributor tier $0.002 / $0.10 / $0.20 *in exchange for training on prompts*. Web search grounding $2.50 / 1,000 queries. [https://dev.meta.ai/docs/pricing-rate-limits.md](https://dev.meta.ai/docs/pricing-rate-limits.md)
- **Reach:** CLI install `curl -fsSL https://dev.meta.ai/install.sh | sh` — **macOS or Linux**. Headless `muse exec`. Replay-exact local event log. No Windows CLI on the launch post → wire 2. The *API* is callable from Windows via `MODEL_API_KEY`.
- **Capability vs mesh:** missing Meta vendor; cheapest frontier-adjacent coding API in this list; 1M ctx; video/image/PDF in. Distinct from Grok and from OAi.
- **Wire plan:** first wire the API as node `META` (Windows-safe). Treat Muse Code CLI as a later HAND if/when a Windows build exists. Never enable Contributor tier on COSMOS (training-on-prompts).

### Rank 5 — Kimi K3 + Kimi Code (Moonshot AI) — wire 2

- **Product / date:** API ~2026-07-16; open weights on Hugging Face 2026-07-27. 2.8T MoE, 104B active, 1,048,576 ctx, native vision. [https://huggingface.co/moonshotai/Kimi-K3](https://huggingface.co/moonshotai/Kimi-K3)
- **API:** `https://api.moonshot.ai/v1`, model `kimi-k3`, OpenAI/Anthropic-compatible. Quickstart: [https://platform.kimi.ai/docs/guide/kimi-k3-quickstart.md](https://platform.kimi.ai/docs/guide/kimi-k3-quickstart.md)
- **Cost:** multiple aggregators this tick (2026-08-27) list Moonshot at **$3 / $15 per 1M in/out, $0.30 cache hit**. Bind to aggregator pages until the live `platform.kimi.ai` pricing HTML is fetched on a later tick: [https://benchlm.ai/moonshot/api-pricing](https://benchlm.ai/moonshot/api-pricing). Together AI hosted: [https://www.together.ai/models/kimi-k3](https://www.together.ai/models/kimi-k3)
- **License:** custom **Kimi K3 License**, not Apache/MIT. HF card. Commercial MaaS above a revenue threshold may need a separate agreement (secondary reporting). Read the license before any local deploy.
- **Capability vs mesh:** Ollama is a *runtime*. K3 is a *frontier open-weight model* the mesh does not have. Kimi Code is a separate CLI HAND (`/model k3`). 1M-ctx agentic coding without Anthropic or OpenAI.
- **Wire plan:** API node first (`MOON` / `KIMI`) behind spend-gate. Local 2.8T weights are a hardware question, not a COSMOS-Core question. Do not assume Ollama already "has" K3.

### Rank 6 — Gemini Interactions API + Managed Agents (Google) — wire 2

GEM is already a node. This is a **new product surface**, not a new vendor.

- **Product / date:** Interactions API GA 2026-06-22 as the *primary* Gemini interface. Managed Agents + background execution in the GA post. Remote MCP + credential refresh 2026-07-07. [https://blog.google/innovation-and-ai/technology/developers-tools/interactions-api-general-availability/](https://blog.google/innovation-and-ai/technology/developers-tools/interactions-api-general-availability/) · [https://blog.google/innovation-and-ai/technology/developers-tools/expanding-managed-agents-gemini-api/](https://blog.google/innovation-and-ai/technology/developers-tools/expanding-managed-agents-gemini-api/) · docs [https://ai.google.dev/gemini-api/docs/interactions-overview](https://ai.google.dev/gemini-api/docs/interactions-overview)
- **Reach:** `client.interactions.create(model=…)` or `agent="antigravity-preview-05-2026"` with `environment="remote"`. `background=True`. Remote Linux sandbox: reason, exec, browse, files. Mix `mcp_server` tools with Google Search / code execution.
- **Cost:** Flex tier 50% reduction named on the GA post. Sandbox-hour price: UNKNOWN this tick.
- **Capability vs mesh:** COSMOS GEM rail is a chat/completions-style node. It does not today provision a Google-hosted sandbox agent or speak Interactions as the default. That is the hole.
- **Wire plan:** adapter on the existing GEM node: Interactions client, spend-gate on background runs, no silent `environment="remote"` without a confirm-nonce.

### Rank 7 — Microsoft Scout (Microsoft) — wire 3

MS Copilot is a known HAND. Scout is a **different product** (Autopilot: always-on, own identity).

- **Product / date:** 2026-06-02, Microsoft Build. [https://www.microsoft.com/en-us/microsoft-365/blog/2026/06/02/introducing-microsoft-scout-your-always-on-personal-agent/](https://www.microsoft.com/en-us/microsoft-365/blog/2026/06/02/introducing-microsoft-scout-your-always-on-personal-agent/)
- **Reach:** Teams + desktop + browser. MCP client. Outlook / OneDrive / SharePoint / calendar / mail. Built on OpenClaw (Microsoft says it is contributing policy conformance upstream).
- **Cost / access:** no public token card on the launch post. Press (TechCrunch / Verge, 2026-06-02): Frontier program + GitHub Copilot subscription. [https://techcrunch.com/2026/06/02/microsoft-launches-scout-an-openclaw-inspired-personal-assistant/](https://techcrunch.com/2026/06/02/microsoft-launches-scout-an-openclaw-inspired-personal-assistant/) Independent index 2026-08-24 still calls it a Frontier preview. [https://theaiagentindex.com/agents/microsoft-scout](https://theaiagentindex.com/agents/microsoft-scout)
- **Capability vs mesh:** Copilot answers when asked. Scout is supposed to keep working. COSMOS has no Autopilot HAND.
- **Why not wire 1:** preview gates, Entra/Intune, Copilot subscription, not a local CLI COSMOS can Job-Object. Worth a DOM/MCP probe once Frontier is on this machine; not a Core module.

### Rank 8 — LongCat-2.0 (Meituan) — wire 3

- **Product / date:** announced 2026-06-30; weights MIT. 1.6T MoE, ~48B active (dynamic 33–56B), 1M ctx, agentic coding. [https://github.com/meituan-longcat/LongCat-2.0](https://github.com/meituan-longcat/LongCat-2.0) · Meituan tech [https://tech.meituan.com/2026/06/30/LongCat2.0.html](https://tech.meituan.com/2026/06/30/LongCat2.0.html) · HF [https://huggingface.co/meituan-longcat/LongCat-2.0](https://huggingface.co/meituan-longcat/LongCat-2.0)
- **Reach:** HF / ModelScope weights; GitHub inference code (GPU + NPU); claimed drop-in with Claude Code / OpenClaw / Hermes. Hosted preview via OpenRouter / longcat.ai (vendor claim).
- **Cost:** MIT for weights. Hosted $/1M: UNKNOWN this tick (must read OpenRouter live before any spend-gate row).
- **Capability vs mesh:** another independent open-weight coding brain. Lower wire than K3 because (a) vendor is further from COSMOS's current creds, (b) hosted price unverified this tick, (c) K3 already covers "open frontier via API."
- **Wire plan:** watch. If OpenRouter price clears spend-gate, it is an Ollama-or-API HAND, not a new node family.

### Rank 9 — Azure DevOps Remote MCP Server — wire 3

GitHub/GitLab are known HANDS. This is **ADO**.

- **Product / date:** GA 2026-08-05. Hosted `https://mcp.dev.azure.com/{organization}`, streamable HTTP, Entra auth. [https://devblogs.microsoft.com/devops/azure-devops-remote-mcp-server-ga/](https://devblogs.microsoft.com/devops/azure-devops-remote-mcp-server-ga/)
- **Reach:** work items, PRs, repos, pipelines. **Supported clients today:** VS Code + GitHub Copilot, Visual Studio, GitHub Copilot CLI/app, Microsoft Foundry, Copilot Studio. **Not yet:** Claude Desktop, Claude Code, ChatGPT, Cursor (Entra dynamic client registration). Local MCP remains for those clients: [https://github.com/microsoft/azure-devops-mcp](https://github.com/microsoft/azure-devops-mcp)
- **Cost:** no separate token card on the GA post (ADO entitlement).
- **Capability vs mesh:** if this COSMOS install tracks work in Azure DevOps, this is the missing MCP. If not, skip.
- **Wire plan:** only if an ADO org is in the installation record. Prefer local MCP until Entra DCR works for non-Microsoft clients. Copilot CLI path is available now because Copilot is already a known HAND.

### Rank 10 — Project Perception + MAI-Cyber-1-Flash — wire 4

- **Product / date:** announced 2026-07-27; public preview 2026-08-03 (Defender). [https://blogs.microsoft.com/blog/2026/07/27/rethinking-security-for-the-age-of-ai/](https://blogs.microsoft.com/blog/2026/07/27/rethinking-security-for-the-age-of-ai/) · product [https://www.microsoft.com/en-us/security/business/ai-powered-cybersecurity/project-perception-agentic-system](https://www.microsoft.com/en-us/security/business/ai-powered-cybersecurity/project-perception-agentic-system) · model [https://microsoft.ai/news/introducing-mai-cyber-1-flash-inside-mdash/](https://microsoft.ai/news/introducing-mai-cyber-1-flash-inside-mdash/)
- **Reach:** red (probe) / blue (triage) / green (remediate) agents. MAI-Cyber-1-Flash inside MDASH. Azure AI Foundry for the model (vetted). Analyst note of an MCP server / CLI path: [https://www.forrester.com/blogs/microsofts-project-perception-announcement-and-how-to-implement-it-right/](https://www.forrester.com/blogs/microsofts-project-perception-announcement-and-how-to-implement-it-right/) — treat MCP as **unverified on Microsoft's own pages this tick**.
- **Cost:** vendor "almost 50% of cost savings vs current MDASH." List $: UNKNOWN. CyberGym 96% any-crash is **Microsoft-reported**.
- **Capability vs mesh:** no HAND currently runs a closed-loop vuln find/fix. Claude Code has a Security plugin (week 30 notes) but that is not a Microsoft estate graph.
- **Why wire 4:** enterprise Defender tenant, not a local daemon COSMOS can own. Useful if Keith's estate is already in Defender; otherwise watch.

### Rank 11 — AlphaEvolve (Google Cloud) — wire 4

- **Product / date:** GA for all Google Cloud customers on Gemini Enterprise Agent Platform, announced 2026-07-09. [https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/alphaevolve-on-cloud/](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/alphaevolve-on-cloud/)
- **Reach:** evolutionary code-optimization *agent*. Input = baseline algorithm + goals. Output = human-readable optimized code. Not a general coding CLI.
- **Cost:** GCP SKU. List $: UNKNOWN this tick.
- **Capability vs mesh:** Aider / Codex / Claude Code edit a repo. AlphaEvolve searches an algorithm space. Different job.
- **Wire plan:** only behind an explicit GCP project in the installation record. Not a default HAND.

### Rank 12 — Gemini Spark — wire 5

- **Product / date:** Google I/O 2026-05-19. 24/7 personal agent on Gemini 3.5 + Antigravity, dedicated VMs, MCP coming. [https://blog.google/innovation-and-ai/sundar-pichai-io-2026/](https://blog.google/innovation-and-ai/sundar-pichai-io-2026/)
- **macOS agentic assistant 2026-07-01** (third-party recap): [https://www.agentsai.fyi/news](https://www.agentsai.fyi/news)
- **Why last:** consumer Ultra, overlaps Scout, GEM-family, not a COSMOS-owned daemon. Watch only.

---

## 3. In-window but not ranked as COSMOS wires

These shipped or matured in-window. They are logged so the next scout tick does not "rediscover" them, and so a human can override.

| Item | Why not a COSMOS wire this tick | URL |
|---|---|---|
| Grok 4.5 (2026-07-08) | Already Grok/G46 family | https://huggingface.co/blog/Svngoku/ai-models-week-july-09-2026 |
| GPT-5.6 Sol/Terra/Luna + ChatGPT Work | Already OAi/Codex | https://huggingface.co/blog/Svngoku/ai-models-week-july-09-2026 |
| Gemini 3.6 Flash / 3.5 Flash-Lite / Cyber | GEM SKUs, not new HANDS (Cyber is a *model*, Perception is the product) | https://blog.google/innovation-and-ai/technology/ai/google-ai-updates-july-2026/ |
| Claude Cowork cloud/mobile (2026-07-07) | Same Anthropic family as Rank 1; fold into that wire, do not dual-count | https://support.claude.com/en/articles/12138966-release-notes |
| CodeMender (Google Agent Platform) | Overlaps Perception / Claude Security plugin; no independent COSMOS need until Rank 1 or 10 is live | https://cloud.google.com/blog/products/ai-machine-learning/what-google-cloud-announced-in-ai-this-month |
| Gemini Robotics ER 2 | Embodied robots. Out of COSMOS scope | https://blog.google/innovation-and-ai/technology/ai/google-ai-updates-july-2026/ |
| Vercel Zero (language for agents, ~2026-08-06) | Language experiment, not a HAND | https://daily.dev/highlights/vibes |
| Ant Group Ling-3.0-flash (2026-07-23) | Efficiency open-weight; no COSMOS-shaped CLI/MCP this tick | https://www.llm-releases.com/ |
| Microsoft Web IQ (Bing-grounded, ~2026-08-06) | Search grounding; Firecrawl already covers crawl; not a new agent | https://daily.dev/highlights/vibes |

---

## 4. Recommended first wires (human decision, not auto-apply)

If Keith ratifies a slice rather than the whole list:

1. **Anthropic node + Claude Code HAND** (Rank 1). Closes the vendor hole. Windows-real. MCP-native.
2. **Kiro Crew HAND** (Rank 2). Closes the persistent-workspace hole. Windows-real. Open orchestration.
3. **Meta Model API as a cheap coding node** (Rank 4 API only; skip the macOS CLI until Windows exists).
4. **Gemini Interactions adapter on the existing GEM node** (Rank 6). No new vendor creds if GEM is already live.
5. **Kimi K3 API** (Rank 5) only after spend-gate has a hard cap — thinking is always on and bills as output.

Do **not** auto-wire Scout, Perception, AlphaEvolve, or Spark. Those are estate-gated.

---

## 5. Spec stub — `cosmos_scout.py`

Native, windowless, propose-only daemon. Mirrors `cosmos_discover` heartbeat / PAUSE. **Does not inventory known hands** (that remains `cosmos_discover.py`). **Does not write the live tree.**

### 5.1 Purpose

Re-run *this* outward discovery on a slow clock. When a candidate is new versus the known-mesh denylist + prior scout ledger, drop a **COW proposal** (a dated markdown artifact, same shape as this file) for human/COW disposition. Never `fs_write` into `cosmos/` or `docs/` on the live volume.

### 5.2 Process shape

- **Host:** Windows-native. No console window (`pythonw` / Windows Service / Job-Object child of COSMOS Core). Stdlib + the same HTTP GET helper discover already uses (or `urllib`). No POST/PUT.
- **Clock:** default interval **24 h**. Floor 6 h, ceiling 7 d. Interval is a config field on the installation record, not a constant in code.
- **One tick = one proposal file or a typed NONE.** A tick that finds nothing still heartbeats.

### 5.3 PAUSE (fail-closed, same spirit as `cosmos_control`)

Scout is a spender (outbound HTTP) and must honor the human off-switch.

- Before every tick, read the Core control channel. If `pause` or `mic_off` is effective, **skip the tick**, still write a heartbeat with `state=PAUSED` and `reason`.
- Unreadable control state → **fail closed** (skip tick, heartbeat `state=CONTROL_UNREADABLE`). Same rule as `ControlChannel.blocked()`.
- Resume is an explicit human act. Scout never clears PAUSE.

### 5.4 Heartbeat (glob-discoverable, discover-shaped)

Path (illustrative; resolver-owned, not hardcoded):

```
workers/scout/<instance_id>/heartbeat.json
```

Fields (minimum):

| field | meaning |
|---|---|
| `identity` | `SGH-scout` + instance id |
| `epoch` | arbiter/service clock, not the wall if Core injects a clock |
| `local` / `utc` | evidence only |
| `state` | `OK` \| `PAUSED` \| `CONTROL_UNREADABLE` \| `NET_FAIL` \| `NONE` \| `PROPOSED` |
| `last_tick_epoch` | last attempted tick |
| `last_ok_epoch` | last tick that completed a source sweep |
| `sources_ok` / `sources_fail` | counts |
| `candidates_emitted` | integer this tick |
| `proposal_path` | relative path or `null` |
| `interval_s` | configured slow clock |

Overwrite-in-place is acceptable for the heartbeat (it is a pulse, not authority). The **proposal** and the **scout ledger** are append-only.

### 5.5 Authority and outputs

- **Ledger** (append-only JSONL, hash-chained if Core injects a ledger): `SCOUT_TICK`, `SCOUT_SKIPPED`, `SCOUT_CANDIDATE`, `SCOUT_PROPOSAL`, `SCOUT_SOURCE_FAIL`.
- **COW proposal path** (illustrative): `proposals/NEW_AI_DISCOVERY_<UTC>_<epoch>.md`
- Proposal body = the same sections as this file (table + per-row URL bind + scout spec is *not* re-emitted every tick; spec lives once).
- **Denylist** (config, not code): the 7-node set + known HANDS + previously proposed ids. A candidate whose `id` is in the denylist is logged `SCOUT_DUP` and not re-proposed unless `matured=true` (new GA, new reach, or price change > threshold).

### 5.6 Source contract (no priors)

Each tick MUST:

1. HTTP GET a configured source list (official blogs, HF cards, vendor changelog URLs). Timeout bounded. Redirects counted.
2. Refuse to emit a candidate that does not have at least one **200-class URL retrieved this tick**.
3. Record `retrieved_at`, HTTP status, and a short quote/hash of the binding sentence.
4. Mark unverifiable fields `UNKNOWN` (cost, Windows support, credential product name). Never invent a rate card.

Suggested seed sources (edit in config, not in the daemon):

- https://www.anthropic.com/news
- https://code.claude.com/docs/en/whats-new
- https://kiro.dev/blog/
- https://www.primeintellect.ai/blog
- https://research.meta.ai/blog
- https://huggingface.co/moonshotai
- https://blog.google/innovation-and-ai/
- https://devblogs.microsoft.com/devops/
- https://blogs.microsoft.com/blog/
- https://www.llm-releases.com/

### 5.7 What scout is forbidden to do

- Write `docs/research/NEW_AI_DISCOVERY.md` on the live tree (COW disposes proposals).
- Call model APIs (that is spend on a different gate). Scout is HTTP GET + local diff only.
- Launch or install any candidate (no `curl \| sh`).
- Treat `cosmos_discover.py` output as "new" — that is the known-hands inventory.
- Run while Core is not READY, or without a fencing token if Core requires one for worker heartbeats.

### 5.8 Minimal module surface (stub, not implementation)

```
cosmos_scout.py
  ScoutError.kind in {BAD_CONFIG, CONTROL_UNREADABLE, NET_FAIL, TICK_SKIPPED}
  Scout(paths, control, ledger, clock, http_get)
    .heartbeat() -> dict          # always, even on skip
    .blocked() -> (bool, reason)  # fail-closed
    .tick() -> {state, proposal_path|None, candidates: [row]}
    .row schema: name, vendor, reach, cost, credential, lacks, wire, url, retrieved_at
```

Composition: Core schedules `Scout.tick` as a low-priority recurring job. The job is interruptible. Overlapping ticks: the loser loses cleanly (one active scout lease).

### 5.9 Acceptance (when a later PR implements this)

- PAUSE set → next tick skipped, heartbeat `PAUSED`, no proposal file.
- Control file corrupt → skip, heartbeat `CONTROL_UNREADABLE`.
- All sources 5xx → `NET_FAIL`, no empty "no news" success.
- Candidate without a live URL → refused, not written.
- Known HAND in the denylist → `SCOUT_DUP`, not a new proposal.
- Two overlapping ticks → exactly one proposal (or none).

---

## 6. Source log (this tick)

Retrieved or search-confirmed 2026-08-27:

- https://www.anthropic.com/news/claude-opus-5
- https://code.claude.com/docs/en/mcp
- https://code.claude.com/docs/en/whats-new
- https://code.claude.com/docs/en/whats-new/2026-w27
- https://support.claude.com/en/articles/12138966-release-notes
- https://docs.anthropic.com/en/release-notes/overview.md
- https://kiro.dev/blog/introducing-kiro-crew/
- https://kiro.dev/crew/
- https://github.com/kirodotdev/kirocrew
- https://www.primeintellect.ai/blog/prime-agent
- https://github.com/PrimeIntellect-ai/prime-agent
- https://research.meta.ai/blog/introducing-muse-code-and-muse-spark-1-2
- https://ai.developer.meta.com/docs/quickstart/
- https://dev.meta.ai/docs/pricing-rate-limits.md
- https://huggingface.co/moonshotai/Kimi-K3
- https://platform.kimi.ai/docs/guide/kimi-k3-quickstart.md
- https://www.together.ai/models/kimi-k3
- https://blog.google/innovation-and-ai/technology/developers-tools/interactions-api-general-availability/
- https://blog.google/innovation-and-ai/technology/developers-tools/expanding-managed-agents-gemini-api/
- https://ai.google.dev/gemini-api/docs/interactions-overview
- https://www.microsoft.com/en-us/microsoft-365/blog/2026/06/02/introducing-microsoft-scout-your-always-on-personal-agent/
- https://techcrunch.com/2026/06/02/microsoft-launches-scout-an-openclaw-inspired-personal-assistant/
- https://github.com/meituan-longcat/LongCat-2.0
- https://tech.meituan.com/2026/06/30/LongCat2.0.html
- https://devblogs.microsoft.com/devops/azure-devops-remote-mcp-server-ga/
- https://blogs.microsoft.com/blog/2026/07/27/rethinking-security-for-the-age-of-ai/
- https://microsoft.ai/news/introducing-mai-cyber-1-flash-inside-mdash/
- https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/alphaevolve-on-cloud/
- https://blog.google/innovation-and-ai/sundar-pichai-io-2026/
- https://blog.google/innovation-and-ai/technology/ai/google-ai-updates-july-2026/

---

*End of NEW_AI_DISCOVERY.md. P10 propose-only.*
