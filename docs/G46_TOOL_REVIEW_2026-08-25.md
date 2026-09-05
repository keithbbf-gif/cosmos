# G46 (grok-4.6) - Critical Tool Review - 2026-08-25

_Dispatched by COW per group via the sgh rail; COW verifies + synthesizes._



## HEART (kernel/ledger/lock/sched)

(no text; detail=API)


## HANDS (rails/node_rails/registry/spend)

## cosmos_rails.py
**(1) FEATURE SET**  
Rail adapters (`CliRail`, `DomRail`, `ApiRail`) with `probe`/`dispatch`; `Dispatcher` picks registry live links (DOM-first), optional spend gate, ledger events, typed fallback vs fail.

**(2) CONTRACT MATCH**  
Mostly matches docstring: DOM-first via `registry.route`; metered path through `spend.guarded_call`; dead DOM kinds allow audited fallback. Gaps vs “never silent fallback” / CHAT/OTHER coverage.

**(3) DEFECTS/GAPS**  
- `Dispatcher.dispatch` — **HIGH**: missing adapter (`adapters.get` is None) is skipped with no ledger event; can exhaust candidates and raise `NO_LIVE_LINK` without a typed “adapter absent”.  
- `Dispatcher.dispatch` — **MED**: spend-gate exception is always `NOT_PERMITTED`; other exceptions from `guarded_call` (UNKNOWN_RAIL, etc.) are mis-kinded.  
- `Dispatcher.dispatch` — **MED**: `CliRail`/`ApiRail` failures without DOM-like `kind` raise `RAIL_FAILED` immediately (no next-link); policy “skip dead only if another LIVE exists” is incomplete for non-DOM.  
- `CliRail.dispatch` — **MED**: no try/except; `run`/`KeyError` can leak untyped. Truncates `out` to 2000 with no flag.  
- `DomRail.dispatch` — **LOW**: assumes `payload["job_id"]`/`["url"]`; KeyError untyped.  
- `ApiRail.probe` — **LOW**: always True (“liveness is per-call”) vs module claim every rail is probed/typed.  
- Group — **UNKNOWN**: `CHAT`/`OTHER` adapters not in this file.

**(4) UNKNOWN**  
`cosmos_platform.run` shape; `DomWorker.run_attempt` result schema; whether `ledger.append` is durable.

---

## cosmos_node_rails.py
**(1) FEATURE SET**  
`NodeRail` wraps incumbent `ask()` via late `sys.path` + import; `register_node_rails` registers four API links, probes, budgets.

**(2) CONTRACT MATCH**  
Wrap-don’t-reimplement and UNREACHABLE-on-import-fail: yes. “DOM lane preferred”: **not implemented here** (no DOM adapter; all `policy_rank=0` API). Cursor mentioned in docstring, not in `specs`.

**(3) DEFECTS/GAPS**  
- `register_node_rails` — **MED**: docstring “cursor” omitted; all ranks 0 so DOM-first must come from elsewhere.  
- `register_node_rails` — **MED**: `spend_gate.set_budget` failures swallowed (`except: pass`) — budget may be missing while adapter is metered.  
- `NodeRail.dispatch` — **MED**: `r.get("ok", True)` treats missing `ok` as success.  
- `NodeRail.probe` — **LOW**: import success ≠ liveness (stated, but registry will mark live).  
- `NodeRail._load` — **LOW**: hardcoded `_BTS = r"V:\Ai\BTS_MESH"`; non-portable.  
- Group — **UNKNOWN**: incumbent `ask` contracts.

**(4) UNKNOWN**  
Whether DOM rails are registered in another module; real module names.

---

## cosmos_registry.py
**(1) FEATURE SET**  
Ledger-backed link claims, attachable probes, `probe`/`probe_all`, `state`/`matrix`, `route` with freshness + DOM preference + `policy_rank`.

