#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_auth — account login for TokenCenter (email code, GitHub, Google).

Design (see PLAN.md):
  * One user per existing account (accounts.account_hash). Balance, plan and keys
    stay on accounts/keys. Stripe paths are untouched.
  * Identities: (provider, subject) unique. Providers: email, github, google; phone
    is reserved in the CHECK list so it can be added later without a migration.
  * Sessions: random id in an HttpOnly, Secure, SameSite=Lax cookie for .tokenctr.com;
    only an HMAC of the id is stored. 30-day sliding, 90-day absolute expiry.
  * CSRF: Origin must be an allowed site origin on every cookie-authenticated or
    auth POST, plus an X-TC-CSRF header (HMAC of the session id) for signed-in POSTs.
  * Matching emails NEVER auto-link. Linking needs a signed-in user + verified email.
  * Feature switch: config.json {"auth": {"enabled": false}} (default OFF).
  * API-key Bearer auth for /v1 is unchanged; Bearer always wins over a cookie.
No secret is ever logged or returned. Stdlib only.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets as _secrets
import smtplib
import ssl
import time
import uuid
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from typing import Any, Dict, List, Optional, Tuple
from urllib import parse as _up
from urllib import request as _ur

UTC = timezone.utc
SESSION_COOKIE = "__Secure-tc_session"
OAUTH_COOKIE = "__Secure-tc_oauth"
SESSION_IDLE = 30 * 86400
SESSION_ABS = 90 * 86400
CODE_TTL = 600
CODE_ATTEMPTS = 5
PROVIDERS = ("email", "github", "google")  # "phone" reserved for later
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[A-Za-z0-9.-]{1,253}\.[A-Za-z]{2,63}$")

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS users (
         id TEXT PRIMARY KEY, account_hash TEXT UNIQUE NOT NULL, display_name TEXT,
         created_at TEXT NOT NULL, deleted_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS identities (
         id TEXT PRIMARY KEY, user_id TEXT NOT NULL,
         provider TEXT NOT NULL CHECK (provider IN ('email','phone','github','google')),
         subject TEXT NOT NULL, email TEXT, email_verified INTEGER NOT NULL DEFAULT 0,
         display TEXT, created_at TEXT NOT NULL, last_used_at TEXT,
         UNIQUE (provider, subject))""",
    "CREATE INDEX IF NOT EXISTS identities_user ON identities(user_id)",
    """CREATE TABLE IF NOT EXISTS sessions (
         id_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL, created_at REAL NOT NULL,
         expires_at REAL NOT NULL, last_seen_at REAL NOT NULL, ip_hash TEXT, ua_short TEXT,
         revoked INTEGER NOT NULL DEFAULT 0)""",
    "CREATE INDEX IF NOT EXISTS sessions_user ON sessions(user_id)",
    """CREATE TABLE IF NOT EXISTS login_codes (
         id TEXT PRIMARY KEY, channel TEXT NOT NULL, target_hash TEXT NOT NULL, code_hash TEXT NOT NULL,
         purpose TEXT NOT NULL, user_id TEXT, created_at REAL NOT NULL, expires_at REAL NOT NULL,
         attempts INTEGER NOT NULL DEFAULT 0, consumed INTEGER NOT NULL DEFAULT 0)""",
    "CREATE INDEX IF NOT EXISTS login_codes_target ON login_codes(target_hash)",
    """CREATE TABLE IF NOT EXISTS oauth_states (
         state_hash TEXT PRIMARY KEY, provider TEXT NOT NULL, verifier TEXT NOT NULL, nonce TEXT,
         return_to TEXT, link_user_id TEXT, expires_at REAL NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS auth_audit (
         id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, user_id TEXT, event TEXT NOT NULL,
         provider TEXT, ip_hash TEXT, detail TEXT)""",
    """CREATE TABLE IF NOT EXISTS auth_ratelimit (
         bucket TEXT NOT NULL, win INTEGER NOT NULL, n INTEGER NOT NULL DEFAULT 0,
         PRIMARY KEY (bucket, win))""",
]


class SessionKey(str):
    """Internal marker: a request authenticated by session cookie. Never built from
    client input, so no header value can impersonate it."""
    account_hash: str = ""
    user_id: str = ""
    key_ref: Optional[str] = None


def _now() -> float:
    return time.time()


def _iso(t: Optional[float] = None) -> str:
    return datetime.fromtimestamp(t if t is not None else _now(), UTC).isoformat()


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def norm_email(e: Any) -> Optional[str]:
    if not isinstance(e, str):
        return None
    e = e.strip().lower()
    return e if len(e) <= 254 and EMAIL_RE.match(e) else None


class Mailer:
    """backend "smtp" (authenticated submission) or "file" (writes .eml to a dir; tests/dry runs)."""

    def __init__(self, cfg: Dict[str, Any], secrets: Dict[str, Any]):
        self.backend = cfg.get("mail_backend", "smtp")
        self.sender = cfg.get("mail_from", "noreply@tokenctr.com")
        self.sender_name = cfg.get("mail_from_name", "TokenCenter")
        self.host = secrets.get("smtp_host") or cfg.get("smtp_host", "localhost")
        self.port = int(secrets.get("smtp_port") or cfg.get("smtp_port", 465))
        self.user = secrets.get("smtp_user", "")
        self._pw = secrets.get("smtp_password", "")
        self.outdir = cfg.get("mail_outbox", "")

    def configured(self) -> bool:
        return self.backend == "file" or bool(self.user and self._pw)

    def send(self, to: str, subject: str, text: str) -> bool:
        m = EmailMessage()
        m["From"] = formataddr((self.sender_name, self.sender))
        m["To"] = to
        m["Subject"] = subject
        m["Message-ID"] = make_msgid(domain=self.sender.split("@")[-1])
        m.set_content(text)
        try:
            if self.backend == "file":
                os.makedirs(self.outdir, exist_ok=True)
                with open(os.path.join(self.outdir, f"{int(_now()*1000)}_{uuid.uuid4().hex[:6]}.eml"), "wb") as f:
                    f.write(bytes(m))
                return True
            ctx = ssl.create_default_context()
            if self.port == 465:
                with smtplib.SMTP_SSL(self.host, self.port, context=ctx, timeout=20) as s:
                    s.login(self.user, self._pw)
                    s.send_message(m)
            else:
                with smtplib.SMTP(self.host, self.port, timeout=20) as s:
                    s.starttls(context=ctx)
                    s.login(self.user, self._pw)
                    s.send_message(m)
            return True
        except Exception as e:  # never include credentials
            import sys
            sys.stderr.write(f"auth mail send failed: {type(e).__name__}\n")
            return False


def _http_json(url: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
               timeout: int = 15) -> Dict[str, Any]:
    body = _up.urlencode(data).encode() if data is not None else None
    req = _ur.Request(url, data=body, headers={"Accept": "application/json",
                                               "User-Agent": "TokenCenter-Auth/1.0", **(headers or {})})
    with _ur.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as r:  # TLS verify ON
        return json.loads(r.read().decode("utf-8") or "{}")


class OAuthProvider:
    def __init__(self, name: str, client_id: str, client_secret: str):
        self.name, self.client_id, self._secret = name, client_id, client_secret

    @property
    def configured(self) -> bool:
        return bool(self.client_id and self._secret)

    def authorize_url(self, redirect_uri: str, state: str, challenge: str, nonce: str) -> str:
        if self.name == "github":
            q = {"client_id": self.client_id, "redirect_uri": redirect_uri, "scope": "read:user user:email",
                 "state": state, "code_challenge": challenge, "code_challenge_method": "S256",
                 "allow_signup": "true"}
            return "https://github.com/login/oauth/authorize?" + _up.urlencode(q)
        q = {"client_id": self.client_id, "redirect_uri": redirect_uri, "response_type": "code",
             "scope": "openid email profile", "state": state, "code_challenge": challenge,
             "code_challenge_method": "S256", "nonce": nonce, "prompt": "select_account"}
        return "https://accounts.google.com/o/oauth2/v2/auth?" + _up.urlencode(q)

    def fetch_identity(self, code: str, verifier: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange code (PKCE) and return {subject, email, email_verified, display}."""
        if self.name == "github":
            tok = _http_json("https://github.com/login/oauth/access_token", {
                "client_id": self.client_id, "client_secret": self._secret, "code": code,
                "redirect_uri": redirect_uri, "code_verifier": verifier})
            at = tok.get("access_token")
            if not at:
                raise ValueError("token_exchange_failed")
            h = {"Authorization": "Bearer " + at, "Accept": "application/vnd.github+json"}
            u = _http_json("https://api.github.com/user", headers=h)
            emails = _http_json_list("https://api.github.com/user/emails", h)
            prim = next((e for e in emails if e.get("primary") and e.get("verified")), None) \
                or next((e for e in emails if e.get("verified")), None)
            return {"subject": str(u["id"]), "email": norm_email(prim["email"]) if prim else None,
                    "email_verified": bool(prim), "display": u.get("login") or ""}
        tok = _http_json("https://oauth2.googleapis.com/token", {
            "client_id": self.client_id, "client_secret": self._secret, "code": code,
            "redirect_uri": redirect_uri, "grant_type": "authorization_code", "code_verifier": verifier})
        at = tok.get("access_token")
        if not at:
            raise ValueError("token_exchange_failed")
        u = _http_json("https://openidconnect.googleapis.com/v1/userinfo",
                       headers={"Authorization": "Bearer " + at})
        return {"subject": str(u["sub"]), "email": norm_email(u.get("email")),
                "email_verified": bool(u.get("email_verified")), "display": u.get("name") or ""}


def _http_json_list(url: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    req = _ur.Request(url, headers={"User-Agent": "TokenCenter-Auth/1.0", **headers})
    with _ur.urlopen(req, timeout=15, context=ssl.create_default_context()) as r:
        d = json.loads(r.read().decode("utf-8") or "[]")
    return d if isinstance(d, list) else []


class AuthService:
    def __init__(self, store: Any, meter: Any, config: Dict[str, Any], secrets: Dict[str, Any]):
        self.store, self.meter = store, meter
        self.cfg = dict(config.get("auth") or {})
        self.enabled = bool(self.cfg.get("enabled", False))
        self.site = self.cfg.get("site", "https://tokenctr.com").rstrip("/")
        self.api_base = self.cfg.get("api_base", "https://api.tokenctr.com").rstrip("/")
        self.origins = tuple(self.cfg.get("allowed_origins") or ("https://tokenctr.com", "https://www.tokenctr.com"))
        self.cookie_domain = self.cfg.get("cookie_domain", ".tokenctr.com")
        self.limits = {"email_ip": 10, "email_addr": 3, "verify_ip": 30, "claim_ip": 10, "oauth_ip": 30, "email_global": 60,
                       **(self.cfg.get("limits") or {})}
        pep = secrets.get("auth_pepper") or ""
        self._pepper = pep.encode() if pep else hashlib.sha256(
            (secrets.get("mesh_hmac_key_hex", "") + "|tc-auth").encode()).digest()
        self.mailer = Mailer(self.cfg, secrets)
        self.oauth = {
            "github": OAuthProvider("github", secrets.get("github_client_id", ""), secrets.get("github_client_secret", "")),
            "google": OAuthProvider("google", secrets.get("google_client_id", ""), secrets.get("google_client_secret", "")),
        }
        self.turnstile_secret = secrets.get("turnstile_secret_key", "")
        self.turnstile_sitekey = self.cfg.get("turnstile_sitekey", "")
        self.db, self.lock = store.db, store.lock
        with self.lock:
            for s in SCHEMA:
                self.db.execute(s)
            self.db.commit()

    # ------------------------------------------------------------------ helpers
    def h(self, *parts: str) -> str:
        return hmac.new(self._pepper, "|".join(parts).encode(), hashlib.sha256).hexdigest()

    def audit(self, event: str, user_id: Optional[str] = None, provider: Optional[str] = None,
              ip: str = "", detail: Optional[Dict[str, Any]] = None) -> None:
        with self.lock:
            self.db.execute("INSERT INTO auth_audit (ts,user_id,event,provider,ip_hash,detail) VALUES (?,?,?,?,?,?)",
                            (_iso(), user_id, event, provider, self.h("ip", ip)[:16] if ip else None,
                             json.dumps(detail or {})[:500]))
            self.db.commit()

    def hit(self, bucket: str, limit: int, window: int) -> bool:
        """True if allowed. Fixed window counter in SQLite."""
        w = int(_now() // window) * window  # window start (epoch seconds)
        b = self.h("rl", bucket, str(window))[:32]
        with self.lock:
            self.db.execute("INSERT INTO auth_ratelimit (bucket,win,n) VALUES (?,?,1) "
                            "ON CONFLICT(bucket,win) DO UPDATE SET n=n+1", (b, w))
            n = self.db.execute("SELECT n FROM auth_ratelimit WHERE bucket=? AND win=?", (b, w)).fetchone()[0]
            if _secrets.randbelow(50) == 0:
                self.db.execute("DELETE FROM auth_ratelimit WHERE win < ?", (int(_now()) - 2 * 86400,))
            self.db.commit()
        return n <= limit

    def origin_ok(self, origin: Optional[str]) -> bool:
        return bool(origin) and origin in self.origins

    def csrf_for(self, sid: str) -> str:
        return self.h("csrf", sid)[:40]

    # ------------------------------------------------------------------ users / identities
    def user_by_id(self, uid: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            r = self.db.execute("SELECT id,account_hash,display_name,created_at FROM users WHERE id=? AND deleted_at IS NULL",
                                (uid,)).fetchone()
        return {"id": r[0], "account_hash": r[1], "display_name": r[2], "created_at": r[3]} if r else None

    def user_for_account(self, account_hash: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            r = self.db.execute("SELECT id FROM users WHERE account_hash=? AND deleted_at IS NULL", (account_hash,)).fetchone()
        return self.user_by_id(r[0]) if r else None

    def identities(self, uid: str) -> List[Dict[str, Any]]:
        with self.lock:
            rows = self.db.execute("SELECT id,provider,subject,email,email_verified,display,created_at,last_used_at "
                                   "FROM identities WHERE user_id=? ORDER BY created_at", (uid,)).fetchall()
        return [{"id": r[0], "provider": r[1], "email": r[3], "email_verified": bool(r[4]),
                 "display": r[5] or (r[3] or ""), "created_at": r[6], "last_used_at": r[7],
                 "_subject": r[2]} for r in rows]

    def identity(self, provider: str, subject: str) -> Optional[Tuple[str, str]]:
        with self.lock:
            r = self.db.execute("SELECT id,user_id FROM identities WHERE provider=? AND subject=?",
                                (provider, subject)).fetchone()
        return (r[0], r[1]) if r else None

    def email_owner(self, email: str) -> Optional[str]:
        """user_id of any identity carrying this verified email (any provider)."""
        with self.lock:
            r = self.db.execute("SELECT user_id FROM identities WHERE email=? AND email_verified=1 LIMIT 1",
                                (email,)).fetchone()
        return r[0] if r else None

    def add_identity(self, uid: str, provider: str, subject: str, email: Optional[str], verified: bool,
                     display: str = "") -> str:
        iid = uuid.uuid4().hex
        with self.lock:
            self.db.execute("INSERT INTO identities (id,user_id,provider,subject,email,email_verified,display,created_at,last_used_at) "
                            "VALUES (?,?,?,?,?,?,?,?,?)",
                            (iid, uid, provider, subject, email, 1 if verified else 0, display[:80], _iso(), _iso()))
            self.db.commit()
        return iid

    def touch_identity(self, iid: str) -> None:
        with self.lock:
            self.db.execute("UPDATE identities SET last_used_at=? WHERE id=?", (_iso(), iid))
            self.db.commit()

    def create_user(self, account_hash: Optional[str] = None, display: str = "") -> Dict[str, Any]:
        """New user. Without account_hash, a fresh $0 free account is created (no key minted)."""
        now = _iso()
        with self.lock:
            if not account_hash:
                import cosmos_pay_meter as meter_mod
                account_hash = meter_mod.hash_account(uuid.uuid4().hex)
                self.db.execute("INSERT INTO accounts (account_hash, plan, credits_face_usd, created_at) VALUES (?,?,?,?)",
                                (account_hash, "free", 0.0, now))
            uid = "u_" + uuid.uuid4().hex
            self.db.execute("INSERT INTO users (id,account_hash,display_name,created_at) VALUES (?,?,?,?)",
                            (uid, account_hash, display[:80], now))
            self.db.commit()
        return self.user_by_id(uid)  # type: ignore[return-value]

    # ------------------------------------------------------------------ sessions
    def new_session(self, uid: str, ip: str, ua: str) -> str:
        sid = _secrets.token_urlsafe(32)
        t = _now()
        with self.lock:
            self.db.execute("INSERT INTO sessions (id_hash,user_id,created_at,expires_at,last_seen_at,ip_hash,ua_short) "
                            "VALUES (?,?,?,?,?,?,?)",
                            (self.h("sid", sid), uid, t, t + SESSION_IDLE, t, self.h("ip", ip)[:16], _ua_short(ua)))
            self.db.commit()
        return sid

    def session(self, sid: Optional[str]) -> Optional[Dict[str, Any]]:
        if not sid or len(sid) > 100:
            return None
        hsid = self.h("sid", sid)
        t = _now()
        with self.lock:
            r = self.db.execute("SELECT user_id,created_at,expires_at,last_seen_at FROM sessions "
                                "WHERE id_hash=? AND revoked=0", (hsid,)).fetchone()
            if not r or r[2] < t or r[1] + SESSION_ABS < t:
                return None
            if t - r[3] > 3600:  # sliding expiry, written at most hourly
                self.db.execute("UPDATE sessions SET last_seen_at=?, expires_at=? WHERE id_hash=?",
                                (t, min(t + SESSION_IDLE, r[1] + SESSION_ABS), hsid))
                self.db.commit()
        u = self.user_by_id(r[0])
        if not u:
            return None
        return {"sid": sid, "id_hash": hsid, "user": u}

    def revoke_sessions(self, uid: str, only_hash: Optional[str] = None, except_hash: Optional[str] = None) -> int:
        with self.lock:
            if only_hash:
                cur = self.db.execute("UPDATE sessions SET revoked=1 WHERE user_id=? AND id_hash LIKE ? AND revoked=0",
                                      (uid, only_hash + "%"))
            elif except_hash:
                cur = self.db.execute("UPDATE sessions SET revoked=1 WHERE user_id=? AND id_hash<>? AND revoked=0",
                                      (uid, except_hash))
            else:
                cur = self.db.execute("UPDATE sessions SET revoked=1 WHERE user_id=? AND revoked=0", (uid,))
            self.db.commit()
            return cur.rowcount

    def sessions_list(self, uid: str, current_hash: str) -> List[Dict[str, Any]]:
        t = _now()
        with self.lock:
            rows = self.db.execute("SELECT id_hash,created_at,last_seen_at,expires_at,ua_short FROM sessions "
                                   "WHERE user_id=? AND revoked=0 AND expires_at>? ORDER BY last_seen_at DESC",
                                   (uid, t)).fetchall()
        return [{"id": r[0][:16], "created_at": _iso(r[1]), "last_seen_at": _iso(r[2]),
                 "expires_at": _iso(r[3]), "device": r[4] or "", "current": r[0] == current_hash} for r in rows]

    # ------------------------------------------------------------------ request-side auth (existing routes)
    def session_key_for(self, headers: Any, method: str) -> Optional[SessionKey]:
        """Cookie auth for existing /v1 routes, only when enabled, Origin is the site, and
        (for writes) the CSRF header matches."""
        if not self.enabled:
            return None
        if not self.origin_ok(headers.get("Origin")):
            return None
        s = self.session(read_cookie(headers.get("Cookie", ""), SESSION_COOKIE))
        if not s:
            return None
        if method != "GET" and not hmac.compare_digest(headers.get("X-TC-CSRF", ""), self.csrf_for(s["sid"])):
            return None
        k = SessionKey("sess:" + s["user"]["id"])
        k.account_hash = s["user"]["account_hash"]
        k.user_id = s["user"]["id"]
        ref = headers.get("X-TC-Key", "")
        k.key_ref = ref.strip()[:80] or None
        return k

    def wrap_account_for_key(self, orig):
        store = self.store

        def account_for_key(key):
            if isinstance(key, SessionKey):
                with store.lock:
                    r = store.db.execute("SELECT account_hash, plan, credits_face_usd FROM accounts WHERE account_hash=?",
                                         (key.account_hash,)).fetchone()
                if not r:
                    return None
                acct = {"account_hash": r[0], "plan": r[1], "credits_face_usd": r[2],
                        "daily_cap_usd": None, "key_hash": None, "via": "session"}
                if key.key_ref:  # dashboard chose one of the account's keys (caps + per-key usage apply)
                    kh = store.resolve_key(key.key_ref, r[0])
                    if not kh:
                        return None
                    with store.lock:
                        k = store.db.execute("SELECT daily_cap_usd, revoked FROM keys WHERE key_hash=?", (kh,)).fetchone()
                    if not k or k[1]:
                        return None
                    acct["daily_cap_usd"], acct["key_hash"] = k[0], kh
                return acct
            return orig(key)
        return account_for_key


def read_cookie(header: str, name: str) -> Optional[str]:
    for part in (header or "").split(";"):
        k, _, v = part.strip().partition("=")
        if k == name:
            return v
    return None


def _ua_short(ua: str) -> str:
    ua = ua or ""
    b = next((n for n in ("Edg", "OPR", "Firefox", "Chrome", "Safari") if n in ua), "Browser")
    b = {"Edg": "Edge", "OPR": "Opera"}.get(b, b)
    o = next((n for n in ("Windows", "Android", "iPhone", "iPad", "Mac OS", "Linux") if n in ua), "")
    return (b + (" on " + o.replace("Mac OS", "macOS") if o else ""))[:40]


# ====================================================================== HTTP routes
class AuthRoutes:
    """Mounted under /v1/auth/*. `hd` is the BaseHTTPRequestHandler instance."""

    def __init__(self, svc: AuthService):
        self.s = svc

    # -------------------------------------------------- response helpers
    def _cors(self, hd: Any) -> List[Tuple[str, str]]:
        o = hd.headers.get("Origin")
        if self.s.origin_ok(o):
            return [("Access-Control-Allow-Origin", o), ("Access-Control-Allow-Credentials", "true"), ("Vary", "Origin")]
        return [("Vary", "Origin")]

    def send(self, hd: Any, code: int, obj: Any, cookies: Optional[List[str]] = None,
             extra: Optional[List[Tuple[str, str]]] = None) -> None:
        payload = json.dumps(obj).encode("utf-8")
        hd.send_response(code)
        hd.send_header("Content-Type", "application/json")
        hd.send_header("Content-Length", str(len(payload)))
        hd.send_header("Cache-Control", "no-store")
        for k, v in self._cors(hd) + (extra or []):
            hd.send_header(k, v)
        for c in cookies or []:
            hd.send_header("Set-Cookie", c)
        hd.end_headers()
        hd.wfile.write(payload)

    def redirect(self, hd: Any, url: str, cookies: Optional[List[str]] = None) -> None:
        hd.send_response(302)
        hd.send_header("Location", url)
        hd.send_header("Cache-Control", "no-store")
        hd.send_header("Content-Length", "0")
        for c in cookies or []:
            hd.send_header("Set-Cookie", c)
        hd.end_headers()

    def err(self, hd: Any, code: int, ecode: str, msg: str = "") -> None:
        self.send(hd, code, {"error": {"code": ecode, "message": msg or ecode.replace("_", " ")}})

    def session_cookie(self, sid: str) -> str:
        return (f"{SESSION_COOKIE}={sid}; Domain={self.s.cookie_domain}; Path=/; Max-Age={SESSION_ABS}; "
                "Secure; HttpOnly; SameSite=Lax")

    def clear_cookie(self) -> str:
        return f"{SESSION_COOKIE}=; Domain={self.s.cookie_domain}; Path=/; Max-Age=0; Secure; HttpOnly; SameSite=Lax"

    # Non-secret hint so static pages can show signed-in state without calling the API on every view.
    def hint_cookie(self, on: bool) -> str:
        return (f"tc_signed_in={'1' if on else ''}; Domain={self.s.cookie_domain}; Path=/; "
                f"Max-Age={SESSION_ABS if on else 0}; Secure; SameSite=Lax")

    def preflight(self, hd: Any) -> None:
        hd.send_response(204)
        for k, v in self._cors(hd):
            hd.send_header(k, v)
        hd.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        hd.send_header("Access-Control-Allow-Headers", "Content-Type, X-TC-CSRF, CF-Turnstile-Token")
        hd.send_header("Access-Control-Max-Age", "600")
        hd.send_header("Content-Length", "0")
        hd.end_headers()

    # -------------------------------------------------- dispatch
    def handle(self, hd: Any, method: str, path: str, query: Dict[str, List[str]], body: Dict[str, Any],
               ip: str) -> None:
        s = self.s
        if method == "OPTIONS":
            return self.preflight(hd)
        if path == "/v1/auth/config":
            return self.send(hd, 200, self.public_config())
        if not s.enabled:
            return self.err(hd, 404, "auth_disabled", "account login is not enabled yet")
        sess = s.session(read_cookie(hd.headers.get("Cookie", ""), SESSION_COOKIE))
        if method == "GET":
            m = re.match(r"^/v1/auth/(github|google)/(start|callback)$", path)
            if m:
                return self.oauth_start(hd, m.group(1), query, sess, ip) if m.group(2) == "start" \
                    else self.oauth_callback(hd, m.group(1), query, ip)
            if not s.origin_ok(hd.headers.get("Origin")):
                return self.err(hd, 403, "bad_origin")
            if path == "/v1/auth/session":
                return self.session_info(hd, sess)
            if not sess:
                return self.err(hd, 401, "not_signed_in")
            if path == "/v1/auth/sessions":
                return self.send(hd, 200, {"data": s.sessions_list(sess["user"]["id"], sess["id_hash"])})
            if path == "/v1/auth/identities":
                return self.send(hd, 200, {"data": self._ids(sess["user"]["id"])})
            if path == "/v1/auth/export":
                return self.export(hd, sess, ip)
            return self.err(hd, 404, "not_found")
        # ---- POST: Origin check on every auth POST (login-CSRF + CSRF)
        if method != "POST":
            return self.err(hd, 405, "method_not_allowed")
        if not s.origin_ok(hd.headers.get("Origin")):
            return self.err(hd, 403, "bad_origin")
        if path == "/v1/auth/email/start":
            return self.email_start(hd, body, sess, ip)
        if path == "/v1/auth/email/verify":
            return self.email_verify(hd, body, sess, ip)
        if path == "/v1/auth/claim":
            return self.claim(hd, body, sess, ip)
        if path == "/v1/auth/signout":
            if sess:
                s.revoke_sessions(sess["user"]["id"], only_hash=sess["id_hash"])
                s.audit("signout", sess["user"]["id"], ip=ip)
            return self.send(hd, 200, {"ok": True}, cookies=[self.clear_cookie(), self.hint_cookie(False)])
        if not sess:
            return self.err(hd, 401, "not_signed_in")
        if not hmac.compare_digest(hd.headers.get("X-TC-CSRF", ""), s.csrf_for(sess["sid"])):
            return self.err(hd, 403, "bad_csrf")
        uid = sess["user"]["id"]
        if path == "/v1/auth/signout-all":
            n = s.revoke_sessions(uid)
            s.audit("signout_all", uid, ip=ip, detail={"n": n})
            return self.send(hd, 200, {"ok": True, "revoked": n}, cookies=[self.clear_cookie(), self.hint_cookie(False)])
        if path == "/v1/auth/sessions/revoke":
            ref = str(body.get("id", ""))
            if len(ref) < 16 or not re.fullmatch(r"[0-9a-f]+", ref):
                return self.err(hd, 400, "bad_session_id")
            n = s.revoke_sessions(uid, only_hash=ref)
            s.audit("session_revoke", uid, ip=ip)
            return self.send(hd, 200, {"ok": True, "revoked": n})
        if path == "/v1/auth/identities/unlink":
            return self.unlink(hd, uid, str(body.get("id", "")), ip)
        if path == "/v1/auth/delete":
            return self.delete(hd, sess, body, ip)
        return self.err(hd, 404, "not_found")

    # -------------------------------------------------- pieces
    def public_config(self) -> Dict[str, Any]:
        s = self.s
        return {"enabled": s.enabled,
                "providers": {"email": s.enabled and s.mailer.configured(),
                              "github": s.enabled and s.oauth["github"].configured,
                              "google": s.enabled and s.oauth["google"].configured,
                              "phone": False},
                "turnstile_sitekey": s.turnstile_sitekey if s.turnstile_secret else ""}

    def _ids(self, uid: str) -> List[Dict[str, Any]]:
        return [{k: v for k, v in i.items() if not k.startswith("_")} for i in self.s.identities(uid)]

    def session_info(self, hd: Any, sess: Optional[Dict[str, Any]]) -> None:
        if not sess:
            return self.send(hd, 200, {"signed_in": False})
        u = sess["user"]
        st = self.s.store
        with st.lock:
            a = st.db.execute("SELECT plan, credits_face_usd FROM accounts WHERE account_hash=?",
                              (u["account_hash"],)).fetchone()
        ids = self._ids(u["id"])
        email = next((i["email"] for i in ids if i["email"]), None)
        self.send(hd, 200, {
            "signed_in": True, "csrf": self.s.csrf_for(sess["sid"]),
            "user": {"id": u["id"], "display": u["display_name"] or email or "", "email": email,
                     "created_at": u["created_at"]},
            "account": {"account": u["account_hash"], "plan": a[0] if a else "free",
                        "credits_face_usd": st.credits(u["account_hash"]) if a else 0.0},
            "identities": ids, "needs_method": not ids})

    def _turnstile_ok(self, hd: Any, body: Dict[str, Any], ip: str) -> bool:
        if not self.s.turnstile_secret:
            return True  # not configured: rely on rate limits
        tok = hd.headers.get("CF-Turnstile-Token") or body.get("turnstile_token") or ""
        try:
            d = _http_json("https://challenges.cloudflare.com/turnstile/v0/siteverify",
                           {"secret": self.s.turnstile_secret, "response": tok, "remoteip": ip})
            return bool(d.get("success"))
        except Exception:
            return False

    def email_start(self, hd: Any, body: Dict[str, Any], sess: Optional[Dict[str, Any]], ip: str) -> None:
        s = self.s
        email = norm_email(body.get("email"))
        if not email:
            return self.err(hd, 400, "bad_email", "enter a valid email address")
        if not s.hit("email_ip:" + ip, s.limits["email_ip"], 3600):
            return self.err(hd, 429, "rate_limited", "too many requests; try again later")
        if not self._turnstile_ok(hd, body, ip):
            return self.err(hd, 403, "turnstile_failed")
        link = bool(body.get("link")) and sess is not None
        generic = {"ok": True, "message": "If that address can sign in, a code is on its way. It expires in 10 minutes."}
        # Per-address limit is silent (same response) to avoid enumeration and mail bombing.
        if not s.hit("email_addr:" + email, s.limits["email_addr"], 900):
            s.audit("email_code_throttled", provider="email", ip=ip)
            return self.send(hd, 200, generic)
        # Whole cPanel account is capped at 250 mails/hour (shared with other sites): keep login mail well under.
        if not s.hit("email_global", s.limits["email_global"], 3600):
            s.audit("email_global_cap", provider="email", ip=ip)
            return self.err(hd, 429, "rate_limited", "sign-in email is busy right now; try again in a few minutes")
        code = f"{_secrets.randbelow(1000000):06d}"
        cid = uuid.uuid4().hex
        t = _now()
        with s.lock:
            s.db.execute("INSERT INTO login_codes (id,channel,target_hash,code_hash,purpose,user_id,created_at,expires_at) "
                         "VALUES (?,?,?,?,?,?,?,?)",
                         (cid, "email", s.h("email", email), s.h("code", cid, code), "link" if link else "login",
                          sess["user"]["id"] if link else None, t, t + CODE_TTL))
            s.db.commit()
        text = (f"Your TokenCenter sign-in code is {code}\n\nIt expires in 10 minutes. If you didn't ask for it, "
                "ignore this email; nobody can sign in without the code.\n\n"
                f"Or open this link on the same device: {s.site}/signin.html#email={_up.quote(email)}&code={code}\n\n"
                "TokenCenter by SolaroLabs - https://tokenctr.com\n")
        ok = s.mailer.send(email, f"{code} is your TokenCenter sign-in code", text)
        s.audit("email_code_sent" if ok else "email_code_send_failed", sess["user"]["id"] if link else None,
                "email", ip)
        return self.send(hd, 200, generic)

    def email_verify(self, hd: Any, body: Dict[str, Any], sess: Optional[Dict[str, Any]], ip: str) -> None:
        s = self.s
        email = norm_email(body.get("email"))
        code = str(body.get("code", "")).strip()
        if not email or not re.fullmatch(r"\d{6}", code):
            return self.err(hd, 400, "bad_code", "that code is not valid or has expired")
        if not s.hit("verify_ip:" + ip, s.limits["verify_ip"], 3600):
            return self.err(hd, 429, "rate_limited", "too many attempts; try again later")
        t = _now()
        with s.lock:
            row = s.db.execute("SELECT id,code_hash,purpose,user_id,attempts FROM login_codes WHERE target_hash=? "
                               "AND consumed=0 AND expires_at>? ORDER BY created_at DESC LIMIT 1",
                               (s.h("email", email), t)).fetchone()
            if not row or row[4] >= CODE_ATTEMPTS:
                return self.err(hd, 400, "bad_code", "that code is not valid or has expired")
            s.db.execute("UPDATE login_codes SET attempts=attempts+1 WHERE id=?", (row[0],))
            good = hmac.compare_digest(row[1], s.h("code", row[0], code))
            if good:
                s.db.execute("UPDATE login_codes SET consumed=1 WHERE id=?", (row[0],))
            s.db.commit()
        if not good:
            s.audit("email_code_bad", provider="email", ip=ip)
            return self.err(hd, 400, "bad_code", "that code is not valid or has expired")
        existing = s.identity("email", email)
        if row[2] == "link":
            uid = row[3]
            if not sess or sess["user"]["id"] != uid:
                return self.err(hd, 401, "not_signed_in")
            if existing:
                if existing[1] != uid:
                    return self.err(hd, 409, "identity_in_use", "that email already signs in to a different account")
                return self.send(hd, 200, {"ok": True, "linked": "email"})
            s.add_identity(uid, "email", email, email, True, email)
            s.audit("identity_linked", uid, "email", ip)
            return self.send(hd, 200, {"ok": True, "linked": "email"})
        if existing:
            iid, uid = existing
            s.touch_identity(iid)
            created = False
        else:
            other = s.email_owner(email)
            if other:  # same verified email on a Google/GitHub identity: never auto-link
                return self.err(hd, 409, "email_in_use_other_method",
                                "this email belongs to an account that signs in another way; sign in with that "
                                "method, then add email under Sign-in methods")
            u = s.create_user(display=email)
            uid = u["id"]
            s.add_identity(uid, "email", email, email, True, email)
            created = True
        sid = s.new_session(uid, ip, hd.headers.get("User-Agent", ""))
        s.audit("signin", uid, "email", ip, {"new_user": created})
        return self.send(hd, 200, {"ok": True, "new_user": created, "csrf": s.csrf_for(sid)},
                         cookies=[self.session_cookie(sid), self.hint_cookie(True)])

    def claim(self, hd: Any, body: Dict[str, Any], sess: Optional[Dict[str, Any]], ip: str) -> None:
        """Paste an existing ck_ key once to attach a login to that account."""
        s = self.s
        if not s.hit("claim_ip:" + ip, s.limits["claim_ip"], 3600):
            return self.err(hd, 429, "rate_limited", "too many attempts; try again later")
        key = str(body.get("key", "")).strip()
        acct = s.store.account_for_key(key) if key.startswith("ck_") and len(key) < 100 else None
        if not acct:
            s.audit("claim_failed", ip=ip)
            return self.err(hd, 400, "claim_failed", "that key can't be used to claim an account")
        owner = s.user_for_account(acct["account_hash"])
        if owner and s.identities(owner["id"]):
            # Account already has a login: the key alone never signs in (prevents takeover by a leaked key).
            s.audit("claim_refused_has_login", owner["id"], ip=ip)
            return self.err(hd, 409, "already_claimed",
                            "this account already has a sign-in method; sign in with it instead")
        if sess and sess["user"]["account_hash"] != acct["account_hash"]:
            return self.err(hd, 409, "signed_in_elsewhere", "sign out first, then claim this account")
        u = owner or s.create_user(account_hash=acct["account_hash"])
        sid = s.new_session(u["id"], ip, hd.headers.get("User-Agent", ""))
        s.audit("claim", u["id"], ip=ip)
        return self.send(hd, 200, {"ok": True, "needs_method": True, "csrf": s.csrf_for(sid)},
                         cookies=[self.session_cookie(sid), self.hint_cookie(True)])

    def unlink(self, hd: Any, uid: str, iid: str, ip: str) -> None:
        s = self.s
        ids = s.identities(uid)
        if not any(i["id"] == iid for i in ids):
            return self.err(hd, 404, "not_found")
        if len(ids) <= 1:
            return self.err(hd, 409, "last_method", "add another sign-in method before removing this one")
        with s.lock:
            s.db.execute("DELETE FROM identities WHERE id=? AND user_id=?", (iid, uid))
            s.db.commit()
        s.audit("identity_unlinked", uid, ip=ip)
        return self.send(hd, 200, {"ok": True})

    def export(self, hd: Any, sess: Dict[str, Any], ip: str) -> None:
        s = self.s
        u = sess["user"]
        ah = u["account_hash"]
        st = s.store
        with st.lock:
            a = st.db.execute("SELECT plan, credits_face_usd, created_at FROM accounts WHERE account_hash=?", (ah,)).fetchone()
        with s.lock:
            aud = s.db.execute("SELECT ts,event,provider FROM auth_audit WHERE user_id=? ORDER BY id DESC LIMIT 500",
                               (u["id"],)).fetchall()
        try:
            usage = s.meter.tail(limit=1000, account=ah)
        except Exception:
            usage = []
        s.audit("export", u["id"], ip=ip)
        self.send(hd, 200, {
            "exported_at": _iso(), "user": {k: u[k] for k in ("id", "display_name", "created_at")},
            "sign_in_methods": self._ids(u["id"]),
            "sessions": s.sessions_list(u["id"], sess["id_hash"]),
            "account": {"account": ah, "plan": a[0] if a else None, "credits_face_usd": a[1] if a else None,
                        "created_at": a[2] if a else None},
            "keys": st.keys_for(ah), "usage_events": usage,
            "security_log": [{"ts": r[0], "event": r[1], "provider": r[2]} for r in aud]},
            extra=[("Content-Disposition", 'attachment; filename="tokenctr-account-export.json"')])

    def delete(self, hd: Any, sess: Dict[str, Any], body: Dict[str, Any], ip: str) -> None:
        s = self.s
        u = sess["user"]
        emails = {i["email"] for i in s.identities(u["id"]) if i["email"]}
        typed = norm_email(body.get("confirm_email"))
        if not emails:
            return self.err(hd, 409, "no_email", "add an email sign-in method first so you can confirm deletion")
        if not typed or typed not in emails:
            return self.err(hd, 400, "confirm_mismatch", "type the email on this account to confirm")
        ah = u["account_hash"]
        bal = s.store.credits(ah)
        if bal > 0 and not body.get("acknowledge_balance"):
            return self.err(hd, 409, "balance_remaining",
                            f"this account still has ${bal:.2f} of credit; deleting does not refund it")
        st = s.store
        with st.lock:  # same connection; one transaction
            st.db.execute("UPDATE keys SET revoked=1 WHERE account_hash=?", (ah,))
            st.db.execute("DELETE FROM identities WHERE user_id=?", (u["id"],))
            st.db.execute("UPDATE sessions SET revoked=1 WHERE user_id=?", (u["id"],))
            st.db.execute("UPDATE users SET deleted_at=?, display_name=NULL WHERE id=?", (_iso(), u["id"]))
            st.db.commit()
        s.audit("account_deleted", u["id"], ip=ip, detail={"balance_left_usd": round(bal, 2)})
        return self.send(hd, 200, {"ok": True, "deleted": True}, cookies=[self.clear_cookie(), self.hint_cookie(False)])

    # -------------------------------------------------- OAuth
    def _return_to(self, v: Optional[str]) -> str:
        if v and re.fullmatch(r"/[A-Za-z0-9_./-]{0,80}(\?[A-Za-z0-9=&_-]{0,80})?", v) and not v.startswith("//"):
            return v
        return "/account.html"

    def oauth_start(self, hd: Any, prov: str, q: Dict[str, List[str]], sess: Optional[Dict[str, Any]], ip: str) -> None:
        s = self.s
        p = s.oauth[prov]
        if not p.configured:
            return self.redirect(hd, f"{s.site}/signin.html?error=provider_unavailable")
        if not s.hit("oauth_ip:" + ip, s.limits["oauth_ip"], 3600):
            return self.redirect(hd, f"{s.site}/signin.html?error=rate_limited")
        link = (q.get("link") or [""])[0] == "1"
        if link and not sess:
            return self.redirect(hd, f"{s.site}/signin.html?error=not_signed_in")
        state = _secrets.token_urlsafe(32)
        verifier = _secrets.token_urlsafe(64)
        challenge = _b64(hashlib.sha256(verifier.encode()).digest())
        nonce = _secrets.token_urlsafe(16)
        with s.lock:
            s.db.execute("DELETE FROM oauth_states WHERE expires_at < ?", (_now(),))
            s.db.execute("INSERT INTO oauth_states (state_hash,provider,verifier,nonce,return_to,link_user_id,expires_at) "
                         "VALUES (?,?,?,?,?,?,?)",
                         (s.h("state", state), prov, verifier, nonce,
                          self._return_to((q.get("return_to") or [""])[0]),
                          sess["user"]["id"] if (link and sess) else None, _now() + 600))
            s.db.commit()
        redirect_uri = f"{s.api_base}/v1/auth/{prov}/callback"
        cookie = f"{OAUTH_COOKIE}={state}; Path=/v1/auth/; Max-Age=600; Secure; HttpOnly; SameSite=Lax"
        return self.redirect(hd, p.authorize_url(redirect_uri, state, challenge, nonce), cookies=[cookie])

    def oauth_callback(self, hd: Any, prov: str, q: Dict[str, List[str]], ip: str) -> None:
        s = self.s
        clear = f"{OAUTH_COOKIE}=; Path=/v1/auth/; Max-Age=0; Secure; HttpOnly; SameSite=Lax"
        fail = lambda code: self.redirect(hd, f"{s.site}/signin.html?error={code}", cookies=[clear])  # noqa: E731
        state = (q.get("state") or [""])[0]
        code = (q.get("code") or [""])[0]
        if (q.get("error") or [""])[0]:
            return fail("provider_cancelled")
        ck = read_cookie(hd.headers.get("Cookie", ""), OAUTH_COOKIE) or ""
        if not state or not code or not hmac.compare_digest(ck, state):
            s.audit("oauth_state_mismatch", provider=prov, ip=ip)
            return fail("state_mismatch")
        with s.lock:
            row = s.db.execute("SELECT provider,verifier,return_to,link_user_id,expires_at FROM oauth_states "
                               "WHERE state_hash=?", (s.h("state", state),)).fetchone()
            s.db.execute("DELETE FROM oauth_states WHERE state_hash=?", (s.h("state", state),))  # single use
            s.db.commit()
        if not row or row[0] != prov or row[4] < _now():
            return fail("state_expired")
        try:
            info = s.oauth[prov].fetch_identity(code, row[1], f"{s.api_base}/v1/auth/{prov}/callback")
        except Exception as e:
            import sys
            sys.stderr.write(f"oauth {prov} exchange failed: {type(e).__name__}\n")
            return fail("provider_error")
        existing = s.identity(prov, info["subject"])
        ret = row[2]
        if row[3]:  # link to the signed-in user
            uid = row[3]
            sess = s.session(read_cookie(hd.headers.get("Cookie", ""), SESSION_COOKIE))
            if not sess or sess["user"]["id"] != uid:
                return fail("not_signed_in")
            if existing and existing[1] != uid:
                return self.redirect(hd, f"{s.site}/account.html?auth_error=identity_in_use", cookies=[clear])
            if not existing:
                if not (info.get("email") and info.get("email_verified")):
                    return self.redirect(hd, f"{s.site}/account.html?auth_error=email_not_verified", cookies=[clear])
                s.add_identity(uid, prov, info["subject"], info["email"], True, info.get("display", ""))
                s.audit("identity_linked", uid, prov, ip)
            return self.redirect(hd, f"{s.site}/account.html?linked={prov}", cookies=[clear])
        if existing:
            iid, uid = existing
            s.touch_identity(iid)
            created = False
        else:
            em = info.get("email") if info.get("email_verified") else None
            if em and s.email_owner(em):
                return fail("email_in_use_other_method")
            u = s.create_user(display=info.get("display") or em or "")
            uid = u["id"]
            s.add_identity(uid, prov, info["subject"], em, bool(em), info.get("display", ""))
            created = True
        sid = s.new_session(uid, ip, hd.headers.get("User-Agent", ""))
        s.audit("signin", uid, prov, ip, {"new_user": created})
        sep = "&" if "?" in ret else "?"
        return self.redirect(hd, f"{s.site}{ret}{sep}signed_in={prov}", cookies=[clear, self.session_cookie(sid), self.hint_cookie(True)])
