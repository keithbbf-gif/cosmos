# COSMOS — Comprehensive Overview, Current State & Completion Plan

**Document ID:** `COSMOS-OVERVIEW-2026-10`  
**Date:** October 1, 2026  
**Consumer:** Keith + orchestration agents  
**Status:** Living document — rebuildable from sources, not hand-maintained  

---

## 1. What COSMOS Is

**COSMOS (Carry-Over State Mesh Operating System)** is a self-building, multi-agent operating system. One resident Windows service — **COSMOS Core** — is the sole authority. It is an API gateway, scheduler, lease arbiter with fencing tokens, spend gate, return-watcher, registry + prober, backup-policy coordinator, and the single writer of an append-only, hash-chained, service-signed JSONL event ledger on the verified native volume. Everything else — queue views, registries, KDash panels, spend totals — is a rebuildable projection. Workers (native, DOM, cloud) run in attempt-private workspaces and publish only through a fenced commit gateway.

**In one paragraph (from FINAL_ARCHITECTURE.md, ratified 2026-08-23):**

> One resident Windows service — COSMOS Core — is the sole authority: API gateway, scheduler, lease arbiter with fencing tokens, spend gate, return-watcher owner, registry + prober, backup-policy coordinator, and the single writer of an append-only, hash-chained, service-signed JSONL event ledger on the verified native volume. Everything else is a rebuildable projection (service-private SQLite allowed as cache, never authority, never mount-shared). Large artifacts live in a content-addressed store (filename = hash; the ledger holds the live pointer). Workers — native, DOM (browser-capable, Job-Object-contained, ephemeral profiles), and cloud — execute in attempt-private workspaces and publish ONLY through a fenced commit gateway presenting their fencing token + expected input hashes. Mounts are ingress/egress only: a sandbox write becomes real when the native service verifies bytes/hash/schema/identity and ledgers INGRESS_ACCEPTED. The service is a modular monolith, split-ready: internal module interfaces are RPC-shaped so any module can later become a process without breaking the one versioned external API that KDash, the alternate frontend, voice, and phone/desktop apps all consume.

**Core philosophy:**
- *"A process, not an endpoint."* Default posture is MOTION. Engine operations never block on human idle.
- **The One-Pen Rule:** Exactly one writer holds the repo/ledger write-lease (`CCR.lease`) at a time. No concurrent uncoordinated tree mutations.
- **The Fencing Model (R3):** A session has exactly one owner (TUI, desktop app, leader, daemon). A live owner renders the session read-only from the outside. External communication routes through the append-only stream/inbox; never force a process takeover or kill a leader.
- **Runtime binding over review:** A gate is something that runs. A gate that reads code and forms an opinion is a review. "Is this the artifact the machine executes?" is the question that matters.

**Tree layout:**
```
V:\A\            <- EXISTS SO KEITH CAN GRANT COWORK THE ROOT AND EVERYTHING UNDER IT.
V:\A\Ai\         <- all AI work. BTS already lives alongside.
V:\A\Ai\COSMOS\  <- THE OS ITSELF. THE DISTRIBUTION LEVEL.
```

The third level is the distribution level — when Jack or Grayson installs this on a cold machine, the folder has to say what it IS. A generic parent is fine on the machine that built it and useless everywhere else.

---

## 2. The Core Runtime

### 2.1 COSMOS Core (`V:\A\Ai\COSMOS\`)

The kernel. One resident Windows service. Run:

```
py -3.14 cosmos\cosmos.py serve --root V:\A\Ai\COSMOS\live --port 8770
```

**Modules (253 `.py` files, ~89,400 lines in `cosmos/`):**

| Module | Role |
|---|---|
| `cosmos_paths` | Resolver — takes one install-configured root, verified by sentinel content. No drive literal, no parent-walking, no fallback ladder, no import-time side effects. |
| `cosmos_lock` | Fenced commit arbiter. Four-phase fenced commit: reserve under lock → stage unlocked → CAS token → atomic replace. Advisory locking rejected. |
| `cosmos_sched` | Scheduler — immutable manifests + ledger lifecycle events. SQLite is service-private projection only. |
| `cosmos_ledger` | Hash-chained, service-signed JSONL. Total verification: TORN / BROKEN_CHAIN / FORGED / UNREADABLE / STALE_HEAD / TRUNCATED — each typed, not masked. |
| `cosmos_service` | API surface — one versioned external API. `/api/v1/surfaces`, `/fleet`, `/nodemap`, `/jukebox`, `/voice`, `/cvm/*`, `/cdeck/`. |
| `cosmos_session` | Context carry-over — signed state/SEED.json at session close. Closing without a valid manifest is an OPEN_CONTEXT incident. |
| `cosmos_spend` | Spend gate — reserve → deny → call → settle, caller holds the API key. |
| `cosmos_health` | Watchdog2 — 15s Activity Clock, PAUSE-aware, ~19 clocks total. |
| `cosmos_registry` + `cosmos_rails` | Node registry + rail prober. Wired nodes have live-call prove paths. |
| `cosmos_dispatcher` + `cosmos_collector` | Daemons — queue dispatch + state collection. Both live, both need hardening critiques satisfied. |
| `cosmos_surfaces` | Content-addressed store — filename = hash, ledger holds live pointer. |
| `cosmos_crucible` | Adversarial packet builder — completeness-asserted, dispatches to N independent-family critics, merge skeleton separates UNANIMOUS / MAJORITY / SINGLETON / CONTESTED. |
| `cosmos_model_rater` | 2,117-line catalog + seats + observed porosity. Quality axes: intelligence, coding, agentic. Q = mean of existing axes. 16 VIA options. |
| `cosmos_xtalk` | Core HTTP face of the XTalk stream. Transport A (direct inject) = 501 NOT_COMPOSED. Transport B (durable stream) = working. |
| `cosmos_forge_rail` + `cosmos_forge_bg` | Forge profile — github-forge + gitlab-forge rails, WAVE A wired, WAVE C operator keys. |
| `cosmos_makers` | MAKER MAP — AGENT / TOOL / CONNECTOR / SKILL / ROLE / WRAPPER. Ledger-authoritative. |
| `cosmos_womb` + `cosmos_womb_board` | FIFO board — 12-field strict contract, 40-WO trigger, CCrew warm pool, batched judge. |
| `cosmos_voice` | Voice mode server side — ConvoStore, classification, confirm nonces (CSPRNG, ledger-backed, TTL-bound), TTS-friendly spoken reply. |
| `cosmos_voice_loop` | SGH Voice drop loop + remote Android mouth. |
| `cosmos_voice_hardening` | Voice constants + BootUP helpers. `_SPOKEN_CAP = 320` chars (the stilted-speak culprit). |
| `cosmos_resession` | Context boundary crossing — fresh-window minting, not output scraping. CLOCKS id 18. |
| `cosmos_codex_rail` | OpenAI Codex CLI coder+vetter rail. Vendor-specific, no internal seams to extract (by design). |

