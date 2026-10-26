#!/usr/bin/env python3
"""Account login (cosmos_pay_auth) through passenger_wsgi, offline temp root.
Email codes go to a file outbox; OAuth provider exchange is mocked."""
import glob, io, json, os, re, sqlite3, sys, tempfile
ROOT = tempfile.mkdtemp(prefix="cpr_auth_")
OUT = os.path.join(ROOT, "outbox")
os.environ["COSMOS_PAY_ROOT"] = ROOT
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open(os.path.join(ROOT, "config.json"), "w") as f:
    json.dump({"free_tier": {"daily_face_usd": 0.0},
               "auth": {"enabled": True, "mail_backend": "file", "mail_outbox": OUT,
                        "limits": {"email_addr": 3, "email_ip": 50, "verify_ip": 100, "claim_ip": 4, "oauth_ip": 50}}}, f)
with open(os.path.join(ROOT, "secrets.json"), "w") as f:
    json.dump({"setup_key": "setup_test", "stripe_secret_key": "sk_test_offline_dummy",
               "stripe_webhook_secret": "whsec_offline_test", "auth_pepper": "pepper-test",
               "github_client_id": "gh_id", "github_client_secret": "gh_secret"}, f)
import cosmos_pay_auth as auth_mod  # noqa: E402
import passenger_wsgi as pw  # noqa: E402

P = F = 0
def check(name, cond):
    global P, F
    if cond: P += 1
    else: F += 1; print("FAIL", name)

SITE = "https://tokenctr.com"
def call(method, path, body=None, headers=None, ip="198.51.100.7"):
    raw = json.dumps(body).encode() if body is not None else b""
    qs = ""
    if "?" in path: path, qs = path.split("?", 1)
    env = {"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": qs, "wsgi.input": io.BytesIO(raw),
           "CONTENT_LENGTH": str(len(raw)), "CONTENT_TYPE": "application/json", "REMOTE_ADDR": "127.0.0.1",
           "HTTP_CF_CONNECTING_IP": ip}
    for k, v in (headers or {}).items():
        env["HTTP_" + k.upper().replace("-", "_")] = v
    out = {}
    def sr(status, hdrs): out["status"] = status; out["headers"] = hdrs
    data = b"".join(pw.application(env, sr))
    try: j = json.loads(data) if data else {}
    except Exception: j = {}
    return int(out["status"].split()[0]), out["headers"], j

def hget(hdrs, name): return [v for k, v in hdrs if k.lower() == name.lower()]
def cookie_from(hdrs, name="__Secure-tc_session"):
    for v in hget(hdrs, "Set-Cookie"):
        if v.startswith(name + "="): return v.split(";")[0].split("=", 1)[1], v
    return None, None

def last_code(addr):
    files = sorted(glob.glob(OUT + "/*.eml"))
    for fp in reversed(files):
        t = open(fp, encoding="utf-8", errors="replace").read()
        if ("To: " + addr) in t:
            return re.search(r"sign-in code is (\d{6})", t).group(1)
    return None

O = {"Origin": SITE}
# ---- config + disabled-safe basics
c, h, j = call("GET", "/v1/auth/config", headers=O)
check("config 200", c == 200 and j["enabled"] is True and j["providers"]["email"] and j["providers"]["github"]
      and not j["providers"]["google"] and j["providers"]["phone"] is False)
check("config cors exact origin+creds", hget(h, "Access-Control-Allow-Origin") == [SITE]
      and hget(h, "Access-Control-Allow-Credentials") == ["true"])
