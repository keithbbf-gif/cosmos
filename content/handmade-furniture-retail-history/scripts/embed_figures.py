#!/usr/bin/env python3
"""Insert <figure> blocks into staged drafts from image_assets.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"
ASSETS = json.loads((ROOT / "image_assets.json").read_text(encoding="utf-8"))
BY_ID = {a["draft_id"]: a for a in ASSETS}

FIGURE_RE = re.compile(r"<figure>.*?</figure>\s*", re.DOTALL | re.IGNORECASE)


def figure_html(asset: dict) -> str:
    return (
        "<figure>\n"
        f'<img src="../images/{asset["file"]}" alt="{asset["alt"]}" width="1200" loading="lazy">\n'
        f"<figcaption>{asset['figcaption']}</figcaption>\n"
        "</figure>\n\n"
    )


def main() -> int:
    updated = 0
    for path in sorted(DRAFTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        m = re.search(r"^id:\s*(\S+)", text, re.MULTILINE)
        if not m:
            print("skip no id", path.name)
            continue
        draft_id = m.group(1)
        asset = BY_ID.get(draft_id)
        if not asset:
            print("skip no asset", draft_id)
            continue
        block = figure_html(asset)
        if FIGURE_RE.search(text):
            text = FIGURE_RE.sub(block, text, count=1)
        else:
            end = text.find("\n---\n", 4)
            if end < 0:
                print("skip bad frontmatter", path.name)
                continue
            insert_at = end + 5
            text = text[:insert_at] + "\n" + block + text[insert_at:].lstrip("\n")
        path.write_text(text, encoding="utf-8")
        updated += 1
    print(f"updated {updated} drafts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
