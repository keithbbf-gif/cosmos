#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P13 Voice Drop: malformed refuses typed; valid drop lands from work_orders/drop."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BITE = ROOT / "cosmos" / "_bite_p13_voice_drop.py"
BITE_JSON = ROOT / "cosmos" / "_bite_p13_voice_drop.json"
FAIL_OLD = ROOT / "cosmos" / "_fail_p13_voice_drop_against_old.py"


def test_p13_voice_drop_bite_all_bite():
    proc = subprocess.run(
        [sys.executable, str(BITE)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    rec = json.loads(BITE_JSON.read_text(encoding="utf-8"))
    assert rec.get("all_bite") is True
    assert rec.get("malformed_refused_typed") is True
    assert rec.get("valid_lands_bucket_from_drop_path") is True
    assert rec.get("github_drop_path") == "work_orders/drop"


def test_p13_fail_old_pin():
    proc = subprocess.run(
        [sys.executable, str(FAIL_OLD)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
