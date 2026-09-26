# Session loose-ends sweep — 2026-09-23

Sweep of unfinished instructions and unanswered questions in the current
ORC/CCr session (seed `ses_f3375edd5ffevQBjUDw27RZMpg`). Items marked DONE
were closed in-session; OPEN items need Keith or a post-PAUSE action.

## DONE (closed this session)

1. **Seat-1 harness fix (grok-coder)** — `6_grok_gitur/PACK.toml` = `cli:grok`,
   SuperGrokHeavy, `forbid cursor_cloud_agent`. Stale "Cursor Gitur BUILD
   only" lines corrected in `CCREW_SEATS.md`, `hero_coders/README.md`,
   `WOMB_CREW.md`, `COSMOS_KB.json`. Cursor credits remain Gitur-role-only.
2. **Wiring: tracer step 6c** — `_tracer.py` wired into `_ccr_cycle.py` line 96;
   live pass returns `ready_for_judge: 109`, 0 stalls.
3. **Second-Judge rule for WOMBAT** — written into `WOMBAT_SEAT.md` and
   `hero-wombat-luna/TASK.md` (`needs-second-judge: true` at file time on any
   set with an `openai`-family coder; second Judge from GLM/DS/Qwen pool).
4. **20 new HERO coder packs + seat keys** — `hero_coders/07…26` PACK.toml +
   LAYERS.md; `SEATS`/`OR_WINDOW` extended; `SEAT_TAG.get()` fallback so no
   KeyError.
5. **Team regroup** — 4 clusters of 3 (Hard Alpha/Beta, Proven Core, Ortho
   Depth), MAX effort everywhere; recorded in `RUN_CONFIG.md`.
6. **Lease** — reacquired after the prior holder (sid `ses_f2e6d2643ffe…`, pid 32724) expired and the pid was gone. Now token 9, sid `ses_f3375edd5ffevQBjUDw27RZMpg`, `expires 1790294582`. Arbiter file is `state/control/CCR.lease.jsonl`, not the forged Core `leases.jsonl`.
7. **PAUSE** — `live/state/control/PAUSE.flag` is **absent** as of 2026-09-24 ~17:33 CT.
   It was `mode=hold` earlier this session. This seat did not delete it.
   Protocol treats absence as RUNNING (`cosmos_pause.py`). This seat is **not**
   treating absence as a spawn order. Five `grok.exe` processes were already
   running (pids 33864, 28788, 31560, 26700, 20464); none were started or
   killed here.
8. **Auditor batch-builder** — `_build_audit_batches.py` on disk + `py_compile`
   clean. Status pass: `[SCAN] Found 0 judged keep items` /
   `WAITING: 0/30`. Bucket-full gate held. `CALL_FINAL_AUDITOR.cmd` fail-closes
   if the flag is missing or `hold` (verified exit 4; did not start grok.exe).
   Stricter than protocol (absence = RUNNING) until Keith confirms the lift.
9. **`hero_wombat_gf38` pointer** — `CCREW_SEATS.md` WOMBAT section + Order #3
   and `hero_coders/README.md` now name Luna 6 MAX; GF38 DUD marked historical.

## OPEN (needs Keith or post-release)

1. **PAUSE flag missing** — confirm whether Keith lifted it. Until that
   confirmation, this seat will not spawn WOMBAT, Judge, Auditor, or another
   grok.exe. Do not restore the flag unless Keith says the lift was a mistake.
2. **Core :8770 re-sign** — live `leases.jsonl` has `FORGED_EVENT line 1`.
   Temp re-sign proof passed; backups exist (`*.bak_20260923`). Needs Keith's
   explicit OK to rewrite live ledger.
3. **Collector/Runner schtasks** — still Disabled + stale (9-17 / 9-09).
   Re-enable only on resume.
4. **WOMBAT summon** — seat recorded (`WOMBAT_SEAT.md`), not called. ORC
   spawns WOMBAT (and Scribe, Final Auditor) after release.
5. **Historical `cursor-gitur` rows** — `WOMB_BOARD*.jsonl`,
   `WOMB_BOARD_PAIRED.jsonl`, `WOMB_CREW` measured cells, `JUDGE_PACK.json`
   still carry old via strings for completed work. Treated as immutable
   history; do not rewrite. Live routing reads the fixed PACK/config files.
6. **Second Judge seat** — pool named (GLM 5.3 / DS / Qwen) but no
   `CALL_*_JUDGE2.cmd` yet; write when first `needs-second-judge` set exists.
7. **`ROSTER_QUALIFIED_FAST.md` → live teams** — the 24-model roster and the
   12-seater 4×3 clusters in RUN_CONFIG are not yet bound to `_code_or_seat.py`
   dispatch defaults (SEATS keys are registered; per-cluster membership is
   config-file only until cranked).

## Questions asked, not yet answered by Keith

- When does PAUSE lift? (drives everything below)
- OK to re-sign live `leases.jsonl` (Core restart)?
- OK to re-enable collector/runner schtasks on release?
- Confirm Judge family split: first Judge SOL 6 (`openai`), second from
  GLM/DS/Qwen — already noted for WOMBAT; confirm before Judge2 spawn.
