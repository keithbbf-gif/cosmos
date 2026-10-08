"""Voice-mode descriptors and session states for COSMOS.

A session plan names a later recording. This module does not open an audio device.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from cosmos_hermes import Refuse, bound_bytes, bound_int, bound_text, const_eq, secret_shape

SCHEMA = "cosmos-hermes-voice_mode/1"
AUDIO_CAP = 1_000_000
TRANSCRIPT_CAP = 4_000
SILENCE_THRESHOLD = 200
SILENCE_DURATION_MS = 3_000
SPEECH_CONFIRM_MS = 300
DIP_TOLERANCE_MS = 200
NO_SPEECH_MS = 15_000
MAX_RECORDING_MS = 120_000
SILENT_CYCLE_LIMIT = 3
BARGE_GRACE_MS = 500
MIN_SENTENCE_CHARS = 20
RMS_MAX = 32_767
INTERRUPT_NOTE = "spoken reply was cut off"
_CLOCK_MAX = 4_000_000_000_000
_NAME_MAX = 128

_STT_OPEN = frozenset({"local"})
_STT_KEYED = frozenset({"groq", "openai", "mistral", "xai"})
_STT = _STT_OPEN | _STT_KEYED
_TTS_OPEN = frozenset({"edge", "neutts"})
_TTS_KEYED = frozenset(
    {"elevenlabs", "openai", "minimax", "mistral", "gemini", "xai", "kittentts", "piper"}
)
_TTS = _TTS_OPEN | _TTS_KEYED
_MODES = frozenset({"chained", "reply"})
_CAPTURES = frozenset({"push-to-talk", "continuous"})

_CRED = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SESSION_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_RECORD_KEY = re.compile(r"^(?:ctrl|alt|shift)(?:\+(?:ctrl|alt|shift))*\+[a-z0-9]{1,12}$")

_PUNCT_CHARS = ".,!?;:\"'`~()[]{}<>/\\|_@#%^&*+=\u2014\u2013\u2026\u00a1\u00bf"
_PUNCT_TABLE = str.maketrans({ord(ch): " " for ch in _PUNCT_CHARS})
_THINK_CLOSED = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_THINK_OPEN = re.compile(r"<think>.*", re.DOTALL | re.IGNORECASE)
_FENCE_CLOSED = re.compile(r"```.*?```", re.DOTALL)
_FENCE_OPEN = re.compile(r"```.*", re.DOTALL)
_MARKDOWN = re.compile(r"[*_#>`\[\]]+")
_EMOJI = re.compile("[\U0001f000-\U0001faff\u2600-\u27bf]+")


def _norm(text: str) -> str:
    return " ".join(text.casefold().translate(_PUNCT_TABLE).split())


_HALLUCINATION_RAW = (
    "thank you for watching",
    "thanks for watching",
    "thank you for listening",
    "thanks for listening",
    "thank you for watching this video",
    "thanks for watching this video",
    "please subscribe",
    "subscribe",
    "like and subscribe",
    "please like and subscribe",
    "don't forget to subscribe",
    "see you next time",
    "see you in the next video",
    "i'll see you next time",
    "subtitles by the amara.org community",
    "please subscribe to my channel",
    "hit the subscribe button",
    "like comment and subscribe",
    "thanks for watching and don't forget to subscribe",
)
_HALLUCINATIONS = frozenset(_norm(item) for item in _HALLUCINATION_RAW)


def _clock(now_ms: object) -> int:
    return bound_int(now_ms, 0, _CLOCK_MAX)


def _flag(value: object) -> bool:
    if not isinstance(value, bool):
        raise Refuse("BAD_FLAG")
    return value


def _cap(requested: object, policy: int) -> tuple[int, int]:
    """Apply the policy cap. A higher request is stored and ignored."""
    if isinstance(requested, bool) or not isinstance(requested, int) or requested < 1:
        return policy, policy
    applied = policy if requested > policy else requested
    return applied, requested


def _audit_cap(applied: object, requested: object, policy: int) -> None:
    if type(applied) is not int or type(requested) is not int:
        raise Refuse("BAD_PLAN")
    if applied < 1 or requested < 1 or applied > policy:
        raise Refuse("BAD_PLAN")
    expected = policy if requested > policy else requested
    if applied != expected:
        raise Refuse("BAD_PLAN")


def _choice(value: object, choices: frozenset[str]) -> str:
    if not isinstance(value, str):
        raise Refuse("UNKNOWN_PROVIDER")
    text = bound_text(value, 32)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text not in choices:
        raise Refuse("UNKNOWN_PROVIDER")
    return text


def _mode_name(value: object) -> str:
    if not isinstance(value, str):
        raise Refuse("UNKNOWN_MODE")
    text = bound_text(value, 32)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text not in _MODES:
        raise Refuse("UNKNOWN_MODE")
    return text


def _capture_name(value: object) -> str:
    if not isinstance(value, str):
        raise Refuse("UNKNOWN_CAPTURE")
    text = bound_text(value, 32)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text not in _CAPTURES:
        raise Refuse("UNKNOWN_CAPTURE")
    return text


def _credential(value: object, required: bool) -> str:
    if not isinstance(value, str):
        raise Refuse("NOT_TEXT")
    if value == "":
        if required:
            raise Refuse("MISSING_CREDENTIAL")
        return ""
    text = bound_text(value, _NAME_MAX)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _CRED.fullmatch(text) is None:
        raise Refuse("BAD_CREDENTIAL")
    return text


def _session_name(value: object) -> str:
    text = bound_text(value, _NAME_MAX)
    if secret_shape(text):
        raise Refuse("SECRET")
    if ".." in text or _SESSION_NAME.fullmatch(text) is None:
        raise Refuse("BAD_SESSION")
    return text


def _record_key(value: object) -> str:
    text = bound_text(value, 32)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _RECORD_KEY.fullmatch(text) is None:
        raise Refuse("BAD_KEY")
    return text


def _speakers(allowed: object) -> tuple[str, ...]:
    if allowed is None:
        return ("local",)
    if not isinstance(allowed, tuple):
        raise Refuse("BAD_ALLOW")
    if len(allowed) == 0:
        raise Refuse("EMPTY_ALLOW")
    found: list[str] = []
    seen: set[str] = set()
    for item in allowed:
        name = bound_text(item, _NAME_MAX)
        if name.strip() == "":
            raise Refuse("NOT_ALLOWED")
        if secret_shape(name):
            raise Refuse("SECRET")
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        found.append(name)
    return tuple(found)


def _phrases(raw: object) -> tuple[str, ...]:
    if raw is None:
        return ("stop",)
    if not isinstance(raw, tuple):
        raise Refuse("BAD_PHRASE")
    found: list[str] = []
    seen: set[str] = set()
    for item in raw:
        text = bound_text(item, _NAME_MAX)
        if secret_shape(text):
            raise Refuse("SECRET")
        norm = _norm(text)
        if norm == "":
            raise Refuse("BAD_PHRASE")
        if norm in seen:
            raise Refuse("DUPLICATE")
        seen.add(norm)
        found.append(norm)
    return tuple(found)


def _repetitive(norm: str) -> bool:
    tokens = norm.split()
    count = len(tokens)
    if count >= 4 and all(token == tokens[0] for token in tokens):
        return True
    if count >= 6 and count % 2 == 0:
        left = tokens[0]
        right = tokens[1]
        return all(tokens[index] == left and tokens[index + 1] == right for index in range(0, count, 2))
    return False


def _classify(text: str, phrases: tuple[str, ...]) -> str:
    if text.strip() == "":
        return "silence"
    norm = _norm(text)
    if norm == "":
        return "silence"
    for phrase in phrases:
        if const_eq(norm, phrase):
            return "stop"
    if norm in _HALLUCINATIONS or _repetitive(norm):
        return "hallucination"
    return "speech"


def _strip_spoken(text: str) -> str:
    cleaned = _THINK_CLOSED.sub(" ", text)
    cleaned = _THINK_OPEN.sub(" ", cleaned)
    cleaned = _FENCE_CLOSED.sub(" ", cleaned)
    cleaned = _FENCE_OPEN.sub(" ", cleaned)
    cleaned = _MARKDOWN.sub(" ", cleaned)
    cleaned = _EMOJI.sub(" ", cleaned)
    return " ".join(cleaned.split())


def _sentences(cleaned: str, minimum: int) -> tuple[str, ...]:
    if cleaned == "" or _norm(cleaned) == "":
        raise Refuse("EMPTY")
    parts: list[str] = []
    buf: list[str] = []
    count = 0
    for ch in cleaned:
        buf.append(ch)
        count += 1
        if ch in ".!?" and count >= minimum:
            parts.append("".join(buf).strip())
            buf = []
            count = 0
    tail = "".join(buf).strip()
    if tail:
        if parts and len(tail) < minimum:
            parts[-1] = f"{parts[-1]} {tail}"
        else:
            parts.append(tail)
    if not parts:
        raise Refuse("EMPTY")
    return tuple(parts)


def _match_speaker(speaker: object, allowed: dict[str, str]) -> str:
    name = bound_text(speaker, _NAME_MAX)
    if name.strip() == "":
        raise Refuse("NOT_ALLOWED")
    if secret_shape(name):
        raise Refuse("SECRET")
    found = allowed.get(name)
    if found is None:
        raise Refuse("NOT_ALLOWED")
    return found


@dataclass(frozen=True, slots=True)
class VoicePolicy:
    """Caps and timing the caller cannot raise."""

    audio_cap: int
    audio_cap_requested: int
    transcript_cap: int
    transcript_cap_requested: int
    silence_threshold: int
    silence_duration_ms: int
    speech_confirm_ms: int
    dip_tolerance_ms: int
    no_speech_ms: int
    max_recording_ms: int
    silent_cycle_limit: int
    barge: bool
    barge_grace_ms: int
    min_sentence_chars: int
    stop_phrases: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class VoiceStatus:
    """Observable session record. Credential ids are not on this record."""

    schema: str
    state: str
    enabled: bool
    mode: str
    tts: bool
    stt_provider: str
    tts_provider: str
    allowed: tuple[str, ...]
    capture: str
    interrupted: bool
    silent_cycles: int
    audio_bytes: int
    audio_cap: int
    audio_cap_requested: int
    transcript_cap: int
    transcript_cap_requested: int
    speech_confirmed: bool
    opens_device: bool


@dataclass(frozen=True, slots=True)
class AudioTick:
    """One accepted chunk. The bytes themselves are not retained."""

    accepted: int
    total_bytes: int
    state: str
    speaker: str
    speech_confirmed: bool
    end_reason: str
    silent_cycles: int
    capture: str
    opens_device: bool


@dataclass(frozen=True, slots=True)
class TranscriptResult:
    """Bounded transcript plus the session decision."""

    text: str
    kind: str
    state: str
    note: str
    to_agent: bool
    silent_cycles: int


@dataclass(frozen=True, slots=True)
class SpeechPlan:
    """Sentence plan for a later player. This module synthesizes no audio."""

    sentences: tuple[str, ...]
    state: str
    interrupted: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionPlan:
    """Frozen recording descriptor. Building it does not open a device."""

    schema: str
    session: str
    capture: str
    record_key: str
    mode: str
    stt_provider: str
    tts: bool
    tts_provider: str
    credential_id: str
    allowed: tuple[str, ...]
    beep: bool
    device_requested: bool
    opens_device: bool
    records: bool
    audio_cap: int
    audio_cap_requested: int
    transcript_cap: int
    transcript_cap_requested: int
    silence_threshold: int
    silence_duration_ms: int
    speech_confirm_ms: int
    dip_tolerance_ms: int
    no_speech_ms: int
    max_recording_ms: int
    silent_cycle_limit: int
    issued_ms: int

    def __post_init__(self) -> None:
        """Reject a record that opens a device or breaks the policy caps."""
        if self.schema != SCHEMA:
            raise Refuse("BAD_PLAN")
        if type(self.opens_device) is not bool or type(self.records) is not bool:
            raise Refuse("BAD_FLAG")
        if self.opens_device or self.records:
            raise Refuse("NO_DEVICE")
        if type(self.beep) is not bool or type(self.device_requested) is not bool or type(self.tts) is not bool:
            raise Refuse("BAD_FLAG")
        _session_name(self.session)
        _record_key(self.record_key)
        _mode_name(self.mode)
        _capture_name(self.capture)
        stt_name = _choice(self.stt_provider, _STT)
        if self.tts:
            tts_name = _choice(self.tts_provider, _TTS)
        elif self.tts_provider != "":
            raise Refuse("BAD_PLAN")
        else:
            tts_name = ""
        needs = stt_name in _STT_KEYED or tts_name in _TTS_KEYED
        cred = _credential(self.credential_id, needs)
        if cred != self.credential_id:
            raise Refuse("BAD_PLAN")
        speakers = _speakers(self.allowed)
        if speakers != self.allowed:
            raise Refuse("BAD_PLAN")
        _audit_cap(self.audio_cap, self.audio_cap_requested, AUDIO_CAP)
        _audit_cap(self.transcript_cap, self.transcript_cap_requested, TRANSCRIPT_CAP)
        if (
            self.silence_threshold != SILENCE_THRESHOLD
            or self.silence_duration_ms != SILENCE_DURATION_MS
            or self.speech_confirm_ms != SPEECH_CONFIRM_MS
            or self.dip_tolerance_ms != DIP_TOLERANCE_MS
            or self.no_speech_ms != NO_SPEECH_MS
            or self.max_recording_ms != MAX_RECORDING_MS
            or self.silent_cycle_limit != SILENT_CYCLE_LIMIT
        ):
            raise Refuse("BAD_PLAN")
        _clock(self.issued_ms)

    def __repr__(self) -> str:
        present = self.credential_id != ""
        return (
            f"SessionPlan(session={self.session!r}, capture={self.capture!r}, "
            f"mode={self.mode!r}, stt_provider={self.stt_provider!r}, "
            f"credential_set={present}, opens_device={self.opens_device}, "
            f"records={self.records})"
        )


class VoiceSession:
    """Idle, listening, and speaking. Disabled until enable()."""

    __slots__ = (
        "_policy",
        "_enabled",
        "_state",
        "_mode",
        "_tts",
        "_stt_provider",
        "_tts_provider",
        "_credential",
        "_allowed",
        "_allowed_index",
        "_capture",
        "_audio_bytes",
        "_speech_ms",
        "_silence_ms",
        "_quiet_ms",
        "_dip_ms",
        "_elapsed_ms",
        "_speech_confirmed",
        "_silent_cycles",
        "_interrupted",
        "_speak_started_ms",
    )

    def __init__(
        self,
        *,
        audio_cap: object = AUDIO_CAP,
        transcript_cap: object = TRANSCRIPT_CAP,
        barge: object = True,
        stop_phrases: object = None,
    ) -> None:
        applied_audio, requested_audio = _cap(audio_cap, AUDIO_CAP)
        applied_text, requested_text = _cap(transcript_cap, TRANSCRIPT_CAP)
        self._policy = VoicePolicy(
            audio_cap=applied_audio,
            audio_cap_requested=requested_audio,
            transcript_cap=applied_text,
            transcript_cap_requested=requested_text,
            silence_threshold=SILENCE_THRESHOLD,
            silence_duration_ms=SILENCE_DURATION_MS,
            speech_confirm_ms=SPEECH_CONFIRM_MS,
            dip_tolerance_ms=DIP_TOLERANCE_MS,
            no_speech_ms=NO_SPEECH_MS,
            max_recording_ms=MAX_RECORDING_MS,
            silent_cycle_limit=SILENT_CYCLE_LIMIT,
            barge=_flag(barge),
            barge_grace_ms=BARGE_GRACE_MS,
            min_sentence_chars=MIN_SENTENCE_CHARS,
            stop_phrases=_phrases(stop_phrases),
        )
        self._enabled = False
        self._state = "idle"
        self._mode = ""
        self._tts = False
        self._stt_provider = ""
        self._tts_provider = ""
        self._credential = ""
        self._allowed: tuple[str, ...] = ()
        self._allowed_index: dict[str, str] = {}
        self._capture = "closed"
        self._audio_bytes = 0
        self._speech_ms = 0
        self._silence_ms = 0
        self._quiet_ms = 0
        self._dip_ms = 0
        self._elapsed_ms = 0
        self._speech_confirmed = False
        self._silent_cycles = 0
        self._interrupted = False
        self._speak_started_ms = 0

    def __repr__(self) -> str:
        return (
            f"VoiceSession(state={self._state!r}, enabled={self._enabled}, "
            f"audio_cap={self._policy.audio_cap}, opens_device=False)"
        )

    @property
    def state(self) -> str:
        return self._state

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def policy(self) -> VoicePolicy:
        return self._policy

    def status(self) -> VoiceStatus:
        """Return the current record. The device stays closed."""
        policy = self._policy
        return VoiceStatus(
            schema=SCHEMA,
            state=self._state,
            enabled=self._enabled,
            mode=self._mode,
            tts=self._tts,
            stt_provider=self._stt_provider,
            tts_provider=self._tts_provider,
            allowed=self._allowed,
            capture=self._capture,
            interrupted=self._interrupted,
            silent_cycles=self._silent_cycles,
            audio_bytes=self._audio_bytes,
            audio_cap=policy.audio_cap,
            audio_cap_requested=policy.audio_cap_requested,
            transcript_cap=policy.transcript_cap,
            transcript_cap_requested=policy.transcript_cap_requested,
            speech_confirmed=self._speech_confirmed,
            opens_device=False,
        )

    def enable(
        self,
        *,
        credential_id: object = "",
        stt_provider: object = "local",
        tts: object = False,
        tts_provider: object = "edge",
        allowed: object = None,
        mode: object = "chained",
        now_ms: object = 0,
    ) -> VoiceStatus:
        """Arm the session. An empty allowlist or an unknown mode refuses."""
        _clock(now_ms)
        mode_name = _mode_name(mode)
        stt_name = _choice(stt_provider, _STT)
        tts_on = _flag(tts)
        tts_name = _choice(tts_provider, _TTS) if tts_on else ""
        needs_key = stt_name in _STT_KEYED or tts_name in _TTS_KEYED
        cred = _credential(credential_id, needs_key)
        speakers = _speakers(allowed)
        if self._state != "idle":
            raise Refuse("WRONG_STATE", self._state)
        self._mode = mode_name
        self._tts = tts_on
        self._stt_provider = stt_name
        self._tts_provider = tts_name
        self._credential = cred
        self._allowed = speakers
        self._allowed_index = {name: name for name in speakers}
        self._enabled = True
        return self.status()

    def disable(self, now_ms: object = 0) -> VoiceStatus:
        """Return to a disabled idle session."""
        _clock(now_ms)
        self._enabled = False
        self._mode = ""
        self._tts = False
        self._stt_provider = ""
        self._tts_provider = ""
        self._credential = ""
        self._allowed = ()
        self._allowed_index = {}
        self._to_idle()
        return self.status()

    def start(self, now_ms: object = 0) -> VoiceStatus:
        """Move idle to listening. No audio device is opened."""
        _clock(now_ms)
        if not self._enabled:
            raise Refuse("DISABLED")
        if self._state != "idle":
            raise Refuse("WRONG_STATE", self._state)
        self._begin_listen(fresh=True)
        return self.status()

    def feed_audio(
        self,
        audio: object,
        *,
        rms: object = 0,
        duration_ms: object = 0,
        speaker: object = "local",
        now_ms: object = 0,
    ) -> AudioTick:
        """Count one caller-supplied chunk. A chunk over the policy cap refuses OVERSIZE."""
        raw = bound_bytes(audio, self._policy.audio_cap)
        _clock(now_ms)
        if not self._enabled:
            raise Refuse("DISABLED")
        if self._state != "listening":
            raise Refuse("WRONG_STATE", self._state)
        if self._capture != "open":
            raise Refuse("CAPTURE_CLOSED")
        speaker_id = _match_speaker(speaker, self._allowed_index)
        level = bound_int(rms, 0, RMS_MAX)
        span = bound_int(duration_ms, 0, self._policy.max_recording_ms)
        if self._audio_bytes + len(raw) > self._policy.audio_cap:
            raise Refuse("OVERSIZE", str(self._policy.audio_cap))
        self._audio_bytes += len(raw)
        end = self._advance_meters(level, span)
        if end == "no_speech":
            self._silent_cycles += 1
            self._audio_bytes = 0
            self._reset_meters()
            if self._silent_cycles >= self._policy.silent_cycle_limit:
                self._to_idle()
                raise Refuse("SILENT_CAP", str(self._policy.silent_cycle_limit))
        elif end != "":
            self._capture = "hold"
        return self._tick(len(raw), speaker_id, end)

    def submit_transcript(self, text: object, now_ms: object = 0) -> TranscriptResult:
        """Bound the transcript, then classify stop, silence, or speech."""
        _clock(now_ms)
        raw = bound_text(text, self._policy.transcript_cap)
        if secret_shape(raw):
            raise Refuse("SECRET")
        if not self._enabled:
            raise Refuse("DISABLED")
        if self._state != "listening":
            raise Refuse("WRONG_STATE", self._state)
        kind = _classify(raw, self._policy.stop_phrases)
        if kind == "silence":
            self._silent_cycles += 1
            self._audio_bytes = 0
            self._reset_meters()
            self._capture = "open"
            if self._silent_cycles >= self._policy.silent_cycle_limit:
                self._to_idle()
                raise Refuse("SILENT_CAP", str(self._policy.silent_cycle_limit))
            return TranscriptResult(
                text=raw,
                kind="silence",
                state=self._state,
                note="",
                to_agent=False,
                silent_cycles=self._silent_cycles,
            )
        if kind == "stop":
            note = INTERRUPT_NOTE if self._interrupted else ""
            self._to_idle()
            return TranscriptResult(
                text=raw,
                kind="stop",
                state=self._state,
                note=note,
                to_agent=False,
                silent_cycles=0,
            )
        if kind == "hallucination":
            self._audio_bytes = 0
            self._reset_meters()
            self._capture = "open"
            return TranscriptResult(
                text=raw,
                kind="hallucination",
                state=self._state,
                note="",
                to_agent=False,
                silent_cycles=self._silent_cycles,
            )
        note = INTERRUPT_NOTE if self._interrupted else ""
        self._interrupted = False
        self._silent_cycles = 0
        self._audio_bytes = 0
        self._reset_meters()
        self._capture = "open"
        self._state = "listening"
        return TranscriptResult(
            text=raw,
            kind="speech",
            state=self._state,
            note=note,
            to_agent=True,
            silent_cycles=0,
        )

    def speak(self, text: object, now_ms: object = 0) -> SpeechPlan:
        """Enter speaking with a sentence plan. No audio is produced."""
        stamp = _clock(now_ms)
        raw = bound_text(text, self._policy.transcript_cap)
        if secret_shape(raw):
            raise Refuse("SECRET")
        if not self._enabled:
            raise Refuse("DISABLED")
        if not self._tts:
            raise Refuse("TTS_OFF")
        if self._state != "listening":
            raise Refuse("WRONG_STATE", self._state)
        sentences = _sentences(_strip_spoken(raw), self._policy.min_sentence_chars)
        self._state = "speaking"
        self._capture = "closed"
        self._audio_bytes = 0
        self._reset_meters()
        self._speak_started_ms = stamp
        return SpeechPlan(
            sentences=sentences,
            state=self._state,
            interrupted=self._interrupted,
        )

    def barge_in(self, now_ms: object = 0) -> VoiceStatus:
        """Cut speaking and return to listening."""
        stamp = _clock(now_ms)
        if self._state != "speaking":
            raise Refuse("WRONG_STATE", self._state)
        if not self._policy.barge:
            raise Refuse("BARGE_DISABLED")
        if stamp > 0 and self._speak_started_ms > 0:
            delta = stamp - self._speak_started_ms
            if delta < 0:
                raise Refuse("OUT_OF_RANGE", "clock")
            if delta < self._policy.barge_grace_ms:
                raise Refuse("BARGE_GRACE")
        self._interrupted = True
        self._begin_listen(fresh=False)
        return self.status()

    def finish_speaking(self, now_ms: object = 0) -> VoiceStatus:
        """Leave speaking. Chained mode listens again. Reply mode returns to idle."""
        _clock(now_ms)
        if self._state != "speaking":
            raise Refuse("WRONG_STATE", self._state)
        if self._mode == "reply":
            self._to_idle()
            return self.status()
        self._begin_listen(fresh=False)
        return self.status()

    def _tick(self, accepted: int, speaker: str, end_reason: str) -> AudioTick:
        return AudioTick(
            accepted=accepted,
            total_bytes=self._audio_bytes,
            state=self._state,
            speaker=speaker,
            speech_confirmed=self._speech_confirmed,
            end_reason=end_reason,
            silent_cycles=self._silent_cycles,
            capture=self._capture,
            opens_device=False,
        )

    def _advance_meters(self, level: int, span: int) -> str:
        if span == 0:
            return ""
        self._elapsed_ms += span
        if level >= self._policy.silence_threshold:
            self._speech_ms += span
            self._dip_ms = 0
            self._silence_ms = 0
            if self._speech_ms >= self._policy.speech_confirm_ms:
                self._speech_confirmed = True
        elif self._speech_confirmed:
            self._silence_ms += span
        elif self._speech_ms > 0:
            self._dip_ms += span
            if self._dip_ms > self._policy.dip_tolerance_ms:
                self._quiet_ms += self._dip_ms
                self._speech_ms = 0
                self._dip_ms = 0
        else:
            self._quiet_ms += span
        if self._elapsed_ms >= self._policy.max_recording_ms:
            return "max_recording"
        if self._speech_confirmed and self._silence_ms >= self._policy.silence_duration_ms:
            return "silence"
        if not self._speech_confirmed and self._elapsed_ms >= self._policy.no_speech_ms:
            return "no_speech"
        return ""

    def _reset_meters(self) -> None:
        self._speech_ms = 0
        self._silence_ms = 0
        self._quiet_ms = 0
        self._dip_ms = 0
        self._elapsed_ms = 0
        self._speech_confirmed = False

    def _begin_listen(self, *, fresh: bool) -> None:
        self._state = "listening"
        self._capture = "open"
        self._audio_bytes = 0
        self._speak_started_ms = 0
        self._reset_meters()
        if fresh:
            self._silent_cycles = 0
            self._interrupted = False

    def _to_idle(self) -> None:
        self._state = "idle"
        self._capture = "closed"
        self._audio_bytes = 0
        self._speak_started_ms = 0
        self._silent_cycles = 0
        self._interrupted = False
        self._reset_meters()


def plan(
    session: object,
    *,
    credential_id: object = "",
    stt_provider: object = "local",
    tts: object = False,
    tts_provider: object = "edge",
    allowed: object = None,
    mode: object = "chained",
    capture: object = "push-to-talk",
    record_key: object = "ctrl+b",
    audio_cap: object = AUDIO_CAP,
    transcript_cap: object = TRANSCRIPT_CAP,
    beep: object = True,
    open_device: object = False,
    now_ms: object = 0,
) -> SessionPlan:
    """Return a push-to-talk or continuous plan. No device is opened."""
    name = _session_name(session)
    issued = _clock(now_ms)
    mode_name = _mode_name(mode)
    capture_name = _capture_name(capture)
    key = _record_key(record_key)
    stt_name = _choice(stt_provider, _STT)
    tts_on = _flag(tts)
    tts_name = _choice(tts_provider, _TTS) if tts_on else ""
    needs_key = stt_name in _STT_KEYED or tts_name in _TTS_KEYED
    cred = _credential(credential_id, needs_key)
    speakers = _speakers(allowed)
    heard = _flag(beep)
    asked_device = _flag(open_device)
    applied_audio, requested_audio = _cap(audio_cap, AUDIO_CAP)
    applied_text, requested_text = _cap(transcript_cap, TRANSCRIPT_CAP)
    return SessionPlan(
        schema=SCHEMA,
        session=name,
        capture=capture_name,
        record_key=key,
        mode=mode_name,
        stt_provider=stt_name,
        tts=tts_on,
        tts_provider=tts_name,
        credential_id=cred,
        allowed=speakers,
        beep=heard,
        device_requested=asked_device,
        opens_device=False,
        records=False,
        audio_cap=applied_audio,
        audio_cap_requested=requested_audio,
        transcript_cap=applied_text,
        transcript_cap_requested=requested_text,
        silence_threshold=SILENCE_THRESHOLD,
        silence_duration_ms=SILENCE_DURATION_MS,
        speech_confirm_ms=SPEECH_CONFIRM_MS,
        dip_tolerance_ms=DIP_TOLERANCE_MS,
        no_speech_ms=NO_SPEECH_MS,
        max_recording_ms=MAX_RECORDING_MS,
        silent_cycle_limit=SILENT_CYCLE_LIMIT,
        issued_ms=issued,
    )


def run(plan_record: object = None) -> None:
    """Refuse to record. No audio device is opened."""
    if type(plan_record) is not SessionPlan:
        raise Refuse("BAD_PLAN")
    if plan_record.opens_device or plan_record.records:
        raise Refuse("NO_DEVICE")
    raise Refuse("NOT_RECORDED")


__all__ = [
    "AUDIO_CAP",
    "BARGE_GRACE_MS",
    "DIP_TOLERANCE_MS",
    "INTERRUPT_NOTE",
    "MAX_RECORDING_MS",
    "MIN_SENTENCE_CHARS",
    "NO_SPEECH_MS",
    "RMS_MAX",
    "SCHEMA",
    "SILENCE_DURATION_MS",
    "SILENCE_THRESHOLD",
    "SILENT_CYCLE_LIMIT",
    "SPEECH_CONFIRM_MS",
    "TRANSCRIPT_CAP",
    "AudioTick",
    "SessionPlan",
    "SpeechPlan",
    "TranscriptResult",
    "VoicePolicy",
    "VoiceSession",
    "VoiceStatus",
    "plan",
    "run",
]
