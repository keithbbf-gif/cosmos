## (A) JSON findings

```json
[
  {
    "id": "API-01",
    "topic": "bts_paths sentinel and MAX_PATH claims",
    "verdict": "Characterization is unsupported: attached bts_paths.py does not perform a sentinel-content assertion and does not apply the Windows \\\\?\\ prefix to filesystem walks.",
    "evidence": "INCUMBENT §1 says COSMOS must include both behaviors, but bts_paths.py only uses os.path.isdir during _resolve/_resolve_ai and role functions only join strings. No sentinel check or extended-length-path helper exists.",
    "confidence": "high"
  },
  {
    "id": "API-02",
    "topic": "bts_paths CLI and undocumented argument behavior",
    "verdict": "The CLI refuses unknown flag-shaped arguments only; arbitrary positional arguments are silently accepted and its advertised --check/--selftest modes have no distinct implementation.",
    "evidence": "bts_paths.py __main__ computes _bad only for arguments beginning with '-', then always prints the report and exits 0. It never branches on --check or --selftest.",
    "confidence": "high"
  },
  {
    "id": "API-03",
    "topic": "bts_paths root selection ambiguity",
    "verdict": "On Linux, the resolver selects sorted(glob.glob(...))[0], not a uniquely identified mount. Multiple matching session mounts can therefore select an arbitrary lexicographically first tree.",
    "evidence": "bts_paths.py _resolve() and _resolve_ai() use hits = sorted(glob.glob(pat)); if hits: return hits[0]. INCUMBENT §1 describes sandbox globbing but does not identify the multiple-match selection behavior.",
    "confidence": "high"
  },
  {
    "id": "API-04",
    "topic": "tree_lock ROLD resolution",
    "verdict": "The characterization is wrong about the attached source: tree_lock.py still derives ROLD from MESH.parent and does not call bts_paths.rold().",
    "evidence": "tree_lock.py sets MESH = pathlib.Path(__file__).resolve().parent and ROLD = MESH.parent / 'ROLD'. bts_paths is later used only to construct LOCK. This contradicts INCUMBENT §2's statement that ROLD now resolves via bts_paths.rold().",
    "confidence": "high"
  },
  {
    "id": "API-05",
    "topic": "tree_lock is race-prone beyond being cooperative",
    "verdict": "The incumbent claim operation is not even an atomic cooperative claim: two claimants can both read free/stale state and overwrite each other's JSON claim.",
    "evidence": "tree_lock.py claim() calls _read(), evaluates holder state, then _write() with ordinary open(..., 'w'). There is no OS lock, exclusive create, compare-and-swap, or atomic rename protocol. INCUMBENT §2 calls it cooperative but omits this read-check-write race.",
    "confidence": "high"
  },
  {
    "id": "API-06",
    "topic": "tree_lock four-state semantics",
    "verdict": "The stated four-state distinction is not implemented by _sha: absent and unreadable both become None; the verifier also ignores files that were absent at claim time and later appear.",
    "evidence": "tree_lock.py _sha catches every Exception and returns None. verify() only marks unreadable where old hash h is non-None and new hash n is None, and only compares keys in the original manifest. INCUMBENT §2 acknowledges the collapse for checker behavior, while Cross-cutting behavior §4 says the states are never collapsed.",
    "confidence": "high"
  },
  {
    "id": "API-07",
    "topic": "tree_lock release and stale-takeover auditability",
    "verdict": "A stale takeover is announced only to stdout, not durably recorded, and a FUSE fallback release replaces the claim with {} rather than a release event.",
    "evidence": "tree_lock.py claim() prints 'taking over a STALE claim' then overwrites LOCK. release() catches unlink failure and calls _write({}). There is no append-only takeover/release audit record. INCUMBENT §2 says takeover is 'WITH ANNOUNCEMENT' but does not distinguish ephemeral console output from durable evidence.",
    "confidence": "high"
  },
  {
    "id": "API-08",
    "topic": "bts_phone write semantics",
    "verdict": "The attached bts_phone.py does not send or write a mailbox message; it only probes and reads its fixed inbound file.",
    "evidence": "bts_phone.py defines OUTBOX but has no send/write function and no write call targeting OUTBOX. Its CLI has only --check, --read, and --selftest. INCUMBENT §3 describes which party writes each letter, but that behavior is not implemented in this source.",
    "confidence": "high"
  },
  {
    "id": "API-09",
    "topic": "bts_phone staleness and file-type behavior",
    "verdict": "The phone reports timestamp and size for an existing regular inbound file but makes no staleness judgment; an inbox path that is a directory is reported identically to a missing inbox.",
    "evidence": "bts_phone.py check() uses os.path.isfile(INBOX), then prints st_mtime/st_size only when true. It contains no age threshold, open-question state, or distinct directory/unreadable outcome. INCUMBENT §3 accurately says it does not alarm on staleness but omits the file-type collapse.",
    "confidence": "high"
  },
  {
    "id": "API-10",
    "topic": "bts_runner resolver and cross-platform safety",
    "verdict": "The runner remains hard-coded to V:\\Ai\\_queue and imports neither bts_paths nor another resolver; its claimed native-only safety is contingent on launch environment rather than enforced before filesystem access.",
    "evidence": "bts_runner.py defines QUEUE_BASE = Path(r'V:\\Ai\\_queue') and has no bts_paths import. _dirs(), beat(), and queue operations can run before any command requiring py is launched. INCUMBENT §4 labels the literal judged-benign but this is not a portable or fail-loud addressing implementation.",
    "confidence": "high"
  },
  {
    "id": "API-11",
    "topic": "bts_runner overlapping-tick failure mode",
    "verdict": "Claim-by-rename prevents two successful same-name claims on a normal single filesystem, but an expected losing rename is uncaught and can abort the tick; collision naming is also check-then-rename.",
    "evidence": "bts_runner.py tick() obtains a pre-claim jobs list then calls _claim(job) without exception handling. _claim() tests dst.exists(), constructs a timestamp suffix if needed, then calls job.rename(dst), with no retry or loser handling. INCUMBENT §4 states the overlap property but omits operational handling of the loser.",
    "confidence": "high"
  },
  {
    "id": "API-12",
    "topic": "bts_runner execution and artifact integrity gaps",
    "verdict": "The runner processes every currently listed runnable job serially in one tick, and its heartbeat and log artifacts are overwrite/truncate writes rather than append-only or torn-state-resistant artifacts.",
    "evidence": "bts_runner.py tick() loops 'for job in jobs' without a one-job break. beat() uses HEARTBEAT.write_text(...), and log.write_text opens/truncates the initial log. INCUMBENT §4 correctly describes serial per-lane execution and append-only ledger, but does not distinguish these other mutable artifacts from the ledger.",
    "confidence": "high"
  }
]
```

