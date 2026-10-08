"""In-process decode for caller-supplied txt and md bytes.

pdf and docx are not parsed. zip is not unpacked. No converter is installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_bytes, bound_int, bound_text, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-document_extract/1"
POLICY_CAP: Final[int] = 256_000
_REPR_CHARS: Final[int] = 80

_PLAIN: Final[frozenset[str]] = frozenset({"txt", "md"})
_EXTERNAL: Final[frozenset[str]] = frozenset({"pdf", "docx"})
_ARCHIVE: Final[frozenset[str]] = frozenset({"zip"})


def _applied_cap(cap: object) -> int:
    """Keep a tighter positive cap. A request above the policy cap is ignored."""
    if cap is None:
        return POLICY_CAP
    if isinstance(cap, bool) or not isinstance(cap, int):
        raise Refuse("BAD_LIMIT")
    if cap > POLICY_CAP:
        return POLICY_CAP
    return bound_int(cap, 1, POLICY_CAP)


def _classify(kind: object) -> str:
    """The kind string is the only format signal."""
    name = bound_text(kind)
    if name in _EXTERNAL:
        raise Refuse("NEED_EXTRACTOR", name)
    if name in _ARCHIVE:
        raise Refuse("ARCHIVE", name)
    if name not in _PLAIN:
        raise Refuse("BAD_KIND")
    return name


def _utf8(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise Refuse("DECODE") from None


@dataclass(frozen=True, slots=True)
class Extract:
    """Decoded text and the cap that was applied."""

    kind: str
    text: str
    cap: int

    def __post_init__(self) -> None:
        if self.kind not in _PLAIN:
            _classify(self.kind)
            raise Refuse("BAD_KIND")
        applied = _applied_cap(self.cap)
        if applied != self.cap:
            raise Refuse("BAD_LIMIT")
        bound_text(self.text, applied)

    def __repr__(self) -> str:
        text = self.text
        if secret_shape(text):
            body = "[redacted]"
        elif len(text) > _REPR_CHARS:
            body = text[:_REPR_CHARS]
        else:
            body = text
        return f"Extract(kind={self.kind!r}, cap={self.cap}, text={body!r})"


def extract(kind: str, data: bytes | bytearray, cap: int | None = None) -> Extract:
    """Decode utf-8 for txt or md. pdf, docx, and zip refuse before the payload is read."""
    name = _classify(kind)
    applied = _applied_cap(cap)
    raw = bound_bytes(data, applied)
    return Extract(kind=name, text=_utf8(raw), cap=applied)


__all__ = ["POLICY_CAP", "SCHEMA", "Extract", "extract"]
