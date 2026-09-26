#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Research-call envelope: file + ingest. Core does not fetch."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_research_call import _selftest as kit_selftest  # noqa: E402


def test_research_call_selftest():
    assert kit_selftest() == 0


def test_service_names_research_call():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/research_call"' in src
    assert "research_call_run" in src


if __name__ == "__main__":
    test_research_call_selftest()
    test_service_names_research_call()
    print("PASS research call")
