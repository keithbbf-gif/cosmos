# Gitur BUILD — P06 COMPARE only after real obs.jsonl rows (PLAN.md C2)

**Repo (PRIVATE):** `keithbbf-gif/cosmos`
**Branch:** `ccr/p06-compare-after-rows` from GitHub `main`.
**Not:** ballot writer, invented pairs, scores to un-UNMEASURED, cDeck mix, leftover PRs.

## Job
Seating/COMPARE of box$ vs token$ only after real rows exist in `live/state/porosity/obs.jsonl`.
At `n_obs=0` return `kind=UNMEASURED`. Same-family double-seat refuse (Sol = Luna). Rotator refuse.

Reuse `cosmos/cosmos_porosity.py` `empty_snapshot`. Do not write fake obs rows.

## Bite
- n_obs=0 → UNMEASURED, no pair, no coverage(N).
- Same-family pair (e.g. gpt-5.6-luna + gpt-5.6-sol) refuses.
- `_bite_p06_unmeasured.py` all_bite:true.