c, h, _ = call("GET", "/healthz"); check("api routes still *", hget(h, "Access-Control-Allow-Origin") == ["*"])
c, h, _ = call("GET", "/healthz", headers={"Origin": "https://evil.example"})
check("foreign origin gets *, no creds", hget(h, "Access-Control-Allow-Origin") == ["*"] and not hget(h, "Access-Control-Allow-Credentials"))
c, h, _ = call("OPTIONS", "/v1/auth/session", headers=O); check("auth preflight", c == 204 and hget(h, "Access-Control-Allow-Credentials") == ["true"])
c, _, j = call("GET", "/v1/auth/session", headers=O); check("signed out session", c == 200 and j["signed_in"] is False)
c, _, _ = call("GET", "/v1/auth/session", headers={"Origin": "https://evil.example"}); check("bad origin GET 403", c == 403)
c, _, _ = call("POST", "/v1/auth/email/start", {"email": "a@example.com"}); check("no origin POST 403", c == 403)

# ---- email sign-up + enumeration resistance
c, _, j1 = call("POST", "/v1/auth/email/start", {"email": "New@Example.com"}, O)
check("email start 200 generic", c == 200 and "If that address" in j1["message"])
code = last_code("new@example.com"); check("code mailed", code is not None and len(code) == 6)
c, _, j = call("POST", "/v1/auth/email/verify", {"email": "new@example.com", "code": "000000" if code != "000000" else "111111"}, O)
check("wrong code 400", c == 400 and j["error"]["code"] == "bad_code")
c, h, j = call("POST", "/v1/auth/email/verify", {"email": "new@example.com", "code": code}, O)
sid, raw_cookie = cookie_from(h)
check("verify ok new user", c == 200 and j["new_user"] is True and sid)
check("hint cookie set (not HttpOnly)", any(v.startswith("tc_signed_in=1;") and "HttpOnly" not in v for v in hget(h, "Set-Cookie")))
check("cookie flags", raw_cookie and all(x in raw_cookie for x in ("HttpOnly", "Secure", "SameSite=Lax", "Domain=.tokenctr.com")))
c, _, j = call("POST", "/v1/auth/email/verify", {"email": "new@example.com", "code": code}, O)
check("code single use", c == 400)
C = {"Origin": SITE, "Cookie": "__Secure-tc_session=" + sid}
c, _, me = call("GET", "/v1/auth/session", headers=C)
check("session signed in", c == 200 and me["signed_in"] and me["user"]["email"] == "new@example.com" and me["csrf"])
check("new account $0 free", me["account"]["plan"] == "free" and me["account"]["credits_face_usd"] == 0.0)
csrf = me["csrf"]; CC = dict(C, **{"X-TC-CSRF": csrf})
# repeat sign-in with existing address -> same user
c, _, _ = call("POST", "/v1/auth/email/start", {"email": "new@example.com"}, O)
c, h2, j = call("POST", "/v1/auth/email/verify", {"email": "new@example.com", "code": last_code("new@example.com")}, O)
check("existing email signs in same user", c == 200 and j["new_user"] is False)
sid2 = cookie_from(h2)[0]
# per-address throttle keeps the same response
for _ in range(3): c, _, jx = call("POST", "/v1/auth/email/start", {"email": "new@example.com"}, O)
check("throttled same response", c == 200 and jx["message"] == j1["message"])
c, _, jn = call("POST", "/v1/auth/email/start", {"email": "nobody@example.com"}, O)
check("unknown address same response", jn["message"] == j1["message"])
# attempts limit
c, _, _ = call("POST", "/v1/auth/email/start", {"email": "brute@example.com"}, O)
good = last_code("brute@example.com"); bad = "123456" if good != "123456" else "654321"
for _ in range(5): call("POST", "/v1/auth/email/verify", {"email": "brute@example.com", "code": bad}, O)
c, _, _ = call("POST", "/v1/auth/email/verify", {"email": "brute@example.com", "code": good}, O)
check("code dead after 5 bad attempts", c == 400)