## (B) Prose reasoning

### Input A — critique and extension

The packet’s broad diagnosis is useful, but several assertions describe desired or incident-derived behavior rather than behavior present in the attached source.

#### `bts_paths.py`

The important undocumented behavior is that Linux resolution is not merely “glob on sandbox side”; it chooses the lexicographically first matching mount if multiple session paths match. That is a silent ambiguity: `sorted(glob.glob(...))[0]` is not an identity assertion. A COSMOS port that simply preserves globbing could select the wrong mounted tree when stale or concurrent mounts coexist.  
**Source:** `bts_paths.py`, `_resolve()` and `_resolve_ai()`.

The characterization’s sentinel-content and MAX_PATH requirements are not code exhibited by this file. There is no sentinel check after `isdir()`, and no extended Windows-path conversion for walks. The prior incident supports adding them to COSMOS, but it does not establish that the incumbent code currently has them.  
**Source:** `INCUMBENT §1`; `bts_paths.py`.

Other silent-loss hazards:

- Environment overrides are lower precedence than platform locations. This is intentional but unusual; a test override cannot shadow a healthy mounted tree. Preserve or explicitly change this policy.  
  **Source:** `bts_paths.py`, `_resolve()`, `_resolve_ai()`.
- Resolution is import-time and therefore imports have machine-state side effects. A port that turns this into lazy resolution changes startup failure behavior.  
  **Source:** `bts_paths.py`, `ROOT, HOW = _resolve()` and `AIROOT, AIHOW = _resolve_ai()`.
