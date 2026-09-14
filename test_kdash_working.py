#!/usr/bin/env python3
"""Repo-root entry for builds/cdeck/test_kdash_working.py."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "builds" / "cdeck" / "test_kdash_working.py"
if not TARGET.is_file():
    print("missing %s" % TARGET, file=sys.stderr)
    raise SystemExit(2)
runpy.run_path(str(TARGET), run_name="__main__")
