#!/usr/bin/env python3
"""Editorial QA for the herbal-medicine-history-blog pack. Not a site runtime."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"
REQUIRED_ROOT = [
    "INDEX.md",
    "STYLE_GUIDE.md",
    "BIBLIOGRAPHY.md",
    "CLAIMS_GUARDRAILS.md",
    "PHOTO_NOTES.md",
    "WP_IMPORT.md",
    "README.md",
]
FM_KEYS = [
    "voice_check",
    "title",
    "slug",
    "summary",
    "tags",
    "sources_notes",
    "legal_frame",
]
BANNED = re.compile(
    r"delve|leverage|\brobust\b|seamless|tapestry|underscore|"
    r"ever-evolving|rapidly evolving|it's important to note|"
    r"it is important to note|needless to say|whether you're|"
    r"in today's world|multifaceted|unpack the|navigate the complexities",
    re.I,
)
SOFT_FLOOR = 650


def strip_fm(text: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, m.group(2)


def main() -> int:
    errors = []
    notes = []
    for name in REQUIRED_ROOT:
        if not (ROOT / name).is_file():
            errors.append(f"missing root file: {name}")

    drafts = sorted(DRAFTS.glob("*.md"))
    if len(drafts) < 40:
        errors.append(f"draft count {len(drafts)} < 40")
    slugs = []
    words = []
    for path in drafts:
        text = path.read_text(encoding="utf-8")
        fm, body = strip_fm(text)
        for key in FM_KEYS:
            if key not in fm:
                errors.append(f"{path.name}: missing {key}")
        vc = fm.get("voice_check")
        if vc not in ("human", "edited"):
            errors.append(f"{path.name}: voice_check must be human or edited (got {vc!r})")
        if fm.get("legal_frame") != "historical-educational":
            errors.append(f"{path.name}: legal_frame not historical-educational")
        if "**Photo:**" not in body:
            errors.append(f"{path.name}: missing photo slot")
        slug = fm.get("slug", "").strip("\"'")
        if slug:
            slugs.append((slug, path.name))
        w = len(body.split())
        words.append((w, path.name))
        if w < SOFT_FLOOR:
            errors.append(f"{path.name}: {w} words < {SOFT_FLOOR} stub floor")
        hit = BANNED.search(body)
        if hit:
            errors.append(f"{path.name}: banned phrase {hit.group(0)!r}")

    seen = {}
    for slug, name in slugs:
        if slug in seen:
            errors.append(f"duplicate slug {slug}: {seen[slug]} and {name}")
        seen[slug] = name

    if words:
        ws = [w for w, _ in words]
        notes.append(f"drafts={len(drafts)}")
        notes.append(f"word_min={min(ws)} ({min(words)[1]})")
        notes.append(f"word_max={max(ws)} ({max(words)[1]})")
        notes.append(f"word_mean={sum(ws)//len(ws)}")
        notes.append(f"slugs={len(seen)}")

    print("PACK QA")
    for n in notes:
        print(f"  {n}")
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
