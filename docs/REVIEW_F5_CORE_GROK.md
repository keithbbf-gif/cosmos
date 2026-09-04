# COSMOS `f5/cosmos-core-v1` — GROK CRITIC REVIEW

**Critic:** Grok (not the builder).  
**Subject:** `origin/f5/cosmos-core-v1` @ `2651e20` (tag `v1.0-f5`).  
**Date:** 2026-08-23.  
**Contracts:** `docs/FINAL_ARCHITECTURE.md` (ratified), `docs/STAGE4_RUBRIC.md` H1–H10, `docs/STAGE2A_INCUMBENT_BEHAVIOR.md`.  
**Method:** read `cosmos/*.py` and `tests/*.py`; run pytest in this Linux container; then attack the claimed safety properties with probes. Docstrings are claims. Behavior is evidence.

**Scope kept:** this review does not modify `cosmos/` or `tests/`.

---

## Verdict

This is not COSMOS Core. It is a first-cut library of protocols plus a selftest harness that certifies the happy path.

The commit subject and tag claim **"full core"** and **"v1.0"** with **"all suites PASS native Windows."** Against the ratified architecture that claim is false. The code FAILS hard criteria **H1, H3, H4, H5, H8**. H2/H6/H7/H9/H10 are PARTIAL at best. A FAILS on any H eliminates. Native PASS is not architecture satisfaction.

The suites that pass do so because they never instantiate the failure modes the architecture exists to close: two writers, a lying mount, an expiring credit, a dead rail mid-run, a forgotten session fact, or a worker that imports around the kernel.

---

## H1–H10 scorecard

| id | score | one-line evidence |
|---|---|---|
| **H1** | **FAILS** | No context manifest. No `OPEN_CONTEXT`. Session close without inherited facts / open watchers / handoff recipient is not a detectable bug. Carry-over is "hope someone appended." |
| **H2** | **PARTIAL** | Many typed refusals exist and some are real. Then: `GET /rails` returns 200 + empty matrix; `install()` silently restamps `tree_id`; missing ledger `payload` is an untyped `KeyError`; `MAX_PATH` skip is marked PASS; spend kinds `RESERVATION_EXPIRED` / `DOUBLE_SETTLE` are never raised. |
| **H3** | **FAILS** | No ingress envelope (`INGRESS_ACCEPTED` does not exist). Concurrent `Ledger.append` / `Kernel()` **tears the authority chain** (measured). Spend after budget expiry is **ALLOWED** (measured). Scheduler never sees rail death. |
| **H4** | **FAILS** | The seven scar primitives are not kernel interfaces. No `VerifiedIO`, `ReturnWatcher`, `ReturnValidator`, `ContextManager`, `PlatformAdapter`. No capability enforcement — any importer writes the ledger. |
| **H5** | **FAILS** | `claim_next` is check-then-append with no serializer. Overlap can emit two `JOB_CLAIMED` **and break the sched ledger** (measured). A forged unsigned `GRANT` loads as a live lease (measured). |
| **H6** | **PARTIAL** | `Registry` knows CLI/API/DOM/CHAT/OTHER and can sort DOM-first. Kernel does not compose it. Probes are in-memory lambdas. No DOM worker, no Job Object, no typed DOM mid-run failure. `/rails` is silently empty unless a test monkey-patches `k.registry`. |
| **H7** | **PARTIAL** | Settable root + sentinel content check works. `install()` writes **no** installation record. Kernel takes a path, not `from_install_record()`. API is stdlib HTTP on `127.0.0.1`, not a served HTTPS Windows service. |
| **H8** | **FAILS** | No log-first. No helper `_` convention. No claimed-path command (nothing executes). Mail uses `os.replace` on a shared inbox. No closed writer set. No hash-manifest. "Exactly-once under overlap" is sequential theater. |
| **H9** | **PARTIAL** | Clock is injectable. `wait_for_submission` is a demo function, not the scheduler loop. HERE it is `POLL-FALLBACK`. No Task Scheduler registration or read-back. No Job Objects. |
| **H10** | **PARTIAL** | Files exist. Internal interfaces are classes, not RPC-shaped command/event contracts. Shipping the MVP boundary requires inventing the missing kernel (watchers, ingress, one writer, context, spend wiring, DOM rail). That is a redesign, not an increment. |

