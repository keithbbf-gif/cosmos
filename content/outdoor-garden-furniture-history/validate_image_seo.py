#!/usr/bin/env python3
"""Validate IMAGE+SEO blocks for outdoor-garden-furniture-history drafts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
DIAGRAMS = ROOT / "assets" / "diagrams"
RIGHTS = ROOT / "RIGHTS.md"
SHARED_FEATURED = ROOT / "assets" / "_shared" / "series-featured.svg"

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
IMG_SRC = re.compile(r'<img[^>]+src="([^"]+)"')
REQUIRED_FM = (
    "meta_description",
    "figure_id",
    "image_rights",
    "image_pass",
    "featured_image",
)
FIGURE_CLASS = "ogfh-figure"
MARKER = "<!-- ogfh-figure:v1 -->"


def main() -> int:
    errors: list[str] = []
    files = sorted(DRAFTS.glob("*.md"))
    if not RIGHTS.is_file():
        errors.append("missing RIGHTS.md")
    if not SHARED_FEATURED.is_file():
        errors.append("missing assets/_shared/series-featured.svg")

    for path in files:
        raw = path.read_text(encoding="utf-8")
        m = FM_RE.match(raw)
        if not m:
            errors.append(f"{path.name}: missing frontmatter")
            continue
        fm, body = m.group(1), m.group(2)
        fields = dict(re.findall(r"^([a-z_]+):[ \t]*(.+)$", fm, re.M))
        for req in REQUIRED_FM:
            if req not in fields:
                errors.append(f"{path.name}: missing {req}")
        if fields.get("image_rights") != "documented":
            errors.append(f"{path.name}: image_rights must be documented")
        if MARKER not in body:
            errors.append(f"{path.name}: missing {MARKER}")
        if f'<figure class="{FIGURE_CLASS}' not in body:
            errors.append(f"{path.name}: missing {FIGURE_CLASS} block")
        if "<em>Rights:</em>" not in body:
            errors.append(f"{path.name}: missing Rights figcaption line")
        srcs = IMG_SRC.findall(body)
        if len(srcs) != 1:
            errors.append(f"{path.name}: expected 1 img src, got {len(srcs)}")
        elif srcs[0].startswith("http"):
            errors.append(f"{path.name}: img must be pack-relative, not hot-linked")
        else:
            rel = srcs[0].replace("../", "")
            disk = ROOT / rel
            if not disk.is_file():
                errors.append(f"{path.name}: missing asset {rel}")
        stem = path.stem
        if not (DIAGRAMS / f"{stem}.svg").is_file():
            errors.append(f"{path.name}: missing diagrams/{stem}.svg")

    for svg in DIAGRAMS.glob("*.svg"):
        text = svg.read_text(encoding="utf-8")
        if "<title>" not in text or "<desc>" not in text:
            errors.append(f"{svg.name}: missing title/desc")
        lower = text.lower()
        if "face" in lower and "surface" not in lower:
            # allow "face grain" etc. — only flag obvious portrait hints
            if "portrait" in lower or "person" in lower:
                errors.append(f"{svg.name}: possible human likeness")

    print(f"drafts={len(files)} diagrams={len(list(DIAGRAMS.glob('*.svg')))}")
    if errors:
        print("FAIL")
        for err in errors:
            print(f"- {err}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
