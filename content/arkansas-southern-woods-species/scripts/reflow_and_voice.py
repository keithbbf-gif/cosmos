#!/usr/bin/env python3
"""One-shot editor utilities: reflow wrapped paragraphs, set voice_check."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BAN_REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"\bit is a landscape property\b", re.I),
        "it is a place property",
    ),
    (
        re.compile(r"\bexample in a landscape of unnamed ones\b"),
        "example among unnamed ones",
    ),
    (
        re.compile(r"\bfull of leverage\b"),
        "full of racking stress",
    ),
]


def reflow_paragraph(block: str) -> str:
    lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
    if not lines:
        return ""
    out = lines[0]
    for nxt in lines[1:]:
        if out.endswith("-") and nxt and nxt[0].islower():
            out = out[:-1] + nxt
        else:
            out = f"{out} {nxt}"
    return out


def reflow_body(body: str) -> str:
    body = body.strip("\n")
    if not body.strip():
        return "\n"
    parts = re.split(r"\n\s*\n", body)
    reflowed = [reflow_paragraph(p) for p in parts]
    return "\n\n".join(reflowed) + "\n"


def patch_frontmatter(fm: str) -> str:
    if "voice_check:" in fm:
        fm = re.sub(r"voice_check:\s*\S+", "voice_check: edited", fm)
    else:
        fm = fm.rstrip("\n") + "\nvoice_check: edited\n"
    return fm


def apply_bans(text: str) -> str:
    for pat, repl in BAN_REPLACEMENTS:
        text = pat.sub(repl, text)
    return text


def process(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise ValueError(f"{path.name}: missing frontmatter")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path.name}: bad frontmatter")
    fm, body = parts[1], parts[2]
    fm = patch_frontmatter(fm)
    body = apply_bans(reflow_body(body))
    return f"---{fm}---\n{body}"


def main() -> int:
    paths = sorted(ROOT.glob("[0-9]*.md"))
    if len(paths) != 46:
        print(f"expected 46 drafts, found {len(paths)}", file=sys.stderr)
        return 1
    for path in paths:
        path.write_text(process(path), encoding="utf-8")
    print(f"reflowed {len(paths)} drafts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
