#!/usr/bin/env python3
"""Wave-2: chapter-specific schematic SVGs for the magazine essay series."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_graphics_pack import (  # noqa: E402
    ACCENT,
    BG,
    FONT,
    GRID,
    INK,
    MUTED,
    RULE,
    esc,
    map_svg,
    plate_svg,
    svg_footer,
    svg_header,
    timeline_svg,
)

META_PATH = ROOT / "chapter_graphics_meta.json"
MAP_PATH = ROOT / "CHAPTER_GRAPHICS_MAP.json"
ASSETS = ROOT / "assets"


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


def typology_chapter(
    slug: str, title: str, focus: str, labels: tuple[str, str, str]
) -> str:
    w, h = 720, 480
    body = svg_header(w, h, f"Typology: {focus}")
    body += f"""
  <text x="36" y="72" font-family="{FONT}" font-size="18" fill="{INK}">Typology diagram</text>
  <text x="36" y="96" font-family="{FONT}" font-size="12" fill="{MUTED}">{esc(focus)} · morphological axes (schematic)</text>
"""
    subs = ("Ceremonial / high status", "Domestic / portable", "Workshop / storage")
    boxes = [
        (80, 160, labels[0], subs[0]),
        (280, 160, labels[1], subs[1]),
        (480, 160, labels[2], subs[2]),
    ]
    for x, y, label, sub in boxes:
        body += f"""
  <rect x="{x}" y="{y}" width="160" height="120" fill="none" stroke="{INK}" stroke-width="1.5"/>
  <line x1="{x + 20}" y1="{y + 70}" x2="{x + 140}" y2="{y + 70}" stroke="{RULE}" stroke-width="1"/>
  <line x1="{x + 80}" y1="{y + 30}" x2="{x + 80}" y2="{y + 110}" stroke="{RULE}" stroke-width="1"/>
  <text x="{x + 80}" y="{y + 24}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{ACCENT}">{esc(label[:28])}</text>
  <text x="{x + 80}" y="{y + 104}" text-anchor="middle" font-family="{FONT}" font-size="9" fill="{MUTED}">{esc(sub)}</text>
"""
    body += f"""
  <text x="36" y="330" font-family="{FONT}" font-size="11" fill="{INK}">Reading the diagram — {esc(title[:52])}</text>
  <text x="36" y="350" font-family="{FONT}" font-size="10" fill="{MUTED}">Solid frames mark idealized morphotypes used in this chapter.</text>
  <text x="36" y="368" font-family="{FONT}" font-size="10" fill="{MUTED}">Dashed elements indicate reconstructed or debated forms.</text>
  <text x="36" y="386" font-family="{FONT}" font-size="10" fill="{MUTED}">Assign museum finds using accession captions, not silhouette alone.</text>
"""
    body += svg_footer()
    return body


def map_chapter(title: str, region: str, period: str) -> str:
    """Regional map with period line for magazine chapters."""
    w, h = 720, 460
    body = svg_header(w, h, f"Regional map: {title}")
    region_short = region.split(",")[0].strip()[:28]
    body += f"""
  <text x="36" y="72" font-family="{FONT}" font-size="18" fill="{INK}">Regional focus (schematic)</text>
  <text x="36" y="96" font-family="{FONT}" font-size="12" fill="{MUTED}">{esc(region)} · {esc(period)}</text>
  <rect x="120" y="130" width="480" height="260" fill="#ebe8e0" stroke="{GRID}" stroke-width="1"/>
  <path d="M180 320 Q260 180 360 210 T520 280 T420 360 T240 340 Z" fill="none" stroke="{RULE}" stroke-width="1.5" stroke-dasharray="6 4"/>
  <circle cx="360" cy="260" r="28" fill="{ACCENT}" fill-opacity="0.15" stroke="{ACCENT}" stroke-width="2"/>
  <line x1="360" y1="232" x2="360" y2="200" stroke="{ACCENT}" stroke-width="1.5"/>
  <text x="360" y="192" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{ACCENT}">{esc(region_short)}</text>
  <text x="132" y="410" font-family="{FONT}" font-size="10" fill="{MUTED}">Coastlines and borders are illustrative, not GIS-accurate.</text>
  <text x="132" y="426" font-family="{FONT}" font-size="10" fill="{MUTED}">Workshop and trade routes discussed in chapter prose.</text>
