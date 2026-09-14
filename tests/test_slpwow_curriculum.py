#!/usr/bin/env python3
"""Pack integrity for content/slpwow-free-resources-curriculum/.

Positive: the checker PASSes on the tree.
Negative: SKU shape rejects junk; a diagnosis-product heading is refused.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "content" / "slpwow-free-resources-curriculum"
CHECKER = PACK / "check_curriculum.py"

sys.path.insert(0, str(PACK))
from check_curriculum import BANNED_HEADING, SKU_RE  # noqa: E402


def test_checker_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(CHECKER)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PASS  slpwow-free-resources-curriculum" in proc.stdout
    assert "skus=24" in proc.stdout


def test_sku_shape_negative() -> None:
    assert SKU_RE.match("SLPWOW-FR-WS-ART-EE-01")
    assert not SKU_RE.match("SLPWOW-FR-WS-ART-EE-1")
    assert not SKU_RE.match("SLPWOW-FR-TEST-DX-EE-01")
    assert not SKU_RE.match("someone-elses-artic-deck")


def test_heading_voice_negative() -> None:
    assert BANNED_HEADING.search("## /r/ screener")
    assert BANNED_HEADING.search("# Diagnose at home")
    assert not BANNED_HEADING.search("## Picture words — you name the sound")


if __name__ == "__main__":
    test_checker_passes()
    test_sku_shape_negative()
    test_heading_voice_negative()
    print("PASS test_slpwow_curriculum")
