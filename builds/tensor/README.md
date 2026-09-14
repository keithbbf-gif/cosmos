# builds/tensor — the measurement brain

Three pure-stdlib modules that measure a multi-model coding farm: which
seats punch **different** holes, what the store of record looks like, and
how a score is earned. No network, no secrets, no writes outside the store
root you pass in.

| Module | Job |
|---|---|
| `tensor_math.py` | `T[pair, domain, judge, scaffold, provider]` — estimators, per-model porosity, greedy seating |
| `dbase.py` | append-only JSONL **authority** → rebuildable sqlite **projection** → read API + CLI |
| `grading.py` | charter judge with a two-tier bar, dual-judge, per-seat model rater, cell writer |

Canon inherited from `docs/arch/ORTHOGONAL_POROSITY.md`, `docs/research/docket/P03_POROSITY.md`
and `cosmos/cosmos_porosity.py`: **JSONL is authority, sqlite is a projection, a GET
never mkdir, UNMEASURED until observed, rotators refused, and nothing invents a score.**

## 1. The tensor

P03 defined `T[pair, domain]`. Measured drops showed the **judge**, the
**scaffold** (seat/preload/prefill) and the **provider** move the numbers as
much as the domain does, so they are variance axes, not metadata. A fold
names the axes it resolves; the rest marginalize to `*` (`tensor_math.ALL`).

Estimators, on pair `(i, j)` over a slice, after `n` scored trials:

| Estimator | Definition | Needs |
|---|---|---|
| `freq(disagree_n, n)` | `disagree_n / n` | ballots |
| `mean_err(err_sum, err_n)` | mean observed hole size 1–10 | a critic/judge hole score |
| `mag(freq, mean_err)` | `freq × mean_err` — pair hole-size \|v\| | both of the above |
| `rescue(counts, of=)` | `P(j right \| i wrong)` — directed | `who_erred` |
| `cofail(counts)` | `P(both wrong)` | `who_erred` |
| `xor_err(counts)` | `P(exactly one wrong)` | `who_erred` |
| `style_fight(counts)` | `P(disagree ∧ both right)` | `who_erred` |
| `orth_sketch(xor, cofail, mean_err)` | `(xor_err − cofail) × mean_err` — working sketch, math still open | `who_erred` (+ weight) |
| `complement(counts)` | union coverage `(1 − cofail)` − gap intersection `(cofail)` | `who_erred` |
| `porosity(obs, axis=)` | per-model `P_i[a]`: `wrong_rate`, `mean_err`, `mass = rate × size` | `who_erred` |
| `recommend_team(obs, cands, k)` | greedy: incumbent seated first, then complementarity × score per token | pair obs |

**Honesty law.** `kind` stays `UNMEASURED` until `mag` exists;
`complement_kind` stays `UNMEASURED` until `who_erred` is scored; a pair
nobody observed is `UNMEASURED` and sorts **last** in seating. Missing values
are `None`, never `0.0`. Two exceptions are algebra, not zero-fill, and are
commented as such: when `xor_err == cofail` the sketch is `0.0` for any
non-negative weight, and a model never wrong on a slice has `mass = 0.0`.

**Orthogonality is not disagreement frequency** (a style fight drives `freq`
to 1.0 and discovers nothing) **and not unsigned \|v\|** (that is hole size —
a co-failing pair and a rescuing pair can share the same `mag` while their
complement has opposite sign).

## 2. The store

```
<root>/obs.jsonl        append-only, one orc-tensor-cell/1 row per line   AUTHORITY
<root>/tensor.sqlite    dropped and rebuilt from the JSONL                PROJECTION
```

Schema id `cosmos-porosity-tensor/5`, read shape `tensors[agent][vs][axis]`.

```sql
CREATE TABLE obs (                      -- one graded cell, as ingested
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  dedupe_key TEXT NOT NULL UNIQUE,      -- order_id|seat|judge
  t TEXT, run_id TEXT, order_id TEXT, fn TEXT, domain TEXT,
  seat TEXT, n_seats INTEGER, judge TEXT, scaffold TEXT, provider TEXT,
  model TEXT, gate TEXT, score REAL, keep INTEGER, err REAL, usd REAL,
  format_ok INTEGER, judge_agreement INTEGER, why TEXT,
  cache_version TEXT, rubric_version TEXT);

CREATE TABLE pair_fold (                -- T[pair, domain, judge, scaffold, provider]
  pair_lo TEXT, pair_hi TEXT, domain TEXT, judge TEXT,
  scaffold TEXT, provider TEXT,
  n INTEGER, disagree_n INTEGER, freq REAL, mean_err REAL, mag REAL,
  scored_n INTEGER, rescue_hi_given_lo REAL, rescue_lo_given_hi REAL,
  cofail REAL, xor_err REAL, style_fight REAL, orth_sketch REAL,
  complement REAL, mean_usd REAL, kind TEXT, complement_kind TEXT,
  PRIMARY KEY (pair_lo, pair_hi, domain, judge, scaffold, provider));

CREATE TABLE agent_tensor (             -- one row = agent vs one other agent, one axis
  agent TEXT, vs TEXT, axis TEXT,
  n INTEGER, freq REAL, mean_err REAL, mag REAL, xor_err REAL, cofail REAL,
  rescue REAL, orth_sketch REAL, complement REAL, style_fight REAL,
  kind TEXT, complement_kind TEXT,
  PRIMARY KEY (agent, vs, axis));
```

