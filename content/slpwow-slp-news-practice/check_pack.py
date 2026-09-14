#!/usr/bin/env python3
"""Editor smoke check for slpwow-slp-news-practice. Exit 1 on fail."""
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
ASSETS = ROOT / "assets"
EMBEDS = ROOT / "embeds"
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
ALLOWED_TYPES = {
    "research-literacy",
    "reimbursement",
    "school-medical",
    "practice-headline",
}
BANNED_BODY = re.compile(
    r"bill 92507|always append KX|gold standard treatment|"
    r"try this protocol|home program:|do these ten|"
    r"your patient has (a |an )?(speech delay|aspiration pneumonia)",
    re.I,
)
SLOP = re.compile(
    r"\b(delve|leverage|robust|game-?changer|cutting-edge|in conclusion|"
    r"it's important to note|whether you're a|plethora|tapestry)\b",
    re.I,
)


def main() -> int:
    files = sorted(ART.glob("*.md"))
    errors: list[str] = []
    if len(files) < 40:
        errors.append(f"article count {len(files)} < 40")
    for p in files:
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
        if not m:
            errors.append(f"{p.name}: missing frontmatter")
            continue
        if yaml:
            meta = yaml.safe_load(m.group(1)) or {}
        else:
            meta = {}
            for line in m.group(1).splitlines():
                if ":" in line and not line.startswith(" ") and not line.startswith("-"):
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
        miss = REQUIRED - set(meta)
        if miss:
            errors.append(f"{p.name}: missing keys {sorted(miss)}")
        if meta.get("status") != "draft" or meta.get("stage") != "draft":
            errors.append(f"{p.name}: status/stage must be draft")
        if meta.get("series") != "slpwow-slp-news-practice":
            errors.append(f"{p.name}: bad series")
        if meta.get("type") not in ALLOWED_TYPES:
            errors.append(f"{p.name}: bad type {meta.get('type')!r}")
        body = text[m.end() :]
        if "Educational" not in body and "Disclaimer" not in body:
            errors.append(f"{p.name}: missing disclaimer")
        words = len(re.findall(r"\b[\w']+\b", body))
        if words < 650:
            errors.append(f"{p.name}: {words} words < 650")
        if BANNED_BODY.search(body):
            errors.append(f"{p.name}: protocol-or-billing-shaped line")
        if SLOP.search(body):
            errors.append(f"{p.name}: style-guide slop")
        slug = str(meta.get("slug", ""))
        if slug and not p.name.endswith(slug + ".md"):
            errors.append(f"{p.name}: slug {slug!r} mismatch")
        if "[CITE NEEDED]" in body:
            errors.append(f"{p.name}: unresolved [CITE NEEDED]")
        if "<figure" not in body or "<figcaption" not in body:
            errors.append(f"{p.name}: missing figure/figcaption embed")
        if 'itemtype="https://schema.org/ImageObject"' not in body:
            errors.append(f"{p.name}: missing ImageObject schema on figure")
    for svg in ASSETS.rglob("*.svg"):
        if "_shared" in svg.parts:
            continue
        body_svg = svg.read_text(encoding="utf-8")
        if "<title" not in body_svg or "<desc" not in body_svg:
            errors.append(f"{svg.relative_to(ROOT)}: missing title/desc")
    if not (ROOT / "RIGHTS.md").is_file():
        errors.append("RIGHTS.md missing")
    if errors:
        print("FAIL")
        for e in errors:
            print(" ", e)
        return 1
    print(f"OK {len(files)} drafts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
