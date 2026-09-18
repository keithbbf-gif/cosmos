#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Native-clock recall refresh. Not an agent loop.

    py -3.14 cosmos\\cosmos_recall_clock.py --root V:\\A\\Ai\\COSMOS\\live --once
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import create_task, query_task, tr_cmdline, write_heartbeat  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_recall import Recall, RecallError  # noqa: E402

TASK_NAME = "COSMOS Recall Refresh"


def once(root: str) -> dict:
    paths = CosmosPaths(root)
    key = paths.config("install_key.bin").read_bytes()
    from cosmos_ledger import Ledger
    led = Ledger(paths.ledger("authority.jsonl"), key, "recall-clock",
                 head_anchor=False)
    idx = paths.role("state", "recall", "turns.sqlite")
    rec = Recall(led, idx).refresh()
    rec["tree_id"] = paths.sentinel.tree_id
    rec["at"] = time.time()
    write_heartbeat(paths.logs() / "recall_clock_heartbeat.json",
                    "recall-clock", extra=rec)
    return rec


def standup(root: str) -> dict:
    """Native schtasks --once every 15m. Not an in-process cron.

    Already registered → started: already. Elevation denied → keith_cmd,
    never invented registered:true. Optional one run_now so the heartbeat
    exists; storms are refused by schtasks itself.
    """
    existing = query_task(TASK_NAME)
    if existing.get("ok"):
        return {
            "ok": True,
            "started": "already",
            "task": TASK_NAME,
            "query": True,
            "keith_cmd": None,
            "needs_elevation": False,
        }
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once")
    rec = create_task(TASK_NAME, tr, "minute", mo=15, run_now=True)
    rec["task"] = TASK_NAME
    rec["started"] = "schtasks" if rec.get("ok") else "refused"
    if rec.get("needs_elevation") or not rec.get("ok"):
        rec["ok"] = False
        rec["registered"] = False
    else:
        rec["ok"] = True
        rec["registered"] = True
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    args = ap.parse_args()
    if args.standup:
        rec = standup(args.root)
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("ok") or rec.get("needs_elevation") else 2
    if not args.once:
        print("usage: --root <live> --once")
        return 2
    try:
        rec = once(args.root)
    except RecallError as e:
        print(json.dumps({"ok": False, "error": e.kind, "detail": str(e)}))
        return 2
    print(json.dumps(rec, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
