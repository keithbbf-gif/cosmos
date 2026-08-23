"""Arbiter clock. Lease expiry is decided here, never on a client clock.

A dying holder is recovered by advancing this clock past expiry — no
cleanup discipline, no unlink, no release call.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


class ArbiterClock:
    """Monotonic-enough wall clock in the arbiter's time source."""

    source_name: str = "arbiter"

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def epoch(self) -> float:
        return self.now().timestamp()


class FrozenClock(ArbiterClock):
    """Injectable clock so expiry tests do not wait 90 minutes."""

    source_name: str = "arbiter-frozen"

    def __init__(self, start: datetime | None = None) -> None:
        self._now = start or datetime(2026, 8, 23, 10, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now

    def epoch(self) -> float:
        return self._now.timestamp()

    def advance(self, seconds: float) -> datetime:
        if seconds < 0:
            raise ValueError("clock does not run backwards")
        self._now = self._now + timedelta(seconds=seconds)
        return self._now
