# RUNNER POOL — concurrent drain + agent-pool supervisor (SPEC for G46)

**Status:** design ratified by COW from an SSA study, 2026-08-26. **Coder: G46 (primary).**
**Directive (Keith 2026-08-26):** "More than one runner for that box to keep draining faster.
A python script needs to create agents and assign jobs to agents."

**Rule:** PROPOSE, don't touch the tree (P10). Return the full `cosmos_pool.py` content + the diffs
below as a proposal; COW disposes. Additive + fail-closed + keep-her-afloat: the legacy single
runner (`cosmos_run.py`) stays byte-identical and still works with the pool off.

## Root cause — why the drain is serial today (verified)
The parallelism the canon promises lives in the scheduler + ledger; it's throttled by the runner
*process shape*:
1. **Singleton lock on the one runner.** `cosmos_run.loop()` `acquire_lock(cosmos_runner.lock)`
   (`cosmos_run.py:351`, LOCK_NAME `:39`); a second `--loop` refuses `already_running`
   (`:352-366`). Exactly one drain process, by design — the primary serializer.
2. **That process blocks per job.** `Runner.run_one()` runs `run_tree_killed(argv, 1800)` inline
   (`cosmos_runner.py:208`); `drain_loop` is single-threaded (`:322-373`). A 10-min grok job holds
   the only thread — nothing behind it is claimed or run.
3. **Claiming ignores lanes.** `Scheduler.queued()` sorts by `(-priority, submitted, job_id)`, no
   lane term (`cosmos_sched.py:91-95`); `claim_next()` takes `q[0]` globally.

## Load-bearing finding — concurrent claiming is ALREADY exactly-once-safe
Nothing in the claim/ledger path assumes one process:
- `claim_next()` samples `head=ledger.head_seq()`, appends `JOB_CLAIMED` with `expect_head_seq=head`
  (`cosmos_sched.py:107-122`).
- `Ledger.append()` takes the sidecar `.lock` msvcrt byte-range mutex, **re-primes seq/prev_sha from
  disk under the lock**, refuses `STALE_HEAD` if head moved, writes one fsync'd line
  (`cosmos_ledger.py:82-181`).
- Two workers both projecting at head H: first append lands (H→H+1); second re-primes, sees
  H+1≠H, raises `STALE_HEAD` → `SchedError("LOST_CLAIM")` (`cosmos_sched.py:116-121`), which
  `drain_loop` already swallows + retries (`cosmos_runner.py:347-349`). **No double-claim.**
- File-drop ingress is likewise exactly-once: claim-by-atomic-rename `src.replace(claimed)`; the
  loser's `src` is gone → `OSError` → `None` (`cosmos_job_adapter.py:146-149`).

So we do NOT invent a claim protocol. We run N drain processes, remove the *singleton* assumption
(not the *safety* mechanism), give each a **distinct worker-id**, and add **lane fairness**.

### CORRECTNESS LANDMINE (must honor)
`Scheduler.done()` requires completer == claimant: `if st[job_id]["by"] != self.worker: raise
BAD_STATE` (`cosmos_sched.py:138-141`). Today all runners are `worker="cosmos-runner"`
(`cosmos_run.py:35`). **Each pool slot MUST build its Scheduler/Runner with a UNIQUE worker id**
(e.g. `cosmos-runner-slot1`, `-slot2`, `-fast`). Within a process claim→execute→done is
single-threaded, so a process only completes its own claims. This is the single most important
invariant.

## Design — pull pool, supervisor owns lifecycle + lane fairness
**Pull, not push.** The supervisor spawns N generic worker processes; each worker **pull-claims**
via the existing `claim_next()`. (Push would add a second scheduler authority + handoff protocol +
its own exactly-once proof — reintroducing the bottleneck. Pull reuses the measured, fenced claim
path. "Assign jobs to agents" is realized by the atomic claim: each agent assigns *itself* the next
job under the ledger fence.) The supervisor's real value is **lifecycle** (create N, replace crashed,
honor PAUSE, scale) and **lane allocation**.

