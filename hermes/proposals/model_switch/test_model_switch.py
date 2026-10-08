"""Refusal, success, and cap checks for a session model pin."""

from __future__ import annotations

from collections.abc import Iterator
from typing import cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from model_switch import (
    ASK_CAP,
    MODEL_CAP,
    POLICY_CAP,
    SCHEMA,
    Session,
    Switch,
    rebuild,
    set_model,
)

_NAMED = "anthropic/claude-sonnet-4"
_OTHER = "anthropic/claude-opus-4.7"
_ALLOW = (_NAMED, _OTHER)


def _session(pin: str = _NAMED) -> Session:
    return Session("chat-1", pin)


def _code(session: Session, model: str, allow: tuple[str, ...]) -> str:
    with pytest.raises(Refuse) as caught:
        set_model(session, model, allow)
    return caught.value.code


def test_schema_success_records_both_pins() -> None:
    assert SCHEMA == "cosmos-hermes-model_switch/1"
    session = _session()
    switched = set_model(session, _OTHER, _ALLOW)
    assert switched.schema == SCHEMA
    assert switched.session_id == "chat-1"
    assert switched.previous == _NAMED
    assert switched.pin == _OTHER
    assert switched.allow == _ALLOW
    assert type(switched.allow) is tuple
    assert switched.allow_routers is False
    assert switched.cap == POLICY_CAP
    assert switched.policy_cap == POLICY_CAP
    assert switched.asked_cap == POLICY_CAP
    assert session.pin == _NAMED
    again = set_model(session, _OTHER, _ALLOW)
    assert again == switched
    played = rebuild(switched)
    assert played == switched
    assert played is not switched
    fresh = set_model(Session("chat-1", ""), _NAMED, _ALLOW)
    assert fresh.previous == ""
    assert fresh.pin == _NAMED
    assert rebuild(fresh) == fresh
    same = set_model(session, _NAMED, _ALLOW)
    assert same.previous == _NAMED
    assert same.pin == _NAMED
    made = Switch(
        schema=SCHEMA,
        session_id="chat-1",
        previous=_NAMED,
        pin=_OTHER,
        allow=cast(tuple[str, ...], [_NAMED, _OTHER]),
        allow_routers=False,
        cap=POLICY_CAP,
        asked_cap=POLICY_CAP,
        policy_cap=POLICY_CAP,
    )
    assert made == switched
    assert type(made.allow) is tuple
    text = repr(session) + repr(switched) + repr(fresh) + repr(made)
    assert "sk-" not in text
    assert "Bearer" not in text
    assert "api_key=" not in text
    assert not secret_shape(text)


def test_router_and_auto_need_an_explicit_flag() -> None:
    session = _session()
    allowed = (_NAMED, "auto", "openrouter/auto", "openrouter/free", "lab-router", "AUTO")
    for model_id in ("auto", "openrouter/auto", "openrouter/free", "lab-router", "AUTO"):
        with pytest.raises(Refuse) as caught:
            set_model(session, model_id, allowed)
        assert caught.value.code == "ROUTER"
    named = set_model(session, _NAMED, allowed)
    assert named.pin == _NAMED
    assert named.allow_routers is False
    opened = set_model(session, "openrouter/auto", allowed, True)
    assert opened.pin == "openrouter/auto"
    assert opened.allow_routers is True
    assert opened.previous == _NAMED
    assert rebuild(opened) == opened
    folded = set_model(session, "AUTO", allowed, allow_routers=True)
    assert folded.pin == "AUTO"
    with pytest.raises(Refuse) as missing:
        set_model(session, "openrouter/auto", (_NAMED,))
    assert missing.value.code == "PIN_REFUSED"
    away = set_model(
        Session("chat-1", "openrouter/auto"),
        _OTHER,
        _ALLOW,
    )
    assert away.previous == "openrouter/auto"
    assert away.pin == _OTHER
    assert away.allow_routers is False
    assert rebuild(away) == away


def test_cap_records_policy_and_ignores_a_higher_request() -> None:
    session = _session("")
    names = tuple(f"vendor/model-{index}" for index in range(POLICY_CAP))
    switched = set_model(session, names[0], names, cap=10_000)
    assert switched.cap == POLICY_CAP
    assert switched.policy_cap == POLICY_CAP
    assert switched.asked_cap == 10_000
    assert switched.pin == names[0]
    assert switched.previous == ""
    assert switched.allow == names
    assert rebuild(switched) == switched
    assert rebuild(switched) is not switched
    tight = set_model(session, _OTHER, _ALLOW, cap=2)
    assert tight.cap == 2
    assert tight.asked_cap == 2
    assert rebuild(tight) == tight
    with pytest.raises(Refuse) as over:
        set_model(session, _OTHER, _ALLOW, cap=1)
    assert over.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as past:
        set_model(session, names[0], names + ("vendor/extra-model",), cap=10_000)
    assert past.value.code == "OVERSIZE"


