# CLOCK_POSTMORTEM — cvm-dt-clock and cvm-dt-voice, 3.5 days stale

**Written** 2026-08-30 (fence: `builds/cvm-dt/`).
**Subjects** `live/logs/cvm_dt_clock_heartbeat.json` (315 715 s stale),
`live/logs/cvm_dt_voice_heartbeat.json` (306 551 s stale).

## Verdict, up front

**Neither worker crashed, and neither was deregistered. Neither was ever registered.**

- `cvm-dt-clock` has a complete daemon vehicle (`--loop`, OS lock, `.out` redirect,
  `--register`) — but `--register` only *emits* the `schtasks /Create` line by design, and
  **the emitted line was never run**. The clock has therefore only ever executed as a
  hand-run `--once`. There was no scheduler to run it a second time.
- `cvm-dt-voice` had **no daemon vehicle at all** — no task name, no `--register`, no lock,
  no `--loop` flag. **No code path anywhere in the repository could create a
  `COSMOS CVM DT Voice` task.** It was never schedulable, so it was never scheduled.

The `UNREACHABLE` recorded in both final heartbeats is **not the cause of death** — see the
controlled comparison below. It is only what the last tick happened to see.

The task brief's framing — "they died in the same window as the motif-route wedge
(2026-08-26 → 2026-08-30)" — is **correlation, not causation**. 2026-08-27 is simply the last
day someone hand-ran them. A process that is never scheduled does not need a wedge to stop.

## The eyewitnesses (verbatim, captured before any change)

`cvm_dt_clock_heartbeat.json`:

```json
{ "last_run": "2026-08-27T07:26:18-05:00", "last_run_epoch": 1787833578,
  "worker": "cvm-dt-clock", "pid": 5404, "polls": 0, "interval_s": 2.0,
  "schema": "cvm-dt-clock/1", "tick": "refused", "state": "REFUSED",
  "clock_id": 18, "quoted_from": "/api/v1/cvm/pull?client_id=cvm-dt",
  "pause_present": true, "pause_mode": "running", "auto_resume_at": null,
  "ok": false, "kind": "UNREACHABLE",
  "detail": "[UNREACHABLE] Core http://127.0.0.1:8770: [WinError 10061] No connection could be made because the target machine actively refused it" }
```

`cvm_dt_voice_heartbeat.json`:

```json
{ "last_run": "2026-08-27T09:59:03-05:00", "last_run_epoch": 1787842743,
  "worker": "cvm-dt-voice", "pid": 14444, "polls": 1, "interval_s": 2.0,
  "clock_id": 18, "mic_state": "idle", "core_kind": "UNREACHABLE",
  "schema": "cvm-dt-voice/1", "stt_kind": "STT_NONE", "tick": "refused",
  "ok": false, "kind": "UNREACHABLE", "ticket_clock_id": 16, "audio_owner": "none" }
```

> ⚠ **Both heartbeat files have since been refreshed by this investigation.** Running the
> fence's own suites (`test_cvm_dt_clock.py`, `test_cvm_dt_voice.py`) writes the *production*
> heartbeat paths — clock `pid 14864`, voice `last_run_epoch 1788149970`. The values above are
> the pre-investigation truth. A fresh reading on those two files today does **not** mean a
> daemon is running. See *Residual finding*.

## Timeline

| when (epoch / local) | event | evidence |
|---|---|---|
| ~2026-08-27T01:50 | `PAUSE.flag` set `RUNNING` by COW auto-resume | `work/g46_critfix_rtb/run_rtb.py:79` |
| pre-08-27 | Gap already flagged and never closed: *"live/logs/ has cvm_clock_heartbeat.json … but NO cvm_dt_clock_heartbeat.json — the DT own-clock is not ticking natively"* | `work/g46_critfix_rtb/run_rtb.py:77` |
| `1787833578` = 2026-08-27T07:26:18-05:00 | **clock's last tick.** Hand-run `--once`; refused `UNREACHABLE`; wrote heartbeat; left `cvm_dt_clock.lock` containing `5404`; process exited normally (that is what `--once` does) | heartbeat `polls: 0`; `live/logs/cvm_dt_clock.lock` mtime 08-27 07:26, content `5404` |
| +9 165 s = 2026-08-27T09:59:03-05:00 | **voice's last tick.** One-shot; refused `UNREACHABLE`, `STT_NONE`, mic idle; exited | heartbeat `polls: 1` |
| 08-27 → 08-30 | nothing re-runs either worker; 315 715 s / 306 551 s accrue | no task exists (below) |
| 2026-08-30 ~23:08 | staleness observed | `builds/health/test_cosmos_health_watchdog.py:282-283` |

