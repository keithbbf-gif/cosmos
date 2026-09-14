#!/usr/bin/env python3
"""Count body words after YAML, before ## Notes."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def body_words(text: str) -> tuple[int, str]:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    if "## Notes" in text:
        text = text.split("## Notes", 1)[0]
    words = re.findall(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*", text)
    return len(words), text


def main() -> None:
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        root = Path(__file__).resolve().parents[1] / "drafts"
        paths = sorted(root.glob("*.md"))
    rows = []
    for path in paths:
        n, _ = body_words(path.read_text())
        flag = "OK" if 1800 <= n <= 2800 else ("SHORT" if n < 1800 else "LONG")
        rows.append((path.name, n, flag))
        print(f"{path.name:48} {n:5d}  {flag}")
    if rows:
        print(f"\n{len(rows)} files")


if __name__ == "__main__":
    main()
