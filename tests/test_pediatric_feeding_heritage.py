"""QA gate for the staged SLPWOW pediatric feeding heritage pack."""
from __future__ import annotations

import runpy
from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "content" / "pediatric-feeding-heritage"


def test_check_pack_passes():
    ns = runpy.run_path(str(PACK / "check_pack.py"))
    assert ns["main"]() == 0
