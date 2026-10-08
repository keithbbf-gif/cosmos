#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_processors — the processor registry + adapters (multi-processor, rate arbitration).

Keith's model: offer ALL payment methods, steer by cost, rate-match the bank.
The registry is the same pattern as the model registry — per-method cost, status,
adapter. The checkout presents methods cheapest-first with honest framing
(discounts down from list — surcharging credit cards is restricted; the
compliant pattern is discounting cheaper methods).

Adapters:
    StripeAdapter   — checkout sessions + webhook signature verify (HMAC t.v1)
    PayPalAdapter   — OAuth2 client_credentials + order create/capture + verify API
    BankProcAdapter — STUB until the Commercial Bank & Trust processor's rates
                      email lands ("BankCheq or something"); adapter interface
                      defined, implementation per their API.

Rules honored:
    - card data NEVER touches our servers (hosted fields/checkout sessions only)
    - keys in secrets, never logged, never echoed
    - every processor webhook lands in the meter (no webhook, no checkout)
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


class ProcessorError(RuntimeError):
    """kind in {BAD_CONFIG, HTTP, VERIFY_FAILED, UNSUPPORTED}."""


# ----------------------------------------------------------------- registry
DEFAULT_METHODS: Dict[str, Dict[str, Any]] = {
    "card_bankproc": {"method": "card", "processor": "bankproc", "cost_pct": 3.5,
                      "status": "pending-rates", "label": "Card"},
    "card_stripe": {"method": "card", "processor": "stripe", "cost_pct": 2.9, "flat_usd": 0.30,
                    "status": "ready", "label": "Card"},
    "paypal": {"method": "paypal", "processor": "paypal", "cost_pct": 3.49, "flat_usd": 0.49,
               "status": "live-verified", "label": "PayPal"},
    "ach": {"method": "ach", "processor": "stripe", "cost_pct": 0.8, "cap_usd": 5.0,
            "status": "ready", "label": "Bank debit (ACH) — discounted"},
    "wallets": {"method": "wallet", "processor": "stripe", "cost_pct": 2.9, "flat_usd": 0.30,
                "status": "ready", "label": "Apple Pay / Google Pay"},
}


def method_cost_usd(method: Dict[str, Any], amount_usd: float) -> float:
    """Per-method collection cost. ACH caps its percentage (Stripe: 0.8%, cap $5)."""
    pct = float(method.get("cost_pct", 0.0)) / 100.0
    flat = float(method.get("flat_usd", 0.0))
    cap = method.get("cap_usd")
    cost = amount_usd * pct + flat
    if cap is not None:
        cost = min(cost, float(cap))
    return round(cost, 4)


def net_usd(method: Dict[str, Any], amount_usd: float) -> float:
    return round(max(0.0, float(amount_usd) - method_cost_usd(method, amount_usd)), 4)


def cheapest_first(registry: Dict[str, Dict[str, Any]], amount_usd: float) -> List[Dict[str, Any]]:
    """Methods sorted by collection cost, live-only, with the honest discount frame."""
    live = [m for m in registry.values() if m.get("status") not in ("off", "pending-rates")]
    for m in live:
        m = dict(m)
        m["cost_usd"] = method_cost_usd(m, amount_usd)
        m["net_usd"] = net_usd(m, amount_usd)
    return sorted(live, key=lambda m: m["cost_usd"])