Soft criteria are not scored. There is no survivor to rank.

---

## What ran HERE vs what is marked NATIVE-DEMO-REQUIRED

### Bare `pytest tests/` (this container, no `PYTHONPATH`)

**6 collection errors. 0 tests collected.**

Every suite imports a top-level `cosmos_*` module. Pytest collects the test module *before* `main()` runs, so the `sys.path.insert(0, tests/)` inside each file never helps. `tests/` does not contain the modules. There is no `conftest.py`, no package install, no `pyproject.toml`.

```
ERROR tests/test_core.py          — No module named 'cosmos_ledger'
ERROR tests/test_cosmos_lock.py   — No module named 'cosmos_lock'
ERROR tests/test_cosmos_mail.py   — No module named 'cosmos_mail'
ERROR tests/test_cosmos_paths.py  — No module named 'cosmos_paths'
ERROR tests/test_kernel.py        — No module named 'cosmos_kernel'
ERROR tests/test_v1.py            — No module named 'cosmos_kernel'
```

A peer who clones the repo and types `pytest` gets this. The native "all suites PASS" claim is an environment claim, not a repo claim.

### `PYTHONPATH=cosmos pytest tests/` (same container)

**6 passed in 1.41s** (pytest wrappers). Script-mode selftests also exit 0 under the same `PYTHONPATH`.

| suite | HERE (Linux container) | marked NATIVE-DEMO-REQUIRED | builder's native note |
|---|---|---|---|
| `test_cosmos_paths.py` | 16 checks, rc=0. `MAX_PATH native demo` **SKIPPED off-Windows — NATIVE-DEMO-REQUIRED**, then recorded as **OK** so the suite still PASSES | yes — the only string in the tree | 17 checks; `MAX_PATH` 682 chars "NATIVE MEASURED" |
| `test_cosmos_lock.py` | 17 checks, rc=0 | no | 17 checks, rc=0 |
| `test_cosmos_mail.py` | 12 checks, rc=0 | no | 12 checks, rc=0 |
| `test_core.py` | 19 checks, rc=0. Wakeup: **`POLL-FALLBACK (watchdog absent - DEGRADED, recorded), 0.751s`** | not marked, but the interrupt *is* the H9 native demo | `V1_SUITE_RESULTS.md`: `os-file-watch, 0.607s`. First-cut notes: POLL-FALLBACK 0.754s |
| `test_kernel.py` | 13 checks, rc=0 | no | 13 checks, rc=0 |
| `test_v1.py` | 18 checks, rc=0 | no | 18 checks, rc=0 |
| `cosmos_spend.py` | **no suite exists** | n/a | unmentioned as a suite |

`watchdog` is not installed here (`find_spec` → `False`). The interrupt test still PASSES: `fired is True` is enough. Degraded observation is printed, then treated as success.

### NATIVE-DEMO-REQUIRED and native-only gaps this container cannot close

Marked in code:

