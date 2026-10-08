"""Reply plans, roster cap, and the refusal to approve or open a terminal."""

from __future__ import annotations

import inspect

import pytest

from bot_mode import (
    GENESIS,
    POLICY_FANOUT,
    POLICY_ROSTER,
    POLICY_SCREEN,
    REPLY_KIND,
    SCHEMA,
    Bot,
    Caps,
    Record,
    ReplyPlan,
    Roster,
    Snapshot,
    approve,
    enable_terminal,
    make_roster,
    rebuild,
    register,
    room_message,
    route,
    screen,
    snapshot,
)
from cosmos_hermes import Refuse, secret_shape


def _ready(*pairs: tuple[str, str]) -> Roster:
    state = make_roster()
    for bot_id, specialty in pairs:
        state = register(state, bot_id, specialty)
    return state


def _say(text: str, *, room: str = "lab-session", sender: str = "ada") -> object:
    return room_message(room, sender, text)


def _record(records: tuple[Record, ...], index: int) -> Record:
    if index < 0 or index >= len(records):
        raise AssertionError("missing record")
    return records[index]


def _bot(state: Roster) -> Bot:
    if not state.bots:
        raise AssertionError("missing bot")
    return state.bots[0]


def test_schema_and_policy_caps() -> None:
    assert SCHEMA == "cosmos-hermes-bot_mode/1"
    assert REPLY_KIND == "reply"
    state = make_roster()
    assert state.caps.roster == POLICY_ROSTER == 20
    assert state.caps.fanout == POLICY_FANOUT == 3
    assert state.caps.screen == POLICY_SCREEN == 20
    assert state.bots == ()
    assert screen(state) == ()
    assert rebuild(snapshot(state)) == state
    wide = make_roster(100, 9, 80)
    assert wide.caps.requested_roster == 100
    assert wide.caps.roster == 20
    assert wide.caps.requested_fanout == 9
    assert wide.caps.fanout == 3
    assert wide.caps.requested_screen == 80
    assert wide.caps.screen == 20
    assert rebuild(snapshot(wide)) == wide


def test_register_route_and_screen() -> None:
    base = make_roster()
    state = register(base, "researcher", "reads sources")
    assert base.bots == ()
    assert state.bots == (Bot("researcher", "reads sources", "ready"),)
    sent = route(state, _say("please @researcher look at the note"))
    assert sent == ReplyPlan(
        room="lab-session",
        sender="ada",
        bot_ids=("researcher",),
        specialties=("reads sources",),
        rounds=(1,),
        kind="reply",
        fanout=False,
        enables_terminal=False,
        approves_tool=False,
    )
    assert screen(state) == ("researcher\treads sources\tready",)
    assert "note" not in repr(sent)
    assert not secret_shape(repr(state))
    assert not secret_shape(repr(sent))
    again = route(state, _say("please @researcher look at the note"))
    assert again == sent
    assert snapshot(state) == snapshot(rebuild(snapshot(state)))


def test_example_bot_mode() -> None:
    first = _story()
    second = _story()
    assert first == second
    plan, lines, shell_code, terminal_code, image = first
    assert plan.kind == "reply"
    assert plan.enables_terminal is False
    assert plan.approves_tool is False
    assert plan.room == "lab-session"
    assert plan.sender == "ada"
    assert plan.bot_ids == ("researcher",)
    assert plan.rounds == (1,)
    assert plan.fanout is False
    assert "light" not in repr(plan)
    assert "shell" not in repr(plan)
    assert lines == (
        "researcher\treads the note\tready",
        "scribe\tfiles the card\tready",
    )
    assert shell_code == "BOT_APPROVAL"
    assert terminal_code == "NO_TERMINAL"
    assert image.tip != GENESIS
    first_link = _record(image.records, 0)
    second_link = _record(image.records, 1)
    assert first_link.prev == GENESIS
    assert second_link.prev == first_link.digest
    assert snapshot(rebuild(image)) == image


def _story() -> tuple[ReplyPlan, tuple[str, ...], str, str, Snapshot]:
    roster = make_roster()
    roster = register(roster, "researcher", "reads the note")
    roster = register(roster, "scribe", "files the card")
    note = room_message(
        "lab-session",
        "ada",
        "@researcher the note under the light belongs with the card",
    )
    plan = route(roster, note)
    lines = screen(roster)
    image = snapshot(roster)
    restored = rebuild(image)
    if restored != roster or route(restored, note) != plan:
        raise AssertionError("story drifted")
    shell_code = ""
    try:
        route(
            roster,
            room_message(
                "lab-session",
                "ada",
                "@researcher please approve the shell command for the card",
            ),
        )
    except Refuse as refused:
        shell_code = refused.code
    terminal_code = ""
    try:
        enable_terminal("lab-session")
    except Refuse as refused:
        terminal_code = refused.code
    return plan, lines, shell_code, terminal_code, image


