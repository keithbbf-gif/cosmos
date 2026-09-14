#!/usr/bin/env python3
"""Validate figure embeds and image files for HFRH drafts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
IMAGES = ROOT / "images"
ASSETS_PATH = ROOT / "image_assets.json"

FIGURE_RE = re.compile(
    r"<figure>\s*<img\s+src=\"\.\./images/([^\"]+)\"\s+alt=\"([^\"]*)\"[^>]*>\s*"
    r"<figcaption>([^<]*)</figcaption>\s*</figure>",
    re.IGNORECASE,
)


def main() -> int:
    if not ASSETS_PATH.is_file():
        print("FAIL: missing image_assets.json — run scripts/fetch_images.py")
        return 1
    assets = json.loads(ASSETS_PATH.read_text(encoding="utf-8"))
    by_id = {a["draft_id"]: a for a in assets}
    errors: list[str] = []
    for path in sorted(DRAFTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        m_id = re.search(r"^id:\s*(\S+)", text, re.MULTILINE)
        if not m_id:
            errors.append(f"{path.name}: missing id")
            continue
        draft_id = m_id.group(1)
        figs = FIGURE_RE.findall(text)
        if len(figs) != 1:
            errors.append(f"{path.name}: expected 1 figure, found {len(figs)}")
            continue
        fname, alt, cap = figs[0]
        asset = by_id.get(draft_id)
        if not asset:
            errors.append(f"{path.name}: no asset for {draft_id}")
            continue
        if asset["file"] != fname:
            errors.append(f"{path.name}: image {fname} != manifest {asset['file']}")
        if not alt.strip():
            errors.append(f"{path.name}: empty alt")
        if not cap.strip():
            errors.append(f"{path.name}: empty figcaption")
        img_path = IMAGES / fname
        if not img_path.is_file() or img_path.stat().st_size < 200:
            errors.append(f"{path.name}: missing image {fname}")
    for a in assets:
        if not (IMAGES / a["file"]).is_file():
            errors.append(f"manifest orphan: {a['file']}")
    if errors:
        print("FAIL")
        for e in errors:
            print("-", e)
        return 1
    print(f"PASS figures={len(list(DRAFTS.glob('*.md')))} assets={len(assets)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
