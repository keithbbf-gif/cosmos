from __future__ import annotations

from cosmos_voice_duplex.vad import EnergyVad

from tests.support import loud, silence


def test_silence_does_not_start() -> None:
    vad = EnergyVad(silence_ms=20, prefix_ms=40, min_speech_ms=40)
    assert vad.push(silence(40)) == []
    assert vad.speaking is False


def test_speech_then_hangover_emits_start_and_end() -> None:
    vad = EnergyVad(silence_ms=20, prefix_ms=40, min_speech_ms=40)
    started = vad.push(loud(40))
    assert [event.kind for event in started] == ["start"]
    assert vad.speaking is True
    ended = vad.push(silence(20))
    assert len(ended) == 1
    assert ended[0].kind == "end"
    assert loud(40) in ended[0].utterance
    assert vad.speaking is False


def test_prefix_zero_keeps_the_trigger_frame() -> None:
    vad = EnergyVad(silence_ms=20, prefix_ms=0, min_speech_ms=20)
    vad.push(loud(20))
    ended = vad.push(silence(20))
    assert ended[0].kind == "end"
    assert ended[0].utterance.startswith(loud(20))


def test_reset_clears_speech() -> None:
    vad = EnergyVad(min_speech_ms=20, silence_ms=500, prefix_ms=0)
    vad.push(loud(20))
    assert vad.speaking is True
    vad.reset()
    assert vad.speaking is False
