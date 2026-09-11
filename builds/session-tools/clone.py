#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clone-detect: identical tail of n chars. Muse/OSS/Llama farm scar."""
from __future__ import annotations

from refusals import SessionToolsRefusal


def shared_tail(a: str, b: str, n: int = 800) -> bool:
    if n <= 0:
        return False
    if not a or not b:
        return False
    if len(a) < n or len(b) < n:
        return False
    return a[-n:] == b[-n:]


def refuse_duplicate(a: str, b: str, n: int = 800) -> None:
    if shared_tail(a, b, n):
        raise SessionToolsRefusal(
            "CLONE",
            "duplicate mouth refused: identical final %s characters" % n,
        )
