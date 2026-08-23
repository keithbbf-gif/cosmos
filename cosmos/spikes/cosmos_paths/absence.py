"""Typed absence algebra.

NOT_FOUND is not OUT_OF_CLOCK is not UNREADABLE is not NOT_IN_RECORD.
An existence check is not an identity check. These kinds must never collapse.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Mapping, TypeVar

T = TypeVar("T")


class AbsenceKind(str, Enum):
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    UNREADABLE = "UNREADABLE"
    UNPARSEABLE = "UNPARSEABLE"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    EMPTY_DIR_TRAP = "EMPTY_DIR_TRAP"
    STALE = "STALE"
    OUT_OF_CLOCK = "OUT_OF_CLOCK"
    NOT_IN_CORPUS = "NOT_IN_CORPUS"
    NOT_IN_RECORD = "NOT_IN_RECORD"
    UNREACHABLE = "UNREACHABLE"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    UNPRICED = "UNPRICED"
    REFUSED = "REFUSED"
    NATIVE_DEMO_REQUIRED = "NATIVE_DEMO_REQUIRED"
    UNSUPPORTED_PLATFORM = "UNSUPPORTED_PLATFORM"


_DISTINCT_CORE = (
    AbsenceKind.NOT_FOUND,
    AbsenceKind.OUT_OF_CLOCK,
    AbsenceKind.UNREADABLE,
    AbsenceKind.NOT_IN_RECORD,
)


def assert_core_kinds_are_distinct() -> None:
    """Load-bearing: the four named absences are four values, not aliases."""
    values = {k.value for k in _DISTINCT_CORE}
    if len(values) != 4:
        raise RuntimeError("typed absence kinds collapsed")


assert_core_kinds_are_distinct()


@dataclass(frozen=True)
class Found(Generic[T]):
    value: T
    detail: str
    observed: Mapping[str, object] = field(default_factory=dict)
    kind: AbsenceKind = field(default=AbsenceKind.FOUND, init=False)


@dataclass(frozen=True)
class Absent:
    kind: AbsenceKind
    detail: str
    observed: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind is AbsenceKind.FOUND:
            raise ValueError("Absent cannot carry FOUND; use Found")


TypedResult = Found[T] | Absent


class TypedRefusal(Exception):
    """Fail-closed refusal. Never a guess, never a fallback."""

    def __init__(
        self,
        kind: AbsenceKind,
        detail: str,
        observed: Mapping[str, object] | None = None,
        **extra: object,
    ) -> None:
        if kind is AbsenceKind.FOUND:
            raise ValueError("TypedRefusal cannot be FOUND")
        self.kind = kind
        self.detail = detail
        merged = dict(observed or {})
        merged.update(extra)
        self.observed = merged
        super().__init__(f"{kind.value}: {detail}")

    def as_absent(self) -> Absent:
        return Absent(kind=self.kind, detail=self.detail, observed=self.observed)


def refuse(kind: AbsenceKind, detail: str, **observed: object) -> TypedRefusal:
    return TypedRefusal(kind, detail, observed)
