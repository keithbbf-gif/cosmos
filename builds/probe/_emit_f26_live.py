#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Live F-26 dry-run + plan-task. Writes nothing under the live root.

    py -3.14 builds/probe/_emit_f26_live.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cosmos_newai_scout as sc  # noqa: E402

ROOT = Path(r"V:\A\Ai\COSMOS\live")
REPO = HERE.parents[1]
OUT = HERE / "_f26_live_dryrun.json"
PLAN = HERE / "_f26_plan_task.json"


def _count_under(root: Path) -> int:
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        n += len(filenames)
    return n


def main() -> int:
    before = _count_under(ROOT)
    rec = sc.tick(ROOT, REPO, dry_run=True)
    after = _count_under(ROOT)
    rec["live_files_before"] = before
    rec["live_files_after"] = after
    rec["live_files_delta"] = after - before
    rec["heartbeat_exists"] = (ROOT / "logs" / sc.HEARTBEAT_NAME).is_file()
    rec["projection_exists"] = ROOT.joinpath(*sc.PROJECTION_REL).is_file()
    # Drop nothing secret-shaped; candidates are names only.
    OUT.write_text(json.dumps(rec, indent=1, default=str) + "\n", encoding="utf-8")
    argv = sc.plan_task_argv(ROOT)
    PLAN.write_text(json.dumps({"task": sc.TASK_NAME, "argv": argv,
                                "registers": False}, indent=1) + "\n",
                    encoding="utf-8")
    print(json.dumps({
        "ok": rec.get("ok"),
        "kind": rec.get("kind"),
        "new_count": rec.get("new_count"),
        "known_count": rec.get("known_count"),
        "feed_count": rec.get("feed_count"),
        "writes": rec.get("writes"),
        "delta": rec["live_files_delta"],
        "heartbeat_exists": rec["heartbeat_exists"],
        "candidates_head": [c.get("name") for c in rec.get("candidates", [])[:8]],
        "plan_tn": argv[3] if len(argv) > 3 else None,
    }, indent=2))
    return 0 if rec.get("kind") in ("MINED", "NEW_NONE") and rec.get("writes") == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
