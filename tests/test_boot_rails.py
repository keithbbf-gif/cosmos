#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OFFLINE CONTRACT: what a writing Kernel boot guarantees with no vendor rails.

Split from the original combined test on 2026-08-30. The original asserted that
`sgh-api`/`gem-api`/`gw-api`/`oa-api` are in the registry and that
`registry/rails.json` has a non-empty matrix -- but `Registry.file_runtime`
projects only PROVEN-LIVE nodes ("a node that does not answer is not
registered"), and `register_node_rails` is handed `_NoClaim()` at boot precisely
so an unproven rail claims nothing. Those assertions therefore required live
vendor APIs answering, which made a green suite unreachable on any machine
without credentials -- and a gate that can never be green teaches you to ignore
it, which is how a 3-day route stall went unnoticed.

The live half now lives in `test_boot_rails_live.py`, which skips honestly when
the incumbent tree is absent and FAILS when it is present but the rails do not
register.

What boot actually promises, with no network and no keys, is asserted here.
"""
from __future__ import annotations

import json
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    root = install(Path(tempfile.mkdtemp(prefix="cosmos_boot_rails_")) / "live",
                   tree_id="boot-rails")
    k = Kernel(root, worker="core")
    st = k.registry.state()

    check("boot leaves a NON-EMPTY registry", lambda: bool(st))

    # The load-bearing invariant: composing a rail is not proving one.
    check("nothing boot-composed claims capability it has not measured",
          lambda: all(r["verified"] is None for r in k.registry.matrix()))

    reg_dir = k.paths.role("registry")
    rails_p = reg_dir / "rails.json"
    nodes_p = reg_dir / "nodes.json"
    check("registry/rails.json written", lambda: rails_p.is_file())
    check("registry/nodes.json written", lambda: nodes_p.is_file())

    disk = json.loads(rails_p.read_text(encoding="utf-8")) if rails_p.is_file() else {}

    # A projection with nothing proven-live is still a WELL-FORMED projection.
    # Demanding it be non-empty is what required live vendors; demanding it be
    # well-formed and self-consistent is the contract that actually holds.
    check("projection is well-formed even when nothing proved live",
          lambda: {"schema", "measured_at", "count", "nodes", "matrix"} <= set(disk))
    check("projection count agrees with its own nodes list",
          lambda: disk.get("count") == len(disk.get("nodes") or []))
    check("projection matrix agrees with its own nodes list",
          lambda: len(disk.get("matrix") or []) == len(disk.get("nodes") or []))
    check("rails.json and nodes.json are the same projection",
          lambda: nodes_p.is_file()
          and json.loads(nodes_p.read_text(encoding="utf-8")).get("nodes")
          == disk.get("nodes"))

    svc = Service(k, port=0)
    svc.serve_background()
    try:
        bodies = {}
        for path in ("/api/v1/rails", "/api/v1/nodes"):
            req = urllib.request.Request(f"http://127.0.0.1:{svc.port}{path}")
            req.add_header("Authorization", "Bearer " + svc.token)
            with urllib.request.urlopen(req, timeout=10) as resp:
                bodies[path] = (resp.status,
                                json.loads(resp.read().decode("utf-8")))
        check("GET /api/v1/rails serves 200",
              lambda: bodies["/api/v1/rails"][0] == 200)
        check("GET /api/v1/nodes serves 200",
              lambda: bodies["/api/v1/nodes"][0] == 200)
        check("both endpoints carry a matrix key",
              lambda: "matrix" in bodies["/api/v1/rails"][1]
              and "matrix" in bodies["/api/v1/nodes"][1])
        check("served link ids agree between /rails and /nodes",
              lambda: {r.get("link_id") for r in bodies["/api/v1/rails"][1]["matrix"]}
              == {r.get("link_id") for r in bodies["/api/v1/nodes"][1]["matrix"]})
    finally:
        svc.shutdown()

    bad = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    print("live_value: " + json.dumps({
        "registered": sorted(st),
        "proven_live_nodes": sorted(disk.get("nodes") or []),
        "verified_claims": [r["verified"] for r in k.registry.matrix()],
    }, sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(RESULTS) - len(bad)}/{len(RESULTS)}  "
          f"(offline contract; live vendor half is test_boot_rails_live.py)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
