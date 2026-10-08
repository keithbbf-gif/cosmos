"""Desktop turn loop.

The PC is the heavy ear when it holds the audio lease. This module does not
open a device and does not open a socket. A mouth is injected.
"""

from __future__ import annotations

from typing import Protocol

from cosmos_voice.confirm import ConfirmGate
from cosmos_voice.control import ControlView
from cosmos_voice.modes import ModeMachine
from cosmos_voice.owner import AudioOwner
from cosmos_voice.session import VoiceSession
from cosmos_voice.types import TurnResult


class _Mouth(Protocol):
    """Anything that can take one transcript to Core."""

    def speak_turn(
        self,
        transcript: str,
        session: VoiceSession,
        *,
        confirm_id: str = "",
    ) -> dict[str, object]:
        """Send one turn and return the Core body."""


class _Engine(Protocol):
    """A local ear and speaker. No device is required."""

    def transcribe(self, pcm: bytes) -> str:
        """Turn captured samples into text."""

    def speak(self, text: str) -> None:
        """Play one line, or record it when the engine is dry."""


class NullEngine:
    """An engine that hears nothing and keeps spoken lines in memory."""

    def __init__(self) -> None:
        """Start with an empty spoken log."""
        self.spoken: list[str] = []

    def transcribe(self, pcm: bytes) -> str:
        """Return no words. Samples are ignored."""
        _ = pcm
        return ""

    def speak(self, text: str) -> None:
        """Record the line. Nothing is played."""
        self.spoken.append(text)

    def capture(self, seconds: float) -> bytes:
        """Return no samples. The duration is ignored."""
        _ = seconds
        return b""

    def devices(self) -> list[str]:
        """Name the only device this engine has."""
        return ["null"]


class ScriptEngine:
    """An engine that replays scripted lines and records what it would say."""

    def __init__(self, lines: list[str]) -> None:
        """Copy ``lines``. Later edits to the caller's list are ignored."""
        self._lines = list(lines)
        self.spoken: list[str] = []

    def transcribe(self, pcm: bytes) -> str:
        """Return the next scripted line, or empty when the script is done."""
        _ = pcm
        if not self._lines:
            return ""
        return self._lines.pop(0)

    def speak(self, text: str) -> None:
        """Record the line. Nothing is played."""
        self.spoken.append(text)

    def capture(self, seconds: float) -> bytes:
        """Return a stand-in buffer. No device is opened."""
        _ = seconds
        return b"pcm"

    def devices(self) -> list[str]:
        """Name the script device."""
        return ["script"]


class DesktopLoop:
    """One desktop turn: gates, then the mouth, then playback if allowed."""

    def __init__(
        self,
        mouth: _Mouth,
        session: VoiceSession,
        confirm: ConfirmGate,
        owner: AudioOwner,
        control: ControlView,
        engine: _Engine,
        modes: ModeMachine,
    ) -> None:
        """Bind the mouth, the gates, and the local engine."""
        self._mouth = mouth
        self._session = session
        self._confirm = confirm
        self._owner = owner
        self._control = control
        self._engine = engine
        self._modes = modes

    def once(
        self,
        *,
        transcript: str | None = None,
        pcm: bytes | None = None,
        held: bool = True,
        tapped: bool = False,
        mode: str = "ptt",
        now: float = 0.0,
    ) -> TurnResult:
        """Take one utterance through the gates and, if allowed, the mouth.

        A blocked control, a missing capture lease, or a refused mode does
        not call the mouth. ``needs_confirm`` is not played. Playback runs
        only when this desktop holds the lease and Core returned text.
        """
        if self._control.blocked()[0]:
            return self._stop("CONTROL_BLOCKED")
        if not self._owner.allows_capture("desktop"):
            kind = "AUDIO_NONE" if self._owner.current() == "none" else "AUDIO_BUSY"
            return self._stop(kind)
        heard = transcript
        if heard is None:
            heard = self._engine.transcribe(pcm or b"")
        decision = self._modes.accept(heard, held=held, tapped=tapped, mode=mode, now=now)
        if not decision.accepted:
            return self._stop(decision.kind)
        if self._confirm.reject_phrase(heard):
            return self._stop("cancelled", ok=True, spoken="Cancelled.")
        confirm_id = self._confirm.accept_phrase(heard) or ""
        body = self._mouth.speak_turn(decision.transcript, self._session, confirm_id=confirm_id)
        self._session.note_reply(body)
        self._confirm.observe(body)
        needs = bool(body.get("needs_confirm"))
        spoken = str(body.get("spoken") or body.get("reply") or "")
        found = body.get("confirm_id")
        echoed = found if isinstance(found, str) else ""
        if needs:
            return self._finish(
                kind="needs_confirm",
                spoken=spoken,
                needs_confirm=True,
                confirm_id=echoed,
                raw=body,
            )
        if self._owner.allows_playback("desktop") and spoken:
            self._engine.speak(spoken)
            self._modes.note_spoken(now)
            return self._finish(kind="spoken", spoken=spoken, confirm_id=echoed, raw=body)
        return self._finish(kind="silent", spoken=spoken, confirm_id=echoed, raw=body)

    def _stop(self, kind: str, *, ok: bool = False, spoken: str = "") -> TurnResult:
        """A turn that never reached the mouth."""
        return TurnResult(
            ok=ok,
            kind=kind,
            spoken=spoken,
            session_id=self._session.session_id,
            needs_confirm=False,
            confirm_id="",
        )

    def _finish(
        self,
        *,
        kind: str,
        spoken: str,
        raw: dict[str, object],
        needs_confirm: bool = False,
        confirm_id: str = "",
    ) -> TurnResult:
        """A turn the mouth answered."""
        return TurnResult(
            ok=True,
            kind=kind,
            spoken=spoken,
            session_id=self._session.session_id,
            needs_confirm=needs_confirm,
            confirm_id=confirm_id,
            raw=raw,
        )
