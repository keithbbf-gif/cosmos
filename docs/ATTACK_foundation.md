# COSMOS foundation cluster — adversarial attack
**Critic:** Cursor background agent (not the builder).
**Subject:** `f5/cosmos-core-v1` @ `e9e23ef`.
**Cluster:** `cosmos_paths`, `cosmos_ledger`, `cosmos_lock`, `cosmos_mail`, `cosmos_sched`, `cosmos_segments`.
**Date:** 2026-08-23. **Host:** Linux container. `PYTHONPATH=cosmos`.
**Contracts:** `docs/FINAL_ARCHITECTURE.md` (ratified), `docs/SPIKE_BRIEFS.md`, `docs/STAGE4_RUBRIC.md` H2/H3/H5/H8.
**Harvest:** `docs/REVIEW_F5_CORE_GROK.md` on `origin/review/f5-core-grok` (subject `2651e20`; not present on this branch). ~24 IDs (B1–B7, M1–M10, m1–m7); this note verifies every ID that touches the cluster and does not take the builder's "closed" labels as evidence.
**Method:** run every existing `tests/test_*.py` that imports the cluster; then new probes in `tests/test_attack_foundation.py`. Docstrings are claims. Behavior is evidence. A finding without a repro that ran is omitted.

`cosmos/` and existing `tests/` were not modified.

---

## 1. What ran HERE vs NATIVE-DEMO-REQUIRED

Command:

```
PYTHONPATH=cosmos python3 -m pytest -q \
  tests/test_cosmos_paths.py tests/test_cosmos_lock.py tests/test_cosmos_mail.py \
  tests/test_core.py tests/test_segments.py tests/test_concurrency.py \
  tests/test_wave3.py tests/test_kernel.py tests/test_port_plan.py
```

| suite | HERE | NATIVE-DEMO-REQUIRED / native-only | builder's native note |
|---|---|---|---|
| `test_cosmos_paths.py` | **PASS** 16 checks (script rc=0). `MAX_PATH native demo` **SKIPPED off-Windows — NATIVE-DEMO-REQUIRED**, recorded as **OK** | yes — the only marked skip in this cluster | 17 checks; MAX_PATH 682 chars "NATIVE MEASURED" |
| `test_cosmos_lock.py` | **PASS** 18 checks | no | 18 checks |
| `test_cosmos_mail.py` | **PASS** 12 checks | no | 12 checks |
| `test_core.py` (ledger+sched) | **PASS** 19 checks. Wakeup: **`POLL-FALLBACK (watchdog absent - DEGRADED, recorded), 0.751s`** counted as OK | not marked; interrupt *is* the H9 native demo | `V1_SUITE_RESULTS.md`: `os-file-watch, 0.607s` |
| `test_segments.py` | **PASS** 21 checks. Long-path CAS works on Linux (`extended()` is a no-op) | no (Linux long paths are not C-60) | same 21, plus Win32 `\\?\` |
| `test_concurrency.py` | **PASS** 17 checks (B1/B2/B7/M2/B5 theater-killers) | no | 17 checks |
| `test_kernel.py` | **PASS** 13 checks | no | 13 checks |
| `test_wave3.py` | **FAIL** `FileNotFoundError: 'py'` in `cosmos_runner` before B6/M4 execute | **NATIVE-DEMO-REQUIRED** — Windows `py` launcher. Not marked in the suite. | 31 checks including B6/M4 |
| `test_port_plan.py` | **FAIL** — discovery looks for `cosmos_*.py` in `tests/` and `SPIKE_F5_*`, not `cosmos/` | environment/layout, not a cluster primitive | 21 checks |

`watchdog` is absent (`find_spec` → False). `py` is absent. `os.name != "nt"`.

Bare `pytest tests/` without `PYTHONPATH` still cannot collect: every suite imports top-level `cosmos_*`. That is unchanged from the harvest.

Attack suite (this branch, not a builder suite):

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py
# 25 passed  (19 living repros + 6 closed-harvest checks)
# flake-checked 5× on the race probes
```

Convention: `test_repro_*` **passes if and only if the hole is present**. `test_closed_*` passes if the named harvest gap is actually closed.

---

## 2. Harvest verification (cluster-touching IDs only)

Source: Grok critic review at `2651e20`. Builder later tagged many "closed" in comments and in `test_concurrency` / `test_wave3` / `cosmos_segments`. Verified on `e9e23ef`.

