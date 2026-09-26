# HOLD — Opus tensor math. Do not change T[i,j,a].

**Opus defined** `docs/arch/POROSITY_MATH.md`: pair `(i,j)` axis `a`,
shape `tensors[agent][vs][axis]`. Schema `/5`. Judge is a **variable**
on the observation (JUDGE pack / `authority` stamp) so another judge can
re-score the same dests. It is **not** a named Forge axis and **not** a
fourth tensor index. CCr reverted `cosmos/cosmos_porosity.py` to
`origin/main`. Closed cosmos #558 #559. Do not merge those.

---

# Gitur BUILD — Judge is one axis (no smear) — SUPERSEDED, do not implement

**Repo (PRIVATE):** `keithbbf-gif/cosmos`
**Branch:** `ccr/porosity-judge-axis` from GitHub `main`. Not unique HEAD.
**Not:** cDeck mix, ballot writer, invented obs rows, leftover PR merge, pull 8b5ad84.

## Job
Same dest pair, different judges, different vectors. Judge is a
**variable** (who scored), not a named Forge scoring axis. Fold key is
`(pair, axis, judge)`. GET tensors[agent][vs][axis][judge]. Do not add
`judge` to PROFILE_AXES. GET never mkdir. JSONL remains authority. Do
not invent scores.

## Bite
Two `record_pair` on the same models × coding, `authority=luna` mag 4 and
`authority=ccr:g46` mag 9 → two folds, two tensor cells, mags not equal.
Unstamped rows still live at `tensors[agent][vs][coding]`.
`py -3.14 cosmos\cosmos_porosity.py --selftest` 22/22.
