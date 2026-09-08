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

Porosity is a **pair vector on named axes**, not a scalar.

```
v_ij[a]  magnitude  =  disagreement_frequency(i,j | a)  ×  error_magnitude(i,j | a)
orthogonality(i,j)  rises with disagreement (aligned holes → near-parallel)
T[i, j, a]          =  the tensor grid of those pair components
```

**Disagreement frequency** = `disagree_n / n` on that pair×axis. Measured
when two named models return ballots on the same frozen DEFINE.

**Error magnitude** = mean of observed 1–10 hole scores on that pair×axis.
UNMEASURED until a critic, runtime-bind, or disposer scores it. Frequency
may exist while magnitude (and therefore `|v|`) is still UNMEASURED.

**Seating:** among candidates, prefer the model whose observed pair
orthogonality versus the already-seated set is large **per token**. That
is token efficiency × error discovery. UNMEASURED sorts last.

## Store (the database)

| Layer | Path under runtime root | Role |
|---|---|---|
| JSONL | `state/porosity/obs.jsonl` | append-only observations. Authority for this measurement. |
| SQLite | `state/porosity/porosity.sqlite` | rebuildable projection. Never authority. |
| Scalar (existing) | `state/model_rater/porosity.json` | per-model hole-set fold. Unchanged. |

Resolver only: `paths.role("state", "porosity", ...)`. No hand-built path.

GET `/api/v1/porosity` reads. If the JSONL is absent: `kind=UNMEASURED`,
`n_obs=0`, **does not mkdir**. POST records and may create the dir.

## Observation row

```
at, trial_id, profile, stage, axis,
model_a, model_b,          # named pins; rotators refused
disagree: 0|1,             # ballots differ
error_mag: 1–10 | null,    # null = UNMEASURED
tokens_a, tokens_b,        # optional; for seating / token cost
who_erred: a|b|both|none|unknown,
source: local|federation,
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

`cosmos_porosity.hook_trial(paths, runs, profile=, stage=, axis=, trial_id=, error_mag=)`

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
- `POST /api/v1/porosity` — `{model_a, model_b, axis, disagree, error_mag?}`
  or `{action: trial, runs, profile, stage, axis}`.
- Existing `POST /api/v1/model_rater/porosity` remains the **scalar**
  loc/severity fold.

## Seating helper

`recommend(paths, seated, candidates, axes=, costs=)`

Score(c) = sum over seated s, over requested axes, of observed mag(c,s,a)
divided by token cost(c) when cost is known. Missing mag → that term is
skipped (not zero-filled as if measured). A candidate with no observed
pairs is UNMEASURED and sorts last.

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
