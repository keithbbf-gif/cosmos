#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_webhooks — the processor-agnostic webhook receiver.

    POST /v1/webhooks/{processor}  -> verify signature -> route event -> grant.

Rules:
    - verify FIRST (per-processor adapter), route SECOND — unsigned bodies never
      touch the credit balance
    - idempotent: processed webhook ids are stored; replays are no-ops
    - every accepted payment emits CREDIT_PURCHASED (money-in) — the meter is the book
    - the Founding offer's paid tier is granted by the webhook (checkout completed),
      not by the checkout click — the click only creates the session
"""
from __future__ import annotations

import json
import sqlite3
import time
from typing import Any, Dict, Optional

import cosmos_pay_meter as meter_mod
from cosmos_pay_meter import SCHEMA as METER_SCHEMA


class WebhookError(RuntimeError):
    """kind in {UNKNOWN_PROCESSOR, VERIFY_FAILED, DUPLICATE, BAD_PAYLOAD}."""


class WebhookRouter:
    def __init__(self, store: Any, meter: Any, founding: Any,
                 stripe: Any = None, paypal: Any = None, bankproc: Any = None):
        import threading
        self.store = store
        self.meter = meter
        self.founding = founding
        self.adapters = {"stripe": stripe, "paypal": paypal, "bankproc": bankproc}
        self._db: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()

    def attach(self, db_path: str) -> None:
        """Processed-webhook idempotency table (own connection, WAL)."""
        self._db = sqlite3.connect(db_path, check_same_thread=False)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS webhook_seen (
                 processor TEXT, event_id TEXT, PRIMARY KEY (processor, event_id))"""
        )
        self._db.commit()

    def _seen(self, processor: str, event_id: str) -> bool:
        with self._lock:
            cur = self._db.execute(
                "SELECT 1 FROM webhook_seen WHERE processor = ? AND event_id = ?",
                (processor, event_id),
            )
            return cur.fetchone() is not None

    def _mark(self, processor: str, event_id: str) -> None:
        with self._lock:
            self._db.execute(
                "INSERT OR IGNORE INTO webhook_seen (processor, event_id) VALUES (?,?)",
                (processor, event_id),
            )
            self._db.commit()

    def _claim(self, processor: str, event_id: str) -> bool:
        """Atomic check-and-mark under one lock — concurrent duplicate webhooks
        cannot both pass the idempotency gate (double-grant defense)."""
        with self._lock:
            cur = self._db.execute(
                "SELECT 1 FROM webhook_seen WHERE processor = ? AND event_id = ?",
                (processor, event_id),
            )
            if cur.fetchone() is not None:
                return False
            self._db.execute(
                "INSERT OR IGNORE INTO webhook_seen (processor, event_id) VALUES (?,?)",
                (processor, event_id),
            )
            self._db.commit()
            return True

    def _release(self, processor: str, event_id: str) -> None:
        """Un-claim a webhook whose routing raised — lets the processor retry."""
        with self._lock:
            self._db.execute(
                "DELETE FROM webhook_seen WHERE processor = ? AND event_id = ?",
                (processor, event_id),
            )
            self._db.commit()

    # ------------------------------------------------------------- routing
    def receive(self, processor: str, payload: bytes, headers: Dict[str, str]) -> Dict[str, Any]:
        adapter = self.adapters.get(processor)
        if adapter is None:
            raise WebhookError(f"UNKNOWN_PROCESSOR {processor!r}")

        # 1. verify FIRST — per-adapter signature scheme
        if processor == "stripe":
            event = adapter.verify_webhook(payload, headers.get("Stripe-Signature", ""))
            event_id = event.get("id", "")
            etype = event.get("type", "")
        elif processor == "paypal":
            event = adapter.verify_webhook(payload, headers)
            event_id = event.get("id", "")
            etype = event.get("event_type", "")
        elif processor == "bankproc":
            event = adapter.verify_webhook(payload, headers)  # adapter pending rates
            event_id = str(event.get("id", ""))
            etype = str(event.get("type", ""))
        else:
            raise WebhookError(f"UNKNOWN_PROCESSOR {processor!r}")

        # 2. idempotency — atomic claim; concurrent replays cannot both route
        if event_id and not self._claim(processor, event_id):
            return {"ok": True, "duplicate": True, "event_id": event_id}

        # 3. route the event — on routing failure, release the claim so the
        # processor's retry can land (a claimed-but-failed grant must not be lost)
        try:
            out = self._route(processor, etype, event)
        except Exception:
            if event_id:
                self._release(processor, event_id)
            raise
        return {"ok": True, "event_id": event_id, "type": etype, **out}

    def _route(self, processor: str, etype: str, event: Dict[str, Any]) -> Dict[str, Any]:
        if processor == "stripe":
            return self._route_stripe(etype, event)
        if processor == "paypal":
            return self._route_paypal(etype, event)
        return {"routed": False, "note": "bankproc adapter pending rates email"}

    # ------------------------------------------------------------- stripe
    def _route_stripe(self, etype: str, event: Dict[str, Any]) -> Dict[str, Any]:
        data = (event.get("data") or {}).get("object") or {}
        account_hash = data.get("client_reference_id") or (data.get("metadata") or {}).get("account_hash")
        amount = None
        if data.get("amount_total"):
            try:
                amount = float(data["amount_total"]) / 100.0
            except (TypeError, ValueError) as e:
                raise WebhookError(f"BAD_PAYLOAD bad amount_total: {e}") from e
        if etype == "checkout.session.completed" and account_hash:
            meta = data.get("metadata") or {}
            founding_tier = meta.get("founding")
            if founding_tier in ("paid", "verified"):
                # Founding: the checkout amount is MONEY-IN only; the tier grant IS
                # the face ($20 paid / $11 verified). Granting both would double-pay.
                if amount is not None:
                    self.meter.emit({
                        "schema": METER_SCHEMA, "event": "CREDIT_PURCHASED",
                        "account": account_hash, "amount_usd": amount,
                        "reason": f"stripe:founding:{founding_tier}",
                        "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    })
                self.founding.grant(account_hash, founding_tier, payment_ref=data.get("id", ""))
                return {"founding": founding_tier, "account": account_hash}
            if amount is None:
                raise WebhookError("BAD_PAYLOAD checkout.session.completed without amount_total")
            self.store.grant(account_hash, amount)
            self.meter.emit({
                "schema": METER_SCHEMA, "event": "CREDIT_PURCHASED",
                "account": account_hash, "amount_usd": amount,
                "reason": f"stripe:{data.get('id', '')}",
                "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            })
            return {"granted_usd": amount, "account": account_hash}
        if etype in ("charge.refunded",) and account_hash:
            # refund: claw back credits (fail-closed — negative balance refuses next reserve)
            try:
                refunded = float(data.get("amount_refunded", 0)) / 100.0
            except (TypeError, ValueError) as e:
                raise WebhookError(f"BAD_PAYLOAD bad amount_refunded: {e}") from e
            self.store.grant(account_hash, -abs(refunded))
            return {"refunded": True, "account": account_hash}
        return {"routed": False, "note": f"unhandled stripe event {etype}"}

    # ------------------------------------------------------------- paypal
    def _route_paypal(self, etype: str, event: Dict[str, Any]) -> Dict[str, Any]:
        resource = event.get("resource") or {}
        custom = resource.get("custom_id") or ""
        account_hash = custom
        founding_tier = None
        if custom.startswith("{"):
            try:
                cdata = json.loads(custom)
                account_hash = cdata.get("account_hash") or account_hash
                founding_tier = cdata.get("founding")
            except Exception:
                pass

        amount = None
        try:
            amount = float(resource["amount"]["value"])
        except (KeyError, TypeError, ValueError):
            amount = None

        if etype in ("CHECKOUT.ORDER.APPROVED", "PAYMENT.CAPTURE.COMPLETED") and account_hash:
            if founding_tier in ("paid", "verified"):
                if amount is not None:
                    self.meter.emit({
                        "schema": METER_SCHEMA, "event": "CREDIT_PURCHASED",
                        "account": account_hash, "amount_usd": amount,
                        "reason": f"paypal:founding:{founding_tier}",
                        "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    })
                self.founding.grant(account_hash, founding_tier, payment_ref=resource.get("id", ""))
                return {"founding": founding_tier, "account": account_hash}

            if amount is not None:
                self.store.grant(account_hash, amount)
                self.meter.emit({
                    "schema": METER_SCHEMA, "event": "CREDIT_PURCHASED",
                    "account": account_hash, "amount_usd": amount,
                    "reason": f"paypal:{resource.get('id', '')}",
                    "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                })
                return {"granted_usd": amount, "account": account_hash}
        return {"routed": False, "note": f"unhandled paypal event {etype}"}

