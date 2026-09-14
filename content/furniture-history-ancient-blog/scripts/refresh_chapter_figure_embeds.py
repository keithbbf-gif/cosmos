#!/usr/bin/env python3
"""Replace Figs. 1–4 schematic embeds with chapter-specific paths and captions."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "CHAPTER_GRAPHICS_MAP.json"
META_PATH = ROOT / "chapter_graphics_meta.json"
FIGURE_HEADING = "## Figure plan"
SUPPLEMENTAL = "### Supplemental photographs and redraws"

KINDS = ["timeline", "map", "typology", "plate"]


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end]
    out: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        out[key.strip()] = val.strip()
    return out


def captions_for(stem: str, fm: dict[str, str], meta: dict) -> list[str]:
    title = fm.get("title", stem)
    period = fm.get("period", "")
    regions = fm.get("regions", "")
    focus = meta.get("focus", "forms discussed in this chapter")
    return [
        f"Chronological anchors for **{title}** ({period}).",
        f"Regional focus (schematic): {regions}.",
        f"Morphological typology for {focus} (idealized morphotypes).",
        f"Comparative elevation and plan plate for {focus}.",
    ]


def schematic_block(stem: str, caps: list[str]) -> str:
    lines: list[str] = []
    for n, kind in enumerate(KINDS, start=1):
        alt = caps[n - 1].replace("**", "")
        rel = f"assets/{stem}/fig-0{n}-{kind}.svg"
        lines.append(f"![{alt}]({rel})")
        lines.append("")
        lines.append(
            f"*Fig. {n}.* {caps[n - 1]} Schematic redrawn line diagram; staged editorial asset (2026). Not a photograph of a museum object."
        )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def refresh_file(path: Path, stem: str, caps: list[str]) -> bool:
    text = path.read_text(encoding="utf-8")
    if FIGURE_HEADING not in text:
        print(f"skip (no figure plan): {path.name}")
        return False

    before, after = text.split(FIGURE_HEADING, 1)
    if SUPPLEMENTAL in after:
        _, supplemental = after.split(SUPPLEMENTAL, 1)
        body_rest = supplemental.lstrip("\n")
    else:
        body_rest = after.lstrip("\n")
        supplemental = ""

    new_block = schematic_block(stem, caps)
    merged = (
        before
        + FIGURE_HEADING
        + "\n\n"
        + new_block
        + "\n"
        + SUPPLEMENTAL
        + "\n\n"
        + body_rest
    )
    if merged == text:
        return False
    path.write_text(merged, encoding="utf-8")
    return True


def main() -> None:
    mapping: dict[str, str] = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    mapping.pop("comment", None)
    meta_all = json.loads(META_PATH.read_text(encoding="utf-8"))
    meta_all.pop("comment", None)
    changed = 0
    for stem in sorted(mapping.keys()):
        essay = ROOT / f"{stem}.md"
        if not essay.exists():
            continue
        fm = parse_frontmatter(essay)
        caps = captions_for(stem, fm, meta_all.get(stem, {}))
        if refresh_file(essay, stem, caps):
            changed += 1
    print(f"updated {changed} essays")


if __name__ == "__main__":
    main()
