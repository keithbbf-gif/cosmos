#!/usr/bin/env python3
"""Validate figure embeds and asset files for custom-furniture-rfq-sales."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "articles"
ASSETS = ROOT / "assets"
MANIFEST = ROOT / "image_assets.json"

FIGURE_RE = re.compile(
    r"<figure>\s*<img\s+src=\"\.\./assets/([^\"]+)\"\s+alt=\"([^\"]*)\"[^>]*>\s*"
    r"<figcaption>([\s\S]*?)</figcaption>\s*</figure>",
    re.IGNORECASE,
)


def main() -> int:
    if not MANIFEST.is_file():
        print("FAIL missing image_assets.json")
        return 1
    assets = json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_article = {a["article_file"]: a for a in assets}
    errors: list[str] = []
    for path in sorted(ART.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        figs = FIGURE_RE.findall(text)
        if len(figs) != 1:
            errors.append(f"{path.name}: expected 1 figure, found {len(figs)}")
            continue
        fname, alt, _cap = figs[0]
        asset = by_article.get(path.name)
        if not asset:
            errors.append(f"{path.name}: no manifest row")
            continue
        if asset["file"] != fname:
            errors.append(f"{path.name}: file {fname} != {asset['file']}")
        if not alt.strip():
            errors.append(f"{path.name}: empty alt")
        if len(alt) < 40:
            errors.append(f"{path.name}: alt too short for SEO ({len(alt)} chars)")
        ap = ASSETS / fname
        if not ap.is_file():
            errors.append(f"{path.name}: missing asset {fname}")
        elif ap.suffix.lower() in {".jpg", ".jpeg", ".png"} and ap.stat().st_size < 400:
            errors.append(f"{path.name}: raster too small {fname}")
    for a in assets:
        p = ASSETS / a["file"]
        if not p.is_file():
            errors.append(f"orphan manifest: {a['file']}")
    if errors:
        print("FAIL")
        for e in errors:
            print("-", e)
        return 1
    print(f"PASS figures={len(list(ART.glob('*.md')))} assets={len(assets)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
