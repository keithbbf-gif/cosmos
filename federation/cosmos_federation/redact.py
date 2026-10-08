"""Secret shapes stay out of repr, logs, and proposal files."""

from __future__ import annotations

import hmac
import re

_SHAPES: tuple[re.Pattern[str], ...] = (
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"ghp_[A-Za-z0-9]{8,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{8,}"),
    re.compile(r"Bearer\s+\S{8,}", re.IGNORECASE),
    re.compile(r"api[_-]?key\s*[:=]", re.IGNORECASE),
    re.compile(r"secret[_-]?access[_-]?key\s*[:=]", re.IGNORECASE),
    re.compile(r"xai-[A-Za-z0-9_\-]{8,}", re.IGNORECASE),
)


def secret_shape(text: str) -> bool:
    """True when the text looks like key material. Empty is not a secret."""
    if not isinstance(text, str) or text == "":
        return False
    return any(p.search(text) for p in _SHAPES)


def redact(text: str) -> str:
    """Replace secret-shaped spans with a fixed mark. Non-strings come back empty."""
    if not isinstance(text, str):
        return ""
    out = text
    for pattern in _SHAPES:
        out = pattern.sub("[REDACTED]", out)
    return out


def const_eq(left: str, right: str) -> bool:
    """Compare two strings without a short-circuit on the first differing byte."""
    if not isinstance(left, str) or not isinstance(right, str):
        return False
    a = left.encode("utf-8")
    b = right.encode("utf-8")
    if len(a) != len(b):
        hmac.compare_digest(a, a)
        return False
    return hmac.compare_digest(a, b)


__all__ = ["const_eq", "redact", "secret_shape"]
