"""Pack checks for content/multimodal-ai-public-history (staged public drafts)."""

from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content" / "multimodal-ai-public-history"
CHECK = PACK / "check_pack.py"


def test_pack_root_exists() -> None:
    assert PACK.is_dir()
    assert CHECK.is_file()


def test_check_pack_passes() -> None:
    ns = runpy.run_path(str(CHECK), run_name="not-main")
    assert ns["main"]() == 0
