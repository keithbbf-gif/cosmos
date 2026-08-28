# ATTACK — guards cluster (scar-derived)

**Critic, not builder.** Subject: `f5/cosmos-core-v1` @ `e9e23ef`.  
**Target:** `cosmos_spend`, `cosmos_validate`, `cosmos_context`, `cosmos_platform`, `cosmos_backup`, `cosmos_health`.  
**Contracts:** `docs/FINAL_ARCHITECTURE.md` (ratified), Decision 8 / 10 / 11, H1–H5 / H9, harvest `docs/REVIEW_F5_CORE_GROK.md` on `origin/review/f5-core-grok` (not present on this branch; 7 BLOCKER + 10 MAJOR + 7 MINOR ≈ the ~19 known gaps).  
**Method:** `PYTHONPATH=cosmos` pytest in this Linux container; then new attacks in `tests/attack_guards.py`. Docstrings are claims. Behavior is evidence.  
**Scope kept:** `cosmos/` and existing `tests/test_*.py` were not modified.

A finding without a repro that runs is an opinion. Every BLOCKER/MAJOR below names the attack id and the command that produced BROKEN.

```
PYTHONPATH=cosmos python3 tests/attack_guards.py
# measured HERE: 33 BROKEN / 1 HELD / 0 ERROR of 34
```

---

## 1. What ran HERE vs NATIVE-DEMO-REQUIRED

`PYTHONPATH` must include `cosmos/` or pytest collection dies (`No module named 'cosmos_*'`). With `PYTHONPATH=/workspace/cosmos`:

| suite | touches | HERE (this container) | NATIVE-DEMO-REQUIRED? |
|---|---|---|---|
| `tests/test_spend_context.py` | spend, context | **PASS** 15/15 (pytest + script rc=0) | no |
| `tests/test_concurrency.py` | spend B7 | **PASS** 17/17 | no |
| `tests/test_migrate_health.py` | health | **PASS** 8/8 — synthetic ingest (`V:\Ai\BTS_MESH\TOOLS_REGISTRY.json` absent) | native measurement of 143-tool registry **skipped**, not marked |
| `tests/test_v1.py` | backup | **PASS** 18/18 | no |
| `tests/test_node_rails.py` | spend gate on rails | **PASS** 12/12 — fake incumbents; `0/4` importable | yes — "real dispatch to a live model is NATIVE-DEMO-REQUIRED" |
| `tests/test_features.py` | platform, validate | **FAIL** `FileNotFoundError: 'py'` at first `run(["py","-3.14",...])` | **not marked**. The UTF-8 / tree-kill checks never ran HERE |
| `tests/test_wave3.py` | health/spend HTTP + runner→platform | **FAIL** same `py` launcher inside `Runner.run_one` | **not marked** |
| `tests/attack_guards.py` | all six | harness **PASS** (did not crash); **33 BROKEN** | MAX_PATH / Job Objects remain native-only |

Bare `pytest tests/` without `PYTHONPATH` still cannot collect (same environment claim the 2651e20 review named).

`test_cosmos_paths.py` marks `MAX_PATH native demo` as `SKIPPED off-Windows - NATIVE-DEMO-REQUIRED` and records it **OK**. That skip is not a guards-suite file, but `cosmos_backup` / `v_path_exists` still walk without `extended()` — HERE cannot produce WinError 3. Those two are called out as NATIVE-DEMO-REQUIRED, not as Linux-measured MAX_PATH breaks.

**Honest HELD (do not re-open):**

- Sequential over-cap deny-before-call (`test_spend_context`) — holds.
- Expired **budget** deny (`test_concurrency` B7) — holds. The harvest's measured "expired credit ALLOWED" is closed for that one path.
- Forced `close(force=True)` writes `OPEN_CONTEXT`; next `boot_inherit` sees it — holds on the happy path.
- Backup hash mismatch on a tampered dest file → `REHEARSAL_FAILED` — holds.
- Health planted-failure row is RED; SHARED-CAUSE on all-red-one-reason — holds.
- Unicode backup filenames survive copy+hash HERE (`BKP-UNICODE-FILENAME` HELD).

The suites that pass do so because they never instantiate the failure modes below.

---