`pair_fold` holds both the full 5-axis cells and the domain-marginal cells
(`judge = scaffold = provider = "*"`), which is the P03 `T[pair, domain]`
view seating uses.

**Pair observations are derived, not declared.** Two seats that answered the
same `order_id` under the same `judge` are one pair trial:

* ballot = the gate token, so two seats that both say `UNCHANGED` are not a fight;
* `who_erred` comes from the `keep` flags (`none` / `a` / `b` / `both`, and
  `unknown` when either flag is missing);
* hole size uses an explicit `err`/`hole` field when the cell carries one,
  else `10 − min(score)` **only when at least one side was wrong**, stamped
  `err_source="derived-from-score"`. A trial where nobody was wrong gets no
  hole size at all;
* a pair whose seats ran different scaffolds or providers folds that axis to
  `MIXED` rather than picking a side;
* a pair where neither seat balloted is counted `n_unballoted` and dropped —
  silence is not agreement.

**Ingest is idempotent** on `order_id + seat + judge`; re-running the same
file adds nothing. The projection is always rebuildable: delete
`tensor.sqlite`, run `rebuild`, get the same rows back.

### CLI

```bash
python -m builds.tensor.dbase ingest cells.jsonl --root /path/to/store
python -m builds.tensor.dbase rebuild --root /path/to/store
python -m builds.tensor.dbase query   --root /path/to/store --agent ling --vs luna --axis core
python -m builds.tensor.dbase query   --root /path/to/store --snapshot
python -m builds.tensor.dbase selftest
```

`--root` is always explicit — no hard-coded path, no parent-walking, no
fallback ladder. An empty store reads `kind=UNMEASURED`, `n_obs=0` and does
**not** create the directory. A refusal prints JSON with its `kind` and exits 3.

## 3. Grading

The bar is config (`Charter.q_setpoint`), and it is two-tier:

| Outcome | Score | Verdict |
|---|---|---|
| real fix | `>= q_setpoint` (8.0) | KEEP |
| honest no-op — the **literal `UNCHANGED` token** | 7.5 | KEEP |
| re-emission without a fix | 5.0 | DROP |
| hallucination | any | DROP regardless |
| malformed | any | DROP |

A no-op *claim* with no literal token is refused (`UNPROVEN_NOOP`), not
quietly worth 7.5. Anchors: 9–10 exemplary (rare) · 8.0 solid · 7.0 minor nit
· 5.0 no fix · 3.0 charter violations · 1.0 garbage.
`judge_range_report` flags a judge that clusters instead of using the range.

* **Judge interface** — `Judge(id, provider, scorer=...)`. The scorer is
  injected, so this module never makes a call; the charter is applied to
  whatever outcome the scorer returns.
* **Dual-judge** — `dual_judge(primary, second)` refuses a second judge from
  the same model family (`SAME_FAMILY`) and returns `judge_agreement` plus the
  score delta. `judge_disagreement(cells)` publishes the rate per judge pair:
  the judge is a tensor axis, so its disagreement is data, not noise.
* **Model rater** — `rate_seats(root, benches=…)` folds per seat: `format_pct`,
  `usable_pct`, `keep_pct`, `usd_per_keep`, `q_per_usd`, the range report, and
  a `blend` of measured quality with a bench value (weights renormalize over
  the components that exist, so a missing bench never drags Q toward zero). A
  zero-cost seat reads `cost_kind="FREE"` with `q_per_usd=None` instead of an
  invented infinity.
* **Seating** — `recommend_seating(root, candidates, k, incumbent=…)` is
  `tensor_math.recommend_team` fed by the store's derived pair observations
  and blended per-seat scores.
* **Every score writes a tensor cell.** `score_and_record()` is the one write
  path; provenance (`run_id, order_id, fn, domain, pair, judge, scaffold,
  provider`) is mandatory and a score without it is refused before the store
  is touched.

## Tests

```bash
python -m pytest builds/tensor/tests -q
python -m builds.tensor.tensor_math --selftest
python -m builds.tensor.dbase selftest
python -m builds.tensor.grading --selftest
```

Every module carries a **negative-control selftest**, and each test file
proves it: `test_selftest_fails_on_mutated_code` re-executes the module with
one line changed (|v| aliased to `freq`, the orthogonality sign flipped,
`None` replaced with `0.0`, dedupe removed, the `UNCHANGED` token check
dropped, hallucinations kept, the provenance gate removed, …) and asserts the
selftest goes **red**. A selftest that survives mutation is decorative.

The corpora in the tests are **synthetic fixtures** shaped like the real
drops (model families × judges × scaffolds). They exercise the store; they
are not the measured 103-cell corpus and must not be read as anybody's
occupancy. Point `ingest` at the real JSONL to measure the real thing.
