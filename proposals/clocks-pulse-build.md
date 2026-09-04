# CLOCKS Pulse — BUILD proposal

**Work order:** `wo-20260904T124800` · **Issue:** [#34](https://github.com/keithbbf-gif/cosmos/issues/34)
**Lane:** B — Cursor Cloud Agent (Claude Opus 5). Independent clone. Lane A not read; PR #32 not read.
**Posture:** **PROPOSE-ONLY.** Nothing here is applied. COW applies; this lane does not write the live tree.
**Artifacts:** `proposals/clocks-pulse-build.json` (the manifest COW consumes) ·
`proposals/pulse/cosmos_pulse.py` (reference tick engine) ·
`proposals/pulse/pulse_bind.py` (the binding gate) ·
`tests/test_clocks_pulse_build.py` (executable acceptance).

---

## 0 · What I could not read, said out loud first

The order opens with *"FIRST read `docs/AGENT_BRIEF.md` and `docs/AGENT_BOUNDARIES.md`"* and points the
target topology at `docs/ORCHESTRATION.md`.

**None of those three files exists on any branch of `github.com/keithbbf-gif/cosmos`.** I fetched every
remote ref and checked each one; they are not in `main`, not in any `cursor/*` branch, not anywhere.
`work_orders/drop/wo-20260904T124800.json` is likewise not in the repo — issue #34 calls it a *local*
drop, and local is not a place this lane can reach.

So: **they were not read.** Absent is not empty and not read — four states, never collapsed. The
boundary set this build honours is the one stated verbatim in the work order and issue #34, plus
`docs/WORK_ORDER_SOP.md` and `docs/AGENTS.md`, which *are* in the clone. Anything that lives only in
the three missing files is **UNCHECKED here**, and that is recorded in the manifest as a context gap
rather than papered over. Publish them to the repo and re-run this lane if the gap matters.

The same honesty applies to the clocks themselves. `cosmos_own_clocks.py`, `cosmos_health_clock.py`,
`cosmos_pool.py`, `cosmos_run.py`, `cosmos_cdeck_feed.py`, `cosmos_index.py` and
`cosmos_principles.py` are live-tree modules. **I never saw the 26 clock names.** A build proposal
that invented them would be worse than useless: it would silently not run the real ones. So the
manifest ships **unbound**, and the binding gate **refuses it** until COW binds every live name. That
refusal is a feature of the build, described in §4.

---

## 1 · The shape of the problem, and the one-sentence answer

Twenty-six resident Python daemons, each doing a small different job, each with its own loop, its own
heartbeat, its own Logon relaunch, and — five times over — its own way of claiming work. Twenty-six
processes is not twenty-six times the work; it is twenty-six times the *supervision*, and supervision
is where this system has historically lost.

**The answer:** one resident tick — **Pulse, every 15 s** — dispatches every sub-minute duty from a
declarative wheel; **`pool.claim_next` becomes the only claim surface**; everything calendar-shaped
leaves residency entirely and becomes a **Task Scheduler `--once`** trigger. Health `--supervise`
stays resident and stays the only restarter of live Core `:8770` until the very last phase.

| | before | after |
|---|---|---|
| resident Python processes | 26 | **2** (Pulse, Health `--supervise`) |
| resident Windows service | Core `:8770` | Core `:8770`, **untouched** |
| `CLOCKS` registry entries | 26 | **26** — re-homed, never shortened |
| claim surfaces | 5 | **1** (`pool.claim_next`) |
| Logon relaunch tasks *enabled* | 13 | **2** (11 disabled + renamed `_delme`, none deleted) |

The registry row is the one to read twice. **Residency changes; the registry does not shrink.** Each
of the 26 entries keeps its name and gains a `residency` field (`resident` | `pulse` | `calendar` |
`parked`). "Do not shrink CLOCKS" is not a promise in this proposal — it is a refusal in
`pulse_bind.py`, and §4 shows the exit code.

---

## 2 · Why 15 s, and why the grid is the hard part

15 s is not a taste. It is **the tightest cadence already live in the tree**: `docs/WORK_ORDER_SOP.md`
step 3 describes the `COSMOS Work-Order Runner` schtask firing at ~15 s. A collapse that lengthens the
tightest live cadence is a behaviour change wearing a refactor's clothes, and a grid finer than the
tightest real need buys nothing but wakeups. So the wheel runs on the cadence the tree already has.

Everything painful about a shared tick follows from the grid:

**Quantization is declared, never silent.** A clock's effective period is
`ceil(declared / 15) * 15`. A 20 s clock gets 30 s — a real change to a real duty. So any clock the
grid would re-time must declare **`max_interval_s`**, the largest gap its duty tolerates. **No
declaration is a refusal** (`QUANTIZATION_UNDECLARED`): only the duty's owner knows whether 30 s is
fine, and a build that assumes on their behalf has changed a cadence without telling anybody. A
declared tolerance the grid cannot meet is also a refusal — that clock stays resident, or the wheel
needs a finer grid.

`max_interval_s` and `deadline_s` are deliberately two fields. The deadline is *how long one run may
take before it is stale*; the interval is *how long a gap between runs is acceptable*. The first
version of this engine used one field for both and refused a nightly job for having a short runtime
deadline — the test board caught it, which is the whole reason the board exists.

**Drift cannot accumulate.** Slot deadlines are `t0 + n·tick` from a monotonic origin, not
`now + tick` after each pass. A tick that takes 4 s does not push the next one to 19 s.

**A resumed Pulse must not stampede.** If Pulse was down for an hour, the honest recovery is *at most
one* catch-up per clock plus a loud `skew_ticks` count — not 240 backlogged ticks fired at a tree that
has been quiet.

**Phase offsets are deterministic.** Slot offset is `sha1(clock_id) % slots`, so 26 clocks spread
across the wheel instead of piling onto tick 0 — and two boots, or two lanes reading the same plan,
compute the same spread.

**The tick has a wall budget.** 5 s of the 15 s for in-process work. Work that does not fit is
**deferred with a reason and runs first next tick**. Deferred is a state; dropped is a defect. Anything
that can plausibly exceed the budget is not in-process at all — it is dispatched as a `--once` child,
so one slow duty cannot hold the wheel hostage.

**Single-flight.** A clock still running when its next slot arrives is **skipped, and the skip is
recorded**. Ticks never queue up behind a slow job. This is the same shape as the double-claim bug the
scheduler already closed: overlap is where two copies of one duty come from.

**Report, never retry.** An in-flight clock past its deadline is reported STALE and **quarantined** —
its side effects may already have happened. Only a clock that *declares* `idempotent: true` may be
re-dispatched, and the re-dispatch is recorded.

**The negative control is a row on the wheel.** `pulse.selftest.planted_red` must report BROKE on
every tick. If it ever reports CLEAN, the verdict is `PULSE-BROKEN` and **no green is published** —
a wheel that cannot detect failure has no greens worth reading. This is the health board's planted
row, applied to the clock layer.

---

## 3 · The five couplings, and what changes in each

The order names them: heartbeats, `PEER_HEARTBEATS`, the cDeck glob, index `REQUIRED_DAEMONS`, the 13
Logon relaunches, and the five claim surfaces. Every one of them is a *reader* problem, and the rule
for all six is the same: **the writer moves first, behind a shim; the readers move when they are
ready; nothing goes red because a writer changed.**

### 3.1 Heartbeats → one file, every clock

Today each loop writes its own heartbeat. Pulse writes **one** per tick, carrying every clock with
`state`, `last_run_epoch`, `residency`, and — the field that matters — **`stale_after_s`**, published
per clock as `2 × effective_period + deadline`. A reader has never had to guess a clock's cadence from
a filename again after this lands.

Every stamp carries **epoch + UTC + aware-local + tz offset + writer identity**, because a naked local
timestamp has already been misread as five hours stale in this system's history and a healthy runner
reported dead.

States are `NEVER-RUN | IDLE | RUNNING | STALE | QUARANTINED`. `NEVER-RUN` is not stale and not green;
it is its own state, and collapsing it into either is the four-states rule being violated.

**Shim:** the same tick data is re-emitted under the per-daemon filenames the existing readers already
watch, for the whole collapse window. The shim is *parked* — not deleted — only after every reader has
run one full day on the primary file.

### 3.2 `PEER_HEARTBEATS` → same keys, new writer

The key set does not change. A peer that has always read a key keeps reading it. What changes is the
writer: Pulse, with `via: "pulse"` and `owner_pid` added. **Gate:** the peer-side diff of the key set
before and after the cutover is empty. Removing a peer-visible key inside a local refactor is how a
federation blocker gets invented.

### 3.3 cDeck glob → feature-flagged move to `clocks[]`

The glob keeps globbing during the collapse (the shim feeds it). Behind a flag, cDeck reads the
primary heartbeat's `clocks[]` instead. **Both paths run side by side for one full day and the panels
must agree** before the flag flips and the shim is parked. A glob told the names goes green over a
name added later — that is exactly the failure the incumbent runner's lane heartbeats were changed to
avoid, and it applies verbatim here.

### 3.4 index `REQUIRED_DAEMONS` → residency, not process-existence

Today liveness means *a process exists*. After the collapse, 24 of those processes do not exist by
design, so the predicate has to change or the index goes permanently red and stops meaning anything.

**The list is not shortened.** Each entry gains `residency`, and liveness becomes **"the clock ticked
within its `stale_after_s`."** That predicate is strictly better than the old one: a wedged daemon
whose process still exists used to be green.

**Gate:** index green with the same entry count — 26 — and no entry removed.

### 3.5 13 Logon relaunches → 2 enabled, 11 parked

Two Logon entries stay enabled: `COSMOS Pulse` and `COSMOS Health --supervise`. The other eleven are
`schtasks /change /disable`'d and renamed under a `_delme` prefix. **Registered, disabled, reversible
with one `/change /enable`. Nothing is `/delete`d — ever.** Every schtask edit is **read back** with
`/query /xml`; a schtask edit verified by its exit code is not verified (the architecture already says
Task Scheduler is a *registered, read-back* trigger, and this is that rule applied).

### 3.6 Five claim surfaces → `pool.claim_next` only

One rule: **`pool.claim_next` is the only code path that may transition a work item to claimed.** The
other four surfaces become thin adapters that call it and keep their public signatures, so callers do
not have to change in the same step.

Pulse itself holds **no claim logic**. It calls the surface, at most 4 times per tick, so a burst of
queued work cannot starve the wheel. A loser gets a **typed `LOST_CLAIM`**, is counted, and the tick
moves on — the losing claimant is a normal outcome, not an exception path nobody has walked.

**Gate — and this is the one worth insisting on:** the overlap test must show zero double-claims **and
at least one observed `LOST_CLAIM`**. A claim path that has never lost is a claim path nobody has seen
contend, and a gate tested only in the passing direction is a gate nobody has seen closed.

---

## 4 · The binding gate: why this manifest refuses itself today

I never saw the 26 names. So `proposals/clocks-pulse-build.json` ships with
`bindings.bound = []` and `bind_required = 26`, and running the gate against it **fails**:

```
$ python proposals/pulse/pulse_bind.py --plan proposals/clocks-pulse-build.json ; echo "exit=$?"
{
 "ok": false,
 "verdict": "REFUSED x1 ['UNBOUND_PLAN']",
 "bound": 0,
 "required": 26,
 "refusals": [
  {
   "kind": "UNBOUND_PLAN",
   "detail": "no clock is bound: this manifest is a design, not an applicable change.
              COW exports the live CLOCKS registry and binds it before apply."
  }
 ]
}
exit=2
```

COW exports the live registry read-only as `{"clocks": [...]}`, binds each name to exactly one
disposition, and re-runs the gate. It refuses on any of:

| refusal | what it stops |
|---|---|
| `UNBOUND_CLOCK` | a live clock with no disposition — every clock is re-homed or the plan does not apply |
| `CLOCKS_SHRUNK` | fewer bound than live — **"do not shrink CLOCKS", enforced, not promised** |
| `UNKNOWN_CLOCK` | a bound name the live registry has never heard of (an invented clock) |
| `REGISTRY_COUNT_MISMATCH` | the plan expects 26 and the export says otherwise — one is stale; refuse rather than pick |
| `QUANTIZATION_UNDECLARED` | the grid re-timing a clock whose owner never said what gap it tolerates |
| `QUANTIZATION_EXCEEDS_TOLERANCE` | a clock the 15 s grid cannot honour, being rounded instead of refused |
| `HOLD_DUTY_PARKED` | a duty required under HOLD being parked in the same breath |
| `FORBIDDEN_SCHTASK_ACTION` / `SCHTASK_DELETE` | **any** `/delete`, anywhere in the plan |
| `CORE_DOWN` | a phase or command that stops, kills or restarts Core |
| `SUPERVISE_DROPPED_EARLY` | Health `--supervise` stood down before the phase that grants Core spawn |
| `SPAWN_HANDOFF_EARLY` / `TWO_SPAWN_OWNERS` | the restarter role moving before the last phase, or to two owners |
| `HOLD_LIFT` / `ANTHROPIC_ON` | HOLD being cleared, or `ANTHROPIC_OFF` being flipped |
| `NO_READ_BACK` | a schtask edit measured by exit code instead of `/query` |
| `PHASE_WITHOUT_GATE` / `PHASE_WITHOUT_ROLLBACK` | an unmeasured or one-way phase |
| `GROKBOT_PEN` / `ABSOLUTE_PATH` | a write at `V:\Ai` or any absolute path |

The boundaries in the work order are not comments in this build. They are exit code 2.

---

## 5 · Collapse order — six phases, Core never goes down

Each phase is one reversible step with a gate that can fail. `core_stop` and `core_restart` are
`false` on every one of them, and the binder refuses the manifest if any phase sets either.

**P0 — Shadow. Dispatch nothing.**
Pulse runs alongside the 26 loops in dry-run: it computes the due set and writes a *shadow* heartbeat
under a distinct name. It dispatches nothing, claims nothing, and touches nothing.
*Gate:* for one full day the shadow due-set reproduces every observed live run, for all 26 clocks,
within one tick. Any clock whose real cadence disagrees with its declared period is **re-declared
before P1** — the plan is wrong there, not the tree.
*Rollback:* stop the shadow process. Nothing else changed.

**P1 — Leaf clocks.** The ones with no claim surface and no Core dependency, idempotent and cheap.
Register `COSMOS Pulse`; the leaf loops exit on a `PULSE_OWNED` flag file; their 11 Logon tasks are
disabled and renamed `_delme`; the legacy heartbeat shim goes on.
*Gate:* no moved clock shows a heartbeat gap longer than its `stale_after_s`; index green at 26; cDeck
glob green; read-back shows the parked tasks still registered.
*Rollback:* delete the flag file, `/change /enable` the eleven. The loops come back.

**P2 — Calendar migration.** Clocks with period ≥ 15 min that tolerate a missed window become Task
Scheduler calendar triggers invoking `<module> --once`. They stop being resident at all.
*Gate:* each new trigger read back with `/query /xml` **and observed to fire once** before its old
loop is stood down. A trigger that has never fired is a trigger nobody has seen work.
*Rollback:* disable the calendar trigger, re-enable the parked loop task.

**P3 — Claim collapse.** The four non-pool surfaces become adapters over `pool.claim_next`; Pulse
drains at most 4 per tick; the ~15 s Work-Order Runner task is disabled and its cadence is served by
the wheel.
*Gate:* zero double-claims under overlap; at least one typed `LOST_CLAIM` observed; a guard test
proving no claim rename or claim ledger append exists outside the pool; end-to-end work-order latency
no worse than the 15 s baseline.
*Rollback:* re-enable the Work-Order Runner task; the adapters keep their old bodies behind a flag for
one release.

**P4 — Collector under HOLD.** The collector tick runs on the wheel with `hold_required: true`, so it
fires while HOLD is set and every discretionary clock is skipped **with a recorded reason**. This build
does not lift HOLD and does not modify the collector's tick requirement — it only changes which
process wakes it.
*Gate:* with HOLD set, the collector's tick count over an hour equals the pre-collapse count; every
skipped clock carries reason `HOLD`; HOLD itself is untouched.
*Rollback:* return the collector to its own loop; the flag file is the switch.

**P5 — Core spawn handoff. Last, deliberately.**
Health `--supervise` is the only in-tree restarter of live Core `:8770`, so it stays exactly as it is
through P0–P4. In P5, Pulse takes a **single-owner spawn lease with a fencing token**, and Health stops
spawning **only after the lease read-back confirms Pulse holds it**. The lease is the interlock: two
spawners can never be live at once, and neither can zero.

**Core is never stopped.** This phase transfers *who would restart it*, not *whether it runs*.
*Gate:* the lease proves single-owner under forced contention; `:8770` answers on **every** 15 s sample
across the whole handoff window with zero misses (one miss aborts the phase); and a deliberate Core
kill **in a rehearsal instance, never live** is restarted by Pulse inside the window Health achieved.
*Rollback:* release the lease — Health resumes as restarter on its next tick.

---

## 6 · What is measured, and what is not

`tests/test_clocks_pulse_build.py` runs on this clone and exercises the engine and the gate. It is
written in the house style: a board of rows, worded outcomes, and **a planted-red row that must be RED
on every pass**. It sits in `tests/` rather than `proposals/` for one reason — `.gitlab-ci.yml` runs
`for t in tests/test_*.py`, so that is the only location where the GitLab check rail actually
*measures* this proposal instead of reading it. It touches nothing outside `proposals/pulse/` and the
manifest.

MEASURED here, on Linux, against the reference engine and the shipped manifest:

- 26 in / 26 out; a dropped clock refuses (`CLOCKS_SHRUNK`), an invented clock refuses (`UNKNOWN_CLOCK`)
- any `/delete` in the plan refuses; a schtask edit without read-back refuses
- no phase stops or restarts Core; the spawn handoff must be last and singular
- an undeclared cadence change refuses, and so does one past its declared tolerance — at both `Clock`
  construction and bind time
- single-flight, budget-defer-not-drop, HOLD-keeps-the-collector, stale-in-flight-quarantined
- Pulse refuses a `spawns_core` clock before P5
- a green planted-red control publishes `PULSE-BROKEN`

**UNMEASURED — and not invented green.** These need the live Windows host, which this lane cannot
reach and does not claim to have touched:

- `:8770` continuity across every phase
- cDeck glob and index panels green across the cutover
- work-order end-to-end latency versus the 15 s baseline
- the real cadences of the 26 clocks (that is precisely what P0 exists to measure)

A rail that is not wired is UNMEASURED, never invented green — `docs/WORK_ORDER_SOP.md` step 5, applied
to my own deliverable.

---

## 7 · Boundaries, item by item

| boundary from the order | how this build honours it |
|---|---|
| PROPOSE only; never write the live COSMOS tree | everything is under `proposals/` and `tests/`; the reference engine's `--execute` raises `REFUSED_PROPOSAL_ONLY` |
| never merge PR #30 or #32 | not merged, not read, not referenced as a source |
| do not shrink CLOCKS | 26 entries in, 26 out; `CLOCKS_SHRUNK` / `UNBOUND_CLOCK` refusals in the gate |
| do not `/delete` schtasks | allow-list of six verbs, none of them delete; a `/delete` pattern scan over the whole plan |
| do not take Core `:8770` down | no phase stops or restarts Core; the binder refuses one that does; P5 transfers spawn ownership under a lease with Core running throughout |
| Health `--supervise` stays until Pulse owns Core spawn | `resident.keep` through P0–P4; `SUPERVISE_DROPPED_EARLY` refusal; handoff must be the last phase |
| collector tick already required under HOLD | `hold_required: true`, runs under HOLD, requirement unchanged by this build |
| HOLD is not lifted | `guards.hold = not_lifted`; `HOLD_LIFT` pattern refusal |
| `ANTHROPIC_OFF` stays | `guards.anthropic_off = true`; `ANTHROPIC_ON` pattern refusal |
| do not write `V:\Ai` | `GROKBOT_PEN` and `ABSOLUTE_PATH` refusals; every path in the plan is relative or a `<PLACEHOLDER>` |
| independent of Lane A / PR #32 | Lane A not read; PR #32's body and files not opened; `docs/ORCHESTRATION.md` does not exist to read |

---

## 8 · Open questions COW must answer before P1

1. **The three missing context docs.** `AGENT_BRIEF.md`, `AGENT_BOUNDARIES.md`, `ORCHESTRATION.md` —
   publish them to the repo, or this build's boundary set stays partly unchecked.
2. **Which clocks tolerate a missed window?** That single predicate decides `pulse.once` vs
   `calendar.once` for every clock over 15 minutes, and only the live owner can answer it per clock.
3. **What gap does each clock tolerate (`max_interval_s`)?** Every clock whose period is not already
   a multiple of 15 s needs that number from its owner, and the binder refuses until it has one. If
   any clock tolerates less than 15 s it cannot be Pulse-owned at this grid at all, and somebody has
   to decide: keep it resident, or drop the grid to 5 s and accept 3× the wakeups.
4. **Does any non-pool claim surface hold state the pool does not model** — lane, priority, or an
   attempt-private workspace? P3 blocks until that is answered, because collapsing five surfaces onto
   a model that is missing a field is how work quietly stops being claimable.
