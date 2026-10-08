#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_webhooks — Stripe signature verify, routing, grants, idempotency."""
import sys
import os
import json
import time
import hmac
import hashlib
import tempfile
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cosmos_pay_meter as meter
import cosmos_pay_gateway as gw
import cosmos_pay_founding as founding
import cosmos_pay_webhooks as hooks

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


WHSEC = "whsec_test_0000000000000000"
tmp = tempfile.mkdtemp()
store = gw.Store(os.path.join(tmp, "keys.db"))
m = meter.Meter(os.path.join(tmp, "meter.db"))
f = founding.Founding(store, m, cap=500)
router = hooks.WebhookRouter(store, m, f, stripe=hooks  # placeholder replaced below
                             )
# real stripe adapter with a known webhook secret
import cosmos_pay_processors as proc
stripe = proc.StripeAdapter(secret_key="sk_test_x", webhook_secret=WHSEC)
router = hooks.WebhookRouter(store, m, f, stripe=stripe)
router.attach(os.path.join(tmp, "webhooks.db"))

ah, _ = store.create_account(plan="free")


def sign(payload: bytes) -> str:
    t = str(int(time.time()))
    sig = hmac.new(WHSEC.encode(), f"{t}.".encode() + payload, hashlib.sha256).hexdigest()
    return f"t={t},v1={sig}"


# --- checkout.session.completed → credit grant + CREDIT_PURCHASED ---
event = {
    "id": "evt_001", "type": "checkout.session.completed",
    "data": {"object": {"id": "cs_001", "client_reference_id": ah,
                        "amount_total": 1000,  # $10.00
                        "metadata": {}}},
}
payload = json.dumps(event).encode()
out = router.receive("stripe", payload, {"Stripe-Signature": sign(payload)})
check("checkout completed → granted $10", out.get("granted_usd") == 10.0)
check("credits incremented", store.credits(ah) == 10.0)
check("CREDIT_PURCHASED emitted", any(e.get("event") == "CREDIT_PURCHASED" and e.get("amount_usd") == 10.0
                                      for e in m.tail(10)))

# --- idempotency: same event replayed → duplicate, no double grant ---
out2 = router.receive("stripe", payload, {"Stripe-Signature": sign(payload)})
check("replay → duplicate no-op", out2.get("duplicate") is True)
check("no double grant", store.credits(ah) == 10.0)

# --- tampered signature → VERIFY_FAILED ---
bad = json.dumps({"id": "evt_002", "type": "checkout.session.completed",
                  "data": {"object": {"client_reference_id": ah, "amount_total": 99000}}}).encode()
try:
    router.receive("stripe", bad, {"Stripe-Signature": "t=1,v1=deadbeef"})
    check("tampered webhook refused", False)
except proc.ProcessorError as e:
    check("tampered webhook refused", "VERIFY_FAILED" in str(e))

# --- founding paid tier via metadata ---
event_f = {
    "id": "evt_003", "type": "checkout.session.completed",
    "data": {"object": {"id": "cs_003", "client_reference_id": ah, "amount_total": 1000,
                        "metadata": {"founding": "paid"}}},
}
payload_f = json.dumps(event_f).encode()
out = router.receive("stripe", payload_f, {"Stripe-Signature": sign(payload_f)})
check("founding paid → plan=founding", store.db.execute(
    "SELECT plan FROM accounts WHERE account_hash = ?", (ah,)).fetchone()[0] == "founding")
check("founding paid → $20 face granted", store.credits(ah) == 30.0)  # 10 + 20
check("founding status 1/500", f.status()["sold"] == 1)

# --- unknown processor ---
try:
    router.receive("venmo", b"{}", {})
    check("unknown processor refused", False)
except hooks.WebhookError as e:
    check("unknown processor refused", "UNKNOWN_PROCESSOR" in str(e))

# --- unhandled event type routes cleanly ---
event_u = {"id": "evt_004", "type": "invoice.paid",
           "data": {"object": {}}}
payload_u = json.dumps(event_u).encode()
out = router.receive("stripe", payload_u, {"Stripe-Signature": sign(payload_u)})
check("unhandled event routes cleanly (no crash)", out.get("routed") is False)

print(f"\n{PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)