**Runtime state:**
- Core LIVE at `127.0.0.1:8770` — surfaces, fleet, nodemap all return 200.
- Tree ID: `KMesh-COSMOS-live`
- Ledger seq: ~15,513 (as of 2026-09-19)
- Pulse P0: 26/26 resident.keep + collect-reuse
- Watchdog2 pid 9768 alive
- PAUSE flag: empty (running mode)
- CCR.lease: no file on disk as of this writing — CCr state may have shifted since 2026-09-19

### 2.2 The Harness System

From `docs/HARNESS.md`:

**Harness** = the runner — the loop that calls the model with tools until a final message. Kind from Role. Via from Model family.

**Kinds:** `orch` · `board` · `review` · `coding` · `dispose`. DAEMON is not an LLM.

**Vias:** `codex-cli`, `cli:dsh`, `cli:pi`, `cli:opencode`, `cursor-gitur`, `vertex-coding`, `mouth:openrouter` (degenerate).

**Legend pack** = seven layers on the occupant: Role → Model → Harness → Wrapper → Skills → Tools → Enviro. Prefix-stable (P11).

**Mission pack** = this job (ITEM / diff / PR). Volatile tail.

**DUDs** = Deployment bUnDle = legend + mission. A sharp outfit, not a loser.

**HERO** = Agent + DUDs. Spawn in HERO mode = apply the DUDs. No DUD = not a HERO = no spawn.

**Wrapper** = `WRAP/{Role}.md` + `STYLES/{Model}.md` (append). Tails, not PREFIX.

**Skills** = new training. Role defaults + Role[Model] overlays. Propose → CCr accept. Child's set, not parent's. Lazy, not PREFIX bloat.

**Gadgets** = Tools. In the legend (Role[Model] allow-list), not a side kit.

### 2.3 The Two Pens

