#!/usr/bin/env py -3.14
"""Gates for cosmos_womb_board.py (propose-only)."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cosmos_womb_board import snapshot


class Paths:
    def __init__(self, root: Path):
        self._root = root

    def role(self, name: str) -> Path:
        return self._root / name  # no mkdir — GET must tolerate absence


def test_absent_is_unmeasured_and_does_not_mkdir():
    root = Path(tempfile.mkdtemp())
    rec = snapshot(Paths(root), tail=10)
    assert rec["kind"] == "UNMEASURED"
    assert rec["board"] == "ABSENT"
    assert rec["judge"]["called"] is False
    assert rec["judge"].get("grade") is None
    assert "not called" in (rec["judge"].get("note") or "").lower()
    assert not (root / "state" / "crew_pipe").exists()


def test_rows_and_judge_honesty():
    root = Path(tempfile.mkdtemp())
    board = root / "state" / "crew_pipe" / "wombat_board.jsonl"
    board.parent.mkdir(parents=True)
    board.write_text(
        json.dumps({"order_id": "WO1", "action": "watch", "note": "ok"}) + "\n",
        encoding="utf-8",
    )
    rec = snapshot(Paths(root), tail=10)
    assert rec["kind"] == "MEASURED"
    assert rec["n"] == 1
    assert rec["rows"][0]["order_id"] == "WO1"
    assert rec["judge"]["called"] is False
    assert "Do not paint KEEP" in rec["judge"]["note"]


def test_unreadable_board_is_unmeasured():
    root = Path(tempfile.mkdtemp())
    board = root / "state" / "crew_pipe" / "wombat_board.jsonl"
    board.parent.mkdir(parents=True)
    board.write_text("{}\n", encoding="utf-8")
    real = Path.read_text

    def boom(self, *a, **k):
        if self.name == "wombat_board.jsonl":
            raise OSError("sharing violation")
        return real(self, *a, **k)

    with patch.object(Path, "read_text", boom):
        rec = snapshot(Paths(root), tail=10)
    assert rec["kind"] == "UNMEASURED", rec
    assert str(rec["board"]).startswith("READ_FAILED")
    assert "empty floor" in rec["note"]


if __name__ == "__main__":
    test_absent_is_unmeasured_and_does_not_mkdir()
    test_rows_and_judge_honesty()
    test_unreadable_board_is_unmeasured()
    print("test_womb_board: 3 ok")
