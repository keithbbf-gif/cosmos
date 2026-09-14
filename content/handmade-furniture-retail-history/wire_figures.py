#!/usr/bin/env python3
"""Insert or refresh <figure> blocks in staged drafts from images/registry.json."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "images" / "registry.json"
DRAFTS = ROOT / "drafts"
FIGURE_RE = re.compile(
    r"\n<figure class=\"hfrh-figure\">.*?</figure>\n",
    re.DOTALL,
)


def figure_html(spec: dict, figure_class: str) -> str:
    src = f"../images/{spec['file']}"
    alt = spec["alt"].replace('"', "&quot;")
    cap = spec["figcaption"]
    return (
        f'\n<figure class="{figure_class}">\n'
        f'  <img src="{src}" alt="{alt}" width="960" loading="lazy" decoding="async" />\n'
        f"  <figcaption>{cap}</figcaption>\n"
        f"</figure>\n"
    )


def insert_after_first_paragraph(body: str, block: str) -> str:
    body = FIGURE_RE.sub("\n", body)
    body = body.lstrip("\n")
    parts = body.split("\n\n", 1)
    if len(parts) == 1:
        return block + body
    return parts[0] + block + "\n\n" + parts[1]


def main() -> int:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    figure_class = reg.get("class", "hfrh-figure")
    errors: list[str] = []
    updated = 0
    for draft_name, spec in reg["drafts"].items():
        path = DRAFTS / draft_name
        if not path.exists():
            errors.append(f"missing draft {draft_name}")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"{draft_name}: no frontmatter")
            continue
        end = text.find("\n---\n", 4)
        if end < 0:
            errors.append(f"{draft_name}: bad frontmatter")
            continue
        head = text[: end + 5]
        body = text[end + 5 :]
        block = figure_html(spec, figure_class)
        new_body = insert_after_first_paragraph(body, block)
        if new_body != body:
            path.write_text(head + new_body, encoding="utf-8")
            updated += 1
    print(f"updated={updated} drafts")
    if errors:
        for err in errors:
            print(f"- {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
