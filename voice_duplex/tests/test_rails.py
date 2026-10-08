from __future__ import annotations

import json

from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.rails.cascade import CascadeRail, parse_stt, stt_request, tts_request
from cosmos_voice_duplex.rails.local_mouth import LocalRail

from tests.support import loud, silence


def test_cascade_turn_uses_fakes_and_barge_drops_audio() -> None:
    rail = CascadeRail()

    def _ask(text: str) -> str:
        assert text == "hello there"
        rail.barge("item", 12)
        return "this reply must not be spoken as audio"

    rail.transcribe = lambda pcm, rate: "hello there"
    rail.ask = _ask
    rail.synthesize = lambda text: b"\x01\x00" * 8
    cfg = VoiceConfig(rail="cascade", silence_ms=500, prefix_padding_ms=200)
    events = []
    rail.open(cfg)
    events.extend(rail.push_audio(loud(100)))
    events.extend(rail.push_audio(silence(500)))
    kinds = [event.kind for event in events]
    assert "user_transcript" in kinds
    assert "audio" not in kinds
    assert any(event.text == "cancelled" for event in events)


def test_cascade_happy_path_speaks() -> None:
    rail = CascadeRail(
        transcribe=lambda pcm, rate: "status",
        ask=lambda text: "Core is up.",
        synthesize=lambda text: b"\x02\x00" * 4,
    )
    cfg = VoiceConfig(rail="cascade")
    rail.open(cfg)
    events = list(rail.push_audio(loud(100)))
    events.extend(rail.push_audio(silence(500)))
    assert any(event.kind == "audio" and event.pcm for event in events)
    assert any(event.text == "Core is up." for event in events)


def test_local_rail_is_honest_and_keeps_bytes() -> None:
    rail = LocalRail()
    rail.open(VoiceConfig(rail="local"))
    events = list(rail.push_audio(loud(100)))
    events.extend(rail.push_audio(silence(500)))
    note = "Grok voice is not connected. I kept what you said on this machine."
    assert any(event.text == note for event in events)
    assert any(event.kind == "audio" and event.pcm for event in events)
    assert rail.utterances
    said = rail.force_say("still here")
    assert said[0].text == "still here"
    assert said[1].pcm


def test_stt_and_tts_requests_do_not_use_the_network() -> None:
    cfg = VoiceConfig()
    stt = stt_request(cfg, b"RIFFxxxx", "test-key")
    assert stt.get_method() == "POST"
    assert stt.full_url.endswith("/stt")
    tts = tts_request(cfg, "hello", "test-key")
    raw = tts.data
    assert isinstance(raw, bytes)
    body = json.loads(raw.decode("utf-8"))
    assert body["voice_id"] == "eve"
    assert body["output_format"]["codec"] == "pcm"
    assert parse_stt(b'{"text": "hello"}') == "hello"
