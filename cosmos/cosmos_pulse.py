#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pulse - 15s HOLD-aware Pulse (P0 shadow + Phase 1 collect).

First duty is RESULTS BACK via the collector (even under HOLD — in-flight
returns must land). P0 writes a distinct SHADOW heartbeat with the live
CLOCKS due-set (26/26 resident.keep). Does NOT claim live/queue. Does NOT
dispatch MOTIF while WD2 is still the dropper. Does NOT call oa-api. Does
NOT /delete schtasks. Does NOT shrink CLOCKS. HOLD never self-clears.

    py -3.14 cosmos\\cosmos_pulse.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_pulse.py --root ... --loop
    py -3.14 cosmos\\cosmos_pulse.py --root ... --status

--shim-wd2 writes logs/watchdog2_heartbeat.json as a collapse shim. Default
OFF so a live WD2 is not last-writer-raced. Turn on only after WD2 is stopped
or for hermetic tests.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    acquire_lock, heartbeat_age_s, read_heartbeat, write_heartbeat,
)
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402
from cosmos_pause import (  # noqa: E402
    classify_pause, is_paused, maybe_auto_resume, read_pause_flag,
)

WORKER = "cosmos-pulse"
TASK_NAME = "COSMOS Pulse"
TASK_NAME_LOGON = "COSMOS Pulse Logon"
HEARTBEAT_NAME = "pulse_heartbeat.json"
SHADOW_HEARTBEAT_NAME = "pulse_shadow_heartbeat.json"
WD2_SHIM_NAME = "watchdog2_heartbeat.json"
LOCK_NAME = "pulse.lock"
SCHEMA = "cosmos-pulse/1"
SHADOW_SCHEMA = "cosmos-pulse-shadow/1"
CLOCK_ID = 27
REQUIRED_CLOCKS = 26
DEFAULT_INTERVAL_S = 15.0
FRESH_S = 90.0

_COLLECT_KEYS = (
    "tick", "new_this_tick", "scanned", "elapsed_s", "error_count",
    "dhx_markers", "dhx_matched", "dhx_missing", "index_rows",
    "index_path", "by_source",
)


class PulseError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__("[%s] %s" % (kind, detail))


def _clocks_due_set() -> dict:
    """P0: observe the live CLOCKS registry. 26 in, 26 out, all resident.keep."""
    from cosmos_own_clocks import CLOCKS
    rows = []
    for spec in CLOCKS:
        rows.append({
            "id": spec["id"],
            "clock": spec["clock"],
            "task": spec["task"],
            "heartbeat": spec.get("heartbeat"),
            "disposition": "resident.keep",
            "dispatch": False,
            "claim": False,
            "schtask": "observe",
        })
    if len(rows) != REQUIRED_CLOCKS:
        raise PulseError(
            "CLOCKS_SHRUNK",
            "due-set has %d clocks, required %d — collapse must not drop names"
            % (len(rows), REQUIRED_CLOCKS))
    names = [r["clock"] for r in rows]
    if len(set(names)) != REQUIRED_CLOCKS:
        raise PulseError("CLOCKS_SHRUNK", "duplicate clock names in due-set")
    return {
        "schema": SHADOW_SCHEMA,
        "phase": "P0",
        "disposition": "resident.keep",
        "n": len(rows),
        "required": REQUIRED_CLOCKS,
        "clocks": rows,
        "dispatch": False,
        "claim": False,
        "schtask_delete": False,
    }


COLLECTOR_HB = "collector_heartbeat.json"
COLLECTOR_REUSE_S = 25.0


def _collect_once(root: str) -> dict:
    """Results back on this clock. HOLD does not skip. Never calls oa-api.

    If the collector daemon already ticked within COLLECTOR_REUSE_S, reuse
    that heartbeat instead of a second full walk (Pulse P0 dual-collect was
    ~10s and blew the 15s wheel).
    """
    try:
        paths = CosmosPaths(root)
        hb = read_heartbeat(paths.role("logs", COLLECTOR_HB))
        age = heartbeat_age_s(hb)
        if hb and age is not None and 0 <= age < COLLECTOR_REUSE_S:
            out = {"ok": True, "reused_age_s": age}
            for k in _COLLECT_KEYS:
                if k in hb:
                    out[k] = hb[k]
            # Collector's own tick (poll/idle) must not hide the reuse signal.
            out["tick"] = "reuse"
            return out
        from cosmos_collector import Collector
        rec = Collector(root).poll_once()
        out = {"ok": True}
        for k in _COLLECT_KEYS:
            if k in rec:
                out[k] = rec[k]
        return out
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}


