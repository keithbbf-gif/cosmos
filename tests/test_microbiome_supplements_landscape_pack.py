"""Pack QA for content/microbiome-supplements-landscape/."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "content/microbiome-supplements-landscape/qa/check_pack.py"


def test_microbiome_supplements_landscape_pack_qa() -> None:
    proc = subprocess.run(
        [sys.executable, str(CHECK)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
