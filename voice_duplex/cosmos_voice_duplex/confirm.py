"""Spoken confirm. First hearing of a consequential command never runs it.

The grammar matches ``cosmos_voice``: first word, exact, case-insensitive.
``submit`` and ``session`` need a second spoken yes that replays the original
utterance. Destructive verbs are refused here and are not dispatched.

When a live ``VoiceMode`` is injected, the nonce lives on that object's
ledger. This module does not open a ledger and does not write ``live/``.
A bare yes is not itself the command: the retry sends the original text
plus the confirm id, which is what ``VoiceMode.handle`` binds the nonce to.
"""

from __future__ import annotations

import string
from dataclasses import dataclass
from typing import Protocol

CONSEQUENTIAL = frozenset({"submit", "session"})
DESTRUCTIVE = frozenset(
    {
        "delete",
        "remove",
        "rm",
        "del",
        "rmdir",
        "format",
        "purge",
        "reset",
        "drop",
        "overwrite",
        "force",
        "wipe",
        "erase",
        "destroy",
        "truncate",
        "uninstall",
    }
)
YES = frozenset({"yes", "confirm", "yes confirm", "confirm yes", "do it", "go ahead"})


class VoiceHandle(Protocol):
    def handle(
        self,
        session_id: str,
        transcript: str,
        mode: str = "voice",
        confirm_id: str | None = None,
    ) -> dict[str, object]: ...


@dataclass
class Pending:
    transcript: str
    confirm_id: str | None
    kind: str  # "voice" | "tool"
    tool_name: str = ""
    tool_args: str = ""
    call_id: str = ""


@dataclass
class GateResult:
    action: str  # "pass" | "hold" | "confirm" | "refuse" | "cancel"
    spoken: str = ""
    transcript: str = ""
    confirm_id: str | None = None
    voice_result: dict[str, object] | None = None
    tool_name: str = ""
    tool_args: str = ""
    call_id: str = ""


def first_word(text: str) -> str:
    parts = text.split()
    if not parts:
        return ""
    return parts[0].strip(string.punctuation).lower()


def normalize(text: str) -> str:
    return " ".join(text.split()).lower()


class ConfirmGate:
    def __init__(self, voice: VoiceHandle | None = None, session_id: str = "voice") -> None:
        self.voice = voice
        self.session_id = session_id
        self.pending: Pending | None = None

    def on_user_text(self, text: str) -> GateResult:
        clean = " ".join(text.split())
        if not clean:
            return GateResult("refuse", "I did not hear anything.")
        if len(clean) > 4000:
            return GateResult("refuse", "That was too long. Say it in a shorter line.")
        if self.pending is not None:
            return self._resolve(clean)
        word = first_word(clean)
        if word in DESTRUCTIVE:
            return GateResult(
                "refuse",
                "I will not do that. Destructive commands are refused.",
                transcript=clean,
            )
        if word in CONSEQUENTIAL:
            return self._issue(clean)
        return GateResult("pass", transcript=clean)

    def hold_tool(self, name: str, arguments: str, call_id: str) -> GateResult:
        spoken = f"Say yes to run {name}. Say anything else to cancel."
        self.pending = Pending("", None, "tool", name, arguments, call_id)
        return GateResult("hold", spoken)

    def _issue(self, transcript: str) -> GateResult:
        if self.voice is not None:
            result = self.voice.handle(self.session_id, transcript, "voice", None)
            confirm_id = result.get("confirm_id")
            cid = confirm_id if isinstance(confirm_id, str) else None
            spoken = result.get("spoken") or result.get("reply") or "Say yes to confirm."
            self.pending = Pending(transcript, cid, "voice")
            return GateResult("hold", str(spoken), transcript, cid, result)
        self.pending = Pending(transcript, None, "voice")
        spoken = "Say yes to confirm that. I have not run it."
        return GateResult("hold", spoken, transcript, None, None)

    def _resolve(self, text: str) -> GateResult:
        pending = self.pending
        assert pending is not None
        if normalize(text) not in YES:
            self.pending = None
            word = first_word(text)
            if word in DESTRUCTIVE:
                return GateResult("refuse", "Cancelled. Destructive commands are refused.", text)
            if word in CONSEQUENTIAL:
                return self._issue(text)
            return GateResult("cancel", "Cancelled.", text)
        self.pending = None
        if pending.kind == "tool":
            return GateResult(
                "confirm",
                transcript=pending.transcript,
                confirm_id=pending.confirm_id,
                tool_name=pending.tool_name,
                tool_args=pending.tool_args,
                call_id=pending.call_id,
            )
        if self.voice is not None and pending.confirm_id:
            result = self.voice.handle(
                self.session_id, pending.transcript, "voice", pending.confirm_id
            )
            spoken = str(result.get("spoken") or result.get("reply") or "")
            return GateResult("confirm", spoken, pending.transcript, pending.confirm_id, result)
        return GateResult("confirm", "Confirmed.", pending.transcript, pending.confirm_id)
