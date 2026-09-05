#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: F-56 LAN federation seam (SRV1 + T7/T7920).

The named machines exist as symbols. Reachability is measured, never
quoted. federation_ready() stays False while blockers stand.

Does not modify kernel/ledger/sched/service. Does not invent a host.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_identity import (  # noqa: E402
    LAN_NODES, FederationError, federation_blockers, federation_ready,
    lan_node, probe_lan_node,
)

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _kind(fn):
    try:
        fn()
    except FederationError as e:
        return e.kind
    return None


def main() -> int:
    check("LAN_NODES has SRV1", lambda: "SRV1" in LAN_NODES)
    check("LAN_NODES T7 alias is T7920",
          lambda: LAN_NODES["T7"]["alias"] == "T7920")
    check("lan_node(SRV1) status is not_installed",
          lambda: lan_node("SRV1")["status"] == "not_installed"
          and lan_node("SRV1")["host"] is None)
    check("lan_node(T7920) resolves to T7",
          lambda: lan_node("T7920")["id"] == "T7"
          and lan_node("T7")["cores"] == 56)
    check("unknown node is UNKNOWN_NODE",
          lambda: _kind(lambda: lan_node("NOPE")) == "UNKNOWN_NODE")

    p = probe_lan_node("SRV1")
    check("probe SRV1 is NO_HOST, not READY",
          lambda: p["kind"] == "NO_HOST" and p["ok"] is False
          and p["reachable"] is False)
    p7 = probe_lan_node("T7920")
    check("probe T7920 is NO_HOST",
          lambda: p7["kind"] == "NO_HOST" and p7["id"] == "T7")

    rec = dict(LAN_NODES["SRV1"])
    rec["host"] = "192.0.2.8"
    # Mutating the live table would lie. Copy, then call with a host via
    # a one-off: probe uses lan_node() which reads LAN_NODES. Injected
    # transport is only consulted when host is set, so a fake host on the
    # live table is forbidden. Prove transport is unused on NO_HOST:
    called = []
    probe_lan_node("SRV1", transport=lambda h: called.append(h) or {"ok": True})
    check("NO_HOST does not call transport (no invented address)",
          lambda: called == [])

    check("federation_ready is False", lambda: federation_ready() is False)
    blockers = federation_blockers()
    check("federation blockers still 5, counted FROM THE FUNCTION",
          lambda: len(blockers) == 5)
    check("blockers name SRV1 and T7920",
          lambda: any("SRV1" in b and "T7920" in b for b in blockers))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    live_value = {
        "checks": len(RESULTS),
        "lan_ids": sorted(LAN_NODES),
        "srv1_kind": p["kind"],
        "t7_kind": p7["kind"],
        "federation_ready": federation_ready(),
        "blocker_count": len(blockers),
    }
    print("LIVE_VALUE", json.dumps(live_value))
    (REPO / "cosmos" / "_f56_federation.json").write_text(
        json.dumps({"ok": not bad, "live_value": live_value}, indent=1) + "\n",
        encoding="utf-8")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
