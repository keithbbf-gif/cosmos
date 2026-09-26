# WO-20260920-002 — COSMOS KB canon: scars/lessons/optim dbase in the LiT

**Grading pile entry.** Scored by JUDGE (not yet seated) with all other outputs.
**Prompt xfer (honest chain):** initial prompt = Keith 2026-09-20 directive:
*"Agreed on the form of the scars/lessons/dbase — proceed. Use them now — w.o. to
make them canon in the LiT."* Context included: the recovered pre-wipe ROLD
(155 scars, `V:\Ai\ROLD` / `pulled/bts-rold/scars.jsonl`), the current ROLD
SCARS (S1–S27), the model scars from WOMBAT notes + HERO autopsies, and the
CCrew seat/optim data from `CCREW_SEATS.md` + `HARNESS.md`.

---

## This job (initial prompt — verbatim)

> Agreed on the form of the scars/lessons/dbase — proceed. Use them now — w.o.
> to make them canon in the LiT.

## What already exists (built this session, pending canon)

| File | Role | State |
|---|---|---|
| `work_orders/ccr/COSMOS_KB.json` | **Source of truth** — models, optim, scars, lessons | 7 models · 35 optim · **164 scars** (155 recovered + 9) · 4 lessons |
| `work_orders/ccr/cosmos_kb.py` | Build script — JSON → SQLite projection | `build` + `query` verbs |
| `work_orders/ccr/ingest_old_scars.py` | One-shot ingest of pre-wipe scars | ran, 155 ingested |
| `live/state/cosmos_kb.db` | SQLite projection (query layer) | rebuilt, 164 scars |

## Canon rules (what this WO makes law)

1. **JSON is the source of truth.** `COSMOS_KB.json` is the only hand-edited
   artifact. The DB is a projection — never hand-edited, always rebuilt:
   `py -3.14 work_orders/ccr/cosmos_kb.py build`.
2. **Scars are append-only, never edited.** A wrong scar stays; a later entry
   names the scar it corrects (same law as ROLD SCARS.md). Status field:
   `ACTIVE | HEALED | SUPERSEDED | RECOVERED`.
3. **Indexed by model, read down the columns.** Every scar/lesson carries
   `scope` (`system | model`) and `model_id` (null for system). Cross-model
   queries are the point: `SELECT model_id FROM scars WHERE kind='...'`.
4. **UNMEASURED, never 0.** Missing cells are `null`/`UNMEASURED`, not
   invented values. Same law as the tensor.
5. **Every scar carries a corrective.** A scar without a fix is a complaint.
   `restricted_tree` is required for sandbox-class scars (see LING-001).
6. **Derivation links.** Scars/lessons that came from a HERO run or derivation
   chain carry the source path (`derivation` field).

## Files to land (closed-form)

| File | Action | Contract |
|---|---|---|
| `work_orders/ccr/COSMOS_KB.json` | **KEEP + canon** | schema `cosmos-kb/1`; append-only scars; UNMEASURED not 0 |
| `work_orders/ccr/cosmos_kb.py` | **KEEP + canon** | `build` (JSON→SQLite, idempotent) + `query` (read-only SQL) |
| `work_orders/ccr/ingest_old_scars.py` | **KEEP** | one-shot; idempotent (skips existing ids) |
| `live/state/cosmos_kb.db` | **KEEP (projection)** | rebuilt by `cosmos_kb.py build`; never hand-edited |
| `docs/COSMOS_KB.md` | **CREATE** | one-page canon: schema, facet table, query examples, maintenance |

## Verification (must pass)

```
py -3.14 work_orders/ccr/cosmos_kb.py build
  → Built ...: {'models': 7, 'optim': 35, 'scars': 164, 'lessons': 4}

py -3.14 work_orders/ccr/cosmos_kb.py query "SELECT COUNT(*) FROM scars WHERE scope='system'"
  → 158   (155 recovered + S25/S26/S27)

py -3.14 work_orders/ccr/cosmos_kb.py query "SELECT model_id FROM scars WHERE kind='PARENT_TREE_WALK'"
  → inclusionai/ling-3.0-flash

py -3.14 work_orders/ccr/cosmos_kb.py query "SELECT model_id FROM optim WHERE key='prefill' AND value='ON'"
  → z-ai/glm-5.3-flash, google/gemini-3.8-flash, inclusionai/ling-3.0-flash
```

## Not in this WO

- Seating the JUDGE (separate, Keith names #587)
- The PE-model training pipeline (WO-20260914-012 — the KB is its human-readable
  canon; the derivation store remains separate)
- Merging the 155 scars into ROLD SCARS.md (ROLD is CCr's desk; this KB is the
  queryable projection — both can coexist)

## Contracts (first and last)

- **First line:** NONE or `diff --git`. Propose only. No merge. No live-tree
  write beyond the named files. No grok.exe.
- **Never:** edit the DB by hand, delete a scar, invent a value, drop the
  `derivation` link on a HERO-sourced scar, or claim GATE_CLOSED on a subset.
- **DONE** = `cosmos_kb.py build` passes + the four verification queries return
  the expected rows.

---

**Derivation chain:** Keith directive → recovered ROLD (155 scars) + model scars
+ CCrew optim → this canon WO. Judge scores this entry against the same bar as
the singles.