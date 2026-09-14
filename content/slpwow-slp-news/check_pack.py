#!/usr/bin/env python3
"""Smoke check for slpwow-slp-news pack."""
from __future__ import annotations

import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parent
ART = ROOT / "articles"
REQUIRED = {
    "title",
    "slug",
    "meta_description",
    "series",
    "type",
    "status",
    "stage",
    "voice_check",
    "citations",
}


def main() -> int:
    files = sorted(ART.glob("*.md"))
    errors: list[str] = []
    if len(files) < 8:
        errors.append(f"article count {len(files)} < 8")
    for p in files:
        text = p.read_text(encoding="utf-8")
        if "<figure" not in text or "<figcaption" not in text:
            errors.append(f"{p.name}: missing figure/figcaption embed")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
        if not m:
            errors.append(f"{p.name}: missing frontmatter")
            continue
        if yaml is None:
            continue
        data = yaml.safe_load(m.group(1)) or {}
        missing = REQUIRED - set(data)
        if missing:
            errors.append(f"{p.name}: missing keys {sorted(missing)}")
        if data.get("series") != "slpwow-slp-news":
            errors.append(f"{p.name}: wrong series")
    for svg in (ROOT / "assets").rglob("*.svg"):
        body = svg.read_text(encoding="utf-8")
        if "<title" not in body or "<desc" not in body:
            errors.append(f"{svg.relative_to(ROOT)}: missing title/desc")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: {len(files)} articles, figures embedded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
