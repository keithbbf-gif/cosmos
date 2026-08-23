# VERIFY STAGE-7 FIXES — GROK

**Critic, not builder.**  
**Subject:** `f5/cosmos-core-v1` @ `ee3fed8` (this branch `verify/stage7` started there).  
**Date:** 2026-08-23.  
**Register:** there is no standalone `docs/STAGE7_DEFECT_REGISTER.md`. The six CRITICALs **K1–K6 + H2** are the Stage-7 set named in the builder's own comments and suite:

| id | critic id | claimed defect | claimed fix site |
|---|---|---|---|
| **K1** | OA C-01 | Kernel composed `Arbiter` **without** the install key; leases unsigned in production; a well-formed forged GRANT loaded as a live lease | `cosmos_kernel.py` passes `key=` |
| **K2** | OA H-02 | `role()` / `protected_write` accepted absolute parts and `..`; escaped the COSMOS root | `cosmos_paths.role` rejects + `relative_to` confine |
| **K3** | OA C-02 / GEM IND-004 | `rehearse_restore` used manifest keys verbatim; `..` / absolute keys wrote arbitrary files | `cosmos_backup.rehearse_restore` rejects + confine |
| **K4** | GEM IND-002 | `py:<path>` ran **any** host script (path-traversal RCE) | `cosmos_runner` confines to `tools_root` |
| **K5** | OA C-03 | `done()` required only `RUNNING`; any worker could complete another worker's job; second completion last-wins | `cosmos_sched.done` claimant + terminal-state refuse |
| **K6** | OA C-04 | `rid = int(clock*1000)`; two reservations in the same ms collided and overwrote in the projection | `cosmos_spend` uuid rid + `expect_head_seq` |
| **H2** | OA H-05 | `route()` filtered only on `ok`; a once-live link stayed dispatch-eligible forever | `cosmos_registry.route` freshness window |

Builder "proof": `tests/test_stage7_fixes.py` (13 OK) and `docs/V1_SUITE_RESULTS.md`. **That suite is not this evidence.** It asserts the fix. This document asserts the **original attack**, then records whether that attack still lands.

**Method:** `tests/verify_stage7_fixes_grok.py` — each `original` probe **PASSES (OPEN) if and only if the defect still lands**. A `closed` claim is evidence only when that same probe now **FAILS (BLOCKED)**. Bypass probes are separate and do not re-open an id unless they produce the **same harm**. `cosmos/` was not modified.

```
PYTHONPATH=cosmos python3 tests/verify_stage7_fixes_grok.py
# measured HERE 2026-08-23, Linux container, Python 3.12.3
# ORIGINALS OPEN 0/13   BYPASSES LANDED 6/17
```

---

## Scoreboard

| id | original attack (would PASS if still open) | measured original | verdict |
|---|---|---|---|
| **K1** | forged unsigned GRANT loads as live lease on Kernel / keyed-Arbiter replay | **BLOCKED** `LockError[FORGED_EVENT]` both paths | **CLOSED** at Kernel composition. Residual API: unkeyed `Arbiter()` still loads the lie |
| **K2** | `role()` / `protected_write` traversal escapes the root | **BLOCKED** `IDENTITY_MISMATCH` on `..`, `/tmp/...`, `C:\...`, `..\..\pwned.txt` | **CLOSED**. Combined-part, symlink-escape, fullwidth-dot also held |
| **K3** | manifest `..\..\k3_escape.txt` restores outside scratch | **BLOCKED** `REHEARSAL_FAILED`, escape file **not** created | **CLOSED**. Absolute key, `ok/../../`, symlink-src also held |
| **K4** | `py:` script outside `tools_root` executes / is accepted for exec | **BLOCKED** `traversal_refused=True`, marker file absent | **CLOSED for `py:` paths. BYPASSABLE** — `argv:` executed `CLEAN` and wrote the marker; bare commands skip confinement and go to `py -c` |
| **K5** | worker B `done()`s A's job; second `done()` last-wins | **BLOCKED** `BAD_STATE` both | **CLOSED for `done()`**. Residual: worker id is a label (spoof as `"A"` works); `JOB_DONE` appended around `done()` is projected |
| **K6** | two reservations at frozen clock share one rid | **BLOCKED** distinct `r-<uuid>` sequential **and** in-flight | **CLOSED** for rid collision. Related residual (not K6): overlap still spent **$1.40 on a $1 cap** |
| **H2** | once-live link still routed after 2 h | **BLOCKED** `stale=0` (default window also 0); `max_age_s=None` still 1 | **CLOSED**. `Dispatcher.dispatch` → `NO_LIVE_LINK`; never-probed not routed |

