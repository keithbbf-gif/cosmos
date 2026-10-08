from __future__ import annotations

import pytest
from cosmos_voice_duplex.turn import TurnMachine


def _speak(machine: TurnMachine) -> None:
    machine.on("session_ready")
    machine.on("speech_start")
    machine.on("speech_stop")
    machine.on("audio_delta")


def test_default_path_reaches_assistant_and_barge() -> None:
    machine = TurnMachine()
    assert machine.on("session_ready") == "listening"
    assert machine.on("speech_start") == "user_speaking"
    assert machine.on("speech_stop") == "thinking"
    assert machine.on("audio_delta") == "assistant_speaking"
    assert machine.on("barge_local") == "barge"
    assert machine.on("speech_start") == "user_speaking"


def test_unknown_event_raises() -> None:
    machine = TurnMachine()
    with pytest.raises(ValueError):
        machine.on("send")


def test_ptt_is_off_unless_asked() -> None:
    machine = TurnMachine()
    machine.on("session_ready")
    assert machine.on("ptt_down") == "listening"
    held = TurnMachine(push_to_talk=True)
    held.on("session_ready")
    assert held.on("ptt_down") == "user_speaking"
    assert held.on("ptt_up") == "thinking"


def test_playback_drain_returns_to_listening() -> None:
    machine = TurnMachine()
    _speak(machine)
    assert machine.state == "assistant_speaking"
    assert machine.on("response_done") == "assistant_speaking"
    assert machine.on("playback_drained") == "listening"


def test_barge_consumes_the_next_event() -> None:
    machine = TurnMachine()
    _speak(machine)
    machine.on("interrupted")
    assert machine.state == "barge"
    assert machine.on("response_done") == "user_speaking"
