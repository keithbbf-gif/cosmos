"""Session options. Defaults match the xAI speech-to-speech guide (2026-10-01).

Push-to-talk and half-duplex exist so a noisy room can opt in. Both are off.
A normal session never requires a Send press or a held key.
"""

from __future__ import annotations

from dataclasses import dataclass, field

PINNED_MODEL = "grok-voice-think-fast-2.0"
"""Versioned voice model. ``grok-voice-latest`` is only an alias."""

SAMPLE_RATE = 24000
FRAME_MS = 20
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000  # 480
FRAME_BYTES = FRAME_SAMPLES * 2

# Server VAD knobs published by xAI. silence_duration_ms has no published
# default; 500 ms matches the OpenAI server_vad hangover and the Gemini
# recommended band (500-800). threshold 0.85 and prefix 333 are xAI defaults.
VAD_THRESHOLD = 0.85
SILENCE_MS = 500
PREFIX_PADDING_MS = 333

SPOKEN_MAX = 320
"""Same spoken cap as cosmos_voice.SPOKEN_MAX / cosmos_voice_hardening."""

MAX_TRANSCRIPT = 4000
SESSION_HARD_CAP_S = 120 * 60  # xAI max session duration
DEFAULT_SESSION_S = 30 * 60

VOICES = ("eve", "ara", "rex", "sal", "leo")
RAILS = ("auto", "xai", "cascade", "local")


def trim_spoken(answer: str, cap: int = SPOKEN_MAX) -> str:
    """Whitespace-collapse and cut on a word boundary. Mirrors cosmos_voice._spoken."""

    flat = " ".join(answer.split())
    if len(flat) <= cap:
        return flat
    cut = flat[:cap]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut + " ..."


@dataclass
class VoiceConfig:
    """Every knob a desktop runner, phone gateway, or plugin host can set."""

    rail: str = "auto"
    model: str = PINNED_MODEL
    voice: str = "eve"
    sample_rate: int = SAMPLE_RATE
    frame_ms: int = FRAME_MS
    vad_threshold: float = VAD_THRESHOLD
    local_rms: float = 0.02
    silence_ms: int = SILENCE_MS
    prefix_padding_ms: int = PREFIX_PADDING_MS
    speed: float = 1.0
    language: str = "en"
    keyterms: tuple[str, ...] = ()
    push_to_talk: bool = False
    ptt_held: bool = False
    barge_in: bool = True
    mute: bool = False
    captions: bool = True
    half_duplex: bool = False
    max_session_s: int = DEFAULT_SESSION_S
    reasoning_effort: str = "high"
    instructions: str = (
        "You are COSMOS speaking on Keith's machine. "
        "Talk in short plain sentences. No markdown. "
        "Never run submit or session changes until he confirms out loud. "
        "Destructive requests are refused."
    )
    replace: dict[str, str] = field(default_factory=dict)
    input_device: str | None = None
    output_device: str | None = None
    spend_ceiling_usd: float | None = None
    api_key_env: str = "XAI_API_KEY"
    base_url: str = "https://api.x.ai/v1"

    def __post_init__(self) -> None:
        if self.rail not in RAILS:
            raise ValueError(f"rail must be one of {RAILS}")
        if not 0.1 <= self.vad_threshold <= 0.9:
            raise ValueError("vad_threshold must be inside 0.1..0.9")
        if not 0 <= self.silence_ms <= 10_000:
            raise ValueError("silence_ms must be inside 0..10000")
        if not 0 <= self.prefix_padding_ms <= 10_000:
            raise ValueError("prefix_padding_ms must be inside 0..10000")
        if not 0.7 <= self.speed <= 1.5:
            raise ValueError("speed must be inside 0.7..1.5")
        if self.reasoning_effort not in {"high", "none"}:
            raise ValueError("reasoning_effort must be 'high' or 'none'")
        if self.max_session_s < 1 or self.max_session_s > SESSION_HARD_CAP_S:
            raise ValueError("max_session_s must be 1..7200")
        if self.sample_rate not in {8000, 16000, 22050, 24000, 32000, 44100, 48000}:
            raise ValueError("sample_rate is not a supported PCM rate")
        self.keyterms = tuple(self.keyterms)
        if len(self.keyterms) > 100 or any(len(term) > 50 for term in self.keyterms):
            raise ValueError("keyterms: at most 100 terms, 50 characters each")

    @property
    def frame_samples(self) -> int:
        return self.sample_rate * self.frame_ms // 1000

    @property
    def frame_bytes(self) -> int:
        return self.frame_samples * 2

    @property
    def realtime_url(self) -> str:
        return f"wss://api.x.ai/v1/realtime?model={self.model}"