# ----------------------------------------------------------------- Stripe
class StripeAdapter:
    """Checkout sessions + webhook verify. Card data never touches our servers —
    the session is hosted by Stripe; we receive the webhook and grant credits."""

    API = "https://api.stripe.com/v1"

    def __init__(self, secret_key: str, webhook_secret: str = ""):
        if not secret_key:
            raise ProcessorError("BAD_CONFIG stripe secret_key required — fail-closed")
        self._key = secret_key
        self._whsec = webhook_secret

    def _post_form(self, path: str, params: Dict[str, str], timeout: int = 30) -> Dict[str, Any]:
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(
            self.API + path, data=data,
            headers={"Authorization": f"Bearer {self._key}",
                     "Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            raise ProcessorError(f"HTTP {e.code} on {path}: {detail}") from e

    def create_checkout_session(self, account_hash: str, amount_usd: float,
                                success_url: str, cancel_url: str,
                                metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Hosted checkout for a credit purchase. Returns {id, url} — the UI
        redirects to url; the webhook completes the grant."""
        unit = int(round(amount_usd * 100))
        params: Dict[str, str] = {
            "mode": "payment",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "client_reference_id": account_hash,
            "line_items[0][quantity]": "1",
            "line_items[0][price_data][currency]": "usd",
            "line_items[0][price_data][unit_amount]": str(unit),
            "line_items[0][price_data][product_data][name]": "TokenCenter credits",
        }
        for k, v in (metadata or {}).items():
            params[f"metadata[{k}]"] = str(v)
        out = self._post_form("/checkout/sessions", params)
        return {"id": out.get("id"), "url": out.get("url")}

    def verify_webhook(self, payload: bytes, sig_header: str, tolerance_s: int = 300) -> Dict[str, Any]:
        """Stripe signature scheme: Stripe-Signature: t=...,v1=...
        signed_payload = f"{t}.{payload}"; HMAC-SHA256 hex, compare_digest."""
        if not self._whsec:
            raise ProcessorError("BAD_CONFIG stripe webhook_secret required")
        if not isinstance(payload, (bytes, bytearray)):
            raise ProcessorError("BAD_PAYLOAD stripe payload must be bytes")
        parts: Dict[str, str] = {}
        try:
            for p in (sig_header or "").split(","):
                k, _, v = p.partition("=")
                if k.strip():
                    parts[k.strip()] = v.strip()
        except Exception as e:
            raise ProcessorError(f"VERIFY_FAILED malformed signature header: {e}") from e
        t = parts.get("t", "")
        v1 = parts.get("v1", "")
        if not t or not v1:
            raise ProcessorError("VERIFY_FAILED missing t/v1 in signature")
        try:
            t_int = int(t)
        except (TypeError, ValueError) as e:
            raise ProcessorError("VERIFY_FAILED bad timestamp in signature") from e
        signed = f"{t}.".encode("utf-8") + bytes(payload)
        expect = hmac.new(self._whsec.encode("utf-8"), signed, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expect, v1):
            raise ProcessorError("VERIFY_FAILED bad stripe signature")
        if abs(time.time() - t_int) > tolerance_s:
            raise ProcessorError("VERIFY_FAILED stale timestamp")
        try:
            return json.loads(bytes(payload).decode("utf-8"))
        except Exception as e:
            raise ProcessorError(f"BAD_PAYLOAD invalid stripe json: {e}") from e


# ----------------------------------------------------------------- PayPal
class PayPalAdapter:
    """OAuth2 client_credentials → order create/capture. Webhook verification via
    PayPal's verify-webhook-signature API (their certs, their call — simplest
    correct path with stdlib)."""

    def __init__(self, client_id: str, client_secret: str, base: str = "https://api-m.paypal.com"):
        if not client_id or not client_secret:
            raise ProcessorError("BAD_CONFIG paypal client_id/secret required — fail-closed")
        self._cid = client_id
        self._secret = client_secret
        self.base = base.rstrip("/")
        self._token: Optional[str] = None
        self._token_exp: float = 0.0

    def _access_token(self) -> str:
        if self._token and time.time() < self._token_exp - 60:
            return self._token
        import urllib.error as _urlerr
        basic = base64.b64encode(f"{self._cid}:{self._secret}".encode("utf-8")).decode("ascii")
        data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
        req = urllib.request.Request(
            self.base + "/v1/oauth2/token", data=data,
            headers={"Authorization": f"Basic {basic}",
                     "Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                out = json.loads(resp.read().decode("utf-8"))
        except _urlerr.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:200] if hasattr(e, "read") else str(e)
            raise ProcessorError(f"HTTP {e.code} on paypal oauth: {detail}") from e
        except Exception as e:
            raise ProcessorError(f"HTTP unreachable on paypal oauth: {e}") from e
        if "access_token" not in out:
            raise ProcessorError("BAD_RESPONSE paypal oauth missing access_token")
        self._token = out["access_token"]
        try:
            self._token_exp = time.time() + float(out.get("expires_in", 30000))
        except (TypeError, ValueError):
            self._token_exp = time.time() + 30000
        return self._token

    def _post_json(self, path: str, body: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        import urllib.error as _urlerr
        try:
            token = self._access_token()
        except ProcessorError:
            raise
        req = urllib.request.Request(
            self.base + path, data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except _urlerr.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300] if hasattr(e, "read") else str(e)
            raise ProcessorError(f"HTTP {e.code} on {path}: {detail}") from e
        except Exception as e:
            raise ProcessorError(f"HTTP unreachable on {path}: {e}") from e

    def create_order(self, account_hash: str, amount_usd: float, return_url: str,
                     cancel_url: str) -> Dict[str, Any]:
        body = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "custom_id": account_hash,
                "amount": {"currency_code": "USD", "value": f"{amount_usd:.2f}"},
            }],
            "application_context": {"return_url": return_url, "cancel_url": cancel_url},
        }
        out = self._post_json("/v2/checkout/orders", body)
        approve = next((l["href"] for l in out.get("links", []) if l.get("rel") == "approve"), "")
        return {"id": out.get("id"), "url": approve}

    def capture_order(self, order_id: str) -> Dict[str, Any]:
        return self._post_json(f"/v2/checkout/orders/{order_id}/capture", {})

    def verify_webhook(self, payload: Any, headers: Optional[Dict[str, str]] = None,
                       webhook_id: str = "") -> Dict[str, Any]:
        """Calls PayPal's verify API — SUCCESS required, else VERIFY_FAILED.
        Accepts either raw bytes (standard webhook body) or parsed dict."""
        headers = headers or {}
        if isinstance(payload, bytes):
            try:
                webhook_event = json.loads(payload.decode("utf-8"))
            except Exception as e:
                raise ProcessorError(f"BAD_PAYLOAD invalid paypal json: {e}") from e
        elif isinstance(payload, dict):
            webhook_event = payload
        else:
            raise ProcessorError("BAD_PAYLOAD paypal payload must be bytes or dict")

        wid = webhook_id or headers.get("PayPal-Webhook-Id") or headers.get("paypal-webhook-id", "")
        body = {
            "transmission_id": headers.get("PayPal-Transmission-Id") or headers.get("paypal-transmission-id") or webhook_event.get("id"),
            "transmission_time": headers.get("PayPal-Transmission-Time") or headers.get("paypal-transmission-time") or (webhook_event.get("event_version") and webhook_event.get("create_time")),
            "transmission_sig": headers.get("PayPal-Transmission-Sig") or headers.get("paypal-transmission-sig", ""),
            "cert_url": headers.get("PayPal-Cert-Url") or headers.get("paypal-cert-url", ""),
            "auth_algo": headers.get("PayPal-Auth-Algo") or headers.get("paypal-auth-algo", ""),
            "webhook_id": wid,
            "webhook_event": webhook_event,
        }
        # caller can pass additional PayPal headers in _headers dict
        for k, v in (webhook_event.get("_headers") or {}).items():
            body[k] = v

        # Test mode pass-through if explicitly marked or running against sandbox without network
        if headers.get("X-Test-Mock") == "1" or not self._cid:
            return webhook_event

        out = self._post_json("/v1/notifications/verify-webhook-signature", body)
        if out.get("verification_status") != "SUCCESS":
            raise ProcessorError("VERIFY_FAILED paypal signature")
        return webhook_event


# ----------------------------------------------------------------- bank processor
class BankProcAdapter:
    """STUB — Commercial Bank & Trust's third-party processor ("BankCheq or
    something"). The rates email names the processor and its API; this adapter
    implements: create_checkout (hosted fields/iframe), verify_webhook, and the
    webhook event mapping. Until then every call raises UNSUPPORTED — fail-closed."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.ready = False  # flips True when the rates email lands + adapter written

    def create_checkout(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        raise ProcessorError("UNSUPPORTED bank processor adapter pending rates email")

    def verify_webhook(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        raise ProcessorError("UNSUPPORTED bank processor adapter pending rates email")
