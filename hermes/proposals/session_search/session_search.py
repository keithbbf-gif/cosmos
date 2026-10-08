"""Owner-scoped recall over caller-supplied turns.

The projection is memory only. A search before rebuild is UNMEASURED.
A path check never creates a database file.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from cosmos_hermes import PathJail, Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA: Final = "cosmos-hermes-session_search/1"
POLICY_CAP: Final = 50
DEFAULT_LIMIT: Final = 10
INDEX_CAP: Final = 4096
PAGE_TOKENS: Final = 8192
MAX_TERMS: Final = 16
MAX_SEQ: Final = 1_000_000_000
_LABEL_LIMIT: Final = 256
_CAPTAIN: Final = "captain:"

_WORD: Final = re.compile(r"\w+")
_FORBIDDEN: Final = re.compile("[*'\"]")
_SEGMENT: Final = re.compile(r"[A-Za-z0-9._-]{1,64}")
_DOT_NAMES: Final = frozenset({".", ".."})


@dataclass(frozen=True, slots=True)
class Turn:
    """One caller-supplied turn. Text is stored only after redact."""

    owner: str
    session: str
    text: str
    seq: int = 0

    def __post_init__(self) -> None:
        owner = _label(self.owner, "BAD_TURN")
        session = _label(self.session, "BAD_TURN")
        text = _message(self.text)
        seq = bound_int(self.seq, 0, MAX_SEQ)
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session", session)
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "seq", seq)


@dataclass(frozen=True, slots=True)
class Hit:
    """One ranked hit. `place` starts at 1. `weight` is higher for a closer match."""

    owner: str
    session: str
    text: str
    seq: int
    weight: int
    place: int


@dataclass(frozen=True, slots=True)
class IndexState:
    """A measured projection. `cap` is the search page cap, not a raised caller cap."""

    schema: str
    count: int
    cap: int
    index_cap: int
    digest: str


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Ranked hits for one principal. `limit` is the applied page size."""

    schema: str
    cap: int
    page_tokens: int
    limit: int
    requested: int
    terms: tuple[str, ...]
    matched: int
    hits: tuple[Hit, ...]


@dataclass(frozen=True, slots=True)
class _Row:
    turn: Turn
    counts: dict[str, int]
    tokens: int
    ordinal: int


@dataclass(frozen=True, slots=True)
class _Scored:
    turn: Turn
    weight: int
    tokens: int
    ordinal: int


def _label(value: object, code: str) -> str:
    text = bound_text(value, _LABEL_LIMIT)
    if text == "" or text != text.strip():
        raise Refuse(code)
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _token_counts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for token in _WORD.findall(text):
        folded = token.casefold()
        counts[folded] = counts.get(folded, 0) + 1
    return counts


def _message(value: object) -> str:
    raw = bound_text(value)
    if raw.strip() == "":
        raise Refuse("BAD_TURN")
    stored = redact(raw) if secret_shape(raw) else raw
    if not _token_counts(stored):
        raise Refuse("BAD_TURN")
    return stored


def _principal(value: object) -> str:
    return _label(value, "BAD_PRINCIPAL")


def _query(value: object) -> tuple[tuple[str, ...], tuple[str, ...]]:
    raw = bound_text(value)
    if secret_shape(raw):
        raise Refuse("SECRET")
    if _FORBIDDEN.search(raw) is not None:
        raise Refuse("BAD_QUERY")
    words = tuple(_WORD.findall(raw))
    if not words or len(words) > MAX_TERMS:
        raise Refuse("BAD_QUERY")
    folded = tuple(word.casefold() for word in words)
    return words, folded


def _limits(limit: object) -> tuple[int, int]:
    """Return `(requested, applied)`. Applied never exceeds the policy cap."""
    if limit is None:
        return DEFAULT_LIMIT, DEFAULT_LIMIT
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise Refuse("NOT_INT")
    if limit < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{POLICY_CAP}")
    applied = POLICY_CAP if limit > POLICY_CAP else limit
    return limit, bound_int(applied, 1, POLICY_CAP)


def _sees_all(principal: str) -> bool:
    return principal.startswith(_CAPTAIN)


def _weight(counts: dict[str, int], folded: tuple[str, ...]) -> int | None:
    total = 0
    for term in folded:
        count = counts.get(term, 0)
        if count == 0:
            return None
        total += count
    return total


def _sort_key(item: _Scored) -> tuple[int, int, int, str, int]:
    return (-item.weight, item.tokens, item.ordinal, item.turn.session, item.turn.seq)


def _page(scored: Sequence[_Scored], applied: int) -> tuple[Hit, ...]:
    chosen: list[Hit] = []
    remaining = PAGE_TOKENS
    for item in scored:
        if len(chosen) == applied:
            break
        if item.tokens > remaining:
            continue
        remaining -= item.tokens
        turn = item.turn
        chosen.append(
            Hit(
                owner=turn.owner,
                session=turn.session,
                text=turn.text,
                seq=turn.seq,
                weight=item.weight,
                place=len(chosen) + 1,
            )
        )
    return tuple(chosen)


def _utf8(text: str) -> bytes:
    try:
        return text.encode("utf-8")
    except UnicodeError as exc:
        raise Refuse("BAD_TURN") from exc