**Lane fairness = a reserved fast slot.** Allocate:
- **1 reserved "fast" slot** claiming ONLY the short lane (`lanes={"default"}`), so an admin job is
  claimable within one poll no matter how many grok jobs run.
- **N general slots** (start N=3) claiming ALL lanes — drain the pb/lg grok MOTIF backlog in
  parallel, help the fast lane when it has depth.

This guarantees a short admin job never waits behind an 1800s grok job.

**Single ledger writer preserved by serialization, not by a single process.** All workers append
through the same `sched_ledger.jsonl` + `.lock`; each append re-primes prev_sha under the exclusive
mutex and writes one fsync'd line. Exactly one append in flight; the hash chain cannot tear. The
`writer` field records which slot wrote each event. **`cosmos_lock.py` needs NO change.**

**Process topology (keep-her-afloat):**
- The **supervisor** is the durable daemon, registered like `COSMOS Runner`: detached pythonw +
  1-min self-heal schtask + onlogon; holds `cosmos_pool.lock` singleton.
- **Workers are CREATE_NO_WINDOW children** of the supervisor; a crashed worker is respawned next
  tick. Each holds a per-slot lock (`cosmos_runner.slotN.lock`) so a relaunched supervisor can't
  double a slot.
- **PAUSE honored:** supervisor + workers gate claiming on `live/state/control/PAUSE.flag`
  (reuse `pause_flag`/`is_paused` from `cosmos_node_worker.py:174-202`); paused = heartbeat
  `state=PAUSED`, claim nothing, don't kill in-flight.
- **Legacy path untouched:** pool off ⇒ COSMOS behaves exactly as today.

**Spend gate:** unchanged — spend is gated inside the rails each job calls, not in the runner; N
runners can't bypass a gate they don't own. (A global concurrency spend cap is a future
admission-control feature — out of scope.)

## Diffs to apply (backward-compatible; default args ⇒ identical current behavior)

### Diff 1 — `cosmos_sched.py` lane-filtered claim
`queued()` gains `lanes: set|None=None, exclude_lanes: set|None=None`; filter `m.get("lane",
"default")` in/out before the existing sort. `claim_next()` gains the same params, passes them to
`queued()`. The `expect_head_seq=head` append is unchanged — the filter narrows *which* job, not the
fence.

### Diff 2 — `cosmos_runner.py`
- `run_one()`: `m = self.sched.claim_next(lanes=getattr(self,"claim_lanes",None),
  exclude_lanes=getattr(self,"claim_exclude",None))`.
- `drain_loop(...)`: add `pause_gate=None` param; at the top of the loop, if `pause_gate and
  pause_gate()`: write a `tick:paused, state:PAUSED` heartbeat, `sleep(interval)`, `continue`.
Both additive; a Runner with no `claim_lanes`/`pause_gate` behaves exactly as today.

### Diff 3 — `cosmos_lock.py`: NO CHANGE (arbiter already cross-process-correct).

### Diff 4 — `cosmos_own_clocks.py`: register the supervisor (telemetry + self-heal)
Add a CLOCKS entry after `COSMOS Runner`: task `COSMOS Runner Pool`, script `cosmos_pool.py`,
`standup:"pool"`, heartbeat `cosmos_pool_heartbeat.json`, vehicle detached+self-heal+onlogon.
**Confirm the `id` doesn't collide** with the existing CLOCKS ids before applying.

## New file — `cosmos/cosmos_pool.py`
Modes: `--supervise` (durable daemon; default), `--worker --slot N` (internal child; users never
call), `--standup` (register schtask + logon, mirror `cosmos_run.install_task`, proof = a FRESH
`cosmos_pool_heartbeat.json` from a live pid, not an exit code), `--status`.
- **Reuse** `cosmos_run` helpers (acquire_lock, pythonw_exe, read_heartbeat, heartbeat_age_s,
  install_task, the CREATE_NO_WINDOW/DETACHED_PROCESS/CREATE_NEW_PROCESS_GROUP flags) and
  `cosmos_node_worker` (pause_flag, is_paused) — no duplication (improvement-not-bloat).
