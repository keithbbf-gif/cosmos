#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_founding — the Founding offer engine: cap counter + two-tier grants.

The offer (Keith, 2026-09-30):
    Founding Member — $10 lifetime, first 500:
        $50 value = $20 token credits + perks (ModelRater, SpiderCaster, PyGents,
        VIP forum, early access)
    Verified Free — the decline path (captures the card either way):
        $40 value = $10 token credits + same perks
        CC-for-ID: $1 auth-and-void, CREDITED BACK as $1 of tokens (no dead money)

Rules:
    - cap 500: sold counter enforced — sold-out refuses grants (loss cap + urgency)
    - the MEMBERSHIP is lifetime; tokens are never free again (credits are
      one-time grants — CREDIT_GRANTED events, never a subscription)
    - every grant emits CREDIT_GRANTED (money-in at $0 cost) — the meter is the book
"""
from __future__ import annotations

import time
from typing import Any, Dict

import cosmos_pay_meter as meter_mod


class FoundingError(RuntimeError):
    """kind in {SOLD_OUT, BAD_TIER, ALREADY_FOUNDING}."""


TIERS: Dict[str, Dict[str, Any]] = {
    "paid": {"price_usd": 10.0, "grant_face_usd": 20.0, "plan": "founding"},
    "verified": {"price_usd": 0.0, "grant_face_usd": 11.0, "plan": "verified_free"},
    # verified = $10 founding-tier tokens + $1 verification credit (the $1 auth,
    # credited back — no dead money). Declared value $40 vs $50.
}


class Founding:
    def __init__(self, store: Any, meter: meter_mod.Meter, cap: int = 500):
        self.store = store          # cosmos_pay_gateway.Store (keys.db + lock)
        self.meter = meter
        self.cap = int(cap)
        self.store.db.execute(
            """CREATE TABLE IF NOT EXISTS founding (
                 id INTEGER PRIMARY KEY CHECK (id = 1),
                 sold INTEGER NOT NULL DEFAULT 0
               )"""
        )
        self.store.db.execute("INSERT OR IGNORE INTO founding (id, sold) VALUES (1, 0)")
        self.store.db.commit()

    def status(self) -> Dict[str, Any]:
        with self.store.lock:
            (sold,) = self.store.db.execute("SELECT sold FROM founding WHERE id = 1").fetchone()
        return {"sold": int(sold), "cap": self.cap, "remaining": max(0, self.cap - int(sold))}

    def _consume_slot(self) -> None:
        with self.store.lock:
            (sold,) = self.store.db.execute("SELECT sold FROM founding WHERE id = 1").fetchone()
            if int(sold) >= self.cap:
                raise FoundingError("SOLD_OUT founding cap reached (first 500)")
            self.store.db.execute("UPDATE founding SET sold = sold + 1 WHERE id = 1")
            self.store.db.commit()

    def grant(self, account_hash: str, tier: str, payment_ref: str = "") -> Dict[str, Any]:
        """Grant a founding tier to an account. Emits CREDIT_GRANTED. Atomic:
        the plan check, slot consume, credit grant, and plan update all hold
        store.lock (an RLock — helpers re-lock safely), so two concurrent
        grants for one account cannot both pass the ALREADY_FOUNDING check
        and double-grant."""
        tier_cfg = TIERS.get(tier)
        if not tier_cfg:
            raise FoundingError(f"BAD_TIER {tier!r} not in {sorted(TIERS)}")
        with self.store.lock:
            row = self.store.db.execute(
                "SELECT plan FROM accounts WHERE account_hash = ?", (account_hash,)
            ).fetchone()
            if row and row[0] in ("founding", "verified_free"):
                raise FoundingError("ALREADY_FOUNDING account already holds a founding tier")
            self._consume_slot()
            face = float(tier_cfg["grant_face_usd"])
            self.store.grant(account_hash, face)
            self.store.db.execute(
                "UPDATE accounts SET plan = ? WHERE account_hash = ?",
                (tier_cfg["plan"], account_hash),
            )
            self.store.db.commit()
        self.meter.emit({
            "schema": meter_mod.SCHEMA, "event": "CREDIT_GRANTED",
            "account": account_hash, "amount_usd": face,
            "reason": f"founding:{tier}", "payment_ref": payment_ref,
            "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        })
        return {"tier": tier, "plan": tier_cfg["plan"], "granted_face_usd": face,
                "status": self.status()}