# ---- session drives existing routes
c, _, j = call("GET", "/v1/account", headers=C); check("/v1/account via session", c == 200 and j["account"] == me["account"]["account"])
c, h, _ = call("GET", "/v1/account", headers=C); check("session route echoes origin", hget(h, "Access-Control-Allow-Origin") == [SITE])
c, _, _ = call("GET", "/v1/account", headers={"Cookie": C["Cookie"]}); check("cookie without Origin ignored", c == 401)
c, _, _ = call("GET", "/v1/account", headers={"Cookie": C["Cookie"], "Origin": "https://evil.example"}); check("cookie from foreign origin ignored", c == 401)
c, _, _ = call("POST", "/v1/keys/issue", {"label": "x"}, C); check("POST without CSRF refused", c == 401)
c, _, j = call("POST", "/v1/keys/issue", {"label": "dash"}, CC); check("POST with CSRF issues key", c == 200 and j["key"].startswith("ck_"))
newkey = j["key"]
c, _, j = call("GET", "/v1/account", headers={"Authorization": "Bearer " + newkey}); check("bearer still works", c == 200)
c, h, _ = call("GET", "/v1/account", headers={"Authorization": "Bearer ck_bogus", "Cookie": C["Cookie"], "Origin": SITE})
check("bearer wins over cookie (bad bearer=401)", c == 401)
c, _, _ = call("GET", "/v1/account", headers=dict(C, **{"X-TC-Key": "nothex!!"})); check("bad X-TC-Key 401", c == 401)

# ---- sessions list / revoke / sign out everywhere
c, _, j = call("GET", "/v1/auth/sessions", headers=C); check("sessions list 2", c == 200 and len(j["data"]) == 2 and any(s["current"] for s in j["data"]))
other = [s for s in j["data"] if not s["current"]][0]["id"]
c, _, _ = call("POST", "/v1/auth/sessions/revoke", {"id": other}, C); check("revoke needs csrf", c == 403)
c, _, j = call("POST", "/v1/auth/sessions/revoke", {"id": other}, CC); check("revoke other session", c == 200 and j["revoked"] == 1)
c, _, j = call("GET", "/v1/auth/session", headers={"Origin": SITE, "Cookie": "__Secure-tc_session=" + sid2}); check("revoked session signed out", j["signed_in"] is False)

# ---- claim existing key holder
c, _, j = call("POST", "/v1/account/create", {"setup_key": "setup_test"}); oldkey = j["key"]; oldacct = j["account"]
c, _, j = call("POST", "/v1/auth/claim", {"key": "ck_wrong"}, O); check("claim bad key", c == 400)
c, h, j = call("POST", "/v1/auth/claim", {"key": oldkey}, O); csid = cookie_from(h)[0]
check("claim ok needs method", c == 200 and j["needs_method"] and csid)
CL = {"Origin": SITE, "Cookie": "__Secure-tc_session=" + csid}
c, _, cm = call("GET", "/v1/auth/session", headers=CL); check("claimed session same account", cm["account"]["account"] == oldacct and cm["needs_method"])
c, _, _ = call("GET", "/v1/account", headers={"Authorization": "Bearer " + oldkey}); check("old key keeps working", c == 200)
c, _, j = call("POST", "/v1/auth/claim", {"key": oldkey}, O); check("re-claim allowed while no method", c == 200)
# add email as link (requires signed-in + verified code)
c, _, _ = call("POST", "/v1/auth/email/start", {"email": "old@example.com", "link": True}, CL)
c, _, j = call("POST", "/v1/auth/email/verify", {"email": "old@example.com", "code": last_code("old@example.com")}, CL)
check("link email to claimed account", c == 200 and j.get("linked") == "email")
c, _, j = call("POST", "/v1/auth/claim", {"key": oldkey}, O); check("claim refused once login exists", c == 409 and j["error"]["code"] == "already_claimed")
c, _, _ = call("POST", "/v1/auth/email/start", {"email": "old@example.com"}, O)
c, _, j = call("POST", "/v1/auth/email/verify", {"email": "old@example.com", "code": last_code("old@example.com")}, O)
check("sign in to claimed account by email", c == 200 and j["new_user"] is False)
# linking an email owned by another user fails
call("POST", "/v1/auth/email/start", {"email": "third@example.com"}, O)
call("POST", "/v1/auth/email/verify", {"email": "third@example.com", "code": last_code("third@example.com")}, O)
c, _, _ = call("POST", "/v1/auth/email/start", {"email": "third@example.com", "link": True}, CL)
c, _, j = call("POST", "/v1/auth/email/verify", {"email": "third@example.com", "code": last_code("third@example.com")}, CL)
check("link email in use elsewhere 409", c == 409 and j["error"]["code"] == "identity_in_use")
# unlink last method refused
ids = call("GET", "/v1/auth/identities", headers=CL)[2]["data"]
c, _, cm = call("GET", "/v1/auth/session", headers=CL)
c, _, j = call("POST", "/v1/auth/identities/unlink", {"id": ids[0]["id"]}, dict(CL, **{"X-TC-CSRF": cm["csrf"]}))
check("unlink last method refused", c == 409 and j["error"]["code"] == "last_method")
# claim rate limit (limit 4/h per ip)
for _ in range(5): c, _, _ = call("POST", "/v1/auth/claim", {"key": "ck_x"}, O, ip="203.0.113.77")
check("claim rate limited", c == 429)