def _digest(rows: tuple[_Row, ...]) -> str:
    hasher = hashlib.sha256()
    for row in rows:
        turn = row.turn
        hasher.update(_utf8(turn.owner))
        hasher.update(b"\0")
        hasher.update(_utf8(turn.session))
        hasher.update(b"\0")
        hasher.update(str(turn.seq).encode("ascii"))
        hasher.update(b"\0")
        hasher.update(_utf8(turn.text))
        hasher.update(b"\n")
    return hasher.hexdigest()


def _project(turns: object) -> tuple[_Row, ...]:
    if isinstance(turns, (str, bytes, bytearray, memoryview)) or not isinstance(turns, Sequence):
        raise Refuse("BAD_TURN")
    if len(turns) > INDEX_CAP:
        raise Refuse("OVER_COUNT", str(INDEX_CAP))
    seen: set[tuple[str, int]] = set()
    owners: dict[str, str] = {}
    rows: list[_Row] = []
    for ordinal, item in enumerate(turns):
        if not isinstance(item, Turn):
            raise Refuse("BAD_TURN")
        clean = Turn(item.owner, item.session, item.text, item.seq)
        key = (clean.session, clean.seq)
        if key in seen:
            raise Refuse("DUPLICATE")
        prior = owners.get(clean.session)
        if prior is None:
            owners[clean.session] = clean.owner
        elif not const_eq(prior, clean.owner):
            raise Refuse("SESSION_OWNER")
        seen.add(key)
        counts = _token_counts(clean.text)
        rows.append(_Row(turn=clean, counts=counts, tokens=sum(counts.values()), ordinal=ordinal))
    return tuple(rows)


class SessionSearch:
    """In-memory recall projection. Not the ledger and not a database file."""

    __slots__ = ("_digest", "_rows")

    def __init__(self) -> None:
        self._rows: tuple[_Row, ...] | None = None
        self._digest: str | None = None

    def __repr__(self) -> str:
        if self._rows is None:
            return "SessionSearch(measured=False)"
        return f"SessionSearch(measured=True, count={len(self._rows)})"

    def rebuild(self, turns: object) -> IndexState:
        """Replace the projection. A refusal leaves the previous rows in place."""
        rows = _project(turns)
        digest = _digest(rows)
        self._rows = rows
        self._digest = digest
        return IndexState(
            schema=SCHEMA,
            count=len(rows),
            cap=POLICY_CAP,
            index_cap=INDEX_CAP,
            digest=digest,
        )

    def clear(self) -> None:
        """Drop the projection. The next search is UNMEASURED."""
        self._rows = None
        self._digest = None

    def records(self) -> tuple[Turn, ...]:
        """Return the measured turns in rebuild order."""
        rows = self._rows
        if rows is None:
            raise Refuse("UNMEASURED")
        return tuple(row.turn for row in rows)

    def search(self, principal: object, query: object, limit: object = None) -> SearchResult:
        """Rank visible turns whose tokens contain every query word."""
        rows = self._rows
        if rows is None:
            raise Refuse("UNMEASURED")
        who = _principal(principal)
        terms, folded = _query(query)
        requested, applied = _limits(limit)
        captain = _sees_all(who)
        scored: list[_Scored] = []
        for row in rows:
            if not captain and not const_eq(who, row.turn.owner):
                continue
            weight = _weight(row.counts, folded)
            if weight is None:
                continue
            scored.append(
                _Scored(turn=row.turn, weight=weight, tokens=row.tokens, ordinal=row.ordinal)
            )
        scored.sort(key=_sort_key)
        return SearchResult(
            schema=SCHEMA,
            cap=POLICY_CAP,
            page_tokens=PAGE_TOKENS,
            limit=applied,
            requested=requested,
            terms=terms,
            matched=len(scored),
            hits=_page(scored, applied),
        )


def stat_index(root: object, name: object) -> None:
    """A missing database path is UNMEASURED. This call does not create a file."""
    if not isinstance(root, str) or not isinstance(name, str):
        raise Refuse("BAD_PATH")
    if secret_shape(root) or secret_shape(name):
        raise Refuse("SECRET")
    if name in _DOT_NAMES or _SEGMENT.fullmatch(name) is None:
        raise Refuse("BAD_PATH")
    jail = PathJail((root,))
    target = jail.contain(str(Path(root) / name))
    if target.exists():
        raise Refuse("FOREIGN_INDEX")
    raise Refuse("UNMEASURED")


_DEFAULT = SessionSearch()


def rebuild(turns: object) -> IndexState:
    """Replace the process-local projection."""
    return _DEFAULT.rebuild(turns)


def search(principal: object, query: object, limit: object = None) -> SearchResult:
    """Search the process-local projection."""
    return _DEFAULT.search(principal, query, limit)


def clear() -> None:
    """Drop the process-local projection."""
    _DEFAULT.clear()


def records() -> tuple[Turn, ...]:
    """Return turns from the process-local projection."""
    return _DEFAULT.records()


__all__ = [
    "DEFAULT_LIMIT",
    "INDEX_CAP",
    "MAX_TERMS",
    "PAGE_TOKENS",
    "POLICY_CAP",
    "SCHEMA",
    "Hit",
    "IndexState",
    "SearchResult",
    "SessionSearch",
    "Turn",
    "clear",
    "rebuild",
    "records",
    "search",
    "stat_index",
]
