#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic pins for cDeck inspector chrome (EVT-1) and pulse map (PULSE-1).

EVT-1: kdash/index.html must declare the inspector chrome class (.finspect)
       and tell the user that rows are clickable and that scrolling pauses
       auto-scroll.  Both are static source checks — no server required.

PULSE-1: the nodemap is built from the rails registry only.  An event
       arriving with an arbitrary node name MUST NOT mint a new entry on
       the map.  Verified by emitting ledger events whose payload.node
       values are not in the registry, then driving _nodemap_overlay_kernel
       and confirming the phantom names are absent from the result.

Run:  py -3.14 builds/cdeck/test_deck_features.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
KDASH = REPO / "kdash" / "index.html"
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_kernel import Kernel, install          # noqa: E402
from cosmos_paths import CosmosPaths               # noqa: E402
from cosmos_service import _nodemap_overlay_kernel  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                          # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _evt1_checks() -> None:
    src = KDASH.read_text(encoding="utf-8")

    # The events panel must indicate rows are clickable (tooltip on .fmore)
    # and that scrolling pauses auto-scroll (feedPinned / "jump to live" chip).
    check(
        "EVT-1 the panel says the row is clickable and that scrolling pauses",
        lambda: (
            'title="click the row for its payload"' in src
            and "feedPinned" in src
        ),
    )

    # The inspector chrome (.finspect) must be declared in the source so that
    # toggleInspect() can insert it into the live DOM on row click.
    check(
        "EVT-1 the inspector chrome exists in the DOM",
        lambda: ".finspect" in src,
    )


def _pulse1_check() -> None:
    td = Path(tempfile.mkdtemp(prefix="deck_pulse_"))
    root = install(td / "live", tree_id="deck-pulse-test")
    k = Kernel(root, worker="core")
    paths = CosmosPaths(root)

    # Seed the on-disk registry with exactly one known node.
    now = time.time()
    reg_p = paths.role("registry", "rails.json")
    reg_p.parent.mkdir(parents=True, exist_ok=True)
    reg_p.write_text(
        json.dumps({
            "schema": "cosmos-registry/1",
            "measured_at": now,
            "count": 1,
            "nodes": ["gem-api"],
            "matrix": [{
                "link_id": "gem-api", "rail_type": "API",
                "route": "core->models", "verified": True,
                "last_probe": now, "rc": 0,
            }],
        }),
        encoding="utf-8",
    )

    # Emit ledger events that carry node names NOT in the registry.
    # These would be returned by GET /api/v1/events in a real session.
    phantom = {"phantom-a", "phantom-b", "phantom-c"}
    k.ledger.append("BOOT_VERIFIED", {"node": "phantom-a", "worker": "test"})
    k.ledger.append("COMMAND_HANDLED", {"node": "phantom-b", "ok": True})
    k.ledger.append("HEALTH_BOARD", {"node": "phantom-c", "verdict": "GREEN"})

    # Construct the nodemap body as the panel handler would (gem-api only).
    nodemap_body = {
        "ok": True,
        "tree_id": "deck-pulse-test",
        "topology": {"nodes": [{"id": "gem-api"}]},
        "registry": {
            "available": True,
            "matrix": [{
                "link_id": "gem-api", "rail_type": "API", "verified": True,
            }],
        },
    }

    # _nodemap_overlay_kernel reads from the disk registry / kernel.registry
    # only — never from the ledger event stream.  Phantom names must be absent.
    result = _nodemap_overlay_kernel(k, nodemap_body)
    map_nodes = (
        {r.get("link_id")
         for r in (result.get("registry") or {}).get("matrix") or []}
        | {n.get("id")
           for n in (result.get("topology") or {}).get("nodes") or []}
    ) - {None}

    _ok = not (map_nodes & phantom) and "gem-api" in map_nodes
    check(
        "PULSE-1 a node the map does not already hold is NEVER created by an event",
        lambda: _ok,
    )


def main() -> int:
    _evt1_checks()
    _pulse1_check()

    bad = [(lbl, err) for lbl, ok, err in RESULTS if not ok]
    for lbl, ok, err in RESULTS:
        print("  %s  %s%s" % (
            "OK  " if ok else "FAIL", lbl,
            ("  [" + err + "]") if err else "",
        ))
    print("SELFTEST %s - %d checks" % (
        "PASS" if not bad else "FAIL", len(RESULTS),
    ))
    return 0 if not bad else 1


def test_deck_features() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