**(2) CONTRACT MATCH**  
Claim vs measurement vs age: yes. Stale-not-live (H-05): yes. `UNREACHABLE` as probe fail: yes. `route` sorts `-policy_rank` then rail pref.

**(3) DEFECTS/GAPS**  
- `route` — **MED**: `not v["ok"]` drops `ok is None` (never probed) — good; but `ok` False and True only — no explicit STALE status in `matrix` (age only).  
- `state` fold — **LOW**: re-`register` same `link_id` resets `last_probe`/`ok` (claim wipe).  
- `probe_all` — **LOW**: `UNKNOWN_LINK` shouldn’t happen if iterating `state()`; `NO_PROBE` recorded as UNPROBEABLE.  
- `matrix` — **LOW**: `verified` is last `ok`, not “fresh AND ok”.  
- Group — **UNKNOWN**: `ledger.project`/`append` concurrency vs spend’s `append_guarded`.

**(4) UNKNOWN**  
Clock/ledger timestamp units (`rec["t"]` vs `time.time()`).

---

## cosmos_spend.py
**(1) FEATURE SET**  
Budget set, reserve/deny/call/settle, expiry sweep, `append_guarded` atomic cap check, audit (overspend + expiry).

**(2) CONTRACT MATCH**  
Reserve-then-call-then-settle: yes. Unpriced `usd is None`: yes. Cap refresh preserves settled (RG-M1): yes. Expired budget deny (B7): yes.

**(3) DEFECTS/GAPS**  
- `guarded_call` — **HIGH**: first cap check mutates in-memory `b["reserved"]` (`del`) **without** `SPEND_RELEASED` for those rids in that path wait — actually it **does** append `SPEND_RELEASED` then `del b["reserved"]` on a **projection copy**; if `project` returns shared nested dicts, this mutates cached state. **UNKNOWN** if fold output is copied. If shared: **HIGH** corruption.  
- `guarded_call` `_decide` — **MED**: expired reservations popped in `st2` **without** ledger `SPEND_RELEASED` under the lock (only in-memory), so outstanding can drop without events; next fold still counts them until a later sweep. Racey headroom.  
- `guarded_call` — **MED**: `DOUBLE_SETTLE` in docstring never raised.  
- `guarded_call` — **LOW**: `RESERVATION_EXPIRED` never raised (sweep instead).  
- `audit` — **LOW**: expiry_risk ignores reserved vs “unspent”.  
- Group — **UNKNOWN**: `append_guarded` lock semantics if `_decide` raises `SpendError`.

**(4) UNKNOWN**  
Whether `ledger.project` deep-copies; `append_guarded` API.

---

## Verdict: **WATCH**
**Top risk:** Dispatcher skip-missing-adapter + spend `_decide` in-memory expiry pop without durable release can dispatch/spend on a wrong picture of “live” and headroom; node rails also register metered adapters even if `set_budget` silently fails (`UNKNOWN_RAIL` at call time).


## CARRYOVER = BU/TU/COS (session/paths)

## cosmos_session.py

**(1) FEATURE SET**  
Session lifecycle: TidyUP (`close_session`) validates control files + ledger, closes in-memory or reconstructed session, writes HMAC’d `SEED.json` + sidecar + dated archive (never-delete). BootUP (`start_session`) verifies length/hash, install-key MAC, tree_id, then injects facts/watchers into a new `Session`. `project_live_session` folds ledger events. Module wrappers on `kernel.sessions`.

**(2) CONTRACT MATCH vs docstring**  
Mostly matches: parse+validate controls, reconstruct if no live Session, inherit via `boot_inherit()`, typed refusals, seed + sidecar, no unlink. `start_session` does INTEGRITY / AUTHENTICITY / IDENTITY in that spirit.

