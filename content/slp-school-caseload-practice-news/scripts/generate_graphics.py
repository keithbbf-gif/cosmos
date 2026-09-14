#!/usr/bin/env python3
"""Generate school caseload news SVG figures, embeds, RIGHTS, and article blocks."""

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
        rights_heading="Rights — SLPWOW school caseload news pack",
        footnote=(
            "SLPWOW school caseload series — original editorial SVG. "
            "No photos or AI faces."
        ),
        embed_credit=(
            "SLPWOW school caseload series — original SVG. "
            "Not legal, billing, union, or clinical advice."
        ),
        desk_beats={},
        default_beat="School SLP / caseload",
    )


if __name__ == "__main__":
    raise SystemExit(main())
