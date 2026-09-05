# RESEARCH_3 — Control / measure / monitor surfaces the OS still lacks

**Node:** G46 (Grok 4.6) · **Target:** COSMOS Core (the OS), not a client
**Date:** 2026-08-25 · **Stage:** Motif RESEARCH (how to surface it, not how to paint it)
**Canon:** `docs/FINAL_ARCHITECTURE.md` (ratified 2026-08-23), `docs/STAGE1_GOAL_SIGNED.md`,
Keith's C/M/M brief in `builds/cdeck/FEATURES_KEITH.md`
**Method:** host-side read of `cosmos/`, `kdash/`, `tests/`, `docs/`. No code edited.
**UNKNOWN rather than guess** is marked as such.

---

## 0. What this research is asking

Keith's requirement, recorded for cDeck but aimed at the OS:

> functional controls to **control, measure, and monitor** every node, channel,
> and aspect of COSMOS … not read-only dashboards — actual controls.
> (`builds/cdeck/FEATURES_KEITH.md`)

Stage 1 already said the same thing about the OS itself:

- "Rails, budgets, spend, and quotas tracked in real time, auditable ON DEMAND
  and on a schedule." (`docs/STAGE1_GOAL_SIGNED.md`)
- "KDash becomes a live backend" and "an alternate orchestration frontend"
  share **one** versioned API. (`docs/FINAL_ARCHITECTURE.md` decision 7)
- "A backup is a scheduled job with a verification, or it is not a backup."
- "REAL-OS HOOKS": system clock, Task Scheduler, interrupts.

So the question is not "what should cDeck draw." It is: **which control,
measure, and monitor verbs exist in Core modules but have no product surface,
and which required verbs do not exist at all.** Clients (KDash, cDeck, CDM,
voice, MCP) can only do what `/api/v1` and the CLI expose.

---

## 1. What the OS already surfaces (so the gaps are against this, not against zero)

### 1.1 HTTP `/api/v1` — `cosmos/cosmos_service.py`

| Method | Path | What it actually does |
|---|---|---|
| GET | `/status` | `ready`, `root`, `tree_id`, ledger head seq/event |
| GET | `/audit` | `Kernel.audit()` — ledger count, job-state histogram, one lease count, mail unread |
| GET | `/jobs` | `{job_id: state_string}` only |
| POST | `/jobs` | `sched.submit(command, priority)` → `{job_id}` |
| GET | `/health` | constructs a new `HealthBoard` and `run()`s it |
| GET | `/spend` | `kernel.spend.audit()` (rail caps / settled / reserved / headroom) |
| GET | `/tools` | `ToolContracts.report()` (projection; does not verify) |
| GET | `/events?since_seq=` | ledger tail, **hard cap 100**, full `verify()` each call |
| GET | `/rails` | `registry.matrix()` (claim + last ok + age). 503 if uncomposed |
| GET | `/makers` | maker catalog; POST adds |
| GET | `/control?client_id=` | voice pause / mic_off / clear_queue state |
| POST | `/kill` (also GET `/kill`) | off-switch: `mic_off` + `clear_queue` |
| POST | `/control/resume` | clears flags **and** SpendGuard counters |
| POST | `/voice` | session-continuous voice seam (hardened) |
| POST | `/command` | Commander grammar (read-mostly + submit + session) |
| POST | `/crucible` | one scheduled round, or 501 |

Auth: bearer on every `/api/v1/*` except `/kill` (capability-reducing, optional
`kill_token.txt`). Responses carry `served_at`. That pattern is the frozen-dashboard
scar closed for **reads that exist**. It does not create the missing verbs.

### 1.2 CLI — `cosmos/cosmos.py`

Verbs actually parsed: `install · status · audit · submit · backup · rehearse ·
serve · session start|close`.

`CLAUDE.md` and `BUCm.toml` advertise `cosmos up` (Tailscale). **That subparser
does not exist.** The logic lives in `cosmos/cosmos_up.py` (`RoadUp.up`) with
no `__main__` and no CLI wiring.

### 1.3 Command seam — `cosmos/cosmos_command.py`

Zero-arg: `status, audit, jobs, health, spend, rails, makers, help`.
Arg-taking: `events [N]`, `session start|close`, `submit <priority> <command>`.
Forbidden set blocks delete/force/reset. **No spend-set, no probe, no backup,
no kill, no pause, no mail, no leases, no surfaces.**

### 1.4 MCP — `cosmos/cosmos_mcp.py`

Tools: `cosmos_status · cosmos_submit · cosmos_jobs · cosmos_audit ·
cosmos_health · cosmos_command · cosmos_events`. Same thin job map as HTTP.
No `__main__` server entry on the CLI. Same surface, third transport.

### 1.5 Kernel composition — `cosmos/cosmos_kernel.py`

A writing Kernel composes: paths, ledger, arbiter, mail, scheduler, registry,
spend, validator, sessions, makers, convo, ITC.

