# CVM Desktop Clock — MOTIF stage-5 critique

- model: `bts_gem`  rc: `0`  secs: `29.9`
- source: `gem_gem_cvmdt_clock_motif_stage_5_critique_g_c4443209_result.json`
- recorded: 2026-08-27T05:19:55-0500 (COW disposition, P10)

---

# cvm_dt - Motif stage-5 critique (gem-api)

This critique assesses `builds/cvm-dt/cvm_dt_clock.py` against its stated contract, the `CVM_ARCH` H-constraints, and live observations. My role as GEM is to provide a "different-family" review, highlighting areas of disagreement or alternative interpretation compared to a Grok-authored module.

### Findings

#### F1: `H10 real OS clock`: `CLOCK_ID` value drift and mismatch with live data

*   **PASS/FAIL**: FAIL
*   **Artifact**: `builds/cvm-dt/cvm_dt_clock.py:L40` (`CLOCK_ID = 17`), `live/state/cvm/pull.json` (`clock_id=16`).
*   **Severity**: HIGH
*   **Critique**: The `CVM_ARCH H10` constraint explicitly states, "Next clock id is **15**". The `cvm_dt_clock.py` source hardcodes `CLOCK_ID = 17`. Furthermore, live data shows `clock_id=16` associated with the `pull.json` data, implying *another* clock (possibly the voice client's own internal pull mechanism, or a precursor) has already claimed `16`. This signifies a critical drift from the architectural blueprint and a mismatch with current runtime data, making `CLOCK_ID = 17` an arbitrary choice lacking clear coordination. If `15` and `16` are already in use, `17` is the *next* available, but the constraint explicitly specified "next is 15". This indicates a failure to adhere to the architectural guidance *or* a lack of update to `H10` to reflect reality. If `H10` was *updated* to reflect `17`, that change is not visible here. The current state suggests uncoordinated clock ID assignment.

#### F2: `H2 satellite` / `H6 exactly ONE AUDIO_OWNER`: Clock implicitly claims `desktop` ownership

*   **PASS/FAIL**: FAIL (against spirit of H6, not direct violation)
*   **Artifact**: `builds/cvm-dt/cvm_dt_clock.py:L109-110`, `builds/cvm-dt/cvm_dt_client.py` (implicit), `test_cvm_dt_clock.py:L157` (`rec1["audio_owner"] == "desktop"`), `live/state/cvm/pull.json` (`audio_owner='none'`).
*   **Severity**: HIGH
*   **Critique**: `H2` states the clock is "heartbeat + projection only", and `H6` mandates "DT never writes the owner file as authority". While `cvm_dt_clock.py` itself doesn't directly write `audio_owner`, it drives `CvmDtClient.cycle_once()`. The `test_cvm_dt_clock.py` test explicitly asserts `rec1["audio_owner"] == "desktop"` after a `poll_once`, indicating that the `CvmDtClient` (driven by this clock) is expected to claim `desktop` ownership. The problem arises because the *live observation* shows `audio_owner='none'`, while `clock_id=16` is present. If `cvm_dt_clock` (with `CLOCK_ID=17`) starts running, it will drive a client that claims `desktop` *without* a visible mechanism for explicitly negotiating or failing that claim if `clock_id=16` or some other process already held `phone` or `desktop`. The clock's job is *not* to implicitly grab owner status, but to reflect it. This implies `CvmDtClient.cycle_once` might be too aggressive in its claim, or the clock is testing an implicit outcome that isn't clearly specified by its *satellite* nature. The lack of `AUDIO_OWNER` field in `cvm_dt_clock.py`'s `_pause_extra()` or explicit `extra` dictionary further supports its supposed non-ownership role, making the client's implicit claim problematic for the clock's satellite contract. This feels like an implicit privilege elevation for a satellite, or a lack of clarity in how `audio_owner` is negotiated *through* this clock's client, rather than merely observed.

#### F3: `Runtime-binding`: Live observation shows DT clock *not* ticking

*   **PASS/FAIL**: FAIL
*   **Artifact**: `cvm_dt_clock.py` docstring, `live/logs/` (absence of `cvm_dt_clock_heartbeat.json`), `live/state/cvm/pull.json` (`core_kind='UNREACHABLE'`, `clock_id=16`).
*   **Severity**: HIGH
*   **Critique**: The docstring clearly defines the runtime-binding value as the heartbeat advancing and `pull.json` advancing "under THIS clock". The live observation directly contradicts this: `live/logs/` contains no `cvm_dt_clock_heartbeat.json`, indicating the DT own-clock is "not ticking natively". Furthermore, `pull.json` shows `core_kind='UNREACHABLE'` and `clock_id=16`. This means the specified runtime-binding value is currently unmet. While the test suite passes under simulated conditions, the actual deployment (or lack thereof) suggests the clock is not yet fulfilling its primary runtime contract. This is the most significant operational failure.

#### F4: `H3 typed refusal` / `H5 keep-her-afloat`: `CvmDtError` handling via `main`

*   **PASS/FAIL**: PASS (with minor caveat)
*   **Artifact**: `cvm_dt_clock.py:L268-272`, `test_cvm_dt_clock.py:L236-242`.
*   **Severity**: LOW (Minor caveat)
*   **Critique**: The `main` function's `except CvmDtError` block correctly prints a JSON-formatted error with `kind` and `detail` to `sys.stderr`, then exits with `2`. This fulfills `H3`'s requirement for a typed refusal (like `UNREACHABLE` seen in `test_dead_core_refuses_and_heartbeats`) and prevents silent failure. `H5` is also maintained as this error handling is client-side and doesn't impact Core. The test case `test_dead_core_refuses_and_heartbeats` confirms this behavior. The minor caveat is that the `traceback` in the `loop` function's `except Exception` block (`L166-177`) prints the full traceback to a log file but only the last 500 characters to the heartbeat, which is reasonable for a heartbeat but still a full traceback on disk. This is a common pattern, not a strict failure, but worth noting for diagnostics.

#### F5: `P8 elegance`: Reuse of `core_get`, `pull_url`, `write_heartbeat`, `pause_flag`/`is_paused`

*   **PASS/FAIL**: PASS
*   **Artifact**: `cvm_dt_clock.py:L26-27` (`cosmos_clock` imports), `cvm_dt_clock.py:L31-32` (`cvm_dt` imports), `cvm_dt_clock.py:L36` (`REUSED` tuple), `cvm_dt_clock.py:L57-81` (`pause_flag`), `cvm_dt_clock.py:L84-93` (`is_paused`).
*   **Severity**: PASS
*   **Critique**: The module explicitly imports and reuses `acquire_lock`, `heartbeat_age_s`, `pid_alive`, `plan_create`, `pythonw_exe`, `read_heartbeat`, `tr_cmdline`, `write_heartbeat` from `cosmos_clock.py`. It also reuses `core_get` and `pull_url` from `cvm_dt`. The `pause_flag` and `is_paused` functions explicitly state they use the "same contract as `cosmos_node_worker`", demonstrating a commitment to a unified pause mechanism. This adherence to shared helper functions for common tasks (HTTP access, heartbeat management, pause logic) strongly fulfills the `P8` elegance constraint by avoiding duplication and consolidating logic.

#### F6: `Pause contract`: `HOLD`/`RESUME-GATE` behavior

*   **PASS/FAIL**: PASS
*   **Artifact**: `cvm_dt_clock.py:L70-81` (`is_paused`), `cvm_dt_clock.py:L116-125` (paused tick logic), `test_cvm_dt_clock.py:L186-218`.
*   **Severity**: PASS
*   **Critique**: The `is_paused` function correctly distinguishes between `HOLD` and `RESUME-GATE` states, stating "HOLD never self-clears. RESUME-GATE stays paused here until WD2 unlinks the flag". The `poll_once` logic correctly sets `extra["tick"] = "paused"` and `extra["state"] = "PAUSED"` if paused, and `drain` behavior allows a `--once` run even while paused. The tests `test_pause_hold_heartbeats_without_pull` and `test_resume_gate_idles_until_cleared` confirm that: 1) Core is not polled when paused, and 2) the heartbeat still advances, correctly reflecting the `PAUSED` state without self-clearing. This behavior aligns perfectly with the stated pause contract.

