#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clone-detect: identical tail of n chars. Muse/OSS/Llama farm scar."""
from __future__ import annotations


def shared_tail(a: str, b: str, n: int = 800) -> bool:
    if n <= 0:
        return False
    if not a or not b:
        return False
    if len(a) < n or len(b) < n:
        return False
    return a[-n:] == b[-n:]