def test_grant_is_copied_and_not_a_subclass() -> None:
    session = _session()
    grant = [_NAMED, _OTHER]
    switched = set_model(session, _OTHER, grant)
    grant.append("google/gemini-2.5-flash")
    assert switched.allow == _ALLOW
    assert switched.pin == _OTHER

    class _Bag(list[str]):
        def __iter__(self) -> Iterator[str]:
            yield _NAMED
            yield _OTHER
            yield "vendor/../escaped"

    with pytest.raises(Refuse) as bag:
        set_model(session, _NAMED, _Bag([_NAMED]))
    assert bag.value.code == "BAD_ALLOW"

    class _Tag(str):
        pass

    tagged = set_model(session, _Tag(_OTHER), (_Tag(_NAMED), _Tag(_OTHER)))
    assert type(tagged.pin) is str
    assert tagged.pin == _OTHER
    assert tagged.allow == _ALLOW
    for item in tagged.allow:
        assert type(item) is str


def test_example_model_switch() -> None:
    def once() -> tuple[Switch, Switch, Switch, Switch, str, str]:
        allow = ("grok-4", "grok-4-fast")
        porch = Session("session-porch", "grok-4")
        light = set_model(porch, "grok-4-fast", allow)
        assert porch.pin == "grok-4"
        note = set_model(Session("session-note", "grok-4"), "grok-4-fast", allow)
        card = set_model(Session("session-card", "grok-4"), "grok-4", allow)
        played = rebuild(light)
        missing = _code(Session("session-porch", "grok-4"), "grok-4-mini", allow)
        routed = _code(
            Session("session-porch", "grok-4"),
            "openrouter/auto",
            ("grok-4", "grok-4-fast", "openrouter/auto"),
        )
        return light, note, card, played, missing, routed

    first = once()
    second = once()
    assert first == second
    light, note, card, played, missing, routed = first
    assert light == played
    assert light is not played
    assert light.schema == SCHEMA
    assert light.session_id == "session-porch"
    assert light.previous == "grok-4"
    assert light.pin == "grok-4-fast"
    assert light.allow == ("grok-4", "grok-4-fast")
    assert light.allow_routers is False
    assert light.cap == POLICY_CAP
    assert note.session_id == "session-note"
    assert note.pin == "grok-4-fast"
    assert card.session_id == "session-card"
    assert card.previous == "grok-4"
    assert card.pin == "grok-4"
    assert missing == "PIN_REFUSED"
    assert routed == "ROUTER"
    assert "sk-" not in repr(light)
    assert not secret_shape(repr((light, note, card)))


