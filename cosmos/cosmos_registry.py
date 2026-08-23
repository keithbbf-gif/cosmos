#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_registry - nodes/rails/links as FIRST-CLASS entities with DATED behavioral
probes (F5 builder). Total connectivity is registry-driven: CLI/API/DOM/CHAT/OTHER are
link types; DOM-first is POLICY DATA; nothing holds verified status without a dated probe.

Registry-reality reconciliation (scar R5): register() records a claim; only probe()
records a MEASUREMENT; status is always (claim, last_measurement, age). UNREACHABLE is
recorded, never assumed - and never silently upgraded.
"""
from __future__ import annotations

import time
from typing import Callable, Optional

from cosmos_ledger import Ledger

RAIL_TYPES = {"CLI", "API", "DOM", "CHAT", "OTHER"}


class RegError(RuntimeError):
    """kind in {UNKNOWN_LINK, BAD_TYPE, NO_PROBE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


class Registry:
    """Backed by the SAME authority pattern: every registration and every probe result
    is a ledger event; current state is a projection."""

    def __init__(self, ledger: Ledger, clock=time.time):
        self.ledger = ledger
        self._clock = clock
        self._probes: dict[str, Callable[[], tuple[bool, str]]] = {}

    # ---------------- claims ----------------
    def register(self, link_id: str, rail_type: str, src: str, dst: str,
                 policy_rank: int = 0) -> None:
        if rail_type not in RAIL_TYPES:
            raise RegError("BAD_TYPE", f"{rail_type!r} not in {sorted(RAIL_TYPES)}")
        self.ledger.append("LINK_REGISTERED",
                           {"link_id": link_id, "rail_type": rail_type,
                            "src": src, "dst": dst, "policy_rank": policy_rank})

    def attach_probe(self, link_id: str, probe: Callable[[], tuple[bool, str]]) -> None:
        """A probe is code, not prose: () -> (ok, detail)."""
        self._probes[link_id] = probe

    # ---------------- measurements ----------------
    def probe(self, link_id: str) -> dict:
        st = self.state()
        if link_id not in st:
            raise RegError("UNKNOWN_LINK", link_id)
        if link_id not in self._probes:
            raise RegError("NO_PROBE",
                           f"{link_id} has no attached probe - a link nobody can probe "
                           f"can never be verified, and saying so beats pretending")
        try:
            ok, detail = self._probes[link_id]()
        except Exception as e:                                        # noqa: BLE001
            ok, detail = False, f"probe raised {type(e).__name__}: {e}"
        self.ledger.append("PROBE_RESULT",
                           {"link_id": link_id, "ok": bool(ok), "detail": str(detail)[:300]})
        return {"link_id": link_id, "ok": ok, "detail": detail}

    def probe_all(self) -> dict:
        """The rails matrix, MEASURED: every registered link probed now; UNREACHABLE
        recorded for links without probes rather than skipped silently."""
        out = {}
        for lid in self.state():
            try:
                out[lid] = self.probe(lid)
            except RegError as e:
                self.ledger.append("PROBE_RESULT",
                                   {"link_id": lid, "ok": False,
                                    "detail": f"UNPROBEABLE: {e.kind}"})
                out[lid] = {"link_id": lid, "ok": False, "detail": e.kind}
        return out

    # ---------------- projection ----------------
    def state(self) -> dict:
        def fold(s, rec):
            p, e = rec["payload"], rec["event"]
            if e == "LINK_REGISTERED":
                s[p["link_id"]] = {"claim": p, "last_probe": None, "ok": None}
            elif e == "PROBE_RESULT" and p.get("link_id") in s:
                s[p["link_id"]]["last_probe"] = rec["t"]
                s[p["link_id"]]["ok"] = p["ok"]
            return s
        return self.ledger.project(fold, {})

    def matrix(self) -> list[dict]:
        """Every link with claim + measurement + AGE. A never-probed link reports
        verified=None (UNKNOWN), never True - registration is not capability."""
        now = self._clock()
        rows = []
        for lid, v in sorted(self.state().items()):
            rows.append({"link_id": lid,
                         "rail_type": v["claim"]["rail_type"],
                         "route": f"{v['claim']['src']}->{v['claim']['dst']}",
                         "verified": v["ok"],
                         "age_s": (now - v["last_probe"]) if v["last_probe"] else None})
        return rows

    def route(self, src: str, dst: str) -> list[dict]:
        """Candidate links for a route, DOM-first by policy_rank then rail preference.
        Only links whose LAST MEASUREMENT was ok are candidates - policy chooses among
        the measured-alive, never among the claimed."""
        pref = {"DOM": 0, "CLI": 1, "API": 2, "CHAT": 3, "OTHER": 4}
        st = self.state()
        live = [v for v in st.values()
                if v["claim"]["src"] == src and v["claim"]["dst"] == dst and v["ok"]]
        return sorted((v["claim"] for v in live),
                      key=lambda c: (-c["policy_rank"], pref[c["rail_type"]]))
