"""Projection counters folded from caller-supplied events. Not a ledger."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, cast

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-observability/1"
AUTHORITY: Final[str] = "projection"
NAME_CAP: Final[int] = 64
EVENT_CAP: Final[int] = 256
INC_MAX: Final[int] = 1000
TOTAL_MAX: Final[int] = EVENT_CAP * INC_MAX
_NAME_LIMIT: Final[int] = 40
_SCHEMA_LIMIT: Final[int] = 64
_AUTHORITY_LIMIT: Final[int] = 32
_NAME: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9_:]{1,40}$")

__all__ = [
    "AUTHORITY",
    "EVENT_CAP",
    "INC_MAX",
    "NAME_CAP",
    "SCHEMA",
    "TOTAL_MAX",
    "Counters",
    "Event",
    "Snapshot",
    "measure",
    "rebuild",
]


def _recorded_cap(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("BAD_LIMIT")
    if value > NAME_CAP:
        return NAME_CAP
    return value


def _name(value: object) -> str:
    text = bound_text(value, _NAME_LIMIT)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _NAME.fullmatch(text) is None:
        raise Refuse("BAD_NAME")
    return text


def _schema(value: object) -> str:
    text = bound_text(value, _SCHEMA_LIMIT)
    if secret_shape(text):
        raise Refuse("SECRET")
    if not const_eq(text, SCHEMA):
        raise Refuse("BAD_SCHEMA")
    return text


def _authority(value: object) -> str:
    text = bound_text(value, _AUTHORITY_LIMIT)
    if secret_shape(text):
        raise Refuse("SECRET")
    if not const_eq(text, AUTHORITY):
        raise Refuse("BAD_AUTHORITY")
    return text


def _total(value: object) -> int:
    return bound_int(value, 1, TOTAL_MAX)


def _event_rows(value: object) -> tuple[Event, ...]:
    if type(value) is not tuple:
        raise Refuse("BAD_EVENTS")
    raw = cast(tuple[object, ...], value)
    if len(raw) > EVENT_CAP:
        raise Refuse("EVENT_CAP")
    rows: list[Event] = []
    for item in raw:
        if type(item) is not Event:
            raise Refuse("BAD_EVENT")
        rows.append(item)
    return tuple(rows)


def _count_rows(counts: object, cap: int) -> tuple[tuple[str, int], ...]:
    if type(counts) is not tuple:
        raise Refuse("BAD_SNAPSHOT")
    raw = cast(tuple[object, ...], counts)
    normalized: list[tuple[str, int]] = []
    seen: set[str] = set()
    for row in raw:
        if type(row) is not tuple:
            raise Refuse("BAD_SNAPSHOT")
        pair = cast(tuple[object, ...], row)
        if len(pair) != 2:
            raise Refuse("BAD_SNAPSHOT")
        label = _name(pair[0])
        total = _total(pair[1])
        if label in seen:
            raise Refuse("BAD_SNAPSHOT")
        if len(normalized) >= cap:
            raise Refuse("NAME_CAP", str(cap))
        seen.add(label)
        normalized.append((label, total))
    return tuple(normalized)


def _fold(events: tuple[Event, ...], cap: int) -> dict[str, int]:
    built: dict[str, int] = {}
    for event in events:
        label = event.name
        step = event.n
        if type(label) is not str or type(step) is not int:
            raise Refuse("BAD_EVENT")
        if step < 1 or step > INC_MAX:
            raise Refuse("OUT_OF_RANGE", f"1..{INC_MAX}")
        current = built.get(label)
        if current is None:
            if len(built) >= cap:
                raise Refuse("NAME_CAP", str(cap))
            built[label] = step
        else:
            built[label] = current + step
    return built


@dataclass(frozen=True, slots=True)
class Event:
    """One caller-supplied increment. Repeats of a name accumulate. They are not a ledger id."""

    name: str
    n: int = 1
    schema: str = SCHEMA
    authority: str = AUTHORITY

    def __post_init__(self) -> None:
        _name(self.name)
        bound_int(self.n, 1, INC_MAX)
        _schema(self.schema)
        _authority(self.authority)

    def __repr__(self) -> str:
        return (
            f"Event(name={redact(self.name)!r}, n={self.n}, "
            f"schema={redact(self.schema)!r}, authority={redact(self.authority)!r})"
        )


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Measured totals in first-seen order. `authority` stays `projection`."""

    schema: str
    counts: tuple[tuple[str, int], ...]
    cap: int
    authority: str

    def __post_init__(self) -> None:
        schema = _schema(self.schema)
        authority = _authority(self.authority)
        recorded = _recorded_cap(self.cap)
        rows = _count_rows(self.counts, recorded)
        object.__setattr__(self, "schema", schema)
        object.__setattr__(self, "counts", rows)
        object.__setattr__(self, "cap", recorded)
        object.__setattr__(self, "authority", authority)

    def __repr__(self) -> str:
        shown = tuple((redact(label), total) for label, total in self.counts)
        return (
            f"Snapshot(schema={redact(self.schema)!r}, counts={shown!r}, "
            f"cap={self.cap}, authority={redact(self.authority)!r})"
        )


