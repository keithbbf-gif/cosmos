#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Orch harvest: bind live CLOCKS names into PR #38 P0 plan. Does not write cosmos/."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, r"V:\A\Ai\COSMOS\cosmos")
from cosmos_own_clocks import CLOCKS  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pulse_bind import bind, load_live_clocks  # noqa: E402

OUT = Path(r"V:\A\Ai\COSMOS\work_orders\ccr")
PR38 = Path(__file__).resolve().parent

PERIOD = {
    1: 15, 2: 30, 3: 15, 4: 900, 5: 3600, 6: 2, 7: 60, 8: 60, 9: 60,
    10: 0.75, 11: 21600, 12: 300, 13: 60, 14: 5, 15: 15, 16: 2, 17: 15,
    18: 60, 19: 3600, 20: 10, 21: 15, 22: 15, 23: 3600, 24: 60, 25: 2, 26: 15,
}


def target_disposition(cid: int) -> str:
    if cid in (16, 25):
        return "parked"
    if cid in (6, 15):
        return "resident.keep"
    if cid in (1, 3, 4):
        return "parked"
    if cid in (5, 11, 19, 23):
        return "calendar.once"
    if cid == 10:
        return "pulse.inproc"
    return "pulse.once"


def role_for(cid: int) -> str:
    return {
        6: "health.supervise",
        2: "collector.tick",
        17: "workorder.runner",
        10: "cdeck.feed",
        13: "index.required_daemons",
    }.get(cid, "")


def note_for(cid: int) -> str:
    if cid == 2:
        return "Collector tick required (HOLD lifted 2026-09-04; still required)."
    if cid in (16, 25):
        return "CVM 2s TABLED. Park later; do not inproc. P0 keeps resident."
    if cid == 4:
        return "Motif Driver is not a second dropper. Pulse owns MOTIF. P0 keeps resident."
    if cid == 6:
        return "Health --supervise resident.keep until P5. Never P5 this tick."
    return "P0 shadow: live loops stay; Pulse computes due-set only."


def main() -> int:
    rows = []
    for c in CLOCKS:
        p = float(PERIOD[c["id"]])
        rows.append({
            "id": c["id"],
            "clock": c["clock"],
            "task": c["task"],
            "script": c["script"],
            "cadence": c["cadence"],
            "logon": c.get("logon"),
            "extra_tasks": c.get("extra_tasks") or [],
            "heartbeat": c["heartbeat"],
            "vehicle": c["vehicle"],
            "period_s": p,
            "deadline_s": max(p * 3.0, 45.0),
            "disposition": "resident.keep",
            "p0": "resident.keep",
            "target_disposition": target_disposition(c["id"]),
            "hold_required": c["id"] == 2,
            "spawns_core": c["id"] == 6,
            "core_spawn_phase": "P5" if c["id"] == 6 else None,
            "role": role_for(c["id"]),
            "park_cvm": c["id"] in (16, 25),
            "note": note_for(c["id"]),
        })

    export = {
        "schema": "cosmos-clocks-export/1",
        "source": "cosmos/cosmos_own_clocks.py CLOCKS",
        "tree_id": "KMesh-COSMOS-live",
        "count": len(rows),
        "clocks": [r["clock"] for r in rows],
        "records": rows,
        "ccr_lease": "ABSENT",
        "p0": "observe-only harvest; not applied to cosmos/cosmos_pulse.py",
    }
    export_path = OUT / "live-clocks-export.json"
    export_path.write_text(json.dumps(export, indent=2), encoding="utf-8")

    names_path = PR38 / "live-clocks-names.json"
    names_path.write_text(
        json.dumps({"clocks": [r["clock"] for r in rows]}, indent=2),
        encoding="utf-8")

    plan = json.loads(
        (PR38 / "clocks-pulse-build.unbound.json").read_text(encoding="utf-8"))
    plan["bindings"]["bound"] = [{
        "clock": r["clock"],
        "disposition": r["disposition"],
        "period_s": r["period_s"],
        "deadline_s": r["deadline_s"],
        "hold_required": r["hold_required"],
        "spawns_core": r["spawns_core"],
        "core_spawn_phase": r["core_spawn_phase"],
        "role": r["role"],
        "target_disposition": r["target_disposition"],
        "note": r["note"],
    } for r in rows]

    slot_map = {
        "workorder.runner": "COSMOS Work-Order Runner",
        "collector.tick": "COSMOS Collector",
        "health.supervise": "COSMOS Health",
        "cdeck.feed": "COSMOS cDeck Feed",
        "index.required_daemons": "COSMOS Index",
    }
    for s in plan["role_slots"]["slots"]:
        role = s["role"]
        if role in slot_map:
            s["bind"] = slot_map[role]
        elif role == "core.service":
            s["bind"] = "COSMOS Core :8770 (not a CLOCKS row; never_touched)"
            s["note"] = (
                "Core is the resident service, not CLOCKS id 1-26. "
                "P0 does not touch :8770.")
    plan["role_slots"]["note"] = (
        "Bound 2026-09-04 orch harvest against live cosmos_own_clocks.py. "
        "P0 dispositions are all resident.keep (observe, dispatch nothing). "
        "target_disposition is later-phase intent; not applied this tick. "
        "HOLD already lifted (PAUSE.flag absent); collector still "
        "hold_required. Do not re-arm HOLD. Never P5 this tick.")
    plan["p0_shadow"] = {
        "applied": False,
        "why": "CCR.lease ABSENT — orch TUI does not write cosmos/*.py",
        "observe": True,
        "dispatch": False,
        "claim": False,
        "merge_into": (
            "cosmos/cosmos_pulse.py (existing Phase 1; "
            "pulse_heartbeat STALE)"),
        "never": [
            "schtasks /delete", "stop :8770", "P5 on live", "merge PR #38",
        ],
    }

    bound_path = OUT / "pr38-p0-bound.json"
    bound_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    (PR38 / "pr38-p0-bound.json").write_text(
        json.dumps(plan, indent=2), encoding="utf-8")

    live_names = load_live_clocks(names_path)
    rep = bind(plan, live_names)
    (OUT / "pr38-p0-bind-report.json").write_text(
        json.dumps(rep.to_dict(), indent=2), encoding="utf-8")
    (PR38 / "bind-report.json").write_text(
        json.dumps(rep.to_dict(), indent=2), encoding="utf-8")
    print(json.dumps({
        "export": str(export_path),
        "bound_plan": str(bound_path),
        "bind_ok": rep.ok,
        "verdict": rep.verdict,
        "bound": rep.bound,
        "required": rep.required,
        "census": rep.census,
        "refusal_count": len(rep.refusals),
        "refusal_kinds": sorted({x["kind"] for x in rep.refusals}),
        "refusals": rep.refusals[:12],
    }, indent=2))
    return 0 if rep.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
