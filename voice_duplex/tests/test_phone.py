from __future__ import annotations

import base64

from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.phone.protocol import MESSAGE_TYPES, SERVER_TYPES
from cosmos_voice_duplex.phone.server import PhoneGateway
from cosmos_voice_duplex.phone.token_broker import (
    EphemeralToken,
    mint_request,
    parse_client_secret,
    subprotocol,
)
from cosmos_voice_duplex.rails.local_mouth import LocalRail
from cosmos_voice_duplex.session import DuplexSession

from tests.support import silence


def _as_dict(item: dict[str, object] | bytes) -> dict[str, object]:
    assert isinstance(item, dict)
    return item


def _gateway() -> PhoneGateway:
    session = DuplexSession(VoiceConfig(rail="local"), LocalRail())
    return PhoneGateway(session)


def test_protocol_names() -> None:
    assert "session.start" in MESSAGE_TYPES
    assert "audio" in MESSAGE_TYPES
    assert "barge" in SERVER_TYPES
    assert "caption" in SERVER_TYPES


def test_hello_start_and_binary_audio() -> None:
    gate = _gateway()
    hello = gate.handle_message({"type": "hello"})
    assert _as_dict(hello[0])["type"] == "ready"
    started = gate.handle_message({"type": "session.start", "voice": "eve"})
    assert _as_dict(started[0])["type"] == "ready"
    assert gate.session.opened is True
    out = gate.handle_message(silence(20))
    assert isinstance(out[-1], bytes)
    assert any(item.get("type") == "state" for item in out if isinstance(item, dict))


def test_audio_before_start_is_an_error() -> None:
    gate = _gateway()
    pcm_b64 = base64.b64encode(silence(20)).decode("ascii")
    out = gate.handle_message({"type": "audio", "pcm": pcm_b64})
    assert _as_dict(out[0])["type"] == "error"


def test_ptt_is_rejected_when_the_option_is_off() -> None:
    gate = _gateway()
    gate.handle_message({"type": "session.start"})
    out = gate.handle_message({"type": "ptt", "held": True})
    assert _as_dict(out[0])["text"] == "push_to_talk is off"


def test_stop_then_start_again() -> None:
    gate = _gateway()
    gate.handle_message({"type": "session.start"})
    gate.handle_message({"type": "stop"})
    again = gate.handle_message({"type": "session.start"})
    assert _as_dict(again[0])["type"] == "ready"
    assert gate.session.opened is True


def test_stop_closes() -> None:
    gate = _gateway()
    gate.handle_message({"type": "session.start"})
    out = gate.handle_message({"type": "stop"})
    assert _as_dict(out[0])["state"] == "idle"
    assert gate.session.opened is False


def test_token_parse_hides_the_value() -> None:
    token = parse_client_secret(b'{"value": "secret-value", "expires_at": 60}')
    assert token.value == "secret-value"
    assert token.expires_at == 60
    assert "secret-value" not in repr(token)
    assert subprotocol(EphemeralToken("secret-value")).endswith("secret-value")
    req = mint_request(VoiceConfig(), "test-key", seconds=300)
    assert req.full_url.endswith("/realtime/client_secrets")
    assert req.get_header("Authorization") == "Bearer test-key"
