"""Stable refusal codes. A refusal is a result, not a repaired input."""

from __future__ import annotations

_CODE_CHARS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")


class Refuse(Exception):
    """Fail closed. `code` is a stable tag. `detail` never carries a secret."""

    code: str
    detail: str

    def __init__(self, code: str, detail: str = "") -> None:
        if (
            not isinstance(code, str)
            or len(code) < 2
            or len(code) > 48
            or any(ch not in _CODE_CHARS for ch in code)
        ):
            raise ValueError("refuse code must be UPPER_SNAKE")
        if not isinstance(detail, str) or len(detail) > 240:
            raise ValueError("refuse detail must be a short string")
        self.code = code
        self.detail = detail
        super().__init__(code if detail == "" else f"{code}: {detail}")


__all__ = ["Refuse"]