- Role methods return strings, not `Path` objects, and do no existence, containment, normalization, or identity validation. A port that “improves” types needs compatibility decisions at each caller.
- The command-line interface only refuses unknown options beginning with `-`; positional garbage is accepted. Also `--check` and `--selftest` are recognized but do not trigger dedicated logic.  
  **Source:** `bts_paths.py`, `__main__`.

#### `tree_lock.py`

The largest source contradiction is `ROLD`. The characterization says it was repaired to use `bts_paths.rold()`. The attached source still uses:

```python
MESH = pathlib.Path(__file__).resolve().parent
ROLD = MESH.parent / "ROLD"
```

That is exactly parent-walking and remains coupled to the deployment location of `tree_lock.py`.  
**Source:** `tree_lock.py`, top-level assignments; contradiction with `INCUMBENT §2`.

The lock is cooperative, but it is also a non-atomic read/check/write protocol. Two processes can both read `{}` or stale state and both `_write()` their claim. Therefore it cannot reliably report who held the pen even among cooperative claimants under overlap.  
**Source:** `tree_lock.py`, `claim()`, `_read()`, `_write()`.

The characterization/cross-cutting four-state claim overstates the implementation. `_sha()` catches all exceptions and returns `None`, so it merges absent, permissions failure, I/O failure, and parse-unrelated file-read failure. `verify()` only detects readable-at-claim becoming `None`, and does not detect absent-at-claim becoming present. This may have been a deliberate anti-noise tradeoff, but it is not four-state preservation.  
**Source:** `tree_lock.py`, `_sha()`, `manifest()`, `verify()`; `INCUMBENT §2`, Cross-cutting §4.

Additional undocumented port-sensitive behavior:

- `KNOWN_WRITERS` is an embedded, closed authorization list. The comparison uppercases input, but no writer identity is cryptographically bound to a process or artifact.  
  **Source:** `tree_lock.py`, `KNOWN_WRITERS`, `claim()`.
- Claim-time timestamps are naive local timestamps (`datetime.now().isoformat()`), unlike the runner’s later corrected aware timestamps. A cross-timezone reader can misjudge staleness.  
  **Source:** `tree_lock.py`, `_now()`, `age_minutes()`.
- A malformed `claimed` timestamp is treated as extremely stale, not torn/refused. Thus malformed whole-lock JSON refuses, but malformed fields within valid JSON enable takeover.  
  **Source:** `tree_lock.py`, `age_minutes()`.
- Stale takeover and FUSE fallback release leave no durable append-only history. Console output is not an audit artifact.  
  **Source:** `tree_lock.py`, `claim()`, `release()`.

#### `bts_phone.py`

The packet describes a bilateral mail convention, but this module does not implement sending. It defines an `OUTBOX`, yet it has no function or CLI path that writes it. It only checks/reads a fixed inbound letter. A COSMOS implementation should not infer a proven atomic send protocol from this source.  
**Source:** `bts_phone.py`; `INCUMBENT §3`.

Behavior a port can silently lose:

- The import-time `AIROOT` assertion is explicitly redundant with `bts_paths`, and that redundancy is a deliberate defense against cwd writes.  
  **Source:** `bts_phone.py`, `AIROOT` assertion.
- `--check` is liveness only in the narrow sense “inbound regular file exists.” A directory, inaccessible target, absent target, and some other file-system errors effectively collapse to failure/missing from this interface.  
  **Source:** `bts_phone.py`, `check()`.
- `read()` probes and then opens separately, allowing a TOCTOU failure if the inbound file changes/disappears between `check()` and `open()`.  
  **Source:** `bts_phone.py`, `read()`.
- Staleness is displayed but not classified. There is neither an age threshold nor knowledge of whether a question remains open.  
  **Source:** `bts_phone.py`, `check()`.
