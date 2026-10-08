"""Deterministic note select inside a byte budget. No model call."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-curator/1"
POLICY_BUDGET: Final[int] = 1_000_000
ID_LIMIT: Final[int] = 64
TEXT_LIMIT: Final[int] = 8_000
PRIORITY_MIN: Final[int] = -1_000
PRIORITY_MAX: Final[int] = 1_000

_ID: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_REASONS: Final[frozenset[str]] = frozenset({"OVERSIZE", "SECRET"})
_INVISIBLE: Final[frozenset[str]] = frozenset(
    (
        "\u007f",
        "\u200b",
        "\u200c",
        "\u200d",
        "\u200e",
        "\u200f",
        "\u2028",
        "\u2029",
        "\u202a",
        "\u202b",
        "\u202c",
        "\u202d",
        "\u202e",
        "\u2060",
        "\u2066",
        "\u2067",
        "\u2068",
        "\u2069",
        "\ufeff",
    )
) | frozenset(chr(code) for code in range(0x20) if code not in (0x09, 0x0A))

__all__ = [
    "SCHEMA",
    "POLICY_BUDGET",
    "ID_LIMIT",
    "TEXT_LIMIT",
    "PRIORITY_MIN",
    "PRIORITY_MAX",
    "Candidate",
    "Drop",
    "Selection",
    "Records",
    "select",
    "curate",
    "records",
    "rebuild",
]


def _visible(text: str) -> None:
    for char in text:
        if char in _INVISIBLE:
            raise Refuse("INVISIBLE")


def _utf8(text: str) -> bytes:
    try:
        return text.encode("utf-8")
    except UnicodeEncodeError:
        raise Refuse("NOT_TEXT") from None


def _check_candidate(
    note_id: object,
    text: object,
    priority: object,
    *,
    allow_secret_text: bool,
) -> None:
    shown = bound_text(note_id, ID_LIMIT)
    body = bound_text(text, TEXT_LIMIT)
    bound_int(priority, PRIORITY_MIN, PRIORITY_MAX)
    if shown == "" or body == "":
        raise Refuse("EMPTY")
    if secret_shape(shown):
        raise Refuse("SECRET")
    _visible(shown)
    _visible(body)
    if _ID.fullmatch(shown) is None:
        raise Refuse("BAD_ID")
    if not allow_secret_text and secret_shape(body):
        raise Refuse("SECRET")
    _utf8(body)


def _number(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    return value


def _requested_budget(value: object) -> int:
    number = _number(value)
    if number < 0:
        raise Refuse("OUT_OF_RANGE", f"0..{POLICY_BUDGET}")
    if number > POLICY_BUDGET:
        return POLICY_BUDGET
    return number


def _schema(value: object) -> str:
    shown = bound_text(value, 64)
    if not const_eq(shown, SCHEMA):
        raise Refuse("MISMATCH")
    return SCHEMA


def _policy_cap(value: object) -> int:
    if _number(value) != POLICY_BUDGET:
        raise Refuse("MISMATCH")
    return POLICY_BUDGET


def _recorded_budget(value: object) -> int:
    number = _number(value)
    if number < 0 or number > POLICY_BUDGET:
        raise Refuse("MISMATCH")
    return number


def _recorded_used(value: object) -> int:
    number = _number(value)
    if number < 0 or number > POLICY_BUDGET:
        raise Refuse("STALE")
    return number


def _digest_token(value: object) -> str:
    shown = bound_text(value, 64)
    if _HEX.fullmatch(shown) is None:
        raise Refuse("BAD_RECORD")
    return shown


@dataclass(frozen=True, slots=True, repr=False)
class Candidate:
    """One note. Secret-shaped text is dropped by select and omitted from repr."""

    id: str
    text: str
    priority: int

    def __post_init__(self) -> None:
        _check_candidate(self.id, self.text, self.priority, allow_secret_text=True)

    def __repr__(self) -> str:
        return (
            f"Candidate(id={redact(self.id)!r}, text={redact(self.text)!r}, "
            f"priority={self.priority})"
        )


@dataclass(frozen=True, slots=True)
class Drop:
    """A note that was not kept. Text is absent, including secret text."""

    id: str
    reason: str

    def __post_init__(self) -> None:
        shown = bound_text(self.id, ID_LIMIT)
        reason = bound_text(self.reason, 16)
        if shown == "" or reason == "":
            raise Refuse("EMPTY")
        if secret_shape(shown) or secret_shape(reason):
            raise Refuse("SECRET")
        if _ID.fullmatch(shown) is None:
            raise Refuse("BAD_ID")
        if reason not in _REASONS:
            raise Refuse("BAD_RECORD")
        object.__setattr__(self, "id", shown)
        object.__setattr__(self, "reason", reason)


@dataclass(frozen=True, slots=True)
class Selection:
    """Chosen notes, the policy cap, and the digest of this projection."""

    schema: str
    cap: int
    budget: int
    chosen: tuple[Candidate, ...]
    dropped: tuple[Drop, ...]
    used: int
    digest: str


@dataclass(frozen=True, slots=True)
class Records:
    """Public snapshot. `rebuild` is the check that it still packs."""

    schema: str
    cap: int
    budget: int
    chosen: tuple[Candidate, ...]
    dropped: tuple[Drop, ...]
    used: int
    digest: str


def _rank(item: Candidate) -> tuple[int, str]:
    return (-item.priority, item.id)


def _take(candidates: object) -> tuple[Candidate, ...]:
    if type(candidates) is not tuple:
        raise Refuse("BAD_ITEMS")
    if len(candidates) == 0:
        raise Refuse("EMPTY")
    rows: list[Candidate] = []
    seen: set[str] = set()
    for item in candidates:
        if type(item) is not Candidate:
            raise Refuse("BAD_ITEMS")
        if item.id in seen:
            raise Refuse("DUP_ID")
        seen.add(item.id)
        rows.append(item)
    return tuple(rows)


def _pack(
    rows: tuple[Candidate, ...],
    budget: int,
    *,
    drop_secrets: bool,
) -> tuple[tuple[Candidate, ...], tuple[Drop, ...], int]:
    chosen: list[Candidate] = []
    dropped: list[Drop] = []
    used = 0
    for item in sorted(rows, key=_rank):
        if drop_secrets and secret_shape(item.text):
            dropped.append(Drop(item.id, "SECRET"))
            continue
        size = len(_utf8(item.text))
        # Skip this note. A later smaller note may still fit.
        if used + size > budget:
            dropped.append(Drop(item.id, "OVERSIZE"))
            continue
        chosen.append(item)
        used += size
    return tuple(chosen), tuple(dropped), used


def _digest(
    budget: int,
    used: int,
    chosen: tuple[Candidate, ...],
    dropped: tuple[Drop, ...],
) -> str:
    running = hashlib.sha256()
    running.update(SCHEMA.encode("ascii"))
    running.update(b"\0")
    running.update(str(POLICY_BUDGET).encode("ascii"))
    running.update(b"\0")
    running.update(str(budget).encode("ascii"))
    running.update(b"\0")
    running.update(str(used).encode("ascii"))
    for note in chosen:
        running.update(b"\0c\0")
        running.update(_utf8(note.id))
        running.update(b"\0")
        running.update(str(note.priority).encode("ascii"))
        running.update(b"\0")
        running.update(_utf8(note.text))
    for drop in dropped:
        running.update(b"\0d\0")
        running.update(_utf8(drop.id))
        running.update(b"\0")
        running.update(_utf8(drop.reason))
    return running.hexdigest()


def _choose(
    candidates: object,
    budget_bytes: object,
) -> tuple[int, tuple[Candidate, ...], tuple[Drop, ...], int]:
    rows = _take(candidates)
    budget = _requested_budget(budget_bytes)
    chosen, dropped, used = _pack(rows, budget, drop_secrets=True)
    return budget, chosen, dropped, used


def select(candidates: object, budget_bytes: object) -> tuple[Candidate, ...]:
    """Chosen notes, highest priority first, then id. A zero budget yields ()."""
    return _choose(candidates, budget_bytes)[1]


def curate(candidates: object, budget_bytes: object) -> Selection:
    """Same notes as select, plus the policy cap, drops, bytes used, and digest."""
    budget, chosen, dropped, used = _choose(candidates, budget_bytes)
    return Selection(
        SCHEMA,
        POLICY_BUDGET,
        budget,
        chosen,
        dropped,
        used,
        _digest(budget, used, chosen, dropped),
    )


def records(selection: object) -> Records:
    """Copy the public snapshot of a selection."""
    if type(selection) is not Selection:
        raise Refuse("BAD_RECORD")
    return Records(
        selection.schema,
        selection.cap,
        selection.budget,
        selection.chosen,
        selection.dropped,
        selection.used,
        selection.digest,
    )


def _public_chosen(value: object) -> tuple[Candidate, ...]:
    if type(value) is not tuple:
        raise Refuse("BAD_RECORD")
    rows: list[Candidate] = []
    seen: set[str] = set()
    for item in value:
        if type(item) is not Candidate:
            raise Refuse("BAD_RECORD")
        _check_candidate(item.id, item.text, item.priority, allow_secret_text=False)
        if item.id in seen:
            raise Refuse("STALE")
        seen.add(item.id)
        rows.append(item)
    return tuple(rows)


def _public_dropped(value: object, chosen_ids: set[str]) -> tuple[Drop, ...]:
    if type(value) is not tuple:
        raise Refuse("BAD_RECORD")
    rows: list[Drop] = []
    seen = set(chosen_ids)
    for item in value:
        if type(item) is not Drop:
            raise Refuse("BAD_RECORD")
        if item.reason not in _REASONS or _ID.fullmatch(item.id) is None:
            raise Refuse("BAD_RECORD")
        if secret_shape(item.id):
            raise Refuse("SECRET")
        if item.id in seen:
            raise Refuse("STALE")
        seen.add(item.id)
        rows.append(item)
    return tuple(rows)


def rebuild(bundle: object) -> Selection:
    """Replay a snapshot. A broken digest or a set that does not fit is STALE."""
    if type(bundle) is not Records:
        raise Refuse("BAD_RECORD")
    schema = _schema(bundle.schema)
    cap = _policy_cap(bundle.cap)
    budget = _recorded_budget(bundle.budget)
    chosen = _public_chosen(bundle.chosen)
    dropped = _public_dropped(bundle.dropped, {item.id for item in chosen})
    used = _recorded_used(bundle.used)
    packed, extra, actual = _pack(chosen, budget, drop_secrets=False)
    if extra != () or packed != chosen or actual != used:
        raise Refuse("STALE")
    digest = _digest(budget, actual, chosen, dropped)
    if not const_eq(digest, _digest_token(bundle.digest)):
        raise Refuse("STALE")
    return Selection(schema, cap, budget, chosen, dropped, used, digest)
