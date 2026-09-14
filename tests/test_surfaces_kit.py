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
    assert "save_surface" in src


def test_gdx_put_verify_probe():
    import tempfile
    from cosmos_surfaces import exchange_put_verify_probe

    td = Path(tempfile.mkdtemp(prefix="gdx_probe_"))
    reachable, free, detail = exchange_put_verify_probe(td)()
    assert reachable is True
    assert free is not None
    assert "atomic put+verify" in detail


def test_get_surfaces_gdx_measured_when_configured():
    import json
    import tempfile

    from cosmos_kernel import Kernel, install
    from cosmos_paths import CosmosPaths
    from cosmos_surfaces import CANON_SURFACE_IDS, measure_canon_surfaces

    td = Path(tempfile.mkdtemp(prefix="gdx_surf_api_"))
    root = install(td / "live", tree_id="gdx-surf")
    paths = CosmosPaths(root)
    gdx_dir = td / "handoff"
    gdx_dir.mkdir()
    cfg = {
        "schema": "cosmos-backup-targets/1",
        "targets": {"gdx": {"dest": str(gdx_dir)}},
    }
    paths.role("config").mkdir(parents=True, exist_ok=True)
    (paths.role("config") / "backup_targets.json").write_text(
        json.dumps(cfg), encoding="utf-8")
    k = Kernel(root, worker="core")
    assert "GDX" in k.surfaces.state()
    measure_canon_surfaces(k.surfaces, paths)
    row = next(r for r in k.surfaces.report() if r["id"] == "GDX")
    assert row["reachable"] is True
    assert row["free_gb"] is not None
    assert set(CANON_SURFACE_IDS) <= {r["id"] for r in k.surfaces.report()}


if __name__ == "__main__":
    raise SystemExit(kit_selftest())
