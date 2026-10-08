"""Voice POST bodies and the client-held session id.

Core owns the conversation. This module builds the ``/api/v1/voice`` body
and remembers the reply fields the handset needs for the next turn.
It does not open a socket.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from cosmos_voice.errors import VoiceError
from cosmos_voice.types import MAX_TITLE, MAX_TRANSCRIPT, VoiceSessionState


def new_idempotency_key() -> str:
    """Return a fresh hex idempotency key.

    The value is ``uuid.uuid4().hex`` (32 lowercase hex characters, no dashes).
    Callers send one key per attempt so Core can dedupe a retry.
    """
    return uuid.uuid4().hex


@dataclass
class VoiceSession(VoiceSessionState):
    """One handset session and the body it posts to ``/api/v1/voice``.

    Fields are ``VoiceSessionState``: ``client_id``, ``build``
    (``cosmos-voice``), ``stream``, ``title`` (``voice session``),
    ``session_id``, ``last_spoken``, and ``last_brain``.
    """

    def voice_body(
        self,
        transcript: str,
        *,
        mode: str,
        confirm_id: str = "",
        idempotency_key: str = "",
    ) -> dict[str, object]:
        """Build one voice request body.

        Always includes ``transcript``, ``mode``, ``title``, ``client_id``,
        ``build``, ``stream``, and ``idempotency_key``. A blank
        ``idempotency_key`` is replaced with :func:`new_idempotency_key`.
        ``session_id`` is omitted when it is ``None`` or ``""``.
        ``confirm_id`` is omitted when it is ``""``.

        Raises:
            VoiceError: ``TRANSCRIPT_TOO_LONG`` when ``transcript`` exceeds
                :data:`cosmos_voice.types.MAX_TRANSCRIPT`, or
                ``TITLE_TOO_LONG`` when ``title`` exceeds
                :data:`cosmos_voice.types.MAX_TITLE`.
        """
        if len(transcript) > MAX_TRANSCRIPT:
            raise VoiceError(
                "TRANSCRIPT_TOO_LONG",
                f"len={len(transcript)} max={MAX_TRANSCRIPT}",
            )
        if len(self.title) > MAX_TITLE:
            raise VoiceError(
                "TITLE_TOO_LONG",
                f"len={len(self.title)} max={MAX_TITLE}",
            )
        key = idempotency_key if idempotency_key != "" else new_idempotency_key()
        body: dict[str, object] = {"transcript": transcript}
        if self.session_id is not None and self.session_id != "":
            body["session_id"] = self.session_id
        body["mode"] = mode
        if confirm_id != "":
            body["confirm_id"] = confirm_id
        body["title"] = self.title
        body["client_id"] = self.client_id
        body["build"] = self.build
        body["stream"] = self.stream
        body["idempotency_key"] = key
        return body

    def note_reply(self, body: dict[str, object]) -> None:
        """Remember ``session_id``, spoken text, and ``brain`` from a reply.

        A field is stored only when its value is a string. Spoken text
        prefers ``spoken`` and falls back to ``reply`` when ``spoken`` is
        not a string. Missing or non-string fields leave the previous
        value in place.
        """
        session_id = body.get("session_id")
        if isinstance(session_id, str):
            self.session_id = session_id
        spoken = body.get("spoken")
        reply = body.get("reply")
        if isinstance(spoken, str):
            self.last_spoken = spoken
        elif isinstance(reply, str):
            self.last_spoken = reply
        brain = body.get("brain")
        if isinstance(brain, str):
            self.last_brain = brain
