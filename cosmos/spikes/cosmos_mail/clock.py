"""Offset-aware clocks. Naive datetimes are refused at the boundary."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Protocol

from cosmos.spikes.cosmos_mail.types import require_aware


class Clock(Protocol):
    def now(self) -> datetime:
        """Return an offset-aware instant. Worker clocks are evidence, not authority."""


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc).astimezone()


class FrozenClock:
    """Deterministic clock for selftests. Advance it to travel through staleness."""

    def __init__(self, instant: datetime) -> None:
        self._instant = require_aware(instant)

    def now(self) -> datetime:
        return self._instant

    def advance(self, seconds: float) -> None:
        self._instant = self._instant + timedelta(seconds=seconds)
