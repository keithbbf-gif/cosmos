# PLAN4NOV-SP4 — COSMOS Acceleration Plan, Sprint 4

**Target:** Oct 31, 2026  
**Author:** Solar Pro4 (ORC seat)  
**Ground truth:** Core LIVE at :8770 · Grok running · 46 DONE / 16 PARTIAL / 3 BLOCKED / 5 ABSENT · WOMB board empty · PAUSE flag empty (running mode) · 8 backlog items open · FEATURE_MASTER §4 ranks F-15 as Keith's #1 usability priority  

**Revision log:**
- SP4 (this): rewrote voice tier after Keith correction — CVM superseded ≠ deprecated; Voice Drop burns Grok credits; synchronous desktop voice is #1 bottleneck; Core+code fundamentals stay first priority.

---

## 1. Priority Order (non-negotiable)

1. **Core + code fundamentals first.** WOMB board, cDeck pivot, auto-resession, Open Sessions, closing easy PARTIALs. Nothing else competes with these.
2. **Voice is Tier 2, not Tier 3.** F-15 is Keith's stated #1 usability priority. Voice Drop is a temporary workaround that burns Grok Bot Credits. Synchronous desktop voice is the real fix.
3. **F-09/F-15 are not dead.** They're seed code in a retained `builds/cvm-dt/` tree (~200KB, 20 files). The engineering is largely done; what's missing is bench numbers, the synchronous loop wiring, and TTS quality.

---

## 2. Tier 1 — Oct 31 Must-Hit (Core + Code Fundamentals)

### 2.1 WOMB Board + 40-WO Trigger Automated
- **Why:** Board is empty today. Empty board = no pipeline = no self-build.
- **What exists:** `cosmos_womb.py`, `cosmos_womb_board.py`, `WOMB_PILE_400.json` (500-slot FIFO, 80 unique non-empty).
- **What's missing:** WOMBAT daemon that evaluates the 40-WO trigger, populates the board from `docs/WISHLIST.md` + `docs/BACKLOG.md` open items, triggers CCr when threshold hit.
- **Owner:** CCr (Grok). WOMBAT is the designated CCr operator.
- **Gate:** Board has ≥1 WO in CLAIMED or PENDING state, driven by a real WISHLIST item.

