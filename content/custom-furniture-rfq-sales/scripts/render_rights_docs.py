#!/usr/bin/env python3
"""Render IMAGE_SOURCES.md and RIGHTS.md tables from image_assets.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "image_assets.json"


def main() -> int:
    assets = json.loads(MANIFEST.read_text(encoding="utf-8"))
    lines = [
        "# Image sources — custom furniture RFQ / quote-only sales",
        "",
        "Local files live in `assets/`. Raster images are **PD or Creative Commons** shop-adjacent documentary photos (Wikimedia Commons or U.S. government scans). **No AI-generated photographs.** Schematics are **original SVG** for this pack.",
        "",
        "| Draft | Local file | License | Commons / source | Credit |",
        "| --- | --- | --- | --- | --- |",
    ]
    for a in assets:
        src = a.get("commons_url") or "*(original SVG in repo)*"
        if a["kind"] == "photo" and not a.get("commons_url"):
            src = "*(staged from sibling content pack — see RIGHTS.md)*"
        lines.append(
            f"| `{a['draft_id']}` | `{a['file']}` | {a['license']} | {src} | {a.get('credit','')} |"
        )
    (ROOT / "IMAGE_SOURCES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote IMAGE_SOURCES.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
