# CORE RESTRUCTURE — staged MOTIF work orders

**Authored:** 2026-08-30, Claude Code (Opus 5), after the audit in
`docs/CHANGELOG_2026-08-30_CC_AUDIT.md`.
**Form:** stage-1 work orders. COW disposes; G46 and the node rails execute. Each phase names
its own runtime-binding gate, so "done" is an emitted value, never an assertion.

---

## Do NOT rewrite the core

38,821 lines across ~85 modules, running a live 20-daemon fleet. A big-bang rewrite would
discard the parts that are genuinely good — typed refusals, never-delete, atomic writes, the
ledger as authority, heartbeats published on every tick — and reintroduce the parts that are
not. **Strangle, don't rewrite.**

Nothing that failed on 2026-08-26 failed because the code was badly written. It failed because
of five structural patterns:

| # | Pattern | What it cost |
|---|---|---|
| 1 | **A claim accepted as evidence** | the health board counted `"inflight"` as work; the driver inferred in-flight from filenames; `COLLECTOR.md` prose was scraped as state → **3 days of silence** |
| 2 | **Liveness read as progress** | every artifact proved "I ticked"; none proved "work advanced" |
| 3 | **Prose used as specification** | a docstring contradicted two tests and cost this audit a regression; the tracker is both a human doc and a database |
| 4 | **No gate on the gates** | 34 of 58 suites dead, nothing running them |
| 5 | **Tests pinning spellings, not properties** | valid refactors turned things red, so red stopped meaning anything |

Every phase below removes one pattern. Phases 1–3 hold nearly all the value.

---

## PHASE 0 — make change safe · **DONE 2026-08-30**

- `builds/selftest_clock/` registered on a 15-minute clock; discovers `tests/` **and**
  `builds/*/test_*.py`; flake-aware (a retry-pass is FLAKY, never PASS).
- `builds/health/` gained `_route_progress_row()` — progress bound to an emitted receipt, RED on
  the wedge signature, and a fresh tree is explicitly not a false alarm.
- `cosmos/cosmos_inflight.py` — owned, expiring leases; `release_completed()` closes on receipt.

**Gate (met):** `selftest_clock_heartbeat.json` shows `passed 68 / total 70 / flaky 0`, and
`watchdog_board.json` carries a `route_progress` row.

---

## PHASE 1 — contracts in one machine-checked place

**Removes pattern 3.** `cosmos_principles.toml` + `--audit` is already the right shape; it just
never covered subsystem contracts, so `register_node_rails`' docstring could contradict
`test_boot_attach` and `Registry.file_runtime` indefinitely.

**Work order 1.1 — `docs/contracts/*.toml`, one per subsystem** (registry, queue, ledger, rails,
motif, service). Each states, in machine-readable form, the invariants that subsystem promises.
Start by transcribing what the CODE actually does today, not what the prose claims — where they
disagree, the code wins and the disagreement is recorded as a finding.

**Work order 1.2 — `cosmos/cosmos_contracts.py --audit`.** Verifies each contract against (a)
the module, (b) its tests, (c) its docstrings. A contradiction is a typed FAIL, not a warning.

**Runtime-binding gate:** the auditor, run against the live tree, emits a
`contract_audit_result.json` naming at least one contradiction it found and one it verified —
proving it can actually detect drift rather than always passing.

---

## PHASE 2 — own the state; derive nothing

**Removes patterns 1 and 2. The deepest fix, and the one that makes the wedge impossible.**

Four primitives are authority. Every other module reads them and derives nothing:

| Primitive | Status |
|---|---|
| `ledger` (authority.jsonl) | exists |
| `registry` | exists |
| **`inflight` leases** | **built 2026-08-30** |
| **`tracker`** | **JSON becomes source; markdown becomes a rendered projection** |

**Work order 2.1 — `live/state/motif_tracker.json` as source of truth.** Stage per slug, with
`updated_at` and the artifact that justified the stage. `MOTIF_TRACKER.md` is regenerated from
it on every tick. COW's disposition blocks stay human-authored in a clearly separated region the
renderer never overwrites. **Additive today:** JSON is published as a projection;
`write_tracker_json` still hard-codes `"authority": "markdown"`.

