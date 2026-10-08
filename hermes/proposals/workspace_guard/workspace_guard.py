"""Write containment inside a grant, and refusal of secret-shaped outbound text."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from cosmos_hermes import PathJail, Refuse, bound_text, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-workspace_guard/1"
POLICY_CAP: Final[int] = 32_000
_PATH_CONTROL: Final[frozenset[int]] = frozenset((*range(1, 32), 127))

__all__ = [
    "POLICY_CAP",
    "SCHEMA",
    "AppliedCap",
    "applied_cap",
    "check_outbound",
    "check_write",
]


def _clamp(asked: int) -> int:
    if asked > POLICY_CAP:
        return POLICY_CAP
    return asked


@dataclass(frozen=True, slots=True)
class AppliedCap:
    """Asked cap, applied cap, and the policy cap. Applied never exceeds policy."""

    asked_cap: int
    cap: int
    policy_cap: int
    schema: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if self.policy_cap != POLICY_CAP:
            raise Refuse("BAD_LIMIT")
        if isinstance(self.asked_cap, bool) or not isinstance(self.asked_cap, int):
            raise Refuse("NOT_INT")
        if isinstance(self.cap, bool) or not isinstance(self.cap, int):
            raise Refuse("NOT_INT")
        if self.asked_cap < 1:
            raise Refuse("OUT_OF_RANGE", f"1..{POLICY_CAP}")
        if self.cap != _clamp(self.asked_cap):
            raise Refuse("BAD_LIMIT")


def applied_cap(asked: object = None) -> AppliedCap:
    """Record the cap in force. A request above the policy cap is ignored."""
    if asked is None:
        asked = POLICY_CAP
    if isinstance(asked, bool) or not isinstance(asked, int):
        raise Refuse("NOT_INT")
    if asked < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{POLICY_CAP}")
    return AppliedCap(
        asked_cap=asked,
        cap=_clamp(asked),
        policy_cap=POLICY_CAP,
        schema=SCHEMA,
    )


def _jail(jail: object) -> PathJail:
    if not isinstance(jail, PathJail):
        raise Refuse("BAD_JAIL")
    return jail


def _path_text(value: object, limit: int) -> str:
    raw = bound_text(value, limit)
    for ch in raw:
        if ord(ch) in _PATH_CONTROL:
            raise Refuse("BAD_PATH")
    return raw


def check_write(jail: object, absolute_path: object, cap: object = None) -> Path:
    """Return the contained path. A jail refusal propagates unchanged."""
    held = _jail(jail)
    limit = applied_cap(cap).cap
    raw = _path_text(absolute_path, limit)
    try:
        contained = held.contain(raw)
    except Refuse:
        raise
    except (OSError, ValueError):
        raise Refuse("BAD_PATH") from None
    if secret_shape(raw):
        raise Refuse("SPILL")
    shown = str(contained)
    if shown != raw:
        bounded = bound_text(shown, limit)
        if secret_shape(bounded):
            raise Refuse("SPILL")
    return contained


def check_outbound(text: object, cap: object = None) -> str:
    """Return the text, or raise SPILL when secret_shape(text) is true."""
    raw = bound_text(text, applied_cap(cap).cap)
    if secret_shape(raw):
        raise Refuse("SPILL")
    return raw
