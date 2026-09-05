#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pulse_bind - the BINDING GATE for the CLOCKS collapse. PROPOSAL ONLY.

The build manifest cannot name the 26 live clocks: this lane never reads the live tree,
and a plan that invents clock names is worse than a plan that admits it does not know
them. So the manifest ships UNBOUND and this gate REFUSES it until every name in the live
`CLOCKS` registry has been bound to exactly one disposition.

That refusal is the point. It makes four of Keith's boundaries structural instead of
hopeful:

  * DO NOT SHRINK CLOCKS - bind() refuses unless the bound set EQUALS the live set, name
    for name. A collapse that "tidied away" an entry cannot pass this gate.
  * DO NOT CHANGE A CADENCE BY ACCIDENT - a clock the 15s grid would re-time must declare
    the gap it tolerates, or the gate refuses it.
  * DO NOT /delete SCHTASKS - any schtask action outside the allow-list, or any command
    string containing /delete, is a refusal.
  * DO NOT TAKE CORE :8770 DOWN - any action that stops, kills, or restarts Core is a
    refusal, and Health --supervise may not be stood down before the phase that hands
    Core spawn to Pulse.
  * HOLD / ANTHROPIC_OFF STAY - any action clearing HOLD or re-enabling Anthropic is a
    refusal; a clock required under HOLD may not be parked.

Usage:
    python pulse_bind.py --plan ../clocks-pulse-build.json --live-clocks live_clocks.json

`live_clocks.json` is a READ-ONLY export of the live registry, produced on the desktop by
COW - `{"clocks": ["<name>", ...]}` - not by this lane.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

DISPOSITIONS = frozenset({"pulse.inproc", "pulse.once", "calendar.once",
                          "resident.keep", "parked"})
PULSE_OWNED = frozenset({"pulse.inproc", "pulse.once"})

# schtasks verbs a proposal may ask COW to run. /delete is not one of them, ever.
ALLOWED_SCHTASK_ACTIONS = frozenset({
    "keep",             # untouched
    "register",         # new calendar --once trigger, then READ BACK with /query /xml
    "change_disable",   # stood down, still registered, one /change away from returning
    "change_enable",    # the rollback verb
    "change_period",    # cadence edit only
    "rename_delme",     # parked under a _delme name; still registered
})

FORBIDDEN_PATTERNS = (
    (re.compile(r"/delete\b", re.I), "SCHTASK_DELETE"),
    (re.compile(r"\bstop-service\b|\bnet\s+stop\b|\btaskkill\b", re.I), "CORE_DOWN"),
    (re.compile(r"\bhold\s*(=|:)?\s*(0|off|false)\b|--lift-hold\b", re.I), "HOLD_LIFT"),
    (re.compile(r"ANTHROPIC_OFF\s*(=|:)\s*(0|false|off)\b", re.I), "ANTHROPIC_ON"),
    (re.compile(r"^[A-Za-z]:\\|^/(?!/)", re.M), "ABSOLUTE_PATH"),
    (re.compile(r"V:\\+Ai\b", re.I), "GROKBOT_PEN"),
)


class BindError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


@dataclass
class BindReport:
    ok: bool = False
    refusals: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    census: dict[str, int] = field(default_factory=dict)
    bound: int = 0
    required: int = 0

    def refuse(self, kind: str, detail: str) -> None:
        self.refusals.append({"kind": kind, "detail": detail})

    @property
    def verdict(self) -> str:
        if self.ok:
            return (f"BOUND: {self.bound}/{self.required} live clocks re-homed, none dropped; "
                    f"census {self.census}")
        kinds = sorted({r['kind'] for r in self.refusals})
        return f"REFUSED x{len(self.refusals)} {kinds}"

    def to_dict(self) -> dict:
        return {"ok": self.ok, "verdict": self.verdict, "bound": self.bound,
                "required": self.required, "census": self.census,
                "refusals": self.refusals, "notes": self.notes}


def _scan_text(report: BindReport, where: str, text: str) -> None:
    for rx, kind in FORBIDDEN_PATTERNS:
        if rx.search(text):
            report.refuse(kind, f"{where}: {text!r} matches the {kind} fence")


