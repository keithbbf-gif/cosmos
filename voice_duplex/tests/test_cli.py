from __future__ import annotations

import pytest
from cosmos_voice_duplex.__main__ import main


def test_prints_config_and_not_a_key(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "cosmos-voice 0.1.0" in out
    assert "api_key=missing" in out
    assert "Bearer" not in out
    assert "Desktop loop is off" in out


def test_connect_without_a_key_is_refused(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    assert main(["--connect"]) == 2
    assert "refused" in capsys.readouterr().out.lower()
