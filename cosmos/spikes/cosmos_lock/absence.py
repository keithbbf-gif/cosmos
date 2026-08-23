"""Typed absence and outcomes.

NOT_FOUND is not OUT_OF_CLOCK is not UNREADABLE is not NOT_IN_RECORD.
A missing fact, an unreadable fact, a clock-skewed fact, and a fact the
ledger never recorded are four different states. Collapsing any pair is
how a checker starts crying wolf (STAGE2A tree_lock._sha) or how a torn
lock is read as free (STAGE2A tree_lock._read).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class AbsenceKind(str, Enum):
    """Closed set of typed states used at every lock-spike boundary."""

    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    OUT_OF_CLOCK = "OUT_OF_CLOCK"
    UNREADABLE = "UNREADABLE"
    NOT_IN_RECORD = "NOT_IN_RECORD"
    UNPARSEABLE = "UNPARSEABLE"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    STALE = "STALE"
    REFUSED = "REFUSED"
    NATIVE_DEMO_REQUIRED = "NATIVE_DEMO_REQUIRED"


class RefusalCode(str, Enum):
    """Measured refusal codes printed by the demo and asserted by selftest."""

    STALE_TOKEN = "STALE_TOKEN"
    EXPIRED_HOLDER = "EXPIRED_HOLDER"
    LEASE_NOT_ACTIVE = "LEASE_NOT_ACTIVE"
    TORN_STATE = "TORN_STATE"
    UNKNOWN_WORKER = "UNKNOWN_WORKER"
    RESOURCE_HELD = "RESOURCE_HELD"
    INGRESS_CANNOT_COMMIT = "INGRESS_CANNOT_COMMIT"
    LEDGER_INTEGRITY = "LEDGER_INTEGRITY"
    INPUT_HASH_MISMATCH = "INPUT_HASH_MISMATCH"
    WRONG_UNIVERSE = "WRONG_UNIVERSE"
    CLOCK_SKEW = "CLOCK_SKEW"
    ADVISORY_LOCK_HELD = "ADVISORY_LOCK_HELD"
    CHANGED_UNDER_HOLDER = "CHANGED_UNDER_HOLDER"
    SANDBOX_NOT_AUTHORITY = "SANDBOX_NOT_AUTHORITY"
    CLIENT_EXPIRY_IGNORED = "CLIENT_EXPIRY_IGNORED"


@dataclass(frozen=True)
class Outcome(Generic[T]):
    """One result. Never a bare None, never a guessed fallback."""

    kind: AbsenceKind
    value: T | None = None
    code: str | None = None
    reason: str = ""
    details: dict[str, object] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        # FOUND(None) is a successful observation of absence-of-holder,
        # not an error. NOT_FOUND is the distinct "we could not look" state.
        return self.kind is AbsenceKind.FOUND

    def unwrap(self) -> T:
        if self.kind is not AbsenceKind.FOUND:
            raise RuntimeError(
                f"unwrap of {self.kind.value} code={self.code} reason={self.reason}"
            )
        return self.value  # type: ignore[return-value]

    @staticmethod
    def found(value: T, *, reason: str = "", details: dict[str, object] | None = None) -> Outcome[T]:
        return Outcome(AbsenceKind.FOUND, value=value, reason=reason, details=details or {})

    @staticmethod
    def absent(
        kind: AbsenceKind,
        *,
        code: str | RefusalCode | None = None,
        reason: str = "",
        details: dict[str, object] | None = None,
    ) -> Outcome[T]:
        if kind is AbsenceKind.FOUND:
            raise ValueError("FOUND is not an absence")
        code_s = code.value if isinstance(code, RefusalCode) else code
        return Outcome(kind, value=None, code=code_s, reason=reason, details=details or {})

    @staticmethod
    def refused(
        code: RefusalCode,
        *,
        reason: str = "",
        details: dict[str, object] | None = None,
    ) -> Outcome[T]:
        return Outcome(
            AbsenceKind.REFUSED,
            value=None,
            code=code.value,
            reason=reason,
            details=details or {},
        )

    @staticmethod
    def native_demo_required(feature: str, *, reason: str = "") -> Outcome[T]:
        text = reason or (
            f"{feature} is Windows-native and is marked NATIVE-DEMO-REQUIRED "
            "for the queue-lane demo; this container cannot execute it."
        )
        return Outcome(
            AbsenceKind.NATIVE_DEMO_REQUIRED,
            value=None,
            code="NATIVE_DEMO_REQUIRED",
            reason=text,
            details={"feature": feature},
        )


# The four absences the brief names. Tests assert these identities are distinct.
REQUIRED_ABSENCES: tuple[AbsenceKind, ...] = (
    AbsenceKind.NOT_FOUND,
    AbsenceKind.OUT_OF_CLOCK,
    AbsenceKind.UNREADABLE,
    AbsenceKind.NOT_IN_RECORD,
)