- **bind_worker(root, slot, lanes, exclude, adapt):** resolve `CosmosPaths(root)`, read the same
  `install_key.bin` gate as `cosmos_run.bind`, build `Scheduler(q, key, worker_id=f"cosmos-runner-
  slot{slot}")` + `Runner(...)`, set `runner.claim_lanes`/`claim_exclude`, and set
  `runner.adapter = LegacyJobAdapter(...)` on the COORDINATOR slot only (single ingestor). Per-slot
  heartbeat + per-slot lock.
- **run_worker:** acquire the per-slot lock (else print `already_running`, return), then
  `runner.drain_loop(hb, interval_s, pause_gate=lambda: is_paused(pause_flag(paths)))`.
- **supervise(root, n, fast_lane, interval):** acquire `cosmos_pool.lock`; `plan_slots` = slot0
  (adapts + general) + slots 1..n-1 (general) + slot "fast" (`lanes=[fast_lane]`); loop: for each
  slot, if child dead → `spawn_worker` (Popen pythonw, DETACHED|NEW_GROUP|NO_WINDOW); write
  supervisor heartbeat (atomic tmp+replace); sleep(interval). Workers self-honor PAUSE; supervisor
  keeps them alive so resume has no respawn latency.
- **Only slot0 reports stale** (pass `stale_after_s=inf` to others, or a `report_stale=False` knob)
  so N workers don't emit duplicate `JOB_STALE`.

## Safety summary (exactly-once + single-writer)
| Guarantee | Mechanism | Evidence |
|---|---|---|
| No two workers run the same job | head-fenced `JOB_CLAIMED`; loser `STALE_HEAD`→`LOST_CLAIM` | sched:107-122, ledger:159-162 |
| Claim atomic across processes | msvcrt sidecar mutex, re-prime-under-lock, one fsync | ledger:82-181 |
| No cross-worker completion | `done()` requires claimed-by==self.worker; **unique slot id** | sched:138-141 |
| No double file-drop ingest | claim-by-rename; loser `OSError`→None | job_adapter:146-149 |
| Single writer / intact chain | one OS-locked append in flight; prev_sha re-primed; `writer` field | ledger:155-181 |
| Pool capped at N across restarts | per-slot `acquire_lock` | cosmos_run:169-192 |
| Short jobs never starve | reserved fast slot `lanes={default}` | Diff 1 + plan_slots |
| PAUSE honored, tree stays up | `pause_gate`; supervisor respawns crashed; legacy untouched | Diff 2; node_worker:174-202 |

## Open items for the coder to resolve (verify against code, don't assume)
1. `cosmos_own_clocks.CLOCKS` — pick an `id` that doesn't collide; wire the `standup:"pool"` handler.
2. Confirm signatures used exactly as `cosmos_run.py` uses them: `CosmosPaths.logs(filename)`,
   `paths.config("install_key.bin")`, `paths.role("queue"|"work"|"tools")`.
3. Chosen worker count N (start 3) and whether the fast lane is `default` or a new dedicated short
   lane.
4. Optional/separate: whether to also teach the legacy single runner (`cosmos_run.py`) to honor
   PAUSE — currently it does not (the pool workers do).

## Acceptance (runtime-binding gate)
Prove it with a value only the live pool can emit: N distinct worker-ids appear as `writer` in
`sched_ledger.jsonl` for overlapping `JOB_CLAIMED`/`JOB_DONE` within the same second, with zero
double-claim (no two `JOB_CLAIMED` for one job_id), AND a short `default`-lane job completes while an
1800s grok job is mid-flight. Report stage, never "complete."
