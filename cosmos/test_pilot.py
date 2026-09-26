#!/usr/bin/env py -3.14
"""Gates for cosmos_pilot.py (propose-only). Run from this folder:

    py -3.14 test_pilot.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cosmos_pilot import PilotError, post_turn, snapshot


class Paths:
    def __init__(self, root: Path):
        self._root = root

    def role(self, name: str) -> Path:
        return self._root / name  # GET must not rely on mkdir here


class Ledger:
    def __init__(self):
        self.events = []

    def append(self, ev, rec):
        self.events.append((ev, rec))


class Kernel:
    def __init__(self, root: Path):
        self.paths = Paths(root)
        self.mail = None
        self.ledger = Ledger()


def test_get_missing_is_unmeasured():
    k = Kernel(Path(tempfile.mkdtemp()))
    rec = snapshot(k.paths, stream="Cm")
    assert rec["kind"] == "UNMEASURED"
    assert rec["n"] == 0
    assert rec["pen"] == "NONE"
    assert rec["turns"] == []


def test_pen_refused():
    k = Kernel(Path(tempfile.mkdtemp()))
    try:
        post_turn(k, {"stream": "Cm", "text": "x", "path": "cosmos/cosmos_service.py"})
    except PilotError as e:
        assert e.kind == "PEN_REFUSED"
    else:
        raise AssertionError("expected PEN_REFUSED")


def test_post_then_get_append_only():
    k = Kernel(Path(tempfile.mkdtemp()))
    a = post_turn(k, {"stream": "Cm", "text": "first", "principal": "captain:cdeck"})
    assert a["kind"] == "ACCEPTED"
    b = post_turn(k, {"stream": "Cm", "text": "second"})
    assert b["kind"] == "ACCEPTED"
    rec = snapshot(k.paths, stream="Cm")
    assert rec["kind"] == "MEASURED"
    assert rec["n"] == 2
    assert rec["turns"][0]["text"] == "first"
    assert rec["turns"][1]["text"] == "second"
    p = Path(rec["path"])
    lines = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(lines) == 2


def test_cdeck_cannot_spoof_orc_role():
    k = Kernel(Path(tempfile.mkdtemp()))
    for principal in ("captain:cdeck", "core:pilot", "occupant:orc"):
        try:
            post_turn(k, {
                "stream": "Cm", "text": "hi", "role": "orc", "principal": principal,
            })
        except PilotError as e:
            assert e.kind == "ORC_REPLY_REFUSED", principal
        else:
            raise AssertionError("expected ORC_REPLY_REFUSED for " + principal)


def test_pen_is_a_path_prefix():
    k = Kernel(Path(tempfile.mkdtemp()))
    ok = post_turn(k, {"stream": "Cm", "text": "note", "path": "notcosmos/notes"})
    assert ok["kind"] == "ACCEPTED"
    try:
        post_turn(k, {"stream": "Cm", "text": "x", "path": "BUILDS/cdeck/ui/app.js"})
    except PilotError as e:
        assert e.kind == "PEN_REFUSED"
    else:
        raise AssertionError("expected PEN_REFUSED for BUILDS/")


def test_ledger_miss_is_named():
    k = Kernel(Path(tempfile.mkdtemp()))

    def boom(*_a, **_k):
        raise RuntimeError("chain down")

    k.ledger.append = boom
    rec = post_turn(k, {"stream": "Cm", "text": "kept"})
    assert rec["kind"] == "ACCEPTED"
    assert rec["ledger"].startswith("APPEND_FAILED")


if __name__ == "__main__":
    test_get_missing_is_unmeasured()
    test_pen_refused()
    test_post_then_get_append_only()
    test_cdeck_cannot_spoof_orc_role()
    test_pen_is_a_path_prefix()
    test_ledger_miss_is_named()
    print("test_pilot: 6 ok")
