#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_bulletproof — comprehensive integration tests for gateway robustness,
CORS, PayPal webhooks, key daily caps, account settings, and statement export."""
from __future__ import annotations

import csv
import hashlib
import hmac
import io
import json
import os
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CODE_DIR))

import cosmos_pay_config as cfg
import cosmos_pay_founding as founding_mod
import cosmos_pay_gateway as gw
import cosmos_pay_meter as meter_mod
import cosmos_pay_processors as proc_mod
import cosmos_pay_webhooks as hooks_mod

PASS = 0
FAIL = 0


def check(name: str, cond: bool) -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}")


print("— test_pay_bulletproof —")

# Fake Rail
class FakeRail:
    def __init__(self):
        self.calls = 0

    def runsync(self, req):
        self.calls += 1
        return {
            "id": f"fake_{self.calls}",
            "choices": [{"message": {"role": "assistant", "content": "bulletproof response"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "cached_tokens": 0},
        }

    def stream(self, req):
        self.calls += 1
        yield {"id": "chunk1", "choices": [{"delta": {"content": "bullet"}}]}
        yield {"id": "chunk2", "choices": [{"delta": {"content": "proof"}}]}
        yield {"id": "chunk3", "choices": [], "usage": {"prompt_tokens": 100, "completion_tokens": 20}}


tmp = tempfile.mkdtemp()
store = gw.Store(str(Path(tmp) / "keys.db"))
meter = meter_mod.Meter(str(Path(tmp) / "meter.db"))
rail = FakeRail()
models = {
    "qwen3-coder-30b-fp8": {
        "endpoint": "fake-qwen",
        "price_per_m_usd": 0.297,
        "cogs_per_m_usd": 0.18,
        "lane": "A",
        "stocked": True,
    }
}
config = {
    "free_tier": {"daily_face_usd": 2.0},
    "toll_brackets": cfg.DEFAULT_CONFIG["toll_brackets"],
}
gateway = gw.PayGateway(store, meter, rail, models, config)

founding = founding_mod.Founding(store, meter, cap=500)
class MockStripe(proc_mod.StripeAdapter):
    def create_checkout_session(self, account_hash, amount_usd, success_url, cancel_url, metadata=None):
        return {"id": "cs_mock_123", "url": "https://checkout.stripe.com/pay/cs_mock_123"}

stripe = MockStripe(secret_key="sk_test_mock", webhook_secret="whsec_test")
paypal = proc_mod.PayPalAdapter(client_id="paypal_client_id", client_secret="paypal_secret")
router = hooks_mod.WebhookRouter(store, meter, founding, stripe=stripe, paypal=paypal)
router.attach(str(Path(tmp) / "webhooks.db"))

api = {
    "founding": founding,
    "webhooks": router,
    "stripe": stripe,
    "paypal": paypal,
    "setup_key": "setup_secret_key",
    "config": config,
}

from http.server import ThreadingHTTPServer

server = ThreadingHTTPServer(("127.0.0.1", 0), gw.make_handler(gateway, api))
port = server.server_address[1]
base_url = f"http://127.0.0.1:{port}"

server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()


def req(path, method="GET", body=None, headers=None, key=None):
    h = {"User-Agent": "bulletproof-test"}
    if headers:
        h.update(headers)
    if key:
        h["Authorization"] = f"Bearer {key}"
    data = None
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode("utf-8")
            h.setdefault("Content-Type", "application/json")
        elif isinstance(body, bytes):
            data = body
            h.setdefault("Content-Type", "application/json")

    r = urllib.request.Request(f"{base_url}{path}", data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            try:
                out = json.loads(raw) if raw else {}
            except Exception:
                out = raw
            return resp.status, out, dict(resp.headers)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            out = json.loads(raw) if raw else {}
        except Exception:
            out = raw
        return e.code, out, dict(e.headers)


# 1. CORS Preflight (OPTIONS)
code, out, headers = req("/v1/chat/completions", method="OPTIONS")
check("OPTIONS preflight returns 204", code == 204)
check("CORS allow-origin present", headers.get("Access-Control-Allow-Origin") == "*")
check("CORS allow-methods includes GET, POST", "POST" in headers.get("Access-Control-Allow-Methods", ""))

# 2. Account bootstrap & Key issue
code, out, _ = req("/v1/account/create", method="POST", body={"setup_key": "setup_secret_key"})
check("account create 200", code == 200)
ah = out["account"]
key = out["key"]

# 3. Settings endpoint (GET and POST /v1/settings/*)
code, out, _ = req("/v1/settings", key=key)
check("GET /v1/settings returns defaults", code == 200 and "settings" in out)

code, out, _ = req("/v1/settings/autotopup", method="POST", body={"enabled": True, "cap_usd": 25.0}, key=key)
check("POST /v1/settings/autotopup 200", code == 200 and out.get("ok") is True)

code, out, _ = req("/v1/settings", key=key)
check("settings persisted properly", out["settings"]["autotopup"]["cap_usd"] == 25.0)

# 4. Key Daily Cap Enforcement
code, out, _ = req("/v1/keys/issue", method="POST", body={"label": "capped-key", "daily_cap_usd": 0.00001}, key=key)
check("issue capped key 200", code == 200)
capped_key = out["key"]

# First call passes and consumes cap
code, out, _ = req("/v1/chat/completions", method="POST",
                   body={"model": "qwen3-coder-30b-fp8", "messages": [{"role": "user", "content": "hi"}]},
                   key=capped_key)
check("first call with capped key succeeds", code == 200)

# Second call fails with key_cap_exhausted
code, out, _ = req("/v1/chat/completions", method="POST",
                   body={"model": "qwen3-coder-30b-fp8", "messages": [{"role": "user", "content": "again"}]},
                   key=capped_key)
check("key daily cap enforces 429", code == 429 and out.get("error", {}).get("code") == "key_cap_exhausted")

# 5. PayPal Webhook Processing via Router & Gateway
# Test PayPal webhook with raw bytes body
paypal_event = {
    "id": "WH-TEST-001",
    "event_type": "PAYMENT.CAPTURE.COMPLETED",
    "resource": {
        "id": "CAP-12345",
        "custom_id": ah,
        "amount": {"value": "15.00", "currency_code": "USD"},
    },
}
paypal_bytes = json.dumps(paypal_event).encode("utf-8")
paypal_headers = {
    "PayPal-Webhook-Id": "WH-ID-999",
    "X-Test-Mock": "1",
}
code, out, _ = req("/v1/webhooks/paypal", method="POST", body=paypal_bytes, headers=paypal_headers)
check("PayPal webhook 200", code == 200)
check("PayPal credits granted to account", store.credits(ah) == 15.0)

# 6. Credit purchase endpoint (POST /v1/credits/purchase)
code, out, _ = req("/v1/credits/purchase", method="POST",
                   body={"amount_usd": 20.0, "processor": "stripe"}, key=key)
check("credits purchase returns checkout session", code == 200 and "checkout" in out)

# 7. Log receipt lookup (GET /v1/logs and GET /v1/logs/{id})
code, out, _ = req("/v1/logs", key=key)
check("logs list returns events", code == 200 and len(out.get("data", [])) >= 1)
first_event_id = out["data"][0]["event_id"]

code, out, _ = req(f"/v1/logs/{first_event_id}", key=key)
check("GET /v1/logs/{id} returns single receipt", code == 200 and out.get("data", {}).get("event_id") == first_event_id)

# 8. CSV Statement Export (GET /v1/statement/export)
code, csv_out, headers = req("/v1/statement/export", key=key)
check("statement export returns text/csv", code == 200 and "text/csv" in headers.get("Content-Type", ""))
check("CSV contains header row", "at,event,lane,model" in csv_out)

# 9. Full Account Export (GET /v1/export/full)
code, full_out, _ = req("/v1/export/full", key=key)
check("full export contains account, keys, settings, events",
      code == 200 and "account" in full_out and "keys" in full_out and "settings" in full_out and "events" in full_out)

# 10. Rate Limiting sliding window check
limiter = gw.RateLimiter(key_rpm=3, ip_rpm=10)
check("limiter allows 1st", limiter.check_and_record("test_key", "127.0.0.1")[0] is True)
check("limiter allows 2nd", limiter.check_and_record("test_key", "127.0.0.1")[0] is True)
check("limiter allows 3rd", limiter.check_and_record("test_key", "127.0.0.1")[0] is True)
blocked, reason = limiter.check_and_record("test_key", "127.0.0.1")
check("limiter blocks 4th request when rpm=3", blocked is False and reason == "rate_limit_exceeded_key")

# 11. Model specific GET /v1/models/{id}
code, out, _ = req("/v1/models/qwen3-coder-30b-fp8", key=key)
check("GET /v1/models/{id} 200", code == 200 and out.get("id") == "qwen3-coder-30b-fp8")

code, out, _ = req("/v1/models/nonexistent_model", key=key)
check("GET /v1/models/nonexistent 404", code == 404 and out.get("error", {}).get("code") == "model_not_found")

# 12. Input validation on /v1/chat/completions
code, out, _ = req("/v1/chat/completions", method="POST", body={"messages": []}, key=key)
check("missing model returns 400", code == 400 and out.get("error", {}).get("code") == "missing_model")

code, out, _ = req("/v1/chat/completions", method="POST", body={"model": "qwen3-coder-30b-fp8"}, key=key)
check("missing messages returns 400", code == 400 and out.get("error", {}).get("code") == "missing_messages")

# 13. Pass-through discount pricing helper
import cosmos_pay_pricing as pricing_mod
pt_base = pricing_mod.passthrough_price(3.00, surcharge_pct=5.0)
check("passthrough base 3.00 + 5% == 3.15", pt_base == 3.15)
pt_batch = pricing_mod.passthrough_price(3.00, surcharge_pct=5.0, is_batch=True)
check("passthrough batch 50% discount == 1.575", pt_batch == 1.575)
pt_cache = pricing_mod.passthrough_price(3.00, surcharge_pct=5.0, cache_discount_pct=90.0)
check("passthrough 90% cache discount == 0.315", pt_cache == 0.315)

# 14. Meter rejects non-dict cost
try:
    meter.emit({"schema": meter_mod.SCHEMA, "event": "RUN_SETTLED", "lane": "A",
                "rail": "fake", "model": "qwen", "wallet": "cosmos",
                "tokens": {"in": 1, "out": 1}, "cost": 0.05})
    check("meter rejects non-dict cost", False)
except meter_mod.MeterError as e:
    check("meter rejects non-dict cost", "cost must be a dict" in str(e))

# 15. Meter ingest endpoint (batched sync)
ingest_events = [{
    "schema": meter_mod.SCHEMA, "event": "RUN_SETTLED", "lane": "A",
    "rail": "sync-test", "model": "qwen3-coder-30b-fp8", "wallet": "cosmos",
    "tokens": {"in": 10, "out": 5},
    "cost": {"measured_usd": 0.0001, "provenance": "measured"},
    "account": ah,
}]
code, out, _ = req("/v1/meter/ingest", method="POST", body={"events": ingest_events}, key=key)
check("meter ingest accepts batch", code == 200 and out.get("ingested") == 1)

code, out, _ = req("/v1/meter/ingest", method="POST", body={"events": "not-a-list"}, key=key)
check("meter ingest rejects non-list", code == 400)

# 16. Stripe malformed signatures fail closed (no 500)
try:
    stripe.verify_webhook(b'{"id":"x"}', "")
    check("stripe empty sig refused", False)
except proc_mod.ProcessorError as e:
    check("stripe empty sig refused", "VERIFY_FAILED" in str(e) or "BAD_" in str(e))

try:
    stripe.verify_webhook(b'{"id":"x"}', "t=notanumber,v1=deadbeef")
    check("stripe bad timestamp refused", False)
except proc_mod.ProcessorError as e:
    check("stripe bad timestamp refused", "VERIFY_FAILED" in str(e))

# 17. Toll statement tolerates malformed events
import cosmos_pay_toll as toll_mod
line = toll_mod.statement_line([None, "x", {"event": "RUN_SETTLED", "lane": "B",
    "cost": "bad", "at": "2026-10-01T00:00:00+0000"}], "2026-10")
check("toll tolerates malformed events", line["runs"] == 0 and line["unpriced_held"] >= 0)

# 18. Entitlement rejects non-numeric clock fields
import cosmos_pay_entitlement as ent_mod
import base64 as _b64, hmac as _hmac, hashlib as _hl, json as _json
k = b"y" * 32
bad_claims = {"plan": "x", "expires_epoch": "not-a-number", "grace_days": 0}
raw = _json.dumps(bad_claims, sort_keys=True, separators=(",", ":")).encode()
mac = _hmac.new(k, raw, _hl.sha256).digest()
tok = _b64.urlsafe_b64encode(raw).decode().rstrip("=") + "." + _b64.urlsafe_b64encode(mac).decode().rstrip("=")
try:
    ent_mod.verify(tok, k)
    check("entitlement bad clock refused", False)
except ent_mod.EntitlementError as e:
    check("entitlement bad clock refused", "BAD_FORMAT" in str(e))

server.shutdown()
print(f"\n{PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)
