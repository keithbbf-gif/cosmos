#!/usr/bin/env python3
"""Validate editorial SVGs and figure HTML for open-source-ai-history-2015-2026."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DRAFTS = ROOT / "drafts"
STAGED = ROOT / "staged-embeds"
REGISTRY = json.loads((ROOT / "figure_registry.json").read_text(encoding="utf-8"))
DRAFT_MAP = REGISTRY["drafts"]

HTTP_REF = re.compile(r'(?:href|xlink:href)\s*=\s*["\']https?://', re.I)
RASTER_EMBED = re.compile(r"<image\b", re.I)
FIGURE_RE = re.compile(
    r'<figure class="oss-stack-figure">[\s\S]*?</figure>',
    re.I,
)


def check_svg(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    if 'viewBox="' not in text and "viewBox='" not in text:
        errs.append("missing viewBox")
    if HTTP_REF.search(text):
        errs.append("external HTTP reference")
    if RASTER_EMBED.search(text):
        errs.append("embedded raster image")
    if "<desc" not in text.lower():
        errs.append("missing desc")
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        errs.append(f"XML: {exc}")
    return errs


def check_embed_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if REGISTRY["marker"] not in text:
        return ["missing graphics marker"]
    figures = FIGURE_RE.findall(text)
    if not figures:
        return ["no figure blocks"]
    for i, fig in enumerate(figures, 1):
        alt_m = re.search(r'alt="([^"]*)"', fig)
        if not alt_m or len(alt_m.group(1)) < 40:
            return [f"figure {i}: SEO alt too short"]
        if "<figcaption>Figure" not in fig:
            return [f"figure {i}: missing figcaption"]
    if re.search(r"!\[[^\]]*\]\(", text):
        return ["legacy markdown image syntax"]
    return []


def main() -> int:
    failed = 0
    for svg in sorted(ASSETS.rglob("*.svg")):
        problems = check_svg(svg)
        if problems:
            failed += 1
            print(f"FAIL SVG {svg.relative_to(ROOT)}: {', '.join(problems)}")

    for slug in DRAFT_MAP:
        for folder, label in ((STAGED, "staged"), (DRAFTS, "draft")):
            path = folder / f"{slug}.md"
            if not path.exists():
                print(f"FAIL {label} missing {slug}.md")
                failed += 1
                continue
            problems = check_embed_file(path)
            if problems:
                failed += 1
                print(f"FAIL {label}/{slug}.md: {', '.join(problems)}")

    if failed:
        print(f"\n{failed} check(s) failed.")
        return 1
    svg_count = len(list(ASSETS.rglob("*.svg")))
    print(f"OK — {svg_count} SVG(s), {len(DRAFT_MAP)} figure-bearing drafts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
