#!/usr/bin/env python3
"""Recount body words, check staged YAML, banned voice, and coverage."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"

BANNED = re.compile(
    r"\b(delve|robust|leverage|unlock|cutting-edge|game-changer|"
    r"moreover|furthermore|key takeaway|let'?s dive|"
    r"in conclusion|at the end of the day)\b|"
    r"in today'?s|in an era of|it'?s important to note|"
    r"whether you'?re a beginner|this article will explore|"
    r"not only .+ but also",
    re.I,
)

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
WC_RE = re.compile(r"^word_count:\s*\d+\s*$", re.M)

REQUIRED = (
    "id:",
    "title:",
    "slug:",
    "status: staged",
    "stage:",
    "voice: human",
    "voice_check:",
    "cluster:",
    "series: gluing-clamping-furniture",
    "dek:",
    "word_count:",
)


def body_words(text: str) -> int:
    m = FM_RE.match(text)
    body = text[m.end() :] if m else text
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    body = re.sub(r"`[^`]+`", " ", body)
    return len(re.findall(r"[A-Za-z0-9']+", body))


def main() -> int:
    files = sorted(DRAFTS.glob("d*.md"))
    errors: list[str] = []
    rows: list[tuple[str, int, str, str]] = []
    if len(files) < 40:
        errors.append(f"draft count {len(files)} < 40")

    for path in files:
        text = path.read_text(encoding="utf-8")
        if not FM_RE.match(text):
            errors.append(f"{path.name}: missing YAML front matter")
            continue
        fm = FM_RE.match(text).group(1)
        for req in REQUIRED:
            if req not in fm and not (req.endswith(":") and any(line.startswith(req) for line in fm.splitlines())):
                if req not in text.split("---", 2)[1]:
                    errors.append(f"{path.name}: missing {req}")
        if "status: staged" not in fm:
            errors.append(f"{path.name}: status is not staged")
        if "voice: human" not in fm:
            errors.append(f"{path.name}: voice is not human")
        if "voice_check: edited" not in fm and "voice_check: human" not in fm:
            errors.append(f"{path.name}: missing voice_check (edited or human)")
        n = body_words(text)
        if n < 680:
            errors.append(f"{path.name}: short body ({n} words)")
        new = WC_RE.sub(f"word_count: {n}", text, count=1)
        if new != text:
            path.write_text(new, encoding="utf-8")
            text = new
        hit = BANNED.search(text.split("---", 2)[-1] if text.count("---") >= 2 else text)
        if hit:
            errors.append(f"{path.name}: banned phrase {hit.group(0)!r}")
        stage = re.search(r"^stage:\s*(\w+)", fm, re.M)
        slug = re.search(r"^slug:\s*(\S+)", fm, re.M)
        rows.append((path.name, n, stage.group(1) if stage else "?", slug.group(1) if slug else "?"))

    total = sum(r[1] for r in rows)
    print(f"drafts: {len(files)}")
    print(f"total_body_words: {total}")
    by = {}
    for _, n, stage, _ in rows:
        by[stage] = by.get(stage, 0) + 1
    print("by_stage:", by)
    for name, n, stage, slug in rows:
        print(f"  {name}\t{n}\t{stage}\t{slug}")
    if errors:
        print("ERRORS:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