**(3) DEFECTS/GAPS**  
- **`close_session` (reconstructed path)** — **HIGH**: If ledger says session is open, it appends `SESSION_CLOSED` without calling `Session.close()`. In-memory path uses `session.close()` (UNRESOLVED unless `force`). Reconstruct path can skip the same close semantics/side effects as `cosmos_context`.  
- **`close_session` + `boot_inherit`** — **MED**: After a live `session.close()`, watchers come from the manifest; incidents from inherit can still merge extra unresolved into the seed. Easy to double-count or re-open already-closed watchers on next boot.  
- **`start_session` / `open`** — **MED**: `open()` only blocks if `self.session._open`. After `close_session` with `self.session is None`, a second `start_session` can inject another seed while a prior session is still “open” on the ledger (no check of `project_live_session`).  
- **`validate_control_files`** — **MED**: Extra `config/*.json` are parse-only; docstring says every control file must parse **and** validate. Same “verify_conf scar” the comments warn about.  
- **`_write_seed` archive** — **LOW**: Archive copies previous seed bytes only; declaration sidecar is not archived. Clock collision (`archive.exists()`) skips archive.  
- **`_install_key`** — **LOW**: Falls back to `config/install_key.bin` if ledger has no `_key`; couples to a private ledger attribute.  
- **`start_session` facts/watchers** — **LOW**: All values coerced with `str()`; non-string inherit is silently flattened.

**(4) UNKNOWN**  
Behavior of `boot_inherit`, `Session.close`/`record_fact`/`open_watcher`, `write_declared`/`read_verified`, and whether `kernel.sessions` is always a `SessionManager`. Ledger event schemas (`FACT_RECORDED` keys, etc.).

---

## cosmos_paths.py

**(1) FEATURE SET**  
Single-root resolver: sentinel content check, optional `expected_tree_id`, `from_install_record` (path or `COSMOS_INSTALL_RECORD`), role table + `__getattr__`, traversal rejection + `relative_to` confine, Windows `extended()` / `walk()`, `write_sentinel`.

**(2) CONTRACT MATCH vs docstring**  
Matches the listed contract well: no ladder/fallback/import-time IO, construction verifies, typed `CosmosPathError`, roles in one table, MAX_PATH helper, no live tree names in the docstring. Empty `tree_id` is still accepted as a valid sentinel (session TidyUP later rejects that).

