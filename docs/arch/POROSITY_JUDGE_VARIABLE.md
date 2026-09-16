# Proposal for review — Judge as a variable on porosity observations

**Not occupancy. Not USPTO. Not a closed formula.**  
**Do not implement this as a change to T.** Opus tensor math stays
`T[i, j, a]` / `tensors[agent][vs][axis]` / schema `/5`.

CCr (Grok 4.6, session `f47bad79`) proposed a fold change, then reverted
it on Keith’s word: *keep it original; Opus defined the math.* This note
is the change and the reasoning, for other mouths to critique.

Hand to: Opus (author of T), Luna (independent formulation), GLM / Sol
(critics), ORC. CCr disposes after feedback. Dest mouths stay for grading.

---

## 1. Original (do not change)

Source: `docs/arch/POROSITY_MATH.md`, `docs/arch/POROSITY_MATH_CCR.md`,
`docs/arch/ORTHOGONAL_POROSITY.md`, live `cosmos/cosmos_porosity.py`
(`origin/main`).

**T[i, j, a]** — one cell per **pair × axis**, after **n scored trials**:

| Symbol | Code |
|---|---|
| `freq` | `disagree_n / n` |
| `mean_err` | mean of 1–10 hole scores (critic / Luna / disposer) |
| `mag` = \|v\| | `freq × mean_err` |
| `rescue` | `P(j right \| i wrong)` — needs `who_erred` |
| `cofail` | `P(both wrong)` |
| `xor_err` | `P(exactly one wrong)` |
| `style_fight` | disagree ∧ both right |
| `orth_sketch` | `(xor_err − cofail) × mean_err` — working sketch, not closed |

Shape: `tensors[agent][vs][axis]`. Complement **C** in the same store.
JSONL `obs.jsonl` is authority. SQLite is a projection. GET never mkdir.
Unseen stays `UNMEASURED`. Never zero-fill.

Fold key in code: `(pair_lo, pair_hi, axis)`.

The **JUDGE pack** is already on the observation row so a different judge
can re-score the **same** prompt+outputs. Opus: judge (public / ours /
blend) feeds **the same tensor** when `who_erred` is written. Multiple
judges are **n on T[i, j, a]**, not a new index.

Interaction tensor slot stays **UNMEASURED**.

---

## 2. Live emit (this machine, 2026-09-15)

GET `/api/v1/porosity` against Core `:8770` (old fold, original math):

| | |
|---|---|
| schema | `cosmos-porosity-tensor/5` |
| `n_obs` | **404** |
| `n_pairs` | **19** |
| axis on those rows | all `coding` |
| `authority` on rows | `ccr:g46` **226** · `luna` **178** |
| action | `ballot` 404 |

So 404 trials collapse to 19 pair×axis cells. `mean_err` on a cell is
the mean over **both** judges.

Dest mouths (TEAM_TABS + harvested Gitur PR diffs) stay on disk for
further grading. That is measurement fuel, not Gitur merge backlog.

---

## 3. What CCr proposed (reverted)

Treat **judge** (who scored) as something that **splits the cell**, so
Luna’s vector and G46’s vector on the same pair × `coding` do not share
one `mean_err`.

Tried, in order, then undone:

1. Named Forge axis `judge` next to `coding` / `spec` / `security`.
   Keith: *I don’t know if it’s an axis.* Removed.
2. Stuff the pin into the axis name: `coding@luna` vs `coding@ccr:g46`.
   That is still changing the axis identity.
3. Nest GET as `tensors[agent][vs][axis][judge]`.
   That is **T[i, j, a, k]** — a fourth index.

Keith then: *it’s a variable.* Then: *Opus defined the math — don’t
change it.* Live `cosmos_porosity.py` restored from `origin/main`.
Selftest **19/19**. Cosmos **#558** and **#559** **closed**, not merged.

---

## 4. Reasoning (why it was proposed)

**Problem that is real:** if Luna scores hole-size 4 and G46 scores 9 on
the same dest pair, Opus’s `mean_err` is the mixture (6.5 if equal n).
That number is neither judge’s vector. Live: two authorities, one
19-cell coding grid.

**Mistake:** calling that “smear” and changing **T**. In Opus, *after n
scored trials* **includes** more than one judge. Extra judges are sample
size on T[i, j, a]. `recommend_team` / `coverage` need **one** mag per
pair×axis. Splitting by judge fragments n and can double-count seating.

**What still holds without touching T:**

- Judge is a **variable** on the **row** (who scored), not a hole-set
  axis (how they fail at coding).
- Keep dests so many judges can write many rows.
- A **view** (GET filter `authority=luna`) can show judge-conditioned
  estimators without changing T.
- Model Rater can paint that view. It must not replace T[i, j, a].

---

## 5. Alternative that does not change Opus math

Leave fold key `(i, j, a)`. Leave GET `tensors[agent][vs][axis]`.

Optional, later, only if reviewers want it:

- GET `/api/v1/porosity?judge=luna` (or `authority=`) rebuilds the **same
  estimators** on the **subset** of JSONL rows. Empty subset →
  `UNMEASURED`. Does not mkdir. Does not invent a pair.
- Default GET (no filter) stays the pooled T[i, j, a] Opus defined.

That is a **slice of n**, not a new tensor. CCr will not ship it unless
this note’s reviewers say so.

---

## 6. Questions for reviewers

1. Are multiple judges on one dest pair **supposed** to pool into one
   `mean_err` (Opus n), or is that a bug when judges systematically
   disagree?
2. If judge is a variable, is the occupancy object still only T[i, j, a],
   with judge used only to filter rows?
3. Should Model Rater show pooled T, a judge slice, or both — without
   replacing T?
4. Luna: does an independent formulation (`POROSITY_MATH_LUNA.md`) want
   k on the tensor, or keep k on the row?

---

## 7. Disposition

| | |
|---|---|
| Tensor math | **Original.** T[i, j, a]. Not modified. |
| Live Core file | Restored `origin/main` `cosmos/cosmos_porosity.py` |
| Gitur | cosmos #558 #559 closed; do not merge |
| Dests | Keep. Grade. Garbage mouths still count as n |
| This file | Proposal for critique only |
