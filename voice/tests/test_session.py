"""Tests for voice session bodies, caps, and reply notes."""

from __future__ import annotations

import pytest
from cosmos_voice.errors import VoiceError
from cosmos_voice.session import VoiceSession, new_idempotency_key
from cosmos_voice.types import MAX_TITLE, MAX_TRANSCRIPT


def test_new_idempotency_key_is_uuid4_hex() -> None:
    """Keys are 32 lowercase hex characters and are not reused."""
    first = new_idempotency_key()
    second = new_idempotency_key()
    assert first != second
    assert len(first) == 32
    assert "-" not in first
    assert first == first.lower()
    int(first, 16)


def test_voice_session_defaults() -> None:
    """The handset starts with the shared session defaults and no id."""
    session = VoiceSession(client_id="handset")
    assert session.client_id == "handset"
    assert session.build == "cosmos-voice"
    assert session.stream == ""
    assert session.title == "voice session"
    assert session.session_id is None
    assert session.last_spoken == ""
    assert session.last_brain == ""


def test_voice_body_required_keys_and_omitted_empties() -> None:
    """A first turn always carries the envelope and omits empty ids."""
    session = VoiceSession(client_id="handset-1", stream="cm", title="drive")
    body = session.voice_body("hello", mode="ptt")
    assert body["transcript"] == "hello"
    assert body["mode"] == "ptt"
    assert body["title"] == "drive"
    assert body["client_id"] == "handset-1"
    assert body["build"] == "cosmos-voice"
    assert body["stream"] == "cm"
    key = body["idempotency_key"]
    assert isinstance(key, str)
    assert len(key) == 32
    int(key, 16)
    assert "session_id" not in body
    assert "confirm_id" not in body


def test_voice_body_omits_blank_session_id() -> None:
    """An empty string session id is omitted the same way ``None`` is."""
    session = VoiceSession(client_id="handset", session_id="")
    body = session.voice_body("hi", mode="off", confirm_id="")
    assert "session_id" not in body
    assert "confirm_id" not in body
    assert body["stream"] == ""


def test_voice_body_includes_session_and_confirm_when_set() -> None:
    """A resumed session and a confirm nonce are sent when they are set."""
    session = VoiceSession(client_id="handset", session_id="sid-1", build="dev")
    body = session.voice_body(
        "hi",
        mode="wake",
        confirm_id="cid-9",
        idempotency_key="given-key",
    )
    assert body["session_id"] == "sid-1"
    assert body["confirm_id"] == "cid-9"
    assert body["idempotency_key"] == "given-key"
    assert body["build"] == "dev"
    assert list(body) == [
        "transcript",
        "session_id",
        "mode",
        "confirm_id",
        "title",
        "client_id",
        "build",
        "stream",
        "idempotency_key",
    ]


def test_empty_idempotency_key_uses_generator(monkeypatch: pytest.MonkeyPatch) -> None:
    """A blank idempotency argument is replaced; a later call is a new key."""
    monkeypatch.setattr("cosmos_voice.session.new_idempotency_key", lambda: "fixed-key")
    session = VoiceSession(client_id="handset")
    body = session.voice_body("hi", mode="tap", idempotency_key="")
    assert body["idempotency_key"] == "fixed-key"


def test_each_generated_key_is_fresh() -> None:
    """Two turns without a caller key do not share an idempotency key."""
    session = VoiceSession(client_id="handset")
    first = session.voice_body("hi", mode="ptt")
    second = session.voice_body("hi", mode="ptt")
    assert first["idempotency_key"] != second["idempotency_key"]


def test_transcript_at_cap_is_allowed() -> None:
    """A transcript of exactly the cap is sent unchanged."""
    session = VoiceSession(client_id="handset")
    text = "a" * MAX_TRANSCRIPT
    body = session.voice_body(text, mode="ptt", idempotency_key="k")
    assert body["transcript"] == text


def test_transcript_over_cap_raises() -> None:
    """Over-cap transcripts refuse and do not echo the text."""
    session = VoiceSession(client_id="handset")
    text = "b" * (MAX_TRANSCRIPT + 1)
    with pytest.raises(VoiceError) as caught:
        session.voice_body(text, mode="ptt")
    assert caught.value.kind == "TRANSCRIPT_TOO_LONG"
    assert text not in caught.value.detail
    assert text not in str(caught.value)


def test_title_at_cap_is_allowed() -> None:
    """A title of exactly the cap is included."""
    title = "t" * MAX_TITLE
    session = VoiceSession(client_id="handset", title=title)
    body = session.voice_body("hi", mode="ptt", idempotency_key="k")
    assert body["title"] == title


def test_title_over_cap_raises() -> None:
    """Over-cap titles refuse and do not echo the title."""
    title = "u" * (MAX_TITLE + 1)
    session = VoiceSession(client_id="handset", title=title)
    with pytest.raises(VoiceError) as caught:
        session.voice_body("hi", mode="ptt")
    assert caught.value.kind == "TITLE_TOO_LONG"
    assert title not in caught.value.detail
    assert title not in str(caught.value)


def test_note_reply_stores_spoken_session_and_brain() -> None:
    """A reply string for session, spoken, and brain is remembered."""
    session = VoiceSession(client_id="handset")
    session.note_reply(
        {
            "session_id": "s1",
            "spoken": "done",
            "reply": "ignored when spoken is a string",
            "brain": "grok",
        }
    )
    assert session.session_id == "s1"
    assert session.last_spoken == "done"
    assert session.last_brain == "grok"


def test_note_reply_falls_back_to_reply() -> None:
    """``reply`` is stored only when ``spoken`` is not a string."""
    session = VoiceSession(client_id="handset", last_spoken="old", last_brain="old")
    session.note_reply({"reply": "from-reply", "brain": 3, "session_id": None})
    assert session.last_spoken == "from-reply"
    assert session.last_brain == "old"
    assert session.session_id is None


def test_note_reply_empty_spoken_does_not_fall_through() -> None:
    """An empty ``spoken`` string is still a string, so ``reply`` is not used."""
    session = VoiceSession(client_id="handset", last_spoken="old")
    session.note_reply({"spoken": "", "reply": "fallback"})
    assert session.last_spoken == ""


def test_note_reply_ignores_non_strings() -> None:
    """Non-string reply fields do not clobber the session."""
    session = VoiceSession(
        client_id="handset",
        session_id="keep",
        last_spoken="keep",
        last_brain="keep",
    )
    session.note_reply(
        {"session_id": 1, "spoken": ["x"], "reply": {"a": 1}, "brain": True}
    )
    assert session.session_id == "keep"
    assert session.last_spoken == "keep"
    assert session.last_brain == "keep"


def test_note_reply_stores_blank_strings() -> None:
    """Blank string fields are stored, which drops the id on the next body."""
    session = VoiceSession(client_id="handset", session_id="sid", last_brain="grok")
    session.note_reply({"session_id": "", "brain": ""})
    assert session.session_id == ""
    assert session.last_brain == ""
    body = session.voice_body("hi", mode="ptt", idempotency_key="k")
    assert "session_id" not in body
