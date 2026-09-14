#!/usr/bin/env python3
"""Desk check for staged fig-mediterranean-foodways drafts."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "id",
    "slug",
    "title",
    "dek",
    "series",
    "status",
    "editorial_stage",
    "lane",
    "themes",
    "region",
    "hero",
    "claims_policy",
]
SLOP = [
    "rich tapestry",
    "delve into",
    "in this article",
    "it's important to note",
    "in conclusion",
    "furthermore",
    "moreover",
    "packed with",
]
# Hits allowed only in refusal / house-rule sentences.
MED = [
    "antioxidant",
    "vitamin",
    "blood sugar",
    "digestive",
    "weight loss",
    "nutrient-rich",
    "boosts",
]
FIGURE_MARKER = "<!-- fmf-hero-figure -->"


def body_words(body: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", body))


def main() -> int:
    drafts = sorted(ROOT.glob("[0-9][0-9]-*.md"))
    img = (ROOT / "IMAGE_SOURCES.md").read_text(encoding="utf-8")
    rights = (ROOT / "RIGHTS.md")
    if not rights.is_file():
        errors.append("missing RIGHTS.md")
    else:
        rights_text = rights.read_text(encoding="utf-8")
    man = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    rows: list[dict] = []
    ids: set[str] = set()
    slugs: set[str] = set()
    theme_counter: Counter[str] = Counter()

    if len(drafts) < 40:
        errors.append(f"draft count {len(drafts)} < 40")

    for path in drafts:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            errors.append(f"{path.name}: missing front matter")
            continue
        parts = text.split("---", 2)
        fm, body = parts[1], parts[2]
        fields: dict[str, str] = {}
        for line in fm.strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip()
        for key in REQUIRED:
            if key not in fields:
                errors.append(f"{path.name}: missing {key}")
        if fields.get("status") != "staged":
            errors.append(f"{path.name}: status is {fields.get('status')!r}")
        if fields.get("series") != "fig-mediterranean-foodways":
            errors.append(f"{path.name}: bad series")
        if fields.get("claims_policy") != "no-medical":
            errors.append(f"{path.name}: claims_policy")
        ident = fields.get("id", "")
        slug = fields.get("slug", "")
        if ident in ids:
            errors.append(f"duplicate id {ident}")
        if slug in slugs:
            errors.append(f"duplicate slug {slug}")
        ids.add(ident)
        slugs.add(slug)
        if ident and f"## {ident}" not in img:
            errors.append(f"{ident}: missing IMAGE_SOURCES block")
        if rights.is_file() and ident and f"`{ident}`" not in rights_text:
            errors.append(f"{ident}: missing RIGHTS.md row")
        if FIGURE_MARKER not in body or "<figure" not in body or "<figcaption" not in body:
            errors.append(f"{path.name}: missing SEO hero figure")
        low = body.lower()
        for term in SLOP:
            if term in low:
                errors.append(f"{path.name}: slop {term!r}")
        for term in MED:
            if term in low:
                errors.append(f"{path.name}: medical-term {term!r}")
        words = body_words(body)
        if words < 220:
            errors.append(f"{path.name}: too thin ({words} words)")
        themes = fields.get("themes", "")
        for theme in re.findall(r"[a-z-]+", themes):
            theme_counter[theme] += 1
        rows.append(
            {
                "file": path.name,
                "id": ident,
                "title": fields.get("title", "").strip('"'),
                "words": words,
                "themes": themes,
                "region": fields.get("region", "").strip('"'),
            }
        )

    man_files = {item["file"] for item in man["drafts"]}
    disk_files = {path.name for path in drafts}
    if man_files != disk_files:
        errors.append(f"manifest mismatch {man_files ^ disk_files}")
    if man.get("draft_count") != len(drafts):
        errors.append("manifest draft_count")
    for theme in ("drying", "markets", "feast", "regional-dish"):
        if theme_counter[theme] < 8:
            errors.append(f"theme {theme} only {theme_counter[theme]}")

    words = [row["words"] for row in rows]
    print(f"drafts={len(drafts)}")
    print(f"words_total={sum(words) if words else 0}")
    print(f"words_min={min(words) if words else 0}")
    print(f"words_median={sorted(words)[len(words)//2] if words else 0}")
    print(f"words_max={max(words) if words else 0}")
    print(f"themes={dict(theme_counter)}")
    print(f"errors={len(errors)}")
    for err in errors:
        print(f"ERROR {err}")
    if errors:
        return 1
    print("OK staged series passes desk check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
