"""Typed absence algebra. Four named states must never collapse.

NOT_FOUND != OUT_OF_CLOCK != UNREADABLE != NOT_IN_RECORD
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class Absence(str, Enum):
    FOUND = "FOUND"
    EMPTY = "EMPTY"
    NOT_FOUND = "NOT_FOUND"
    UNREADABLE = "UNREADABLE"
    UNPARSEABLE = "UNPARSEABLE"
    STALE = "STALE"
    OUT_OF_CLOCK = "OUT_OF_CLOCK"
    NOT_IN_RECORD = "NOT_IN_RECORD"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    UNREACHABLE = "UNREACHABLE"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    REFUSED = "REFUSED"
    LOST_CLEANLY = "LOST_CLEANLY"
    FLAGGED = "FLAGGED"
    NATIVE_DEMO_REQUIRED = "NATIVE_DEMO_REQUIRED"
    CLEAN = "CLEAN"
    FINDINGS = "FINDINGS"
    BROKE = "BROKE"
    TIMED_OUT = "TIMED_OUT"


@dataclass(frozen=True)
class TypedResult(Generic[T]):
    kind: Absence
    detail: str
    value: T | None = None

    def is_found(self) -> bool:
        return self.kind is Absence.FOUND

    def refuse_if_absent(self) -> T:
        if self.kind is not Absence.FOUND or self.value is None:
            raise AbsenceError(self)
        return self.value


class AbsenceError(Exception):
    def __init__(self, result: TypedResult[object]) -> None:
        self.result = result
        super().__init__(f"{result.kind.value}: {result.detail}")
