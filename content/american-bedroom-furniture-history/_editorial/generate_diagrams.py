#!/usr/bin/env python3
"""Generate original lead-timeline SVG diagrams (furniture silhouettes, no portraits)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"
DIAGRAMS = ROOT / "assets" / "diagrams"

FRONT = re.compile(r"^---\n(.*?)\n---", re.S)

# Chapter band labels for the horizontal axis (American bedroom furniture spine).
BANDS = [
    (1, 6, "Chamber & case", "#8b5a2b"),
    (7, 11, "High chest & bedstead", "#5c4d3c"),
    (12, 17, "Suite & factory", "#4a6741"),
    (18, 21, "Arts & Crafts", "#6b4c35"),
    (22, 30, "Catalog & modern", "#3d5a80"),
    (31, 45, "Flat pack & revival", "#5a3d6e"),
]


def parse_fields(fm: str) -> dict[str, str]:
    return {k: v.strip().strip('"') for k, v in re.findall(r"^([a-z_]+):\s*(.+)$", fm, re.M)}


def svg_for(chapter: int, title: str, period: str) -> str:
    w, h = 960, 220
    active = "#c9a227"
    ink = "#1a1a1a"
    muted = "#5a5a5a"
    bg = "#f7f4ef"
    bar_y = 118
    bar_h = 14
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
        f'aria-labelledby="title desc">',
        f'<title id="title">{title} — period diagram</title>',
        f'<desc id="desc">Original timeline placing chapter {chapter} ({period}) on the '
        f"American bedroom furniture series axis. Furniture silhouettes only; no portraits.</desc>",
        f'<rect width="{w}" height="{h}" fill="{bg}"/>',
        f'<text x="32" y="36" font-family="Georgia, serif" font-size="20" fill="{ink}">'
        f"Ch. {chapter:02d} on the series axis</text>",
        f'<text x="32" y="62" font-family="system-ui, sans-serif" font-size="14" fill="{muted}">'
        f"{period}</text>",
    ]
    seg_w = (w - 64) / len(BANDS)
    for i, (lo, hi, label, color) in enumerate(BANDS):
        x = 32 + i * seg_w
        fill = color if lo <= chapter <= hi else "#d8d2c8"
        stroke = active if lo <= chapter <= hi else "#b8b0a4"
        sw = 3 if lo <= chapter <= hi else 1
        parts.append(
            f'<rect x="{x:.1f}" y="{bar_y}" width="{seg_w - 4:.1f}" height="{bar_h}" '
            f'rx="4" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )
        parts.append(
            f'<text x="{x + (seg_w - 4) / 2:.1f}" y="{bar_y + 34}" text-anchor="middle" '
            f'font-family="system-ui, sans-serif" font-size="11" fill="{muted}">{label}</text>'
        )
    # Furniture silhouette markers (abstract chest + posts), not human figures.
    cx = 32 + (chapter - 1) / 44 * (w - 64)
    parts.append(f'<rect x="{cx - 18:.1f}" y="78" width="36" height="22" rx="2" fill="{ink}" opacity="0.85"/>')
    parts.append(f'<line x1="{cx - 10:.1f}" y1="78" x2="{cx - 10:.1f}" y2="58" stroke="{ink}" stroke-width="3"/>')
    parts.append(f'<line x1="{cx + 10:.1f}" y1="78" x2="{cx + 10:.1f}" y2="58" stroke="{ink}" stroke-width="3"/>')
    parts.append(
        f'<text x="32" y="{h - 24}" font-family="system-ui, sans-serif" font-size="11" fill="{muted}">'
        f"Original diagram · Bradley Brand Furniture history pack · not a museum plate</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> int:
    n = 0
    for path in sorted(DRAFTS.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        m = FRONT.match(raw)
        if not m:
            continue
        fields = parse_fields(m.group(1))
        slug = fields.get("slug", path.stem)
        chapter = int(fields.get("chapter", "0") or 0)
        title = fields.get("title", slug)
        period = fields.get("period", "American bedroom furniture")
        out_dir = DIAGRAMS / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "lead-timeline.svg").write_text(
            svg_for(chapter, title, period), encoding="utf-8"
        )
        n += 1
    # Pack-level overview diagram.
    pack = DIAGRAMS / "series-overview.svg"
    pack.write_text(
        svg_for(1, "American Bedroom Furniture History", "1650–present (45 chapters)").replace(
            "Ch. 01 on the series axis", "Series overview — 45 chapters"
        ),
        encoding="utf-8",
    )
    print(f"generated {n} lead-timeline SVGs + series-overview.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
