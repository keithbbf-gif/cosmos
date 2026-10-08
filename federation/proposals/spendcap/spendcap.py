"""Day-one spend fold. The check runs before the first model call.

This is not a second wallet. Core's append-only ledger stays the authority
when CCr lands the fold. If this fold and the chain disagree, the chain wins.
The policy ceiling stays MAX_CAP_USD_MICROS. A book never raises it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from cosmos_federation import Refuse, bound_int, bound_text, check_cap, secret_shape

SCHEMA = "cosmos-federation-spendcap/1"

# Caller epochs and micro-dollar amounts fit a signed 64-bit int.
# Wider values are not day-one inputs. Amounts inside this range that
# pass the book cap still refuse OVER_CAP, not BOUND.
_INT_HI = 2**63 - 1

Kind = Literal["RESERVE", "SETTLE", "RELEASE"]
_Status = Literal["open", "settled", "released"]


@dataclass(frozen=True, slots=True)
class Event:
    kind: Kind
    event_id: str
    micros: int
    epoch: int


@dataclass(frozen=True, slots=True)
class Book:
    cap_usd_micros: int
    events: tuple[Event, ...]


@dataclass(frozen=True, slots=True)
class _Row:
    status: _Status
    hold: int
    settled: int


def open_book(cap_usd_micros: int) -> Book:
    """Open an empty fold. check_cap refuses a ceiling above one dollar."""
    cap = check_cap(cap_usd_micros)
    return Book(cap, ())


def reserve(book: Book, micros: int, now: int, event_id: str) -> Book:
    """Hold worst-case micros before a model call. The prior book is unchanged."""
    rows, charged = _project(book)
    ident = _event_id(event_id)
    epoch = _now(now)
    # A zero hold would let the call through without touching the cap.
    amount = _micros(micros, lo=1)
    if ident in rows:
        raise Refuse("DUP_EVENT", "event_id already used")
    # Same shape as SpendGate: deny before the call when the hold would pass the cap.
    # The chain, not this fold, is the authority if the two later disagree.
    if charged + amount > book.cap_usd_micros:
        raise Refuse("OVER_CAP", "reserve would pass the cap")
    event = Event("RESERVE", ident, amount, epoch)
    return Book(book.cap_usd_micros, book.events + (event,))


def settle(book: Book, event_id: str, micros: int, now: int) -> Book:
    """Replace an open hold with the measured micros. Measured may be lower."""
    rows, _charged = _project(book)
    ident = _event_id(event_id)
    epoch = _now(now)
    amount = _micros(micros, lo=0)
    row = rows.get(ident)
    if row is None or row.status != "open":
        raise Refuse("NO_RESERVE", "no open reserve")
    # Settling above the hold would spend money the reserve never locked.
    if amount > row.hold:
        raise Refuse("OVER_CAP", "settle above the reserve")
    event = Event("SETTLE", ident, amount, epoch)
    return Book(book.cap_usd_micros, book.events + (event,))


def release(book: Book, event_id: str, now: int) -> Book:
    """Drop an open hold. The reserve event stays in the fold."""
    rows, _charged = _project(book)
    ident = _event_id(event_id)
    epoch = _now(now)
    row = rows.get(ident)
    if row is None or row.status != "open":
        raise Refuse("NO_RESERVE", "no open reserve")
    event = Event("RELEASE", ident, 0, epoch)
    return Book(book.cap_usd_micros, book.events + (event,))


def _event_id(value: object) -> str:
    text = bound_text(value, limit=64, name="event_id")
    # A pasted key would land in repr(book). The id is a label, not key material.
    if secret_shape(text):
        raise Refuse("BOUND", "event_id")
    return text


def _now(value: object) -> int:
    return bound_int(value, lo=0, hi=_INT_HI, name="now")


def _micros(value: object, *, lo: int) -> int:
    return bound_int(value, lo=lo, hi=_INT_HI, name="micros")


def _project(book: Book) -> tuple[dict[str, _Row], int]:
    """Replay the fold. A log this API did not write is refused, not repaired."""
    if not isinstance(book, Book) or not isinstance(book.events, tuple):
        raise Refuse("BOUND", "book")
    cap = check_cap(book.cap_usd_micros)
    rows: dict[str, _Row] = {}
    charged = 0
    for ev in book.events:
        if not isinstance(ev, Event) or ev.kind not in ("RESERVE", "SETTLE", "RELEASE"):
            raise Refuse("BOUND", "book")
        # Same bounds as reserve/settle/release. A forged id must not reach repr.
        try:
            ident = _event_id(ev.event_id)
            micros = _micros(ev.micros, lo=0)
            _now(ev.epoch)
        except Refuse:
            raise Refuse("BOUND", "book") from None
        row = rows.get(ident)
        if ev.kind == "RESERVE":
            if row is not None or micros < 1:
                raise Refuse("BOUND", "book")
            charged += micros
            rows[ident] = _Row("open", micros, 0)
        elif ev.kind == "SETTLE":
            if row is None or row.status != "open" or micros > row.hold:
                raise Refuse("BOUND", "book")
            charged += micros - row.hold
            rows[ident] = _Row("settled", row.hold, micros)
        else:
            if row is None or row.status != "open" or micros != 0:
                raise Refuse("BOUND", "book")
            charged -= row.hold
            rows[ident] = _Row("released", row.hold, 0)
        # The cap binds every prefix. A later settle or release cannot hide an over-cap hold.
        if charged < 0 or charged > cap:
            raise Refuse("BOUND", "book")
    return rows, charged


__all__ = [
    "SCHEMA",
    "Book",
    "Event",
    "open_book",
    "release",
    "reserve",
    "settle",
]
