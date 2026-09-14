#!/usr/bin/env python3
"""QA for content/open-source-ai-history-2015-2026 — run from repo root or here."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
SLUGS = json.loads((ROOT / "writer-slugs.json").read_text())["draft_slugs"]

BANNED = re.compile(
    r"\b("
    r"delve|robust|leverage|unlock|cutting-edge|game-changer|"
    r"Moreover|Whether you're|In conclusion|It's important to note|"
    r"In today's|At the end of the day|rich tapestry|paradigm shift|"
    r"Cambrian|democratize|seamless|holistic|unpack|revolution|journey|"
    r"elevate|empower"
    r")\b",
    re.I,
)
WORD_RE = re.compile(r"[A-Za-z0-9']+")
BAND = (600, 1800)


def body_words(text: str) -> int:
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"^\*.*?\*$", "", text, flags=re.M)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.split(r"^## Sources", text, flags=re.M)[0]
    return len(WORD_RE.findall(text))


def main() -> int:
    errors: list[str] = []
    rows: list[tuple[str, int, str]] = []
    found = {p.stem for p in DRAFTS.glob("*.md")}
    missing = [s for s in SLUGS if s not in found]
    extra = sorted(found - set(SLUGS))
    if missing:
        errors.append(f"missing drafts: {missing}")
    if extra:
        errors.append(f"extra drafts: {extra}")

    for slug in SLUGS:
        path = DRAFTS / f"{slug}.md"
        if not path.exists():
            continue
        raw = path.read_text()
        if "COSMOS" in raw or re.search(r"\bcosmos\b", raw, re.I):
            errors.append(f"{slug}: COSMOS mention")
        if not raw.startswith("---"):
            errors.append(f"{slug}: no frontmatter")
        if "status: draft" not in raw:
            errors.append(f"{slug}: status not draft")
        if "voice_check: edited" not in raw:
            errors.append(f"{slug}: voice_check not edited")
        if f"slug: {slug}" not in raw:
            errors.append(f"{slug}: slug mismatch")
        if "series: open-source-ai-history-2015-2026" not in raw:
            errors.append(f"{slug}: series mismatch")
        if "## Sources" not in raw:
            errors.append(f"{slug}: no Sources")
        hits = sorted(set(BANNED.findall(raw)))
        if hits:
            errors.append(f"{slug}: banned {hits}")
        n = body_words(raw)
        title_m = re.search(r"^title:\s*(.*)$", raw, re.M)
        title = title_m.group(1).strip().strip('"') if title_m else slug
        rows.append((slug, n, title))
        if not (BAND[0] <= n <= BAND[1]):
            errors.append(f"{slug}: {n} words outside {BAND[0]}–{BAND[1]}")

    print(f"drafts: {len(rows)} (want {len(SLUGS)})")
    print(f"total body words: {sum(n for _, n, _ in rows)}")
    for i, (slug, n, title) in enumerate(rows, 1):
        print(f"{i:2} {n:5}  {slug}  — {title}")
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
