#!/usr/bin/env python3
"""Count, weigh, and sniff the staged essays. Not a truth gate."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"

# Surface-level slop and unguarded medical voice. False positives are fine;
# a hit is a place a human should look, not an automatic fail.
SLOP = [
    r"\brich tapestry\b",
    r"\bsince ancient times\b",
    r"\bit is important to note\b",
    r"\bin this article we\b",
    r"\bdive into\b",
    r"\bunleash\b",
    r"\bthe test of time\b",
    r"\bholistic wellness\b",
]
# Unguarded clinical verbs aimed at a reader. Allow "the text claims".
UNGUARDED = [
    r"\bthis herb (cures|treats|prevents|heals)\b",
    r"\brecommended dose\b",
    r"\btake \d+ (g|mg|grams)\b",
    r"\bconsult your doctor\b",
]

FRONT = re.compile(r"^---\n(.*?)\n---", re.S)


def words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9’'-]+", text))


def main() -> int:
    files = sorted(DRAFTS.rglob("*.md"))
    if not files:
        print("no drafts", file=sys.stderr)
        return 2

    rows = []
    problems = []
    for path in files:
        raw = path.read_text(encoding="utf-8")
        m = FRONT.match(raw)
        if not m:
            problems.append(f"{path}: missing frontmatter")
            continue
        fm = m.group(1)
        body = raw[m.end() :]
        fields = dict(re.findall(r"^([a-z_]+):\s*(.+)$", fm, re.M))
        for req in ("id", "title", "stage", "status", "sequence"):
            if req not in fields:
                problems.append(f"{path}: missing {req}")
        if fields.get("status") != "draft":
            problems.append(f"{path}: status is {fields.get('status')!r}, expected draft")
        wc = words(body)
        if wc < 400:
            problems.append(f"{path}: thin ({wc} words)")
        blob = body.lower()
        for pat in SLOP + UNGUARDED:
            if re.search(pat, blob):
                problems.append(f"{path}: sniff {pat}")
        if "## claims i am not making" not in blob:
            problems.append(f"{path}: missing claims-refusal section")
        if "## open questions" not in blob:
            problems.append(f"{path}: missing open questions")
        rows.append((int(fields.get("sequence", "0") or 0), path, wc, fields.get("id")))

    rows.sort()
    total = sum(r[2] for r in rows)
    print(f"essays: {len(rows)}")
    print(f"words:  {total}")
    print(f"median: {sorted(r[2] for r in rows)[len(rows)//2]}")
    print()
    for seq, path, wc, eid in rows:
        print(f"{seq:02d}  {wc:4d}  {eid}  {path.relative_to(ROOT)}")
    print()
    if problems:
        print("sniffs / defects:")
        for p in problems:
            print(" -", p)
        return 1
    print("structure ok (still drafts; not a truth gate)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