**Not composed:** `Surfaces`, `ToolContracts` (GET `/tools` constructs on the
fly), `Backup`, `HealthBoard` (constructed per GET), `Runner`, rail adapters /
`register_node_rails`, `ControlChannel`, `SpendGuard`, `RoadUp`, `MCPServer`,
`DomWorker`, `Segments`. Composition in a test is not composition in Core —
that critic finding is still the binding constraint.

---

## 2. The gap pattern (already earned; do not invent a second one)

Three modules already encode the only honest C/M/M split:

1. **Claim** (`register` / `declare` / `BUDGET_SET`) is not capability.
2. **Measure** (`probe` / `measure` / `verify` / `audit`) is a dated run of code.
3. **Control** is a mutation that the ledger (or the control-state file) records,
   with an explicit road back.

`cosmos_registry.py`: `register()` vs `probe()` vs `matrix()` age.
`cosmos_surfaces.py`: `register()` vs `measure()` vs `qualify_backup_target()`.
`cosmos_tools.py`: `declare()` vs `verify()` vs `report()` (`verified=None` until
a check ran).
`cosmos_control.py`: `kill()` / `set_flags()` / `resume()`; `blocked()` fails closed.

The OS still **lacks the product surface** that applies this split to the
entities Keith named (nodes, channels, rails, surfaces, spend, jobs, voice,
reach, backup, session, mail, leases) as **controls**, not just as panels.

cDeck already has empty panels waiting on those surfaces
(`builds/cdeck/ui/index.html`): jukebox, node map, batteries, caps, CVM,
channels, surfaces — and the surfaces panel itself says
`"no /surfaces route on this API"`.

---

## 3. Gaps — module exists, product surface does not

These are the cheapest, highest-leverage holes: the verb is written, tested,
and unused by `/api/v1` or the CLI.

### 3.1 Spend — measure without control

- `SpendGate.set_budget(rail, cap_usd, expires_epoch)` exists
  (`cosmos/cosmos_spend.py`). GET `/spend` only returns `audit()`.
- Keith: "the ability to *set/adjust* them, not just view"
  (`builds/cdeck/FEATURES_KEITH.md`).
- Voice path **does** call `set_budget` as a side effect when a rail is
  missing (`cosmos_service.py` around the `_ASK_RAILS` / `"sgh-api"` blocks).
  That is silent Core mutation from `/voice`, not an operator control.
- `SpendGuard` (voice breaker: session/day USD + rate) has its own `audit()`
  (`cosmos/cosmos_spendguard.py`) and live-tunable
  `config/spendguard_config.json`. **GET `/spend` never includes it.**
  Resume clears the guard; nothing else can set the caps except editing the
  JSON on disk.
- Two spend ledgers, one HTTP number. A deck that paints `/spend` is not
  painting the breaker that actually stops `/voice`.

**How to surface (do not invent a second wallet):**

```
GET  /api/v1/spend                  # already: SpendGate.audit()
GET  /api/v1/spend?lane=guard       # SpendGuard.audit()  OR fold both under keys
POST /api/v1/spend                  # {rail, cap_usd, expires_epoch?} -> set_budget
POST /api/v1/spend/guard            # {session_usd?, day_usd?, rate_per_min?}
                                    # writes spendguard_config.json (already re-read)
```

Auth: bearer. Typed refusals: `UNKNOWN_RAIL` if POST names a rail that was
never `BUDGET_SET` **and** you decide POST is refresh-only — or allow create
(today `set_budget` creates). Ledger event `BUDGET_SET` is already the
receipt. Constraint: never treat unpriced as 0; keep provenance
estimate|measured|UNPRICED. Subscription pools (Claude/Grok) stay
human-posted; Core must not invent a measurement for them
(`FEATURES_KEITH.md`).

### 3.2 Rails — matrix without probe, without dispatch, without DOM

- `Registry.probe` / `probe_all` (`cosmos_registry.py`) are the **measure**
  verbs. GET `/rails` only **projects** the last measurement. Nothing on the
  API **runs** a probe.
- `register_node_rails` (`cosmos_node_rails.py`) is called from tests and
  (indirectly, one-rail-at-a-time) from the voice handler. It is **not**
  called at Kernel/Service boot. A cold `serve` has an empty matrix until
  something else appends `LINK_REGISTERED`.
- Specs omit Cursor (docstring mentions it; `PORT_DECISIONS["bts_cursor"]`
  is ADAPTED). All four API ranks are `0`. No DOM link is registered here.
- `Dispatcher` (`cosmos_rails.py`) is not an HTTP verb. There is no
  `POST /api/v1/rails/dispatch`.
- `RAIL_TYPES` includes `CHAT` and `OTHER`; no adapters, no routes.

**How to surface:**

```
GET  /api/v1/rails                 # matrix (exists)
POST /api/v1/rails/probe           # {link_id?} -> probe or probe_all
POST /api/v1/rails                 # register claim (kind in CLI|API|DOM|CHAT|OTHER)
```

