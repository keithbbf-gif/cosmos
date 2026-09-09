# DEFINE — Orthogonal porosity tensor (MOTIF stage 1)

**Keith 2026-09-07.** Frozen prompt. Verbatim to every model. Do not paraphrase.
**Spoken:** Pourosity. **Written:** Porosity.

Keith, verbatim: *Pourosity measurement must be built in to FORGE (and every
advesarial trial invoked in COSMOS or any of it's PROFILES). It is measured
ORTHOGANOL to the other agents/models on the axes of interest - so it's a
vector, not a single value. That means it gets a database. This needs to be
architected fully by MOTIF. You have the magnitudge of pourosity -
disagreement frequency times error magnitute - against another model - the
more disagreement the between two models, the more orthoganol the vector for
that pair. This will build a tensor grid for maximizing model choices for
token efficiency and error discovery. Add this to the patent applications.*

## WHAT

Porosity of a coder is a **vector**, measured **orthogonal** to the other
named agents/models on the **axes of interest**. It is not a single scalar.

For models *i* and *j* on axis *a*:

- one observation is an adversarial trial (Forge MOTIF step, or any profile
  trial) in which both models produced a ballot on the same frozen DEFINE.
- **disagreement** is observed when the ballots differ. Do not invent it.
- **error magnitude** is observed when a critic, runtime-bind, or human
  disposer scores the hole (1–10). Until then it is **UNMEASURED**.
- **pair magnitude** `|v_ij| = disagreement_frequency(i,j) × error_magnitude(i,j)`.
- **orthogonality of the pair** rises with disagreement: more disagreement
  between two models → more orthogonal that pair vector. Same-family copies
  that keep the same holes sit near-parallel (aligned holes). Different-mistake
  overlays sit farther from parallel.

The set of pair vectors is a **tensor grid** `T[i, j, a]`. The grid is how
COSMOS **seats** models: maximize **error discovery** (cover residual holes)
per **token** (cheap different-mistake beats an expensive copy).

Because it is a vector/tensor, it **gets a database**. JSONL is the
append-only observation log (authority for this measurement). SQLite is the
rebuildable projection (never authority — same rule as every COSMOS cache).
GET never mkdir. GET never invents a score. Empty store = UNMEASURED.

**Built in**, not optional:

- **Forge** (coding profile): every adversarial trial (background free CLI
  RESEARCH / ARCH / CONSENSUS, and later BUILD dual-lane / CRITICS) writes
  pair observations when two named models return on the same statement.
- **Every PROFILE** that invokes an adversarial trial (Crucible, Diligence,
  Differentiator, Docket, Website GC, UPS when rebuilt) uses the same hook.
- **Every COSMOS adversarial trial** (occupancy engine P05) uses the same hook.
- Scalar Model Rater porosity (`loc_per_100 × severity`) stays as a
  **per-model hole-set fold**. It does not replace the pair tensor.

## TERMS — Keith 2026-09-09 (concepts; math still open)

Spoken: Pourosity, orthoganol. Written: **porosity**, **orthogonality**.
Keith: math is still poorly defined. The **concepts** are:

**Porosity** — of a model (or of the seated set). **How big** the holes
are, **and the distribution** of those holes across the axes of interest.
A scalar `loc_per_100 × severity` is size-only. Distribution is a vector
over named axes (coding vs spec vs security…). UNMEASURED until holes are
scored on those axes. Porosity is **not** the pair.

**Orthogonality** — of a **pair**. **Different × accurate.**
- **High:** the pair identifies **different** errors well (one catches what
  the other misses).
- **Low:** the pair identifies the **same** errors well — and shares the
  **same** mistakes / blind spots.

Disagreement frequency alone is not orthogonality (two models can disagree
and both be right — style fight). Unsigned `|v| = freq × error_mag` is a
pair **hole-size** fold, not orthogonality. Complement `xor_err − cofail`
(when `who_erred` is scored) is the **working sketch** of orthogonality.
Do not treat that sketch as a finished formula. Do not invent scores.

## WHY

A scalar `p(m)` cannot tell you *which other model punches a different hole*.
Copies of one family look “good” and still leave the same swiss-cheese holes.
The pair vector is the occupancy signal: who is orthogonal to whom, on which
axis, at what error size, at what token cost. That is how several inexpensive
models, chosen for disagreement, beat the single best model on price and on
performance (`docs/MOTIF.md` swiss cheese).

## ACCEPTANCE

1. DEFINE file on disk (this file). RESEARCH return on disk. ARCH on disk.
2. Patent packets updated **before filing** (P03 written description + P05
   hook). This TUI does not click USPTO. Not a 14th $65 slot.
3. Database exists: append-only pair observations + SQLite projection.
4. Forge facilitate (and the shared trial hook) records pairs. Rotators
   (`openrouter/free`, `openrouter/auto`, `openrouter/free:free`,
   `openrouter/pareto-code`) REFUSED. Same-model pair REFUSED.
5. Magnitude = disagreement frequency × error magnitude. Mag is UNMEASURED
   until error magnitude is observed. Frequency may be measured first.
6. Seating helper ranks candidates by observed pair orthogonality / token
   cost. UNMEASURED candidates sort last. Never invent a bake-off number.
7. Live emit: GET `/api/v1/porosity` returns `n_obs` and pair folds the
   JSONL actually contains — not a green log.
8. **Complement tensor C** (Keith 2026-09-07: *better way to measure how
   different models complement positively vs negatively — add that as an
   additional tensor in our dbase*). Same observation log. `who_erred` in
   {a, b, both, none} scores rescue / co-failure / XOR-error. `unknown`
   or omitted → C UNMEASURED. Ballot disagreement alone does not invent
   who was wrong. Unsigned T stays.

## OFF-LIMITS

- Do not invent observations, frequencies, magnitudes, or exponents.
- Do not click Patent Center. Do not write `V:\Ai`. Do not post.
- Do not vendor LangGraph/Temporal/n8n as the OS.
- Do not start IMPLEMENT of a fake populated tensor.
- Do not silently swap rotators (H3). Named pins only.
- Do not treat cosine-of-embeddings as the invention. Observed task
  disagreement on named axes is the measurement.
- Do not add a 14th provisional slot. This is P03 new matter before filing,
  with a P05 embodiment (every adversarial trial writes the tensor).
- Do not stand up a blockchain this tick. Public weighted-average digest
  is TABLED in `docs/research/docket/P03_PUBLIC_TENSOR.md`, not Core.

## LIVE EMIT TO HONOR

A value only the live tree can emit: GET `/api/v1/porosity` after a real
Forge (or other profile) pair of named models has returned. `n_obs >= 1`
and the pair key matches those two model ids. Empty tree stays
`kind=UNMEASURED`. A selftest with a recorded pair is not the live emit.

## MOTIF

Stage 1 = this file. Stage 2 RESEARCH = `CREW/OUT/DOCKET/R5_ORTHOGONAL_POROSITY.md`.
Stage 3 ARCH = `docs/arch/ORTHOGONAL_POROSITY.md`. Consensus is Keith's math
(not contested). BUILD = Core tensor store + Forge/profile hook + Gitur.
CRITICS later vs this DEFINE.
