# Porosity surface — holes, axes, complexity, difficulty

**Not USPTO. Not a closed formula.** Spoken pourosity / orthoganol; written
porosity / orthogonality. Estimators stay UNMEASURED until observed. Do not
invent scores.

Companion: `docs/arch/POROSITY_MATH.md` (Opus `T[i,j,a]`),
`docs/arch/POROSITY_JUDGE_VARIABLE.md` (judge is a co-variable / axis of the
**comparison**, not a hole-set of the coder), Model Rater pack
`snapshot.compare` (`cosmos-porosity-compare/1`).

---

## Porosity

Porosity is the **density (size)** and the **distribution** of **holes**
(errors) on an AI’s surface.

- **Size / density** — how big the miss is (1–10 hole score; pair
  `|v| = freq × mean_err`).
- **Distribution** — *where* the holes sit on the surface (which axis, which
  mistake type, which prompt size, which complexity/difficulty class, which
  judge labeled the bits).

A scalar `loc_per_100 × severity` is hole **size only**. It does not replace
the pair tensor. The surface map is the tensor.

---

## The vector is the comparison

Each model is a hit-string on a fixed set of holes: `+` right, `−` wrong.
Comparing two mouths on one cell is three buckets — **not** a smeared mean:

| bucket | bits | meaning |
|---|---|---|
| **shared hit** | both `+` | both already have the code; not a hole; do not fold into `mean_err` |
| **xor** | one `+`, one `−` | productive disagreement; partner can cover if you pick |
| **cofail** | both `−` | leftover hole; pairing cannot pick it away |

```
coverage     = 1 − cofail          # pair-OR, if a picker exists
orth_sketch  = (xor − cofail) × mean_err   # working sketch, not closed
```

Shared hits are their own category. They hide from `|v|` (an expensive bit
both get right never enters `mean_err`). Clones share hits and cofails.
Complements (A vs C on `++--` / `--++`) are all xor, zero cofail.

**Call ranking:** coverage **per dollar**, then orth. A high-hit expensive
model whose hits are already on cheaper mouths stays on the bench.

Example (cost A ≫ B ≫ C ≫ D): pair **C+D** (max orth, cheap, 9/10 cover);
three **B+C+D** (B patches C+D’s one cofail). A adds no unique hit.

---

## Six surface axes (now) — each has a meter

An axis that nobody can count is not an axis. These six are ones **we**
and/or **public rankers** already emit. Hit = the meter’s pass. Miss = fail
or empty. Missing meter = UNMEASURED, never 0.

| Axis | Hole it maps | **Others measure** | **We measure** | Unit |
|---|---|---|---|---|
| **coding** | wrong code | OpenRouter/AA **Coding** index; **SciCode** %; **Terminal-Bench Hard** % | 4Cs on dest (`py_compile` / ruff / mypy / pytest); first line `NONE` or `diff --git`; Output file exists | % or PASS/FAIL per dest |
| **agentic** | can’t use tools / env | AA **Agentic**; **TAU2**; Terminal-Bench as agent | tool-job dest: allowed tool used, forbidden tool not used, ballot returned | % or who_erred on frozen DEFINE |
| **intelligence** | can’t solve hard Q | AA **Intelligence**; **GPQA Diamond**; **HLE** | KEEP/DROP on a frozen hard DEFINE (same text to every mouth) | % correct |
| **math** | quantitative miss | AA **Math** | same as intelligence, math DEFINE dests only | % correct |
| **instruction** | didn’t obey the contract | **IFBench** | first_line match; `output_what` (`text`/`python`/`no_prose`); Output `folder \| file`; no essay when What=python | 0/1 per dest |
| **knowledge** | fact miss / hallucination | AA-**Omniscience** accuracy + non-hallucination | fact dest + judge `who_erred`; else UNMEASURED until we run those dests | % correct / % non-hallucinate |

