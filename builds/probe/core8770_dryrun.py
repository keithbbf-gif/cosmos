#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""core8770_dryrun - zero-write reproduction of the `cosmos.py serve` boot against a
COSMOS root, for the :8770 diagnosis. Read-only kernel + a faithful dry-run of
Kernel.compose_rails minus every ledger write, then Service() on an EPHEMERAL port
(never 8770) so no competing server is ever started against the live root.

    py -3.14 builds/probe/core8770_dryrun.py --root V:/A/Ai/COSMOS/live

No hard-coded paths: --root is required and resolved by CosmosPaths sentinel content.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "cosmos"))

RAILS = (
    ("node_rails", "cosmos_node_rails", "register_node_rails", False),
    ("cursor-api", "cosmos_cursor_rail", "attach_to_kernel", True),
    ("codex-cli", "cosmos_codex_rail", "attach_to_kernel", True),
    ("playwright-dom", "cosmos_playwright_rail", "attach_to_kernel", True),
    ("firecrawl-web", "cosmos_firecrawl_rail", "attach_to_kernel", True),
    ("claude-cli", "cosmos_claude_rail", "attach_to_kernel", True),
)


class _NoClaim:
    """Kernel.compose_rails' own boot-time registry stand-in (adapters + budgets only)."""

    def state(self):
        return {}

    def register(self, *_a, **_k):
        return None

    def attach_probe(self, *_a, **_k):
        return None


def main() -> int:
    ap = argparse.ArgumentParser(prog="core8770_dryrun")
    ap.add_argument("--root", required=True)
    a = ap.parse_args()

    from cosmos_kernel import Kernel
    out: dict = {"root": a.root}

    k = Kernel(a.root, worker="probe-ro", read_only=True)
    out["read_only_boot"] = {"ready": k.ready,
                             "tree_id": k.paths.sentinel.tree_id,
                             "rails_compose": k.rails_compose,
                             "dispatcher": k.dispatcher}

    adapters: dict = {}
    composed: list = []
    warnings: dict = {}
    for name, mod, attr, attach in RAILS:
        try:
            fn = getattr(importlib.import_module(mod), attr)
            if attach:
                fn(k, adapters, boot_compose=True)
            else:
                # spend_gate=None: set_budget() would append BUDGET_SET to the LIVE ledger.
                fn(_NoClaim(), adapters, spend_gate=None, paths=k.paths)
            composed.append(name)
        except Exception as e:                                        # noqa: BLE001
            warnings[name] = f"{type(e).__name__}: {e}"
    out["dryrun_compose"] = {"composed": composed, "warnings": warnings,
                             "adapters": sorted(adapters)}

    from cosmos_rails import Dispatcher
    d = Dispatcher(k.registry, adapters, k.ledger, spend=k.spend)
    out["dispatcher_constructs"] = type(d).__name__

    # Service on port 0 - an ephemeral bind, closed at once. NEVER 8770.
    from cosmos_service import Service
    svc = Service(k, host="127.0.0.1", port=0)
    out["service_constructs"] = {"scheme": svc.scheme, "ephemeral_port": svc.port}
    svc.httpd.server_close()
    out["service_closed"] = True

    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