def test_roster_cap_blocks_the_twenty_first() -> None:
    state = make_roster()
    for index in range(POLICY_ROSTER):
        state = register(state, f"bot-{index}", f"job {index}")
    assert len(state.bots) == 20
    assert len(screen(state)) == 20
    assert len(screen(state, 10_000)) == 20
    with pytest.raises(Refuse) as caught:
        register(state, "bot-extra", "overflow")
    assert caught.value.code == "BOT_CAP"
    assert len(state.bots) == 20
    tight = make_roster(2, 1, 1)
    tight = register(tight, "alpha", "one job")
    tight = register(tight, "beta", "other job")
    assert tight.caps.roster == 2
    assert screen(tight) == ("alpha\tone job\tready",)
    assert len(tight.bots) == 2
    with pytest.raises(Refuse) as full:
        register(tight, "gamma", "third job")
    assert full.value.code == "BOT_CAP"
    pane = make_roster(requested_screen=1)
    pane = register(pane, "researcher", "reads the note")
    pane = register(pane, "scribe", "files the card")
    assert screen(pane) == ("researcher\treads the note\tready",)
    assert screen(pane, 50) == ("researcher\treads the note\tready",)


def test_unknown_mention_and_missing_mention() -> None:
    state = _ready(("researcher", "reads sources"))
    with pytest.raises(Refuse) as unknown:
        route(state, _say("ask @scribe instead"))
    assert unknown.value.code == "NO_BOT"
    with pytest.raises(Refuse) as bare:
        route(state, _say("nobody was named"))
    assert bare.value.code == "NO_MENTION"
    with pytest.raises(Refuse) as mail:
        route(state, _say("mail ada@lab.example about the note"))
    assert mail.value.code == "NO_MENTION"
    mixed = route(state, _say("mail ada@lab.example and ping @researcher."))
    assert mixed.bot_ids == ("researcher",)
    folded = route(state, _say("ping @Researcher, please"))
    assert folded.bot_ids == ("researcher",)
    with pytest.raises(Refuse) as partial:
        route(state, _say("@researcher then @scribe"), fanout=True)
    assert partial.value.code == "NO_BOT"
    with pytest.raises(Refuse) as truncated:
        route(state, _say("ping @researcher_extra"))
    assert truncated.value.code == "NO_MENTION"


def test_fanout_stops_at_three() -> None:
    state = make_roster(requested_fanout=9)
    for name, role in (
        ("researcher", "reads the note"),
        ("scribe", "files the card"),
        ("keeper", "watches the light"),
        ("porter", "carries the card"),
    ):
        state = register(state, name, role)
    assert state.caps.fanout == 3
    sent = route(
        state,
        _say("@keeper @researcher @keeper @scribe"),
        fanout=True,
    )
    assert sent.bot_ids == ("keeper", "researcher", "scribe")
    assert sent.rounds == (1, 2, 3)
    assert sent.fanout is True
    assert sent.kind == "reply"
    assert sent.enables_terminal is False
    with pytest.raises(Refuse) as over:
        route(
            state,
            _say("@researcher @scribe @keeper @porter"),
            fanout=True,
        )
    assert over.value.code == "FANOUT_CAP"
    with pytest.raises(Refuse) as single:
        route(state, _say("@researcher @scribe"))
    assert single.value.code == "NEED_FANOUT"
    narrow = make_roster(requested_fanout=1)
    narrow = register(narrow, "alpha", "one work")
    narrow = register(narrow, "beta", "two work")
    with pytest.raises(Refuse) as capped:
        route(narrow, _say("@alpha @beta"), fanout=True)
    assert capped.value.code == "FANOUT_CAP"


