"""Size and range caps applied before any other work."""

from __future__ import annotations

from cosmos_hermes.errors import Refuse

MAX_TEXT = 256_000
MAX_BYTES = 1_048_576


def bound_text(value: object, limit: int = MAX_TEXT) -> str:
    """Return `value` when it is a string inside `limit` and free of NUL."""
    if not isinstance(limit, int) or limit < 1 or limit > MAX_TEXT:
        raise Refuse("BAD_LIMIT")
    if not isinstance(value, str):
        raise Refuse("NOT_TEXT")
    if "\x00" in value:
        raise Refuse("NULL_BYTE")
    if len(value) > limit:
        raise Refuse("OVERSIZE", str(limit))
    return value


def bound_bytes(value: object, limit: int = MAX_BYTES) -> bytes:
    """Return `value` when it is `bytes` inside `limit`."""
    if not isinstance(limit, int) or limit < 1 or limit > MAX_BYTES:
        raise Refuse("BAD_LIMIT")
    if not isinstance(value, (bytes, bytearray)):
        raise Refuse("NOT_BYTES")
    raw = bytes(value)
    if len(raw) > limit:
        raise Refuse("OVERSIZE", str(limit))
    return raw


def bound_int(value: object, lo: int, hi: int) -> int:
    """Return `value` when it is an int in `[lo, hi]`. Bool is refused."""
    if not isinstance(lo, int) or not isinstance(hi, int) or lo > hi:
        raise Refuse("BAD_LIMIT")
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < lo or value > hi:
        raise Refuse("OUT_OF_RANGE", f"{lo}..{hi}")
    return value


__all__ = ["MAX_BYTES", "MAX_TEXT", "bound_bytes", "bound_int", "bound_text"]