#### F7: `register() EMITS schtasks /Create and must NOT run it`

*   **PASS/FAIL**: PASS
*   **Artifact**: `cvm_dt_clock.py:L185-200` (`register` function), `test_cvm_dt_clock.py:L221-233`.
*   **Severity**: PASS
*   **Critique**: The `register` function returns a dictionary including `ok: True`, `ran: False`, and `keith_cmds` containing the `schtasks /Create` commands, alongside a `note` explicitly stating it is "EMITTED, not executed. Keith runs COSMOS himself. No bats." The test `test_register_emits_does_not_run` further reinforces this by mocking `subprocess.run` and asserting it is *never* called. This directly satisfies the constraint.

#### F8: `skip_alive by unique clock_id so a second launch no-ops`

*   **PASS/FAIL**: PASS
*   **Artifact**: `cvm_dt_clock.py:L96-103` (`skip_alive`), `cvm_dt_clock.py:L142-152` (`loop` logic), `test_cvm_dt_clock.py:L202-213`.
*   **Severity**: PASS
*   **Critique**: The `skip_alive` function checks for a matching `clock_id` in the heartbeat and verifies if the associated PID is still alive using `pid_alive()`. The `loop` function uses `acquire_lock` first, then `skip_alive`, and exits if a matching, live clock is found. The test `test_skip_alive_same_clock_id` successfully demonstrates that `skip_alive` correctly identifies an active clock with the same `CLOCK_ID` and ignores those with different IDs. This mechanism ensures uniqueness and prevents redundant clock instances, directly fulfilling the constraint.

