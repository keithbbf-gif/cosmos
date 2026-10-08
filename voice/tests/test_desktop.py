"""Desktop loop tests. No device and no socket."""

from __future__ import annotations

from typing import cast

from cosmos_voice.confirm import ConfirmGate
from cosmos_voice.control import ControlView
from cosmos_voice.desktop import DesktopLoop, NullEngine, ScriptEngine
from cosmos_voice.modes import ModeMachine
from cosmos_voice.owner import AudioOwner
from cosmos_voice.session import VoiceSession
from cosmos_voice.types import ModeDecision


class _Mouth:
    """Records speak_turn and returns a fixed body."""

    def __init__(self, body: dict[str, object]) -> None:
        """Store the body the mouth will return."""
        self._body = body
        self.calls: list[tuple[str, str]] = []

    def speak_turn(
        self,
        transcript: str,
        session: VoiceSession,
        *,
        confirm_id: str = "",
    ) -> dict[str, object]:
        """Record the call and return the fixed body."""
        _ = session
        self.calls.append((transcript, confirm_id))
        return self._body


class _Session:
    """Just enough session for the loop: an id and stored replies."""

    def __init__(self) -> None:
        """Start from a known session id."""
        self.session_id: str | None = "sess-1"
        self.replies: list[dict[str, object]] = []

    def note_reply(self, body: dict[str, object]) -> None:
        """Remember the body. A string session id on it replaces ours."""
        found = body.get("session_id")
        if isinstance(found, str):
            self.session_id = found
        self.replies.append(body)


class _Gate:
    """Confirm double. Reject and the phrase id are injected."""

    def __init__(self, *, phrase_id: str | None = None, reject: bool = False) -> None:
        """Store the scripted phrase id and reject flag."""
        self._phrase_id = phrase_id
        self._reject = reject
        self.seen: list[dict[str, object]] = []

    def observe(self, body: dict[str, object]) -> str | None:
        """Remember the body and return a string confirm id when present."""
        self.seen.append(body)
        found = body.get("confirm_id")
        if isinstance(found, str):
            return found
        return None

    def pending(self) -> str | None:
        """Return the scripted phrase id."""
        return self._phrase_id

    def accept_phrase(self, transcript: str) -> str | None:
        """Return the scripted phrase id. The words are not inspected."""
        _ = transcript
        return self._phrase_id

    def reject_phrase(self, transcript: str) -> bool:
        """Return the scripted reject flag."""
        _ = transcript
        return self._reject


class _Owner:
    """Audio-owner double with injected capture, playback, and current holder."""

    def __init__(self, *, capture: bool, playback: bool, who: str = "desktop") -> None:
        """Store the scripted lease answers."""
        self._capture = capture
        self._playback = playback
        self._who = who

    def claim(self, who: str) -> None:
        """Remember a claim. The loop itself does not call this."""
        self._who = who

    def allows_capture(self, who: str) -> bool:
        """True when capture was injected and the caller is desktop."""
        return self._capture and who == "desktop"

    def allows_playback(self, who: str) -> bool:
        """True when playback was injected and the caller is desktop."""
        return self._playback and who == "desktop"

    def current(self) -> str:
        """Return the scripted holder."""
        return self._who


class _Control:
    """Control double. The flag is the whole poll."""

    def __init__(self, flag: bool) -> None:
        """Store whether the loop should see a block."""
        self._flag = flag

    def blocked(self) -> tuple[bool, str]:
        """Return the scripted block and a short reason."""
        if self._flag:
            return True, "pause"
        return False, ""


class _Modes:
    """Mode double. Strips one wake prefix so the mouth sees decision text."""

    def __init__(self) -> None:
        """Start with no accepts and no spoken notes."""
        self.accepted: list[str] = []
        self.spoken_at: list[float] = []

    def accept(
        self,
        transcript: str,
        *,
        held: bool,
        tapped: bool,
        mode: str,
        now: float,
    ) -> ModeDecision:
        """Accept the line. A leading wake prefix is removed from the result."""
        _ = (held, tapped, now)
        self.accepted.append(transcript)
        prefix = "hey cosmos "
        cleaned = transcript[len(prefix) :] if transcript.startswith(prefix) else transcript
        return ModeDecision(accepted=True, transcript=cleaned, kind="ok", mode=mode)

    def note_spoken(self, now: float) -> None:
        """Record the clock of a line that was actually played."""
        self.spoken_at.append(now)


