"""Projection counters rebuilt from caller-supplied events. A missing name is not zero."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from observability import (
    AUTHORITY,
    EVENT_CAP,
    INC_MAX,
    NAME_CAP,
    SCHEMA,
    TOTAL_MAX,
    Counters,
    Event,
    Snapshot,
    measure,
    rebuild,
)


def _at(counts: tuple[tuple[str, int], ...], index: int) -> tuple[str, int]:
    if index < 0 or index >= len(counts):
        raise AssertionError(index)
    return counts[index]


def _make(
    name: object,
    n: object = 1,
    schema: object = SCHEMA,
    authority: object = AUTHORITY,
) -> Event:
    return Event(cast(str, name), cast(int, n), cast(str, schema), cast(str, authority))


def _snap(schema: object, counts: object, cap: object, authority: object) -> Snapshot:
    return Snapshot(
        cast(str, schema),
        cast(tuple[tuple[str, int], ...], counts),
        cast(int, cap),
        cast(str, authority),
    )


def _code(board: Counters, case: str) -> str:
    with pytest.raises(Refuse) as caught:
        _fire(board, case)
    return str(caught.value.code)


def _missing(board: Counters, name: str) -> str:
    with pytest.raises(Refuse) as caught:
        board.get(name)
    return str(caught.value.code)


def _fire(board: Counters, case: str) -> None:
    if case == "cap_bool":
        Counters(True)
        return
    if case == "cap_false":
        Counters(False)
        return
    if case == "cap_none":
        Counters(None)
        return
    if case == "cap_str":
        Counters("64")
        return
    if case == "cap_float":
        Counters(1.5)
        return
    if case == "cap_zero":
        Counters(0)
        return
    if case == "cap_negative":
        Counters(-1)
        return
    if case == "name_int":
        _make(1)
        return
    if case == "name_none":
        _make(None)
        return
    if case == "name_bytes":
        _make(b"a")
        return
    if case == "name_nul":
        _make("a\x00b")
        return
    if case == "name_over":
        _make("a" * 41)
        return
    if case == "name_empty":
        _make("")
        return
    if case == "name_upper":
        _make("A")
        return
    if case == "name_hyphen":
        _make("has-hyphen")
        return
    if case == "name_space":
        _make("has space")
        return
    if case == "secret_token":
        _make("token:abcdefgh")
        return
    if case == "secret_api":
        _make("api_key:abcdef")
        return
    if case == "secret_word":
        _make("secret:abcdef")
        return
    if case == "secret_sk":
        _make("sk-livekeyvalue")
        return
    if case == "step_bool":
        _make("kept", True)
        return
    if case == "step_false":
        _make("kept", False)
        return
    if case == "step_str":
        _make("kept", "1")
        return
    if case == "step_none":
        _make("kept", None)
        return
    if case == "step_float":
        _make("kept", 1.5)
        return
    if case == "step_zero":
        _make("kept", 0)
        return
    if case == "step_negative":
        _make("kept", -1)
        return
    if case == "step_over":
        _make("kept", INC_MAX + 1)
        return
    if case == "schema_int":
        _make("kept", 1, 1)
        return
    if case == "schema_nul":
        _make("kept", 1, "bad\x00")
        return
    if case == "schema_over":
        _make("kept", 1, "x" * 65)
        return
    if case == "schema_bad":
        _make("kept", 1, "cosmos-hermes-observability/2")
        return
    if case == "schema_secret":
        _make("kept", 1, "token:abcdefghijklmnop")
        return
    if case == "authority_ledger":
        _make("kept", 1, SCHEMA, "ledger")
        return
    if case == "authority_spend":
        _make("kept", 1, SCHEMA, "spend")
        return
    if case == "authority_empty":
        _make("kept", 1, SCHEMA, "")
        return
    if case == "authority_secret":
        _make("kept", 1, SCHEMA, "token:abcdefgh")
        return
    if case == "snap_schema_int":
        _snap(1, (), NAME_CAP, AUTHORITY)
        return
    if case == "snap_schema_nul":
        _snap("bad\x00", (), NAME_CAP, AUTHORITY)
        return
    if case == "snap_schema_over":
        _snap("x" * 65, (), NAME_CAP, AUTHORITY)
        return
    if case == "snap_schema_bad":
        _snap("cosmos-hermes-observability/2", (), NAME_CAP, AUTHORITY)
        return
    if case == "snap_schema_secret":
        _snap("token:abcdefghijklmnop", (), NAME_CAP, AUTHORITY)
        return
    if case == "snap_authority_ledger":
        _snap(SCHEMA, (), NAME_CAP, "ledger")
        return
    if case == "snap_authority_spend":
        _snap(SCHEMA, (), NAME_CAP, "spend")
        return
    if case == "snap_authority_empty":
        _snap(SCHEMA, (), NAME_CAP, "")
        return
    if case == "snap_authority_secret":
        _snap(SCHEMA, (), NAME_CAP, "token:abcdefgh")
        return
    if case == "snap_cap_bool":
        _snap(SCHEMA, (), True, AUTHORITY)
        return
    if case == "snap_cap_zero":
        _snap(SCHEMA, (), 0, AUTHORITY)
        return
    if case == "snap_list":
        _snap(SCHEMA, [("a", 1)], NAME_CAP, AUTHORITY)
        return
    if case == "snap_short":
        _snap(SCHEMA, (("only",),), NAME_CAP, AUTHORITY)
        return
    if case == "snap_dup":
        _snap(SCHEMA, (("a", 1), ("a", 2)), NAME_CAP, AUTHORITY)
        return
    if case == "snap_zero":
        _snap(SCHEMA, (("a", 0),), NAME_CAP, AUTHORITY)
        return
    if case == "snap_huge":
        _snap(SCHEMA, (("a", TOTAL_MAX + 1),), NAME_CAP, AUTHORITY)
        return
    if case == "snap_bool_total":
        _snap(SCHEMA, (("a", True),), NAME_CAP, AUTHORITY)
        return
    if case == "snap_bad_name":
        _snap(SCHEMA, (("A", 1),), NAME_CAP, AUTHORITY)
        return
    if case == "snap_secret_name":
        _snap(SCHEMA, (("token:abcdefgh", 1),), NAME_CAP, AUTHORITY)
        return
    if case == "bad_events_none":
        board.rebuild(None)
        return
    if case == "bad_events_list":
        board.rebuild(["kept"])
        return
    if case == "bad_events_str":
        board.rebuild("request")
        return
    if case == "bad_event_item":
        board.rebuild((Event("kept"), "kept"))
        return
    if case == "measure_type":
        measure(board, "kept")
        return
    if case == "name_cap":
        rows = tuple(Event(f"n{index}") for index in range(NAME_CAP + 1))
        board.rebuild(rows)
        return
    if case == "event_cap":
        rows = tuple(Event("request") for _index in range(EVENT_CAP + 1))
        board.rebuild(rows)
        return
    if case == "fresh_get":
        Counters().get("request")
        return
    if case == "fresh_snapshot":
        Counters().snapshot()
        return
    if case == "missing_get":
        board.get("request")
        return
    if case == "missing_measure":
        measure(board.snapshot(), "request")
        return
    if case == "fresh_secret":
        Counters().get("sk-livekeyvalue")
        return
    if case == "missing_bad_name":
        board.get("A")
        return
    if case == "empty_named":
        empty = Counters()
        empty.rebuild(())
        empty.get("request")
        return
    raise AssertionError(case)


_CASES: tuple[tuple[str, str], ...] = (
    ("NOT_INT", "cap_bool"),
    ("NOT_INT", "cap_false"),
    ("NOT_INT", "cap_none"),
    ("NOT_INT", "cap_str"),
    ("NOT_INT", "cap_float"),
    ("BAD_LIMIT", "cap_zero"),
    ("BAD_LIMIT", "cap_negative"),
    ("NOT_TEXT", "name_int"),
    ("NOT_TEXT", "name_none"),
    ("NOT_TEXT", "name_bytes"),
    ("NULL_BYTE", "name_nul"),
    ("OVERSIZE", "name_over"),
    ("BAD_NAME", "name_empty"),
    ("BAD_NAME", "name_upper"),
    ("BAD_NAME", "name_hyphen"),
    ("BAD_NAME", "name_space"),
    ("SECRET", "secret_token"),
    ("SECRET", "secret_api"),
    ("SECRET", "secret_word"),
    ("SECRET", "secret_sk"),
    ("NOT_INT", "step_bool"),
    ("NOT_INT", "step_false"),
    ("NOT_INT", "step_str"),
    ("NOT_INT", "step_none"),
    ("NOT_INT", "step_float"),
    ("OUT_OF_RANGE", "step_zero"),
    ("OUT_OF_RANGE", "step_negative"),
    ("OUT_OF_RANGE", "step_over"),
    ("NOT_TEXT", "schema_int"),
    ("NULL_BYTE", "schema_nul"),
    ("OVERSIZE", "schema_over"),
    ("BAD_SCHEMA", "schema_bad"),
    ("SECRET", "schema_secret"),
    ("BAD_AUTHORITY", "authority_ledger"),
    ("BAD_AUTHORITY", "authority_spend"),
    ("BAD_AUTHORITY", "authority_empty"),
    ("SECRET", "authority_secret"),
    ("NOT_TEXT", "snap_schema_int"),
    ("NULL_BYTE", "snap_schema_nul"),
    ("OVERSIZE", "snap_schema_over"),
    ("BAD_SCHEMA", "snap_schema_bad"),
    ("SECRET", "snap_schema_secret"),
    ("BAD_AUTHORITY", "snap_authority_ledger"),
    ("BAD_AUTHORITY", "snap_authority_spend"),
    ("BAD_AUTHORITY", "snap_authority_empty"),
    ("SECRET", "snap_authority_secret"),
    ("NOT_INT", "snap_cap_bool"),
    ("BAD_LIMIT", "snap_cap_zero"),
    ("BAD_SNAPSHOT", "snap_list"),
    ("BAD_SNAPSHOT", "snap_short"),
    ("BAD_SNAPSHOT", "snap_dup"),
    ("OUT_OF_RANGE", "snap_zero"),
    ("OUT_OF_RANGE", "snap_huge"),
    ("NOT_INT", "snap_bool_total"),
    ("BAD_NAME", "snap_bad_name"),
    ("SECRET", "snap_secret_name"),
    ("BAD_EVENTS", "bad_events_none"),
    ("BAD_EVENTS", "bad_events_list"),
    ("BAD_EVENTS", "bad_events_str"),
    ("BAD_EVENT", "bad_event_item"),
    ("BAD_SNAPSHOT", "measure_type"),
    ("NAME_CAP", "name_cap"),
    ("EVENT_CAP", "event_cap"),
    ("UNMEASURED", "fresh_get"),
    ("UNMEASURED", "fresh_snapshot"),
    ("UNMEASURED", "missing_get"),
    ("UNMEASURED", "missing_measure"),
    ("SECRET", "fresh_secret"),
    ("BAD_NAME", "missing_bad_name"),
    ("UNMEASURED", "empty_named"),
)

_CODES: frozenset[str] = frozenset(
    {
        "SECRET",
        "BAD_NAME",
        "NAME_CAP",
        "EVENT_CAP",
        "BAD_SCHEMA",
        "BAD_AUTHORITY",
        "BAD_SNAPSHOT",
        "BAD_EVENT",
        "BAD_EVENTS",
        "BAD_LIMIT",
        "NOT_TEXT",
        "NULL_BYTE",
        "OVERSIZE",
        "NOT_INT",
        "OUT_OF_RANGE",
        "UNMEASURED",
    }
)


@dataclass(frozen=True, slots=True)
class _Story:
    session: str
    light: str
    note: str
    first: Snapshot
    second: Snapshot
    folded: Snapshot
    request_n: int
    refusal_n: int
    missing: str
    fresh: str


def _story() -> _Story:
    session = "lamp_west"
    light = "north_porch"
    note = "porch_note"
    events = (Event("request"), Event("refusal"), Event("request"))
    fresh_board = Counters()
    fresh = _missing(fresh_board, "request")
    board = Counters()
    first = board.rebuild(events)
    second = board.rebuild(events)
    folded = rebuild(events)
    return _Story(
        session,
        light,
        note,
        first,
        second,
        folded,
        board.get("request"),
        measure(folded, "refusal"),
        _missing(board, note),
        fresh,
    )


def test_example_observability() -> None:
    left = _story()
    right = _story()
    assert left == right
    assert left.session == "lamp_west"
    assert left.light == "north_porch"
    assert left.note == "porch_note"
    assert left.first == left.second == left.folded
    assert left.first.schema == SCHEMA
    assert left.first.authority == AUTHORITY
    assert left.first.authority != "ledger"
    assert left.first.cap == NAME_CAP
    assert left.first.counts == (("request", 2), ("refusal", 1))
    assert left.request_n == 2
    assert left.refusal_n == 1
    assert left.missing == "UNMEASURED"
    assert left.fresh == "UNMEASURED"
    assert ("porch_note", 0) not in left.first.counts
    for _label, total in left.first.counts:
        assert total > 0
    with pytest.raises(Refuse) as caught:
        measure(left.first, "porch_note")
    assert str(caught.value.code) == "UNMEASURED"


def test_schema_success_and_replace() -> None:
    assert SCHEMA == "cosmos-hermes-observability/1"
    assert AUTHORITY == "projection"
    assert NAME_CAP == 64
    assert EVENT_CAP == 256
    assert INC_MAX == 1000
    assert TOTAL_MAX == EVENT_CAP * INC_MAX
    board = Counters()
    assert board.schema == SCHEMA
    assert board.cap == NAME_CAP
    assert board.authority == AUTHORITY
    assert board.indexed is False
    events = (
        Event("once"),
        Event("tool:ok", 1),
        Event("tool:ok", INC_MAX),
        Event("other_1", 2),
        Event(":_0"),
        Event("a" * 40),
    )
    snap = board.rebuild(events)
    assert board.indexed is True
    assert snap == rebuild(events)
    assert snap.counts == (
        ("once", 1),
        ("tool:ok", 1001),
        ("other_1", 2),
        (":_0", 1),
        ("a" * 40, 1),
    )
    assert measure(snap, "tool:ok") == 1001
    assert board.get("once") == 1
    again = board.rebuild(events)
    assert again == snap
    assert board.get("tool:ok") == 1001
    ordered = rebuild((Event("b"), Event("a")))
    assert ordered.counts == (("b", 1), ("a", 1))
    assert rebuild((Event("a"), Event("b"))).counts == (("a", 1), ("b", 1))
    assert ordered != rebuild((Event("a"), Event("b")))
    replaced = board.rebuild((Event("once"),))
    assert replaced.counts == (("once", 1),)
    assert board.get("once") == 1
    with pytest.raises(Refuse) as dropped:
        board.get("tool:ok")
    assert str(dropped.value.code) == "UNMEASURED"
    board.clear()
    assert board.cap == NAME_CAP
    assert board.indexed is False
    with pytest.raises(Refuse) as cleared:
        board.snapshot()
    assert str(cleared.value.code) == "UNMEASURED"
    with pytest.raises(Refuse) as cleared_get:
        board.get("once")
    assert str(cleared_get.value.code) == "UNMEASURED"
    restored = board.rebuild(events)
    assert restored == snap
    text = repr(board) + repr(snap) + repr(Event("once")) + repr(Counters())
    assert secret_shape(text) is False
    assert "sk-" not in text
    assert "Bearer" not in text
    assert "api_key=" not in text


def test_cap_records_policy_and_refuses_one_past_it() -> None:
    for asked in (65, 1000, 10**18):
        held = Counters(asked)
        assert held.cap == NAME_CAP
        assert held.rebuild((Event("request"),)).cap == NAME_CAP
    assert rebuild((Event("request"),), 2).cap == 2
    assert rebuild((Event("request"),), 99).cap == NAME_CAP
    lowered = Counters(1)
    assert lowered.cap == 1
    kept = lowered.rebuild((Event("only", 2), Event("only", 3)))
    assert kept.counts == (("only", 5),)
    assert lowered.get("only") == 5
    with pytest.raises(Refuse) as caught:
        lowered.rebuild((Event("only"), Event("next")))
    assert str(caught.value.code) == "NAME_CAP"
    assert lowered.snapshot() == kept
    assert lowered.get("only") == 5
    with pytest.raises(Refuse) as missing:
        lowered.get("next")
    assert str(missing.value.code) == "UNMEASURED"
    names = tuple(Event(f"n{index}") for index in range(NAME_CAP))
    full = Counters(10**6)
    snap = full.rebuild(names)
    assert full.cap == NAME_CAP
    assert len(snap.counts) == NAME_CAP
    assert _at(snap.counts, NAME_CAP - 1) == ("n63", 1)
    bumped = full.rebuild(names + (Event("n0", 3),))
    assert full.get("n0") == 4
    assert len(bumped.counts) == NAME_CAP
    with pytest.raises(Refuse) as overflow:
        full.rebuild(names + (Event("overflow"),))
    assert str(overflow.value.code) == "NAME_CAP"
    assert full.snapshot() == bumped
    ceiling = tuple(Event("request", INC_MAX) for _index in range(EVENT_CAP))
    top = rebuild(ceiling)
    assert measure(top, "request") == TOTAL_MAX
    held_top = Counters()
    before = held_top.rebuild((Event("kept"),))
    with pytest.raises(Refuse) as over_events:
        held_top.rebuild(ceiling + (Event("request"),))
    assert str(over_events.value.code) == "EVENT_CAP"
    assert held_top.snapshot() == before
    clamped = Snapshot(SCHEMA, (("a", 1),), 99, AUTHORITY)
    assert clamped.cap == NAME_CAP
    wide = tuple((f"n{index}", 1) for index in range(NAME_CAP + 1))
    with pytest.raises(Refuse) as wide_snap:
        Snapshot(SCHEMA, wide, 99, AUTHORITY)
    assert str(wide_snap.value.code) == "NAME_CAP"


def test_missing_index_is_unmeasured_not_zero() -> None:
    fresh = Counters()
    assert fresh.indexed is False
    with pytest.raises(Refuse) as fresh_get:
        fresh.get("request")
    assert str(fresh_get.value.code) == "UNMEASURED"
    with pytest.raises(Refuse) as fresh_snap:
        fresh.snapshot()
    assert str(fresh_snap.value.code) == "UNMEASURED"
    with pytest.raises(Refuse) as bad:
        fresh.rebuild(None)
    assert str(bad.value.code) == "BAD_EVENTS"
    assert fresh.indexed is False
    empty_board = Counters()
    empty = empty_board.rebuild(())
    assert empty_board.indexed is True
    assert empty.counts == ()
    with pytest.raises(Refuse) as named:
        empty_board.get("request")
    assert str(named.value.code) == "UNMEASURED"
    with pytest.raises(Refuse) as named_measure:
        measure(empty, "request")
    assert str(named_measure.value.code) == "UNMEASURED"
    with pytest.raises(Refuse) as secret:
        fresh.get("token:abcdefgh")
    assert str(secret.value.code) == "SECRET"
    assert "token:abcdefgh" not in repr(fresh)
    assert "UNMEASURED" in repr(fresh)


def test_refusal_codes_leave_the_projection() -> None:
    seen: set[str] = set()
    for code, case in _CASES:
        board = Counters()
        held = board.rebuild((Event("kept", 1),))
        got = _code(board, case)
        assert got == code
        assert board.snapshot() == held
        assert board.get("kept") == 1
        seen.add(got)
    assert seen == _CODES


def test_module_has_no_thread_socket_or_log() -> None:
    source = Path(__file__).with_name("observability.py").read_text(encoding="utf-8")
    for banned in (
        "threading",
        "subprocess",
        "socket",
        "urllib",
        "requests",
        "pickle",
        "sqlite3",
        "time.sleep",
        "eval(",
        "exec(",
        "open(",
        "logging",
    ):
        assert banned not in source
