"""Named refusals.

A missing layer, a bad path, or a tool the harness does not offer is a
reason string. Callers branch on ``exc.reason``. The message is for the
journal. It is not a second code path.
"""

from __future__ import annotations


class Refuse(Exception):
    """Fail closed. ``reason`` is the stable token. ``detail`` is the evidence."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else f"{reason}: {detail}")
