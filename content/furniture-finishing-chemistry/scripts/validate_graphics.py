#!/usr/bin/env python3
"""Validate graphics pass completeness."""

from __future__ import annotations

from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SPECS = json.loads((Path(__file__).resolve().parent / "ffc_graphics_specs.json").read_text(encoding="utf-8"))


def main() -> int:
    errors = []
    for slug in SPECS:
        svg = ROOT / "assets" / slug / "shop-diagram.svg"
        if not svg.is_file():
            errors.append(f"missing SVG: {slug}")
        else:
            try:
                ET.parse(svg)
            except ET.ParseError as exc:
                errors.append(f"bad SVG {slug}: {exc}")
    for path in sorted(ROOT.glob("[0-9][0-9]-*.md")):
        text = path.read_text(encoding="utf-8")
        if text.count("<figure") < 1:
            errors.append(f"no figure: {path.name}")
        if "meta_description:" not in text:
            errors.append(f"no meta_description: {path.name}")
        if "graphic:" not in text:
            errors.append(f"no graphic frontmatter: {path.name}")
        if 'alt="' not in text:
            errors.append(f"no img alt: {path.name}")
    for req in ("RIGHTS.md", "STYLE_GUIDE.md", "GRAPHICS_INDEX.md"):
        if not (ROOT / req).is_file():
            errors.append(f"missing {req}")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"OK: {len(SPECS)} SVGs, {len(list(ROOT.glob('[0-9][0-9]-*.md')))} drafts, RIGHTS/STYLE/INDEX present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
