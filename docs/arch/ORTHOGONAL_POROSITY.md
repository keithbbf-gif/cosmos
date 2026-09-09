# ARCH — Orthogonal porosity tensor

**DEFINE:** `work_orders/ccr/DEFINE_ORTHOGONAL_POROSITY.md` (verbatim).
**RESEARCH:** `work_orders/ccr/CREW/OUT/DOCKET/R5_ORTHOGONAL_POROSITY.md`.
**Decision:** Keith named the math. Not contested.

Rubric (first): one Core, ledger remains OS authority, this store is a
**measurement database** (JSONL authority for pair observations; SQLite
projection). GET never mkdir. GET never invents. Rotators REFUSED. Forge
and every profile adversarial trial write the same hook. Scalar
`loc_per_100 × severity` stays a per-model fold, not the tensor.

## Decision

Keith's terms (2026-09-09). Math still open. Concepts:

**Porosity** — hole **size** and hole **distribution** (per model, vector
on named axes). How big, and where.

**Orthogonality** — of a pair: **different × accurate**.
High = they catch **different** errors well. Low = they catch (and miss)
the **same** errors.

```
Porosity P_i[a]     size + mass of i's holes on axis a     (per-model)
                    UNMEASURED until i is scored wrong on a
Pair hole-size
  |v_ij[a]|         =  disagreement_frequency × error_magnitude
                    (not orthogonality; style-fight can raise freq)
Orthogonality O_ij[a]  working sketch when who_erred is scored:
                    (xor_err − cofail) × error_magnitude
                    = existing signed complement
                    UNMEASURED until who_erred
T[i, j, a]          pair grid (freq, mag, O when scored)
```

**Disagreement frequency** = `disagree_n / n` on that pair×axis. Measured
when two named models return ballots on the same frozen DEFINE.

**Error magnitude** = mean of observed 1–10 hole scores on that pair×axis.
UNMEASURED until a critic, runtime-bind, or disposer scores it. Frequency
may exist while magnitude (and therefore `|v|`) is still UNMEASURED.

Do not alias orthogonality to `|v|`. Do not invent a closed formula.

**Seating:** among candidates, prefer the model whose observed pair
orthogonality versus the already-seated set is large **per token**. That
is token efficiency × error discovery. UNMEASURED sorts last.

**Keith 2026-09-09:** several cheap in-house seats, orthogonal, can match or
beat one frontier. Seat the cheap specialist that punches a **new** hole.
Do not add a same-family twin and call it diversity.

**Complement tensor C[i, j, a]** (additional, same database). Unsigned `|v|`
does not split help vs hurt. From `who_erred` on the same observation:

```
rescue(j|i)  = P(j right | i wrong)     # positive complement
cofail(i,j)  = P(both wrong)            # negative complement
xor_err      = P(exactly one wrong)     # productive disagreement
style_fight  = P(disagree ∧ both right) # does not cover holes
signed       = (xor_err − cofail) × error_magnitude
```

Directed: rescue of *j* given *i* is not rescue of *i* given *j*.
`who_erred` in {a, b, both, none} scores the cell. `unknown` / omitted →
complement UNMEASURED (ballot disagreement alone does not invent who was
wrong). Seating prefers signed complement per token when scored, else `|v|`.

## Store (the database)

| Layer | Path under runtime root | Role |
|---|---|---|
| JSONL | `state/porosity/obs.jsonl` | append-only observations. Authority for this measurement. |
| SQLite | `state/porosity/porosity.sqlite` | rebuildable projection. Never authority. |
| `obs` | one trial row + Irbe stamps (`at`, `authority`, `action`) | |
| `pair_fold` | undirected cell T[i,j,a] | |
| `agent_tensor` | **one row = agent vs other agent on one axis** — the parameter set (freq, mag, xor, cofail, rescue, orthogonality) | |
| Scalar (existing) | `state/model_rater/porosity.json` | per-model hole-set fold. Unchanged. |