## 2. Harvest verification (guards-touching gaps)

Harvest source: `origin/review/f5-core-grok:docs/REVIEW_F5_CORE_GROK.md` (B1–B7, M1–M10, m1–m7). Items that do not touch this cluster (B1 ledger tear, B2 claim race, B3 ingress, B6 forged leases, M1 TAKEOVER, M2 install record, M3–M6/M8–M10, m1/m3–m7) are out of scope except where a guard is the claimed fix.

| harvest | claimed closed by builder? | actually closed? | evidence |
|---|---|---|---|
| **B4** seven primitives are kernel interfaces; workers cannot import around them | partial — Kernel now constructs `SpendGate`, `ReturnValidator`, `Session` | **OPEN** | `SPEND-IMPORT-AROUND-KERNEL`: a rogue `SpendGate(k.ledger)` wrote `BUDGET_SET`+`SPEND_SETTLED` on the authority ledger. `PlatformAdapter` is still not composed. No capability boundary. |
| **B5** no context manifest / `OPEN_CONTEXT` | yes — `Session` + `test_spend_context` + kernel `open_session` | **OPEN** (happy-path only) | `CTX-CRASH-FORGETS`: die without `close()` → `boot_inherit` is `{facts:{}, incidents:[], last_handoff:None}`. Facts and the open watcher are in the ledger as events and are still invisible. H1 is not a mechanism. |
| **B7** spend ignores expiry; not composed; `RESERVATION_EXPIRED`/`DOUBLE_SETTLE` never raised; audit ignores reserved | yes — expiry deny + Kernel.spend + B7 notes in `_state` | **PARTIAL** | Expired **budget** deny holds. `RESERVATION_EXPIRED` still never raised (`SPEND-RESERVATION-EXPIRED-NOT-RAISED`: expire-during-call still `SPEND_SETTLED`). Audit still does not sweep expired reservations (`SPEND-AUDIT-SKIPS-EXPIRED-RESERVE`). Cap is not exclusive under overlap. |
| **M7** backup is a library function, not a scheduled job; `rglob` without `extended()` | no (test_v1 only proves copy+hash) | **OPEN** | `BKP-NOT-A-JOB`, `BKP-WALK-NO-EXTENDED`, plus stamp collision / missing=empty / manifest overwrite. |
| **m2** reservation id `r%d % int(clock*1000)` | no | **OPEN** | `SPEND-RID-COLLISION`: two in-flight reserves at frozen clock 1000.0 both used `r1000000`. |

Builder comments that say `CRITIC B7 FIX` / `B5 composed` describe the sequential tests. They do not describe the attacks.

---

## 3. Ranked findings

### BLOCKER

**G-B1 — The spend cap is not a breaker. Overlap, a budget rewrite, or a negative estimate all spend past it.**  
H3 (expiring/overspend credit), Decision 1, harvest B7.

`guarded_call` projects, then decides, then `ledger.append`s the reserve. The OS lock serializes the append, not the decision. `BUDGET_SET` fold **replaces** the rail dict (`reserved={}, settled=0`). `worst_case_usd` is not validated.

Measured HERE:

| attack | result |
|---|---|
| `SPEND-RACE-OVERSPEND` | two threads, 50ms after `_state()`: both spent $0.70, **total $1.40 on a $1 cap**, `errors=[]` |
| `SPEND-BUDGET-RESET-WIPES-SETTLED` | spend $0.90, `set_budget` same cap, spend $0.90 again — **ALLOWED**; projected settled=$0.90 (true spend $1.80) |
| `SPEND-NEGATIVE-WORST-CASE` | hanging reserve of **-$10** then `guarded_call(..., 5.00)` on a $1 cap — **ALLOWED**, call ran |

Repro:

```
PYTHONPATH=cosmos python3 -c "
from tests.attack_guards import _spend_race, _spend_reset, _spend_neg, RESULTS
_spend_race(); _spend_reset(); _spend_neg()
print(*RESULTS, sep='\n')
"
```

Or: `PYTHONPATH=cosmos python3 tests/attack_guards.py` and read the three `SPEND-*` BROKEN lines.

The existing B7 test advances a fake clock on a **quiet** gate. It never overlaps two callers and never rewrites the budget.

