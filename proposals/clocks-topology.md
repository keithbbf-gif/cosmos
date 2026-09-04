# CLOCKS topology — how many resident Python processes

**Work order:** `work_orders/drop/wo-20260904T120000.json` · **Issue:** #31 · **Lane:** Cursor Cloud Agent (Opus 5)
**Status: PROPOSE only (P10).** Nothing here is wired. No `schtasks` was created, changed, or deleted. Core `:8770` was not touched. `CLOCKS` is not shrunk by this PR. `PEER_HEARTBEATS` is not edited by this PR — the proposed change appears only as a diff inside this file.

**Answer in one line:** **four resident Python processes — Core plus three daemons** — down from Core plus fourteen. All twelve calendar `--once` rows stay exactly as they are. The reduction comes from deleting *interpreters*, not from deleting *duties*.

---

## 0. Evidence ledger — read this before you weigh anything below

I was asked to read a registry and thirty satellite files. **None of them exist in this repository.** This is not a fetch failure and not a stale checkout:

| Check | Result |
|---|---|
| `cosmos/cosmos_own_clocks.py` on `main` | absent |
| All 30 satellite paths in issue #31 | absent (0/30 present) |
| `docs/ORCHESTRATION.md`, `docs/AGENT_BRIEF.md`, `docs/AGENT_BOUNDARIES.md` | absent |
| Search across all 60+ remote branches | no match |
| Search across entire commit history (`git log --all --diff-filter=A`) | no match |
| `raw.githubusercontent.com/.../main/cosmos/cosmos_own_clocks.py` | HTTP 404 |
| `8791`, `--supervise`, `pythonw`, `PEER_HEARTBEATS`, `REQUIRED_DAEMONS`, `anti_loss_daemons`, `resume_gate`, `classify_pause` | zero matches anywhere in repo |

**Every file link in issue #31 is a 404.** The CLOCKS fleet exists only in the Windows live tree, which P10 forbids me to read or write.

So this proposal is built on three things I *can* stand behind, and I mark which is which throughout:

- **[CODE]** — read from this repository. The ancestor modules the clock tree was built on: `cosmos_sched.py`, `cosmos_lock.py`, `cosmos_health.py`, `cosmos_runner.py`, `cosmos_service.py`, `cosmos_up.py`, `cosmos_port_plan.py`, `cosmos_daemon.py`, `README.md`, `SOP.md`, `CRON.md`, `docs/WORK_ORDER_SOP.md`, and the committed work orders in `work_orders/drop/`.
- **[WO]** — the normative table and coupling list written by the owner in issue #31 and the work order. Cadences, vehicles, and coupling names are taken from there verbatim.
- **[ASSUMED]** — an inference I could not check. Every one carries the specific command that confirms or refutes it.

I did not read any Grok or COW proposal, any uncommitted local doc, or any CLOCKS collapse text. There is none in this clone to read.

### Finding 0 — the thing I found on the way in, which outranks the topology question

`README.md` [CODE]:

> **This repository is the live tree, not a copy of it.** Its predecessor kept a full duplicate of the mesh beside the working one, and the scheduler ran the duplicate for six days while every repair landed elsewhere. One tree, one truth.

Twenty-six registered clocks are executing code that is **not in the tree that declares itself the live tree**. The exact scar that sentence was written to prevent is open right now, at twenty-six-fold scale. Two consequences that bear directly on this work order:

1. **No reviewer on this repo can review the fleet.** Issue #31 asks GitHub critics to read thirty files and links to thirty 404s. Any critic who returns a confident verdict on those files did not read them.
2. **The collapse should not start until the fleet's source is in a tree a reviewer can diff.** Retiring a process whose source you cannot read means you cannot enumerate what it wrote, and step 4 below (heartbeat shims) depends on exactly that enumeration.

**Recommendation, ahead of any collapse:** land the 26 scripts + `cosmos_own_clocks.py` + `docs/ORCHESTRATION.md` in this repo, under `.gitignore`'s existing code-tracked / state-ignored split. This is a read-and-copy of code (not live state, not ledgers, not secrets), so it does not conflict with deny-by-default. Until then, everything below marked **[ASSUMED]** stays assumed.

---

## 1. How many resident Python processes, and what each does

### The rule I am applying is the owner's, not mine

From `work_orders/drop/wo-20260902T194500.json` [CODE]:

> "Design the query-handling addition to the existing single `cosmos_daemon.py` (**no second process**, no new window, no GUI flash) … Then evaluate whether separate lightweight daemons are better for isolation if one crashes, but **default to single-daemon extension unless isolation clearly wins**."

