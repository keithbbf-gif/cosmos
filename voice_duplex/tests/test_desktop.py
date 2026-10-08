from __future__ import annotations

import pytest
from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.desktop.loop import SoundDeviceLoop, mix_callback
from cosmos_voice_duplex.desktop.runner import ScriptedDevice, build_session, run_frames
from cosmos_voice_duplex.rails.local_mouth import LocalRail
from cosmos_voice_duplex.session import DuplexSession
from cosmos_voice_duplex.spend import AllowSpend

from tests.support import silence


def test_scripted_device_runs_without_a_card() -> None:
    spend = AllowSpend()
    session = DuplexSession(VoiceConfig(rail="local"), LocalRail(), spend=spend)
    assert session.open()
    device = ScriptedDevice([silence(20), silence(20)])
    run_frames(session, device, 2)
    assert len(device.played) == 2
    assert all(len(frame) == session.cfg.frame_bytes for frame in device.played)


def test_mix_callback_fills_the_speaker_buffer() -> None:
    session = DuplexSession(VoiceConfig(rail="local"), LocalRail())
    session.open()
    out = bytearray(session.cfg.frame_bytes)
    mix_callback(silence(20), out, session)
    assert len(out) == session.cfg.frame_bytes


def test_card_callback_does_not_feed_the_session() -> None:
    spend = AllowSpend()
    session = DuplexSession(VoiceConfig(rail="local"), LocalRail(), spend=spend)
    session.open()
    loop = SoundDeviceLoop(session)
    out = bytearray(session.cfg.frame_bytes)
    loop.callback(silence(20), out)
    assert spend.ms == 0
    assert loop.rings.mic_waiting() == session.cfg.frame_bytes
    assert out == bytearray(session.cfg.frame_bytes)
    loop.pump()
    assert spend.ms == 20


def test_auto_without_a_key_is_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    session = build_session(VoiceConfig(rail="auto"))
    assert session.rail.name == "local"