def test_approve_and_terminal_refuse() -> None:
    state = _ready(("researcher", "reads sources"))
    plan = route(state, _say("@researcher"))
    assert plan.bot_ids == ("researcher",)
    assert plan.approves_tool is False
    assert plan.enables_terminal is False
    with pytest.raises(Refuse) as bare:
        approve()
    assert bare.value.code == "BOT_APPROVAL"
    with pytest.raises(Refuse) as named:
        approve("kiln-token", action="grant")
    assert named.value.code == "BOT_APPROVAL"
    assert "kiln-token" not in str(named.value)
    with pytest.raises(Refuse) as shell:
        route(state, _say("@researcher please approve the shell command"))
    assert shell.value.code == "BOT_APPROVAL"
    assert "shell" not in str(shell.value)
    with pytest.raises(Refuse) as tool:
        route(state, _say("pre-approve the tool before @researcher speaks"))
    assert tool.value.code == "BOT_APPROVAL"
    with pytest.raises(Refuse) as yolo:
        route(state, _say("@researcher yolo"))
    assert yolo.value.code == "BOT_APPROVAL"
    with pytest.raises(Refuse) as slash:
        route(state, _say("/approve @researcher"))
    assert slash.value.code == "BOT_APPROVAL"
    with pytest.raises(Refuse) as terminal:
        route(state, _say("@researcher enable the terminal"))
    assert terminal.value.code == "NO_TERMINAL"
    with pytest.raises(Refuse) as runs:
        route(state, _say("@researcher runs the shell"))
    assert runs.value.code == "NO_TERMINAL"
    with pytest.raises(Refuse) as slash_terminal:
        route(state, _say("/terminal @researcher"))
    assert slash_terminal.value.code == "NO_TERMINAL"
    with pytest.raises(Refuse) as opened:
        enable_terminal("west-pier")
    assert opened.value.code == "NO_TERMINAL"
    assert "west-pier" not in str(opened.value)
    prose = route(state, _say("@researcher approve the note and start the lamp"))
    assert prose.kind == "reply"
    assert prose.enables_terminal is False
    listed = route(state, _say("@researcher file the tool note"))
    assert listed.bot_ids == ("researcher",)


def test_held_duplicate_self_and_bad_fields() -> None:
    state = register(make_roster(), "researcher", "reads sources", status="held")
    assert screen(state) == ("researcher\treads sources\theld",)
    assert rebuild(snapshot(state)) == state
    with pytest.raises(Refuse) as held:
        route(state, _say("@researcher"))
    assert held.value.code == "HELD"
    with pytest.raises(Refuse) as duplicate:
        register(state, "researcher", "other work")
    assert duplicate.value.code == "DUPLICATE"
    ready = _ready(("researcher", "reads sources"), ("scribe", "files the card"))
    with pytest.raises(Refuse) as echo:
        route(ready, _say("@researcher look", sender="researcher"))
    assert echo.value.code == "SELF"
    handoff = route(ready, _say("@researcher look", sender="scribe"), fanout=False)
    assert handoff.bot_ids == ("researcher",)
    with pytest.raises(Refuse) as bad_id:
        register(make_roster(), "Researcher", "reads sources")
    assert bad_id.value.code == "BAD_ID"
    with pytest.raises(Refuse) as bad_role:
        register(make_roster(), "researcher", "  reads")
    assert bad_role.value.code == "BAD_SPECIALTY"
    with pytest.raises(Refuse) as bad_line:
        register(make_roster(), "researcher", "reads\nsources")
    assert bad_line.value.code == "BAD_SPECIALTY"
    with pytest.raises(Refuse) as bad_grant:
        register(make_roster(), "researcher", "run the shell")
    assert bad_grant.value.code == "BAD_SPECIALTY"
    with pytest.raises(Refuse) as bad_status:
        register(make_roster(), "researcher", "reads sources", status="off")
    assert bad_status.value.code == "BAD_STATUS"
    with pytest.raises(Refuse) as room:
        room_message("Lab Room", "ada", "@researcher")
    assert room.value.code == "BAD_ROOM"
    with pytest.raises(Refuse) as sender:
        room_message("lab-session", "Ada", "@researcher")
    assert sender.value.code == "BAD_SENDER"


def test_secret_is_not_stored() -> None:
    state = make_roster()
    with pytest.raises(Refuse) as role:
        register(state, "researcher", "token=supersecretvalue")
    assert role.value.code == "SECRET"
    assert state.bots == ()
    assert "supersecretvalue" not in str(role.value)
    kept = register(state, "researcher", "reads sources")
    with pytest.raises(Refuse) as body:
        route(kept, _say("use sk-abcdefghij now @researcher"))
    assert body.value.code == "SECRET"
    with pytest.raises(Refuse) as bearer:
        route(kept, _say("Bearer abcdefghijkl @researcher"))
    assert bearer.value.code == "SECRET"
    with pytest.raises(Refuse) as room:
        room_message("sk-abcdefghij", "ada", "@researcher hi")
    assert room.value.code == "SECRET"
    assert "abcdefghij" not in str(room.value)
    assert not secret_shape(repr(kept))