Compose `register_node_rails` at writing-Kernel boot (or first READY), then
`probe_all` once so the matrix is a measurement, not an empty list. DOM-first
is policy_rank data; do not hard-code API-only.

Probe payload already: `{link_id, ok, detail}` + ledger `PROBE_RESULT`.
Constraint: stale ≠ live (`route()` already drops age > `max_age_s`; H-05).
A probe that is not code is a claim — refuse `NO_PROBE` rather than painting
green.

**UNKNOWN:** whether the **live** `V:\A\Ai\COSMOS\live` ledger currently holds
`LINK_REGISTERED` for sgh/gem/gw/oa (BUCm.toml `[live].hands` claims four
rails probed 2026-08-25; this research did not re-fold the live JSONL).

### 3.3 Jobs / jukebox — submit without operate

Scheduler verbs in `cosmos_sched.py`: `submit`, `queued`, `claim_next`,
`done`, `report_stale`, `wait_for_submission`. Runner: `run_one`, `drain`
(`cosmos_runner.py`).

HTTP:

- GET `/jobs` → `{job_id: v["st"]}` (`cosmos_service.py`). Drops command,
  priority, lane, timeout, submitter, claimant, claimed time, `stale_reported`.
- POST `/jobs` → submit only.
- No claim, no drain, no stale-report, no cancel (and cancel is **not** a
  scheduler verb today — stale is report-never-retry).
- `Runner` is **not** started by `serve`. Queueing a job from KDash/cDeck
  does not execute it unless some other process claims.

Terminal states **are** `CLEAN` / `FINDINGS` / `BROKE` (`OUTCOMES` in
`cosmos_sched.py`), not `DONE`/`FAILED`. cDeck's jukebox filter buttons use
DONE/FAILED (`builds/cdeck/ui/index.html`) — a vocabulary the OS does not
emit. That is an OS-surface thinness **and** a client mismatch; Core should
publish the three words and `stale_reported`, not invent a fourth state.

**How to surface:**

```
GET  /api/v1/jobs                  # full projection per job:
                                   # {id, st, command, priority, lane,
                                   #  submitter, by, claimed, stale_reported, timeout_s}
POST /api/v1/jobs                  # exists
POST /api/v1/jobs/stale            # report_stale(older_than_s)
POST /api/v1/jobs/drain            # Runner.drain(max_jobs) — only if Core
                                   # actually runs a runner (composition first)
```

Do **not** expose `claim_next`/`done` as a human deck control unless the
caller is a worker presenting identity. Those are worker verbs; jukebox is
operator submit + observe + stale-report.

Constraint: no silent retry. A stuck RUNNING job stays RUNNING until the
claimant `done()`s or an operator-facing stale report flags it. G46 tool
review already flagged this as WATCH (`docs/G46_TOOL_REVIEW_2026-08-25.md`).

### 3.4 Control / CVM — kill and resume, no pause, no POST /control

`ControlChannel.set_flags(pause, mic_off, clear_queue)` exists
(`cosmos_control.py`). HTTP exposes:

- GET `/control` (poll)
- POST `/kill` (mic_off + clear_queue only — **not** pause)
- POST `/control/resume`

There is **no** `POST /api/v1/control` that sets an arbitrary flag subset.
A deck cannot PAUSE without KILL, and cannot KILL-mic without clear_queue.
KDash desktop (`kdash/index.html`) does not consume `/control` at all.
Mobile talks `/voice` but does not poll `/control`.

**How to surface:**

```
POST /api/v1/control   {client_id?, pause?, mic_off?, clear_queue?}
                       -> ControlChannel.set_flags  (None = leave)
```

Keep kill as the ungated off-switch. Keep resume as the authenticated road
back. `set_flags` already fails on corrupt state (`recover=False`); kill/resume
overwrite. That asymmetry is load-bearing — do not unify them.

Voice CVM from cDeck can then be a pure client of GET `/control` + POST
`/control` + `/kill` + `/resume` + `/voice`. Session start/close already ride
`POST /command` (`session start|close`).

### 3.5 Surfaces — first-class module, zero routes, not composed

`cosmos/cosmos_surfaces.py` is the storage-surface registry Keith's backup
canon requires (LOCAL/LAN/CLOUD/PUBLISH × ARCHIVE/BACKUP/SCRATCH/PUBLISH;
measure reachability + free_bytes; qualify on three questions). Tests exist
(`tests/test_surfaces.py`). Kernel does not construct `Surfaces`. No
`/api/v1/surfaces`. Port plan already maps `bts_drive_health`,
`backup_to_onedrive`, `backup_watchdog` here (`cosmos_port_plan.py`).

cDeck's "surfaces" panel currently means maker locations — a **different
word**. Core must keep the storage-surface meaning; maker locations are
already GET `/makers`. Do not collapse the two.

**How to surface:**

```
GET  /api/v1/surfaces                         # state() projection + ages
POST /api/v1/surfaces                         # register {id, kind, path_or_url, role}
POST /api/v1/surfaces/measure                 # {surface_id} or all
POST /api/v1/surfaces/qualify                 # {surface_id, min_free_bytes, require_offmachine?}
```