## Evidence per conclusion

### 1. Not registered — measured, not inferred

Read-only `schtasks /Query` through the tree's own `cosmos_clock.query_task`:

```
{"task": "COSMOS CVM DT Clock",       "ok": false, "rc": 1, "out": "ERROR: The system cannot find the file specified."}
{"task": "COSMOS CVM DT Clock Logon", "ok": false, "rc": 1, "out": "ERROR: The system cannot find the file specified."}
{"task": "COSMOS CVM DT Voice",       "ok": false, "rc": 1, "out": "ERROR: The system cannot find the file specified."}
{"task": "COSMOS CVM Clock",          "ok": true,  "rc": 0, "out": "TaskName: \\COSMOS CVM Clock  Next Run Time: 8/30/2026 11:13:00 PM"}
{"task": "COSMOS Runner Pool",        "ok": true,  "rc": 0, "out": "TaskName: \\COSMOS Runner Pool Next Run Time: 8/30/2026 11:13:00 PM"}
```

`rc=1 / "cannot find the file specified"` is Task Scheduler's *no such task* answer. Registered
siblings answer `rc=0` with a next-run time in the same query, so the query itself is proven
working. **Not a deregistration** — a deregistered task and a never-created task are
indistinguishable *at the scheduler*, so the discriminator is §2.

### 2. `--loop` never ran against this root — the clock never was a daemon

`cvm_dt_clock.loop()` (`cvm_dt_clock.py:263-266`) creates and opens
`logs/cvm_dt_clock.out` **unconditionally, before anything else**:

```python
out_path = paths.logs("cvm_dt_clock.out")
out_path.parent.mkdir(parents=True, exist_ok=True)
log_fh = open(out_path, "a", encoding="utf-8", buffering=1)
```

`find live -name cvm_dt_clock.out` → **no such file anywhere under the runtime root.** If a
scheduled task had ever fired `--loop`, even once, even to die immediately after, that file
would exist. It does not. Therefore `loop()` has never executed against this root, therefore
the clock was never running as a daemon — so there was nothing to crash, and nothing to
deregister. Corroborated by heartbeat `polls: 0`: `loop()` increments `polls` to ≥1 before its
first `poll_once`, while the `--once` path calls `poll_once` with the default `polls=0`.

### 3. Voice was never *schedulable*

`cvm_dt_voice.py` as found defined `HEARTBEAT_NAME` and `WORKER` and nothing else of a
vehicle: no `TASK_NAME`, no `register()`, no `acquire_lock`, no `--loop` flag, no `.out`
redirect. `register()` is the only thing in this package that emits a `schtasks` line, and
voice did not have one. No `cvm_dt_voice.lock` has ever existed in `live/logs/`. So the
absence of a `COSMOS CVM DT Voice` task is not a loss — the task was never creatable.

### 4. `UNREACHABLE` did not kill them — the controlled comparison

The registered sibling `cosmos-cvm-clock` (id 16), read this minute:

```json
{ "worker": "cosmos-cvm-clock", "pid": 18660, "polls": 96040, "tick": "loop",
  "state": "RUNNING", "core_ready": false, "core_kind": "UNREACHABLE",
  "last_run": "2026-08-30T23:17:11-05:00", "clock_id": 16 }
```

And Core right now: `CORE 8770: DOWN timed out`.

id 16 has taken **96 040 polls** (≈53 h at 2 s) in exactly the `UNREACHABLE` condition the two
dead heartbeats recorded, and it is `RUNNING` this minute. A clock that is scheduled survives a
dead Core indefinitely; `UNREACHABLE` is a typed refusal the loop is designed to absorb, not a
fatal error. **The only material difference between id 16 and id 18 is registration.**

### 5. The stale lock is residue, not a blocker

