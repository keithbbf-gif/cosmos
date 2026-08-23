# SPIKE FINDINGS — cosmos_sched

**Worker:** `cosmos_sched-spike-findings`  
**Instance:** `48051524fc634a40947b201077e4a9e9`  
**Host:** `cursor` (Linux container)  
**Written at (local / UTC):** `2026-08-23T10:05:58.563+00:00`  
**Offset:** `+00:00`  
**Epoch:** `1787479558.5633838`  
**Spike:** `cosmos_sched`  
**Branch:** `spike/cosmos_sched`  
**Contract:** `docs/SPIKE_BRIEFS.md` SPIKE 4 · `docs/FINAL_ARCHITECTURE.md` · `docs/STAGE2A_INCUMBENT_BEHAVIOR.md` §4

This note is an artifact. It carries worker identity, an offset-aware timestamp, and Unix epoch.

---

## What held

The incumbent scheduler scars are load-bearing and they survived contact with a live run:

- **Priority is a manifest field.** A job named `zzz_last_alphabetically` with priority 50 is admitted before `aaa_first_alphabetically` at priority 1. Filename sort would have inverted that.
- **Atomic claim, loser loses cleanly.** 100 overlapping ticks: 100 executions, 100 `LOST_CLEANLY` results. The winner runs the job; the loser does not crash, does not retry that job, and moves on.
- **Three worded outcomes, three destinations.** `rc=0` → `done/`. `rc=2` → `done/findings/` (a checker that did its job is not broken — PLM-44). Anything else → `failed/`.
- **Log-first.** Every run log opens with `RUNNING <claimed-cmd>` and fsyncs before the child starts. Command is built from the claimed identity, not a pre-claim path.
- **Report-never-retry.** A claim older than the stale threshold is ledgered `STALE_REPORTED` and is not admissible again.
- **Helper `_` files are not jobs.** The adapter prints `SKIP helper ... (never claimed)` and leaves the file untouched.
- **Per-worker heartbeats, glob-discovered.** `runner_heartbeat__*.json` finds workers the checker was not told about. Each tick carries aware-local, UTC, offset, epoch, lane, and worker id.
- **A lane with jobs and no worker is FLAGGED.** An unrun queue is not an empty queue.
- **Interrupt-driven wakeup, no polling loop.** `threading.Timer` and Linux inotify both fire work. Measured vs the incumbent 60 s Task Scheduler tick.
- **Typed absence stays distinct.** `NOT_FOUND` ≠ `OUT_OF_CLOCK` ≠ `UNREADABLE` ≠ `NOT_IN_RECORD`. Torn ledger tails `UNPARSEABLE` and refuse. Naive heartbeat timestamps are `OUT_OF_CLOCK`. Empty queue ≠ missing lane.
- **UTF-8 both ends.** Child env `PYTHONIOENCODING=utf-8` + `PYTHONUTF8=1`; parent decodes the pipe as UTF-8. Emoji survives.
- **DOM is a first-class rail.** A `rail=DOM` manifest is admitted by the same scheduler and returns typed `UNREACHABLE` in this container rather than silently becoming CLI/API.
- **Compatibility lane is serialized.** `max_inflight=1` reserved under the admit lock. Parallelism is not the default.
- **Import has no filesystem side effect.**

## MEASURED (this container)

```
MEASURED overlap_iterations=100 executions=100 losers=100
MEASURED priority_winner=prio-high
MEASURED rc2_in_findings=True rc2_not_in_failed=True
MEASURED destinations clean=True broke=True
MEASURED helper_untouched=True
MEASURED lanes_flagged=['lg', 'pb']
MEASURED log_first=True heartbeats=1 glob=FOUND
MEASURED wakeup_timer_s=0.050216 poll_interval_s=60.0 speedup=1194.8x
MEASURED concurrent_start_delta_s=0.000164
MEASURED platform=posix windows={"drive_semantics": "NATIVE_DEMO_REQUIRED", "job_objects": "NATIVE_DEMO_REQUIRED", "msvcrt": "NATIVE_DEMO_REQUIRED", "readdirectorychangesw": "NATIVE_DEMO_REQUIRED"}
MEASURED inotify_note=container-inotify inotify={'wakeup_latency_s': 0.0002609770000390199, 'poll_interval_s': 60.0, 'speedup_vs_poll': 229905.31729244}
```

Two workers entered `claim_and_run` 0.164 ms apart and both children ran concurrently. Timer wakeup is the armed 50 ms delay (no poll). Inotify file-change wakeup was 0.26 ms — five orders of magnitude under the 60 s incumbent tick.

## What surprised

1. **A late overlapping tick often never reaches `try_claim`.** If tick B admits after tick A has already created the claim file, B sees the job as claimed and returns `EMPTY` (nothing admissible). That is *not* a double-run, but it is also not the incumbent's unhandled-loser gap — it hides the race. The proof that "the loser LOSES CLEANLY" has to race `try_claim` itself (`O_EXCL`). The bulk port must treat "already assigned" as `LOST_CLEANLY` / move-on, never as "queue empty, all is well" and never as an exception.

2. **Capacity must be reserved before the admit lock is released.** Two threads calling `admit_one` on a serialized compatibility lane will both see `inflight=0` unless reservation is inside the same critical section as admission. Claim-by-rename alone does not serialize a lane.

3. **`status()` before any tick flags every populated lane.** That is correct: a queue with jobs and no heartbeat is the "sits forever" case. After a worker ticks, the flag clears for that lane. Do not treat "no heartbeat yet this process" as healthy idle.