Compose `kernel.surfaces = Surfaces(ledger)` at boot. Attach probes as code
(disk `shutil.disk_usage`, LAN path exists+free, R2/GDX/ODX via injected
callables). A PUBLISH kind must not qualify as BACKUP — the module already
refuses that structurally.

**UNKNOWN:** whether live SMART / GDX / ODX / R2 probe callables exist outside
this tree (incumbent `bts_gdx` / `bts_odx` / R2 tools). Do not claim they
are wired.

### 3.6 Backup / rehearse — CLI only, not a scheduled job type

`Backup.run` / `rehearse_restore` (`cosmos_backup.py`) are CLI `backup` and
`rehearse` only. Architecture decision 8: policy in Core; execution as
scheduled jobs; `rehearse-restore` is a first-class **job type**; Task
Scheduler = registered, read-back trigger.

None of that is on HTTP. Nothing submits a backup job through `sched.submit`
with a typed command. No target qualification through `Surfaces` before
`Backup.run`.

**How to surface:**

```
POST /api/v1/backup     {src_role|src, target_surface_id}  # qualify then submit job
POST /api/v1/rehearse   {backup_dest, scratch_role}
GET  /api/v1/backup     last BACKUP_VERIFIED / BACKUP_FAILED + ages
```

Execution path: `sched.submit("backup:…")` then the (missing) resident Runner
claims it. A backup that is a 200 from the HTTP handler and never a job is
the green-log class this module was written to stop.

### 3.7 Mail — probe row only

`Mailbox.send / unread / ack / probe` (`cosmos_mail.py`). Four probe states:
LIVE | EMPTY | MISSING | UNREADABLE | STALE. Health board calls `probe(me)`
only. Audit reports `my_unread`. No list, no send, no ack, no probe-other
on HTTP. Federation blocker #3 is exactly "no wire protocol (message schema
exists in cosmos_mail; transport between machines does not)"
(`cosmos_identity.py`).

**How to surface (local first):**

```
GET  /api/v1/mail                 # probe(me) + unread summaries (ids, subject, age, sender)
POST /api/v1/mail                 # send {to, subject, body, requires_ack?}
POST /api/v1/mail/ack             # {message_id}
GET  /api/v1/mail/probe?worker=   # typed state for any registered worker
```

Do not pretend this is cross-machine until a transport exists. Surface the
local mailbox honestly; federation stays `federation_ready() == False`.

### 3.8 Leases — one resource, always-green health

`Arbiter.status(resource)` (`cosmos_lock.py`) is per-resource. Kernel audit
counts only `("tree",)` (`cosmos_kernel.py` `leases_live`). Health
`lease_board` **always returns True** (`cosmos_health.py`) — a held tree is
not RED, a free tree is not RED. That is the C-46 class (a checker that
cannot go red) on the lease row, even with the planted failure sitting beside
it.

No GET `/leases`. No list of live grants. No operator release (and exposing
release is dangerous — fencing exists so a stale holder cannot be
"cleared" silently).

**How to surface:**

```
GET /api/v1/leases    # projection of live grants: resource, holder, token, expires_at
```

Control: do **not** add "force unlock" to the deck. Takeover is acquire-after-expiry
and a recorded chain. Monitor is the surface that is missing; silent clear is
the scar.

Health: a lease row that can go RED (torn ledger, lock sidecar held past
bound, UNKNOWN) — not "always True with a detail string."

### 3.9 Session / watchers / facts — CLI + command only

`session start|close` on CLI and Commander. No REST resource for the live
session, open watchers, inherited facts, or SEED health (length/HMAC).
`Kernel.audit()` does not mention sessions. Architecture decision 10:
closure without a valid manifest is OPEN_CONTEXT.

`cosmos_context.Session` already ledgers `SESSION_OPENED`, `FACT_RECORDED`,
`WATCHER_OPENED` / resolve. Those events are only visible if a client
happens to catch them on `/events`.

**How to surface:**

```
GET  /api/v1/session           # live projection: sid, stream, facts, watchers, seed hmac_matches
POST /api/v1/session/start     {stream}   # or keep command-only for voice
POST /api/v1/session/close     {handoff?} # force remains CLI-only (command seam forbids it)
```

SEED read-back (length + HMAC) is the measure. `hmac_matches` belongs on
this resource — BUCm already notes `stream` came back null on the live SEED;
that is a monitor finding with no panel.

### 3.10 Tools — report without verify

GET `/tools` → `report()` (disposition + last verify + age). `verify` /
`verify_all` (`cosmos_tools.py`) are not HTTP. Unverifiable tools stay
`verified=None` forever unless a test attaches a check. Migrator backlog
(UNDECIDED count) is a `Migrator.report()` query with no route.

**How to surface:**

```
POST /api/v1/tools/verify   {name?} -> verify or verify_all
GET  /api/v1/tools          # already; include UNDECIDED counts from Migrator.report()
```

