#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_node_rails - THE ADAPTED RAILS (F5 builder). Port-plan disposition ADAPTED:
the incumbent node clients (bts_sgh/gem/gw/oa_api/cursor) become COSMOS rail adapters,
so the Dispatcher can reach live models through the registry — DOM-first, spend-gated,
typed. This is what turns a tested skeleton into a working mesh.

DESIGN: each adapter WRAPS the incumbent module by import (the incumbent runs natively
and keeps its own ledger — we do not reimplement it, we drive it). An adapter that
cannot import its incumbent is REGISTERED-BUT-UNREACHABLE, never a fake success. Metered
adapters carry metered_usd so cosmos_rails routes them through the spend breaker. The
DOM lane is preferred by policy_rank; the API adapters are the fallback, exactly as the
ratified goal says ("DOM is the default, the API is the fallback").
"""
from __future__ import annotations

import sys
from pathlib import Path

# the incumbent modules live in the live BTS tree; add it to the path at construction,
# never at import (import-time side effects are the resolver scar).
_BTS = r"V:\Ai\BTS_MESH"


class NodeRail:
    """Base: wraps one incumbent node client. kind=API (a metered model rail). probe()
    imports the incumbent and asks it the cheapest liveness question; dispatch() sends a
    prompt. A missing incumbent is UNREACHABLE, not a fabricated OK."""
    kind = "API"

    def __init__(self, module_name: str, metered_usd: float = 0.02):
        self.module_name = module_name
        self.metered_usd = metered_usd
        self._mod = None

    def _load(self):
        if self._mod is None:
            if _BTS not in sys.path:
                sys.path.insert(0, _BTS)
            self._mod = __import__(self.module_name)
        return self._mod

    def probe(self):
        try:
            self._load()
            return True, f"{self.module_name} importable (liveness is per-call)"
        except Exception as e:                                        # noqa: BLE001
            return False, f"UNREACHABLE: {self.module_name} did not import: {e}"

    def dispatch(self, payload: dict) -> dict:
        try:
            mod = self._load()
        except Exception as e:                                        # noqa: BLE001
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": f"{self.module_name}: {e}"}
        ask = getattr(mod, "ask", None)
        if ask is None:
            return {"ok": False, "kind": "BROKE",
                    "detail": f"{self.module_name} has no ask()"}
        try:
            r = ask(payload["prompt"], **payload.get("kwargs", {}))
        except Exception as e:                                        # noqa: BLE001
            return {"ok": False, "kind": "BROKE",
                    "detail": f"{self.module_name}.ask raised: {e}"}
        # incumbent returns a dict {ok,text,...} or a str — normalize
        if isinstance(r, dict):
            return {"ok": r.get("ok", True), "kind": "API",
                    "text": r.get("text") or r.get("full_text") or "",
                    "usd": r.get("usd"), "node": self.module_name}
        return {"ok": True, "kind": "API", "text": str(r), "node": self.module_name}


def register_node_rails(registry, adapters: dict, spend_gate=None,
                        src: str = "core", dst: str = "models") -> dict:
    """Register every available node rail into a Registry with a live probe attached,
    and populate the Dispatcher's adapter map. Returns the built adapter set. A rail
    whose incumbent will not import is registered UNREACHABLE (probe records it), NOT
    dropped — 'registration is not capability', and absence must be visible."""
    specs = [
        # (link_id, incumbent module, rail_type, policy_rank, metered_usd, budget)
        ("sgh-api", "bts_sgh", "API", 0, 0.02, 10.0),
        ("gem-api", "bts_gem", "API", 0, 0.03, 300.0),   # the expiring Vertex credit
        ("gw-api", "bts_gw", "API", 0, 0.001, 5.0),
        ("oa-api", "bts_oa_api", "API", 0, 0.05, 5.0),
    ]
    for link_id, mod, rtype, rank, usd, budget in specs:
        rail = NodeRail(mod, metered_usd=usd)
        registry.register(link_id, rtype, src, dst, policy_rank=rank)
        registry.attach_probe(link_id, rail.probe)
        adapters[link_id] = rail
        if spend_gate is not None:
            # budget keyed by link_id so the breaker gates THIS rail
            try:
                spend_gate.set_budget(link_id, budget)
            except Exception:                                        # noqa: BLE001
                pass
    return adapters
