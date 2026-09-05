# ORCHESTRATION — permanent COSMOS Windows clocks

**Consumer:** COSMOS / COW / Keith. Governance. Encoded 2026-08-25, matrix
measured 2026-08-25T23:19-05.

The orchestration layer is a **permanent feature of COSMOS**, not a session event.
The clock is **Windows Task Scheduler** (`schtasks`) plus detached Python daemons
for anything faster than the 1-minute schtasks floor. These tasks survive reboot
and run whether or not Claude, Grok, Cursor, or any other app is open. They are
**not** Cowork `/loop` tasks, not Grok Build `/loop`, and not `cosmos.py serve`.

**Collapse target (Keith 2026-09-04, not live):** one 15s Pulse + one Runner
Pool + calendar `--once` schtasks, optionally Health as a third FAST process
for `:8770` supervise. See **CLOCKS collapse** at the bottom of this file.
Do not shrink the 26-row `CLOCKS` matrix or `/delete` tasks until that
section’s phases. HOLD stays.

Canon (CLAUDE.md): *The Windows clock carries the overhead. Claude makes only
the sparse decisions; the OS runs the machine.*

**COSMOS uses NO BTS.** Own clocks, own runner, own queue
(`V:\A\Ai\COSMOS\live\queue`). Task names are `COSMOS <x>`. No `bts_*` import
in the clock satellites. Core (`kernel` / `ledger` / `sched` / `service`) is
unchanged — clocks are satellites that **read** core and write only their own
heartbeat + projection.

Standup: `py -3.14 cosmos\cosmos_own_clocks.py --root V:\A\Ai\COSMOS\live --standup`

---

## Clock cadence rubric (Keith — found and encoded)

**This is the rubric.** COSMOS does not invent cadences.

| tier | interval | vehicle | used for |
|---|---|---|---|
| **FAST** | **0.5 s – few seconds** | **detached Python daemon** (schtasks cannot express this) | cDeck display + OS dynamics (health/heartbeat, live feed) |
| **NO-IDLE** | **15 s** (Keith 2026-08-25 never-idle ceiling) | **detached Python daemon** + 1-min schtask self-heal + onlogon relaunch | Watchdog2 / Activity Clock. Collector stays ~30 s |
| **SLOW** | **~1 min** (schtasks floor) | **schtasks** | hard-drive meters on massive drives; spend; rails prober; Runner/Collector/Health/cDeck self-heal |
| **MOTIF** | **15 min** | schtasks `/sc minute /mo 15` | mechanical Motif next-stage drop |
| **SLOWER** | **hourly** | schtasks `/sc HOURLY` | mesh-hands discovery |
| **BACKUP** | **4× daily** (07/11/19/23) | schtasks DAILY | backup |
| **VERIFY** | **5 min** | schtasks `/sc minute /mo 5` | ledger chain verify |

`schtasks` repeating interval **cannot go below 1 minute**. Anything faster
**must** be a detached Python daemon (the `--loop` process sleeps; a 1-min
schtask is only the self-heal / logon relaunch).

**Rule of placement:** if the thing is a display or an OS dynamic, it is a
detached daemon at 0.5 s–few-s. If it hammers a massive drive (SMART, free
space, tree walk), it is schtasks at ~1 min — never a 0.5 s loop. If it is
the no-idle assigner, it is a 15 s daemon because 1 min is too slow for
"never idle > 15 s".

Keith 2026-08-22 security ruling: run **only when the user is logged on** (no
stored password). `ONSTART` is the **wrong** trigger: the runtime root is
`V:\A\Ai\COSMOS\live` and `V:` is a user-session volume.

---

## Matrix (measured 2026-08-25T23:19-05)

