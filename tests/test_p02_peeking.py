#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P02 peeking ban: sibling workspace read refuses. No ballot writer."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_dispatch_workspace import prepare_dual_lane_workspaces  # noqa: E402
from cosmos_peeking import (  # noqa: E402
    PeekingError, assert_no_peek, refuse_ballot,
)


def test_sibling_read_is_peeking_violation():
    td = Path(tempfile.mkdtemp(prefix="p02_"))
    a = td / "A"
    b = td / "B"
    a.mkdir()
    b.mkdir()
    secret = b / "x.txt"
    secret.write_text("no", encoding="utf-8")
    assert_no_peek(a, a / "own.txt", b)
    try:
        assert_no_peek(a, secret, b)
    except PeekingError as e:
        assert e.kind == "PEEKING_VIOLATION"
    else:
        raise AssertionError("sibling read must PEEKING_VIOLATION")


def test_no_ballot_writer():
    try:
        refuse_ballot()
    except PeekingError as e:
        assert e.kind == "NO_BALLOT_WRITER"
    else:
        raise AssertionError("ballot writer must refuse")


def test_dual_lane_workspaces_are_siblings():
    td = Path(tempfile.mkdtemp(prefix="p02d_"))
    src = td / "src"
    src.mkdir()
    (src / "f.txt").write_text("x", encoding="utf-8")
    live = install(td / "live", tree_id="p02-peek")
    pair = prepare_dual_lane_workspaces(src, live_root=live, attempt_id="p02")
    ws_a, rec_a = pair["A"]
    ws_b, rec_b = pair["B"]
    assert Path(ws_a).resolve() != Path(ws_b).resolve()
    assert rec_a.get("sibling") == str(ws_b)
    assert rec_b.get("sibling") == str(ws_a)
    assert rec_a.get("ballot_writer") is False
    secret = Path(ws_b) / "secret.txt"
    secret.write_text("b", encoding="utf-8")
    try:
        assert_no_peek(ws_a, secret, ws_b)
    except PeekingError as e:
        assert e.kind == "PEEKING_VIOLATION"
    else:
        raise AssertionError("dual-lane sibling read must refuse")


def main() -> int:
    test_sibling_read_is_peeking_violation()
    test_no_ballot_writer()
    test_dual_lane_workspaces_are_siblings()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
