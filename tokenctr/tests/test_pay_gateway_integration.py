#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_gateway_integration â€” the gateway end-to-end with a FAKE rail.

No network: ThreadingHTTPServer on an ephemeral port, a FakeRail returning a
fixed OpenAI response with a usage block. Proves the full lane:
    auth â†’ quota â†’ route â†’ relay â†’ settle â†’ meter â†’ headers
Plus: 401 bad key, 429 quota exhaustion (QUOTA_HIT), webhook raw-body signature
through the real HTTP layer (the re-serialize bug class).
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import urllib.request
import hmac
import hashlib

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cosmos_pay_config as cfg
import cosmos_pay_gateway as gw
import cosmos_pay_meter as meter_mod
import cosmos_pay_processors as proc
import cosmos_pay_webhooks as hooks
import cosmos_pay_founding as founding

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


class FakeRail:
    """Stands in for RunPod â€” returns a fixed OpenAI response with usage."""

    def __init__(self):
        self.calls = 0

    def runsync(self, openai_request, timeout_s=None):
        self.calls += 1
        return {
            "choices": [{"message": {"role": "assistant", "content": "verified output"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "cached_tokens": 0},
        }


tmp = tempfile.mkdtemp()
store = gw.Store(os.path.join(tmp, "keys.db"))
meter = meter_mod.Meter(os.path.join(tmp, "meter.db"))
rail = FakeRail()
models = {"qwen3-coder-30b-fp8": {"endpoint": "ep-test", "price_per_m_usd": 0.297,
                                  "cogs_per_m_usd": 0.18, "or_retail_per_m_usd": 0.30}}
config = json.loads(json.dumps(cfg.DEFAULT_CONFIG))
config["free_tier"]["daily_face_usd"] = 0.00001  # tiny quota â†’ 429 reachable fast
gw_inst = gw.PayGateway(store, meter, rail, models, config)

founding_inst = founding.Founding(store, meter, cap=500)
stripe = proc.StripeAdapter(secret_key="sk_test_x", webhook_secret="whsec_test")
router = hooks.WebhookRouter(store, meter, founding_inst, stripe=stripe)
router.attach(os.path.join(tmp, "webhooks.db"))
class FakeStripeCheckout:
    """Checkout sessions without network; webhook verify stays on the real adapter."""
    def create_checkout_session(self, account_hash, amount_usd, success_url, cancel_url, metadata=None):
        return {"id": "cs_test_1", "url": "https://checkout.stripe.com/test"}

api = {"founding": founding_inst, "webhooks": router, "stripe": FakeStripeCheckout(),
       "setup_key": "setup-test-key", "config": config}

httpd = gw.ThreadingHTTPServer(("127.0.0.1", 0), gw.make_handler(gw_inst, api))
port = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{port}"


def post(path, body, key=None, headers=None):
    h = {"Content-Type": "application/json"}
    if key:
        h["Authorization"] = f"Bearer {key}"
    h.update(headers or {})
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
                                 headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode()), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode()), dict(e.headers)


def get(path, key=None):
    h = {"Authorization": f"Bearer {key}"} if key else {}
    req = urllib.request.Request(BASE + path, headers=h, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode()), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode()), dict(e.headers)


# --- bootstrap: account create via setup key ---
code, out, _ = post("/v1/account/create", {"setup_key": "setup-test-key", "plan": "free"})
check("account create 200", code == 200)
check("key shown once (ck_ prefix)", out.get("key", "").startswith("ck_"))
KEY = out["key"]
AH = out["account"]

code, out, _ = post("/v1/account/create", {"setup_key": "WRONG"})
check("bad setup key â†’ 403", code == 403)

# --- 401: bad bearer ---
code, out, _ = post("/v1/chat/completions", {"model": "qwen3-coder-30b-fp8", "messages": []}, key="ck_bogus")
check("bad bearer â†’ 401", code == 401)

# --- 503: unknown model ---
code, out, _ = post("/v1/chat/completions", {"model": "nope", "messages": []}, key=KEY)
check("unknown model â†’ 503 no_supply", code == 503)

# --- the main lane: 200 + meter + headers ---
code, out, headers = post("/v1/chat/completions",
                          {"model": "qwen3-coder-30b-fp8",
                           "messages": [{"role": "user", "content": "x"}]}, key=KEY)
check("chat 200", code == 200)
check("rail relayed (choices present)", "choices" in out)
check("quota header present", "x-cosmos-quota-remaining" in headers or "x-cosmos-credit-balance" in headers)
check("FakeRail called once", rail.calls == 1)
events = meter.tail(10)
check("RUN_SETTLED emitted", any(e.get("event") == "RUN_SETTLED" for e in events))
settled = next(e for e in events if e.get("event") == "RUN_SETTLED")
check("provenance measured", settled["cost"]["provenance"] == "measured")
check("cost = tokens Ã— price", abs(settled["cost"]["measured_usd"] - (120 * 0.297 / 1e6)) < 1e-9)

# --- free-tier 429: the Founding-offer moment ---
code, out, headers = post("/v1/chat/completions",
                          {"model": "qwen3-coder-30b-fp8", "messages": [{"role": "user", "content": "x"}]},
                          key=KEY)
check("quota exhausted â†’ 429", code == 429)
check("429 carries founding_offer", "founding_offer" in out.get("error", {}))
check("429 carries resets_at", "resets_at" in out.get("error", {}))
check("QUOTA_HIT emitted", any(e.get("event") == "QUOTA_HIT" for e in meter.tail(10)))

# --- webhook through the REAL HTTP layer: raw-body signature survives ---
event = {"id": "evt_http_1", "type": "checkout.session.completed",
         "data": {"object": {"id": "cs_http", "client_reference_id": AH, "amount_total": 1000,
                             "metadata": {}}}}
payload = json.dumps(event).encode("utf-8")  # exact bytes over the wire
t = str(int(time.time()))
sig = hmac.new(b"whsec_test", f"{t}.".encode() + payload, hashlib.sha256).hexdigest()
code, out, _ = post("/v1/webhooks/stripe", event, headers={"Stripe-Signature": f"t={t},v1={sig}"})
check("webhook via HTTP â†’ 200 granted", code == 200 and out.get("granted_usd") == 10.0)
check("credits granted via webhook", store.credits(AH) == 10.0)

# --- tampered webhook through HTTP â†’ 400 ---
bad = json.dumps({"id": "evt_http_2", "type": "checkout.session.completed",
                  "data": {"object": {"client_reference_id": AH, "amount_total": 99000}}}).encode()
code, out, _ = post("/v1/webhooks/stripe", json.loads(bad), headers={"Stripe-Signature": "t=1,v1=deadbeef"})
check("tampered webhook via HTTP â†’ 400", code == 400)

# --- founding purchase â†’ checkout session URL ---
code, out, _ = post("/v1/founding/purchase", {"tier": "paid",
                                              "success_url": "https://tokenctr.com/done",
                                              "cancel_url": "https://tokenctr.com/x"}, key=KEY)
check("founding purchase â†’ checkout url", code == 200 and "url" in out.get("checkout", {}))

# --- models + usage endpoints ---
code, out, _ = get("/v1/models", key=KEY)
check("models list 200", code == 200 and out["data"][0]["id"] == "qwen3-coder-30b-fp8")
code, out, _ = get("/v1/usage/today", key=KEY)
check("usage today 200", code == 200 and "free_used_face_usd" in out)

httpd.shutdown()
print(f"\n{PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)

