#!/usr/bin/env python3
"""Editor pass: voice_check stamp and humanize dXX backtick refs."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
REF_RE = re.compile(r"`d(\d{2})`")


def load_titles() -> dict[str, str]:
    titles: dict[str, str] = {}
    for path in sorted(DRAFTS.glob("d*.md")):
        text = path.read_text(encoding="utf-8")
        m = FM_RE.match(text)
        if not m:
            continue
        fm = m.group(1)
        id_m = re.search(r"^id:\s*(\S+)", fm, re.M)
        title_m = re.search(r"^title:\s*(.+)$", fm, re.M)
        if id_m and title_m:
            titles[id_m.group(1)] = title_m.group(1).strip()
    return titles


def essay_ref(did: str, titles: dict[str, str]) -> str:
    key = f"d{int(did):02d}"
    title = titles.get(key)
    if not title:
        return f"`d{did}`"
    return f"*{title}* (essay {int(did)})"


def humanize_refs(text: str, titles: dict[str, str]) -> str:
    return REF_RE.sub(lambda m: essay_ref(m.group(1), titles), text)


def add_voice_check(text: str) -> str:
    if "voice_check:" in text.split("---", 2)[1]:
        return re.sub(r"^voice_check:.*$", "voice_check: edited", text, count=1, flags=re.M)
    return text.replace("voice: human\n", "voice: human\nvoice_check: edited\n", 1)


def main() -> None:
    titles = load_titles()
    changed = 0
    for path in sorted(DRAFTS.glob("d*.md")):
        original = path.read_text(encoding="utf-8")
        updated = add_voice_check(humanize_refs(original, titles))
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"updated {changed} drafts; titles loaded: {len(titles)}")


if __name__ == "__main__":
    main()
