# PR #38 — CLOCKS Pulse BUILD (harvest)

- **When:** 2026-09-04
- **Cursor:** `bc-dc8b193e-af1a-4317-89bb-ca80e73949d3` / `run-ff790352-2581-4512-bbbf-3d7b6a5fa407` **FINISHED** (durationMs 1642810)
- **PR:** https://github.com/keithbbf-gif/cosmos/pull/38
- **Issue:** https://github.com/keithbbf-gif/cosmos/issues/34
- **P10:** propose only. Files: `proposals/clocks-pulse-build.md` + `.json`, `proposals/pulse/cosmos_pulse.py`, `proposals/pulse/pulse_bind.py`, `tests/test_clocks_pulse_build.py`.
- **Do not merge.** Do not `/delete` schtasks. Do not stop Core `:8770`.

## Matches encoded target

Pulse 15s + pool-only `claim_next` + calendar `--once`. Health `--supervise` stays until P5 spawn-lease handoff. CLOCKS registry **not shrunk** (26 in, 26 out). Schtasks `/change /disable` + `_delme` rename, never `/delete`. Collector tick `hold_required`. PEER_HEARTBEATS keeps the **declared key set** (not a glob — same scar as Duo 6958190 / PR #32 cDeck feed).

## CCr disposition

**Accept topology as the BUILD proposal.** **Do not apply this pass.** GitHub `main` clone could not see `cosmos_own_clocks.py`; the manifest ships **UNBOUND**. CCr bind against the **live** CLOCKS export (`python proposals/pulse/pulse_bind.py --plan … --live-clocks <export>`) before any write.

### Keep
- Two resident Python processes after collapse: Pulse + Health `--supervise`. Core `:8770` untouched through every phase.
- `pool.claim_next` the only claimer. `cosmos_run` dies (P3 adapters).
- Shadow P0 first. Core-spawn handoff last.
- Binding gate refusals: `CLOCKS_SHRUNK`, `SCHTASK_DELETE`, `CORE_DOWN`, `SUPERVISE_DROPPED_EARLY`.
- Live-host checks marked UNMEASURED (honest).

### Refine (do not apply as written)
1. **Bind live names.** Role slots are null. Inventing the 26 ids would silently miss the real clocks.
2. **CVM 2s is closed.** Classification rule 4 (sub-minute → `pulse.inproc`) would keep CVM clocks as 2s in-process work. Voice refine is TABLED; park CVM rows, do not inproc them.
3. **Motif Driver** is not a preserved second dropper. Pulse owns MOTIF; calendar optional.
4. **PEER_HEARTBEATS** stays a declared roster written by Pulse (`via='pulse'`). Never glob `logs/*heartbeat*.json`.
5. `planted_red` is a **new** wheel clock (not taken from the 26). Fine if the original 26 stay.
6. Tests live in `tests/` so GitLab CI measures them — fence stretch vs `proposals/` only; keep as verification, not a live-tree apply.

Apply later as a **phased CCr write** after bind, starting P0 shadow. Not this tick.

## 2026-09-04 cook tick — live CLOCKS bind (orch harvest, not applied)

- **CCR.lease:** ABSENT (`live/state/control/CCR.lease`). Orch TUI did **not** write `cosmos/cosmos_pulse.py`. P0 shadow **not applied**.
- **Core:** unsigned `/api/v1/status` `ready true` `tree_id=KMesh-COSMOS-live` `ledger_head.seq=6521` `CRUCIBLE_CRITICS_ATTACHED`. Health `--supervise` `ALREADY_UP`. Never stopped `:8770`. Never P5.
- **HOLD:** `PAUSE.flag` absent (lifted). Collector tick still required. Live `collector_heartbeat.json` age 0s (`pid 33704`, `polls 8330`, `tick=idle`). WD2 `pid 9768` `tick=assigned`. Pulse Phase-1 heartbeat **STALE** (`pulse_heartbeat.json` last_run 11:17:52, age ~7544s) — existing `cosmos_pulse.py` is observe-only and not looping.
- **Export:** `work_orders/ccr/live-clocks-export.json` — 26 names from live `cosmos/cosmos_own_clocks.py CLOCKS`.
- **Bound plan:** `work_orders/ccr/pr38-p0-bound.json`. P0 dispositions **all `resident.keep`** (observe, dispatch nothing, claim nothing). `target_disposition` recorded for later phases (park CVM 16+25; Pulse owns MOTIF; Health keep until P5).
- **Role slots bound:** workorder.runner=`COSMOS Work-Order Runner` · collector.tick=`COSMOS Collector` · health.supervise=`COSMOS Health` · cdeck.feed=`COSMOS cDeck Feed` · index.required_daemons=`COSMOS Index` · core.service=`COSMOS Core :8770` (not a CLOCKS row).
- **pulse_bind:** `work_orders/ccr/pr38-p0-bind-report.json` — **BOUND: 26/26**, census `resident.keep=26`, refusals 0. Ran `work_orders/ccr/_pr38/pulse_bind.py` (PR #38 copy) against the live export. Did not install that module into `cosmos/`.
- **Do not merge** #30/#32/#36/#37/#38. Issues #33/#34/#35 still open. No Cursor relaunch.
- **Next CCr write (needs `CCR.lease`):** merge P0 shadow into **existing** `cosmos/cosmos_pulse.py` — due-set + distinct SHADOW heartbeat, collector tick stays, `dispatch=false` `claim=false`. Never `/delete` schtasks. Never P5 this pass.
