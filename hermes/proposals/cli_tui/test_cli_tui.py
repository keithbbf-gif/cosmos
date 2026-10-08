"""Refusal and success coverage for the CLI composer."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

import pytest

from cli_tui import (
    ASK_MAX,
    BUFFER_CAP,
    COMMANDS,
    EFFECT,
    HISTORY_CAP,
    INDEX_MAX,
    JOIN_CAP,
    LINE_CAP,
    SCHEMA,
    Buffer,
    Descriptor,
    HistoryItem,
    Interrupt,
    Plain,
    Policy,
    Session,
    Transcript,
    parse,
    rebuild,
    restore,
)
from cosmos_hermes import Refuse, secret_shape


def _at(items: tuple[HistoryItem, ...], index: int) -> HistoryItem:
    if index < 0 or index >= len(items):
        raise AssertionError(index)
    return items[index]


def _draft(session: Session) -> tuple[str, ...]:
    return session.buffer.lines


def _line(lines: tuple[str, ...], index: int) -> str:
    if index < 0 or index >= len(lines):
        raise AssertionError(index)
    return lines[index]


def _code(func: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        func()
    assert secret_shape(str(caught.value)) is False
    assert secret_shape(repr(caught.value)) is False
    return str(caught.value.code)


def _clean(value: object) -> None:
    assert secret_shape(repr(value)) is False
    assert secret_shape(str(value)) is False


def _parse_at(line: object, checkpoints: object = None) -> Callable[[], object]:
    def run() -> Descriptor | Plain:
        return parse(line, checkpoints=checkpoints)

    return run


def _accept_at(session: Session, line: object, checkpoints: object = None) -> Callable[[], object]:
    def run() -> Descriptor | Plain:
        return session.accept(line, checkpoints=checkpoints)

    return run


def _append_at(session: Session, line: object) -> Callable[[], object]:
    def run() -> Buffer:
        return session.append_line(line)

    return run


def _flush_at(session: Session) -> Callable[[], object]:
    def run() -> Plain:
        return session.flush()

    return run


def _session_at(history_cap: object = None, buffer_cap: object = None) -> Callable[[], object]:
    def run() -> Session:
        return Session(history_cap=history_cap, buffer_cap=buffer_cap)

    return run


def _descriptor_at(
    schema: str,
    name: str,
    args: tuple[str, ...],
    index: int | None,
    catalog: tuple[str, ...],
    effect: str,
) -> Callable[[], object]:
    def run() -> Descriptor:
        return Descriptor(schema, name, args, index, catalog, effect)

    return run


def _plain_at(schema: str, text: str, kind: str) -> Callable[[], object]:
    def run() -> Plain:
        return Plain(schema, text, kind)

    return run


def _history_at(schema: str, kind: str, text: str, name: str) -> Callable[[], object]:
    def run() -> HistoryItem:
        return HistoryItem(schema, kind, text, name)

    return run


def _interrupt_at(schema: str, flagged: bool) -> Callable[[], object]:
    def run() -> Interrupt:
        return Interrupt(schema, flagged)

    return run


def _policy_at(
    schema: str,
    history_cap: int,
    asked_history_cap: int,
    history_capped: bool,
    buffer_cap: int,
    asked_buffer_cap: int,
    buffer_capped: bool,
) -> Callable[[], object]:
    def run() -> Policy:
        return Policy(
            schema,
            history_cap,
            asked_history_cap,
            history_capped,
            buffer_cap,
            asked_buffer_cap,
            buffer_capped,
        )

    return run


def _buffer_at(
    schema: str,
    lines: tuple[str, ...],
    text: str,
    count: int,
    cap: int,
    policy_cap: int,
    asked_cap: int,
    capped: bool,
) -> Callable[[], object]:
    def run() -> Buffer:
        return Buffer(schema, lines, text, count, cap, policy_cap, asked_cap, capped)

    return run


def test_schema_and_exports() -> None:
    assert SCHEMA == "cosmos-hermes-cli_tui/1"
    assert COMMANDS == ("help", "tools", "model", "approval", "rollback", "interrupt")
    assert EFFECT == "none"
    assert HISTORY_CAP == 50
    assert JOIN_CAP == BUFFER_CAP * LINE_CAP + (BUFFER_CAP - 1)
    exported = __import__("cli_tui").__all__
    for name in (
        "parse",
        "Session",
        "Descriptor",
        "Plain",
        "Transcript",
        "rebuild",
        "restore",
        "SCHEMA",
        "HISTORY_CAP",
        "BUFFER_CAP",
        "JOIN_CAP",
    ):
        assert name in exported


def test_parse_help_is_frozen_and_has_no_side_effect() -> None:
    session = Session()
    session.accept("keep")
    session.append_line("draft")
    before = (session.history, session.buffer, session.interrupted, session.policy)
    found = parse("/help")
    again = parse("/help")
    assert found == again
    assert isinstance(found, Descriptor)
    assert found == Descriptor(SCHEMA, "help", (), None, COMMANDS, EFFECT)
    assert found.effect == "none"
    assert (session.history, session.buffer, session.interrupted, session.policy) == before
    with pytest.raises(AttributeError):
        setattr(found, "name", "tools")
    _clean(found)
    _clean(session)


def test_commands_and_plain_text() -> None:
    assert parse("/HELP") == parse("/help")
    assert parse("  /tools") == Descriptor(SCHEMA, "tools", (), None, (), EFFECT)
    assert parse("/model") == Descriptor(SCHEMA, "model", (), None, (), EFFECT)
    assert parse("/model anthropic/claude-sonnet-4") == Descriptor(
        SCHEMA, "model", ("anthropic/claude-sonnet-4",), None, (), EFFECT
    )
    assert parse("/approval") == Descriptor(SCHEMA, "approval", (), None, (), EFFECT)
    assert parse("/approval MANUAL") == Descriptor(SCHEMA, "approval", ("manual",), None, (), EFFECT)
    assert parse("/rollback") == Descriptor(SCHEMA, "rollback", (), None, (), EFFECT)
    listed = parse("/rollback 0002", checkpoints=2)
    assert listed == Descriptor(SCHEMA, "rollback", ("2",), 2, (), EFFECT)
    assert parse("/rollback 99") == Descriptor(SCHEMA, "rollback", ("99",), 99, (), EFFECT)
    assert parse("/interrupt") == Descriptor(SCHEMA, "interrupt", (), None, (), EFFECT)
    plain = parse("hello")
    assert isinstance(plain, Plain)
    assert plain == Plain(SCHEMA, "hello", "text")
    assert parse("  spaced  ") == Plain(SCHEMA, "  spaced  ", "text")
    assert parse("") == Plain(SCHEMA, "", "text")
    assert parse("porch\tlight") == Plain(SCHEMA, "porch\tlight", "text")
    assert parse("!git status") == Plain(SCHEMA, "!git status", "text")
    assert parse("/help") == parse("/help")
    _clean(plain)


def test_interrupt_flag_is_separate_from_the_slash() -> None:
    session = Session()
    assert session.interrupted is False
    assert type(session.interrupted) is bool
    interrupted = parse("/interrupt")
    assert isinstance(interrupted, Descriptor)
    assert interrupted.name == "interrupt"
    assert session.interrupted is False
    accepted = session.accept("/interrupt")
    assert isinstance(accepted, Descriptor)
    assert accepted.effect == "none"
    assert session.interrupted is False
    latest = _at(session.history, len(session.history) - 1)
    assert latest.kind == "slash"
    assert latest.name == "interrupt"
    assert latest.text == "/interrupt"
    flag = session.interrupt()
    assert flag == Interrupt(SCHEMA, True)
    assert session.interrupted is True
    assert type(session.interrupted) is bool
    assert session.interrupt() == flag
    assert len(session.history) == 1
    session.accept("still here")
    assert session.interrupted is True
    _clean(flag)


def test_history_cap_and_asked_cap() -> None:
    capped = Session(history_cap=ASK_MAX, buffer_cap=1_000)
    assert capped.policy.history_cap == HISTORY_CAP
    assert capped.policy.asked_history_cap == ASK_MAX
    assert capped.policy.history_capped is True
    assert type(capped.policy.history_capped) is bool
    assert capped.policy.buffer_cap == BUFFER_CAP
    assert capped.policy.asked_buffer_cap == 1_000
    assert capped.policy.buffer_capped is True
    assert type(capped.policy.buffer_capped) is bool
    assert capped.policy.schema == SCHEMA
    for number in range(HISTORY_CAP + 1):
        capped.accept(f"m{number}")
    assert len(capped.history) == HISTORY_CAP
    assert [item.text for item in capped.history] == [f"m{number}" for number in range(1, HISTORY_CAP + 1)]
    assert _at(capped.history, 0).kind == "text"
    small = Session(history_cap=2, buffer_cap=2)
    assert small.policy.history_capped is False
    assert small.policy.history_cap == 2
    small.accept("/help")
    small.accept("b")
    small.accept("c")
    assert [item.text for item in small.history] == ["b", "c"]
    default = Session()
    assert default.policy.history_cap == HISTORY_CAP
    assert default.policy.asked_history_cap == HISTORY_CAP
    assert default.policy.history_capped is False
    _clean(capped.policy)


def test_multiline_buffer() -> None:
    session = Session(buffer_cap=2)
    assert session.buffer.count == 0
    assert session.buffer.text == ""
    assert session.buffer.policy_cap == BUFFER_CAP
    assert session.buffer.cap == 2
    assert len(session.history) == 0
    held = session.append_line("/help")
    assert held.lines == ("/help",)
    assert len(session.history) == 0
    session.append_line("two")
    assert session.buffer.text == "/help\ntwo"
    assert _code(_append_at(session, "three")) == "BUFFER_FULL"
    assert session.buffer.lines == ("/help", "two")
    flushed = session.flush()
    assert flushed == Plain(SCHEMA, "/help\ntwo", "text")
    assert session.buffer.count == 0
    flushed_item = _at(session.history, len(session.history) - 1)
    assert flushed_item.text == "/help\ntwo"
    assert flushed_item.kind == "text"
    assert flushed_item.name == ""
    assert _code(_flush_at(session)) == "EMPTY_BUFFER"
    wide = Session(buffer_cap=ASK_MAX)
    assert wide.buffer.cap == BUFFER_CAP
    assert wide.buffer.capped is True
    assert type(wide.buffer.capped) is bool
    for _ in range(BUFFER_CAP):
        wide.append_line("x")
    assert _code(_append_at(wide, "y")) == "BUFFER_FULL"
    _clean(held)


def test_rollback_retry() -> None:
    session = Session()
    assert _code(_parse_at("/rollback 9", checkpoints=0)) == "ROLLBACK_MISS"
    assert len(session.history) == 0
    assert _code(_accept_at(session, "/rollback 9", checkpoints=0)) == "ROLLBACK_MISS"
    assert len(session.history) == 0
    assert session.transcript().misses == 1
    restored = session.accept("/rollback 1", checkpoints=1)
    assert isinstance(restored, Descriptor)
    assert restored.index == 1
    assert _at(session.history, len(session.history) - 1).name == "rollback"
    assert session.transcript().misses == 0
    assert _code(_accept_at(session, "/rollback 4", checkpoints=1)) == "ROLLBACK_MISS"
    assert _code(_accept_at(session, "/rollback 4", checkpoints=1)) == "RETRY_CAP"
    assert _at(session.history, len(session.history) - 1).text != "/rollback 4"
    carried = restore(session.transcript())
    assert carried.transcript() == session.transcript()
    assert _code(_accept_at(carried, "/rollback 4", checkpoints=1)) == "RETRY_CAP"
    fresh = Session()
    assert _code(_accept_at(fresh, "/rollback 2", checkpoints=1)) == "ROLLBACK_MISS"
    fresh.accept("/rollback")
    assert _code(_accept_at(fresh, "/rollback 2", checkpoints=1)) == "RETRY_CAP"
    again = Session()
    assert _code(_accept_at(again, "/rollback foo")) == "BAD_INDEX"
    assert _code(_accept_at(again, "/rollback foo")) == "BAD_INDEX"


def test_split_secret_does_not_stick() -> None:
    session = Session()
    session.append_line("sk-")
    assert _code(_append_at(session, "livekey12")) == "SECRET"
    kept = _draft(session)
    assert len(kept) == 1
    assert _line(kept, 0) == "sk-"
    assert "livekey12" not in repr(session)
    assert "livekey12" not in repr(session.buffer)
    session.append_line("porch note")
    later = _draft(session)
    assert (_line(later, 0), _line(later, 1)) == ("sk-", "porch note")
    _clean(session.buffer)


def test_refusal_codes() -> None:
    assert _code(_parse_at(None)) == "NOT_TEXT"
    assert _code(_parse_at(12)) == "NOT_TEXT"
    assert _code(_parse_at("a\x00b")) == "NULL_BYTE"
    assert _code(_parse_at("x" * (LINE_CAP + 1))) == "OVERSIZE"
    assert _code(_parse_at("a\nb")) == "BAD_LINE"
    assert _code(_parse_at("a\rb")) == "BAD_LINE"
    assert _code(_parse_at("esc\x1b[31m")) == "BAD_LINE"
    assert _code(_parse_at("bad\u202e/help")) == "BAD_LINE"
    assert _code(_parse_at("hi\u2069there")) == "BAD_LINE"
    assert _code(_parse_at("hi\u2028there")) == "BAD_LINE"
    assert _code(_parse_at("hi\x85there")) == "BAD_LINE"
    assert _code(_parse_at("\uff0fhelp")) == "BAD_LINE"
    key = "sk-" + "livekey1"
    assert _code(_parse_at("/model " + key)) == "SECRET"
    assert _code(_parse_at("token = hunter2")) == "SECRET"
    assert _code(_parse_at("Bearer " + "abcdefghij")) == "SECRET"
    session = Session()
    session.append_line("token")
    assert _code(_append_at(session, "= " + "abcdefgh")) == "SECRET"
    assert session.buffer.lines == ("token",)
    assert "abcdefgh" not in repr(session)
    assert _code(_parse_at("/nope")) == "UNKNOWN_COMMAND"
    assert _code(_parse_at("/")) == "UNKNOWN_COMMAND"
    assert _code(_parse_at("/ yolo")) == "UNKNOWN_COMMAND"
    assert _code(_parse_at("/yolo")) == "UNKNOWN_COMMAND"
    assert _code(_parse_at("//help")) == "UNKNOWN_COMMAND"
    assert _code(_parse_at("/help extra")) == "BAD_ARGS"
    assert _code(_parse_at("/tools x")) == "BAD_ARGS"
    assert _code(_parse_at("/interrupt now")) == "BAD_ARGS"
    assert _code(_parse_at("/model a b")) == "BAD_ARGS"
    assert _code(_parse_at("/model bad id")) == "BAD_ARGS"
    assert _code(_parse_at("/rollback 1 2")) == "BAD_ARGS"
    assert _code(_parse_at("/approval manual extra")) == "BAD_ARGS"
    assert _code(_parse_at("/approval off")) == "BAD_MODE"
    assert _code(_parse_at("/approval yolo")) == "BAD_MODE"
    assert _code(_parse_at("/approval smart")) == "BAD_MODE"
    assert _code(_parse_at("/approval always")) == "BAD_MODE"
    assert _code(_parse_at("/rollback foo")) == "BAD_INDEX"
    assert _code(_parse_at("/rollback 0")) == "BAD_INDEX"
    assert _code(_parse_at("/rollback -1")) == "BAD_INDEX"
    assert _code(_parse_at("/rollback " + str(INDEX_MAX + 1))) == "OUT_OF_RANGE"
    assert _code(_parse_at("/rollback 1", checkpoints=True)) == "NOT_INT"
    assert _code(_parse_at("/rollback 1", checkpoints=INDEX_MAX + 1)) == "OUT_OF_RANGE"
    assert _code(_session_at(history_cap=0)) == "BAD_LIMIT"
    assert _code(_session_at(history_cap=True)) == "BAD_LIMIT"
    assert _code(_session_at(history_cap="50")) == "BAD_LIMIT"
    assert _code(_session_at(buffer_cap=-1)) == "BAD_LIMIT"
    assert _code(_session_at(history_cap=ASK_MAX + 1)) == "BAD_LIMIT"
    assert _code(_accept_at(Session(), "/missing")) == "UNKNOWN_COMMAND"
    assert Session().history == ()
    _clean(Session())


def test_record_guards() -> None:
    assert _code(_descriptor_at("other", "help", (), None, COMMANDS, EFFECT)) == "BAD_SCHEMA"
    assert _code(_descriptor_at(SCHEMA, "help", (), None, COMMANDS, "run")) == "BAD_EFFECT"
    assert _code(_descriptor_at(SCHEMA, "help", (), None, COMMANDS, "yolo")) == "BAD_EFFECT"
    assert _code(_descriptor_at(SCHEMA, "nope", (), None, (), EFFECT)) == "UNKNOWN_COMMAND"
    assert _code(_descriptor_at(SCHEMA, "help", ("x",), None, COMMANDS, EFFECT)) == "BAD_ARGS"
    assert _code(_descriptor_at(SCHEMA, "rollback", ("1",), True, (), EFFECT)) == "BAD_INDEX"
    assert _code(_plain_at("nope", "hi", "text")) == "BAD_SCHEMA"
    assert _code(_plain_at(SCHEMA, "hi", "slash")) == "BAD_KIND"
    assert _code(_plain_at(SCHEMA, "sk-" + "livekey1", "text")) == "SECRET"
    assert _code(_plain_at(SCHEMA, "esc\x1b[31m", "text")) == "BAD_LINE"
    assert _code(_plain_at(SCHEMA, "a\x00b", "text")) == "NULL_BYTE"
    assert _code(_history_at("nope", "text", "hi", "")) == "BAD_SCHEMA"
    assert _code(_history_at(SCHEMA, "other", "hi", "")) == "BAD_KIND"
    assert _code(_history_at(SCHEMA, "text", "hi", "help")) == "BAD_KIND"
    assert _code(_history_at(SCHEMA, "slash", "/help", "tools")) == "BAD_KIND"
    assert _code(_history_at(SCHEMA, "slash", "/nope", "nope")) == "UNKNOWN_COMMAND"
    assert _code(_interrupt_at("nope", True)) == "BAD_SCHEMA"
    assert _code(_interrupt_at(SCHEMA, False)) == "BAD_FLAG"
    assert _code(_policy_at("nope", HISTORY_CAP, HISTORY_CAP, False, BUFFER_CAP, BUFFER_CAP, False)) == "BAD_SCHEMA"
    assert _code(_policy_at(SCHEMA, 10, 100, True, BUFFER_CAP, BUFFER_CAP, False)) == "BAD_LIMIT"
    assert _code(_policy_at(SCHEMA, HISTORY_CAP, HISTORY_CAP, True, BUFFER_CAP, BUFFER_CAP, False)) == "BAD_LIMIT"
    assert _code(_buffer_at("nope", (), "", 0, BUFFER_CAP, BUFFER_CAP, BUFFER_CAP, False)) == "BAD_SCHEMA"
    assert _code(_buffer_at(SCHEMA, ("a",), "b", 1, BUFFER_CAP, BUFFER_CAP, BUFFER_CAP, False)) == "BAD_KIND"
    assert _code(_buffer_at(SCHEMA, (), "", 0, BUFFER_CAP, BUFFER_CAP, BUFFER_CAP, cast(bool, 1))) == "BAD_FLAG"
    built = HistoryItem(SCHEMA, "slash", "/help", "help")
    assert built.name == "help"
    _clean(built)


def test_rebuild_round_trip() -> None:
    session = Session(history_cap=4, buffer_cap=3)
    session.accept("/help")
    session.append_line("draft card")
    session.interrupt()
    shot = session.transcript()
    assert rebuild(shot) == shot
    assert rebuild(shot) is not shot
    opened = restore(shot)
    assert opened.transcript() == shot
    assert opened.interrupted is True
    assert opened.buffer.lines == ("draft card",)
    opened.accept("later note")
    assert opened.transcript() != shot
    assert rebuild(shot) == shot

    def bad_record() -> Transcript:
        return rebuild(session)

    assert _code(bad_record) == "BAD_KIND"

    def bad_miss() -> Transcript:
        return Transcript(SCHEMA, shot.policy, shot.history, shot.lines, False, True)

    assert _code(bad_miss) == "BAD_LIMIT"

    def bad_flag() -> Transcript:
        return Transcript(SCHEMA, shot.policy, shot.history, shot.lines, cast(bool, 1), 0)

    assert _code(bad_flag) == "BAD_FLAG"

    def oversized() -> Plain:
        return Plain(SCHEMA, "x" * (JOIN_CAP + 1), "text")

    with pytest.raises(Refuse) as caught:
        oversized()
    assert caught.value.code == "OVERSIZE"
    assert caught.value.detail == str(JOIN_CAP)


def _porch_story() -> Transcript:
    """Mira's evening: help, a note, then a named rollback. Interrupt stays a descriptor."""
    session = Session()
    assert len(session.history) == 0
    listed = session.accept("/help")
    assert isinstance(listed, Descriptor)
    assert listed.name == "help"
    assert listed.effect == "none"
    assert listed.catalog == COMMANDS
    note = session.accept("Mira left a card on the porch-light note before the evening session.")
    assert isinstance(note, Plain)
    assert note.kind == "text"
    rolled = session.accept("/rollback 1", checkpoints=2)
    assert isinstance(rolled, Descriptor)
    assert rolled.name == "rollback"
    assert rolled.index == 1
    assert rolled.effect == "none"
    stopped = parse("/interrupt")
    assert isinstance(stopped, Descriptor)
    assert stopped.name == "interrupt"
    assert stopped.effect == "none"
    assert session.interrupted is False

    def hidden() -> Descriptor | Plain:
        return session.accept("api_key=" + "porch-session-key")

    with pytest.raises(Refuse) as caught:
        hidden()
    assert caught.value.code == "SECRET"
    assert secret_shape(str(caught.value)) is False
    assert "porch-session-key" not in repr(session)
    first = _at(session.history, 0)
    middle = _at(session.history, 1)
    last = _at(session.history, len(session.history) - 1)
    assert first.name == "help"
    assert middle.kind == "text"
    assert middle.name == ""
    assert "card" in middle.text
    assert "note" in middle.text
    assert last.name == "rollback"
    assert last.kind == "slash"
    shot = session.transcript()
    assert rebuild(shot) == shot
    assert rebuild(shot) is not shot
    assert "porch-session-key" not in repr(shot)
    return shot


def test_example_cli_tui() -> None:
    assert _porch_story() == _porch_story()
