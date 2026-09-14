#!/usr/bin/env python3
"""Structural QA for content/sports-nutrition-rd-2020/ image + SEO pass."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
SPECS_SLUGS: set[str] = set()

# Import slug list from build_figures without running main
from build_figures import SPECS  # noqa: E402

SPECS_SLUGS = set(SPECS)

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
FIGURE_RE = re.compile(r'<figure class="sn-rd-figure', re.I)
DISCLAIMER_NEEDLE = "not medical advice"
AI_FACE = re.compile(
    r"(ai[- ]generated|synthetic (?:face|likeness|portrait)|midjourney|stable diffusion)",
    re.I,
)

REQUIRED_YAML = [
    "title",
    "slug",
    "status",
    "stage",
    "series",
    "meta_description",
    "hero_figure",
    "figure_status",
    "claims",
    "last_reviewed",
]

BANNED = [
    r"\bdelve(?:s|d|ing)?\b",
    r"it's important to note",
    r"it is important to note",
    r"\bleverage\b",
    r"\bunlock(?:s|ed|ing)?\b",
    r"cutting-edge",
    r"game-chang",
    r"\bbiohack",
]


def parse_front(text: str) -> dict[str, str]:
    m = FRONT_RE.match(text)
    if not m:
        return {}
    data: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    return data


def main() -> int:
    errors: list[str] = []
    drafts = sorted(ROOT.glob("stage-*/*.md"))
    if len(drafts) != 45:
        errors.append(f"draft count {len(drafts)} != 45")

    for path in drafts:
        text = path.read_text(encoding="utf-8")
        fm = parse_front(text)
        for key in REQUIRED_YAML:
            if key not in fm:
                errors.append(f"{path.name}: missing YAML {key}")
        slug = fm.get("slug", "")
        if slug not in SPECS_SLUGS:
            errors.append(f"{path.name}: slug {slug!r} not in figure SPECS")
        if fm.get("series") != "sports-nutrition-rd-2020":
            errors.append(f"{path.name}: bad series")
        if fm.get("figure_status") not in {"original-svg", "cleared-pd"}:
            errors.append(f"{path.name}: bad figure_status")
        hero = fm.get("hero_figure", "")
        if not hero.startswith(f"figures/{slug}/figure."):
            errors.append(f"{path.name}: hero_figure path mismatch")
        if len(fm.get("meta_description", "")) > 165:
            errors.append(f"{path.name}: meta_description too long")
        if DISCLAIMER_NEEDLE not in text.lower():
            errors.append(f"{path.name}: missing disclaimer")
        if not FIGURE_RE.search(text):
            errors.append(f"{path.name}: missing sn-rd-figure")
        if AI_FACE.search(text) and "do not" not in text.lower():
            errors.append(f"{path.name}: possible AI-face language")
        low = text.lower()
        for pat in BANNED:
            if re.search(pat, low):
                errors.append(f"{path.name}: banned /{pat}/")

    if not FIG.is_dir():
        errors.append("missing figures/")
    else:
        for slug in sorted(SPECS_SLUGS):
            folder = FIG / slug
            rights = folder / "RIGHTS.md"
            if not rights.is_file():
                errors.append(f"missing {rights.relative_to(ROOT)}")
            else:
                rt = rights.read_text(encoding="utf-8")
                if "ai_generated | no" not in rt:
                    errors.append(f"{rights.relative_to(ROOT)} must declare ai_generated | no")
            spec = SPECS[slug]
            ext = "jpg" if spec["status"] == "cleared-pd" else "svg"
            fig = folder / f"figure.{ext}"
            if not fig.is_file():
                errors.append(f"missing {fig.relative_to(ROOT)}")

        for img in ROOT.rglob("*"):
            if img.suffix.lower() not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                continue
            rel = img.relative_to(ROOT)
            if rel.parts[0] != "figures":
                errors.append(f"raster outside figures/: {rel}")

    for name in ("README.md", "_editorial/IMAGE_SEO.md", "_editorial/CLAIMS_POLICY.md"):
        if not (ROOT / name).is_file():
            errors.append(f"missing {name}")

    print(f"drafts: {len(drafts)}")
    print(f"figure folders: {len(list(FIG.glob('*'))) if FIG.is_dir() else 0}")
    print(f"errors: {len(errors)}")
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
