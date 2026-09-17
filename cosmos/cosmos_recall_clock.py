#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_recall_clock - native recall refresh (CLOCKS id 27).

One schtasks /sc minute /mo 15 --once tick; not an in-process cron loop.
Each tick rebuilds the GET /api/v1/recall projection via cosmos_recall.refresh
and writes live/logs/recall_clock_heartbeat.json.

Does not modify kernel / ledger / sched / service.

    py -3.14 cosmos\\cosmos_recall_clock.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_recall_clock.py --root ... --standup
    py -3.14 cosmos\\cosmos_recall_clock.py --root ... --plan-task
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    create_task, plan_create, query_task, tr_cmdline, write_heartbeat,
)
from cosmos_paths import CosmosPathError, CosmosPaths  # noqa: E402
from cosmos_recall import refresh, snapshot  # noqa: E402

WORKER = "cosmos-recall-clock"
SCHEMA = "cosmos-recall-clock/1"
CLOCK_ID = 27
TASK_NAME = "COSMOS Recall Refresh"
HEARTBEAT_NAME = "recall_clock_heartbeat.json"
NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def _assert_clock_id() -> str | None:
    from cosmos_own_clocks import CLOCKS
    hits = [c for c in CLOCKS if c.get("id") == CLOCK_ID]
    if len(hits) != 1:
        return "clock id %s hits=%d in CLOCKS (need 1)" % (CLOCK_ID, len(hits))
    if hits[0].get("script") != "cosmos_recall_clock.py":
        return "clock id %s script mismatch" % CLOCK_ID
    if hits[0].get("task") != TASK_NAME:
        return "clock id %s task is not %s" % (CLOCK_ID, TASK_NAME)
    return None


def poll_once(root: str, *, dry_run: bool = False) -> dict:
    t0 = time.time()
    clock_err = _assert_clock_id()
    if clock_err:
        return {"ok": False, "state": "REFUSED", "kind": "IDENTITY_MISMATCH",
                "detail": clock_err, "clock_id": CLOCK_ID}
    paths = CosmosPaths(root)
    if dry_run:
        snap = snapshot(paths)
        return {"ok": True, "state": "DRY_RUN", "kind": snap.get("kind"),
                "clock_id": CLOCK_ID, "dry_run": True}
    rec = refresh(paths)
    elapsed = round(time.time() - t0, 3)
    extra = {
        "ok": bool(rec.get("ok")),
        "state": "REFRESHED",
        "kind": rec.get("kind"),
        "n_sources": rec.get("n_sources"),
        "dest": rec.get("dest"),
        "bytes": rec.get("bytes"),
        "clock_id": CLOCK_ID,
        "elapsed_s": elapsed,
        "schema": SCHEMA,
    }
    if clock_err:
        extra["clock_id_error"] = clock_err
    hb_path = paths.logs() / HEARTBEAT_NAME
    hb = write_heartbeat(hb_path, WORKER, extra=extra)
    return {
        "ok": bool(rec.get("ok")),
        "state": "REFRESHED",
        "kind": rec.get("kind"),
        "dest": rec.get("dest"),
        "heartbeat": hb,
        "heartbeat_path": str(hb_path),
        "elapsed_s": elapsed,
        "clock_id": CLOCK_ID,
    }


def standup(root: str) -> dict:
    """Register the 15-minute --once task if missing."""
    clock_err = _assert_clock_id()
    existing = query_task(TASK_NAME)
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once")
    if existing.get("ok"):
        tick_rec = poll_once(root, dry_run=False)
        return {
            "started": "already",
            "task": existing,
            "tick": tick_rec,
            "keith_cmd": None,
            "task_name": TASK_NAME,
            "clock_id": CLOCK_ID,
            "clock_id_error": clock_err,
        }
    task = create_task(TASK_NAME, tr, "minute", mo=15, run_now=False)
    tick_rec = poll_once(root)
    return {
        "started": "schtasks" if task.get("ok") else "planned",
        "task": task,
        "tick": tick_rec,
        "proof": {"ok": tick_rec.get("ok"), "heartbeat": tick_rec.get("heartbeat")},
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
        "task_name": TASK_NAME,
        "clock_id": CLOCK_ID,
        "clock_id_error": clock_err,
    }


def plan_task_argv(root: Path) -> list[str]:
    tr = tr_cmdline(Path(__file__).resolve(), str(root), "--once")
    return plan_create(TASK_NAME, tr, "minute", mo=15)


def emit_plan(root: str) -> dict:
    argv = plan_task_argv(Path(root))
    tr = tr_cmdline(Path(__file__).resolve(), root, "--once")
    return {
        "schema": "cosmos-recall-clock-plan/1",
        "clock_id": CLOCK_ID,
        "task_name": TASK_NAME,
        "cadence": "schtasks /sc minute /mo 15 --once",
        "tr": tr,
        "argv": argv,
        "argv_cmdline": subprocess.list2cmdline(argv),
        "heartbeat": HEARTBEAT_NAME,
        "script": "cosmos/cosmos_recall_clock.py",
        "root": str(Path(root).resolve()),
        "once_flag": "--once",
        "note": "Native Windows clock only; not an in-process cron loop.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_recall_clock")
    ap.add_argument("--root", help="runtime root (live/)")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--plan-task", action="store_true")
    a = ap.parse_args()
    if a.plan_task:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}), file=sys.stderr)
            return 2
        print(json.dumps(emit_plan(a.root), indent=1))
        return 0
    if a.standup:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}), file=sys.stderr)
            return 2
        rec = standup(a.root)
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("started") in ("already", "schtasks") else 2
    if not a.root:
        print(json.dumps({"ok": False, "kind": "NO_ROOT",
                          "detail": "--root is required"}), file=sys.stderr)
        return 2
    if not (a.once or a.dry_run):
        a.once = True
    rec = poll_once(a.root, dry_run=bool(a.dry_run))
    print(json.dumps(rec, indent=1, default=str))
    return 0 if rec.get("ok") else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(json.dumps({"ok": False, "state": "REFUSED", "kind": "NO_ROOT",
                          "detail": str(e)}), file=sys.stderr)
        raise SystemExit(2)
