#!/usr/bin/env python3
"""Quality gate for the table-extension draft series. Exit 1 on fail."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_DRAFTS = 40
MIN_WORDS = 280
REQUIRED_FM = ("series", "id", "slug", "title", "stage", "status", "voice")
SLOP = (
    "in today's world",
    "it is important to note",
    "delve",
    "tapestry",
    "multifaceted",
    "in conclusion",
    "unlock the potential",
    "in the realm of",
    "moreover,",
    "furthermore,",
    "a testament to",
)

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def parse(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text()
    m = FM_RE.match(text)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, text[m.end() :]


def drafts() -> list[Path]:
    return sorted(
        p
        for p in ROOT.rglob("*.md")
        if p.parent.name.startswith("stage-") and p.name[0].isdigit()
    )


def main() -> int:
    files = drafts()
    fails: list[str] = []
    if len(files) < MIN_DRAFTS:
        fails.append(f"draft count {len(files)} < {MIN_DRAFTS}")

    ids = []
    slugs = []
    titles = []
    openings = []
    words_by = []
    stages = Counter()

    for path in files:
        fm, body = parse(path)
        for key in REQUIRED_FM:
            if key not in fm:
                fails.append(f"{path.name}: missing {key}")
        if fm.get("status") != "draft":
            fails.append(f"{path.name}: status is {fm.get('status')!r} not draft")
        if fm.get("voice") != "human":
            fails.append(f"{path.name}: voice is {fm.get('voice')!r} not human")
        if fm.get("series") != "table-extension-mechanisms":
            fails.append(f"{path.name}: bad series")
        ids.append(fm.get("id", path.name))
        slugs.append(fm.get("slug", path.name))
        titles.append(fm.get("title", path.name))
        stages[fm.get("stage", path.parent.name)] += 1
        words = len(body.split())
        words_by.append((path.name, words, fm.get("title", "")))
        if words < MIN_WORDS:
            fails.append(f"{path.name}: {words} words < {MIN_WORDS}")
        low = body.lower()
        for phrase in SLOP:
            if phrase in low:
                fails.append(f"{path.name}: slop {phrase!r}")
        paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip() and not p.strip().startswith("#")]
        if paras:
            openings.append(" ".join(paras[0].split()[:10]))
        else:
            fails.append(f"{path.name}: no opening paragraph")

    if len(set(ids)) != len(ids):
        fails.append(f"duplicate ids: {Counter(ids)}")
    if len(set(slugs)) != len(slugs):
        fails.append("duplicate slugs")
    if len(set(titles)) != len(titles):
        fails.append("duplicate titles")
    if len(set(openings)) != len(openings):
        fails.append("duplicate openings")

    map_text = (ROOT / "00-series-map.md").read_text()
    for path in files:
        fm, _ = parse(path)
        if fm.get("id") and f'| {int(fm["id"]):02d} |' not in map_text and f'| {fm["id"]} |' not in map_text:
            # ids in map are unpadded (01 style in table as 01)
            if f"| {fm['id']} |" not in map_text:
                fails.append(f"id {fm.get('id')} missing from series map")
        rel = str(path.relative_to(ROOT))
        if rel not in map_text:
            fails.append(f"path {rel} missing from series map")

    print(f"drafts={len(files)}")
    print(f"unique_ids={len(set(ids))}")
    print(f"unique_openings={len(set(openings))}")
    print(f"total_words={sum(w for _, w, _ in words_by)}")
    print("stages=" + ", ".join(f"{k}:{v}" for k, v in sorted(stages.items())))
    print("shortest:")
    for name, w, title in sorted(words_by, key=lambda x: x[1])[:8]:
        print(f"  {w:4d}  {name}  {title}")
    print("longest:")
    for name, w, title in sorted(words_by, key=lambda x: -x[1])[:5]:
        print(f"  {w:4d}  {name}  {title}")
    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