### 3.11 ITC / corpus — composed, voice-only

Kernel constructs `ITC` with a live HTTPS fetcher (`cosmos_kernel.py`).
`search` / `get` / `register_corpus` / `search_corpus` (`cosmos_itc.py`) are
reachable from the voice orchestrator (`cosmos_orchestrator.py` `search_itc`)
and nowhere else. No GET `/itc`. A deck cannot search the index or see
`index_hash` / fetch age.

**How to surface:**

```
GET  /api/v1/itc/search?q=&max_age=
GET  /api/v1/itc/object/{key}
POST /api/v1/itc/refresh
GET  /api/v1/itc            # last ITC_REFRESHED: url, fetch_epoch, content_hash, row_count
```

Read-only. Corpus register is a control with accumulation-only semantics —
keep it bearer-authed and ledgered.

### 3.12 Identity / federation / reach

`federation_blockers()` / `federation_ready()` (`cosmos_identity.py`) are
functions with no route. Peers are a dict in source, not a registry.

`RoadUp.detect_tailscale` / `up` / `install_persistent` (`cosmos_up.py`)
measure Tailscale, plan serve argv, optionally `schtasks /create`. Not on
CLI despite `cosmos up` in `CLAUDE.md`. Stale comment in `plan_serve_cmd`:
it still says serve has no `--cert/--key`; `cosmos.py` **does** (lines 48–51).
The reach planner will tell an operator the trusted cert is unused **after
the flag landed**. That is a monitor that lies.

**How to surface:**

```
GET  /api/v1/identity       # MESH_ID, OWNER, PEERS, federation_blockers(), federation_ready()
GET  /api/v1/up             # RoadUp.up() measured dict (phone_url may be null)
POST /api/v1/up             # optional: ensure_cert + persist task — Keith-elevated
```

CLI: add the `up` subparser that already has a function. Point
`plan_serve_cmd` at `--cert/--key` now that they exist.

Tailscale status JSON is the measurement (`tailscale status --json`).
Publisher docs: https://tailscale.com/kb/1080/cli ·
https://tailscale.com/kb/1153/enabling-https ·
https://tailscale.com/download/windows
(verify at implement time; do not hard-code admin-console click paths).

### 3.13 Health board — five rows, two of them cannot represent their subsystems

Builtins (`cosmos_health.py`): ledger chain, resolver/sentinel, queue, mail,
leases (always True), planted RED.

Missing rows that **have** modules: spend gate, spendguard, rails matrix
freshness, surfaces qualification, backup last-verified age, session/SEED,
tools UNDECIDED, ITC index age, TLS/reach (`RoadUp`), runner-alive (is
anyone draining?), control-state readable.

GET `/health` constructs a fresh board every call and ledgers `HEALTH_BOARD`.
That is a measure-on-demand. It is not a scheduled board (Stage 1 item 9:
"a scheduled audit runs and lands where it is read").

`lease_board` always-True is a concrete defect, not a future feature.

### 3.14 Events feed — exists, but is not a monitor you can operate

- Full `ledger.verify()` on every poll (`cosmos_service.py`).
- Slice `[:100]` after filter — a busy tree silently drops events between
  polls with no `truncated` flag.
- No `event=` filter, no SSE/WebSocket. Architecture asked for interrupts
  "not poll-only loops" (`STAGE1_GOAL_SIGNED.md`). `/events` is poll-only
  by construction; `wait_for_submission` already has an OS-file-watch path
  (`cosmos_sched.py`) that the API never exposes.

**How to surface (minimal honest fix, then the interrupt):**

- Return `{head_seq, events, truncated: bool, next_since}` so a client can
  see loss.
- Optional `?event=` / `?writer=` filters (still a projection, still
  append-only).
- Bound work: `cosmos_segments.py` exists specifically because one JSONL
  re-verify is O(n). It is **not** what `kernel.ledger` is. Monitor cost
  and segment rotation are the same problem.

SSE: stdlib `http.server` can write `text/event-stream` but ThreadingHTTPServer
+ a blocked verify is a poor fit. **UNKNOWN** whether a later split-ready
module should own a push feed. Do not claim SSE is required for v1; **do**
claim a truncated flag is required or the frozen-dashboard scar returns as
silent drop.

### 3.15 Return validation / watchers

`ReturnValidator` is composed (`cosmos_kernel.py` `accept_return`). Stage 1:
"every dispatch registers a watcher; no return lands unobserved." Crossref
existence check is named in `v_doi_shape` as **not implemented** — shape
only, "EXISTENCE UNPROVEN until the Crossref resolver runs"
(`cosmos_validate.py`). No HTTP for open watchers, pending returns, or
validator register.

**UNKNOWN:** whether any production path calls `accept_return` outside tests.

---

## 4. Gaps — required by canon, no module surface *and* incomplete module

### 4.1 Node as an entity

