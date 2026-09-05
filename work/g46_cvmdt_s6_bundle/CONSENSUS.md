# CVM DT own-clock — stage-6 consensus (G46)

Fold of the runtime-bound stage-5 critiques:

| rail | artifact | bytes | sha256_16 |
|---|---|---:|---|
| gem-api / bts_gem | `docs/critique/cvmdt_CRITIQUE_gem-api.md` | 11638 | f94061e1b3ec7f28 |
| oa-api / bts_oa_api | `docs/critique/cvmdt_CRITIQUE_oa-api.md` | 16484 | 3f8962ca56c0ed1a |

Both: **NOT ready for stage-6 runtime-binding** at dispatch. This slice fixes the software-fixable HIGHs (CLOCK_ID, native heartbeat emit) and SUBTRACTs the duplication they named. It does not pretend Core `:8770` is up, does not run `schtasks`, and does not edit `cosmos/` or the live tree.

## Shared HIGH (both rails)

### 1. Native DT heartbeat is missing — gate is not a green log

GEM F3 / OA #1. `live/logs/` has `cvm_clock_heartbeat.json` (id 16) and no `cvm_dt_clock_heartbeat.json`. Loopback `rc=0` is not the gate. The module already *calls* `write_heartbeat` on a tick; the live file is absent because the emitted schtasks line has not been registered, and the error-path heartbeat in `--loop` used a thinner schema than `poll_once`.

**Fix (this slice):** one stamp path. Every `poll_once` (pass / idle / paused / refused / unread-control / unexpected) writes `logs/cvm_dt_clock_heartbeat.json` in the handed-in root, cosmos_runner-shaped: `worker`, `pid`, `last_run`, `last_run_epoch`, `last_run_utc`, `polls`, `interval_s`, plus `clock_id` and mode (`state`, `pause_mode`, `core_kind`). Dead Core is `core_kind=UNREACHABLE`, `ok=false` — never fake-alive. `--loop` no longer has a second skinny heartbeat writer.

Keith/COW still owes the elevated `schtasks` install. Once that line is registered, this emit is what stage-6 quotes.

### 2. `CLOCK_ID = 17` is unratified drift

GEM F1 / OA #2. Three numbers were in play:

| id | who actually owns it |
|---:|---|
| 15 | `cosmos_own_clocks.CLOCKS` Runner Pool (`cosmos_pool.py`). Stale H10 prose still says “next is **15**”. |
| 16 | CVM satellite `cosmos_cvm_clock.py`. `live/state/cvm/pull.json` `clock_id=16` is **that** ticket issuer (PASS_THROUGH from GET `/cvm/pull`). |
| 17 | `CLOCKS` Work-Order Runner (`cosmos_work_order_run.py`). The DT clock **stole** 17. |

One truth for **this** satellite: **`CLOCK_ID = 18`** (first integer not in `CLOCKS`). The pull ticket’s `clock_id=16` stays the CVM satellite’s — this clock does not overwrite the issuer id, and `skip_alive` keys on **this** heartbeat file + **this** id, so 16 is foreign by design.

`cosmos/` is untouched this slice (P10). A CLOCKS row 18 is owed on a later own-clocks dispose; the unit test fails if 18 collides.

### 3. Live Core `:8770` is UNREACHABLE

GEM F3 / OA #11. H5 “keep Core up” is an operational condition, not something this client can repair. User: Core is UNREACHABLE **by design** right now. Preserve fail-closed; do not mask with cached/synthetic success.

**Fix:** on `CvmDtError.UNREACHABLE` the heartbeat still advances and stamps `core_kind=UNREACHABLE`. The named cursor-advance gate waits for a restarted Core + registered task.

### 4. H6 audio-owner authority is not proven from the clock file alone

GEM F2 / OA #10. Both note the clock delegates `CvmDtClient.cycle_once()` and the loopback test sees `audio_owner==desktop`. The clock does not open `audio.json`. Owner-file authority is the already-shipped client/handoff surface (H13: CVM satellite remains sole `audio.json` writer).

**Fix (clock, not bloat):** quote `audio_owner` from the cycle; do not add a second claim path. H6 live proof stays a client + restarted-Core concern, not a copy of `AudioHandoff` into this module.

## OA-only (kept)

| # | finding | disposition |
|---|---|---|
| 5 | Unreadable `PAUSE.flag` reported `ok=True` paused, no typed kind | **Fix.** `kind=CONTROL_BLOCKED`, `state=REFUSED`, `ok=False`, heartbeat still advances. |
| 7 | `--loop` generic `Exception` heartbeat dropped `state`/`kind` | **Fix / subtract.** Funnel through `poll_once` (one stamp). `kind=BAD_CORE`. |
| 8 | `--once` bypasses `skip_alive`/lock | **Document, do not add a lock.** Same contract as `cosmos_node_worker`: `--once` is a commanded drain (even while paused). `skip_alive` guards `--loop` only. |
| 13 | `REUSED = (core_get, pull_url, write_heartbeat)` is dead decorative code | **Subtract.** Tuple gone. Unused `core_get` import gone. `pull_url` stays as the quoted provenance field. Identity-of-import tests gone. |
| 3 | H10 design present, deployment proof absent | **Keith.** `register()` already emits; this slice does not run `schtasks`. |

## GEM-only

| # | finding | disposition |
|---|---|---|
| F4 | `CvmDtError` in `main` is typed | **Keep.** |
| F5 | pause_flag/is_paused same contract as node worker | **Keep the local copy.** Importing `cosmos_node_worker` would pull dispatch — not lean. Same pattern as `cosmos_work_order_run`. Nested `pause` dict + duplicate `mode` key **subtracted**. |
| F6 | HOLD / RESUME-GATE | **Keep.** Tests stay. |
| F7 | `register()` emits, does not run | **Keep.** |
| F8 | `skip_alive` unique-id + live pid | **Keep.** Foreign id in the test is now 16 (pull issuer), not a magic “other”. |
| F9 | logged-on + 1-min floor | **Keep.** |

## Subtract (improvement is not bloat)

- Dead `REUSED` tuple + unused `core_get` import.
- Duplicate `--loop` heartbeat writer (skinny `tick=error` extra).
- Duplicate `_pause_extra` keys (`mode` + nested `pause`).
- Import-identity assertions in the test that did not prove transport reuse.

Net: clock LOC must not grow for grow’s sake. No drive literals. No `bts_` imports. Resolver paths only (`--root` handed in; source-layout hop to `cosmos/` is the same as the live file).

## Not done (honest)

- Did not write the live tree or `cosmos/` package.
- Did not register Task Scheduler / run `pythonw --loop` against live.
- Did not restart Core `:8770`.
- Did not add CLOCKS row 18 (owed; cosmos/ freeze).
- Did not rewrite `CvmDtClient` / `DesktopPullClock` / H6 owner-file proof.
- Did not claim the named two-native-ticks-plus-live-cursor gate. Software emit + CLOCK_ID truth are what this bundle proves.