def _loop(
    mouth: _Mouth,
    *,
    blocked: bool = False,
    capture: bool = True,
    playback: bool = True,
    who: str = "desktop",
    phrase_id: str | None = None,
    reject: bool = False,
) -> tuple[DesktopLoop, NullEngine, _Modes, _Session, _Gate]:
    """Build a loop around fakes. The engine is the dry null engine."""
    session = _Session()
    gate = _Gate(phrase_id=phrase_id, reject=reject)
    owner = _Owner(capture=capture, playback=playback, who=who)
    control = _Control(blocked)
    ear = NullEngine()
    modes = _Modes()
    loop = DesktopLoop(
        mouth,
        cast(VoiceSession, session),
        cast(ConfirmGate, gate),
        cast(AudioOwner, owner),
        cast(ControlView, control),
        ear,
        cast(ModeMachine, modes),
    )
    return loop, ear, modes, session, gate


def test_blocked_skips_mouth() -> None:
    """A blocked control returns CONTROL_BLOCKED and does not call the mouth."""
    mouth = _Mouth({"spoken": "nope"})
    loop, ear, modes, session, gate = _loop(mouth, blocked=True)
    result = loop.once(transcript="hello", now=1.0)
    assert mouth.calls == []
    assert modes.accepted == []
    assert ear.spoken == []
    assert modes.spoken_at == []
    assert gate.seen == []
    assert session.replies == []
    assert result.ok is False
    assert result.kind == "CONTROL_BLOCKED"
    assert result.spoken == ""
    assert result.needs_confirm is False
    assert result.confirm_id == ""
    assert result.session_id == "sess-1"
    assert result.raw == {}


def test_needs_confirm_does_not_speak() -> None:
    """A confirm ask is stored and not played."""
    body: dict[str, object] = {
        "needs_confirm": True,
        "spoken": "Say yes.",
        "confirm_id": "c1",
    }
    mouth = _Mouth(body)
    loop, ear, modes, session, gate = _loop(mouth)
    result = loop.once(transcript="turn on the oven", now=2.0)
    assert mouth.calls == [("turn on the oven", "")]
    assert ear.spoken == []
    assert modes.spoken_at == []
    assert gate.seen == [body]
    assert session.replies == [body]
    assert result.ok is True
    assert result.kind == "needs_confirm"
    assert result.needs_confirm is True
    assert result.spoken == "Say yes."
    assert result.confirm_id == "c1"
    assert result.session_id == "sess-1"
    assert result.raw == body


def test_playback_speaks() -> None:
    """An allowed turn speaks when desktop may play audio."""
    body: dict[str, object] = {"spoken": "hello", "confirm_id": "from-core"}
    mouth = _Mouth(body)
    loop, ear, modes, session, gate = _loop(mouth, phrase_id="cid-9")
    result = loop.once(transcript="hey cosmos hello there", now=4.0)
    assert mouth.calls == [("hello there", "cid-9")]
    assert ear.spoken == ["hello"]
    assert modes.spoken_at == [4.0]
    assert gate.seen == [body]
    assert session.replies == [body]
    assert result.ok is True
    assert result.kind == "spoken"
    assert result.spoken == "hello"
    assert result.needs_confirm is False
    assert result.confirm_id == "from-core"
    assert result.session_id == "sess-1"
    assert result.raw == body


def test_engines_are_dry() -> None:
    """Null hears nothing. Script yields the next line and records speech."""
    mute = NullEngine()
    assert mute.transcribe(b"pcm") == ""
    assert mute.capture(1.0) == b""
    assert mute.devices() == ["null"]
    mute.speak("nope")
    assert mute.spoken == ["nope"]
    script = ScriptEngine(["one", "two"])
    assert script.transcribe(b"") == "one"
    assert script.transcribe(b"") == "two"
    assert script.transcribe(b"") == ""
    assert script.capture(0.5) == b"pcm"
    assert script.devices() == ["script"]
    script.speak("back")
    assert script.spoken == ["back"]