class Counters:
    """A replaceable fold of caller-supplied events. Missing names are not zero."""

    __slots__ = ("_cap", "_counts", "_indexed")

    _cap: int
    _counts: dict[str, int]
    _indexed: bool

    def __init__(self, requested_cap: object = NAME_CAP) -> None:
        self._cap = _recorded_cap(requested_cap)
        self._counts = {}
        self._indexed = False

    @property
    def schema(self) -> str:
        return SCHEMA

    @property
    def cap(self) -> int:
        return self._cap

    @property
    def authority(self) -> str:
        return AUTHORITY

    @property
    def indexed(self) -> bool:
        """True after a successful rebuild. False is a missing index, not an empty measurement."""
        return self._indexed

    def rebuild(self, events: object) -> Snapshot:
        """Replace the projection. The same events produce the same counts."""
        built = _fold(_event_rows(events), self._cap)
        snap = Snapshot(SCHEMA, tuple(built.items()), self._cap, AUTHORITY)
        self._counts = built
        self._indexed = True
        return snap

    def snapshot(self) -> Snapshot:
        """Return the measured counts. A missing index is UNMEASURED."""
        if not self._indexed:
            raise Refuse("UNMEASURED")
        return Snapshot(SCHEMA, tuple(self._counts.items()), self._cap, AUTHORITY)

    def get(self, name: object) -> int:
        """Return one total. An absent name is UNMEASURED, not zero."""
        label = _name(name)
        if not self._indexed:
            raise Refuse("UNMEASURED")
        found = self._counts.get(label)
        if found is None:
            raise Refuse("UNMEASURED")
        return found

    def clear(self) -> None:
        """Drop the index. The recorded cap stays. The next read is UNMEASURED."""
        self._counts = {}
        self._indexed = False

    def __repr__(self) -> str:
        if self._indexed:
            shown = tuple((redact(label), total) for label, total in self._counts.items())
            body = repr(shown)
        else:
            body = "UNMEASURED"
        return (
            f"Counters(schema={SCHEMA!r}, cap={self._cap}, "
            f"authority={AUTHORITY!r}, indexed={self._indexed}, {body})"
        )


def measure(snapshot: object, name: object) -> int:
    """Return one total from a snapshot. A name it does not hold is UNMEASURED, not zero."""
    if type(snapshot) is not Snapshot:
        raise Refuse("BAD_SNAPSHOT")
    label = _name(name)
    totals: dict[str, int] = {row_name: total for row_name, total in snapshot.counts}
    found = totals.get(label)
    if found is None:
        raise Refuse("UNMEASURED")
    return found


def rebuild(events: object, requested_cap: object = NAME_CAP) -> Snapshot:
    """Fold `events` on a fresh projection. A requested cap above policy is ignored."""
    return Counters(requested_cap).rebuild(events)
