# REATTACK — foundation cluster
**Critic, not builder.** Subject: `main` @ `483e0fe`
(`merge fixed f5 (stage-7 K1-K6+H2 closed, 341 checks)`).

**Cluster:** `cosmos_paths`, `cosmos_ledger`, `cosmos_lock`, `cosmos_mail`,
`cosmos_sched`, `cosmos_segments`, plus Kernel composition of those six.

**Method:** check out merged main, set `PYTHONPATH=cosmos`, run the cluster
suites, then land **new** repros. `test_repro_*` passing means the hole is
still present. A claim without a repro that ran is an opinion and is not
filed.

Prior attack (`attack/foundation` @ `e9e23ef`) is the harvest, not this
evidence. Stage-7 verification (`verify/stage7` @ `ee3fed8`) named the
residuals this pass re-tested **if they touch the cluster**.

---

## 1. Cluster suites on this tree

`PYTHONPATH=cosmos` · Linux · `483e0fe`

| Suite | Result |
|---|---|
| `tests/test_cosmos_paths.py` | PASS 16 (MAX_PATH SKIPPED NATIVE-DEMO-REQUIRED) |
| `tests/test_cosmos_lock.py` | PASS 18 |
| `tests/test_cosmos_mail.py` | PASS 12 |
| `tests/test_core.py` | PASS 19 (`POLL-FALLBACK` 0.751s counted OK) |
| `tests/test_segments.py` | PASS 21 |
| `tests/test_concurrency.py` | PASS 17 |
| `tests/test_kernel.py` | PASS 13 |
| `tests/test_stage7_fixes.py` | PASS 13 |

The builder suites are green. They do not exercise overlap across
**processes** on the lease file, do not authenticate segment anchors, and
do not treat `worker` as an adversary-controlled constructor argument.

Full transcript: captured in this run as
`PYTHONPATH=cosmos python3 tests/test_reattack_foundation.py` → **20/20**.
Race probes flake-checked 5× each (lock xproc, segmented writers).

---

## 2. Known-residual touch analysis

The re-attack brief named six residuals. Only the ones that **touch this
cluster** are findings. The others are located, not re-litigated.

| Residual | Touches foundation? | Site | This pass |
|---|---|---|---|
| Cross-process arbiter serialization | **YES** | `cosmos_lock._append` — open/append/fsync, no flock, no `expect_head_seq`. Kernel now signs (K1) and still does not serialize. | **OPEN** RF-LOCK-XPROC |
| Segment anchor authentication | **YES** | `cosmos_segments._rotate` writes `last_record_sha`; `verify_all` never reads it. Anchors have no `hmac`/`sig`. | **OPEN** RF-SEG-ANCHOR (+ RF-SEG-LOAD, RF-SEG-RACE) |
| Worker-id spoofing | **YES** | `Scheduler.worker` and `Mailbox.me` are constructor strings. K5 closed `done()` vs a *different* label; the label itself is unauthenticated. Path join on `worker_id` has no jail. | **OPEN** RF-SCHED-SPOOF, RF-SCHED-LEDGER, RF-MAIL-ABS, RF-MAIL-DOTDOT |
| `argv:` runner confinement bypass | **NO** | `cosmos_runner.py` (`json.loads(cmd[5:])`). Kernel does not compose a Runner. Scheduler stores the command as an opaque string. | Located, not a foundation finding |
| Spend over-cap under overlap | **NO** | `cosmos_spend.SpendGate`. Kernel composes it; the module is not in this cluster. | Located, not a foundation finding |
| Ingress `envelope_id` traversal | **NO** | `cosmos_ingress._verify_one`: `self.dir / (env["envelope_id"] + ".payload")`. Ingress is not composed by Kernel. `envelope_id` does not appear in lock/sched/segments. | Located, not a foundation finding |

Touch proof (not a finding): `test_note_argv_spend_ingress_do_not_live_in_cluster_modules`.

---

## 3. What stage-7 actually closed on this cluster

