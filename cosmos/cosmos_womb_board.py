#!/usr/bin/env python3
"""cosmos_womb_board — WOMB factory-floor projection. Propose-only.

GET /api/v1/womb/board — read-only tail of crew_pipe/wombat_board.jsonl.
GET never mkdir. Missing file = UNMEASURED (not empty MEASURED).
Does not call pipe_root() — that mkdir's inboxes.

Does not paint KEEP. If Judge has not been called, say so.

Live splice: cosmos/cosmos_womb_board.py
Does not replace GET /api/v1/womb/seat (pair pick stays).
"""
from __future__ import annotations

import json
from pathlib import Path

SCHEMA = "cosmos-womb-board/1"
TAIL_DEFAULT = 40
TAIL_MAX = 200


class WombBoardError(RuntimeError):
    def __init__(self, kind: str, detail: str = ""):
        super().__init__(detail or kind)
        self.kind = kind
        self.detail = detail or kind


def _state_dir(paths) -> Path:
    return Path(paths.role("state"))


def _board_path(paths) -> Path:
    return _state_dir(paths) / "crew_pipe" / "wombat_board.jsonl"


def _judge_seat_path(paths) -> Path:
    return _state_dir(paths) / "womb" / "judge_seat.json"


def _roster_path(paths) -> Path:
    return _state_dir(paths) / "crew" / "roster.jsonl"


def _read_jsonl_tail(path: Path, n: int) -> tuple[list[dict], str]:
    if not path.is_file():
        return [], "ABSENT"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        return [], f"READ_FAILED:{type(e).__name__}"
    rows: list[dict] = []
    for line in lines[-n:]:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            rec = {"kind": "BROKE", "raw": line[:160]}
        if isinstance(rec, dict):
            rows.append(rec)
    return rows, "PRESENT"


def _judge_honesty(paths) -> dict:
    p = _judge_seat_path(paths)
    if not p.is_file():
        return {
            "called": False,
            "kind": "UNMEASURED",
            "note": "Judge not called — judge_seat.json absent. Do not paint KEEP.",
        }
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {
            "called": False,
            "kind": "BROKE",
            "note": f"judge_seat unreadable: {type(e).__name__}. Do not paint KEEP.",
        }
    if not isinstance(rec, dict):
        return {"called": False, "kind": "BROKE", "note": "judge_seat not an object"}
    grade = rec.get("grade") or rec.get("verdict")
    return {
        "called": True,
        "kind": "MEASURED",
        "grade": grade if grade is not None else "UNMEASURED",
        "note": rec.get("note") or "Judge file present. Grade is the file, not a painted KEEP.",
    }


def snapshot(paths, *, tail: int = TAIL_DEFAULT) -> dict:
    n = int(tail)
    if n < 1 or n > TAIL_MAX:
        raise WombBoardError("BAD_TAIL", f"tail must be 1..{TAIL_MAX}")
    board_p = _board_path(paths)
    rows, board_st = _read_jsonl_tail(board_p, n)
    roster, roster_st = _read_jsonl_tail(_roster_path(paths), 12)
    judge = _judge_honesty(paths)
    failed = board_st.startswith("READ_FAILED") or roster_st.startswith("READ_FAILED")
    if failed:
        kind = "UNMEASURED"
        note = (
            "board or roster unreadable (" + board_st + " / " + roster_st
            + "). Not an empty floor."
        )
    elif board_st == "ABSENT" and not rows:
        kind = "UNMEASURED"
        note = (
            "WOMB board file absent. GET never mkdir. "
            "WOMBAT rows appear after crew_pipe appends wombat_board.jsonl."
        )
    else:
        kind = "MEASURED"
        note = "FIFO tail. WOMBAT runs CCrew. Keith talks to the manager, not each coder."
    return {
        "schema": SCHEMA,
        "kind": kind,
        "rows": rows,
        "n": len(rows),
        "board": board_st,
        "board_path": str(board_p),
        "crew": roster,
        "crew_file": roster_st,
        "judge": judge,
        "manager": "WOMBAT",
        "pen": "NONE",
        "note": note,
    }