That is the standing rule, and it puts the burden of proof on *each additional process*. From `README.md` [CODE]:

> **Fully multithread capable by design. Concurrency is a property of the scheduler, not a flag on a script.**

The 26-clock fleet inverts that: it makes concurrency a property of **process count**. Twenty-six jobs that need to run independently became twenty-six interpreters, when the tree's own charter says independence is the scheduler's job. That is the whole defect in one sentence, and it is an architectural regression against a written requirement — not a matter of taste.

**Isolation clearly wins exactly twice.** I can justify three daemons and not a fourth:

1. **A supervisor may not share a fault domain with what it restarts.** Health `--supervise` is the only in-tree restarter of live Core `:8770` [WO]. Collapse it into the same process as the work it watches and a single crash takes both the fleet *and* Core's restarter. Fourteen processes are too many, but one is fewer than the problem allows.
2. **An executor of foreign work may not share a fault domain with the observer that reports on it.** `cosmos_runner` spawns arbitrary child commands under `run_tree_killed` with `timeout_s` defaulting to 1800 [CODE: `cosmos_runner.py:137-181`]; bucket workers dispatch to paid external rails [WO]. If the observer lives in that process, a wedged 30-minute child means the heartbeat stops — and the fleet reports *dead* when it is merely *busy*, or worse, reports nothing while looking fine. `cosmos_health.py` exists specifically to close that defect class [CODE]:

   > a checker that cannot go RED … a checker that cannot go GREEN

Everywhere else, single-daemon extension wins, and I take it.

### The four resident processes

| # | Process | Vehicle | Absorbs (CLOCKS ids) | Duty |
|---|---|---|---|---|
| **P0** | **COSMOS Core** | `cosmos.py serve --port 8770`, own `schtasks /sc onlogon` | *(not a CLOCKS row)* | The `:8770` API surface. `ThreadingHTTPServer` [CODE: `cosmos_service.py:639-652`]. **Never stopped by this plan.** |
| **P1** | **`cosmos_sentinel`** | resident, 2s tick, one ONLOGON entry | **1, 6** | Supervision and truth. |
| **P2** | **`cosmos_tick`** | resident, 1s base tick | **2, 16, 25** | Short observational ticks. **Can disappear — see below.** |
| **P3** | **`cosmos_work`** | resident, event-driven + 5s floor | **3, 14, 15, 17, 20, 21, 22, 26** | The five claim surfaces. |

Accounting: 2 + 3 + 8 = 13 resident rows absorbed, plus row 10 abandoned outright = **all 14 resident rows**. The other 12 are calendar and unchanged (§2).

**P1 — `cosmos_sentinel`.** Restarts Core `:8770` when it stops answering (inherits row 6's `--supervise`). Restarts P2 and P3 on stale heartbeat — the thing ONLOGON structurally cannot do. Publishes the single fleet roll-up (expected roster vs observed). Owns the pause/resume gate and is the sole unlinker of `resume_gate` (inherits row 1's WD2 duty).
Constraints, which are the point of it: **stdlib imports only; no foreign work; no subprocess except a fixed allow-list of restart commands; no paid rail; no claim surface.** A supervisor with a dependency graph is a supervisor that can fail to start. It must be the most boring process on the box.

**P2 — `cosmos_tick`.** Collector, CVM clock, CVM DT clock. Never claims work, never spawns a child, never blocks past one tick; a job that overruns its per-job deadline is *reported*, not retried — `cosmos_sched`'s report-never-retry discipline [CODE: `cosmos_sched.py:157-170`].

**P3 — `cosmos_work`.** One lane thread per claim surface: `queue`, `dispatch`, `work_order`, `buckets`, `critique`, plus `intake` for SGH drop ingest. Every claim goes through the ledger's optimistic-concurrency path. Every child runs under `run_tree_killed` with a hard timeout. At startup it takes an `Arbiter` lease per surface, so an accidental second copy refuses `HELD` instead of double-claiming [CODE: `cosmos_lock.py`].

### Why threads, and not five more interpreters

The work these lanes do is `subprocess.Popen` + wait [CODE: `cosmos_platform.py:70-95`]. That is **I/O wait, not CPU**, so the GIL is irrelevant to it, and the actual concurrency lives in the *child* processes — which are separate OS processes no matter what. `cosmos_service` already runs `ThreadingHTTPServer` in production, so threads are an accepted in-tree idiom, not a new one.

**A resident Python process is not the unit of concurrency. The child process is.** The 26-daemon fleet paid ~15–30 MB of interpreter baseline, a Windows working set, and a wakeup timer *per job* to buy concurrency it already had for free. You do not need five interpreters to run five subprocesses.

