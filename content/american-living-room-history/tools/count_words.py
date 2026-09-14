#!/usr/bin/env python3
"""Count body words in a series draft (tokens after YAML, before Sources)."""
from __future__ import annotations

import pathlib
import re
import sys

TOKEN = re.compile(r"[A-Za-z0-9']+")


def body_words(text: str) -> int:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]
    lower = text.lower()
    cut = len(text)
    for marker in ("\n## Sources\n", "\n## Sources\r\n"):
        i = lower.find(marker.strip().lower())
        # find heading
    m = re.search(r"^## Sources\s*$", text, re.M)
    if m:
        text = text[: m.start()]
    return len(TOKEN.findall(text))


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1] / "drafts"
    files = sorted(root.glob("*.md"))
    if not files:
        print("no drafts", file=sys.stderr)
        return 1
    rows = []
    for path in files:
        n = body_words(path.read_text(encoding="utf-8"))
        rows.append((n, path.name))
        flag = "OK" if 1400 <= n <= 2200 else "OUT"
        print(f"{n:5d}  {flag:3s}  {path.name}")
    print(f"count={len(rows)} total={sum(r[0] for r in rows)}")
    bad = [r for r in rows if not (1400 <= r[0] <= 2200)]
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
