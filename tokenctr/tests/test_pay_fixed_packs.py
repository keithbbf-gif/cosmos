#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_fixed_packs: the server owns pack prices (Keith 2026-10-18).

/v1/credits/purchase: only mini $5 / maker $19 / studio $59, priced server-side;
unknown pack or a client amount that differs from the table is 400 and no
checkout session is created. /v1/founding/purchase: paid $10, verified $1.
Line-item names match the Stripe products. A signed verified-tier webhook
credits exactly $1; verified -> founding upgrade works; repeat tier refused.
No network (fake checkout over a real HTTP server; real webhook verifier).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import tempfile
import threading
import time
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cosmos_pay_config as cfg
import cosmos_pay_founding as founding
import cosmos_pay_gateway as gw
import cosmos_pay_meter as meter_mod
import cosmos_pay_processors as proc
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


WHSEC = "whsec_test_fixed"


class RecordingStripe(proc.StripeAdapter):
    """Real adapter (real webhook verify, real form building); network replaced."""

    def __init__(self):
        super().__init__(secret_key="sk_test_x", webhook_secret=WHSEC)
        self.forms = []

    def _post_form(self, path, params):  # noqa: D401 - test double
        self.forms.append((path, dict(params)))
        return {"id": f"cs_test_{len(self.forms)}", "url": f"https://checkout.stripe.com/c/pay/cs_test_{len(self.forms)}"}


def signed(body: bytes):
    t = str(int(time.time()))
    sig = hmac.new(WHSEC.encode(), (t + ".").encode() + body, hashlib.sha256).hexdigest()
    return {"Stripe-Signature": f"t={t},v1={sig}"}


