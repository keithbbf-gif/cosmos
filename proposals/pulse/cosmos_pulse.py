#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pulse - REFERENCE ENGINE for the CLOCKS collapse. PROPOSAL ONLY.

This file lives under proposals/. It is not the live tree, it never writes the live
tree, and it refuses to execute anything: `--execute` raises REFUSED_PROPOSAL_ONLY.
Its job is to make the Pulse contract *executable* so the design can be argued with a
test run instead of a paragraph.

THE CONTRACT (see proposals/clocks-pulse-build.md for the argument):
  * ONE resident tick at 15 s replaces N resident loops. 15 s is not a taste: it is the
    tightest live cadence in the tree (the ~15 s Work-Order Runner), and a collapse that
    lengthens the tightest cadence is a behaviour change wearing a refactor's clothes.
  * A clock's period is QUANTIZED to the grid (ceil to a multiple of the tick). A clock
    whose cadence CHANGES under quantization must DECLARE how much slip it tolerates
    (max_interval_s); an undeclared cadence change is REFUSED, and a declared tolerance
    that the grid cannot meet is REFUSED. Never silently rounded.
  * SINGLE-FLIGHT: a clock still running when its next slot comes is SKIPPED and the skip
    is recorded. Ticks never queue up behind a slow job; overlap is the double-claim shape.
  * BUDGET: work that does not fit the tick's wall budget is DEFERRED with a reason and
    runs first next tick. Deferred is a state; dropped is a defect.
  * REPORT-NEVER-RETRY: an in-flight clock past its deadline is reported STALE and
    quarantined. Only a clock that DECLARES itself idempotent may be re-dispatched.
  * NEGATIVE CONTROL AS A ROW: the plan carries a planted-red clock. If it ever reports
    CLEAN, the verdict is PULSE-BROKEN and no green is published.
  * PULSE DOES NOT SPAWN CORE. A clock flagged `spawns_core` is refused unless the
    Core-spawn lease has been handed over (phase 5). Health --supervise stays the only
    restarter of live Core :8770 until then.
  * ABSENT != UNREADABLE != CHANGED != EMPTY. The heartbeat carries per-clock state and
    per-clock stale_after_s so a reader never has to infer staleness from a bare mtime.

Stdlib only, no imports from the live tree, deterministic clocks injectable.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional, Protocol

TICK_S = 15.0

DISPOSITIONS = frozenset({
    "pulse.inproc",    # dispatched inside the Pulse process; must be cheap and idempotent
    "pulse.once",      # Pulse spawns `<command> --once`; crash-isolated
    "calendar.once",   # Task Scheduler calendar trigger, --once; Pulse must NEVER dispatch it
    "resident.keep",   # stays a resident process (Core, Health --supervise, Pulse itself)
    "parked",          # loop stood down, duty absorbed elsewhere; CLOCKS entry RETAINED
})
PULSE_OWNED = frozenset({"pulse.inproc", "pulse.once"})

OUTCOMES = frozenset({"CLEAN", "FINDINGS", "BROKE"})

SKIP_INFLIGHT = "INFLIGHT"
SKIP_HOLD = "HOLD"
SKIP_BUDGET = "BUDGET"
SKIP_QUARANTINED = "QUARANTINED"
SKIP_CORE_SPAWN = "CORE_SPAWN_NOT_OWNED"