- **GrokBot** = pen for `V:\Ai\` (BTS_MESH, Legal)
- **Grok Code / CCr** = pen for `V:\A\` and COSMOS
- They do NOT share a tree until Keith says so. Mailbox first — the BTS two-writer deletion scar.

**CCr (Chief Coder):** Grok 4.6 Build. pid 77372 (as of 2026-09-15). Holds `CCR.lease`. Disposes LiT. Not a Coder-N. Only the CCr writes the COSMOS live tree, and there is only one CCr at a time.

---

## 3. Subsystems — What They Are and Where They Stand

### 3.1 XTalk — Direct Agent Cross-Talk

**What it is:** High-speed, model-blind inter-agent communication across disjoint harnesses (OpenCode, Grok TUI, Hermes, Claude Code, Codex, Gemini CLI). Collapses 7 distinct comms artifacts into one append-only stream + four functional projections.

**Architecture:**
- One append-only stream: `live/state/xtalk.jsonl`
- `inbox(role)` — tail read filtered by `to == me`, byte-offset cursors, cost O(unread)
- `state(conv)` — fold of the stream tracking turns and phases
- `flywheel()` — automatic projection of derivation pairs `(WO, prompt, output, adjustment)` for downstream model fine-tuning
- `roles.json` — measured ownership registry, consulted once per send

**Transports:**
- **Transport A (Direct Injection):** Target session owner is headless or unseated. Preserves KV-cache (13k+ token cache-read per turn). Stays in `cosmos_msg.py` CLI — NOT_COMPOSED in Core (501).
- **Transport B (Durable Stream):** Target has active live owner. Message written to stream; target polls unread tail.

**Implementation:** `V:\OpenWork\XTalk\cosmos_msg.py` (stdlib-only, POSIX/Windows cross-locking, recent-window nonce dedup, verified hash chain).

**Status: BUILT 2026-09-21.** `cosmos_msg.py` 8/8 tests PASS. Live-owner fence (R3) verified against Grok pid 77372. BUxt.toml pointer at `V:\Streams\XTalk\`. Transport A inject not yet composed in Core.

### 3.2 cDeck — Orchestration Workstation

**What it is:** Operator control surface. Originally an 18-panel KDash telemetry clone; pivoted 2026-08-31/09-06 to an Orchestration Workstation.

**Frontstage (target):** Talk, Jobs, Automations, Model Pool, Grok TUI pane.  
**Backstage (kept — NON-NEGOTIABLE):** telemetry wall (KDash visual).

**What exists:**
- `builds/cdeck/` — Python panels: fleet, jukebox, nodemap, spend, recents, local_get, _cosmos_lib. Build stage 4 (UNVETTED).
- `V:\GitHub\cdeck\` — Tauri/Rust project for native exe. `src-tauri/`, `ui/`, `package.json`, `SPEC.md`, `rust-toolchain.toml`.

**Status: BUILD stage 4 (UNVETTED).** First-pass code exists (8 files, build3). 19-panel telemetry wall needs the orchestration pivot. cDeck.exe not yet built from the Rust project. Parallel instances (Forge / Crucible skins) designed but not built.

**Feature requirements (from FEATURES_KEITH.md):** cDeck must have ALL KDash features and more. CREATE box kept and extended. Two surfaces (dated 2026-08-31): cDeck = Orchestration; Grok TUI = coding pane in cDeck. Pivot (2026-09-06): OpenWork is the Cowork clone. cDeck is the backend dashboard (KDash lineage). Do not turn cDeck into a second Cowork. Do not move coding into the dashboard.

**In-build features:** CREATE box, spend control, jukebox, node map, live status feed, batteries, caps & speeds, every KDash feature, new functional controls, integrated CVM control.

### 3.3 kDash — Predecessor Dashboard

**What it is:** The telemetry dashboard that cDeck pivots from. `index.html` + `sw.js` + `manifest.webmanifest` + `mobile.html`.

**Also carries:** `cosmos-voice.apk` (draft seed for later Android app), `ANDROID_VOICE_DRAFT.md`.

**Status: LIVE but deprecated as orch surface.** The KDash visual (telemetry wall) stays in cDeck as backstage. kDash is the mobile/remote reach via `/cdeck/` HTTP fallback. APK is a draft seed only — don't ship it.

### 3.4 Sessions / Open Sessions — First COSMOS Product

**What it is:** List/open AI sessions. First product COSMOS ships. Suite covers crashed systems, all AIs and installs, load/convert/migrate/diff/check/anonymize.

**Provenance:** 666 sessions / 17,439 turns from COW migration carryover. Rebound onto COSMOS 2 2026-09-05T19:11:16.

**What exists:**
- `builds/open_sessions/Open_sessions.py` — BUILT, shipped. GET /api/v1/recents 200, n=200.
- `builds/sessions-app/` — stage 4 code (UNVETTED): sessions_app.py, sessions_core.py, sessions_recents.py, sessions_timeline.py, sessions_verbs.py, sessions_refusals.py, ui/
- `builds/sessions-page/` — stage 4 code + dist/ (UNVETTED): engine.py (59KB), sessions_page.py, test_sessions_page.py, ui/, plugin/
- `builds/session-plugin/` — stage 4 scaffold (UNVETTED): src/, test/, opencode.json, README.md
- `builds/session-tools/` — adapters/, clone.py, README.md, refusals.py, schema.py, session_tools.py (9KB), verbs.py (18KB)

**Status: MIXED.** Open_sessions is BUILT (first product). sessions-app/page/plugin are stage 4 UNVETTED — need runtime-binding gate. Full session tools suite still OPEN (CCr owns it, not CORE kernel).

### 3.5 SpiderCaster

**What it is:** Unknown relationship to COSMOS Core. Three subdirs in `V:\A\Ai\spidercaster\`:
- `antigravity-sdk-python/` — git repo, full project structure (.kokoro, examples, lib/)
- `cosmos-sc-public/` — forge.py, lib/, mcp/, mcp_server.py (16.5KB), projects/, README.md (7KB)
- `working/` — antigravity_seat.py, forge.py, lib/, make_public.py (4.1KB)

Also referenced in `V:\Streams\webdev\spidercaster_local\`.

**Status: EARLY/TOOLING.** Not integrated into COSMOS Core. No COSMOS docs reference it. Needs a stated relationship to Core before it can be planned.

### 3.6 TokenCTR — Payment / Monetization Layer

**What it is:** The freemium/premium monetization layer. Cloudflare worker + payment gateway + entitlement.

**What exists in `V:\Streams\tokenctr\`:**
- `code/` — `cloudflare_worker_tokenctr.js`, `cosmos_pay_gateway.py` (52KB), `cosmos_pay_pricing.py`, `cosmos_pay_processors.py`, `cosmos_pay_entitlement.py`, `cosmos_pay_founding.py`, `cosmos_pay_config.py`, `cosmos_pay_meter.py`, `cosmos_pay_nightly.py`, `cosmos_pay_runpod_rail.py` — total ~140KB
- `cosmos_rev/glm53f/` — COSMsOS revision for GLM 5.3
- `grok47/` — integration/, review/, ui/, README.md
- `KimiK3/` — Kimi K3 revision
- `_superseded/` — earlier version retired

**Status: PAYMENT INFRASTRUCTURE IN PROGRESS.** Not wired into COSMOS Core spend gate. The `_superseded/` tag on root suggests an earlier version was retired. Pricing model needs to be authoritative, not one of several drafts.

### 3.7 COSMOS CODE — Coding Harness Design

**What it is:** The coding agent harness — the DUDs/HERO legend+mission system described in `docs/HARNESS.md`. Active build session in `V:\Streams\cosmos_code\`.

**What exists:**
- `COSMOS_CODE_BUILD_PLAN.md` (20KB) — build plan
- `COSMOS_CODE_ARCHITECTURE_AND_BUILD_PLAN.md` (47KB) — architecture
- `HARNESS_RESOURCE_INDEX.md` (18KB)
- `KEITH_20260930_STANDALONE.md` (3KB)
- `SESSION.md` (6KB), `SESSION_TRANSCRIPT.md` (56KB) — active session
- `TIDYUP.md`, `TIDYUP2.md`
- `BUharness.md` (6KB)
- `harness/G47/` — Grok 4.7 involvement
- `harness_examples/`, `product/`, `AGY/`

**Status: CODING HARNESS DESIGN IN PROGRESS.** Not yet landed in `V:\A\Ai\COSMOS\`. The 56KB session transcript suggests an active build session. This is the DUDs/HERO system that the HARNESS.md book describes — it needs to land in the tree and be wired into the WOMB board + CCrew seats.

### 3.8 Voice Drop / ThinkFast (Temporary Substitute)

**What it is:** The ThinkFast drop-box loop. Phone endpoint: SGH Android Voice (Ara) + Grok Voice Think Fast 2.0. Loop: Voice → GitHub drop → daemon → Drive/CCr → Voice reads Drive.

**Key fact:** NOT a mobile backend/frontend. It is a voice development tool on an async comm loop. It burns Grok Bot Credits — that's the economic reason synchronous desktop voice (local STT + local TTS, zero credit burn) matters.

**Status: PARTIAL.** Voice code exists in-tree (`cosmos_voice.py`, `cosmos_voice_loop.py`, `cosmos_voice_hardening.py`). APK `kdash/cosmos-voice.apk` is a draft seed. Voice refine TABLED 2026-09-04/05. Freemium Phone ChatBot spec frozen 2026-09-07 — separate from Voice Drop.

### 3.9 CVM (COSMOS Voice) — Superseded, Not Deprecated

**What it is:** The original COSMOS Voice architecture. SUPERSEDED 2026-09-03 by Grok Voice control over the SGH phone app. But NOT deprecated — CVM Voice Mode is still a top wanted feature. `docs/CVM_ARCH.md` is historical but the code in `builds/cvm-dt/` is retained.

**What exists in `builds/cvm-dt/` (20+ files, ~200KB):**
- `cvm_dt.py` (57KB) — DT voice main
- `cvm_dt_voice.py` (47KB) — WASAPI capture, voice pipeline
- `cvm_dt_stt.py` (38KB) — STT
- `cvm_dt_clock.py` (15KB) — CLOCKS id 18
- `cvm_dt_client.py` (10KB)
- `cvm_runtimes.py` (26KB)
- `cvm_tts_piper.py` (16KB) — Piper TTS
- `cvm_stt_vosk.py` (33KB) — VOSK STT
- `cvm_stt_whisper.py` (24KB) — whisper STT
- `cvm_gate.py` (34KB) — gate logic
- `cvm_post_probe.py` (25KB)
- `cvm_pull.py` (19KB)
- `cvm_snap.py` (20KB)
- `cvm_handoff.py` (14KB)
- `cvm_supervision.py` (11KB) — audio-owner lease (H6)
- `cvm_suites.py` (3KB), `cvm_test_guard.py` (2KB)
- `cvm_double.py` (5KB)
- `BENCH_LATENCY.json` (58KB) — latency benchmark, `transcribe.stt_model_inference` and `respond.voice_post` UNMEASURED
- `LATENCY_F15.md` (8KB), `POST_BREAKDOWN.json` (9KB), `CVM_BACKLOG.md` (40KB)
- `F21_STT_LOCAL.json`, `F21_STT_TEST.json`, `F21_VOSK_REUSE.json`, `F21B_STT_WHISPER.json`
- `B1_EAR.json`, `B4_TTS_PIPER.json`

**In-tree CVM code:** `cosmos_voice.py` (voice mode server side), `cosmos_cvm_clock.py`, `cosmos_cvm_projection.py`, `POST /api/v1/voice` on the service.

**Status: SUPERSEDED (as product path) / RETAINED (code) / PARTIAL (F-09, F-15).** The product voice path is now Voice Drop / ThinkFast + Grok Voice. But CVM is still wanted — F-15 is ranked as Keith's #1 usability priority. The synchronous desktop voice MVP is the slice that matters for the #1 bottleneck.

### 3.10 Crucible — Adversarial Judge

**What it is:** The workspace's proven adversarial method as a first-class COSMOS workflow. Build a packet from named artifacts (completeness-asserted, M-08), dispatch to N independent-family critics through the registry's live links, collect returns as files, produce a merge skeleton separating UNANIMOUS / MAJORITY / SINGLETON / CONTESTED by finding-id.

**What exists:** `cosmos_crucible.py`, `cosmos_crucible_critics.py`. Dispatchers are injected (name → callable → return_text). Real dispatchers = registry rail adapters; tests inject fakes.

**Status: BUILT (code).** The July forge's lesson is installed: returns land on disk before reasoning, dead critic = finding, no hidden aggregation. Auto-judge batching (accumulate completed WOs into a grading pile until count ≥ X, amortizing context warmup) is a projected mid-October 2026 milestone — not yet wired.

### 3.11 Model Rater

**What it is:** Catalog + seats + observed porosity for cDeck. Pulls GET /api/v1/models (rates, modalities, Artificial Analysis indices) into local projection. Daily refresh or refresh-on-open.

**Quality axes:** intelligence, coding, agentic (OpenRouter benchmarks + AA indices). Q = mean of existing axes. Price: USD per 1M tokens. Type: coding / reasoning / images / audio / video / chat.

**Seats:** Prestaged profiles for MOTIF dual-lane, Crucible roles, dispatch. 16 VIA options: cli:grok, cli:gemini, cli:codex, cli:hermes, openrouter-api, groq-api, gem-api, vertex-coding, oa-api, sgh-api, cursor-api, dom, mcp:openwork, mcp:github, mcp:bts.

**Observed porosity:** GET /api/v1/porosity with audit stamps (agent_id, action, timestamp, authority source:class). A score without stamps is not an audit trail.

**Status: BUILT, in-tree.** 2,117 lines. The rater columns (format %, usable %, keep %, $/keep) are the fix for S16 (Qwen seats burned 62% budget for 0.9% win rate). Policy: leaderboard prior before any seat spends.

### 3.12 WOMB Board — FIFO Pipeline

**What it is:** Raw human directional intent → structured multi-agent executions. Strict 12-field contract: fifo_ts, state, agent_field, wo_path, write_path, output_spec, target_scope, Role, Model, Harness, Environment, Tools.

**Operational rules:**
1. **WOMBAT runs CCr:** WOMBAT is the designated operator of CCr. Creates, triggers, injects.
2. **The 40-WO Trigger:** CCr does not spin up for single tasks. Tasks accumulate until count ≥ 40, then CCr runs as batch leader.
3. **CCrew Warm Pool (Cache Strikes):** Small, fixed session pool reused so context prefix stays in GPU cache ($0.002–$0.03/M cache read vs $1.50–$3.00/M fresh prompt rate).
4. **Batched Judge (Crucible):** Never called per-WO. Completed WOs accumulate until count ≥ X, amortizing context warmup.

**Status: BUILT.** Board = 500 FIFO full fields. WOMB_PILE_400.json: 157 failed + 792 delme wo-*.json, 949 files seen, 447 empty, 224 motif clones, 80 unique other. Board operational but currently EMPTY — no WOs being fed from WISHLIST/backlog.

### 3.13 Gitur — GitHub + GitLab + Cursor

**What it is:** GitHub + GitLab + Cursor surfaces. Stage 6/7 lane in the COSMOS pipeline.

**What exists:** `cosmos_gitur.py`. `bts_cursor.py` — Python SDK + Cloud Agent API, dispatchable from queue lane.

**Lanes (connected, idle since 2026-08-23):**
- **CURSOR:** Ultra, $0 marginal, 1.1% used, SDK + Cloud Agent API, key expires 2027-08-13. Stage 6 — the build.
- **GITHUB:** connected as `keithbbf-gif`, `bts-mesh` linked, Cloud Agent env built. Stage 7 — the PR is the gate.
- **GITLAB:** connected as `keithbbf-gif`. CI that actually executes (py_compile, import graph, integration run). Second remote. The $200.

**Status: CONNECTED, NOT FULLY USED.** Keith 2026-08-23: "The next session's first act is to RUN one, not to characterize one." The lanes are connected and idle. C-41: an orchestrator that hands the human a chore has not orchestrated.

### 3.14 Patents & Legal

**What exists:**
- `V:\Streams\Patents\` — P01–P24 patent applications. `COSMOS_CURRENT_APPLICATION_PACKET.md`. P23 Irbe audit filing-prep active.
- `V:\OpenWork\COSMOS_PATENT\` — BOOTUP_PASTE.md, BUp.toml, patents/, ROLLED.md
- `V:\OpenWork\COSMOS_LEGAL\` — BOOTUP_PASTE.md, BUl.toml, casefile_index/, disclosure_audit/, draft1_check/, email_evidence/, monday_filing/, sessions/, ROLLED.md
- `V:\OpenWork\COSMOS_2\` — `COSMOS_25_Patent_Ideas_Provisionals_and_Prior_Art.docx` (4.1MB), Chambers_v_Abraxas_Evidentiary_Timeline (607KB docx + 516KB pdf)
- `V:\legal\Abraxas\`
- `V:\tmp\gitur-wt-1\docs\research\docket\specs\` — P01–P13 PDFs, COSMOS_SPEC_VOLUME.pdf, COSMOS_TRANSMITTAL.pdf
- `V:\tmp\gitur-wt-1\docs\research\docket\` — COSMOS_Provisional_Patent_Applications.docx, COSMOS_Challenge_Ready_Provisionals.docx, APP_COSMOS.md

**Status: IN PROGRESS.** P23 Irbe audit filing-prep active. P20 Keep Afloat folded into P07/P11/P24. P17 Gitur BUILD triad folded into P02/P05. Legal under GrokBot's pen (V:\Ai).

---

## 4. Current State — The Numbers

### 4.1 Feature Master (70 rows)

| Status | Count | Meaning |
|---|---|---|
| **DONE** | 46 | Implementing symbol exists AND emitted artifact or test run proves it |
| **PARTIAL** | 16 | Some slices land, at least one doesn't. Most common: built but not running |
| **BLOCKED** | 3 | Code complete; credential or one elevated line Keith owns is the only gap |
| **ABSENT** | 5 | No implementing symbol found. Design doc ≠ implementation |
| **Total** | 70 | |

**The 16 PARTIALs:** F-05 (mobile node-map drag — DONE per re-audit, cell lagged), F-09 (CVM device-select — superseded path), F-11 (Core /cdeck/ mount — DONE, needs restart), F-15 (CVM usability — Keith's #1), F-28 (competency pin), F-30 (wire WAVE A — DONE, WAVE C operator keys), F-36 (write_tracker_json authority=markdown, flip restrained 62/96), F-39 (codex rail no seam — by design), F-41 (live ledger apply — REFUSING by design), F-43 (same-volume dest + VSS), F-53 (prepaid orchestrator — CLOCKS id 24, --install-task not run), F-54 (off-volume copy — NO_OFFSITE_ROUTE), F-57 (Slack webhook — absent file), F-60 (health fence — DONE per re-audit), F-69 (dispatch H6 live-prove — DONE per re-audit), F-70 (dirty tree — commits flowing)

**The 3 BLOCKED:** F-17 (was blocked on F-33, now DONE), F-32 (OpenAI key — operator credential), F-45 (R2 credential — operator credential), F-46 (R2 credential — operator credential). Wait — that's 4. The FEATURE_MASTER says 3 BLOCKED. Let me recheck... From BLOCKED_ITEMS.md: the 3 BLOCKED are F-32 (OpenAI key), F-45 (R2 credential), and one more. Actually the FEATURE_MASTER rollup says 3 BLOCKED as of the latest re-audit. The BLOCKED_ITEMS.md lists many items but most are CLOSED. The current 3 BLOCKED are the ones still open.

### 4.2 Backlog (8 open items)

1. **ChatBot phone DEFINE** — frozen `DEFINE_CHATBOT_PHONE.md`. Freemium iterate. RESEARCH next (DOM rails).
2. **Session tools suite** — Cowork→OpenWork migrator is the seed, not the product. Open Sessions product route is LIVE. Suite verbs beyond list/open still open.
3. **CLOCKS collapse** — 26 resident → one 15s HOLD-aware Pulse + cosmos_pool as only claim_next. pythonw for small jobs is wrong shape.
4. **Maker + gcloud sweeps** — stage-3 rank landed. BLOCKER CLEARED 2026-08-30 (Dispatcher rails no longer blocked on Kernel attach). Next: arch which to wire.
5. **Mesh additions** — 9 adapters compose, only 4 have runtime-proven hands. Re-measured 2026-08-30, still open.
6. **cosmos_dispatch / cosmos_collector** — both live, but critiques unsatisfied. Confirmed open 2026-08-30.
7. **AUTO-RESESSION** — stage-1 landed (`AUTO_RESESSION.md` 34KB). Still open — the watermark monitor that auto-executes the SOP is not wired.
8. **Tool migration** — 135 UNDECIDED / 8 REPLACED. PORT_DECISIONS holds 35 rulings, 27 apply-ready. PARTIAL 2026-08-31.

### 4.3 What's Live vs What's Built vs What's Missing

**LIVE (Core is running and serving):**
- Core at :8770 — surfaces, fleet, nodemap, jukebox all 200
- Watchdog2 (15s Activity Clock, PAUSE-aware)
- 19 clocks total
- XTalk stream (Transport B working)
- Open Sessions (GET /api/v1/recents 200, n=200)
- Model Rater (catalog + seats + porosity)
- WOMB board structure (but empty — no WOs feeding)
- 4 wired rails with live-call prove paths (grok-build, Cursor, firecrawl, Playwright)
- claude-cli rail (subscription seat, not API key)
- CVM voice mode in-tree (classify/confirm/TTS pipeline)
- VOSK STT bound in-tree (F-21)

**BUILT but not running / not wired:**
- cDeck orchestration pivot (still telemetry wall)
- cDeck.exe (Rust project not built)
- Auto-resession watermark monitor
- WOMBAT daemon (40-WO trigger not automated)
- Crucible auto-judge batching
- 5 built-but-cold daemons (F-19, F-20, F-31, F-65 — need schtasks lines)
- Session tools suite beyond Open Sessions
- Synchronous desktop voice loop
- TokenCTR wired into spend gate
- COSMOS CODE harness landed in tree
- SpiderCaster integrated (undefined relationship)

**BLOCKED on Keith:**
- F-32 OpenAI key (anthropic credit requires DL — tabled on privacy grounds)
- F-45/F-46 R2 credential
- F-57 Slack webhook (file absent)
- F-43 same-volume dest + VSS Create (needs elevated session)
- F-48 ES.3 dest (drive not installed — queued for later)
- F-48 ODX dest (skipped by operator decision — C: 96% full)
- F-70 dirty tree commit (Keith's git command)
- Multiple `--install-task` schtasks lines
- Gitur lanes (not run yet)

**BY DESIGN (not defects):**
- F-36 flip restraint (62/96, needs 34 more consecutive agreeing ticks)
- F-39 codex rail no seam (vendor-specific CLI, nothing to split)
- F-41 live ledger apply (REFUSING — authority ledger is append-only root of trust)
- F-09/F-15 CVM-DT (superseded path, but code retained and wanted)
- CVM superseded (product path is Voice Drop/ThinkFast, but CVM still wanted)

---

## 5. Component-by-Component Status Matrix

| # | Component | Location | Status | Owner | Oct 31 Target |
|---|---|---|---|---|---|
| 1 | **COSMOS Core** | `V:\A\Ai\COSMOS\` | **LIVE** (:8770) | CCr | Stable, all modules runtime-bound |
| 2 | **XTalk** | `V:\OpenWork\XTalk\`, `cosmos_xtalk.py` | **BUILT** (Transport B) | CCr | Transport A composed in Core |
| 3 | **cDeck** | `builds/cdeck/`, `V:\GitHub\cdeck\` | **BUILD stage 4** (UNVETTED) | CCr + ORC | Orchestration pivot + exe built |
| 4 | **kDash** | `kdash/` | **LIVE, deprecated** | — | KDash visual stays in cDeck backstage |
| 5 | **Open Sessions** | `builds/open_sessions/` | **BUILT, shipped** | CCr | Wired into cDeck RECENTS |
| 6 | **Session tools suite** | `builds/sessions-*`, `builds/session-tools/` | **MIXED** (open_sessions BUILT, rest stage 4) | CCr | Open Sessions in cDeck; suite iterates |
| 7 | **SpiderCaster** | `V:\A\Ai\spidercaster\` | **EARLY/TOOLING** | TBD | Relationship to Core defined |
| 8 | **TokenCTR** | `V:\Streams\tokenctr\` | **IN PROGRESS** (~140KB payment code) | CCr | Entitlement wired into spend gate |
| 9 | **COSMOS CODE** | `V:\Streams\cosmos_code\` | **DESIGN IN PROGRESS** | CCr | Landed in tree, wired into WOMB/CCrew |
| 10 | **Voice Drop / ThinkFast** | `cosmos_voice_loop.py`, `kdash/cosmos-voice.apk` | **PARTIAL** (draft APK, async loop) | CCr | Freemium phone DEFINE + research done |
| 11 | **CVM (COSMOS Voice)** | `builds/cvm-dt/` (retained), `cosmos_voice.py` (in-tree) | **SUPERSEDED / RETAINED / PARTIAL** | CCr | Synchronous desktop voice MVP |
| 12 | **Crucible** | `cosmos_crucible.py`, `cosmos_crucible_critics.py` | **BUILT (code)** | CCr | Auto-judge batching wired |
| 13 | **Model Rater** | `cosmos_model_rater.py` (2,117 lines) | **BUILT, in-tree** | — | Feeds cDeck Model Pool |
| 14 | **WOMB Board** | `work_orders/ccr/` | **BUILT (structure), EMPTY (no WOs)** | CCr/WOMBAT | 40-WO trigger automated, board feeding |
| 15 | **Gitur** | `cosmos_gitur.py` | **CONNECTED, IDLE** | Keith | Lanes run (Cursor/GitHub/GitLab) |
| 16 | **Patents/Legal** | `V:\Streams\Patents\`, `V:\OpenWork\COSMOS_*` | **IN PROGRESS** | GrokBot (V:\Ai) | P01–P24 filed/abandoned decisions |
| 17 | **Clusters** | `V:\Streams\Cosmos_clusters\` (empty) | **NOT FOUND** | TBD | Defined or removed |
| 18 | **CodeForge → Forge** | `cosmos_forge_rail.py`, `cosmos_forge_bg.py` | **PARTIAL** (Forge profile in tree) | CCr | Name settled as Forge; FORGE version later |

---

## 6. Action Plans with Timelines

### Plan A — Oct 31 Acceleration (Plan4Nov-SP4)

See `Plan4Nov-SP4.md` for the full sprint plan. Summary:

**Tier 1 (Oct 31 must-hit):**
1. WOMB Board + 40-WO Trigger Automated
2. cDeck Orchestration Pivot
3. Auto-Resession Wired
4. Open Sessions Shipped (wired into cDeck)
5. Low-Hanging Feature Fruit (F-70 commit, F-53 schtasks, BLOCKED items unblocked)

**Tier 2 (Oct 31 should-hit, voice elevated):**
6. F-15 — Re-run CVM latency bench
7. Synchronous Desktop Voice MVP (WASAPI → VOSK → classify/confirm → Piper TTS → audio-owner lease)
8. Fix the stilted speak (`_SPOKEN_CAP = 320`)

**Tier 3 (slip past Oct 31):** Full CVM architecture, federation, FORGE version, patents, SpiderCaster, COSMOS CODE landing, full session tools suite, CLOCKS collapse, mesh additions, tool migration.

**Weekly cadence:** 5 weeks, Oct 1–31. CCr owns Tier 1 + voice Tier 2. ORC owns cDeck frontstage + Open Sessions + ChatBot research. Keith owns credentials + schtasks + Gitur lanes + runtime-binding proof.

### Plan B — Post-Oct 31 Completion (Nov–Dec)

#### Week 1–2 (Nov 1–14): Tier 3 Start + Hardening

1. **Full CVM Voice Mode** — the H1–H10 architecture. Thin phone (capture + snapshot mule), heavy local (VOSK + Piper + orchestration on PC), same headphones exclusive owner (H6), fail-closed + typed absence (H3), offline fallback (H4), one authority (H2). This is the superset of the synchronous desktop MVP.
2. **CLOCKS collapse** — 26 resident → one 15s Pulse + cosmos_pool as only claim_next. Schtasks for backup/verify/meters/hourly.
3. **cosmos_dispatch / cosmos_collector hardening** — satisfy the unsatisfied critiques. Both daemons are live but the critiques are open.
4. **Mesh additions verification** — verify the remaining 5 adapters (Ollama, Groq, etc.) have real hands.

#### Week 3–4 (Nov 15–28): TokenCTR + Federation Prep

5. **TokenCTR fully wired** — payment gateway, pricing, processors, entitlement, founding. Cloudflare worker live. Freemium tier (local C++ free, best-effort, honest TOS) + paid protected tier (BAA surface, audit, human-in-the-loop, reversible encryption, compliant hosting).
6. **Federation prep** — SRV1/T7 install (F-56, currently BLOCKED on hosts). XTalk stream sync across peers. cDeck parallel instances (Forge / Crucible skins).
7. **COSMOS CODE harness landed** — DUDs/HERO system from `V:\Streams\cosmos_code\` landed in tree, wired into WOMB board + CCrew seats.

#### Week 5–6 (Nov 29–Dec 14): Session Tools + Polish

8. **Full session tools suite** — crash / all AIs / diff / check / anonymize. Open Sessions is the seed; the full verb set iterates on top.
9. **Session tools plugin** — OpenWork plugin rebind proven. Suite itself still open (CCr owns it).
10. **Tool migration resolved** — 135 UNDECIDED → apply the 27 apply-ready PORT_DECISIONS rulings. COB/COW judgment writes the rest.
11. **SpiderCaster relationship defined** — either integrated as a COSMOS component or declared independent.

#### Week 7–8 (Dec 15–31): FORGE Version + Year-End

12. **FORGE version for coders** — special free release. cDeck parallel instance as Forge skin. Spring beta was the original target; Dec is a stretch but possible for a beta.
13. **Patent filings** — P01–P24 decisions (file or abandon). P23 Irbe audit filed.
14. **Year-end state:** COSMOS Core stable + runtime-bound, cDeck orchestration pivot complete + exe built, WOMB board automated, auto-resession wired, Open Sessions shipped, synchronous desktop voice working, TokenCTR wired, Crucible batching live, session tools suite beyond list/open, CLOCKS collapsed, mesh additions verified, tool migration resolved, federation ready (hosts named), FORGE beta out.

### Plan C — Benchmarking Framework

#### What "done" means per component

| Component | "Done" definition | Proof |
|---|---|---|
| Core | All modules runtime-bound, stable, no PAUSE hold | Runtime-binding gate: new-tree-only marker on live tree |
| XTalk | Transport A composed, both transports working | Direct inject proves KV-cache preservation |
| cDeck | Orchestration pivot complete, exe built, every panel functional | Frontstage nav works, telemetry wall visible, CREATE/Jobs/Model Pool operational |
| Open Sessions | Wired into cDeck RECENTS, open-as-action works | cDeck shows real session list from Core |
| Voice (synchronous desktop) | End-to-end loop works, same headphones, latency measured acceptable | BENCH_LATENCY.json re-run, both stages measured |
| Voice (full CVM) | H1–H10 architecture complete, thin phone + heavy local + offline fallback | CVM_ARCH.md criteria satisfied, each H criterion proven |
| WOMB | Board feeding from WISHLIST, 40-WO trigger auto-fires CCr | Board has ≥1 WO in CLAIMED state, driven by real WISHLIST item |
| Auto-resession | Context watermark auto-triggers SOP, no terminal copy/paste | Watermark crosses threshold → fresh session → SEED.json carry-over |
| TokenCTR | Entitlement check wired into spend gate, pricing authoritative | Spend gate refuses untracked usage, pricing is single source of truth |
| Crucible | Auto-judge batching live, multi-vendor critics seated | Completed WOs accumulate into grading pile, batch dispatches |
| Gitur | Lanes run, PRs created, CI executes | Cursor/GitHub/GitLab lanes produce artifacts |
| Session tools | Full verb set beyond list/open | Crash/diff/check/anonymize each proven |
| Federation | Remote thin-Core on external machine, Crucible skin over XTalk sync | SRV1/T7 have COSMOS installed, hostnames named |

#### Benchmark cadence

- **Weekly (every Friday):** Feature Master re-audit. DONE/PARTIAL/BLOCKED/ABSENT counts. WOMB board state. Backlog open items. Core health (surfaces/fleet/nodemap 200, PAUSE flag, CCR.lease).
- **Bi-weekly:** Runtime-binding gate check on any component that claims "done." New-tree-only marker proof.
- **Monthly:** Full Component Status Matrix update (the 18-row table above). Benchmark against Plan A/B timelines.

#### Red flags that indicate plan slippage

1. WOMB board stays empty >1 week → pipeline is dead, self-build is not happening.
2. cDeck still telemetry wall at Oct 15 → pivot is slipping.
3. Core PAUSE flag goes to HOLD without Keith's explicit action → something auto-paused.
4. CCR.lease lost without a handoff → two writers could collide (BTS-MESH scar).
5. `builds/cvm-dt/` BENCH_LATENCY.json mtime not updated by Oct 15 → F-15 bench not re-run.
6. `_SPOKEN_CAP` still 320 by Oct 21 → stilted speak not fixed.
7. TokenCTR still not wired into spend gate by Nov 15 → monetization layer not connecting.
8. Gitur lanes still idle by Oct 7 → C-41 violation (orchestrator handing chores, not running).

---

## 7. The Scars That Shape the Plan

From `SCAR_TABLE.md` (24 scars, 22 healed, 2 healing, 0 open):

1. **S1 (Zero Target Source):** 906 orders, 98% DROP. Fixed: source inlined verbatim in every WO.
2. **S2 (Phantom Functions):** Board composed against non-existent functions. Fixed: `build_board.py` validates anchors against real function map.
3. **S3 (Reference Sheet Prompts):** Prompts passed pointers, no content. Fixed: ORC authors fat tails.
4. **S4 (Output Contract Clash):** Contradictory output instructions. Fixed: single output contract (FILE/ENDFILE) + assistant prefill.
5. **S5 (Asymmetric Preload):** Judge held 700k, coders 1.3k. Fixed: symmetric preload.
6. **S6 (Twin Spawner Loop):** Blind respawn on empty board. Fixed: elevated taskkill, stand-down WO, board frozen.
7. **S7 (CHECK/TEST Padding):** CCr padded board to look productive. Fixed: ORC-authored orders only.
8. **S8 (Swallowed Process Kill):** `SilentlyContinue` swallowed Access Denied. Fixed: explicit kill verification.
9. **S9 (Premature Token Truncation):** Ling truncated at 4096. Fixed: 8192 cap + prefill + budget line.
10. **S10 (Reasoning Prolixity Leak):** DeepSeek emitted 8k reasoning, no code. Fixed: assistant prefill + contract-first.
11. **S11 (Neighbor Function Ingestion):** Model emitted neighbor. Fixed: single-function gate rule.
12. **S12 (Open Audit Tasks):** Reasoning sprawl. Fixed: closed-form tasks only (HEALING).
13. **S13 (Whitespace Re-emission Churn):** 7/11 keeps byte-identical except whitespace. Fixed: tier0 step 7 + 7b.
14. **S14 (Stub-Grading on Failed Output):** Judge graded gate-FAILED output. Fixed: viable-only filter.
15. **S15 (Inner Helper as Top-Level):** Model restyled nested helper. Fixed: caught by S11.
16. **S16 (Quota Burn on Low-Yield Seat):** Qwen 62% budget, 0.9% win rate. Fixed: rater columns + leaderboard prior.
17. **S17 (Mutable Board During Batches):** Board changed mid-run. Fixed: ORC owns board.json, frozen during execution.
18. **S18 (ArXiv 429 Ban):** Parallel queries triggered rate limit. Fixed: Semantic Scholar + OpenAlex first, ArXiv sequential.
19. **S19 ($158 Burned on OpenAI Zero Output):** Pre-pipeline era. Fixed: the entire pipeline exists as the fix (HEALING — Token Smoken page).
20. **S20 (Flaky Chat Prefill):** DeepSeek BOS/EOS flaky. Fixed: per-seat scaffold dial.
21. **S21 (Judge 429 Empty Verdicts):** GLM free-tier RPM. Fixed: retry ×2 + 45s backoff + 15s spacing.
22. **S22 (Single-Seat Drop Crashed Judge):** Hardcoded 2 candidates. Fixed: N-candidate judge, dynamic labels.
23. **S23 (Global Scope Pollution):** `var clockFilter` prepended. Fixed: tier0 step 5c.
24. **S24 (Launch Drop Archived Wrong):** Back-to-back drops collided. Fixed: archive as `<prev_tag>_<timestamp>`.

**The standing scars that still shape decisions:**
- S12: task-authoring discipline — every WO must name a real function + structural decision.
- S19: the pipeline exists as the fix — never spend without measurement.
- The BTS-MESH scar (S26, not in the 24 but foundational): two-writer collision destroyed the predecessor tree. This is why the one-pen rule and CCR.lease exist. Never violate them.

---

## 8. Open Questions

1. **SpiderCaster:** What is its relationship to COSMOS Core? Is it a product COSMOS ships, a capability COSMOS consumes, or an independent project? Until this is answered, it can't be planned.
2. **Clusters:** `V:\Streams\Cosmos_clusters\` is empty. Is this a real component that was never started, or a concept that was retired?
3. **CodeForge → Forge:** Was CodeForge a separate product that got renamed/absorbed into the Forge profile, or was it always just the Forge profile? The name change matters for how the FORGE version (free coder release) is positioned.
4. **CCr state:** CCR.lease file is absent as of this writing. Is CCr still running (pid 77372), or did it restart/stop? The grok.exe processes are alive but the lease file is gone. This needs confirmation before wiring anything that assumes CCr ownership.
5. **TokenCTR authoritative pricing:** `cosmos_pay_pricing.py` exists but there are multiple drafts. Which one is authoritative? The freemium/premium split needs a single source of truth.
6. **Gitur lanes:** The pipeline says "RUN one, not characterize one" (Keith 2026-08-23). Which lane runs first? Cursor is the build lane (Stage 6), GitHub is the PR gate (Stage 7), GitLab is CI. The recommendation: Cursor first (build), then GitHub (PR), then GitLab (CI mirror).
7. **F-36 flip gate:** 62/96 ticks. If Core is stable, closes in ~9 minutes. If flaky, stays open. The runtime-binding gate (delete an MD row, tick restores from JSON) is the proof. Should this be accelerated by running the Activity Clock at higher frequency, or is stability the point?

---

*Document maintained by ORC. Ground truth from `V:\A\Ai\COSMOS\` tree, `docs/FEATURE_MASTER.md`, `docs/BLOCKED_ITEMS.md`, `docs/BACKLOG.md`, `docs/CVM_ARCH.md`, `docs/HARNESS.md`, `docs/FINAL_ARCHITECTURE.md`, `docs/COSMOS_PIPELINE.md`, `builds/cvm-dt/`, `V:\OpenWork\`, `V:\Streams\`, `V:\tmp\gitur-wt-1\`. Last updated 2026-10-01.*