**Ours that rankers do not sell** (same tensor, extra axes later — not in the
six yet): pair **coverage / xor / cofail** on a frozen DEFINE; empty-Output
class 1–4; OpenRouter **429 class** vs pin-hole vs mouth-form (S-156);
`cached_tokens` hit/miss; spend vs ledger.

---

## Extra cheap meters (objective only)

Judge KEEP/DROP is **one session’s mouth**. Assume it is only *generally*
consistent across sessions. Prefer bytes we can count without a second LLM.

**Add**

| Meter | Count (no judge) | `+` / size | Why cheap / useful |
|---|---|---|---|
| **brevity** | `tokens_out`; or `+` lines in the diff; or bytes of Output | size. Optional bit: under OPTIMUM when OPTIMUM is a number | Shorter among equal 4C is cheaper to read, cache, and judge. Shared-hit on a 2k dump vs a 40-line patch is not the same product. |
| **brittleness** | 4C pattern: `py_compile` PASS and (`pytest` FAIL or `NO_TESTS`) | `+` = not that pattern; `−` = compiles but doesn’t hold | Looks like code, isn’t. Pair xor here is gold (one mouth ships tests). |
| **robustness** | `pytest` PASS (rc 0). `NO_TESTS` is **not** robust | `+` = tests green | Inverse of brittleness. Needs a dest that has tests. |

**Do not add as meters**

| Tempting | Why not |
|---|---|
| **AI judge 1–10** | Session-drift. Allowed as `judge` co-variable on a row, never as the axis definition. |
| **stability** (same model twice) | Objective, but **not cheap** (2× spend). Later. |

Brevity is a **size** (like `mean_err`), not a fourth 4C bit, unless Keith names a cut (e.g. over OPTIMUM = `−`). Brittleness/robustness are bits **on coding**, next to the four Cs — don’t OR them into “4Cs PASS.”

**Derived display (not an axis):** **V = Q / cost** (blended $/M). Same number as `quality_per_cost`. Free or missing Q → UNMEASURED (`None`), never ÷0. INT/$ COD/$ AGT/$ stay beside it. Calc and show; do not seat on V alone.

Forge lanes (`coding`, `spec`, `security`, `tests`, `tool_use`) are **jobs**.
These six are the **surface**. Record the axis the trial was **run as**.

How a public index becomes a hit-string: pick a threshold only when Keith
names it; until then copy the vendor **%** as size, not as `+`/`−`. Our dests
are already `+`/`−` (4C PASS, first_line ok, KEEP). Do not invent a threshold
to binarize AA.

---

## Pending axes (show **1** until measured)

Include the slot. Do not pretend we counted it. **1** is the multiplicative
identity on a 0–1 quality scale — it does not change V or a product of axes.
**0** is a measured miss (a hole). Never store `1` in `obs.jsonl` as if it
were a trial.

| Axis | Why we want it | Meter when it exists |
|---|---|---|
| **stability** | same dest, twice | second call; ballot hash match (not cheap) |
| **file** | file-work | vendor file index; else UNMEASURED |
| **office** | sheets/docs | vendor office index; else UNMEASURED |
| **long_context** | holes only at 100k+ | needle dest at named length |
| **multilingual** | non-English holes | public MT/MMLU-X when we subscribe |
| **security** | vuln / leak | dest + 4C; forge lane `security` |
| **multimodal** | image/audio miss | AA image in; our vision dests |
| **law** | Crucible | profile axes `law`/`facts`/`procedure` |

---

## Normalize (yes) — fixed scale, not catalog min-max

Catalog min-max would **move every rank** when one card is added. Don’t.

| Kind | Normalize | Unmeasured |
|---|---|---|
| vendor % / Q (0–100) | `/100` → **[0, 1]** | **1** (neutral) |
| 4C / first_line bit | already **0 or 1** | **1** |
| brevity | `min(1, OPTIMUM/tokens_out)` when OPTIMUM is a number; else leave size | **1** |
| difficulty / complexity **class** | **labels, not 0–1.** Do not multiply. Unmeasured = omit, not 1 (1 means hardest) | omit |
| pair coverage / xor / cofail | already **[0, 1]** | omit cell (UNMEASURED), never 0-fill mag |

