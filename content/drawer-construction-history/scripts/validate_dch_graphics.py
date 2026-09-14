#!/usr/bin/env python3
"""Validate IMAGE+SEO assets for drawer-construction-history."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = Path(__file__).with_name("dch_graphics_specs.json")
DRAFTS = ROOT / "drafts"
PLACEHOLDER = ROOT / "assets" / "placeholders" / "bbf-shop-pending.svg"


def main() -> int:
    specs = json.loads(SPECS.read_text(encoding="utf-8"))
    errors: list[str] = []
    if not PLACEHOLDER.is_file():
        errors.append(f"missing placeholder: {PLACEHOLDER.relative_to(ROOT)}")
    for item in specs["diagrams"]:
        slug = item["slug"]
        svg = ROOT / "assets" / slug / "joinery-diagram.svg"
        if not svg.is_file():
            errors.append(f"missing SVG: {svg.relative_to(ROOT)}")
    for draft in sorted(DRAFTS.glob("*.md")):
        text = draft.read_text(encoding="utf-8")
        if "graphics:" not in text:
            errors.append(f"no graphics front matter: {draft.name}")
        n_fig = text.count('class="dch-figure')
        if n_fig < 3:
            errors.append(f"expected 3 figures per draft, got {n_fig}: {draft.name}")
        if "<!-- PHOTO:" in text:
            errors.append(f"unconverted PHOTO comment: {draft.name}")
        if not re.search(r"joinery-diagram\.svg", text):
            errors.append(f"no schematic img: {draft.name}")
        if re.search(r"status:\s*needed", text) is None:
            errors.append(f"expected BBF photo slots status needed: {draft.name}")
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1
    print(
        f"OK: {len(specs['diagrams'])} SVGs, "
        f"{len(list(DRAFTS.glob('*.md')))} drafts with figures"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
