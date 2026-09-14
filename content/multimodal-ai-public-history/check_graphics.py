#!/usr/bin/env python3
"""Validate graphics, RIGHTS, and SEO embed conventions for the multimodal history pack."""

from __future__ import annotations

import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GRAPHICS = ROOT / "graphics"
INDEX = ROOT / "GRAPHICS_INDEX.md"
RIGHTS = ROOT / "RIGHTS.md"
EMBEDS = ROOT / "EMBEDS.md"

FIG_RE = re.compile(r"`(graphics/fig-\d{2}-[^`]+\.svg)`", re.MULTILINE)
EMBED_REQUIRED = (
    "<figure",
    "<img",
    'alt="',
    "width=",
    "height=",
    "<figcaption",
    "itemprop=",
)
FORBIDDEN_SVG = (
    "<image ",  # raster embed — no uncredited photos / AI faces
    "href=\"http",  # external raster
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def parse_svg(path: Path) -> ET.Element:
    return ET.fromstring(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    if not RIGHTS.is_file():
        errors.append("missing RIGHTS.md")
    if not INDEX.is_file():
        errors.append("missing GRAPHICS_INDEX.md")
    if not EMBEDS.is_file():
        errors.append("missing EMBEDS.md")

    index_text = INDEX.read_text(encoding="utf-8") if INDEX.is_file() else ""
    listed = sorted(set(FIG_RE.findall(index_text)))
    if not listed:
        errors.append("GRAPHICS_INDEX.md lists no graphics/*.svg paths")

    embeds_text = EMBEDS.read_text(encoding="utf-8") if EMBEDS.is_file() else ""
    for needle in EMBED_REQUIRED:
        if needle not in embeds_text:
            errors.append(f"EMBEDS.md missing SEO fragment: {needle!r}")

    checksums: dict[str, str] = {}
    for rel in listed:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"indexed file missing: {rel}")
            continue
        raw = path.read_text(encoding="utf-8")
        for bad in FORBIDDEN_SVG:
            if bad in raw:
                errors.append(f"{rel}: forbidden token {bad!r}")
        if "<title" not in raw or "<desc" not in raw:
            errors.append(f"{rel}: missing <title> or <desc>")
        try:
            parse_svg(path)
        except ET.ParseError as exc:
            errors.append(f"{rel}: invalid XML: {exc}")
        checksums[rel] = sha256(path)
        print(f"OK {rel} sha256={checksums[rel][:16]}…")

    # Every file on disk should be indexed
    for path in sorted(GRAPHICS.glob("fig-*.svg")):
        rel = f"graphics/{path.name}"
        if rel not in listed:
            errors.append(f"unindexed SVG: {rel}")

    # Essays that reference figures should use <figure> blocks
    figure_essays = {
        "stage-00-how-to-read/00-how-to-read-this-series.md": "fig-02-series-stage-map.svg",
        "stage-02-contrastive-vl/10-clip-the-public-paper.md": "fig-03-contrastive-joint-space.svg",
        "stage-04-diffusion-mechanics/24-latent-diffusion.md": "fig-04-latent-diffusion-loop.svg",
        "stage-05-public-t2i/27-the-stable-diffusion-weights-drop.md": "fig-01-public-multimodal-timeline.svg",
        "stage-05-public-t2i/30-two-publics-api-and-weights.md": "fig-05-two-publics-api-vs-weights.svg",
        "stage-08-beyond-still-images/44-imagebind-and-joint-spaces-after-clip.md": "fig-06-modality-fanout.svg",
    }
    for rel_essay, svg_name in figure_essays.items():
        essay = ROOT / rel_essay
        if not essay.is_file():
            errors.append(f"missing essay for figure embed: {rel_essay}")
            continue
        body = essay.read_text(encoding="utf-8")
        if "<figure" not in body or svg_name not in body:
            errors.append(f"{rel_essay}: missing <figure> embed for {svg_name}")
        if 'alt="' not in body:
            errors.append(f"{rel_essay}: figure missing alt text")

    readme = ROOT / "README.md"
    if readme.is_file():
        rb = readme.read_text(encoding="utf-8")
        if "fig-01-public-multimodal-timeline.svg" not in rb:
            errors.append("README.md missing hero timeline figure")
        if "fig-02-series-stage-map.svg" not in rb:
            errors.append("README.md missing stage map figure")

    if errors:
        print("FAIL")
        for err in errors:
            print(f"  {err}")
        return 1
    print(f"PASS figures={len(listed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