---

**G-B2 — A session that dies is silent forgetting. H1 is still discipline.**  
H1, Decision 10, harvest B5.

`Session` keeps `_facts` / `_watchers` in process memory. `boot_inherit` only folds `SESSION_CLOSED`, `OPEN_CONTEXT`, and `WATCHER_RESOLVED`. An unclosed session has all three of those absent.

Measured HERE (`CTX-CRASH-FORGETS`):

```
boot_inherit after unclosed session={'facts': {}, 'incidents': [], 'last_handoff': None}
ledger events=['SESSION_OPENED', 'FACT_RECORDED', 'WATCHER_OPENED']
```

The next boot cannot detect the open watcher or the recorded fact. `OPEN_CONTEXT` is emitted only if someone calls `close(force=True)`. A crash is the case Decision 10 exists for.

Related, same root (MAJOR if you split them): `CTX-WATCHER-AFTER-CLOSE` ledgers `WATCHER_OPENED` **after** `SESSION_CLOSED`; `CTX-RESOLVE-DROPS-SIBLING` lets resolving `w-a` delete an incident that still named `w-b`; `CTX-MANIFEST-NO-LEASES` manifest keys are `{facts, handoff_to, sid, unresolved_watchers}` — no active leases, no evidence pointers.

Repro: `PYTHONPATH=cosmos python3 tests/attack_guards.py` → `CTX-CRASH-FORGETS`.

---

**G-B3 — Timeout does not kill the tree. Grandchildren survive both process doors.**  
Module contract (`cosmos_platform.py`): "timeout kills the TREE". H9 Job Objects. Architecture: contained workers, including DOM descendants.

Measured HERE:

| attack | result |
|---|---|
| `PLT-TREE-KILL-ORPHAN` | `run_tree_killed` `timed_out=True`, `kill_result='SIGKILL (non-Windows; process group not chased) \| KILL_INCOMPLETE: child did not reap in 10s'`, **grandchild_alive=True**, heartbeat still advancing |
| `PLT-RUN-TIMEOUT-NOT-TREE` | `run()` `timed_out=True`, kill_result admits "descendants not guaranteed", **grandchild_alive=True** |

The adapter records the lie and returns success-shaped dicts. `test_features` never reached this check HERE because it dies on `py` first; even natively it only asserts `timed_out and kill_result is not None` — a string is not a dead tree.

Repro: `PYTHONPATH=cosmos python3 tests/attack_guards.py` → `PLT-TREE-KILL-ORPHAN`, `PLT-RUN-TIMEOUT-NOT-TREE`.

---

**G-B4 — Guards are importable libraries. Decision 11 is not enforced.**  
H4, Decision 11, harvest B4.

Kernel composition (`self.spend = SpendGate(...)`) is a constructor line. It is not a capability.

Measured HERE (`SPEND-IMPORT-AROUND-KERNEL`):

```
rogue SpendGate wrote [..., 'BUDGET_SET', 'SPEND_RESERVED', 'SPEND_SETTLED']
onto the kernel authority ledger with no capability check
```

The same pattern works for `ReturnValidator`, `Backup`, `Session`, `run()` / `run_tree_killed`. A worker that can `import cosmos_spend` is the spend gate.

Repro: `PYTHONPATH=cosmos python3 tests/attack_guards.py` → `SPEND-IMPORT-AROUND-KERNEL`.

---

### MAJOR

**G-M1 — Reservation identity collides; declared spend kinds are dead; audit lies until the next call.**  
Harvest m2 + B7 remainder.

- `SPEND-RID-COLLISION`: frozen clock → `reserved_rids=['r1000000','r1000000']`. Projection key overwrite. Two settles of one rid cannot raise `DOUBLE_SETTLE` (the kind is never constructed).
- `SPEND-RESERVATION-EXPIRED-NOT-RAISED`: expire during the callback → events `BUDGET_SET, SPEND_RESERVED, SPEND_SETTLED`, `raised=[]`. The reservation expired and the spend still settled.
- `SPEND-AUDIT-SKIPS-EXPIRED-RESERVE`: after ttl, `audit()` still reports `reserved=0.8 headroom=0.2`. Sweep lives only inside `guarded_call`.

