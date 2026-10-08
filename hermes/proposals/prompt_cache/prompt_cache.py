"""Frozen prompt prefix. The tail is not part of the cache id.

No network. A cached-token count is stored only when the caller measured it.
A date or UUID in the prefix refuses. assume_hit never returns a count.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_bytes, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final = "cosmos-hermes-prompt_cache/1"
PREFIX_CAP: Final = 262_144
TAIL_CAP: Final = 65_536
TOKEN_CAP: Final = 2_000_000
PIECE_CAP: Final = 64
_NAME_CAP: Final = 64
_ID_LEN: Final = 64
_KINDS: Final[frozenset[str]] = frozenset(("prefix", "tail"))

_DATE: Final[re.Pattern[str]] = re.compile(
    r"(?<![0-9])[0-9]{4}-[0-9]{2}-[0-9]{2}(?![0-9])"
)
_UUID: Final[re.Pattern[str]] = re.compile(
    r"(?i)(?<![0-9a-f])[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?![0-9a-f])"
)


def _digest(prefix: bytes) -> str:
    return hashlib.sha256(prefix).hexdigest()


def _recorded_cap(requested: object) -> int:
    if isinstance(requested, bool) or not isinstance(requested, int):
        raise Refuse("NOT_INT")
    if requested < 1:
        raise Refuse("BAD_LIMIT")
    if requested > PREFIX_CAP:
        return PREFIX_CAP
    return requested


def _scan_prefix(raw: bytes) -> None:
    if len(raw) == 0:
        raise Refuse("EMPTY")
    if b"\x00" in raw:
        raise Refuse("NULL_BYTE")
    text = raw.decode("latin-1")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _DATE.search(text) is not None:
        raise Refuse("VOLATILE_PREFIX", "date")
    if _UUID.search(text) is not None:
        raise Refuse("VOLATILE_PREFIX", "uuid")


def _scan_tail(raw: bytes) -> None:
    if b"\x00" in raw:
        raise Refuse("NULL_BYTE")
    if len(raw) == 0:
        return
    if secret_shape(raw.decode("latin-1")):
        raise Refuse("SECRET")


def _name(value: object) -> str:
    if not isinstance(value, str):
        raise Refuse("BAD_PLAN")
    name = bound_text(value, _NAME_CAP)
    if name == "":
        raise Refuse("EMPTY")
    if secret_shape(name):
        raise Refuse("SECRET")
    return name


def _kind(value: object) -> str:
    if not isinstance(value, str) or value not in _KINDS:
        raise Refuse("BAD_KIND")
    return value


def _names(value: object) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, tuple):
        raise Refuse("BAD_PLAN")
    seen: set[str] = set()
    out: list[str] = []
    for item in value:
        name = _name(item)
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        out.append(name)
    return tuple(out)


def _rows(value: object) -> tuple[Piece, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, (list, tuple)):
        raise Refuse("BAD_PLAN")
    if len(value) == 0:
        raise Refuse("EMPTY")
    if len(value) > PIECE_CAP:
        raise Refuse("OVERSIZE", str(PIECE_CAP))
    rows: list[Piece] = []
    for item in value:
        if not isinstance(item, Piece):
            raise Refuse("BAD_PLAN")
        rows.append(item)
    return tuple(rows)


@dataclass(frozen=True, slots=True)
class Piece:
    """One named block. `kind` is `prefix` or `tail`. The body is not yet a cache."""

    name: str
    kind: str
    body: bytes

    def __post_init__(self) -> None:
        name = _name(self.name)
        kind = _kind(self.kind)
        body = bound_bytes(self.body, PREFIX_CAP)
        if len(body) == 0:
            raise Refuse("EMPTY")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "body", body)

    def __repr__(self) -> str:
        return f"Piece(name={self.name!r}, kind={self.kind!r}, body_len={len(self.body)})"


def _install(
    prefix: bytes,
    tail: bytes,
    tokens: int | None,
    cap: int,
    cache_id: str,
) -> PrefixCache:
    obj = PrefixCache.__new__(PrefixCache)
    object.__setattr__(obj, "schema", SCHEMA)
    object.__setattr__(obj, "cache_id", cache_id)
    object.__setattr__(obj, "prefix", prefix)
    object.__setattr__(obj, "tail", tail)
    object.__setattr__(obj, "cached_tokens", tokens)
    object.__setattr__(obj, "cap", cap)
    return obj


@dataclass(frozen=True, slots=True)
class PrefixCache:
    """One frozen prefix plus an append-only tail. `cap` is policy."""

    schema: str
    cache_id: str
    prefix: bytes
    tail: bytes
    cached_tokens: int | None
    cap: int

    def __post_init__(self) -> None:
        if not isinstance(self.schema, str) or self.schema != SCHEMA:
            raise Refuse("BAD_CACHE")
        cap = _recorded_cap(self.cap)
        prefix = bound_bytes(self.prefix, cap)
        _scan_prefix(prefix)
        if not isinstance(self.cache_id, str) or len(self.cache_id) != _ID_LEN:
            raise Refuse("BAD_ID")
        digest = _digest(prefix)
        if not const_eq(self.cache_id, digest):
            raise Refuse("BAD_ID")
        tail = bound_bytes(self.tail, TAIL_CAP)
        _scan_tail(tail)
        tokens = None if self.cached_tokens is None else bound_int(self.cached_tokens, 0, TOKEN_CAP)
        object.__setattr__(self, "cap", cap)
        object.__setattr__(self, "prefix", prefix)
        object.__setattr__(self, "tail", tail)
        object.__setattr__(self, "cached_tokens", tokens)

    def __repr__(self) -> str:
        measured = "None" if self.cached_tokens is None else str(self.cached_tokens)
        return (
            f"PrefixCache(schema={self.schema!r}, cache_id={self.cache_id!r}, "
            f"prefix_len={len(self.prefix)}, tail_len={len(self.tail)}, "
            f"cached_tokens={measured}, cap={self.cap})"
        )

    def append(self, tail: object) -> PrefixCache:
        """Append volatile tail bytes. The cache id stays the prefix digest."""
        piece = bound_bytes(tail, TAIL_CAP)
        if len(piece) == 0:
            raise Refuse("EMPTY")
        if len(self.tail) + len(piece) > TAIL_CAP:
            _scan_tail(piece)
            raise Refuse("OVERSIZE", str(TAIL_CAP))
        merged = self.tail + piece
        _scan_tail(merged)
        return _install(self.prefix, merged, self.cached_tokens, self.cap, self.cache_id)

    def record_hit(self, measured: object) -> PrefixCache:
        """Store the caller-supplied cached token count. Does not guess."""
        count = bound_int(measured, 0, TOKEN_CAP)
        return _install(self.prefix, self.tail, count, self.cap, self.cache_id)

    def measured(self) -> int:
        """Return the stored count. Unmeasured is ASSUMED_HIT, not zero."""
        if self.cached_tokens is None:
            raise Refuse("ASSUMED_HIT")
        return self.cached_tokens

    def assume_hit(self) -> None:
        """Refuse a hit that was not supplied as a measured count."""
        raise Refuse("ASSUMED_HIT")


@dataclass(frozen=True, slots=True)
class CachePlan:
    """Prefix id plus the block names that landed or were skipped."""

    schema: str
    cache: PrefixCache
    kept: tuple[str, ...]
    skipped: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.schema, str) or self.schema != SCHEMA:
            raise Refuse("BAD_CACHE")
        if not isinstance(self.cache, PrefixCache):
            raise Refuse("BAD_CACHE")
        kept = _names(self.kept)
        skipped = _names(self.skipped)
        if not kept:
            raise Refuse("EMPTY")
        if not set(kept).isdisjoint(skipped):
            raise Refuse("DUPLICATE")
        object.__setattr__(self, "kept", kept)
        object.__setattr__(self, "skipped", skipped)

    def __repr__(self) -> str:
        cache = self.cache
        return (
            f"CachePlan(schema={self.schema!r}, cache_id={cache.cache_id!r}, "
            f"kept={self.kept!r}, skipped={self.skipped!r}, "
            f"prefix_len={len(cache.prefix)}, tail_len={len(cache.tail)}, cap={cache.cap})"
        )


def freeze(prefix: object, requested_cap: object = PREFIX_CAP) -> PrefixCache:
    """Freeze prefix bytes. The id is their sha256. Dates and UUIDs refuse."""
    cap = _recorded_cap(requested_cap)
    raw = bound_bytes(prefix, cap)
    _scan_prefix(raw)
    return _install(raw, b"", None, cap, _digest(raw))


def append(cache: object, tail: object) -> PrefixCache:
    """Append volatile tail bytes. The cache id stays the prefix digest."""
    return _require(cache).append(tail)


def record_hit(cache: object, measured: object) -> PrefixCache:
    """Store the caller-supplied cached token count. Does not guess."""
    return _require(cache).record_hit(measured)


def measured(cache: object) -> int:
    """Return the stored count. Unmeasured is ASSUMED_HIT, not zero."""
    return _require(cache).measured()


def assume_hit() -> None:
    """Refuse a hit that was not supplied as a measured count."""
    raise Refuse("ASSUMED_HIT")


def plan(pieces: object, requested_cap: object = PREFIX_CAP) -> CachePlan:
    """Join prefix blocks that fit. Skip a block that does not fit.

    A date, UUID, or secret in a prefix block refuses, including when that
    block would not fit. Tail blocks may hold a date. The cache id is the
    sha256 of the kept prefix only.
    """
    cap = _recorded_cap(requested_cap)
    rows = _rows(pieces)
    seen: set[str] = set()
    prefix_parts: list[bytes] = []
    tail_parts: list[bytes] = []
    kept: list[str] = []
    skipped: list[str] = []
    used = 0
    tail_used = 0
    in_tail = False
    for piece in rows:
        raw = piece.body
        if not isinstance(raw, bytes):
            raise Refuse("NOT_BYTES")
        body = raw
        if piece.kind == "prefix":
            _scan_prefix(body)
        elif piece.kind == "tail":
            _scan_tail(body)
        else:
            raise Refuse("BAD_KIND")
        name = _name(piece.name)
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        if piece.kind == "prefix":
            if in_tail:
                raise Refuse("BAD_ORDER")
            if used + len(body) > cap:
                skipped.append(name)
                continue
            prefix_parts.append(body)
            kept.append(name)
            used += len(body)
            continue
        in_tail = True
        if tail_used + len(body) > TAIL_CAP:
            skipped.append(name)
            continue
        tail_parts.append(body)
        kept.append(name)
        tail_used += len(body)
    if not prefix_parts:
        raise Refuse("EMPTY")
    if len(prefix_parts) == 1:
        prefix = prefix_parts[0]
    else:
        # Join is a new string: a date or secret can start in one block and end in the next.
        prefix = b"".join(prefix_parts)
        _scan_prefix(prefix)
    if len(tail_parts) == 0:
        tail = b""
    elif len(tail_parts) == 1:
        tail = tail_parts[0]
    else:
        tail = b"".join(tail_parts)
        _scan_tail(tail)
    cache = _install(prefix, tail, None, cap, _digest(prefix))
    return CachePlan(SCHEMA, cache, tuple(kept), tuple(skipped))


def rebuild(cache: object) -> PrefixCache:
    """Re-validate a cache record and return the same public state."""
    current = _require(cache)
    return PrefixCache(
        schema=current.schema,
        cache_id=current.cache_id,
        prefix=current.prefix,
        tail=current.tail,
        cached_tokens=current.cached_tokens,
        cap=current.cap,
    )


def _require(cache: object) -> PrefixCache:
    if not isinstance(cache, PrefixCache):
        raise Refuse("BAD_CACHE")
    return cache


__all__ = [
    "PIECE_CAP",
    "PREFIX_CAP",
    "SCHEMA",
    "TAIL_CAP",
    "TOKEN_CAP",
    "CachePlan",
    "Piece",
    "PrefixCache",
    "append",
    "assume_hit",
    "freeze",
    "measured",
    "plan",
    "rebuild",
    "record_hit",
]
