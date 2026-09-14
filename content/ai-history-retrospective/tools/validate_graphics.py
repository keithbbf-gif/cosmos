#!/usr/bin/env python3
"""Validate SVG graphics under content/ai-history-retrospective/assets/."""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

HTTP_IMAGE = re.compile(r'(?:href|xlink:href)\s*=\s*["\']https?://', re.I)
PORTRAIT_IMAGE = re.compile(r"<image\b", re.I)
SKIP_NAMES = {"archival-defs.svg", "portrait-plate.svg"}


def is_portrait_plate(path: Path) -> bool:
    return path.parent.name.startswith("figure-") and path.name == "portrait-plate.svg"


def check_svg(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    if 'viewBox="' not in text and "viewBox='" not in text:
        errs.append("missing viewBox")
    if HTTP_IMAGE.search(text):
        errs.append("external HTTP image reference")
    if "<desc" not in text and path.name not in SKIP_NAMES:
        errs.append("missing desc (accessibility + archival caption source)")
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        errs.append(f"XML parse: {exc}")
    if is_portrait_plate(path):
        if PORTRAIT_IMAGE.search(text):
            errs.append("portrait plate must not embed raster image until rights cleared")
        if "rights not cleared" not in text.lower():
            errs.append('portrait plate must state "rights not cleared"')
        if "no likeness reproduced" not in text.lower():
            errs.append('portrait plate must state "No likeness reproduced"')
    return errs


def main() -> int:
    if not ASSETS.is_dir():
        print(f"assets missing: {ASSETS}", file=sys.stderr)
        return 1
    failed = 0
    counted = 0
    for svg in sorted(ASSETS.rglob("*.svg")):
        if "_templates" in svg.parts:
            continue
        counted += 1
        problems = check_svg(svg)
        if problems:
            failed += 1
            print(f"FAIL {svg.relative_to(ROOT)}: {', '.join(problems)}")
    if failed:
        print(f"\n{failed} file(s) failed validation.")
        return 1
    print(f"OK — {counted} production SVG(s) under assets/ (excluding _templates).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
