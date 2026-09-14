#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck occupancy pins + Portfolio Studio contract on existing profiles route.

Run:  py -3.14 builds/cdeck/test_kdash_working.py

UI string pins run only when ui/ is vendored (additive — every existing
panel stays). JACK'S MESH / Signal Core / kdash_native.js are off-limits
and are not rewritten here. Core contract always runs.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
UI = REPO / "ui"
ROOT = REPO.parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_profiles import (  # noqa: E402
    PS_ROUTE,
    UNMEASURED,
    assert_portfolio_studio_contract,
    iter_unbound_live,
    save_engine,
    snapshot,
)

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), str(detail)[:400]))


def _read(*names: str) -> str:
    parts = []
    for name in names:
        path = UI / name
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def _core_contract() -> None:
    import tempfile
    td = Path(tempfile.mkdtemp(prefix="cdeck_ps01_"))
    paths = CosmosPaths(install(td / "live", tree_id="cdeck-ps01"))
    snap = snapshot(paths, profile="website")
    try:
        assert_portfolio_studio_contract(snap)
        ok = True
        detail = "GET NO_SOURCE"
    except Exception as e:  # noqa: BLE001
        ok = False
        detail = "%s: %s" % (type(e).__name__, e)
    check(
        "PS-01: GET /api/v1/profiles legacy envelope + Portfolio Studio contract",
        ok and snap.get("does_not_start_motif") is True
        and snap.get("does_not_publish") is True
        and isinstance(snap.get("profiles"), list)
        and len(snap.get("stages") or []) == 9
        and "engine" in snap
        and snap.get("portfolio_studio", {}).get("route") == PS_ROUTE,
        detail,
    )
    saved = save_engine(paths, {
        "profile": "website",
        "define": {"text": "WHAT: contract freeze. WHY: PS-01."},
        "dest": {"kind": "staged", "path": "preview/index.html"},
        "stages": {"improve": "staged only"},
    })
    live_ok = True
    live_detail = ""
    try:
        assert_portfolio_studio_contract(saved)
        for path, val in iter_unbound_live(saved["portfolio_studio"]):
            if val == 0:
                live_ok = False
                live_detail = "%s is 0" % path
                break
            if path.endswith((".kind", ".status", ".outcome")) or path.startswith(
                    "typed_states.live."):
                if val != UNMEASURED:
                    live_ok = False
                    live_detail = "%s=%r" % (path, val)
                    break
    except Exception as e:  # noqa: BLE001
        live_ok = False
        live_detail = "%s: %s" % (type(e).__name__, e)
    check(
        "PS-01: SAVE does not start MOTIF; unbound live fields stay UNMEASURED (never 0)",
        live_ok and saved.get("does_not_start_motif") is True
        and saved["portfolio_studio"]["current_stage"]["id"] is None
        and saved["portfolio_studio"]["spend"]["usd"] is None
        and saved["portfolio_studio"]["occupancy"]["n"] is None,
        live_detail,
    )
    svc = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    check(
        "PS-01: no invented Portfolio Studio route — existing /api/v1/profiles only",
        'parsed.path == "/api/v1/profiles"' in svc
        and 'parsed.path == "/api/v1/portfolio"' not in svc
        and 'parsed.path == "/api/v1/portfolio_studio"' not in svc,
        "profiles route",
    )


