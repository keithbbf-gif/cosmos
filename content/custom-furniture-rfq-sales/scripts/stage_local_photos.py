#!/usr/bin/env python3
"""Copy pre-staged or duplicate local photos when Commons is shared."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

COPIES = [
    ("cf-rfq-07-kitchen-measure-prep.jpg", "cf-rfq-09-tape-measure-wall.jpg"),
    ("cf-rfq-07-kitchen-measure-prep.jpg", "cf-rfq-17-two-tapes-measure.jpg"),
]


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for src, dest in COPIES:
        s = ASSETS / src
        d = ASSETS / dest
        if not s.is_file():
            print("skip missing", src)
            continue
        shutil.copy2(s, d)
        print("copied", dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