**Work order 2.1a — agreement evidence before the flip (WHOSE judgement).**
`live/state/motif_agreement.json` banks whether the JSON projection on disk agrees with a
fresh parse of `MOTIF_TRACKER.md`, every tick. `consecutive_agreements` can only rise on an
actual `agree`; any divergence resets it to 0. `FLIP_STREAK_TARGET = 96` (24 hours on the
15-minute motif-driver clock, encoded in `cosmos/cosmos_motif_driver.py`). `flip_ready` is
**advice, never an action.** **The human who lands the flip is Keith or COW on the `cosmos/`
fence**, and not before `flip_ready` is true. Flipping because the projection *ought* to match
is the 2026-08-26 scar (a claim accepted as evidence → three days of silence). This work order
does not change `write_tracker_json`. A row parked on this threshold is Keith's / COW's call,
not an agent's.

**Work order 2.2 — `parse_tracker()` reads JSON.** Markdown parsing survives only as a one-time
importer, marked deprecated with the date. Lands in the same tick as the authority flip (2.1a).

**Work order 2.3 — audit every remaining derivation.** Grep for state inferred from filenames,
mtimes, or prose. Each hit either moves to a primitive or is documented as advisory-only, the
way `soft_names` now is. **Artifact exists (2026-08-31):** `cosmos/cosmos_derivation_audit.py`
(`unreviewed_count=0`). **OPEN remaining:** `parse_tracker_markdown` (work order 2.2; waits
on the 2.1a flip). Four filename/prose skip sites were reclassified **advisory** on the
`cosmos/` fence (`critique_filename_stage`, `inflight_filenames_mtime`, `wd2_dhx_haystack`,
`wd2_uses_inflight_filenames` — counted, cannot decide a skip). Closing `parse_tracker_markdown`
is the `cosmos/` fence, after `flip_ready`.

**Runtime-binding gate:** delete a row from the rendered `MOTIF_TRACKER.md`, run one tick, and
show the row restored from JSON — proving the markdown is genuinely a projection. This gate
**cannot pass** while `authority` is `"markdown"`; it is the proof that 2.1+2.2 landed, not a
reason to skip 2.1a.

---

## PHASE 3 — one rail seam

**Removes pattern 5 for the largest group of suites.** `_ledger_is_authority`,
`attach_to_kernel`, probe, and spend are duplicated across five rail modules; three of them
carried the same stale assertion and went red together.

**Work order 3.1 — `cosmos/cosmos_rail_base.py`.** One `Rail` protocol + adapter base. Each rail
module keeps only what is genuinely vendor-specific.

**Work order 3.2 — split contract tests from live probes.** Every rail gets an offline contract
test (recorded fixture, no network, no credentials) and a separate live probe that skips
cleanly when unreachable. **This is what makes a green suite mean something** — today
`test_boot_rails` and `test_tls` cannot pass without vendor APIs and a TLS exclusion, so "green"
is unreachable by construction.

**Runtime-binding gate:** the offline suite reaches 70/70 on a machine with no network and no
vendor keys.

---

## PHASE 4 — split the god modules

Hygiene, not correctness. Do it last and only along seams that already exist.

`cosmos_dispatch.py` 2,777 · `cosmos_collector.py` 2,178 · `cosmos_service.py` ~1,500 ·
`cosmos_codex_rail.py` 1,781 · `cosmos_watchdog2.py` 1,350.

**Rule:** no split lands without its tests moving with it and the gate staying green in the same
tick.

---

## PHASE 5 — one refusal taxonomy

Already ~80% there. Collect every `*Error(kind, detail)` into a single documented set so a caller
can branch on `kind` without knowing which module raised.

---

## Execution rules

1. **One phase in flight at a time.** Phase 2 before 3; 4 and 5 last.
2. **Every work order carries its gate**, and the gate is an emitted value — never rc=0.
3. **The selftest clock must be green before and after each landing.** A phase that reddens the
   gate is not done, whatever the return says.
4. **Propose-only for agents; COW disposes.** P10 is unchanged by this document.
5. **The route now reports honestly.** If it stalls, `route_progress` goes RED within 4 hours
   instead of 3 days. That is what makes this plan safe to run autonomously at all.
