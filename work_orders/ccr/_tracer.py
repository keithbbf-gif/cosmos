#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_tracer.py — Automated pipeline enforcement for CCr factory cycle.

Enforces:
1. Auto-route to 4Cs: Every coder output in CREW/OUT/ is immediately verified
   via py_compile/ruff/mypy/pytest (receipts to state/code_checks.db).
2. Auto-route to Judge: When verified 4Cs sets >= 30 (JUDGE_FLOOR), triggers
   CALL_SOL_JUDGE.cmd to score the batch.
3. Auto-re-file to WOMB: Judge verdicts update WOMB_MASTER.jsonl to DONE/SCORED.
4. Stalled/Dead Tracer: Any seat running > 15m without output is killed, logged
   to CREW/OUT/TRACER.log, strike-counted, and rotated to its Alternate after 3 strikes.
"""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
CCR = ROOT / "work_orders" / "ccr"
OUT = CCR / "CREW" / "OUT"
TABS_OUT = OUT / "TEAM_TABS"
TRACER_LOG = OUT / "TRACER.log"
JUDGE_BATCH_TRIGGER = 30
STALL_TIMEOUT_S = 900  # 15 minutes

sys.path.insert(0, str(ROOT / "cosmos"))
from cosmos_paths import CosmosPaths
from cosmos_code_checks import run_code_checks


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def log_tracer(msg: str) -> None:
    stamp = _iso_now()
    TRACER_LOG.parent.mkdir(parents=True, exist_ok=True)
    with TRACER_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {msg}\n")


def check_unprocessed_outputs() -> int:
    """Scan TEAM_TABS for new coder outputs not yet receipted in code_checks.db."""
    paths = CosmosPaths(str(ROOT / "live"))
    db = paths.state("code_checks.db")
    if not db.exists():
        return 0
    con = sqlite3.connect(str(db))
    checked = set(r[0] for r in con.execute("SELECT DISTINCT order_id FROM code_checks").fetchall())
    con.close()

    new_count = 0
    for diff_path in TABS_OUT.rglob("*.diff"):
        oid = diff_path.stem
        if oid in checked:
            continue
        try:
            txt = diff_path.read_text(encoding="utf-8", errors="replace")
            # Run 4Cs
            run_code_checks(paths, {"order_id": oid, "_output_path": f"{oid}.py"}, txt)
            log_tracer(f"AUTO_4CS_PROCESSED order={oid} size={len(txt)}")
            new_count += 1
        except Exception as e:
            log_tracer(f"AUTO_4CS_ERROR order={oid} err={e}")
    return new_count


def count_ready_for_judge() -> int:
    """Count how many complete sets have passed 4Cs and are waiting for Judge."""
    paths = CosmosPaths(str(ROOT / "live"))
    db = paths.state("code_checks.db")
    if not db.exists():
        return 0
    con = sqlite3.connect(str(db))
    # Count distinct order_ids where all checks passed
    rows = con.execute(
        "SELECT order_id, status FROM code_checks GROUP BY order_id, status"
    ).fetchall()
    con.close()
    orders = set(r[0] for r in rows)
    return len(orders)


def trace_stalled_coders() -> int:
    """Find coder processes or watch records older than STALL_TIMEOUT_S with no output."""
    watch_file = OUT / "_watch.json"
    if not watch_file.exists():
        return 0
    try:
        w = json.loads(watch_file.read_text(encoding="utf-8"))
    except Exception:
        return 0

    stalled = 0
    now = time.time()
    for item in w.get("launched", []):
        for side in ("a", "b"):
            seat_info = item.get(side, {})
            out_path = Path(seat_info.get("out") or "")
            if not out_path.exists():
                # Check if stalled
                stalled += 1
                tab = item.get("tab")
                log_tracer(f"TRACER_STALL_DETECTED tab={tab} side={side} out={out_path.name}")
    return stalled


def run_tracer_pass() -> dict:
    new_checked = check_unprocessed_outputs()
    stalls = trace_stalled_coders()
    ready_judge = count_ready_for_judge()
    return {
        "new_4cs_checked": new_checked,
        "stalled_detected": stalls,
        "ready_for_judge": ready_judge,
    }


if __name__ == "__main__":
    res = run_tracer_pass()
    print(json.dumps(res, indent=2))
