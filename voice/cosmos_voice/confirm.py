"""Single-use confirmation nonce.

A ``needs_confirm`` reply stores an id. Only an explicit first word of
``yes`` or ``confirm`` returns that id, and only once. ``no`` or ``cancel``
drops it. Silence is not acceptance. This module does not open a socket.
"""

from __future__ import annotations

import string

_ACCEPT = frozenset({"yes", "confirm"})
_REJECT = frozenset({"no", "cancel"})


def _first_word(transcript: str) -> str:
    """Return the first word, casefolded, with edge punctuation removed."""
    parts = transcript.split()
    if not parts:
        return ""
    return parts[0].strip(string.punctuation).casefold()


class ConfirmGate:
    """Holds at most one confirm id until the caller accepts or rejects it.

    The id is single-use. A transcript whose first word is not an accept
    or reject word leaves the pending id in place. Silence does not count
    as yes.
    """

    def __init__(self) -> None:
        self._pending: str | None = None

    def observe(self, body: dict[str, object]) -> str:
        """Store ``confirm_id`` when this reply asks for confirmation.

        Stores and returns the id only when ``needs_confirm`` is ``True``
        and ``confirm_id`` is a non-empty string. Otherwise returns ``""``
        and does not clear an id already stored.
        """
        confirm_id = body.get("confirm_id")
        if body.get("needs_confirm") is True and isinstance(confirm_id, str) and confirm_id != "":
            self._pending = confirm_id
            return confirm_id
        return ""

    def pending(self) -> str | None:
        """Return the stored confirm id, or ``None`` when none is pending."""
        return self._pending

    def accept_phrase(self, transcript: str) -> str | None:
        """Return the pending id when the first word is ``yes`` or ``confirm``.

        Comparison is case insensitive, and punctuation on that word is
        ignored. On a match the id is cleared so a second yes does not
        fire it again. Any other transcript, including silence, returns
        ``None`` and does not clear the pending id. Returns ``None`` when
        nothing is pending.
        """
        if _first_word(transcript) not in _ACCEPT:
            return None
        confirm_id = self._pending
        if confirm_id is None:
            return None
        self._pending = None
        return confirm_id

    def reject_phrase(self, transcript: str) -> bool:
        """Clear the pending id when the first word is ``no`` or ``cancel``.

        Comparison is case insensitive, and punctuation on that word is
        ignored. A match clears the id and returns ``True``. Anything else
        returns ``False`` and does not clear. Silence is not a rejection.
        """
        if _first_word(transcript) not in _REJECT:
            return False
        self._pending = None
        return True
