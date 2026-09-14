#!/usr/bin/env python3
"""Fail if any article is missing edited voice_check or period figure."""
from __future__ import annotations

import re
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ARTICLES = PACK / "articles"
errors: list[str] = []

for path in sorted(ARTICLES.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    front = parts[1] if len(parts) > 1 else ""
    if "voice_check: edited" not in front:
        errors.append(f"{path.name}: missing voice_check: edited")
    if "../assets/photos/" not in text:
        errors.append(f"{path.name}: missing period photo figure")
    if "Figure 2." not in text:
        errors.append(f"{path.name}: missing Figure 2 caption")
    if 'class="wilmar-figure"' not in text:
        errors.append(f"{path.name}: missing wilmar-figure class")
    imgs = re.findall(r"<img\b", text)
    if len(imgs) < 2:
        errors.append(f"{path.name}: expected at least 2 img tags, got {len(imgs)}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"ok: {len(list(ARTICLES.glob('*.md')))} articles")
