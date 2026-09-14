#!/usr/bin/env python3
"""Validate butcher-block guide IMAGE+SEO assets and figure embeds."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content" / "butcher-block-countertops-guide"
DRAFT_DIR = PACK / "drafts"
RIGHTS = PACK / "RIGHTS.md"
INDEX = PACK / "GRAPHICS_INDEX.md"
FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    data: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith("  -"):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    return data, m.group(2)


def main() -> int:
    errors: list[str] = []
    if not RIGHTS.is_file():
        errors.append("missing RIGHTS.md")
    if not INDEX.is_file():
        errors.append("missing GRAPHICS_INDEX.md")
    rights_text = RIGHTS.read_text(encoding="utf-8") if RIGHTS.is_file() else ""
    illustrated = 0
    for path in sorted(DRAFT_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        if "meta_description" not in fm:
            errors.append(f"{path.name}: missing meta_description")
        if "featured_image" not in fm:
            errors.append(f"{path.name}: missing featured_image")
        feat = fm.get("featured_image", "")
        if feat:
            asset = PACK / "drafts" / feat
            if not asset.is_file():
                errors.append(f"{path.name}: featured_image missing file {feat}")
        if "figures:" in text or fm.get("figures"):
            illustrated += 1
            if "bradley-figure" not in body:
                errors.append(f"{path.name}: figures frontmatter but no <figure> in body")
            if "<img" in body and 'alt="' not in body:
                errors.append(f"{path.name}: figure img missing alt")
            m = re.search(r'src="(\.\./assets/[^"]+)"', body)
            if m:
                rel = m.group(1)
                rights_key = rel.removeprefix("../")
                if rights_key not in rights_text:
                    errors.append(f"{path.name}: asset not listed in RIGHTS.md: {rel}")
                if not (PACK / "drafts" / rel).is_file():
                    errors.append(f"{path.name}: figure src missing file {rel}")
    if illustrated < 10:
        errors.append(f"expected >= 10 illustrated drafts, got {illustrated}")
    if errors:
        print("errors:")
        for e in errors:
            print(f"  FAIL  {e}")
        return 1
    print(f"OK ({illustrated} illustrated drafts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