### The one lever that changes the answer

**P2 exists only if the CVM 2s cadence is real.** Its other duty, the collector, has no sub-minute requirement — `anti_loss_daemons` demands freshness under 180s [WO], which a 60s calendar `--once` meets with a factor of three in hand. So:

> If rows 16 and 25 do not own a real-time interactive surface with a latency budget under ~250ms, **P2 should not exist**: the collector becomes a 60s calendar `--once` and the CVM ticks follow. That is **two daemons plus Core — three resident processes.**

This is the single largest remaining decision and I cannot make it from this clone. **[ASSUMED]** that CVM is voice-adjacent and latency-critical, because `PEER_HEARTBEATS` carries `cvm_dt_voice_heartbeat.json` [WO] and `cosmos_voice.py` is the largest module in the tree at 33 KB [CODE].
**Check that settles it:** `grep -nE "sleep|interval|latency|voice|speak|listen|record" cosmos/cosmos_cvm_clock.py builds/cvm-dt/cvm_dt_clock.py`. If neither drives an audio or input surface, drop P2.

### What this costs and what it buys — stated as estimate, not measurement

**[ASSUMED]** ~15–30 MB RSS per idle CPython interpreter, so 14 loops ≈ **250–400 MB** in interpreter baseline alone before any working set. The 0.75s cDeck feed wakes roughly **115,000 times per day**; all 14 loops together are order 10⁵–10⁶ wakeups/day of scheduler churn.

I did not measure this and neither should you take it on faith. **Measure before and after:**
```powershell
Get-Process python,pythonw | Select-Object Id,Name,WS,CPU |
  Sort-Object WS -Descending | Format-Table -AutoSize
```
The proposal is falsified if the 14 loops are not materially above the 3 daemons on total WS and CPU.

---

## 2. Which CLOCKS rows stay calendar `--once`

**All twelve of them. Unchanged. Zero edits.**

| id | clock | cadence | disposition |
|---|---|---|---|
| 4 | Motif Driver | 15m | PRESERVED |
| 5 | Mesh Discovery | hourly | PRESERVED |
| 7 | Rails Prober | 1m | PRESERVED |
| 8 | Spend Meter | 1m | PRESERVED |
| 9 | Drive Meter | 1m | PRESERVED |
| 11 | Backup | 4× daily | PRESERVED |
| 12 | Ledger Verify | 5m | PRESERVED |
| 13 | Index | 1m | PRESERVED |
| 18 | Resession | 1m | PRESERVED |
| 19 | Askmine | hourly | PRESERVED |
| 23 | NEW-AI Scout | hourly | PRESERVED |
| 24 | Prepaid Orchestrator | 1m | PRESERVED |

**The calendar rows were never the problem.** Every one of them is already correct: fire, run, exit, hold nothing. The problem is the fourteen sub-minute rows that each took an interpreter.

The governing rule, which the twelve already satisfy:

> **cadence ≥ 60s → calendar `--once`. cadence < 60s → a tick inside a resident process. Unbounded duration → a job on the queue, never a clock at all.**

And there is a reason to prefer `--once` beyond tidiness. `README.md` names among its founding failures [CODE]:

> a scheduler executing eight-day-old code

**Every resident loop is a runtime-binding hazard.** A `pythonw --loop` started at logon is pinned to whatever was on disk at logon; a daemon up for eight days *is* that failure, by construction. A `--once` task re-reads its source from disk on every fire and therefore cannot execute stale code. This is why the collapse must reduce residents to the smallest set that latency actually requires — and why each of P1/P2/P3 should carry a version stamp and self-restart when the on-disk source hash changes. Otherwise the collapse trades 14 small runtime-binding hazards for 3 large ones.

One addition, not a removal: give **row 2 (Collector)** a calendar `--once` **backstop** at 120s that no-ops when P2's heartbeat is fresh. `anti_loss_daemons` guards data loss [WO]; a duty that load-bearing should not have exactly one vehicle. This costs no resident process.

---

## 3. Which loops should die, and why

Using the tree's own four dispositions [CODE: `cosmos_tools.py:27` — `PRESERVED / ADAPTED / REPLACED / ABANDONED`], and its own rule from `cosmos_port_plan.py`: *"a successor that does not exist is a claim, not a port."*

