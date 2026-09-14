"""QA hook for the staged SLPWOW SLP News wave-2 pack."""
from __future__ import annotations

import runpy
from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "content" / "slpwow-slp-news-wave2"


def test_check_pack_passes() -> None:
    script = PACK / "check_pack.py"
    assert script.is_file()
    ns = runpy.run_path(str(script))
    assert ns["main"]() == 0
