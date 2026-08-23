An honest gap outranks a confident invention. Disagreement is the value.

**Family:** CCF5
**Independent Reviewer:** A-5
**Date:** 2026-08-23

### PART A — JSON FINDINGS

```json
[
  {
    "id": "CCF5-01",
    "topic": "Characterization: bts_paths.py",
    "verdict": "Characterization missed that the module itself contains the evidence for why a content assertion is necessary: the `mesh()` function was pointing at an empty but extant directory, a defect class the `isdir()` checks it recommends would not have caught. The prose points to the solution without naming the code that proves its necessity.",
    "evidence": "INCUMBENT_BEHAVIOR_4_SPIKE_MODULES.md, Section 1; bts_paths.py, `mesh()` function docstring and fix comment.",
    "confidence": "high"
  },
  {
    "id": "CCF5-02",
    "topic": "Characterization: bts_runner.py",
    "verdict": "Characterization is wrong about a key detail. It states the `RUNNABLE` dict was deleted for drifting from `_cmd_for()`. The code shows the more critical reason was that it was also the *sole predicate for runnable files* in `tick()` and `status()`, so deleting it blind would have broken the runner. The characterization understates the dependency and the risk.",
    "evidence": "bts_runner.py, comment block above DEFAULT_TIMEOUT titled '`RUNNABLE` DELETED 2026-08-22'. The comment explicitly states that `tick()` and `status()` used the dict as their filter.",
    "confidence": "high"
  },
  {
    "id": "CCF5-03",
    "topic": "Undocumented Behavior: bts_paths.py",
    "verdict": "A spec-driven port would lose the hard-won rule that path-rewriting migration sweeps must skip prose. The file's own docstring was corrupted by the migration tooling it exists to enable, turning true history into a false record. This meta-level behavior (the file as a victim of its own purpose) is undocumented in the 'WHAT IT ACTUALLY DOES' section.",
    "evidence": "bts_paths.py, main docstring `⚠⚠ 2026-07-17` warning.",
    "confidence": "high"
  },
  {
    "id": "CCF5-04",
    "topic": "Undocumented Behavior: tree_lock.py",
    "verdict": "A spec-driven port would lose the reason for the `KNOWN_WRITERS` list. The code presents it as a closed set, but the behavior docs do not mention its role as a gatekeeper against typos or unauthorized agents attempting to claim the lock. The code refuses an unknown writer with exit code 2; this is an undocumented enforcement behavior.",
    "evidence": "tree_lock.py, `claim()` function logic and `KNOWN_WRITERS` set definition.",
    "confidence": "med"
  },
  {
    "id": "CCF5-05",
    "topic": "Undocumented Behavior: bts_phone.py",
    "verdict": "A spec-driven port would lose the distinction between a dead phone and a silent one. The code's `--check` function returns a non-zero exit code on a missing inbound file, a critical behavior enabling automation to detect a broken channel. The characterization mentions this but frames it as a probe; the undocumented behavior is the non-zero exit code as a machine-readable signal of channel failure.",
    "evidence": "bts_phone.py, `check()` and `selftest()` functions. The selftest explicitly includes a negative control to assert that a missing inbox returns non-zero.",
    "confidence": "high"
  },
  {
    "id": "CCF5-06",
    "topic": "Undocumented Behavior: bts_runner.py",
    "verdict": "A spec-driven port would silently lose the rule for naming lanes. The `--lane` argument is validated by a regex (`[a-z0-9_-]{1,16}`) to prevent path traversal or case-collision bugs. This is a security and stability feature tied to the filesystem that is not documented in the behavioral characterization, only in the code's `main()` function.",
    "evidence": "bts_runner.py, `main()` function, argument parsing section.",
    "confidence": "high"
  },
  {
    "id": "CCF5-07",
    "topic": "Design Question 1: Enforcing Lock",
    "verdict": "Propose OS-level advisory file locks (`fcntl`/`msvcrt.locking`) on a dedicated lock file, combined with a fencing token. A single arbiter process is a single point of failure. Lease files without OS locks are susceptible to race conditions on expiry. This hybrid approach survives process death (OS releases lock), FUSE refusal (lock is on a separate file), and cross-universe writers (if both can see the same lock file and respect the OS API).",
    "evidence": "Design requirement analysis based on tree_lock.py behavior and COSMOS design questions.",
    "confidence": "med"
  },
  {
    "id": "CCF5-08",
    "topic": "Design Question 2: Scheduler Concurrency",
    "verdict": "Minimal design: A central, durable queue (e.g., Redis, SQLite) where each job is a record with `(id, priority, command, status, worker_id)`. Workers query for the highest-priority `QUEUED` job, transactionally update its status to `RUNNING` and set their `worker_id`. Concurrency is the number of worker processes. This preserves claim-by-rename (as transactional update), worded outcomes (in the status field), log-first (worker logs its attempt), report-never-retry (failed jobs are marked `FAILED`), and helper convention (helpers are not jobs in the queue).",
    "evidence": "Design requirement analysis based on bts_runner.py behavior and COSMOS design questions.",
    "confidence": "high"
  },
  {
    "id": "CCF5-09",
    "topic": "Design Question 3: Resolver for One Root",
    "verdict": "The resolver should be a class, not a module with import-time effects. `resolver = CosmosPaths(drive_letter='E')`. It reads a sentinel file (e.g., `V:\A\Ai\COSMOS\.cosmos_root`) at instantiation to verify identity. The content of this sentinel could be a simple JSON `{\"schema_version\": 1}`. Role methods (`resolver.secrets()`) build `\\?\`-prefixed paths. MAX_PATH-safe walks are properties of the class. Portability is achieved by passing the drive letter at instantiation. Failure to resolve raises an exception.",
    "evidence": "Design requirement analysis based on bts_paths.py limitations and COSMOS design questions.",
    "confidence": "high"
  },
  {
    "id": "CCF5-10",
    "topic": "Design Question 4: IPC at N>2",
    "verdict": "Generalize mailboxes to a directory structure: `.../mailboxes/<worker_id>/in/`. A sender writes a uniquely named file (e.g., `<uuid>.json`) into the recipient's `in` directory. The payload includes sender identity and creation time. A worker probes its own `in` directory. Missing-vs-empty is `isdir()` vs `listdir()`. Staleness is judged by file `mtime` or payload timestamp. This avoids file locks and last-writer-wins.",
    "evidence": "Design requirement analysis based on bts_phone.py limitations and COSMOS design questions.",
    "confidence": "high"
  },
  {
    "id": "CCF5-11",
    "topic": "Design Question 5: What Else Breaks?",
    "verdict": "The implicit dependency on atomic renames on a single volume will break. The runner's 'claim-by-rename' and the ledger's 'append-over-rename' both rely on all queue directories (`pending`, `running`, `done`, `logs`) residing on the same filesystem volume. If COSMOS architecture places, for instance, logs on a separate storage system from the queue, these atomic operations will fail or become non-atomic copies, introducing race conditions the incumbent design successfully prevented.",
    "evidence": "bts_runner.py, design notes on 'claim-by-rename' being atomic on one volume.",
    "confidence": "high"
  }
]
```

### PART B — PROSE REASONING

This return is from AI family CCF5. The findings are based on the provided research packet.

#### A. Critique and Extension of Incumbent Characterization

The provided characterization is high-quality and captures most of the expensive, "scar-tissue" behaviors of the incumbent system. However, it misses a few key connections and understates specific risks.

-   **(CCF5-01) What the characterization missed:** The `bts_paths.py` characterization correctly identifies the need for a "sentinel-content check." What it omits is that the strongest evidence for this need is in the `bts_paths.py` source itself. The `mesh()` function was fixed on 2026-08-21 because it resolved to `ROOT/Ai/BTS_MESH`, a directory that existed but was empty of tools. This proves that an `os.path.isdir()` check, which the characterization seems to implicitly trust, is insufficient. The characterization identifies the solution but doesn't connect it to the most pointed example of the problem in the provided code.

-   **(CCF5-02) What in the characterization is wrong:** The `bts_runner.py` characterization states that the `RUNNABLE` dictionary was deleted for "drifting" from `_cmd_for()`. This is true but incomplete to the point of being misleading. The source comment (`RUNNABLE DELETED 2026-08-22`) reveals a more critical issue: `tick()` and `status()` used `RUNNABLE` as their exclusive filter for what constituted a job. Simply deleting the dictionary would have caused the runner to stop seeing any jobs at all. The actual change was to replace this second source of truth with a single predicate, `_is_runnable()`. The characterization frames this as cleaning up drift; the code shows it was fixing a structural dependency that made the runner fragile.

-   **Undocumented behaviors a spec-port would lose:**
    -   **(CCF5-03) `bts_paths.py`:** The module's primary docstring contains a critical warning: the path migration tool this module was built to enable *corrupted the module's own documentation*, falsifying the historical record. A spec-driven port would copy the functional code but lose this meta-lesson: automated tooling that operates on code and prose together is dangerous. This is a rule about building and maintaining the system, not just using it.
    -   **(CCF5-04) `tree_lock.py`:** The characterization mentions a "closed writer set" but not its undocumented behavior: it acts as a permissions gate. The `claim()` function explicitly refuses unknown writers and exits with a specific code (2). A spec might simply require a `writer` field, but the incumbent *enforces* a known list, preventing a simple typo (`GBQA` vs `GBAQ`) or a rogue agent from acquiring the lock.
    -   **(CCF5-05) `bts_phone.py`:** The characterization notes the "missing ≠ empty" distinction. The key undocumented behavior is *how* this is communicated to automated systems. `check()` returns a non-zero exit code if the inbox file is missing. This transforms a human-readable warning ("THE PHONE IS DEAD") into a machine-readable signal that can halt a workflow. A spec might just call for a printed warning, losing the automated guardrail.
    -   **(CCF5-06) `bts_runner.py`:** The `main()` function contains a regex validation for lane names (`[a-z0-9_-]{1,16}`). This is an undocumented security and stability feature. It prevents the creation of directory paths with malicious (`../`) or problematic characters. A spec-driven port, seeing only the `--lane` flag, might accept any string, reintroducing path injection vulnerabilities that the incumbent code silently prevents.

#### B. Open Design Questions for COSMOS

1.  **Enforcing Lock (CCF5-07):** A single arbiter process is a brittle single point of failure. A pure lease-file/fencing-token system is complex and prone to clock-skew issues and race conditions if a client misbehaves after its lease expires.

    **Proposal:** A hybrid approach. Use an OS-level advisory file lock on a dedicated file (e.g., `V:\A\Ai\COSMOS\.cosmos.lock`). Both native Windows (`msvcrt.locking`) and Linux (`fcntl.flock`) can interact with this. The lock file should contain a JSON object with a "fencing token" (e.g., a UUID or timestamp).
    -   **To acquire:** A writer must (1) obtain an exclusive, non-blocking OS lock on the file, and (2) write a new fencing token and its identity to the file.
    -   **To release:** Remove the OS lock.
    -   **Survival:**
        -   *Session dying:* The OS automatically releases the file lock. The stale token inside is irrelevant because no new writer can acquire the OS lock until it's free.
        -   *FUSE mount refusing unlink:* The lock is a separate, tiny file, not part of a rename operation. Release is an OS-level operation, not a filesystem `unlink`.
        -   *Two writers, different universes:* As long as both universes mount the shared drive such that they can see the *same* lock file, the OS-level locking mechanism on the host (Windows) will arbitrate. The Linux sandbox's `fcntl` call would be passed through the mount to the host OS, which would see the contention.

2.  **Scheduler Concurrency + Priority (CCF5-08):** The incumbent's filesystem-as-queue is elegant but not scalable for priority or true concurrency.

    **Proposal:** Use a transactional, centralized queue, but keep it simple. A single SQLite database file (`V:\A\Ai\COSMOS\scheduler.db`) with a `jobs` table is the minimal durable design.
    -   **Schema:** `jobs (job_id, priority INT, command TEXT, status TEXT, worker_id TEXT, created_at, updated_at)`
    -   **Concurrency:** Is simply the number of worker processes launched. Each worker has a unique `worker_id`.
    -   **Claim-by-rename equivalent:** A worker queries for `SELECT * FROM jobs WHERE status = 'QUEUED' ORDER BY priority DESC, created_at ASC LIMIT 1`. It then attempts an `UPDATE jobs SET status = 'RUNNING', worker_id = ? WHERE job_id = ? AND status = 'QUEUED'`. This atomic update is the new "claim." If the `UPDATE` affects 0 rows, another worker got the job.
    -   **Proven Properties:**
        -   *Three worded outcomes:* The `status` field can hold `QUEUED`, `RUNNING`, `DONE_CLEAN`, `DONE_FINDINGS`, `FAILED`.
        -   *Log-first:* The first thing a worker does after a successful claim is write a log entry.
        -   *Report-never-retry:* A `FAILED` job stays failed unless explicitly re-queued.
        -   *Helper convention:* Helpers are not jobs; they are not submitted to the `jobs` table.
    This design avoids shared mutable files and "last writer wins" scenarios.

3.  **Resolver for One Root (CCF5-09):** The import-time resolution is a hazard. A module's import should not have filesystem side effects.

    **Proposal:** A `CosmosPaths` class.
    -   **Instantiation:** `resolver = CosmosPaths(root_path="V:\\A\\Ai\\COSMOS")`. The root is passed in. For portability to a machine with a different drive letter, `resolver = CosmosPaths(root_path="E:\\COSMOS")`.
    -   **Fail-loud / Sentinel-content assertion:** In its `__init__`, the class immediately checks for the existence and content of a sentinel file, e.g., `os.path.join(root_path, ".cosmos_root")`. It would assert this file contains `{"version": "1.0"}` or similar. If the file is missing, unreadable, or has wrong content, `__init__` raises an exception.
    -   **Role-based API:** Methods like `resolver.artifacts()` or `resolver.secrets()` return path objects.
    -   **MAX_PATH-safe:** All path construction methods internally prepend `\\?\` on Windows. This is an implementation detail of the class, invisible to the caller. `pathlib` handles this well.
    -   **No fallback:** The design has no concept of a fallback. It is given one root and either succeeds or fails.

4.  **IPC at N>2 (CCF5-10):** The two-fixed-files model is brittle.

    **Proposal:** A directory-based mailbox system.
    -   **Structure:** A shared `mailboxes` directory, e.g., `.../ipc/mailboxes/`. Inside, a directory for each potential recipient: `.../mailboxes/<worker_id>/`.
    -   **Sending:** To send a message to `worker-01`, a sender creates a new, uniquely named file (e.g., using `uuid.uuid4()`) inside `.../mailboxes/worker-01/`. The file's content is the message payload (e.g., JSON), which includes sender identity and a timestamp.
    -   **Receiving:** A worker monitors its own mailbox directory.
    -   **Properties:**
        -   *Per-worker identity:* The directory structure enforces this.
        -   *Staleness signaling:* A receiver can check the file's `mtime` or a timestamp within the payload.
        -   *Probe-not-assume:* A worker probes by listing files in its directory (`os.listdir`).
        -   *Missing-vs-empty:* An empty mailbox is an empty list from `listdir`. A missing mailbox is a `FileNotFoundError` when trying to access the directory itself. This distinction is preserved.

5.  **What Else Breaks at the Port? (CCF5-11):** The incumbent design has a hidden dependency on the queue-related directories all residing on the *same filesystem volume*.
    -   **Hazard:** The `bts_runner.py` "claim-by-rename" mechanism is explicitly noted as being atomic *on one volume*. The same is true for moving jobs to `done` or `failed`. An `os.rename()` across different filesystems (e.g., from a C: drive to a V: drive) is not an atomic operation; it's a copy-then-delete, which is subject to race conditions and partial failure states.
    -   **Porting Risk:** If the COSMOS architecture separates storage concerns—for example, by placing queues on a fast local disk but archiving logs to a network share—the atomic rename guarantee is lost. The `claim-by-rename` pattern would need to be replaced with a locking mechanism or the transactional database approach described in (CCF5-08). This cross-cutting assumption of a single volume for all runner artifacts is a major hazard.