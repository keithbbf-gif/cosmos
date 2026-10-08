"""Deterministic rank over an in-memory tool catalog.

Exact name, then prefix, then a whitespace-normalized description substring.
At most eight hits. An unknown name refuses. An empty query refuses.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_text, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-tool_search/1"
POLICY_CAP: Final[int] = 8
QUERY_LIMIT: Final[int] = 512
MAX_NAME: Final[int] = 128
MAX_DESCRIPTION: Final[int] = 4_000
MAX_CATALOG: Final[int] = 4_096
REQUEST_LIMIT: Final[int] = 10_000
QUERY_BATCH_CAP: Final[int] = 16

_BAND_RANK: Final[dict[str, int]] = {"exact": 0, "prefix": 1, "description": 2}
_NAME_START: Final[frozenset[str]] = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
)
_NAME_BODY: Final[frozenset[str]] = _NAME_START | frozenset(".-")


def _gate_text(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE")
    return text


def _check_name(name: str) -> None:
    if name == "" or name[0] not in _NAME_START:
        raise Refuse("BAD_NAME")
    if any(char not in _NAME_BODY for char in name):
        raise Refuse("BAD_NAME")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _gate_query(query: object) -> str:
    normal = _norm(bound_text(query, QUERY_LIMIT))
    if normal == "":
        raise Refuse("EMPTY_QUERY")
    if secret_shape(normal):
        raise Refuse("SECRET_SHAPE")
    return normal


def _cap_int(value: object, lo: int, hi: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("BAD_CAP")
    if value < lo or value > hi:
        raise Refuse("BAD_CAP")
    return value


@dataclass(frozen=True, slots=True)
class ToolRecord:
    """One granted tool's name and description."""

    name: str
    description: str

    def __post_init__(self) -> None:
        name = _gate_text(self.name, MAX_NAME)
        description = _gate_text(self.description, MAX_DESCRIPTION)
        _check_name(name)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "description", description)


@dataclass(frozen=True, slots=True)
class ToolHit:
    """A ranked row and the band that selected it."""

    name: str
    description: str
    band: str

    def __post_init__(self) -> None:
        name = _gate_text(self.name, MAX_NAME)
        description = _gate_text(self.description, MAX_DESCRIPTION)
        band = _gate_text(self.band, 16)
        _check_name(name)
        if band not in _BAND_RANK:
            raise Refuse("BAD_BAND")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "band", band)


def _hit(name: str, description: str, band: str) -> ToolHit:
    """Build a hit from text that already passed the gate."""
    row = object.__new__(ToolHit)
    object.__setattr__(row, "name", name)
    object.__setattr__(row, "description", description)
    object.__setattr__(row, "band", band)
    return row


def _check_hits(hits: object, matched: int, applied: int) -> None:
    if not isinstance(hits, tuple):
        raise Refuse("BAD_CAP")
    if len(hits) != min(matched, applied):
        raise Refuse("BAD_CAP")
    seen: set[str] = set()
    last: tuple[int, str] | None = None
    for hit in hits:
        if not isinstance(hit, ToolHit):
            raise Refuse("BAD_HIT")
        if hit.name in seen:
            raise Refuse("DUPLICATE_NAME")
        seen.add(hit.name)
        rank = _BAND_RANK.get(hit.band)
        if rank is None:
            raise Refuse("BAD_BAND")
        key = (rank, hit.name)
        if last is not None and key <= last:
            raise Refuse("BAD_ORDER")
        last = key


