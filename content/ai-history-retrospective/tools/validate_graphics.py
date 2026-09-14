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


def check_svg(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    if 'viewBox="' not in text and "viewBox='" not in text:
        errs.append("missing viewBox")
    if HTTP_IMAGE.search(text):
        errs.append("external HTTP image reference")
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        errs.append(f"XML parse: {exc}")
    if "portrait" in path.name or path.parent.name.startswith("figure-"):
        if PORTRAIT_IMAGE.search(text) and "rights not cleared" not in text:
            errs.append("portrait SVG contains <image> but no rights placeholder text")
    return errs


def main() -> int:
    if not ASSETS.is_dir():
        print(f"assets missing: {ASSETS}", file=sys.stderr)
        return 1
    failed = 0
    for svg in sorted(ASSETS.rglob("*.svg")):
        if "_templates" in svg.parts:
            continue
        problems = check_svg(svg)
        if problems:
            failed += 1
            print(f"FAIL {svg.relative_to(ROOT)}: {', '.join(problems)}")
    if failed:
        print(f"\n{failed} file(s) failed validation.")
        return 1
    count = len(list(ASSETS.rglob("*.svg"))) - len(list((ASSETS / "_templates").rglob("*.svg")))
    print(f"OK — {count} SVG(s) under assets/ (excluding _templates).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
