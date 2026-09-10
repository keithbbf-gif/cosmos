#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P02 peeking ban — dual-lane BUILD, no shared scratch, no ballot writer.

Each lane has a private workspace. A read of the sibling workspace (path
or prompt that names it) is PEEKING_VIOLATION. Compare is later, CCr
disposes. Occupancy: dual-lane BUILD has no ballot writer.
"""
from __future__ import annotations

from pathlib import Path


class PeekingError(RuntimeError):
    """kind in {PEEKING_VIOLATION, NO_BALLOT_WRITER, BAD_LANE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _resolve(path: str | Path) -> Path:
    return Path(path).resolve()


def assert_no_peek(reader_ws: str | Path, path: str | Path,
                   sibling_ws: str | Path) -> None:
    """Refuse a path that lives under the sibling workspace.

    Own-workspace reads are allowed. Distinct lanes stay independent.
    """
    try:
        reader = _resolve(reader_ws)
        target = _resolve(path)
        sibling = _resolve(sibling_ws)
    except OSError as e:
        raise PeekingError("BAD_LANE", f"unreadable lane path: {e}") from e
    if reader == sibling:
        raise PeekingError("BAD_LANE", "reader and sibling are the same workspace")
    try:
        target.relative_to(sibling)
    except ValueError:
        return
    try:
        target.relative_to(reader)
    except ValueError:
        raise PeekingError(
            "PEEKING_VIOLATION",
            f"lane {reader} must not read sibling {sibling} path {target}",
        )
    # Nested under both only if one workspace contains the other — still peeking.
    raise PeekingError(
        "PEEKING_VIOLATION",
        f"workspace overlap reader={reader} sibling={sibling}",
    )


def assert_prompt_no_peek(prompt: str, sibling_ws: str | Path) -> None:
    """Refuse a prompt that names the sibling workspace path."""
    try:
        marker = str(_resolve(sibling_ws))
    except OSError as e:
        raise PeekingError("BAD_LANE", f"unreadable sibling: {e}") from e
    if marker and marker in (prompt or ""):
        raise PeekingError(
            "PEEKING_VIOLATION",
            "sibling workspace path present in prompt",
        )


def refuse_ballot(*_a, **_k) -> None:
    """Occupancy lock: dual-lane BUILD has no ballot writer."""
    raise PeekingError(
        "NO_BALLOT_WRITER",
        "dual-lane BUILD has no ballot writer — CCr disposes after compare",
    )
