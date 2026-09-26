#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Station queue and OpenRouter routing variants."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ok = 0
for name in ("cosmos_route_variant.py", "cosmos_stations.py"):
    proc = subprocess.run(
        [sys.executable, str(ROOT / "cosmos" / name), "--selftest"],
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        ok = proc.returncode
raise SystemExit(ok)
