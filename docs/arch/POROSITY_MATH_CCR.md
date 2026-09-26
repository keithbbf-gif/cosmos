# CCr math review — porosity / orthogonality / complement tensor

**Not a closed formula.** Keith 2026-09-09: math still open. This is what
Core **implements** vs what stays **UNMEASURED**. No invented scores.
No USPTO. Spoken pourosity / orthoganol; written porosity / orthogonality.

## Database (patent WS3 — in Core)

JSONL `live/state/porosity/obs.jsonl` is **authority**. SQLite
`porosity.sqlite` is a **rebuildable projection** (tables `obs`,
`pair_fold`, `agent_tensor`). GET `/api/v1/porosity` never mkdir, never
invents. Empty store → `kind=UNMEASURED`, `n_obs=0`. Rotators refused.
Forge + Crucible + runner hook `record_pair` / `hook_trial`.

Perplex tensor = pair grid `T[i,j,a]` plus complement `C` in the **same**
store. Schema `cosmos-porosity-tensor/5`. Shape
`tensors[agent][vs][axis]`.

## What is measured (when observations exist)

On pair `(i,j)` axis `a`, after `n` trials:

| Symbol | Code | When |
|---|---|---|
| disagreement frequency | `freq = disagree_n / n` | both named models returned |
| error magnitude | `mean_err` of scored 1–10 holes | critic / bind / disposer scored |
| pair hole-size `\|v\|` | `mag = freq × mean_err` | both freq and mean_err exist |
| rescue | `P(j right \| i wrong)` | `who_erred` scored |
| cofail | `P(both wrong)` | `who_erred` scored |
| xor_err | `P(exactly one wrong)` | `who_erred` scored |
| style_fight | both right, ballots differ | `who_erred` scored |
| orthogonality **sketch** | `(xor_err − cofail) × mean_err` | `who_erred` scored; `mean_err` weights, else 1 |

`kind=UNMEASURED` until `mag` exists. `complement_kind=UNMEASURED` until
`who_erred`. Unseen pairs stay UNMEASURED. Recommend ranks measured first;
UNMEASURED sorts last. Never zero-fill.

## What is not closed

- Orthogonality is **not** disagreement frequency alone (style fight).
- Orthogonality is **not** unsigned `|v|` (that is pair hole-size).
- `(xor − cofail) × mag` is the **working sketch**, not a finished formula.
- Interaction tensor slot stays UNMEASURED.
- Per-model porosity vector `P_i[a]` (size + distribution on named axes)
  is folded from pair obs; scalar Model Rater `loc_per_100 × severity` is
  a **different** per-model fold and does not replace `T`.

## Patent ideas (honest)

This file implements **WS3 — porosity tensor + JSONL authority**. Other
FILE packets (P01 MOTIF, P07 fence, P11 SEED, P14 precache, …) are **not**
all shipped as one drop. They stay on the docket. CCr does not pretend
the whole patent pack is coded because the tensor DB exists.

CCr: the sketch is consistent with DEFINE_ORTHOGONAL_POROSITY.md. Do not
replace it with a prettier closed form without Keith.
