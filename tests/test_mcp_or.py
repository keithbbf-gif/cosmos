#!/usr/bin/env py -3.14
"""OpenRouter MCP cookbook: convert tools, named pins, no filesystem spawn."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_mcp_client import _selftest  # noqa: E402


def test_mcp_client_selftest():
    assert _selftest() == 0


def test_service_declares_mcp_route():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/mcp"' in src
    assert "named_servers" in src
    assert "Filesystem MCP REFUSED" in src


if __name__ == "__main__":
    raise SystemExit(_selftest())