4. **Inotify is fast enough that a 60 s poll is only a reconciliation backstop.** Filesystem-notification overflow (named in the architecture) was not produced here; the bulk port still needs a loud degraded state plus a bounded scan.

## What the bulk port must change

- Queue authority is **immutable manifests + append-only ledger events**. Directory placement is a projection. Atomic rename / `O_EXCL` is a single-volume optimization, never the authority (architecture decision 2 and 4).
- Concurrency and priority live on the **scheduler**, not on a lane being single-threaded or on a filename.
- Compatibility / legacy mutable-file tools stay on a **serialized** lane until a behavior card earns parallelism. The Legacy Job Adapter maps file-drop → manifest and `0/2/else` → `CLEAN/FINDINGS/BROKE`. No `.bat`.
- `__tNNNN` timeout-from-filename (cap 21600) belongs only on that adapter, not on first-class manifests.
- Stale running work is **reported and never retried**. A new attempt is a new admission, not a silent re-execution.
- Every artifact (log, heartbeat, outcome, ledger event, this note) carries worker identity + offset-aware timestamp + epoch. Naked local timestamps are `OUT_OF_CLOCK`.
- Heartbeats are **per-worker** and **glob-discovered**. Do not revive a shared `runner_heartbeat.json`.
- Wakeups are interrupt-driven (timer, file-change, later Task Scheduler / DOM events). The 60 s poll is reconciliation, not the primary mechanism.
- DOM remains a scheduler rail with typed `UNREACHABLE` / `SESSION_EXPIRED` / `AUTH_REQUIRED` / `BROKE`. This container cannot prove a live browser session.
- Platform-specific behavior goes through the adapter only.

## NATIVE-DEMO-REQUIRED (queue-lane demo on live Windows)

These are implemented behind `WindowsAdapter` and return typed `NATIVE_DEMO_REQUIRED` on this host. The queue-lane demo on Keith's machine must run them, not this container:

| Surface | Why the container cannot close it |
|---|---|
| **Job Objects** | Contain worker subprocess trees (and DOM browser descendants) on timeout/kill. POSIX uses process groups only. |
| **ReadDirectoryChangesW** | Windows file-change wakeup. Inotify is the container analogue and *did* run. |
| **Drive semantics / `\\?\` prefix** | `V:` identity and MAX_PATH (C-60). A 275+ char path without the prefix returns WinError 3. |
| **msvcrt / `SetConsoleOutputCP(65001)`** | Redirected cp1252 is how emoji died when anyone watched the monitor. |
| **Task Scheduler read-back** | Registered durable trigger; must be read back through the OS API. |
| **Live DOM rail** | keith.bbf profile / contained browser exists only on the native box. |

A spike that claims those four Windows surfaces from Linux has not run them.

## Pytest (this container, before final commit)

```
python3 -m pytest cosmos/spikes/cosmos_sched/selftest.py -v --tb=short
```

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /workspace
collecting ... collected 31 items

cosmos/spikes/cosmos_sched/selftest.py::test_positive_priority_is_manifest_field_not_filename PASSED [  3%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_n_concurrent_workers_overlap_in_time PASSED [  6%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_three_worded_outcomes_three_destinations PASSED [  9%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_log_first_running_line PASSED [ 12%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_command_built_from_claimed_identity PASSED [ 16%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_heartbeat_glob_discovers_unknown_workers PASSED [ 19%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_interrupt_timer_wakeup_beats_sixty_second_poll PASSED [ 22%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_interrupt_inotify_file_change_wakeup PASSED [ 25%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_utf8_both_ends_of_the_pipe PASSED [ 29%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_ledger_hash_chain_and_identity PASSED [ 32%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_dom_is_first_class_rail_typed_unreachable PASSED [ 35%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_compat_lane_is_serialized PASSED [ 38%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_timeout_from_filename_capped PASSED [ 41%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_adapter_posix_utf8_and_paths PASSED [ 45%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_rc2_lands_in_findings_not_failed PASSED [ 48%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_lane_with_jobs_and_no_worker_is_flagged PASSED [ 51%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_helper_underscore_file_untouched PASSED [ 54%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_overlapping_ticks_execute_exactly_once_100 PASSED [ 58%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_stale_reported_never_retried PASSED [ 61%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_torn_ledger_refuses PASSED [ 64%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_unknown_flag_exit_2 PASSED [ 67%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_typed_absence_four_states_never_collapse PASSED [ 70%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_heartbeat_naive_timestamp_is_out_of_clock PASSED [ 74%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_empty_queue_is_not_missing_lane PASSED [ 77%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_loser_loses_cleanly_and_moves_on PASSED [ 80%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_windows_surfaces_are_native_demo_required PASSED [ 83%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_posix_job_object_is_not_faked_as_success PASSED [ 87%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_helper_submit_refused PASSED [ 90%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_unknown_rail_refused PASSED [ 93%]
cosmos/spikes/cosmos_sched/selftest.py::test_negative_import_has_no_filesystem_side_effect PASSED [ 96%]
cosmos/spikes/cosmos_sched/selftest.py::test_positive_measured_demo PASSED [100%]

============================= 31 passed in 17.10s ==============================
```

31 passed, 0 failed. Positive and negative controls both closed. This is the pytest run taken immediately before the findings commit.

Re-run: `python3 -m pytest cosmos/spikes/cosmos_sched/selftest.py -v`  
Measured demo: `python3 -m cosmos.spikes.cosmos_sched.demo`