- Unknown option-like flags refuse, but arbitrary positional arguments are tolerated; mutually conflicting known modes are resolved by branch order.  
  **Source:** `bts_phone.py`, `__main__`.

#### `bts_runner.py`

The runner’s queue claim is stronger than `tree_lock` on a normal shared single volume, but it has a missing loser path. Two overlapping ticks can list the same pending job; one rename succeeds and the other can get an unhandled `OSError` from `_claim()`, aborting its tick. The system avoids double execution, but not clean concurrency behavior.  
**Source:** `bts_runner.py`, `tick()`, `_claim()`.

Important behavior not emphasized in the characterization:

- One tick executes **all** jobs present in its initial sorted list serially, not one job then return. This changes scheduler fairness and heartbeat cadence under a long backlog.  
  **Source:** `bts_runner.py`, `tick()`.
- The `running` claim, final move, heartbeat, and initial log are mutable overwrite/rename artifacts. Only the ledger is append-only/fsynced. A port must not generalize “the runner uses append-only artifacts” beyond the ledger.  
  **Source:** `bts_runner.py`, `_claim()`, `beat()`, log `write_text()`, `_append()`.
- A failed final move leaves the job in `running` but still records an `end` ledger event and prints a terminal verdict. That can produce contradictory state: ledger says done/failed while the executable remains stale-running.  
  **Source:** `bts_runner.py`, final `claimed.rename(target)` exception branch.
- Log names use second-resolution timestamps. Same stem in the same second can collide and overwrite the initial log.  
  **Source:** `bts_runner.py`, `log = LOGS / ... time.strftime(...)`.
- Stale jobs are reported on every tick and appended repeatedly; there is no once-only stale transition/deduplication.  
  **Source:** `bts_runner.py`, `report_stale()`, `tick()`.
- `--lanes` discovers a lane only if either its heartbeat exists or its directory exists under `_lanes`; it cannot discover an intended-but-never-created configured worker. This is reasonable filesystem discovery, but it is not complete scheduler inventory.  
  **Source:** `bts_runner.py`, `lanes_status()`.

Finally, the incumbent runner directly hard-codes `V:\Ai\_queue` and does not use `bts_paths`. The “native-only” justification is operational convention, not a pre-access platform guard. `beat()` and directory creation can execute before a command fails due to absent `py`.  
**Source:** `bts_runner.py`, `QUEUE_BASE`, `tick()`, `_dirs()`, `beat()`.

---

### Input B.1 — enforcing lock design

Use a **single native Windows lock-arbiter service** as the authority, with fencing tokens and a durable append-only event ledger. Do not make OS file locking alone the cross-universe protocol.

#### Why not OS-level file locking alone

Windows file locks are not a sufficient shared protocol for native Windows plus a Linux sandbox/FUSE mount:

- FUSE/WSL/Samba-like bridges may not preserve Windows locking semantics consistently.
- A process death may release an OS handle, but a remote bridge can have delayed/disconnected semantics.
- Locking a file does not create a durable ownership/audit record or fence an old holder after lease expiry.
- The stated unlink refusal means lock-state cleanup must not depend on deletion.

#### Minimal concrete design

1. **Arbiter location and transport**
   - Run `cosmos-lockd.exe` as a Windows service on the host that owns the COSMOS volume.
   - Expose a local authenticated named pipe for Windows workers and an HTTPS or mutually authenticated loopback/host endpoint reachable from Linux sandbox workers.
   - The arbiter is the only process permitted to create lease records in the control area.

2. **Identity**
   - Each worker has immutable `worker_id`, `instance_id` (new UUID per process start), and credential.
   - Every request carries all three. Do not use a closed hard-coded writer list.

3. **Lease acquisition**
   - `Acquire(resource="tree-write", worker, instance, purpose, expected_generation)` is serialized by the arbiter.
   - If free/expired, arbiter increments a monotonic `fencing_token`, records `GRANTED` in an append-only JSONL/event store, and returns `{lease_id, fencing_token, expires_at_utc}`.
   - Lease record is overwritten only by the arbiter; historical evidence remains append-only.