| ID | harvest claim | builder says | HERE | verdict |
|---|---|---|---|---|
| **B1** | concurrent `Ledger.append` tears the chain | OS flock + re-prime | 3 processes × 30 appends = 90 records, seq 1..90, 3 writers, verifies. `test_closed_B1_multiprocess_ledger_chain` | **CLOSED** |
| **B2** | `claim_next` double-claim + broken sched ledger | `expect_head_seq` / `STALE_HEAD` → `LOST_CLAIM` | 100 thread-pair overlaps, 0 doubles, 0 broken chains. `test_closed_B2_hundred_thread_claim_races` | **CLOSED** (threads; the spike brief's 100-iter bar) |
| **B3** | no ingress; mount write is already real | `cosmos_ingress` exists | Ingress is a sibling. Mail still `os.replace`s into a shared inbox. Sched `wait_for_submission` watches `manifests/*.json`, not `JOB_SUBMITTED`. `test_repro_sched_fs_drop_wakes_without_ledger` | **OPEN** on cluster surfaces |
| **B6** | forged unsigned GRANT loads as a live lease | HMAC on events when `key=` | Keyed path refuses (`test_closed_B6_keyed_arbiter_refuses_forged_grant`). **Kernel composes `Arbiter(path)` with `key=None`.** Forged GRANT loads; `fenced_commit` returns `"PWN"`. `test_repro_lock_kernel_unsigned_forged_grant_commits` | **OPEN** in composition |
| **M1** | TAKEOVER was dead code | decide from last EXPIRE | `EXPIRE` then `TAKEOVER`, token monotonic. `test_closed_M1_expire_then_takeover_event` | **CLOSED** |
| **M2** | `install()` silent restamp / no install record | restamp refused; record written | `test_concurrency` M2 checks **PASS HERE** (paths-adjacent) | **CLOSED** |
| **M4** | lease expiry during callback still COMMITs | post-callback recheck → `COMMIT_UNFENCED` | Independent of the `py`-crashed wave3 suite. `test_closed_M4_unfenced_commit_is_incident` | **CLOSED** |
| **M9** | ledger is not framed JSONL segments + CAS + incident | `cosmos_segments.py` added | Module exists. Kernel authority is still `Ledger(authority.jsonl)`. Anchors unsigned. `last_record_sha` unused. Concurrent writers break history. `_load` appends onto poison. | **OPEN** |
| **m1** | `requires_ack` stored, never consulted | — | unanswered required-ack is `LIVE` if mtime is fresh. `test_repro_mail_requires_ack_unused` | **OPEN** |
| **m3** | `Arbiter.events()` is untyped `json.loads` | — | torn tail: replay → `TORN_LEDGER`; `events()` → `JSONDecodeError`. `test_repro_lock_events_untyped_on_torn` | **OPEN** |
| **m4** | probe `UNREADABLE` almost dead | — | inbox-is-a-file → `MAILBOX_MISSING`, not `UNREADABLE`. `test_repro_mail_file_inbox_is_missing_not_unreadable` | **OPEN** |
| **m6** | HMAC truncated to 32 hex chars | — | measured `len(hmac)==32` (`0bfc034c90de9a958a3a7b2eed9e9894`) | **OPEN** (design leftover; 128-bit truncate) |
| **m7** | poll fallback treated as interrupt proof | — | `test_core` wakeup OK via `POLL-FALLBACK`; `watchdog` absent | **OPEN HERE** |

Out of cluster (not re-litigated): B4, B5, B7, M3, M5, M6, M7, M8, M10, m2, m5.

---

## 3. Ranked findings

Every item names the pytest function that ran on this host and passed as a living repro.

### BLOCKER

**F-LOCK-RACE — The arbiter does not serialize. Eight processes all hold token 1.**
H5, Decision 2, spike 2 ("stale takeover = recorded event chain"), harvest B6's sibling: even an honest GRANT is not exclusive.

`Arbiter.acquire` is check-then-append with no flock, no mutex, no `expect_head_seq`. Two `Arbiter` objects (or eight processes that constructed before the first GRANT hit disk) all see free, all write `GRANT` with `token=1`. Replay last-writer-wins. Every caller believes it holds the fence.

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_lock_eight_process_same_lease
```

Measured: `WON W0..W7 token=1` × 8; ledger has 8 GRANT lines; replay lease holder is whoever flushed last. Flake-checked 5×.

The ledger flock on `cosmos_ledger` is not used here. The lock module is its own unsigned JSONL.

---

**F-LOCK-UNSIGNED — Kernel's arbiter is unkeyed. A forged GRANT commits. Harvest B6 is not closed.**
H3, Decision 2 + 3, harvest B6.

```74:74:cosmos/cosmos_kernel.py
        self.arbiter = Arbiter(self.paths.ledger("leases.jsonl"), clock=clock)
```

No `key=`. `test_wave3` "closes" B6 by constructing `Arbiter(..., key=KEY)` in the test process. Composition does not.

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_lock_kernel_unsigned_forged_grant_commits
```

Measured: `k.arbiter._key is None`; append unsigned `GRANT resource=secret holder=ATTACKER token=77`; next `Kernel` loads it; `fenced_commit` returns `"PWN"`.

---

**F-LOCK-MUTATE — `acquire()` returns the live authority object.**
H5. `Lease` is a mutable dataclass stored in `_leases` and returned to the caller. `status()` returns the same object. Mutating `expires_at` makes the lease immortal on the arbiter clock. Mutating `token` makes a stale handle current.

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_lock_lease_is_shared_mutable_authority
```

Measured: `arb.status("r") is lease`; set `expires_at=9e18`; jump clock 49s past TTL; `status` still live; `fenced_commit` after `lease.token=0` returns `"x"`.

---

**F-SEG-RACE — Two `SegmentedLedger` writers break the history they exist to protect.**
Decision 3, harvest M9. Rotation + in-memory `_active_count` are outside the per-file flock. Two instances rotate independently; `verify_all` raises `BROKEN_CHAIN` (seq accounting / anchor).

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_segments_concurrent_writers_break_history
```

Measured (5×): `LedgerError [BROKEN_CHAIN] seg-00001.anchor.json: seq accounting disagrees with the records`.

---

**F-SEG-LOAD — `_load` does not verify. Append continues a poisoned chain.**
Decision 3: "Corrupt segment ⇒ REFUSE + incident, never repair-in-place." `_load` reads anchors for counts and opens the live head. A corrupt sealed segment is not consulted until someone calls `verify_all`. `append` lands.

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_segments_load_appends_onto_corrupt_history
```

Measured: tamper `seg-00001.jsonl` payload; new instance appends `global_seq=5`; `verify_all` then refuses. The write already happened.

---

### MAJOR

**F-SEG-M9 — Harvest M9 is not closed. Kernel authority is still one JSONL file.**
Decision 3 (framed JSONL **segments** + CAS; corrupt segment ⇒ incident). `cosmos_segments` is a sibling library. `Kernel` opens `Ledger(self.paths.ledger("authority.jsonl"), ...)`. No segment rotation, no anchors, no CAS pointer, no incident log on the authority path.

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_segments_not_the_kernel_authority
```

Measured: `type(k.ledger).__name__ == "Ledger"`; path name `authority.jsonl`; no `k.segments`.

---

**F-SEG-ANCHOR — `last_record_sha` is written and never checked.**
The module's own docstring says the seam is auditable because the closing hash is carried in the anchor. Tamper `last_record_sha` on the last sealed anchor (no subsequent `prev_anchor_sha256` to break). `verify_all` yields all records.

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_segments_last_record_sha_is_decorative
```

Measured: 7 records, `max_records=3`; lie `last_record_sha="0"*64` on `seg-00002.anchor.json`; `verify_all` returns 7.

Anchors are also unsigned. A consistent rewrite of `prev_anchor_sha256` down the chain would pass the checks that do run.

---

**F-SEG-GAP — Missing closed segment is `FileNotFoundError`, not `LedgerError`.**
Four-state / H2. Delete `seg-00002.jsonl` + its anchor after a 3-segment history. Constructing `SegmentedLedger` raises untyped `FileNotFoundError` from `_load` reading a missing earlier anchor. The `verify_all` "unsealed mid-history" path is unreachable.

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_segments_gap_is_untyped
```

---

**F-PATH-ESC — `role()` will assemble a path outside the verified root.**
Decision 5 / H2: "no plausible-path assembly"; unknown roles refuse. Known roles accept `..` parts. `queue/../../etc/passwd` resolves outside the sentinel root.

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_paths_role_escapes_root
```

Measured: joined `.../rootA/queue/../../etc/passwd` → resolved `.../etc/passwd`, not under `rootA`.

---

**F-MAIL-ESC — `worker_id=".."` registers an inbox outside the mail root.**
Spike 3: addresses derived from one handed-in root; no resolution. `Path / worker / "inbox"` with `worker=".."` is `root/../inbox`.

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_mail_worker_escapes_root
```

Measured: inbox resolves to the temp parent, not under `mail/`.

---

**F-SCHED-DONE — Any worker can `done()` a job another worker claimed.**
H5 / spike 4: per-worker identity in every artifact; claim is exclusive. `done` checks `RUNNING`, not `by == self.worker`. Worker B writes `JOB_DONE` / `CLEAN` on A's claim.

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_sched_any_worker_can_done
```

Measured: state `st=CLEAN, by=B` after A claimed.

---

**F-SCHED-WAKE / B3 — A forged manifest wakes the waiter. No job exists.**
Decision 2: mount write is ingress until native verify + `INGRESS_ACCEPTED`. `wait_for_submission` watches the filesystem for `*.json`, not the ledger.

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_sched_fs_drop_wakes_without_ledger
```

Measured: drop `manifests/forged.json`; `fired=True` via `POLL-FALLBACK`; `queued()==[]`; ledger events `[]`.

Mail `send()` is the same class of hole (shared-inbox `os.replace`, no ingress). The sched wakeup is the one with a clean measured repro.

---

**F-CAS-LIE — `CAS.put` returns a sha that `get` cannot read.**
Decision 3 / CAS contract: idempotent put; get self-checks. If a blob of the right name already exists, put does **not** rewrite and does **not** hash-check. A planted `junk` file under the real sha: `put` returns the sha, `has()` is True, disk is still `junk`, `get` raises `HASH_MISMATCH`.

```
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py::test_repro_cas_put_lies_about_planted_blob
```

---

### MINOR

**F-PATH-SCHEMA — empty `tree_id` is a valid identity; bad `schema_version` is untyped `ValueError`.**
`test_repro_paths_empty_tree_id_and_untyped_schema`. H2 typed absence.

**F-LOCK-EVENTS / m3 — `events()` vs replay disagree on torn state.**
`test_repro_lock_events_untyped_on_torn`.

**F-LOCK-KIND — missing expected-input file raises `NO_LEASE`.**
`test_repro_lock_unreadable_input_miskinded`. Wrong kind (H2).

**F-MAIL-ACK-POLICY / m1 — `requires_ack` is payload decoration.**
`test_repro_mail_requires_ack_unused`. Also: `ack("no-such-id")` creates a ghost receipt.

**F-MAIL-UNREADABLE / m4 — file-where-inbox-should-be is `MAILBOX_MISSING`.**
`test_repro_mail_file_inbox_is_missing_not_unreadable`. Four states collapsed.

**F-LEDGER-HMAC-TYPE — `hmac` as int is `TypeError`, not `FORGED`.**
`test_repro_ledger_int_hmac_is_untyped`. `compare_digest` type-checks instead of refusing.

**m6 — HMAC truncated to 32 hex chars.** Measured: `len==32`. Decision 3 asked for service-signed records; this is a truncated HMAC, not a CoPG signature, and it is what Kernel actually uses on `authority.jsonl`.

**m7 / MAX_PATH skip-as-pass.** `test_cosmos_paths` records `MAX_PATH native demo` as OK with `SKIPPED off-Windows - NATIVE-DEMO-REQUIRED`. `test_core` records `POLL-FALLBACK` as the interrupt proof. Both suites exit 0. The native properties the architecture exists to close were not measured on this host and were not failed.

---

## 4. Contract check (ratified architecture vs this cluster)

| ratified rule | this cluster |
|---|---|
| One resident writer; never a second unsynchronized writer | **Ledger:** flock holds (B1 closed). **Arbiter / SegmentedLedger / mail inbox:** second writer is the implementation. |
| Leases + monotonic fencing tokens + fenced commit | Protocol exists in-process. Tokens are not exclusive across processes. Kernel fence is unsigned. Caller can mutate the live `Lease`. |
| Ledger = framed, hash-chained, signed JSONL **segments**; corrupt ⇒ REFUSE + incident | `cosmos_ledger` is one signed JSONL (HMAC[:32]). `cosmos_segments` is unused by Kernel. Concurrent segment writers and unverified `_load` violate the refuse-before-write rule. |
| Queue = immutable manifests + ledger lifecycle | Manifest file is not the claim source (good — mutation after submit is ignored). Waiter still treats a dropped file as a submission. `done` is not bound to the claiming worker. |
| Resolver = explicit, sentinel-verified, no guess | Holds for missing/empty/torn/wrong-system. Escapes via `role(..., "..")`. Empty `tree_id` is an identity. |
| Mounts are ingress/egress only | Mail and sched manifest dir are still mount-visible authority surfaces. |
| Typed absence, four facts four values | Several untyped crashes (`ValueError`, `TypeError`, `FileNotFoundError`, `JSONDecodeError`) and kind collisions (`NO_LEASE` for missing input, `MAILBOX_MISSING` for a file). |

What held and should be kept: sentinel content check (mesh() scar); ledger flock + `STALE_HEAD`; thread-safe `claim_next` exactly-once; keyed-arbiter `FORGED_EVENT`; `COMMIT_UNFENCED`; mail `MISSING`≠`EMPTY` for a truly absent dir; `FINDINGS`≠`BROKE`; stale-RUNNING report-never-retry; torn JSONL line refuses on ledger and on arbiter **replay**.

---

## 5. How to re-run

```
git checkout attack/foundation
PYTHONPATH=cosmos python3 -m pytest -q tests/test_attack_foundation.py
PYTHONPATH=cosmos python3 tests/test_attack_foundation.py   # same probes, script reporter
```

`test_repro_*` passing means the hole is still there. If a builder closes a hole, that repro should fail — that is the signal, not a regression in this file.
