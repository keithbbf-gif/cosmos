"""Pack checks for content/multimodal-ai-public-history (drafts + graphics)."""

from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content" / "multimodal-ai-public-history"
CHECK_GRAPHICS = PACK / "check_graphics.py"


def test_pack_root_exists() -> None:
    assert PACK.is_dir()
    assert (PACK / "RIGHTS.md").is_file()
    assert (PACK / "graphics").is_dir()


def test_check_graphics_passes() -> None:
    ns = runpy.run_path(str(CHECK_GRAPHICS), run_name="not-main")
    assert ns["main"]() == 0
