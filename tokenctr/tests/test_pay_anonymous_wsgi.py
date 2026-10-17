#!/usr/bin/env python3
"""Anonymous key route + passenger_wsgi adapter (offline, temp root)."""
import io, json, os, sys, tempfile
ROOT = tempfile.mkdtemp(prefix="cpr_anon_")
os.environ["COSMOS_PAY_ROOT"] = ROOT
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open(os.path.join(ROOT, "config.json"), "w") as f:
    json.dump({"anonymous": {"per_ip_daily": 2, "global_daily": 3}, "free_tier": {"daily_face_usd": 0.0}}, f)
with open(os.path.join(ROOT, "secrets.json"), "w") as f:
    json.dump({"setup_key": "setup_test", "stripe_secret_key": "sk_test_offline_dummy", "stripe_webhook_secret": "whsec_offline_test"}, f)
import passenger_wsgi as pw  # noqa: E402

P = F = 0
def check(name, cond):
    global P, F
    if cond: P += 1
    else: F += 1; print("FAIL", name)

def call(method, path, body=b"", headers=None):
    env = {"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": "", "wsgi.input": io.BytesIO(body),
           "CONTENT_LENGTH": str(len(body)), "CONTENT_TYPE": "application/json", "REMOTE_ADDR": "127.0.0.1"}
    for k, v in (headers or {}).items():
        env["HTTP_" + k.upper().replace("-", "_")] = v
    out = {}
    def sr(status, hdrs): out["status"] = status; out["headers"] = dict(hdrs)
    data = b"".join(pw.application(env, sr))
    return int(out["status"].split()[0]), out["headers"], data

c, h, b = call("GET", "/healthz"); check("healthz 200", c == 200 and json.loads(b)["ok"])
check("cors on healthz", h.get("Access-Control-Allow-Origin") == "*")
c, h, _ = call("OPTIONS", "/v1/account/anonymous", headers={"Origin": "https://tokenctr.com"}); check("preflight 204", c == 204)
ip1 = {"CF-Connecting-IP": "203.0.113.5"}
c, h, b = call("POST", "/v1/account/anonymous", b"{}", ip1); j = json.loads(b)
check("anon 200", c == 200); check("anon api_key", j.get("api_key", "").startswith("ck_")); check("anon $0", j.get("credits_face_usd") == 0.0)
key = j["api_key"]
c, _, b = call("GET", "/v1/usage/today", headers={"Authorization": "Bearer " + key}); check("usage with anon key", c == 200 and json.loads(b)["credits_face_usd"] == 0.0)
c, _, _ = call("POST", "/v1/account/anonymous", b"{}", ip1); check("anon 2nd same ip ok", c == 200)
c, _, b = call("POST", "/v1/account/anonymous", b"{}", ip1); check("anon 3rd same ip 429", c == 429 and json.loads(b)["error"]["code"] == "anonymous_ip_limit")
c, _, _ = call("POST", "/v1/account/anonymous", b"{}", {"CF-Connecting-IP": "203.0.113.9"}); check("anon other ip ok", c == 200)
c, _, b = call("POST", "/v1/account/anonymous", b"{}", {"CF-Connecting-IP": "203.0.113.10"}); check("global cap 429", c == 429 and json.loads(b)["error"]["code"] == "anonymous_daily_cap")
c, _, _ = call("POST", "/v1/credits/purchase", b'{"amount_usd":5}'); check("purchase no key 401", c == 401)
c, _, b = call("POST", "/v1/webhooks/stripe", b'{"type":"x"}', {"Stripe-Signature": "t=1,v1=bad"}); check("webhook bad sig 400", c == 400)
import hmac, hashlib, time
acct = j["account"]
def signed(evt):
    body = json.dumps(evt).encode(); t = str(int(time.time()))
    sig = hmac.new(b"whsec_offline_test", (t + ".").encode() + body, hashlib.sha256).hexdigest()
    return call("POST", "/v1/webhooks/stripe", body, {"Stripe-Signature": f"t={t},v1={sig}"})
def sess(eid, status, etype="checkout.session.completed"):
    return {"id": eid, "type": etype, "data": {"object": {"id": "cs_test_x", "amount_total": 500,
            "payment_status": status, "metadata": {"account_hash": acct}}}}
c, _, b = signed(sess("evt_unpaid", "unpaid")); check("unpaid completed not granted", c == 200 and json.loads(b).get("routed") is False)
c, _, b = call("GET", "/v1/usage/today", headers={"Authorization": "Bearer " + key}); check("balance still 0", json.loads(b)["credits_face_usd"] == 0.0)
c, _, b = signed(sess("evt_async_ok", "paid", "checkout.session.async_payment_succeeded")); check("async succeeded grants", c == 200 and json.loads(b).get("granted_usd") == 5.0)
c, _, b = signed(sess("evt_async_ok", "paid", "checkout.session.async_payment_succeeded")); check("replay is duplicate", json.loads(b).get("duplicate") is True)
c, _, b = call("GET", "/v1/usage/today", headers={"Authorization": "Bearer " + key}); check("balance 5", json.loads(b)["credits_face_usd"] == 5.0)
print(f"{P} pass, {F} fail"); sys.exit(1 if F else 0)
