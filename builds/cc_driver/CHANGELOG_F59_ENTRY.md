

## 2026-08-31 ~01:35 · `cc/140_queue_timeout_vs_failure` — F-59: the queue recorded a wall clock as a verdict

**The defect, measured.** `cosmos_cc_driver.run_job` collapsed two different facts
into one boolean. A `subprocess.TimeoutExpired` set `ok = False`, and `ok = False`
filed the order in `failed/`. The PROCESS died; the WORK was never asked about.
`live/queue/_lanes/cc-cdeck/failed/070_cdeck_mobile_parity.json` was the proof on
disk: filed FAILED, its whole 219-byte result record reading `"rc": null, "error":
"timeout", "secs": 2404.3` — no stdout, no artifact check, no report. The agent had
already finished.

**What the classifier found when it asked.** `cc_refile.py` reconstructed the run
window from the record's own `ts_start` + `secs` (1788152280.0 → 1788154684.3 — the
end matches `live/state/cc_incident_070_cdeck_mobile_parity_1788154684.json` to the
second, independently), read the fence out of the order's own contract line (`write
ONLY under builds/cdeck/`), and walked it:

```
outcome=TIMED_OUT_WITH_OUTPUT rc=None secs=2404.3 report=no artifacts=3/63391B
  fence=V:\A\Ai\COSMOS\builds\cdeck
  mobile_probe.py            26768 B  t0+1242.9s
  test_transport_parity.py   22643 B  t0+1329.1s
  test_mobile_layout.py      13980 B  t0+1398.3s
```

Three deliverables, 63,391 bytes, all written **inside** the run window — the agent
was done at t0+1398s and was killed at t0+2404s, a thousand seconds later.

Note what the window also did: it **excluded** `PARITY_AUDIT.md` and
`MOBILE_PROBE.json`, both of which the supervisor's report named as 070's output.
They are — but a later job rewrote both (`PARITY_AUDIT.md` at 06:23:51Z, 45 minutes
after 070's window closed, 73,959 → 87,221 B), so mtime can no longer attribute them
to 070 and the record does not claim them. Evidence that has been overwritten is
reported as absent, not asserted from memory.

**The fix — a typed outcome, not a boolean.** New `builds/cc_driver/cc_outcome.py`:

| outcome | filed in | requeue |
|---|---|---|
| `COMPLETED` / `COMPLETED_NO_REPORT` | `done/` | none |
| `TIMED_OUT_WITH_OUTPUT` | **`timed_out/`** (new bucket) | review |
| `TIMED_OUT_NO_OUTPUT` | `failed/` | safe |
| `REFUSED` | `failed/` | **reorder** (re-running it will refuse again) |
| `CRASHED` | `failed/` | safe |
| `BAD_ORDER` | `failed/` | reorder |

The split is on the **work**, not the clock: both timeouts are the same process
event and land in different buckets. And it is not an amnesty — a timeout that
produced nothing still fails (`test_empty_timeout_stays_failed`).

**Three evidence questions asked before anything is filed** (`_finish` → the
`<jid>_outcome.json` sidecar):

1. did the agent emit its MANDATORY LAST LINE JSON? — recovered from
   `TimeoutExpired.stdout`, which the old code threw away. Measured on this host:
   the partial stdout of a killed child **does** survive the kill (Windows 10,
   py 3.14 — `test_partial_stdout_is_recovered_from_the_kill`). The driver now
   writes the stdout sidecar on the timeout path too, where it never did.
2. did files land under the order's declared write-fence inside the run window?
3. do the files the report *claims* actually exist, with an in-window mtime? Each
   is typed `verified` / `stale` / `missing` — `missing` is the fabricated-compliance
   signal, and it is a first-class field, not a footnote.

**070 re-filed by the classifier, not by hand.** `cc_refile.py --apply` moved it
`failed/` → `timed_out/`, wrote `returns/070_cdeck_mobile_parity_outcome.json`, and
staged the superseded result to
`builds/cc_driver/_delme/predispose_070_cdeck_mobile_parity_result_20260831T062948Z/`.
`cc-cdeck/failed/` is now **empty**. The record states honestly that 070's report is
`report_recoverable: false` — the pre-fix driver kept no stdout, so the agent's
report is *unrecoverable*, which is not the same fact as the agent never writing one.

**Tests, and the proof they were watched fail.** 41 new tests, all run:

```
test_cc_driver_outcome.py   13 tests  OK   (6.5s — real subprocesses, real wall-clock kills)
test_cc_outcome_evidence.py 28 tests  OK   (0.12s)
```

The end-to-end suite driven against the **staged pre-fix driver** in
`_delme/predispose_cosmos_cc_driver_20260831T062224Z/`:

```
Ran 13 tests — FAILED (failures=5, errors=7)
  FAIL test_timeout_with_deliverables_is_not_filed_failed
       'failed' == 'failed' : a timeout with deliverables on disk was filed FAILED
  FAIL test_partial_stdout_is_recovered_from_the_kill
       unexpectedly None : no stdout sidecar written for a timeout
  FAIL test_outcome_is_a_type_not_a_boolean
       {'timeout_with_output': None, ...} != {'timeout_with_output': 'TIMED_OUT_WITH_OUTPUT', ...}
```

12 of 13 fail on the old code. The one that passes is `test_completed_still_files_done`
— correct: the success path was never broken, and a suite that failed on *everything*
would only prove it was miswired.

That comparison is possible because the driver grew one seam: `claude_bin()` honours
`COSMOS_CC_CLAUDE_BIN`, so `_stub_agent.py` can play an agent that finishes-then-hangs.
The current driver is exercised completely unpatched; only the pre-fix copy (which has
no seam) is monkeypatched. **F-59 survived because the timeout path had never once been
executed by a test** — driving real `claude` costs 40 minutes and money, so nobody did.
The stub costs 3 seconds.

**Fleet gate: 103/104, 0 flaky.** Both new suites are collected by
`cosmos_selftest_clock` (`builds/*/test_*.py`; 69 + 35 = 104) and both passed. The
single failure is **not from this work**: `tests/test_refusals.py` —
`docs/REFUSAL_TAXONOMY.md` has drifted from `cosmos/*.py`, which `cosmos_refusals.py`
scans (`code_dir.glob("*.py")`, line 225). Nothing in this entry touches `cosmos/`;
`cosmos_backup_clock.py` was written **2.1 minutes before** the gate ran and
`cosmos_backup.py` 5 minutes before, by a concurrent agent whose taxonomy regeneration
is still in flight. Left alone: another agent holds that fence.

**Files** (all under `builds/cc_driver/`, plus this entry):
`cc_outcome.py` (new, the classifier) · `cc_refile.py` (new, the repair tool) ·
`cosmos_cc_driver.py` (edited: `timed_out/` bucket + `route_dir`, classify-before-file,
`TimeoutExpired.stdout` recovery, stdout sidecar always, `claude_bin()` seam, typed
`BAD_ORDER`) · `_stub_agent.py` (new, test agent) · `test_cc_driver_outcome.py` (new,
13) · `test_cc_outcome_evidence.py` (new, 28) · pre-fix driver staged in `_delme/`.

**What this does NOT fix.** On Windows the timeout kill reaches only the top process —
a `claude` that has spawned children can leave them running. 070's own record cannot
prove that either way. This is a real gap and it belongs to whoever owns process-tree
teardown; it is not silently folded into the "fixed" claim.