**(3) DEFECTS/GAPS**  
- **`role` confinement** — **MED**: `out.resolve().relative_to(self._root)` — if `_root` is not resolved the same way as `out` (symlinks), `relative_to` can false-positive or miss. `_root` is `resolve()`d in `__init__`; generally OK, still symlink-sensitive on some platforms.  
- **`role` `..` check** — **LOW**: `".." in p.replace(...).split("/")` misses `foo/../bar` if split is wrong on mixed separators — they normalize `\` to `/` first, so OK; `....` is not `..`. Fine.  
- **`_read_sentinel` missing file** — **LOW**: Missing sentinel is `IDENTITY_MISMATCH` not `NOT_FOUND` (intentional per mesh() scar; kind set is still used).  
- **`from_install_record`** — **LOW**: `tree_id` optional (`d.get`); record without tree_id skips identity match. Session TidyUP requires both.  
- **`walk`** — **LOW**: `os.walk(extended(...))` on Windows may yield `\\?\` strings; callers expecting `Path` under root are unspecified.  
- **`write_sentinel`** — **LOW**: No atomic write / no validation of `tree_id`. Installer helper only.

**(4) UNKNOWN**  
Whether service READY actually constructs `CosmosPaths`; selftest “two scratch roots” is claimed in docstring but not in this file.

---

## Verdict: **WATCH**

**Top risk:** Session close/reconstruct vs BootUP can desync: reconstructed `SESSION_CLOSED` ≠ `Session.close()`, no ledger-open check on `start_session`, and inherit/incident watcher merge can re-inject watchers. Wrong or duplicate carry-over across process restart — the exact failure this module exists to make loud. Paths are comparatively solid; session lifecycle is the FIX candidate if those close/open invariants are load-bearing.


## RUNNER + PULSE (runner/health)

## cosmos_runner.py

**(1) FEATURE SET**  
Claim/execute/drain scheduler jobs. `py:` scripts and `argv:` JSON lists confined to tools root; `_`-prefixed helpers refused. Log-first attempt dirs, `run_tree_killed`, outcomes CLEAN / FINDINGS / BROKE. Interpreter whitelist for `argv[0]`. `drain(max_jobs)`.

**(2) CONTRACT MATCH vs docstring**  
Mostly matches: log-first, claimed path, helper refusal recorded, UTF-8 via `run_tree_killed` (assumed), rc mapping, attempt-private artifacts. Gaps: docstring says default tools dir `work parent / "cosmos"` vs comment `"tools"`; `tools_root` is never set in `__init__`. Bare `cmd` (not `py:`/`argv:`) becomes `py -3.14 -c` with no confinement. `py:` always uses `["py", "-3.14", str(script)]`, not the claimed interpreter.

**(3) DEFECTS/GAPS**  
- `_tools_root` / `run_one` — **MED**: default `work.parent / "cosmos"` vs comments/`tools`; no constructor injection of `tools_root`.  
- `run_one` (else `-c`) — **HIGH**: unprefixed command is `-c` with no argv confinement (docstring “no shell” ≠ code injection via `-c`).  
- `_confine_argv` — **MED**: `-c` anywhere in rest skips all path confinement (e.g. script + `-c`).  
- `_confine_path` — **MED**: `exists()` after `resolve()`; TOCTOU vs claimed path; `relative_to` can still allow same-drive surprises on some Pythons/Windows.  
- `_is_whitelisted_interp` — **LOW**: `name.startswith("python3")` after whitelist (e.g. `python3-evil`).  
- `run_one` — **LOW**: `json.loads` only catches `ValueError` (not `TypeError`); refuse path may skip log/result.json (doc: every artifact attempt-private).  
- `run_one` — **UNKNOWN**: whether `cosmos_platform.run_tree_killed` is no-shell UTF-8 as claimed.

**(4) UNKNOWN**  
`Scheduler.claim_next`/`done` contracts, `run_tree_killed` kill/timeout semantics, real `tools_root` wiring.

---

## cosmos_health.py

**(1) FEATURE SET**  
`HealthBoard`: builtin rows (ledger, sentinel, queue, mail, leases, planted RED), `add_row`, `run()` with exception isolation, strip negative control, SHARED-CAUSE if all remaining reds share a detail prefix, ledger `HEALTH_BOARD`.

**(2) CONTRACT MATCH vs docstring**  
Matches: rows are callables, planted failure must be RED, GREEN-control → `BOARD-BROKEN`, all-red same reason → `DIAGNOSIS: SHARED-CAUSE`. “every subsystem” is only the registered builtins; ages are epoch/`elapsed_s`, not per-row ages.

**(3) DEFECTS/GAPS**  
- `queue_alive` — **MED**: uses `k.sched._state()` (private); `stale_reported` meaning UNKNOWN — empty queue is GREEN by design.  
- `ledger_chain` — **MED**: `sum(1 for _ in k.ledger.verify())` — if verify is a bool or raises, row handling exists; if it yields without validating, always GREEN.  
- `resolver` — **LOW**: second tuple element is always the same string even when `ok` is False (detail does not say missing).  
- `lease_board` — **LOW**: always `True` (cannot go RED).  
- `run` SHARED-CAUSE — **LOW**: only when *all* non-control rows red and same `detail.split(":")[0]`; planted row excluded (correct).  
- `add_row` — **LOW**: can overwrite `"negative control (must be RED)"` and break the pop/check.

**(4) UNKNOWN**  
`Kernel`/`ledger.verify`/`mail.probe`/`arbiter.status` shapes; whether `stale_reported` is populated.

---

**Verdict: WATCH**  
**Top risk:** Runner `py -c` / `-c` short-circuit plus weak `tools_root` default — job text can execute unconstrained Python while K4 confinement is documented as the boundary.

## HEART (kernel/ledger/lock/sched) - completed split


### HEART/kernel+ledger

## cosmos_kernel.py

**FEATURE SET**  
Composition root: `CosmosPaths` → install key → `Ledger` → optional `BOOT_VERIFIED` → Arbiter/Mailbox/Scheduler/Registry/SpendGate/ReturnValidator/SessionManager/MakerMap/ConvoStore/ITC. `read_only` skips mkdir, boot event, mail register, maker seed; monkey-patches arbiter append/expire. `open_session`, `accept_return`, `protected_write` (path then lease → stage → fenced_commit → ledger), `audit()`, `install()`.

**CONTRACT MATCH vs docstring**  
Mostly matches boot order, fail-fast, read-only “reader is not a writer”, fenced commit, audit from measurements. Gaps vs stated contract: no public `status()` (docstring claims it); `leases_live` only counts `"tree"`; `accept_return` still calls `sched.done` even if validator path is the “gate”; ITC `_https_get` is live urllib at construct (not called until refresh).

**DEFECTS/GAPS**  
- `Kernel.__init__` / `_ro_append` — **MED**: patches private `_append` / `_expire_if_due`; fragile vs Arbiter internals.  
- `Kernel.audit` — **MED**: `leases_live` hardcoded to `("tree",)` only; not a measured lease set.  
- `Kernel.accept_return` — **MED**: if `job_id` set, `sched.done` runs after `validator.accept` with no check that accept refused; docstring says unvalidated return leaves scheduler unchanged. UNKNOWN: `ReturnValidator.accept` raise vs return.  
- `Kernel.protected_write` — **LOW**: docstring after `target = ...` is a stranded string, not attached to the method.  
- `Kernel.__init__` `_https_get` — **LOW**: `# noqa: S310` unbounded URL fetch on refresh.  
- `install` — **LOW**: `tree_id` `""` treated as matching any re-install (`not in ("", tree_id)`).  
- Missing `status()` — **MED** vs module docstring.