| # | clock | cadence | script | task name | REGISTERED? | heartbeat |
|---|---|---|---|---|---|---|
| 1 | **COSMOS Activity Clock** (Watchdog2) | 15s daemon | `cosmos_watchdog2.py --loop` | `COSMOS Watchdog2` | **YES** (1-min self-heal). Logon: **NO** — Keith cmd below | `live\logs\watchdog2_heartbeat.json` |
| 2 | **COSMOS Collector** | 30s daemon | `cosmos_collector.py --loop` | `COSMOS Collector` | **YES**. Logon: **NO** — Keith cmd | `live\logs\collector_heartbeat.json` |
| 3 | **COSMOS Runner** | 15s loop / 1-min self-heal | `cosmos_run.py --loop` | `COSMOS Runner` | **YES**. Logon: **NO** — Keith cmd | `live\logs\cosmos_runner_heartbeat.json` |
| 4 | **COSMOS Motif Driver** | 15m | `cosmos_motif_driver.py --once` | `COSMOS Motif Driver` | **YES** | `live\logs\motif_driver_heartbeat.json` |
| 5 | **COSMOS Discovery** | hourly | `cosmos_discover.py --once` | `COSMOS Mesh Discovery` | **YES** | `live\logs\mesh_discovery_heartbeat.json` |
| 6 | **COSMOS Health** | ~2s daemon | `cosmos_health_clock.py --loop` | `COSMOS Health` | **YES**. Logon: **NO** — Keith cmd | `live\logs\health_clock_heartbeat.json` |
| 7 | **COSMOS Rails Prober** | 1m | `cosmos_rails_prober.py --once` | `COSMOS Rails Prober` | **YES** | `live\logs\rails_prober_heartbeat.json` |
| 8 | **COSMOS Spend Meter** | 1m | `cosmos_spend_meter.py --once` | `COSMOS Spend Meter` | **YES** | `live\logs\spend_meter_heartbeat.json` |
| 9 | **COSMOS Drive Meter** | 1m | `cosmos_drive_meter.py --once` | `COSMOS Drive Meter` | **YES** | `live\logs\drive_meter_heartbeat.json` |
| 10 | **COSMOS cDeck Feed** | 0.75s daemon | `cosmos_cdeck_feed.py --loop` | `COSMOS cDeck Feed` | **YES**. Logon: **NO** — Keith cmd | `live\logs\cdeck_feed_heartbeat.json` |
| 11 | **COSMOS Backup** | 07/11/19/23 daily | `cosmos_backup_clock.py --once --force` | `COSMOS Backup 07/11/19/23` | **YES** (four tasks) | `live\logs\backup_clock_heartbeat.json` |
| 12 | **COSMOS Ledger Verify** | 5m | `cosmos_ledger_verify.py --once` | `COSMOS Ledger Verify` | **YES** | `live\logs\ledger_verify_heartbeat.json` |
| 13 | **COSMOS Index** | 1m | `cosmos_index.py --once` | `COSMOS Index` | **YES** | `live\logs\cosmos_index_heartbeat.json` |
| 14 | **COSMOS Dispatcher** | 5s daemon + 1-min self-heal | `cosmos_dispatcher_daemon.py --loop` | `COSMOS Dispatcher` | **YES** (CLOCKS id 14). Logon: **NO** — Keith cmd | `live\logs\dispatcher_heartbeat.json` |
| 15 | **COSMOS Runner Pool** | 15s loop / 1-min self-heal | `cosmos_pool.py --supervise` | `COSMOS Runner Pool` | **YES** (CLOCKS id 15). Logon: **NO** — Keith cmd | `live\logs\cosmos_pool_heartbeat.json` |
| 16 | **COSMOS CVM Clock** | 2s daemon (audio/ux) + 15s pull ticket | `cosmos_cvm_clock.py --loop` | `COSMOS CVM Clock` | **YES** (CLOCKS id 16). Logon: **NO** — Keith cmd | `live\logs\cvm_clock_heartbeat.json` |

Queue identity for #1–#3 (measured after restart onto the new default):
`queue=V:\A\Ai\COSMOS\live\queue`. Not `V:\Ai\_queue`.

---

## What each clock does

