"""Harness law compared. This is not a coding-benchmark score.

Claude Code loses these axes because its loop swaps the pin, retries a failed
guard, and has a delete tool. COSMOS CODE keeps the opposite law on the seat.
A task win is a separate measurement and is not claimed here.
"""

from __future__ import annotations

from g47.seat import Seat

AXES = (
    "pin_lock",
    "no_ungated_retry",
    "done_bundle",
    "oracle_before_edit",
    "delete_is_not_a_tool",
    "four_checks",
    "live_refused",
    "turn_cap",
    "pack_eight",
    "scar_sop",
    "one_corrective",
)

# Steal-list from Claude Code 2.1.88. fallbackModel, while(true), delete tool.
CLAUDE_LAW = {axis: 0 for axis in AXES}


def law(seat: Seat) -> dict[str, int]:
    """1 when this seat's harness actually enforces the axis."""
    pack = 1 if seat.pack_applied and len(seat.layers) == 8 else 0
    pin = 1 if "--fallback-model" not in seat.plan.argv else 0
    if seat.via == "cosmos-code":
        loop = seat.plan.files.get("LOOP.md", "")
        tools = seat.plan.files.get("TOOLS.md", "")
        return {
            "pin_lock": pin,
            "no_ungated_retry": 1 if "failed grade is not cleared" in loop else 0,
            "done_bundle": 1 if "DoneBundle" in loop else 0,
            "oracle_before_edit": 1 if "Oracle fails before" in loop else 0,
            "delete_is_not_a_tool": 1 if "delete is not a tool" in tools else 0,
            "four_checks": 1 if "py_compile, ruff, mypy, pytest" in loop else 0,
            "live_refused": 1 if "live/ is refused" in loop else 0,
            "turn_cap": 1 if "Turn cap" in loop else 0,
            "pack_eight": pack,
            "scar_sop": 1 if "One scar maps to one SOP" in loop else 0,
            "one_corrective": 1 if "The same scar does not fire twice" in loop else 0,
        }
    # A native door can carry a full pack and still not own the rail.
    return {
        "pin_lock": pin,
        "no_ungated_retry": 0,
        "done_bundle": 0,
        "oracle_before_edit": 0,
        "delete_is_not_a_tool": 0,
        "four_checks": 0,
        "live_refused": 0,
        "turn_cap": 0,
        "pack_eight": pack,
        "scar_sop": 0,
        "one_corrective": 0,
    }


def ahead_of(seat: Seat, other: dict[str, int]) -> bool:
    ours = law(seat)
    return sum(ours.values()) > sum(other.values())