def test_refusal_codes() -> None:
    session = _session()
    with pytest.raises(Refuse) as empty:
        set_model(session, _NAMED, ())
    assert empty.value.code == "EMPTY_ALLOW"
    with pytest.raises(Refuse) as empty_list:
        set_model(session, _NAMED, [])
    assert empty_list.value.code == "EMPTY_ALLOW"
    with pytest.raises(Refuse) as refused:
        set_model(session, "google/gemini-2.5-flash", _ALLOW)
    assert refused.value.code == "PIN_REFUSED"
    with pytest.raises(Refuse) as folded_name:
        set_model(session, "Anthropic/claude-sonnet-4", _ALLOW)
    assert folded_name.value.code == "PIN_REFUSED"
    with pytest.raises(Refuse) as secret_model:
        set_model(session, "sk-abcdefghij", ("sk-abcdefghij",))
    assert secret_model.value.code == "SECRET"
    with pytest.raises(Refuse) as secret_allow:
        set_model(session, _NAMED, ("api_key=abcdefgh",))
    assert secret_allow.value.code == "SECRET"
    with pytest.raises(Refuse) as bearer:
        set_model(session, "Bearer abcdefghijk", _ALLOW)
    assert bearer.value.code == "SECRET"
    with pytest.raises(Refuse) as secret_pin:
        Session("chat-1", "sk-abcdefghij")
    assert secret_pin.value.code == "SECRET"
    with pytest.raises(Refuse) as bad_model:
        set_model(session, "", _ALLOW)
    assert bad_model.value.code == "BAD_MODEL"
    with pytest.raises(Refuse) as spaced:
        set_model(session, "claude sonnet", _ALLOW)
    assert spaced.value.code == "BAD_MODEL"
    for shaped in ("vendor/../other", "vendor//other", "vendor/./other", "vendor/", r"ven\dor"):
        with pytest.raises(Refuse) as path_id:
            set_model(session, shaped, _ALLOW)
        assert path_id.value.code == "BAD_MODEL"
    with pytest.raises(Refuse) as bad_session:
        set_model("chat-1", _NAMED, _ALLOW)
    assert bad_session.value.code == "BAD_SESSION"
    with pytest.raises(Refuse) as blank_session:
        Session("", _NAMED)
    assert blank_session.value.code == "BAD_SESSION"
    with pytest.raises(Refuse) as dotted_session:
        Session("porch..light", _NAMED)
    assert dotted_session.value.code == "BAD_SESSION"
    with pytest.raises(Refuse) as bad_allow:
        set_model(session, _NAMED, _NAMED)
    assert bad_allow.value.code == "BAD_ALLOW"
    with pytest.raises(Refuse) as mapping:
        set_model(session, _NAMED, {_NAMED: _NAMED})
    assert mapping.value.code == "BAD_ALLOW"

    def _once_names() -> Iterator[str]:
        yield _NAMED

    with pytest.raises(Refuse) as stream:
        set_model(session, _NAMED, _once_names())
    assert stream.value.code == "BAD_ALLOW"
    with pytest.raises(Refuse) as flag:
        set_model(session, _NAMED, _ALLOW, "yes")
    assert flag.value.code == "BAD_FLAG"
    with pytest.raises(Refuse) as duplicate:
        set_model(session, _NAMED, (_NAMED, _NAMED))
    assert duplicate.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as text:
        set_model(session, 12, _ALLOW)
    assert text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as item:
        set_model(session, _NAMED, (_NAMED, 4))
    assert item.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        set_model(session, _NAMED + "\x00", _ALLOW)
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as huge:
        set_model(session, "a" * (MODEL_CAP + 1), _ALLOW)
    assert huge.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as flag_cap:
        set_model(session, _NAMED, _ALLOW, cap=True)
    assert flag_cap.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low:
        set_model(session, _NAMED, _ALLOW, cap=0)
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as high:
        set_model(session, _NAMED, _ALLOW, cap=ASK_CAP + 1)
    assert high.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as record:
        Switch(
            schema="nope",
            session_id="chat-1",
            previous="",
            pin=_NAMED,
            allow=(_NAMED,),
            allow_routers=False,
            cap=1,
            asked_cap=1,
            policy_cap=POLICY_CAP,
        )
    assert record.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as raised:
        Switch(
            schema=SCHEMA,
            session_id="chat-1",
            previous="",
            pin=_NAMED,
            allow=(_NAMED,),
            allow_routers=False,
            cap=100,
            asked_cap=100,
            policy_cap=POLICY_CAP,
        )
    assert raised.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as asked_bool:
        Switch(
            schema=SCHEMA,
            session_id="chat-1",
            previous="",
            pin=_NAMED,
            allow=(_NAMED,),
            allow_routers=False,
            cap=1,
            asked_cap=True,
            policy_cap=POLICY_CAP,
        )
    assert asked_bool.value.code == "NOT_INT"
    with pytest.raises(Refuse) as forged:
        Switch(
            schema=SCHEMA,
            session_id="chat-1",
            previous=_NAMED,
            pin="openrouter/auto",
            allow=(_NAMED, "openrouter/auto"),
            allow_routers=False,
            cap=POLICY_CAP,
            asked_cap=POLICY_CAP,
            policy_cap=POLICY_CAP,
        )
    assert forged.value.code == "ROUTER"
    with pytest.raises(Refuse) as unlisted_router:
        Switch(
            schema=SCHEMA,
            session_id="chat-1",
            previous=_NAMED,
            pin="openrouter/auto",
            allow=(_NAMED,),
            allow_routers=False,
            cap=POLICY_CAP,
            asked_cap=POLICY_CAP,
            policy_cap=POLICY_CAP,
        )
    assert unlisted_router.value.code == "PIN_REFUSED"
    with pytest.raises(Refuse) as off_list:
        Switch(
            schema=SCHEMA,
            session_id="chat-1",
            previous="",
            pin=_OTHER,
            allow=(_NAMED,),
            allow_routers=False,
            cap=POLICY_CAP,
            asked_cap=POLICY_CAP,
            policy_cap=POLICY_CAP,
        )
    assert off_list.value.code == "PIN_REFUSED"
    with pytest.raises(Refuse) as replay:
        rebuild(session)
    assert replay.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as replay_text:
        rebuild("session-porch")
    assert replay_text.value.code == "BAD_RECORD"