**A 'closed' claim without a repro that now fails is not evidence.** Every original row above is a repro that **failed to land** against `ee3fed8`.

---

## What ran HERE

```
PYTHONPATH=/workspace/cosmos python3 tests/verify_stage7_fixes_grok.py
scratch=/tmp/cosmos_s7verify_odr74ssj
```

Builder suite (not the evidence; recorded so nobody claims it was skipped):

```
PYTHONPATH=/workspace/cosmos python3 tests/test_stage7_fixes.py
SELFTEST PASS - 13 checks
```

Bare `pytest tests/` without `PYTHONPATH=cosmos` still cannot collect (`No module named 'cosmos_*'`). Same environment claim as the earlier f5 review. All numbers below are from the adversarial script under `PYTHONPATH=cosmos`.

---

## K1 — OA C-01 — signed leases at composition

**Original (OPEN if):** plant an unsigned well-formed GRANT after a real signed grant; reconstruct via `Kernel(..., read_only=True)` (the production composition) **or** `Arbiter(path, key=install_key)`; the attacker lease is live.

**Measured:**

```
[K1 original] forged unsigned GRANT loads as live lease via Kernel replay
    BLOCKED  holder=None err=LockError[FORGED_EVENT] line 2: event is unsigned or mis-signed
[K1 original] forged GRANT loads via keyed Arbiter() replay (builder vector)
    BLOCKED  holder=None err=LockError[FORGED_EVENT] line 2
```

`Kernel.arbiter._key` is set (32 bytes). The composition hole named in the comment is closed: replay through the live kernel refuses the lie.

**Bypass:**

```
[K1 bypass] unkeyed Arbiter() still loads the forged GRANT
    LANDED  holder='ATTACKER'
[K1 bypass] live Kernel.arbiter has no key
    held    Kernel.arbiter._key set=True len=32
```

`Arbiter.__init__(..., key=None)` is still a public constructor. An unkeyed replay **loads ATTACKER as a live lease**. Production Kernel no longer takes that path. Any caller that constructs `Arbiter(path)` without the install key (tests, a future CLI, an importer) re-opens the B6 forge. That is a residual API, not a Kernel-composition miss.

**Verdict: CLOSED** (original vector). Do not treat "the suite reopens Arbiter with a key" as the only proof — Kernel replay was measured here and also refuses.

---

## K2 — OA H-02 — role / protected_write traversal

**Original (OPEN if):** `role("state", "..", "..", "escape.txt")`, an absolute POSIX part, a drive-letter part, or `protected_write("tree", "..\\..\\pwned.txt", ...)` resolves or writes outside the root.

**Measured:** all four **BLOCKED** `CosmosPathError[IDENTITY_MISMATCH]`. No path escaped; no write landed.

**Bypass:**

| probe | result |
|---|---|
| single-part `ok/../../escape.txt` | **held** — `..` in a split component refused |
| symlink `state/outlink` → scratch outside the tree, then `role("state", "outlink", "x.txt")` | **held** — `resolve().relative_to` refuse |
| fullwidth dots `U+FF0E U+FF0E` | **held** — stayed under root (literal dirname `．．`, not `..`) |

Callers who skip `role()` and join on `paths.root` themselves are outside this id (discipline, not the role API).

**Verdict: CLOSED.** No measured escape of `role()` / `protected_write`.

---

## K3 — OA C-02 / GEM IND-004 — backup manifest traversal

**Original (OPEN if):** `_MANIFEST.sha256.json` key `..\..\k3_escape.txt` causes `rehearse_restore` to succeed **or** to create the escape file outside scratch.

**Measured:**

