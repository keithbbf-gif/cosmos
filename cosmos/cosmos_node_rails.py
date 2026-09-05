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

The incumbent tree is resolved from COSMOS_BTS_ROOT or config/node_rails.json
`bts_root` (via CosmosPaths when given). Never a drive literal.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

CONFIG_NAME = "node_rails.json"
INCUMBENT_ENV = "COSMOS_BTS_ROOT"


def resolve_incumbent_root(paths=None) -> str | None:
    """Incumbent BTS tree from env or COSMOS config. Never a drive literal.

    Missing config is None (UNREACHABLE on import), not a guessed path.
    """
    env = (os.environ.get(INCUMBENT_ENV) or "").strip()
    if env:
        return env
    if paths is None:
        return None
    cfg = getattr(paths, "config", None)
    if not callable(cfg):
        return None
    for name in (CONFIG_NAME, "node_worker.json"):
        p = cfg(name)
        try:
            if not Path(p).exists():
                continue
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            continue
        if isinstance(d, dict):
            root = str(d.get("bts_root") or "").strip()
            if root:
                return root
    return None


def fail_closed_empty(r: dict) -> dict:
    """ONE empty-body rule: whitespace/empty text is FAILED, never rc=0."""
    if str(r.get("text") or "").strip():
        if r.get("ok") and r.get("rc") is None:
            r["rc"] = 0
        return r
    r["ok"] = False
    if r.get("kind") in (None, "API", "OK", "CLI"):
        r["kind"] = "EMPTY_OUTPUT"
    if not r.get("rc"):
        r["rc"] = 2
    r.setdefault("detail", r.get("reason") or "empty_stdout")
    return r


class NodeRail:
    """Base: wraps one incumbent node client. kind=API (a metered model rail). probe()
    imports the incumbent and asks it the cheapest liveness question; dispatch() sends a
    prompt. A missing incumbent is UNREACHABLE, not a fabricated OK."""
    kind = "API"

    def __init__(self, module_name: str, metered_usd: float = 0.02, *,
                 bts_root: str | None = None, paths=None):
        self.module_name = module_name
        self.metered_usd = metered_usd
        self._mod = None
        self._bts_root = (bts_root if bts_root is not None
                          else resolve_incumbent_root(paths))

    def _load(self):
        if self._mod is None:
            root = self._bts_root
            if root and root not in sys.path:
                sys.path.insert(0, root)
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
                    "detail": f"{self.module_name}: {e}",
                    "text": "", "rc": 2, "node": self.module_name,
                    "model": self.module_name}
        ask = getattr(mod, "ask", None)
        if ask is None:
            return {"ok": False, "kind": "BROKE",
                    "detail": f"{self.module_name} has no ask()",
                    "text": "", "rc": 2, "node": self.module_name,
                    "model": self.module_name}
        try:
            r = ask(payload["prompt"], **payload.get("kwargs", {}))
        except Exception as e:                                        # noqa: BLE001
            return {"ok": False, "kind": "BROKE",
                    "detail": f"{self.module_name}.ask raised: {e}",
                    "text": "", "rc": 2, "stderr_tail": str(e),
                    "node": self.module_name, "model": self.module_name}
        if isinstance(r, dict):
            text = r.get("text") or r.get("full_text") or ""
            out = {"ok": bool(r.get("ok", True)), "kind": r.get("kind") or "API",
                   "text": text, "usd": r.get("usd"),
                   "node": r.get("node") or self.module_name,
                   "model": r.get("model") or r.get("node") or self.module_name,
                   "detail": r.get("detail") or r.get("reason"),
                   "rc": r.get("rc"), "via": r.get("via"),
                   "stderr_tail": str(r.get("stderr_tail") or r.get("stderr") or ""),
                   "reason": r.get("reason")}
        else:
            out = {"ok": True, "kind": "API", "text": str(r),
                   "node": self.module_name, "model": self.module_name}
        return fail_closed_empty(out)


def register_node_rails(registry, adapters: dict, spend_gate=None,
                        src: str = "core", dst: str = "models",
                        paths=None) -> dict:
    """Register every available node rail into a Registry with a live probe attached,
    and populate the Dispatcher's adapter map. Returns the built adapter set.

    CONTRACT (corrected 2026-08-30 — the prior docstring described a design that was
    changed and cost an audit a regression): a rail is registered here only into the
    registry it is HANDED. On the Kernel boot path it is handed _NoClaim(), so boot
    wires adapters + budgets ONLY and registration is deferred to the prove() gate --
    'a node that does not answer is not registered' (Registry.file_runtime), which
    tests/test_boot_attach.py pins. Do not "fix" this by passing the real registry:
    that registers rails whose incumbent never imported, and a failed rail then shows
    up in live_nodes() claiming presence it has not earned.

    'Registration is not capability' still holds where registration DOES happen:
    verified stays None until a probe measures it."""
    specs = [
        # (link_id, incumbent module, rail_type, policy_rank, metered_usd, budget)
        ("sgh-api", "bts_sgh", "API", 0, 0.02, 10.0),
        ("gem-api", "bts_gem", "API", 0, 0.03, 300.0),   # the expiring Vertex credit
        ("gw-api", "bts_gw", "API", 0, 0.001, 5.0),
        ("oa-api", "bts_oa_api", "API", 0, 0.05, 5.0),
    ]
    existing = set(registry.state())
    for link_id, mod, rtype, rank, usd, budget in specs:
        rail = NodeRail(mod, metered_usd=usd, paths=paths)
        if link_id not in existing:
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
