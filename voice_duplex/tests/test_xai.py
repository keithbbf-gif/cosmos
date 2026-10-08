from __future__ import annotations

import base64

from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.rails.xai_realtime import (
    MemoryTransport,
    XaiRealtimeRail,
    build_session_update,
    decode_event,
    encode_force,
    encode_truncate,
)


def test_session_update_uses_server_vad_and_no_commit() -> None:
    cfg = VoiceConfig(rail="xai", keyterms=("COSMOS",))
    message = build_session_update(cfg, [{"type": "function", "name": "status"}])
    assert message["type"] == "session.update"
    session = message["session"]
    assert isinstance(session, dict)
    turn = session["turn_detection"]
    assert isinstance(turn, dict)
    assert turn["type"] == "server_vad"
    assert turn["threshold"] == 0.85
    assert "input_audio_buffer.commit" not in str(message)
    assert session["tools"] == [{"type": "function", "name": "status"}]


def test_push_to_talk_clears_turn_detection() -> None:
    cfg = VoiceConfig(push_to_talk=True)
    message = build_session_update(cfg)
    session = message["session"]
    assert isinstance(session, dict)
    assert session["turn_detection"] is None


def test_decode_speech_and_audio_alias() -> None:
    started = decode_event({"type": "input_audio_buffer.speech_started", "item_id": "it"})
    assert started[0].kind == "speech_started"
    pcm = b"\x01\x00\x02\x00"
    audio = decode_event(
        {
            "type": "response.audio.delta",
            "delta": base64.b64encode(pcm).decode("ascii"),
            "item_id": "it",
        }
    )
    assert audio[0].kind == "audio"
    assert audio[0].pcm == pcm
    assert decode_event(pcm)[0].pcm == pcm


def test_truncate_uses_played_ms() -> None:
    message = encode_truncate("item-1", 42)
    assert message["audio_end_ms"] == 42
    assert message["content_index"] == 0
    assert message["type"] == "conversation.item.truncate"


def test_force_message_does_not_create_a_response() -> None:
    message = encode_force("Say yes to confirm that.")
    assert message["type"] == "conversation.item.create"
    item = message["item"]
    assert isinstance(item, dict)
    assert item["type"] == "force_message"
    assert "response.create" not in str(message)


def test_barge_cancels_and_truncates_without_clearing_input() -> None:
    transport = MemoryTransport()
    rail = XaiRealtimeRail(transport)
    rail.open(VoiceConfig(rail="xai"))
    rail.item_id = "item-9"
    rail.barge("item-9", 15)
    kinds = [message["type"] for message in transport.sent]
    assert "response.cancel" in kinds
    assert "conversation.item.truncate" in kinds
    assert "input_audio_buffer.clear" not in kinds
    truncate = transport.sent[-1]
    assert truncate["audio_end_ms"] == 15