**Measured 0** = hole. **Unmeasured 1** = “not in the product yet.”  
`V = Q/cost` stays Q on the vendor scale / blended $/M; do not re-min-max V.

---

## Co-variables (do not pool)

Each is a dimension of the comparison. Mixing any two is the 4-and-9 → 6.5
smear.

| Co-variable | Role |
|---|---|
| **judge** | who marked `+`/`−`. An axis of the comparison. Luna’s C-vector ≠ G46’s. Extra judges are **not** extra n on a pooled cell. |
| **mistake_type** | *kind* of hole (off-by-one, wrong API, empty Output class 1–4, preamble not NONE, …). Distribution, not size. |
| **prompt_size** | house vs fat; under 200k vs surcharge band. |
| **complexity** | how many steps (below). |
| **difficulty** | how few AIs can do it (below). |

Tensor cell:

`T[i, j, axis, judge, mistake_type, prompt_size, complexity, difficulty]`

Opus `T[i,j,a]` is one **slice** (pair × coarse work-axis). Default GET
`/porosity` stays that slice. Model Rater `compare` does **not** pool the
co-variables.

---

## Complexity class (steps) — countable

A **complex** task has multiple steps. Class is the step count in the
**frozen statement**, not how hard each step is. Count imperative steps
(read / patch / test / call). Do not guess.

| Class | Steps | Example |
|---|---|---|
| **1** | 1 | one file, one function, one answer |
| **2** | 2 | read X then patch Y |
| **3** | 3 | research → patch → test |
| **4** | **4 or more** | pipeline / MOTIF bite / “then also …” |

Class 4 is the bucket for long chains. Do not invent class 5–10 for
complexity until we have a reason. Difficulty is the other knob.

---

## Difficulty class (who can do it) — countable

A **difficult** task is one **few AIs get right**. Measure: on this dest,
`n_hit / n_seated` across named pins (not rotators). Then bin. This scale
is **not** “higher number = harder.” **Class 1 is hardest. Class 10 is easiest.**

| Class | Who gets it right (Keith anchors) |
|---|---|
| **1** | **no** AI gets it right |
| **5** | only the **top ~10%** of AIs |
| **6** | ~**1%** |
| **7** | ~**0.1%** — **zero at this point** (nobody we can seat) |
| **10** | **essentially all** get it right |

Classes 2–4 and 8–9 are UNMEASURED interpolations until we count them.
Do not pretend a linear % between 1 and 10. The 5 / 6 / 7 anchors are the
calibration; 1 and 10 are the ends.

A class-7 hole is not a seating signal yet — no mouth hits it, so every
pair **cofails**. Record it. Don’t average it into a cheap pair’s mag as
if it were a class-10 typo.

---

## Model Rater

- Scalar porosity pane: size-only (`loc_per_100 × severity`).
- Pair grid: GET `/api/v1/porosity` — Opus `T[i,j,a]`.
- **Compare pack:** `snapshot.compare` (`recommend_pair`, `recommend_three`,
  `top_pairs` with shared_hit / xor / cofail / coverage). Judge stays an
  axis. Empty store → `kind=UNMEASURED`, GET never mkdir.
- Write observations with `record_pair` / `record_hit_vectors` (hit-strings
  `+`/`−`). Do not stuff fake vectors into live `obs.jsonl`.

Code: `cosmos/cosmos_porosity.py` (`COMPARE_SCHEMA`, `SURFACE_AXES`,
`compare_pack`, `recommend_call`). Selftest: C+D pair, B+C+D three, A
benched when A ≫ B ≫ C ≫ D in cost.
