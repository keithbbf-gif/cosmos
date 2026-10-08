"""Named refusals. A missing layer or a bad flag is a reason, never a fake call."""

from __future__ import annotations


class Refuse(Exception):
    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else f"{reason}: {detail}")