These **original** vectors no longer land. New closed-checks, not the
builder's own suite, measured it.

| ID | Original vector | Measured now |
|---|---|---|
| **K1** / F-LOCK-UNSIGNED | Forged unsigned GRANT on Kernel lease file loads as live | `LockError[FORGED_EVENT]` on keyed replay |
| **K2** / F-PATH-ESC | `role("queue", "..", ..)` / absolute part / `protected_write("..\\..")` | all `IDENTITY_MISMATCH` |
| **K5** / F-SCHED-DONE | Worker B calls `done()` on A's RUNNING job | `BAD_STATE` *claimed by A, not B* |

```
CLOSED K1: forged GRANT -> FORGED_EVENT
CLOSED K2 role .. -> IDENTITY_MISMATCH
CLOSED K2 role abs -> IDENTITY_MISMATCH
CLOSED K2 protected_write -> IDENTITY_MISMATCH
CLOSED K5: B done() of A's job -> [BAD_STATE] ... claimed by A, not B
```

K3/K4/K6/H2 are not this cluster. They were green in `test_stage7_fixes`
and are not re-opened here.

---

## 4. Ranked remaining findings

Every entry has a repro in `tests/test_reattack_foundation.py` that
**passed on this tree**.

### BLOCKER

#### RF-LOCK-XPROC — signed Kernel arbiters do not serialize
**Contract:** Decision 2 / H3 — one writer; the arbiter serializes acquire.
**What remains:** K1 added `key=` at composition. `_append` is still
check-then-append with no OS lock. Six processes construct `Kernel` (keyed
Arbiter), wait on a start gate, then `acquire("crown")`.

```
RF-LOCK-XPROC wins=6 tokens=['1', '1', '1', '1', '1', '1']
grants=6 holders=[('W5', 1), ('W3', 1), ('W1', 1), ('W0', 1), ('W4', 1), ('W2', 1)]
```

Six GRANTs, all token 1, six holders. Replay is last-writer-wins.
Flake-checked 5/5.

```bash
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_reattack_foundation.py::test_repro_signed_kernel_arbiters_do_not_serialize
```

#### RF-SEG-RACE — two SegmentedLedger processes tear history
**Contract:** Decision 3 — a corrupt / raced segment refuses; one writer.
**What remains:** each segment file uses `Ledger.append` (flock), but
rotation + in-memory `_active_count` / `_prior_count` are not a
cross-process protocol. Two processes, 12 appends each, `max_records=4`:

```
RF-SEG-RACE writers: W A ok=12 err= | W B ok=12 err=
RF-SEG-RACE verify_all BROKEN_CHAIN: seg-00001.anchor.json:
  seq accounting disagrees with the records (first/last/count)
```

Both writers believe they succeeded. The history does not verify.
Flake-checked 5/5.

```bash
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_reattack_foundation.py::test_repro_two_segmented_writers_break_history
```

#### RF-SEG-LOAD — `_load` appends onto a poisoned sealed segment
**Contract:** Decision 3 — loading is verifying.
**What remains:** `_load` sums `record_count` from anchors and opens the
live head. It does not verify sealed segment bytes. After flipping a
payload byte in `seg-00001.jsonl`, a new `SegmentedLedger` appends
`AFTER_POISON` at `global_seq=8`. `verify_all` later raises
`BROKEN_CHAIN` — the write already landed.

```
RF-SEG-LOAD append_after_poison global_seq=8 event=AFTER_POISON
RF-SEG-LOAD verify_all later BROKEN_CHAIN (append already landed)
```

```bash
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_reattack_foundation.py::test_repro_load_appends_onto_poisoned_sealed_segment
```

#### RF-LOCK-UNKEYED — `Arbiter()` without `key=` still loads ATTACKER
**Contract:** B6 / K1 — a well-formed lie is still a lie.
**What remains:** K1 closed the Kernel composition path. The constructor
still treats `key=None` as "do not verify". Unsigned GRANT
`holder=ATTACKER token=77` loads; `fenced_commit` returns `"PWN"`.