```
[K3 original] manifest key '..\..\k3_escape.txt' restores outside scratch
    BLOCKED  refused=True kind=REHEARSAL_FAILED escape_landed=False scratch_exists=True
```

Refusal without a write is the closed form. A raise after the write would still be OPEN.

**Bypass:**

| probe | result |
|---|---|
| absolute key = a path under the temp root | **held** `REHEARSAL_FAILED`, file not created |
| `ok/../../k3_rel.txt` | **held** `REHEARSAL_FAILED`, file not created |
| symlink `innocent.txt` → secret outside dest (src confinement) | **held** `manifest key 'innocent.txt' escapes containment` |

**Verdict: CLOSED.** The named restore-outside-scratch harm did not land on the original key or the three bypass keys.

---

## K4 — GEM IND-002 — runner `py:` confinement

**Original (OPEN if):** submit `py:<absolute-path-outside-tools_root>`; `run_one()` executes it or accepts it for execution (no `traversal_refused`). Marker file written only if the child actually ran.

**Measured:**

```
[K4 original] py: script OUTSIDE tools_root is executed (or accepted for exec)
    BLOCKED  result={..., 'outcome': 'BROKE', 'traversal_refused': True}
             marker=False refused=True
```

`py:` + `tools_root/../../evil.py` and `py:` + symlink-inside-tools-root → outside script: both **held** (`traversal_refused=True`). `Path.resolve().relative_to` follows the symlink; confinement is on the resolved path.

**Bypass — same submit surface, other command forms (LANDED):**

```
[K4 bypass] argv: form runs arbitrary host argv (skips tools_root)
    LANDED  outcome=CLEAN rc=0 elapsed_s=0.07 marker=True
            argv = [sys.executable, "-c", "Path(marker).write_text('argv-pwned')"]
[K4 bypass] bare command is exec'd as py -c (no tools_root check)
    LANDED  dashc_log=True
            argv ['py', '-3.14', '-c', "print('dashc')"]
            child then FileNotFoundError: 'py'  (this host has no `py` launcher)
```

`cosmos_runner.py` confines **only** the `py:` prefix. Everything else is:

```python
argv = ["py", "-3.14", "-c", cmd] if not cmd.startswith("argv:") else json.loads(cmd[5:])
```

`POST /api/v1/jobs` (`cosmos_service.py`) submits `d["command"]` with no form check. The service itself queues crucible work as `argv:` + `py -3.14 -c ...`.

The **path-traversal RCE via `py:`** is closed. The **property "a submitter cannot run arbitrary host code"** is not. On this host the `argv:` child ran with `sys.executable` and wrote the marker (`CLEAN`). That is measured RCE, not a reading of the source.

**Verdict: CLOSED for the named `py:` vector. BYPASSABLE** — do not ship a "RCE closed" claim from the builder suite alone.

---

## K5 — OA C-03 — `done()` claimant + no last-wins

**Original (OPEN if):** worker B completes A's `RUNNING` job; or a second `done()` after `CLEAN` changes the outcome to `FINDINGS`.

**Measured:**

```
[K5 original] non-claimant worker B completes A's RUNNING job
    BLOCKED  completed=False state=RUNNING by=A
             err=SchedError[BAD_STATE] ... claimed by A, not B
[K5 original] second done() after a terminal state is accepted (last-wins)
    BLOCKED  double=False state=CLEAN
             err=SchedError[BAD_STATE] ... is CLEAN, not RUNNING
```

**Bypass (LANDED):**

```
[K5 bypass] attacker constructs Scheduler(worker='A') and completes
    LANDED  spoofed=True state=CLEAN by=A
[K5 bypass] worker B appends JOB_DONE via the ledger (skips done())
    LANDED  state=CLEAN by=B
```

The guard is `st[job_id]["by"] != self.worker` where `worker` is a constructor string. Anyone who can open the sched ledger (install key is tree-global) can instantiate `Scheduler(..., worker="A")` or `ledger.append("JOB_DONE", ...)`. `_state()` folds any `JOB_DONE` for a known id. That is the H4 / B4 "import around the kernel" gap, not a miss of the `done()` comparisons.

