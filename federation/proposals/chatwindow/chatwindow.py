"""Day-one chat window. The document is static. The bearer stays out of it.

Core's serve banner points at kdash and checks an Authorization header against
config/api_token.txt. A peer's first window cannot contain that bearer. The
installer opens http://127.0.0.1:8770/dayone. issue_nonce takes caller-supplied
bytes. redeem trades that one-time nonce for an httpOnly loopback cookie.
The cookie is a session id, not the long-term bearer file.

draw and now are arguments. This module does not call os.urandom or time.time.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from cosmos_federation import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    NONCE_TTL_S,
    ROUTE_CHAT,
    ROUTE_PAGE,
    Refuse,
    bound_int,
    const_eq,
    secret_shape,
)

SCHEMA = "cosmos-federation-chatwindow/1"

# Twelve hex chars name the grant in logs and on the cookie. Not the raw nonce.
_ID_LEN = 12
_NONCE_BYTES = 16
_HEX = "0123456789abcdef"
# Fixed bound_int ceiling (2100-01-01 UTC). Not a clock read.
_EPOCH_HI = 4_102_444_800
COOKIE_NAME = "cosmos_dayone"

_PAGE_PATH = Path(__file__).resolve().parent / "dayone.html"
_OPEN = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}{ROUTE_PAGE}"


@dataclass(slots=True)
class _Use:
    """Nonce is frozen. The one-time bit has to live on a mutable latch."""

    spent: bool = False


@dataclass(frozen=True, slots=True)
class Nonce:
    """One issued grant. `code` is what the caller presents. It is not in repr."""

    value_id: str
    issued_epoch: int
    code: str = field(repr=False, compare=False)
    _use: _Use = field(default_factory=_Use, repr=False, compare=False)

    def __post_init__(self) -> None:
        if len(self.value_id) != _ID_LEN or any(ch not in _HEX for ch in self.value_id):
            raise Refuse("NONCE", "id")
        if len(self.code) != _NONCE_BYTES * 2 or any(ch not in _HEX for ch in self.code):
            raise Refuse("NONCE", "code")
        # Hex cannot look like a key. Refuse anyway if a future alphabet drifts.
        if secret_shape(self.code) or secret_shape(self.value_id):
            raise Refuse("NONCE", "shape")
        bound_int(self.issued_epoch, lo=0, hi=_EPOCH_HI, name="issued_epoch")
        if not isinstance(self._use, _Use):
            raise Refuse("NONCE", "latch")


@dataclass(frozen=True, slots=True)
class Cookie:
    """Loopback session handle. value_id is not the raw nonce and not the bearer."""

    name: str
    value_id: str
    http_only: bool = True
    host: str = DEFAULT_HOST

    def __post_init__(self) -> None:
        # A caller cannot retarget this into a script-readable or non-loopback cookie.
        if self.name != COOKIE_NAME or self.http_only is not True or self.host != DEFAULT_HOST:
            raise Refuse("COOKIE", "loopback httpOnly")
        if len(self.value_id) != _ID_LEN or any(ch not in _HEX for ch in self.value_id):
            raise Refuse("COOKIE", "id")


def page() -> str:
    """The inlined day-one document. Same bytes as dayone.html."""
    text = _PAGE_PATH.read_text(encoding="utf-8")
    # The file is static. Refuse if it drifts off the installer URL or the chat route,
    # or if a key shape was pasted into the document.
    if _OPEN not in text or ROUTE_CHAT not in text:
        raise Refuse("PAGE", "route")
    # The document must not carry a one-time code, a bearer, or an sk- key.
    folded = text.casefold()
    if secret_shape(text) or "sk-" in folded or "bearer" in folded or "nonce" in folded:
        raise Refuse("PAGE", "secret shape")
    return text


def issue_nonce(draw: Callable[[int], bytes], now: int) -> Nonce:
    """Mint one nonce from caller bytes. The raw code stays off repr."""
    now_i = bound_int(now, lo=0, hi=_EPOCH_HI, name="now")
    if not callable(draw):
        raise Refuse("NONCE", "draw")
    raw = draw(_NONCE_BYTES)
    if not isinstance(raw, bytes) or len(raw) != _NONCE_BYTES:
        raise Refuse("NONCE", "draw")
    return Nonce(
        value_id=hashlib.sha256(raw).hexdigest()[:_ID_LEN],
        issued_epoch=now_i,
        code=raw.hex(),
    )


def redeem(nonce: Nonce, presented: str, now: int, remote: bool) -> Cookie:
    """Trade a matching unspent nonce for the loopback cookie.

    Remote is refused first so a non-loopback caller learns nothing about the
    nonce. A wrong presentation is always NONCE: a separate length or type
    error would tell those cases apart. Only a success spends the latch.
    """
    if not isinstance(remote, bool) or remote:
        raise Refuse("REMOTE", "loopback only")
    if not isinstance(nonce, Nonce):
        raise Refuse("NONCE", "mismatch")
    if (
        not isinstance(presented, str)
        or len(presented) != _NONCE_BYTES * 2
        or not const_eq(nonce.code, presented)
    ):
        raise Refuse("NONCE", "mismatch")
    if nonce._use.spent:
        raise Refuse("NONCE_USED", "replay")
    now_i = bound_int(now, lo=0, hi=_EPOCH_HI, name="now")
    age = now_i - nonce.issued_epoch
    # Greater-than the product ttl. Equal is still inside the window.
    # A clock behind issue time is outside the window too.
    if age < 0 or age > NONCE_TTL_S:
        raise Refuse("NONCE_EXPIRED", "outside the one-minute window")
    nonce._use.spent = True
    return Cookie(
        name=COOKIE_NAME,
        value_id=nonce.value_id,
        http_only=True,
        host=DEFAULT_HOST,
    )


__all__ = [
    "COOKIE_NAME",
    "SCHEMA",
    "Cookie",
    "Nonce",
    "issue_nonce",
    "page",
    "redeem",
]
