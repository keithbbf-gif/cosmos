"""Ordered gates. A gate that cannot run is GateUnavailable, not a pass."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GateFailure:
    axis: str
    locus: str
    detail: str


@dataclass(frozen=True)
class GateUnavailable:
    axis: str
    reason: str


_AXIS = {
    "py_compile": "D0",
    "ruff": "D1",
    "mypy": "D2",
    "pytest": "D3",
}


def ladder_from_rows(rows: list[dict[str, Any]]) -> list[GateFailure | GateUnavailable]:
    """Stop-worthy rows only. NO_TESTS and NO_CODE are recorded by the checker, not failures."""
    found: list[GateFailure | GateUnavailable] = []
    for row in rows:
        tool = str(row.get("tool") or "")
        axis = _AXIS.get(tool)
        if axis is None:
            continue
        status = row.get("status")
        locus = str(row.get("target") or "")
        if status == "MISSING":
            found.append(GateUnavailable(axis, f"{tool} missing"))
        elif status == "FAIL":
            found.append(GateFailure(axis, locus, str(row.get("stderr") or "")[:240]))
    return found
