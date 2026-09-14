#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repo-root runner for builds/cdeck/test_kdash_working.py."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "builds" / "cdeck" / "test_kdash_working.py"
if __name__ == "__main__":
    g = runpy.run_path(str(TARGET), run_name="not_main")
    sys.exit(int(g.get("main", lambda: 1)()))