4. **Fencing enforcement**
   - Every COSMOS mutation-capable operation must present the currently held fencing token to a local write gateway/library.
   - The gateway rejects a request with a token lower than the most recently granted token.
   - For operations performed directly against a filesystem where the OS cannot validate a token, enforce policy architecturally: workers do not receive direct write capability to protected live-tree paths. They submit mutation bundles to the Windows gateway/arbiter, which validates token then applies them.
   - This is the distinction between a lease that merely reports ownership and a fence that prevents an expired writer from committing afterward.

5. **Death without release**
   - No release is required for eventual recovery. Heartbeats renew the lease; absence causes expiry.
   - Expiry produces a durable `EXPIRED` event. A subsequent grant produces `TAKEOVER` referring to prior lease and reason.
   - A worker recovering after expiry cannot renew; it receives a stale-token rejection and must re-read state.

6. **FUSE refuses unlink**
   - Never use unlink as correctness or release semantics.
   - State transitions are append-only events plus arbiter-owned current-state storage. A retained lease file is evidence, not authority.
   - If a filesystem mirror is wanted, write immutable lease-event files with unique token names rather than delete/mutate a single lock file.

7. **Two universes on the same tree**
   - Native Windows and Linux sandbox never independently “claim” a filesystem lock file.
   - Both contact the same arbiter and write only through the same fenced gateway for protected paths.
   - If Linux cannot contact the arbiter, it is refused from protected writes rather than given an offline fallback.

8. **Torn state**
   - Clients treat unreadable local mirror state as diagnostic only and query arbiter; they never infer free.
   - The arbiter’s durable event store must use checksummed framed records or a transactional local store. On corruption, fail closed for new protected writes and alert.

This supplies enforcement, recovery, cross-universe consistency, fencing, and durable evidence.

---

### Input B.2 — COSMOS scheduler: concurrency and priority

Use immutable job manifests plus per-worker claim records; do not use a single mutable queue file.

#### Job submission

A submitter creates an immutable job directory:

```text
jobs/
  20260823T120000Z_<job_uuid>/
    manifest.json
    payload/
    submitted.json
```

`manifest.json` includes:

- `job_id` UUID
- `priority`: bounded integer or named class such as `critical`, `high`, `normal`, `low`
- submitter `worker_id`, `instance_id`, and timestamp with UTC offset
- immutable payload hashes
- requested resource class: `read-only`, `live-tree-write`, etc.
- timeout
- retry policy: default `never`
- command type, not arbitrary unreviewed shell text where avoidable
- dependencies, if any

Submission is complete only after a completion marker or manifest hash is read back and verified. If the underlying shared filesystem cannot safely rename, use write-once job directories and make the scheduler accept only valid complete manifests.

#### Scheduling and claim

Each scheduler worker:

1. Scans valid completed manifests.
2. Sorts by `(priority descending, submitted_at ascending, job_id)`.
3. Attempts an atomic claim through the scheduler coordinator or job-specific exclusive creation:
   ```text
   claims/<job_id>/<worker_id>_<instance_id>_<claim_uuid>.json
   ```
4. The coordinator decides one winner and emits an immutable assignment event. A losing worker records nothing as successful and moves to another job.

For the minimal reliable design, the same Windows arbiter service should also serialize assignment decisions. This avoids assuming cross-platform filesystem exclusive-create/rename semantics.

#### Concurrency model

- Concurrency is explicit scheduler configuration: `max_workers`, resource-class limits, and optional per-project limits.
- A job is independently runnable; lanes are not the unit of isolation.
- `live-tree-write` jobs acquire the fenced tree-write lease before execution. Read-only jobs can run concurrently without it.
- A worker runs at most one job at a time unless it advertises bounded local parallelism.
- Priority belongs to the immutable job manifest, not a filename or queue ordering accident.
- Add starvation protection: aging can raise effective priority after a defined wait, and this transition must be observable.

#### Artifacts

