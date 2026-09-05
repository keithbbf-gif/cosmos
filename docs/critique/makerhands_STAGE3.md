# Maker-hands sweep — Motif STAGE-3 critique/rank (G46) + STAGE-2 ARCH (which to wire)

**Reviewer (rank):** G46 (Grok Build), dispatched `motif_makerhands_s3` 2026-08-25T22:42:11-05:00.
**Architect (this pass):** G46 (Grok Build), dispatched `motif_makerhands_s6` 2026-08-25T23:12:02-05:00 — tracker next-stage text is **2 arch, not stage 6**. ARCH lives in this file because the work order names `docs/critique/makerhands_STAGE3.md` (not `docs/arch/`). Same-family as the rank (H1 still open).
**Question:** which researched hands should ARCH wire, in what order, as what kind of surface — not "is this good research."
**Decided target (wishlist / DHx / tracker):** sweep GitHub/GitLab + 12 makers; wire the useful ones as COSMOS rails/nodes. Artifact: `docs/research/*_HANDS.md`. Next-stage text on dispatch: *2 arch: which to wire (rubric+WAVE A in STAGE3; satellite workers first; Dispatcher rails blocked on Kernel attach) · not stage 6*.
**Core:** `cosmos_kernel` / `cosmos_ledger` / `cosmos_sched` / `cosmos_service` were not edited. This file is docs-only. Satellite rank + satellite ARCH; no rail registration.

**Family note (process, not a packet defect):** Motif stage 3 is a *critique/rank* of the research packet. Every `*_HANDS.md` in this packet was also written by G46. This is **not** a second family's vote. COW still owes a non-Grok-Build pass (gem-api and/or oa-api) before treating the rank as consensus. Same-family rank is still bound to files + host-side probes below.

`rc=0` on a maker-docs job is not complete. Stage 6 is a value only the live tree can emit *for a wired COSMOS hand* (e.g. `GET http://127.0.0.1:11434/api/version` JSON, `glab ci status` SHA matching HEAD, Playwright `tools/list` from a COSMOS worker). A host spawn of `@playwright/mcp` is evidence for ARCH, not a wired rail. This row has **not** passed stage 6.

---

## Verdict

**Research packet is on disk and is usable as ARCH input. It is not a live-mesh claim. Wire satellite workers first. Do not add Dispatcher `ApiRail`s until Kernel attach exists (BACKLOG; this job cannot modify kernel).**

The 14 named HANDS files (GitHub + GitLab + 12 makers) plus bonus `GCLOUD_HANDS.md` are present, dated 2026-08-25, docs-grounded, and consistently mark themselves **not live-probed**. MESH_ADDITIONS rows for Ollama/Groq/Playwright/browser-use/Aider/Firecrawl/MCP remain UNVERIFIED against a live install; the HANDS files are the vendor-doc verification those rows asked for, **not** the live probe.

This critique adds host-side ground truth (2026-08-25, this process) that the scouts mostly did not have. That ground truth **changes the wiring order**: several "highest" research rows are blocked on a missing binary or a missing key; several "install first" rows are already authenticated on this machine.

Until ARCH designs the worker vs Dispatcher split against the Kernel-attach gap, this row stays DRAFT. Do not treat a HANDS.md "recommended stack" as shipped.

---

## Packet assertion (the research this rank uses)

Host-side `Get-ChildItem docs/research/*HANDS.md` this critique:

| file | bytes | mtime (local) | DHx maker |
|---|---:|---|---|
| `GITHUB_HANDS.md` | 33502 | 21:52:03 | GitHub (forge) |
| `GITLAB_HANDS.md` | 41821 | 21:52:20 | GitLab (forge) |
| `ANTHROPIC_HANDS.md` | 40940 | 21:59:00 | Anthropic |
| `AIDER_HANDS.md` | 48104 | 21:58:05 | Aider |
| `BROWSER_USE_HANDS.md` | 49984 | 22:05:35 | browser-use |
| `FIRECRAWL_HANDS.md` | 41971 | 22:10:53 | Firecrawl |
| `MCP_REFERENCE_SERVERS_HANDS.md` | 42279 | 22:10:56 | MCP |
| `OLLAMA_HANDS.md` | 40161 | 22:15:41 | Ollama |
| `GOOGLE_GEMINI_HANDS.md` | 35050 | 22:15:14 | Google |
| `GROQ_HANDS.md` | 34696 | 22:20:13 | Groq |
| `OPENAI_HANDS.md` | 44532 | 22:21:40 | OpenAI |
| `MICROSOFT_COPILOT_HANDS.md` | 38618 | 22:24:36 | Copilot (M365) |
| `PLAYWRIGHT_MCP_HANDS.md` | 39105 | 22:26:09 | Playwright |
| `XAI_GROK_HANDS.md` | 46763 | 22:32:48 | xAI |
| `GCLOUD_HANDS.md` | 32068 | 22:50:10 | gcloud (BACKLOG extra, not in the 12) |

**12/12 makers + 2/2 forges present. No stub files.** Smallest is GitHub (33.5 KB). All scouts: G46, 2026-08-25, "no COSMOS core edited," "not a live-mesh claim."

DHx named makers: Anthropic / xAI / Google / OpenAI / Copilot / Ollama / Groq / Playwright / browser-use / Aider / Firecrawl / MCP. Copilot in DHx is covered by `MICROSOFT_COPILOT_HANDS.md` (M365 Graph/Studio/Foundry). GitHub Copilot CLI/cloud-agent lives in `GITHUB_HANDS.md` rows 21–25, not the M365 file. That split is correct; ARCH must not conflate the two wallets.

---

## Decision rubric (ARCH uses this first — no peeking past it)

Rank a hand **to wire** only if all of:

1. **It is a hand** — CLI / REST / MCP / DOM with a named verb. Chat chrome is out (every scout already applied this).
2. **Free or prepaid beats metered** at equal power. A surface that can run out (credits, weekly pool, Vertex expiry 2026-10-13, Groq 429) ranks below one that cannot (local Ollama, local Playwright, `gh`/`glab` REST).
3. **Satellite before Kernel.** This assignment cannot modify kernel/ledger/sched/service. `Kernel.__init__` does not call `register_node_rails` (`docs/BACKLOG.md`, `docs/COSMOS_INDEX.md`). A new `ApiRail` in `cosmos_node_rails.py` would still not attach on normal boot. **Wire queue-native workers, MCP-host configs, and CLI jobs first.** Dispatcher rails are a *later* ARCH slice, gated on the Kernel-attach BACKLOG item (Keith's call, not fire-and-forget).
4. **One authority.** Forge CI, MCP, and coding agents publish through the fenced commit gateway. No second ledger writer. GitLab CI is an executable gate; it is **not** the runtime-binding gate (only this machine is).
5. **Already-on-mesh is not "new."** `sgh-api` / `gw-api` / `gem-api` / `oa-api` + `claude -p` + `grok -p` + Cursor Cloud Agents stay. Rank *deltas* (settle `cost_in_usd_ticks`, Studio Flash sibling, Responses shape), not re-registration.
6. **UNKNOWN is a typed hole**, not a guess. Missing binary, missing key, unread quota page, unread license = do not invent a green path.
7. **Vendor-plural where it adds a disagreeing member**, not a fifth copy of chat. DOM a11y vs open-ended browser vs prepaid search; local weights vs metered; GitLab gate vs GitHub mirror.
8. **Elegance.** A new coding-agent lane that duplicates Claude Code + Grok Build + Cursor without a distinct wallet or edit-protocol is a tax. Aider earns a slot because it auto-commits SEARCH/REPLACE in the attempt repo (maps onto the fence). OpenCode/Goose from MESH_ADDITIONS_grok are **out of this packet** — do not sneak them in from a different scout.

---

## Live-tree probes (this critique, 2026-08-25) — not a stage-6 pass

Host-side, this process. Secrets not printed.

| probe | result | implication |
|---|---|---|
| `git rev-parse --short HEAD` | `56fa423` | Rank bound to this commit. |
| `live/config/` file names | `api_token.txt`, `cursor_cosmos_key.txt`, `cursor_rail.json`, `cursor_rail_probe.json`, `install_key.bin`, `install_record.json` | **No** `groq_api_key`, `OLLAMA_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, Firecrawl `fc-`, browser-use `bu_`. Keith has not dropped those maker keys into COSMOS config. |
| `Get-Command ollama` | `NOT_ON_PATH` | Ollama rail cannot be probed. |
| `GET http://127.0.0.1:11434/api/version` | **timeout** (`OLLAMA_DOWN`) | MESH row 1 still UNVERIFIED on this machine. Highest *new* capability is **install-blocked**. |
| `Get-Command gh` | `C:\Program Files\GitHub CLI\gh.exe` | Worker-ready. |
| `gh auth status` | logged in `keithbbf-gif` (keyring); scopes `gist`, `read:org`, `repo`, `workflow`; protocol https | GitHub hand **auth is live**. |
| `gh repo view keithbbf-gif/cosmos --json isPrivate` | **`isPrivate: true`** | GITHUB_HANDS recommended public = $0 Actions minutes. Live repo is **private**. Private hosted minutes burn the Free 2,000/mo (or need a self-hosted runner). Do not copy the "keep it public" stack blindly. |
| `.github/workflows` | **missing** | No GitHub Actions to dispatch yet. |
| `Get-Command glab` | `...\Programs\glab\glab.exe` | Worker-ready. |
| `glab auth status` | logged in `keithbbf-gif` (keyring); API https `gitlab.com/api/v4`; git over **ssh** | GitLab hand **auth is live**. |
| `.gitlab-ci.yml` | **exists** | Motif gate file is in the tree. |
| `glab ci status` | pipeline **success**, 41s, URL `https://gitlab.com/keithbbf-gif/cosmos/-/pipelines/2790929269`, SHA `419bfb5e5a6f21d85da96a663b4572945d64cedd` | CI runs. **SHA ≠ HEAD `56fa423`.** A green pipeline on an older SHA is not runtime binding of this tree. Remaining hosted minutes: **UNKNOWN** (did not read Usage quotas; GITLAB_HANDS already marked that UNKNOWN). |
| `git remote -v` | `origin` = `github.com/keithbbf-gif/cosmos.git`; `gitlab` remote present | Two forges. **Hygiene:** the GitLab remote URL embeds a `glpat-` token in the userinfo field. That belongs in keyring / `live/config/`, not in `git remote -v` output. Do not commit it. Keith rotates if this remote was ever logged. Token value not repeated here. |
| `Get-Command grok` | `C:\Users\Papa\.grok\bin\grok.exe` · `grok 1.0.5 (5115b46bc9) [stable]` | Overflow coding CLI is installed. |
| `Get-Command claude` | `C:\Users\Papa\.local\bin\claude.exe` · `2.1.220 (Claude Code)` | Prepaid coding / `cosmos_brain.py` path is installed. |
| `Get-Command codex` | `...\npm\codex.ps1` | Codex CLI **binary present**. ChatGPT-seat vs `oa-api` wallet: **UNKNOWN** (`codex login status` not run this pass). |
| `Get-Command gemini` | `...\npm\gemini.ps1` | Gemini CLI **binary present**. Studio key vs Vertex ADC: **UNKNOWN** (no `GEMINI_API_KEY` in `live/config/`; GCLOUD_HANDS says ADC exists for `joanna.bbf@gmail.com`). |
| `Get-Command aider` | `NOT_ON_PATH` | Aider is install-blocked. |
| `Get-Command playwright` | `NOT_ON_PATH` | Expected: use `npx @playwright/mcp`, not a global `playwright` CLI. |
| `Get-Command node` | `C:\Program Files\nodejs\node.exe` · `v24.18.0` | Meets Playwright MCP engines `>=18` (docs prefer 20+). |
| `Get-Command npx` | present (`npx.ps1`) | MCP stdio spawn path exists. `npm view` from this PowerShell hit **ExecutionPolicy** on `npm.ps1` — do not treat npm-registry re-probe as done here; PLAYWRIGHT_HANDS already bound `@playwright/mcp@0.0.79` on 2026-08-25. |
| `register_node_rails` specs (`cosmos/cosmos_node_rails.py`) | exactly four: `sgh-api`, `gem-api`, `gw-api`, `oa-api` | Matches MESH_ADDITIONS baseline. No ollama/groq/anthropic rail in code. |

These numbers prove binaries and auth. They do not prove a wired COSMOS worker.

---

## Already on the mesh — do **not** re-add

| surface | evidence | what ARCH may still do (delta, not a new maker) |
|---|---|---|
| `sgh-api` / `gw-api` | `cosmos_node_rails.py` specs; SELFTEST live dispatch | Settle spend from xAI `cost_in_usd_ticks` (XAI_HANDS #24). Grow new work onto Responses. Unset leftover `XAI_API_KEY` in Grok Build env so SuperGrok pool is used. |
| `gem-api` (Vertex) | same; GCLOUD_HANDS: ADC exists, `aiplatform.googleapis.com` enabled, account `joanna.bbf@gmail.com`, credit MESH-expires **2026-10-13** | Keep spend-gated. Remaining dollars: **UNKNOWN** (gcloud billing list does not return them; DOM reports). Do not split the $300 onto partner MaaS / Studio — credit cannot pay those (GCLOUD_HANDS + GEMINI_HANDS). |
| `oa-api` | same; MESH cap $5 | Speak Responses, not Chat Completions, for new work. **Assistants API shuts down 2026-08-26** (OPENAI_HANDS) — do not add an Assistants client. |
| `claude -p` | `cosmos/cosmos_brain.py`; claude 2.1.220 on PATH | Keep prepaid coding/review. `--output-format json`, capture `session_id`. Unset `ANTHROPIC_API_KEY` in that env so the seat is used. |
| `grok -p` | grok 1.0.5 on PATH; ROUTING overflow default | Keep. `--output-format json`. Do not use `/loop` as the mesh clock. |
| Cursor Cloud Agents | DHx + CURSOR_LANE.md; `--gate` live `/v1/me` 200 | Already a coding overflow. Lease vs Copilot cloud agent / Claude GitHub Action / Gemini Action so they do not double-write a branch. Kernel attach of `cursor-api` remains BACKLOG. |
| `cosmos_browser` | `cosmos/cosmos_browser.py` | DOM rail exists (`--dump-dom` class). Playwright MCP is the *upgrade*, not a first DOM. |

---

## Rank — which to wire (ARCH input)

Power here is **new COSMOS capability**, not vendor marketing. Cost is the wallet that would actually bill. **Reach** is the only legal path under the no-kernel constraint.

### WAVE A — wire first (auth or binary already live; satellite; $0 tool)

| # | hand | kind | why this rank | reach (no kernel) | blocker / UNKNOWN |
|---|---|---|---|---|---|
| **A1** | **GitLab `glab` + pipeline artifacts + webhook** | CLI + CI + inbound HTTP | Motif named GitLab as the executable gate (`MOTIF.md`, FINAL_ARCHITECTURE § GitLab CI after `glab auth login`). Auth is live. `.gitlab-ci.yml` exists. A pipeline has succeeded. Highest *on-mission* forge hand. | Queue worker: `glab ci run` / `glab ci status --wait` / `glab job artifact`. Return-watcher: project webhook `pipeline_events`+`job_events` (GITLAB_HANDS #7). Self-hosted **project runner** so the 400 hosted minutes are not the clock (GITLAB_HANDS #1). | Remaining hosted minutes: **UNKNOWN**. Latest success SHA `419bfb5e` ≠ HEAD `56fa423`. Webhook ingress URL (Tailscale/`cosmos up`) **UNKNOWN** if live. Duo Credits: **do not buy**. |
| **A2** | **GitHub `gh` (issues/PRs/api)** | CLI | Second forge already connected; `gh auth` live; scopes include `repo`+`workflow`. Coordination surface (issues/PRs) is free at 5k REST/hr. | Queue worker: `gh issue` / `gh pr` / `gh api`. Prefer `gh` over raw curl (GITHUB_HANDS #1). | **Repo is private** — do not enable hosted Actions as $0. No `.github/workflows` yet. Copilot cloud-agent = credits, not this row. |
| **A3** | **Playwright MCP `@playwright/mcp`** | MCP stdio + DOM | Canonical DOM upgrade over `cosmos_browser` dump-dom. $0 Apache-2.0. Node v24 present. npm `0.0.79` bound in the scout. Vendor-plural with browser-use later. | Spawn from Claude Code / Grok Build / Cursor MCP host **or** a COSMOS MCP-client worker: `npx -y @playwright/mcp@latest --headless --isolated --browser chromium --caps=network,storage --output-dir <attempt>/pw` (PLAYWRIGHT_HANDS default flags). | First `tools/list` on this box: **not run** (npm.ps1 ExecutionPolicy blocked a registry re-probe). Browser binary download on first use: **UNKNOWN** until spawned. |
| **A4** | **MCP Fetch (reference `mcp-server-fetch`)** | MCP stdio | Cheap URL→markdown before Playwright. $0. Official live reference (not archived). | `uvx mcp-server-fetch` or pip package; allowlist hosts (SSRF). | Spawn **not run**. Python SDK pin `mcp>=1.29.0,<2` (MCP_HANDS). |
| **A5** | **xAI Docs MCP + OpenAI Docs MCP** | hosted MCP, no key | Free docs hands so agents stop using stale copies. | Point Grok Build / Claude Code / Cursor at `https://docs.x.ai/api/mcp` and `https://developers.openai.com/mcp`. | Config files not inspected this pass. |

### WAVE B — wire next (binary present, wallet UNKNOWN — probe then attach as worker)

| # | hand | kind | why | reach | UNKNOWN that ARCH must not guess |
|---|---|---|---|---|---|
| **B1** | **Gemini CLI `gemini -p --output-format json`** | CLI + agent | Fourth coding-agent lane; binary on PATH. Distinct from Vertex `gem-api` if authenticated with a **Studio** key (free Flash RPD). | Queue worker in attempt workspace. | Auth method: Google-login vs `GEMINI_API_KEY` vs Vertex ADC. Unpaid Google-login path **migrated to Antigravity CLI 2026-06-18** (GEMINI_HANDS) — do not build on that. No Studio key in `live/config/`. |
| **B2** | **Codex CLI `codex exec --json --sandbox workspace-write`** | CLI + agent | Fifth coding-agent lane; binary on PATH. Apache-2.0. Distinct wallet = ChatGPT seat (if any) vs `oa-api`. | Queue worker. Prefer ChatGPT login so it does not burn `oa-api`. | Whether a ChatGPT Plus/Pro seat exists: **UNKNOWN**. `codex login status` not run. |
| **B3** | **Grok Build MCP host → GitLab/GitHub/Playwright** | MCP client on existing CLI | Gives G46 forge+DOM tools without Core growing clients. grok 1.0.5 is installed. | `grok mcp add` / project `.mcp.json`. | What is already in `~/.grok/` : **UNKNOWN**. `--bare`/sandbox still required for unattended jobs. |

### WAVE C — install-blocked (highest new *capability*, not highest *now*)

| # | hand | kind | why it still ranks high | what Keith must do (money/credentials/install — not a bat) | COSMOS after that |
|---|---|---|---|---|---|
| **C1** | **Ollama local `ApiRail` `ollama-local`** | local HTTP | Only candidate immune to quota/billing/consent-to-lapse (canon). OpenAI-compat drop-in on `:11434`. MESH #1. | Install Ollama Windows app (Keith). Pull a small tool model. Leave `OLLAMA_NO_CLOUD=1` until he opts in. | Probe `GET /api/version` + `/api/tags` + `/api/ps`. Worker via OpenAI shim **or** native `/api/chat`. Dispatcher registration waits on Kernel attach. VRAM: **UNKNOWN** — do not pull 30B until `ollama ps` exists. Default until then: `llama3.2` / `qwen3:8b` / `embeddinggemma` per OLLAMA_HANDS. |
| **C2** | **Aider `aider --yes-always --message`** | CLI coding agent | Distinct protocol: SEARCH/REPLACE + **one git commit per edit** in the attempt repo. Maps onto fenced commit. Apache-2.0, BYO existing rails (incl. future Ollama). | Keith `aider-install` (isolates its own Python). | Queue worker, `--subtree-only`, `--analytics-disable`, `--read` conventions. `--no-auto-commits` if Core will commit. |
| **C3** | **Groq `groq-api` Free** | OpenAI-compat HTTP | Speed class the mesh does not have (LPU). Free = no card, 429 when over (not a hidden bill). Default model **`openai/gpt-oss-20b`** — Mixtral/Llama-4 are **dead** on Free/Dev (GROQ_HANDS, do not copy MESH's older Llama blurb). | Keith mints `gsk_` at console.groq.com/keys; store `live/config/groq_api_key.txt`. | Worker HTTP through spend-gate budget **$0**. Probe `GET /models`. Persist `x-ratelimit-*`. Dispatcher rail waits on Kernel attach. Live org limits: **UNKNOWN** until Console Limits page is read. |

### WAVE D — capability gaps, metered or license-gated (ARCH designs, does not enable)

| # | hand | why later | constraint |
|---|---|---|---|
| **D1** | **Anthropic Messages `anthropic-api`** | Closes MESH #17: Claude is only reachable via F5/`claude -p`, never Dispatcher. | Real money after tiny new-account credits. Keith mints `sk-ant-api`. Spend-gate. Do not put this key in the `claude -p` environment (steals the seat). Kernel attach required for a true rail. |
| **D2** | **Gemini Studio Flash sibling** | Wallet that survives Vertex credit death **2026-10-13**. Free Flash RPD. | Distinct from `gem-api`. Studio ToS (free may train). Keith mints **auth key** (standard keys die Sep 2026). |
| **D3** | **Firecrawl keyless MCP** then paper endpoints | Chapter-4 citation / URL→markdown. Research Index papers **free on every plan**. | Keyless = per-IP daily cap **unpublished** (FIRECRAWL_HANDS). 429 is correct. Cloud credits do not roll over. AGPL: keep self-host as a **separate process**, never fold into Core. |
| **D4** | **browser-use OSS Agent** (local Chromium + Ollama or existing rails) | Vendor-plural DOM: open-ended vs Playwright a11y. | `ANONYMIZED_TELEMETRY=false` required. Cloud MCP **out** (trains; MESH_ADDITIONS_grok). Depends on C1 or a metered LLM. |
| **D5** | **GitHub App webhook + `repository_dispatch`** | Interrupt-driven GitHub return-watcher; $0 API. | Needs an App (Keith) + public ingress. Private-repo Actions still cost minutes — skip hosted Actions until a self-hosted runner or a public mirror. |
| **D6** | **M365 Graph Search + Graph CRUD** | Free M365 hands (mail/files/calendar) if Keith's seat is eligible. | Eligibility **UNKNOWN**. Copilot Chat API / Retrieval need the **$30 add-on** or PAYG — do not enable those without Keith. DOM Copilot Chat is the license-free LLM fallback. |
| **D7** | **gcloud worker (Vertex ops, not new inference)** | Same $300 wallet. `gcloud` 578.0.0 + ADC already live (GCLOUD_HANDS). | Watch credit in Billing reports (DOM). Enable Run/Scheduler/Tasks only if ARCH needs them; they are **not enabled** today. Partner models **cannot** draw the welcome credit. |

---

## Do not wire this cycle

| rejected | bound reason |
|---|---|
| **Grok Bot / GBt REST** | XAI_HANDS #52: **not documented**. Mailbox remains. Inventing `team_id` RPC is fabricated compliance. |
| **GitLab Duo / Credits / Orbit MCP** | Free namespace has $0 included Credits. Cursor Ultra + Grok Build have headroom. New bill. |
| **GitHub Copilot cloud agent as default** | Credit-metered; Free = limited. Cursor Cloud Agents already prepaid. Lease if ever used. Repo private → Actions minutes too. |
| **OpenAI Assistants / Fine-tunes / Sora / Completions** | Assistants **shuts 2026-08-26**. Fine-tune closed to new orgs. Sora shuts 2026-09-24. |
| **Antigravity CLI (`agy`)** | GEMINI_HANDS: do not build COSMOS on it until Keith chooses. Prefer OSS `gemini` + key. |
| **n8n / Zapier as orchestrator** | Second scheduler. Canon: one authority. |
| **OpenRouter rotating `free`** | Silent model rotation. Contradicts no-silent-fallback. |
| **MCP reference Filesystem/Git replacing Core pathlib/git** | Educational, not production (official warning). BTS `fs_*` and native `git` already exist. Fetch + Time only as agent tools. Memory must not write `SEED.json`. |
| **Playwright `browser_run_code_unsafe` as default** | RCE in the server process. Job-Object + allowlist or not at all. |
| **browser-use Cloud / Cloud MCP** | Metered; trains on inputs. |
| **Firecrawl Smart Upgrade** | Auto-spend. COSMOS default **off**; fail-closed 402. |
| **Microsoft Copilot Chat API / Studio as daily driver** | $30 seat or Credits. Graph Search is the free hand if Entra exists. |
| **Vertex Express / Foundry Grok / Azure OpenAI** | Would split wallets already owned (`gem-api`, `oa-api`). Azure credit remaining: **UNKNOWN**. Inference beta SDK retires 2026-08-26. |
| **`gcloud ai-platform` (legacy ML Engine)** | GCLOUD_HANDS: ranked last among named groups. Not Vertex. |
| **Dispatcher `ApiRail` registration as the first commit** | Kernel does not attach rails. A green `register_node_rails` edit without Kernel compose is a false green. |

---

## Critique of the research packet itself (HIGH / MED / UNKNOWN)

### HIGH

**H1 — Same family wrote research and this rank.**
Every HANDS file is G46. Motif vendor-plural is not satisfied. gem-api and oa-api still owe an independent rank against the same rubric. Contested items below should go to Keith only after a second family disagrees, not before.

**H2 — "Wire as COSMOS rails" collides with Kernel attach.**
Wishlist + BACKLOG say "wire as COSMOS rails." `register_node_rails` is a no-op on normal boot. ARCH that starts by editing `cosmos_node_rails.py` will produce an artifact the machine does not execute — the exact false-green class `docs/PIPELINE_CRITIQUE_MERGE.md` forbade. Rank above forces **worker-first**.

**H3 — GitHub HANDS assumed a public repo; live `keithbbf-gif/cosmos` is private.**
Actions-on-public = $0 is false for this tree. Any ARCH that copies GITHUB_HANDS recommended stack step 4 (`workflow_dispatch` on public = $0 minutes) without a self-hosted runner or a visibility change will burn private minutes or silently no-op.

**H4 — Ollama is ranked #1 new rail in MESH + OLLAMA_HANDS and is not on this machine.**
`NOT_ON_PATH` + `:11434` timeout. Treating C1 as "ready to code" is a guess. ARCH may *design* the rail; BUILD of the rail waits on Keith's install.

**H5 — Two-wallet theft is documented in four makers and is not yet a COSMOS control.**
Claude Code, Grok Build, Codex, Gemini CLI all warn: a leftover API key in env **steals** the prepaid seat. `live/config/` has no those keys, which is safer for CLI seats — and means metered rails have **no** COSMOS-owned credential either. ARCH must specify env isolation per job (`--bare` / `--ignore-user-config` / unset vs set), not hope.

### MEDIUM

**M1 — GitLab CI success is not bound to HEAD.**
Pipeline 2790929269 SHA `419bfb5e` vs HEAD `56fa423`. A green badge on an old SHA is the C-48 class. ARCH of A1 must define the runtime-binding value (job artifact / nonce / `py_compile` output hash) and require it on the SHA the fence just published.

**M2 — GitLab remote embeds a PAT in the URL.**
`git remote -v` shows a `glpat-` in the GitLab remote userinfo. glab itself uses keyring. Two credentials, one of them log-leaky. Hygiene for ARCH: remote = SSH (glab already says git is ssh) or HTTPS without token in the URL.

**M3 — MESH_ADDITIONS still lists Groq as "Llama/Qwen/GPT-OSS/Whisper"; GROQ_HANDS says Llama 4 / Mixtral are dead on Free/Dev.**
MESH row 2 is stale relative to the HANDS file. ARCH must cite GROQ_HANDS live IDs (`openai/gpt-oss-20b`, Whisper turbo/v3, `qwen/qwen3.6-27b` vision), not MESH prose.

**M4 — Coding-agent sprawl.**
Packet + MESH_ADDITIONS_grok name Claude Code, Grok Build, Cursor, Copilot CLI, Copilot cloud, Codex, Gemini CLI, Aider, OpenCode, Goose, GitLab Duo, Claude GitHub Action, Gemini GitHub Action. Rubric 8: only lanes with a **distinct wallet or distinct edit protocol** earn a slot. This rank keeps: Claude Code (prepaid F5), Grok Build (prepaid Heavy), Cursor (prepaid Ultra), Aider (git-commit protocol, after install), Codex/Gemini CLI (only if their *other* wallet is confirmed). Duo / Copilot-cloud / extra Actions agents = lease-or-skip.

**M5 — Playwright MCP vs `cosmos_browser` ownership is undecided in the packet.**
PLAYWRIGHT_HANDS recommends MCP-client stdio; `cosmos_browser` already exists as a Python Chrome driver. ARCH must pick one default DOM worker and keep the other as vendor-plural overflow — not two unsynchronized DOM authorities.

**M6 — GCLOUD_HANDS is extra and locally probed; the 12-maker list did not require it.**
Use it as ground truth for the Vertex wallet (account, project id, enabled APIs, ADC). Do not expand this MOTIF row into a GCP platform rewrite.

### LOW / hygiene

- Power scales are not comparable across files (`highest` vs numeric 5). This rank re-scored against the rubric; do not average the scouts' # columns.
- Dates: GITLAB_HANDS header says written 2026-08-26; file mtime is 2026-08-25 21:52. Treat as same-session scout, not a future document.
- `ROUTING.md` GitLab line "deplete ~5% over 24h" still has no remaining-minutes bind (GITLAB_HANDS left that UNKNOWN). Do not plan a pour against it.

---

## UNKNOWN register (do not fill with guesses)

| id | hole | who can close it |
|---|---|---|
| U1 | Ollama installed? GPU/VRAM? `ollama ps` | Keith install + a probe job |
| U2 | Groq key / Console live RPM-RPD | Keith mints; probe `/models` + `settings/limits` |
| U3 | ChatGPT seat for Codex | `codex login status` / chatgpt usage page (Keith) |
| U4 | Gemini CLI auth in use (ADC vs Studio vs login) | `gemini` `/stats` or env inspect in a contained job |
| U5 | GitLab namespace remaining compute minutes + whether a project runner exists | Usage quotas DOM (Keith) / `glab runner list` |
| U6 | GitHub Actions minutes remaining on private Free | Billing DOM (Keith) |
| U7 | M365 plan eligibility + whether any Copilot add-on seat exists | Keith |
| U8 | Remaining Vertex $300 dollars | Cloud Billing reports DOM (Keith); MESH expiry 2026-10-13 |
| U9 | Firecrawl keyless remaining (unpublished cap) | One keyless `search` call; 429 = the answer |
| U10 | Playwright MCP first-run browser download + `tools/list` | `npx -y @playwright/mcp@latest` in an attempt workspace |
| U11 | Whether `~/.claude` / `~/.grok` / `~/.codex` already have MCP servers | `claude mcp list` / `grok inspect --json` / `codex mcp list` |
| U12 | Azure credit remaining | only if D7/Foundry is ever in play |
| U13 | GitLab Education/OSS license on `keithbbf-gif` | UNKNOWN per GITLAB_HANDS; do not plan 50k minutes |

---

## What ARCH (next stage) must produce

Not code. A decision document that:

1. Restates this rubric (or contests it — CONTESTED goes to Keith, one line).
2. Picks **WAVE A** as the first build slice: GitLab worker + GitHub `gh` worker + Playwright MCP (agent-host config) + MCP Fetch. No kernel.
3. Specifies the **runtime-binding value** for each chosen hand (examples: `glab ci status` SHA == fenced HEAD; Playwright `browser_snapshot` hash in GEM; Ollama `/api/version` JSON). `rc=0` is not that value.
4. Specifies env isolation so prepaid CLIs cannot see metered keys.
5. Leaves WAVE C as **designed-but-dark** until U1/U2 close.
6. Leaves Dispatcher `ApiRail`s on the Kernel-attach BACKLOG — does not pretend `cosmos_node_rails.py` is live.
7. Names the lease rule for coding agents (one writer per branch).
8. Does not expand into OpenCode/Goose/n8n/Duo.

Suggested ARCH artifact path: `docs/arch/makerhands_WIRE.md` (COW assigns; different family than G46 if possible).

**This pass produced that decision in-file** (work order: edit only `docs/research/*_HANDS.md` + this file). See **STAGE-2 ARCH — which to wire** below. `docs/arch/makerhands_WIRE.md` was **not** created (out of lane).

---

## Stage-6 (not this job — still)

Nothing here has passed the runtime-binding gate **for a wired COSMOS hand**. Closest live-tree values:

- `gh auth status` → `keithbbf-gif` + scopes (GitHub CLI identity). `gh repo view --json isPrivate` → **`true`**.
- `glab ci status` → pipeline `2790929269` success on SHA `419bfb5e` (GitLab CI exists; **not** bound to HEAD `56fa423`).
- `GET :11434/api/version` → **`OLLAMA_DOWN:System.Net.WebException`** (Ollama not a rail).
- Playwright MCP stdio `tools/list` (host spawn, not a COSMOS worker) → `serverInfo.version=1.63.0-alpha-2026-08-05`, **24 tools**. Evidence for A3 ARCH, not a stage-6 pass.

Those are evidence for the rank + ARCH. They are not a wired COSMOS capability.

---

## Sources this critique actually read

Packet: all 15 `docs/research/*HANDS.md` listed above (full or through ranking + recommended-wiring sections). Governance: `docs/AGENT_BRIEF.md`, `docs/MOTIF_TRACKER.md`, `docs/MOTIF.md`, `docs/WISHLIST.md`, `docs/BACKLOG.md`, `docs/MESH_ADDITIONS.md`, `docs/MESH_ADDITIONS_grok.md`, `docs/ROUTING.md`, `docs/FINAL_ARCHITECTURE.md` decisions 1/5/6, `cosmos/cosmos_node_rails.py` specs, `docs/critique/collector_CRITIQUE_g46.md` (format precedent). Host probes as tabulated.

---

## STAGE-2 ARCH — which to wire (G46, 2026-08-25, `motif_makerhands_s6`)

**Honest stage:** 2 ARCHITECTURE. Dispatch label was s6; tracker + this rank already said **not stage 6**. Rubric is not contested. No CONTESTED line to Keith on the WAVE A pick. H1 (same family wrote research + rank + this ARCH) remains a process hole — gem-api / oa-api still owe an independent rank before consensus.

**Core still not edited.** No `ApiRail`. No Kernel attach. Satellite workers / MCP-host configs / CLI jobs only.

### Rubric (restated, not peeked past)

Wire a hand only if all of: (1) it is a hand, (2) free/prepaid beats metered at equal power, (3) satellite before Kernel — Dispatcher rails blocked on Kernel attach, (4) one authority / fenced commit, (5) already-on-mesh is a delta not a re-add, (6) UNKNOWN is typed, (7) vendor-plural where it disagrees, (8) elegance — no twin coding lane without a distinct wallet or edit protocol.

### First build slice = WAVE A (satellite, $0 tool, auth or binary live)

| slice | hand | surface | next build (stage 4, later) | runtime-binding value (`rc=0` is not it) | this-pass live emit |
|---|---|---|---|---|---|
| **A1** | GitLab `glab` + pipeline artifacts + webhook | queue CLI worker + inbound HTTP | `glab ci run` / `status --wait` / `job artifact`; webhook `pipeline_events`+`job_events`; prefer project runner | Pipeline SHA **equals** fenced HEAD **and** job artifact hash (nonce / `py_compile` output) in GEM | pipeline **2790929269** success SHA **`419bfb5e5a6f21d85da96a663b4572945d64cedd`** ≠ HEAD **`56fa423`** — **not bound** |
| **A2** | GitHub `gh` issues/PRs/api | queue CLI worker | `gh issue` / `gh pr` / `gh api`. **No** hosted Actions | `gh repo view --json isPrivate` plus a worker-emitted issue/PR `id` JSON | **`isPrivate: true`**, `visibility: PRIVATE`, login `keithbbf-gif`, scopes `gist,read:org,repo,workflow`. `.github/workflows` **missing** |
| **A3** | Playwright MCP `@playwright/mcp` | MCP stdio / agent-host | `cmd /c npx -y @playwright/mcp@latest --headless --isolated --browser chromium --caps=network,storage --output-dir <attempt>/pw`. Default DOM worker. `cosmos_browser --dump-dom` = overflow | `tools/list` `serverInfo.version` + later `browser_snapshot` hash in GEM | **`Version 0.0.79`**; MCP `serverInfo.version=1.63.0-alpha-2026-08-05`; **`tools` count = 24** (names in PLAYWRIGHT_MCP_HANDS host bind). Host spawn, **not** a COSMOS worker |
| **A4** | MCP Fetch (`mcp-server-fetch`) | MCP stdio | `uvx mcp-server-fetch` or pip; SSRF allowlist | `tools/list` contains `fetch` + markdown of a pinned URL | spawn **not run** |
| **A5** | xAI Docs MCP + OpenAI Docs MCP | hosted MCP, no key | point Grok Build / Claude Code / Cursor at `https://docs.x.ai/api/mcp` and `https://developers.openai.com/mcp` | `tools/list` from each host | config files **not** inspected |

**Do not put Dispatcher `ApiRail` registration in this slice.** `Kernel.__init__` does not call `register_node_rails`. A green `cosmos_node_rails.py` edit without Kernel compose is a false green.

### WAVE B — probe then attach as worker (not this slice)

B1 Gemini CLI — binary on PATH; auth method **UNKNOWN**. B2 Codex CLI — binary on PATH; ChatGPT seat **UNKNOWN**. B3 Grok Build MCP host → GitLab/GitHub/Playwright — grok 1.0.5 installed; `~/.grok/` contents **UNKNOWN**.

### WAVE C — designed-but-dark (Keith install/key; no BUILD of the rail)

C1 Ollama — `NOT_ON_PATH` + `OLLAMA_DOWN:System.Net.WebException`. C2 Aider — `NOT_ON_PATH`. C3 Groq — no `groq_api_key` in `live/config/`; default model **`openai/gpt-oss-20b`** (this file, not MESH prose).

### WAVE D — later / metered / license-gated

D1 anthropic-api (MESH #17). D2 Studio Flash sibling (Vertex credit dies 2026-10-13). D3 Firecrawl keyless then papers. D4 browser-use OSS (not Cloud). D5 GitHub App webhook. D6 M365 Graph Search if eligible. D7 gcloud Vertex ops (M6: do not expand this row into a GCP rewrite).

### Rejected this cycle (unchanged)

Grok Bot REST (not documented). GitLab Duo/Credits/Orbit. Copilot cloud-agent as default. Assistants/Fine-tunes/Sora/Completions. Antigravity CLI. n8n/Zapier orchestrator. OpenRouter rotating free. MCP Filesystem/Git replacing Core. `browser_run_code_unsafe` as default. browser-use Cloud. Firecrawl Smart Upgrade. Copilot Chat API / Studio daily driver. Vertex Express / Foundry Grok / Azure OpenAI. `gcloud ai-platform` legacy. Dispatcher `ApiRail` as the first commit.

### Env isolation (H5) — prepaid CLIs must not see metered keys

| job | unset in that env | set in that env |
|---|---|---|
| `claude -p` (seat) | `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` | Claude Code OAuth / `--bare` as appropriate |
| `grok -p` (SuperGrok) | `XAI_API_KEY` | `grok login` session |
| `codex exec` (ChatGPT seat) | `OPENAI_API_KEY` | ChatGPT login or invocation-scoped `CODEX_API_KEY` |
| `gem-api` Vertex | `GEMINI_API_KEY`, `GOOGLE_API_KEY` | ADC / `GOOGLE_GENAI_USE_VERTEXAI=true` |
| Studio Flash sibling (later) | (do not share the Vertex job env) | Studio **auth** key (standard keys die Sep 2026) |
| `sgh-api` / `gw-api` / `oa-api` HTTP | (isolated from CLI seats) | COSMOS-owned key under `live/config/` when Keith drops it |

`live/config/` this pass names only: `api_token.txt`, `cursor_cosmos_key.txt`, `cursor_rail.json`, `cursor_rail_probe.json`, `install_key.bin`, `install_record.json`. No maker API keys. Safer for CLI seats; metered rails have no COSMOS-owned credential yet.

### Coding-agent lease (M4 / rubric 8)

**One writer per branch.** Keep: Claude Code (prepaid F5), Grok Build (prepaid Heavy), Cursor Cloud Agents (prepaid Ultra). Aider after install (distinct SEARCH/REPLACE + git-commit protocol). Codex CLI / Gemini CLI only after B1/B2 wallets are confirmed. Duo / Copilot-cloud / extra GitHub Actions agents = lease-or-skip. Do not expand into OpenCode / Goose / n8n.

### HIGH / MED this pass (additive; every existing HANDS feature kept)

| id | fix | where |
|---|---|---|
| **H1** | Cannot close in-family. Noted. gem-api/oa-api still owe a rank. | this file |
| **H2** | ARCH is worker-first; no `cosmos_node_rails.py` edit | this file |
| **H3** | Live repo **PRIVATE**; recommended public=$0 stack superseded | `GITHUB_HANDS.md` Host bind |
| **H4** | Ollama `NOT_ON_PATH` + `OLLAMA_DOWN`; C1 dark | `OLLAMA_HANDS.md` Host bind |
| **H5** | Per-job unset vs set for Claude / Grok / Codex / Gemini | `ANTHROPIC_HANDS.md`, `XAI_GROK_HANDS.md`, `OPENAI_HANDS.md`, `GOOGLE_GEMINI_HANDS.md` |
| **M1** | A1 binding = SHA==HEAD + artifact; current SHA ≠ HEAD | `GITLAB_HANDS.md` Host bind |
| **M2** | `glpat-` still in GitLab remote userinfo; value not repeated; rotate if logged; prefer SSH URL | `GITLAB_HANDS.md` Host bind |
| **M3** | GROQ_HANDS is authority; default `openai/gpt-oss-20b`; MESH row 2 stale | `GROQ_HANDS.md` ARCH pick |
| **M4** | Lease rule above | this file |
| **M5** | Default DOM = Playwright MCP; `cosmos_browser` overflow | `PLAYWRIGHT_MCP_HANDS.md` ARCH pick |
| **M6** | GCLOUD extra; not expanded | this file |

LOW hygiene left as-is (power-scale incomparability; GITLAB_HANDS header date vs mtime).

### UNKNOWN register — closed / still open this pass

| id | this pass |
|---|---|
| **U10** | `tools/list` **closed as host spawn** (24 tools, Playwright `1.63.0-alpha-2026-08-05`). Browser binary download on first `browser_navigate` **still open**. |
| U1–U9, U11–U13 | **still open** (Ollama, Groq key, ChatGPT seat, Gemini auth, GitLab minutes/runner, GitHub Actions minutes, M365, Vertex dollars, Firecrawl keyless, MCP host configs, Azure, GitLab Education). |

### Packet bind (value only this tree's files can hash to)

Concatenation `name:sha256:bytes|` over the 15 `docs/research/*HANDS.md` in name order, then SHA-256:

**`PACKET_SHA256=f9e6ffab716404f9aa2c6286a5a0b9bc4b95b9bfc4dbbcee3dbeddde42360337`**

| file | bytes | sha256 |
|---|---:|---|
| `AIDER_HANDS.md` | 48104 | `496ee88e7511410efb91e33d3c0896a9cbfcf33af4b872fbde6b5b4b8f7d21b5` |
| `ANTHROPIC_HANDS.md` | 41607 | `5d141a9c8ca996e073aaf7c9901ee6b8dd2336843b23ed7321f9665c876dc595` |
| `BROWSER_USE_HANDS.md` | 49984 | `edc95049e353efc54f997a01d6f41c36f3813282d01f3bd8dba534ced1dc41da` |
| `FIRECRAWL_HANDS.md` | 41971 | `387749067cecb102388c1bc7f626c6f3a7da91b5373a013322a41ff87e9fa8b5` |
| `GCLOUD_HANDS.md` | 32068 | `99eb1e65fce86ed0f868764fd908cf4f992d5cff4c7eeb554223186b1cf21589` |
| `GITHUB_HANDS.md` | 34634 | `44afc117e9a3a3acd5be844031d31a1dea634826be0dfad43dc4578266c40136` |
| `GITLAB_HANDS.md` | 43508 | `526f08f7f2acddd7a2285b3ebb73af4c3e341681fe70aa43b969eb88f96add62` |
| `GOOGLE_GEMINI_HANDS.md` | 35924 | `c36cf55f5481ac0c96b6fa04904adc898f41afa1429d1970f3b6e4c857c46c4c` |
| `GROQ_HANDS.md` | 35456 | `291bf01b2e84fa8866ec0b74037497adf3c5480468cfb38081db6b7ccc4ea1ba` |
| `MCP_REFERENCE_SERVERS_HANDS.md` | 42823 | `f712556ec16f9b3e9b3e4743b4489bb429c13c9aeb5755ca55d7bb806775cf8a` |
| `MICROSOFT_COPILOT_HANDS.md` | 38618 | `c478e8b01a1b0ee5af77951ba4edfecc3f8b0c77c51fb1b2a8170c358e1eb52a` |
| `OLLAMA_HANDS.md` | 40917 | `c4605a30700f162b01d119ddec805ba25462dcdbb81dd332e3d9c1982e90e852` |
| `OPENAI_HANDS.md` | 45440 | `fa5ca26e21b3e2f62b3c9bd18f835092f42edd30685d25e46150b158feaabe73` |
| `PLAYWRIGHT_MCP_HANDS.md` | 40857 | `8220a8a3b361fc95925e3e0c9e636025844489d6771538b4e5e2dd8d88d58afb` |
| `XAI_GROK_HANDS.md` | 47558 | `d027a9bfd63dac7a574fb0285cdff31848a307e74e336ef5d8865cc228f9dd08` |

Tree HEAD this bind: **`56fa423c9e9600278a2e51248fcbde77307330a6`**. Node `v24.18.0`. grok `1.0.5 (5115b46bc9)`. claude `2.1.220`. gh `2.97.0`. glab `1.114.0`.

### Next Motif stage (honest)

**3 consensus** — different-family critique of this ARCH vs the rubric (gem-api and/or oa-api). Then stage-4 code of WAVE A satellite workers. **Not stage 6.** Stage 6 for this row is a wired COSMOS worker emitting one of the binding values above from Core's path (queue job / MCP-client worker), not a host `npx` in an agent session.

---

## STAGE-6 satellite re-probe (G46, 2026-08-27, `motif_makerhands_s6`)

**Dispatch label was s6.** No stage-5 critique file exists for this row (`docs/critique/` has `makerhands_STAGE3.md` only — same-family rank+ARCH). HIGH/MED from STAGE3 were already in the HANDS packet (H3/H4/H5/M1/M2/M3/M5). This pass **applied remaining HIGH/MED additively** (every existing HANDS feature kept): host-binds on the five files STAGE3 never wrote (Aider/Firecrawl/browser-use/M365/gcloud), plus 2026-08-27 live re-probes on the rest.

**Core not edited** (`cosmos_kernel` / `cosmos_ledger` / `cosmos_sched` / `cosmos_service`). No Dispatcher `ApiRail` added. Satellite `--probe` only (did **not** overwrite meshadditions `--gate` JSON).

**Honest row status:** WAVE A3 Playwright + WAVE D3 Firecrawl papers are **satellite-bound** (values below). WAVE A1/A2 `glab`/`gh` are live CLIs, **not** COSMOS workers; GitLab SHA still ≠ HEAD. WAVE A4 Fetch spawn blocked. WAVE A5 Docs MCP not configured. Dispatcher rails still blocked on Kernel attach. Core `:8770` **DOWN** this pass — live registry matrix unproven. **This row has not passed stage 6 for a wired COSMOS gh/glab worker.**

### Stage-5 critique

**None.** HIGH/MED source = this file's 2026-08-25 rank. H1 (same family wrote research + rank + ARCH + this re-probe) remains open — gem-api / oa-api still owe an independent rank.

### HIGH / MED this pass (additive)

| id | this pass |
|---|---|
| **H1** | Still open (process). |
| **H2** | Held: no `cosmos_node_rails.py` / kernel edit. |
| **H3** | Re-probed: `isPrivate: true` still. |
| **H4** | Re-probed: Ollama still down. U1 VRAM **closed** = RTX 3070 **8192 MiB**. |
| **H5** | Held. Codex ChatGPT seat confirmed — still unset `OPENAI_API_KEY` on that job. |
| **M1** | Re-probed: pipeline `2790929269` SHA `419bfb5e` ≠ HEAD `56fa423`. **Not bound.** |
| **M2** | Still open: `glpat-` in GitLab remote userinfo (value not repeated). |
| **M3** | Held: Groq default `openai/gpt-oss-20b`. Live GET `/models` **401** `invalid_api_key`. |
| **M4** | **B1 demoted** — Gemini CLI `selectedAuthType=vertex-ai` is the same wallet as `gem-api`. **B2 promoted** — `codex login status` = `Logged in using ChatGPT` (distinct wallet). |
| **M5** | Held. Playwright `--probe` 24 tools. |
| **M6** | Held. GCLOUD not expanded. |

### UNKNOWN register this pass

| id | this pass |
|---|---|
| **U1** | Install still blocked. VRAM **closed: 8192 MiB**. |
| **U2** | Still open (no `gsk_`). Endpoint live (401). |
| **U3** | **closed:** `Logged in using ChatGPT`. |
| **U4** | **closed:** `selectedAuthType=vertex-ai`. |
| **U5** | Minutes still UNKNOWN. Runner existence **closed: no project runner** (30 GitLab.com shared only). |
| **U6** | Still open (Keith billing DOM). |
| **U7** | Still open. Claude M365 MCP **Needs authentication**. |
| **U8** | Still open. |
| **U9** | Keyless papers **200** this pass (not 429). Remaining cap unpublished. |
| **U10** | **closed** by 2026-08-26 `--gate` snapshot `tree_id=KMesh-COSMOS-live` at `http://127.0.0.1:59571/` + this-pass `--probe` tools=24. |
| **U11** | **partial:** Grok MCP=`BFast`; Cursor=`bts`; Gemini=`BFast`; Claude=Gmail/Slack/Box/Cloudflare/GDrive. **No** xAI/OpenAI Docs MCP, **no** Fetch, **no** Playwright in those hosts. |
| **U12** | Still open / not in play. |
| **U13** | Still open. |

### RAN (build + run — satellite, no core)

| cmd | live emit (`rc=0` is not this) |
|---|---|
| `py -3.14 cosmos\cosmos_playwright_rail.py --root V:\A\Ai\COSMOS\live --probe` | `ok=true` `link_id=playwright-dom` **`tool_count=24`** `serverInfo.version=1.63.0-alpha-2026-08-05` navigate+snapshot present |
| `py -3.14 cosmos\cosmos_firecrawl_rail.py --root V:\A\Ai\COSMOS\live --probe` | `ok=true` `link_id=firecrawl-web` **`primaryId=pmid:11089135`** `http=200` `date=Thu, 27 Aug 2026 06:55:06 GMT` |
| `gh repo view keithbbf-gif/cosmos --json isPrivate,visibility` | **`isPrivate: true`** `visibility: PRIVATE` |
| `glab ci status` | pipeline **2790929269** success SHA **`419bfb5e5a6f21d85da96a663b4572945d64cedd`** ≠ HEAD **`56fa423`** |
| `GET https://api.groq.com/openai/v1/models` | HTTP **401** `invalid_api_key` |
| `GET http://127.0.0.1:11434/api/version` | timeout |
| `GET http://127.0.0.1:8770/api/v1/health` | Core **DOWN** (connect timeout) |
| `cmd /c "codex login status"` | **`Logged in using ChatGPT`** |
| `grok mcp list` | **BFast** only |
| `glab runner list` | 30 shared; **no project runner** |
| `nvidia-smi` | `NVIDIA GeForce RTX 3070, 8192 MiB` |

`live/config/` names this pass: `api_token.txt`, `cursor_cosmos_key.txt`, `cursor_rail.json`, `cursor_rail_probe.json`, **`firecrawl_rail.json`**, **`firecrawl_rail_probe.json`**, `install_key.bin`, `install_record.json`, **`playwright_rail.json`**, **`playwright_rail_probe.json`**. No `groq_api_key`, no `ANTHROPIC_API_KEY`, no `OPENAI_API_KEY`, no `GEMINI_API_KEY`, no `fc-`.

### Proof artifact (value only the live tree can emit)

**Path:** `docs/critique/makerhands_STAGE3.md` (this section) + `docs/research/FIRECRAWL_HANDS.md` Host bind 2026-08-27 + `docs/research/PLAYWRIGHT_MCP_HANDS.md` Host bind 2026-08-27.

**Emitted values** (not an exit code):

1. Firecrawl satellite `--probe`: **`primaryId=pmid:11089135`** `http=200` `date=Thu, 27 Aug 2026 06:55:06 GMT` `tree_id` identity `KMesh-COSMOS-live` (sentinel `live/.cosmos-root.json`).
2. Playwright satellite `--probe`: **`tool_count=24`** `serverInfo.version=1.63.0-alpha-2026-08-05` `link_id=playwright-dom`.
3. Packet bind below.

Prior meshadditions `--gate` files (not rewritten): `live/config/playwright_rail_probe.json` `gate=PASS` snapshot `tree_id=KMesh-COSMOS-live`; `live/config/firecrawl_rail_probe.json` `primaryId=arxiv:physics/0103087`. Those are 2026-08-26. Today's unique papers id is **`pmid:11089135`**.

### Packet bind (value only this tree's files can hash to)

Concatenation `name:sha256:bytes|` over the 15 `docs/research/*HANDS.md` in name order, then SHA-256, after the 2026-08-27 additive binds:

**`PACKET_SHA256=fc6af6b054bf28582d12c559b0ee8068b6027fd9373e33f47432beba7f5db63b`**

(prior 2026-08-25 bind was `f9e6ffab716404f9aa2c6286a5a0b9bc4b95b9bfc4dbbcee3dbeddde42360337` — superseded by additive HANDS edits, not deleted.)

| file | bytes | sha256 |
|---|---:|---|
| `AIDER_HANDS.md` | 48479 | `50c3ed68e64ceccf891c1a894ddd079e8f5b15f152ac174b57f747cd78566171` |
| `ANTHROPIC_HANDS.md` | 41952 | `1dae588df594ce1fc21b24276239c51c12d1cd2b1bed67ed01838ecb4c78e559` |
| `BROWSER_USE_HANDS.md` | 50304 | `a992184f0a91002f3aaa747d9151dffbbaf6efd5d85b598300ec9081b59be55e` |
| `FIRECRAWL_HANDS.md` | 42924 | `760418fcaf35ab6e3a301fae02a611c845f650584ebf3fb095789ad122ddbe32` |
| `GCLOUD_HANDS.md` | 32409 | `2ab6c76fcec10f1a3cd5af6fe06b8efb8d52e3a94f0e074b162aa3a93b9cc55c` |
| `GITHUB_HANDS.md` | 35247 | `40a150acd53acfbd46b0f42782493d0f0a4ad71c658eb71a6aa82c9ff38b4936` |
| `GITLAB_HANDS.md` | 44611 | `882d632a072c6d83d00e1ec42e64563f58eb05795329a84a3017d8daa0118305` |
| `GOOGLE_GEMINI_HANDS.md` | 36541 | `3b9b3b098a90ede10c952737423aafc1240c5f9c3b18ade5a2166a9cefadaebc` |
| `GROQ_HANDS.md` | 35867 | `8e5f05bb9eba5f8d57f1d2a8c3a6ebc6da1d58165a519f3a7b7eb7bfc6d0ceb0` |
| `MCP_REFERENCE_SERVERS_HANDS.md` | 43320 | `e78c4c158f3efdfcd6dfb5bb3bff43f23150df3b5a2828fba5ca1ac46d300d97` |
| `MICROSOFT_COPILOT_HANDS.md` | 39014 | `4af52e294784e0f3bc362bde9923c639bc02b79c26ee6203f88c5ed7edb376c4` |
| `OLLAMA_HANDS.md` | 41437 | `1845959c130e32d4d2e5d4c0e379b800a2a9b313bb71a188aa24c99f38bebfa5` |
| `OPENAI_HANDS.md` | 46077 | `bdd0b2e76d1b4c0add4523254589bc84648283e45fefc342da8af8f933aff8dd` |
| `PLAYWRIGHT_MCP_HANDS.md` | 41889 | `a6c3a9147852db8fe8e1c9bb9c13cb4793c934114c309d6374f505349187f3f5` |
| `XAI_GROK_HANDS.md` | 48054 | `cd6b307c46fed2cdfa8981377e8d096559201c2429e318dfe2aa2b022236c73a` |

Tree HEAD this bind: **`56fa423c9e9600278a2e51248fcbde77307330a6`**. Sentinel `tree_id=KMesh-COSMOS-live`. Node `v24.18.0`. grok `1.0.5 (5115b46bc9)`. claude `2.1.220`. gh `2.97.0`. glab `1.114.0`. gemini `0.52.0`.

### Next Motif stage (honest, after this s6 dispatch)

**3 consensus** — different-family critique of this ARCH vs the rubric (gem-api and/or oa-api) still owed (H1). Then stage-4 code of WAVE A1/A2 satellite `glab`/`gh` workers (SHA==HEAD + artifact). WAVE A3 Playwright satellite is already bound; do not re-add. WAVE A4 waits on `uvx`/`mcp-server-fetch`. WAVE A5 is a host-MCP config drop (docs.x.ai + developers.openai.com). **B1 Gemini CLI is not a new lane** (Vertex ADC). **B2 Codex CLI** may attach as a ChatGPT-seat worker. WAVE C still dark (Ollama install / Aider install / Groq key). Dispatcher `ApiRail`s blocked on Kernel attach + a live Core restart. **Not a full-row stage-6 pass.**
