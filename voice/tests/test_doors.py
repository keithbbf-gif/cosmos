"""Doors refuse Claude, a missing key, and a missing transport. Core posts voice."""

from __future__ import annotations

import inspect
import json

import cosmos_voice.doors as doors
import pytest
from cosmos_voice.doors import (
    ClaudeDoor,
    CoreMouth,
    GrokVoiceDoor,
    OpenAIRealtimeDoor,
    open_door,
)
from cosmos_voice.errors import VoiceError
from cosmos_voice.session import VoiceSession
from cosmos_voice.transport import CoreClient, MemoryTransport


def _session() -> VoiceSession:
    """One handset session for a door test."""

    return VoiceSession(client_id="handset")


def _json_body(raw: bytes | None) -> dict[str, object]:
    """Decode one recorded request body. A missing body is a failed post."""

    assert raw is not None
    parsed: object = json.loads(raw.decode("utf-8"))
    assert isinstance(parsed, dict)
    found: dict[str, object] = {}
    for key, value in parsed.items():
        found[str(key)] = value
    return found


def _raise(
    door: CoreMouth | GrokVoiceDoor | OpenAIRealtimeDoor | ClaudeDoor,
    transcript: str = "hello",
) -> VoiceError:
    """Call ``speak_turn`` and return the VoiceError. Other errors propagate."""

    with pytest.raises(VoiceError) as caught:
        door.speak_turn(transcript, _session())
    err = caught.value
    assert isinstance(err, VoiceError)
    return err


def test_claude_raises_anthropic_off() -> None:
    """Claude raises ANTHROPIC_OFF and stores neither a key nor the transcript."""

    door = ClaudeDoor()
    secret = "sk-claude-example"
    err = _raise(door, secret)
    assert err.kind == "ANTHROPIC_OFF"
    leaked = secret in str(err)
    assert not leaked
    assert door.__dict__ == {}
    opened = open_door("claude", api_key=secret)
    assert isinstance(opened, ClaudeDoor)
    assert opened.__dict__ == {}
    again = _raise(opened, secret)
    assert again.kind == "ANTHROPIC_OFF"
    leaked_again = secret in str(again)
    assert not leaked_again


def test_grok_without_key_raises_no_key() -> None:
    """An empty Grok key is NO_KEY, before any transport is used."""

    err = _raise(GrokVoiceDoor(""))
    assert err.kind == "NO_KEY"
    opened = _raise(open_door("grok"))
    assert opened.kind == "NO_KEY"


def test_grok_key_without_transport_raises_not_composed() -> None:
    """A key with no injected transport is NOT_COMPOSED and the key is not in the error."""

    secret = "grok-test-key"
    door = GrokVoiceDoor(secret)
    leaked = secret in repr(door)
    assert not leaked
    err = _raise(door)
    assert err.kind == "NOT_COMPOSED"
    leaked_error = secret in str(err) or secret in err.detail
    assert not leaked_error
    opened = _raise(open_door("grok", api_key=secret))
    assert opened.kind == "NOT_COMPOSED"
    leaked_opened = secret in str(opened)
    assert not leaked_opened


def test_openai_matches_grok_refusals() -> None:
    """OpenAI uses the same NO_KEY and NOT_COMPOSED refusals and opens no socket."""

    missing = _raise(OpenAIRealtimeDoor())
    assert missing.kind == "NO_KEY"
    secret = "openai-test-key"
    err = _raise(OpenAIRealtimeDoor(secret))
    assert err.kind == "NOT_COMPOSED"
    leaked = secret in str(err)
    assert not leaked
    via = _raise(open_door("openai", api_key=secret, transport=None))
    assert via.kind == "NOT_COMPOSED"


def test_open_door_rejects_unknown_and_core_without_client() -> None:
    """Unknown names and a core door without client= are BAD_MODE."""

    with pytest.raises(VoiceError) as unknown:
        open_door("nope")
    err = unknown.value
    assert isinstance(err, VoiceError)
    assert err.kind == "BAD_MODE"
    with pytest.raises(VoiceError) as missing:
        open_door("core")
    core_err = missing.value
    assert isinstance(core_err, VoiceError)
    assert core_err.kind == "BAD_MODE"


def test_core_mouth_posts_voice() -> None:
    """CoreMouth posts the session body to /api/v1/voice and returns that reply."""

    reply: dict[str, object] = {"spoken": "ready", "needs_confirm": False, "brain": "core"}
    transport = MemoryTransport([("POST", "/api/v1/voice", 200, reply)])
    client = CoreClient("https://core.example", "", transport=transport)
    session = _session()
    result = CoreMouth(client).speak_turn("ping", session, mode="wake", confirm_id="c1")
    assert result == reply
    posted = False
    for method, url, _headers, body, _timeout in transport.calls:
        if method == "POST" and "/api/v1/voice" in url:
            posted = True
            sent = _json_body(body)
            assert sent.get("transcript") == "ping"
            assert sent.get("mode") == "wake"
            assert sent.get("confirm_id") == "c1"
    assert posted is True
    mouth = open_door("core", client=client)
    assert isinstance(mouth, CoreMouth)


def test_grok_posts_json_and_maps_output() -> None:
    """Grok posts model plus input. The key is a header, not the JSON, and output maps."""

    secret = "grok-header-key"
    first: dict[str, object] = {"output": "alpha", "needs_confirm": True}
    second: dict[str, object] = {"spoken": "beta"}
    transport = MemoryTransport(
        [
            ("POST", "/v1/realtime", 200, first),
            ("POST", "/v1/realtime", 200, second),
        ]
    )
    door = GrokVoiceDoor(secret, transport=transport)
    session = _session()
    mapped = door.speak_turn("hello", session)
    assert mapped == {"spoken": "alpha", "needs_confirm": False, "brain": "grok"}
    spoken = door.speak_turn("again", session)
    assert spoken["spoken"] == "beta"
    assert spoken["brain"] == "grok"
    assert spoken["needs_confirm"] is False
    saw_header = False
    for _method, url, headers, body, _timeout in transport.calls:
        auth = headers.get("Authorization", "")
        if auth == "Bearer " + secret:
            saw_header = True
        sent = _json_body(body)
        leaked = secret in str(sent) or secret in url
        assert not leaked
        assert sent.get("model") == "grok-voice-think-fast-2.0"
        assert "input" in sent
    assert saw_header is True


def test_openai_maps_spoken_field() -> None:
    """OpenAI uses its model name and maps a spoken field to brain openai."""

    secret = "openai-header-key"
    transport = MemoryTransport(
        [("POST", "/v1/realtime", 200, {"spoken": "there"})]
    )
    door = OpenAIRealtimeDoor(secret, transport=transport)
    mapped = door.speak_turn("hi", _session())
    assert mapped == {"spoken": "there", "needs_confirm": False, "brain": "openai"}
    _method, _url, headers, body, _timeout = transport.calls[0]
    sent = _json_body(body)
    assert sent.get("model") == "gpt-realtime-2.1"
    matched = headers.get("Authorization", "") == "Bearer " + secret
    assert matched is True


def test_doors_do_not_open_sockets_or_read_env() -> None:
    """The door module does not import a socket stack or read the environment."""

    source = inspect.getsource(doors)
    assert "import socket" not in source
    assert "urlopen" not in source
    assert "os.environ" not in source
    assert "getenv" not in source
