#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_registry - nodes/rails/links as FIRST-CLASS entities with DATED behavioral
probes (F5 builder). Total connectivity is registry-driven: CLI/API/DOM/CHAT/OTHER are
link types; DOM-first is POLICY DATA; nothing holds verified status without a dated probe.

Registry-reality reconciliation (scar R5): register() records a claim; only probe()
records a MEASUREMENT; status is always (claim, last_measurement, age). UNREACHABLE is
recorded, never assumed - and never silently upgraded.

Runtime map (wishlist #64): prove() is fail-closed. A node is registered at
RUNTIME only after a live rail call returns rc=0 + non-empty body + the model
that answered. A claim (register) is not a proof; an empty live/registry dir
is not identity. live/registry/{nodes,rails}.json is a rebuildable projection
of proven-live nodes; the ledger is authority.

F-25 FIX (MEASURED, 2026-08-31): the projection now applies the SAME freshness
filter route() has carried since the STAGE-7 H-05 fix. It did not, and the live
tree showed exactly the failure that fix was written to prevent:

    live/registry/rails.json  measured_at 1788160741
      claude-cli   "verified": true   "age_s": 318547.6      <- 3.69 DAYS

A proof is a DATED measurement. `verified: True` on a 3.69-day-old probe is the
projection asserting a capability the mesh has not demonstrated since Wednesday -
and nothing in the tree contradicted it, because every consumer reads `verified`
and has no reason to read `age_s`. Freshness is now a gate, not a field; and the
rows it drops are NAMED in the projection's `stale` list rather than silently
vanishing, because a projection that shrinks without saying why teaches nobody.
Regression: `builds/probe/test_registry_freshness.py` (20 checks; 13 of them FAIL
against the pre-fix module, measured 2026-08-31 - that is the proof it bites).
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from cosmos_clock import atomic_json
from cosmos_ledger import Ledger

RAIL_TYPES = {"CLI", "API", "DOM", "CHAT", "OTHER"}
RUNTIME_SCHEMA = "cosmos-registry/1"

# How long a runtime proof stays a proof. ONE number for the whole registry:
# route() defaulted to 3600 and the projection defaulted to forever, and that
# disagreement IS the defect. Deliberately equal to
# cosmos_rails_prober.NODE_PROOF_TTL_S (3600.0) - the prober re-proves on that
# cadence, so a shorter TTL here would flap rows between every probe.
# The prober does not import this and this does not import the prober; the two
# constants are pinned equal by builds/probe/test_registry_freshness.py.
PROOF_TTL_S = 3600.0


def proof_ok(rec: dict) -> bool:
    """Runtime-binding predicate. A claim, an import, or a --version is not this.

    Required: ok, rc==0, non-empty body, non-empty model that answered.
    """
    if not rec or not rec.get("ok"):
        return False
    if rec.get("rc") not in (0, "0"):
        return False
    body = str(rec.get("body") or rec.get("text") or "")
    if not body.strip():
        return False
    if not str(rec.get("model") or "").strip():
        return False
    return True


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

    def prove(self, link_id: str, rail_type: str, src: str, dst: str,
              live_call: Callable[[], dict], policy_rank: int = 0) -> dict:
        """Fail-closed runtime registration.

        live_call() must be a real rail call returning {ok, rc, body|text, model}.
        LINK_REGISTERED is appended only if proof_ok. A node that does not
        answer is NOT registered. The measurement is always ledgered.
        """
        if rail_type not in RAIL_TYPES:
            raise RegError("BAD_TYPE", f"{rail_type!r} not in {sorted(RAIL_TYPES)}")
        try:
            rec = live_call()
            if not isinstance(rec, dict):
                rec = {"ok": False, "rc": 2, "body": "", "model": "",
                       "detail": f"live_call returned {type(rec).__name__}"}
        except Exception as e:                                        # noqa: BLE001
            rec = {"ok": False, "rc": 2, "body": "", "model": "",
                   "detail": f"probe raised {type(e).__name__}: {e}"}
        rec = dict(rec)
        body = str(rec.get("body") or rec.get("text") or "")
        rec["body"] = body
        rec["body_bytes"] = int(rec.get("body_bytes")
                                or len(body.encode("utf-8")))
        rec.setdefault("model", rec.get("model") or "")
        if rec.get("rc") is None and rec.get("ok") and body.strip():
            rec["rc"] = 0
        proven = proof_ok(rec)
        rec["ok"] = bool(proven)
        rec["link_id"] = link_id
        if proven and link_id not in self.state():
            self.register(link_id, rail_type, src, dst, policy_rank=policy_rank)
        self.ledger.append("PROBE_RESULT", {
            "link_id": link_id,
            "ok": bool(proven),
            "detail": str(rec.get("detail") or rec.get("kind") or "")[:300],
            "model": str(rec.get("model") or "")[:120],
            "rc": rec.get("rc"),
            "body_bytes": rec.get("body_bytes"),
        })
        rec["registered"] = bool(proven) and link_id in self.live_nodes()
        return rec

    def _proven(self) -> dict:
        """Every row that clears the RUNTIME-BINDING gates - ok + rc==0 + a model
        that answered + a non-empty body - carrying its measured age.

        Freshness is deliberately NOT applied here. live_nodes() and stale_nodes()
        both read this one function and split on age, so the two can never
        disagree about what counts as a proof; only about how old it is.
        """
        now = self._clock()
        out = {}
        for lid, v in self.state().items():
            if not v.get("ok"):
                continue
            if v.get("rc") not in (0, "0"):
                continue
            if not str(v.get("model") or "").strip():
                continue
            if int(v.get("body_bytes") or 0) <= 0:
                continue
            last = v.get("last_probe")
            out[lid] = {
                "link_id": lid,
                "rail_type": v["claim"]["rail_type"],
                "src": v["claim"]["src"],
                "dst": v["claim"]["dst"],
                "route": f"{v['claim']['src']}->{v['claim']['dst']}",
                "policy_rank": v["claim"].get("policy_rank", 0),
                "model": v.get("model"),
                "rc": v.get("rc"),
                "body_bytes": v.get("body_bytes"),
                "last_probe": last,
                "age_s": (now - last) if last is not None else None,
            }
        return out

    @staticmethod
    def _fresh(row: dict, max_age_s: float | None) -> bool:
        """Fail-closed: an age we cannot compute is STALE, never fresh."""
        if max_age_s is None:
            return True
        age = row.get("age_s")
        return age is not None and age <= max_age_s

    def live_nodes(self, max_age_s: float | None = PROOF_TTL_S) -> dict:
        """Proven-live nodes only. Claim-only, unanswered and STALE rows dropped.

        `verified: True` is emitted here and nowhere else, and it now means all
        five things at once: it answered, rc==0, a model is named, the body was
        non-empty, AND the measurement is younger than max_age_s. Pass
        max_age_s=None only where staleness is genuinely irrelevant - the same
        escape hatch, with the same warning, as route().
        """
        return {lid: {**row, "verified": True}
                for lid, row in self._proven().items()
                if self._fresh(row, max_age_s)}

    def stale_nodes(self, max_age_s: float | None = PROOF_TTL_S) -> dict:
        """Rows that were proven once and are no longer fresh.

        These exist so that dropping a row from the projection is a STATEMENT
        rather than a disappearance: the mesh saying "claude-cli answered, 3.69
        days ago, and nothing has asked it since" is useful; the row quietly
        going missing is the same silence the filter was added to remove.
        """
        return {lid: {**row, "verified": False, "proof_state": "STALE"}
                for lid, row in self._proven().items()
                if not self._fresh(row, max_age_s)}

    def file_runtime(self, dest_dir,
                     max_age_s: float | None = PROOF_TTL_S) -> dict:
        """Write live/registry/{nodes,rails}.json from proven-live nodes.

        Existence of the directory is not identity; the files carry the
        measurement. Ledger remains authority; these are projections.

        The file declares the TTL it applied and names every row that TTL
        excluded, so a reader can tell "nothing answered" from "nothing has been
        asked lately" without opening the ledger.
        """
        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)
        nodes = self.live_nodes(max_age_s)
        stale = self.stale_nodes(max_age_s)
        body = {
            "schema": RUNTIME_SCHEMA,
            "measured_at": self._clock(),
            "proof_ttl_s": max_age_s,
            "count": len(nodes),
            "nodes": sorted(nodes),
            "matrix": [nodes[k] for k in sorted(nodes)],
            "stale_count": len(stale),
            "stale": [stale[k] for k in sorted(stale)],
            "note": ("rebuildable projection of proven-live nodes; "
                     "ledger is authority; a node that does not answer "
                     "is not registered, and a node whose only proof is "
                     "older than proof_ttl_s is listed under 'stale', "
                     "not under 'nodes'"),
        }
        atomic_json(dest / "nodes.json", body)
        atomic_json(dest / "rails.json", body)
        return body

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
                s[p["link_id"]] = {"claim": p, "last_probe": None, "ok": None,
                                   "model": None, "rc": None, "body_bytes": None}
            elif e == "PROBE_RESULT" and p.get("link_id") in s:
                s[p["link_id"]]["last_probe"] = rec["t"]
                s[p["link_id"]]["ok"] = p["ok"]
                if "model" in p:
                    s[p["link_id"]]["model"] = p.get("model")
                if "rc" in p:
                    s[p["link_id"]]["rc"] = p.get("rc")
                if "body_bytes" in p:
                    s[p["link_id"]]["body_bytes"] = p.get("body_bytes")
            return s
        return self.ledger.project(fold, {})

    def matrix(self) -> list[dict]:
        """Every link with claim + measurement + AGE. A never-probed link reports
        verified=None (UNKNOWN), never True - registration is not capability."""
        now = self._clock()
        rows = []
        for lid, v in sorted(self.state().items()):
            age = (now - v["last_probe"]) if v["last_probe"] else None
            if v["last_probe"] is None:
                proof_state = "UNMEASURED"
            elif not v["ok"]:
                proof_state = "FAIL"
            elif age is None or age > PROOF_TTL_S:
                proof_state = "STALE"
            else:
                proof_state = "LIVE"
            model = v.get("model")
            if model is not None:
                model = str(model)
            rows.append({"link_id": lid,
                         "rail_type": v["claim"]["rail_type"],
                         "route": f"{v['claim']['src']}->{v['claim']['dst']}",
                         "verified": v["ok"],
                         "age_s": age,
                         "model": model,
                         "rc": v.get("rc"),
                         "body_bytes": v.get("body_bytes"),
                         "proof_state": proof_state})
        return rows

    def route(self, src: str, dst: str,
              max_age_s: float | None = PROOF_TTL_S) -> list[dict]:
        """Candidate links for a route, DOM-first by policy_rank then rail preference.
        Only links whose LAST MEASUREMENT was ok AND FRESH are candidates.
        STAGE-7 H-05 FIX (OA, MEASURED): route() filtered only on ok, so a link probed
        live ONCE was dispatch-eligible forever - a stale DOM session would be chosen
        days later. A measurement older than max_age_s is STALE, not live; pass
        max_age_s=None only where staleness is genuinely irrelevant."""
        pref = {"DOM": 0, "CLI": 1, "API": 2, "CHAT": 3, "OTHER": 4}
        now = self._clock()
        st = self.state()
        live = []
        for v in st.values():
            c = v["claim"]
            if c["src"] != src or c["dst"] != dst or not v["ok"]:
                continue
            if max_age_s is not None and (v["last_probe"] is None
                                          or now - v["last_probe"] > max_age_s):
                continue                      # measured live, but not RECENTLY
            live.append(v)
        return sorted((v["claim"] for v in live),
                      key=lambda c: (-c["policy_rank"], pref[c["rail_type"]]))