| id | clock | disposition | successor | why |
|---|---|---|---|---|
| 1 | Activity / WD2 | REPLACED | P1 | Resume-gate duty is control-plane. **The only thing that can lift a pause must not live in a process that can be wedged by the work it paused.** |
| 2 | Collector | REPLACED | P2 (+ calendar backstop) | Observer. 30s cadence exceeds the 180s freshness it must satisfy. |
| 3 | Runner | REPLACED | P3 `queue` lane | Merges with row 15 — see below. |
| 6 | Health | REPLACED | P1 | The `--supervise` duty survives intact and gains P2/P3 restart. |
| **10** | **cDeck Feed** | **ABANDONED** | Core `/api/v1` + P1 roll-up | **See below — this one is a defect, not a process.** |
| 14 | Dispatcher | REPLACED | P3 `dispatch` lane | 5s poll → OS file-watch. |
| **15** | **Runner Pool** | **ABANDONED** (both duties) | P3 `queue` lane / P1 | **See below.** |
| 16 | CVM Clock | REPLACED | P2 | Conditional on §1's lever. |
| 17 | Work-Order Runner | REPLACED | P3 `work_order` lane | Documented ~15s pickup path [CODE: `docs/WORK_ORDER_SOP.md:63`] preserved as a latency budget, not as a process. |
| 20 | CritConsumer | REPLACED | P3 `critique` lane | |
| 21 | Grok Bucket Worker | REPLACED | P3 `buckets` lane | Two rails, one lane; `cosmos_rails` already models rails as adapters [CODE]. |
| 22 | GEM Bucket Worker | REPLACED | P3 `buckets` lane | Same. |
| 25 | CVM DT Clock | REPLACED | P2 | Also: it lives under `builds/`. A build-tree clock resident in production is worth a separate question. |
| 26 | SGH Drop Ingest | REPLACED | P3 `intake` lane | Network-facing (GitHub → live bucket) [CODE: `docs/WORK_ORDER_SOP.md:63`]. Needs the timeout discipline of P3, not a bare loop. |

### The three that die on merit, not on headcount

**Row 15, Runner Pool — abandon both duties.** It is a *second claimer* of `live/queue` alongside `cosmos_run`, and a *second supervisor* alongside Health.
- Two claimers on one surface is not redundancy, it is a race. The in-tree `Scheduler.claim_next()` survives it — the loser gets a typed `LOST_CLAIM` [CODE: `cosmos_sched.py:98-122`] — but that only holds if *both* claim through the ledger. The other claim path in this tree does not: `cosmos_daemon.claim()` mutates JSON in place with `os.replace` on the same path, no lock, no head check [CODE: `cosmos_daemon.py:77-86`]. Two processes on that path is last-writer-wins. Which path row 15 uses is **[ASSUMED]** and must be checked: `grep -n "claim_next\|os.replace\|expect_head_seq" cosmos/cosmos_pool.py cosmos/cosmos_run.py`.
- Two supervisors is how you get restart storms — both observe one failure, both restart, and you have two Cores.

**Row 10, cDeck Feed — abandon the process outright.** Three independent reasons:
1. **The tree already ruled on it.** `cosmos_port_plan.py` [CODE: lines 61-64]: `bts_kdash_feed` → REPLACED by `cosmos_service + kdash`, reason: *"KDash becomes an API projection client of cosmos_service /api/v1; **no file-reading dashboard**, so writer-splits-from-launcher cannot recur."* A 0.75s daemon writing files for a deck to glob is the exact shape that ruling abandoned. It came back.
2. **It is a checker that cannot go red.** Fleet staleness is measured on *the feed's own age* [WO], so the feed can only ever report on itself. Kill eleven peers and the deck stays green — the glob just returns fewer files. This is the `cosmos_health` C-46 defect class verbatim [CODE].
3. **0.75s is a number, not a requirement.** No human reads a dashboard at 1.3 Hz. The deck should *pull* from Core `:8770`, which is already resident and already serving.

**The 13 ONLOGON `--loop` relaunches — abandon as a class.** ONLOGON is not supervision. It fires once, at logon, and never again: a 03:00 crash stays dead until the next logon, and on a workstation that stays logged in for a week that is a week of silent absence. Worse, an ONLOGON relaunch landing on top of a surviving process gives you two claimers on one surface — the failure in row 15, generalised across thirteen entries.

Replace with **one** ONLOGON entry for P1; P1 starts and restarts P2 and P3. And note what that buys, given the live registration state recorded in `work_orders/drop/wo-20260902T191500.json` [CODE]:

> "C2 machine 1-min names are mostly unregistered (Watchdog2 registered=false, logon_registered=true; only Work-Order Runner and SGH Drop Ingest 1-min registered=true)"

The fleet is **already** in a half-registered state where the ONLOGON entry is the only live vehicle for some rows. That is not a stable base to add to.

