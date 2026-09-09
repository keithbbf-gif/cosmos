#!/usr/bin/env py -3.14
"""pid_alive: dead PIDs must not look running (Health ghost-child scar)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cosmos"))

from cosmos_clock import pid_alive  # noqa: E402


def test_pid_alive_self_true():
    assert pid_alive(os.getpid()) is True


def test_pid_alive_bogus_false():
    assert pid_alive(0) is False
    assert pid_alive(-1) is False
    assert pid_alive(999_999_999) is False