`live/logs/cvm_dt_clock.lock` still holds `5404` — the dead clock's own pid. It is *not* why
nothing restarted. `cosmos_clock.acquire_lock` (`cosmos_clock.py:99-122`) takes an **OS
byte-range lock** (`msvcrt.locking(fd, LK_NBLCK, 1)`) on an `O_CREAT` (not `O_EXCL`) handle;
Windows drops the lock when the holding process exits. A leftover lock *file* therefore blocks
nothing. Recorded so no one later "fixes" this by deleting a red herring.

### 6. Why nothing reported it

Two independent registries, both hard-coded, both stopping short of these workers:

- **`cosmos/cosmos_own_clocks.py`** — `CLOCKS` runs id 1…**17** and stops
  (`cosmos_own_clocks.py:163-173` is id 17, the last entry). `cvm_dt_clock.py` declares
  `CLOCK_ID = PULL_CLOCK_ID = 18`. `matrix()` iterates `CLOCKS`, so **id 18 produces no row** —
  no registration check, no heartbeat age, no standup self-heal.
- **`cosmos/cosmos_health_clock.py`** — `PEER_HEARTBEATS` (`:61-73`) is a 12-name tuple.
  Neither `cvm_dt_clock_heartbeat.json` nor `cvm_dt_voice_heartbeat.json` is in it (nor is
  `cvm_clock_heartbeat.json`).

A repo-wide grep for either heartbeat filename returns **no hit under `cosmos/` at all** — the
only references are the workers themselves, their own tests, and `builds/health/` fixtures. The
monitors were never told these files exist. That is the whole of "nothing reported it."

## What was fixed, in fence (`builds/cvm-dt/`)

Backups taken **before** editing, per canon:
`_delme/predispose_cvm_dt_voice_20260830-231749/cvm_dt_voice.py` (39 336 B),
`_delme/predispose_cvm_dt_clock_20260830-231749/cvm_dt_clock.py` (14 604 B).

**`cvm_dt_voice.py` — given the daemon vehicle it never had.** Mirrors `cvm_dt_clock`, reusing
`cosmos_clock` helpers; no new abstraction:
- `TASK_NAME` / `TASK_NAME_LOGON` / `LOCK_NAME` / `OUT_NAME` / `FRESH_S`;
- `loop()` now redirects `stdout`/`stderr` to `logs/cvm_dt_voice.out` **before** looping, and
  holds the OS lock (`_locked` + `skip_alive`) so a 1-min self-heal task cannot stack processes;
- `register()` emits the two `schtasks /Create` lines and **does not run them** (`"ran": false`);
- `status()` reports heartbeat age **and** `registered`;
- CLI: `--loop`, `--register`, `--status`. `--loop` also had to be *accepted* — `register()`
  emits `--loop`, which the old parser would have rejected as an unrecognized argument.

**`cvm_dt_clock.py` — `status()` can now see registration.** It previously answered from the
heartbeat alone, so it could not tell *"the daemon died"* from *"no daemon was ever
scheduled"* — and it was the second. `status()` now also quotes `query_task(TASK_NAME)`, and
`--status` fails closed (`rc=2`) when the task is unregistered, not merely when the heartbeat
is stale.

### The fix, exercised (post-change, verbatim)

```
$ py -3.14 builds/cvm-dt/cvm_dt_clock.py --root V:/A/Ai/COSMOS/live --status   # rc=2
 "age_s": 316386.1661980152, "clock_id": 18, "fresh": false,
 "task_name": "COSMOS CVM DT Clock", "registered": false, "logon_registered": false

$ py -3.14 builds/cvm-dt/cvm_dt_voice.py --root V:/A/Ai/COSMOS/live --status   # rc=2
 "worker": "cvm-dt-voice", "age_s": 307212.22437882423, "fresh": false,
 "task_name": "COSMOS CVM DT Voice", "registered": false, "logon_registered": false
```

Both now name the actual cause on sight. Suites after the change:
`test_cvm_dt_clock.py` → `result: ok 10/10`; `test_cvm_dt_voice.py` → `result: 33/33`.

### A hypothesis this postmortem had to discard

Initial reading was that voice's `loop()` would be killed on its first tick by the bare
`print()` in `_print_tick`, because `pythonw.exe` has no console. **Measured, and it is false**
(`_disposal/pythonw_stdout_probe.py`, run under `pythonw`):

