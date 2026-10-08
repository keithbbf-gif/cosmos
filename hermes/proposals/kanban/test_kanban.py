"""Kanban chain, columns, caps, and rebuild."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from kanban import (
    BODY_LIMIT,
    CARD_LIMIT,
    COLUMN_LIMIT,
    COLUMNS,
    EVENT_CAP,
    GENESIS,
    KINDS,
    POLICY_CAP,
    SCHEMA,
    Board,
    Event,
    Placement,
    Snapshot,
    link_sha,
    rebuild,
)


def _nth(events: tuple[Event, ...], index: int) -> Event:
    if index < 0 or index >= len(events):
        raise AssertionError(index)
    return events[index]


def _flip(digest: str) -> str:
    first = "1" if digest[:1] == "0" else "0"
    return first + digest[1:]


def _linked(bodies: tuple[str, ...]) -> tuple[Event, ...]:
    prev = GENESIS
    rows: list[Event] = []
    for body in bodies:
        event = Event(prev, body, link_sha(prev, body))
        rows.append(event)
        prev = event.sha
    return tuple(rows)


@dataclass(frozen=True, slots=True)
class _Story:
    added: tuple[str, str, str]
    doing: tuple[str, str, str]
    done: tuple[str, str, str]
    rebuilt: tuple[str, str, str]
    placements: tuple[Placement, ...]
    events: tuple[Event, ...]
    chain: str
    live: Snapshot
    folded: Snapshot


def _story() -> _Story:
    board = Board()
    board.add_card("bisque")
    board.add_card("glaze")
    board.add_card("fire")
    added = (
        board.column_of("bisque"),
        board.column_of("glaze"),
        board.column_of("fire"),
    )
    board.move("bisque", "doing")
    board.move("glaze", "doing")
    board.move("fire", "doing")
    doing = (
        board.column_of("bisque"),
        board.column_of("glaze"),
        board.column_of("fire"),
    )
    board.move("bisque", "done")
    board.move("glaze", "done")
    board.move("fire", "done")
    folded = rebuild(board.events())
    done = (
        board.column_of("bisque"),
        board.column_of("glaze"),
        board.column_of("fire"),
    )
    rebuilt = (
        folded.column_of("bisque"),
        folded.column_of("glaze"),
        folded.column_of("fire"),
    )
    opened = _nth(board.events(), 0)
    try:
        Event(opened.prev_sha, opened.body, _flip(opened.sha))
    except Refuse as err:
        chain = err.code
    else:
        chain = "MISS"
    return _Story(
        added=added,
        doing=doing,
        done=done,
        rebuilt=rebuilt,
        placements=folded.cards(),
        events=board.events(),
        chain=chain,
        live=board.snapshot(),
        folded=folded.snapshot(),
    )


def test_example_kanban() -> None:
    first = _story()
    second = _story()
    assert first == second
    assert first.added == ("todo", "todo", "todo")
    assert first.doing == ("doing", "doing", "doing")
    assert first.done == ("done", "done", "done")
    assert first.rebuilt == first.done
    assert first.live == first.folded
    assert first.live.cap == POLICY_CAP
    assert first.live.schema == SCHEMA
    assert first.live.columns == (
        ("bisque", "done"),
        ("glaze", "done"),
        ("fire", "done"),
    )
    assert first.placements == (
        Placement("bisque", "done"),
        Placement("glaze", "done"),
        Placement("fire", "done"),
    )
    assert first.chain == "CHAIN"
    assert [event.body for event in first.events] == [
        "add|bisque|todo",
        "add|glaze|todo",
        "add|fire|todo",
        "move|bisque|doing",
        "move|glaze|doing",
        "move|fire|doing",
        "move|bisque|done",
        "move|glaze|done",
        "move|fire|done",
    ]
    prev = GENESIS
    for event in first.events:
        assert event.prev_sha == prev
        assert event.schema == SCHEMA
        assert event.sha == link_sha(prev, event.body)
        prev = event.sha
    assert first.live.tip == prev
    assert secret_shape(repr(first.events)) is False
    assert secret_shape(repr(first.live)) is False
    assert secret_shape(repr(first.placements)) is False


def test_schema_columns_and_direct_add() -> None:
    assert SCHEMA == "cosmos-hermes-kanban/1"
    assert COLUMNS == frozenset({"todo", "doing", "done"})
    assert KINDS == frozenset({"add", "move"})
    assert GENESIS == "0" * 64
    assert len(GENESIS) == 64
    board = Board()
    event = board.add_card("kiln", "doing")
    assert event == Event(GENESIS, "add|kiln|doing", link_sha(GENESIS, "add|kiln|doing"))
    board.move("kiln", "done")
    assert board.column_of("kiln") == "done"
    assert rebuild(board.events()).column_of("kiln") == "done"
    assert rebuild(board.events()).snapshot() == board.snapshot()


def test_empty_rebuild() -> None:
    board = rebuild(())
    assert board.events() == ()
    assert board.cards() == ()
    assert board.recorded_cap() == POLICY_CAP
    assert board.snapshot() == Snapshot(SCHEMA, POLICY_CAP, GENESIS, ())
    with pytest.raises(Refuse) as missing:
        board.column_of("bisque")
    assert missing.value.code == "UNKNOWN_CARD"


def test_duplicate_add_refuses() -> None:
    board = Board()
    board.add_card("bisque")
    board.move("bisque", "doing")
    with pytest.raises(Refuse) as dup:
        board.add_card("bisque", "done")
    assert dup.value.code == "DUPLICATE"
    assert str(dup.value) == "DUPLICATE"
    assert board.column_of("bisque") == "doing"
    assert len(board.events()) == 2
    rows = _linked(("add|glaze|todo", "add|glaze|doing"))
    with pytest.raises(Refuse) as folded:
        rebuild(rows)
    assert folded.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as snap:
        Snapshot(
            SCHEMA,
            2,
            GENESIS,
            (("bisque", "todo"), ("bisque", "done")),
        )
    assert snap.value.code == "DUPLICATE"


def test_unknown_move_leaves_the_chain() -> None:
    board = Board()
    board.add_card("bisque")
    with pytest.raises(Refuse) as missing:
        board.move("glaze", "doing")
    assert missing.value.code == "UNKNOWN_CARD"
    assert board.column_of("bisque") == "todo"
    assert len(board.events()) == 1
    with pytest.raises(Refuse) as folded:
        rebuild(_linked(("move|fire|doing",)))
    assert folded.value.code == "UNKNOWN_CARD"


@pytest.mark.parametrize(
    "body",
    [
        "add|bisque",
        "add",
        "",
        "add|bisque|todo|extra",
        "add|bisque|todo|",
    ],
)
def test_bad_body_refuses(body: str) -> None:
    digest = link_sha(GENESIS, body)
    with pytest.raises(Refuse) as err:
        Event(GENESIS, body, digest)
    assert err.value.code == "BAD_BODY"
    assert not isinstance(err.value, ValueError)


@pytest.mark.parametrize(
    ("body", "code"),
    [
        ("jump|bisque|todo", "BAD_EVENT"),
        ("Add|bisque|todo", "BAD_EVENT"),
        ("|bisque|todo", "BAD_EVENT"),
        ("add|bisque|later", "BAD_COLUMN"),
        ("add|bisque|todo ", "BAD_COLUMN"),
        ("add||todo", "EMPTY"),
        ("add|   |todo", "EMPTY"),
        ("add|Bisque|todo", "BAD_CARD"),
        ("add|a.b|todo", "BAD_CARD"),
        ("add|-bisque|todo", "BAD_CARD"),
        ("add|../x|todo", "BAD_CARD"),
    ],
)
def test_body_fields(body: str, code: str) -> None:
    with pytest.raises(Refuse) as err:
        Event(GENESIS, body, link_sha(GENESIS, body))
    assert err.value.code == code


def test_chain_and_bad_sha() -> None:
    body = "add|bisque|todo"
    with pytest.raises(Refuse) as tampered:
        Event(GENESIS, body, "f" * 64)
    assert tampered.value.code == "CHAIN"
    with pytest.raises(Refuse) as upper:
        Event(GENESIS, body, "F" * 64)
    assert upper.value.code == "BAD_SHA"
    with pytest.raises(Refuse) as short:
        Event("0" * 63, body, "f" * 64)
    assert short.value.code == "BAD_SHA"
    with pytest.raises(Refuse) as huge:
        link_sha("0" * 65, body)
    assert huge.value.code == "OVERSIZE"
    first = _nth(_linked((body,)), 0)
    other = _nth(_linked(("add|glaze|todo",)), 0)
    with pytest.raises(Refuse) as fork:
        rebuild((first, other))
    assert fork.value.code == "CHAIN"
    prev = "1" * 64
    lone = Event(prev, body, link_sha(prev, body))
    with pytest.raises(Refuse) as genesis:
        rebuild((lone,))
    assert genesis.value.code == "CHAIN"


def test_secrets_are_not_stored() -> None:
    board = Board()
    samples = (
        "sk-abcdefghij",
        "token=supersecretvalue",
        "Bearer abcdefghijk",
        "password = hunter22",
    )
    for card in samples:
        with pytest.raises(Refuse) as err:
            board.add_card(card)
        assert err.value.code == "SECRET"
        assert secret_shape(str(err.value)) is False
    with pytest.raises(Refuse) as column:
        board.add_card("bisque", "api_key=abcd")
    assert column.value.code == "SECRET"
    assert board.events() == ()
    with pytest.raises(Refuse) as body:
        Event(GENESIS, "add|sk-abcdefghij|todo", "ab" * 32)
    assert body.value.code == "SECRET"
    with pytest.raises(Refuse) as kind:
        Event(GENESIS, "sk-abcdefghij|bisque|todo", "ab" * 32)
    assert kind.value.code == "SECRET"
    with pytest.raises(Refuse) as digest:
        link_sha(GENESIS, "add|sk-abcdefghij|todo")
    assert digest.value.code == "SECRET"
    with pytest.raises(Refuse) as named:
        Event(GENESIS, "add|bisque|todo", link_sha(GENESIS, "add|bisque|todo"), schema="sk-abcdefghij")
    assert named.value.code == "SECRET"


def test_bounds_and_types() -> None:
    board = Board()
    with pytest.raises(Refuse) as empty:
        board.add_card("")
    assert empty.value.code == "EMPTY"
    with pytest.raises(Refuse) as blank:
        board.add_card("   ")
    assert blank.value.code == "EMPTY"
    with pytest.raises(Refuse) as missing:
        board.add_card(None)
    assert missing.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as number:
        board.add_card(1)
    assert number.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as raw:
        board.add_card(b"bisque")
    assert raw.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as flag:
        board.add_card("bisque", True)
    assert flag.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        board.add_card("bis\x00que")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as wide:
        board.add_card("a" * (CARD_LIMIT + 1))
    assert wide.value.code == "OVERSIZE"
    assert wide.value.detail == str(CARD_LIMIT)
    kept = board.add_card("a" * CARD_LIMIT)
    assert kept.body == f"add|{'a' * CARD_LIMIT}|todo"
    with pytest.raises(Refuse) as column:
        board.add_card("bisque", "x" * (COLUMN_LIMIT + 1))
    assert column.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as later:
        board.add_card("bisque", "later")
    assert later.value.code == "BAD_COLUMN"
    long_body = "x" * (BODY_LIMIT + 1)
    with pytest.raises(Refuse) as body:
        Event(GENESIS, long_body, GENESIS)
    assert body.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as card_in_body:
        Event(GENESIS, f"add|{'a' * (CARD_LIMIT + 1)}|todo", GENESIS)
    assert card_in_body.value.code == "OVERSIZE"
    assert board.events() == (kept,)


def test_cap_is_recorded_and_not_raised() -> None:
    high = Board(POLICY_CAP + 50)
    assert high.recorded_cap() == POLICY_CAP
    assert high.snapshot().cap == POLICY_CAP
    for index in range(POLICY_CAP):
        high.add_card(f"n{index}")
    with pytest.raises(Refuse) as full:
        high.add_card("extra")
    assert full.value.code == "CARD_CAP"
    high.move("n0", "doing")
    assert high.column_of("n0") == "doing"
    assert high.column_of("n1") == "todo"
    assert len(high.cards()) == POLICY_CAP
    low = Board(1)
    assert low.recorded_cap() == 1
    low.add_card("bisque")
    with pytest.raises(Refuse) as tight:
        low.add_card("glaze")
    assert tight.value.code == "CARD_CAP"
    low.move("bisque", "done")
    assert low.column_of("bisque") == "done"
    assert rebuild(low.events(), 1).snapshot() == low.snapshot()
    with pytest.raises(Refuse) as smaller:
        rebuild(low.events(), 0)
    assert smaller.value.code == "OUT_OF_RANGE"
    grown = Board()
    grown.add_card("bisque")
    grown.add_card("glaze")
    with pytest.raises(Refuse) as replay:
        rebuild(grown.events(), 1)
    assert replay.value.code == "CARD_CAP"
    again = rebuild(grown.events(), POLICY_CAP + 9)
    assert again.recorded_cap() == POLICY_CAP
    assert again.snapshot() == grown.snapshot()
    with pytest.raises(Refuse) as boolean:
        Board(True)
    assert boolean.value.code == "NOT_INT"
    with pytest.raises(Refuse) as text:
        Board("64")
    assert text.value.code == "NOT_INT"
    with pytest.raises(Refuse) as zero:
        Board(0)
    assert zero.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as negative:
        Board(-3)
    assert negative.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as snap_cap:
        Snapshot(SCHEMA, POLICY_CAP + 1, GENESIS, ())
    assert snap_cap.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as snap_bool:
        Snapshot(SCHEMA, cast(int, True), GENESIS, ())
    assert snap_bool.value.code == "NOT_INT"
    with pytest.raises(Refuse) as snap_count:
        Snapshot(SCHEMA, 1, GENESIS, (("bisque", "todo"), ("glaze", "todo")))
    assert snap_count.value.code == "CARD_CAP"


def test_event_cap() -> None:
    board = Board(1)
    board.add_card("bisque")
    column = "doing"
    while len(board.events()) < EVENT_CAP:
        board.move("bisque", column)
        column = "done" if column == "doing" else "doing"
    assert len(board.events()) == EVENT_CAP
    with pytest.raises(Refuse) as capped:
        board.move("bisque", column)
    assert capped.value.code == "EVENT_CAP"
    assert len(board.events()) == EVENT_CAP
    assert rebuild(board.events(), 1).column_of("bisque") == board.column_of("bisque")
    tip = _nth(board.events(), EVENT_CAP - 1)
    extra_body = "move|bisque|todo"
    extra = Event(tip.sha, extra_body, link_sha(tip.sha, extra_body))
    with pytest.raises(Refuse) as folded:
        rebuild(board.events() + (extra,))
    assert folded.value.code == "EVENT_CAP"


def test_bad_events_schema_snapshot_and_placement() -> None:
    with pytest.raises(Refuse) as listed:
        rebuild(["nope"])
    assert listed.value.code == "BAD_EVENTS"
    with pytest.raises(Refuse) as text:
        rebuild("add|bisque|todo")
    assert text.value.code == "BAD_EVENTS"
    with pytest.raises(Refuse) as raw:
        rebuild(b"add|bisque|todo")
    assert raw.value.code == "BAD_EVENTS"
    with pytest.raises(Refuse) as row:
        rebuild((Event(GENESIS, "add|bisque|todo", link_sha(GENESIS, "add|bisque|todo")), "glaze"))
    assert row.value.code == "BAD_EVENT"
    good = link_sha(GENESIS, "add|bisque|todo")
    with pytest.raises(Refuse) as schema:
        Event(GENESIS, "add|bisque|todo", good, schema="cosmos-hermes-kanban/2")
    assert schema.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as snap:
        Snapshot("cosmos-hermes-kanban/2", POLICY_CAP, GENESIS, ())
    assert snap.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as tip:
        Snapshot(SCHEMA, POLICY_CAP, "zz" * 32, ())
    assert tip.value.code == "BAD_SHA"
    broken = cast(tuple[tuple[str, str], ...], (("bisque",),))
    with pytest.raises(Refuse) as shape:
        Snapshot(SCHEMA, POLICY_CAP, GENESIS, broken)
    assert shape.value.code == "BAD_SNAPSHOT"
    with pytest.raises(Refuse) as placed:
        Placement("Bisque", "todo")
    assert placed.value.code == "BAD_CARD"
    with pytest.raises(Refuse) as dest:
        Placement("bisque", "later")
    assert dest.value.code == "BAD_COLUMN"
    with pytest.raises(Refuse) as secret:
        Placement("sk-abcdefghij", "todo")
    assert secret.value.code == "SECRET"
