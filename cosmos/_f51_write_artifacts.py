#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write UTF-8 F-51 live artifacts. No key material. Does not spawn or register."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
LIVE = REPO / "live"
MOD = HERE / "cosmos_resession.py"


def run(args: list[str], dest: Path) -> None:
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    dest.write_text(p.stdout, encoding="utf-8")
    print(f"{dest.name} rc={p.returncode} bytes={dest.stat().st_size}")


def main() -> int:
    run(["py", "-3.14", str(MOD), "--root", str(LIVE), "--dry-run"],
        HERE / "_f51_live_dryrun.json")
    run(["py", "-3.14", str(MOD), "--root", str(LIVE), "--plan-task"],
        HERE / "_f51_plan_task.json")
    d = json.loads((HERE / "_f51_live_dryrun.json").read_text(encoding="utf-8"))
    p = json.loads((HERE / "_f51_plan_task.json").read_text(encoding="utf-8"))
    pr = json.loads((HERE / "_f51_promote.json").read_text(encoding="utf-8"))
    b = json.loads((HERE / "_bite_f51_promote.json").read_text(encoding="utf-8"))
    summary = {
        "dry_run_state": d.get("state"),
        "dry_run_tree": d.get("tree_id"),
        "dry_run_clock": d.get("clock_id"),
        "prompt_sha": d.get("prompt_sha"),
        "why": d.get("why"),
        "plan_task": p.get("task"),
        "plan_clock_id": p.get("clock_id"),
        "promote_ok": pr.get("ok"),
        "promote": "%s/%s" % (pr.get("passed"), pr.get("total")),
        "bite": b.get("all_bite"),
        "live_hb": (LIVE / "logs" / "resession_heartbeat.json").exists(),
        "live_proj": (LIVE / "state" / "control" / "RESESSION.json").exists(),
    }
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