def bind(plan: dict, live_clocks: Iterable[str]) -> BindReport:
    """Validate a build manifest against the live CLOCKS registry. Refusals are collected,
    not raised one at a time: an operator should see every reason at once, not peel them."""
    r = BindReport()
    live = list(live_clocks)
    live_set = set(live)
    if len(live) != len(live_set):
        r.refuse("DUPLICATE_LIVE_CLOCK",
                 "the live export lists a clock twice - fix the export before binding")

    tick_s = float(plan.get("pulse", {}).get("tick_s", 0) or 0)
    if tick_s <= 0:
        r.refuse("BAD_TICK", "pulse.tick_s missing or non-positive")

    bindings = plan.get("bindings", {})
    required = int(bindings.get("bind_required", 0) or 0)
    bound_rows = bindings.get("bound", [])
    r.required = required or len(live_set)
    r.bound = len(bound_rows)

    if required and live_set and required != len(live_set):
        r.refuse("REGISTRY_COUNT_MISMATCH",
                 f"plan expects {required} live clocks, the export lists {len(live_set)} - "
                 f"one of the two is stale; refusing rather than picking a winner")

    seen: set[str] = set()
    census = {d: 0 for d in sorted(DISPOSITIONS)}
    hold_clocks: list[str] = []
    supervise_rows: list[dict] = []

    for row in bound_rows:
        cid = row.get("clock")
        if not cid:
            r.refuse("NAMELESS_BINDING", f"binding without a clock name: {row!r}")
            continue
        if cid in seen:
            r.refuse("DUPLICATE_BINDING", f"{cid} bound twice - one clock, one home")
            continue
        seen.add(cid)
        if live_set and cid not in live_set:
            r.refuse("UNKNOWN_CLOCK",
                     f"{cid} is bound but is not in the live registry - a plan that invents "
                     f"a clock will silently not run the real one")
        disp = row.get("disposition")
        if disp not in DISPOSITIONS:
            r.refuse("UNKNOWN_DISPOSITION", f"{cid}: {disp!r} not in {sorted(DISPOSITIONS)}")
            continue
        census[disp] += 1

        period = float(row.get("period_s", 0) or 0)
        deadline = float(row.get("deadline_s", 0) or 0)
        tolerance = row.get("max_interval_s")
        if period <= 0 or deadline <= 0:
            r.refuse("BAD_PERIOD", f"{cid}: period={period} deadline={deadline}")
        elif disp in PULSE_OWNED and tick_s > 0:
            effective = max(1, math.ceil(period / tick_s)) * tick_s
            if effective == period:
                pass
            elif tolerance is None:
                r.refuse("QUANTIZATION_UNDECLARED",
                         f"{cid}: the {tick_s}s grid moves this cadence {period}s -> "
                         f"{effective}s and no max_interval_s says whether that is "
                         f"tolerable - only the duty's owner knows")
            elif effective > float(tolerance):
                r.refuse("QUANTIZATION_EXCEEDS_TOLERANCE",
                         f"{cid}: {period}s quantizes to {effective}s on the {tick_s}s grid, "
                         f"past the {tolerance}s gap it tolerates - keep it resident or give "
                         f"the wheel a finer grid; do not round the tolerance away")
            else:
                r.notes.append(f"{cid}: cadence {period}s -> {effective}s within its "
                               f"{tolerance}s tolerance (declared quantization, not a "
                               f"silent one)")

        if row.get("hold_required"):
            hold_clocks.append(cid)
            if disp == "parked":
                r.refuse("HOLD_DUTY_PARKED",
                         f"{cid} is required under HOLD and parked in the same breath")
        if row.get("spawns_core") and disp in PULSE_OWNED:
            phase = row.get("core_spawn_phase")
            if phase is None:
                r.refuse("CORE_SPAWN_UNPHASED",
                         f"{cid} touches Core spawn but names no phase - Health --supervise "
                         f"stays the only restarter until the handoff phase")
        if str(row.get("role", "")).startswith("health.supervise"):
            supervise_rows.append(row)
        for key in ("command", "note"):
            if row.get(key):
                _scan_text(r, f"bindings[{cid}].{key}", str(row[key]))

    missing = sorted(live_set - seen)
    if missing:
        r.refuse("UNBOUND_CLOCK",
                 f"{len(missing)} live clock(s) have no disposition: {missing[:8]}"
                 f"{' ...' if len(missing) > 8 else ''} - every clock is re-homed or the "
                 f"plan does not apply")
    if live_set and len(seen) < len(live_set):
        r.refuse("CLOCKS_SHRUNK",
                 f"{len(seen)} bound vs {len(live_set)} live - the registry may be re-homed, "
                 f"never shortened")
    if not bound_rows:
        r.refuse("UNBOUND_PLAN",
                 "no clock is bound: this manifest is a design, not an applicable change. "
                 "COW exports the live CLOCKS registry and binds it before apply.")

    # health --supervise must survive until Pulse owns Core spawn
    handoff = [p for p in plan.get("phases", []) if p.get("grants_core_spawn")]
    for row in supervise_rows:
        if row.get("disposition") != "resident.keep" and not handoff:
            r.refuse("SUPERVISE_DROPPED_EARLY",
                     f"{row.get('clock')}: Health --supervise is the only in-tree restarter "
                     f"of live Core :8770 and no phase grants Core spawn to Pulse")

    _check_schtasks(r, plan)
    _check_phases(r, plan)
    _check_guards(r, plan)

    r.census = census
    r.ok = not r.refusals
    return r


