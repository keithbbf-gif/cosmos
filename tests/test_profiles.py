#!/usr/bin/env py -3.14
"""profiles: Website GC MOTIF skins, IMPLEMENT dest, no auto-MOTIF."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_profiles import (  # noqa: E402
    MOTIF_STAGES,
    PORTFOLIO_STUDIO_SCHEMA,
    STAGE_PROJECTION_LIVE_FIELDS,
    _selftest,
    portfolio_studio_contract,
    portfolio_studio_live_is_honest,
    snapshot,
)
from cosmos_kernel import install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402


def test_profiles_selftest():
    assert _selftest() == 0


def test_service_declares_profiles_routes():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/profiles"' in src
    assert "profiles_save" in src
    assert "Does not start MOTIF" in src
    assert "Does not publish" in src


def _fresh_paths() -> CosmosPaths:
    import tempfile

    td = Path(tempfile.mkdtemp(prefix="test_profiles_contract_"))
    root = install(td / "live", tree_id="test-profiles-contract")
    return CosmosPaths(root)


def test_legacy_profiles_snapshot_fields():
    paths = _fresh_paths()
    snap = snapshot(paths, profile="website")
    assert snap["ok"] is True
    assert len(snap["profiles"]) >= 7
    assert len(snap["stages"]) == 9
    assert snap["stages"][0]["id"] == "define"
    assert snap["engine"]["schema"]
    assert snap["does_not_start_motif"] is True
    assert snap["does_not_publish"] is True


def test_portfolio_studio_contract_schemas_frozen():
    contract = portfolio_studio_contract()
    sp = contract["stage_projection"]
    ts = contract["typed_state"]
    tr = contract["transition"]
    assert sp["schema"].startswith("cosmos-profiles-stage-projection/")
    assert ts["schema"].startswith("cosmos-profiles-typed-state/")
    assert tr["schema"].startswith("cosmos-profiles-transition/")
    assert sp["stage_ids"] == [s["id"] for s in MOTIF_STAGES]
    assert len(tr["allowed_edges"]) == len(MOTIF_STAGES)
    assert set(sp["live_fields"]) == set(STAGE_PROJECTION_LIVE_FIELDS)


def test_portfolio_studio_live_fields_unmeasured():
    paths = _fresh_paths()
    snap = snapshot(paths, profile="forge")
    ps = snap["portfolio_studio"]
    assert ps["schema"] == PORTFOLIO_STUDIO_SCHEMA
    assert ps["profile"] == "forge"
    live = ps["live"]
    assert portfolio_studio_live_is_honest(live)
    assert len(live["stage_projection"]) == 9
    assert len(live["typed_state"]) == 9
    for row in live["stage_projection"]:
        for field in STAGE_PROJECTION_LIVE_FIELDS:
            slot = row[field]
            assert slot["kind"] == "UNMEASURED"
            assert slot["value"] is None
    for row in live["typed_state"]:
        assert row["state"] == "UNMEASURED"
        assert row["since"] is None


if __name__ == "__main__":
    raise SystemExit(_selftest())
