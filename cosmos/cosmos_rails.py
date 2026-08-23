#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_rails - THE RAIL ADAPTERS + DOM-INTO-SCHEDULER (F5 builder). Closes M6: DOM
was a sort key; now it is a dispatchable rail the scheduler drives, alongside CLI/API/
CHAT/OTHER, every one probed and typed.

A RAIL ADAPTER is: kind (CLI/API/DOM/CHAT/OTHER) · a probe() -> (ok, detail) ·
a dispatch(payload) -> {ok, kind, ...}. The Dispatcher picks a live link for a route
(DOM-first by policy), reserves budget through the spend gate if the link is metered,
runs the adapter, and records a typed result. A dead DOM browser is SESSION_EXPIRED/
UNREACHABLE, never a silent fallback to API.
"""
from __future__ import annotations

import subprocess
import time
from typing import Callable

from cosmos_registry import Registry
from cosmos_dom import DomWorker, DomError


class RailError(RuntimeError):
    """kind in {NO_LIVE_LINK, RAIL_FAILED, NOT_PERMITTED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


class CliRail:
    """A CLI rail: dispatch runs an argv through the platform adapter. probe checks the
    binary exists."""
    kind = "CLI"

    def __init__(self, binary: str):
        self.binary = binary

    def probe(self):
        import shutil
        return (bool(shutil.which(self.binary)),
                f"{self.binary} {'on PATH' if shutil.which(self.binary) else 'ABSENT'}")

    def dispatch(self, payload: dict) -> dict:
        from cosmos_platform import run
        r = run([self.binary] + payload.get("args", []),
                timeout_s=payload.get("timeout_s", 60))
        return {"ok": r["rc"] == 0, "kind": "CLI", "rc": r["rc"],
                "out": r["out"][:2000]}


class DomRail:
    """A DOM rail: dispatch runs a contained DOM attempt. The driver is injected (real
    browser in 6b; fake in tests). This is the M6 wiring - DOM is now a rail the
    dispatcher can select and run, with typed failure."""
    kind = "DOM"

    def __init__(self, dom_worker: DomWorker):
        self.worker = dom_worker

    def probe(self):
        try:
            ok = self.worker.driver.session_ok()
            return ok, "session live" if ok else "session not valid"
        except Exception as e:                                        # noqa: BLE001
            return False, f"probe raised {type(e).__name__}"

    def dispatch(self, payload: dict) -> dict:
        r = self.worker.run_attempt(payload["job_id"], payload["url"],
                                    require_session=payload.get("require_session", False))
        return r                       # already {ok, kind, ...} typed


class ApiRail:
    kind = "API"

    def __init__(self, fn: Callable[[dict], dict], metered_usd: float = 0.0):
        self.fn = fn
        self.metered_usd = metered_usd

    def probe(self):
        return True, "api adapter present (liveness is per-call)"

    def dispatch(self, payload: dict) -> dict:
        return self.fn(payload)


class Dispatcher:
    """Selects a live link for a route and runs its adapter. DOM-first is registry
    policy; a dead link is skipped only if another LIVE link exists, and the skip is
    typed - never a silent downgrade."""

    def __init__(self, registry: Registry, adapters: dict, ledger, spend=None,
                 clock=time.time):
        self.registry = registry
        self.adapters = adapters            # link_id -> adapter
        self.ledger = ledger
        self.spend = spend
        self._clock = clock

    def dispatch(self, src: str, dst: str, payload: dict) -> dict:
        candidates = self.registry.route(src, dst)   # live, DOM-first
        if not candidates:
            raise RailError("NO_LIVE_LINK",
                            f"no measured-live link {src}->{dst} - registration is not "
                            f"capability; probe first")
        for claim in candidates:
            lid = claim["link_id"]
            adapter = self.adapters.get(lid)
            if adapter is None:
                continue
            self.ledger.append("RAIL_DISPATCH",
                               {"link_id": lid, "kind": claim["rail_type"],
                                "src": src, "dst": dst})
            # metered rail -> through the spend breaker
            if self.spend and getattr(adapter, "metered_usd", 0):
                try:
                    result = self.spend.guarded_call(
                        lid, adapter.metered_usd, lambda: adapter.dispatch(payload))
                except Exception as e:                                # noqa: BLE001
                    self.ledger.append("RAIL_RESULT",
                                       {"link_id": lid, "ok": False,
                                        "detail": f"spend-gated: {e}"})
                    raise RailError("NOT_PERMITTED", str(e)) from e
            else:
                result = adapter.dispatch(payload)
            self.ledger.append("RAIL_RESULT",
                               {"link_id": lid, "ok": result.get("ok"),
                                "kind": result.get("kind")})
            if result.get("ok"):
                return result
            # DOM typed failure: record it, and only continue to the NEXT live link if
            # policy permits fallback (explicit, audited - never silent).
            if result.get("kind") in ("UNREACHABLE", "SESSION_EXPIRED", "AUTH_REQUIRED"):
                self.ledger.append("RAIL_FALLBACK",
                                   {"from": lid, "reason": result["kind"],
                                    "detail": "explicit audited fallback to next live link"})
                continue
            raise RailError("RAIL_FAILED",
                            f"{lid} failed: {result.get('detail', result.get('kind'))}")
        raise RailError("NO_LIVE_LINK", "all candidate links failed or absent")