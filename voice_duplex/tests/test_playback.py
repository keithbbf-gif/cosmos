from __future__ import annotations

import pytest
from cosmos_voice_duplex.playback import Playback


def test_read_counts_only_real_audio_and_pads() -> None:
    play = Playback(sample_rate=1000)
    play.write(b"\x01\x00" * 10)
    out = play.read(8)
    assert out == b"\x01\x00" * 4
    assert play.played_ms() == 4
    pad = play.read(30)
    assert len(pad) == 30
    assert pad[:12] == b"\x01\x00" * 6
    assert pad.endswith(b"\x00\x00")
    # Six more real samples count. The zero pad does not.
    assert play.played_ms() == 10


def test_clear_does_not_reset_played() -> None:
    play = Playback()
    play.write(b"\x02\x00" * 50)
    play.read(20)
    played = play.played_ms()
    dropped = play.clear()
    assert dropped == 80
    assert play.played_ms() == played
    assert play.pending is False
    play.reset_played()
    assert play.played_ms() == 0


def test_overflow_drops_oldest() -> None:
    play = Playback(sample_rate=24000, cap_ms=10)  # 480 bytes
    play.write(b"\x01\x00" * 100)
    play.write(b"\x02\x00" * 200)
    assert len(play) <= play.cap_bytes + 1
    assert play.dropped_bytes > 0


def test_read_rejects_negative() -> None:
    with pytest.raises(ValueError):
        Playback().read(-1)
