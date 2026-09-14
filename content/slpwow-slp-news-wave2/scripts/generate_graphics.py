#!/usr/bin/env python3
"""Generate wave-2 SVG figures, embeds, RIGHTS, and article figure blocks."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "tools"))

from slpwow_figure_engine import run_pack  # noqa: E402

PACK = Path(__file__).resolve().parents[1]


def main() -> int:
    return run_pack(
        PACK,
        rights_heading="Rights — SLPWOW SLP News wave 2",
        footnote="SLPWOW SLP News wave 2 — original editorial SVG. No photographs or AI faces.",
        embed_credit=(
            "SLPWOW SLP News wave 2 — original SVG. "
            "Not legal, billing, or clinical advice."
        ),
        desk_beats={
            "literacy": "Practice trends",
            "asha": "Medicare / CMS / ASHA",
            "cms": "Medicare / CMS / ASHA",
            "compact": "ASLP-IC",
            "research": "Research",
        },
        default_beat="Practice trends",
    )


if __name__ == "__main__":
    raise SystemExit(main())
