#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repo-root runner for cDeck occupancy pins (Sessions tab).

Run: py -3.14 test_kdash_working.py
     python3 test_kdash_working.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "builds" / "cdeck" / "test_kdash_working.py"

if __name__ == "__main__":
    if not TARGET.is_file():
        print(f"FAIL  missing {TARGET}")
        raise SystemExit(1)
    sys.path.insert(0, str(ROOT / "cosmos"))
    ns = runpy.run_path(str(TARGET), run_name="kdash_working_pin")
    main_fn = ns.get("main")
    raise SystemExit(main_fn() if callable(main_fn) else 1)