**Verdict: CLOSED for `done()`.** Claimant-as-credential and "the projection is the gate" were never this id's claim; they remain open.

---

## K6 — OA C-04 — spend rid uniqueness

**Original (OPEN if):** two `guarded_call`s at a frozen clock produce the same `rid` (harvest m2 / `attack_guards.SPEND-RID-COLLISION` shape: `r%d % int(clock*1000)`).

**Measured:**

```
[K6 original] two sequential reservations at the same clock ms share a rid
    BLOCKED  rids=['r-909ec7876e09', 'r-ad5415d25d94']
[K6 original] two in-flight reservations at frozen clock collide on one rid
    BLOCKED  reserved_rids=['r-b1e40313796c', 'r-f62a5c0fd732'] errors=[]
```

Both in-flight reserves landed (two distinct uuid rids). The old collision key is gone. The harvest m2 repro that required `len(rids)>=2 and len(set(rids))==1` now fails.

**Related residual (not K6 — do not re-open the id):**

```
[K6 bypass] two overlapping $0.70 calls spend past a $1 cap
    LANDED  spent=[0.7, 0.7] total=1.4 errors=[]
```

`expect_head_seq` did **not** stop both reserves: both callbacks ran. That is the older G-B1 / harvest-B7 overlap (decision then append). Unique rids make the overwrite-in-`reserved` dict impossible; they do not make the cap exclusive. Logged here so a "K6 closed" sentence is not read as "the breaker holds under overlap."

**Verdict: CLOSED** for rid collision. Cap-exclusivity is a different defect and is still OPEN.

---

## H2 — OA H-05 — route freshness

**Original (OPEN if):** probe live at t=1000, advance 7200 s, `route(..., max_age_s=3600)` still returns the link.

**Measured:**

```
[H2 original] once-live link still routed after 2h
    BLOCKED  fresh=1 stale=0 defaulted=0 opt_out=1
```

Default `max_age_s=3600` also dropped it. `max_age_s=None` still returns it (documented opt-out, not a production default).

**Bypass:**

```
[H2 bypass] Dispatcher.dispatch still uses a 2h-stale link
    held  RailError[NO_LIVE_LINK] no measured-live link a->b
[H2 bypass] never-probed link is routed as live
    held  routed=[]
```

`cosmos_rails.Dispatcher.dispatch` calls `registry.route(src, dst)` with the default window. The production caller honors freshness.

**Verdict: CLOSED.**

---

## Residuals that are not Stage-7 reopenings

These landed. They do not put K1–K6 / H2 back on the register as originally written. They **do** bound what "closed" means.

1. **Unkeyed `Arbiter()`** still treats a well-formed unsigned GRANT as a live lease. Kernel no longer constructs that. The constructor still does.
2. **`argv:` and bare `-c`** are unconstrained exec on the same job-submit surface that K4 confined for `py:` only. Measured: `argv:` wrote a file and returned `CLEAN`.
3. **Scheduler worker id is a label.** `done()` compares strings. The install key is not per-worker.
4. **`JOB_DONE` is a ledger event anyone with the key can append.** Projection is not `done()`.
5. **Spend cap is not exclusive under overlap** (`$1.40` on `$1`). Unique rids (K6) made this measurable instead of hidden by dict overwrite.

---

## How to re-run

```
PYTHONPATH=cosmos python3 tests/verify_stage7_fixes_grok.py
# original probe True  = OPEN (adversarial PASS)
# original probe False = BLOCKED (the only evidence a Stage-7 id is closed)
```

JSON dump of the row list: set `VERIFY_STAGE7_JSON` (default `/tmp/verify_stage7.json`).

---

## Bottom line

Against `ee3fed8`, every original Stage-7 CRITICAL repro **failed to land**. That is the evidence K1, K2, K3, K4(`py:`), K5(`done()`), K6(rid), and H2(freshness) are closed **as named**.

K4 is the id I will not rubber-stamp as "RCE closed": the builder confined one command form and left two that implement the same submit-to-exec harm. K6's rid collision is closed; the spend cap still is not a breaker under overlap. K1/K5 residuals are API/identity, not missed comparisons on the original path.
