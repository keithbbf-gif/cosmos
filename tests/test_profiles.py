#!/usr/bin/env py -3.14
"""profiles: Website GC MOTIF skins, IMPLEMENT dest, no auto-MOTIF.

Portfolio Studio schemas (response, stage-projection, typed-state,
transition) are frozen as executable contracts on the existing
GET/POST /api/v1/profiles route. No new route.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_profiles import (  # noqa: E402
    EMPTY,
    PS_ROUTE,
    PS_SCHEMA,
    SCHEMA,
    UNMEASURED,
    _selftest,
    assert_portfolio_studio_contract,
    iter_unbound_live,
    legacy_view,
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
    assert 'parsed.path == "/api/v1/portfolio"' not in src
    assert 'parsed.path == "/api/v1/portfolio_studio"' not in src


def test_portfolio_studio_contract_on_existing_route():
    import tempfile
    td = Path(tempfile.mkdtemp(prefix="cosmos_ps01_"))
    paths = CosmosPaths(install(td / "live", tree_id="spike-ps01"))
    snap = snapshot(paths, profile="website")
    assert_portfolio_studio_contract(snap)
    ps = snap["portfolio_studio"]
    assert ps["schema"] == PS_SCHEMA
    assert ps["route"] == PS_ROUTE
    assert snap["schema"] == SCHEMA
    assert "portfolio_studio" not in legacy_view(snap)
    assert ps["typed_states"]["define"] == EMPTY
    for path, val in iter_unbound_live(ps):
        assert val != 0, path
        if path.endswith((".kind", ".status", ".outcome")) or path.startswith(
                "typed_states.live."):
            assert val == UNMEASURED, path
        else:
            assert val is None, path


if __name__ == "__main__":
    raise SystemExit(_selftest())
