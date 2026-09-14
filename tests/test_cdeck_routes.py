#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GET /api/v1/fleet · /nodemap · /jukebox — Core hands off to cDeck binders.

No new measurement. A missing feed is 200 + available:false, not an empty
fleet. Ledger head must not move. Loopback is open (DT auto-connect).
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_service import Service  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_cdeck_routes_"))
    root = install(td / "live", tree_id="cdeck-routes")
    paths = CosmosPaths(root)
    now = time.time()
    feed_p = paths.role("state", "cdeck", "feed.json")
    feed_p.parent.mkdir(parents=True, exist_ok=True)
    feed_p.write_text(json.dumps({
        "schema": "cosmos-cdeck-feed/1",
        "worker": "cosmos-cdeck-feed",
        "tree_id": "cdeck-routes",
        "measured_epoch": now - 4,
        "pause": {"state": "RUNNING", "present": False},
        "queue": {"manifests": 2},
        "clocks": {
            "pulse_heartbeat.json": {
                "worker": "cosmos-pulse", "pid": 7, "alive": True,
                "state": "RUNNING", "last_run_epoch": now - 3,
            },
        },
        "snapshots": {"health": {"verdict": "GREEN"}},
    }), encoding="utf-8")
    k = Kernel(root, worker="core")
    # Kernel compose_rails rewrites registry/rails.json. Plant AFTER boot.
    rails_p = paths.role("registry", "rails.json")
    rails_p.parent.mkdir(parents=True, exist_ok=True)
    rails_p.write_text(json.dumps({
        "schema": "cosmos-registry/1",
        "measured_at": now - 20,
        "count": 1,
        "nodes": ["gem-api"],
        "note": "test",
        "matrix": [{
            "link_id": "gem-api", "rail_type": "API", "route": "core->models",
            "verified": True, "model": "gemini-2.5-flash", "rc": 0,
            "last_probe": now - 30,
        }],
    }), encoding="utf-8")
    head_before = k.ledger.head_seq()
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    base = f"http://127.0.0.1:{svc.port}"

    def get(path, tok=None):
        req = urllib.request.Request(base + path)
        if tok:
            req.add_header("Authorization", "Bearer " + tok)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    try:
        code, body = get("/api/v1/fleet")
        check("GET /fleet without a token -> 200 on loopback",
              lambda: code == 200 and body.get("ok") is True
              and body.get("tree_id") == "cdeck-routes")
        check("GET /fleet carries the feed clocks (not an empty invention)",
              lambda: body.get("fleet", {}).get("available") is True
              and any(r.get("worker") == "cosmos-pulse"
                      for r in body["fleet"].get("clocks") or []))
        code, body = get("/api/v1/nodemap")
        check("GET /nodemap is 200 and names gem-api from the registry",
              lambda: code == 200 and body.get("ok") is True
              and body.get("registry", {}).get("available") is True
              and any(n.get("id") == "gem-api"
                      for n in (body.get("topology") or {}).get("nodes") or []))
        check("GET /nodemap registry carries matrix for the browser wrap",
              lambda: isinstance(body.get("registry", {}).get("matrix"), list)
              and len(body["registry"]["matrix"]) >= 1
              and body["registry"]["matrix"][0].get("link_id"))
        rails_p.write_text(json.dumps({
            "schema": "cosmos-registry/1",
            "measured_at": now,
            "count": 0, "nodes": [], "matrix": [],
            "note": "proven-live empty",
        }), encoding="utf-8")
        code_e, body_e = get("/api/v1/nodemap")
        check("empty disk rails.json overlays kernel projection (not a blank map)",
              lambda: code_e == 200 and body_e.get("registry", {}).get("source")
              in ("kernel.projection_view", "kernel.matrix")
              and len(body_e["registry"].get("matrix") or []) >= 1)
        code, body = get("/api/v1/jukebox")
        check("GET /jukebox is 200 (rich queue fold, even if empty)",
              lambda: code == 200 and body.get("ok") is True
              and body.get("tree_id") == "cdeck-routes")
        check("GET /jukebox is not 503 CDECK_PANEL_NOT_COMPOSED (query= only on recents)",
              lambda: body.get("error") != "CDECK_PANEL_NOT_COMPOSED")
        code_r, body_r = get("/api/v1/recents")
        check("GET /recents is 200 (query= forwarded; empty is NO_SOURCE not 503)",
              lambda: code_r == 200 and body_r.get("ok") is True
              and body_r.get("tree_id") == "cdeck-routes"
              and (body_r.get("schema") == "cdeck-recents/1"
                   or body_r.get("kind") == "NO_SOURCE")
              and body_r.get("error") != "CDECK_PANEL_NOT_COMPOSED")
        check("cDeck GETs are reads — ledger head did not move",
              lambda: k.ledger.head_seq() == head_before)
        check("GET /fleet WITH the bearer still 200",
              lambda: get("/api/v1/fleet", svc.token)[0] == 200)
    finally:
        svc.shutdown()

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % (
            "OK  " if ok else "FAIL", label,
            ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks" % (
        "PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_cdeck_routes():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
