# REATTACK — guards cluster (after stage-7)

**Critic, not builder.**  
**Subject:** `main` @ `483e0fe` (stage-7 K1–K6+H2 claimed closed, 341 checks).  
**Cluster:** `cosmos_spend`, `cosmos_validate`, `cosmos_context`, `cosmos_platform`, `cosmos_backup`, `cosmos_health`.  
**Date:** 2026-08-23. **Host:** Linux container, Python 3.12.3.  
**Method:** `PYTHONPATH=cosmos`; run every existing suite that touches the cluster; then **new** probes in `tests/reattack_guards.py`. Docstrings are claims. Behavior is evidence. `cosmos/` was not modified.

A finding without a repro that runs is an opinion. Every OPEN row below names a function that **PASSED HERE**, meaning the hole is present.

```
PYTHONPATH=cosmos python3 tests/reattack_guards.py
# measured HERE: 5 BROKEN / 3 HELD / 0 ERROR of 8

PYTHONPATH=cosmos python3 -m pytest -v tests/reattack_guards.py
# 7 passed  (test_repro_* passes IFF the hole is present)
```

---

## 1. Known residuals vs this cluster

Stage-7 closed the *named* originals. The verify critic (`origin/verify/stage7`) listed residuals that do **not** re-open those ids. This reattack only ranks a residual if it touches the guards cluster **and** a new repro ran.

| known residual | cluster that owns it | touches guards? | this reattack |
|---|---|---|---|
| **Spend over-cap under overlap** | `cosmos_spend` | **YES** | **OPEN** — three new repros, all landed |
| Cross-process arbiter serialization | `cosmos_lock` (foundation) | no | not attacked; not claimed |
| `argv:` runner confinement bypass | `cosmos_runner` (K4 leftover) | no — platform is the exec door; confinement is the runner's | not attacked; not claimed |
| Ingress `envelope_id` traversal | `cosmos_ingress` (kernel-rails) | no | not attacked; not claimed |
| Segment anchor authentication | `cosmos_segments` (foundation) | no — spend/backup use `Ledger`, not `SegmentedLedger` | not attacked; not claimed |
| Worker-id spoofing | `cosmos_sched` (foundation) | no | not attacked; not claimed |

The K6 comment in `cosmos_spend.py` says the check-then-append race is closed:

> "two concurrent callers cannot both slip past the cap"

That sentence is false. Unique rids are real. Cap exclusivity is not.

---

## 2. What the existing suites proved HERE

`PYTHONPATH=/workspace/cosmos`.

| suite | HERE | notes |
|---|---|---|
| `tests/test_spend_context.py` | **PASS** 15/15 | sequential deny holds; no overlap |
| `tests/test_concurrency.py` | **PASS** 17/17 | B7 expired-budget deny holds; no overlap |
| `tests/test_migrate_health.py` | **PASS** 8/8 | synthetic ingest |
| `tests/test_v1.py` | **PASS** 18/18 | backup hash + rehearsal happy path |
| `tests/test_stage7_fixes.py` | **PASS** 13/13 | K6 proves **distinct rids**, not an exclusive cap |
| `tests/test_node_rails.py` | **PASS** 12/12 | sequential spend-gate on a dispatcher |
| `tests/test_features.py` | **FAIL** `FileNotFoundError: 'py'` | **not marked** NATIVE-DEMO-REQUIRED |
| `tests/test_wave3.py` | **FAIL** same `py` inside `Runner.run_one` | **not marked**; platform/runner checks never ran HERE |

Bare `pytest tests/` without `PYTHONPATH=cosmos` still cannot collect (`No module named 'cosmos_*'`).

The suites that pass never instantiate the failure modes below. Sequential `$0.70` then `$0.70` on a `$1` cap **does** deny. That is a real hold. It is not the overlap case.

---

## 3. Ranked findings

### BLOCKER

**RG-B1 — The spend cap is still not exclusive under overlap. Stage-7 sampled `expect_head_seq` at append time, so a stale decision binds a fresh head and `STALE_HEAD` never fires.**

H3 / Decision 1 / harvest B7 / verify residual #5. The builder's K6 comment claims the opposite.

`guarded_call` projects (`_state()`), decides against that snapshot, then calls:

```python
self.ledger.append("SPEND_RESERVED", ...,
                   expect_head_seq=self.ledger.head_seq())
```

`head_seq()` is evaluated **now**, under no lock, after the decision. The scheduler does this correctly — it captures `head = self.ledger.head_seq()` **before** `queued()` / the claimant check, then passes that captured value. Spend does not.

Timeline that landed HERE:

1. Stale caller projects: `settled=0 reserved={}` (head = 1, the `BUDGET_SET`).
2. Fresh caller runs a full `guarded_call($0.70)` to completion. Ledger is now `BUDGET_SET, SPEND_RESERVED, SPEND_SETTLED` (head = 3).
3. Stale caller continues with the empty snapshot, passes the `$1` cap check, then `head_seq()` returns **3**.
4. `expect_head_seq=3` matches. `STALE_HEAD` does not fire. Second `$0.70` settles.

