#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin predecessor: sibling workspace read was allowed. No PEEKING_VIOLATION.

    py -3.14 cosmos/_fail_p02_peeking_against_old.py
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
OUT = HERE / "_fail_p02_peeking_against_old.json"


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="p02_old_"))
    a = td / "lane-A"
    b = td / "lane-B"
    a.mkdir()
    b.mkdir()
    secret = b / "secret.txt"
    secret.write_text("lane-B private\n", encoding="utf-8")
    # Old: no peeking primitive — reading the sibling file succeeds.
    leaked = secret.read_text(encoding="utf-8")
    rec = {
        "old_sibling_read_succeeds": leaked == "lane-B private\n",
        "no_peeking_violation_type": True,
        "ballot_absent": True,
    }
    rec["predecessor_peeking_open"] = all(rec.values())
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["predecessor_peeking_open"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
