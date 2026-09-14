#!/usr/bin/env python3
"""Verify lead figures, SEO frontmatter, and caption guardrails."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
REQUIRED = ("figure_id", "image_rights", "meta_description", "image_pass", "hero_figure")
CAP_BAD = (" cures ", " treats ", " prevents ", " heals ", " clinically ", " antioxidant")


def main() -> int:
    problems: list[str] = []
    paths = sorted(ROOT.glob("stage-*/[0-9][0-9]-*.md"))
    if len(paths) < 40:
        problems.append(f"draft count {len(paths)} < 40")

    for path in paths:
        raw = path.read_text(encoding="utf-8")
        m = FM_RE.match(raw)
        if not m:
            problems.append(f"{path}: missing frontmatter")
            continue
        fm = dict(re.findall(r"^([a-z_]+):\s*(.+)$", m.group(1), re.M))
        for key in REQUIRED:
            if key not in fm:
                problems.append(f"{path}: missing {key}")
        if fm.get("image_rights") != "documented":
            problems.append(f"{path}: image_rights not documented")
        body = m.group(2)
        if "<!-- htf-figure:v1 -->" not in body:
            problems.append(f"{path}: missing figure marker")
        if 'class="htf-figure"' not in body:
            problems.append(f"{path}: missing htf-figure block")
        imgs = re.findall(r'<img src="([^"]+)"', body)
        if len(imgs) != 1:
            problems.append(f"{path}: expected 1 img, got {len(imgs)}")
        for src in imgs:
            if not src.startswith("../assets/"):
                problems.append(f"{path}: img path must be relative ../assets/ ({src})")
        cap_m = re.search(r"<figcaption>(.*?)</figcaption>", body, re.S | re.I)
        cap = (cap_m.group(1) if cap_m else "").lower()
        if "<em>rights:</em>" not in cap:
            problems.append(f"{path}: figcaption missing Rights line")
        for bad in CAP_BAD:
            if bad in cap:
                problems.append(f"{path}: caption sniff {bad.strip()}")
        if 'alt=""' in body:
            problems.append(f"{path}: empty alt")

    print(f"drafts checked: {len(paths)}")
    if problems:
        print("defects:")
        for p in problems:
            print(" -", p)
        return 1
    print("figures ok (desk check; not legal review)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