Every artifact path includes `job_id`, `attempt_id`, `worker_id`, and `instance_id`. No `runner_heartbeat.json` shared among workers.

Examples:

```text
workers/<worker_id>/<instance_id>/heartbeat.json
jobs/<job_id>/attempts/<attempt_id>/start.json
jobs/<job_id>/attempts/<attempt_id>/log.jsonl
jobs/<job_id>/attempts/<attempt_id>/result.json
events/scheduler-YYYYMMDD.jsonl
```

For FUSE-exposed data, use append-only event/log files and unique object names, not overwrite/rename as the correctness primitive.

#### Preserve incumbent properties

- **Claim-by-rename equivalent:** arbiter-issued atomic assignment/claim.
- **Three worded outcomes:** `CLEAN`, `FINDINGS`, `BROKE`; retain numeric exit code separately.
- **Log-first:** durable `start` event and initial log record before child execution.
- **Report-never-retry:** timeouts and abandoned attempts become `BROKE`/`STALE` reports; no automatic re-execution unless a new explicitly approved attempt is submitted.
- **Helper convention:** helper files cannot be jobs because jobs are manifests with typed payloads. If compatibility queue files remain temporarily, reject `_`-prefixed files and visibly report them.
- **Per-worker heartbeat:** per immutable worker-instance path, discovery by directory scan/registry.
- **UTF-8:** mandate UTF-8 for child environment, capture decode, JSON, and logs.
- **Timezone-aware timestamps:** require UTC `Z` or RFC 3339 with offset plus epoch milliseconds.

---

### Input B.3 — one-root resolver successor

Provide a role-based `cosmos_paths` object initialized from a single explicit root identity.

#### Resolution rule

1. Resolve exactly one candidate root from:
   - explicit CLI/config value, then
   - `COSMOS_ROOT`, then
   - platform-specific mounted locations only if no explicit value exists.
2. Do **not** silently fall back across candidates.
3. Canonicalize/normalize the candidate.
4. Assert root identity before returning it:
   - root contains `.cosmos-root.json`;
   - file contains a fixed `system: "COSMOS"` value;
   - includes stable `tree_id` and schema version;
   - optional signature/hash if threat model requires it.
5. If sentinel missing, unreadable, malformed, wrong tree ID, or ambiguous multiple mount candidates: raise with all attempted paths and observed states.

#### Roles

Roles are centrally declared, e.g.:

```python
paths.root()
paths.mesh()
paths.queue()
paths.board()
paths.secrets()
paths.archive()
paths.working()
paths.control()
```

Roles must be rooted under one `COSMOS_ROOT`; no role can use `parent`, `__file__`, cwd, or another root. `secrets` should remain location-separated from publishable content, such as `COSMOS_ROOT/.secrets` while published data is `COSMOS_ROOT/published/`; publish should select an allowlisted subtree, not exclude secrets by blocklist.

#### Cold-machine portability

Drive letters are configuration/mount implementation details. On a peer’s cold machine, set `COSMOS_ROOT` or supply signed bootstrap configuration pointing to its mount. The sentinel validates that mount is COSMOS rather than merely an existing directory.

#### MAX_PATH-safe operations

Use `pathlib` for logical construction, plus a Windows filesystem adapter for all traversal/open/stat operations:

- normalize to absolute paths;
- use `\\?\` extended-length form for local Windows paths;
- use `\\?\UNC\server\share\...` for UNC paths;
- never prepend blindly to already extended paths;
- reject paths escaping the root after normalization;
- test long paths through every walk, glob, stat, read, write, and subprocess working-directory path.

Do not apply Windows extended syntax in Linux paths. This should be a platform adapter, not scattered string prefixes.

---

### Input B.4 — mailbox at N>2

Replace fixed pairwise letters with an append-only, addressed message system.

#### Mailbox layout

```text
mail/
  workers/
    <worker_id>/
      <instance_id>/
        identity.json
        heartbeat.json
        inbox/
          <message_id>.json
        outbox/
          <message_id>.json
  messages/
    <message_id>.json
  receipts/
    <message_id>/
      delivered-<worker_id>-<instance_id>.json
      read-<worker_id>-<instance_id>.json
