#!/usr/bin/env python3
"""Validate RIGHTS.md, image files, and figure markup in drafts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "images" / "registry.json"
DRAFTS = ROOT / "drafts"
IMAGES = ROOT / "images"
RIGHTS = ROOT / "RIGHTS.md"

FIGURE_RE = re.compile(
    r'<figure class="hfrh-figure">\s*'
    r'<img src="(?P<src>[^"]+)" alt="(?P<alt>[^"]*)"[^>]*/>\s*'
    r"<figcaption>(?P<cap>.*?)</figcaption>\s*</figure>",
    re.DOTALL,
)


def main() -> int:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    errors: list[str] = []
    if not RIGHTS.is_file():
        errors.append("missing RIGHTS.md")

    for draft_name, spec in reg["drafts"].items():
        img_path = IMAGES / spec["file"]
        if not img_path.is_file():
            errors.append(f"missing image {spec['file']} for {draft_name}")
        draft_path = DRAFTS / draft_name
        if not draft_path.is_file():
            errors.append(f"missing draft {draft_name}")
            continue
        body = draft_path.read_text(encoding="utf-8")
        m = FIGURE_RE.search(body)
        if not m:
            errors.append(f"{draft_name}: no hfrh-figure block")
            continue
        if m.group("src") != f"../images/{spec['file']}":
            errors.append(f"{draft_name}: img src mismatch")
        if m.group("alt") != spec["alt"]:
            errors.append(f"{draft_name}: alt text mismatch registry")
        if m.group("cap").strip() != spec["figcaption"].strip():
            errors.append(f"{draft_name}: figcaption mismatch registry")
        if "alt=\"\"" in body or len(spec["alt"]) < 40:
            errors.append(f"{draft_name}: alt too short for SEO")

    if errors:
        print("FAIL")
        for err in errors:
            print(f"- {err}")
        return 1
    print(f"PASS images={len(reg['drafts'])} rights={RIGHTS.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