> **Safety property, and it is the one that protects Core:** P0 keeps its **own independent** `COSMOS Serve` ONLOGON entry — the existing in-tree pattern [CODE: `cosmos_up.py:199-220`, `TASK_NAME = "COSMOS Serve"`, `/sc onlogon /rl highest /f`]. **Core's *start* path never routes through P1.** P1 only ever *restarts* Core. A P1 misconfiguration then costs you the clocks, never Core.

**Deletion is out of bounds.** P10 forbids `schtasks /delete`. Every retirement below is `schtasks /change /tn "<name>" /disable` — reversible with `/enable`, and the entry stays visible for audit.

---

## 4. What couplings break, and the file-level change list

Four separate rosters currently answer the question *"who is supposed to be alive?"* and **none of them agree**: `PEER_HEARTBEATS` (hardcoded names, and it carries `cvm_dt_voice_heartbeat.json`, which is not a CLOCKS row), the cDeck glob `logs/*heartbeat*.json`, `REQUIRED_DAEMONS`, and `anti_loss_daemons` [WO]. `README.md` names this failure class directly [CODE]: *"a handoff asserting three different counts of the same fact."* Here it is four.

The collapse breaks all four at once, because heartbeat files are named after *processes* and the processes are what is going away.

### 4.1 `PEER_HEARTBEATS` — `cosmos_health_clock.py`

**Breaks:** most named files stop being written; P1 reports a permanently red fleet — the "checker that cannot go GREEN" defect [CODE: `cosmos_health.py:7-9`]. It is also a hardcoded name list, which `README.md` forbids outright [CODE]: *"**No hard-coded paths.**"*

**Fix:** derive the roster from the `CLOCKS` registry plus one explicit extras list for non-CLOCKS peers, so the registry and the watcher cannot drift.

**Proposed diff — not applied in this PR, per the work order.** The `-` lines are the *shape described* in issue #31, **[ASSUMED]**, since the file is not in this repo. Treat this as intent, and re-cut it against the real file:

```diff
--- a/cosmos/cosmos_health_clock.py
+++ b/cosmos/cosmos_health_clock.py
-# The roster, by hand. Every rename here is a silent red.
-PEER_HEARTBEATS = (
-    "cosmos_watchdog2_heartbeat.json",
-    "cosmos_collector_heartbeat.json",
-    "cosmos_runner_heartbeat.json",
-    "cosmos_cdeck_feed_heartbeat.json",
-    "cosmos_dispatcher_heartbeat.json",
-    "cosmos_pool_heartbeat.json",
-    "cosmos_cvm_heartbeat.json",
-    "cvm_dt_voice_heartbeat.json",
-    ...
-)
+# ROSTER IS DERIVED, NEVER TYPED (README: "No hard-coded paths"). Two predicates,
+# kept apart because they fail differently: a process that must be RESIDENT, and a
+# duty that must have RUN RECENTLY. Conflating them is why an hourly --once job
+# ended up on a daemon liveness list.
+from cosmos_own_clocks import CLOCKS
+
+# Resident processes: absence is RED immediately.
+RESIDENT_PEERS = {
+    "cosmos_sentinel_heartbeat.json": 10,     # P1 - self
+    "cosmos_tick_heartbeat.json":     10,     # P2
+    "cosmos_work_heartbeat.json":     30,     # P3 (a lane may be mid-child)
+}
+
+# Calendar duties: absence is RED only past the duty's own cadence x tolerance.
+# Derived from the registry, so a CLOCKS edit cannot silently desync the watcher.
+FRESH_DUTIES = {
+    c.heartbeat: c.cadence_s * 3 for c in CLOCKS if c.vehicle == "once"
+}
+
+# Peers that are NOT CLOCKS rows. Explicit, so "not in CLOCKS" stays a real signal
+# instead of a thing you remember. cvm_dt_voice was on the old list with no row.
+EXTRA_PEERS = {
+    "cvm_dt_voice_heartbeat.json": 30,
+}
+
+# Retired names, kept writable as shims during the collapse and asserted EMPTY at
+# the end of it. A shim nobody removes is the next stale roster.
+COLLAPSE_SHIMS = {
+    "cosmos_collector_heartbeat.json",        # -> P2 duty=collector
+    "cosmos_runner_heartbeat.json",           # -> P3 lane=queue
+    "cosmos_watchdog2_heartbeat.json",        # -> P1 duty=activity
+}
```

### 4.2 cDeck feed glob `logs/*heartbeat*.json`