```
RF-LOCK-UNKEYED holder=ATTACKER token=77 key=None
```

```bash
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_reattack_foundation.py::test_repro_unkeyed_arbiter_still_loads_forged_grant
```

---

### MAJOR

#### RF-SEG-ANCHOR — `last_record_sha` is decorative; anchors unsigned
**Contract:** Decision 3 / harvest M9 — signed framed segments; the seam
hash is auditable.
**What remains:** `_rotate` writes `last_record_sha`. `verify_all` checks
`segment_sha256`, `prev_anchor_sha256`, and seq accounting. It never
reads `last_record_sha`. No `hmac` / `sig` field exists. Lying
`last_record_sha="ab"*32` on the last sealed anchor: `verify_all`
yields all 7 records.

```
RF-SEG-ANCHOR unsigned=True honest_last=0b68015f0637c56f
actual_line=0b68015f0637c56f lied=ab*32 verify_all=7
```

```bash
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_reattack_foundation.py::test_repro_anchor_last_record_sha_is_unauthenticated
```

#### RF-SCHED-SPOOF — worker id is a constructor label (K5 residual)
**Contract:** per-worker identity in every artifact; only the claimant
completes.
**What remains:** `done()` compares `st[job]['by'] != self.worker`.
`self.worker` is the string passed to `Scheduler(...)`. An attacker who
constructs `Scheduler(root, key, "honest")` completes the honest
worker's job. K5's foreign-label check still holds (see §3).

```
RF-SCHED-SPOOF spoofed_done st=CLEAN by=honest
```

```bash
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_reattack_foundation.py::test_repro_sched_worker_id_is_a_constructor_label
```

#### RF-SCHED-LEDGER — `JOB_DONE` append bypasses `done()`
**Contract:** H4 / B4 — workers cannot import around the kernel verbs.
**What remains:** projection fold accepts any `JOB_DONE` for a known
`job_id`. Worker B appends via `Ledger` with the install key.
State becomes `CLEAN by=B` without `done()`.

```
RF-SCHED-LEDGER after_direct_JOB_DONE st=CLEAN by=B
```

```bash
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_reattack_foundation.py::test_repro_job_done_append_bypasses_done_guard
```

#### RF-MAIL-ABS / RF-MAIL-DOTDOT — Kernel worker_id escapes the mail root
**Contract:** Decision 5 — role paths stay under the verified root;
per-worker inboxes live under the mail root.
**What remains:** K2 jailed `paths.role()`. `Mailbox._inbox` is
`self.root / worker / "inbox"` with no jail. Kernel passes `worker`
straight through.

Absolute worker:

```
RF-MAIL-ABS inbox=/tmp/.../escaped_inbox_home/inbox
mail_root=/tmp/.../Cosmos/state/mail under_mail=False
```

`worker=".."`:

```
RF-MAIL-DOTDOT inbox=/tmp/.../Cosmos/state/inbox
mail_root=/tmp/.../Cosmos/state/mail
```

```bash
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_reattack_foundation.py::test_repro_kernel_worker_id_escapes_mail_root \
  tests/test_reattack_foundation.py::test_repro_mail_dotdot_worker_escapes_mail_root
```

#### RF-LOCK-MUTATE — returned `Lease` is the live authority object
`acquire()` / `status()` return the same dataclass stored in
`_leases`. Setting `expires_at = 9e18` survives a clock jump;
`fenced_commit` still runs.

```
RF-LOCK-MUTATE same_object=True after_clock_jump holder=holder expires=9e+18
```

```bash
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_reattack_foundation.py::test_repro_lease_object_is_shared_mutable_authority
```

#### RF-SCHED-WAKE — filesystem drop wakes a waiter with an empty queue
Harvest B3 on the sched surface. `wait_for_submission` watches
`manifests/*.json`, not `JOB_SUBMITTED`. A forged file fires the waiter;
`queued()==[]`; ledger events `[]`.

