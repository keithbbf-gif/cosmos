# DEFINE — Complement tensor C (compatible-model seating)

**Keith 2026-09-08 (this TUI):** pull the most useful tensor for determining
compatible models into a 1–9 MOTIF work order and run it. Named in
`docs/arch/ORTHOGONAL_POROSITY.md` — **Complement tensor C[i, j, a]**.

## WHAT

Unsigned orthogonal porosity `|v|` does not split help vs hurt. Complement
C scores *who covered whose hole*:

- rescue(j|i) = P(j right | i wrong)
- cofail(i,j) = P(both wrong)
- xor_err = P(exactly one wrong)
- style_fight = P(disagree ∧ both right)
- signed = (xor_err − cofail) × error_magnitude

Seating prefers **signed complement per token** when `who_erred` is scored,
else `|v|`. GET `/api/v1/porosity` already folds C. This DEFINE is the MOTIF
thread so Model Rater auto-stores and auto-shows it (not a scalar afterthought).

## WHY

Forge dual-lane / Crucible critics need a pair measurement that says
“this model rescues that one” — not just “they disagree.” Compatible seating
is complement, not mere orthogonality.

## Constraints

GET never mkdir. GET never invents. `who_erred` unknown → C UNMEASURED.
JSONL `state/porosity/obs.jsonl` is authority; SQLite is a projection.
Scalar `loc_per_100 × severity` stays the per-model fold.

## BUILD already on disk

`cosmos/cosmos_porosity.py` SCHEMA `cosmos-porosity-tensor/2`. This DEFINE
binds Model Rater to **read C automatically** on catalog load and to write
pair observations on dual-lane trials (Forge facilitate hook).
