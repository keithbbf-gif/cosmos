"""Session liveness. The caller passes the only clock. No thread and no sleep."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq

SCHEMA: Final[str] = "cosmos-hermes-heartbeat/1"
MIN_INTERVAL_S: Final[int] = 15
# Signed 32-bit ceiling. A larger request is out of range, not a raised cap.
POLICY_CAP: Final[int] = 2_147_483_647
_CLOCK_HI: Final[int] = 10**18
_SCHEMA_LIMIT: Final[int] = 64

__all__ = [
    "MIN_INTERVAL_S",
    "POLICY_CAP",
    "SCHEMA",
    "Beat",
    "Heartbeat",
    "Interval",
    "Snapshot",
    "rebuild",
]


def _flag(value: object) -> bool:
    if type(value) is not bool:
        raise Refuse("NOT_BOOL")
    return value


def _clock(value: object) -> int:
    return bound_int(value, 0, _CLOCK_HI)


def _requested(value: object) -> int:
    return bound_int(value, 0, POLICY_CAP)


def _effective(requested: int) -> int:
    if requested < MIN_INTERVAL_S:
        return MIN_INTERVAL_S
    return requested


def _schema(value: object) -> str:
    text = bound_text(value, _SCHEMA_LIMIT)
    if not const_eq(text, SCHEMA):
        raise Refuse("BAD_SCHEMA")
    return text


def _as_beat(value: object) -> Beat:
    if not isinstance(value, Beat) or type(value) is not Beat:
        raise Refuse("BAD_RECORD")
    return value


@dataclass(frozen=True, slots=True)
class Interval:
    """Requested interval beside the policy interval that applies."""

    requested: int
    effective: int

    def __post_init__(self) -> None:
        requested = _requested(self.requested)
        effective = bound_int(self.effective, MIN_INTERVAL_S, POLICY_CAP)
        if effective != _effective(requested):
            raise Refuse("BAD_INTERVAL")


@dataclass(frozen=True, slots=True)
class Beat:
    """One tick. `alive` is true even when `task_ok` is false."""

    schema: str
    at: int
    alive: bool
    task_ok: bool
    requested_s: int
    interval_s: int

    def __post_init__(self) -> None:
        _schema(self.schema)
        _clock(self.at)
        if type(self.alive) is not bool:
            raise Refuse("NOT_BOOL")
        if self.alive is not True:
            raise Refuse("NOT_ALIVE")
        _flag(self.task_ok)
        requested = _requested(self.requested_s)
        interval = bound_int(self.interval_s, MIN_INTERVAL_S, POLICY_CAP)
        if interval != _effective(requested):
            raise Refuse("BAD_INTERVAL")


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Public liveness. `last_at` is the watermark. Absent until the first beat."""

    schema: str
    requested_s: int
    interval_s: int
    alive: bool
    task_ok: bool | None
    last_at: int | None

    def __post_init__(self) -> None:
        _schema(self.schema)
        requested = _requested(self.requested_s)
        interval = bound_int(self.interval_s, MIN_INTERVAL_S, POLICY_CAP)
        if interval != _effective(requested):
            raise Refuse("BAD_INTERVAL")
        if type(self.alive) is not bool:
            raise Refuse("NOT_BOOL")
        if self.last_at is None:
            if self.alive is not False or self.task_ok is not None:
                raise Refuse("MISMATCH")
            return
        _clock(self.last_at)
        if self.alive is not True:
            raise Refuse("NOT_ALIVE")
        _flag(self.task_ok)


class Heartbeat:
    """Liveness for one session. The caller passes `now`. No thread and no sleep."""

    __slots__ = ("_alive", "_interval_s", "_last_at", "_requested_s", "_task_ok")

    _requested_s: int
    _interval_s: int
    _last_at: int | None
    _task_ok: bool | None
    _alive: bool

    def __init__(self, interval_s: object) -> None:
        requested = _requested(interval_s)
        self._requested_s = requested
        self._interval_s = _effective(requested)
        self._last_at = None
        self._task_ok = None
        self._alive = False

    @property
    def requested_s(self) -> int:
        return self._requested_s

    @property
    def interval_s(self) -> int:
        """Effective interval. A request below 15 stays recorded and this stays 15."""
        return self._interval_s

    @property
    def interval(self) -> Interval:
        return Interval(self._requested_s, self._interval_s)

    @property
    def alive(self) -> bool:
        return self._alive

    @property
    def task_ok(self) -> bool | None:
        return self._task_ok

    @property
    def last_at(self) -> int | None:
        """Watermark. A caller timestamp behind this value is stale."""
        return self._last_at

    def snapshot(self) -> Snapshot:
        return Snapshot(
            SCHEMA,
            self._requested_s,
            self._interval_s,
            self._alive,
            self._task_ok,
            self._last_at,
        )

    def beat(self, now: object, task_ok: object) -> Beat:
        """Record liveness at `now`. A failed task is still alive."""
        at = _clock(now)
        ok = _flag(task_ok)
        watermark = self._last_at
        if watermark is not None:
            if at < watermark:
                raise Refuse("STALE")
            if at == watermark:
                raise Refuse("REPLAY")
        record = Beat(SCHEMA, at, True, ok, self._requested_s, self._interval_s)
        self._last_at = record.at
        self._task_ok = record.task_ok
        self._alive = record.alive
        return record

    def miss(self, now: object) -> bool:
        """True when `now - last` is greater than the effective interval."""
        at = _clock(now)
        watermark = self._last_at
        if watermark is None:
            raise Refuse("NO_BEAT")
        if at < watermark:
            raise Refuse("STALE")
        return (at - watermark) > self._interval_s

    def __repr__(self) -> str:
        return (
            f"Heartbeat(schema={SCHEMA!r}, requested_s={self._requested_s}, "
            f"interval_s={self._interval_s}, cap={POLICY_CAP}, alive={self._alive}, "
            f"task_ok={self._task_ok!r}, last_at={self._last_at!r})"
        )


def rebuild(interval_s: object, beats: object) -> Snapshot:
    """Replay emitted beats in order. One stale or replayed row refuses the snapshot."""
    session = Heartbeat(interval_s)
    if not isinstance(beats, tuple) or type(beats) is not tuple:
        raise Refuse("BAD_RECORD")
    for item in beats:
        row = _as_beat(item)
        if row.requested_s != session.requested_s or row.interval_s != session.interval_s:
            raise Refuse("MISMATCH")
        session.beat(row.at, row.task_ok)
    return session.snapshot()