**UNKNOWN**  
Arbiter/Mailbox/Scheduler/SessionManager/ReturnValidator APIs; whether `ready=True` is ever false after partial compose; CosmosPathError kind `"NOT_FOUND"` for policy refusals.

---

## cosmos_ledger.py

**FEATURE SET**  
HMAC’d hash-chained JSONL; `verify` primes seq/prev; exclusive sidecar lock (msvcrt poll / flock); `append` re-verify under lock + optional `expect_head_seq`; `append_guarded`; `project`/`last`/`head_seq`; TORN vs BROKEN_CHAIN vs FORGED vs UNREADABLE; empty missing file vs unreadable.

**CONTRACT MATCH vs docstring**  
Matches record fields, total verify, three-way break kinds, append+fsync, STALE_HEAD, legacy 32-hex HMAC. `hmac` is over `seq|prev_sha|payload_sha` as documented (not full line).

**DEFECTS/GAPS**  
- `Ledger.verify` — **HIGH**: `prev_sha` of next record is SHA256 of **raw file line**, but `append` sets `_prev_sha` from SHA256 of `json.dumps(rec, ...)` **without** requiring that equals the on-disk line forever; verify hashes `ln` as read. Consistent if dumps is stable. Risk: any future dump change / `\r` / non-UTF8 tears chain.  
- `Ledger.append` / `append_guarded` — **MED**: full-file `verify()` on every append (O(n) under lock).  
- `Ledger._lock_handle` (Windows) — **MED**: infinite poll on contention; no timeout.  
- `Ledger.verify` HMAC — **LOW**: accepts truncated 32-hex forever (intentional, still weaker compare surface).  
- `utc_off` — **LOW**: `time.timezone` + `tm_isdst`; DST/platform offset UNKNOWN vs “offset-aware”.  
- `append` vs `append_guarded` — **LOW**: duplicated record construction.

**UNKNOWN**  
Crash between write and fsync leaving TORN last line (by design refuse); concurrent readers during append; lock file leftover empty.

