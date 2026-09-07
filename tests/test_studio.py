#!/usr/bin/env py -3.14
"""Studio DEFINE + RESEARCH pack: persist config, do not start MOTIF."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_studio import _selftest  # noqa: E402


def test_studio_pack_selftest():
    assert _selftest() == 0


def test_service_declares_studio_routes():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/studio"' in src
    assert "studio_save" in src
    assert "studio_snapshot" in src
    assert "Does not" in src and "MOTIF" in src


def test_studio_does_not_submit_jobs():
    src = (ROOT / "cosmos" / "cosmos_studio.py").read_text(encoding="utf-8")
    assert "sched.submit" not in src
    assert "Does not start MOTIF" in src
    assert "uspto" in src
    assert "gov_federal" in src
    assert "gov_state" in src
    assert "gov_local" in src
    assert "plurality" in src
    assert "majority" in src
    assert "complete" in src
    assert "arch_choice" in src
    assert "hitl" in src
    assert "artifact" in src
    assert "simultaneous" in src
    assert "continue_when" in src
    assert "via_gitur" in src
    assert "max_rounds" in src
    assert "budget_usd" in src
    assert "IMPLEMENT" in src


if __name__ == "__main__":
    raise SystemExit(_selftest())