Repro: same harness, those three ids.

**G-M2 — UNPRICED and `worst_case=0` make the cap a suggestion.**

- `SPEND-UNPRICED-INFINITE`: 20 calls with `worst_case=$0.40` on a $0.50 cap, each returning no `usd` → `unpriced_calls=20 settled=0.0`. The estimate reserved, the settle consumed nothing, the next estimate saw a clean cap.
- `SPEND-ZERO-WORST-CASE`: `worst_case=0` then settle **$99** on a **$0.01** cap — ALLOWED. Reserve is the gate; settle is a receipt. The module docstring says that like it is a virtue.

Repro: harness ids above.

**G-M3 — Return validation is optional and forges on empty inputs.**  
H2 / H4 / scar R4 (fabricated citation).

- `VAL-EMPTY-CLAIMS-ACCEPTED`: `accept("r-empty", [])` → `RETURN_VALIDATED`. A fabricating return that names no validators is a validated return.
- `VAL-EMPTY-QUOTE-MATCHES`: `quote=""` is "verbatim in source".
- `VAL-MISSING-FILE-UNTYPED`: `read_verified` on a missing path → `FileNotFoundError`, not `ValidateError`.
- `VAL-PATH-EXISTS-DIRECTORY`: a directory is "on disk".

Repro: harness ids above.

**G-M4 — Backup is still not a backup in the ratified sense, and two runs in one second mix trees.**  
Decision 8, harvest M7, H2 missing-vs-empty.

- `BKP-NOT-A-JOB`: `Backup.run` / `rehearse_restore` never admit a scheduler job. `test_v1` calls the library.
- `BKP-STAMP-COLLISION`: injected clock, two `run()`s → **same dest**; dest holds `a.txt` from src1 **and** `b.txt` from src2. Exactly-once under overlap: failed.
- `BKP-MISSING-EQ-EMPTY`: missing source and empty source both `EMPTY_SCOPE`.
- `BKP-MANIFEST-OVERWRITE`: source file `_MANIFEST.sha256.json` is hashed into the manifest then overwritten by the generated JSON; `BACKUP_VERIFIED` is ledgered; rehearsal then fails.
- `BKP-REHEARSE-MISSING-FILE-UNTYPED`: delete a dest file after a good run → `FileNotFoundError`, not `REHEARSAL_FAILED`.
- `BKP-WALK-NO-EXTENDED`: `Path.rglob` — C-60; **NATIVE-DEMO-REQUIRED** to measure WinError 3.

Repro: harness ids above.

**G-M5 — The board cannot see the guards and cannot go RED on leases.**  
C-46 (a checker that cannot go red), harvest B4 composition claim.

- `HLTH-LEASE-ROW-ALWAYS-GREEN`: acquire tree as `attacker` token=1; leases row `{ok: True, detail: 'tree held by attacker (token 1)'}`; verdict GREEN.
- `HLTH-BOARD-SKIPS-GUARDS`: rows are `ledger chain, resolver/sentinel, queue, mail, leases`. Missing: spend, backup, validate, context, platform. Verdict GREEN.
- `HLTH-EMPTY-LEDGER-GREEN`: GREEN with zero `BUDGET_*`/`SPEND_*`/`BACKUP_*`/`RESTORE_*` events.

`test_migrate_health` only proves the planted row is red and a raising row is red. It never asks whether absence of a rehearsal or a held tree is visible.

Repro: harness ids above.

**G-M6 — The platform adapter does not own process start. Absence is untyped; the Windows launcher is hard-coded above it.**

- `PLT-MISSING-BINARY-UNTYPED`: `run(["cosmos-no-such-binary-9f3a"])` → `FileNotFoundError`.
- `PLT-LAUNCHER-NOT-ADAPTED`: `run(["py","-3.14","-c","print(1)"])` → `FileNotFoundError`. HERE has `python3`, not `py`.
- This is why `tests/test_features.py` and `tests/test_wave3.py` **FAIL HERE** (not skipped, not NATIVE-DEMO-REQUIRED). `cosmos_runner.py` builds `argv = ["py", "-3.14", ...]`. The adapter is the door; the runner walks around the OS.

Repro:

