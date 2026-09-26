#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gitur 1-minute check for CCr cycle.
"""
import json
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
PAUSE = ROOT / "live" / "state" / "control" / "PAUSE.flag"


def main():
    try:
        raw = json.loads(PAUSE.read_text(encoding="utf-8"))
        if raw.get("state") == "PAUSED":
            print("GITUR: none pending (paused)", flush=True)
            return
    except Exception:
        pass
    print("GITUR: none pending", flush=True)


if __name__ == "__main__":
    main()
