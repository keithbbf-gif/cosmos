"""Shared PCM builders for the duplex tests. No hardware and no network."""

from __future__ import annotations

import struct


def loud(ms: int, rate: int = 24000, amp: int = 20000) -> bytes:
    count = rate * ms // 1000
    return struct.pack("<h", amp) * count


def silence(ms: int, rate: int = 24000) -> bytes:
    count = rate * ms // 1000
    return b"\x00\x00" * count
