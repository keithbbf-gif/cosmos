#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Report sink status for CCr loop roster.
"""
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
OUT = ROOT / "work_orders" / "ccr" / "CREW" / "OUT"


def main():
    if not OUT.is_dir():
        print("SINK: OUT directory missing", flush=True)
        return
    n_logs = len(list(OUT.glob("*.log")))
    n_txt = len(list(OUT.glob("*.txt")))
    tabs_dir = OUT / "TEAM_TABS"
    n_pairs = len(list(tabs_dir.rglob("*.json"))) if tabs_dir.is_dir() else 0
    print(f"SINK: {n_logs} logs, {n_txt} txt, {n_pairs} team tab pairs", flush=True)


if __name__ == "__main__":
    main()
