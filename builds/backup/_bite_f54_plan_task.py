#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: F-54 packer has no schtasks vehicle (required before belief).

The incumbent cosmos_state_offsite.py can --preflight / --selfcheck / --once
and REFUSES NO_OFFSITE_ROUTE. Nothing emits a schtasks /create line. F-47
and F-48 clocks push *scopes*, not the F-54 whitelist (SEED / inflight /
tracker). Without --plan-task the packed payload is never armed.

    py -3.14 builds/backup/_bite_f54_plan_task.py
    py -3.14 builds/backup/_bite_f54_plan_task.py --impl <staged incumbent>
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_bite_f54_plan_task.json"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("so_bite_f54", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def bite(impl: Path) -> dict:
    rec: dict = {"impl": str(impl), "exists": impl.is_file()}
    if not impl.is_file():
        rec.update({"state": "ABSENT", "all_bite": True})
        return rec
    so = _load(impl)
    rec["has_plan_task_argv"] = hasattr(so, "plan_task_argv")
    rec["has_install_task"] = hasattr(so, "install_task")
    rec["has_TASK_NAME"] = hasattr(so, "TASK_NAME")
    rec["has_DEFAULT_AT"] = hasattr(so, "DEFAULT_AT")
    rec["has_STALE_S"] = hasattr(so, "STALE_S")
    p = subprocess.run(
        [sys.executable, str(impl), "--root", str(HERE), "--plan-task"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=60)
    rec["cli_plan_task_rc"] = p.returncode
    err = (p.stderr or "") + (p.stdout or "")
    low = err.lower()
    rec["cli_plan_task_unrecognized"] = (
        "unrecognized arguments" in low
        or "one of the arguments" in low
        or "--plan-task" in err and p.returncode != 0)
    rec["cli_plan_task_not_a_verb"] = p.returncode != 0
    rec["cli_plan_task_stderr_tail"] = err[-400:]
    rec["all_bite"] = (
        rec["has_plan_task_argv"] is False
        and rec["has_install_task"] is False
        and rec["has_TASK_NAME"] is False
        and rec["cli_plan_task_not_a_verb"] is True)
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--impl", default=str(HERE / "cosmos_state_offsite.py"))
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    rec = bite(Path(a.impl))
    Path(a.out).write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    print("all_bite", rec.get("all_bite"))
    return 0 if rec.get("all_bite") else 1


if __name__ == "__main__":
    raise SystemExit(main())