Registry models **links** (`src -> dst`, `rail_type`, `policy_rank`). There
is no Node object with identity, health, quota, latency, battery. cDeck
derives a map from rails routes + spend rails + makers
(`builds/cdeck/ui/index.html` node-map copy). That is a client guess.

Stage 1: "WRK7 / SRV1 / new hardware: registered as nodes/surfaces in the
same registry, same three questions (reachability, measured throughput,
mesh addressability)." Throughput is **not measured anywhere** in Core.
Probe detail is a string; `PROBE_RESULT` has `ok` + `detail`, no
`latency_ms`, no tokens/sec.

**How to surface:** do not invent a second registry. Either:

- extend `LINK_REGISTERED` / `PROBE_RESULT` with optional `latency_ms`,
  `throughput` (measured, or absent — never 0), and treat `src`/`dst` as
  node ids, **or**
- add `NODE_REGISTERED` events beside links, same ledger, same age rule.

Batteries = per-node fold of: last probe ok+age, spend headroom for that
node's rails, quota remaining, control blocked?. Caps & speeds = measured
latency on probe + spend cap. If a number was not measured, omit it.

**UNKNOWN:** authoritative node list (this box, phone, T7920, SVR1, Jack,
Harrison). `cosmos_identity.PEERS` is not that list.

### 4.2 Channel as an entity

Keith asked to C/M/M **channels**. Core has rails (link types) and mail
(worker inboxes) and voice (a seam). Nothing named channel. Honest mapping:

- A **rail link** is a channel (CLI/API/DOM/CHAT).
- A **mailbox pair** is a channel.
- **Voice** is a channel with its own control plane.

Do not create a `Channel` class until one of those three is incomplete as a
channel view. The missing surface is `GET /rails` + probe latency + spend
on the same id — a **channel projection**, not a new kernel object.

### 4.3 Windows service + Task Scheduler read-back

Ratified: one **resident Windows service**, recovery, ledger replay
(`docs/FINAL_ARCHITECTURE.md` decision 1). What exists: `py … serve` in a
console, plus `RoadUp.install_persistent` which shells `schtasks /create /tn
"COSMOS Serve" /sc onlogon` with **no `/query` read-back**.

Decision 8: Task Scheduler = registered, **read-back** trigger. Port plan
claims `task_registry` was REPLACED by `cosmos_sched`. That replacement is
the in-process job queue, **not** the Windows task list. Scheduled
probe / audit / backup / health as OS tasks: absent.

Precedent (publisher):
`schtasks /Query /TN "COSMOS Serve" /FO LIST /V` and
`schtasks /Query /TN <name> /XML` then hash-compare to the registered argv.
Microsoft: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-query

Windows service (publisher):
https://learn.microsoft.com/en-us/windows/win32/services/service-control-manager
— pywin32 `servicemanager` / `win32serviceutil`, or NSSM, or a tiny
scm-registered launcher that execs `py -3.14 cosmos.py serve …`. **None of
these are in the tree.** `serve` is a foreground HTTP server.

**UNKNOWN:** Keith's preferred host mechanism (SCM vs schtasks-onlogon vs
both). Measure: `install_persistent` already chose schtasks-onlogon.

### 4.4 Resident runner / drain loop

Without a Runner inside `serve`, POST `/jobs` is a ledger event that nobody
executes. That is a control surface that does not control a machine. Spike
4 required N concurrent workers on one queue (`docs/SPIKE_BRIEFS.md`).
`serve` starts zero workers.

Composition: `Service` should own a drain thread (or a scheduled job that
is the drain), Job-Object contained, worker identity = service worker.
Until that exists, jukebox QUEUE is a claim.

### 4.5 DOM as a first-class rail — protocol yes, product no

`cosmos_dom.py` + `cosmos_browser.py` (dump-dom read driver; interactive CDP
explicitly later). `register_node_rails` registers only API links. No DOM
worker in `serve`. No `/api/v1/dom` status (binary found? last attempt
kind?). Architecture decision 6 is routing **policy**, currently unenforced
at the product surface.

Browser-hardening / secret-store: architecture lists as UNKNOWN, contract-only.
Leave UNKNOWN.

### 4.6 Elevated ops

`bts_elevated_ops` is ADAPTED, `successor=None` (`cosmos_port_plan.py`):
external helper, one UAC click, not absorbed. No dispatch surface from Core
("submit to elevated queue"). Operator cannot see pending elevated work.

**UNKNOWN:** path and contract of the surviving elevated worker on this
machine. Do not guess `V:\Ai\…` from memory; measure at implement time.

### 4.7 Interrupt-driven wakeup as a demonstrated product fact

`wait_for_submission` tries watchdog `on_created`, else loud poll
(`cosmos_sched.py`). Stage 1 done-test #8: "an event-driven wakeup
DEMONSTRATED (interrupt, not poll)." That demonstration is a unit test
(`tests/test_core.py`), not a service behavior a deck can see. No
`GET /api/v1/status` field `wakeup_mechanism`.

### 4.8 MCP as a served surface