Measured HERE (`SPEND-OVERCAP-STALE-PROJECTION`):

```
spent=[0.7, 0.7] total=1.4 cap=1.00 reserved=2 settled=2 denied=0 stale_kinds=[] errors=[]
```

Mechanism (`SPEND-HEAD-SEQ-SAMPLED-AT-APPEND`):

```
source_binds_live_head=True projected_head=1 later_head_seq_samples=[1, 3]
```

The same hole across **two OS processes** on one ledger file (`SPEND-OVERCAP-MULTIPROCESS`). The flock serializes append+re-prime. It does not re-check the cap.

```
got=[('fresh', 0.7, None), ('stale', 0.7, None)] spent=1.4
events=['BUDGET_SET', 'SPEND_RESERVED', 'SPEND_SETTLED', 'SPEND_RESERVED', 'SPEND_SETTLED']
```

A no-hook sibling (barrier inside the callback, 24 trials) also landed — once on retry 1, once on retry 5. That is corroboration, not the evidence. The evidence is the two deterministic probes.

Repro:

```
PYTHONPATH=cosmos python3 -m pytest -v \
  tests/reattack_guards.py::test_repro_spend_overcap_stale_projection \
  tests/reattack_guards.py::test_repro_spend_overcap_multiprocess \
  tests/reattack_guards.py::test_repro_spend_head_seq_sampled_at_append
# all three PASSED HERE (adversarial PASS = hole present)
```

Or: `PYTHONPATH=cosmos python3 tests/reattack_guards.py` and read the three `SPEND-OVERCAP-*` / `SPEND-HEAD-SEQ-*` BROKEN lines.

`test_stage7_fixes` K6 and `test_spend_context` "over-cap call DENIED" remain green. They never overlap two callers around one projection.

---

### MAJOR

**RG-M1 — `BUDGET_SET` still wipes settled/reserved. A refresh of the same cap is a second wallet.**

Not the K6 residual. Same breaker. The fold still replaces the rail dict:

```python
if e == "BUDGET_SET":
    s[p["rail"]] = {"cap": p["cap_usd"], ..., "reserved": {}, "settled": 0.0, ...}
```

Measured HERE (`SPEND-BUDGET-RESET-STILL-WIPES`): spend `$0.90`, `set_budget` same `$1`, spend `$0.90` again — **ALLOWED**; projected settled `$0.90`; true spend `$1.80`.

```
PYTHONPATH=cosmos python3 -m pytest -v \
  tests/reattack_guards.py::test_repro_spend_budget_reset_wipes_settled
# PASSED HERE
```

---

## 4. What HOLDS (do not re-open)

These new probes **HELD**. The named stage-7 closes that touch this cluster are still closed.

| probe | measured HERE |
|---|---|
| `CLOSED-K6-RID-UNIQUE` | `rids=['r-40f971dfdd68', 'r-bababc2dc858']` — distinct at a frozen clock |
| `CLOSED-SEQUENTIAL-CAP` | first `$0.70` ran; second **DENIED**; call did not run |
| `CLOSED-K3-BACKUP-TRAVERSAL` | `REHEARSAL_FAILED`, escape file **not** created |

Expired-budget deny (`test_concurrency` B7) and sequential over-cap deny (`test_spend_context`) also held. Do not file those again.

K4 `py:` confinement, K5 `done()` claimant, K1 keyed Kernel replay, K2 `role()` jail, and H2 freshness were not re-attacked here. They are not this cluster's residuals.

---

## 5. What the builder suite does not prove

| claimed | what actually ran |
|---|---|
| K6 "two concurrent callers cannot both slip past the cap" | two **sequential** `guarded_call`s at one frozen clock; asserts distinct rids |
| "over-cap call DENIED" | one thread, quiet gate, second call after the first has settled |
| B7 "expired budget DENIED" | one thread, clock rewritten, no overlap, no `set_budget` rewrite |
| "RESTORE REHEARSAL" / K3 | sequential `..` key; does not re-open; not a spend finding |

---

## 6. How to re-run

```
export PYTHONPATH=cosmos   # from repo root
python3 tests/reattack_guards.py
python3 -m pytest -v tests/reattack_guards.py
```

`test_repro_*` passing means the hole is still there. If a builder closes RG-B1, those three repros should **fail** — that is the signal.

Transcript of this critic run: cluster suites + harness + pytest, 2026-08-23, Python 3.12.3, Linux.

---

## Bottom line

Against `483e0fe`, the **named** K6 rid collision is closed and sequential deny still holds. The property the K6 comment claimed — **the cap is exclusive under overlap** — is open. `expect_head_seq=self.ledger.head_seq()` binds the head at append time, so a stale projection plus a moved head is a successful reserve. Measured: **$1.40 spent on a $1 cap**, in-process and across two processes. `BUDGET_SET` still zeroes settled. The other five listed residuals do not touch this cluster and were not scored.
