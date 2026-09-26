#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spend summary for CCr loop roster.
"""
import json
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
METER = ROOT / "live" / "state" / "spend" / "meter.json"
ROSTER = ROOT / "live" / "state" / "crew" / "roster.jsonl"


def main():
    if METER.is_file():
        try:
            d = json.loads(METER.read_text(encoding="utf-8"))
            totals = d.get("totals", {})
            tot = totals.get("total_usd", totals.get("total", 0.0))
            run = totals.get("running_usd", totals.get("running", 0.0))
            print(f"SPEND: total=${float(tot):.4f} running=${float(run):.4f}", flush=True)
            return
        except Exception:
            pass
    if ROSTER.is_file():
        try:
            lines = [line.strip() for line in ROSTER.read_text(encoding="utf-8").splitlines() if line.strip()]
            if lines:
                last = json.loads(lines[-1])
                txt = last.get("text")
                if txt:
                    print(txt, flush=True)
                    return
                print(f"SPEND running: ${float(last.get('running_total', 0.0)):.4f}", flush=True)
                return
        except Exception:
            pass
    print("SPEND: unmeasured", flush=True)


if __name__ == "__main__":
    main()
