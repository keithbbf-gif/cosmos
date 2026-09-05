# F-25 — the registry projection reported a 3.69-day-old proof as `verified: true`

**Consumer:** COW + the mesh work orders. **Measured 2026-08-31 07:05–07:30Z** on the live
tree `V:\A\Ai\COSMOS`, root `V:\A\Ai\COSMOS\live`, `py -3.14`. Every number below came from
a run; the runs are named and their artifacts are on disk. **Fence honored:** this shift
wrote only under `docs/`, `builds/probe/` and `builds/backup/`. `cosmos/` was not touched —
the change to it is a **proposal** (§6).

---

## 1. The defect, in one line

**`Registry.route()` drops a stale proof. `Registry.live_nodes()` — the function that writes
`live/registry/rails.json` — does not, and hard-codes `"verified": True`.** The same scar,
one function over.

Read straight off the live projection, unmodified:

```
$ py -3.14 -c "...json.loads(Path('live/registry/rails.json').read_text())..."
measured_at 1788160741.85  count 4
  claude-cli  verified True  age_s 318547.6   model haiku              <-- 3.69 DAYS
  gem-api     verified True  age_s    356.8   model gemini-2.5-flash
  oa-api      verified True  age_s    353.7   model gpt-5.6-terra
  sgh-api     verified True  age_s    358.3   model grok-4.6
```

Three rows re-proved six minutes ago. One re-proved last **Wednesday**, and the file says
the same word about all four.

## 2. Why this is the failure class the canon names, not a cosmetic field

`route()` already carries the fix, and its own docstring says why it was needed:

> `cosmos/cosmos_registry.py:238-241` — *"STAGE-7 H-05 FIX (OA, MEASURED): route() filtered
> only on ok, so a link probed live ONCE was dispatch-eligible forever — a stale DOM session
> would be chosen days later."*

The projection was never given that fix. It matters more there than in `route()`, because
**nothing in the tree contradicts the row**: a consumer reads `verified` and has no reason to
read `age_s`. `cosmos_kernel.py:220` writes it at every boot; `cosmos_rails_prober.py:322`
rewrites it on every poll; cDeck, MESH_STATUS and the health board all read it. Each of them
is being told the mesh has four proven hands. It has three, and one memory.

That is **coverage claimed over a hole** — the identical shape as the MAX_PATH backup defect
(F-44), in the registry instead of the walker, and it is what
`docs/SCAR_PLACATION.md` and the runtime-binding gate exist to make impossible.

## 3. A second, quieter lie this uncovers — in the prober

Because the prober asks the projection first, the stale row also makes the prober mislabel
its own skip. `cosmos/cosmos_rails_prober.py:243-272`:

```python
row = registry.live_nodes().get(spec["link_id"])       # :247 - stale row still present
if row and row.get("age_s") < ttl_s: return False      # not taken: 318547 > 3600
...                                                     # falls through to
return _claude_configured(paths)                        # :255 - False, no key on disk
...
row = registry.live_nodes().get(lid)
if row: out.append({**row, "skipped": "fresh"})         # :268 - and the row IS still there
```

The node is skipped because **there are no hands configured**, and the projection reports it
as skipped because it is **fresh**. Two different facts, one label, and the wrong one.
Measured, both before and after — see §5.

## 4. The regression test, proven to bite

`builds/probe/test_registry_freshness.py` — 20 checks. It binds the module under test into
`sys.modules` before anything imports it, so the identical checks run against either
implementation (`tests/*.py` insert `cosmos/` at `sys.path[0]`, which no `PYTHONPATH` can
outrank).

The ledger stamps `last_probe` and the registry computes `age_s` against its own clock, so
the test injects **one** clock into both — two clocks make an age meaningless.

| run | command | result |
|---|---|---|
| against the **live** module | `py -3.14 builds/probe/test_registry_freshness.py --impl-live` | **FAIL — 13 of 20** |
| against the **proposed** module | `py -3.14 builds/probe/test_registry_freshness.py --impl builds/probe/proposed/cosmos_registry.py` | **PASS — 20/20** |

The 7 checks that pass on the live module are the pre-existing invariants (claim ≠ proof, a
node that did not answer is absent, a proof with no model is absent, `nodes.json` ==
`rails.json`). **A test that fails on everything is failing on import, not on the defect** —
these seven are the control that says it is neither.

The 13 that fail, verbatim from `live_value`:

```
STALE row is NOT in live_nodes()          | no row carries verified=True on a stale proof
route() and live_nodes() agree            | the OTHER node is still stale too
the un-reproven node stays out            | max_age_s=None disables the filter  [TypeError]
file_runtime inherits the filter          | the dropped row is NAMED, not silently vanished
the named stale row carries its age       | the projection declares the TTL it applied
PROOF_TTL_S == NODE_PROOF_TTL_S           | route()'s default IS that constant
NEGATIVE CONTROL - everything aged out
```

The suite carries its own negative control as the last check: with every row aged past the
TTL, `live_nodes()` must be empty **and** `live_nodes(max_age_s=None)` must still hold both —
so a "filter" that simply returned `{}` would not pass either.

## 5. What applying it does to THIS tree — measured on a replica, not predicted

`builds/probe/registry_freshness_effect.py` reads the current `live/registry/rails.json`,
rebuilds an equivalent ledger in a temp dir with **each node's real measured age preserved**,
and runs both implementations against it. Read-only with respect to `live/`: it opens
`registry/rails.json` and tests the *existence* (never the contents) of the two claude
credential filenames. It never opens the authority ledger and reads no key material.

Artifact: `builds/probe/_registry_freshness_effect.json`

