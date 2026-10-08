"""Secret-shaped text is refused at the edge and scrubbed in anything we keep."""

from __future__ import annotations

import hashlib
import hmac
import re

_SK = re.compile(r"sk-[A-Za-z0-9_\-]{8,}")
_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]{8,}")
_ASSIGN = re.compile(
    r"(?i)\b(api_key|apikey|token|secret|password|authorization)\b\s*[:=]\s*\S+"
)


def secret_shape(text: str) -> bool:
    """True when `text` carries a key-shaped substring."""
    if not isinstance(text, str):
        return False
    return bool(_SK.search(text) or _BEARER.search(text) or _ASSIGN.search(text))


def redact(text: str) -> str:
    """Replace key-shaped substrings. The input is otherwise unchanged."""
    if not isinstance(text, str):
        return ""
    out = _ASSIGN.sub("[redacted-assignment]", text)
    out = _BEARER.sub("[redacted-bearer]", out)
    out = _SK.sub("[redacted-key]", out)
    return out


def const_eq(left: str, right: str) -> bool:
    """Compare two strings without leaking which byte differed."""
    if not isinstance(left, str) or not isinstance(right, str):
        return False
    digest_left = hashlib.sha256(left.encode("utf-8")).digest()
    digest_right = hashlib.sha256(right.encode("utf-8")).digest()
    return hmac.compare_digest(digest_left, digest_right)


__all__ = ["const_eq", "redact", "secret_shape"]
