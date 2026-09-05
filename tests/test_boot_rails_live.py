#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LIVE PROBE: the vendor half of boot rails, split out on 2026-08-30.

These are the assertions that genuinely need `sgh-api`/`gem-api`/`gw-api`/`oa-api`
to answer. They cannot pass on a machine with no incumbent tree, and fusing them
to the offline contract made a green suite unreachable by construction -- so the
suite stayed red, and red stopped carrying information.

The skip here is NARROW on purpose. A test that always skips is worth less than
no test at all, because it looks like coverage. This one skips only when the
incumbent root cannot be resolved -- i.e. the rails are structurally absent. If
the incumbent tree IS configured and the node rails still do not register, that
is a FAIL, not a skip.

Exit codes: 0 = passed or honestly skipped, 1 = failed.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_node_rails import resolve_incumbent_root  # noqa: E402

_NODE = ("sgh-api", "gem-api", "gw-api", "oa-api")


def main() -> int:
    root = install(Path(tempfile.mkdtemp(prefix="cosmos_boot_live_")) / "live",
                   tree_id="boot-rails-live")
    k = Kernel(root, worker="core")

    incumbent = resolve_incumbent_root(k.paths)
    if not incumbent:
        # Structurally unreachable: no BTS incumbent tree configured, so the node
        # rails cannot import, cannot probe, and correctly do not register.
        print("SKIPPED  no incumbent tree resolved "
              "(set COSMOS_BTS_ROOT or config bts_root to run this probe)")
        print("live_value: " + json.dumps({"incumbent_root": None,
                                           "skipped_reason": "NO_INCUMBENT"}))
        return 0

    st = k.registry.state()
    missing = [lid for lid in _NODE if lid not in st]
    reg_dir = k.paths.role("registry")
    disk = {}
    rails_p = reg_dir / "rails.json"
    if rails_p.is_file():
        disk = json.loads(rails_p.read_text(encoding="utf-8"))
    nodes = set(disk.get("nodes") or [])

    results = [
        ("incumbent tree resolved", True, incumbent),
        ("all four node rails registered after boot", not missing,
         f"missing={missing}"),
        ("proven-live projection carries the node rails",
         set(_NODE) <= nodes, f"nodes={sorted(nodes)}"),
    ]
    bad = [r for r in results if not r[1]]
    for label, ok, detail in results:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}  [{detail}]")
    print("live_value: " + json.dumps({
        "incumbent_root": incumbent,
        "registered": sorted(st),
        "proven_live_nodes": sorted(nodes),
    }, sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(results) - len(bad)}/{len(results)}  (live vendor probe)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
