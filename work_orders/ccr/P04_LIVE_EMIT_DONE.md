# Gitur BUILD — P04 live-emit on DONE (PLAN.md B2)

**Repo (PRIVATE):** `keithbbf-gif/cosmos`
**Branch:** `ccr/p04-live-emit-done` from GitHub `main` blob. Do not pull unique HEAD.
**Not:** cDeck mix, ballot writer, extra grok.exe, parked leftover PRs, USPTO, 407k pack.

## Job
Extend, do not replace, `tests/test_live_emit.py`. Runner DONE with `runtime_bind=true` requires a value only Core `:8770` can emit (`tree_id=KMesh-COSMOS-live`). pytest `rc=0` is not that value.

Reuse: `tests/test_live_emit.py` GET `/api/v1/status`. Hook `cosmos/cosmos_work_order.py` `file_done`. Do **not** invent `cosmos_runtime_bind.py` as a second Core. Default `runtime_bind` off so existing work-order tests stay DONE.

## Bite
Pin: old `file_done` seals DONE on Output+rc=0 with no Core emit.
Fix: `runtime_bind=true` + missing emit → `FAILED` `MISSING_EMIT`.
Lock: `_bite_` `all_bite:true`. Existing `test_live_emit.py` checks stay; add one that the helper quotes live `tree_id`.

## Luna (cached group, occupancy)
Only `runtime_bind=true` work-orders. GET never-mkdir is a later P03 job, not this PR.
