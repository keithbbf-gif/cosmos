# Wiring check — wish/WO → 4Cs → WOMB re-file → tracer

Verified 2026-09-23 under PAUSE. Read-only; no side effects beyond the tracer
pass already run.

## Chain

```
wish/WO (WOMB_MASTER.jsonl / RESURRECT_*.jsonl)
    │
    ▼
coder output → CREW/OUT/TEAM_TABS/**/*.diff
    │
    ▼  step 6c (_ccr_cycle.py L96 → _tracer.py)
_tracer.check_unprocessed_outputs()
    │  scans TEAM_TABS for *.diff not in state/code_checks.db
    │  runs cosmos_code_checks.run_code_checks() → receipts to code_checks.db
    │  logs AUTO_4CS_PROCESSED / AUTO_4CS_ERROR → CREW/OUT/TRACER.log
    ▼
_tracer.trace_stalled_coders()
    │  CREW/OUT/_watch.json, >900s no output → TRACER_STALL_DETECTED
    ▼
_tracer.count_ready_for_judge()
    │  distinct order_ids with 4Cs receipts
    ▼
ready_for_judge ≥ 30 (JUDGE_BATCH_TRIGGER) → CALL_SOL_JUDGE path
    │
    ▼
Judge verdict → WOMB re-file (WOMB_MASTER state DONE/SCORED)
    │  openai-family coder sets tagged needs-second-judge (WOMBAT rule)
    ▼
Final Auditor bucket (bucket-full-only 30)
    │  `_build_audit_batches.py` slices 5–9 pairs/call
    │  dry-run under pause: 0/30 keeps, gate held
    ▼
CALL_FINAL_AUDITOR.cmd (unrun wrapper; grok-4.7 HIGH, local grok.exe)
```

## Evidence

| Check | Result |
|---|---|
| `_tracer.py` exists + compiles | yes |
| Wired as cycle step 6c | `_ccr_cycle.py:95-96` |
| Live pass | `{"new_4cs_checked":0,"stalled_detected":0,"ready_for_judge":109}` |
| code_checks.db | 1,232 rows, 108 grade-lane order_ids (+4× SKIP_NONPY) |
| 108 leftover grades | `RESURRECT_GRADE.jsonl` PENDING, Judge one-time spawn queued |
| TRACER.log | absent (no AUTO_4CS / stall events yet — correct under pause) |
| PAUSE gate | flag **absent** 2026-09-24 ~17:33 CT (was hold). Not a spawn order. |

## Gaps (not broken, not finished)

1. **Judge re-file loop** — tracer counts ready sets but does not yet write
   verdicts back into `WOMB_MASTER.jsonl` (Judge fires only after release).
2. **Auditor batch-builder** — `_build_audit_batches.py` written; waits on
   `live/queue/gitur_keeps` or `audit_bins/final` reaching 30 judged keeps
   (empty under pause — correct). Does not spawn grok.exe.
3. **needs-second-judge reader** — tag rule documented; no consumer until
   Judge1 finishes an openai-family set.

Gaps 1 and 3 are post-PAUSE; the pipe itself is wired and green.
