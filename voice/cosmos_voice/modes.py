"""Half-duplex listen modes.

Transcripts are already text. This module does not call a recognizer
and it does not open a socket.
"""

from __future__ import annotations

from cosmos_voice.types import FOLLOW_WINDOW_S, WAKE_WORDS, ModeDecision

_SEPARATORS = " \t\r\n,.;:!?\"'"


def _boundary(char: str) -> bool:
    """A wake word ends at whitespace or light punctuation, not inside a token."""
    return char.isspace() or char in _SEPARATORS


def _wake_remainder(text: str, wake_words: tuple[str, ...]) -> tuple[bool, str]:
    """Strip one leading wake word.

    The bool is whether a wake word matched. Matching is case-insensitive.
    The longer word wins, so ``hey cosmos`` is not read as ``cosmos``.
    """
    words = sorted((word.strip() for word in wake_words), key=len, reverse=True)
    for word in words:
        if not word:
            continue
        size = len(word)
        if len(text) < size or text[:size].casefold() != word.casefold():
            continue
        if len(text) > size and not _boundary(text[size]):
            continue
        return True, text[size:].lstrip(_SEPARATORS)
    return False, text


class ModeMachine:
    """Decide whether one utterance may leave the phone.

    ``off`` refuses. ``ptt`` needs ``held``. ``tap`` needs ``tapped``.
    ``wake`` strips a leading ``hey cosmos`` or ``cosmos``. A bare wake
    is ``wake_only`` and is not accepted. ``note_spoken`` opens one
    follow utterance that does not need the wake word, until ``follow_s``.
    """

    def __init__(
        self,
        wake_words: tuple[str, ...] = WAKE_WORDS,
        follow_s: float = FOLLOW_WINDOW_S,
    ) -> None:
        """Store the wake words and the follow-window length."""
        self.wake_words = wake_words
        self.follow_s = follow_s
        self._follow_start: float | None = None
        self._follow_until: float | None = None

    def note_spoken(self, now: float) -> None:
        """Start the one-utterance follow window at ``now``."""
        self._follow_start = now
        self._follow_until = now + self.follow_s

    def _in_follow(self, now: float) -> bool:
        start = self._follow_start
        until = self._follow_until
        if start is None or until is None:
            return False
        return start <= now <= until

    def _close_follow(self) -> None:
        self._follow_start = None
        self._follow_until = None

    def _gated(self, text: str, allow: bool, mode: str, kind: str) -> ModeDecision:
        if allow and text:
            return ModeDecision(True, text, kind, mode)
        return ModeDecision(False, "", "ignored", mode)

    def accept(
        self,
        transcript: str,
        *,
        held: bool,
        tapped: bool,
        now: float,
        mode: str,
    ) -> ModeDecision:
        """Accept or drop one transcript.

        ``mode`` ``off`` and any unknown mode return kind ``BAD_MODE``.
        Push-to-talk accepts only while ``held`` (kind ``ptt``, else
        ``ignored``). Tap accepts only when ``tapped`` (kind ``tap``).
        Wake mode strips a leading wake word. An empty remainder is
        ``wake_only``. Inside the follow window, one utterance without
        a wake word is kind ``follow``.
        """
        text = transcript.strip()
        if mode == "off":
            return ModeDecision(False, "", "BAD_MODE", mode)
        if mode == "ptt":
            return self._gated(text, held, mode, "ptt")
        if mode == "tap":
            return self._gated(text, tapped, mode, "tap")
        if mode != "wake":
            return ModeDecision(False, "", "BAD_MODE", mode)
        matched, remainder = _wake_remainder(text, self.wake_words)
        if matched:
            if not remainder:
                return ModeDecision(False, "", "wake_only", mode)
            self._close_follow()
            return ModeDecision(True, remainder, "wake", mode)
        if text and self._in_follow(now):
            self._close_follow()
            return ModeDecision(True, text, "follow", mode)
        return ModeDecision(False, "", "ignored", mode)
