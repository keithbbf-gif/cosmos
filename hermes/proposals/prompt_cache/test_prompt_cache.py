"""Prefix cache: frozen bytes, volatile tail, measured hits only. No network."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from prompt_cache import (
    PIECE_CAP,
    PREFIX_CAP,
    SCHEMA,
    TAIL_CAP,
    TOKEN_CAP,
    CachePlan,
    Piece,
    PrefixCache,
    append,
    assume_hit,
    freeze,
    measured,
    plan,
    rebuild,
    record_hit,
)

_PREFIX = b"stable prefix policy v2"
_UUID = b"123e4567-e89b-12d3-a456-426614174000"


def _digest(prefix: bytes) -> str:
    return hashlib.sha256(prefix).hexdigest()


def test_schema_freeze_append_and_id() -> None:
    cache = freeze(_PREFIX)
    assert SCHEMA == "cosmos-hermes-prompt_cache/1"
    assert cache.schema == SCHEMA
    assert cache.cache_id == _digest(_PREFIX)
    assert len(cache.cache_id) == 64
    assert cache.tail == b""
    assert cache.cached_tokens is None
    assert cache.cap == PREFIX_CAP
    assert freeze(_PREFIX) == cache
    assert freeze(_PREFIX, 64).cache_id == freeze(_PREFIX, 128).cache_id
    assert freeze(_PREFIX, 64).cap == 64
    assert freeze(_PREFIX, 128).cap == 128
    via_fn = append(cache, b"item one")
    via_method = cache.append(b"item one")
    assert via_fn == via_method
    assert via_fn.cache_id == cache.cache_id
    assert via_fn.prefix == _PREFIX
    assert via_fn.tail == b"item one"
    assert cache.tail == b""
    twice = append(via_fn, b" item two")
    assert twice.tail == b"item one item two"
    assert twice.cache_id == cache.cache_id
    assert via_fn.tail == b"item one"


def test_one_byte_change_changes_id() -> None:
    cache = freeze(_PREFIX)
    flipped = bytearray(_PREFIX)
    flipped[-1] ^= 0x01
    other = freeze(bytes(flipped))
    assert other.cache_id == _digest(bytes(flipped))
    assert other.cache_id != cache.cache_id
    assert freeze(_PREFIX[:-1] + bytes([_PREFIX[-1] ^ 0x01])).cache_id != cache.cache_id


def test_record_hit_stores_measured_count() -> None:
    cache = freeze(_PREFIX)
    miss = record_hit(cache, 0)
    assert miss.cached_tokens == 0
    assert miss.cache_id == cache.cache_id
    assert cache.cached_tokens is None
    hit = miss.record_hit(7265)
    assert hit.cached_tokens == 7265
    assert hit == record_hit(miss, 7265)
    kept = append(hit, b"the task")
    assert kept.cached_tokens == 7265
    assert kept.cache_id == cache.cache_id
    top = record_hit(cache, TOKEN_CAP)
    assert top.cached_tokens == TOKEN_CAP


def test_assume_hit_always_refuses() -> None:
    cache = freeze(_PREFIX)
    hit = record_hit(cache, 128)
    with pytest.raises(Refuse) as bare:
        assume_hit()
    assert bare.value.code == "ASSUMED_HIT"
    with pytest.raises(Refuse) as method:
        hit.assume_hit()
    assert method.value.code == "ASSUMED_HIT"
    assert hit.cached_tokens == 128


def test_volatile_date_and_uuid() -> None:
    samples = (
        b"2026-10-01",
        b"rules 2026-10-01 more",
        b"2026-10-01T18:41:41-05:00",
        _UUID,
        b"id " + _UUID.upper() + b" end",
        b"urn:uuid:123e4567-e89b-12d3-a456-426614174000",
        b"\xff2026-10-01",
    )
    for sample in samples:
        with pytest.raises(Refuse) as caught:
            freeze(sample)
        assert caught.value.code == "VOLATILE_PREFIX"
    allowed = freeze(b"\xffstable prefix policy v2")
    assert allowed.prefix == b"\xffstable prefix policy v2"
    clock = freeze(b"stable prefix at 18:41:41 policy v2")
    assert clock.cache_id == _digest(b"stable prefix at 18:41:41 policy v2")
    assert freeze(b"build 20261001 policy v2").cached_tokens is None
    assert freeze(b"123e4567e89b12d3a456426614174000").prefix.startswith(b"123e")


def test_tail_may_hold_a_date_or_uuid() -> None:
    cache = freeze(_PREFIX)
    dated = append(cache, b"ticket 2026-10-01 " + _UUID)
    assert dated.cache_id == cache.cache_id
    assert dated.tail == b"ticket 2026-10-01 " + _UUID


def test_secret_prefix_and_tail() -> None:
    cache = freeze(_PREFIX)
    with pytest.raises(Refuse) as prefix:
        freeze(b"token sk-livexxxxhere")
    assert prefix.value.code == "SECRET"
    with pytest.raises(Refuse) as dated_secret:
        freeze(b"api_key=2026-10-01")
    assert dated_secret.value.code == "SECRET"
    with pytest.raises(Refuse) as tail:
        append(cache, b"Authorization: Bearer abcdefghijk")
    assert tail.value.code == "SECRET"
    assert cache.tail == b""
    partial = append(cache, b"sk-")
    with pytest.raises(Refuse) as split:
        append(partial, b"abcdefghij")
    assert split.value.code == "SECRET"
    assert partial.tail == b"sk-"
    assert not secret_shape(repr(partial))


def test_repr_omits_prefix_body() -> None:
    cache = freeze(_PREFIX)
    text = repr(cache)
    assert "stable prefix policy v2" not in text
    assert cache.cache_id in text
    assert SCHEMA in text
    assert not secret_shape(text)


def test_empty_prefix_and_tail() -> None:
    with pytest.raises(Refuse) as prefix:
        freeze(b"")
    assert prefix.value.code == "EMPTY"
    cache = freeze(_PREFIX)
    with pytest.raises(Refuse) as tail:
        append(cache, b"")
    assert tail.value.code == "EMPTY"
    with pytest.raises(Refuse) as method:
        cache.append(b"")
    assert method.value.code == "EMPTY"
    digest = _digest(b"")
    with pytest.raises(Refuse) as built:
        PrefixCache(SCHEMA, digest, b"", b"", None, PREFIX_CAP)
    assert built.value.code == "EMPTY"


def test_bad_types() -> None:
    cache = freeze(_PREFIX)
    with pytest.raises(Refuse) as prefix:
        freeze("stable prefix")
    assert prefix.value.code == "NOT_BYTES"
    with pytest.raises(Refuse) as missing:
        freeze(None)
    assert missing.value.code == "NOT_BYTES"
    with pytest.raises(Refuse) as tail:
        append(cache, "item")
    assert tail.value.code == "NOT_BYTES"
    with pytest.raises(Refuse) as flag:
        freeze(_PREFIX, True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as text:
        freeze(_PREFIX, "9")
    assert text.value.code == "NOT_INT"
    with pytest.raises(Refuse) as zero:
        freeze(_PREFIX, 0)
    assert zero.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as negative:
        freeze(_PREFIX, -3)
    assert negative.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as measured:
        record_hit(cache, True)
    assert measured.value.code == "NOT_INT"
    assert cache.cached_tokens is None
    with pytest.raises(Refuse) as fraction:
        record_hit(cache, 1.5)
    assert fraction.value.code == "NOT_INT"
    digest = _digest(b"abc")
    with pytest.raises(Refuse) as cap_flag:
        PrefixCache(SCHEMA, digest, b"abc", b"", None, cast(int, True))
    assert cap_flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as token_flag:
        PrefixCache(SCHEMA, digest, b"abc", b"", cast(int, False), PREFIX_CAP)
    assert token_flag.value.code == "NOT_INT"


def test_cap_is_policy() -> None:
    high = freeze(b"abcd", 9_999_999)
    assert high.cap == PREFIX_CAP
    full = freeze(b"a" * PREFIX_CAP, PREFIX_CAP + 50)
    assert full.cap == PREFIX_CAP
    assert len(full.prefix) == PREFIX_CAP
    with pytest.raises(Refuse) as over:
        freeze(b"a" * (PREFIX_CAP + 1), 9_999_999)
    assert over.value.code == "OVERSIZE"
    tight = freeze(b"abcd", 4)
    assert tight.cap == 4
    with pytest.raises(Refuse) as tight_over:
        freeze(b"abcde", 4)
    assert tight_over.value.code == "OVERSIZE"
    digest = _digest(b"abc")
    built = PrefixCache(SCHEMA, digest, b"abc", b"", None, 9_999_999)
    assert built.cap == PREFIX_CAP


def test_tail_cap() -> None:
    cache = freeze(_PREFIX)
    exact = cache.append(b"x" * TAIL_CAP)
    assert len(exact.tail) == TAIL_CAP
    assert exact.cache_id == cache.cache_id
    with pytest.raises(Refuse) as over:
        append(cache, b"x" * (TAIL_CAP + 1))
    assert over.value.code == "OVERSIZE"
    half = append(cache, b"y" * (TAIL_CAP // 2))
    with pytest.raises(Refuse) as summed:
        append(half, b"y" * ((TAIL_CAP // 2) + 1))
    assert summed.value.code == "OVERSIZE"
    assert half.tail == b"y" * (TAIL_CAP // 2)
    assert half.cache_id == cache.cache_id


def test_token_bounds() -> None:
    cache = freeze(_PREFIX)
    with pytest.raises(Refuse) as low:
        record_hit(cache, -1)
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as high:
        cache.record_hit(TOKEN_CAP + 1)
    assert high.value.code == "OUT_OF_RANGE"
    assert cache.cached_tokens is None


def test_bad_id_and_bad_cache() -> None:
    digest = _digest(b"abc")
    with pytest.raises(Refuse) as bad_id:
        PrefixCache(SCHEMA, "0" * 64, b"abc", b"", None, PREFIX_CAP)
    assert bad_id.value.code == "BAD_ID"
    with pytest.raises(Refuse) as schema:
        PrefixCache("cosmos-hermes-other/1", digest, b"abc", b"", None, PREFIX_CAP)
    assert schema.value.code == "BAD_CACHE"
    with pytest.raises(Refuse) as append_bad:
        append("nope", b"item")
    assert append_bad.value.code == "BAD_CACHE"
    with pytest.raises(Refuse) as hit_bad:
        record_hit(None, 4)
    assert hit_bad.value.code == "BAD_CACHE"
    volatile = _PREFIX + b" 2026-10-01"
    with pytest.raises(Refuse) as still_volatile:
        PrefixCache(SCHEMA, _digest(volatile), volatile, b"", None, PREFIX_CAP)
    assert still_volatile.value.code == "VOLATILE_PREFIX"


def test_null_byte() -> None:
    with pytest.raises(Refuse) as prefix:
        freeze(b"stable\x00prefix")
    assert prefix.value.code == "NULL_BYTE"
    cache = freeze(_PREFIX)
    with pytest.raises(Refuse) as tail:
        append(cache, b"item\x00")
    assert tail.value.code == "NULL_BYTE"
    assert cache.tail == b""


def test_bytearray_is_copied() -> None:
    raw = bytearray(_PREFIX)
    cache = freeze(raw)
    raw[0] = ord("X")
    assert cache.prefix == _PREFIX
    assert cache.cache_id == _digest(_PREFIX)
    piece_raw = bytearray(b"north light rules")
    piece = Piece("light", "prefix", cast(bytes, piece_raw))
    piece_raw[0] = ord("X")
    assert piece.body == b"north light rules"


def _tokens(cache: PrefixCache) -> int:
    got = cache.cached_tokens
    if got is None:
        raise AssertionError("unmeasured")
    return got


def test_direct_record_matches_freeze_and_rebuild() -> None:
    cache = freeze(_PREFIX)
    direct = PrefixCache(SCHEMA, cache.cache_id, _PREFIX, b"", None, PREFIX_CAP)
    assert direct == cache
    counted = record_hit(append(cache, b"the harbor note"), 7265)
    assert rebuild(counted) == counted
    assert rebuild(rebuild(counted)) == counted
    assert _tokens(rebuild(counted)) == 7265
    with pytest.raises(Refuse) as bad:
        rebuild("nope")
    assert bad.value.code == "BAD_CACHE"


def test_measured_requires_a_count() -> None:
    cache = freeze(_PREFIX)
    with pytest.raises(Refuse) as missing:
        measured(cache)
    assert missing.value.code == "ASSUMED_HIT"
    with pytest.raises(Refuse) as method:
        cache.measured()
    assert method.value.code == "ASSUMED_HIT"
    miss = record_hit(cache, 0)
    assert measured(miss) == 0
    assert miss.measured() == 0
    hit = miss.record_hit(7265)
    assert measured(hit) == 7265
    with pytest.raises(Refuse) as assumed:
        hit.assume_hit()
    assert assumed.value.code == "ASSUMED_HIT"


def test_cache_id_shape() -> None:
    digest = _digest(b"abc")
    with pytest.raises(Refuse) as short:
        PrefixCache(SCHEMA, "abc", b"abc", b"", None, PREFIX_CAP)
    assert short.value.code == "BAD_ID"
    with pytest.raises(Refuse) as long:
        PrefixCache(SCHEMA, "a" * 10_000, b"abc", b"", None, PREFIX_CAP)
    assert long.value.code == "BAD_ID"
    with pytest.raises(Refuse) as number:
        PrefixCache(SCHEMA, cast(str, 123), b"abc", b"", None, PREFIX_CAP)
    assert number.value.code == "BAD_ID"
    assert PrefixCache(SCHEMA, digest, b"abc", b"", None, PREFIX_CAP).cache_id == digest


def test_plan_skips_over_budget_and_keeps_later() -> None:
    big = Piece("big-card", "prefix", b"12345678")
    small = Piece("small-card", "prefix", b"1234")
    planned = plan((big, small), 6)
    assert planned.kept == ("small-card",)
    assert planned.skipped == ("big-card",)
    assert planned.cache.prefix == b"1234"
    assert planned.cache.tail == b""
    assert planned.cache.cap == 6
    assert planned.cache.cache_id == _digest(b"1234")
    assert planned.cache.cached_tokens is None
    again = plan([big, small], 6)
    assert again == planned
    first = Piece("a", "prefix", b"123456")
    middle = Piece("b", "prefix", b"123456")
    last = Piece("c", "prefix", b"1234")
    note = Piece("note", "tail", b"zz")
    mixed = plan((first, middle, last, note), 10)
    assert mixed.kept == ("a", "c", "note")
    assert mixed.skipped == ("b",)
    assert mixed.cache.prefix == b"1234561234"
    assert mixed.cache.tail == b"zz"
    assert mixed.cache.cache_id == _digest(b"1234561234")


def test_plan_tail_skip_keeps_a_later_tail() -> None:
    prefix = Piece("rules", "prefix", b"rules")
    wide = Piece("wide", "tail", b"y" * (TAIL_CAP - 2))
    bulky = Piece("bulky", "tail", b"yyyy")
    fit = Piece("fit", "tail", b"zz")
    planned = plan((prefix, wide, bulky, fit))
    assert planned.kept == ("rules", "wide", "fit")
    assert planned.skipped == ("bulky",)
    assert len(planned.cache.tail) == TAIL_CAP
    assert planned.cache.tail.endswith(b"zz")
    assert planned.cache.cache_id == _digest(b"rules")
    huge = Piece("huge", "tail", b"h" * (TAIL_CAP + 1))
    later = Piece("later", "tail", b"ok")
    skipped_huge = plan((prefix, huge, later))
    assert skipped_huge.skipped == ("huge",)
    assert skipped_huge.cache.tail == b"ok"


def test_volatile_prefix_is_not_skipped() -> None:
    dated = Piece("dated", "prefix", b"2026-10-01")
    later = Piece("later", "prefix", b"ok")
    with pytest.raises(Refuse) as caught:
        plan((dated, later), 4)
    assert caught.value.code == "VOLATILE_PREFIX"
    with pytest.raises(Refuse) as uuid_block:
        plan((Piece("id", "prefix", b"id " + _UUID), later))
    assert uuid_block.value.code == "VOLATILE_PREFIX"
    body = b"stable rules for the card"
    planned = plan(
        (
            Piece("rules", "prefix", body),
            Piece("job", "tail", b"job " + _UUID + b" 2026-10-01"),
        )
    )
    assert planned.cache.cache_id == _digest(body)
    assert _UUID in planned.cache.tail


def test_split_date_and_secret_across_blocks() -> None:
    with pytest.raises(Refuse) as dated:
        plan(
            (
                Piece("left", "prefix", b"rules 2026-10-"),
                Piece("right", "prefix", b"01 more"),
            )
        )
    assert dated.value.code == "VOLATILE_PREFIX"
    with pytest.raises(Refuse) as secret:
        plan(
            (
                Piece("left", "prefix", b"prefix sk-"),
                Piece("right", "prefix", b"abcdefghij end"),
            )
        )
    assert secret.value.code == "SECRET"
    with pytest.raises(Refuse) as tail_secret:
        plan(
            (
                Piece("rules", "prefix", b"rules"),
                Piece("left", "tail", b"api_key="),
                Piece("right", "tail", b"abcdef"),
            )
        )
    assert tail_secret.value.code == "SECRET"


def test_plan_shape_and_caps() -> None:
    with pytest.raises(Refuse) as empty:
        plan(())
    assert empty.value.code == "EMPTY"
    with pytest.raises(Refuse) as text:
        plan("prefix")
    assert text.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as missing:
        plan(None)
    assert missing.value.code == "BAD_PLAN"
    good = Piece("card", "prefix", b"card-body")
    with pytest.raises(Refuse) as mixed:
        plan((good, None))
    assert mixed.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as kind:
        Piece("card", "context", b"card-body")
    assert kind.value.code == "BAD_KIND"
    with pytest.raises(Refuse) as blank:
        Piece("", "prefix", b"card-body")
    assert blank.value.code == "EMPTY"
    with pytest.raises(Refuse) as named:
        Piece("sk-livexxxx", "prefix", b"card-body")
    assert named.value.code == "SECRET"
    with pytest.raises(Refuse) as naked:
        plan((Piece("note", "tail", b"only-the-note"),))
    assert naked.value.code == "EMPTY"
    with pytest.raises(Refuse) as order:
        plan((Piece("note", "tail", b"tail-note"), Piece("card", "prefix", b"card-body")))
    assert order.value.code == "BAD_ORDER"
    with pytest.raises(Refuse) as duplicate:
        plan((Piece("card", "prefix", b"one"), Piece("card", "prefix", b"two")))
    assert duplicate.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as flag:
        plan((good,), True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as zero:
        plan((good,), 0)
    assert zero.value.code == "BAD_LIMIT"
    high = plan((good,), 9_999_999)
    assert high.cache.cap == PREFIX_CAP
    with pytest.raises(Refuse) as too_many:
        plan(_blocks(PIECE_CAP + 1))
    assert too_many.value.code == "OVERSIZE"
    full = plan(_blocks(PIECE_CAP), PIECE_CAP)
    assert full.kept == tuple(f"b{index}" for index in range(PIECE_CAP))
    assert full.skipped == ()
    assert len(full.cache.prefix) == PIECE_CAP
    with pytest.raises(Refuse) as none_fit:
        plan((Piece("big", "prefix", b"123456"),), 4)
    assert none_fit.value.code == "EMPTY"
    with pytest.raises(Refuse) as over:
        Piece("big", "prefix", b"a" * (PREFIX_CAP + 1))
    assert over.value.code == "OVERSIZE"
    shown = Piece("session-rules", "prefix", b"session north-light body")
    assert "session north-light body" not in repr(shown)
    assert not secret_shape(repr(shown))
    assert "session north-light body" not in repr(high)
    assert not secret_shape(repr(high))
    with pytest.raises(Refuse) as bad_plan:
        CachePlan("cosmos-hermes-other/1", high.cache, ("card",), ())
    assert bad_plan.value.code == "BAD_CACHE"
    with pytest.raises(Refuse) as bad_cache:
        CachePlan(SCHEMA, cast(PrefixCache, None), ("card",), ())
    assert bad_cache.value.code == "BAD_CACHE"
    with pytest.raises(Refuse) as no_kept:
        CachePlan(SCHEMA, high.cache, (), ())
    assert no_kept.value.code == "EMPTY"
    with pytest.raises(Refuse) as overlap:
        CachePlan(SCHEMA, high.cache, ("card",), ("card",))
    assert overlap.value.code == "DUPLICATE"


def _blocks(count: int) -> tuple[Piece, ...]:
    rows: list[Piece] = []
    for index in range(count):
        rows.append(Piece(f"b{index}", "prefix", b"x"))
    return tuple(rows)


def test_secret_that_does_not_fit_stays_secret() -> None:
    cache = append(freeze(_PREFIX), b"y" * (TAIL_CAP - 4))
    with pytest.raises(Refuse) as caught:
        append(cache, b"Bearer abcdefghijk")
    assert caught.value.code == "SECRET"
    filler = Piece("fill", "tail", b"y" * (TAIL_CAP - 4))
    secret = Piece("leak", "tail", b"Bearer abcdefghijk")
    with pytest.raises(Refuse) as planned:
        plan((Piece("rules", "prefix", _PREFIX), filler, secret))
    assert planned.value.code == "SECRET"


@dataclass(frozen=True, slots=True)
class _StoryResult:
    cache_id: str
    prefix: bytes
    tail: bytes
    kept: tuple[str, ...]
    skipped: tuple[str, ...]
    tokens: int
    assumed: str
    dated: str
    rebuilt_tokens: int


def _story() -> _StoryResult:
    prefix = b"session north-light. card harbor-note. the north light stays warm."
    tail = b"note: dim the north light after the harbor card is filed. 2026-10-01"
    planned = plan(
        (
            Piece("session-rules", "prefix", prefix),
            Piece("harbor-note", "tail", tail),
        )
    )
    counted = record_hit(planned.cache, 7265)
    assumed = "returned"
    try:
        counted.assume_hit()
    except Refuse as exc:
        assumed = exc.code
    dated = "returned"
    try:
        freeze(prefix + b" 2026-10-01")
    except Refuse as exc:
        dated = exc.code
    rebuilt = rebuild(counted)
    return _StoryResult(
        cache_id=planned.cache.cache_id,
        prefix=planned.cache.prefix,
        tail=planned.cache.tail,
        kept=planned.kept,
        skipped=planned.skipped,
        tokens=measured(counted),
        assumed=assumed,
        dated=dated,
        rebuilt_tokens=_tokens(rebuilt),
    )


def test_example_prompt_cache() -> None:
    first = _story()
    second = _story()
    assert first == second
    assert first.dated == "VOLATILE_PREFIX"
    assert first.assumed == "ASSUMED_HIT"
    assert first.tokens == 7265
    assert first.rebuilt_tokens == 7265
    assert first.kept == ("session-rules", "harbor-note")
    assert first.skipped == ()
    assert first.prefix == b"session north-light. card harbor-note. the north light stays warm."
    assert first.tail.endswith(b"2026-10-01")
    assert b"2026-10-01" not in first.prefix
    assert first.cache_id == _digest(first.prefix)
