"""Reserve, settle, release, over-cap, and duplicate id for the day-one fold."""

from __future__ import annotations

from typing import cast

from cosmos_federation import DEFAULT_CAP_USD_MICROS, MAX_CAP_USD_MICROS, Refuse
from spendcap import SCHEMA, Book, Event, open_book, release, reserve, settle


def test_schema_names_the_fold() -> None:
    assert SCHEMA == "cosmos-federation-spendcap/1"


def test_reserve_settle_and_release_append_and_keep_the_prior_book() -> None:
    first = open_book(DEFAULT_CAP_USD_MICROS)
    held = reserve(first, 100_000, 10, "job")
    assert first.events == ()
    assert held is not first
    assert held.cap_usd_micros == DEFAULT_CAP_USD_MICROS
    assert held.events[0].kind == "RESERVE"
    assert held.events[0].event_id == "job"
    assert held.events[0].micros == 100_000
    assert held.events[0].epoch == 10
    settled = settle(held, "job", 40_000, 11)
    assert tuple(ev.kind for ev in settled.events) == ("RESERVE", "SETTLE")
    assert settled.events[1].micros == 40_000
    assert settled.events[1].epoch == 11
    other = reserve(settled, 1, 12, "tail")
    freed = release(other, "tail", 13)
    assert freed.events[-1].kind == "RELEASE"
    assert freed.events[-1].micros == 0
    assert len(other.events) == 3
    again = open_book(DEFAULT_CAP_USD_MICROS)
    assert again == first


def test_reserve_at_the_cap_is_allowed_and_one_more_micro_is_not() -> None:
    full = reserve(open_book(MAX_CAP_USD_MICROS), MAX_CAP_USD_MICROS, 0, "all")
    assert full.events[0].micros == MAX_CAP_USD_MICROS
    done = settle(full, "all", MAX_CAP_USD_MICROS, 1)
    assert done.events[1].micros == MAX_CAP_USD_MICROS
    try:
        reserve(done, 1, 2, "more")
    except Refuse as exc:
        assert exc.code == "OVER_CAP"
    else:
        raise AssertionError("headroom")
    split = reserve(open_book(100), 60, 1, "a")
    split = reserve(split, 40, 2, "b")
    try:
        reserve(split, 1, 3, "c")
    except Refuse as exc:
        assert exc.code == "OVER_CAP"
    else:
        raise AssertionError("split")


def test_over_cap_does_not_append() -> None:
    book = open_book(100)
    try:
        reserve(book, 101, 0, "too-big")
    except Refuse as exc:
        assert exc.code == "OVER_CAP"
    else:
        raise AssertionError("over")
    assert book.events == ()
    held = reserve(book, 40, 5, "job")
    try:
        settle(held, "job", 41, 6)
    except Refuse as exc:
        assert exc.code == "OVER_CAP"
    else:
        raise AssertionError("settle")
    assert len(held.events) == 1


def test_settle_under_the_hold_frees_the_difference() -> None:
    book = reserve(open_book(100), 80, 1, "a")
    book = settle(book, "a", 30, 2)
    book = reserve(book, 70, 3, "b")
    assert book.events[1].micros == 30
    try:
        reserve(book, 1, 4, "c")
    except Refuse as exc:
        assert exc.code == "OVER_CAP"
    else:
        raise AssertionError("exact")
    book = settle(book, "b", 0, 5)
    book = reserve(book, 70, 6, "d")
    assert book.events[-1].event_id == "d"


def test_release_returns_the_whole_hold() -> None:
    book = reserve(open_book(100), 80, 1, "a")
    book = reserve(book, 20, 2, "b")
    book = release(book, "a", 4)
    book = reserve(book, 80, 5, "d")
    assert book.events[-1].kind == "RESERVE"
    assert book.events[-1].micros == 80
    try:
        reserve(book, 1, 6, "e")
    except Refuse as exc:
        assert exc.code == "OVER_CAP"
    else:
        raise AssertionError("full")


def test_duplicate_event_id_stays_used_after_release_and_settle() -> None:
    book = reserve(open_book(500), 10, 1, "same")
    try:
        reserve(book, 10, 2, "same")
    except Refuse as exc:
        assert exc.code == "DUP_EVENT"
    else:
        raise AssertionError("dup")
    released = release(book, "same", 3)
    try:
        reserve(released, 10, 4, "same")
    except Refuse as exc:
        assert exc.code == "DUP_EVENT"
    else:
        raise AssertionError("reuse")
    settled = settle(book, "same", 10, 5)
    try:
        reserve(settled, 1, 6, "same")
    except Refuse as exc:
        assert exc.code == "DUP_EVENT"
    else:
        raise AssertionError("settled-id")
    assert len(book.events) == 1


