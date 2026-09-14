#!/usr/bin/env python3
"""Prepend four schematic SVG figures to each chapter's Figure plan section."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "CHAPTER_GRAPHICS_MAP.json"
FIGURE_HEADING = "## Figure plan"

CAPTIONS = {
    1: (
        "Chronological anchors for the evidence discussed below.",
        "Chronological anchors for the evidence discussed below. Schematic redrawn line diagram; staged editorial asset (2026). Not a photograph of a museum object.",
    ),
    2: (
        "Regional focus for circulation and local workshop traditions.",
        "Regional focus for circulation and local workshop traditions. Schematic redrawn line diagram; staged editorial asset (2026). Not a photograph of a museum object.",
    ),
    3: (
        "Morphological typology (idealized morphotypes).",
        "Morphological typology for archaeology (idealized morphotypes). Schematic redrawn line diagram; staged editorial asset (2026). Not a photograph of a museum object.",
    ),
    4: (
        "Comparative elevation and plan plate.",
        "Comparative elevation and plan plate for archaeology. Schematic redrawn line diagram; staged editorial asset (2026). Not a photograph of a museum object.",
    ),
}

KINDS = ["timeline", "map", "typology", "plate"]


def schematic_block(slug: str) -> str:
    lines: list[str] = []
    for n, kind in enumerate(KINDS, start=1):
        alt, cap = CAPTIONS[n]
        rel = f"assets/{slug}/fig-0{n}-{kind}.svg"
        lines.append(f"![{alt}]({rel})")
        lines.append("")
        lines.append(f"*Fig. {n}.* {cap}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def merge_file(path: Path, slug: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if FIGURE_HEADING not in text:
        print(f"skip (no figure plan): {path.name}")
        return False
    if f"assets/{slug}/fig-01-timeline.svg" in text:
        return False

    before, after = text.split(FIGURE_HEADING, 1)
    body_rest = after.lstrip("\n")
    # Renumber legacy photo figure entries Fig. N -> Fig. N+4 when they use **Fig. digit.**
    body_rest = re.sub(
        r"\*\*Fig\. (\d+)\.\*\*",
        lambda m: f"**Fig. {int(m.group(1)) + 4}.**",
        body_rest,
    )

    new_block = schematic_block(slug)
    merged = before + FIGURE_HEADING + "\n\n" + new_block + "\n### Supplemental photographs and redraws\n\n" + body_rest
    path.write_text(merged, encoding="utf-8")
    return True


def main() -> None:
    mapping: dict[str, str] = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    mapping.pop("comment", None)
    changed = 0
    for stem, asset_slug in sorted(mapping.items()):
        essay = ROOT / f"{stem}.md"
        if not essay.exists():
            print(f"missing essay: {essay}")
            continue
        if merge_file(essay, asset_slug):
            changed += 1
    print(f"updated {changed} essays")


if __name__ == "__main__":
    main()
