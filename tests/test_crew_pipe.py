#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crew pipe: saved reply → checks → judge inbox → Gitur → CCr inbox."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = subprocess.run(
    [sys.executable, str(ROOT / "cosmos" / "cosmos_crew_pipe.py"), "--selftest"],
    cwd=str(ROOT),
)
raise SystemExit(PROC.returncode)