def test_settle_and_release_need_an_open_reserve() -> None:
    book = reserve(open_book(200), 20, 1, "job")
    try:
        settle(book, "missing", 1, 2)
    except Refuse as exc:
        assert exc.code == "NO_RESERVE"
    else:
        raise AssertionError("missing-settle")
    try:
        release(book, "missing", 2)
    except Refuse as exc:
        assert exc.code == "NO_RESERVE"
    else:
        raise AssertionError("missing-release")
    settled = settle(book, "job", 5, 3)
    try:
        settle(settled, "job", 5, 4)
    except Refuse as exc:
        assert exc.code == "NO_RESERVE"
    else:
        raise AssertionError("twice")
    try:
        release(settled, "job", 5)
    except Refuse as exc:
        assert exc.code == "NO_RESERVE"
    else:
        raise AssertionError("after-settle")
    freed = release(book, "job", 6)
    try:
        release(freed, "job", 7)
    except Refuse as exc:
        assert exc.code == "NO_RESERVE"
    else:
        raise AssertionError("after-release")
    try:
        settle(freed, "job", 0, 8)
    except Refuse as exc:
        assert exc.code == "NO_RESERVE"
    else:
        raise AssertionError("settle-freed")


def test_replay_refuses_a_hold_the_writers_could_not_append() -> None:
    # A later release must not launder two holds that were open together over the cap.
    hidden = Book(
        100,
        (
            Event("RESERVE", "a", 80, 1),
            Event("RESERVE", "b", 80, 2),
            Event("RELEASE", "a", 0, 3),
        ),
    )
    try:
        reserve(hidden, 1, 4, "c")
    except Refuse as exc:
        assert exc.code == "BOUND"
    else:
        raise AssertionError("released-overlap")
    assert len(hidden.events) == 3
    # Settling down must not launder a reserve that was already over the cap.
    settled_over = Book(
        100,
        (
            Event("RESERVE", "a", 500, 1),
            Event("SETTLE", "a", 10, 2),
        ),
    )
    try:
        settle(settled_over, "a", 10, 3)
    except Refuse as exc:
        assert exc.code == "BOUND"
    else:
        raise AssertionError("settled-over")
    raw = "sk-" + ("b" * 16)
    poisoned = Book(100, (Event("RESERVE", raw, 1, 0),))
    try:
        release(poisoned, "nope", 1)
    except Refuse as exc:
        assert exc.code == "BOUND"
        assert raw not in exc.detail
        assert "sk-" not in str(exc)
    else:
        raise AssertionError("secret-id")
    wide = Book(100, (Event("RESERVE", "a", 1, 2**63),))
    try:
        release(wide, "a", 1)
    except Refuse as exc:
        assert exc.code == "BOUND"
    else:
        raise AssertionError("epoch")
    blank = Book(100, (Event("RESERVE", "", 1, 0),))
    try:
        reserve(blank, 1, 1, "b")
    except Refuse as exc:
        assert exc.code == "BOUND"
    else:
        raise AssertionError("blank-id")


def test_open_book_does_not_raise_the_policy_cap() -> None:
    assert MAX_CAP_USD_MICROS == 1_000_000
    assert DEFAULT_CAP_USD_MICROS == 250_000
    assert open_book(1).cap_usd_micros == 1
    assert open_book(MAX_CAP_USD_MICROS).cap_usd_micros == MAX_CAP_USD_MICROS
    for bad in (0, -1, MAX_CAP_USD_MICROS + 1):
        try:
            open_book(bad)
        except Refuse as exc:
            assert exc.code == "CAP"
        else:
            raise AssertionError(bad)
    try:
        open_book(True)
    except Refuse as exc:
        assert exc.code == "CAP"
    else:
        raise AssertionError(True)


def test_bounds_and_secret_ids_do_not_enter_the_book() -> None:
    book = open_book(1_000)
    raw = "sk-" + ("a" * 12)
    cases: tuple[tuple[object, object, object], ...] = (
        (1, 0, ""),
        (1, 0, "e" * 65),
        (1, 0, raw),
        (1, -1, "ok"),
        (0, 0, "ok"),
        (True, 0, "ok"),
        (1, True, "ok"),
    )
    for micros, now, event_id in cases:
        try:
            reserve(book, cast(int, micros), cast(int, now), cast(str, event_id))
        except Refuse as exc:
            assert exc.code == "BOUND"
        else:
            raise AssertionError((micros, now, event_id))
    assert book.events == ()
    assert raw not in repr(book)
    assert "sk-" not in repr(book)
    accepted = reserve(book, 1, 0, "e" * 64)
    assert accepted.events[0].event_id == "e" * 64
    assert "sk-" not in repr(accepted)
    try:
        settle(accepted, "e" * 64, -1, 1)
    except Refuse as exc:
        assert exc.code == "BOUND"
    else:
        raise AssertionError("negative-settle")
