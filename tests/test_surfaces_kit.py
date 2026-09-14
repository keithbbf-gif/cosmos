#!/usr/bin/env py -3.14
"""Surfaces kit: storage + channels + callable tools. GET only."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_surfaces_kit import _selftest as kit_selftest  # noqa: E402


def test_surfaces_kit_fold():
    assert kit_selftest() == 0


def test_service_names_surfaces_kit():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/surfaces_kit"' in src
    assert "surfaces_kit_snapshot" in src
    assert "surfaces_kit_save" not in src


def test_kit_storage_names_itc_unmeasured():
    """Writing kernel seeds ITC as a claim; kit storage does not invent reachability."""
    import tempfile
    from cosmos_kernel import Kernel, install
    from cosmos_surfaces_kit import snapshot

    td = Path(tempfile.mkdtemp(prefix="kit_itc_"))
    root = install(td / "live", tree_id="kit-itc")
    kernel = Kernel(root, worker="core")
    rec = snapshot(kernel)
    rows = {r["id"]: r for r in rec["storage"]["rows"]}
    assert "itc" in rows
    itc = rows["itc"]
    assert itc["reachable"] is None
    assert itc["free_gb"] is None
    assert itc["age_s"] is None
    assert itc["qualified"] is None
    assert itc["kind"] == "PUBLISH"
    assert itc["role"] == "PUBLISH"


if __name__ == "__main__":
    raise SystemExit(kit_selftest())
