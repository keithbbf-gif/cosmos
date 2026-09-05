# COSMOS runner (own queue) — Motif STAGE-5 critique (G46)

**Reviewer:** G46 (Grok Build), dispatched `motif_runner_s5` 2026-08-25T22:42:11.748578-05:00
(`root/g46_grok_motif_runner_s5_you_are_g46_grok_bui_db2f17fd__t1800.py`, this job).
**Question:** is the build the thing that was decided — not "is this good code."
**Spec (decided):** DHx standup (`docs/AGENT_BRIEF.md`: "stand up COSMOS's own runner
(live\queue)"); `docs/ORCHESTRATION.md` Runner clock; ratified decisions 4 + 9
(`docs/FINAL_ARCHITECTURE.md`); port-plan successor `cosmos_sched + cosmos_runner`
(`cosmos/cosmos_port_plan.py` `bts_runner`); incumbent card `docs/STAGE2A_INCUMBENT_BEHAVIOR.md`
§4; H8 / GEM adapter (`docs/STAGE4_MERGE.md`, `docs/STAGE4_DESIGN_GEM.md`); PAUSE
(`docs/PAUSE_PROTOCOL.md`); resolver (`cosmos_paths`); Keith: no BTS, migrate onto
`live\queue` via the own runner (`BUCm.toml` `[live].daemons`).
**Build:** `cosmos/cosmos_run.py` (untracked daemon), `cosmos/cosmos_runner.py`
(`Runner.write_heartbeat` / `poll_once` / `drain_loop` added on the existing executor),
`tests/test_runner_daemon.py` (untracked). Live: `live/logs/cosmos_runner_heartbeat.json`,
schtasks `\COSMOS Runner`, pid 32400.
**Core:** `cosmos_kernel` / `cosmos_ledger` / `cosmos_sched` / `cosmos_service` were not
modified (`git diff --name-only` on those four is empty; HEAD `56fa423`). Satellite
composes `Scheduler`; it does not edit it.

**Family note (process, not a runner defect):** Motif stage 5 is a *different-family*
review. This job was dispatched to G46, who also wrote the standup (`cosmos_run.py` +
heartbeat loop on `Runner`). The findings below are still spec-vs-build, bound to files
and to a live-tree read. They are not a second family's vote. COW still owes a
non-Grok-Build pass before any stage-6 claim.

`rc=0` on `cosmos_standup_runner` is not complete. Stage 6 is a value only the live
tree can emit *for the decided drain*. A fresh idle heartbeat over a queue that holds
runnable work is not that value. Tracker: nothing has passed stage 6.

---

## Verdict

**Partly — the daemon is the decided *clock* on the decided *queue identity*. It is not
the decided *drain* of that queue.**

The build *is* a COSMOS-own `--loop` daemon that:

- binds through `CosmosPaths` to this install's `queue` / `work` / `logs` / `tools` roles
  (not `V:\Ai\_queue`);
- composes `Scheduler` + `Runner` with the install key (does not invent auth material);
- writes `live/logs/cosmos_runner_heartbeat.json` on every poll, idle or not, with
  `last_run_epoch` (bts_runner scar);
- holds `cosmos_runner.lock` and no-ops a second `--loop` when the heartbeat is fresh;
- does **not** honor `PAUSE.flag` (decided: runner keeps moving);
- does **not** import `bts_*`;
- does **not** write `live/ledger/authority.jsonl`.

That matches the *shape* in `docs/ORCHESTRATION.md` ("Persistent drain of **this
install's** queue role through `cosmos_runner.Runner`. Isolated from the BTS queue.").

It is **not** the decided *function*:

1. Decision 4: queue = **immutable manifests + ledger lifecycle**. Decision 9: a
   **Legacy Job Adapter** maps file-drop → scheduler jobs. Port-plan: `cosmos_runner`
   **keeps claim-by-rename**. The live queue role holds six Motif file-drops and
   **zero** manifests. `sched_ledger.jsonl` is **missing**. `Runner.run_one` only
   calls `Scheduler.claim_next`. There is no rename into `running\`, no adapter, no
   glob of `*.py`. The heartbeat says `tick=idle` while the queue has work.
2. `--standup` still plans `schtasks /create /tn "COSMOS Runner" /sc onlogon /f` —
   the same task name as the live **1-minute self-heal**. Re-running standup would
   clobber the clock `docs/ORCHESTRATION.md` measured. `COSMOS Runner Logon` does
   not exist.
3. Bare `Scheduler.submit` text becomes `py -3.14 -c` with **no** K4 confinement
   (the module's own boundary). That is how the only `live/work` attempt on this
   tree actually ran.

Until HIGH defects close, this row stays DRAFT at stage 5. Do not treat
`cosmos_runner_heartbeat.json` `tick=idle` + `age < 60s` as Motif stage 6.

---

## What was decided (the contract this review uses)

From DHx + tracker + BUCm:

1. Stand up **COSMOS's own runner** on **`live\queue`**, isolated from BTS
   `V:\Ai\_queue`.
2. Verify the heartbeat. Next: **confirm live, then gate**.
3. Migrate dispatch onto `live\queue` *via* the own runner — the runner is the
   drain, not a second idle universe.

From `docs/ORCHESTRATION.md`:

- Cadence: 15s `--loop` daemon + 1-min schtask self-heal + onlogon relaunch
  (separate `COSMOS Runner Logon` name; do **not** `/f` the minute task).
- Queue identity: resolver role `queue` = `V:\A\Ai\COSMOS\live\queue`. Not BTS.
- Second start no-ops on the lock if the heartbeat is fresh.
- Does **not** honor PAUSE.
- Heartbeat: `live\logs\cosmos_runner_heartbeat.json`. COMPARE USING
  `last_run_epoch`.

From ratified architecture:

- **Decision 4:** Queue = immutable manifests + ledger lifecycle events.
- **Decision 5:** Resolver is identity; no drive literal; no fallback ladder.
- **Decision 9:** Compatibility lane. **Legacy Job Adapter (GEM)** maps file-drop →
  scheduler jobs; exit codes → CLEAN / FINDINGS / BROKE.
- **Decision 2:** Atomic rename survives only as a single-volume *optimization*,
  never authority.

From port-plan / incumbent:

- `bts_runner` REPLACED by `cosmos_sched + cosmos_runner`.
- `cosmos_runner` **keeps claim-by-rename**, worded outcomes, log-first,
  report-never-retry, append-only ledger.
- Incumbent: **the file IS the dispatch**; claim-by-rename into `running\` BEFORE
  execution; command from the **claimed** path; `_`-prefix refused in-runner;
  three worded outcomes; log-first; stale RUNNING reported never auto-rerun;
  per-worker heartbeat with epoch + UTC.

From PAUSE: runner executes already-queued jobs during a hold. A paused retask
clock is not a paused drain.

---

## Live-tree read (this critique, not a stage-6 pass)

Host clock `2026-08-25T23:30:36-05:00` (epoch `1787718636`), then a second read
of the heartbeat file.

Quoted from `live/logs/cosmos_runner_heartbeat.json` (host read this session):

```
last_run        = 2026-08-25T23:32:16-05:00
last_run_epoch  = 1787718736
worker          = cosmos-runner
pid             = 32400
queue_root      = V:\A\Ai\COSMOS\live\queue
work_root       = V:\A\Ai\COSMOS\live\work
instance_id     = 103899b42eb7
polls           = 513
interval_s      15.0
stale_reported  = []
jobs_this_tick  = 0
job_ids         = []
tick            = idle
```

Process: pid **32400** alive, `pythonw.exe`
(`C:\Users\Papa\AppData\Local\Programs\Python\Python314\pythonw.exe`), start
`2026-08-25 21:24:14`. Same pid as standup SNAP (`cosmos_standup_runner_result.json`,
polls 1→3 at `2026-08-25T21:24:44-05:00`). Polls 3 → 513 over ~128 min at 15 s is
the same loop, not a restarted counter.

schtasks `\COSMOS Runner` (host `/query /fo LIST /v`):

```
Task To Run:     py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_run.py --root V:\A\Ai\COSMOS\live --loop
Status:          Ready
Last Run Time:   8/25/2026 11:30:00 PM
Last Result:     0
Schedule Type:   One Time Only, Minute
Repeat:          1 Minute(s)
Logon Mode:      Interactive only
```

`schtasks /query /tn "COSMOS Runner Logon"` → **ERROR: The system cannot find the
file specified.** (ORCHESTRATION: Keith's one elevated line still owed.)

`live/state/control/PAUSE.flag` is present (`mode=hold`, TidyUP). Runner kept
writing heartbeats — correct vs PAUSE protocol.

**What is sitting on the queue role the heartbeat names**, host walk
`2026-08-25T23:30`:

| path | mtime | claimed? |
|---|---|---|
| `live/queue/g46_grok_motif_cdeck_s6_…__t1800.py` | 23:27:01 | no |
| `live/queue/g46_grok_motif_gbridge_s6_…__t1800.py` | 23:27:01 | no |
| `live/queue/_lanes/lg/g46_grok_motif_cvm_s6_…__t1800.py` | 23:27:01 | no |
| `live/queue/_lanes/lg/g46_grok_motif_meshadditions_s3_…__t1800.py` | 23:27:01 | no |
| `live/queue/_lanes/pb/g46_grok_motif_cdm_s6_…__t1800.py` | 23:27:01 | no |
| `live/queue/_lanes/pb/g46_grok_motif_cursor_s6_…__t1800.py` | 23:27:01 | no |

Counts: `done=0` `failed=0` `running=0` `logs=0` `manifests=0` `returns=0`.
`live/queue/sched_ledger.jsonl` **MISSING**. `live/cosmos` (resolver `tools` role)
exists and is **empty**.

`live/work` holds one attempt, **not from this daemon**:

```
RUNNING 1787485334732-740d78bf3a attempt 3f31141b14
worker cutover
argv ['py', '-3.14', '-c', "print('cosmos live: hello from the runner')"]
started Sun Aug 23 06:42:14 2026
```

This critique job itself is **not** on `live\queue`. It is
`V:\Ai\_queue\running\g46_grok_motif_runner_s5_you_are_g46_grok_bui_db2f17fd__t1800.py`
— BTS runner, drop from 22:42. After own-clocks, Motif Driver writes the *same
shape* onto `live\queue` (`cosmos_motif_driver.drive_once` → `dispatch(..., queue=q)`
with `q = runtime_root / "queue"`). Native runner cannot see either generation.

These numbers prove a daemon is polling **this** install's queue role on the 15 s
clock. They do not prove it drains that queue.

---

## HIGH

### H1 — Live queue-role work is invisible; heartbeat is idle over stranded jobs

- **File/symbol:** `cosmos/cosmos_runner.py` — `Runner.run_one` (`m = self.sched.claim_next()`);
  `Runner.drain` / `poll_once` / `drain_loop`. No glob of `*.py`, no `running\`, no
  `_lanes`. `cosmos/cosmos_run.py` — `bind` (`sched = Scheduler(q, key, WORKER)`).
- **Decided:** Own runner **drains this install's queue role**. Decision 4: manifests
  + ledger lifecycle. Decision 9: file-drops are not ignored — they are **adapted**
  into scheduler jobs. Port-plan: keep claim-by-rename. Incumbent: the file IS the
  dispatch; an unrun queue must not look like an empty one (lane scar,
  STAGE2A §4).
- **Build:** The only ingress is `JOB_SUBMITTED` on `queue/sched_ledger.jsonl`.
  File-drops under `queue/` and `queue/_lanes/<lane>/` are not jobs. Heartbeat has
  no `stranded` / `pending_files` field, so idle-empty and idle-stranded are the
  same `tick=idle`.
- **Live proof:** six Motif `.py` files dated `2026-08-25T23:27:01-05:00` still
  unclaimed at `23:32:16` (~20 idle polls). `manifests=0`, `sched_ledger.jsonl`
  missing, `jobs_this_tick=0`, `polls=513`. Motif Driver already pointed `queue`
  at the native role (`cosmos_motif_driver.drive_once` default `rt / "queue"`).
- **Impact:** The migration BUCm named ("onto `live\queue` via the own runner")
  moved the **drop** and not the **drain**. Operators (and WD2 `inflight_filenames`)
  treat those files as queued work. The own runner is a green idle loop over them.
  That is the fabricated-compliance class on the deliverable's own heartbeat:
  liveness without the decided function. A peer on a cold machine with only
  `live\queue` file-drops gets the same silent stall.
- **Fix:** One ingress on the queue role. Either (a) producers `Scheduler.submit`
  immutable manifests (decision 4) and file-drops are a typed refusal, or (b) a
  Legacy Job Adapter (decision 9) claims-by-rename (or copies into the attempt
  dir) and submits the claimed path. Heartbeat must name stranded file-drops
  (`pending_files` / `tick=stranded`) so idle-empty ≠ idle-full. Test: drop a
  `__t30.py` under the bound queue **without** `submit()`; the next `poll_once`
  either runs it or heartbeats a typed stranded count — never quiet `idle`.

### H2 — No claim-by-rename and no Legacy Job Adapter (the successor did not keep the incumbent)

- **File/symbol:** missing in `cosmos_runner.Runner` (no `Path.rename` into
  `running\`, no `_is_runnable`, no lane rebind). Missing adapter module (no
  `cosmos_job_adapter` / `Legacy Job Adapter`). `cosmos_port_plan.PORT_PLAN["bts_runner"]`
  still claims the successor "keeps claim-by-rename".
- **Decided:** Port-plan replacement text. STAGE4_MERGE adopted GEM's adapter as
  an explicit component. Decision 9 is ratified. Decision 2: rename is an
  optimization, not authority — which still requires *a* claim, ledgered.
  H8: claim-by-rename when single-volume, else arbiter-issued claims.
- **Build:** `Scheduler.claim_next` is the "or better" ledger claim
  (`JOB_CLAIMED` + `expect_head_seq`). That is the native path (decision 4) and
  it is real. The compatibility path (decision 9) was not built. `Runner` never
  moves a file. `done/` `failed/` `running/` on the live queue role stay empty
  by construction.
- **Live proof:** H1's six files. `live/work` has no attempt for any of them.
- **Impact:** Spec-and-build agree on Scheduler-native jobs and then the OS
  actually drops the *other* shape onto the same directory. Without the adapter,
  "own queue" is two protocols sharing a folder. Closing H1 by telling producers
  to `submit()` still leaves every existing file-drop (Motif Driver, dispatch
  harness, any sandbox that can write a `.py`) stranded — the exact class
  decision 9 existed to carry.
- **Fix:** Ship the adapter as a satellite next to `cosmos_run` (do not edit
  `cosmos_sched`). Claim the file (rename on this volume into attempt-private
  work, or ledger the claim and copy), `Scheduler.submit` the claimed command,
  map rc 0/2/other → CLEAN/FINDINGS/BROKE, land `result.json`. Do not run the
  pre-claim path (incumbent scar: verifying a path is not verifying the path
  you are about to use).

### H3 — `--standup` `/f` onlogon onto the live 1-min task name (clock clobber)

- **File/symbol:** `cosmos/cosmos_run.py` — `TASK_NAME = "COSMOS Runner"`;
  `plan_task_argv` (`/sc onlogon /f`); `install_task`; `standup` calls
  `install_task` whenever the heartbeat is not already fresh.
- **Decided:** `docs/ORCHESTRATION.md` — 1-min self-heal on `\COSMOS Runner`;
  onlogon is a **separate** `COSMOS Runner Logon`. Quote: *Do not `/f`-overwrite
  the existing minute self-heal names with onlogon-only.* Own-clocks standup
  already split the names (`cosmos_own_clocks.py` `logon_specs`).
- **Build:** A cold `cosmos_run --standup` (or a dead-heartbeat restart) runs
  `schtasks /create /tn "COSMOS Runner" /sc onlogon /f`. That is the live
  minute task's name. `/f` replaces it. `tests/test_runner_daemon.py` asserts
  the onlogon plan (`plan_task_argv: schtasks /create /tn COSMOS Runner /sc onlogon`)
  — the test encodes the wrong clock.
- **Live proof:** Minute task is registered and firing (`Last Result: 0`,
  `Last Run 11:30:00 PM`). `COSMOS Runner Logon` is absent. Standup result
  recorded `schtasks /create` **Access is denied** and survived via WMI pid
  32400; own-clocks later registered the minute task. Re-running *this*
  module's standup is what would destroy that.
- **Impact:** The survival clock the matrix treats as live is not the clock
  this deliverable's `--standup` recreates. Logoff/reboot currently depends
  on the 1-min self-heal once `V:` is mounted (ORCHESTRATION). A "heal" via
  `cosmos_run --standup` would leave only onlogon — which this session could
  not register unelevated — and kill the minute trigger.
- **Fix:** `--standup` must not use `TASK_NAME="COSMOS Runner"` with `/sc onlogon`.
  Either call the own-clocks registrar, or create `COSMOS Runner Logon` only and
  leave the minute task alone. Change the selftest assertion. Keith's elevated
  one-liner stays the logon path.

### H4 — Unprefixed `submit()` text is `py -c` with no K4 confinement

- **File/symbol:** `cosmos/cosmos_runner.py` — `Runner.run_one` `else:` branch
  (`argv = ["py", "-3.14", "-c", cmd]`); `_confine_argv` (`if interp and "-c" in rest:
  return None` — skips path confinement whenever `-c` appears).
- **Decided:** Module docstring: K4 tools-root confinement is the boundary;
  "no shell, ever." Incumbent: command from a **claimed path**, not an
  unconstrained interpreter. Decision 9 adapter maps file-drops to scheduler
  jobs — those jobs must still be confined.
- **Build:** `Scheduler.submit("print('hello')")` (the native API, and the
  `tests/test_runner_daemon.py` / `tests/test_wave3.py` M5 happy path) becomes
  `-c` with no `tools_root` check. `-c` anywhere in `argv:` rest disables
  confinement for the rest of the vector (a script + `-c` flag skips the
  script check). `bind()` does set `runner.tools_root = paths.role("tools")`
  (`live/cosmos`, empty on this tree) — that only applies to `py:` / path
  tokens, not `-c`.
- **Live proof:** the only `live/work` attempt on this install is exactly that
  path: `argv ['py', '-3.14', '-c', "print('cosmos live: hello from the runner')"]`
  worker `cutover`, 2026-08-23. Selftests certify it as CLEAN.
- **Impact:** Anyone who can `Scheduler.submit` a string (or any adapter that
  wraps file bytes as `-c`) runs unconstrained Python as the runner's user.
  That is the STAGE-7 K4 hole the `py:` branch closed, left open on the
  default command form. Tests treat the hole as the success case.
- **Fix:** Default command form is `py:` / `argv:` only; a bare string is
  FINDINGS/BROKE (`BAD_COMMAND`), not `-c`. If `-c` remains a deliberate
  native form, it still does not skip confinement of other path tokens, and
  it is not the adapter's translation of a file-drop (adapter copies into
  `work/<job>/<attempt>/job.py` and runs the claimed copy). Test: bare
  `submit("import os; os.system('...')")` is refused; `argv:` with
  `python -c` + a path token still confines the path.

---

## MEDIUM

### M1 — Isolated selftest never exercises the decided live behaviors

- **File/symbol:** `tests/test_runner_daemon.py` (17 checks: bind paths, idle
  heartbeat, `drain_loop` polls, one `submit()` CLEAN, schtasks onlogon argv
  has no `V:\Ai\_queue`).
- **Missing vs spec:** file-drop on the queue role (H1); adapter (H2); minute
  self-heal argv not onlogon (H3); `-c` refuse (H4); `tools_root` empty → typed
  miss; PAUSE non-gating; second `--loop` no-op on fresh lock; stranded
  heartbeat field; `sched_ledger` created under the bound queue after a real
  submit.
- **Impact:** `17/17` and standup `rc=0` are exactly the class Motif forbids
  treating as complete. The live tree is the counterexample the selftest cannot
  see.

### M2 — Heartbeat cannot tell empty from full (lane scar, unclosed)

- **File/symbol:** `Runner.write_heartbeat` / `drain_loop` extra keys
  (`jobs_this_tick`, `job_ids`, `stale_reported` — no pending-file count, no
  `manifests_queued`, no `file_drops`).
- **Decided:** STAGE2A: "jobs queued into a lane with no runner sit forever,
  and an unrun queue looks exactly like an empty one."
- **Live:** `tick=idle` is true for both. `stale_reported=[]` because nothing
  was ever `JOB_CLAIMED`.
- **Fix:** Project `Scheduler.queued()` length **and** unmatched `*.py` under
  the queue role into the heartbeat every tick.

### M3 — `tools_root` is `live/cosmos` and empty; queue-resident scripts would be refused even after H1

- **File/symbol:** `cosmos_run.bind` (`runner.tools_root = paths.role("tools")`);
  `cosmos_paths.ROLES["tools"] = "cosmos"`; `Runner._confine_path`
  (`relative_to` tools root).
- **Decided:** K4 confinement is real. Incumbent command is the **claimed**
  queue file, which does not live under `tools`. Adapter (H2) must stage into
  attempt-private work (inside `work/`, which is also outside `tools`) or the
  runner must treat a *claimed* attempt copy as in-bound.
- **Live:** `V:\A\Ai\COSMOS\live\cosmos` exists, no children. A naive
  `submit("py:V:\\A\\Ai\\COSMOS\\live\\queue\\foo.py")` → `traversal_refused`.
- **Impact:** H1 "just submit the path" is not a fix. The adapter and K4 have
  to be designed together or every adapted file-drop BROKEs.

### M4 — `report_stale` window is 1 h vs incumbent 2 h; errors are swallowed into extra

- **File/symbol:** `Runner.drain_loop` (`stale_after_s: float = 3600.0`;
  `except Exception` around `self.sched.report_stale` → `stale = []`).
- **Decided:** STAGE2A stale RUNNING > **2 h**, reported never retried.
- **Build:** 3600 s; a `report_stale` exception becomes an empty list and the
  loop continues. Fail-closed would record `tick=error` (the drain `except`
  already does that for `SchedError` other than `LOST_CLAIM`).
- **Impact:** Stale claims (once H1/H2 land real claims) report an hour early,
  or not at all if the reporter throws.

### M5 — `--status` constructs `bind()` (mkdir queue/work/logs, compose Scheduler)

- **File/symbol:** `cosmos_run.main` `--status` → `bind(a.root)`.
- **Defect:** a liveness read mkdir's roles and instantiates `Scheduler` (which
  mkdir `manifests/`). Status is not a write of the tree. Cheap, but it is a
  side effect on a probe — and it can create an empty `manifests/` that looks
  like a live scheduler that has never submitted.

### M6 — Dual universe still live: this job runs on BTS while native ticks idle

- **File/symbol:** not in `cosmos_run` (producer: `cosmos_dispatch.DEFAULT_QUEUE`
  still `V:\Ai\_queue`; Motif Driver now passes `live\queue`). Cited because
  the *runner* deliverable was "migrate onto live\queue **via** the own runner."
- **Live:** `V:\Ai\_queue\running\g46_grok_motif_runner_s5_…` (this critique);
  six siblings idle on `live\queue`. Native `tick=idle`.
- **Impact:** Confirming the heartbeat "live" without a native drain proof
  ratifies the split. Stage 6 cannot be a BTS `*_result.json`. Tied to H1;
  separate because even after adapter, dispatch default identity remains BTS
  (dispatch STAGE3 H1) — the runner gate must still be a **native** job_id.

### M7 — `cosmos_runner.py` default `_tools_root` is `work.parent / "cosmos"` vs comments `"tools"`

- **File/symbol:** `Runner._tools_root`; `run_one` comment "default the
  runner's work parent / tools".
- **Mitigation:** `cosmos_run.bind` sets `tools_root` to the resolver role.
  Do not regress. The unbound `Runner(sched, work, id)` used in
  `test_wave3` / `test_rest_guards` still hits the docstring mismatch.
  G46 tool-review 2026-08-25 already flagged this; standup did not close it.

---

## LOW

### L1 — `_is_whitelisted_interp` `startswith("python3")` after the set check

- **File/symbol:** `Runner._is_whitelisted_interp`.
- **Defect:** `python3-evil` qualifies as an interpreter name. Harmless while
  `_looks_like_path` then requires it to resolve to a real python; still a
  wider gate than `{py, python, python3}`.

### L2 — `json.loads` of `argv:` only catches `ValueError`

- **File/symbol:** `Runner.run_one` `argv:` branch. `json.loads("2")` / a JSON
  object is not a `ValueError`; `_confine_argv` then refuses non-list — OK —
  but a non-str payload can `TypeError` before refuse.

### L3 — Refuse path may skip attempt log / `result.json`

- **File/symbol:** `Runner._refuse` → `sched.done` + return, **before**
  `makedirs(adir)` / log-first write when called from `_confine_path` prior
  to log open. Helper/traversal refusals have no attempt-private artifact.
  Docstring: every artifact is attempt-private.

### L4 — `drain_loop` `max_jobs=1` is correct; `--once` `poll_once` also 1, but `drain()` default is 50

- **File/symbol:** `Runner.drain(max_jobs: int = 50)` vs daemon `max_jobs=1`
  "so a long job cannot starve the next heartbeat."
- **Defect:** any caller of `drain()` (tests, future clocks) can run 50 jobs
  with no heartbeat between them. Not the live daemon. Note for the next
  composer.

### L5 — Lock file is a 1-byte `msvcrt.locking` slot; pid write is best-effort

- **File/symbol:** `acquire_lock`. Host read of `live/logs/cosmos_runner.lock`
  this session was empty/non-text. Heartbeat `pid` is the liveness key, not
  the lock file. Fine; do not treat the lock file as a pid proof.

### L6 — `bind()` mkdir of `queue` / `work` / `logs` if missing

- **Decided:** existence is not identity; missing identity is a typed refusal.
- **Build:** missing queue dir is created, then drained as empty. For a daemon
  this is survival. For `--status` (M5) it is a write. Fail-closed would still
  demand the sentinel + install key (it does) and could refuse a missing
  **role** rather than mkdir on a status probe.

### L7 — Worded outcomes are ledger events, not `done/` `findings/` `failed/` directories

- **File/symbol:** `Runner.run_one` → `sched.done(job_id, outcome, detail)`.
- **Decided:** decision 4 prefers ledger lifecycle over mutable dirs. Incumbent
  dirs are the compatibility mapping (decision 9). Native is correct; the
  adapter (H2) still owes the directory projection so a human looking at
  `live/queue/done` is not lied to. Today `done/` empty means "nothing ran",
  which happens to be true, and will become a lie the first time a Scheduler
  job CLEANs.

---

## What is positively evidenced (bound to artifacts)

- Satellite, not Core: git diff on kernel/ledger/sched/service is empty. HEAD
  `56fa423`. `cosmos_run.py` untracked; `cosmos_runner.py` modified (heartbeat
  API); `tests/test_runner_daemon.py` untracked.
- Queue identity is the resolver role. Heartbeat `queue_root` =
  `V:\A\Ai\COSMOS\live\queue`. No `bts_*` import. `plan_task_argv` `/tr` does
  not mention `V:\Ai\_queue` (selftest).
- Install key required: `bind` raises `CosmosPathError` if
  `config/install_key.bin` is missing — does not invent material.
- Heartbeat on every poll with `last_run_epoch` + UTC + local offset. Pid
  32400 advanced polls 3 (standup 21:24:44) → 513 (23:32:16). Age at first
  host sample was 5 s. Same `instance_id=103899b42eb7`.
- Second `--loop` no-op: schtasks Last Result `0` every minute while pid 32400
  holds the lock (the 1-min `/tr` is `--loop`; fresh heartbeat → return 0).
  Matches ORCHESTRATION "a second start no-ops on the lock if the heartbeat
  is fresh."
- PAUSE hold present; runner still polling. Decided.
- Log-first + three worded outcomes + helper refusal exist on `Runner` and are
  tested in `tests/test_wave3.py` M5 (`CLEAN` / `FINDINGS` / `BROKE` /
  `_`-prefix `helper_refused` / attempt `result.json`) — on a **scratch**
  `Scheduler.submit`, not on `live\queue`.
- WMI standup survived the job-object kill that ate pythonw pid 4284
  (`cosmos_standup_runner_result.json`). That survival is real.
- Does not write authority.jsonl. Does not modify kernel/sched/service.

Those are foundations. They are not evidence that the own queue is drained,
that file-drops are adapted, or that `--standup` recreates the live clock.

---

## Safety (the review MOTIF_TRACKER named)

| question | finding |
|---|---|
| Does it write the authority ledger? | No. Scheduler ledger would be `queue/sched_ledger.jsonl` (missing; no submits). |
| Does it modify kernel/sched/service? | No. Compose only. |
| Can it look alive while dropping work? | **Yes (H1, M2).** Fresh `tick=idle` over six queued files. |
| Does it stop on PAUSE? | Correctly no. |
| Drive-literal default? | **No** in this module. `bind()` uses `paths.role("queue")`. |
| Claim-by-rename / adapter? | **Absent (H2).** |
| Unconstrained execution? | **Yes (H4)** via default `-c`. |
| Clock clobber on re-standup? | **Yes (H3).** `/f` onlogon onto `\COSMOS Runner`. |
| Second authority? | Queue ledger is the decided scheduler ledger, not a second Core writer. File-drops on the same directory are a second *protocol*. |

COW in-session safety review should treat H1+H2 as the blocking pair: do not
call the row live-complete while Motif files sit on `live\queue`; do not
`Scheduler.submit` those paths as `py:` without the adapter (M3). Do not
re-run `cosmos_run --standup` against this tree until H3 is closed (it would
`/f` the minute self-heal).

---

## Acceptance conclusion

**Confirm live: YES — the process. Confirm drain: NO. Do not advance to stage 6.**

Live-tree confirmation (this session, bound to artifacts):

- pid **32400** alive, `pythonw`, start 21:24:14, `instance_id=103899b42eb7`
- `last_run_epoch=1787718736` (`2026-08-25T23:32:16-05:00`), age < 15 s
- `queue_root=V:\A\Ai\COSMOS\live\queue`, `interval_s=15.0`, `polls=513`
- schtasks `\COSMOS Runner` Enabled, 1-min, `/tr` `cosmos_run.py --loop --root …\live`

That is the standup's heartbeat proof, still true two hours later. It is not
the decided runner.

The build delivered a live 15 s daemon at the named paths, isolated from BTS.
It did not deliver the decided drain: manifests+ledger on that role, a Legacy
Job Adapter for file-drops, claim-by-rename (or a ledgered equivalent that
still *sees* the files), or a `--standup` that recreates the measured clock.

Stage-6 gate, when H1–H4 are closed, is not `rc=0` and not "heartbeat age < 60s."
It is a live-tree quadruple only this install can emit, for example:

1. A job that landed on **this** `live\queue` (Scheduler manifest **or**
   adapted file-drop) appears in `cosmos_runner_heartbeat.json` as
   `tick=drained` with that `job_id` (not `tick=idle` while the file still
   sits in the queue root / `_lanes`).
2. `live/queue/sched_ledger.jsonl` verifies `JOB_SUBMITTED` → `JOB_CLAIMED` →
   `JOB_DONE` for that id, worker `cosmos-runner`, outcome CLEAN or a typed
   BROKE/FINDINGS.
3. `live/work/<job_id>/<attempt>/result.json` exists and names the same id
   (attempt-private artifact).
4. Same pid's `last_run_epoch` continues to advance on the 15 s clock after
   that drain.

Until that quadruple is quoted from the live tree, the MOTIF_TRACKER row
remains stage 5 DRAFT. A BTS `*_result.json` for this critique is not the
gate.

---

## Suggested next (stage 6 consensus / improve — not done here)

1. Adapter + heartbeat stranded field (H1, H2, M2). Do not `py:` the
   pre-claim queue path (M3).
2. Stop `--standup` from `/f` onlogon onto `\COSMOS Runner` (H3).
3. Refuse bare `-c` as the default `submit()` form (H4); fix the tests that
   certify it.
4. Point Motif Driver / `cosmos_dispatch` default identity at resolver
   `queue` **and** `Scheduler.submit` (or the adapter) so the native drain
   is the OS path (M6; dispatch's own STAGE3 H1).
5. Different-family (non-Grok-Build) pass on this critique + the patched
   build.

This critique does not edit `cosmos_kernel.py` / `cosmos_ledger.py` /
`cosmos_sched.py` / `cosmos_service.py`.
