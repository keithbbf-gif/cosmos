#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_daemon - mail-drop work-order reader.

Polls the queue/bucket for JSON work orders, acts on them, writes status back.
Process is defined in SOP.md — keep them together.

Usage:
    py -3.14 cosmos_daemon.py --root <live> --once
    py -3.14 cosmos_daemon.py --root <live>
    py -3.14 cosmos_daemon.py --root <live> --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos.cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

WORKER = "cosmos-daemon"
HEARTBEAT_NAME = "daemon_heartbeat.json"
SLEEP_S = 60
OPEN_STATES = frozenset({"DROPPED", "PICKED_UP"})


def _iso(ts=None):
    if ts is None:
        return datetime.now().astimezone().isoformat(timespec="seconds")
    return datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


def _read_json(path: Path):
    if not path.is_file():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    return obj if isinstance(obj, dict) else None


def work_order_dirs(paths: CosmosPaths):
    q = paths.queue()
    return {
        "bucket": q / "bucket",
        "picked": q / "picked",
        "done": q / "done",
    }


def open_orders(paths: CosmosPaths, agent_substr: str) -> list[Path]:
    dirs = work_order_dirs(paths)
    found = []
    for name in ("bucket", "picked"):
        folder = dirs[name]
        if not folder.is_dir():
            continue
        for p in folder.glob("*.json"):
            obj = _read_json(p)
            if not obj:
                continue
            agent = str(obj.get("Agent") or "").lower()
            if agent_substr.lower() not in agent:
                continue
            if obj.get("state") in OPEN_STATES:
                found.append(p)
    return found


def claim(path: Path) -> dict | None:
    obj = _read_json(path)
    if not obj:
        return None
    obj["state"] = "PICKED_UP"
    obj["picked_at"] = _iso()
    tmp = path.with_suffix(".part")
    tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    os.replace(tmp, path)
    return obj


def finish(path: Path, dirs, obj: dict, result: dict) -> Path:
    obj["state"] = "DONE"
    obj["done_at"] = _iso()
    obj["result"] = result
    dest = dirs["done"] / path.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    os.replace(tmp, dest)
    path.unlink(missing_ok=True)
    return dest


def act_on(obj: dict, repo: Path) -> dict:
    """Dispatch by task. Test one: verify cosmos-test.txt."""
    task = str(obj.get("Task") or "").lower()
    if "cosmos-test" in task or "verify github write" in task:
        target = repo / "cosmos-test.txt"
        if not target.is_file():
            return {"ok": False, "kind": "MISSING_FILE", "path": str(target)}
        text = target.read_text(encoding="utf-8")
        expected = "This is a test for the Cosmo Orchestrator"
        ok = expected in text
        return {
            "ok": ok,
            "kind": "TEST_ONE",
            "path": str(target),
            "chars": len(text),
            "matched": ok,
        }
    return {"ok": False, "kind": "UNKNOWN_TASK", "task": obj.get("Task")}


def poll_once(root: str, *, dry_run: bool = False) -> dict:
    paths = CosmosPaths(root)
    dirs = work_order_dirs(paths)
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    repo = Path(__file__).resolve().parent
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    hb = logs / HEARTBEAT_NAME

    rec = {
        "schema": "cosmos-daemon/1",
        "worker": WORKER,
        "ok": True,
        "dry_run": dry_run,
        "tree_id": paths.sentinel.tree_id,
        "handled": 0,
        "errors": 0,
        "orders": [],
    }

    pending = open_orders(paths, "daemon") or open_orders(paths, "grok")
    if not pending:
        rec["state"] = "IDLE"
    else:
        rec["state"] = "WORKING"
        # flood guard: one at a time
        p = pending[0]
        if dry_run:
            rec["orders"].append({"path": str(p), "action": "would-claim"})
        else:
            obj = claim(p)
            if obj is None:
                rec["errors"] += 1
                rec["orders"].append({"path": str(p), "error": "unreadable"})
            else:
                result = act_on(obj, repo)
                dest = finish(p, dirs, obj, result)
                rec["handled"] += 1
                rec["orders"].append({
                    "from": str(p), "to": str(dest),
                    "result": result,
                })
                if not result.get("ok"):
                    rec["errors"] += 1

    if not dry_run:
        tmp = hb.with_suffix(".tmp")
        tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
        os.replace(tmp, hb)
    rec["heartbeat"] = str(hb)
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="cosmos_daemon")
    ap.add_argument("--root", required=True, help="runtime root (live/)")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--loop", action="store_true", help="run forever, sleeping between ticks")
    a = ap.parse_args(argv)

    try:
        if a.once or not a.loop:
            rec = poll_once(a.root, dry_run=a.dry_run)
            print(json.dumps(rec, indent=1, default=str))
            return 0 if rec.get("ok") else 2
        while True:
            rec = poll_once(a.root, dry_run=a.dry_run)
            print(json.dumps(rec, indent=1, default=str), flush=True)
            time.sleep(SLEEP_S)
    except CosmosPathError as e:
        print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