### 2.2 cDeck Orchestration Pivot
- **Why:** Today cDeck is a 19-panel telemetry wall. It needs to be the operator face: Talk / Jobs / Automations / Model Pool / Grok TUI pane (frontstage) + telemetry wall (backstage, kept — NON-NEGOTIABLE).
- **What exists:** `builds/cdeck/` (Python panels: fleet, jukebox, nodemap, spend, recents, local_get, _cosmos_lib). `V:\GitHub\cdeck\` (Tauri/Rust project for native exe).
- **What's missing:** Frontstage nav wiring, Talk → XTalk inbox, Jobs → WOMB board, cDeck exe build from Rust project.
- **Owner:** CCr for Python panels. Separate track for Rust exe build (parallel).
- **Gate:** cDeck shows Talk + Jobs + Model Pool as navigable frontstage, telemetry wall still visible in backstage, every existing panel still functional.

### 2.3 Auto-Resession Wired
- **Why:** Context boundary crossing is a core COSMOS capability. Today it requires operator terminal copy/paste.
- **What exists:** `docs/research/AUTO_RESESSION.md` (34KB, stage-1 landed), `RESESSION_SOP.md`, `cosmos_resession.py`, CLOCKS id 18.
- **What's missing:** Context watermark monitor that auto-executes the SOP without operator intervention.
- **Owner:** CCr.
- **Gate:** Context watermark crosses threshold → SOP triggers → fresh session → carry-over via SEED.json, no terminal copy/paste.

### 2.4 Open Sessions Shipped (First Product)
- **Why:** First COSMOS product. GET /api/v1/recents 200, n=200 already live.
- **What exists:** `builds/open_sessions/Open_sessions.py` (built, shipped).
- **What's missing:** Wire `/api/v1/recents` into cDeck leftmost RECENTS (resume-any). Add open-as-action.
- **Owner:** CCr.
- **Gate:** cDeck RECENTS panel shows real session list from Core, open action works.

### 2.5 Low-Hanging Feature Fruit
- **F-70** — commit the dirty tree (51 modified / 58 untracked, HEAD `4b22290`). One git command. Keith's to give.
- **F-53** — prepaid orchestrator satellite CLOCKS id 24 exists, `--install-task` not run. One schtasks line.
- **F-28** — competency pin is a superset now, but COMPETENCY.toml ratings not invented. CCr batch.
- **F-30** — WAVE A wired, WAVE C (Ollama/Aider/Groq) is operator install/key.
- **From BLOCKED items:** check `docs/BLOCKED_ITEMS.md` for the 3 BLOCKED features — these are credentials or one elevated line Keith owns. Fastest wins if unblocked.
- **Owner:** CCr. Batch as WOMB entries.

---

## 3. Tier 2 — Oct 31 Should-Hit (Voice Elevated)

### 3.1 F-15 — Re-Run the CVM Latency Bench
- **Why:** FEATURE_MASTER ranks F-15 as Keith's #1. *"A usability claim with no number is an opinion."*
- **What exists:** `builds/cvm-dt/cvm_dt_bench.py` (31KB), `BENCH_LATENCY.json` (58KB, `transcribe.stt_model_inference` and `respond.voice_post` UNMEASURED), F-21 vosk STT bound in-tree (`cosmos/_f21_stt_probe.json` ok:true).
- **What's missing:** Bench re-run after F-21 landed. The numbers for STT inference latency and voice POST latency.
- **Owner:** CCr (one session, one bench run).
- **Gate:** `BENCH_LATENCY.json` re-run, both UNMEASURED stages have numbers, mtime updated.

### 3.2 Synchronous Desktop Voice MVP
- **Why:** #1 usability bottleneck. Voice Drop burns Grok Bot Credits. Synchronous voice on desktop is the real fix.
- **What exists (every piece):**
  - WASAPI capture: `cvm_dt_voice.py` (47KB), `cvm_dt.py` (57KB)
  - Local STT: `cvm_dt_stt.py` (38KB), `cvm_stt_vosk.py` (33KB), `cvm_stt_whisper.py` (24KB), F-21 vosk bound in-tree
  - TTS: `cvm_tts_piper.py` (16KB), `B4_TTS_PIPER.json`
  - Audio-owner lease (H6): `cvm_supervision.py` (11KB), `cvm_gate.py` (34KB)
  - Classify/confirm/TTS pipeline: `cosmos_voice.py` (in-tree)
  - Voice constants: `cosmos_voice_hardening.py` (in-tree)
- **What's missing:** Wire them into one synchronous loop: capture → local VOSK STT → Core classify/confirm → Piper TTS → audio-owner lease on same headphones. Prove latency acceptable.
- **Owner:** CCr.
- **Scope boundary:** This is the synchronous desktop MVP, NOT the full CVM H1–H10 architecture. No thin-phone path, no offline fallback tier, no phone-side HTTP server. Just: Keith speaks, desktop hears, desktop answers, same headphones.
- **Gate:** End-to-end loop works on desktop with same headphones, latency measured and acceptable, audio-owner lease enforced.

### 3.3 Fix the Clunky/Stilted Speak
- **Why:** Read-aloud on Hermes is clunky and stilted. The user feels it.
- **Root cause:** `cosmos_voice_hardening.py` `_SPOKEN_CAP = 320` chars, whitespace-collapsed, cut at word boundary with `...`. That's a hard trim — explains the stilted feel.
- **What's missing:** Lift the cap, add pause insertion, tune Piper cadence for natural speech, not trimmed fragments.
- **Owner:** CCr.
- **Gate:** Spoken reply is no longer capped at 320 chars, pauses inserted at sentence boundaries, Piper cadence tuned. Perceptual improvement.

---

## 4. Tier 3 — Slip Past Oct 31

These are real but don't block the system being coherent and usable by Oct 31:

| Component | Why it slips |
|---|---|
| Full CVM Voice Mode (H1–H10) | Superset of the desktop MVP. Thin phone, offline fallback, fail-closed, etc. — too much for 31 days with Core-first priority. |
| Federation / Grayson install | Depends on cDeck + XTalk being solid first. |
| Full local voice mode (November arch) | Voice Drop is the temporary substitute; full local voice is the November milestone. |
| FORGE version for coders | Spring beta was the target; Oct 31 too tight for a polished free release. |
| Patent filings P01–P24 | Ongoing legal process, not a dev completion gate. |
| SpiderCaster integration | Unclear if it's even a COSMOS component — needs definition first. |
| COSMOS CODE harness landing in tree | `V:\Streams\cosmos_code\` is a design-in-progress; landing it is a separate merge. |
| Full session tools suite | Open Sessions is the seed; crash/diff/check/anonymize iterate after. |
| CLOCKS collapse (26→1 pulse) | Nice-to-have, not blocking. |
| Mesh additions (9 adapters, 4 hands) | Verify the rest, but not blocking. |
| Tool migration (135 UNDECIDED) | PORT_DECISIONS has 27 apply-ready; batch after Oct 31. |

---

## 5. Weekly Cadence (Oct 1–31)

### Week 1 (Oct 1–7)
- **CCr:** Seed WOMB board from WISHLIST + BACKLOG items. Commit F-70 dirty tree.
- **ORC:** Read `builds/cdeck/FEATURES_KEITH.md` + existing panels. Produce concrete cDeck frontstage nav + wire plan.
- **Keith:** Unblock BLOCKED features (credentials / elevated lines). Run Gitur lanes (Cursor/GitHub/GitLab) — prepare commands, execute.

### Week 2 (Oct 8–14)
- **CCr:** WOMBAT trigger loop wired. Auto-resession watermark monitor wired. Open Sessions wired into cDeck RECENTS.
- **ORC:** cDeck frontstage nav implemented (Talk / Jobs / Model Pool). Telemetry wall kept as backstage.
- **Keith:** Register schtasks lines for F-53, F-19, F-20, F-31, F-65 (built-but-cold daemons).

### Week 3 (Oct 15–21)
- **CCr:** Close easy PARTIALs (F-28, F-30 WAVE C if keys available). Crucible batching logic wired.
- **CCr (voice):** Re-run CVM latency bench. Fix `_SPOKEN_CAP = 320` — lift cap, add pause insertion.
- **ORC:** ChatBot phone DEFINE + research returns on disk (build tabled).
- **Keith:** TokenCTR entitlement check wired into Core spend gate (at least foundational).

### Week 4 (Oct 22–28)
- **CCr:** Synchronous desktop voice MVP wired end-to-end. Latency measured.
- **ORC:** cDeck exe build from `V:\GitHub\cdeck\` (Rust/Tauri). Integration run — all modules together.
- **Keith:** Runtime-binding gate proofs for Tier 1 items.

### Week 5 (Oct 29–31)
- **All:** Final sweep. Runtime-binding gate on the live tree (new-tree-only marker proof). Oct 31 handoff.

---

## 6. Parallel Tracks

| Track | Owner | Focus |
|---|---|---|
| **CCr (Grok)** | Grok 4.6 Build, pen `V:\A`, pid 77372 | WOMB automation, feature closure, resession wiring, Crucible batching, TokenCTR wire, voice bench + synchronous MVP |
| **ORC (this seat)** | Hermes / Solar Pro4 | cDeck frontstage (Python panels), Open Sessions wiring, ChatBot research, integration run, plan maintenance |
| **Keith** | Human | Credentials for BLOCKED features, schtasks lines, Gitur lane execution, directional wishes, final runtime-binding proof, ES.3 install decision |

---

## 7. Constraints & Honest Risks

1. **CCr time is the bottleneck.** Everything in Tier 1 + voice Tier 2 is CCr work. If CCr gets pulled to other tasks, the plan slips. WOMBAT batching (40-WO trigger) exists to amortize CCr time — use it.
2. **F-36 flip gate is independent.** 62/96 ticks, needs 34 more consecutive agreeing ticks. If Core is stable, closes in ~9 minutes. If flaky, stays open. Doesn't block Oct 31 work — it's a separate stability gate.
3. **`builds/cvm-dt/` is retained but was built in a forbidden session.** The code is there. To use it for the synchronous desktop MVP, a session that's allowed to touch it is needed. CCr has the pen for `V:\A` — that should cover it.
4. **Voice Drop burns Grok Bot Credits.** That's the economic reason synchronous desktop voice (local STT + local TTS) matters. The MVP uses local VOSK + Piper — zero credit burn.
5. **Oct 31 is aggressive.** achievable only if Tier 1 and voice Tier 2 stay focused and don't sprawl. The plan intentionally leaves full CVM architecture, federation, FORGE version, and patents for after Oct 31.

---

## 8. Not On This Plan (Explicitly)

- Full CVM H1–H10 architecture
- Federation / Grayson install
- FORGE version for coders (spring beta)
- Patent filings
- SpiderCaster integration ( undefined relationship to Core)
- COSMOS CODE harness landing in tree
- Full session tools suite beyond Open Sessions
- CLOCKS collapse
- Tool migration (135 UNDECIDED)
- Mesh additions verification (beyond the 4 already proven)

---

*Document maintained by ORC. CCr executes. Keith steers.*
