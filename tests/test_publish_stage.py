#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic stage of the MOTIF pack. No network. No live Core."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_publish_stage import stage  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_pub_"))
    src = td / "docs" / "publish"
    dest = td / "live" / "publish"
    src.mkdir(parents=True)
    for rel in (
        "README.md", "MOTIF_WHITEPAPER.md", "MOTIF_WHITEPAPER.pdf",
        "MOTIF_X.md", "MOTIF_LINKEDIN.md",
        "arxiv/motif_swiss_cheese.tex", "arxiv/motif_swiss_cheese.pdf",
    ):
        p = src / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"staged\n")

    def refuse():
        try:
            stage(td)
        except RuntimeError as e:
            return "refusing mkdir" in str(e)
        return False

    check("refuses to mkdir live/publish", refuse)
    dest.mkdir(parents=True)
    rec = stage(td)
    check("publish flag is false", lambda: rec.get("publish") is False)
    check("dest is staged", lambda: rec.get("dest") == "staged")
    check("manifest written", lambda: (dest / "STAGED_MANIFEST.json").is_file())
    check("whitepaper copied",
          lambda: (dest / "MOTIF_WHITEPAPER.md").read_bytes() == b"staged\n")
    man = json.loads((dest / "STAGED_MANIFEST.json").read_text(encoding="utf-8"))
    check("manifest n matches rows", lambda: man["n"] == len(man["rows"]))

    failed = 0
    for label, ok, err in RESULTS:
        mark = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print("%s %s %s" % (mark, label, err))
    print("result %d/%d" % (len(RESULTS) - failed, len(RESULTS)))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