"""
    body += svg_footer().replace("480", str(h))
    return body


def write_chapter_assets(stem: str, topic: dict, meta: dict) -> None:
    slug = stem
    assets_dir = ASSETS / slug
    assets_dir.mkdir(parents=True, exist_ok=True)
    labels = (
        meta.get("typology_a", "Type A"),
        meta.get("typology_b", "Type B"),
        meta.get("typology_c", "Type C"),
    )
    focus = meta.get("focus", topic["focus"])

    (assets_dir / "fig-01-timeline.svg").write_text(
        timeline_svg(slug, topic["title"], topic["era"], topic["region"]),
        encoding="utf-8",
    )
    (assets_dir / "fig-02-map.svg").write_text(
        map_chapter(topic["title"], topic["region"], topic["era"]),
        encoding="utf-8",
    )
    (assets_dir / "fig-03-typology.svg").write_text(
        typology_chapter(slug, topic["title"], focus, labels),
        encoding="utf-8",
    )
    (assets_dir / "fig-04-plate.svg").write_text(
        plate_svg(slug, topic["title"], focus),
        encoding="utf-8",
    )


def chapter_topic(stem: str, fm: dict[str, str], meta: dict) -> dict:
    return {
        "slug": stem,
        "title": fm.get("title", stem),
        "region": fm.get("regions", "Cross-regional"),
        "era": fm.get("period", "see essay"),
        "focus": meta.get("focus", "furniture forms"),
    }


def append_graphics_index(chapters: list[dict]) -> None:
    path = ROOT / "GRAPHICS_INDEX.md"
    text = path.read_text(encoding="utf-8")
    marker = "## Magazine chapter figures (wave 2)"
    if marker in text:
        text = text.split(marker)[0].rstrip() + "\n"
    lines = [
        "",
        marker,
        "",
        "One schematic set per magazine chapter (`assets/<chapter-stem>/`). "
        "Regenerate with `scripts/build_chapter_graphics_wave2.py`.",
        "",
        "| Chapter slug | Fig | File | Description |",
        "|---|---:|---|---|",
    ]
    for t in chapters:
        slug = t["slug"]
        for i, (kind, desc) in enumerate(
            [
                ("timeline", "Chronological anchors"),
                ("map", "Regional schematic map"),
                ("typology", "Typology morphotypes"),
                ("plate", "Comparative plate"),
            ],
            start=1,
        ):
            lines.append(
                f"| `{slug}` | {i} | `assets/{slug}/fig-{i:02d}-{kind}.svg` | {desc} |"
            )
    path.write_text(text + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    meta_all = json.loads(META_PATH.read_text(encoding="utf-8"))
    meta_all.pop("comment", None)

    old_map: dict[str, str] = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    old_map.pop("comment", None)

    stems = sorted(old_map.keys())
    chapters: list[dict] = []
    for stem in stems:
        essay = ROOT / f"{stem}.md"
        if not essay.exists():
            print(f"skip missing essay: {stem}")
            continue
        fm = parse_frontmatter(essay)
        meta = meta_all.get(stem, {})
        topic = chapter_topic(stem, fm, meta)
        write_chapter_assets(stem, topic, meta)
        chapters.append(topic)
        print(f"wrote assets/{stem}/")

    new_map = {
        "comment": "Maps each magazine chapter file (stem) to assets/<stem>/ fig-01..04 SVG set (wave-2 chapter-specific).",
    }
    for stem in stems:
        new_map[stem] = stem
    MAP_PATH.write_text(json.dumps(new_map, indent=2) + "\n", encoding="utf-8")
    append_graphics_index(chapters)
    print(f"Done: {len(chapters)} chapter asset sets; CHAPTER_GRAPHICS_MAP.json updated.")


if __name__ == "__main__":
    main()