#### F9: `H10 real OS clock`: "Logged-on only" and "schtasks floor 1 min"

*   **PASS/FAIL**: PASS
*   **Artifact**: `cvm_dt_clock.py:L189` (`plan_create` for `minute`), `cvm_dt_clock.py:L190` (`plan_create` for `onlogon`), `cvm_dt_clock.py:L200` (`note`).
*   **Severity**: PASS
*   **Critique**: The `register` function explicitly generates `schtasks /Create` commands for both a "minute" schedule (`mo=1`) and an "onlogon" trigger. The docstring and `register`'s `note` clearly state "schtasks floor is 1 minute; anything faster is a detached daemon + 1-min self-heal + onlogon" and "Logged-on only". This design aligns with `H10` by using the OS scheduler for coarse-grained (1-minute) triggers and an `onlogon` event, indicating compliance with the "logged-on only" requirement. The `--loop` argument then handles the sub-minute interval as a detached daemon.

### GATE-READINESS Verdict

The desktop clock is **NOT ready for stage-6 runtime-binding**.

**Must Change First:**

1.  **Resolve `CLOCK_ID` inconsistency (HIGH)**: The `CLOCK_ID` in `cvm_dt_clock.py` (17) directly contradicts `CVM_ARCH H10` ("Next clock id is **15**") and the `live/state/cvm/pull.json` observation (`clock_id=16`). A definitive `CLOCK_ID` must be established, reconciled with `H10`, and agreed upon across all relevant components. If `15` and `16` are indeed consumed by other clocks, `H10` in `CVM_ARCH.md` must be updated *before* this clock goes live with `17` to avoid future architectural drift.
2.  **Clarify `AUDIO_OWNER` claiming mechanism for satellites (HIGH)**: The `test_cvm_dt_clock.py` asserting `audio_owner == "desktop"` implies the `CvmDtClient.cycle_once()` driven by this clock actively claims ownership. This behavior is at odds with the clock's `H2 satellite` nature ("heartbeat + projection only") and the spirit of `H6` ("DT never writes the owner file as authority"). There needs to be an explicit negotiation or projection mechanism for `AUDIO_OWNER` status that this clock *observes* and heartbeats, rather than implicitly claims via its client. A satellite clock should not be the initiator of an `AUDIO_OWNER` change, only report on its current state.
3.  **Address live deployment gap (HIGH)**: The primary runtime-binding value is currently unmet, as evidenced by the missing `cvm_dt_clock_heartbeat.json` and the `UNREACHABLE` status in `pull.json` with a different `clock_id`. The clock's code and tests pass in isolation, but the actual stage-6 goal requires live, continuous operation where `last_run_epoch` and `cursor` advance under its authority. This indicates a deployment or configuration issue that must be resolved to bring the clock into active service.