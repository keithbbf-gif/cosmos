# Sets to grade — 2026-09-24

No Judge. A set is finished only when it has three code copies and each copy passes the 4Cs.

## Count

| | |
|---|---|
| Jobs in `RESURRECT_GRADE.jsonl` | 108 (78 pairs, 30 solos, **0 triples**) |
| Arms checked | 186 |
| Arms with no Python | 15 |
| Arms whose patched Python passed py_compile + ruff + mypy + pytest | **1** |
| Jobs with 3 passing code copies | **0** |
| Jobs with 2 passing code copies | **0** |
| Jobs with 1 passing code copy | 1 (`grade-gitur-cdeck-b25-011` side b only) |

Third copy: not on disk. Grade folders have `cursor-a` and `cursor-b` only. One WO dir in the old inbox has 3 diffs (`gitur-cosmos-slp-pediatric-milestones-editor`); those are solo retries, not a code triple.

## How the 4Cs were run

Each `.py` hunk was applied onto a temp copy of the current file (`git apply --whitespace=nowarn`). Live tree was not written. Receipts: `work_orders/ccr/SETS_4C.jsonl`.

Of the failing arms, file tags were mostly `FAIL` (applied, then a tool failed) or `APPLY_FAIL` (hunk does not fit the current tree).

Floor is 30 finished sets. Finished sets: 0.
