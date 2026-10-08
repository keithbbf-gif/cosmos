#!/usr/bin/env python3
"""Plan parallel clone seats. This module does not start them.

One row per seat, in call order. Each row carries the hero index pointer.
The plan's pen is false and its executable is empty: a clone never takes
a second live pen, and this planner does not run the mouths. A bad call
raises ClonePlanError and returns no rows.
"""
from __future__ import annotations

from typing import TypedDict

INDEX_POINTER = "work_orders/ccr/HERO_SEAT_INDEX.md"
MAX_SEATS = 12

_REASONS = frozenset(
    {
        "EMPTY_MISSION",
        "NO_SEATS",
        "TOO_MANY",
        "DUPLICATE_SEAT",
        "BLANK_SEAT",
        "SECOND_PEN",
    }
)


class CloneRow(TypedDict):
    seat: str
    mission: str
    pen: bool
    spawn: bool
    index_pointer: str


class ClonePlan(TypedDict):
    pen: bool
    executable: str
    rows: list[CloneRow]


class ClonePlanError(Exception):
    """One refusal. `reason` is the stable code; the plan is not partial."""

    def __init__(self, reason: str) -> None:
        if reason not in _REASONS:
            raise ValueError(reason)
        self.reason = reason
        super().__init__(reason)


def _blank(value: object) -> bool:
    return not isinstance(value, str) or value.strip() == ""


def plan_clones(
    seats: list[str],
    mission: str,
    *,
    pen: bool = False,
) -> ClonePlan:
    """Return one inert row per seat.

    Check order is the pen, then the mission, then the roster size, then
    each id. The first failure raises. Nothing is returned before then.
    """
    if pen is True:
        raise ClonePlanError("SECOND_PEN")
    if _blank(mission):
        raise ClonePlanError("EMPTY_MISSION")
    if not isinstance(seats, list) or len(seats) == 0:
        raise ClonePlanError("NO_SEATS")
    if len(seats) > MAX_SEATS:
        raise ClonePlanError("TOO_MANY")
    seen: set[str] = set()
    ordered: list[str] = []
    for seat in seats:
        if _blank(seat):
            raise ClonePlanError("BLANK_SEAT")
        if seat in seen:
            raise ClonePlanError("DUPLICATE_SEAT")
        seen.add(seat)
        ordered.append(seat)
    rows: list[CloneRow] = [
        {
            "seat": seat,
            "mission": mission,
            "pen": False,
            "spawn": False,
            "index_pointer": INDEX_POINTER,
        }
        for seat in ordered
    ]
    return {"pen": False, "executable": "", "rows": rows}
