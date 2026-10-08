"""Typed refusals for the COSMOS voice module.

A refusal is a named kind plus a short detail. Callers match on ``kind``.
The detail is safe to log: it must already be redacted by the raiser.
"""

from __future__ import annotations


class VoiceError(Exception):
    """Fail-closed voice refusal. ``kind`` is the stable token."""

    def __init__(self, kind: str, detail: str = "") -> None:
        self.kind = kind
        self.detail = detail
        message = f"{kind}: {detail}" if detail else kind
        super().__init__(message)