| clock | behavior |
|---|---|
| **Activity Clock / Watchdog2** | 15s no-idle **DRIVER** of the already-canonized MOTIF mail-carrier route + step-8 ITERATE (`docs/MOTIF.md`). Does **not** invent a rubric. Every cycle: honor PAUSE first; else scan `docs/WISHLIST.md` (open wishes → MOTIF stage 1) + `docs/BACKLOG.md` + `docs/MOTIF_TRACKER.md` + DHx + `live\queue`, pick the next unworked route item, DROP its agent via `cosmos_dispatch`. Max 3 drops/pass. Heartbeat `state=PAUSED` while the flag exists (paused ≠ dead). **mode=`hold`** waits forever; **mode=`resume_gate`** self-clears at `auto_resume_at` (auto-resession, no human turn). PAUSE never kills in-flight agents. On boot TidyUP leaves the flag, so WD2 comes up PAUSED. |
| **Collector** | ~30s results collector over `live\queue` + `docs/research` + the authority ledger. Projection `live\state\collector\index.jsonl` + `docs/COLLECTOR.md`. Not a second ledger writer. Does **not** honor PAUSE (in-flight returns must land). |
| **Runner** | Persistent drain of **this install's** queue role through `cosmos_runner.Runner`. Isolated from the BTS queue. `--loop` daemon; a second start no-ops on the lock if the heartbeat is fresh. Does **not** honor PAUSE. |
| **Motif Driver** | Mechanical next-stage drop for MOTIF_TRACKER rows not at stage 6 and not in-flight. Judgment (straight-implement vs 8-stage vs obsolete) stays with COW. |
| **Discovery** | Mesh-hands inventory. Scans `docs/research/**/*_HANDS.md` and probes a closed table of CLI binaries + local HTTP. `live\state\discovery\hands.json`. No model call, no spend. |
| **Health** | ~2s Core liveness. Does **not** instantiate Kernel/HealthBoard (those ledger every run). Probes sentinel, ledger file, install key, queue role, `:8770`, peer-clock ages. Projection `live\state\health\board.json`. |
| **Rails Prober** | 1m rail freshness: Cursor `GET /v1/me` (never launches an agent), CLI binaries, local HTTP (Core :8770, Ollama :11434). `live\state\rails\probe.json`. |
| **Spend Meter** | 1m `SpendGate.audit()` projection (no append). `live\state\spend\meter.json`. |
| **Drive Meter** | 1m `shutil.disk_usage` on a closed table (V:/C:/D:/X: + runtime-root volume). No tree walk. `live\state\drive\meter.json`. |
| **cDeck Feed** | 0.75s display snapshot. Aggregates heartbeats + meter files + PAUSE + queue counts. Does not walk the ledger every tick. `live\state\cdeck\feed.json`. |
| **Backup** | 4× daily hash-verified snapshot of ledger + identity + SEED + control + queue manifests (not `work/` / collector index). Uses `cosmos_backup.Backup`. First force-run **VERIFIED files=8**. |
| **Ledger Verify** | 5m `Ledger.verify()` walk. A break is REFUSED and named (TORN / BROKEN_CHAIN / FORGED) — never repaired. First tick **VERIFIED records=301**. |
| **Dispatcher** | 5s daemon. Tag-routed agent creation from the shared OUT bucket (TAG → rail); auto-attaches `docs/AGENT_BOUNDARIES.md`; files DHx + `live\state\assignments\`. Honors PAUSE (`--loop` IDLEs; paused ≠ dead). |
| **Runner Pool** | Concurrent pull supervisor + N drain workers (`claim_next` under the ledger head-fence; 3 general + 1 fast). Legacy `cosmos_run.py` untouched. PAUSE keeps workers alive (workers self-gate claiming). |
| **CVM Clock** | FAST ~2s CVM satellite (AUDIO_OWNER + 15s pull ticket + UX). CLOCKS **id 16** (Runner Pool holds **15**). Does **not** instantiate Kernel, append the ledger, or bind a port. Feed-class PAUSE: keeps moving, stamps `pause_present`. Sole writer of `live\state\cvm\audio.json`. |

PAUSE contract (`docs/PAUSE_PROTOCOL.md`): checked at the **top** of every
**retask** cycle (Watchdog2, Motif Driver, Dispatcher). Runner, collector,
discovery, health, meters, cDeck feed, backup, ledger-verify, Runner Pool,
CVM Clock keep moving.

---

## Proof (`schtasks /query /tn <name> /fo LIST /v` — 2026-08-25T23:18-05)

Host-side table (`schtasks /query /fo TABLE` filtered to COSMOS):

```
COSMOS Backup 07                         8/26/2026 7:00:00 AM   Ready
COSMOS Backup 11                         8/26/2026 11:00:00 AM  Ready
COSMOS Backup 19                         8/26/2026 7:00:00 PM   Ready
COSMOS Backup 23                         8/26/2026 11:00:00 PM  Ready
COSMOS cDeck Feed                        8/25/2026 11:19:00 PM  Running
COSMOS Collector                         8/25/2026 11:19:00 PM  Ready
COSMOS Drive Meter                       8/25/2026 11:19:00 PM  Ready
COSMOS Health                            8/25/2026 11:19:00 PM  Running
COSMOS Index                             8/25/2026 11:19:00 PM  Ready
COSMOS Ledger Verify                     8/25/2026 11:22:00 PM  Ready
COSMOS Mesh Discovery                    8/26/2026 12:17:00 AM  Ready
COSMOS Motif Driver                      8/25/2026 11:27:00 PM  Ready
COSMOS Rails Prober                      8/25/2026 11:19:00 PM  Ready
COSMOS Runner                            8/25/2026 11:19:00 PM  Ready
COSMOS Spend Meter                       8/25/2026 11:19:00 PM  Ready
COSMOS Watchdog2                         8/25/2026 11:19:00 PM  Running
```

(The underscore names `COSMOS_Backup_Daily` and `COSMOS_Serve_Watchdog` still
exist on this machine. Their `/tr` is `V:\Ai\BTS_MESH\...`. They are **not**
COSMOS-own clocks. Not deleted.)

### COSMOS Watchdog2 (Activity Clock)

```
TaskName:                             \COSMOS Watchdog2
Status:                               Running
Task To Run:                          py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_watchdog2.py --root V:\A\Ai\COSMOS\live --loop
Scheduled Task State:                 Enabled
Schedule Type:                        One Time Only, Minute
Repeat: Every:                        0 Hour(s), 1 Minute(s)
Stop Task If Runs X Hours and X Mins: Disabled
```

Heartbeat after restart onto COSMOS-own queue (COMPARE USING `last_run_epoch`):

```
last_run=2026-08-25T23:19:25-05:00  last_run_epoch=1787717965
pid=33532  polls=3  interval_s=15
queue=V:\A\Ai\COSMOS\live\queue
state=PAUSED  mode=hold  assigned_this_pass=0
```

`live\state\control\PAUSE.flag` is set (`mode=hold`,
`reason=TidyUP + resession (Keith, 2026-08-25)`). Watchdog2 honors it: drops
no agents, keeps writing `state=PAUSED` so a paused clock is not
indistinguishable from a dead one. `WATCHDOG2.log`:
`watchdog2 UP. interval=15s. pid=33532` then
`PAUSED mode=hold ... auto_resume_at=None`.

On RESUME (delete the flag, or a `resume_gate` whose `auto_resume_at` is
reached), it re-reads BACKLOG + MOTIF_TRACKER + `live\queue` and drops for
any open item with no in-flight agent.

### COSMOS Collector

```
TaskName:                             \COSMOS Collector
Status:                               Ready
Task To Run:                          py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_collector.py --root V:\A\Ai\COSMOS\live --loop
Repeat: Every:                        0 Hour(s), 1 Minute(s)
Stop Task If Runs X Hours and X Mins: Disabled
```

Heartbeat (restarted onto COSMOS-own queue): `pid=26920` `interval_s=30`
`queue_root=V:\A\Ai\COSMOS\live\queue`.

### COSMOS Runner

```
TaskName:                             \COSMOS Runner
Task To Run:                          py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_run.py --root V:\A\Ai\COSMOS\live --loop
Repeat: Every:                        0 Hour(s), 1 Minute(s)
```

Heartbeat: `queue_root=V:\A\Ai\COSMOS\live\queue` `pid=32400` `interval_s=15`.

### COSMOS Motif Driver

```
TaskName:                             \COSMOS Motif Driver
Task To Run:                          py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_motif_driver.py --once
Repeat: Every:                        0 Hour(s), 15 Minute(s)
Last Result:                          0
```

### COSMOS Mesh Discovery

```
TaskName:                             \COSMOS Mesh Discovery
Task To Run:                          py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_discover.py --root V:\A\Ai\COSMOS\live --once
Schedule Type:                        One Time Only, Hourly
Repeat: Every:                        1 Hour(s), 0 Minute(s)
Last Result:                          0
```

### COSMOS Health

```
TaskName:                             \COSMOS Health
Status:                               Running
Task To Run:                          py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_health_clock.py --root V:\A\Ai\COSMOS\live --loop
Repeat: Every:                        0 Hour(s), 1 Minute(s)
Stop Task If Runs X Hours and X Mins: Disabled
```

Heartbeat: `pid=33440` `interval_s=2.0` `polls=54` (in ~2 min) `state=RUNNING`
`verdict=RED x1` — the red is `:8770` not listening (BACKLOG: live Core not
up). Sentinel/ledger/install_key/queue are GREEN. Projection
`live\state\health\board.json`.

### COSMOS Rails Prober / Spend Meter / Drive Meter

All `/sc minute /mo 1 --once`, Enabled, `/tr` points at the COSMOS script
under `V:\A\Ai\COSMOS\cosmos\` with `--root V:\A\Ai\COSMOS\live`.

Rails first tick: `live_count=10` `probed_count=14`; Cursor
`GET /v1/me` HTTP 200 `apiKeyName=Cursor COSMOS 2` (key redacted
`crsr_…31ab`). Spend: `rail_count=4` `state=OK`. Drive: `present_count=4`
`warn_count=0` (V:/C:/D:/X:).

### COSMOS cDeck Feed

```
TaskName:                             \COSMOS cDeck Feed
Status:                               Running
Task To Run:                          py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_cdeck_feed.py --root V:\A\Ai\COSMOS\live --loop
Repeat: Every:                        0 Hour(s), 1 Minute(s)
```

Heartbeat: `pid=36828` `interval_s=0.75` `polls=145` `clocks=13`
`pause_present=true`. Feed: `live\state\cdeck\feed.json`.

### COSMOS Backup 07/11/19/23

```
Task To Run:                          py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_backup_clock.py --root V:\A\Ai\COSMOS\live --once --force
Schedule Type:                        Daily
Start Time:                           7:00 / 11:00 / 19:00 / 23:00
```

Force-run at standup: `state=VERIFIED` `files=8`
`dest=V:\A\Ai\COSMOS\live\backups\verified\20260825T231757`.

### COSMOS Ledger Verify

```
Task To Run:                          py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_ledger_verify.py --root V:\A\Ai\COSMOS\live --once
Repeat: Every:                        0 Hour(s), 5 Minute(s)
```

First tick: `state=VERIFIED` `records=301` `head_seq=301`.

### COSMOS Index

```
Task To Run:                          py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_index.py --root V:\A\Ai\COSMOS\live --once
Repeat: Every:                        0 Hour(s), 1 Minute(s)
Last Result:                          0
```

---

## Keith — ONE elevated command (onlogon relaunch)

Minute / hourly / daily registration did **not** need elevation. `/sc ONLOGON`
returned **ERROR: Access is denied.** from this unelevated session for every
daemon Logon task. `/rl highest` was **not** required and is not requested
(these processes do not need admin; Highest would be a blast-radius grant).

If you want the daemons to also fire at **logon** (in addition to the live
minute self-heal — the lock makes a double start safe), run **this one line**
from an elevated Command Prompt:

```
schtasks /create /tn "COSMOS Watchdog2 Logon" /tr "py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_watchdog2.py --root V:\A\Ai\COSMOS\live --loop" /sc onlogon /f & schtasks /create /tn "COSMOS Collector Logon" /tr "py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_collector.py --root V:\A\Ai\COSMOS\live --loop" /sc onlogon /f & schtasks /create /tn "COSMOS Runner Logon" /tr "py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_run.py --root V:\A\Ai\COSMOS\live --loop" /sc onlogon /f & schtasks /create /tn "COSMOS Health Logon" /tr "py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_health_clock.py --root V:\A\Ai\COSMOS\live --loop" /sc onlogon /f & schtasks /create /tn "COSMOS cDeck Feed Logon" /tr "py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos_cdeck_feed.py --root V:\A\Ai\COSMOS\live --loop" /sc onlogon /f
```

Do **not** `/f`-overwrite the existing minute self-heal names with
onlogon-only: that would drop the 1-min relaunch. Separate `Logon` names
keep both triggers.

Until that line runs, reboot survival for the five daemons is the **1-min
self-heal** (already registered, Enabled) once `V:` is mounted and Papa is
logged on. The onlogon wrapper is the faster post-logon kick.

---

## Adjacent clocks (not these)

| name | notes |
|---|---|
| `\BTS Queue Runner` / `LG` / `PB` | BTS's runner. COSMOS Runner does **not** drain `V:\Ai\_queue`. |
| `\BTS Backup *`, `\BTS Daily Brief`, `\BTS Drive Health`, `\BTS Elevated Ops`, `\BTS Health`, `\BTS KDash Feed`, `\BTS Publish Watch`, `\BTS Rail Check` | BTS mesh clocks. Untouched. |
| `\COSMOS_Backup_Daily` | Name says COSMOS; `/tr` is `V:\Ai\BTS_MESH\run_backup_daily.py`. Not a COSMOS-own clock. |
| `\COSMOS_Serve_Watchdog` | Name says COSMOS; `/tr` is `V:\Ai\BTS_MESH\cosmos_watchdog.py` against **trylive:8791**, not live:8770. |
| `\COSMOS Serve` | **Not registered.** `cosmos_up.RoadUp.TASK_NAME`; `/rl highest` needs Keith. Out of scope here. |

---

## How to verify (any later session)

```
py -3.14 cosmos\cosmos_own_clocks.py --root V:\A\Ai\COSMOS\live --status
schtasks /query /tn "COSMOS Watchdog2" /fo LIST /v
schtasks /query /tn "COSMOS Collector" /fo LIST /v
schtasks /query /tn "COSMOS Runner" /fo LIST /v
schtasks /query /tn "COSMOS Motif Driver" /fo LIST /v
schtasks /query /tn "COSMOS Mesh Discovery" /fo LIST /v
schtasks /query /tn "COSMOS Health" /fo LIST /v
schtasks /query /tn "COSMOS Rails Prober" /fo LIST /v
schtasks /query /tn "COSMOS Spend Meter" /fo LIST /v
schtasks /query /tn "COSMOS Drive Meter" /fo LIST /v
schtasks /query /tn "COSMOS cDeck Feed" /fo LIST /v
schtasks /query /tn "COSMOS Backup 07" /fo LIST /v
schtasks /query /tn "COSMOS Ledger Verify" /fo LIST /v
schtasks /query /tn "COSMOS Index" /fo LIST /v
schtasks /query /tn "COSMOS Dispatcher" /fo LIST /v
schtasks /query /tn "COSMOS Runner Pool" /fo LIST /v
schtasks /query /tn "COSMOS CVM Clock" /fo LIST /v
py -3.14 cosmos\cosmos_watchdog2.py     --root V:\A\Ai\COSMOS\live --status
py -3.14 cosmos\cosmos_collector.py     --root V:\A\Ai\COSMOS\live --status
py -3.14 cosmos\cosmos_run.py           --root V:\A\Ai\COSMOS\live --status
py -3.14 cosmos\cosmos_health_clock.py  --root V:\A\Ai\COSMOS\live --status
py -3.14 cosmos\cosmos_cdeck_feed.py    --root V:\A\Ai\COSMOS\live --status
py -3.14 cosmos\cosmos_dispatcher_daemon.py --root V:\A\Ai\COSMOS\live --status
py -3.14 cosmos\cosmos_pool.py          --root V:\A\Ai\COSMOS\live --status
py -3.14 cosmos\cosmos_cvm_clock.py     --root V:\A\Ai\COSMOS\live --status
```

`--status` exit 0 means the heartbeat is fresh. Compare using `last_run_epoch`,
never a timezone-naive stamp. Watchdog2 `state=PAUSED` with a fresh epoch is
alive-and-held, not dead.

---

## CLOCKS collapse — one pulse, one runner, calendar (Keith 2026-09-04)

**Status: TARGET, not live.** The matrix above is still 26 CLOCKS. Do not
shrink `CLOCKS`, `/delete` tasks, or lift HOLD until the phases below. Core
`:8770` stays up through the change (keep-her-afloat). Encoded after the
26-daemon occupancy review: one (or 2–3) resident Python processes should do
the small different jobs, not eighteen `--loop` daemons.

### Target topology

| process | cadence | does | does not |
|---|---|---|---|
| **1. Pulse** (`cosmos_pulse`, 15s `--loop` + 1-min self-heal + Logon) | NO-IDLE | HOLD first (`classify_pause` + WD2 `maybe_auto_resume`); collector tick; MOTIF/wishlist/BACKLOG drops cap 3 via `dispatch()`; drain ingress adapters into `live/queue`; rewrite `state/cdeck/feed.json`; dual-write `watchdog2_heartbeat.json` + `collector_heartbeat.json` until readers retarget | claim jobs; spawn Core; hammer drives |
| **2. Runner** (`cosmos_pool --supervise`) | 15s workers | **only** `Scheduler.claim_next` on `live/queue` under the ledger head-fence | invent a second claim protocol; run calendar jobs |
| **3. Health** (optional FAST, keep until Pulse owns supervise) | ~2s | Core liveness + `--supervise` spawn of `cosmos.py serve --port 8770`; write `state/health/board.json` | spawn other clocks |

**Calendar** is not a fourth daemon. Existing `--once` schtasks fire, run,
exit: Backup 07/11/19/23, ledger verify 5m, rails/spend/drive/index 1m,
Discovery/Askmine/NEW-AI hourly, Resession 1m HOLD-gated. Rails timer is
**identity only** — never `--live` on a timer.

That is two resident processes if Health supervise folds into Pulse (Core-down
detected on the next 15s tick). It is three if Core-down at ~2s stays sacred.
cDeck fleet `FEED_MAX_AGE_S = 120` (`builds/cdeck/cosmos_fleet_panel.py`,
`ui/app.js`) — a 15s feed rewrite does **not** trip stale; the 0.75s feed
daemon is display snappiness, not a panic threshold.

### Why not 26

`CLOCKS` in `cosmos/cosmos_own_clocks.py` is 26 rows. Thirteen of those are
detached `--loop` pythonw + matching `* Logon` relaunch. Most of those loops
do a small job (rename a drop, write a meter, drain one inbox) that a pulse
tick or a `--once` schtask already knows how to do. Two MOTIF droppers
(WD2 15s + Motif Driver 15m) plus prepaid orch as a fourth dropper is the
duplicate-assigner scar. Legacy `cosmos_run.py` **and** `cosmos_pool.py` both
`claim_next` the same ledger. CVM + CVM DT are superseded by Grok Voice.

### Job map — each CLOCKS row → new vehicle

| id | today | new vehicle | notes |
|---|---|---|---|
| 1 WD2 | 15s `--loop` | **Pulse IS this** | dual-write `watchdog2_heartbeat.json` until P3/PEER retarget |
| 2 Collector | 30s `--loop` | Pulse tick (every other pulse) | dual-write `collector_heartbeat.json` (P5 anti-loss) |
| 3 Runner (`cosmos_run`) | 15s `--loop` | **KILL** | pool is the only `claim_next`; two runners double-claim |
| 4 Motif Driver | 15m `--once` | Pulse owns MOTIF; calendar optional | kill as a second dropper |
| 5 Discovery | hourly `--once` | calendar stays | HOLD-gated |
| 6 Health | 2s `--loop` | process #3 until Pulse owns `--supervise` | **only** in-tree restarter of `:8770` |
| 7 Rails | 1m `--once` | calendar stays | never `--live` on timer |
| 8 Spend | 1m `--once` | calendar stays | |
| 9 Drive | 1m `--once` | calendar stays | |
| 10 cDeck Feed | 0.75s `--loop` | Pulse tick (rewrite `feed.json`) | 15s < 120s stale; drop the 0.75s daemon |
| 11 Backup | 4× daily `--once` | calendar stays | |
| 12 Ledger verify | 5m `--once` | calendar stays | |
| 13 Index | 1m `--once` | calendar stays | retarget `REQUIRED_DAEMONS` |
| 14 Dispatcher | 5s `--loop` | Pulse adapter tick | drain `state/dispatch/bucket` → `dispatch()` |
| 15 Runner Pool | 15s `--supervise` | **the runner** | keep Logon |
| 16 CVM | 2s `--loop` | **KILL** | Grok Voice superseded |
| 17 Work-Order Runner | 15s `--loop` | Pulse adapter / pool job | `pickup_order` → `live/queue` |
| 18 Resession | 1m `--once` | calendar stays | HOLD-gated; do not spawn |
| 19 Askmine | hourly `--once` | calendar stays | HOLD-gated |
| 20 CritConsumer | 10s `--loop` | Pulse adapter / pool job | critique inbox → A |
| 21/22 Grok/GEM buckets | 5–15s `--loop` | Pulse adapter / pool job | `live/buckets/{grok,gem}` → A |
| 23 NEW-AI Scout | hourly `--once` | calendar stays | HOLD-gated (today it scouts during HOLD) |
| 24 Prepaid orch | 1m `--once` | calendar adapter, not a dropper | `drop_order` → A; kill fourth-dropper role |
| 25 CVM DT | 2s `--loop` | **KILL** | emit-only standup; PEER still lists it |
| 26 SGH ingest | 15s `--loop` | Pulse adapter | drop → work-order / A |

### Five claim surfaces today — one after collapse

| surface | path | today | after |
|---|---|---|---|
| **A. Sched/ledger** | `live/queue` | `cosmos_run` **and** `cosmos_pool` **and** Core HTTP | **pool only** |
| B. Dispatch bucket | `live/state/dispatch/bucket` | CLOCKS 14 rename → `dispatch()` | Pulse adapter into A |
| C. Work-order bucket | `live/state/work_orders/bucket` | CLOCKS 17 `pickup_order` | Pulse adapter into A |
| D. Node buckets | `live/buckets/{grok,gem}` | CLOCKS 21/22 `claim_drop` | Pulse adapter into A |
| E. Critique inbox | `live/state/dispatch/workers/{gem,oa,ssa}` | CLOCKS 20 `claim_packet` | Pulse adapter into A |

B–E are ingress, not a second scheduler. Pulse (or a pool slot-0 adapter)
enqueues; pool drains **A**. Running `cosmos_run` and pool together is the
double-claim. Core HTTP `claim_next` (`cosmos_service.py`) stays for Crucible
posts — that is request-path, not a clock.

`dispatch()` production callers today: WD2, Motif Driver, Dispatcher daemon.
Prepaid orch does **not** call it (`drop_order` into C). Collapse: Pulse is
the only `dispatch()` caller.

### Coupling — consumer → artifact → required change

| consumer | artifact today | if CLOCKS shrinks without this change |
|---|---|---|
| cDeck feed | glob `logs/*heartbeat*.json` | **no panic** — missing files vanish from the dict, not RED. Stale **feed** (`age > 120s`) is the panic |
| cDeck feed | `SNAPSHOT_FILES` (`health/board`, spend/drive/rails/discovery/ledger json) | Pulse or calendar must still rewrite those six files |
| cDeck fleet / `app.js` | `state/cdeck/feed.json` | Pulse must rewrite feed every tick (15s is inside 120s) |
| Health `PEER_HEARTBEATS` | **hardcoded 15 names** including `cvm_clock`, `cvm_dt_clock`, `cvm_dt_voice` (voice is **not** a CLOCKS row) | `present:false` forever — not RED, but a lying fleet. **Shrink the tuple with CLOCKS, or glob like cDeck** |
| Health `--supervise` | `:8770` + `core_serve.lock` | **only** in-tree Core restarter. BTS `COSMOS_Serve_Watchdog` still points at **trylive:8791**. Do not kill Health until Pulse owns supervise |
| Health RED set | sentinel / ledger / install_key / queue / serve_8770 | peer heartbeats are **excluded** from RED — missing peers never take Core down |
| `cosmos_index.REQUIRED_DAEMONS` | `cosmos_runner`, `collector`, `mesh_discovery` | synthesizes `exists:False` if those heartbeat files vanish. Pulse/pool must keep writing `cosmos_runner_heartbeat.json` **or** retarget REQUIRED to `cosmos_pool` |
| P5 `anti_loss_daemons` | `collector_heartbeat.json` **and** `cosmos_runner_heartbeat.json` both `<180s` | UNPROVEN if runner process dies. Dual-write from Pulse/pool, or retarget the check to pool + collector |
| P3 `activity_clock_15s` | `DEFAULT_INTERVAL_S = 15.0` in `cosmos_watchdog2.py` + `watchdog2_heartbeat.json` | Pulse must keep that interval encoded **and** that filename until the check moves |
| Satellites | `CLOCKS` row matching `CLOCK_ID` | resession 18, askmine 19, crit 20, grok/gem 21/22, scout 23, prepaid 24, index 13, CVM 16 **selftest fail** if the row is gone. Retarget tests **before** shrinking `CLOCKS` |
| `standup_all` | iterates every `CLOCKS` spec + 13 `logon_specs` | shrinking CLOCKS does **not** `/delete` old tasks. Reboot Logon will **respawn** old `--loop` daemons unless those Logon tasks are deleted |
| WD2 | only unlinker of resume_gate (`maybe_auto_resume`) | Pulse must call it. `is_paused` (pool/crit) cannot self-clear a gate |
| Pause readers | **no single API** — copies in resession `classify_pause`, node_worker `is_paused`, WD2, dispatcher, WO, buckets, sgh, cdeck, health, CVM, motif, index | extract `classify_pause` + `maybe_auto_resume`; Pulse HOLD-aware; do **not** pause Health observe, feed rewrite, or in-flight drain |

### Files that have to change (same fence as CLOCKS shrink)

| file | change |
|---|---|
| `cosmos/cosmos_pulse.py` | **new** — 15s HOLD-aware pulse (WD2 scan + classify + auto-resume + adapter ticks + feed rewrite + dual-write WD2/collector heartbeats) |
| `cosmos/cosmos_own_clocks.py` | CLOCKS shrinks to Pulse + Pool + Health (+ calendar `--once` rows that stay as tasks, not daemons). `logon_specs` becomes Pulse / Pool / Health only |
| `cosmos/cosmos_health_clock.py` | `PEER_HEARTBEATS` → glob or the surviving names; later fold `--supervise` into Pulse |
| `cosmos/cosmos_index.py` | `REQUIRED_DAEMONS` → pool + collector + discovery (or whatever Pulse dual-writes) |
| `cosmos/cosmos_principles.py` | `anti_loss_daemons` + `activity_clock_15s` retarget when Pulse owns those filenames |
| `cosmos/cosmos_pool.py` | drop “Legacy cosmos_run.py is untouched”; pool-off is no longer “behaves as today” |
| `cosmos/cosmos_run.py` | stop registering; stage to `_delme\` after pool is the only claimant |
| `cosmos/cosmos_cdeck_feed.py` | `--once` callable from Pulse; retire `--loop` / Logon |
| `cosmos/cosmos_{watchdog2,collector,dispatcher_daemon,work_order_run,crit_consumer,grok_bucket_worker,gem_bucket_worker,sgh_drop_ingest,motif_driver,cvm_clock,prepaid_orch}.py` | become libraries Pulse/calendar import, not resident daemons. Keep `--once` for calendar and for bite tests |
| `cosmos/cosmos_resession.py` (export `classify_pause`) | one pause function; everyone else imports it |
| `tests/test_own_clocks.py` | pins ids 18–24 and 26 today (`len(CLOCKS) >= 12`, not ==26). Retarget **before** shrink |
| `tests/test_{resession,askmine,crit_consumer,grok_gem_bucket_workers,newai_scout,cosmos_index}.py` | CLOCK_ID identity |
| `docs/BACKLOG.md` | “26 CLOCKS” is the old done row; collapse is a new open item |
| `docs/CVM_ARCH.md` | stale: CVM DT as id 18 (now Resession) |

### Logon — reboot will undo a half-collapse

Today `standup_all` `logon_specs` (`cosmos_own_clocks.py`) registers 13 ONLOGON
relaunches of `--loop`. After collapse only **Pulse Logon**, **Runner Pool
Logon**, and (until folded) **Health Logon** may exist. Any leftover Logon
task respawns its old daemon after reboot even if the minute task is gone.
`/delete` Logon in the same phase as `/delete` of that clock’s minute task.

`--once` clocks (motif, discovery, meters, backup, verify, index, resession,
askmine, scout, prepaid) have no Logon row — they are already the right
vehicle.

### Collapse order (does not take Core `:8770` down)

Health `--supervise` is the only in-tree restarter of live Core. Never in the
same step: delete the Health task **and** stop a running `pythonw cosmos.py serve`.

0. **Leave running:** Health (`--supervise`), cDeck feed, Core `serve`. HOLD stays.
1. **Dual-write, no deletes.** `cosmos/cosmos_pulse.py` + `cosmos/cosmos_pause.py`
   landed 2026-09-04. **First duty is collect** (`Collector.poll_once`) even under
   HOLD — results back on the time daemon; in-flight returns land. No MOTIF drop,
   no `claim_next`, no oa-api. Default does not shim WD2. Do not `--standup` /
   `--loop` on live until Pulse is proven. `--shim-wd2` is the collapse shim after
   WD2 stops. Keep the WD2 process until Pulse is proven live (fresh epoch,
   HOLD-aware). The 30s collector daemon still runs; Pulse tick is idempotent.
2. **One runner.** Prove pool heartbeats. Drain `cosmos_run` (CLOCKS 3) and `COSMOS Runner Logon`. Core does not depend on runner.
3. **Calendar only.** Confirm motif/backup/verify/meters/index/resession/askmine/scout/prepaid are `--once`. Stop any accidental `--loop` on those. Disable Motif Driver + prepaid as *droppers* (Pulse owns MOTIF).
4. **Fold ingress.** Dispatcher, WO runner, SGH, crit, grok/gem buckets — one at a time. Keep heartbeat **filenames** until PEER/index/cDeck lists update.
5. **Kill CVM + CVM DT** (superseded). Shrink `PEER_HEARTBEATS` in the same fence.
6. **Shrink CLOCKS + Logon list + tests** in one fence. `/delete` old minute + Logon tasks.
7. **Last:** fold Health supervise into Pulse **or** keep Health as process #3. Only then stop `COSMOS Health` / `COSMOS cDeck Feed` loops.

**First cut if collapsing live under HOLD:** stop CVM/CVM DT, disable Motif Driver + prepaid orch schtasks as droppers, leave WD2 as the only dropper. Do not lift HOLD onto the current 26.

### Pause contract (do not conflate)

- **HOLD** (`PAUSE.flag` `mode=hold`) — Pulse drops nothing; never self-clears. Health observe, feed rewrite, pool in-flight drain, collector keep moving (today’s motif contract).
- **resume_gate** — Pulse calls `maybe_auto_resume`; default is MOTION at `auto_resume_at`.
- NEW-AI scout today has **zero** PAUSE and ran SCOUTED during HOLD — calendar scout must HOLD-gate.

### Not this section

Do not merge PR #30 as-is. Do not lift `ANTHROPIC_OFF`. Do not restart Core
for critic attach. Do not mix wallets. Two pens: GrokBot `V:\Ai`; this tree
`V:\A`. Crucible HTTP stays 501 until next serve.