class PulseError(RuntimeError):
    """kind in {UNKNOWN_DISPOSITION, BAD_PERIOD, MISSING_COMMAND, QUANTIZATION_UNDECLARED,
    QUANTIZATION_EXCEEDS_TOLERANCE, HOLD_DUTY_PARKED, DUPLICATE_CLOCK, NOT_PULSE_OWNED,
    REFUSED_PROPOSAL_ONLY, BAD_OUTCOME}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


class LostClaim(RuntimeError):
    """Raised by a claim surface that lost the race. Typed, clean, and NOT fatal to the tick."""


# --------------------------------------------------------------------------- clocks
@dataclass(frozen=True)
class Clock:
    """One entry of the live CLOCKS registry, re-homed. The registry is never shrunk:
    every live clock keeps an entry here, and `disposition` records where it now runs."""

    id: str
    disposition: str
    period_s: float                  # how often the duty is meant to run
    deadline_s: float                # how long ONE run may take before it is STALE
    max_interval_s: Optional[float] = None   # largest tolerable GAP between runs; required
                                             # once the grid changes the declared cadence
    hold_required: bool = False      # runs even while HOLD is set (e.g. the collector tick)
    idempotent: bool = False         # may be re-dispatched after a stale in-flight
    budget_ms: int = 250             # expected inproc cost; used for tick admission
    lane: str = "default"
    command: Optional[str] = None    # required for pulse.once / calendar.once
    spawns_core: bool = False        # touches Core :8770 lifecycle
    planted_red: bool = False        # negative control: must never report CLEAN
    tick_s: float = TICK_S

    def __post_init__(self) -> None:
        if self.disposition not in DISPOSITIONS:
            raise PulseError("UNKNOWN_DISPOSITION",
                             f"{self.id}: {self.disposition!r} not in {sorted(DISPOSITIONS)}")
        if self.period_s <= 0 or self.deadline_s <= 0:
            raise PulseError("BAD_PERIOD",
                             f"{self.id}: period={self.period_s} deadline={self.deadline_s} "
                             f"- a clock with no period is not a clock")
        if self.disposition in ("pulse.once", "calendar.once") and not self.command:
            raise PulseError("MISSING_COMMAND",
                             f"{self.id}: {self.disposition} needs the command it invokes "
                             f"- 'the daemon knows' is how a tick becomes unrunnable")
        if self.hold_required and self.disposition == "parked":
            raise PulseError("HOLD_DUTY_PARKED",
                             f"{self.id}: required under HOLD and parked at the same time")
        if self.disposition in PULSE_OWNED and self.quantized:
            if self.max_interval_s is None:
                raise PulseError("QUANTIZATION_UNDECLARED",
                                 f"{self.id}: the {self.tick_s}s grid moves this cadence "
                                 f"{self.period_s}s -> {self.effective_period_s}s and no "
                                 f"max_interval_s says whether that is tolerable - only the "
                                 f"duty's owner knows, so refuse rather than assume")
            if self.effective_period_s > self.max_interval_s:
                raise PulseError("QUANTIZATION_EXCEEDS_TOLERANCE",
                                 f"{self.id}: {self.period_s}s quantizes to "
                                 f"{self.effective_period_s}s, past the {self.max_interval_s}s "
                                 f"gap it tolerates - keep it resident or take a finer grid; "
                                 f"do not round the tolerance away")

    @property
    def slots(self) -> int:
        """Period in whole ticks. Never zero: the grid is the floor on cadence."""
        return max(1, math.ceil(self.period_s / self.tick_s))

    @property
    def effective_period_s(self) -> float:
        """The cadence this clock ACTUALLY gets after quantization. Declared, never implied."""
        return self.slots * self.tick_s

    @property
    def quantized(self) -> bool:
        return self.effective_period_s != self.period_s

    @property
    def phase(self) -> int:
        """Deterministic slot offset so 26 clocks do not all land on the same tick.
        Derived from the id, not from boot order or random - two runs agree, and so do
        two lanes reading the same plan."""
        h = hashlib.sha1(self.id.encode("utf-8")).digest()
        return int.from_bytes(h[:4], "big") % self.slots

    @property
    def stale_after_s(self) -> float:
        """A reader's staleness threshold: two full periods plus the deadline. Published so
        no reader has to guess a clock's cadence from a filename."""
        return 2 * self.effective_period_s + self.deadline_s

    def due_at(self, tick_seq: int) -> bool:
        return (tick_seq - self.phase) % self.slots == 0


# --------------------------------------------------------------------------- dispatch
class Handle(Protocol):
    def poll(self) -> Optional[str]:
        """Terminal outcome (CLEAN / FINDINGS / BROKE), or None while still running."""


