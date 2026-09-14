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

    orders = _read("deck_orders.js")
    check(
        "ORDERS: list is fed by GET /api/v1/work_orders (timestamped rows from Core)",
        '"/api/v1/work_orders"' in orders
        and "apiGet" in orders
        and "rowStamp" in orders
        and "picked_at" in orders,
        "path=%s apiGet=%s"
        % ('"/api/v1/work_orders"' in orders, "apiGet" in orders),
    )
    check(
        "ORDERS: state filters are chips, not search/hunt boxes",
        "wo-state-chip" in orders
        and "wo-chips" in orders
        and 'type="search"' not in orders
        and "placeholder" not in orders.lower(),
        "chips=%s search_input=%s"
        % ("wo-state-chip" in orders, 'type="search"' in orders),
    )
    check(
        "ORDERS: pickup notifies Core via POST /api/v1/work_orders/picked",
        '"/api/v1/work_orders/picked"' in orders
        and "apiPost" in orders
        and "pickupOrder" in orders
        and "order_id" in orders,
        "picked_path=%s"
        % ('"/api/v1/work_orders/picked"' in orders,),
    )
    check(
        "ORDERS: NO_SOURCE is painted honestly (not an invented empty queue)",
        'kind === "NO_SOURCE"' in orders
        and "NO_SOURCE" in orders
        and "wo-honest-kind" in orders,
        "no_source_branch=%s"
        % ('kind === "NO_SOURCE"' in orders,),
    )
    tabs = _read("deck_tabs.js")
    check(
        "TAB SMOKE: FILL_TABS names studio runs orders gitur forge crucible",
        all(n + ":" in tabs for n in (
            "studio", "runs", "orders", "gitur", "forge", "crucible")),
        "orders_in_fill=%s" % ("orders:" in tabs),
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
