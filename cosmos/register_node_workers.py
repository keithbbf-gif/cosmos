#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""schtasks self-heal registration for GROK + GEM bucket daemons.

EMIT-ONLY. This helper NEVER calls schtasks / create_task / run_schtasks.
Keith runs the one elevated `keith_cmd` after COW files the worker onto
the live tree. Windowless pythonw --loop, 1-min self-heal + ONLOGON
relaunch, same vehicle as cosmos_runner / cosmos_collector.

    py -3.14 cosmos\\register_node_workers.py --root V:\\A\\Ai\\COSMOS\\live
    py -3.14 cosmos\\register_node_workers.py --root <live> --plan

Both invocations print the /Create plan and exit 0. There is no --apply.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import plan_create, pythonw_exe, tr_cmdline  # noqa: E402
from cosmos_node_bucket_worker import NODES  # noqa: E402


def worker_script() -> Path:
    return Path(__file__).resolve().parent / "cosmos_node_bucket_worker.py"


def plan_tr(root: str, node: str) -> str:
    """pythonw.exe <script> --root <root> --node <node> --loop"""
    return tr_cmdline(worker_script(), root, "--node", node, "--loop")


def plan_loop_argv(root: str, node: str) -> list[str]:
    return [pythonw_exe(), str(worker_script()),
            "--root", str(Path(root).resolve()),
            "--node", node, "--loop"]


def plan_minute(root: str, node: str) -> list[str]:
    spec = NODES[node]
    return plan_create(spec["task_name"], plan_tr(root, node), "minute", mo=1)


def plan_logon(root: str, node: str) -> list[str]:
    spec = NODES[node]
    return plan_create(spec["task_logon"], plan_tr(root, node), "onlogon")


def plan_node(root: str, node: str) -> dict:
    spec = NODES[node]
    return {
        "node": node,
        "task_name": spec["task_name"],
        "task_logon": spec["task_logon"],
        "heartbeat": spec["heartbeat"],
        "lock": spec["lock"],
        "script": str(worker_script()),
        "tr": plan_tr(root, node),
        "loop_argv": plan_loop_argv(root, node),
        "minute": plan_minute(root, node),
        "logon": plan_logon(root, node),
        "windowless": True,
    }


def keith_cmd(root: str) -> str:
    """One elevated line: /Create for grok+gem minute+logon (four tasks)."""
    argv_lists = []
    for node in ("grok", "gem"):
        argv_lists.append(plan_minute(root, node))
        argv_lists.append(plan_logon(root, node))
    return " & ".join(subprocess.list2cmdline(a) for a in argv_lists)


def plan(root: str) -> dict:
    return {
        "ok": True,
        "ran_schtasks": False,
        "emit_only": True,
        "script": str(worker_script()),
        "windowless": True,
        "vehicle": "detached --loop daemon + 1-min self-heal + onlogon",
        "note": (
            "EMIT-ONLY. This helper does not call schtasks. "
            "Keith runs keith_cmd from an elevated prompt."
        ),
        "nodes": [plan_node(root, n) for n in ("grok", "gem")],
        "keith_cmd": keith_cmd(root),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="register_node_workers")
    ap.add_argument("--root", required=True)
    ap.add_argument("--plan", action="store_true",
                    help="print argv only (default behaviour either way)")
    a = ap.parse_args(argv)
    rec = plan(a.root)
    print(json.dumps(rec, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
