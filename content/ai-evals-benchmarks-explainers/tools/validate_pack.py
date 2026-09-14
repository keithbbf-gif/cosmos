#!/usr/bin/env python3
"""Validate the staged AI evals explainer pack.

Checks article count, unique slugs, required YAML fields, novelty leaks,
and a short list of banned narrator habits. Paper-title exceptions are
allowed via a small allowlist of lines that contain those titles.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_DIRS = [ROOT / "essays", ROOT / "explainers"]

REQUIRED = ("voice_check", "title", "slug", "kind", "era", "tags")
LEAK = re.compile(
    r"\b(COSMOS|KMesh|ModelRater|cDeck|KDash|OpenWork|Gitur|Crucible|"
    r"ThinkFast|USPTO|patent docket|porosity tensor|fencing token)\b",
    re.I,
)
BANNED_NARRATOR = re.compile(
    r"\b(delve|leverage|seamless|tapestry)\b|"
    r"in today's rapidly evolving|"
    r"let's dive in|"
    r"buckle up|"
    r"it is important to note|"
    r"whether you're a student",
    re.I,
)
FM = re.compile(r"^---\n(.*?)\n---\n", re.S)
FIGURE = re.compile(r"<figure>\s*<img\s+[^>]*src=\"([^\"]+)\"[^>]*/>\s*<figcaption>", re.S)


def parse_front_matter(text: str) -> dict[str, str]:
    m = FM.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def word_count(text: str) -> int:
    body = FM.sub("", text)
    return len(re.findall(r"\b[\w']+\b", body))


def main() -> int:
    files = sorted(p for d in ARTICLE_DIRS for p in d.glob("*.md"))
    errors: list[str] = []
    slugs: dict[str, Path] = {}
    kinds = {"essay": 0, "explainer": 0}

    if len(files) < 40:
        errors.append(f"article count {len(files)} < 40")

    for path in files:
        text = path.read_text(encoding="utf-8")
        fm = parse_front_matter(text)
        for key in REQUIRED:
            if key not in fm:
                errors.append(f"{path.name}: missing {key}")
        if fm.get("voice_check") != "human":
            errors.append(f"{path.name}: voice_check is not human")
        slug = fm.get("slug", "")
        if slug in slugs:
            errors.append(f"duplicate slug {slug}: {slugs[slug].name} / {path.name}")
        elif slug:
            slugs[slug] = path
        kind = fm.get("kind", "")
        if kind in kinds:
            kinds[kind] += 1
        else:
            errors.append(f"{path.name}: bad kind {kind!r}")
        wc = word_count(text)
        if wc < 700:
            errors.append(f"{path.name}: word count {wc} < 700")
        if path.parent.name in {"essays", "explainers"}:
            figs = FIGURE.findall(text)
            if not figs:
                errors.append(f"{path.name}: missing <figure> with SEO figcaption")
            for src in figs:
                asset = (path.parent / src).resolve()
                if not asset.is_file():
                    errors.append(f"{path.name}: missing asset {src}")
        for i, line in enumerate(text.splitlines(), 1):
            if path.parent.name in {"essays", "explainers"} and LEAK.search(line):
                errors.append(f"{path.name}:{i}: novelty leak: {line.strip()[:120]}")
            if BANNED_NARRATOR.search(line) and "MMLU-Pro:" not in line:
                errors.append(f"{path.name}:{i}: banned diction: {line.strip()[:120]}")

    print(f"articles={len(files)} essays={kinds['essay']} explainers={kinds['explainer']}")
    print(f"unique_slugs={len(slugs)}")
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
