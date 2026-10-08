from __future__ import annotations

import pytest
from cosmos_voice_duplex.config import PINNED_MODEL, VoiceConfig


def test_defaults_match_the_xai_voice_rail() -> None:
    cfg = VoiceConfig()
    assert cfg.model == PINNED_MODEL
    assert cfg.push_to_talk is False
    assert cfg.half_duplex is False
    assert cfg.barge_in is True
    assert cfg.vad_threshold == 0.85
    assert cfg.realtime_url.endswith("model=" + PINNED_MODEL)


def test_rejected_knobs() -> None:
    with pytest.raises(ValueError):
        VoiceConfig(rail="semantic_vad")
    with pytest.raises(ValueError):
        VoiceConfig(speed=2.0)
    with pytest.raises(ValueError):
        VoiceConfig(max_session_s=9000)
    with pytest.raises(ValueError):
        VoiceConfig(reasoning_effort="low")
