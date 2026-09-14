#!/usr/bin/env python3
"""Structural QA for counseling-ethics-history image + SEO pass."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from image_seo_specs import TIMELINE_SPECS

ROOT = Path(__file__).resolve().parent
FIGURE_RE = re.compile(r"<!-- figure-id:.*?lead-timeline -->")
PORTRAIT_RE = re.compile(r"<!-- figure-id:.*?lead-portrait -->")
FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def main() -> int:
    errors: list[str] = []
    drafts = sorted(ROOT.glob("stage-*/*.md"))
    if len(drafts) < 48:
        errors.append(f"expected 48 drafts, found {len(drafts)}")

    for path in drafts:
        text = path.read_text(encoding="utf-8")
        m = FRONT_RE.match(text)
        if not m:
            errors.append(f"{path.name}: missing frontmatter")
            continue
        slug = None
        for line in m.group(1).splitlines():
            if line.startswith("slug:"):
                slug = line.split(":", 1)[1].strip()
        if not slug:
            errors.append(f"{path.name}: no slug")
            continue
        if slug not in TIMELINE_SPECS:
            errors.append(f"{path.name}: slug {slug} not in TIMELINE_SPECS")
        svg = ROOT / "assets" / "era" / slug / "lead-timeline.svg"
        if not svg.is_file():
            errors.append(f"missing timeline SVG for {slug}")
        if not FIGURE_RE.search(text):
            errors.append(f"{path.name}: no lead-timeline figure embed")
        if "lead_asset:" not in m.group(1):
            errors.append(f"{path.name}: missing lead_asset frontmatter")

    if not (ROOT / "RIGHTS.md").is_file():
        errors.append("missing pack RIGHTS.md")
    if not (ROOT / "GRAPHICS_INDEX.md").is_file():
        errors.append("missing GRAPHICS_INDEX.md")

    cleared = ROOT / "plates" / "1947-tolman-committee" / "RIGHTS.md"
    if not cleared.is_file():
        errors.append("missing Commons plate RIGHTS for tolman")

    for msg in errors:
        print(f"ERROR: {msg}")
    if errors:
        return 1
    print(f"OK: {len(drafts)} drafts, {len(TIMELINE_SPECS)} timelines, RIGHTS + embeds present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
