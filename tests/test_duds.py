#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DUDs gate, CPU first pass, WOMBAT xFORM, Judge at 40."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = subprocess.run(
    [sys.executable, str(ROOT / "cosmos" / "cosmos_duds.py"), "--selftest"],
    cwd=str(ROOT),
)
raise SystemExit(PROC.returncode)
