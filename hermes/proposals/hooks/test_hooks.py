"""Registry behavior for the four hook points."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import hooks
from cosmos_hermes import PathJail, Refuse, secret_shape
from hooks import (
    ALLOW_CAP,
    COMMAND_WILDCARD,
    GATEWAY_EVENTS,
    NOTE_CAP,
    PLAN_TOOLS,
    POINTS,
    POLICY_CAP,
    SCHEMA,
    TEXT_CAP,
    TRANSCRIPT_CAP,
    Action,
    Line,
    Outcome,
    Registry,
    load_from_path,
    rebuild,
)


def _ok(_action: Action) -> None:
    return None


def test_schema_and_points() -> None:
    assert SCHEMA == "cosmos-hermes-hooks/1"
    assert hooks.SCHEMA == SCHEMA
    assert POINTS == ("pre_tool", "post_tool", "stop", "gateway")
    assert POLICY_CAP == 16
    assert PLAN_TOOLS == ("read", "glob", "grep", "oracle")
    reg = Registry()
    assert reg.cap == 16
    assert reg.asked_cap == 16
    assert reg.policy_cap == 16


def test_success_runs_in_registration_order() -> None:
    reg = Registry(cap=100)
    seen: list[str] = []

    def first(action: Action) -> Outcome:
        seen.append(action.tool)
        return Outcome(note="one", tool_names=("read",))

    def middle(_action: Action) -> None:
        seen.append("stop")

    def last(action: Action) -> dict[str, object]:
        seen.append("last")
        return {"note": "two", "tool_names": ["grep", "read"]}

    reg.register("first", "pre_tool", first)
    reg.register("middle", "stop", middle)
    reg.register("last", "pre_tool", last)
    verdict = reg.fire(
        "pre_tool",
        kind="observe",
        mode="act",
        tool="read",
        allowed=("read", "read", "grep"),
        text="look",
        stamp=4,
    )
    assert seen == ["read", "last"]
    assert verdict.code == "ADMIT"
    assert verdict.schema == SCHEMA
    assert verdict.ran == ("first", "last")
    assert verdict.notes == ("one", "two")
    assert verdict.tools == ("read", "grep")
    assert verdict.cap == 16
    assert verdict.asked_cap == 100
    assert verdict.policy_cap == 16
    assert verdict.stamp == 4
    again = reg.fire(
        "pre_tool",
        kind="observe",
        mode="act",
        tool="read",
        allowed=("read", "grep"),
        text="look",
        stamp=4,
    )
    assert again == verdict
    assert tuple(line.name for line in verdict.lines) == verdict.ran
    assert tuple(line.point for line in verdict.lines) == ("pre_tool", "pre_tool")
    stopped = reg.fire("stop", kind="halt", mode="plan", allowed=("edit", "read"), stamp=4)
    assert stopped.ran == ("middle",)
    assert stopped.code == "ADMIT"
    assert tuple(line.name for line in stopped.lines) == stopped.ran


def test_each_point_admits() -> None:
    reg = Registry(credential_id="vault.primary")
    pre = reg.fire(
        "pre_tool",
        kind="mutate",
        mode="act",
        tool="edit",
        allowed=("edit",),
        stamp=1,
    )
    post = reg.fire(
        "post_tool",
        kind="observe",
        mode="act",
        tool="edit",
        allowed=("edit",),
        stamp=1,
    )
    stopped = reg.fire("stop", kind="halt", mode="act", stamp=1)
    started = reg.fire(
        "gateway",
        kind="dispatch",
        mode="act",
        event="gateway:startup",
        credential_id="vault.primary",
        stamp=1,
    )
    assert (pre.code, post.code, stopped.code, started.code) == ("ADMIT",) * 4
    assert "vault.primary" not in repr(reg)


def test_gateway_events_and_command_wildcard() -> None:
    reg = Registry(credential_id="vault.primary")
    seen: list[str] = []

    def grab(action: Action) -> None:
        seen.append(action.event)

    reg.register("all", "gateway", grab, events=GATEWAY_EVENTS)
    reg.register("cmds", "gateway", grab, events=(COMMAND_WILDCARD, "command:reset"))
    for event in GATEWAY_EVENTS:
        reg.fire(
            "gateway",
            kind="dispatch",
            mode="act",
            event=event,
            credential_id="vault.primary",
            stamp=2,
        )
    reg.fire(
        "gateway",
        kind="dispatch",
        mode="act",
        event="command:reset",
        credential_id="vault.primary",
        stamp=2,
    )
    assert seen == [*GATEWAY_EVENTS, "command:reset"]
    reg.fire(
        "gateway",
        kind="dispatch",
        mode="act",
        event="agent:end",
        credential_id="vault.primary",
        stamp=2,
    )
    assert seen[-1] == "agent:end"


def test_cap_policy_and_duplicate() -> None:
    wide = Registry(cap=100)
    assert wide.cap == 16
    assert wide.asked_cap == 100
    for index in range(16):
        wide.register(f"h{index:02d}", "stop", _ok)
    with pytest.raises(Refuse) as over:
        wide.register("h16", "stop", _ok)
    assert over.value.code == "HOOK_CAP"
    verdict = wide.fire("stop", kind="halt", mode="act", stamp=7)
    assert verdict.ran == tuple(f"h{index:02d}" for index in range(16))
    assert verdict.cap == 16
    tight = Registry(cap=2)
    assert tight.cap == 2
    assert tight.policy_cap == 16
    tight.register("a", "stop", _ok)
    tight.register("b", "stop", _ok)
    with pytest.raises(Refuse) as third:
        tight.register("c", "stop", _ok)
    assert third.value.code == "HOOK_CAP"
    with pytest.raises(Refuse) as dup:
        tight.register("a", "stop", _ok)
    assert dup.value.code == "DUPLICATE"


def test_bad_cap() -> None:
    for raw in (0, -1, True, False, "16", 1_000_001):
        with pytest.raises(Refuse) as caught:
            Registry(cap=raw)
        assert caught.value.code == "BAD_CAP"


def test_register_refusals() -> None:
    reg = Registry()
    with pytest.raises(Refuse) as name:
        reg.register("Bad", "pre_tool", _ok)
    assert name.value.code == "BAD_NAME"
    with pytest.raises(Refuse) as point:
        reg.register("ok", "pre_llm", _ok)
    assert point.value.code == "UNKNOWN_POINT"
    with pytest.raises(Refuse) as events:
        reg.register("ok", "pre_tool", _ok, events=("agent:start",))
    assert events.value.code == "BAD_EVENTS"
    with pytest.raises(Refuse) as text_events:
        reg.register("ok", "gateway", _ok, events="agent:start")
    assert text_events.value.code == "BAD_EVENTS"
    with pytest.raises(Refuse) as empty:
        reg.register("ok", "gateway", _ok, events=())
    assert empty.value.code == "EMPTY_EVENTS"
    with pytest.raises(Refuse) as unknown:
        reg.register("ok", "gateway", _ok, events=("nope",))
    assert unknown.value.code == "UNKNOWN_EVENT"
    with pytest.raises(Refuse) as dead:
        reg.register("ok", "pre_tool", None)
    assert dead.value.code == "NOT_CALLABLE"
    with pytest.raises(Refuse) as body:
        reg.register("run", "stop", "print('no')")
    assert body.value.code == "NOT_CALLABLE"
    assert reg.hooks == ()


def test_refuse_return_and_raise_latch() -> None:
    returned: list[str] = []
    raised: list[str] = []

    def blocks(_action: Action) -> Refuse:
        returned.append("block")
        return Refuse("BLOCKED", "stop")

    def after_return(_action: Action) -> None:
        returned.append("after")

    def denies(_action: Action) -> None:
        raised.append("deny")
        raise Refuse("DENIED", "stop")

    def after_raise(_action: Action) -> None:
        raised.append("after")

    reg = Registry()
    reg.register("blocks", "stop", blocks)
    reg.register("after", "stop", after_return)
    with pytest.raises(Refuse) as first:
        reg.fire("stop", kind="halt", mode="act", stamp=1)
    assert first.value.code == "BLOCKED"
    assert returned == ["block"]
    assert reg.transcript() == ()
    other = Registry()
    other.register("denies", "stop", denies)
    other.register("after", "stop", after_raise)
    with pytest.raises(Refuse) as second:
        other.fire("stop", kind="halt", mode="act", stamp=1)
    assert second.value.code == "DENIED"
    assert raised == ["deny"]


def test_hook_fail_and_bad_result() -> None:
    seen: list[str] = []

    def boom(_action: Action) -> None:
        seen.append("boom")
        raise RuntimeError("sk-livekeyvalue")

    def later(_action: Action) -> None:
        seen.append("later")

    reg = Registry()
    reg.register("boom", "stop", boom)
    reg.register("later", "stop", later)
    with pytest.raises(Refuse) as failed:
        reg.fire("stop", kind="halt", mode="act", stamp=1)
    assert failed.value.code == "HOOK_FAIL"
    assert seen == ["boom"]
    assert "sk-" not in repr(failed.value)
    assert not secret_shape(repr(failed.value))

    def bad(_action: Action) -> bool:
        return False

    other = Registry()
    other.register("bad", "stop", bad)
    with pytest.raises(Refuse) as shape:
        other.fire("stop", kind="halt", mode="act", stamp=1)
    assert shape.value.code == "BAD_RESULT"


def test_guard_escape() -> None:
    seen: list[str] = []

    def extra(_action: Action) -> Outcome:
        seen.append("extra")
        return Outcome(tool_names=("read", "terminal"))

    def later(_action: Action) -> None:
        seen.append("later")

    reg = Registry()
    reg.register("extra", "pre_tool", extra)
    reg.register("later", "pre_tool", later)
    with pytest.raises(Refuse) as caught:
        reg.fire(
            "pre_tool",
            kind="observe",
            mode="act",
            tool="read",
            allowed=("read",),
            stamp=1,
        )
    assert caught.value.code == "GUARD_ESCAPE"
    assert caught.value.detail == "terminal"
    assert seen == ["extra"]
    marked = Registry()

    def note(_action: Action) -> Outcome:
        return Outcome(note="also tool:terminal")

    marked.register("note", "stop", note)
    with pytest.raises(Refuse) as marker:
        marked.fire("stop", kind="halt", mode="act", stamp=1)
    assert marker.value.code == "GUARD_ESCAPE"
    keyed = Registry()

    def stray(_action: Action) -> dict[str, object]:
        return {"terminal": True}

    keyed.register("stray", "gateway", stray, events=("gateway:startup",))
    with pytest.raises(Refuse) as keys:
        keyed.fire(
            "gateway",
            kind="dispatch",
            mode="act",
            event="gateway:startup",
            credential_id="vault.primary",
            stamp=1,
        )
    assert keys.value.code == "MISSING_CRED"
    held = Registry(credential_id="vault.primary")
    held.register("stray", "gateway", stray, events=("gateway:startup",))
    with pytest.raises(Refuse) as escaped:
        held.fire(
            "gateway",
            kind="dispatch",
            mode="act",
            event="gateway:startup",
            credential_id="vault.primary",
            stamp=1,
        )
    assert escaped.value.code == "GUARD_ESCAPE"


def test_confirm_retry_is_once() -> None:
    calls: list[tuple[str, bool]] = []

    def first(action: Action) -> Refuse | None:
        calls.append(("first", action.confirm))
        if not action.confirm:
            return Refuse("CONFIRM", "once")
        return None

    def second(action: Action) -> None:
        calls.append(("second", action.confirm))

    reg = Registry()
    reg.register("first", "stop", first)
    reg.register("second", "stop", second)
    verdict = reg.fire("stop", kind="halt", mode="act", stamp=3)
    assert calls == [("first", False), ("first", True), ("second", False)]
    assert verdict.ran == ("first", "second")
    assert tuple(line.name for line in verdict.lines) == ("first", "second")
    assert reg.transcript() == verdict.lines
    raised: list[bool] = []

    def always(action: Action) -> None:
        raised.append(action.confirm)
        raise Refuse("CONFIRM", "no")

    def skipped(_action: Action) -> None:
        raised.append(True)

    latch = Registry()
    latch.register("always", "stop", always)
    latch.register("skipped", "stop", skipped)
    with pytest.raises(Refuse) as caught:
        latch.fire("stop", kind="halt", mode="act", stamp=3)
    assert caught.value.code == "CONFIRM"
    assert raised == [False, True]
    already: list[bool] = []

    def once(action: Action) -> Refuse:
        already.append(action.confirm)
        return Refuse("CONFIRM")

    direct = Registry()
    direct.register("once", "stop", once)
    with pytest.raises(Refuse) as held:
        direct.fire("stop", kind="halt", mode="act", stamp=3, confirm=True)
    assert held.value.code == "CONFIRM"
    assert already == [True]
    flaky_calls: list[bool] = []

    def flaky(action: Action) -> Refuse | None:
        flaky_calls.append(action.confirm)
        if not action.confirm:
            return Refuse("CONFIRM")
        raise RuntimeError("boom")

    broke = Registry()
    broke.register("flaky", "stop", flaky)
    with pytest.raises(Refuse) as failed:
        broke.fire("stop", kind="halt", mode="act", stamp=3)
    assert failed.value.code == "HOOK_FAIL"
    assert flaky_calls == [False, True]


def test_action_validation() -> None:
    reg = Registry()
    reg.register("spy", "pre_tool", _ok)
    with pytest.raises(Refuse) as mode:
        reg.fire("pre_tool", kind="observe", mode="yolo", tool="read", allowed=("read",), stamp=1)
    assert mode.value.code == "UNKNOWN_MODE"
    with pytest.raises(Refuse) as off:
        reg.fire("stop", kind="halt", mode="off", stamp=1)
    assert off.value.code == "UNKNOWN_MODE"
    with pytest.raises(Refuse) as kind:
        reg.fire("pre_tool", kind="halt", mode="act", tool="read", allowed=("read",), stamp=1)
    assert kind.value.code == "UNCLASSIFIED"
    with pytest.raises(Refuse) as tool:
        reg.fire("stop", kind="halt", mode="act", tool="read", stamp=1)
    assert tool.value.code == "UNCLASSIFIED"
    with pytest.raises(Refuse) as empty:
        reg.fire("pre_tool", kind="observe", mode="act", tool="read", allowed=(), stamp=1)
    assert empty.value.code == "EMPTY_ALLOW"
    with pytest.raises(Refuse) as missing:
        reg.fire("post_tool", kind="observe", mode="act", tool="", allowed=("read",), stamp=1)
    assert missing.value.code == "MISSING_TOOL"
    with pytest.raises(Refuse) as shape:
        reg.fire("pre_tool", kind="observe", mode="act", tool="Edit", allowed=("Edit",), stamp=1)
    assert shape.value.code == "BAD_TOOL"
    with pytest.raises(Refuse) as granted:
        reg.fire("pre_tool", kind="observe", mode="act", tool="grep", allowed=("read",), stamp=1)
    assert granted.value.code == "NOT_ALLOWED"
    with pytest.raises(Refuse) as allow:
        reg.fire("pre_tool", kind="observe", mode="act", tool="read", allowed="read", stamp=1)
    assert allow.value.code == "BAD_ALLOW"
    with pytest.raises(Refuse) as flag:
        reg.fire("stop", kind="halt", mode="act", stamp=1, confirm=1)
    assert flag.value.code == "BAD_CONFIRM"
    with pytest.raises(Refuse) as point:
        reg.fire("pre_llm", kind="observe", mode="act", stamp=1)
    assert point.value.code == "UNKNOWN_POINT"
    with pytest.raises(Refuse) as event:
        reg.fire(
            "pre_tool",
            kind="observe",
            mode="act",
            tool="read",
            allowed=("read",),
            event="agent:start",
            stamp=1,
        )
    assert event.value.code == "BAD_EVENTS"
    with pytest.raises(Refuse) as unknown:
        reg.fire(
            "gateway",
            kind="dispatch",
            mode="act",
            event="command:*",
            credential_id="vault.primary",
            stamp=1,
        )
    assert unknown.value.code == "UNKNOWN_EVENT"
    too_many = tuple(f"t{index:02d}" for index in range(ALLOW_CAP + 1))
    with pytest.raises(Refuse) as cap:
        reg.fire("stop", kind="halt", mode="act", allowed=too_many, stamp=1)
    assert cap.value.code == "BAD_ALLOW"


def test_plan_mode() -> None:
    reg = Registry()
    with pytest.raises(Refuse) as mixed:
        reg.fire(
            "pre_tool",
            kind="observe",
            mode="plan",
            tool="read",
            allowed=("read", "edit"),
            stamp=1,
        )
    assert mixed.value.code == "PLAN_MODE"
    ok = reg.fire(
        "pre_tool",
        kind="observe",
        mode="plan",
        tool="oracle",
        allowed=("oracle", "grep"),
        stamp=1,
    )
    assert ok.code == "ADMIT"
    with pytest.raises(Refuse) as write:
        reg.fire(
            "post_tool",
            kind="observe",
            mode="plan",
            tool="write",
            allowed=("write",),
            stamp=1,
        )
    assert write.value.code == "PLAN_MODE"


def test_credentials() -> None:
    with pytest.raises(Refuse) as bad:
        Registry(credential_id="1234")
    assert bad.value.code == "BAD_CRED"
    bare = Registry()
    with pytest.raises(Refuse) as missing:
        bare.fire("gateway", kind="dispatch", mode="act", event="session:start", stamp=1)
    assert missing.value.code == "MISSING_CRED"
    half = Registry()
    with pytest.raises(Refuse) as only_action:
        half.fire(
            "gateway",
            kind="dispatch",
            mode="act",
            event="session:start",
            credential_id="vault.primary",
            stamp=1,
        )
    assert only_action.value.code == "MISSING_CRED"
    reg = Registry(credential_id="vault.primary")
    with pytest.raises(Refuse) as mismatch:
        reg.fire(
            "gateway",
            kind="dispatch",
            mode="act",
            event="session:start",
            credential_id="vault.other",
            stamp=1,
        )
    assert mismatch.value.code == "CRED_MISMATCH"
    assert str(mismatch.value) == "CRED_MISMATCH"
    with pytest.raises(Refuse) as tool_mismatch:
        reg.fire(
            "stop",
            kind="halt",
            mode="act",
            credential_id="vault.other",
            stamp=1,
        )
    assert tool_mismatch.value.code == "CRED_MISMATCH"
    admitted = reg.fire("stop", kind="halt", mode="act", stamp=1)
    assert admitted.code == "ADMIT"


def test_secrets_stay_out_of_repr() -> None:
    samples = ("sk-livekeyvalue", "Bearer abcdefghijk", "api_key=supersecret")
    reg = Registry()
    for sample in samples:
        with pytest.raises(Refuse) as caught:
            reg.fire("stop", kind="halt", mode="act", text=sample, stamp=1)
        assert caught.value.code == "SECRET"
        assert sample not in repr(caught.value)
        assert not secret_shape(repr(caught.value))
    with pytest.raises(Refuse) as named:
        reg.register("sk-livekeyvalue", "stop", _ok)
    assert named.value.code == "SECRET"
    assert not secret_shape(repr(named.value))

    def leak(_action: Action) -> Outcome:
        return Outcome(note="token=supersecret")

    reg.register("leak", "stop", leak)
    with pytest.raises(Refuse) as note:
        reg.fire("stop", kind="halt", mode="act", stamp=1)
    assert note.value.code == "SECRET"
    assert "supersecret" not in repr(note.value)

    def blocked(_action: Action) -> Refuse:
        return Refuse("BLOCKED", "sk-livekeyvalue")

    other = Registry()
    other.register("blocked", "stop", blocked)
    with pytest.raises(Refuse) as detail:
        other.fire("stop", kind="halt", mode="act", stamp=1)
    assert detail.value.code == "BLOCKED"
    assert not secret_shape(repr(detail.value))
    held: list[Action] = []

    def grab(action: Action) -> Outcome:
        held.append(action)
        return Outcome(note="kept", tool_names=("read",))

    clean = Registry(credential_id="vault.primary")
    clean.register("grab", "pre_tool", grab)
    verdict = clean.fire(
        "pre_tool",
        kind="observe",
        mode="act",
        tool="read",
        allowed=("read",),
        text="hello",
        stamp=1,
    )
    blob = " ".join(
        (
            repr(clean),
            repr(verdict),
            repr(clean.hooks[0]),
            repr(held[0]),
            repr(Outcome("kept", ("read",))),
        )
    )
    assert not secret_shape(blob)
    assert held[0].schema == SCHEMA


def test_bounds() -> None:
    reg = Registry()
    with pytest.raises(Refuse) as nul:
        reg.fire("stop", kind="halt", mode="act", text="a\x00b", stamp=1)
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as big:
        reg.fire("stop", kind="halt", mode="act", text="x" * (TEXT_CAP + 1), stamp=1)
    assert big.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as kind:
        reg.fire("stop", kind=1, mode="act", stamp=1)
    assert kind.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as flag:
        reg.fire("stop", kind="halt", mode="act", stamp=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low:
        reg.fire("stop", kind="halt", mode="act", stamp=-1)
    assert low.value.code == "OUT_OF_RANGE"

    def wide(_action: Action) -> Outcome:
        return Outcome(note="n" * (NOTE_CAP + 1))

    reg.register("wide", "stop", wide)
    with pytest.raises(Refuse) as note:
        reg.fire("stop", kind="halt", mode="act", stamp=1)
    assert note.value.code == "OVERSIZE"


def test_reenter_clears() -> None:
    reg = Registry()

    def nest(action: Action) -> None:
        reg.fire("stop", kind="halt", mode="act", stamp=action.stamp)

    reg.register("nest", "stop", nest)
    with pytest.raises(Refuse) as caught:
        reg.fire("stop", kind="halt", mode="act", stamp=1)
    assert caught.value.code == "REENTER"
    reg.register("after", "pre_tool", _ok)
    verdict = reg.fire(
        "pre_tool",
        kind="observe",
        mode="act",
        tool="read",
        allowed=("read",),
        stamp=1,
    )
    assert verdict.ran == ("after",)


def test_path_jail() -> None:
    grant = Path(__file__).resolve().parent / "attempt-grant"
    inside = grant / "note.txt"
    seen: list[str] = []

    def spy(action: Action) -> None:
        seen.append(action.path)

    reg = Registry()
    reg.register("spy", "stop", spy)
    verdict = reg.fire(
        "stop",
        kind="halt",
        mode="act",
        path=str(inside),
        jail=PathJail([str(grant)]),
        stamp=1,
    )
    assert verdict.path == str(inside.resolve())
    assert seen == [str(inside.resolve())]
    cases = (
        ("NO_GRANT", str(inside), None),
        ("OUTSIDE_GRANT", str(grant.parent / "other.txt"), PathJail([str(grant)])),
        ("RELATIVE_PATH", "note.txt", PathJail([str(grant)])),
        ("DOTDOT", str(grant) + "\\..\\x", PathJail([str(grant)])),
        ("FILE_URL", "file:///etc/passwd", PathJail([str(grant)])),
    )
    for code, raw, jail in cases:
        with pytest.raises(Refuse) as caught:
            reg.fire("stop", kind="halt", mode="act", path=raw, jail=jail, stamp=1)
        assert caught.value.code == code
    assert seen == [str(inside.resolve())]


def _at(lines: tuple[Line, ...], index: int) -> Line:
    return lines[index]


def _porch_session() -> tuple[Line, ...]:
    """A card and a porch read one note, then the light, then the session."""
    reg = Registry(credential_id="vault.porch")

    def porch(action: Action) -> Outcome:
        return Outcome(note="porch card on the note", tool_names=(action.tool,))

    def card(action: Action) -> Outcome:
        return Outcome(note="card left on the note", tool_names=(action.tool,))

    def light(action: Action) -> Outcome:
        return Outcome(note="porch light on", tool_names=(action.tool,))

    def session(_action: Action) -> None:
        return None

    reg.register("light", "post_tool", light)
    reg.register("porch", "pre_tool", porch)
    reg.register("card", "pre_tool", card)
    reg.register("session", "gateway", session, events=("session:start",))
    pre = reg.fire(
        "pre_tool",
        kind="observe",
        mode="act",
        tool="note",
        allowed=("note",),
        text="evening note",
        stamp=12,
    )
    post = reg.fire(
        "post_tool",
        kind="observe",
        mode="act",
        tool="note",
        allowed=("note",),
        text="evening note",
        stamp=12,
    )
    gate = reg.fire(
        "gateway",
        kind="dispatch",
        mode="act",
        event="session:start",
        credential_id="vault.porch",
        stamp=12,
    )
    lines = pre.lines + post.lines + gate.lines
    assert lines == reg.transcript()
    return lines


def test_example_hooks() -> None:
    first = _porch_session()
    second = _porch_session()
    assert first == second
    assert rebuild(first) == first
    assert tuple(line.name for line in first) == ("porch", "card", "light", "session")
    assert tuple(line.point for line in first) == ("pre_tool", "pre_tool", "post_tool", "gateway")
    assert tuple(line.tool for line in first) == ("note", "note", "note", "")
    porch = _at(first, 0)
    light = _at(first, 2)
    session = _at(first, 3)
    assert porch.tool == light.tool == "note"
    assert porch.point == "pre_tool"
    assert light.point == "post_tool"
    assert porch != light
    assert session.event == "session:start"
    assert session.note == ""
    assert len(set(first)) == len(first)
    reg = Registry()
    with pytest.raises(Refuse) as missing:
        reg.get("porch")
    assert missing.value.code == "UNKNOWN_HOOK"
    with pytest.raises(Refuse) as unknown:
        reg.register("porch", "on_llm", _ok)
    assert unknown.value.code == "UNKNOWN_POINT"
    with pytest.raises(Refuse) as imported:
        load_from_path(None)
    assert imported.value.code == "IMPORT"
    with pytest.raises(Refuse) as disk:
        Registry().load_from_path("proposals/plugins/plugins.py")
    assert disk.value.code == "IMPORT"
    with pytest.raises(Refuse) as secret:
        load_from_path("sk-livekeyvalue")
    assert secret.value.code == "SECRET"
    assert not secret_shape(repr(secret.value))
    with pytest.raises(Refuse) as doubled:
        rebuild((porch, porch))
    assert doubled.value.code == "DUPLICATE"


def test_rebuild_transcript() -> None:
    later = Line("stop", "card", "", "porch note", "", 5)
    earlier = Line("stop", "light", "", "porch light", "", 4)
    assert rebuild((later,)) == (later,)
    with pytest.raises(Refuse) as stale:
        rebuild((later, earlier))
    assert stale.value.code == "STALE"
    with pytest.raises(Refuse) as unknown:
        rebuild((Line("pre_llm", "card", "", "", "", 1),))
    assert unknown.value.code == "UNKNOWN_POINT"
    with pytest.raises(Refuse) as shape:
        rebuild("porch")
    assert shape.value.code == "BAD_RESULT"
    with pytest.raises(Refuse) as row:
        rebuild((object(),))
    assert row.value.code == "BAD_RESULT"
    too_many = tuple(Line("stop", "card", "", "", "", 1) for _ in range(TRANSCRIPT_CAP + 1))
    with pytest.raises(Refuse) as over:
        rebuild(too_many)
    assert over.value.code == "OVERSIZE"


def test_imports_stay_in_process() -> None:
    source = Path(hooks.__file__ or "").read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module.split(".")[0])
    assert modules <= {"__future__", "re", "collections", "dataclasses", "typing", "cosmos_hermes"}
    banned = ("threading", "subprocess", "socket", "urllib", "pickle", "asyncio")
    for name in banned:
        assert name not in source
