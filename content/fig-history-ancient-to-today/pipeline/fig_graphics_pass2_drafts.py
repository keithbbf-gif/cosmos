#!/usr/bin/env python3
"""Add pass-2 supplemental embeds to fig-history staging drafts."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "articles" / "_staging"
DRAFTS = ROOT / "drafts" / "staging"

BLOCK = """
<!-- figure-id: {slug}.preservation-stack-pass2 -->
![Stacked schematic of dried fig preservation stages for export.](../../assets/shared/svg/infographic-dried-fig-preservation-stack.svg)

*Figure (pass 2). Dried-fig preservation stack — editorial schematic (CC0). No AI imagery.*

*Rights: original SVG only; rasters elsewhere must match IMAGE_SOURCES.md (PD/CC).*
"""

SLUGS = [
    "silk-road-dried-fig-economy",
    "estahban-iran-dried-figs",
    "california-mission-fig-spread",
    "roman-fig-orchards-and-trade",
    "turkey-aydin-dried-fig-industry",
]


def main() -> None:
    DRAFTS.mkdir(parents=True, exist_ok=True)
    for slug in SLUGS:
        src = STAGING / slug / "index.md"
        if not src.exists():
            print(f"skip missing {slug}")
            continue
        body = src.read_text(encoding="utf-8")
        header = f"<!-- graphics-pass: 2 | source: articles/_staging/{slug}/index.md -->\n"
        if "preservation-stack-pass2" not in body:
            body = body.rstrip() + "\n" + BLOCK.format(slug=slug)
        (DRAFTS / f"{slug}.md").write_text(header + body, encoding="utf-8")
    print(f"Wrote drafts under {DRAFTS}")


if __name__ == "__main__":
    main()
