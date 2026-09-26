# Succession — CCr `f47bad79`

Keith 2026-09-17 evening: **THE PEN HAS PASSED to `f47bad79`.**
Chair `716fbaea-a18f-41af-b9cb-e7ecbd164c66` does **not** hold the pen.
That chair is orch only: no live tree, no `CCR.lease`, no Core writes.

This file is the handoff. Orch-authored. Not a lease. Not a SEED.

---

## First acts (in order)

1. Read `docs/CCR.md` + `docs/CODER_BRIEF.md` + this file.
2. **Acquire / retarget** `live/state/control/CCR.lease` onto **your** sid `f47bad79…` (Arbiter resource `ccr:KMesh-COSMOS-live`). Projection on disk at T17:55 still showed sid `716fbaea-…` pid **109496** token **1** schema `/2` — that is **not** a pen grant. Your word + acquire is occupancy.
3. `assert_pen` for **your** sid. One CCr. Pen `V:\A` only. Never `V:\Ai`. Never extra `grok.exe`.
4. Unique HEAD **`8b5ad84`**. Do **not** pull `origin/main`. Do not merge leftover PRs 30/32/36/37/38. Do not merge Gitur cosmos **563/564** or cdeck **320** (thinner than live; Gitur G46 discarded vs unique HEAD).
5. Prove occupancy: `py -3.14 builds\cdeck\test_kdash_working.py` → **165/165**.
6. Bounce Core when you want live GET `/action_chain` to leave `n=0` (Core loaded `skills.py` before the chain wire). `/sandbox` was already MEASURED `job_object`.

**Attribution (measured, this chair `716fbaea`):** post-17:27 mtimes on unique HEAD are **this TUI + its G46 subagents**, not Gitur merges. Evidence: files are **uncommitted** (`??` / `M`) on unique HEAD `8b5ad84`; last git commit on tracked ones is 2026-09-05/09-08, not a 2026-09-17 Gitur merge. Gitur PRs 563/564/cdeck 320 were **not** merged. Keith asked; this chair should know — it issued the `search_replace` / subagent writes.

---

## After 17:27 — this chair (`716fbaea`) local, not Gitur

| Timestamp | Path | This chair |
|---|---|---|
| 17:55:48 | `cosmos/cosmos_stagehand_rail.py` | G46 subagent Stagehand wire |
| 17:55:48 | `cosmos/cosmos_playwright_rail.py` | same |
| 17:44:29 | `tests/test_steal_impl.py` | G46 plugin-waist / steal pins |
| 17:35:00 | `tests/test_steal_http.py` | this TUI HITL GET pin |
| 17:35:00 | `tests/test_hermes_features.py` | this TUI SK4 ACTION pin |
| 17:32:43 | `cosmos/cosmos_vertex_rail.py` | this TUI guard + packets |
| 17:32:21 | `cosmos/cosmos_skills.py` | this TUI `append_action` |
| 17:32:21 | `builds/cdeck/ui/deck_jobs.js` | this TUI stale inflight |
| 17:32:21 | `builds/cdeck/test_kdash_working.py` | this TUI occupancy fold |
| 17:29:29 | `cosmos/cosmos_openrouter_rail.py` | packets G46 + this TUI guard |
| 17:27:04 | `builds/cdeck/ui/deck_studio.js` | this TUI HITL Review paint |

---

## Before 17:27 — this chair local G46, not Gitur

| Timestamp | Path | What |
|---|---|---|
| 17:24:05 | `cosmos/cosmos_packet.py` | Tool-output packets |
| 17:20:55 | `cosmos/cosmos_studio.py` / `cosmos_review.py` | HITL bind |
| 16:51:57 | `builds/cdeck/ui/deck_orc.js` | Chamber ORC |
| 16:51:16 | `cosmos/cosmos_sandbox.py` | Daytona/E2B facade |

---

## Prove (quoted this occupancy)

```
py -3.14 builds\cdeck\test_kdash_working.py          # 165/165
py -3.14 cosmos\cosmos_review.py --selftest           # 7/7
py -3.14 cosmos\cosmos_studio.py --selftest           # 33/33
py -3.14 cosmos\cosmos_stagehand_rail.py --selftest    # 16/16
py -3.14 cosmos\cosmos_playwright_rail.py --selftest   # 21/21
py -3.14 cosmos\cosmos_packet.py --selftest            # 6/6
py -3.14 cosmos\cosmos_rail_guard.py --selftest        # 3/3
py -3.14 cosmos\cosmos_sandbox.py --selftest           # 12/12
py -3.14 cosmos\cosmos_openrouter_rail.py --selftest   # 50/50
py -3.14 cosmos\cosmos_vertex_rail.py --selftest       # 25/25
py -3.14 tests\test_steal_http.py                      # 21/21 (HITL ledger-bound)
py -3.14 -m pytest tests/test_hermes_features.py tests/test_steal_impl.py tests/test_steal_http.py -q
```