---

**Verdict: WATCH**  
**Top risk:** Kernel `accept_return` / audit lease accounting vs stated gates; ledger lock + full-chain reverify under every write, plus line-vs-canonical hash coupling for `prev_sha`.

### HEART/lock

(no text; None)

### HEART/sched

## HEART/sched — `cosmos_sched.py`

### FEATURE SET
- Immutable job manifests on disk + all transitions as ledger events; queue is a fold projection.
- Submit with explicit priority (no silent default), deterministic order `(priority desc, submitted asc, job_id)`.
- Optimistic-concurrency claim (`expect_head_seq`) → typed `LOST_CLAIM`.
- Three worded outcomes; claimant-only `done()`; refuse second completion.
- `report_stale`: `JOB_STALE` only, no auto-retry.
- `wait_for_submission`: watchdog if present, poll fallback that labels itself DEGRADED.
- Per-worker identity on events; `SchedError` kinds as documented.

### CONTRACT MATCH vs docstring
| Clause | Match |
|---|---|
| Immutable manifests + ledger events | Yes (`submit` writes then `JOB_SUBMITTED`) |
| Priority field + sort key | Yes |
| Atomic claim, loser typed | Yes (`STALE_HEAD` → `LOST_CLAIM`) |
| CLEAN / FINDINGS / BROKE | Yes (`OUTCOMES`) |
| Worker on events | Yes on claim/done/stale; submit uses `submitter` |
| No overwrite of shared mutable file | Ledger append-only; manifests never rewritten |
| Stale = report, never retry | Yes |
| Interrupts: OS wakeup or loud poll | Partial: watchdog path never records “which mechanism fired” vs contract’s ReadDirectoryChangesW; poll does say so |

Gaps vs contract (not silent):
- `wait_for_submission` watches **manifest files**, not ledger events; claim/done do not wake waiters.
- Watchdog `on_created` only; no Windows-specific API named in the return value.
- `JOB_CLAIMED` fold ignores claim if not QUEUED (good) but **does not surface** a losing append that still landed if `expect_head_seq` were omitted—depends on Ledger.
- Terminal states are outcome strings (`CLEAN` etc.), not a separate `DONE` + outcome field—projection `st` overloads status vs outcome.

### DEFECTS/GAPS
- **`claim_next` — MED**: Head is sampled **before** `queued()`. A submit between `head_seq()` and `append` yields `STALE_HEAD`/`LOST_CLAIM` even when this worker would still win the same job (spurious loss; caller must retry—documented, but noisy).
- **`claim_next` — MED**: After a lost claim, the job may still be QUEUED; loser must re-call. Fine. If Ledger **does** append `JOB_CLAIMED` without `expect_head_seq` on older Ledger, double-claim is possible — **UNKNOWN** without `cosmos_ledger`.
- **`done` — MED**: Same TOCTOU: `_state()` then later `head_seq()`. Completing worker can `BAD_STATE` on unrelated ledger traffic. Also: if claimer crashed after claim, **no other worker can `done()`** (by design of K5) and stale only flags, never completes—jobs can stay `RUNNING` forever except `stale_reported`.
- **`report_stale` — HIGH**: No `expect_head_seq`; concurrent `report_stale` can double-append `JOB_STALE`. Fold sets `stale_reported` only after project; race window is real. Does not require reporter == claimant (OK per “report”). Does **not** change `st` from RUNNING—stale jobs still look RUNNING to `queued`/`done`.
- **`report_stale` — MED**: `claimed` missing → `now - now` never stale (`v.get("claimed", now)`). Old events without `claimed` never report.
- **`_state` / `JOB_CLAIMED` — LOW**: Ignores claims when not QUEUED (correct) but does not record refused claims.
- **`wait_for_submission` — MED**: Uses wall `time.time()`, not injected `_clock` (tests/latency). Observer may miss events during `sleep(0.01)`. `ImportError` only; watchdog present-but-broken is unhandled. Timeout with watchdog returns `fired: False` still labeled `os-file-watch`. Does not wait on ledger.
- **`submit` — LOW**: Manifest write then ledger; crash between = orphan file, projection empty until replay of event (file not source of truth—OK) but waiters fire on file not event.
- **`submit` — LOW**: `job_id` from clock ms + 10 hex chars; same-ms collision theoretically possible (uuid makes it rare).
- **`SchedError` — LOW**: Docstring kinds omit using `BAD_STATE` for outcome/completer/stale-head on done.