def _check_schtasks(r: BindReport, plan: dict) -> None:
    for t in plan.get("schtasks", []):
        name, action = t.get("name", "?"), t.get("action")
        if action not in ALLOWED_SCHTASK_ACTIONS:
            r.refuse("FORBIDDEN_SCHTASK_ACTION",
                     f"{name}: {action!r} not in {sorted(ALLOWED_SCHTASK_ACTIONS)} - nothing "
                     f"is deleted; a parked task is one /change from coming back")
        _scan_text(r, f"schtasks[{name}]", json.dumps(t))
        if action in ("register", "change_period", "change_disable") and not t.get("read_back"):
            r.refuse("NO_READ_BACK",
                     f"{name}: a schtask edit without a /query read-back is an exit code, "
                     f"not a measurement")


def _check_phases(r: BindReport, plan: dict) -> None:
    phases = plan.get("phases", [])
    if not phases:
        r.refuse("NO_PHASES", "a collapse with no ordered phases is a flag day")
        return
    for p in phases:
        pid = p.get("id", "?")
        if not p.get("gate"):
            r.refuse("PHASE_WITHOUT_GATE", f"{pid}: no gate - an unmeasured phase cannot pass")
        if not p.get("rollback"):
            r.refuse("PHASE_WITHOUT_ROLLBACK", f"{pid}: no rollback")
        if p.get("core_restart") or p.get("core_stop"):
            r.refuse("CORE_DOWN", f"{pid}: phase stops or restarts Core :8770")
        _scan_text(r, f"phases[{pid}]", json.dumps(p))
    ids = [p.get("id") for p in phases]
    if ids != sorted(ids):
        r.refuse("PHASE_ORDER", f"phases are not in applied order: {ids}")
    grants = [p for p in phases if p.get("grants_core_spawn")]
    if len(grants) > 1:
        r.refuse("TWO_SPAWN_OWNERS", "more than one phase grants Core spawn")
    if grants and grants[0].get("id") != ids[-1]:
        r.refuse("SPAWN_HANDOFF_EARLY",
                 f"Core-spawn handoff is phase {grants[0].get('id')}, not the last phase "
                 f"({ids[-1]}) - it is the only step that can lose the restarter")


def _check_guards(r: BindReport, plan: dict) -> None:
    g = plan.get("guards", {})
    if g.get("posture") != "PROPOSE-ONLY":
        r.refuse("POSTURE", "guards.posture must be PROPOSE-ONLY")
    if g.get("anthropic_off") is not True:
        r.refuse("ANTHROPIC_ON", "guards.anthropic_off must stay true")
    if g.get("hold") != "not_lifted":
        r.refuse("HOLD_LIFT", "guards.hold must be not_lifted")
    if int(g.get("core_port", 0)) != 8770:
        r.refuse("CORE_PORT", "guards.core_port must be 8770 and must stay up")
    fence = g.get("write_fence") or []
    if "proposals/" not in fence:
        r.refuse("WRITE_FENCE", "guards.write_fence must contain proposals/")
    for path in plan.get("outputs", []):
        if not any(str(path).startswith(f) for f in fence):
            r.refuse("WRITE_FENCE", f"output {path!r} is outside {fence}")


def load_live_clocks(p: Path) -> list[str]:
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("clocks", [])
    if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
        raise BindError("BAD_EXPORT",
                        f"{p}: expected {{'clocks': ['name', ...]}} - refusing to guess")
    return data


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="CLOCKS binding gate (PROPOSAL ONLY)")
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--live-clocks", type=Path,
                    help="read-only export of the live CLOCKS registry; omit to check "
                         "manifest self-consistency only")
    args = ap.parse_args(argv)

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    live = load_live_clocks(args.live_clocks) if args.live_clocks else []
    rep = bind(plan, live)
    print(json.dumps(rep.to_dict(), indent=1))
    return 0 if rep.ok else 2


if __name__ == "__main__":
    sys.exit(main())
