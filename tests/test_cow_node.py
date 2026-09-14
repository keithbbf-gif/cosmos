#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic pins: CoW node row is honest (vendor model, stale RED, UNMEASURED)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_cow_node import (  # noqa: E402
    INDEPENDENCE_NOTE, LINK_ID, ROLE, attach_to_nodemap, bind_row,
)

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    empty = bind_row(None)
    check("unmeasured COW is explicit, age_s is None never 0",
          lambda: empty["proof_state"] == "UNMEASURED"
          and empty["verified"] is None
          and empty["model"] == ""
          and empty["age_s"] is None
          and empty["id"] == LINK_ID)
    check("role is orch not reading",
          lambda: empty["role"] == ROLE and empty["does_not"] == "read")
    check("independence note names SGH+GBW",
          lambda: empty["independence"]["note"] == INDEPENDENCE_NOTE
          and empty["independence"]["same_family"] == ["SGH", "GBW"])

    live = bind_row({
        "ok": True, "verified": True, "model": "claude-opus-4-5",
        "rc": 0, "body_bytes": 4, "age_s": 12.0,
        "model_source": "vendor-emitted JSON model (Claude/Cowork seat)",
    })
    check("live proof quotes vendor model and verified True",
          lambda: live["verified"] is True and live["proof_state"] == "LIVE"
          and live["model"] == "claude-opus-4-5" and live["age_s"] == 12.0)

    stale = bind_row({
        "ok": True, "verified": False, "proof_state": "STALE",
        "model": "claude-opus-4-5", "rc": 0, "body_bytes": 4, "age_s": 9000.0,
    })
    check("stale proof is STALE + verified False (not a green memory)",
          lambda: stale["proof_state"] == "STALE" and stale["verified"] is False
          and stale["model"] == "claude-opus-4-5")

    aged = bind_row({
        "ok": True, "verified": True, "model": "claude-opus-4-5",
        "rc": 0, "body_bytes": 4, "age_s": 4000.0,
    }, ttl_s=3600.0)
    check("age past TTL flips LIVE claim to STALE",
          lambda: aged["proof_state"] == "STALE" and aged["verified"] is False)

    body = attach_to_nodemap({"ok": True, "topology": {"nodes": []}}, None)
    check("nodemap attach always lists COW (empty = explicit UNMEASURED)",
          lambda: body["cow"]["proof_state"] == "UNMEASURED"
          and any(n.get("id") == "cow" for n in body["topology"]["nodes"])
          and body["cow"]["independence"]["note"] == INDEPENDENCE_NOTE)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (COW node honesty)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_cow_node():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
