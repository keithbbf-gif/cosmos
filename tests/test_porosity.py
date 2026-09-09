#!/usr/bin/env py -3.14
"""orthogonal porosity tensor: pair vectors, no invented scores."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_porosity import _selftest  # noqa: E402


def test_porosity_selftest():
    assert _selftest() == 0


def test_service_declares_porosity_routes():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/porosity"' in src
    assert "POST /api/v1/porosity" in src
    assert "GET never mkdir" in src
    assert "cosmos_porosity" in src
    assert "complement" in src.lower()
    assert "tensors[agent][vs][axis]" in src
    assert "authority=d.get(\"authority\")" in src
    assert "action=d.get(\"audit_action\")" in src
    assert "agent_id=d.get(\"agent_id\")" in src


def test_forge_facilitate_hooks_porosity():
    src = (ROOT / "cosmos" / "cosmos_forge_bg.py").read_text(encoding="utf-8")
    assert "hook_trial" in src
    assert "cosmos_porosity" in src
    assert 'authority="crew:forge"' in src
    assert 'action="facilitate"' in src


def test_crucible_and_runner_hook_porosity():
    cru = (ROOT / "cosmos" / "cosmos_crucible.py").read_text(encoding="utf-8")
    assert "hook_returns" in cru
    assert 'authority="crew:crucible"' in cru
    critics = (ROOT / "cosmos" / "cosmos_crucible_critics.py").read_text(
        encoding="utf-8")
    assert "hook_returns" in critics
    run = (ROOT / "cosmos" / "cosmos_runner.py").read_text(encoding="utf-8")
    assert 'cmd.startswith("crucible:round")' in run
    assert "spend_round" in run
    pool = (ROOT / "cosmos" / "cosmos_pool.py").read_text(encoding="utf-8")
    assert "runner.paths = paths" in pool


if __name__ == "__main__":
    raise SystemExit(_selftest())
