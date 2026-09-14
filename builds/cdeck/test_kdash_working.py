#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck occupancy pins — string checks on ui/ sources.

Run:  py -3.14 builds/cdeck/test_kdash_working.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
UI = REPO / "ui"
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


def main() -> int:
    css = _read("header.css", "deck_more.css", "app.css")
    html = _read("index.html", "deck_more.html")
    js = _read("header.js", "model_rater.js", "kdash_native.js", "app.js", "deck_tabs.js")
    blob = css + "\n" + html + "\n" + js
    appjs = _read("app.js")
    tabsjs = _read("deck_tabs.js")
    forgejs = _read("deck_forge.js")
    nmp = (REPO / "cosmos_nodemap_panel.py").read_text(encoding="utf-8")

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

    check(
        "HEADER INSTANCE: native second window or honest browser refusal",
        "btnInstance" in html
        and "open_profile_window" in js
        and "native second window" in js.lower(),
        "instance wiring",
    )

    check(
        "HEADER HOME/CODE: orch mode toggle on body",
        "btnHomeCode" in html and "data-orch-mode" in html and "bindHomeCode" in js,
        "home/code",
    )

    check(
        "HEADER type size S/M/L: body classes cdeck-type-*",
        all(x in html for x in ("btnTypeSizeS", "btnTypeSizeM", "btnTypeSizeL"))
        and "cdeck-type-" in js,
        "type size",
    )

    check(
        "HEADER KILL: POST /api/v1/kill",
        "btnKill" in html and 'apiPost("/api/v1/kill"' in js,
        "kill",
    )

    check(
        "HEADER control/resume: GET control + POST control/resume",
        "btnControlResume" in html
        and "/api/v1/control?client_id=" in js
        and 'apiPost("/api/v1/control/resume"' in js,
        "control/resume",
    )

    check(
        "HEADER NEW coding: POST /api/v1/session_tools scan",
        "btnNewCoding" in html
        and 'apiPost("/api/v1/session_tools"' in js
        and "NEW coding" in js,
        "new coding",
    )

    check(
        "HEADER GEM search: honest NOT_ADDRESSABLE / Chrome Profile 2 copy",
        "btnGemSearch" in html
        and "NOT_ADDRESSABLE" in js
        and "Profile 2" in js,
        "gem",
    )

    check(
        "HEADER MODEL RATER: GET /api/v1/model_rater",
        "btnModelRater" in html and 'apiGet("/api/v1/model_rater' in js,
        "model rater",
    )

    check(
        "HEADER OpenWork snap-right: native invoke or refusal",
        "btnOpenWorkSnap" in html
        and "snap_openwork_right" in js
        and "OpenWork" in js,
        "openwork snap",
    )

    check(
        "HEADER GBW snap: native invoke or refusal",
        "btnGbwSnap" in html and "snap_gbw" in js,
        "gbw snap",
    )

    check(
        "HEADER ORC stream picker POST /api/v1/orc",
        "selOrcStream" in html
        and 'apiGet("/api/v1/orc")' in js
        and 'apiPost("/api/v1/orc"' in js,
        "orc",
    )

    check(
        "CVM/SGH launch pads: honest copy, not silent dead",
        "cvm-launch-pad" in html
        and "sgh-launch-pad" in html
        and "launch-copy" in html
        and "builds/cvm-dt" in html
        and "/api/v1/voice_loop" in html,
        "launch pads",
    )

    check(
        "SYSTEM: pane board defaults system 160×120 at origin (x and y)",
        "PANE_CELL_W = 160" in tabsjs
        and "PANE_CELL_H = 120" in tabsjs
        and "cdeckPaneBoard:v4" in tabsjs
        and re.search(
            r"system:\s*\{\s*x:\s*0,\s*y:\s*0,\s*w:\s*PANE_CELL_W,\s*h:\s*PANE_CELL_H",
            tabsjs,
        )
        is not None,
        "pane defaults",
    )

    check(
        "SYSTEM: renderStatus / renderHealth / renderFleet painters in app.js",
        "function renderStatus" in appjs
        and "function renderHealth" in appjs
        and "function renderFleet" in appjs
        and "function renderNodemap" in appjs,
        "renderers",
    )

    check(
        "SYSTEM: spend / rails / fleet / nodemap paint live Core GETs (not invented hosts)",
        all(
            p in appjs
            for p in (
                'apiGet("/api/v1/status")',
                'apiGet("/api/v1/health")',
                'apiGet("/api/v1/spend")',
                'apiGet("/api/v1/rails")',
                'apiGet("/api/v1/fleet")',
                'apiGet("/api/v1/nodemap")',
            )
        ),
        "get paths",
    )

    check(
        "SYSTEM: health RED negative control stays red (ncrow / nclabel, not placated)",
        "SUPPOSED TO BE RED" in appjs
        and "ncrow" in appjs
        and "negative_control_red" in appjs
        and "r.ok === false" in appjs
        and "negative control" in appjs.lower(),
        "negative control",
    )

    check(
        "SYSTEM: 503 surfaces CDECK_PANEL_NOT_COMPOSED verbatim",
        "CDECK_PANEL_NOT_COMPOSED" in appjs,
        "503 string",
    )

    check(
        "SYSTEM: rails table paints vendor model + STALE renders red (sgh-api row)",
        "function proofCell" in appjs
        and "vendor-emitted on live_call only" in appjs
        and 'proof_state === "STALE"' in appjs
        and "ncrow" in appjs,
        "rails proof",
    )
    check(
        "SYSTEM: nodemap paints SGH routing row from GET /api/v1/nodemap payload",
        "independence_notes" in appjs
        and "not independent" not in appjs
        and "proofCell(n, ttl)" in appjs
        and '<th>node</th><th>link</th><th>model</th>' in appjs,
        "nodemap table",
    )
    check(
        "FORGE: SGH node panel wired to GET /api/v1/nodemap (model + proof, not COMPETENCY.toml)",
        "panel-forge-sgh" in forgejs
        and 'apiGet("/api/v1/nodemap")' in forgejs
        and "paintSghNode" in forgejs
        and 'nodes[i].id === "SGH"' in forgejs
        and "live_call only" in forgejs,
        "forge sgh",
    )
    check(
        "FORGE: independence note kept (SGH + GBW not independent checks)",
        "independence_notes" in forgejs
        and "notes[0].note" in forgejs
        and "SGH (sgh-api) and GBW (gw-api)" in nmp,
        "independence",
    )

    check(
        "NODEMAP: registry entry maps SGH -> sgh-api with paid-rail note",
        '"id": "SGH"' in nmp
        and '"link_id": "sgh-api"' in nmp
        and "spend_ok" in nmp
        and "ROUTING_NODES" in nmp,
        "nodemap panel",
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
