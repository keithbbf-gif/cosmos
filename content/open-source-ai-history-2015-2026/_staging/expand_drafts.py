#!/usr/bin/env python3
"""Insert unique expansions before ## Sources. Run from repo root."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "drafts"

# Each value is markdown inserted immediately before the Sources heading.
EXPAND: dict[str, str] = {}


def add(slug: str, text: str) -> None:
    EXPAND[slug] = text.strip() + "\n\n"


# Filled by subsequent exec of sibling fragments, or inline below.

def apply() -> None:
    for slug, block in EXPAND.items():
        path = ROOT / f"{slug}.md"
        text = path.read_text()
        needle = "## Sources"
        if needle not in text:
            raise SystemExit(f"no Sources in {slug}")
        if f"<!-- expanded:{slug} -->" in text:
            print("skip", slug)
            continue
        marked = f"<!-- expanded:{slug} -->\n\n{block}"
        text = text.replace(needle, marked + needle, 1)
        path.write_text(text)
        print("ok", slug)


if __name__ == "__main__":
    # import fragments
    from expand_part_a import EXPAND as A
    from expand_part_b import EXPAND as B
    from expand_part_c import EXPAND as C
    EXPAND.update(A)
    EXPAND.update(B)
    EXPAND.update(C)
    apply()
