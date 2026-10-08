"""Exclusive audio lease for the phone or the desktop.

One live holder at a time. ``none`` means idle and is not a holder.
The clock is injected so a test can expire a lease without sleeping.
This module does not open a socket and does not write a file.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from cosmos_voice.errors import VoiceError
from cosmos_voice.types import OWNER_TTL_S, OWNERS

# Claimable names from the shared owner list. ``none`` is idle, not a holder.
_HOLDERS: frozenset[str] = frozenset(name for name in OWNERS if name != "none")


class AudioOwner:
    """Exclusive capture and playback lease.

    The same owner may renew. A different live owner raises ``AUDIO_BUSY``.
    Expiry follows the injected clock. The deadline itself is already expired.
    """

    def __init__(
        self,
        now: Callable[[], float] | None = None,
        ttl_s: float = OWNER_TTL_S,
    ) -> None:
        """Bind ``now`` (default ``time.monotonic``) and the lease length."""
        self._now: Callable[[], float] = time.monotonic if now is None else now
        self._ttl_s = float(ttl_s)
        self._holder = "none"
        self._expires_at = 0.0

    def claim(self, who: str) -> dict[str, object]:
        """Take or renew the lease for ``phone`` or ``desktop``.

        Any other name, including ``none``, raises ``BAD_MODE``. A different
        unexpired holder raises ``AUDIO_BUSY``.
        """
        if who not in _HOLDERS:
            raise VoiceError("BAD_MODE", "owner must be phone or desktop")
        at = float(self._now())
        current, _expired = self._state(at)
        if current not in ("none", who):
            raise VoiceError("AUDIO_BUSY", current)
        self._holder = who
        self._expires_at = at + self._ttl_s
        return self._row(at)

    def release(self, who: str) -> dict[str, object]:
        """Drop the lease when ``who`` is the live holder.

        Idle, expired, or a different name raises ``AUDIO_BUSY``. After a
        successful release the current owner is ``none``.
        """
        at = float(self._now())
        current, _expired = self._state(at)
        if current not in _HOLDERS or current != who:
            raise VoiceError("AUDIO_BUSY", current)
        self._holder = "none"
        self._expires_at = 0.0
        return self._row(at)

    def current(self) -> str:
        """Return the live holder, or ``none`` when idle or expired."""
        current, _expired = self._state(float(self._now()))
        return current

    def expired(self) -> bool:
        """True when a stored holder is at or past its deadline.

        Idle is not expired. A release clears the holder, so it is not expired.
        """
        _current, is_expired = self._state(float(self._now()))
        return is_expired

    def allows_capture(self, who: str) -> bool:
        """True only when ``who`` is the live, unexpired holder."""
        return self._allows(who)

    def allows_playback(self, who: str) -> bool:
        """True only when ``who`` is the live, unexpired holder."""
        return self._allows(who)

    def _allows(self, who: str) -> bool:
        if who not in _HOLDERS:
            return False
        current, _expired = self._state(float(self._now()))
        return current == who

    def _state(self, at: float) -> tuple[str, bool]:
        # Live strictly before the deadline. The deadline itself is expired.
        if self._holder == "none":
            return ("none", False)
        if at < self._expires_at:
            return (self._holder, False)
        return ("none", True)

    def _row(self, at: float) -> dict[str, object]:
        current, is_expired = self._state(at)
        expires = self._expires_at if self._holder != "none" else 0.0
        row: dict[str, object] = {
            "owner": current,
            "expires_at": expires,
            "expired": is_expired,
        }
        return row
