#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repo-root runner for builds/cdeck/test_kdash_working.py."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "builds" / "cdeck" / "test_kdash_working.py"
    sys.exit(runpy.run_path(str(target), run_name="__main__") or 0)