1. **MAX_PATH / `\\?\` walk** (`tests/test_cosmos_paths.py`). HERE: skipped, counted as OK. The F5 notes themselves say plain `mkdir` died with WinError 206/3 on creation — that measurement is not reproduced here.

Not marked, but the architecture/incumbent require a native machine to prove:

2. **Interrupt-driven wakeup** (`ReadDirectoryChangesW` / watchdog). HERE: poll. Native v1 note claims `os-file-watch`. Even there it is a demo function, not the scheduler.
3. **Two-universes / lying mount** (sandbox write vs native authority). No ingress path exists to demo.
4. **Windows service recovery**, Task Scheduler register + read-back, Job Objects, DOM worker containment.
5. **UTF-8 both ends of a redirected pipe** — nothing executes a child.

Those are not "deferred polish." They are H3/H8/H9 load-bearing. Marking one skip and claiming v1.0 is the defect class.

---

## Ranked findings

### BLOCKER

**B1 — There is no single writer. Concurrent `Ledger.append` tears the authority chain.**  
H3, H5, Decision 1 + 3.

`Ledger.append` opens the file, writes a line, fsyncs. No flock, no mutex, no process-owned writer. Two `Ledger` objects primed on the same head both write `seq=2`. Reload: `BROKEN_CHAIN`. Measured.

`Kernel.__init__` **appends `BOOT_VERIFIED` on every construct.** `cosmos.py` builds a `Kernel` for `status`, `audit`, `submit`, `backup`, `rehearse`, and `serve`. A read is a write. Two overlapping `Kernel()` — the shape of `serve` plus `cosmos status` — leave the tree unbootable:

```
final Kernel boot: LedgerError [BROKEN_CHAIN] line 4: prev_sha does not chain to line 3
```

The architecture's mitigation for a single availability point is "never a second unsynchronized writer." This implementation *is* that second writer, any time two processes open the same root.

The suites never overlap two `Kernel` objects that both append. `test_kernel` constructs `k2` after `k1` is idle; that is restart, not concurrency.

**B2 — `claim_next` is not atomic. Overlap can double-claim and break the sched ledger.**  
H5, spike 4 brief ("the loser LOSES CLEANLY"), incumbent claim-by-rename.

```python
q = self.queued()           # projection
st = self._state()          # second projection
if st[m["job_id"]]["st"] != "QUEUED":
    raise SchedError("LOST_CLAIM", ...)