Module exists; CLI does not start it; Service does not expose a streamable
HTTP MCP transport. Stdio JSON-RPC is the documented shape
(`cosmos_mcp.py`, protocol `2024-11-05`). Publisher:
https://modelcontextprotocol.io/specification/2024-11-05
(verify version before implementing HTTP transport; MCP has moved).

---

## 5. Thin measures that actively mislead (fix these as part of C/M/M)

These are not missing routes. They are existing routes whose payload cannot
support control/measure/monitor without lying.

| Surface | Lie / omission | File |
|---|---|---|
| GET `/jobs` | state string only; no stale flag; vocabulary ≠ CLEAN/FINDINGS/BROKE | `cosmos_service.py` |
| GET `/audit` | no spend, no rails, no session, leases=`tree` only | `cosmos_kernel.py` |
| GET `/spend` | SpendGate only; SpendGuard invisible | `cosmos_service.py` |
| GET `/rails` | last probe, never runs one; empty if uncomposed-but-503 is honest, empty-and-200 after boot with no register is not | `cosmos_kernel.py` vs `cosmos_node_rails.py` |
| GET `/health` leases | cannot go RED | `cosmos_health.py` |
| GET `/events` | 100-cap silent drop; O(n) verify | `cosmos_service.py` |
| GET `/tools` | report without verify | `cosmos_service.py` |
| `Kernel.audit` docstring vs `status()` | module claims `status()`; Kernel has no `status()` (G46 review) | `cosmos_kernel.py` |
| `cosmos_up.plan_serve_cmd` | says `--cert/--key` missing; CLI has them | `cosmos_up.py` vs `cosmos.py` |
| Commander `jobs` | same thin map as HTTP | `cosmos_command.py` |
| MCP `cosmos_jobs` | same | `cosmos_mcp.py` |

---

## 6. How to build (integration, not a second architecture)

One versioned API. Decision 7 is closed. **Extend `/api/v1`.** Do not add a
`/api/v2` for C/M/M and do not let cDeck talk to the filesystem.

### 6.1 Pattern (already in `cosmos_service.py`)

- GET = projection + `measured_at` / `measured_at_epoch` + `served_at`.
- POST = one kernel verb, ledgered, typed error as `{error: KIND, detail}`.
- 503 with `*_NOT_COMPOSED` when the kernel lacks the module (makers/rails
  already do this — copy it).
- 401 bearer; `/kill` remains the exception.
- Body cap `_MAX_BODY_BYTES`. No path from request text to filesystem
  (static allowlist lesson).
- Never return 0 for an unmeasured number; omit the field or use `null`.

### 6.2 Composition first

A route that constructs `HealthBoard`/`ToolContracts`/`Surfaces` ad hoc will
drift from the writing Kernel. Compose on `Kernel.__init__` (writing path),
project on read-only path, refuse writes with the existing
`read_only` / `NOT_FOUND` reader-is-not-a-writer rule.

Resident `serve` must also compose: rail registration + one probe_all,
Runner drain loop, ControlChannel (already in the handler), SpendGuard
(already in the handler — **fold its audit into GET `/spend`**).

### 6.3 Auth / fail-closed

- Spend set, backup, probe-all, session close, mail send: bearer.
- Kill: remains ungated (or kill_token) because it only reduces capability.
- Resume / pause-off: bearer (already).
- Federation / peer control: do not ship while `federation_blockers()` is
  non-empty; the GET that **lists the blockers** is the monitor.

### 6.4 Command seam

Add only **zero-arg or strictly parsed** verbs that delegate to the same
kernel methods (`probe`, `spend set` is argument-taking and dangerous on
voice — keep spend-set HTTP/CLI, not Commander, until a confirm-nonce
exists). Voice already has confirm for consequential turns
(`cosmos_service.py` `/voice`). Reuse that; do not teach the Commander to
set budgets from a misheard word.

### 6.5 CLI

Add `up`. Add `probe`. Consider `spend set` as a native verb so Keith is
not editing JSON. Backup already exists; HTTP should call the same
`Backup` class, not a parallel implementation.

### 6.6 Precedents inside this tree (do not shop for a new stack)

| Need | Precedent in-tree |
|---|---|
| Claim vs measure vs age | `cosmos_registry`, `cosmos_surfaces`, `cosmos_tools` |
| Off-switch + explicit on | `cosmos_control` |
| Reserve-deny-call-settle | `cosmos_spend` |
| Append-only live feed | GET `/events` |
| Typed 503 not-composed | GET `/rails`, GET `/makers` |
| Job as immutable manifest + ledger | `cosmos_sched` |
| Reach measured not labelled | `cosmos_up.detect_tailscale`, `Surfaces.qualify_backup_target` |
| Negative control on a board | `HealthBoard` planted RED |

External publishers only where Core must speak a foreign protocol:
Tailscale CLI/HTTPS KB (above), Windows `schtasks /Query`, MCP spec,
Crossref REST `https://api.crossref.org/works/{doi}` (DOI existence —
named, not wired).

---