### UNKNOWN (not guessed)
- Whether `Ledger.append(..., expect_head_seq=)` and `head_seq()` / `STALE_HEAD` exist and are atomic under the OS lock.
- Whether `project(fold, {})` is a full replay every call (perf) and whether payload always has `job_id`.
- Multi-process vs threads; watchdog Observer thread-safety with this process’s ledger writers.
- Lane field: stored, never used (routing UNKNOWN if required by brief elsewhere).

### Verdict: **WATCH**
**Top risk:** stale RUNNING jobs cannot be completed by anyone but the original claimant, and `report_stale` neither terminals them nor is concurrency-safe—stuck RUNNING + duplicate `JOB_STALE` under concurrent reporters.

### HEART/lock (via Grok Build CLI, internal rail bypassed -- see cosmos_rails.py defect notes)


| Grant/renew/expiry on arbiter clock | **Match.** |
| Tokens survive restart via replay | **Match.** Tested. |
| Stale/superseded install refused and ledgered | **Match** for `StagedArtifact`. |
| Dying holder: no release, expiry, higher token, late commit refused | **Match.** Tested (`EXPIRE` then `TAKEOVER`). |
| Torn line → `TORN_LEDGER`, never “free” | **Match** for unparseable JSON. |
| RF-LOCK-LIVENESS: OS mutex not held across callback | **Match.** Tested, including FakeMsvcrt. |
| RF-LOCK-XPROC: two keyed arbiters cannot both grant token 1 | **Match.** Same-process + two-interpreter tests. |
| “Commit callback runs ONLY under a currently-valid token” | **Mismatch.** Phase B still runs after expiry; install is fenced at Phase C. Legacy 0-arg callbacks can write unfenced (`COMMIT_UNFENCED`) — documented later, contradicts this bullet. |
| “Every event is marked `unsigned=true`” | **Mismatch.** `_append` never sets it. Unkeyed events are simply unsigned. |
| “A signed ledger REFUSES an unsigned event” | **Match only if this `Arbiter` is keyed.** Unkeyed load ignores `sig`. |
| `LockError.kind` includes `UNKNOWN_RESOURCE` | **Mismatch.** Never raised. |
| Spike brief `LEASE_EXPIRED→LEASE_GRANTED` | **Mismatch vs brief** (names). Module uses `EXPIRE`→`TAKEOVER` and tests the module names. |

Architecture decision 3 (hash-chained framed JSONL) is **`cosmos_ledger`**, not this file. This ledger is HMAC’d JSONL, not chained. Dual authority is a composition fact, not a silent match.

---

## (3) DEFECTS / GAPS

**`Arbiter.__init__`, `status`, `events` — MED.** Replay/status/events are not under the sidecar lock. Mutating paths lock + reprime; these do not.

- `status`: if memory has no lease, returns `None` with no disk read. If memory has a not-yet-due lease, returns it with no reprime. Same-process `ThreadingHTTPServer` can report “tree free” during another thread’s `_reprime` (`self._leases = {}` then rebuild). Cross-process, a long-lived `Arbiter` can show held/free opposite to disk until a locked op.
- `events` / constructor `_replay`: a concurrent append can make the last line look torn → `TORN_LEDGER` on a healthy writer.