```
PYTHONPATH=cosmos python3 -c "
from cosmos_platform import run
run(['py','-3.14','-c','print(1)'])
"
# FileNotFoundError: [Errno 2] No such file or directory: 'py'
```

---

### MINOR

**G-m1 — `v_path_exists` / `write_declared` skip the I/O contract they sit next to.**  
`VAL-PATH-EXISTS-NO-EXTENDED` (no `extended()` — MAX_PATH is NATIVE-DEMO-REQUIRED). `VAL-WRITE-NO-VERIFY-AFTER` hashes the argument, never the bytes on disk (scar R1 is declared-vs-consumed on **read**; write is one-sided).

**G-m2 — Double `SESSION_OPENED` for one sid is allowed** (`CTX-DOUBLE-OPEN-SAME-SID`). Carry-over then has two lives, one close.

**G-m3 — Unicode filenames on backup HOLD HERE.** Not a finding. Listed so nobody files it.

---

## 4. Contract check (module vs ratified text)

| module | ratified job | what shipped | verdict |
|---|---|---|---|
| `cosmos_spend` | breaker **in the caller**; reserve worst-case → deny → call → settle measured; both directions; Core-owned | sequential deny works; expiry of **budget** works; overlap/reset/negative/unpriced/zero/`rid` do not; kinds `RESERVATION_EXPIRED`/`DOUBLE_SETTLE` are docstring fiction | **fails H3 as a control** |
| `cosmos_validate` | gate wired into acceptance; fabricated citation cannot land; declared-vs-consumed | optional (`accept([])`); empty quote; untyped missing file; not invoked by Kernel on any return path | **bolted-on library (H4)** |
| `cosmos_context` | close **must** record facts, **active leases**, open watchers, evidence pointers, handoff; else `OPEN_CONTEXT` | in-memory session; crash is silent; no leases in manifest; `boot_inherit` is a partial fold | **fails H1 / Decision 10** |
| `cosmos_platform` | one layer owns encoding, quoting, path length, line endings, **tree kill**; no tool touches shell | LF/CRLF helpers work; `extended()` on write/makedirs; `run`/`run_tree_killed` leak `FileNotFoundError`; tree kill is a comment on Linux; runner still says `py` | **fails own RULES + H9** |
| `cosmos_backup` | policy/verification/evidence in Core; execution as **scheduled jobs**; `rehearse-restore` first-class job; hash verify | library copy+hash; real tamper detect; not a job; stamp collision; missing=empty; C-60 walk | **M7 still open** |
| `cosmos_health` | one run, every subsystem proves itself; planted red; cannot be stuck green | planted red works; lease row cannot go red; spend/backup/validate/context/platform never asked | **GREEN is not a measurement of the guards** |

---

## 5. What the existing suites do not prove

| claimed | what actually ran |
|---|---|
| B7 "expired budget DENIED" | one thread, clock rewritten, no overlap, no `set_budget` rewrite, no negative estimate |
| B5 "close over open watcher REFUSES" | in-process `Session`; no crash, no replay, no lease field |
| "RESTORE REHEARSAL" | `Backup.rehearse_restore` in the test process, not a scheduled job |
| "board runs GREEN on a healthy kernel" | healthy = planted row red + no other rows unhappy; spend/backup never exist |
| platform UTF-8 both ends / tree-kill reported | HERE: **never executed** (`py` missing). Native: `kill_result is not None` is enough |
| "kernel COMPOSES spend/validator" | attributes are not None; no capability test |

---

## 6. Repro index

```
export PYTHONPATH=cosmos   # from repo root
python3 tests/attack_guards.py
python3 -m pytest tests/test_spend_context.py tests/test_concurrency.py \
  tests/test_migrate_health.py tests/test_v1.py tests/test_node_rails.py \
  tests/test_features.py tests/test_wave3.py tests/attack_guards.py -v
```

Attack ids are stable labels in `tests/attack_guards.py` (`@attack("...")`). The harness returns 0 if it ran; BROKEN is the finding, not a crash. pytest `test_attack_guards_harness_runs` only asserts the harness executed.

Raw HERE transcript: this critic run produced the 33/1/0 tally quoted above (2026-08-23, Python 3.12.3, Linux).
