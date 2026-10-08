from __future__ import annotations

import wave
from io import BytesIO

import pytest
from cosmos_voice_duplex.config import trim_spoken
from cosmos_voice_duplex.pcm import chunk, resample, rms, silence, to_wav, tone


def test_rms_silence_and_tone() -> None:
    assert rms(b"") == 0.0
    assert rms(silence(100)) == 0.0
    assert rms(tone(240)) > 0.05


def test_resample_same_rate_is_identity() -> None:
    pcm = tone(32)
    assert resample(pcm, 24000, 24000) == pcm


def test_resample_changes_length() -> None:
    pcm = tone(240, rate=24000)
    out = resample(pcm, 24000, 16000)
    assert len(out) == 160 * 2


def test_wav_header() -> None:
    pcm = tone(240)
    blob = to_wav(pcm, 24000)
    with wave.open(BytesIO(blob), "rb") as handle:
        assert handle.getnchannels() == 1
        assert handle.getsampwidth() == 2
        assert handle.getframerate() == 24000
        assert handle.readframes(handle.getnframes()) == pcm


def test_chunk_drops_a_short_tail() -> None:
    frames = chunk(b"\x01\x00" * 5, 4)
    assert frames == [b"\x01\x00\x01\x00", b"\x01\x00\x01\x00"]


def test_chunk_rejects_odd_frame() -> None:
    with pytest.raises(ValueError):
        chunk(b"\x00\x00", 3)


def test_trim_spoken_cuts_on_a_word() -> None:
    text = "one two three four"
    assert trim_spoken(text, cap=10) == "one two ..."
    assert trim_spoken("short", cap=10) == "short"
