#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_drive_meter - 1-minute drive-health satellite for massive volumes.

Cadence rubric: drive meters are schtasks ~1 min, never a 0.5s loop (they
must not hammer SMART / tree-walk a huge volume). This clock uses
shutil.disk_usage only — free/total/used. No tree walk, no bts_*.

Closed table of Keith's COSMOS/BTS volumes plus the runtime-root drive.
A missing drive is reported ABSENT, not a fault to invent.

    py -3.14 cosmos\\cosmos_drive_meter.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_drive_meter.py --root ... --standup

Task: COSMOS Drive Meter. Does not honor PAUSE. Does not modify core.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    create_task, heartbeat_age_s, query_task, read_heartbeat, tr_cmdline,
    write_heartbeat, atomic_json,
)
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

WORKER = "cosmos-drive-meter"
TASK_NAME = "COSMOS Drive Meter"
HEARTBEAT_NAME = "drive_meter_heartbeat.json"
SCHEMA = "cosmos-drive-meter/1"
FRESH_S = 180.0

# Closed table. Labels are identity notes, not a walk list.
DRIVE_TABLE = (
    ("V:\\", "COSMOS/BTS mesh volume"),
    ("C:\\", "system"),
    ("D:\\", "data / PhD / backups"),
    ("X:\\", "Google Drive (My Drive)"),
)


def _usage(letter_root: str) -> dict:
    p = Path(letter_root)
    rec = {"path": letter_root, "present": p.exists()}
    if not rec["present"]:
        rec["ok"] = True
        rec["state"] = "ABSENT"
        return rec
    try:
        u = shutil.disk_usage(letter_root)
    except OSError as e:
        rec.update({"ok": False, "state": "UNREADABLE",
                    "detail": f"{type(e).__name__}: {e}"})
        return rec
    total, used, free = int(u.total), int(u.used), int(u.free)
    pct_free = (free / total * 100.0) if total else 0.0
    rec.update({
        "ok": True,
        "state": "OK",
        "total_bytes": total,
        "used_bytes": used,
        "free_bytes": free,
        "pct_free": round(pct_free, 2),
        "warn": pct_free < 10.0,
    })
    return rec


def poll_once(root: str) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    dest_dir = paths.state("drive")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "meter.json"
    t0 = time.time()

    drives = []
    seen = set()
    for letter, label in DRIVE_TABLE:
        rec = _usage(letter)
        rec["label"] = label
        drives.append(rec)
        seen.add(os.path.splitdrive(letter)[0].upper())

    # Always include the runtime-root's volume even if it is not in the table.
    root_drive = os.path.splitdrive(str(paths.root))[0].upper()
    if root_drive and (root_drive + "\\") not in {
            d["path"].upper() for d in drives}:
        rec = _usage(root_drive + "\\")
        rec["label"] = "runtime-root volume"
        drives.append(rec)

    present = [d for d in drives if d.get("present")]
    warn = [d["path"] for d in present if d.get("warn")]
    extra = {
        "schema": SCHEMA,
        "tick": "once",
        "ok": True,
        "present_count": len(present),
        "warn_count": len(warn),
        "warn": warn,
        "projection": str(dest),
        "elapsed_s": round(time.time() - t0, 3),
        "runtime_root_drive": root_drive,
    }
    hb = write_heartbeat(logs / HEARTBEAT_NAME, WORKER, extra=extra)
    projection = {
        "schema": SCHEMA,
        "measured_at": hb["last_run"],
        "measured_epoch": hb["last_run_epoch"],
        "worker": WORKER,
        "drives": drives,
        "warn": warn,
        "elapsed_s": extra["elapsed_s"],
    }
    atomic_json(dest, projection)
    return {"ok": True, "heartbeat": hb, "projection": str(dest),
            "present_count": len(present), "warn_count": len(warn)}


def standup(root: str) -> dict:
    existing = query_task(TASK_NAME)
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once")
    tick = poll_once(root)
    if existing.get("ok"):
        return {"started": "already", "task": existing, "tick": tick,
                "keith_cmd": None, "task_name": TASK_NAME}
    task = create_task(TASK_NAME, tr, "minute", mo=1, run_now=False)
    return {
        "started": "schtasks" if task.get("ok") else "in-process-tick",
        "task": task,
        "tick": {"present_count": tick.get("present_count"),
                 "warn_count": tick.get("warn_count")},
        "proof": {"ok": True, "heartbeat": tick.get("heartbeat")},
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
        "task_name": TASK_NAME,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_drive_meter")
    ap.add_argument("--root", required=True)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.status:
        paths = CosmosPaths(a.root)
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        print(json.dumps({"path": str(paths.logs(HEARTBEAT_NAME)),
                          "age_s": age, "heartbeat": rec}, indent=1,
                         default=str))
        return 0 if age is not None and age < FRESH_S else 2
    if a.standup:
        r = standup(a.root)
        print(json.dumps(r, indent=1, default=str))
        return 0 if r.get("started") else 2
    r = poll_once(a.root)
    print(json.dumps({"ok": True, "present_count": r["present_count"],
                      "warn_count": r["warn_count"],
                      "projection": r["projection"]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
