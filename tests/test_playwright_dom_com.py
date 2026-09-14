#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B29: CHECK / WIRE / MAP / CONFIRM the playwright-dom com rail.

Hermetic. Does not spawn Chromium. Does not invent GREEN. Live Core :8770 is
the only confirm source; ConnectionRefused is UNMEASURED (never 0, never ok).

    python3 -m unittest tests.test_playwright_dom_com
    py -3.14 -m unittest tests.test_playwright_dom_com
"""
from __future__ import annotations

import json
import socket
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import Kernel, install
from cosmos_model_rater import DEFAULT_SEATS, VIA_OPTIONS
from cosmos_playwright_rail import (
    LINK_ID, PlaywrightRailError, attach_to_kernel,
)
from cosmos_rails_prober import SATELLITES, WIRED_NODES, probe_module_for

REPO = Path(__file__).resolve().parent.parent
RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _wired_row() -> dict:
    rows = [s for s in WIRED_NODES if s["link_id"] == LINK_ID]
    return rows[0] if len(rows) == 1 else {}


def confirm_core_8770() -> dict:
    """One live confirm. Absent listener is UNMEASURED — count stays None."""
    rec = {
        "status": "UNMEASURED",
        "verified": None,
        "count": None,
        "model": None,
        "tree_id": None,
        "detail": None,
        "green": False,
    }
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.6)
    try:
        s.connect(("127.0.0.1", 8770))
    except OSError as e:
        rec["detail"] = f"{type(e).__name__}: {e}"
        return rec
    finally:
        try:
            s.close()
        except OSError:
            pass
    try:
        req = urllib.request.Request("http://127.0.0.1:8770/api/v1/status")
        with urllib.request.urlopen(req, timeout=2) as r:  # noqa: S310
            status = json.loads(r.read().decode("utf-8", "replace"))
        rec["tree_id"] = status.get("tree_id")
        req = urllib.request.Request("http://127.0.0.1:8770/api/v1/rails")
        with urllib.request.urlopen(req, timeout=2) as r:  # noqa: S310
            body = json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        rec["status"] = "EMPTY"
        rec["detail"] = f"HTTP {e.code}"
        return rec
    except Exception as e:  # noqa: BLE001
        rec["detail"] = f"{type(e).__name__}: {e}"
        return rec
    matrix = body.get("matrix") if isinstance(body, dict) else None
    if not isinstance(matrix, list):
        rec["status"] = "EMPTY"
        rec["detail"] = "GET /api/v1/rails matrix absent"
        return rec
    rec["count"] = len(matrix)
    row = next((x for x in matrix if x.get("link_id") == LINK_ID), None)
    if row is None:
        rec["status"] = "EMPTY"
        rec["detail"] = "playwright-dom absent from matrix"
        return rec
    rec["status"] = "ROW"
    rec["verified"] = row.get("verified")
    rec["model"] = row.get("model")
    rec["green"] = bool(row.get("verified") is True and rec["model"])
    rec["detail"] = (
        f"route={row.get('route')} verified={row.get('verified')!r} "
        f"age_s={row.get('age_s')!r}"
    )
    return rec


def main() -> int:
    row = _wired_row()
    check("CHECK: WIRED_NODES has exactly one playwright-dom row",
          lambda: bool(row))
    check("CHECK: row is DOM core->interact satellite=playwright (no module)",
          lambda: row.get("rail_type") == "DOM"
          and row.get("src") == "core"
          and row.get("dst") == "interact"
          and row.get("satellite") == "playwright"
          and row.get("module") is None)
    check("CHECK: SATELLITES maps playwright to cosmos_playwright_rail + live_call",
          lambda: SATELLITES.get("playwright", (None, None))[0]
          == "cosmos_playwright_rail"
          and SATELLITES["playwright"][1].__name__ == "_playwright_live_call")
    check("CHECK: probe_module_for names this rail, never Anthropic fallback",
          lambda: probe_module_for(row) == "cosmos_playwright_rail")

    ksrc = (REPO / "cosmos" / "cosmos_kernel.py").read_text(encoding="utf-8")
    check("WIRE: Kernel compose table names playwright-dom attach_to_kernel",
          lambda: '("playwright-dom", "cosmos_playwright_rail", '
                  '"attach_to_kernel", True)' in ksrc)
    check("WIRE: production boot does not dispatch (live=live_calls is not None)",
          lambda: "live=live_calls is not None" in ksrc)

    td = Path(tempfile.mkdtemp(prefix="cosmos_pwdom_com_"))
    root = install(td / "live", tree_id="b29-playwright-dom")
    k = Kernel(root, worker="b29-playwright-dom")
    composed = list((k.rails_compose or {}).get("composed") or [])
    check("WIRE: writing Kernel composes playwright-dom (adapter row)",
          lambda: LINK_ID in composed and LINK_ID in k.adapters)
    mx = {r["link_id"]: r for r in k.registry.matrix()}
    check("WIRE: compose registers the link but claims no capability (verified=None)",
          lambda: LINK_ID in mx and mx[LINK_ID]["verified"] is None
          and mx[LINK_ID]["route"] == "core->interact")
    check("WIRE: unproven compose is absent from live_nodes (fail-closed)",
          lambda: LINK_ID not in k.registry.live_nodes())
    before = set(k.registry.state())
    refused = False
    try:
        attach_to_kernel(k, {})
    except PlaywrightRailError as e:
        refused = e.kind == "REFUSED"
    check("WIRE: attach_to_kernel without boot_compose refuses and adds nothing",
          lambda: refused and set(k.registry.state()) == before)

    via_dom = [v for v in VIA_OPTIONS if v.get("id") == "dom"]
    farm = [(s["profile"], s["seat"]) for s in DEFAULT_SEATS
            if s.get("via") == "dom"]
    check("MAP: Model Rater via id=dom kind=DOM (hand, not a second link_id)",
          lambda: len(via_dom) == 1 and via_dom[0].get("kind") == "DOM")
    check("MAP: farm seats via=dom are MOTIF RESEARCH pplx/bing/chatgpt",
          lambda: set(farm) == {
              ("motif", "research_pplx"),
              ("motif", "research_bing"),
              ("motif", "research_chatgpt"),
          })

    comp = (REPO / "docs" / "COMPETENCY.toml").read_text(encoding="utf-8")
    check("MAP: COMPETENCY nodes.DOM cosmos_lane is playwright-dom",
          lambda: 'id = "DOM"' in comp
          and 'cosmos_lane = "playwright-dom (cosmos_playwright_rail)"' in comp
          and "[skills.DOM-automation.DOM]" in comp
          and "possessed = true" in comp.split("[skills.DOM-automation.DOM]", 1)[1][:80])

    kdash = (REPO / "kdash" / "index.html").read_text(encoding="utf-8")
    check("MAP: KDash RAILS MATRIX paints GET /api/v1/rails with esc() on data",
          lambda: 'id="panel-rails"' in kdash
          and "function renderRails" in kdash
          and "maybe(\"rails\",\"/api/v1/rails\"" in kdash
          and "esc(r.link_id" in kdash
          and "esc(r.rail_type" in kdash
          and "esc(r.route" in kdash)
    svc = (REPO / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    check("MAP: Core GET /api/v1/rails is the rails matrix source (no invented route)",
          lambda: '"/api/v1/rails"' in svc and "reg.matrix()" in svc)

    brief = (REPO / "docs" / "CODER_BRIEF.md").read_text(encoding="utf-8")
    check("MAP: cDeck System tab consumes Core rails; Models tab is Model Rater",
          lambda: "GET `/health` is System-tab only" in brief
          and "rails" in brief
          and "model_rater" in brief)

    live = confirm_core_8770()
    check("CONFIRM: UNMEASURED count is None, never 0",
          lambda: live["status"] != "UNMEASURED" or live["count"] is None)
    check("CONFIRM: GREEN only when verified is True AND a vendor model is named",
          lambda: live["green"] is False
          or (live.get("verified") is True and bool(live.get("model"))))
    check("CONFIRM: status is UNMEASURED, EMPTY, or ROW — never invented GREEN",
          lambda: live["status"] in ("UNMEASURED", "EMPTY", "ROW")
          and (live["status"] != "UNMEASURED" or live["green"] is False))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("CONFIRM " + json.dumps(live, sort_keys=True, default=str))
    print("SELFTEST %s - %d checks (playwright-dom CHECK/WIRE/MAP/CONFIRM)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


class TestPlaywrightDomCom(unittest.TestCase):
    def test_playwright_dom_com(self):
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    raise SystemExit(main())
