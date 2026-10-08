"""Loopback bearer and install key for a day-one peer.

``draw`` and ``now`` are arguments. This module does not read the clock and
does not draw from the operating system.
"""

from __future__ import annotations

import base64
import hashlib
import os
from collections.abc import Callable
from dataclasses import dataclass, field, replace

from cosmos_federation import (
    ROLES,
    PathJail,
    Refuse,
    bound_int,
    bound_text,
    secret_shape,
)

SCHEMA = "cosmos-federation-secrets/1"

# Live loopback serve asks token_urlsafe for 24 bytes. Install stores 32.
_TOKEN_BYTES = 24
_KEY_BYTES = 32
_ID_HEX = 12
_TOKEN_LIMIT = 256
_EPOCH_HI = 2**63 - 1

_TOKEN_REL = ROLES["config"] + "/api_token.txt"
_KEY_REL = ROLES["config"] + "/install_key.bin"

Draw = Callable[[int], bytes]

_HEX = frozenset("0123456789abcdef")


def _draw_exact(draw: Draw, n: int) -> bytes:
    if not callable(draw):
        raise Refuse("DRAW", "draw must be callable")
    raw = draw(n)
    if not isinstance(raw, bytes) or len(raw) != n:
        raise Refuse("DRAW", "draw must return exactly the requested bytes")
    return raw


def _bearer(raw: bytes) -> str:
    # Same construction as token_urlsafe: url-safe base64, padding stripped.
    # 24 bytes divides by 3, so the padding is empty. Strip anyway.
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _id12(material: bytes) -> str:
    """Twelve hex chars of SHA-256 over the bytes that land in the file."""
    return hashlib.sha256(material).hexdigest()[:_ID_HEX]


def _shown_id(value: str) -> str:
    if len(value) == _ID_HEX and all(ch in _HEX for ch in value):
        return value
    return "hidden"


@dataclass(frozen=True, slots=True)
class Mint:
    """Bearer shown once. After acknowledge, only ids remain on the object."""

    token_id: str
    key_id: str
    minted_epoch: int
    show_token: str | None = field(repr=False)
    install_key: bytes | None = field(repr=False)

    def __repr__(self) -> str:
        held = "held" if self.show_token is not None else "cleared"
        return (
            "Mint("
            f"token_id={_shown_id(self.token_id)!r}, "
            f"key_id={_shown_id(self.key_id)!r}, "
            f"minted_epoch={self.minted_epoch!r}, "
            f"show_token={held})"
        )


def mint(draw: Draw, now: int) -> Mint:
    """Mint a loopback bearer and a 32-byte install key.

    A remote bind must not call mint: live serve refuses TOKEN_MISSING on
    remote rather than inventing a token.
    """
    epoch = bound_int(now, lo=0, hi=_EPOCH_HI, name="now")
    token_raw = _draw_exact(draw, _TOKEN_BYTES)
    key = _draw_exact(draw, _KEY_BYTES)
    bearer = _bearer(token_raw)
    if bearer.strip() == "":
        raise Refuse("BLANK_TOKEN", "empty token is an open door")
    if secret_shape(bearer):
        raise Refuse("SECRET_SHAPE", "bearer looked like vendor key material")
    return Mint(
        token_id=_id12(bearer.encode("utf-8")),
        key_id=_id12(key),
        minted_epoch=epoch,
        show_token=bearer,
        install_key=key,
    )


def acknowledge(mint: Mint) -> Mint:
    """Return a mint that keeps ids only.

    The bearer is shown once. A later log of the retained object must not
    be able to reprint it or the install key.
    """
    if not isinstance(mint, Mint):
        raise Refuse("MINT", "not a mint")
    return replace(mint, show_token=None, install_key=None)


def _write_private(path: object, data: bytes) -> None:
    """Owner-only from the first byte, matching live ``_write_private``.

    A create with default permissions followed by chmod would race. Mode
    ``0o600`` is the intent. Windows treats that mode as advisory.
    """
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)


def write_files(jail: PathJail, token: str, key: bytes) -> None:
    """Write ``config/api_token.txt`` and ``config/install_key.bin``.

    The token file is UTF-8 with no added newline. Live serve strips on read.
    ``O_TRUNC`` matches live ``_write_private``. Whether the file was absent
    is the caller's decision. A remote bind still must not call ``mint``.
    """
    if not isinstance(jail, PathJail):
        raise Refuse("JAIL", "writer requires a path jail")
    if not isinstance(token, str) or token.strip() == "":
        raise Refuse("BLANK_TOKEN", "empty token is an open door")
    cleaned = bound_text(token, limit=_TOKEN_LIMIT, name="token").strip()
    if secret_shape(cleaned):
        raise Refuse("SECRET_SHAPE", "bearer looked like vendor key material")
    if not isinstance(key, bytes) or len(key) != _KEY_BYTES:
        raise Refuse("BAD_KEY", "install key must be 32 bytes")
    token_path = jail.contain(_TOKEN_REL)
    key_path = jail.contain(_KEY_REL)
    token_path.parent.mkdir(parents=True, exist_ok=True)
    _write_private(token_path, cleaned.encode("utf-8"))
    _write_private(key_path, key)


__all__ = [
    "SCHEMA",
    "Mint",
    "acknowledge",
    "mint",
    "write_files",
]