Live `:8770` (last probe, no mkdir): `/status` 200 ready `tree_id=KMesh-COSMOS-live` ledger seq **15510** `SKILL_ACCEPTED`. `/skills` MEASURED `verification-before-completion` **v2**. `/sandbox` MEASURED `composed=job_object`; daytona/e2b/modal **named_not_composed**. `/review` 200 `blockers.kind=OK` — HITL rows were none on live (BROKE/FINDINGS/STALE RUNNING only); hermetic POST `/studio` hitl then GET `/review` is ledger-bound. `/action_chain` 200 **n=0 UNMEASURED** until bounce + next accept (Core loaded `skills.py` before the chain wire). `/chamber` `/recall` `/seats` `/temporal` 200 UNMEASURED empty folds. Loopback **legacy** (`live/config/loopback_trust.txt`) — Keith propped the port; do not flip bearer unless he says.

Ledger: `mac_v: 2`. HMAC SEED len=10878 mac `5e7805c6…`. Porosity GET still `/5` MEASURED n_obs=619.

---

## SGH besides-Hermes — already vetted

Full vet: `work_orders/ccr/CREW/OUT/FARM/NOW/SGH_VET.md`

**KEEP (on disk, dispose):** HITL bind, Stagehand wire, tool-output packets.

**HOLD (do not compose without Keith):** Daytona/E2B live vendor (needs keys; no key already `UNCONFIGURED`). Remaining 5 Superpowers activate (CCr fence). Graphiti *product* (fold exists). DeerFlow (DOM/PhD/legal). NL cron (optional). OpenHarness/ACP as stacks.

**SKIP:** OpenHands as scheduler, rkchoudary install, Pi install, PydanticAI orchestrator, LangGraph/Temporal/n8n/Letta/CrewAI/OpenClaw-yolo/ruflo, Chamber as second scheduler, plugin-waist again. No Hermes `yolo`/`off`, no in-process cron, no agent self-edit of live skills.

---

## Farm (if you keep it)

WOMBAT = GF38 Vertex `gemini-3.8-flash` (fat job pack, **no patent**). JUDGE = `qwen/qwen3.8-max-0902`. Crew: GLM 5.3, two SOL, Muse Spark **1.2** (`meta/muse-spark-1.2`), Luna, Gemini 3.6 Flash, DS V4 Flash 0731, DS V4 Pro 0813, Gemini 3.8 Flash OR, Grok 4.6 OR. Cursor BUILD = grok-4.6; CHECK = Composer 2.5 not Auto. Job pack = tensor + `cosmos/*.py` to ~80% window; closest-to-job in ITEM tail so cache family stays. Prefix must stay identical per seated coder.

Judge r2: SOL Daytona GOOD, leftover GOOD, Muse chamber BAD (duplicate of landed POST).

Three KEEP WOs in `work_orders/drop/` (`wo-20260917T165800-keep-hitl` …801 stagehand …802 packets). **Not** in the live runner bucket (that path still spawns `grok.exe`).

---

## Gitur (do not merge onto unique HEAD)

| Agent | PR | Dispose |
|---|---|---|
| plugin-waist `bc-cb4eb18c` | cosmos **563** draft | Skip. Live already has 24+6 in `tools/` + shims. |
| daytona `bc-8f0e80a1` | cosmos **564** | Skip. Gitur HOST_PEN = whole `V:\` would refuse Job-Object cwd. Live facade is better. |
| chamber-orc `bc-96012a3c` | cdeck **320** | Skip. Paint + POST already on disk. Occupancy 165. |
| recall `bc-1e2315b8` | no PR | Discard. Defaulted `--once` wrong vs WO. Live `standup()` already wired. |
| composer-check `bc-15c2ef13` | — | CHECK vs `origin/main`, not unique HEAD. Not gospel. |

---

## Hard fences (unchanged)

| Fence | Rule |
|---|---|
| One CCr | `f47bad79`. This file's author does not write CORE. |
| Unique HEAD | `8b5ad84`. Do not pull origin/main. |
| Pens | COSMOS `V:\A`. GrokBot `V:\Ai`. Never share a root. |
| No extra grok.exe | 5a inject exits; 5b is the live TUI. |
| Occupancy | 165/165. Fold strings into existing pins. Never drop a pin. Extra panes in `deck_*.js` not `app.js`. No JACK'S MESH / `drawCore`. No iframe OpenWork. |
| Loopback | `legacy` until Keith says bearer. |
| Opus T | Frozen. 700k FROZEN. Luna dests pairs-only. |
| Never delete | Stage `_delme`. No bats. No USPTO from this tree. |
| P10 | Agents propose. CCr disposes. |

---

## Pointers

- Session pointer: `V:\A\Ai\COSMOS\BUCm.toml` (git-ignored; `[next]` now names CCr `f47bad79`)
- SGH vet: `V:\A\Ai\COSMOS\work_orders\ccr\CREW\OUT\FARM\NOW\SGH_VET.md`
- Farm watch: `V:\A\Ai\COSMOS\work_orders\ccr\CREW\OUT\FARM\NOW\_watch_crew_job2.json`
- Contract: `docs/CCR.md` · `docs/AGENT_BOUNDARIES.md` · `docs/STEAL_MAP.md`
- Resession SOP: `docs/RESESSION_SOP.md` (5a then 5b; do not 5a twice)
