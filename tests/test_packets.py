#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused tests for cosmos_packets (KEEP_PACKETS CAS fold).

PR #565 proposed a GitHub-main-relative tests/test_steal_impl.py that would
overlay live plugin-waist pins. Those packet pins live here instead.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

try:
    from cosmos_packets import (  # noqa: E402
        CAS_PART,
        EVENT,
        SCHEMA,
        _selftest,
        cas_root,
        get_packet,
        live_pointer,
        snapshot,
    )
except ModuleNotFoundError as exc:
    if getattr(exc, "name", None) not in {None, "cosmos_packets"}:
        raise
    pytest.skip(
        "cosmos_packets cannot be imported because it is not on main. "
        "The singular module is cosmos/cosmos_packet.py, already covered by "
        "tests/test_packet_singular.py. The old packets API is not restored.",
        allow_module_level=True,
    )
from cosmos_segments import CAS  # noqa: E402


def test_packets_selftest():
    assert _selftest() == 0


def test_packets_use_existing_cas_class():
    src = (ROOT / "cosmos" / "cosmos_packets.py").read_text(encoding="utf-8")
    prod = src.split("def _selftest")[0]
    assert "from cosmos_segments import CAS" in prod
    assert "class CAS" not in prod
    assert "import langgraph" not in prod.lower()
    assert "subprocess" not in prod and "Popen" not in prod
    assert EVENT == "TOOL_OUTPUT_PACKET"
    assert SCHEMA == "cosmos-packets/1"
    assert CAS_PART == "cas"
    assert hasattr(CAS, "put") and hasattr(CAS, "get")


def test_get_folds_never_mkdir_ast():
    src = (ROOT / "cosmos" / "cosmos_packets.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    names = {"snapshot", "get_packet", "live_pointer", "cas_root"}
    found = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            found.add(node.name)
            for n in ast.walk(node):
                if isinstance(n, ast.Call):
                    attr = n.func.attr if isinstance(n.func, ast.Attribute) else ""
                    ident = n.func.id if isinstance(n.func, ast.Name) else ""
                    assert attr != "mkdir" and ident != "mkdir", node.name
            if node.name == "snapshot":
                assert "Never mkdir" in (ast.get_docstring(node) or "")
    assert found == names


def test_porosity_opus_t_untouched():
    """Do not change Opus T on GET /porosity — this WO does not touch that file."""
    poro = (ROOT / "cosmos" / "cosmos_porosity.py").read_text(encoding="utf-8")
    assert "Tensor grid T[i,j,a]" in poro
    svc = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/porosity"' in svc
    prod = (ROOT / "cosmos" / "cosmos_packets.py").read_text(
        encoding="utf-8").split("def _selftest")[0]
    assert "/porosity" not in prod
    assert "api/v1" not in prod


def test_cas_get_mkdir_false_refuses_absent(tmp_path):
    """Additive CAS fold: GET handle never creates the store directory."""
    from cosmos_ledger import LedgerError

    missing = tmp_path / "cas-absent"
    try:
        CAS(missing, mkdir=False)
        raised = False
    except LedgerError as e:
        raised = e.kind == "NOT_FOUND"
    assert raised
    assert not missing.exists()


def test_snapshot_callable_export():
    assert callable(snapshot)
    assert callable(get_packet)
    assert callable(live_pointer)
    assert callable(cas_root)


if __name__ == "__main__":
    raise SystemExit(_selftest())