def _check_result(
    query: str,
    hits: object,
    matched: object,
    cap: object,
    requested: object,
    applied: object,
) -> None:
    if query == "":
        raise Refuse("EMPTY_QUERY")
    _cap_int(cap, POLICY_CAP, POLICY_CAP)
    matched_n = _cap_int(matched, 0, MAX_CATALOG)
    requested_n = _cap_int(requested, 1, REQUEST_LIMIT)
    applied_n = _cap_int(applied, 1, POLICY_CAP)
    expected = POLICY_CAP if requested_n > POLICY_CAP else requested_n
    if applied_n != expected:
        raise Refuse("BAD_CAP")
    _check_hits(hits, matched_n, applied_n)


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Hits, the policy cap, and the limit that was actually applied."""

    query: str
    hits: tuple[ToolHit, ...]
    matched: int
    cap: int
    requested: int
    applied: int

    def __post_init__(self) -> None:
        query = _gate_query(self.query)
        _check_result(query, self.hits, self.matched, self.cap, self.requested, self.applied)
        object.__setattr__(self, "query", query)


def _result(
    query: str,
    hits: tuple[ToolHit, ...],
    matched: int,
    requested: int,
    applied: int,
) -> SearchResult:
    _check_result(query, hits, matched, POLICY_CAP, requested, applied)
    row = object.__new__(SearchResult)
    object.__setattr__(row, "query", query)
    object.__setattr__(row, "hits", hits)
    object.__setattr__(row, "matched", matched)
    object.__setattr__(row, "cap", POLICY_CAP)
    object.__setattr__(row, "requested", requested)
    object.__setattr__(row, "applied", applied)
    return row


def _index(catalog: object) -> dict[str, ToolRecord]:
    if isinstance(catalog, (str, bytes, bytearray)) or not isinstance(catalog, Sequence):
        raise Refuse("BAD_CATALOG")
    if len(catalog) > MAX_CATALOG:
        raise Refuse("CATALOG_CAP", str(MAX_CATALOG))
    by_name: dict[str, ToolRecord] = {}
    for item in catalog:
        if not isinstance(item, ToolRecord):
            raise Refuse("BAD_CATALOG")
        if item.name in by_name:
            raise Refuse("DUPLICATE_NAME")
        by_name[item.name] = item
    return by_name


def freeze(catalog: object) -> tuple[ToolRecord, ...]:
    """Validate `catalog` and return the same records in input order."""
    return tuple(_index(catalog).values())


def lookup(catalog: object, name: object) -> ToolRecord:
    """Return the granted record named `name`. An unknown name refuses."""
    by_name = _index(catalog)
    text = _gate_text(name, MAX_NAME)
    _check_name(text)
    found = by_name.get(text)
    if found is None:
        raise Refuse("UNKNOWN_TOOL")
    return found


def _limits(limit: object | None) -> tuple[int, int]:
    """Return `(requested, applied)`. Applied never exceeds the policy cap."""
    if limit is None:
        return (POLICY_CAP, POLICY_CAP)
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise Refuse("NOT_INT")
    if limit < 1 or limit > REQUEST_LIMIT:
        raise Refuse("OUT_OF_RANGE", f"1..{REQUEST_LIMIT}")
    applied = POLICY_CAP if limit > POLICY_CAP else limit
    return (limit, applied)


def _rank(name: str, description_norm: str, query: str) -> tuple[int, str] | None:
    if name == query:
        return (0, "exact")
    if name.startswith(query):
        return (1, "prefix")
    if query in description_norm:
        return (2, "description")
    return None


def _row_key(row: tuple[int, str, ToolHit]) -> tuple[int, str]:
    return (row[0], row[1])


def _prepare(by_name: dict[str, ToolRecord]) -> tuple[tuple[ToolRecord, str], ...]:
    return tuple((tool, _norm(tool.description)) for tool in by_name.values())


def _rank_text(
    prepared: tuple[tuple[ToolRecord, str], ...],
    text: str,
    requested: int,
    applied: int,
) -> SearchResult:
    found: list[tuple[int, str, ToolHit]] = []
    for tool, description_norm in prepared:
        ranked = _rank(tool.name, description_norm, text)
        if ranked is None:
            continue
        order, band = ranked
        found.append((order, tool.name, _hit(tool.name, tool.description, band)))
    found.sort(key=_row_key)
    hits = tuple(row[2] for row in found[:applied])
    return _result(text, hits, len(found), requested, applied)


def search(catalog: object, query: object, limit: object | None = None) -> SearchResult:
    """Rank `catalog` for one query. A limit above the policy cap is ignored."""
    prepared = _prepare(_index(catalog))
    text = _gate_query(query)
    requested, applied = _limits(limit)
    return _rank_text(prepared, text, requested, applied)


def _query_list(queries: object) -> tuple[object, ...]:
    if isinstance(queries, (str, bytes, bytearray)) or not isinstance(queries, Sequence):
        raise Refuse("BAD_QUERIES")
    if len(queries) == 0:
        raise Refuse("EMPTY_QUERY")
    if len(queries) > QUERY_BATCH_CAP:
        raise Refuse("QUERY_CAP", str(QUERY_BATCH_CAP))
    return tuple(queries)


def search_many(
    catalog: object,
    queries: object,
    limit: object | None = None,
) -> tuple[SearchResult, ...]:
    """Rank each query on one index. `limit` applies per query."""
    raw = _query_list(queries)
    prepared = _prepare(_index(catalog))
    texts = tuple(_gate_query(query) for query in raw)
    requested, applied = _limits(limit)
    return tuple(_rank_text(prepared, text, requested, applied) for text in texts)


__all__ = [
    "MAX_CATALOG",
    "MAX_DESCRIPTION",
    "MAX_NAME",
    "POLICY_CAP",
    "QUERY_BATCH_CAP",
    "QUERY_LIMIT",
    "REQUEST_LIMIT",
    "SCHEMA",
    "SearchResult",
    "ToolHit",
    "ToolRecord",
    "freeze",
    "lookup",
    "search",
    "search_many",
]