**`Arbiter._replay` — MED.** Parseable JSON missing `resource` / `holder` / `expires_at` / a non-int `token` raises `KeyError`/`ValueError`/`TypeError`, not `TORN_LEDGER`/`FORGED_EVENT`. Fail-closed in spirit, untyped.

**`Arbiter._append` / `Arbiter` docstring — MED.** Claimed `unsigned=true` is not written. Mixed keyed/unkeyed on one file is a silent split brain: unkeyed will load a signed history without verifying.

**Lease JSONL has no `prev_sha` — MED.** Tail truncate rewinds `RELEASE`/`EXPIRE`/`TAKEOVER` without `FORGED_EVENT`. B6 closed *append a well-formed GRANT*. Delete-from-end is the same class of lie from the other direction. Needs write access to `leases.jsonl` (compromised host), but the authority ledger closed this with a chain and this file did not.

**`Arbiter.fenced_commit` (Phase C) — MED.** `os.replace` then `COMMIT`. If replace succeeds and `_append`/crash fails, the artifact is published with no `COMMIT`. Architecture: rename is an optimization, ledger is authority — this order inverts that for the resource bytes. Replace/`OSError` is also untyped (not `BAD_STAGE`/`LockError`).

**`Arbiter.fenced_commit` (Phase A `expected_inputs`) — MED.** Whole-file SHA-256 runs **while the ledger mutex is held**, which is the liveness hole four-phase was built to close, just on hash I/O instead of the callback. Unreadable input is `NO_LEASE` (wrong kind). Kernel `protected_write` does not pass `expected_inputs` today.

**`Arbiter._os_lock` (msvcrt) — MED.** Polls forever. Windows `EACCES` is both contention and real access-denied. A read-only/unusable sidecar never becomes a typed refusal.

**`fcntl.flock` path — MED (POSIX/CI only).** `flock` is process-scoped; two threads in one process can both believe they hold `LOCK_EX`. Live COSMOS is Windows + `msvcrt` (same-process handles conflict). Tests cover the FakeMsvcrt thread race, not real flock threads.

**`Arbiter.renew` — LOW/MED (composition).** Implemented and unit-tested; kernel/service never heartbeat-renew. Default TTL is 90 minutes. Fine for short `protected_write`; a long holder dies by expiry with no renew path in Core.

**`release` — LOW.** Does not `_expire_if_due`. An overdue-but-not-yet-EXPIRE’d lease is `RELEASE` rather than `EXPIRE`; the next acquire is `GRANT` not `TAKEOVER`.

**`_accepts_token` — LOW.** Any positional parameter → called with the token. Inspect failure → `True`. Wrong arity becomes untyped `TypeError`.

**`status` / `renew` return live `Lease` objects — LOW.** Not frozen; caller mutation is visible until the next reprime.

**`ttl or self._ttl` — LOW.** `ttl=0` is treated as default.

---

## (4) UNKNOWN (not guessed)

- Whether 6b was supposed to fold this JSONL into the hash-chained authority ledger or keep a second file.
- Whether `os.replace` across volumes on this Windows Python is `EXDEV` or a copy; `StagedArtifact` requires same volume, nothing checks it.
- Whether any HTTP/API path will accept a client-supplied token (tokens are sequential ints, not secrets). Kernel `protected_write` acquires then commits itself; I did not find a service route that takes a raw token.
- Whether a production sidecar can sit on a lock-hostile volume (SMB/AV). `flock`/`msvcrt` semantics there are unmeasured in this review.
- Wave3 B6/M4 not re-executed in this pass.

---

## Verdict

**WATCH**

**Top risk:** HMAC on `leases.jsonl` authenticates *appends*, not *history shape*. Truncating the tail rewinds a live lease without `FORGED_EVENT`, and `status`/`__init__` can disagree with disk because they are not in the lock+reprime discipline the mutating API now uses.

The measured holes this module claims to have closed (xproc double-grant, lock-across-callback, forged GRANT, dying-holder stale install) are closed in code and in `test_cosmos_lock`. That is why this is not **FIX-NOW**.
