#!/usr/bin/env python3
"""Sync staged-embeds and drafts with <figure> blocks from figure_registry.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "figure_registry.json").read_text(encoding="utf-8"))
MARKER = REGISTRY["marker"]
ASSETS = REGISTRY["assets"]
DRAFT_MAP = REGISTRY["drafts"]

FIGURE_BLOCK = re.compile(
    rf"{re.escape(MARKER)}\s*<figure[\s\S]*?</figure>\s*",
    re.IGNORECASE,
)
LEGACY_MD = re.compile(
    r"!\[[^\]]*\]\(\.\./assets/[^)]+\)\s*\n\*Figure \d+[^*]*\*\s*\n",
    re.MULTILINE,
)


def resolve_entry(entry: str | dict) -> tuple[dict, str]:
    if isinstance(entry, str):
        asset = ASSETS[entry]
        return asset, asset["caption"]
    asset = ASSETS[entry["asset"]]
    cap = entry.get("caption", asset["caption"])
    return asset, cap


def figure_html(asset: dict, caption: str) -> str:
    return (
        f"{MARKER}\n"
        '<figure class="oss-stack-figure">\n'
        f'<img src="{asset["file"]}" alt="{asset["alt"]}" '
        f'width="{asset["width"]}" height="{asset["height"]}" '
        f'loading="lazy" decoding="async" />\n'
        f"<figcaption>{caption}</figcaption>\n"
        "</figure>\n"
    )


def strip_figures(text: str) -> str:
    text = FIGURE_BLOCK.sub("", text)
    text = LEGACY_MD.sub("", text)
    return text


def lede_insert_pos(body: str) -> int:
    """Byte offset after the opening H1 lede (before the next heading)."""
    body = body.lstrip("\n")
    if not body.startswith("# "):
        return 0
    i = 0
    while i < len(body) and body[i] != "\n":
        i += 1
    i += 1
    while i < len(body) and body[i] in "\n\r":
        i += 1
    while i < len(body) and not body[i : i + 1] == "#":
        nxt = body.find("\n", i)
        if nxt < 0:
            return len(body)
        line = body[i:nxt]
        if line.startswith("#"):
            break
        i = nxt + 1
    return i


def embed_block(slug: str) -> str:
    entries = DRAFT_MAP.get(slug, [])
    parts: list[str] = []
    for entry in entries:
        asset, caption = resolve_entry(entry)
        parts.append(figure_html(asset, caption))
    return "\n".join(parts).rstrip() + ("\n" if parts else "")


def patch_draft(path: Path, slug: str) -> bool:
    entries = DRAFT_MAP.get(slug)
    if not entries:
        return False
    raw = path.read_text(encoding="utf-8")
    fm_m = re.match(r"^(---\n.*?\n---\n)", raw, re.S)
    if not fm_m:
        raise SystemExit(f"no front matter: {path}")
    fm = fm_m.group(1)
    body = strip_figures(raw[len(fm) :]).lstrip("\n")
    block = embed_block(slug)
    pos = lede_insert_pos(body)
    body = body[:pos] + block + "\n" + body[pos:].lstrip("\n")
    new_text = fm + body
    if new_text == raw:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def write_staged(slug: str) -> None:
    out = ROOT / "staged-embeds" / f"{slug}.md"
    out.write_text(embed_block(slug), encoding="utf-8")


def main() -> int:
    updated = 0
    for slug in DRAFT_MAP:
        write_staged(slug)
        path = ROOT / "drafts" / f"{slug}.md"
        if path.exists() and patch_draft(path, slug):
            updated += 1
    print(f"staged-embeds: {len(DRAFT_MAP)}")
    print(f"drafts patched: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
