#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Native factory loop. 60s cycle. TICK every 5 min. Roster every 30 min. No Grok.

    pythonw work_orders\\ccr\\_ccr_loop.py
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
PY = sys.executable.replace("pythonw.exe", "python.exe")
CCR = ROOT / "work_orders" / "ccr"
OUT = CCR / "CREW" / "OUT"
CYCLE = CCR / "_ccr_cycle.py"
SPEND = CCR / "_crew_spend.py"
SINK = CCR / "_crew_report_sink.py"
CHART = CCR / "_crew_chart.py"
OW = CCR / "_ow_post.py"
LOOP_LOG = OUT / "_ccr_loop.log"
TICK_LOG = OUT / "_tick.log"
ROSTER = OUT / "_roster_30m.txt"


def _run(script: Path, timeout: int = 180, extra: list[str] | None = None) -> str:
    cmd = [PY, str(script)] + (extra or [])
    p = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )
    return (p.stdout or "") + (p.stderr or "")


def _run_text(script: Path, text: str) -> str:
    return _run(script, 30, ["--text", text])


def _tick_line(cycle_out: str) -> str:
    line = ""
    for row in cycle_out.splitlines():
        if row.startswith("TICK "):
            line = row
    return line or "TICK missing"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    while True:
        stamp = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
        try:
            cycle_out = _run(CYCLE)
            tick = _tick_line(cycle_out)
            with LOOP_LOG.open("a", encoding="utf-8") as f:
                f.write("%s %s\n" % (stamp, tick))
            # TICK every 5 minutes (cycle still every 60s)
            if n % 5 == 0:
                with TICK_LOG.open("a", encoding="utf-8") as f:
                    f.write("%s %s\n" % (stamp, tick))
                _run_text(OW, tick)
            if n % 30 == 0:
                spend = _run(SPEND, 120)
                sink = _run(SINK, 120)
                chart = _run(CHART, 120)
                blob = "\n".join(
                    ("=== ROSTER %s ===" % stamp, spend.strip(), sink.strip(),
                     chart.strip()[-2000:], "")
                )
                with ROSTER.open("a", encoding="utf-8") as f:
                    f.write(blob + "\n")
                _run_text(OW, blob[:8000])
        except Exception as e:
            with LOOP_LOG.open("a", encoding="utf-8") as f:
                f.write("%s ERR %s\n" % (stamp, e))
        n += 1
        time.sleep(60)


if __name__ == "__main__":
    raise SystemExit(main())