# ---- OAuth (GitHub, mocked exchange)
c, h, _ = call("GET", "/v1/auth/google/start")
check("unconfigured provider redirects with error", c == 302 and "provider_unavailable" in hget(h, "Location")[0])
c, h, _ = call("GET", "/v1/auth/github/start?return_to=/logs.html")
loc = hget(h, "Location")[0]; st, stc = cookie_from(h, "__Secure-tc_oauth")
check("github start redirect", c == 302 and loc.startswith("https://github.com/login/oauth/authorize?") and "code_challenge_method=S256" in loc
      and "scope=read%3Auser+user%3Aemail" in loc and "redirect_uri=https%3A%2F%2Fapi.tokenctr.com%2Fv1%2Fauth%2Fgithub%2Fcallback" in loc)
state = re.search(r"state=([^&]+)", loc).group(1)
check("state cookie bound", st == state and "HttpOnly" in stc)
seen = {}
def fake(self, code, verifier, redirect_uri):
    seen["verifier"] = verifier; seen["code"] = code
    return dict(seen.get("ret") or {"subject": "4242", "email": "gh@example.com", "email_verified": True, "display": "octo"})
auth_mod.OAuthProvider.fetch_identity = fake
c, h, _ = call("GET", f"/v1/auth/github/callback?code=abc&state={state}", headers={"Cookie": "__Secure-tc_oauth=WRONG"})
check("state mismatch refused", c == 302 and "state_mismatch" in hget(h, "Location")[0])
c, h, _ = call("GET", f"/v1/auth/github/callback?code=abc&state={state}", headers={"Cookie": "__Secure-tc_oauth=" + state})
check("state consumed on first use (even after mismatch? no: mismatch did not consume)", c == 302)
gsid = cookie_from(h)[0]
check("github new user signed in", gsid and hget(h, "Location")[0].startswith(SITE + "/logs.html?signed_in=github") and len(seen["verifier"]) > 40)
c, h, _ = call("GET", f"/v1/auth/github/callback?code=abc&state={state}", headers={"Cookie": "__Secure-tc_oauth=" + state})
check("state replay refused", "state_expired" in hget(h, "Location")[0])
c, h, _ = call("GET", "/v1/auth/github/start?return_to=//evil.example/x")
st2 = re.search(r"state=([^&]+)", hget(h, "Location")[0]).group(1)
seen["ret"] = {"subject": "999", "email": "old@example.com", "email_verified": True, "display": "x"}
c, h, _ = call("GET", f"/v1/auth/github/callback?code=z&state={st2}", headers={"Cookie": "__Secure-tc_oauth=" + st2})
check("no auto-link on matching email", "email_in_use_other_method" in hget(h, "Location")[0] and not cookie_from(h)[0])
# link GitHub to the claimed (old) account while signed in
c, h, _ = call("GET", "/v1/auth/github/start?link=1&return_to=/account.html", headers={"Cookie": CL["Cookie"]})
st3 = re.search(r"state=([^&]+)", hget(h, "Location")[0]).group(1)
c, h, _ = call("GET", f"/v1/auth/github/callback?code=z&state={st3}", headers={"Cookie": CL["Cookie"] + "; __Secure-tc_oauth=" + st3})
check("link github while signed in", "linked=github" in hget(h, "Location")[0])
c, _, j = call("GET", "/v1/auth/identities", headers=CL); check("two methods now", len(j["data"]) == 2)
c, h, _ = call("GET", "/v1/auth/github/start?link=1")
check("link without session refused", "not_signed_in" in hget(h, "Location")[0])

