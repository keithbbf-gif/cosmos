#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Portfolio Studio feature pins + optional FEATURE_PROBE ui/ byte gate.

Run:  py -3.14 builds/cdeck/test_deck_features.py

Freezes response / stage-projection / typed-state / transition schemas
as executable contracts on GET/POST /api/v1/profiles. FEATURE_PROBE
runs only when ui/ is vendored.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UI = HERE / "ui"
PROBE = HERE / "FEATURE_PROBE.json"
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_profiles import (  # noqa: E402
    EMPTY,
    LEGACY_SNAPSHOT_KEYS,
    LEGACY_STAGE_KEYS,
    PS_ROUTE,
    PS_SCHEMA,
    SCHEMA,
    TRANSITION_CATALOG,
    TYPED_STATES,
    UNMEASURED,
    assert_legacy_compatible,
    assert_portfolio_studio_contract,
    assert_unbound_unmeasured,
    save_engine,
    snapshot,
)

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _probe_ui_files() -> dict:
    if not PROBE.is_file():
        raise FileNotFoundError(str(PROBE))
    rec = json.loads(PROBE.read_text(encoding="utf-8"))
    ui_files = rec.get("ui_files")
    if not isinstance(ui_files, dict) or not ui_files:
        raise ValueError("FEATURE_PROBE.json missing ui_files map")
    return ui_files


def _ui_matches_probe() -> bool:
    ui_files = _probe_ui_files()
    if not UI.is_dir():
        raise FileNotFoundError(str(UI))
    live: dict[str, dict] = {}
    for path in sorted(UI.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(UI).as_posix()
        data = path.read_bytes()
        live[rel] = {
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    if set(ui_files) != set(live):
        missing = sorted(set(ui_files) - set(live))
        extra = sorted(set(live) - set(ui_files))
        raise ValueError(f"ui_files keys drift probe-only={missing} disk-only={extra}")
    for rel, rec_fp in ui_files.items():
        disk_fp = live[rel]
        if not isinstance(rec_fp, dict):
            if rec_fp != disk_fp["bytes"]:
                raise ValueError(f"{rel}: probe bytes {rec_fp!r} != disk {disk_fp['bytes']}")
            continue
        if rec_fp.get("bytes") != disk_fp["bytes"]:
            raise ValueError(
                f"{rel}: bytes probe={rec_fp.get('bytes')} disk={disk_fp['bytes']}")
        if rec_fp.get("sha256") != disk_fp["sha256"]:
            raise ValueError(f"{rel}: sha256 mismatch")
    return True


def _ps_paths():
    import tempfile
    td = Path(tempfile.mkdtemp(prefix="cdeck_ps01_feat_"))
    return CosmosPaths(install(td / "live", tree_id="cdeck-ps01-feat"))


def main() -> int:
    paths = _ps_paths()
    snap = snapshot(paths, profile="website")
    saved = save_engine(paths, {
        "profile": "website",
        "define": {"text": "WHAT: PS-01 freeze. WHY: executable contract."},
        "stages": {"research": "DOM rails first"},
    })

    check(
        "response schema: legacy keys + cosmos-profiles/1 stay on /api/v1/profiles",
        lambda: assert_legacy_compatible(snap)
        and snap["schema"] == SCHEMA
        and list(LEGACY_SNAPSHOT_KEYS)
        == snap["portfolio_studio"]["response"]["legacy_keys"]
        and snap["portfolio_studio"]["response"]["additive"] == "portfolio_studio",
    )
    check(
        "stage-projection: nine rows, catalog fields == stages[], live UNMEASURED",
        lambda: assert_portfolio_studio_contract(snap)
        and [{k: r[k] for k in LEGACY_STAGE_KEYS}
             for r in snap["portfolio_studio"]["stage_projection"]]
        == [{k: s[k] for k in LEGACY_STAGE_KEYS} for s in snap["stages"]]
        and all(r["status"] == UNMEASURED and r["note_kind"] == EMPTY
                for r in snap["portfolio_studio"]["stage_projection"]),
    )
    check(
        "typed-state: vocab frozen; empty=EMPTY; engine NO_SOURCE then OK; live UNMEASURED",
        lambda: list(snap["portfolio_studio"]["typed_states"]["vocab"]) == list(TYPED_STATES)
        and snap["portfolio_studio"]["typed_states"]["engine"] == "NO_SOURCE"
        and snap["portfolio_studio"]["typed_states"]["define"] == EMPTY
        and saved["portfolio_studio"]["typed_states"]["engine"] == "OK"
        and saved["portfolio_studio"]["typed_states"]["define"] == "OK"
        and saved["portfolio_studio"]["typed_states"]["live"]["current_stage"] == UNMEASURED
        and next(r for r in saved["portfolio_studio"]["stage_projection"]
                 if r["id"] == "research")["note_kind"] == "OK",
    )
    check(
        "transition schema: GET no-mutate / POST save; neither starts MOTIF nor publishes",
        lambda: [t["id"] for t in TRANSITION_CATALOG] == ["get_snapshot", "save_engine"]
        and all(t["starts_motif"] is False and t["publishes"] is False
                for t in TRANSITION_CATALOG)
        and saved["portfolio_studio"]["transitions"]["last"]["kind"] == UNMEASURED
        and saved["portfolio_studio"]["transitions"]["next_live"]["id"] is None
        and saved["does_not_start_motif"] is True
        and saved["does_not_publish"] is True
        and saved["portfolio_studio"]["route"] == PS_ROUTE
        and saved["portfolio_studio"]["schema"] == PS_SCHEMA,
    )
    check(
        "unbound live fields emit UNMEASURED / None — never 0, never inferred stage",
        lambda: assert_unbound_unmeasured(saved["portfolio_studio"])
        and saved["portfolio_studio"]["current_stage"]["id"] is None
        and saved["portfolio_studio"]["spend"]["usd"] is None
        and saved["portfolio_studio"]["spend"]["tokens"] is None
        and saved["portfolio_studio"]["occupancy"]["n"] is None
        and saved["portfolio_studio"]["motif_running"]["value"] is None,
    )

    if PROBE.is_file() and UI.is_dir():
        check(
            "FEATURE_PROBE.json is present and matches the shipped ui/ byte for byte",
            lambda: _ui_matches_probe(),
        )
    else:
        check(
            "FEATURE_PROBE skipped — ui/ not vendored (existing panels stay off this lane)",
            lambda: True,
        )

    pf = UI / "deck_profiles.js"
    if pf.is_file():
        src = pf.read_text(encoding="utf-8")
        check(
            "deck_profiles.js: esc() on data text; live Core /api/v1/profiles only",
            lambda: "function esc(" in src
            and 'api("/api/v1/profiles"' in src
            and "/api/v1/portfolio" not in src,
        )
    else:
        check(
            "deck_profiles.js pin skipped — pane not vendored (kdash_native.js off-limits)",
            lambda: True,
        )

    bad = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