self.ledger.append("JOB_CLAIMED", ...)
```

The `LOST_CLAIM` path is the window between those two projections. Sequential callers never hit it: the second `queued()` is already empty and returns `None`. The suite's "every job claimed EXACTLY once" is a `while claim_next()` loop in one thread, then a count.

Force the window that exists in production (two callers both observed `QUEUED`, then both append):

```
results: [('B', '<same-job-id>', 'ok'), ('A', '<same-job-id>', 'ok')]
reload after overlapped claims: LedgerError [BROKEN_CHAIN] line 3: prev_sha does not chain to line 2
```

The incumbent's unhandled-loser gap is not closed. The new failure mode is worse: the queue's "authority" file is now unreadable.

Scheduler also does not take an arbiter lease. Fencing tokens are a different file, unused by the thing that needs them.

**B3 — No ingress. Mount-visible writes are already real.**  
H3 (lying mount + two universes), Decision 2, OA mount rule.

`INGRESS_ACCEPTED` does not appear in `cosmos/`. Mail `send()` writes the recipient inbox via `os.replace`. Scheduler `submit()` writes `manifests/<id>.json` then a ledger line. `wait_for_submission` watches the **filesystem** for a new `*.json`, not `JOB_SUBMITTED`. A sandbox that can drop a file can wake the waiter without a job existing.

Architecture: a mount write is ingress until the native service verifies bytes/hash/schema/identity and ledgers acceptance. Rename, lock-file, and directory observation on a mount are not authority. This code uses all three as authority.

**B4 — The seven scar primitives are not kernel interfaces. Workers import around them.**  
H4, Decision 11.

Stage 1 named: integrity-verified I/O · return watchers · return-validation · registry-reality reconciliation · session/context manager · platform adapter · typed absence.

Present as importable libraries: a ledger, a registry class, some typed errors, `extended()` for MAX_PATH. Absent as interfaces and as enforcement: `VerifiedIO`, `ReturnWatcher`, `ReturnValidator`, `ContextManager`, `PlatformAdapter`. No dispatch registers a watcher. No return is validated before use. `Kernel` docstring admits "no spend gate wiring." Tests and any worker `import cosmos_ledger` / `import cosmos_lock` and write.

A nominal module is what H4 called bolted-on. Capability enforcement is "workers cannot import around them." Here everyone can.

**B5 — Carry-over is not structural. No context manifest, no `OPEN_CONTEXT`.**  
H1, Decision 10.

OA's load-bearing H1 mechanism, adopted unanimously: every session close records inherited facts, active leases, open watchers, evidence pointers, handoff recipient; closure without a valid manifest is an `OPEN_CONTEXT` incident. Grep of `cosmos/*.py`: `OPEN_CONTEXT` = 0. A forgotten fact is still a fact nobody can detect.

The ledger can only preserve what someone chose to append. That is discipline, not mechanism.

**B6 — Three ledgers, two of them not the authority, one of them forgeable.**  
H2, H3, H5, Decision 3.

| file | hash chain | HMAC | who writes |
|---|---|---|---|
| `ledger/authority.jsonl` | yes | truncated | `Kernel` |
| `ledger/leases.jsonl` | **no** | **no** | `Arbiter._append` |
| `queue/sched_ledger.jsonl` | yes | truncated | `Scheduler` |

`Kernel.audit()` re-verifies only `authority.jsonl`. It does not verify the lease file or the sched ledger. A planted unsigned GRANT is a live lease:

```
forged GRANT loaded: Lease(resource='tree', holder='ATTACKER', token=99, expires_at=1e+18)
```

The arbiter's "torn ledger refuses" test plants unparseable JSON. It never plants a well-formed lie. The architecture said the lease table is a projection of the one signed ledger. This is a second unsynchronized writer with no authentication.

**B7 — Spend gate does not enforce expiring credit and is not composed.**  
H3 (expiring credit), Decision 1 (Core owns the spend gate), stage-1 "breaker lives in the caller."

`SpendGate.guarded_call` never reads `expires_epoch` on the budget or on a reservation. `RESERVATION_EXPIRED` and `DOUBLE_SETTLE` are declared on `SpendError` and never raised. Measured: budget `expires_epoch=1001`, clock advanced to `5000`, `guarded_call` **ALLOWED**.

Expired reservations are never swept; they hold the cap forever and deny later valid spend (fail-closed leak), while `audit()["headroom_usd"]` is `cap - settled` and **does not subtract reserved**. The audit lies in the other direction.

`Kernel` does not construct a `SpendGate`. `cosmos.py` does not call one. There is no spend test file. A module that cannot deny an expired credit is not a breaker.

---

### MAJOR

**M1 — `TAKEOVER` is dead code. The suite asserts the bug.**  
`Arbiter.acquire` sets `was_takeover = False` and never computes it. Comment says the chain is `EXPIRE -> TAKEOVER`. Events measured after dying-holder recovery: `['GRANT', 'EXPIRE', 'GRANT']`. `TAKEOVER present: False`.

`tests/test_cosmos_lock.py` checks `"EXPIRE" in ev` and that it is not the last event. It does not require a `TAKEOVER`. The test was written to the implementation.

**M2 — `install()` silently restamps identity. No installation record is written. Kernel never reads one.**  
H7, Decision 5.

`install()` calls `write_sentinel` unconditionally. Re-install with `tree_id="hijacked"` changes the identity of a live root. The comment says "Idempotent for the same tree_id; REFUSES to re-key." The refuse applies only to `install_key.bin`, not to the sentinel.

After install+boot, `config/` holds `install_key.bin` only. No `install_record.json`. `CosmosPaths.from_install_record()` exists and is tested for the *absent* case. `Kernel(root)` takes a path. Architecture: service cannot go READY without sentinel-verified root **and** installation record; the record is never inferred.

**M3 — `GET /api/v1/rails` is a silent fallback.**  
H2, H6.

If `kernel.registry` is missing — the Kernel never attaches one — the handler returns HTTP 200, `matrix: []`, `note: "no registry attached"`. Measured. `test_v1` does `k.registry = reg` after boot, then hits `/rails`. The CLI `serve` path never attaches a registry. An operator sees an empty rails matrix and can read it as "no links" rather than "registry not composed."

**M4 — Fenced commit is a mutex around a callback, not a fenced gateway.**  
Decision 2. Architecture: present fencing token **+ expected input hashes**; reject stale token, mismatched inputs, invalid identity.

`fenced_commit(self, lease, commit)` — no hashes. Check, run `commit()`, append `COMMIT`. No recheck after the callback. Measured: expire the clock *inside* the callback; result is `"landed"`, events `['GRANT', 'COMMIT']`. The write is real; the lease is already dead.

`Kernel.protected_write` acquire → replace → release in one call. Workers do not hold a token across a job. `os.replace` of a `.part` file is the "atomic rename survives only as a single-volume optimization, never authority" path used as the write.

**M5 — H8 incumbent behaviors are not in the runner because there is no runner.**  
`Scheduler` never calls a subprocess. No log-first `RUNNING` file. No helper `_` skip. No claimed-path command. No UTF-8 pipe. No `_`-prefix enforcement. No lane-with-jobs-and-no-worker flag. Three worded outcomes are strings in `done()`. `report_stale` is the one incumbent scar that landed.

Mail `send()` uses `os.replace` on a shared inbox — the mount-exposed rename the incumbent banned (append-over-rename). Closed writer set (`KNOWN_WRITERS`) is gone. Hash-manifest-at-claim is gone. These are not "adapted with the architecture-wins escape valve, recorded per tool." They are dropped.

**M6 — DOM is a sort key, not a scheduler rail.**  
H6, Decision 6.

`Registry.route` sorts live links with `pref["DOM"]=0`. That is the entire DOM implementation. No contained worker, no ephemeral profile, no Job Object, no `UNREACHABLE` / `SESSION_EXPIRED` / `AUTH_REQUIRED` / `BROKE` as attempt outcomes, no `report-never-retry` on a dead browser, no `DOM_BROWSER_LOST`. Compatibility lane / Legacy Job Adapter: absent.

**M7 — Backup is a library function, not a scheduled job type.**  
Decision 8, H9.

`Backup.run` / `rehearse_restore` copy + hash + ledger an event. Real verification on a tampered file: yes. Not a `rehearse-restore` job. Not admitted by the scheduler. Not registered with Task Scheduler. Not read back. Walk is `Path.rglob` without `extended()` — the C-60 MAX_PATH scar, unaddressed on the backup path. "Off-machine" is whatever directory the caller passed.

**M8 — The HTTP surface is not the product the architecture specified.**  
H7, Decision 7.

`ThreadingHTTPServer` on `127.0.0.1`. Not HTTPS. Not a Windows service. Not remote authorized access. `Service.__init__` **invents** `api_token.txt` if missing — the Kernel refuses to invent `install_key.bin` on the same install. Auth exists; the creation of the secret does not. POST `/jobs` swallows `Exception` as 400. No spend, backup, lease, or mail endpoints.

**M9 — Ledger is not the ratified ledger.**  
Decision 3: framed JSONL **segments**, OA framing, CoPG signatures, GEM content-addressed store (filename = hash; ledger holds the pointer). Corrupt segment ⇒ REFUSE + **incident**.

What shipped: one JSONL file, HMAC truncated to 32 hex chars (`[:32]`), no framing, no segments, no anchors, no CAS. A parseable line missing `payload` raises untyped `KeyError`, not `LedgerError`. No incident event (cannot append if verify dies — and nothing else records it).

**M10 — Audit is a partial projection that hard-codes the demo resource.**  
`Kernel.audit()` counts live leases as `sum(1 for r in ("tree",) if self.arbiter.status(r))`. Any other resource is invisible. Mail unread is "how many letters I have," not channel health. Jobs come from the *other* ledger, unverified by this audit's "chain: VERIFIED."

---

### MINOR

**m1 — `requires_ack` is stored on mail and never consulted.** Spike 3 asked for staleness = age threshold + unanswered required-ack. Probe uses mtime only.

**m2 — Spend reservation id is `r%d % int(clock * 1000)`.** Same millisecond, same `rid`. Projection key collision.

**m3 — `Arbiter.events()` is an untyped `json.loads` over the file.** Replay refuses torn lines. Introspection does not.

**m4 — Mail `probe` `UNREADABLE` is almost dead.** It only catches `OSError` from `glob()`. `unread()` collapses read/parse/hash failures to `TORN_MESSAGE`. Incumbent four-state rule: absent ≠ unreadable ≠ changed ≠ empty.

**m5 — `secrets()` location-safety is gone** with no recorded architecture-wins adaptation. Incumbent: `.secrets` is a sibling of the published tree so publish cannot ship it. COSMOS roles have `publish` under the one root and no secrets sibling.

**m6 — HMAC compare is on a truncated digest.** Not a substitute for the signed-anchor design. Fine as a spike; not fine as "service-signed authority" under a v1.0 tag.

**m7 — `wait_for_submission` poll fallback is honest when watchdog is missing.** It is still not wired to a run loop, and the test treats `fired=True` as the interrupt proof.

---

## What the suites do not prove (test theater)

These checks are named as if they closed a scar. They close a sequential unit test.

| claimed | what the test actually does |
|---|---|
| "every job claimed EXACTLY once (ledger count = jobs)" | one thread, `while claim_next()` |
| "fencing token is MONOTONIC across takeover" | expiry then `GRANT`, not `TAKEOVER` |
| "wakeup FIRED on submission" | any mechanism, including POLL-FALLBACK; `fired is True` |
| "MAX_PATH native demo" (off-Windows) | `RESULTS.append((..., True, "SKIPPED ... NATIVE-DEMO-REQUIRED"))` — skip is a pass |
| "DOM-first routing" | two lambdas, `policy_rank`, no worker |
| "RESTORE REHEARSAL" | `shutil.copy2` to a temp dir, not a scheduled job |
| "GET /rails: matrix served" | test attaches `k.registry = reg` first |
| "fenced write lands" | acquire+write+release in one process |
| "restarted kernel verifies the same chain" | sequential construct, no overlapping writer |
| spend breaker | **no tests** |
| two-universes / ingress | **no tests** |
| context close / `OPEN_CONTEXT` | **no tests** |
| helper `_` / log-first / claimed-path | **no tests** — no runner |
| unknown CLI flags | argparse default; **no test** |
| `from_install_record` happy path | only the absent-record refusal |

Negative controls that *do* land (torn sentinel, torn lock JSON, forged HMAC, dropped ledger line, missing mailbox, bare-rc outcome) are real and should be kept. They are not a substitute for the H-criteria the builder tagged v1.0 against.

---

## Incumbent scar gaps (stage 2a, unpaid)

Stage 2a rule: scars first, code second, docstrings never as evidence.

| scar / standing condition | this tree |
|---|---|
| Existence ≠ identity (mesh() empty dir) | **honored** — missing sentinel is `IDENTITY_MISMATCH` |
| No fallback / no drive literal in resolver | **honored** for `CosmosPaths` |
| Import-time vs explicit instantiation | **honored** — no module-global `ROOT` |
| Torn state refuses | **honored** on signed ledger + arbiter *parse*; **failed** on well-formed forged lease |
| Two universes / hard-coded path | resolver is clean; **mail and manifests are still shared writable surfaces** |
| Claim-by-rename under overlap | **replaced with a racy ledger append** |
| Command built from the *claimed* path | **nothing is claimed as a runnable path** |
| Three worded outcomes, log-first | outcomes exist as strings; **log-first absent** |
| Report-never-retry | **honored** for stale RUNNING |
| Helper `_` enforced in-runner | **absent** |
| Append-over-rename on mount-exposed state | **mail uses `os.replace`** |
| Closed writer set | **absent** |
| Hash manifest at claim | **absent** |
| Missing phone ≠ empty | **honored** (`MISSING` vs `EMPTY`) |
| Staleness on unanswered mail | **mtime only**; `requires_ack` unused |
| Per-worker identity, no last-writer-wins outbox | unique message ids; **inbox is still a shared rename target** |
| UTF-8 both ends of the pipe | **no pipe** |
| Heartbeat glob-discoverable, timezone-aware | **no worker heartbeat** |
| `\\?\` on every walk (C-60) | `extended()` exists; **backup `rglob` ignores it**; HERE MAX_PATH skipped-as-pass |
| Secrets safe by location, not blocklist | **dropped**, not recorded as architecture-wins |
| No parent-walking / no `__file__` arithmetic | **honored** in resolver |
| Negative controls in every selftest | present for the units they wrote; **absent for the H-failures above** |

---

## Composition map (what Core actually is)

```
install(root) → sentinel + role dirs + install_key.bin
                (no install record)

Kernel(root)  → CosmosPaths(root)          # path, not record
              → Ledger(authority.jsonl)    # HMAC-truncated JSONL
              → append BOOT_VERIFIED       # every construct
              → Arbiter(leases.jsonl)      # unsigned, unchained
              → Mailbox.register()
              → Scheduler(sched_ledger)    # third ledger
              → ready = True
              # NOT composed: Registry, SpendGate, Backup, Service,
              #               watchers, validators, context, DOM, ingress
```

The kernel docstring is more honest than the tag: "no HTTPS API yet, no DOM worker, no spend gate wiring, no Windows-service wrapper." Then `cosmos_service.py` / `cosmos_spend.py` / `cosmos_registry.py` landed as sibling files, the tag became `v1.0-f5`, and `test_v1` wired them in the test process by assignment. Composition in a test is not composition in Core.

---

## Recommendation

Do not treat `2651e20` / `v1.0-f5` as COSMOS Core. Do not ratify a runtime-binding gate against this artifact.

Keep: explicit resolver + sentinel content check; typed path errors; signed-ledger verify kinds (`TORN` / `BROKEN_CHAIN` / `FORGED`) when they actually run; mail's missing-vs-empty-vs-stale split; FINDINGS ≠ BROKE as vocabulary; stale-RUNNING report-never-retry; backup hash mismatch refusal.

Required before this can be called Core, in order, because each is an H-FAIL:

1. **One** hash-chained, service-signed ledger. Lease and queue state are projections of that ledger. One serialized writer. `Kernel()` must not append on read. A second process must not be able to boot-and-write.
2. **Ingress envelope** on every mount-visible surface. Directory watches and `os.replace` are not authority.
3. **Fenced claim** that is actually exclusive (arbiter token or equivalent), with a loser that loses cleanly **without** breaking the chain. A 100-iteration overlap test, as the spike brief asked.
4. **Context manifest + `OPEN_CONTEXT`.** H1 is not optional.
5. **Seven primitives as kernel interfaces with import/capability enforcement.** Watchers before dispatch. Returns validated before use.
6. **Spend gate composed and failing closed on expiry.** Tests that raise `RESERVATION_EXPIRED`.
7. **Incumbent runner scars** (log-first, helper `_`, claimed-path, UTF-8 pipes) or a recorded architecture-wins adaptation per tool.
8. Suites that fail when the environment cannot prove the native property — `NATIVE-DEMO-REQUIRED` must be a skip that **fails the v1 claim**, not an `OK`.

Until those close, the honest label is **spike-composition**, not v1.0.
