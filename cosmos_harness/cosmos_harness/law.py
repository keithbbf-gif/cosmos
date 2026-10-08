"""Harness law compared with the recorded Claude Code zeros.

This is the G47 scorecard, applied to this package's own files. It is not a
task bakeoff and it does not claim an Opus win on a benchmark. Claude Code
with Opus seated still clears its compaction latch and still exposes a
delete-shaped bash. Those are the zeros in ``g47.superior.CLAUDE_LAW``.

A task-win measurement is a separate run. This function only reports whether
the files that ship here still contain the gates.
"""

from __future__ import annotations

import sys
from pathlib import Path

_G47 = Path(__file__).resolve().parents[2] / "harness" / "G47"
if str(_G47) not in sys.path:
    sys.path.insert(0, str(_G47))

from g47.superior import AXES, CLAUDE_LAW  # noqa: E402

_ROOT = Path(__file__).resolve().parents[1]


def _text() -> str:
    parts = [
        (_ROOT / "pack" / "LOOP.md").read_text(encoding="utf-8"),
        (_ROOT / "pack" / "L6_TOOLS.json").read_text(encoding="utf-8"),
        (_ROOT / "cosmos_harness" / "loop.py").read_text(encoding="utf-8"),
        (_ROOT / "cosmos_harness" / "hooks.py").read_text(encoding="utf-8"),
    ]
    return "\n".join(parts)


def score() -> dict[str, int]:
    """1 when this tree still enforces the axis. 0 when the phrase is gone."""
    blob = _text()
    values = {
        "pin_lock": 1 if "fallback" in blob and "PIN_SWAP" in blob else 0,
        "no_ungated_retry": 1 if "latch is not cleared" in blob else 0,
        "done_bundle": 1 if "DoneBundle" in blob or "five hashes" in blob else 0,
        "oracle_before_edit": 1 if "oracle_red" in blob or "Oracle fails before" in blob else 0,
        "delete_is_not_a_tool": 1 if "delete" in blob and "NOT_A_HAND" in blob else 0,
        "four_checks": 1 if "py_compile" in blob and "ruff" in blob and "mypy" in blob and "pytest" in blob else 0,
        "live_refused": 1 if "live/ is refused" in blob else 0,
        "turn_cap": 1 if "Turn cap 8" in blob else 0,
        "pack_eight": 1 if "eight" in blob.lower() and "l8_mission" in blob else 0,
        "scar_sop": 1 if "One scar maps to one SOP" in blob else 0,
        "one_corrective": 1 if "same scar does not fire twice" in blob else 0,
    }
    if tuple(values) != AXES:
        missing = [axis for axis in AXES if axis not in values]
        raise RuntimeError(f"axes drifted: {missing}")
    return values


def ahead_of_claude_record() -> bool:
    """True when every axis here is 1 and the recorded Claude law is still all zeros."""
    ours = score()
    return all(value == 1 for value in ours.values()) and all(value == 0 for value in CLAUDE_LAW.values())
