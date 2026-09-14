#!/usr/bin/env python3
"""Validate graphics pack: SVG XML, figure embeds, registry plates."""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

from pack_data import ARTICLES

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "assets" / "figures" / "REGISTRY.toml"
MARKER = "<!-- graphics-pack:nlp-bt-v1 -->"


def check_svg(path: Path) -> list[str]:
    errs: list[str] = []
    try:
        ET.parse(path)
    except ET.ParseError as e:
        errs.append(f"{path}: XML {e}")
    text = path.read_text(encoding="utf-8")
    if 'xmlns="http://www.w3.org/2000/svg"' not in text:
        errs.append(f"{path}: missing SVG namespace")
    if "http://" in text and "wikimedia" not in text:
        if "<image" in text and "href=" in text:
            errs.append(f"{path}: external raster ref in SVG")
    return errs


def main() -> int:
    plates = tomllib.loads(REGISTRY.read_text(encoding="utf-8")).get("plates", {})
    errs: list[str] = []
    for art in ARTICLES:
        slug = art["slug"]
        for name in ("historical-timeline.svg", "concept-chart.svg"):
            p = ROOT / "assets" / slug / name
            if not p.exists():
                errs.append(f"missing {p}")
            else:
                errs.extend(check_svg(p))
        if art["plate"] not in plates:
            errs.append(f"plate key missing in REGISTRY: {art['plate']} ({slug})")
        md = ROOT / art["file"]
        body = md.read_text(encoding="utf-8")
        if MARKER not in body:
            errs.append(f"no graphics marker in {md}")
        if body.count("<figure") < 3:
            errs.append(f"expected 3 figures in {md}")
        if "portrait: null" not in body:
            errs.append(f"portrait: null not set in {md}")
        if not re.search(r'alt="[^"]{20,}"', body):
            errs.append(f"short or missing img alt in {md}")
    if errs:
        for e in errs:
            print(e, file=sys.stderr)
        return 1
    print(f"ok: {len(ARTICLES)} essays, {len(plates)} registry plates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