if __name__ == "__main__":
    tmp = tempfile.mkdtemp()
    store = gw.Store(os.path.join(tmp, "keys.db"))
    meter = meter_mod.Meter(os.path.join(tmp, "meter.db"))
    config = json.loads(json.dumps(cfg.DEFAULT_CONFIG))
    config["free_tier"]["daily_face_usd"] = 0.0
    g = gw.PayGateway(store, meter, None, {}, config)
    f = founding.Founding(store, meter, cap=500)
    stripe = RecordingStripe()
    router = hooks.WebhookRouter(store, meter, f, stripe=stripe)
    router.attach(os.path.join(tmp, "webhooks.db"))
    api = {"founding": f, "webhooks": router, "stripe": stripe, "setup_key": "s", "config": config}
    httpd = gw.ThreadingHTTPServer(("127.0.0.1", 0), gw.make_handler(g, api))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    BASE = f"http://127.0.0.1:{httpd.server_address[1]}"

    def post(path, body, key=None, headers=None, raw=None):
        h = {"Content-Type": "application/json"}
        if key:
            h["Authorization"] = f"Bearer {key}"
        h.update(headers or {})
        data = raw if raw is not None else json.dumps(body).encode()
        req = urllib.request.Request(BASE + path, data=data, headers=h, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode())

    ah, key = store.create_account(plan="free", credits_face_usd=0.0)

    def last_form():
        return stripe.forms[-1][1] if stripe.forms else {}

    # --- valid packs: server price + product name ---
    for pack, cents, name in (("mini", "500", "Mini — $5 credit"), ("maker", "1900", "Maker — $19 credit"),
                              ("studio", "5900", "Studio — $59 credit")):
        n0 = len(stripe.forms)
        code, out = post("/v1/credits/purchase", {"pack_id": pack}, key=key)
        fm = last_form()
        check(f"{pack}: 200 + session", code == 200 and out.get("checkout", {}).get("url", "").startswith("https://checkout.stripe.com/")
              and len(stripe.forms) == n0 + 1)
        check(f"{pack}: unit_amount {cents}", fm.get("line_items[0][price_data][unit_amount]") == cents)
        check(f"{pack}: line item name {name!r}", fm.get("line_items[0][price_data][product_data][name]") == name)
        check(f"{pack}: metadata pack_id + account", fm.get("metadata[pack_id]") == pack and fm.get("metadata[account_hash]") == ah)

    code, out = post("/v1/credits/purchase", {"pack_id": "maker", "amount_usd": 19}, key=key)
    check("matching client amount accepted", code == 200 and last_form().get("line_items[0][price_data][unit_amount]") == "1900")
    code, out = post("/v1/credits/purchase", {"pack": "MINI"}, key=key)
    check("pack alias + case-insensitive", code == 200 and last_form().get("line_items[0][price_data][unit_amount]") == "500")

    # --- rejections create no session ---
    for label, body, want in (("tampered amount (mini, 1)", {"pack_id": "mini", "amount_usd": 1}, "amount_mismatch"),
                              ("tampered amount (studio, 0.59)", {"pack_id": "studio", "amount_usd": 0.59}, "amount_mismatch"),
                              ("non-numeric amount", {"pack_id": "mini", "amount_usd": "abc"}, "amount_mismatch"),
                              ("unknown pack", {"pack_id": "mega", "amount_usd": 100}, "bad_pack"),
                              ("missing pack (amount only)", {"amount_usd": 5}, "bad_pack")):
        n0 = len(stripe.forms)
        code, out = post("/v1/credits/purchase", body, key=key)
        check(f"{label} -> 400 {want}, no session", code == 400 and out.get("error", {}).get("code") == want and len(stripe.forms) == n0)
    code, _ = post("/v1/credits/purchase", {"pack_id": "mini"})
    check("no key -> 401", code == 401)

    # --- founding offers ---
    code, out = post("/v1/founding/purchase", {"tier": "verified"}, key=key)
    fm = last_form()
    check("verified: 200, $1, name, founding metadata", code == 200 and fm.get("line_items[0][price_data][unit_amount]") == "100"
          and fm.get("line_items[0][price_data][product_data][name]") == "Card verification — $1 credit"
          and fm.get("metadata[founding]") == "verified" and out.get("amount_usd") == 1.0)
    code, out = post("/v1/founding/purchase", {"tier": "paid"}, key=key)
    fm = last_form()
    check("paid: 200, $10, name", code == 200 and fm.get("line_items[0][price_data][unit_amount]") == "1000"
          and fm.get("line_items[0][price_data][product_data][name]") == "Founding — lifetime membership + $20 credit")
    n0 = len(stripe.forms)
    code, out = post("/v1/founding/purchase", {"tier": "verified", "amount_usd": 11}, key=key)
    check("verified with tampered amount -> 400, no session", code == 400 and len(stripe.forms) == n0)
    code, out = post("/v1/founding/purchase", {"tier": "gold"}, key=key)
    check("bad tier -> 400", code == 400 and out["error"]["code"] == "bad_tier")

    # --- signed webhook: verified tier credits exactly $1 ---
    evt = {"id": "evt_fixed_verified", "type": "checkout.session.completed",
           "data": {"object": {"id": "cs_v", "amount_total": 100, "payment_status": "paid",
                               "client_reference_id": ah, "metadata": {"founding": "verified", "account_hash": ah}}}}
    raw = json.dumps(evt).encode()
    before = store.credits(ah)
    code, out = post("/v1/webhooks/stripe", None, headers=signed(raw), raw=raw)
    check("verified webhook 200", code == 200)
    check("verified webhook credits exactly $1", abs(store.credits(ah) - before - 1.0) < 1e-12)
    plan = store.db.execute("SELECT plan FROM accounts WHERE account_hash = ?", (ah,)).fetchone()[0]
    check("plan verified_free", plan == "verified_free")
    code, out = post("/v1/founding/purchase", {"tier": "verified"}, key=key)
    check("second verified checkout -> 409", code == 409)

    # --- advertised upgrade: verified -> founding ---
    code, out = post("/v1/founding/purchase", {"tier": "paid"}, key=key)
    check("verified account may start Founding checkout", code == 200)
    evt2 = {"id": "evt_fixed_paid", "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_p", "amount_total": 1000, "payment_status": "paid",
                                "client_reference_id": ah, "metadata": {"founding": "paid", "account_hash": ah}}}}
    raw2 = json.dumps(evt2).encode()
    before = store.credits(ah)
    code, out = post("/v1/webhooks/stripe", None, headers=signed(raw2), raw=raw2)
    check("upgrade webhook credits $20, plan founding", code == 200 and abs(store.credits(ah) - before - 20.0) < 1e-12
          and store.db.execute("SELECT plan FROM accounts WHERE account_hash = ?", (ah,)).fetchone()[0] == "founding")
    code, out = post("/v1/founding/purchase", {"tier": "paid"}, key=key)
    check("founding account -> 409 on another Founding checkout", code == 409)

    # --- pack webhook credits the pack amount ---
    ah2, key2 = store.create_account(plan="free", credits_face_usd=0.0)
    evt3 = {"id": "evt_fixed_mini", "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_m", "amount_total": 500, "payment_status": "paid",
                                "client_reference_id": ah2, "metadata": {"account_hash": ah2, "pack_id": "mini"}}}}
    raw3 = json.dumps(evt3).encode()
    code, out = post("/v1/webhooks/stripe", None, headers=signed(raw3), raw=raw3)
    check("mini webhook credits $5", code == 200 and abs(store.credits(ah2) - 5.0) < 1e-12)

    httpd.shutdown()
    print(f"{PASS} pass, {FAIL} fail")
    sys.exit(1 if FAIL else 0)
