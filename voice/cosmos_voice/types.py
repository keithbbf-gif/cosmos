"""Shared records for the voice module.

Other modules import these names. They do not invent a second copy of the
same fields. Core remains the authority for a spoken turn. These records
are the client-side view of that turn.
"""

from __future__ import annotations

from dataclasses import dataclass, field

OWNERS = ("phone", "desktop", "none")
MODES = ("off", "ptt", "tap", "wake", "follow")
KNOWN_KINDS = (
    "voice_session",
    "device",
    "notifications",
    "sms",
    "calls",
    "contacts",
    "calendar",
    "pcm",
)
PCM_INLINE = ("bytes", "pcm", "data", "b64")
MAX_TRANSCRIPT = 4000
MAX_TITLE = 200
VOICE_READ_TIMEOUT_S = 70.0
FAST_TIMEOUT_S = 8.0
FOLLOW_WINDOW_S = 10.0
DEDUPE_WINDOW_S = 15.0
OWNER_TTL_S = 30.0

WAKE_WORDS = ("hey cosmos", "cosmos")


@dataclass(frozen=True)
class HttpResponse:
    """One HTTP result. ``body`` is a JSON object, or empty when the peer sent none."""

    status: int
    body: dict[str, object]


@dataclass
class VoiceSessionState:
    """The handset carries the session id. The id, not the phone, holds the conversation."""

    client_id: str
    build: str = "cosmos-voice"
    stream: str = ""
    title: str = "voice session"
    session_id: str | None = None
    last_spoken: str = ""
    last_brain: str = ""


@dataclass(frozen=True)
class ModeDecision:
    """Whether this utterance is allowed to leave the phone."""

    accepted: bool
    transcript: str
    kind: str
    mode: str


@dataclass(frozen=True)
class PullPlan:
    """What the thin phone may do with one pull ticket."""

    play_tts: bool
    capture: bool
    fight_bluetooth: bool
    core_kind: str
    audio_owner: str


@dataclass
class TurnResult:
    """What one desktop or phone turn did. ``raw`` is the Core body, already redacted."""

    ok: bool
    kind: str
    spoken: str
    session_id: str | None
    needs_confirm: bool
    confirm_id: str
    raw: dict[str, object] = field(default_factory=dict)
