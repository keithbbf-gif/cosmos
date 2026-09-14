#!/usr/bin/env python3
"""Insert captioned figure embeds and sync front matter `figures:` (idempotent)."""

from __future__ import annotations

import re
from pathlib import Path

from pack_data import EMBED_PLAN

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
MARKER = "<!-- graphics-pack:v1 -->"
FIG_BLOCK_RE = re.compile(
    r"\n<!-- graphics-pack:v1 -->(?:\n\n!\[[^\]]*\]\([^)]+\)\n\n\*[^*]+\*\n\n)+",
    re.MULTILINE,
)
FM_RE = re.compile(r"^---\n.*?\n---\n", re.MULTILINE | re.DOTALL)
FIGURES_FM_RE = re.compile(r"^figures:\s*\n(?:\s+-\s+.*\n)*", re.MULTILINE)


def block(figures: list[tuple[str, str, str]]) -> str:
    lines = [MARKER, ""]
    for path, alt, cap in figures:
        lines.append(f"![{alt}]({path})")
        lines.append("")
        lines.append(f"*{cap}*")
        lines.append("")
    return "\n".join(lines)


def sync_figures_front_matter(text: str, paths: list[str]) -> str:
    fm = FM_RE.match(text)
    if not fm:
        return text
    body = text[fm.end() :]
    front = fm.group(0)
    yaml_lines = ["figures:"]
    for p in paths:
        yaml_lines.append(f"  - {p}")
    yaml_lines.append("")
    new_block = "\n".join(yaml_lines)
    if FIGURES_FM_RE.search(front):
        front = FIGURES_FM_RE.sub(new_block, front, count=1)
    else:
        front = front[:-4] + new_block + "---\n"
    return front + body


def embed_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        text = FIG_BLOCK_RE.sub("", text)
    name = path.name
    plan = EMBED_PLAN.get(name, [])
    if not plan:
        return []
    all_paths: list[str] = []
    for heading, figures in reversed(plan):
        insert = block(figures)
        pattern = re.compile(rf"({re.escape(heading)}\n)")
        if not pattern.search(text):
            raise SystemExit(f"Heading not found in {name}: {heading}")
        text = pattern.sub(rf"\1\n{insert}\n", text, count=1)
        for rel, _, _ in figures:
            all_paths.append(rel)
    text = sync_figures_front_matter(text, list(dict.fromkeys(all_paths)))
    path.write_text(text, encoding="utf-8")
    return all_paths


def main() -> None:
    total_paths: list[str] = []
    for md in sorted(ARTICLES.glob("*.md")):
        total_paths.extend(embed_file(md))
    print(f"Embedded figures in {len(EMBED_PLAN)} articles ({len(total_paths)} paths)")


if __name__ == "__main__":
    main()
