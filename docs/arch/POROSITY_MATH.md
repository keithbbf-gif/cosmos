# Porosity / orthogonality tensor — math + dbase plan

**Not USPTO. Not a closed formula.** Surface, six axes, complexity/difficulty
classes: `docs/arch/POROSITY_SURFACE.md`. CCr plan. Luna files an independent
formulation as `POROSITY_MATH_LUNA.md` from 8-session evidence. Core
implements the **estimators that have observations**; everything else is
`UNMEASURED`. Spoken pourosity / orthoganol; written porosity / orthogonality.

## Database (Core occupancy — already in tree)

| Layer | Path | Role |
|---|---|---|
| Authority | `live/state/porosity/obs.jsonl` | append-only observations |
| Projection | `live/state/porosity/porosity.sqlite` | rebuildable `obs`, `pair_fold`, `agent_tensor` |
| API | GET `/api/v1/porosity` | never mkdir, never invents |

Empty store → `kind=UNMEASURED`, `n_obs=0`. Rotators refused. Forge /
Crucible / runner hook `record_pair`. Schema `cosmos-porosity-tensor/5`.
Shape `tensors[agent][vs][axis]`. Complement `C` lives in the same store.

## Estimators (when both named models returned)

On pair `(i,j)` axis `a` after `n` scored trials:

| Symbol | Code | Meaning |
|---|---|---|
| `freq` | `disagree_n / n` | disagreement frequency |
| `mean_err` | mean 1–10 hole size | critic / Luna / disposer scored |
| `mag` | `freq × mean_err` | pair hole-size `\|v\|` |
| `rescue` | `P(j right \| i wrong)` | needs `who_erred` |
| `cofail` | `P(both wrong)` | needs `who_erred` |
| `xor_err` | `P(exactly one wrong)` | needs `who_erred` |
| `style_fight` | both right, ballots differ | not orthogonality |
| `orth_sketch` | `(xor_err − cofail) × mean_err` | **working sketch**, not closed |

`kind=UNMEASURED` until `mag` exists. `complement_kind=UNMEASURED` until
`who_erred`. Unseen pairs stay UNMEASURED. Never zero-fill.

## Team of k

`coverage()` seats incumbent first, then `recommend()` vs seated.
`recommend_team(k)` returns that greedy team. Goal: maximize
error-discovery coverage per token. Low orthogonality = same errors and
same blinds. UNMEASURED pairs sort last.

## What is not closed (Luna may disagree)

- Orthogonality ≠ disagreement frequency (style fight).
- Orthogonality ≠ unsigned `|v|` (that is hole-size).
- Interaction tensor slot stays UNMEASURED.
- Per-model porosity vector `P_i[a]` is a fold of pair obs; Model Rater
  `loc_per_100 × severity` is a **different** fold and does not replace `T`.
- Judge axes (public / ours / blend / split) feed `ours` scores into the
  same tensor only when `record_ours` / Luna `who_erred` writes them.

## Plan

1. Keep JSONL authority. SQLite projection only.
2. Luna grades WO dests → `who_erred` / KEEP/DROP → `record_pair`.
3. `recommend_team(k)` for cheap-coder pairing (already GET `/porosity`).
4. Luna independent FILE `docs/arch/POROSITY_MATH_LUNA.md` — do not confirm
   this sketch. CCr disposes after Luna.
5. No invented scores. No USPTO from this TUI.
