#!/usr/bin/env python3
"""Validate IMAGE+SEO assets for furniture-advanced-joinery."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = Path(__file__).with_name("faj_graphics_specs.json")
DRAFTS = ROOT / "drafts"


def main() -> int:
    specs = json.loads(SPECS.read_text(encoding="utf-8"))
    errors: list[str] = []
    for item in specs["diagrams"]:
        slug = item["slug"]
        svg = ROOT / "assets" / slug / "joinery-diagram.svg"
        if not svg.is_file():
            errors.append(f"missing SVG: {svg.relative_to(ROOT)}")
    for draft in sorted(DRAFTS.glob("*.md")):
        text = draft.read_text(encoding="utf-8")
        if "graphics:" not in text:
            errors.append(f"no graphics front matter: {draft.name}")
        n_fig = text.count('class="faj-figure')
        if n_fig < 4:
            errors.append(f"expected 4 figures per draft, got {n_fig}: {draft.name}")
        if "<!-- PHOTO:" in text:
            errors.append(f"unconverted PHOTO comment: {draft.name}")
        if not re.search(r'joinery-diagram\.svg', text):
            errors.append(f"no schematic img: {draft.name}")
    museum = ROOT / "assets" / "museum" / "museum_manifest.json"
    if not museum.is_file():
        errors.append("missing museum_manifest.json")
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1
    print(f"OK: {len(specs['diagrams'])} SVGs, {len(list(DRAFTS.glob('*.md')))} drafts with figures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