@dataclass
class Done:
    """A dispatch that finished inside the tick."""

    outcome: str

    def __post_init__(self) -> None:
        if self.outcome not in OUTCOMES:
            raise PulseError("BAD_OUTCOME",
                             f"{self.outcome!r} not in {sorted(OUTCOMES)} - three words, "
                             f"never a bare rc")

    def poll(self) -> Optional[str]:
        return self.outcome


@dataclass
class Running:
    """A dispatch that outlived the tick (a spawned --once child). Pulse polls it."""

    probe: Callable[[], Optional[str]]

    def poll(self) -> Optional[str]:
        out = self.probe()
        if out is not None and out not in OUTCOMES:
            raise PulseError("BAD_OUTCOME", f"{out!r} not in {sorted(OUTCOMES)}")
        return out


@dataclass
class _InFlight:
    handle: Handle
    started_tick: int
    started_epoch: float


# --------------------------------------------------------------------------- wheel
class Wheel:
    """The due-set calculator. Holds every clock in the registry - including the ones Pulse
    does not dispatch - because the registry must not shrink to make the wheel tidy."""

    def __init__(self, clocks: Iterable[Clock], tick_s: float = TICK_S):
        self.tick_s = tick_s
        self.clocks: dict[str, Clock] = {}
        for c in clocks:
            if c.id in self.clocks:
                raise PulseError("DUPLICATE_CLOCK", f"{c.id} declared twice")
            if c.tick_s != tick_s:
                raise PulseError("BAD_PERIOD",
                                 f"{c.id}: clock grid {c.tick_s}s != wheel grid {tick_s}s")
            self.clocks[c.id] = c

    @property
    def owned(self) -> list[Clock]:
        return [c for c in self.clocks.values() if c.disposition in PULSE_OWNED]

    def residency_census(self) -> dict[str, int]:
        out = {d: 0 for d in sorted(DISPOSITIONS)}
        for c in self.clocks.values():
            out[c.disposition] += 1
        return out

    def due(self, tick_seq: int) -> list[Clock]:
        """Due clocks for this tick, ordered cheapest-first so a fat job cannot starve the
        cheap ones out of the wall budget."""
        due = [c for c in self.owned if c.due_at(tick_seq)]
        return sorted(due, key=lambda c: (c.budget_ms, c.id))