```json
{"stdout_is_none": true, "stderr_is_none": true, "print_ok": true}
```

`sys.stdout` *is* `None` under `pythonw`, but CPython's `print` returns silently when the file
is `None`. So an unredirected windowless loop does not crash — it goes **silently
undiagnosable**, which is the same failure family and is why the `.out` redirect is still the
right fix, but the mechanism is loss of evidence, not death. Recorded because the wrong
mechanism would have sent the next reader hunting a crash that never happened.

## Residual finding (reported, not fixed)

`test_cvm_dt_voice.py` and `test_cvm_dt_clock.py` write the **production** heartbeat paths
under `live/logs/`. A test run therefore makes a dead worker look alive for `FRESH_S`. This is
a live false-green generator and it is *inside* this fence, but rewriting the assertions of a
45 KB / 33-row suite to redirect the heartbeat is a larger change than this postmortem's remit
and would risk the gate. Mitigation already in place: both `--status` paths now require
`registered` as well as `fresh`, so a freshened heartbeat alone can no longer produce `rc=0`.
Recommend a follow-up work order to point the suites at a temp root.

### ⚠ CORRECTION — the residual finding does NOT reproduce (2026-08-31, follow-up job)

The follow-up work order ran the measurement the finding above asserts, and the assertion is
**wrong as stated**. Every suite in `builds/cvm-dt/` and `builds/cvm-phone/` was run one at a
time with `live/logs/` fingerprinted `(size, mtime_ns, sha256)` immediately before and after
each one. **Twelve suites, zero production writes.** The two subject heartbeats hold the same
`mtime_ns` before the sweep, after the sweep, and after the full 95-row repo gate:

```
BEFORE  cvm_dt_clock_heartbeat.json mtime_ns=1787833578833948400 size=732
        cvm_dt_voice_heartbeat.json mtime_ns=1787842743336049600 size=559
AFTER   cvm_dt_clock_heartbeat.json mtime_ns=1787833578833948400 size=732
        cvm_dt_voice_heartbeat.json mtime_ns=1787842743336049600 size=559
```

Both suites already build a `tempfile.mkdtemp` root with its own sentinel, and
`run_selftest()` does the same (`cvm_dt.py:769`). Nothing in either fence resolves an implicit
root: `load_paths` takes the root by argument and `cosmos_paths` **refuses** when no install
record is given, so there is no code path by which a suite falls back to production.

The freshened values the finding quotes (`clock pid 14864`, `voice last_run_epoch 1788149970`)
are far more likely the postmortem's own hand-run `--once --root .../live` than its suites —
but which run produced them is **UNMEASURED** and is now unrecoverable, because the files have
since been restored to their 2026-08-27 content. The finding attributed a real observation to
the wrong cause.

**What was wrong is now also impossible.** Observing that the suites are clean today is weaker
than making a leak unshippable, so the follow-up added `cvm_test_guard.sandbox_heartbeats()`:
during a guarded run, every `write_heartbeat` / `acquire_lock` target that is not under the OS
temp dir is a typed `PROD_WRITE_REFUSED` **at the write**, naming the target — not a silent
production write found days later. `test_cvm_fence_isolation.py` proves the guard bites, proves
it does not over-refuse, and (`--sweep <PROD_LOGS_DIR>`) re-runs the whole fence under it. The
rule needs no notion of where production *is*, so it carries to a peer's cold machine unchanged.

## PROPOSALS — outside this fence, for the Orchestrator

### P1 — register the two tasks (`schtasks`; **not run by this agent**)

Emitted by `--register`, verbatim, unexecuted:

