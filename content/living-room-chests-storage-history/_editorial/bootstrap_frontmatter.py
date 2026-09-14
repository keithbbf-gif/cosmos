#!/usr/bin/env python3
"""Add YAML frontmatter to object essays 05–29 if missing."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUGS = json.loads((ROOT / "writer-slugs.json").read_text(encoding="utf-8"))["slugs"]

FRONT = re.compile(r"^---\n.*?\n---\n", re.S)


def main() -> None:
    for slug in SLUGS:
        path = ROOT / f"{slug}.md"
        raw = path.read_text(encoding="utf-8")
        if FRONT.match(raw):
            continue
        title_m = re.search(r"^# (.+)$", raw, re.M)
        title = title_m.group(1).strip() if title_m else slug
        first_para = ""
        for line in raw.splitlines():
            if line.strip() and not line.startswith("#"):
                first_para = line.strip()
                break
        dek = first_para[:220] if first_para else title
        fm = (
            f"---\n"
            f"title: {title}\n"
            f"slug: {slug}\n"
            f"series: living-room-chests-storage-history\n"
            f"status: draft\n"
            f"voice_check: edited\n"
            f'dek: "{dek.replace(chr(34), chr(39))}"\n'
            f"---\n"
        )
        path.write_text(fm + raw, encoding="utf-8")
        print("frontmatter:", slug)


if __name__ == "__main__":
    main()
