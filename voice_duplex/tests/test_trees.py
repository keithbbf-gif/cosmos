"""Read-only checks against the live trees. This file does not write them."""

from __future__ import annotations

from pathlib import Path

from cosmos_voice_duplex.bind.cosmos_voice import probe
from cosmos_voice_duplex.config import MAX_TRANSCRIPT, SPOKEN_MAX
from cosmos_voice_duplex.confirm import CONSEQUENTIAL, DESTRUCTIVE

LIVE_VOICE = Path(r"V:\A\Ai\COSMOS\cosmos\cosmos_voice.py")
KEITH = Path(r"V:\streams\cosmos_code\harness\KEITH_20260930_STANDALONE.md")
STAGED = Path(r"V:\streams\cosmos_code_voice")
PRODUCT = Path(r"V:\streams\cosmos_code\product")


def test_live_voice_constants_match_the_duplex_gate() -> None:
    found = probe(LIVE_VOICE)
    assert found["SPOKEN_MAX"] == SPOKEN_MAX == 320
    assert found["MAX_TRANSCRIPT"] == MAX_TRANSCRIPT == 4000
    assert found["CONFIRM_TTL"] == 300.0
    assert found["CONSEQUENTIAL_VERBS"] == set(CONSEQUENTIAL) == {"submit", "session"}
    assert found["DESTRUCTIVE_VERBS"] == set(DESTRUCTIVE)
    assert "delete" in set(DESTRUCTIVE)
    assert found["handle_args"] == [
        "self",
        "session_id",
        "transcript",
        "mode",
        "confirm_id",
    ]


def test_probe_source_does_not_import_cosmos() -> None:
    path = STAGED / "cosmos_voice_duplex" / "bind" / "cosmos_voice.py"
    text = path.read_text(encoding="utf-8")
    assert "import cosmos\n" not in text
    assert "import cosmos_voice\n" not in text


def test_named_code_plugins_and_voice_stays_outside_both_trees() -> None:
    text = KEITH.read_text(encoding="utf-8")
    assert "SESSIONS" in text
    assert "CLUSTERS" in text
    assert (STAGED / "cosmos_voice_duplex" / "session.py").is_file()
    assert not Path(r"V:\A\Ai\COSMOS\cosmos\cosmos_voice_duplex").exists()
    assert not (PRODUCT / "cosmos_voice_duplex").exists()
    assert not (PRODUCT / "cosmos_code" / "cosmos_voice_duplex").exists()


def test_android_client_matches_the_gateway_words() -> None:
    root = STAGED / "android"
    sources = [path.read_text(encoding="utf-8") for path in root.rglob("*.kt")]
    blob = "\n".join(sources)
    for word in ("hello", "session.start", "mute", "ptt", "stop", "barge", "caption"):
        assert word in blob
    assert "AcousticEchoCanceler" in blob
    assert "XAI_API_KEY" not in blob
    assert "api_token" not in blob
