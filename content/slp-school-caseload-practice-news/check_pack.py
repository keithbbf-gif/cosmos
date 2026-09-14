#!/usr/bin/env python3
"""Editor smoke check for slp-school-caseload-practice-news. Exit 1 on fail."""
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
FIGURE_NEEDLES = (
    "<figure",
    "<figcaption",
    'itemtype="https://schema.org/ImageObject"',
    'itemprop="contentUrl"',
)
FIG_OPS_FILES = ("RIGHTS.md", "AGENTS_GRAPHICS.md", "GRAPHICS_CHECKLIST.md", "GRAPHICS_INDEX.md")
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
    "news-explainer",
    "practice-explainer",
    "caseload-explainer",
    "series-map",
}
BANNED_BODY = re.compile(
    r"your child has (a |an )?(speech delay|language disorder|autism|apraxia)|"
    r"asha'?s caseload cap|asha'?s caseload limit|"
    r"bill medicaid this way|"
    r"maya,? \d|on my tuesday|"
    r"causes autism|treat autism|gold standard treatment|"
    r"this means they have",
    re.I,
)
PHI_SHAPE = re.compile(
    r"\b(student named|IEP for [A-Z][a-z]+, \d|in our Fayetteville clinic)\b"
)
SLOP = re.compile(
    r"\b(delve|leverage|robust|game-?changer|cutting-edge|in conclusion|"
    r"it's important to note|whether you're a)\b",
    re.I,
)
DISCLAIMER = re.compile(r"Educational only|Disclaimer", re.I)


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
                if ":" in line and not line.startswith(" "):
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
        miss = REQUIRED - set(meta)
        if miss:
            errors.append(f"{p.name}: missing keys {sorted(miss)}")
        if meta.get("status") != "draft" or meta.get("stage") != "draft":
            errors.append(f"{p.name}: status/stage must be draft")
        if meta.get("series") != "slp-school-caseload-practice-news":
            errors.append(f"{p.name}: bad series")
        if meta.get("type") not in ALLOWED_TYPES:
            errors.append(f"{p.name}: bad type {meta.get('type')!r}")
        if meta.get("voice_check") not in {"human", "edited"}:
            errors.append(f"{p.name}: voice_check must be human or edited")
        body = text[m.end() :]
        if not DISCLAIMER.search(body):
            errors.append(f"{p.name}: missing disclaimer")
        if "PHI" not in body and "protected health" not in body.lower():
            errors.append(f"{p.name}: disclaimer should name PHI / student records")
        words = len(re.findall(r"\b[\w']+\b", body))
        if words < 650:
            errors.append(f"{p.name}: {words} words < 650")
        if BANNED_BODY.search(body):
            errors.append(f"{p.name}: diagnosis/cap/PHI-shaped line")
        if PHI_SHAPE.search(body):
            errors.append(f"{p.name}: PHI-shaped proper name")
        if SLOP.search(body):
            errors.append(f"{p.name}: style-guide slop")
        if "[CITE NEEDED]" in body:
            errors.append(f"{p.name}: unresolved [CITE NEEDED]")
        slug = str(meta.get("slug", ""))
        if slug and not p.name.endswith(slug + ".md"):
            errors.append(f"{p.name}: slug {slug!r} mismatch")
        for needle in FIGURE_NEEDLES:
            if needle not in text:
                errors.append(f"{p.name}: missing SEO figure hook {needle!r}")
        if slug:
            asset_dir = ASSETS / slug
            if not asset_dir.is_dir() or not any(asset_dir.glob("*.svg")):
                errors.append(f"{p.name}: no SVG under assets/{slug}/")
            embed = EMBEDS / f"{slug}.md"
            if not embed.is_file():
                errors.append(f"{p.name}: missing embeds/{slug}.md")
    for svg in ASSETS.rglob("*.svg") if ASSETS.is_dir() else []:
        svg_text = svg.read_text(encoding="utf-8")
        if "<title" not in svg_text or "<desc" not in svg_text:
            errors.append(f"{svg.relative_to(ROOT)}: missing <title> or <desc>")
    for name in FIG_OPS_FILES:
        if not (ROOT / name).is_file():
            errors.append(f"missing ops file {name}")
    if errors:
        print("FAIL")
        for e in errors:
            print(" ", e)
        return 1
    svg_n = len(list(ASSETS.rglob("*.svg"))) if ASSETS.is_dir() else 0
    print(f"OK {len(files)} drafts, {svg_n} SVG figures embedded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
