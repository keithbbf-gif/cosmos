#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crew chart status for CCr loop roster.
"""
import json
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
PAUSE = ROOT / "live" / "state" / "control" / "PAUSE.flag"
WATCH = ROOT / "work_orders" / "ccr" / "CREW" / "OUT" / "_watch.json"


def main():
    state = "ACTIVE"
    if PAUSE.is_file():
        try:
            raw = json.loads(PAUSE.read_text(encoding="utf-8"))
            if raw.get("state") == "PAUSED":
                state = f"PAUSED ({raw.get('mode', 'hold')})"
        except Exception:
            state = "PAUSED"
    n_tabs = 0
    if WATCH.is_file():
        try:
            w = json.loads(WATCH.read_text(encoding="utf-8"))
            n_tabs = w.get("n_tabs", 0)
        except Exception:
            pass
    print(f"CHART: state={state} tabs={n_tabs} seats=0 (idle under pause)", flush=True)


if __name__ == "__main__":
    main()