```

A message is immutable and contains:

- `message_id`
- sender worker/instance identity
- one or more recipient worker IDs or a broadcast topic
- timestamp with offset and epoch
- subject/correlation ID
- payload hash and optional content reference
- TTL/staleness deadline
- `requires_ack` / `requires_answer`

The sender creates a unique message object and reads it back by hash. Delivery is represented by immutable recipient references or receipt files; never overwrite `OUTBOX.md`.

#### Missing versus empty distinction

Maintain explicit states:

- **mailbox missing:** recipient identity/inbox path absent or unresolved — routing/liveness failure, non-zero.
- **mailbox exists but empty:** valid mailbox with no unread messages — normal no-message state.
- **mailbox unreadable/torn:** refusal/infrastructure failure, distinct from empty.
- **mailbox present but stale:** last heartbeat/message is older than policy threshold — degraded/dead conversation signal.
- **message unacknowledged past deadline:** alert based on message contract, not merely file age.

This preserves the incumbent’s “missing is not no news” rule while making it meaningful at N>2.

#### Probe-not-assume

`cosmos-mail probe <worker>` must report identity validity, heartbeat age, inbox existence, unreadable state, unread count, oldest unacknowledged required-ack message, and last successful read receipt. A send command returns success only after the immutable message is read back and routing record is verified; delivery/reading are separate facts.

---

### Input B.5 — additional port hazards

1. **Semantic drift between exit status and scheduler outcome.** Preserve `rc=2` as `FINDINGS`, but define whether other tools use 1, 2, and 3 differently. A generic “nonzero failed” wrapper would reintroduce PLM-44.  
   **Source:** `INCUMBENT §4`; `bts_runner.py`.

2. **Valid JSON with invalid fields.** Current lock refusal protects malformed JSON but not malformed timestamps/manifests. COSMOS validation must schema-check required fields, types, identities, and clocks; malformed valid JSON must fail closed.  
   **Source:** `tree_lock.py`, `_read()`, `age_minutes()`.

3. **Artifact completion protocol.** Append-only is not alone sufficient: readers need a way to distinguish partial append/write from complete record. Use framed/checksummed JSONL records or write-once immutable objects with completion/hash markers.

4. **Clock skew.** Lease expiry, heartbeat age, priorities, and staleness all become unsafe if worker clocks differ. The arbiter’s clock should define lease expiry; worker timestamps are evidence, not authority.

5. **Case-insensitive collisions.** Windows case-insensitivity can collapse distinct worker IDs, lane names, artifact names, or job payload files. Canonicalize identities and reject case-colliding names.

6. **Unicode normalization and encoding.** UTF-8 pipe handling is necessary but not sufficient. Normalize artifact naming and preserve raw byte hashes for payload integrity. Avoid using visually confusable identities.

7. **Subprocess containment.** A timed-out wrapper may not terminate spawned descendants. COSMOS needs process-group/job-object containment on Windows and a recorded kill/escalation outcome.

8. **Scheduler crash between state transitions.** Crash after assignment but before log-first record, after process completion but before result, or after result before finalization must be modeled as recoverable explicit states, never inferred as “retry safely.”

9. **Priority abuse and starvation.** If submitters set priority, authorization and quotas are needed. Otherwise every submitter selects critical and priority loses meaning.

10. **Immutable payload integrity.** Claiming a job does not prove its command/payload was unchanged after inspection. Hash manifests and execute only the verified payload referenced by the claimed immutable job object.

11. **Self-test isolation.** Incumbent self-tests touch shared/default queue structures and rely on cleanup. COSMOS self-tests should use isolated temporary roots and must prove negative controls without racing production workers.

12. **Observability must not become authority.** Heartbeats, dashboards, and mirrored lock files are diagnostic artifacts. Only the arbiter/transactional state should decide ownership and assignment.

---

### Input C — behavioral cards

Skipped. The source appendix contains only the four deep modules; no additional module source files are included.