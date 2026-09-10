#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P02 peeking ban. Sibling read refuses; own workspace still works.

    py -3.14 cosmos/_bite_p02_peeking.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cosmos_peeking import (  # noqa: E402
    PeekingError, assert_no_peek, assert_prompt_no_peek, refuse_ballot,
)

OUT = HERE / "_bite_p02_peeking.json"


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_p02_"))
    a = td / "A"
    b = td / "B"
    a.mkdir()
    b.mkdir()
    own = a / "ok.txt"
    sib = b / "secret.txt"
    own.write_text("a", encoding="utf-8")
    sib.write_text("b", encoding="utf-8")

    assert_no_peek(a, own, b)
    peek = None
    try:
        assert_no_peek(a, sib, b)
    except PeekingError as e:
        peek = e.kind
    prompt = None
    try:
        assert_prompt_no_peek(f"read {sib.resolve()}", b)
    except PeekingError as e:
        prompt = e.kind
    ballot = None
    try:
        refuse_ballot()
    except PeekingError as e:
        ballot = e.kind

    rec = {
        "own_allowed": True,
        "sibling_path_kind": peek,
        "sibling_prompt_kind": prompt,
        "no_ballot_kind": ballot,
        "lanes_distinct": a.resolve() != b.resolve(),
    }
    rec["all_bite"] = (
        rec["own_allowed"] is True
        and rec["sibling_path_kind"] == "PEEKING_VIOLATION"
        and rec["sibling_prompt_kind"] == "PEEKING_VIOLATION"
        and rec["no_ballot_kind"] == "NO_BALLOT_WRITER"
        and rec["lanes_distinct"] is True
    )
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
