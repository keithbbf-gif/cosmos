"""Seat binds a day-one door and builds a keyless chat body."""

from __future__ import annotations

import json

import pytest

from cosmos_federation import DEFAULT_CAP_USD_MICROS, MAX_CAP_USD_MICROS, Refuse, secret_shape
from seat import SCHEMA, Reply, Seat, Turn, bind, fake_reply, request_body, suggested_pin, user_turn

_OPENROUTER = "google/gemma-4-26b-a4b-it:free"
_XAI = "grok-4.6"


def _seat(door: str = "openrouter", cap: int = DEFAULT_CAP_USD_MICROS) -> Seat:
    pin = suggested_pin(door)
    return bind(door, "cred-dayone-1", pin, cap)


def _strings(value: object) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, dict):
        for key, item in value.items():
            found.extend(_strings(key))
            found.extend(_strings(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(_strings(item))
    return found


def test_schema_and_suggested_pins() -> None:
    assert SCHEMA == "cosmos-federation-seat/1"
    assert suggested_pin("openrouter") == _OPENROUTER
    assert suggested_pin("OpenRouter") == _OPENROUTER
    assert suggested_pin("xai") == _XAI
    assert suggested_pin("XAI") == _XAI


def test_suggested_pin_refuses_unknown_and_anthropic() -> None:
    with pytest.raises(Refuse) as anthropic:
        suggested_pin("anthropic")
    assert anthropic.value.code == "ANTHROPIC_OFF"
    with pytest.raises(Refuse) as door:
        suggested_pin("other")
    assert door.value.code == "DOOR"


def test_bind_stores_the_folded_door_and_the_pin() -> None:
    seat = bind("OpenRouter", "  cred-dayone-1  ", "  " + _OPENROUTER + "  ", DEFAULT_CAP_USD_MICROS)
    assert seat.door == "openrouter"
    assert seat.credential_id == "cred-dayone-1"
    assert seat.pin == _OPENROUTER
    assert seat.cap_usd_micros == DEFAULT_CAP_USD_MICROS
    assert isinstance(seat, Seat)
    assert "pin" in Seat.__slots__
    assert "text" in Turn.__slots__
    assert "usd_micros" in Reply.__slots__


def test_bind_refuses_empty_pin_anthropic_secret_id_and_bad_cap() -> None:
    with pytest.raises(Refuse) as empty:
        bind("openrouter", "cred-dayone-1", "   ", 1)
    assert empty.value.code == "BOUND"
    for pin in ("anthropic/claude-sonnet", "claude-3", "vendor/Claude-x"):
        with pytest.raises(Refuse) as off:
            bind("xai", "cred-dayone-1", pin, 1)
        assert off.value.code == "ANTHROPIC_OFF"
        assert pin not in str(off.value)
    shaped = "sk-" + ("a" * 12)
    with pytest.raises(Refuse) as secret:
        bind("openrouter", shaped, _OPENROUTER, 1)
    assert secret.value.code == "SECRET"
    assert shaped not in str(secret.value)
    for bad in (0, -1, MAX_CAP_USD_MICROS + 1, True, 1.5):
        with pytest.raises(Refuse) as cap:
            bind("openrouter", "cred-dayone-1", _OPENROUTER, bad)  # type: ignore[arg-type]
        assert cap.value.code == "CAP"


def test_user_turn_bounds_text_at_4000() -> None:
    seat = _seat()
    turn = user_turn(seat, "a" * 4000)
    assert turn.text == "a" * 4000
    assert turn.pin == seat.pin
    assert turn.cap_usd_micros == seat.cap_usd_micros
    with pytest.raises(Refuse) as over:
        user_turn(seat, "a" * 4001)
    assert over.value.code == "BOUND"
    with pytest.raises(Refuse) as blank:
        user_turn(seat, "  ")
    assert blank.value.code == "BOUND"
    leaked = "Bearer " + ("c" * 8)
    with pytest.raises(Refuse) as secret:
        user_turn(seat, leaked)
    assert secret.value.code == "SECRET"
    assert leaked not in str(secret.value)


def test_request_body_matches_the_rail_and_has_no_key_shaped_string() -> None:
    seat = _seat("xai", cap=10)
    turn = user_turn(seat, "hello from a new peer")
    body = request_body(turn)
    assert body["model"] == _XAI
    assert body["messages"] == [{"role": "user", "content": "hello from a new peer"}]
    assert body["max_tokens"] == 1024
    assert body["stream"] is False
    assert body["provider"] == {"allow_fallbacks": False}
    assert "credential_id" not in body
    assert "Authorization" not in body
    encoded = json.dumps(body)
    assert secret_shape(encoded) is False
    for piece in _strings(body):
        assert secret_shape(piece) is False
    lowered = encoded.lower()
    assert "authorization" not in lowered
    assert "bearer" not in lowered
    assert "api_key" not in lowered
    assert "sk-" not in encoded
    assert seat.credential_id not in encoded


def test_fake_reply_refuses_cost_above_the_seat_cap() -> None:
    turn = user_turn(_seat(cap=100), "ping")
    same = fake_reply(turn, "pong", 100)
    assert same == Reply(pin=turn.pin, text="pong", usd_micros=100)
    free = fake_reply(turn, "free", 0)
    assert free.usd_micros == 0
    with pytest.raises(Refuse) as over:
        fake_reply(turn, "too much", 101)
    assert over.value.code == "OVER_CAP"
    with pytest.raises(Refuse) as policy:
        fake_reply(turn, "way over", MAX_CAP_USD_MICROS + 5)
    assert policy.value.code == "OVER_CAP"
    with pytest.raises(Refuse) as negative:
        fake_reply(turn, "nope", -1)
    assert negative.value.code == "BOUND"


def test_repr_of_public_objects_has_no_secret_shape() -> None:
    seat = _seat()
    turn = user_turn(seat, "a plain sentence")
    reply = fake_reply(turn, "a plain answer", 1)
    for obj in (seat, turn, reply):
        assert secret_shape(repr(obj)) is False