**Breaks silently, which is the dangerous kind.** A glob is count-free and order-free: it cannot distinguish *"peer X is missing"* from *"peer X was never there."* After the collapse it returns 3 files instead of 15 and the deck looks **healthier, not different**. Combined with staleness measured on the feed's own age, a fleet that lost eleven processes still shows green.

**Fix:** the deck compares a **declared roster against observed**, the expected-vs-observed shape `HealthBoard` already uses [CODE: `cosmos_health.py:76-113`]. Then per §3, the deck pulls that roll-up from Core `/api/v1` rather than globbing at all.

> Note `.gitignore:28` is `*_heartbeat*.json` [CODE] — heartbeats are correctly untracked. The roster must therefore be declared **in code**, not inferred from what happens to be on disk.

### 4.3 `REQUIRED_DAEMONS` — `cosmos_index.py`

`REQUIRED_DAEMONS = {runner, collector, mesh_discovery}` [WO]. **This is already wrong today, before any collapse:** `mesh_discovery` is row 5, an **hourly `--once`** job. It is on a *daemon liveness* list while being, by design, not resident. The predicate it actually wants is "ran within the hour."

**Breaks:** after the collapse there is no `runner` process and no `collector` process either, so 2 of 3 rows go red for the same reason.

**Fix:** split the predicate, exactly as in the diff above — `REQUIRED_RESIDENT` (liveness) vs `REQUIRED_FRESH` (recency, with each duty's own cadence).

### 4.4 `anti_loss_daemons` — `cosmos_principles.py`

`collector` **and** `cosmos_runner_heartbeat.json`, both `< 180s` [WO]. Both filenames vanish.

**Fix:** assert on the **duty**, not the filename. P2 and P3 write `{"duty": "collector", "last_ok_epoch": ...}` and the predicate becomes *"the collector duty completed within 180s"* — which stays true across any future re-homing. This is the load-bearing one: it guards data loss, so it gets both the shim (§5 step 4) *and* the calendar backstop (§2).

### 4.5 Logon relaunch

Covered in §3. Thirteen entries → one, with Core's start path deliberately kept independent.

### 4.6 The five claim surfaces

| surface | claimers today [WO] | after |
|---|---|---|
| `live/queue` | **two** — `cosmos_run` *and* `cosmos_pool`, both `claim_next` | P3 `queue` lane, one |
| dispatch bucket | 1 | P3 `dispatch` lane |
| work-order bucket | 1 | P3 `work_order` lane |
| `live/buckets/{grok,gem}` | 2 (one per rail) | P3 `buckets` lane, per-rail adapters |
| critique inbox | 1 | P3 `critique` lane |

**Breaks:** any operator habit of "start another pool member for throughput." Throughput now comes from lane concurrency and child processes, not from more claimers.

**Gains:** every surface takes an `Arbiter` lease, so a second claimer is refused `HELD` [CODE: `cosmos_lock.py`] instead of racing. And the non-atomic mail-drop claim [CODE: `cosmos_daemon.py:77-86`] is retired in favour of the ledger claim that already handles the race [CODE: `cosmos_sched.py:98-122`].

### 4.7 Pause is not one function

Copies in WD2, `resession.classify_pause`, `pool.is_paused` [WO]; and `SOP.md:23` documents a `control/PAUSE.flag` check that **no Python in this repo implements** [CODE — grep for `PAUSE.flag`, `resume_gate`, `classify_pause` returns zero matches].

Two of the three copies disappear by construction (pool is abandoned, WD2 folds into P1). The third — `resession`, row 18, a calendar job — survives and will drift alone.

**Fix:** one `cosmos_pause` module exporting `classify_pause()`; P1 and resession both import it. **Ordering constraint, and it is not optional:** P1 must be the `resume_gate` unlinker *before* WD2 stops. If the only process that can lift a pause is inside the set you just paused, you have deadlocked the fleet and the fix is a manual file delete on a machine you may not be at.

### 4.8 The stale watchdog — `COSMOS_Serve_Watchdog` → `trylive:8791`

**This is a live hazard and it is first in the collapse order.** `8791` and `trylive` appear **nowhere in this repository** [CODE — zero grep matches; `.gitignore:69` ignores `/trylive/`]. So a registered Windows task is pointed at a port no code in the tree binds, inside a tree the repo deliberately ignores.

Two possibilities, and they need different responses:
- **Inert** — 8791 answers nothing, the task no-ops. Harmless, still disable it.
- **Live** — it resurrects a *second* Core on a *second* tree. Then you have two Cores fighting over one live root, which is **"the scheduler ran the duplicate for six days"** [CODE: `README.md`] recurring, with a supervisor actively keeping the duplicate alive.

**Do not collapse anything until this is resolved.** Confirm with `Test-NetConnection -ComputerName localhost -Port 8791` and `schtasks /query /tn "COSMOS_Serve_Watchdog" /v /fo LIST`. If 8791 answers, that is an incident, not a step.

### 4.9 File-level change list

| File | Change |
|---|---|
| `cosmos/cosmos_own_clocks.py` | **No shrink.** Add `vehicle`, `owner_process`, `heartbeat`, `cadence_s` fields per row. The tuple stays 26 long; the registry becomes the roster everything else derives from. |
| `cosmos/cosmos_health_clock.py` | Derive `PEER_HEARTBEATS` (§4.1 diff). Split resident vs fresh. Add P2/P3 restart. Keep `--supervise` semantics for Core byte-for-byte. |
| `cosmos/cosmos_index.py` | `REQUIRED_DAEMONS` → `REQUIRED_RESIDENT` + `REQUIRED_FRESH`. |
| `cosmos/cosmos_principles.py` | `anti_loss_daemons` asserts on `duty`, not filename. |
| `cosmos/cosmos_cdeck_feed.py` | Roster diff, not glob; then retire in favour of Core `/api/v1`. |
| `cosmos/cosmos_pause.py` | **New.** The single `classify_pause()`. |
| `cosmos/cosmos_resession.py` | Import `cosmos_pause`; drop the local copy. |
| `cosmos/cosmos_sentinel.py` | **New — P1.** Absorbs `cosmos_health_clock` + `cosmos_watchdog2`. |
| `cosmos/cosmos_tick.py` | **New — P2**, conditional on §1's lever. |
| `cosmos/cosmos_work.py` | **New — P3.** Lane host; leases per surface. |
| `cosmos/cosmos_run.py`, `cosmos_pool.py`, `cosmos_dispatcher_daemon.py`, `cosmos_work_order_run.py`, `cosmos_crit_consumer.py`, `cosmos_{grok,gem}_bucket_worker.py`, `cosmos_sgh_drop_ingest.py` | Keep the *work* function; delete the `--loop` `main()`. Each becomes a module P3 calls, still runnable `--once` for debugging. **The duty is preserved; only the interpreter is removed.** |
| `cosmos/cosmos_collector.py`, `cosmos_cvm_clock.py`, `builds/cvm-dt/cvm_dt_clock.py` | Same, called by P2. |
| `docs/ORCHESTRATION.md` | Rewrite the matrix as target-state; keep today's as a dated appendix. |

---

## 5. Collapse order that does not take Core `:8770` down

**The invariant, held at every single step:**

> At all times, **at least one live process is able to restart Core `:8770`**, and Core itself is never stopped. Two restarters is a recoverable condition. Zero restarters, even for one step, is not.

Never in this order, at any step: stopping Core · `schtasks /delete` · lifting HOLD/PAUSE · writing `V:\Ai` · turning `ANTHROPIC_OFF` off.

| # | Step | Invariant held by | Gate before the next step |
|---|---|---|---|
| **0** | **Inventory, change nothing.** Record every CLOCKS row → schtasks entry name, PID, heartbeat filename. This *is* the expected roster §4.2 needs. | existing Health `--supervise` | Roster is complete and every heartbeat file has a named owner. |
| **1** | **Reconcile `COSMOS_Serve_Watchdog` → `trylive:8791`** (§4.8). Confirm Health `--supervise` is running and is the sole restarter of `:8770`, then `/disable` — never `/delete`. | existing Health | `:8791` confirmed not answering. If it answers, **stop — that is an incident.** |
| **2** | **Land P1 in observe-only.** It writes its heartbeat and roll-up. `--supervise` **stays** with the old health clock. Two observers, one restarter. | existing Health | Soak. P1's verdict matches the old clock on every tick, **including at least one deliberately induced red** — a checker that has never gone red has not been tested [CODE: `README.md`]. |
| **3** | **Hand over the Core supervise duty.** Start P1 `--supervise` **first**, stop the old health clock **second**. Order is not negotiable. | brief overlap: both | Both guard on "is `:8770` answering" *and* take the `Arbiter` lease on resource `core-restart` before acting, so the loser refuses `HELD` and the overlap cannot double-restart [CODE: `cosmos_lock.py`]. |
| **4** | **Shim the heartbeats.** P1/P2/P3 write the **legacy filenames** in addition to their own (§4.1 `COLLAPSE_SHIMS`). Nothing is removed yet. | P1 | `REQUIRED_DAEMONS`, `anti_loss_daemons`, and the cDeck glob all still see what they expect. |
| **5** | **Collapse the observers.** Start P2. Soak. Stop the old loops **one at a time**, confirming the deck stays green after each. `/disable` each ONLOGON entry. **cDeck feed last** — it is what you are watching the collapse through, so do not blind yourself mid-procedure. | P1 | Deck green after every individual stop. |
| **6** | **Collapse the executors, one claim surface at a time.** Per surface: P3 takes the lease → the old daemon's next claim refuses `HELD` → stop the old daemon → `/disable` its entry → confirm the surface still drains. Order: `critique` → `buckets` → `dispatch` → `work_order` → `queue`. Lowest blast radius first. | P1 | Each surface drains a test item before moving on. |
| **6a** | **`live/queue` specifically** — it is the double-claimed one. Retire **`cosmos_pool`'s claim first**, confirm `cosmos_run` still drains **alone**, *then* move the lane to P3, *then* retire `cosmos_run`. **Never both at once**, or you cannot tell which one was doing the work. | P1 | Queue drains with exactly one claimer at each sub-step. |
| **7** | **Move the pause gate.** Land `cosmos_pause`. P1 becomes the `resume_gate` unlinker **while WD2 is still up as a fallback**. Then pause and resume once, deliberately, to prove it. Only then stop WD2. | P1 | A real pause/resume round-trip succeeded with P1 driving. |
| **8** | **Flip the readers, then drop the shims.** Update `PEER_HEARTBEATS` / `REQUIRED_DAEMONS` / `anti_loss_daemons` to the new roster. **Prove each can still go RED** by inducing a failure. Only then stop writing the legacy shim names. | P1 | Every consumer demonstrated red, then green. |
| **9** | **Retire the deck's glob.** Point cDeck at Core `/api/v1` (§3). Last, because it is the observation surface. | P1 | Deck matches P1's roll-up. |

**Rollback, at every step:** `schtasks /change /tn "<name>" /enable` and start the old loop. Because nothing is ever deleted, every step above is reversible — which is the reason `/disable` is worth the extra audit noise.

---

## 6. What would prove me wrong

Stated up front, because the tree's rule is *"a check that cannot fail is not a check"* [CODE: `README.md`]:

| Claim | Falsified if | Command |
|---|---|---|
| 14 loops cost materially more than 3 | total WS/CPU is comparable | `Get-Process python,pythonw \| Measure-Object WS -Sum` |
| CVM has no real-time surface (→ drop P2) | either CVM file drives audio/input | `grep -nE "voice\|speak\|listen\|audio\|record" cosmos/cosmos_cvm_clock.py builds/cvm-dt/cvm_dt_clock.py` |
| Lane threads suffice for 5 surfaces | any lane does sustained CPU work rather than waiting on a child | `grep -n "Popen\|run_tree_killed\|subprocess" <each surface daemon>` |
| Sub-second polling is unnecessary | no OS file-watch available, so polling is the only vehicle | `python -c "import watchdog; print(watchdog.__version__)"` — [CODE: `cosmos_sched.py:180-207`] already prefers `ReadDirectoryChangesW` and *reports* the poll fallback as a recorded degradation |
| Row 15 is a genuine double-claim | pool claims a different surface than run | `grep -n "claim_next" cosmos/cosmos_pool.py cosmos/cosmos_run.py` |
| `8791` is dead | it answers | `Test-NetConnection localhost -Port 8791` |

## 7. Open questions I could not close from this clone

1. **The 26 satellites are not in this repo** (§0). Everything marked **[ASSUMED]** rests on issue #31's prose.
2. **Does CVM own a real-time surface?** The single lever between 3 and 4 resident processes (§1).
3. **Is `trylive:8791` live?** Blocks step 1 (§4.8).
4. **Does `cosmos_pool` claim via the ledger or via the non-atomic file path?** Determines whether the double-claim is currently *contained* or *silently corrupting* (§3).
5. **What writes `cvm_dt_voice_heartbeat.json`?** It is in `PEER_HEARTBEATS` and is not a CLOCKS row — so either the registry is missing a row or the watcher is watching a ghost.
6. **`standup_all` and `logon_specs` semantics.** I could not read `cosmos_own_clocks.py`, so I cannot say whether `standup_all` is idempotent — which matters, because step 5 and step 6 depend on stopping loops individually without a standup re-launching them behind you.

---

**Recommendation:** resolve §0 (get the fleet into a reviewable tree) and question 2 (the CVM lever) before step 1. Neither is a large change, and both are prerequisites for anyone — human or agent — to check this work rather than take it on trust.
