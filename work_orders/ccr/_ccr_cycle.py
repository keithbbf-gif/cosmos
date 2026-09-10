#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One CCr factory pass: fetch → crews → Luna tail → Gitur merge → report.

    py -3.14 work_orders\\ccr\\_ccr_cycle.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
sys.path.insert(0, str(ROOT / "cosmos"))
sys.path.insert(0, str(ROOT / "work_orders" / "ccr"))
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_session import require_bootup  # noqa: E402

PY = sys.executable


def _run(args: list[str]) -> str:
    p = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = (p.stdout or "") + (p.stderr or "")
    return out[-1500:]


def _live_seats() -> int:
    p = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Process | Where-Object { "
         "$_.CommandLine -match '_cdeck_code_seat|_code_or_seat' }).Count"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    try:
        return int((p.stdout or "0").strip() or 0)
    except ValueError:
        return 0


def main() -> int:
    require_bootup(CosmosPaths(str(ROOT / "live")), stream="Cm")
    log = []
    n0 = _live_seats()
    refill = n0 < 40
    log.append(f"1 FETCH live_seats={n0}")
    if refill:
        log.append("2 ASSIGN two OR-heavy tab-team sets")
        for _ in range(2):
            _run([PY, str(ROOT / "work_orders" / "ccr" / "_crew_tab_teams.py")])
        n = _live_seats()
        log.append(f"   after={n}")
    else:
        n = n0
        log.append("2 ASSIGN skip (at floor)")
    hhmm = datetime.now(timezone.utc).strftime("%H:%MZ")
    tick = (
        f"TICK {hhmm} n={n} luna=SKIP $ gitur=pending refill="
        f"{'yes' if refill else 'no'}"
    )
    print(tick, flush=True)
    log.append(tick)
    log.append("3 PROMPT ITEMs already TABS/*.md")
    log.append("4 LUNA skip — no freeze until cycles complete")
    log.append("5 CCR review = Luna q-NNN on disk; KEEP diffs only")
    log.append("6 GITUR merge CLEAN + launch apply if needed")
    gitur_out = _run([PY, str(ROOT / "work_orders" / "ccr" / "_gitur_minute.py")])
    log.append(gitur_out[-400:])
    log.append("6b PAIR I/O+judge save")
    log.append(_run([PY, str(ROOT / "work_orders" / "ccr" / "_porosity_pair_save.py")])[-400:])
    log.append("7-9 IMPLEMENT=merge; SYNC=gh; REPEAT=1-min scheduler")
    log.append("SOL queued not fired")
    gitur = "none"
    low = gitur_out.lower()
    if "merged" in low and "none" not in low:
        gitur = "merged"
    print("\n".join(log), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
