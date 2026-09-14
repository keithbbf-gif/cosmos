#!/usr/bin/env python3
"""Validate fig-history content pack figure embeds against GRAPHICS_INDEX.md."""

from __future__ import annotations

import re
import sys
from pathlib import Path

FIGURE_ID_RE = re.compile(r"figure-id:\s*([a-z0-9][a-z0-9.-]*)")
INDEX_ID_RE = re.compile(r"`([^`]+)`")


def load_index_ids(index_path: Path) -> set[str]:
    text = index_path.read_text(encoding="utf-8")
    ids: set[str] = set()
    for line in text.splitlines():
        if "| `" not in line:
            continue
        m = re.search(r"\|\s*`([^`]+)`\s*\|", line)
        if m:
            ids.add(m.group(1))
    return ids


def scan_articles(pack_root: Path) -> list[tuple[Path, str]]:
    found: list[tuple[Path, str]] = []
    articles = pack_root / "articles"
    if not articles.is_dir():
        return found
    for md in articles.rglob("*.md"):
        if md.name.startswith("_"):
            continue
        content = md.read_text(encoding="utf-8")
        for m in FIGURE_ID_RE.finditer(content):
            found.append((md, m.group(1)))
    return found


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: fig_graphics_validate.py <pack-root>", file=sys.stderr)
        return 2
    pack_root = Path(sys.argv[1]).resolve()
    index_path = pack_root / "GRAPHICS_INDEX.md"
    if not index_path.is_file():
        print(f"Missing {index_path}", file=sys.stderr)
        return 1

    registered = load_index_ids(index_path)
    embeds = scan_articles(pack_root)
    errors: list[str] = []

    for md, fig_id in embeds:
        if fig_id not in registered:
            errors.append(f"{md.relative_to(pack_root)}: unknown figure-id `{fig_id}`")

    # Warn on registered slug IDs never embedded (informational only)
    embedded_ids = {fid for _, fid in embeds}
    orphan_article_ids = [
        i
        for i in registered
        if not i.startswith("shared.") and i not in embedded_ids
    ]

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"OK: {len(embeds)} embed(s) across articles; {len(registered)} index IDs.")
    if orphan_article_ids:
        print(
            f"Note: {len(orphan_article_ids)} article-bound index IDs not yet embedded "
            "(expected while drafts land)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
