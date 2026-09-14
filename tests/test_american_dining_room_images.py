#!/usr/bin/env python3
"""Validate american-dining-room-history staged images and embeds."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "content" / "american-dining-room-history"
IMAGES = ROOT / "staged" / "images"
DRAFTS = ROOT / "drafts"

# Slugs from PHOTO_CAPTIONS.md that must have figures in Pass 1
REQUIRED_SLUGS = [
    "the-room-is-invented",
    "hall-table-before-the-room",
    "gateleg-and-drop-leaf",
    "hepplewhite-sideboard-arrives",
    "phyfe-new-york-dining",
    "thomas-day-southern-shops",
    "hunt-board-southern-vernacular",
    "hitchcock-fancy-chairs",
    "stickley-mission-dining",
    "extension-table-patents",
    "midcentury-eames-saarinen",
    "studio-furniture-nakashima",
    "arkansas-southern-hardwood-dining",
    "reading-a-table-now",
]

FIGURE_RE = re.compile(
    r'<figure class="adrh-figure">\s*'
    r'<img src="content/american-dining-room-history/staged/images/([^"]+)"\s*'
    r'alt="([^"]+)"\s*'
    r'width="\d+" height="\d+" loading="lazy" decoding="async"/>\s*'
    r'<figcaption>.+</figcaption>\s*'
    r"</figure>",
    re.DOTALL,
)


def main() -> int:
    errors: list[str] = []
    if not (ROOT / "RIGHTS.md").is_file():
        errors.append("missing RIGHTS.md")

    for slug in REQUIRED_SLUGS:
        md = DRAFTS / f"{slug}.md"
        if not md.is_file():
            errors.append(f"missing draft {slug}.md")
            continue
        text = md.read_text(encoding="utf-8")
        m = FIGURE_RE.search(text)
        if not m:
            errors.append(f"{slug}: no valid adrh-figure embed")
            continue
        fname, alt = m.group(1), m.group(2)
        if len(alt) < 40:
            errors.append(f"{slug}: alt text too short for SEO")
        img_path = IMAGES / fname
        if not img_path.is_file():
            errors.append(f"{slug}: missing image file {fname}")
        elif img_path.stat().st_size < 10_000:
            errors.append(f"{slug}: suspiciously small image {fname}")

    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print(f"OK: {len(REQUIRED_SLUGS)} drafts with museum/CC figures; RIGHTS.md present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
