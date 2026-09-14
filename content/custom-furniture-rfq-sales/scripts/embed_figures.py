#!/usr/bin/env python3
"""Insert or replace one <figure> per article from image_assets.json."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "articles"
MANIFEST = ROOT / "image_assets.json"

FIGURE_RE = re.compile(r"<figure>.*?</figure>\s*", re.DOTALL | re.IGNORECASE)
DISCLAIMER_RE = re.compile(
    r"(\*\*Disclaimer\.\*\*[^\n]+\n\n)",
    re.MULTILINE,
)


def figure_html(asset: dict) -> str:
    fname = asset["file"]
    alt = asset["alt"].replace('"', "&quot;")
    cap = asset["figcaption"]
    lic = asset.get("license") or ""
    credit = asset.get("credit") or ""
    commons = asset.get("commons_url") or ""
    if fname.lower().endswith(".svg"):
        full_cap = cap if "CC0" in cap else f"{cap} Original schematic for this pack (CC0 1.0)."
    elif commons and "Public domain" in lic:
        full_cap = f"{cap} Photo: {credit} / public domain (<a href=\"{commons}\">source</a>)."
    elif commons:
        full_cap = f"{cap} Photo: {credit} / <a href=\"{commons}\">{lic}</a>."
    else:
        full_cap = f"{cap} {credit}".strip()
    return (
        "<figure>\n"
        f'  <img src="../assets/{fname}" alt="{alt}" width="1200" loading="lazy" decoding="async" />\n'
        f"  <figcaption>{full_cap}</figcaption>\n"
        "</figure>\n\n"
    )


def main() -> int:
    assets = json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_file = {a["article_file"]: a for a in assets}
    updated = 0
    for path in sorted(ART.glob("*.md")):
        asset = by_file.get(path.name)
        if not asset:
            print("skip no asset", path.name)
            continue
        text = path.read_text(encoding="utf-8")
        block = figure_html(asset)
        if FIGURE_RE.search(text):
            text = FIGURE_RE.sub(block, text, count=1)
        elif DISCLAIMER_RE.search(text):
            text = DISCLAIMER_RE.sub(r"\1" + block, text, count=1)
        else:
            print("skip no anchor", path.name)
            continue
        path.write_text(text, encoding="utf-8")
        updated += 1
    print(f"updated {updated} articles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
