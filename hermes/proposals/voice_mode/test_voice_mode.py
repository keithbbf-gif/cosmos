"""Voice-mode state machine refusals and the success path."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import NamedTuple

import pytest

from cosmos_hermes import Refuse, secret_shape
from voice_mode import (
    AUDIO_CAP,
    INTERRUPT_NOTE,
    SCHEMA,
    TRANSCRIPT_CAP,
    SessionPlan,
    VoiceSession,
    plan,
    run,
)


def _listen(*, tts: bool = False, mode: str = "chained", barge: bool = True) -> VoiceSession:
    session = VoiceSession(barge=barge)
    session.enable(tts=tts, mode=mode)
    session.start()
    return session


def _spoken() -> str:
    return "This reply is long enough. Another sentence follows it now."


def test_schema_and_initial_state() -> None:
    session = VoiceSession()
    assert SCHEMA == "cosmos-hermes-voice_mode/1"
    assert session.state == "idle"
    assert session.enabled is False
    status = session.status()
    assert status.schema == SCHEMA
    assert status.state == "idle"
    assert status.capture == "closed"
    assert status.opens_device is False
    policy = session.policy
    assert policy.audio_cap == 1_000_000
    assert policy.transcript_cap == 4_000
    assert policy.silence_threshold == 200
    assert policy.silence_duration_ms == 3_000
    assert policy.speech_confirm_ms == 300
    assert policy.no_speech_ms == 15_000
    assert policy.max_recording_ms == 120_000
    assert policy.silent_cycle_limit == 3
    assert policy.barge_grace_ms == 500
    assert policy.min_sentence_chars == 20
    assert policy.stop_phrases == ("stop",)


def test_start_while_disabled() -> None:
    session = VoiceSession()
    with pytest.raises(Refuse) as caught:
        session.start()
    assert caught.value.code == "DISABLED"
    assert session.state == "idle"


def test_enable_then_start_listens() -> None:
    session = VoiceSession()
    armed = session.enable()
    assert armed.enabled is True
    assert armed.state == "idle"
    assert armed.mode == "chained"
    assert armed.stt_provider == "local"
    started = session.start()
    assert started.state == "listening"
    assert session.state == "listening"
    assert started.capture == "open"


def test_feed_audio_oversize_and_boundary() -> None:
    session = _listen()
    with pytest.raises(Refuse) as caught:
        session.feed_audio(b"a" * (AUDIO_CAP + 1))
    assert caught.value.code == "OVERSIZE"
    assert session.status().audio_bytes == 0
    tick = session.feed_audio(b"b" * AUDIO_CAP)
    assert tick.accepted == AUDIO_CAP
    assert tick.total_bytes == AUDIO_CAP
    assert tick.opens_device is False
    with pytest.raises(Refuse) as again:
        session.feed_audio(b"c")
    assert again.value.code == "OVERSIZE"
    assert session.status().audio_bytes == AUDIO_CAP
    assert session.state == "listening"


def test_higher_cap_is_ignored_and_recorded() -> None:
    session = VoiceSession(audio_cap=9_000_000, transcript_cap=50_000)
    assert session.policy.audio_cap == AUDIO_CAP
    assert session.policy.audio_cap_requested == 9_000_000
    assert session.policy.transcript_cap == TRANSCRIPT_CAP
    assert session.policy.transcript_cap_requested == 50_000
    session.enable()
    session.start()
    with pytest.raises(Refuse) as caught:
        session.feed_audio(b"a" * (AUDIO_CAP + 1))
    assert caught.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as text:
        session.submit_transcript("a" * (TRANSCRIPT_CAP + 1))
    assert text.value.code == "OVERSIZE"
    heard = session.submit_transcript("a" * TRANSCRIPT_CAP)
    assert heard.kind == "speech"
    assert heard.to_agent is True


def test_lower_cap_is_honored() -> None:
    session = VoiceSession(audio_cap=32, transcript_cap=8)
    assert session.policy.audio_cap == 32
    assert session.policy.audio_cap_requested == 32
    session.enable()
    session.start()
    session.feed_audio(b"z" * 32)
    with pytest.raises(Refuse) as caught:
        session.feed_audio(b"z")
    assert caught.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as text:
        session.submit_transcript("a" * 9)
    assert text.value.code == "OVERSIZE"


def test_invalid_cap_request_uses_policy() -> None:
    session = VoiceSession(audio_cap=True, transcript_cap=0)
    assert session.policy.audio_cap == AUDIO_CAP
    assert session.policy.audio_cap_requested == AUDIO_CAP
    assert session.policy.transcript_cap == TRANSCRIPT_CAP
    other = VoiceSession(audio_cap=-5, transcript_cap=False)
    assert other.policy.audio_cap == AUDIO_CAP
    assert other.policy.transcript_cap_requested == TRANSCRIPT_CAP


def test_barge_in_from_speaking_listens() -> None:
    session = _listen(tts=True)
    plan = session.speak(_spoken())
    assert session.state == "speaking"
    assert len(plan.sentences) == 2
    assert all(len(part) >= 20 for part in plan.sentences)
    status = session.barge_in()
    assert status.state == "listening"
    assert status.interrupted is True
    assert status.capture == "open"
    assert session.state == "listening"


def test_barge_grace_and_disabled() -> None:
    session = _listen(tts=True)
    session.speak(_spoken(), now_ms=1_000)
    with pytest.raises(Refuse) as early:
        session.barge_in(now_ms=1_499)
    assert early.value.code == "BARGE_GRACE"
    assert session.state == "speaking"
    status = session.barge_in(now_ms=1_500)
    assert status.state == "listening"
    blocked = _listen(tts=True, barge=False)
    blocked.speak(_spoken())
    with pytest.raises(Refuse) as caught:
        blocked.barge_in()
    assert caught.value.code == "BARGE_DISABLED"
    assert blocked.state == "speaking"


def test_barge_clock_going_backwards() -> None:
    session = _listen(tts=True)
    session.speak(_spoken(), now_ms=2_000)
    with pytest.raises(Refuse) as caught:
        session.barge_in(now_ms=1_000)
    assert caught.value.code == "OUT_OF_RANGE"
    assert session.state == "speaking"


def test_submit_transcript_uses_bounds() -> None:
    session = _listen()
    heard = session.submit_transcript("  hello there  ")
    assert heard.text == "  hello there  "
    assert heard.kind == "speech"
    assert heard.to_agent is True
    assert heard.state == "listening"
    with pytest.raises(Refuse) as blank_type:
        session.submit_transcript(b"hello")
    assert blank_type.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        session.submit_transcript("a\x00b")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as huge:
        session.submit_transcript("a" * (TRANSCRIPT_CAP + 1))
    assert huge.value.code == "OVERSIZE"


def test_stop_phrase_is_exact() -> None:
    session = _listen()
    ended = session.submit_transcript("Stop!")
    assert ended.kind == "stop"
    assert ended.to_agent is False
    assert ended.state == "idle"
    assert session.enabled is True
    session.start()
    kept = session.submit_transcript("stop doing that and try again")
    assert kept.kind == "speech"
    assert kept.to_agent is True
    assert session.state == "listening"


def test_custom_stop_list_and_disabled_list() -> None:
    custom = VoiceSession(stop_phrases=("goodbye hermes", "Stop"))
    assert custom.policy.stop_phrases == ("goodbye hermes", "stop")
    custom.enable()
    custom.start()
    ended = custom.submit_transcript("Goodbye, Hermes!")
    assert ended.kind == "stop"
    assert custom.state == "idle"
    open_list = VoiceSession(stop_phrases=())
    assert open_list.policy.stop_phrases == ()
    open_list.enable()
    open_list.start()
    heard = open_list.submit_transcript("stop")
    assert heard.kind == "speech"
    assert heard.to_agent is True


def test_hallucination_filter() -> None:
    session = _listen()
    phantom = session.submit_transcript("Thank you for watching!")
    assert phantom.kind == "hallucination"
    assert phantom.to_agent is False
    assert session.state == "listening"
    please = session.submit_transcript("Please subscribe to my channel!")
    assert please.kind == "hallucination"
    assert please.to_agent is False
    repeated = session.submit_transcript("thank you thank you thank you")
    assert repeated.kind == "hallucination"
    real = session.submit_transcript("thank you")
    assert real.kind == "speech"
    stamps = session.submit_transcript("ha ha ha ha")
    assert stamps.kind == "hallucination"


def test_silent_transcripts_hit_the_cycle_cap() -> None:
    session = _listen()
    first = session.submit_transcript("   ")
    second = session.submit_transcript("\n")
    assert first.kind == "silence"
    assert second.silent_cycles == 2
    assert session.state == "listening"
    with pytest.raises(Refuse) as caught:
        session.submit_transcript("...")
    assert caught.value.code == "SILENT_CAP"
    assert session.state == "idle"
    assert session.enabled is True
    session.start()
    assert session.state == "listening"


def test_no_speech_timeout_hits_the_cycle_cap() -> None:
    session = _listen()
    window = session.policy.no_speech_ms
    first = session.feed_audio(b"q", rms=0, duration_ms=window)
    assert first.end_reason == "no_speech"
    assert first.silent_cycles == 1
    assert session.state == "listening"
    session.feed_audio(b"q", rms=0, duration_ms=window)
    with pytest.raises(Refuse) as caught:
        session.feed_audio(b"q", rms=0, duration_ms=window)
    assert caught.value.code == "SILENT_CAP"
    assert session.state == "idle"
    session.start()
    assert session.state == "listening"


def test_silence_end_closes_capture() -> None:
    session = _listen()
    heard = session.feed_audio(b"wav", rms=200, duration_ms=300)
    assert heard.speech_confirmed is True
    assert heard.end_reason == ""
    closed = session.feed_audio(b"wav", rms=199, duration_ms=3_000)
    assert closed.end_reason == "silence"
    assert closed.capture == "hold"
    with pytest.raises(Refuse) as caught:
        session.feed_audio(b"more")
    assert caught.value.code == "CAPTURE_CLOSED"
    result = session.submit_transcript("what time is it")
    assert result.kind == "speech"
    assert session.status().capture == "open"


def test_dip_before_confirmation_is_tolerated() -> None:
    session = _listen()
    session.feed_audio(b"a", rms=200, duration_ms=200)
    dipped = session.feed_audio(b"a", rms=0, duration_ms=200)
    assert dipped.speech_confirmed is False
    confirmed = session.feed_audio(b"a", rms=250, duration_ms=200)
    assert confirmed.speech_confirmed is True
    reset = _listen()
    reset.feed_audio(b"a", rms=200, duration_ms=200)
    lost = reset.feed_audio(b"a", rms=0, duration_ms=201)
    assert lost.speech_confirmed is False


def test_max_recording_closes_capture() -> None:
    session = _listen()
    tick = session.feed_audio(b"a", rms=200, duration_ms=120_000)
    assert tick.end_reason == "max_recording"
    assert tick.capture == "hold"
    assert session.state == "listening"


def test_feed_while_speaking_is_refused() -> None:
    session = _listen(tts=True)
    session.speak(_spoken())
    with pytest.raises(Refuse) as caught:
        session.feed_audio(b"echo")
    assert caught.value.code == "WRONG_STATE"
    session.barge_in()
    tick = session.feed_audio(bytearray(b"ok"))
    assert tick.accepted == 2
    assert tick.speaker == "local"


def test_finish_speaking_follows_mode() -> None:
    chained = _listen(tts=True)
    chained.speak(_spoken())
    assert chained.finish_speaking().state == "listening"
    reply = _listen(tts=True, mode="reply")
    reply.speak(_spoken())
    done = reply.finish_speaking()
    assert done.state == "idle"
    assert done.enabled is True
    assert reply.start().state == "listening"


def test_unknown_mode_and_provider() -> None:
    session = VoiceSession()
    for mode in ("off", "yolo", "gpt-live"):
        with pytest.raises(Refuse) as caught:
            session.enable(mode=mode)
        assert caught.value.code == "UNKNOWN_MODE"
    assert session.enabled is False
    with pytest.raises(Refuse) as provider:
        session.enable(stt_provider="whisper")
    assert provider.value.code == "UNKNOWN_PROVIDER"
    with pytest.raises(Refuse) as typed:
        session.enable(stt_provider=12)
    assert typed.value.code == "UNKNOWN_PROVIDER"
    with pytest.raises(Refuse) as tts_name:
        session.enable(tts=True, tts_provider="nope")
    assert tts_name.value.code == "UNKNOWN_PROVIDER"


def test_missing_credential_and_keyed_success() -> None:
    session = VoiceSession()
    with pytest.raises(Refuse) as caught:
        session.enable(stt_provider="groq")
    assert caught.value.code == "MISSING_CREDENTIAL"
    assert session.enabled is False
    with pytest.raises(Refuse) as tts_key:
        session.enable(tts=True, tts_provider="elevenlabs")
    assert tts_key.value.code == "MISSING_CREDENTIAL"
    armed = session.enable(stt_provider="openai", credential_id="cred-openai-1", tts=True)
    assert armed.enabled is True
    assert armed.tts_provider == "edge"
    assert "cred-openai-1" not in repr(session)
    assert "cred-openai-1" not in repr(session.status())


def test_secret_shapes_are_refused() -> None:
    samples = (
        "sk-abcdefghijklmnop",
        "Bearer abcdefghijk",
        "api_key=abcdef",
    )
    for raw in samples:
        assert secret_shape(raw)
        session = VoiceSession()
        with pytest.raises(Refuse) as caught:
            session.enable(stt_provider="openai", credential_id=raw)
        assert caught.value.code == "SECRET"
        assert session.enabled is False
        assert raw not in repr(session)
        listening = _listen()
        with pytest.raises(Refuse) as said:
            listening.submit_transcript(f"please use {raw}")
        assert said.value.code == "SECRET"
        assert listening.state == "listening"


def test_allowlist_refuses_empty_and_unknown_speakers() -> None:
    session = VoiceSession()
    with pytest.raises(Refuse) as empty:
        session.enable(allowed=())
    assert empty.value.code == "EMPTY_ALLOW"
    with pytest.raises(Refuse) as shape:
        session.enable(allowed=["local"])
    assert shape.value.code == "BAD_ALLOW"
    with pytest.raises(Refuse) as bad_item:
        session.enable(allowed=(1,))
    assert bad_item.value.code == "NOT_TEXT"
    session.enable(allowed=("ada",))
    session.start()
    tick = session.feed_audio(b"a", speaker="ada")
    assert tick.speaker == "ada"
    with pytest.raises(Refuse) as caught:
        session.feed_audio(b"a", speaker="bob")
    assert caught.value.code == "NOT_ALLOWED"
    with pytest.raises(Refuse) as secret:
        session.feed_audio(b"a", speaker="sk-abcdefghij")
    assert secret.value.code == "SECRET"
    with pytest.raises(Refuse) as blank:
        session.feed_audio(b"a", speaker="  ")
    assert blank.value.code == "NOT_ALLOWED"


def test_wrong_state_matrix() -> None:
    idle = VoiceSession()
    idle.enable()
    with pytest.raises(Refuse) as feed:
        idle.feed_audio(b"a")
    assert feed.value.code == "WRONG_STATE"
    with pytest.raises(Refuse) as said:
        idle.submit_transcript("hello")
    assert said.value.code == "WRONG_STATE"
    with pytest.raises(Refuse) as talk:
        idle.speak(_spoken())
    assert talk.value.code == "TTS_OFF"
    idle.enable(tts=True)
    with pytest.raises(Refuse) as early:
        idle.speak(_spoken())
    assert early.value.code == "WRONG_STATE"
    with pytest.raises(Refuse) as barge:
        idle.barge_in()
    assert barge.value.code == "WRONG_STATE"
    with pytest.raises(Refuse) as done:
        idle.finish_speaking()
    assert done.value.code == "WRONG_STATE"
    idle.start()
    with pytest.raises(Refuse) as again:
        idle.start()
    assert again.value.code == "WRONG_STATE"
    with pytest.raises(Refuse) as retune:
        idle.enable()
    assert retune.value.code == "WRONG_STATE"
    assert idle.state == "listening"


def test_disabled_feed_and_submit() -> None:
    session = VoiceSession()
    with pytest.raises(Refuse) as feed:
        session.feed_audio(b"a")
    assert feed.value.code == "DISABLED"
    with pytest.raises(Refuse) as said:
        session.submit_transcript("hello")
    assert said.value.code == "DISABLED"
    with pytest.raises(Refuse) as talk:
        session.speak("This reply is long enough to speak aloud now.")
    assert talk.value.code == "DISABLED"


def test_bad_construction_flags() -> None:
    with pytest.raises(Refuse) as flag:
        VoiceSession(barge="yes")
    assert flag.value.code == "BAD_FLAG"
    with pytest.raises(Refuse) as phrase:
        VoiceSession(stop_phrases=("...",))
    assert phrase.value.code == "BAD_PHRASE"
    with pytest.raises(Refuse) as shape:
        VoiceSession(stop_phrases="stop")
    assert shape.value.code == "BAD_PHRASE"
    with pytest.raises(Refuse) as secret:
        VoiceSession(stop_phrases=("sk-abcdefghij",))
    assert secret.value.code == "SECRET"
    session = VoiceSession()
    with pytest.raises(Refuse) as tts_flag:
        session.enable(tts="yes")
    assert tts_flag.value.code == "BAD_FLAG"


def test_speak_strips_markdown_and_refuses_empty() -> None:
    session = _listen(tts=True)
    plan = session.speak("**This reply is long enough.** Yes!")
    assert "[" not in plan.sentences[0]
    assert "*" not in plan.sentences[0]
    session.barge_in()
    hidden = session.speak("<think>secret plan</think> This spoken line is certainly long enough.")
    assert "secret" not in hidden.sentences[0]
    assert session.state == "speaking"
    session.barge_in()
    with pytest.raises(Refuse) as caught:
        session.speak("```only a fence```")
    assert caught.value.code == "EMPTY"
    assert session.state == "listening"
    with pytest.raises(Refuse) as memory:
        session.feed_audio(memoryview(b"abcd"))
    assert memory.value.code == "NOT_BYTES"


def test_interrupt_note_rides_the_next_transcript() -> None:
    session = _listen(tts=True)
    session.speak(_spoken())
    session.barge_in()
    heard = session.submit_transcript("continue from there")
    assert heard.note == INTERRUPT_NOTE
    assert heard.to_agent is True
    assert session.status().interrupted is False
    session.speak(_spoken())
    session.barge_in()
    ended = session.submit_transcript("stop")
    assert ended.kind == "stop"
    assert ended.note == INTERRUPT_NOTE
    assert session.state == "idle"


def test_disable_clears_the_session() -> None:
    session = _listen(tts=True)
    session.speak(_spoken())
    status = session.disable()
    assert status.enabled is False
    assert status.state == "idle"
    assert status.mode == ""
    assert status.allowed == ()
    with pytest.raises(Refuse) as caught:
        session.start()
    assert caught.value.code == "DISABLED"
    session.enable(tts=True)
    assert session.start().state == "listening"


def test_meter_and_clock_types() -> None:
    session = _listen()
    with pytest.raises(Refuse) as flag:
        session.feed_audio(b"a", rms=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as high:
        session.feed_audio(b"a", rms=32_768)
    assert high.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as clock:
        session.feed_audio(b"a", now_ms=-1)
    assert clock.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as span:
        session.feed_audio(b"a", duration_ms=120_001)
    assert span.value.code == "OUT_OF_RANGE"
    assert session.status().audio_bytes == 0


def test_same_inputs_match() -> None:
    left = _listen(tts=True)
    right = _listen(tts=True)
    assert left.speak(_spoken()) == right.speak(_spoken())
    assert left.barge_in().state == right.barge_in().state
    assert left.submit_transcript("hello") == right.submit_transcript("hello")


def test_policy_record_is_frozen() -> None:
    session = VoiceSession()
    with pytest.raises(AttributeError):
        setattr(session.policy, "audio_cap", AUDIO_CAP + 1)
    assert session.policy.audio_cap == AUDIO_CAP


def test_submit_before_enable_bounds_first() -> None:
    session = VoiceSession()
    with pytest.raises(Refuse) as caught:
        session.submit_transcript("a\x00")
    assert caught.value.code == "NULL_BYTE"


def test_source_imports_stay_local() -> None:
    source = Path(__file__).with_name("voice_mode.py").read_text(encoding="utf-8")
    banned = ("socket", "subprocess", "threading", "urllib", "requests", "pickle", "sounddevice")
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            for name in banned:
                assert name not in stripped
    assert "exec(" not in source
    assert "eval(" not in source


class _DeskStory(NamedTuple):
    missing: str
    armed: SessionPlan
    keyed: SessionPlan
    blocked: str
    accepted: int
    confirmed: bool
    text: str
    kind: str
    to_agent: bool
    audio_bytes: int
    opens_device: bool


def _ada_desk() -> _DeskStory:
    when = 1_714_433_200_000
    armed = plan(
        "ada-desk",
        capture="push-to-talk",
        record_key="ctrl+b",
        stt_provider="local",
        mode="chained",
        allowed=("ada",),
        open_device=True,
        beep=True,
        now_ms=when,
    )
    with pytest.raises(Refuse) as missing:
        plan(
            "ada-desk",
            capture="push-to-talk",
            stt_provider="groq",
            credential_id="",
            now_ms=when,
        )
    keyed = plan(
        "ada-desk",
        capture="push-to-talk",
        stt_provider="groq",
        credential_id="cred-groq-ada",
        allowed=("ada",),
        now_ms=when,
    )
    with pytest.raises(Refuse) as blocked:
        run(armed)
    session = VoiceSession()
    session.enable(allowed=("ada",), mode="chained", now_ms=when)
    session.start(now_ms=when)
    tick = session.feed_audio(
        b"note",
        rms=240,
        duration_ms=300,
        speaker="ada",
        now_ms=when + 100,
    )
    heard = session.submit_transcript(
        "ada left a note that the porch light is on",
        now_ms=when + 200,
    )
    return _DeskStory(
        missing=missing.value.code,
        armed=armed,
        keyed=keyed,
        blocked=blocked.value.code,
        accepted=tick.accepted,
        confirmed=tick.speech_confirmed,
        text=heard.text,
        kind=heard.kind,
        to_agent=heard.to_agent,
        audio_bytes=session.status().audio_bytes,
        opens_device=session.status().opens_device,
    )


def test_example_voice_mode() -> None:
    first = _ada_desk()
    second = _ada_desk()
    assert first == second
    assert first.missing == "MISSING_CREDENTIAL"
    assert first.armed.session == "ada-desk"
    assert first.armed.capture == "push-to-talk"
    assert first.armed.record_key == "ctrl+b"
    assert first.armed.device_requested is True
    assert first.armed.opens_device is False
    assert first.armed.records is False
    assert first.keyed.credential_id == "cred-groq-ada"
    assert first.keyed.opens_device is False
    assert "cred-groq-ada" not in repr(first.keyed)
    assert "sk-" not in repr(first.keyed)
    assert first.blocked == "NOT_RECORDED"
    assert first.accepted == 4
    assert first.confirmed is True
    assert first.text == "ada left a note that the porch light is on"
    assert first.kind == "speech"
    assert first.to_agent is True
    assert first.audio_bytes == 0
    assert first.opens_device is False


def test_plan_caps_and_run_do_not_record() -> None:
    made = plan("ada-desk", audio_cap=9_000_000, transcript_cap=50_000, open_device=True)
    assert made.audio_cap == AUDIO_CAP
    assert made.audio_cap_requested == 9_000_000
    assert made.transcript_cap == TRANSCRIPT_CAP
    assert made.transcript_cap_requested == 50_000
    assert made.device_requested is True
    assert made.opens_device is False
    assert made.records is False
    small = plan("ada-desk", audio_cap=32, transcript_cap=8)
    assert small.audio_cap == 32
    assert small.audio_cap_requested == 32
    assert small.transcript_cap == 8
    continuous = plan("ada-desk", capture="continuous", record_key="ctrl+shift+b")
    assert continuous.capture == "continuous"
    assert continuous.opens_device is False
    with pytest.raises(Refuse) as once:
        run(continuous)
    assert once.value.code == "NOT_RECORDED"
    with pytest.raises(Refuse) as twice:
        run(continuous)
    assert twice.value.code == "NOT_RECORDED"
    assert continuous.records is False
    with pytest.raises(Refuse) as shape:
        run(VoiceSession())
    assert shape.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as flag:
        plan("ada-desk", open_device="yes")
    assert flag.value.code == "BAD_FLAG"


def test_plan_name_key_and_capture_refuse() -> None:
    with pytest.raises(Refuse) as blank:
        plan(" ")
    assert blank.value.code == "BAD_SESSION"
    with pytest.raises(Refuse) as dotted:
        plan("ada/../desk")
    assert dotted.value.code == "BAD_SESSION"
    with pytest.raises(Refuse) as secret:
        plan("sk-abcdefghij")
    assert secret.value.code == "SECRET"
    with pytest.raises(Refuse) as key:
        plan("ada-desk", record_key="enter")
    assert key.value.code == "BAD_KEY"
    with pytest.raises(Refuse) as capture:
        plan("ada-desk", capture="microphone")
    assert capture.value.code == "UNKNOWN_CAPTURE"
    with pytest.raises(Refuse) as typed:
        plan("ada-desk", capture=12)
    assert typed.value.code == "UNKNOWN_CAPTURE"
    with pytest.raises(Refuse) as missing:
        plan("ada-desk", stt_provider="openai", tts=True, tts_provider="elevenlabs")
    assert missing.value.code == "MISSING_CREDENTIAL"


def test_bad_credential_shape() -> None:
    session = VoiceSession()
    with pytest.raises(Refuse) as blank:
        session.enable(stt_provider="openai", credential_id=" ")
    assert blank.value.code == "BAD_CREDENTIAL"
    assert session.enabled is False
    with pytest.raises(Refuse) as spaced:
        session.enable(stt_provider="openai", credential_id="cred openai")
    assert spaced.value.code == "BAD_CREDENTIAL"
    with pytest.raises(Refuse) as typed:
        plan("ada-desk", stt_provider="groq", credential_id=12)
    assert typed.value.code == "NOT_TEXT"
    armed = session.enable(stt_provider="openai", credential_id="cred-openai-1")
    assert armed.enabled is True
    assert "cred-openai-1" not in repr(session)


def test_duplicate_speaker_and_phrase() -> None:
    with pytest.raises(Refuse) as phrase:
        VoiceSession(stop_phrases=("stop", "Stop!"))
    assert phrase.value.code == "DUPLICATE"
    session = VoiceSession()
    with pytest.raises(Refuse) as speaker:
        session.enable(allowed=("ada", "ada"))
    assert speaker.value.code == "DUPLICATE"
    assert session.enabled is False
    with pytest.raises(Refuse) as planned:
        plan("ada-desk", allowed=("ada", "ada"))
    assert planned.value.code == "DUPLICATE"


def test_forged_plan_refuses() -> None:
    base = plan("ada-desk")
    with pytest.raises(Refuse) as schema:
        replace(base, schema="cosmos-hermes-voice_mode/2")
    assert schema.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as device:
        replace(base, opens_device=True)
    assert device.value.code == "NO_DEVICE"
    with pytest.raises(Refuse) as recorded:
        replace(base, records=True)
    assert recorded.value.code == "NO_DEVICE"
    with pytest.raises(Refuse) as timing:
        replace(base, silence_duration_ms=1)
    assert timing.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as cap:
        replace(base, audio_cap=AUDIO_CAP + 1)
    assert cap.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as keyed:
        replace(base, stt_provider="groq")
    assert keyed.value.code == "MISSING_CREDENTIAL"
    with pytest.raises(Refuse) as secret:
        replace(base, credential_id="sk-abcdefghij")
    assert secret.value.code == "SECRET"
    tampered = plan("ada-desk")
    object.__setattr__(tampered, "opens_device", True)
    with pytest.raises(Refuse) as lied:
        run(tampered)
    assert lied.value.code == "NO_DEVICE"
    assert tampered.records is False