def _ui_pins() -> None:
    css = _read("header.css", "deck_more.css", "app.css")
    html = _read("index.html", "deck_more.html")
    blob = css + "\n" + html

    check(
        "WINDOW: MESH and extra panes share the viewport; no vh floor clips the tab rail",
        "#cdeck-viewport" in blob
        and "#cdeck-mesh-fold" in css
        and "#cdeck-more" in css
        and "min-height: 0" in css
        and not re.search(r"min-height:\s*\d+vh", css),
        "viewport=%s min0=%s vh_min=%s"
        % (
            "#cdeck-viewport" in blob,
            "min-height: 0" in css,
            bool(re.search(r"min-height:\s*\d+vh", css)),
        ),
    )

    check(
        "TABS: left rail scrolls inside the extra-pane shell so the lowest tab is reachable",
        "extra-pane-shell" in blob
        and "deck-tabs-rail" in blob
        and bool(
            re.search(
                r"\.deck-tabs-rail[^{]*\{[^}]*overflow-y:\s*(auto|scroll)",
                css,
                re.S | re.I,
            )
        )
        and "min-height: 0" in css,
        "shell=%s rail=%s"
        % ("extra-pane-shell" in blob, "deck-tabs-rail" in blob),
    )

    check(
        "PANES: the tab shell gets the whole fold, not one cockpit grid column",
        "deck-tab-shell" in blob
        and "deck-more-fold" in blob
        and "grid-column: 1 / -1" in css,
        "tab_shell=%s grid_span=%s"
        % ("deck-tab-shell" in blob, "grid-column: 1 / -1" in css),
    )

    studio = _read("deck_studio.js")
    appjs = _read("app.js")
    runs_blob = studio + "\n" + appjs

    check(
        "RUNS: list+detail painter loads from GET /api/v1/jukebox (not /jobs)",
        'apiGet("/api/v1/jukebox")' in runs_blob
        and "function paintRunsList" in studio
        and "function rowHtml" in studio
        and "function renderJobs" in appjs
        and '"/api/v1/jobs"' not in studio.split("fileNewJob")[0],
        "jukebox=%s paint=%s render=%s"
        % (
            'apiGet("/api/v1/jukebox")' in runs_blob,
            "paintRunsList" in studio,
            "renderJobs" in appjs,
        ),
    )

    check(
        "RUNS: JOB_ORDER includes FINDINGS and chip can filter FINDINGS when Core sends it",
        "JOB_ORDER" in studio
        and re.search(r'JOB_ORDER\s*=\s*\[[^\]]*"FINDINGS"', studio) is not None
        and "findingsInEmit" in studio
        and 'chipHtml("FINDINGS"' in studio,
        "findings_chip=%s" % ("FINDINGS" in studio),
    )

    check(
        "RUNS: filter chips survive the 10s poll (runsFilter module state, not reset on refresh)",
        "runsFilter" in studio
        and "10000" in appjs
        and "setInterval" in appjs
        and "paintRunsList(lastBody" in studio,
        "runsFilter=%s poll=%s"
        % ("runsFilter" in studio, "10000" in appjs),
    )

    check(
        "RUNS: file NEW job POSTs /api/v1/jobs without re-submitting a job_id",
        "file NEW job" in studio
        and 'apiPost("/api/v1/jobs"' in studio
        and "job_id" not in studio.split("function fileNewJob")[1].split("}")[0],
        "post=%s" % ('apiPost("/api/v1/jobs"' in studio),
    )

    mr = _read("model_rater.js")
    html_full = _read("index.html")
    check(
        "MODEL RATER: catalog from GET /api/v1/model_rater (no fake local catalog)",
        'apiGet("/api/v1/model_rater' in mr
        and "FAKE_CATALOG" not in mr
        and "fake catalog" not in mr.lower()
        and not re.search(r"var\s+CATALOG\s*=\s*\[", mr),
        "get=%s fake=%s"
        % ('apiGet("/api/v1/model_rater' in mr, "FAKE_CATALOG" in mr),
    )
    check(
        "MODEL RATER: seats + estimate POST /api/v1/model_rater/*",
        'apiPost("/api/v1/model_rater/seat"' in mr
        and 'apiPost("/api/v1/model_rater/estimate"' in mr
        and 'apiPost("/api/v1/model_rater/job_estimate"' in mr
        and 'apiPost("/api/v1/model_rater/refresh"' in mr,
        "estimate=%s job=%s refresh=%s"
        % (
            'apiPost("/api/v1/model_rater/estimate"' in mr,
            'apiPost("/api/v1/model_rater/job_estimate"' in mr,
            'apiPost("/api/v1/model_rater/refresh"' in mr,
        ),
    )
    check(
        "MODEL RATER: bench_defs + blend paint from Core snapshot",
        "bench_defs" in mr
        and "paintBlend" in mr
        and "paintBenchDefs" in mr
        and "blended_per_m" in mr,
        "bench=%s blend=%s"
        % ("bench_defs" in mr, "paintBlend" in mr),
    )
    check(
        "HEADER MODEL RATER drawer wired",
        "btnModelRater" in html_full and "model-rater-drawer" in html_full,
        "header drawer",
    )

    pf = _read("deck_profiles.js")
    if pf:
        check(
            "PROFILES: paints Core GET /api/v1/profiles; esc() on data text; no invented route",
            'api("/api/v1/profiles"' in pf
            and "function esc(" in pf
            and "esc(rec.label" in pf
            and "esc(s.name)" in pf
            and "/api/v1/portfolio" not in pf,
            "profiles pane",
        )
        check(
            "PROFILES: SAVE does not start MOTIF / does not publish (legacy say)",
            "Does not start MOTIF" in pf
            and "Does not publish" in pf,
            "save say",
        )


def main() -> int:
    _core_contract()
    if (UI / "index.html").is_file():
        _ui_pins()
    else:
        check(
            "UI occupancy pins skipped — ui/ not vendored in this tree (panels unchanged)",
            True,
            "no ui/",
        )

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        mark = "OK  " if ok else "FAIL"
        print("  %s  %s%s" % (mark, label, ("  [" + detail + "]") if detail and not ok else ""))
    print(
        "SELFTEST %s %d/%d"
        % ("PASS" if not failed else "FAIL", len(RESULTS) - len(failed), len(RESULTS))
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