## 7. Recommended research ranking (not an implementation plan)

Order is "unblocks the most C/M/M with the least new invention." Architecture
is not reopened.

1. **Thicken the reads that already exist** — jobs projection, spend+guard,
   events truncated flag, health rows that can go RED, rails composed at
   boot. Clients can paint truth the same day.
2. **POST `/control` (set_flags)** — CVM pause without kill; module done.
3. **POST `/spend` (set_budget)** — Keith's spend-control requirement;
   module done.
4. **POST `/rails/probe`** — measure on demand; then scheduled probe as a
   job once a Runner lives in `serve`.
5. **Compose Runner inside `serve`** — otherwise jukebox/submit is theater.
6. **Compose Surfaces + GET/POST `/surfaces` + backup-as-job** — Stage 1
   backup done-test is otherwise unreachable from any client.
7. **GET `/session`, `/leases`, `/mail`, `/itc`, `/identity`, `/up`** —
   monitors for subsystems that already run.
8. **Node/channel projection** (latency on probe, batteries as a fold) —
   after links actually probe.
9. **Windows service + schtasks read-back** — real-OS hooks; needs Keith
   for the one elevated registration.
10. **Federation / DOM-interactive / Crossref existence** — UNKNOWN or
    blocked on purpose; surface the blocker list, do not report working.

---

## 8. UNKNOWN (explicit)

- Live ledger contents at research time (whether four rails are currently
  registered on `V:\A\Ai\COSMOS\live`); BUCm claims yes as of 2026-08-25.
- Whether anyone drains the live queue besides ad-hoc tests / BTS runner.
- Crossref (or other) DOI existence resolver — shape gate only.
- DOM secret-store / interactive CDP — architecture UNKNOWN.
- Preferred Windows residency (SCM vs schtasks) — schtasks is what `cosmos_up`
  already generates.
- SSE vs thicker poll — not decided; truncated flag is not optional either way.
- Elevated-ops worker path on this machine.
- Authoritative node inventory (WRK7/SRV1/phone/peers).
- Whether `accept_return` is on any production path.
- MCP HTTP/streamable transport vs stdio-only for COSMOS.

---

## 9. What this research is not

- Not a cDeck UI spec. cDeck is a client; empty panels there are **evidence**
  of missing OS surfaces (`builds/cdeck/ui/index.html` surfaces copy).
- Not a re-vote of the spend breaker, ledger, or DOM-first policy.
- Not a claim that KDash is unfinished because it lacks buttons. KDash is
  correctly a projection client of the API it was given
  (`kdash/index.html` polls status/health/spend/jobs/rails/audit/tools/events
  + command + makers). The OS did not give it control verbs.
- Not code. No files under `cosmos/` were edited.

---

## 10. File index (cited)

| File | Why it matters to C/M/M |
|---|---|
| `cosmos/cosmos_service.py` | the product surface |
| `cosmos/cosmos.py` | CLI verbs; missing `up` |
| `cosmos/cosmos_kernel.py` | composition root; thin `audit()` |
| `cosmos/cosmos_command.py` | voice/frontend grammar |
| `cosmos/cosmos_mcp.py` | third transport, same thin verbs |
| `cosmos/cosmos_spend.py` / `cosmos_spendguard.py` | two wallets, one GET |
| `cosmos/cosmos_registry.py` / `cosmos_rails.py` / `cosmos_node_rails.py` | claim/probe/dispatch |
| `cosmos/cosmos_sched.py` / `cosmos_runner.py` | jobs vs execution |
| `cosmos/cosmos_control.py` | flags the HTTP does not fully expose |
| `cosmos/cosmos_surfaces.py` / `cosmos_backup.py` | storage C/M/M, CLI-only backup |
| `cosmos/cosmos_health.py` | board that does not cover the OS |
| `cosmos/cosmos_mail.py` / `cosmos_lock.py` / `cosmos_session.py` / `cosmos_context.py` | unsurfaced kernel verbs |
| `cosmos/cosmos_tools.py` / `cosmos_migrate.py` / `cosmos_port_plan.py` | contracts without verify-on-demand |
| `cosmos/cosmos_itc.py` / `cosmos_orchestrator.py` | search only via voice |
| `cosmos/cosmos_identity.py` / `cosmos_up.py` | federation + road reach |
| `cosmos/cosmos_dom.py` / `cosmos_browser.py` | DOM protocol without a rail |
| `cosmos/cosmos_validate.py` / `cosmos_segments.py` | return gate; monitor-cost layer unused by Kernel |
| `docs/FINAL_ARCHITECTURE.md` / `docs/STAGE1_GOAL_SIGNED.md` | required surfaces |
| `builds/cdeck/FEATURES_KEITH.md` / `builds/cdeck/ui/index.html` | operator C/M/M demand vs empty panels |
| `kdash/index.html` / `kdash/mobile.html` | what the API actually feeds today |
| `docs/G46_TOOL_REVIEW_2026-08-25.md` | prior WATCH items on the same modules |
