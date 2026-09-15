# Gitur BUILD — Judge is one axis (no smear)

**Repo (PRIVATE):** `keithbbf-gif/cosmos`
**Branch:** `ccr/porosity-judge-axis` from GitHub `main`. Not unique HEAD.
**Not:** cDeck mix, ballot writer, invented obs rows, leftover PR merge, pull 8b5ad84.

## Job
Same dest pair, different judges, different vectors. Fold key is
`(pair_lo, pair_hi, axis, judge)`. Axis slot is `coding` when unstamped,
`coding@luna` / `coding@ccr:g46` when stamped. Forge axes include `judge`.
GET never mkdir. JSONL remains authority. Do not invent scores.

## Bite
Two `record_pair` on the same models × coding, `authority=luna` mag 4 and
`authority=ccr:g46` mag 9 → two folds, two tensor cells, mags not equal.
Unstamped rows still live at `tensors[agent][vs][coding]`.
`py -3.14 cosmos\cosmos_porosity.py --selftest` 22/22.
