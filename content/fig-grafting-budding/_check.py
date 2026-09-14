#!/usr/bin/env python3
"""Validate staged fig-grafting drafts. Authority is the files, not this script."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIN_DRAFTS = 40
MIN_WORDS = 420
REQUIRED = ("id", "title", "stage", "status", "zone", "voice", "kind")

FRONT = re.compile(r"^---\n(.*?)\n---\n", re.S)


def parse_front(text: str) -> dict[str, str]:
    m = FRONT.match(text)
    if not m:
        raise ValueError("missing YAML frontmatter")
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip("'\"")
    return out


def words(text: str) -> int:
    body = FRONT.sub("", text)
    return len(re.findall(r"[A-Za-z0-9']+", body))


def main() -> int:
    drafts = sorted(
        p
        for p in ROOT.glob("stage-*/*.md")
        if p.name != "README.md"
    )
    errors: list[str] = []
    ids: set[str] = set()
    titles: set[str] = set()

    if len(drafts) < MIN_DRAFTS:
        errors.append(f"draft count {len(drafts)} < {MIN_DRAFTS}")

    for path in drafts:
        text = path.read_text(encoding="utf-8")
        try:
            meta = parse_front(text)
        except ValueError as e:
            errors.append(f"{path.name}: {e}")
            continue
        for key in REQUIRED:
            if key not in meta:
                errors.append(f"{path.name}: missing {key}")
        if meta.get("status") != "staged":
            errors.append(f"{path.name}: status={meta.get('status')!r} (want staged)")
        if meta.get("zone") != "8a":
            errors.append(f"{path.name}: zone={meta.get('zone')!r} (want 8a)")
        if meta.get("voice") != "human":
            errors.append(f"{path.name}: voice={meta.get('voice')!r} (want human)")
        if meta.get("kind") != "draft":
            errors.append(f"{path.name}: kind={meta.get('kind')!r} (want draft)")
        folder_stage = path.parent.name.removeprefix("stage-")
        if meta.get("stage") and not folder_stage.startswith(str(meta["stage"])):
            errors.append(
                f"{path.name}: stage {meta.get('stage')!r} does not match folder {path.parent.name}"
            )
        did = meta.get("id", "")
        if did in ids:
            errors.append(f"duplicate id {did}")
        ids.add(did)
        title = meta.get("title", "")
        if title in titles:
            errors.append(f"duplicate title {title!r}")
        titles.add(title)
        n = words(text)
        if n < MIN_WORDS:
            errors.append(f"{path.name}: {n} words < {MIN_WORDS}")
        if "comprehensive guide" in text.lower():
            errors.append(f"{path.name}: banned phrase 'comprehensive guide'")
        if "unlock" in text.lower():
            errors.append(f"{path.name}: banned phrase 'unlock'")

    print(f"drafts={len(drafts)} min={MIN_DRAFTS} errors={len(errors)}")
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        return 1
    print("PASS staged Zone 8a fig grafting drafts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
