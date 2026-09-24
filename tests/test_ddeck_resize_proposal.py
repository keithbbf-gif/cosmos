"""Pins the D-deck resize/drag P10 proposal. Does not write the cdeck live tree."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIFF = ROOT / "work_orders" / "ccr" / "proposals" / "ddeck-resize-drag.diff"
META = ROOT / "ccr" / "proposals" / "ddeck-resize-drag.json"


def test_proposal_files_exist():
    assert DIFF.is_file(), DIFF
    assert META.is_file(), META
    text = DIFF.read_text(encoding="utf-8")
    assert text.startswith("diff --git a/builds/cdeck/ui/app.js")
    assert "@@ -0,0 +1," not in text


def test_app_js_hunk_keeps_live_selector_and_excludes_cdeck_more():
    text = DIFF.read_text(encoding="utf-8")
    assert (
        '".home-card[id], .orch-code[id], #home-nav, #orch-home, #orch-east, .advanced, .panel[id]"'
        in text
    )
    assert 'el.closest("#cdeck-more")' in text
    assert "cdeckPaneBoard" not in text
    assert "panelGeom:v" not in text
    assert "function ensureRh" not in text


def test_header_css_hunk_paints_existing_pane_rh_only():
    text = DIFF.read_text(encoding="utf-8")
    assert "-#cdeck-more .pane-rh{position:absolute;z-index:3;background:transparent}" in text
    assert "+#cdeck-more .pane-rh-se{" in text
    assert "background:linear-gradient(135deg" in text
    assert "#8a5a2b" in text
    assert ".rh{" not in text
    assert "grid-template-columns" not in text


def _geom_nodes(nodes):
    """Mirror of the proposed panelGeomNodes filter (no DOM)."""
    out = []
    for el in nodes:
        ancestors = el.get("ancestors") or []
        if "cdeck-more" in ancestors:
            continue
        out.append(el["id"])
    return out


def test_panel_geom_filter_leaves_orch_and_drops_ddeck():
    nodes = [
        {"id": "orch-home", "ancestors": ["orch"]},
        {"id": "home-nav", "ancestors": ["orch"]},
        {"id": "pNodes", "ancestors": ["win", "body"]},
        {"id": "panel-studio", "ancestors": ["cdeck-more", "deck-stage"]},
        {"id": "panel-model-rater", "ancestors": ["cdeck-more", "deck-view"]},
        {"id": "home-code", "ancestors": ["cdeck-more", "deck-view"]},
    ]
    got = _geom_nodes(nodes)
    assert got == ["orch-home", "home-nav", "pNodes"]
    assert "panel-studio" not in got
    assert "home-code" not in got