GET `/api/v1/porosity` `tensors[agent][vs][axis]` is the same grid. Each
named pin owns a tensor: its parameters against every other seated agent.

Resolver only: `paths.role("state", "porosity", ...)`. No hand-built path.

GET `/api/v1/porosity` reads. If the JSONL is absent: `kind=UNMEASURED`,
`n_obs=0`, **does not mkdir**. POST records and may create the dir.

## Observation row

```
at, trial_id, profile, stage, axis,
model_a, model_b,          # named pins; rotators refused — agent_id keys
disagree: 0|1,             # ballots differ
error_mag: 1–10 | null,    # null = UNMEASURED
tokens_a, tokens_b,        # optional; for seating / token cost
who_erred: a|b|both|none|unknown,
source: local|federation,
authority: source:class,   # who let this trial run; see docs/AGENT_AUDIT.md
note
```

Pair fold key is undirected: `lo, hi = sorted((model_a, model_b))`.
Same-model pair REFUSED.

## Axes of interest

Named per profile. Slots only — values stay UNMEASURED until observed.

| Profile | Default axes |
|---|---|
| forge | coding, spec, security, tests, tool_use |
| crucible | law, facts, procedure |
| diligence | bull, bear, risk |
| differentiator | diagnosis, plan |
| docket | novelty, enablement, prior_art |
| website | copy, layout, a11y |
| (other) | task |

A trial names **one** axis it is scoring. Do not broadcast one ballot
disagreement onto every axis.

## Hooks (built in)

`cosmos_porosity.hook_trial(paths, runs, profile=, stage=, axis=, trial_id=, error_mag=, authority=, action=)`

`runs` = `[{model, ballot, tokens?}, ...]`. Every unordered pair of distinct
named models: `disagree = (ballot_i != ballot_j)`. error_mag optional.

Call sites:

1. **Forge** `cosmos_forge_bg.facilitate` — RESEARCH / ARCH / CONSENSUS1 /
   CONSENSUS2 after ballots exist.
2. **POST `/api/v1/porosity`** — explicit pair or `action=trial`.
3. **Every later profile trial** (Crucible critic round, Diligence
   bull/bear/risk, dual-lane BUILD, CRITICS) calls the same function. No
   second store.

## HTTP

- `GET /api/v1/porosity` — tensor snapshot. Never mutates.
  Directed grid: `tensors[agent][vs][axis]`.
- `POST /api/v1/porosity` — `{model_a, model_b, axis, disagree, error_mag?,
  authority?, audit_action?}` or `{action: trial, runs, profile, stage,
  axis, authority?, audit_action?}`.
- Existing `POST /api/v1/model_rater/porosity` remains the **scalar**
  loc/severity fold. Forwards `agent_id` / `action` / `authority`.

## Seating helper

`recommend(paths, seated, candidates, axes=, costs=, mode="complement")`

Default `mode=complement`: Score(c) = sum over seated s, over requested
axes, of (rescue(c|s) − cofail(c,s)) × error_magnitude, divided by token
cost(c) when cost is known. Missing C → fall back to unsigned mag for
that term. `mode=mag` uses `|v|` only. Missing term skipped (not
zero-filled as if measured). A candidate with no observed pairs is
UNMEASURED and sorts last.

## Public weighted tensor (TABLED)

Parked: `docs/research/docket/P03_PUBLIC_TENSOR.md`. Not this BUILD.
Do not post. Do not click USPTO. Do not stand up a chain.

## Not this ARCH

- Cosine of embedding vectors as the measurement.
- Invented bake-off numbers, a fake superlinear exponent, federation
  scores without a host.
- A second Core, a vendor graph runtime, a 14th provisional.
- Replacing family-axis occupancy. Family still does not count twice.
  The tensor *measures* which pairs are actually orthogonal.

## BUILD this pass

Core module `cosmos/cosmos_porosity.py` + GET/POST + Forge facilitate hook
+ tests + P03/P05 written description (before filing). cDeck pane paints
GET later; measurement must not wait on chrome.
