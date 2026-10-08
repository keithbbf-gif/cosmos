"""Length and type caps. A caller who sends more is refused, not truncated."""

from __future__ import annotations

from cosmos_federation.errors import Refuse


def bound_text(value: object, *, limit: int, name: str) -> str:
    """Accept a short non-empty string. Null bytes are refused."""
    if (
        not isinstance(value, str)
        or isinstance(value, bytes)
        or "\x00" in value
        or value.strip() == ""
        or len(value) > limit
    ):
        raise Refuse("BOUND", name)
    return value


def bound_int(value: object, *, lo: int, hi: int, name: str) -> int:
    """Accept an int in range. Booleans are not ints here."""
    if isinstance(value, bool) or not isinstance(value, int) or value < lo or value > hi:
        raise Refuse("BOUND", name)
    return value


__all__ = ["bound_int", "bound_text"]
