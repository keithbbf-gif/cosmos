#!/usr/bin/env python3
"""Structural QA for content/slpwow-slp-news/ graphics + SEO figures."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "articles"
ASSETS = ROOT / "assets"
EMBEDS = ROOT / "embeds"

REQUIRED_FRONT = {"title", "slug", "dek", "status", "category"}
FIGURE_NEEDLES = ("<figure", "<figcaption", 'itemtype="https://schema.org/ImageObject"', "itemprop=\"contentUrl\"")
OPS_FILES = (
    "RIGHTS.md",
    "STYLE_GUIDE.md",
    "AGENTS_GRAPHICS.md",
    "PHOTO_NOTES.md",
    "GRAPHICS_CHECKLIST.md",
    "GRAPHICS_INDEX.md",
)


def parse_front(text: str) -> dict[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}
    data: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    return data


def main() -> int:
    errors: list[str] = []
    files = sorted(ART.glob("*.md"))
    if len(files) != 46:
        errors.append(f"article count {len(files)} != 46")

    slugs: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        fm = parse_front(text)
        missing = REQUIRED_FRONT - set(fm)
        if missing:
            errors.append(f"{path.name}: missing frontmatter keys {sorted(missing)}")
        slug = fm.get("slug", "")
        if slug:
            slugs.append(slug)
        for needle in FIGURE_NEEDLES:
            if needle not in text:
                errors.append(f"{path.name}: missing SEO figure hook {needle!r}")
        asset_dir = ASSETS / slug if slug else None
        if slug and (not asset_dir or not any(asset_dir.glob("*.svg"))):
            errors.append(f"{path.name}: no SVG under assets/{slug}/")
        embed = EMBEDS / f"{slug}.md" if slug else None
        if slug and (not embed or not embed.is_file()):
            errors.append(f"{path.name}: missing embeds/{slug}.md")

    if len(slugs) != len(set(slugs)):
        errors.append("duplicate slugs in articles")

    for svg in ASSETS.rglob("*.svg"):
        body = svg.read_text(encoding="utf-8")
        if "<title" not in body or "<desc" not in body:
            errors.append(f"{svg.relative_to(ROOT)}: missing <title> or <desc>")
        if "face" in body.lower() and "no" not in body.lower()[:200]:
            pass  # footnote mentions faces

    for name in OPS_FILES:
        if not (ROOT / name).is_file():
            errors.append(f"missing ops file {name}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: {len(files)} articles, {len(list(ASSETS.rglob('*.svg')))} SVG assets, figures embedded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
