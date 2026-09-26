#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Host-fill truncated WOMB drop Task fields from docs/WISHLIST.md.
Does not invent. Does not call a model. Pointer analog: WISHLIST is the source.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

WISHLIST = Path(r"V:\A\Ai\COSMOS\docs\WISHLIST.md")
DROP = Path(r"V:\A\Ai\COSMOS\work_orders\drop")


def _open_wishes(text: str) -> list[str]:
    chunks = re.split(r"\n(?=- \[[ xX]\])", text)
    out = []
    for c in chunks:
        c = c.strip()
        if c.startswith("- [ ]"):
            body = c[len("- [ ]"):].strip()
            body = re.sub(r"^(\*\*)(.+?)(\*\*)", r"\2", body, count=1)
            out.append("WISH: " + body)
    return out


def main() -> int:
    wishes = _open_wishes(WISHLIST.read_text(encoding="utf-8"))
    files = sorted(DROP.glob("wo-luna-wombat-*.json"))
    n = min(len(files), len(wishes))
    filled = 0
    for i in range(n):
        p = files[i]
        rec = json.loads(p.read_text(encoding="utf-8"))
        src = wishes[i]
        old = str(rec.get("Task") or "")
        if len(src) > len(old) + 20:
            rec["Task"] = src
            ctx = rec.get("Context source") or []
            if isinstance(ctx, list) and "docs/WISHLIST.md [read*]" not in ctx:
                rec["Context source"] = ["docs/WISHLIST.md [read*]"] + list(ctx)
            p.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8", newline="\n")
            filled += 1
    print(json.dumps({"ok": True, "drops": len(files), "wishes": len(wishes),
                      "filled": filled}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