# ---- export + delete
c, h, j = call("GET", "/v1/auth/export", headers=C)
check("export", c == 200 and j["user"]["id"] and "keys" in j and "security_log" in j and hget(h, "Content-Disposition"))
check("export hides subjects", "_subject" not in json.dumps(j))
c, _, j = call("POST", "/v1/auth/delete", {"confirm_email": "wrong@example.com"}, CC); check("delete needs typed email", c == 400)
# give the account a balance -> warning
db = sqlite3.connect(os.path.join(ROOT, "keys.db")); db.execute("UPDATE accounts SET credits_face_usd=7.5 WHERE account_hash=?", (me["account"]["account"],)); db.commit()
c, _, j = call("POST", "/v1/auth/delete", {"confirm_email": "new@example.com"}, CC)
check("balance warning", c == 409 and j["error"]["code"] == "balance_remaining" and "7.50" in j["error"]["message"])
c, h, j = call("POST", "/v1/auth/delete", {"confirm_email": "new@example.com", "acknowledge_balance": True}, CC)
check("delete ok", c == 200 and j["deleted"])
c, _, j = call("GET", "/v1/auth/session", headers=C); check("deleted -> signed out", j["signed_in"] is False)
c, _, _ = call("GET", "/v1/account", headers={"Authorization": "Bearer " + newkey}); check("deleted account keys revoked", c == 401)
r = db.execute("SELECT credits_face_usd FROM accounts WHERE account_hash=?", (me["account"]["account"],)).fetchone()
check("no automatic refund / balance row kept", r and r[0] == 7.5)

# ---- sign out + sign out everywhere
c, _, cm = call("GET", "/v1/auth/session", headers=CL)
c, h, _ = call("POST", "/v1/auth/signout-all", {}, dict(CL, **{"X-TC-CSRF": cm["csrf"]}))
check("signout-all clears cookie", c == 200 and "Max-Age=0" in cookie_from(h)[1])
c, _, j = call("GET", "/v1/auth/session", headers=CL); check("after signout-all", j["signed_in"] is False)
c, _, _ = call("GET", "/v1/account", headers={"Authorization": "Bearer " + oldkey}); check("key survives sign-out", c == 200)

# ---- audit + no secrets stored in clear
rows = db.execute("SELECT event FROM auth_audit").fetchall(); ev = {r[0] for r in rows}
check("audit events", {"signin", "claim", "identity_linked", "account_deleted", "signout_all", "export"} <= ev)
dump = "\n".join(str(r) for r in db.execute("SELECT * FROM sessions UNION ALL SELECT id,user_id,code_hash,target_hash,purpose,consumed,0,0 FROM login_codes"))
check("no raw sid stored", sid not in dump and csid not in dump)

# ---- switch OFF: routes 404, cookies ignored
import importlib
svc = None
for o in __import__("gc").get_objects():
    if isinstance(o, auth_mod.AuthService): svc = o
svc.enabled = False
c, _, j = call("GET", "/v1/auth/config", headers=O); check("off: config says disabled", j["enabled"] is False and not j["providers"]["email"])
c, _, _ = call("POST", "/v1/auth/email/start", {"email": "x@example.com"}, O); check("off: routes 404", c == 404)
c, h, _ = call("GET", "/healthz", headers=O); check("off: CORS back to *", hget(h, "Access-Control-Allow-Origin") == ["*"])
print(f"{P} pass, {F} fail"); sys.exit(1 if F else 0)
