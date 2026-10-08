"""Hash-chained kanban projection. Cards move by events. Not a second queue."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from cosmos_hermes import Refuse, bound_text, redact, secret_shape

SCHEMA = "cosmos-hermes-kanban/1"
POLICY_CAP = 64
EVENT_CAP = 256
CARD_LIMIT = 64
COLUMN_LIMIT = 32
BODY_LIMIT = 160
GENESIS = "0" * 64
COLUMNS = frozenset({"todo", "doing", "done"})
KINDS = frozenset({"add", "move"})

_SHA = re.compile(r"^[0-9a-f]{64}$")
_CARD = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")

__all__ = [
    "BODY_LIMIT",
    "CARD_LIMIT",
    "COLUMNS",
    "COLUMN_LIMIT",
    "EVENT_CAP",
    "GENESIS",
    "KINDS",
    "POLICY_CAP",
    "SCHEMA",
    "Board",
    "Event",
    "Placement",
    "Snapshot",
    "link_sha",
    "rebuild",
]


def _clamp(value: object) -> int:
    """Record a request. A value above the policy cap is ignored."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{POLICY_CAP}")
    if value > POLICY_CAP:
        return POLICY_CAP
    return value


def _applied_cap(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < 1 or value > POLICY_CAP:
        raise Refuse("OUT_OF_RANGE", f"1..{POLICY_CAP}")
    return value


def _schema(value: object) -> str:
    text = bound_text(value, 64)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text != SCHEMA:
        raise Refuse("BAD_SCHEMA")
    return text


def _link(value: object) -> str:
    text = bound_text(value, 64)
    if _SHA.fullmatch(text) is None:
        raise Refuse("BAD_SHA")
    return text


def _digest(prev: str, body: str) -> str:
    return hashlib.sha256(f"{prev}\n{body}".encode("utf-8")).hexdigest()


def _card(value: object) -> str:
    text = bound_text(value, CARD_LIMIT)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text.strip() == "":
        raise Refuse("EMPTY")
    if _CARD.fullmatch(text) is None:
        raise Refuse("BAD_CARD")
    return text


def _column(value: object) -> str:
    text = bound_text(value, COLUMN_LIMIT)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text not in COLUMNS:
        raise Refuse("BAD_COLUMN")
    return text


def _parse(body: str) -> tuple[str, str, str]:
    # Unpacking split raises ValueError when a body has fewer than two bars.
    parts = body.split("|")
    if len(parts) != 3:
        raise Refuse("BAD_BODY")
    kind, card, column = parts
    if secret_shape(kind):
        raise Refuse("SECRET")
    if kind not in KINDS:
        raise Refuse("BAD_EVENT")
    return kind, _card(card), _column(column)


def _rows(events: object) -> tuple[Event, ...]:
    if isinstance(events, (str, bytes)) or not isinstance(events, tuple):
        raise Refuse("BAD_EVENTS")
    rows: list[Event] = []
    for item in events:
        if not isinstance(item, Event):
            raise Refuse("BAD_EVENT")
        rows.append(item)
    if len(rows) > EVENT_CAP:
        raise Refuse("EVENT_CAP")
    return tuple(rows)


def _take_columns(columns: object, cap: int) -> None:
    if not isinstance(columns, tuple):
        raise Refuse("BAD_SNAPSHOT")
    seen: set[str] = set()
    for row in columns:
        if not isinstance(row, tuple) or len(row) != 2:
            raise Refuse("BAD_SNAPSHOT")
        card = _card(row[0])
        column = _column(row[1])
        if card != row[0] or column != row[1]:
            raise Refuse("BAD_SNAPSHOT")
        if card in seen:
            raise Refuse("DUPLICATE")
        seen.add(card)
    if len(seen) > cap:
        raise Refuse("CARD_CAP")


@dataclass(frozen=True, slots=True)
class Event:
    """One sealed link. A mismatched sha is CHAIN."""

    prev_sha: str
    body: str
    sha: str
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        prev = _link(self.prev_sha)
        body = bound_text(self.body, BODY_LIMIT)
        digest = _link(self.sha)
        _schema(self.schema)
        kind, card, column = _parse(body)
        if f"{kind}|{card}|{column}" != body:
            raise Refuse("BAD_BODY")
        if digest != _digest(prev, body):
            raise Refuse("CHAIN")

    def __repr__(self) -> str:
        return (
            f"Event(prev_sha={self.prev_sha!r}, body={redact(self.body)!r}, "
            f"sha={self.sha!r}, schema={self.schema!r})"
        )


def _seal(prev: str, body: str) -> Event:
    digest = _digest(prev, body)
    made = Event.__new__(Event)
    object.__setattr__(made, "prev_sha", prev)
    object.__setattr__(made, "body", body)
    object.__setattr__(made, "sha", digest)
    object.__setattr__(made, "schema", SCHEMA)
    return made


@dataclass(frozen=True, slots=True)
class Placement:
    """One card's column after the chain is applied."""

    card: str
    column: str

    def __post_init__(self) -> None:
        card = _card(self.card)
        column = _column(self.column)
        if card != self.card or column != self.column:
            raise Refuse("BAD_CARD")


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Cap, tip, and columns. The applied cap never exceeds policy."""

    schema: str
    cap: int
    tip: str
    columns: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        _schema(self.schema)
        cap = _applied_cap(self.cap)
        _link(self.tip)
        _take_columns(self.columns, cap)


def link_sha(prev: object, body: object) -> str:
    """Hex digest of one link. Grammar is checked when the event is built."""
    link = _link(prev)
    text = bound_text(body, BODY_LIMIT)
    if secret_shape(text):
        raise Refuse("SECRET")
    return _digest(link, text)


class Board:
    """In-memory column projection. The queue stays the only writer."""

    __slots__ = ("_cap", "_column", "_events", "_order")

    def __init__(self, requested_cap: object = None) -> None:
        self._cap = POLICY_CAP if requested_cap is None else _clamp(requested_cap)
        self._events: list[Event] = []
        self._column: dict[str, str] = {}
        self._order: list[str] = []

    def recorded_cap(self) -> int:
        """Card cap actually stored. A higher request is not kept."""
        return self._cap

    def events(self) -> tuple[Event, ...]:
        """Links in commit order."""
        return tuple(self._events)

    def column_of(self, card_id: object) -> str:
        """Column for one card already on the board."""
        card = _card(card_id)
        found = self._column.get(card)
        if found is None:
            raise Refuse("UNKNOWN_CARD")
        return found

    def cards(self) -> tuple[Placement, ...]:
        """Placements in the order the cards were added."""
        out: list[Placement] = []
        for card in self._order:
            column = self._column.get(card)
            if column is None:
                raise Refuse("UNKNOWN_CARD")
            out.append(Placement(card, column))
        return tuple(out)

    def snapshot(self) -> Snapshot:
        """Public state. A later rebuild of these events matches it."""
        rows: list[tuple[str, str]] = []
        for card in self._order:
            column = self._column.get(card)
            if column is None:
                raise Refuse("UNKNOWN_CARD")
            rows.append((card, column))
        tip = GENESIS if not self._events else self._events[-1].sha
        return Snapshot(SCHEMA, self._cap, tip, tuple(rows))

    def add_card(self, card_id: object, column: object = "todo") -> Event:
        """Append an add link. A second add of the same card refuses."""
        card = _card(card_id)
        dest = _column(column)
        if card in self._column:
            raise Refuse("DUPLICATE")
        if len(self._column) >= self._cap:
            raise Refuse("CARD_CAP")
        return self._commit("add", card, dest)

    def move(self, card_id: object, column: object) -> Event:
        """Append a move link for a card already on the board."""
        card = _card(card_id)
        dest = _column(column)
        if card not in self._column:
            raise Refuse("UNKNOWN_CARD")
        return self._commit("move", card, dest)

    def _commit(self, kind: str, card: str, column: str) -> Event:
        if kind not in KINDS:
            raise Refuse("BAD_EVENT")
        if len(self._events) >= EVENT_CAP:
            raise Refuse("EVENT_CAP")
        body = f"{kind}|{card}|{column}"
        prev = GENESIS if not self._events else self._events[-1].sha
        event = _seal(prev, body)
        self._install(kind, card, column)
        self._events.append(event)
        return event

    def _install(self, kind: str, card: str, column: str) -> None:
        if kind == "add":
            if card in self._column:
                raise Refuse("DUPLICATE")
            if len(self._column) >= self._cap:
                raise Refuse("CARD_CAP")
            self._column[card] = column
            self._order.append(card)
            return
        if kind == "move":
            if card not in self._column:
                raise Refuse("UNKNOWN_CARD")
            self._column[card] = column
            return
        raise Refuse("BAD_EVENT")


def rebuild(events: object, requested_cap: object = None) -> Board:
    """Fold caller-supplied links into a new board. One bad link refuses."""
    rows = _rows(events)
    board = Board(POLICY_CAP if requested_cap is None else requested_cap)
    prev = GENESIS
    for event in rows:
        _schema(event.schema)
        link = _link(event.prev_sha)
        body = bound_text(event.body, BODY_LIMIT)
        digest = _link(event.sha)
        if secret_shape(body):
            raise Refuse("SECRET")
        if link != prev or digest != _digest(link, body):
            raise Refuse("CHAIN")
        kind, card, column = _parse(body)
        if f"{kind}|{card}|{column}" != body:
            raise Refuse("BAD_BODY")
        board._install(kind, card, column)
        board._events.append(event)
        prev = digest
    return board
