"""Pins for the clone-session planner. It plans seats and does not run them."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

_MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "cosmos" / "cosmos_clone_plan.py"
)
_INDEX = "work_orders/ccr/HERO_SEAT_INDEX.md"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "cosmos_clone_plan", _MODULE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("clone plan module is missing")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_plan = _load()
plan_clones = _plan.plan_clones
ClonePlanError = _plan.ClonePlanError


def _reason(seats: list[str], mission: str, *, pen: bool = False) -> str:
    with pytest.raises(ClonePlanError) as caught:
        plan_clones(seats, mission, pen=pen)
    return caught.value.reason


def test_empty_mission() -> None:
    assert _reason(["seat-a"], "") == "EMPTY_MISSION"
    assert _reason(["seat-a"], "   ") == "EMPTY_MISSION"


def test_no_seats() -> None:
    assert _reason([], "grade the seat") == "NO_SEATS"


def test_too_many() -> None:
    seats = [f"seat-{i:02d}" for i in range(13)]
    assert _reason(seats, "grade the seat") == "TOO_MANY"
    assert _reason([""] * 13, "grade the seat") == "TOO_MANY"


def test_duplicate_seat() -> None:
    assert _reason(["seat-a", "seat-b", "seat-a"], "grade the seat") == (
        "DUPLICATE_SEAT"
    )


def test_blank_seat() -> None:
    assert _reason(["seat-a", ""], "grade the seat") == "BLANK_SEAT"
    assert _reason(["seat-a", "   "], "grade the seat") == "BLANK_SEAT"
    assert _reason(["   "], "grade the seat") == "BLANK_SEAT"


def test_second_pen() -> None:
    assert _reason(["seat-a"], "grade the seat", pen=True) == "SECOND_PEN"
    assert _reason([], "", pen=True) == "SECOND_PEN"
    full = [f"seat-{i:02d}" for i in range(12)]
    assert _reason(full, "grade the seat", pen=True) == "SECOND_PEN"


def test_twelve_seat_plan() -> None:
    seats = [f"seat-{i:02d}" for i in range(12)]
    mission = "grade the seat"
    plan = plan_clones(seats, mission)
    assert plan["pen"] is False
    assert plan["executable"] == ""
    assert list(plan) == ["pen", "executable", "rows"]
    rows = plan["rows"]
    assert len(rows) == 12
    assert [row["seat"] for row in rows] == seats
    for row in rows:
        assert row == {
            "seat": row["seat"],
            "mission": mission,
            "pen": False,
            "spawn": False,
            "index_pointer": _INDEX,
        }
        assert list(row) == [
            "seat",
            "mission",
            "pen",
            "spawn",
            "index_pointer",
        ]


def test_module_source_has_no_process_launcher() -> None:
    text = _MODULE_PATH.read_text(encoding="utf-8")
    assert "Popen" not in text
    assert "subprocess" not in text
