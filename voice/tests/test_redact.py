"""Redaction keeps secret-shaped spans out of text we might print."""

from __future__ import annotations

from cosmos_voice.redact import redact, secret_shape

_EMBEDDED = (
    "Authorization: Bearer abcdefghijk",
    "sk-livekeyvalue",
    "sk-ant-livekeyvalue",
    "xai-livekeyvalue",
    "api_key=livekeyvalue",
    "token=livekeyvalue",
    "AKIAIOSFODNN7EXAMPLE",
)
_BARE = ("AKIA", "sk-", "sk-ant-", "xai-", "api_key=", "token=")


def test_empty_and_plain_text() -> None:
    assert secret_shape("") is False
    assert redact("") == ""
    assert secret_shape("hello cosmos") is False
    assert redact("hello cosmos") == "hello cosmos"


def test_each_named_shape_is_redacted() -> None:
    for sample in _EMBEDDED:
        cleaned = redact(f"before {sample} after")
        leaked = sample in cleaned
        assert secret_shape(sample) is True
        assert leaked is False
        assert secret_shape(cleaned) is False
        assert cleaned.startswith("before ") is True
        assert cleaned.endswith(" after") is True
        assert "[REDACTED]" in cleaned
    for sample in _BARE:
        cleaned = redact(sample)
        leaked = sample in cleaned
        assert secret_shape(sample) is True
        assert leaked is False
        assert cleaned == "[REDACTED]"


def test_neighbor_text_survives() -> None:
    cleaned = redact("note sk-abc123 then token=zzz done")
    assert cleaned == "note [REDACTED] then [REDACTED] done"
