#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_money_safety — regression tests for the spark13 money-path fixes.

F1: concurrent Founding grants for one account grant exactly once.
F2: /v1/meter/ingest stamps the caller's account (no cross-account writes).
F3: malformed Stripe amounts fail closed as BAD_PAYLOAD (no grant, no 500).
F5: streamed calls without a usage block settle as RUN_UNPRICED, never measured.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import sys
import tempfile
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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


if __name__ == "__main__":
    print("-- test_pay_money_safety --")

    # ---------------------------------------------------------------- F1: grant race
    tmp = tempfile.mkdtemp()
    store = gw.Store(str(Path(tmp) / "keys.db"))
    meter = meter_mod.Meter(str(Path(tmp) / "meter.db"))
    founding = founding_mod.Founding(store, meter, cap=500)
    ah, _raw = store.create_account(plan="free")

    results = []


    def _grant():
        try:
            founding.grant(ah, "paid")
            results.append("granted")
        except founding_mod.FoundingError as e:
            results.append(str(e).split(" ")[0])


    threads = [threading.Thread(target=_grant) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    check("concurrent double-grant: exactly one grant lands",
          sorted(results) == ["ALREADY_FOUNDING", "granted"])
    check("concurrent double-grant: sold incremented once", founding.status()["sold"] == 1)
    check("concurrent double-grant: credits equal one face only",
          abs(store.credits(ah) - 20.0) < 1e-9)

    # ------------------------------------------------- F2/F3 harness: router + HTTP
    tmp2 = tempfile.mkdtemp()
    store2 = gw.Store(str(Path(tmp2) / "keys.db"))
    meter2 = meter_mod.Meter(str(Path(tmp2) / "meter.db"))
    founding2 = founding_mod.Founding(store2, meter2, cap=500)
    stripe = proc_mod.StripeAdapter(secret_key="sk_test_safety", webhook_secret="whsec_safety")
    router = hooks_mod.WebhookRouter(store2, meter2, founding2, stripe=stripe)
    router.attach(str(Path(tmp2) / "webhooks.db"))

    ah_a, key_a = store2.create_account(plan="free")
    ah_b, _key_b = store2.create_account(plan="free")
    store2.grant(ah_a, 10.0)


    def sign(payload: bytes) -> str:
        t = str(int(time.time()))
        sig = hmac.new(b"whsec_safety", f"{t}.".encode() + payload, hashlib.sha256).hexdigest()
        return f"t={t},v1={sig}"


    # ---------------------------------------------------------------- F3: bad amounts
    bad_total = json.dumps({
        "id": "evt_safety_1", "type": "checkout.session.completed",
        "data": {"object": {"id": "cs_x", "client_reference_id": ah_a, "amount_total": "abc"}},
    }).encode()
    try:
        router.receive("stripe", bad_total, {"Stripe-Signature": sign(bad_total)})
        check("stripe malformed amount_total refused", False)
    except hooks_mod.WebhookError as e:
        check("stripe malformed amount_total refused", "BAD_PAYLOAD" in str(e))
    check("stripe malformed amount_total grants nothing", store2.credits(ah_a) == 10.0)

    bad_refund = json.dumps({
        "id": "evt_safety_2", "type": "charge.refunded",
        "data": {"object": {"id": "ch_x", "client_reference_id": ah_a, "amount_refunded": "xyz"}},
    }).encode()
    try:
        router.receive("stripe", bad_refund, {"Stripe-Signature": sign(bad_refund)})
        check("stripe malformed amount_refunded refused", False)
    except hooks_mod.WebhookError as e:
        check("stripe malformed amount_refunded refused", "BAD_PAYLOAD" in str(e))

    # ------------------------------------------------------- F2: ingest over HTTP
    models = {"m1": {"endpoint": "fake", "price_per_m_usd": 0.3, "lane": "A", "stocked": True}}
    config = {"free_tier": {"daily_face_usd": 2.0}}
    gateway = gw.PayGateway(store2, meter2, None, models, config)
    server = ThreadingHTTPServer(("127.0.0.1", 0), gw.make_handler(gateway, None))
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()


    def post(path, body, key):
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}{path}", data=data,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode())


    foreign = {
        "schema": meter_mod.SCHEMA, "event": "RUN_SETTLED", "lane": "A",
        "rail": "safety", "model": "m1", "wallet": "cosmos",
        "tokens": {"in": 5, "out": 5},
        "cost": {"measured_usd": 0.0001, "provenance": "measured"},
        "account": ah_b,  # lies: claims to be account B
    }
    code, out = post("/v1/meter/ingest", {"events": [foreign]}, key_a)
    check("ingest accepts batch", code == 200 and out.get("ingested") == 1)
    stored = meter2.tail(10, account=ah_a)
    check("ingest stamps caller hash (foreign account rewritten)",
          any(e.get("event") == "RUN_SETTLED" for e in stored))
    stored_b = meter2.tail(10, account=ah_b)
    check("ingest writes nothing to the spoofed account",
          not any(e.get("event") == "RUN_SETTLED" for e in stored_b))

    server.shutdown()

    # ---------------------------------------------------------------- F5: streams
    tmp3 = tempfile.mkdtemp()
    store3 = gw.Store(str(Path(tmp3) / "keys.db"))
    meter3 = meter_mod.Meter(str(Path(tmp3) / "meter.db"))


    class NoUsageRail:
        def runsync(self, req):
            raise AssertionError("not used")

        def stream(self, req):
            yield {"id": "c1", "choices": [{"delta": {"content": "hi"}}]}
            yield {"id": "c2", "choices": [{"delta": {"content": "there"}}]}


    class UsageRail:
        def runsync(self, req):
            raise AssertionError("not used")

        def stream(self, req):
            yield {"id": "c1", "choices": [{"delta": {"content": "hi"}}]}
            yield {"id": "c2", "choices": [],
                   "usage": {"prompt_tokens": 50, "completion_tokens": 10}}


    gw_nousage = gw.PayGateway(store3, meter3, NoUsageRail(), models, config)
    ah_c, key_c = store3.create_account(plan="free")
    store3.grant(ah_c, 10.0)
    chunks = list(gw_nousage.chat_stream(key_c, {"model": "m1", "messages": []}))
    check("stream without usage still terminates", any("DONE" in c for c in chunks))
    evs = meter3.tail(10, account=ah_c)
    check("stream without usage emits RUN_UNPRICED",
          any(e.get("event") == "RUN_UNPRICED" for e in evs))
    check("stream without usage emits no RUN_SETTLED",
          not any(e.get("event") == "RUN_SETTLED" for e in evs))
    check("stream without usage refunds the full reserve",
          abs(store3.credits(ah_c) - 10.0) < 1e-6)

    gw_usage = gw.PayGateway(store3, meter3, UsageRail(), models, config)
    ah_d, key_d = store3.create_account(plan="free")
    store3.grant(ah_d, 10.0)
    list(gw_usage.chat_stream(key_d, {"model": "m1", "messages": []}))
    evs_d = meter3.tail(10, account=ah_d)
    settled = next((e for e in evs_d if e.get("event") == "RUN_SETTLED"), None)
    check("stream with usage still settles measured",
          settled is not None and settled["cost"]["provenance"] == "measured")

    print(f"\n{PASS} pass, {FAIL} fail")
    sys.exit(1 if FAIL else 0)