| | live module | proposed module |
|---|---|---|
| `count` | **4** | **3** |
| `nodes` | claude-cli, gem-api, oa-api, sgh-api | gem-api, oa-api, sgh-api |
| `proof_ttl_s` | `null` (no such key) | `3600.0` |
| `stale` | *(no such key)* | `claude-cli · age_s 318967.4 · verified false` |
| rows with `verified:true` **older than the TTL** | **`claude-cli` @ 318967.4s** | **none** |
| prober label for `claude-cli` | `skipped=fresh` | `skipped=no-hands-configured` |

So the whole live-tree delta is: **one false `verified` becomes one named `stale` row, and
one mislabelled skip starts telling the truth.** The three genuinely-fresh nodes are
untouched, `count` drops 4 → 3 because 3 is the measured number, and §3's second lie closes
without `cosmos_rails_prober.py` being edited at all.

**The row is not deleted, it is RELOCATED.** A projection that silently shrinks teaches
nobody: "claude-cli answered, 3.69 days ago, and nothing has asked it since" is the useful
sentence, and it is now in the file.

## 6. The proposal — `cosmos/` is not this fence

- **`builds/probe/proposed/cosmos_registry.py`** → target `cosmos/cosmos_registry.py`
- unified diff in `builds/probe/proposed/_PROPOSED.diff` (**+82 / −7** for this file),
  regenerable with `py -3.14 builds/probe/proposed/_make_diffs.py`

What it contains:

1. **`PROOF_TTL_S = 3600.0`** at module scope. One number for the whole registry — `route()`
   defaulted to `3600` and the projection defaulted to *forever*, and **that disagreement is
   the defect**. Deliberately equal to `cosmos_rails_prober.NODE_PROOF_TTL_S`: the prober
   re-proves on that cadence, so a shorter TTL here would flap every row between every probe.
   The two modules do not import each other (layering), so the test pins them equal.
2. **`_proven()`** — the four runtime-binding gates (ok · rc==0 · a model that answered · a
   non-empty body) factored out of `live_nodes`, carrying `age_s`. `live_nodes()` and
   `stale_nodes()` both read it and split on age, so the two can never disagree about what a
   proof *is* — only about how old it is. This is why the change is **+82/−7 and not a
   parallel implementation**.
3. **`live_nodes(max_age_s=PROOF_TTL_S)`** — `verified: True` is emitted here and nowhere
   else, and now means five things at once, the fifth being *recent*. `max_age_s=None` is the
   same escape hatch, with the same warning, `route()` already documents.
4. **`stale_nodes(max_age_s=PROOF_TTL_S)`** — proven-once, no-longer-fresh, `verified: False`,
   `proof_state: "STALE"`.
5. **`file_runtime(dest, max_age_s=PROOF_TTL_S)`** — declares `proof_ttl_s` and lists `stale`,
   so a reader can tell *"nothing answered"* from *"nothing has been asked lately"* without
   opening the ledger.
6. **`route()`'s literal `3600` replaced by the constant.** Behaviour identical; the second
   source of truth is gone.

**Fail-closed by construction:** `_fresh()` treats an age it cannot compute as STALE, never as
fresh.

### No regression — measured, not read off the diff

`builds/probe/proposed/run_suites_against_proposed.py` runs the **existing tree suites**
against the proposed module (each in its own subprocess, because suites mutate `sys.modules`
and a shared interpreter would let one suite's leftovers decide the next one's verdict).

| run | result |
|---|---|
| `--live` (control, binds `cosmos/cosmos_registry.py`) | **8/8 PASS** |
| default (binds the proposed module) | **8/8 PASS** |

`test_registry` 20 · `test_boot_attach` 21 · `test_boot_rails` (no SELFTEST line; offline) ·
`test_node_rails` 24 · `test_stage7_fixes` 13 · `test_command` 51 · `test_v1` 18 ·
`test_wave4` 16. The eight are every suite under `tests/` that names `cosmos_registry`,
enumerated by grep rather than by memory.

`test_boot_attach.py:124-128` asserts `verified is True` on all four wired nodes and
`live_nodes()` == the disk projection — it stays green because those four are proven
*milliseconds* earlier in that test, which is the point: **a fresh proof is unaffected.**

## 7. Two things COW should know before applying

- **`live/registry/rails.json` gains keys and loses a row.** Any consumer that reads
  `count` as "how many hands exist" rather than "how many are currently proven" will show 3
  where it showed 4. That is the correction, not a regression — but `builds/cdeck/`,
  `builds/probe/mesh_blockers.py` and the health board read this file and were not re-run by
  this shift. **UNMEASURED: the cDeck panels and the health board against the new shape.**
- **`builds/probe/mesh_blockers.py:326` and `:400` will become stale prose** the moment this
  lands — both say *"`Registry.file_runtime` applies no freshness filter"*, which is the
  finding this closes. Left as-is deliberately: editing them before the proposal is disposed
  of would make the tree describe a fix it has not received.

## 8. What is UNMEASURED

- **The applied change on the live root.** Everything in §5 was measured on a faithful
  *replica* built from the live projection's own numbers. No `cosmos/` file was edited and
  `live/registry/` was not rewritten.
- **The other readers of the projection** (cDeck panels, health board) — named above.
- **Whether `claude-cli` would answer if asked.** This shift proves the *proof* is 3.69 days
  old, not that the rail is dead. `cosmos_rails_prober` declines to probe it because
  `_claude_configured()` finds neither `anthropic_api_key.txt` nor `claude_rail.json`, which
  is F-32 (BLOCKED — Keith) and untouched here.
