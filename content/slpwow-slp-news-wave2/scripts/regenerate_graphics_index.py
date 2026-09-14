#!/usr/bin/env python3
"""Regenerate GRAPHICS_INDEX.md from assets/ under the wave-2 pack."""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SERIES_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SERIES_ROOT / "assets"
INDEX_PATH = SERIES_ROOT / "GRAPHICS_INDEX.md"
EMBEDS = SERIES_ROOT / "embeds"


def _title_from_svg(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(r"<title[^>]*>([^<]+)</title>", text, re.I)
    return m.group(1).strip() if m else None


def main() -> int:
    rows: list[tuple[str, str, str, str]] = []
    if ASSETS.is_dir():
        for slug_dir in sorted(ASSETS.iterdir()):
            if not slug_dir.is_dir():
                continue
            slug = slug_dir.name
            for svg in sorted(slug_dir.glob("*.svg")):
                rel = svg.relative_to(SERIES_ROOT).as_posix()
                title = _title_from_svg(svg) or svg.stem
                embed = EMBEDS / f"{slug}.md"
                embed_rel = f"embeds/{slug}.md" if embed.is_file() else "—"
                rows.append((slug, rel, title, embed_rel))

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Graphics index — SLPWOW SLP News wave 2",
        "",
        f"_Auto-generated {ts}. Run `python scripts/regenerate_graphics_index.py`._",
        "",
        "| Slug | Asset | SVG `<title>` | Embed snippet |",
        "|------|-------|---------------|---------------|",
    ]
    for slug, rel, title, embed_rel in rows:
        lines.append(f"| `{slug}` | `{rel}` | {title} | `{embed_rel}` |")
    if not rows:
        lines.append("| _none_ | — | — | — |")
    lines.extend(["", "See `RIGHTS.md` and `PHOTO_NOTES.md`.", ""])
    INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {INDEX_PATH} ({len(rows)} assets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