```
schtasks /create /tn "COSMOS CVM DT Clock" /tr "C:\Users\Papa\AppData\Local\Programs\Python\Python314\pythonw.exe V:\A\Ai\COSMOS\builds\cvm-dt\cvm_dt_clock.py --root V:\A\Ai\COSMOS\live --loop" /sc minute /f /mo 1
schtasks /create /tn "COSMOS CVM DT Clock Logon" /tr "C:\Users\Papa\AppData\Local\Programs\Python\Python314\pythonw.exe V:\A\Ai\COSMOS\builds\cvm-dt\cvm_dt_clock.py --root V:\A\Ai\COSMOS\live --loop" /sc onlogon /f
schtasks /create /tn "COSMOS CVM DT Voice" /tr "C:\Users\Papa\AppData\Local\Programs\Python\Python314\pythonw.exe V:\A\Ai\COSMOS\builds\cvm-dt\cvm_dt_voice.py --root V:\A\Ai\COSMOS\live --loop" /sc minute /f /mo 1
schtasks /create /tn "COSMOS CVM DT Voice Logon" /tr "C:\Users\Papa\AppData\Local\Programs\Python\Python314\pythonw.exe V:\A\Ai\COSMOS\builds\cvm-dt\cvm_dt_voice.py --root V:\A\Ai\COSMOS\live --loop" /sc onlogon /f
```

Note on the voice pair: `loop()` still calls `wait_for_ptt`, which reads the keyboard via
`msvcrt.kbhit()`. Under `pythonw` that raises `OSError`, which `wait_for_ptt` already catches
and degrades to a plain sleep (`cvm_dt_voice.py:439-440`) — so a windowless voice loop idles
and heartbeats correctly but can never PTT. That is the correct daemon behaviour (canon: the
mic never auto-starts); interactive PTT stays a foreground `cvm_dt.py voice --root …` run.
Registering the voice pair is therefore safe but delivers a heartbeat-only ear. **Recommend
registering the clock pair first**, and treating the voice pair as a separate decision.

### P2 — `cosmos/cosmos_own_clocks.py`: add id 18 / id 19 to `CLOCKS`

Insert after the id 17 entry (before the closing `)` at `:173`):

```python
    {
        "id": 18, "clock": "COSMOS CVM DT Clock",
        "cadence": "2s daemon (pull drain-fold) + 1-min self-heal",
        "script": "builds/cvm-dt/cvm_dt_clock.py",
        "task": "COSMOS CVM DT Clock", "logon": "COSMOS CVM DT Clock Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "cvm_dt_clock_heartbeat.json",
        "standup": None,
    },
    {
        "id": 19, "clock": "COSMOS CVM DT Voice",
        "cadence": "2s idle ear/mouth + 1-min self-heal",
        "script": "builds/cvm-dt/cvm_dt_voice.py",
        "task": "COSMOS CVM DT Voice", "logon": "COSMOS CVM DT Voice Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "cvm_dt_voice_heartbeat.json",
        "standup": None,
    },
```

⚠ Two caveats for the Orchestrator, not to be waved through:
1. `"standup"` is `None` for both. The `standup` dispatch at `cosmos_own_clocks.py:271`
   branches on known names; confirm a `None` standup is tolerated (id 18/19 have no in-repo
   standup entry point) or add one before merging.
2. `"script"` on ids 1–17 is a bare `cosmos/` filename; these two live under `builds/cvm-dt/`.
   Check how `script` is consumed before assuming a relative path is accepted.
3. Voice is **not a clock** — it consumes id 18 read-only and issues no clock id (its own
   docstring, `cvm_dt_voice.py:19-21`). Giving it registry id 19 is a *supervision* slot, not a
   clock-id grant. If that conflicts with the CLOCKS registry's meaning, supervise it elsewhere.

### P3 — `cosmos/cosmos_health_clock.py`: watch both heartbeats

```diff
--- a/cosmos/cosmos_health_clock.py
+++ b/cosmos/cosmos_health_clock.py
@@ PEER_HEARTBEATS = (
     "backup_clock_heartbeat.json",
     "ledger_verify_heartbeat.json",
+    "cvm_clock_heartbeat.json",
+    "cvm_dt_clock_heartbeat.json",
+    "cvm_dt_voice_heartbeat.json",
 )
```

`cvm_clock_heartbeat.json` (id 16) is included deliberately: it is registered and running, and
it was *also* unwatched. It survived on luck, not on observation.

### P4 — the class of defect, not the instance

A worker can today ship a `--register` that only *emits*, never be registered, and be watched
by nobody — and every local signal stays green. Both registries are hand-maintained lists that
a new worker must be manually added to, and nothing fails when it is not. Recommend a work
order to derive supervision from the workers themselves (each declares its task name and
heartbeat; the health clock reads that set) so "shipped but never scheduled" becomes
impossible rather than merely unlikely.