```
RF-SCHED-WAKE fired=True mech=POLL-FALLBACK ... queued=[] events=[]
```

```bash
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_reattack_foundation.py::test_repro_sched_fs_drop_wakes_without_ledger
```

#### RF-CAS-LIE — `put()` trusts a planted blob name
`CAS.put` returns the content sha if a file of that name exists, without
reading it. `has()` is True. `get()` then raises `HASH_MISMATCH`.
Idempotence without a read-back is a lie about what is stored.

```
RF-CAS-LIE put=a36d196c... has=True
RF-CAS-LIE get -> HASH_MISMATCH (put already lied)
```

```bash
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_reattack_foundation.py::test_repro_cas_put_trusts_planted_blob_name
```

#### RF-SEG-M9 — Kernel authority is still a single `Ledger`
Harvest M9: framed segments + CAS are the authority. Module exists.
`type(k.ledger).__name__ == "Ledger"` on a booted Kernel. Anchors and
CAS are unused at the composition root.

```
RF-SEG-M9 kernel.ledger type=Ledger
```

```bash
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_reattack_foundation.py::test_repro_kernel_authority_is_not_segmented
```

---

### MINOR

#### RF-LOCK-EVENTS — `events()` is untyped on a torn line
Replay raises `TORN_LEDGER`. `events()` raises `JSONDecodeError`.

```
RF-LOCK-EVENTS replay=TORN_LEDGER events()=JSONDecodeError
```

#### RF-HMAC-32 — service HMAC is 128 bits
`len(rec["hmac"]) == 32` (`035459adcfc30b6f1d316ab7decb224f`). Harvest m6
is unchanged. Ledger flock + verify still hold (B1 closed).

#### RF-PATH-EMPTY — empty `tree_id` is a valid identity
`write_sentinel(root, tree_id="")` then `CosmosPaths(root)` succeeds.
`tree_id=''`.

---

## 5. What still holds (do not re-open without new evidence)

- Authority `Ledger` OS-lock + `STALE_HEAD` under overlap (B1/B2,
  `test_concurrency` PASS).
- Keyed Kernel lease replay refuses unsigned GRANT (K1).
- `role()` / `protected_write` refuse `..` and absolute parts (K2).
- Foreign-label `done()` refused (K5).
- TAKEOVER is a real event after EXPIRE (`test_cosmos_lock`).
- Mail `MISSING` ≠ `EMPTY`; torn message by hash.
- Sentinel content check (mesh() scar).
- `expect_head_seq` on `claim_next` / `done` (in-process).

---

## 6. Contract check (foundation only)

| Ratified rule | After stage-7 + this re-attack |
|---|---|
| One serialized writer (leases) | **Broken across processes.** Signing ≠ serialization. |
| Leases + fencing, stale refused | Holds in-process and on keyed replay. Unkeyed API and mutable `Lease` remain. |
| Framed signed segments | Module exists. Kernel unused. Anchors unsigned. `_load` not verify. Concurrent writers tear. |
| Queue = ledger lifecycle | Manifest dir is still a wakeup authority surface. |
| Resolver jail | `role()` holds. Mail `worker_id` join does not. |
| Per-worker identity | A label. Install key is tree-global. |
| Mounts are ingress only | Mail inbox + sched manifests remain mount-visible authority surfaces. |

---

## 7. Re-run

```bash
git checkout reattack/foundation
export PYTHONPATH=cosmos
python3 tests/test_cosmos_paths.py
python3 tests/test_cosmos_lock.py
python3 tests/test_cosmos_mail.py
python3 tests/test_core.py
python3 tests/test_segments.py
python3 tests/test_concurrency.py
python3 tests/test_kernel.py
python3 tests/test_stage7_fixes.py
python3 -m pytest -q tests/test_reattack_foundation.py
```

`test_repro_*` passing means the hole is still present.
`test_closed_*` passing means the original vector stayed closed.