def _rewrite_cdeck_feed(root: str) -> dict:
    """Existing cDeck feed --once callable. No second writer. No schtasks."""
    try:
        from cosmos_cdeck_feed import poll_once as feed_once
        rec = feed_once(root)
        return {
            "ok": True,
            "via": "poll_once",
            "feed": rec.get("feed") or rec.get("feed_path"),
        }
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}


def poll_once(root: str, polls: int = 0,
              interval_s: float = DEFAULT_INTERVAL_S,
              shim_wd2: bool = False) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    flag = read_pause_flag(paths)
    resume = maybe_auto_resume(paths, flag)
    if resume.get("cleared"):
        flag = read_pause_flag(paths)
    classified = classify_pause(flag)
    paused = is_paused(flag)
    collect = _collect_once(root)
    feed = _rewrite_cdeck_feed(root)
    shadow = _clocks_due_set()
    extra = {
        "schema": SCHEMA,
        "clock_id": CLOCK_ID,
        "phase": "P0",
        "state": "PAUSED" if paused else "RUNNING",
        "pause_class": classified.get("class"),
        "pause_why": classified.get("why"),
        "resume": resume,
        "assigned_this_pass": 0,
        "dispatch": False,
        "claim": False,
        "oa_api": "PAUSED_LANE",
        "feed": feed,
        "runner": "pool",
        "cosmos_run": "double-claim",
        "shim_wd2": bool(shim_wd2),
        "collect": collect,
        "shadow_n": shadow["n"],
        "note": (
            "P0 shadow: 26/26 resident.keep, collect first (HOLD still "
            "collects). No MOTIF drop, no claim_next, no oa-api, no "
            "schtasks /delete. HOLD never self-clears."
        ),
    }
    hb = write_heartbeat(
        logs / HEARTBEAT_NAME, WORKER, extra=extra,
        polls=polls, interval_s=interval_s)
    shadow_hb = write_heartbeat(
        logs / SHADOW_HEARTBEAT_NAME, WORKER + "-shadow",
        extra={
            "schema": SHADOW_SCHEMA,
            "phase": "P0",
            "due": shadow,
            "dispatch": False,
            "claim": False,
            "collect_ok": collect.get("ok"),
        },
        polls=polls, interval_s=interval_s)
    shim = None
    if shim_wd2:
        shim_extra = dict(extra)
        shim_extra["shim_from"] = "pulse"
        shim_extra["worker"] = "cosmos-watchdog2"
        shim = write_heartbeat(
            logs / WD2_SHIM_NAME, "cosmos-watchdog2", extra=shim_extra,
            polls=polls, interval_s=interval_s)
    return {
        "ok": True,
        "paused": paused,
        "pause_class": classified.get("class"),
        "heartbeat": hb,
        "shadow": shadow_hb,
        "due_n": shadow["n"],
        "collect": collect,
        "feed": feed,
        "shim_wd2": shim,
        "resume": resume,
        "path": str(logs / HEARTBEAT_NAME),
    }


def loop(root: str, interval_s: float, *, shim_wd2: bool = False) -> int:
    paths = CosmosPaths(root)
    lock = acquire_lock(paths.logs(LOCK_NAME))
    if lock is None:
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        print(json.dumps({
            "ok": False, "kind": "HELD",
            "detail": "pulse.lock held",
            "heartbeat_age_s": age,
        }, indent=1))
        return 2
    polls = 0
    try:
        while True:
            polls += 1
            rec = poll_once(root, polls=polls, interval_s=interval_s,
                            shim_wd2=shim_wd2)
            print(json.dumps({
                "polls": polls,
                "state": rec["heartbeat"].get("state"),
                "pause_class": rec.get("pause_class"),
            }, default=str), flush=True)
            time.sleep(max(0.2, interval_s))
    finally:
        os.close(lock)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_pulse")
    ap.add_argument("--root", required=True)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--shim-wd2", action="store_true",
                    help="Also write watchdog2_heartbeat.json (collapse shim).")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    a = ap.parse_args()
    if a.status:
        paths = CosmosPaths(a.root)
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        print(json.dumps({"path": str(paths.logs(HEARTBEAT_NAME)),
                          "age_s": age, "heartbeat": rec}, indent=1,
                         default=str))
        return 0 if age is not None and age < FRESH_S else 2
    if a.once:
        r = poll_once(a.root, interval_s=a.interval, shim_wd2=a.shim_wd2)
        print(json.dumps(r, indent=1, default=str))
        return 0 if r.get("ok") else 2
    if a.loop:
        return loop(a.root, a.interval, shim_wd2=a.shim_wd2)
    print(json.dumps({"ok": False, "kind": "BAD_ARGV",
                      "error": "pass --once, --loop, or --status"}, indent=1))
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
