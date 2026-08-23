#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_spend - THE BREAKER IN THE CALLER (F5 builder). Settled by four-family
convergence, not up for re-vote: reserve worst case -> deny if reserve fails -> call ->
settle against actual usage. The decision lives WHERE THE CALL HAPPENS - a ledger
written afterward is a receipt, not a control.

Both directions governed (scar R6/S-102): overspend AND under-use of expiring credit.
An unpriced call is UNPRICED, never zero. Every number carries provenance:
estimate | measured | billed.
"""
from __future__ import annotations

import time
from typing import Callable, Optional

from cosmos_ledger import Ledger


class SpendError(RuntimeError):
    """kind in {DENIED, UNKNOWN_RAIL, RESERVATION_EXPIRED, DOUBLE_SETTLE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


class SpendGate:
    def __init__(self, ledger: Ledger, clock=time.time):
        self.ledger = ledger
        self._clock = clock

    # ---------------- budgets ----------------
    def set_budget(self, rail: str, cap_usd: float,
                   expires_epoch: Optional[float] = None) -> None:
        # STAGE-7B RG-M1 FIX (MEASURED): BUDGET_SET wiped settled/reserved in the fold,
        # so a cap REFRESH became a second wallet - re-setting the same rail's cap reset
        # its spend to zero. The fold now PRESERVES settled/reserved across a re-set
        # (see _state); this event only changes the cap and expiry.
        self.ledger.append("BUDGET_SET", {"rail": rail, "cap_usd": cap_usd,
                                          "expires_epoch": expires_epoch})

    def _state(self) -> dict:
        def fold(s, rec):
            p, e = rec["payload"], rec["event"]
            if e == "BUDGET_SET":
                # RG-M1: preserve accounting across a cap refresh - only cap/expiry change
                if p["rail"] in s:
                    s[p["rail"]]["cap"] = p["cap_usd"]
                    s[p["rail"]]["expires"] = p.get("expires_epoch")
                else:
                    s[p["rail"]] = {"cap": p["cap_usd"], "expires": p.get("expires_epoch"),
                                    "reserved": {}, "settled": 0.0, "unpriced": 0}
            elif e == "SPEND_RESERVED" and p["rail"] in s:
                s[p["rail"]]["reserved"][p["rid"]] = {"usd": p["worst_case_usd"],
                                                      "expires": p["expires_epoch"]}
            elif e == "SPEND_SETTLED" and p["rail"] in s:
                s[p["rail"]]["reserved"].pop(p["rid"], None)
                if p["measured_usd"] is None:
                    s[p["rail"]]["unpriced"] += 1
                else:
                    s[p["rail"]]["settled"] += p["measured_usd"]
            elif e == "SPEND_RELEASED" and p["rail"] in s:
                s[p["rail"]]["reserved"].pop(p["rid"], None)
            return s
        return self.ledger.project(fold, {})

    # ---------------- the breaker ----------------
    def guarded_call(self, rail: str, worst_case_usd: float,
                     call: Callable[[], dict],
                     ttl_s: float = 600) -> dict:
        """RESERVE -> DENY-or-CALL -> SETTLE. The call receives nothing until the
        reservation exists; a failed reserve raises BEFORE any spend can happen."""
        st = self._state()
        if rail not in st:
            raise SpendError("UNKNOWN_RAIL",
                             f"{rail!r} has no budget - an unbudgeted rail cannot spend")
        b = st[rail]
        now = self._clock()
        # CRITIC B7 FIX (measured: an expired budget ALLOWED a call): an expired credit
        # cannot be spent - that is what expiry MEANS - and the denial is typed.
        if b.get("expires") and now >= b["expires"]:
            self.ledger.append("SPEND_DENIED",
                               {"rail": rail, "worst_case_usd": worst_case_usd,
                                "detail": "BUDGET EXPIRED"})
            raise SpendError("DENIED",
                             f"{rail}: budget expired "
                             f"{(now - b['expires'])/86400:.1f} days ago - an expired "
                             f"credit is not money")
        # B7 also: expired reservations are SWEPT (released with an event), not held
        # against the cap forever - a fail-closed leak is still a defect.
        for rid, r in list(b["reserved"].items()):
            if now >= r["expires"]:
                self.ledger.append("SPEND_RELEASED",
                                   {"rail": rail, "rid": rid,
                                    "detail": "reservation expired unsettled - swept"})
                del b["reserved"][rid]
        outstanding = sum(r["usd"] for r in b["reserved"].values())
        if b["settled"] + outstanding + worst_case_usd > b["cap"]:
            self.ledger.append("SPEND_DENIED",
                               {"rail": rail, "worst_case_usd": worst_case_usd,
                                "settled": b["settled"], "outstanding": outstanding,
                                "cap": b["cap"]})
            raise SpendError("DENIED",
                             f"{rail}: worst case ${worst_case_usd:.2f} would pass the "
                             f"cap (settled ${b['settled']:.2f} + reserved "
                             f"${outstanding:.2f} of ${b['cap']:.2f}) - denied BEFORE "
                             f"the call, which is the whole point")
        # STAGE-7B T3/RG-B1 FIX (MEASURED: overlap spent $1.40 on a $1 cap): the K6
        # expect_head_seq check sampled the head at APPEND time, so a decision made on a
        # stale projection still bound a fresh head. The cap check and the reservation
        # append must be ONE atomic critical section. append_guarded holds the OS lock
        # across re-read -> re-check-headroom -> append; two overlapping callers are
        # serialized and the second sees the first's reservation. rid is a uuid (K6).
        import uuid as _uuid
        rid = "r-%s" % _uuid.uuid4().hex[:12]

        def _decide(_recs):
            st2 = self._state()                 # re-derived UNDER the lock
            b2 = st2[rail]
            now2 = self._clock()
            for r2id, r2 in list(b2["reserved"].items()):
                if now2 >= r2["expires"]:
                    b2["reserved"].pop(r2id, None)
            out2 = sum(r["usd"] for r in b2["reserved"].values())
            if b2["settled"] + out2 + worst_case_usd > b2["cap"]:
                raise SpendError(
                    "DENIED",
                    f"{rail}: worst case ${worst_case_usd:.2f} passes the cap under the "
                    f"lock (settled ${b2['settled']:.2f} + reserved ${out2:.2f} of "
                    f"${b2['cap']:.2f}) - denied atomically, no overlap slip")
            return ("SPEND_RESERVED",
                    {"rail": rail, "rid": rid, "worst_case_usd": worst_case_usd,
                     "expires_epoch": now2 + ttl_s, "provenance": "estimate"})
        self.ledger.append_guarded(_decide)
        try:
            result = call()
        except Exception:
            self.ledger.append("SPEND_RELEASED", {"rail": rail, "rid": rid,
                                                  "detail": "call raised - released"})
            raise
        measured = result.get("usd")            # None = UNPRICED, and that is a state
        self.ledger.append("SPEND_SETTLED",
                           {"rail": rail, "rid": rid,
                            "measured_usd": measured,
                            "provenance": "measured" if measured is not None else "UNPRICED"})
        return result

    # ---------------- both-direction audit ----------------
    def audit(self) -> dict:
        """Overspend risk AND expiry risk, one view, every number dated."""
        now = self._clock()
        out = {"measured_at_epoch": now, "rails": {}}
        for rail, b in self._state().items():
            reserved = sum(r["usd"] for r in b["reserved"].values())
            row = {"cap_usd": b["cap"], "settled_usd": round(b["settled"], 6),
                   "reserved_usd": round(reserved, 6),
                   "unpriced_calls": b["unpriced"],
                   # CRITIC B7: headroom that ignores reservations lies toward spending.
                   "headroom_usd": round(b["cap"] - b["settled"] - reserved, 6)}
            if b["expires"]:
                days = (b["expires"] - now) / 86400
                burn_needed = b["cap"] - b["settled"]
                row["expires_in_days"] = round(days, 1)
                row["expiry_risk"] = (f"${burn_needed:.2f} unspent with {days:.0f} days "
                                      f"left - EXPIRING CREDIT IS THE RISK, not overspend"
                                      ) if burn_needed > 0 and days < 60 else None
            out["rails"][rail] = row
        return out