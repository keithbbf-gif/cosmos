#!/usr/bin/env python3
"""QA for content/ai-safety-public-discourse — run from repo root or this folder."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERIES = "ai-safety-public-discourse"
NUMBERED = [f"{i:02d}" for i in range(1, 53)]

BANNED = re.compile(
    r"\b("
    r"delve|leverage|unlock|cutting-edge|game-changer|"
    r"Moreover|Whether you're|In conclusion|It's important to note|"
    r"In today's|At the end of the day|rich tapestry|paradigm shift|"
    r"democratize|seamless|holistic|unpack|revolution|journey|"
    r"elevate|empower"
    r")\b",
    re.I,
)
HOUSE = re.compile(r"\b(COSMOS|KMesh|OpenWork|KDash|BUCm)\b", re.I)
WORD_RE = re.compile(r"[A-Za-z0-9']+")
BODY_BAND = (280, 850)
FOOTER = (
    "This piece does not propose a new method, a new policy instrument, "
    "or a new research result."
)


def body_words(text: str) -> int:
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"\*\*Stage:\*\*.*", "", text, flags=re.S)
    return len(WORD_RE.findall(text))


def main() -> int:
    errors: list[str] = []
    all_md = sorted(ROOT.glob("*.md"))
    if len(all_md) < 58:
        errors.append(f"expected 58 markdown files, found {len(all_md)}")

    meta = {"README.md", "INDEX.md", "MANIFEST.md", "SOURCES.md", "EDITOR_REPORT.md"}
    for path in all_md:
        raw = path.read_text(encoding="utf-8")
        if "voice_check: edited" not in raw:
            errors.append(f"{path.name}: voice_check not edited")
        if path.name in meta and f"series: {SERIES}" not in raw:
            errors.append(f"{path.name}: series mismatch")
        if path.name not in meta:
            if HOUSE.search(raw):
                errors.append(f"{path.name}: house or COSMOS mention")
            hits = sorted(set(BANNED.findall(raw)))
            if hits:
                errors.append(f"{path.name}: banned {hits}")

    rows: list[tuple[str, int]] = []
    for seq in ["00"] + NUMBERED:
        matches = list(ROOT.glob(f"{seq}-*.md"))
        if len(matches) != 1:
            errors.append(f"sequence {seq}: expected one file, got {len(matches)}")
            continue
        path = matches[0]
        raw = path.read_text(encoding="utf-8")
        if f"series: {SERIES}" not in raw:
            errors.append(f"{path.name}: series mismatch")
        if "stage: draft" not in raw:
            errors.append(f"{path.name}: stage not draft")
        if "novelty: public-record-only" not in raw:
            errors.append(f"{path.name}: novelty tag missing")
        if FOOTER not in raw:
            errors.append(f"{path.name}: missing novelty footer")
        n = body_words(raw)
        rows.append((path.name, n))
        if not (BODY_BAND[0] <= n <= BODY_BAND[1]):
            errors.append(f"{path.name}: {n} body words outside {BODY_BAND[0]}–{BODY_BAND[1]}")

    report = ROOT / "EDITOR_REPORT.md"
    if not report.is_file():
        errors.append("EDITOR_REPORT.md missing")

    print(f"numbered drafts: {len(rows)} (want {1 + len(NUMBERED)})")
    print(f"total body words (00 + 01–52): {sum(n for _, n in rows)}")
    for name, n in rows:
        print(f"  {n:4}  {name}")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
