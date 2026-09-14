#!/usr/bin/env python3
"""Regenerate GRAPHICS_INDEX.md from assets/ under the series root."""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SERIES_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SERIES_ROOT / "assets"
INDEX_PATH = SERIES_ROOT / "GRAPHICS_INDEX.md"
EMBEDS = SERIES_ROOT / "embeds"

SKIP_DIRS = {"_shared"}


def _title_from_svg(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(r"<title[^>]*>([^<]+)</title>", text, re.I)
    return m.group(1).strip() if m else None


def collect_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not ASSETS.is_dir():
        return rows
    for slug_dir in sorted(ASSETS.iterdir()):
        if not slug_dir.is_dir() or slug_dir.name in SKIP_DIRS:
            continue
        slug = slug_dir.name
        svgs = sorted(slug_dir.glob("*.svg"))
        if not svgs:
            continue
        embed = EMBEDS / f"{slug}.md"
        embed_rel = f"embeds/{slug}.md" if embed.is_file() else "—"
        for svg in svgs:
            rel = svg.relative_to(SERIES_ROOT).as_posix()
            title = _title_from_svg(svg) or svg.stem
            rows.append(
                {
                    "slug": slug,
                    "file": rel,
                    "title": title,
                    "embed": embed_rel,
                }
            )
    return rows


def render_index(rows: list[dict[str, str]]) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Graphics index — SLPWOW SLP News (stage 46)",
        "",
        f"_Auto-generated {ts}. Run `python scripts/regenerate_graphics_index.py` to refresh._",
        "",
        "| Slug | Asset | SVG `<title>` | Embed snippet |",
        "|------|-------|---------------|---------------|",
    ]
    for r in rows:
        lines.append(
            f"| `{r['slug']}` | `{r['file']}` | {r['title']} | `{r['embed']}` |"
        )
    if not rows:
        lines.append("| _none_ | — | — | — |")
    lines.extend(
        [
            "",
            "## Rights",
            "",
            "See `RIGHTS.md` and `PHOTO_NOTES.md`. All wave graphics are original SVG schematics.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    rows = collect_rows()
    INDEX_PATH.write_text(render_index(rows), encoding="utf-8")
    print(f"Wrote {INDEX_PATH} ({len(rows)} assets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