# --------------------------------------------------------------------------- pulse
class Pulse:
    """The single resident tick. Dispatches; does not do the work itself."""

    def __init__(self, wheel: Wheel, dispatch: Callable[[Clock], Handle], *,
                 identity: str = "pulse@unbound",
                 now: Callable[[], float] = time.time,
                 mono: Callable[[], float] = time.monotonic,
                 tick_budget_s: float = 5.0,
                 hold: Callable[[], bool] = lambda: False,
                 claim_next: Optional[Callable[[], Optional[dict]]] = None,
                 max_claims_per_tick: int = 4,
                 core_spawn_owner: bool = False):
        if tick_budget_s <= 0 or tick_budget_s >= wheel.tick_s:
            raise PulseError("BAD_PERIOD",
                             f"tick budget {tick_budget_s}s must sit inside the "
                             f"{wheel.tick_s}s grid - a tick that can consume its own period "
                             f"is a resident loop again")
        self.wheel = wheel
        self.dispatch = dispatch
        self.identity = identity
        self._now = now
        self._mono = mono
        self.tick_budget_s = tick_budget_s
        self._hold = hold
        self._claim_next = claim_next
        self.max_claims_per_tick = max_claims_per_tick
        self.core_spawn_owner = core_spawn_owner

        self.tick_seq = 0
        self.inflight: dict[str, _InFlight] = {}
        self.quarantined: dict[str, str] = {}
        self.deferred: list[str] = []
        self.last: dict[str, dict] = {}
        self.grid_t0: Optional[float] = None
        self.skew_ticks = 0

    # ---------------- grid ----------------
    def grid_advance(self) -> int:
        """Advance to the next grid slot. Deadlines come from t0 + n*tick, so a slow tick
        does NOT push the grid - drift cannot accumulate. Missed slots are REPORTED (skew),
        and at most one catch-up runs: a backlog replay is how a 15 s clock becomes a stampede."""
        t = self._mono()
        if self.grid_t0 is None:
            self.grid_t0 = t
            self.tick_seq = 0
            return 0
        want = int((t - self.grid_t0) // self.wheel.tick_s)
        missed = max(0, want - self.tick_seq - 1)
        if missed:
            self.skew_ticks += missed
        self.tick_seq = max(self.tick_seq + 1, want)
        return self.tick_seq

    def seconds_to_next_slot(self) -> float:
        if self.grid_t0 is None:
            return 0.0
        elapsed = self._mono() - self.grid_t0
        return max(0.0, ((self.tick_seq + 1) * self.wheel.tick_s) - elapsed)

    # ---------------- the tick ----------------
    def tick(self) -> dict:
        seq = self.grid_advance()
        t_start = self._mono()
        report: dict = {"tick_seq": seq, "epoch": self._now(), "hold": bool(self._hold()),
                        "ran": {}, "skipped": {}, "deferred": [], "stale": [],
                        "claims": {"taken": 0, "lost": 0, "empty": False},
                        "skew_ticks": self.skew_ticks, "refusals": []}

        self._poll_inflight(seq, report)

        # deferrals first, in the order they were deferred: a job pushed out of one tick
        # must not be pushed out of the next one by a fresh arrival.
        queue: list[Clock] = [self.wheel.clocks[i] for i in self.deferred
                              if i in self.wheel.clocks]
        seen = {c.id for c in queue}
        for c in self.wheel.due(seq):
            if c.id not in seen:
                queue.append(c)
        self.deferred = []

        # Admission uses the WORSE of what the clocks declared they cost and what the tick
        # has actually burned so far. Declared-only lets a lying clock overrun the tick;
        # measured-only admits everything on a fast machine and then blows the budget.
        planned = 0.0
        measured = 0.0
        for c in queue:
            spent = max(planned, measured)
            skip = self._skip_reason(c)
            if skip:
                report["skipped"][c.id] = skip
                if skip == SKIP_CORE_SPAWN:
                    report["refusals"].append(
                        f"{c.id}: refused - Pulse does not own Core spawn; Health "
                        f"--supervise is still the restarter")
                continue
            if spent + (c.budget_ms / 1000.0) > self.tick_budget_s and report["ran"]:
                # never drop: the clock keeps its place at the head of the next tick
                self.deferred.append(c.id)
                report["skipped"][c.id] = SKIP_BUDGET
                continue
            t0 = self._mono()
            planned += c.budget_ms / 1000.0
            try:
                handle = self.dispatch(c)
            except Exception as e:                                        # noqa: BLE001
                self._record(c, "BROKE", f"dispatch RAISED {type(e).__name__}: {e}", seq)
                report["ran"][c.id] = "BROKE"
                measured += self._mono() - t0
                continue
            out = handle.poll()
            if out is None:
                self.inflight[c.id] = _InFlight(handle, seq, self._now())
                report["ran"][c.id] = "RUNNING"
            else:
                self._record(c, out, "", seq)
                report["ran"][c.id] = out
            measured += self._mono() - t0

        report["deferred"] = list(self.deferred)
        self._drain_claims(report)
        report["elapsed_s"] = self._mono() - t_start
        report["verdict"] = self._verdict(report)
        report["heartbeat"] = self.heartbeat(report)
        return report

    def _skip_reason(self, c: Clock) -> Optional[str]:
        if c.disposition not in PULSE_OWNED:
            raise PulseError("NOT_PULSE_OWNED",
                             f"{c.id} is {c.disposition} and must never be dispatched by Pulse")
        if c.id in self.quarantined:
            return SKIP_QUARANTINED
        if c.id in self.inflight:
            return SKIP_INFLIGHT
        if c.spawns_core and not self.core_spawn_owner:
            return SKIP_CORE_SPAWN
        if self._hold() and not c.hold_required:
            return SKIP_HOLD
        return None

    def _poll_inflight(self, seq: int, report: dict) -> None:
        for cid, fl in list(self.inflight.items()):
            c = self.wheel.clocks[cid]
            out = fl.handle.poll()
            if out is not None:
                self._record(c, out, "", seq)
                del self.inflight[cid]
                continue
            age = (seq - fl.started_tick) * self.wheel.tick_s
            if age > c.deadline_s:
                # REPORT, never retry. Its side effects may already have happened.
                self._record(c, "BROKE", f"STALE in-flight {age:.0f}s past "
                                         f"{c.deadline_s:.0f}s deadline - reported, NOT retried",
                             seq, state="STALE")
                report["stale"].append(cid)
                del self.inflight[cid]
                if not c.idempotent:
                    self.quarantined[cid] = ("stale in-flight; not declared idempotent - "
                                             "an operator clears this, a timer does not")

    def _drain_claims(self, report: dict) -> None:
        """POOL-ONLY. Pulse holds no claim logic of its own; it calls the one surface and
        stops. Bounded per tick so a burst of work cannot starve the wheel."""
        if self._claim_next is None:
            return
        for _ in range(self.max_claims_per_tick):
            try:
                item = self._claim_next()
            except LostClaim:
                report["claims"]["lost"] += 1
                continue
            if item is None:
                report["claims"]["empty"] = True
                return
            report["claims"]["taken"] += 1

    def _record(self, c: Clock, outcome: str, detail: str, seq: int,
                state: str = "IDLE") -> None:
        if outcome not in OUTCOMES:
            raise PulseError("BAD_OUTCOME", f"{c.id}: {outcome!r} not in {sorted(OUTCOMES)}")
        self.last[c.id] = {"outcome": outcome, "detail": detail, "epoch": self._now(),
                           "tick_seq": seq, "state": state}

    def _verdict(self, report: dict) -> str:
        planted = [c for c in self.wheel.owned if c.planted_red]
        for c in planted:
            rec = self.last.get(c.id)
            if rec and rec["outcome"] == "CLEAN":
                return ("PULSE-BROKEN: the planted-red clock reported CLEAN - this tick "
                        "cannot detect failure, so none of its greens mean anything")
        if not planted:
            return ("PULSE-UNVERIFIED: no planted-red clock in the plan - a wheel with no "
                    "negative control has never been seen to fail")
        # the control's own BROKE is the board working, not a finding
        control_ids = {c.id for c in planted}
        broke = [i for i, o in report["ran"].items()
                 if o == "BROKE" and i not in control_ids]
        if report["stale"]:
            return f"RED: {len(report['stale'])} stale in-flight reported"
        if broke:
            return f"RED x{len(broke)}"
        return "GREEN"

    # ---------------- heartbeat ----------------
    def heartbeat(self, report: Optional[dict] = None) -> dict:
        """ONE heartbeat carrying every clock, replacing N per-daemon files. Aware-local +
        epoch + UTC + writer identity, because a naked local stamp has already been misread
        as five hours stale and a healthy runner reported dead."""
        now = self._now()
        local = _dt.datetime.fromtimestamp(now).astimezone()
        clocks = {}
        for cid, c in self.wheel.clocks.items():
            rec = self.last.get(cid)
            if cid in self.quarantined:
                state = "QUARANTINED"
            elif cid in self.inflight:
                state = "RUNNING"
            elif rec is None:
                state = "NEVER-RUN"      # not "stale", not "green": a fourth state, kept
            else:
                state = rec["state"]
            clocks[cid] = {
                "residency": c.disposition,
                "effective_period_s": c.effective_period_s,
                "declared_period_s": c.period_s,
                "quantized": c.quantized,
                "max_interval_s": c.max_interval_s,
                "stale_after_s": c.stale_after_s,
                "hold_required": c.hold_required,
                "state": state,
                "last_run_epoch": rec["epoch"] if rec else None,
                "last_outcome": rec["outcome"] if rec else None,
                "detail": rec["detail"] if rec else "",
            }
        return {
            "writer": self.identity,
            "mechanism": f"pulse-{self.wheel.tick_s:g}s",
            "tick_seq": self.tick_seq,
            "epoch": now,
            "utc": _dt.datetime.fromtimestamp(now, _dt.timezone.utc).isoformat(),
            "local": local.isoformat(),
            "tz_offset": local.strftime("%z"),
            "skew_ticks": self.skew_ticks,
            "census": self.wheel.residency_census(),
            "clock_count": len(self.wheel.clocks),
            "verdict": report["verdict"] if report else None,
            "clocks": clocks,
        }

    def legacy_heartbeats(self) -> dict[str, dict]:
        """Compatibility shim for the collapse window: the same tick data, re-emitted under
        the per-daemon filenames the cDeck glob and the index already watch. Readers move
        when they are ready; nothing goes red because a writer changed."""
        hb = self.heartbeat()
        out = {}
        for cid, row in hb["clocks"].items():
            out[f"clock_heartbeat__{cid}.json"] = {
                "writer": self.identity, "via": "pulse", "clock": cid,
                "epoch": row["last_run_epoch"], "state": row["state"],
                "stale_after_s": row["stale_after_s"], "utc": hb["utc"],
                "local": hb["local"], "tz_offset": hb["tz_offset"],
            }
        return out


# --------------------------------------------------------------------------- plan I/O
def clocks_from_plan(plan: dict, tick_s: float = TICK_S) -> list[Clock]:
    """Build the wheel from the build manifest's bound clocks. An unbound plan yields an
    empty wheel - and Pulse refuses to serve one (see main)."""
    out = []
    for row in plan.get("bindings", {}).get("bound", []):
        out.append(Clock(
            id=row["clock"],
            disposition=row["disposition"],
            period_s=float(row["period_s"]),
            deadline_s=float(row["deadline_s"]),
            max_interval_s=(float(row["max_interval_s"])
                            if row.get("max_interval_s") is not None else None),
            hold_required=bool(row.get("hold_required", False)),
            idempotent=bool(row.get("idempotent", False)),
            budget_ms=int(row.get("budget_ms", 250)),
            lane=str(row.get("lane", "default")),
            command=row.get("command"),
            spawns_core=bool(row.get("spawns_core", False)),
            planted_red=bool(row.get("planted_red", False)),
            tick_s=tick_s,
        ))
    return out


def _dry_dispatch(c: Clock) -> Handle:
    """Dry run: nothing is executed. The planted-red row still reports BROKE, so a dry run
    that shows the control green is itself a finding."""
    return Done("BROKE" if c.planted_red else "CLEAN")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Pulse reference engine (PROPOSAL ONLY)")
    ap.add_argument("--plan", type=Path, required=True, help="build manifest JSON")
    ap.add_argument("--ticks", type=int, default=1)
    ap.add_argument("--tick-s", type=float, default=TICK_S)
    ap.add_argument("--hold", action="store_true", help="simulate HOLD set")
    ap.add_argument("--execute", action="store_true",
                    help="refused: this file is a proposal, not the live clock")
    args = ap.parse_args(argv)

    if args.execute:
        raise PulseError("REFUSED_PROPOSAL_ONLY",
                         "this engine lives under proposals/ and will not execute the live "
                         "tree; COW applies an accepted proposal, an agent does not")

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    clocks = clocks_from_plan(plan, tick_s=args.tick_s)
    if not clocks:
        print("REFUSED [UNBOUND_PLAN]: no clock is bound in "
              f"{args.plan} - the wheel is empty, and an empty wheel that starts is a "
              "silent outage. Bind the live CLOCKS registry first "
              "(proposals/pulse/pulse_bind.py).")
        return 2

    p = Pulse(Wheel(clocks, tick_s=args.tick_s), _dry_dispatch,
              identity="pulse@dry-run", hold=lambda: args.hold)
    seq = 0
    for _ in range(args.ticks):
        rep = p.tick()
        seq = rep["tick_seq"]
        print(json.dumps({k: v for k, v in rep.items() if k != "heartbeat"},
                         indent=1, sort_keys=True))
        p.grid_t0 = (p.grid_t0 or 0) - args.tick_s   # advance the simulated grid one slot
    print(json.dumps(p.heartbeat(), indent=1, sort_keys=True))
    return 0 if seq >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