def test_bounds_and_types() -> None:
    state = _ready(("researcher", "reads sources"))
    with pytest.raises(Refuse) as bad_roster:
        route("researcher", _say("@researcher"))
    assert bad_roster.value.code == "BAD_ROSTER"
    with pytest.raises(Refuse) as raw:
        route(state, "@researcher")
    assert raw.value.code == "BAD_MESSAGE"
    with pytest.raises(Refuse) as flag:
        route(state, _say("@researcher"), fanout=1)
    assert flag.value.code == "BAD_FLAG"
    with pytest.raises(Refuse) as off:
        route(state, _say("@researcher"), mode="off")
    assert off.value.code == "BAD_MODE"
    with pytest.raises(Refuse) as yolo:
        route(state, _say("@researcher"), mode="yolo")
    assert yolo.value.code == "BAD_MODE"
    with pytest.raises(Refuse) as not_text:
        room_message(5, "ada", "hi")
    assert not_text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        route(state, _say("hi\x00 @researcher"))
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as surrogate:
        route(state, _say("@researcher \ud800"))
    assert surrogate.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as over:
        route(state, _say("a" * 4_001))
    assert over.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as not_int:
        make_roster(True)
    assert not_int.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low:
        make_roster(0)
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as window:
        screen(state, 0)
    assert window.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as forged:
        Caps(100, 3, 20, 100, 3, 20)
    assert forged.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as flagged:
        Caps(True, 1, 1, 1, 1, 1)
    assert flagged.value.code == "BAD_LIMIT"


def test_reply_plan_cannot_grant() -> None:
    with pytest.raises(Refuse) as terminal:
        ReplyPlan(
            room="lab-session",
            sender="ada",
            bot_ids=("researcher",),
            specialties=("reads sources",),
            rounds=(1,),
            kind="reply",
            fanout=False,
            enables_terminal=True,
            approves_tool=False,
        )
    assert terminal.value.code == "NO_TERMINAL"
    with pytest.raises(Refuse) as grant:
        ReplyPlan(
            room="lab-session",
            sender="ada",
            bot_ids=("researcher",),
            specialties=("reads sources",),
            rounds=(1,),
            kind="reply",
            fanout=False,
            enables_terminal=False,
            approves_tool=True,
        )
    assert grant.value.code == "BOT_APPROVAL"
    with pytest.raises(Refuse) as kind:
        ReplyPlan(
            room="lab-session",
            sender="ada",
            bot_ids=("researcher",),
            specialties=("reads sources",),
            rounds=(1,),
            kind="grant",
            fanout=False,
            enables_terminal=False,
            approves_tool=False,
        )
    assert kind.value.code == "BAD_KIND"
    with pytest.raises(Refuse) as shape:
        ReplyPlan(
            room="lab-session",
            sender="ada",
            bot_ids=("researcher",),
            specialties=("reads sources",),
            rounds=(2,),
            kind="reply",
            fanout=False,
            enables_terminal=False,
            approves_tool=False,
        )
    assert shape.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as wide:
        ReplyPlan(
            room="lab-session",
            sender="ada",
            bot_ids=("alpha", "beta", "gamma", "delta"),
            specialties=("one", "two", "three", "four"),
            rounds=(1, 2, 3, 4),
            kind="reply",
            fanout=True,
            enables_terminal=False,
            approves_tool=False,
        )
    assert wide.value.code == "FANOUT_CAP"


def test_snapshot_chain() -> None:
    state = _ready(("researcher", "reads the note"), ("scribe", "files the card"))
    image = snapshot(state)
    assert rebuild(image) == state
    assert snapshot(rebuild(image)) == image
    link = _record(image.records, 0)
    with pytest.raises(Refuse) as broken:
        Record(link.seq, link.bot_id, link.specialty, link.status, link.prev, "ab" * 32)
    assert broken.value.code == "BROKEN"
    with pytest.raises(Refuse) as stale:
        Snapshot(
            image.requested_roster,
            image.requested_fanout,
            image.requested_screen,
            image.records,
            "ab" * 32,
        )
    assert stale.value.code == "STALE"
    second = _record(image.records, 1)
    with pytest.raises(Refuse) as gap:
        Snapshot(20, 3, 20, (second,), second.digest)
    assert gap.value.code == "STALE"
    with pytest.raises(Refuse) as empty_tip:
        Snapshot(20, 3, 20, (), "ab" * 32)
    assert empty_tip.value.code == "STALE"
    with pytest.raises(Refuse) as bad_prev:
        Record(1, "researcher", "reads the note", "ready", "zz", "ab" * 32)
    assert bad_prev.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as bad_image:
        rebuild(None)
    assert bad_image.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as over_cap:
        Snapshot(1, 3, 20, image.records, image.tip)
    assert over_cap.value.code == "BOT_CAP"
    first_bot = _bot(state)
    with pytest.raises(Refuse) as dup:
        Roster(make_roster().caps, (first_bot, first_bot))
    assert dup.value.code == "DUPLICATE"


def test_registration_order_and_no_dial_out() -> None:
    state = register(make_roster(), "zeta", "last specialty")
    state = register(state, "alpha", "first specialty")
    assert screen(state) == (
        "zeta\tlast specialty\tready",
        "alpha\tfirst specialty\tready",
    )
    source = inspect.getsource(route) + inspect.getsource(approve) + inspect.getsource(enable_terminal)
    for banned in ("socket", "urllib", "requests", "subprocess", "pickle"):
        assert banned not in source
    assert "cosmos_profiles" not in inspect.getsource(make_roster)
