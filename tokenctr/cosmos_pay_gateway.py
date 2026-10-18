#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_gateway — api.cosmos…/v1: the only public surface.

    POST /v1/chat/completions   auth -> rate-limit -> quota/breaker (fail-closed) ->
                                route -> relay (runsync or SSE stream) -> settle ->
                                meter -> headers
    GET  /v1/models             the supply registry (our prices)
    GET  /v1/usage/today        local meter query (real-time, no delayed dashboard)
    GET  /v1/account            account info, plan, credit balance, keys
    GET  /v1/logs               audit logs and verification receipts
    GET  /v1/logs/{id}          single event receipt lookup
    GET  /v1/statement          monthly usage summary and credit purchases
    GET  /v1/statement/export   CSV export of statement
    GET  /v1/export             audit export (events)
    GET  /v1/export/full        full export: account, keys, settings, meter
    GET  /v1/settings           account settings (autotopup, data, alerts)
    POST /v1/settings/{key}     update account setting
    POST /v1/keys/issue         mint a new mesh API key
    POST /v1/keys/revoke        revoke an API key
    POST /v1/keys/rotate        atomically rotate an API key
    POST /v1/keys/cap           set key-specific daily cap (governance)
    POST /v1/credits/purchase   create checkout session for credit purchase
    POST /v1/founding/purchase  create checkout session for Founding member offer
    POST /v1/webhooks/{proc}    processor webhook receiver (raw body verified first)
    GET  /v1/founding/status    Founding cohort counter (sold/500)
    GET  /v1/cloudflare/status  Cloudflare zone status (X-Setup-Key required)
    GET  /healthz               gateway liveness
    POST /v1/account/anonymous  anonymous key, $0 credit, per-IP daily limit
    OPTIONS *                   CORS preflight for browser portal

Security & Stewardship Rules:
  - Raw body signature verification on webhooks (never re-serialize JSON before verify)
  - No secrets in git, logs, errors, or responses (no-echo rule, cDeck SET-2)
  - Provenance on every number (estimate | measured | billed); estimates never bill
  - The core never gates: local solo work is untouched; grace period on expired entitlements
  - True client IP extracted via Cloudflare edge headers (CF-Connecting-IP)
  - Fail-closed defaults everywhere

Windows-first, stdlib only.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Iterator, List, Optional, Tuple

import cosmos_pay_azure_rail as azure_mod
import cosmos_pay_bedrock_rail as bedrock_mod
import cosmos_pay_config as cfg
import cosmos_pay_founding as founding_mod
import cosmos_pay_meter as meter_mod
import cosmos_pay_openrouter_rail as openrouter_mod
import cosmos_pay_processors as proc_mod
import cosmos_pay_vertex_rail as vtx_mod
import cosmos_pay_webhooks as hooks_mod
from cosmos_pay_runpod_rail import RailError, RunPodRail

cf_mod: Any = None
try:
    import cosmos_pay_cloudflare as cf_mod
except ImportError:
    cf_mod = None

UTC = timezone.utc


def _is_no_supply(exc: BaseException) -> bool:
    """Rails raise this when key or endpoint is missing. It is not a billed failure."""
    return getattr(exc, "no_supply", False) is True


def attach_rails(config: Dict[str, Any], secrets: Dict[str, Any]) -> Dict[str, Any]:
    """Build resale rails from config. Missing fields stay unset so chat returns 503."""
    return {
        "vertex_rail": vtx_mod.from_config(config, secrets),
        "bedrock_rail": bedrock_mod.from_config(config, secrets),
        "openrouter_rail": openrouter_mod.from_config(config, secrets),
        "azure_rail": azure_mod.from_config(config, secrets),
    }


# ----------------------------------------------------------------------------- rate limiting
class RateLimiter:
    """In-memory sliding window rate limiter (requests per minute).
    Tracks separate windows for API keys and client IP addresses."""

    def __init__(self, key_rpm: int = 60, ip_rpm: int = 120):
        self.key_rpm = int(key_rpm)
        self.ip_rpm = int(ip_rpm)
        self.key_history: Dict[str, List[float]] = {}
        self.ip_history: Dict[str, List[float]] = {}
        self.lock = threading.Lock()

    def check_and_record(self, key_or_account: str, ip: str) -> Tuple[bool, str]:
        now = time.time()
        cutoff = now - 60.0
        with self.lock:
            # Periodic prune to bound memory on long-running gateway
            if (len(self.key_history) + len(self.ip_history)) > 10000:
                for _map in (self.key_history, self.ip_history):
                    for k in list(_map.keys()):
                        pruned = [t for t in _map[k] if t > cutoff]
                        if pruned:
                            _map[k] = pruned
                        else:
                            del _map[k]
            # Check key
            if key_or_account:
                hist = self.key_history.get(key_or_account, [])
                hist = [t for t in hist if t > cutoff]
                if len(hist) >= self.key_rpm:
                    self.key_history[key_or_account] = hist
                    return False, "rate_limit_exceeded_key"
                hist.append(now)
                self.key_history[key_or_account] = hist

            # Check IP
            if ip:
                ip_hist = self.ip_history.get(ip, [])
                ip_hist = [t for t in ip_hist if t > cutoff]
                if len(ip_hist) >= self.ip_rpm:
                    self.ip_history[ip] = ip_hist
                    return False, "rate_limit_exceeded_ip"
                ip_hist.append(now)
                self.ip_history[ip] = ip_hist

        return True, ""


# ----------------------------------------------------------------------------- store
class Store:
    """keys.db: mesh keys, accounts, credits, key caps, settings. SQLite, WAL."""

    def __init__(self, path: str):
        self.db = sqlite3.connect(path, check_same_thread=False)
        # RLock: Founding.grant holds this across check+consume+grant+plan,
        # and the inner helpers (_consume_slot, grant) lock again. A plain
        # Lock would deadlock there; RLock keeps the section atomic.
        self.lock = threading.RLock()
        with self.lock:
            self.db.execute("PRAGMA journal_mode=WAL")
            self.db.execute(
                """CREATE TABLE IF NOT EXISTS accounts (
                     account_hash TEXT PRIMARY KEY,
                     plan TEXT NOT NULL DEFAULT 'free',       -- free | founding | verified_free
                     credits_face_usd REAL NOT NULL DEFAULT 0,
                     created_at TEXT NOT NULL
                   )"""
            )
            self.db.execute(
                """CREATE TABLE IF NOT EXISTS keys (
                     key_hash TEXT PRIMARY KEY,
                     account_hash TEXT NOT NULL,
                     label TEXT,
                     created_at TEXT NOT NULL,
                     revoked INTEGER NOT NULL DEFAULT 0,
                     daily_cap_usd REAL DEFAULT NULL
                   )"""
            )
            # Ensure daily_cap_usd exists if keys table was created in earlier revision
            try:
                self.db.execute("ALTER TABLE keys ADD COLUMN daily_cap_usd REAL DEFAULT NULL")
            except sqlite3.OperationalError:
                pass

            self.db.execute(
                """CREATE TABLE IF NOT EXISTS free_daily (
                     account_hash TEXT NOT NULL,
                     day TEXT NOT NULL,                      -- UTC date
                     face_usd REAL NOT NULL DEFAULT 0,
                     PRIMARY KEY (account_hash, day)
                   )"""
            )
            self.db.execute(
                """CREATE TABLE IF NOT EXISTS key_daily (
                     key_hash TEXT NOT NULL,
                     day TEXT NOT NULL,                      -- UTC date
                     face_usd REAL NOT NULL DEFAULT 0,
                     PRIMARY KEY (key_hash, day)
                   )"""
            )
            self.db.execute(
                """CREATE TABLE IF NOT EXISTS settings (
                     account_hash TEXT NOT NULL,
                     key TEXT NOT NULL,
                     value TEXT NOT NULL,
                     updated_at TEXT NOT NULL,
                     PRIMARY KEY (account_hash, key)
                   )"""
            )
            self.db.commit()

    def anon_allow(self, client_ip: str, per_ip_daily: int = 3, global_daily: int = 300) -> Tuple[bool, str]:
        """Persistent per-IP + global daily limit for POST /v1/account/anonymous.
        Survives process restarts (Passenger recycles workers). The IP is stored
        only as a sha256 hash (privacy structural)."""
        day = datetime.now(UTC).strftime("%Y-%m-%d")
        ip_hash = hashlib.sha256(("anon:" + (client_ip or "unknown")).encode("utf-8")).hexdigest()
        with self.lock:
            self.db.execute(
                """CREATE TABLE IF NOT EXISTS anon_issuance (
                     ip_hash TEXT NOT NULL, day TEXT NOT NULL, n INTEGER NOT NULL DEFAULT 0,
                     PRIMARY KEY (ip_hash, day))"""
            )
            total = self.db.execute(
                "SELECT COALESCE(SUM(n), 0) FROM anon_issuance WHERE day = ?", (day,)
            ).fetchone()[0]
            if int(total) >= int(global_daily):
                return False, "anonymous_daily_cap"
            row = self.db.execute(
                "SELECT n FROM anon_issuance WHERE ip_hash = ? AND day = ?", (ip_hash, day)
            ).fetchone()
            if row and int(row[0]) >= int(per_ip_daily):
                return False, "anonymous_ip_limit"
            self.db.execute(
                """INSERT INTO anon_issuance (ip_hash, day, n) VALUES (?,?,1)
                   ON CONFLICT(ip_hash, day) DO UPDATE SET n = n + 1""",
                (ip_hash, day),
            )
            self.db.commit()
        return True, ""

    @staticmethod
    def hash_key(key: str) -> str:
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def account_for_key(self, key: str) -> Optional[Dict[str, Any]]:
        if not key or not isinstance(key, str):
            return None
        kh = self.hash_key(key)
        with self.lock:
            row = self.db.execute(
                """SELECT a.account_hash, a.plan, a.credits_face_usd, k.daily_cap_usd, k.key_hash FROM keys k
                   JOIN accounts a ON a.account_hash = k.account_hash
                   WHERE k.key_hash = ? AND k.revoked = 0""",
                (kh,),
            ).fetchone()
        if not row:
            return None
        return {
            "account_hash": row[0],
            "plan": row[1],
            "credits_face_usd": row[2],
            "daily_cap_usd": row[3],
            "key_hash": row[4],
        }

    def create_account(self, plan: str = "free", credits_face_usd: float = 0.0) -> Tuple[str, str]:
        """Bootstrap helper: mint an account + key. Returns (account_hash, raw_key).
        The raw key is shown ONCE (no-echo rule); only its hash is stored."""
        account_hash = meter_mod.hash_account(uuid.uuid4().hex)
        raw_key = self.issue_key(account_hash, "bootstrap")
        now = datetime.now(UTC).isoformat()
        with self.lock:
            self.db.execute(
                "INSERT INTO accounts (account_hash, plan, credits_face_usd, created_at) VALUES (?,?,?,?)",
                (account_hash, plan, credits_face_usd, now),
            )
            self.db.commit()
        return account_hash, raw_key

    def issue_key(self, account_hash: str, label: str = "", daily_cap_usd: Optional[float] = None) -> str:
        """Mint a new key for an existing account. Raw shown ONCE (no-echo)."""
        raw = "ck_" + uuid.uuid4().hex + uuid.uuid4().hex[:8]
        now = datetime.now(UTC).isoformat()
        with self.lock:
            self.db.execute(
                "INSERT INTO keys (key_hash, account_hash, label, created_at, daily_cap_usd) VALUES (?,?,?,?,?)",
                (self.hash_key(raw), account_hash, label, now, daily_cap_usd),
            )
            self.db.commit()
        return raw

    MIN_KEY_REF = 8

    def resolve_key(self, key_ref: Any, account_hash: str) -> Optional[str]:
        """Map a raw key, full hash, or displayed hash prefix ("abcd1234ef56...")
        to exactly ONE key_hash on this account. Empty, short, non-hex,
        unknown or ambiguous references resolve to None — an empty prefix
        must never match every key on the account."""
        if not isinstance(key_ref, str):
            return None
        ref = key_ref.strip()
        if ref.startswith("ck_"):
            ref = self.hash_key(ref)
        ref = ref.rstrip(".").lower()
        if len(ref) < self.MIN_KEY_REF or any(c not in "0123456789abcdef" for c in ref):
            return None
        with self.lock:
            rows = self.db.execute(
                "SELECT key_hash FROM keys WHERE account_hash = ? AND substr(key_hash, 1, ?) = ?",
                (account_hash, len(ref), ref),
            ).fetchall()
        return rows[0][0] if len(rows) == 1 else None

    def revoke_key(self, key_hash: str, account_hash: str) -> bool:
        target = self.resolve_key(key_hash, account_hash)
        if not target:
            return False
        with self.lock:
            cur = self.db.execute(
                "UPDATE keys SET revoked = 1 WHERE key_hash = ? AND account_hash = ?",
                (target, account_hash),
            )
            self.db.commit()
        return cur.rowcount > 0

    def set_key_cap(self, key_hash: str, account_hash: str, daily_cap_usd: Optional[float]) -> bool:
        target = self.resolve_key(key_hash, account_hash)
        if not target:
            return False
        with self.lock:
            cur = self.db.execute(
                "UPDATE keys SET daily_cap_usd = ? WHERE key_hash = ? AND account_hash = ?",
                (daily_cap_usd, target, account_hash),
            )
            self.db.commit()
        return cur.rowcount > 0

    def keys_for(self, account_hash: str) -> list:
        """Presence + metadata only — key material never leaves the store."""
        with self.lock:
            rows = self.db.execute(
                "SELECT key_hash, label, created_at, revoked, daily_cap_usd FROM keys WHERE account_hash = ?",
                (account_hash,),
            ).fetchall()
        return [
            {
                "key_hash": r[0][:12] + "...",
                "label": r[1],
                "created_at": r[2],
                "revoked": bool(r[3]),
                "daily_cap_usd": r[4],
            }
            for r in rows
        ]

    def credits(self, account_hash: str) -> float:
        with self.lock:
            row = self.db.execute(
                "SELECT credits_face_usd FROM accounts WHERE account_hash = ?", (account_hash,)
            ).fetchone()
        return float(row[0]) if row else 0.0

    def reserve(self, account_hash: str, worst_case_usd: float) -> bool:
        """SpendGate semantics: reserve worst case -> deny if reserve fails.
        Mirrors cosmos_spend (on-tree, bind SpendGate directly)."""
        with self.lock:
            row = self.db.execute(
                "SELECT credits_face_usd FROM accounts WHERE account_hash = ?", (account_hash,)
            ).fetchone()
            if not row:
                return False
            if float(row[0]) + 1e-9 < worst_case_usd:
                return False
            self.db.execute(
                "UPDATE accounts SET credits_face_usd = credits_face_usd - ? WHERE account_hash = ?",
                (worst_case_usd, account_hash),
            )
            self.db.commit()
            return True

    def settle_refund_unused(self, account_hash: str, reserved: float, measured: float) -> None:
        """Settle: adjust balance by (reserved - measured)."""
        diff = round(float(reserved) - float(measured), 12)
        if abs(diff) > 1e-13:
            with self.lock:
                self.db.execute(
                    "UPDATE accounts SET credits_face_usd = credits_face_usd + ? WHERE account_hash = ?",
                    (diff, account_hash),
                )
                self.db.commit()

    def grant(self, account_hash: str, face_usd: float) -> None:
        with self.lock:
            self.db.execute(
                "UPDATE accounts SET credits_face_usd = credits_face_usd + ? WHERE account_hash = ?",
                (float(face_usd), account_hash),
            )
            self.db.commit()

    def free_today(self, account_hash: str) -> float:
        day = datetime.now(UTC).strftime("%Y-%m-%d")
        with self.lock:
            row = self.db.execute(
                "SELECT face_usd FROM free_daily WHERE account_hash = ? AND day = ?", (account_hash, day)
            ).fetchone()
        return float(row[0]) if row else 0.0

    def free_add(self, account_hash: str, face_usd: float) -> None:
        day = datetime.now(UTC).strftime("%Y-%m-%d")
        with self.lock:
            self.db.execute(
                """INSERT INTO free_daily (account_hash, day, face_usd) VALUES (?,?,?)
                   ON CONFLICT(account_hash, day) DO UPDATE SET face_usd = face_usd + ?""",
                (account_hash, day, float(face_usd), float(face_usd)),
            )
            self.db.commit()

    def key_usage_today(self, key_hash: str) -> float:
        day = datetime.now(UTC).strftime("%Y-%m-%d")
        with self.lock:
            row = self.db.execute(
                "SELECT face_usd FROM key_daily WHERE key_hash = ? AND day = ?", (key_hash, day)
            ).fetchone()
        return float(row[0]) if row else 0.0

    def key_usage_add(self, key_hash: str, face_usd: float) -> None:
        day = datetime.now(UTC).strftime("%Y-%m-%d")
        with self.lock:
            self.db.execute(
                """INSERT INTO key_daily (key_hash, day, face_usd) VALUES (?,?,?)
                   ON CONFLICT(key_hash, day) DO UPDATE SET face_usd = face_usd + ?""",
                (key_hash, day, float(face_usd), float(face_usd)),
            )
            self.db.commit()

    def get_settings(self, account_hash: str) -> Dict[str, Any]:
        with self.lock:
            rows = self.db.execute(
                "SELECT key, value FROM settings WHERE account_hash = ?", (account_hash,)
            ).fetchall()
        out: Dict[str, Any] = {}
        for k, v in rows:
            try:
                out[k] = json.loads(v)
            except Exception:
                out[k] = v
        # Defaults
        out.setdefault("autotopup", {"enabled": False, "cap_usd": 0.0})
        out.setdefault("data_contribution", {"aggregates": True, "per_run": False})
        out.setdefault("alerts", {"thresholds": [0.5, 0.8, 1.0], "slack_webhook": ""})
        return out

    def set_setting(self, account_hash: str, key: str, value: Any) -> None:
        val_str = json.dumps(value) if not isinstance(value, str) else value
        now = datetime.now(UTC).isoformat()
        with self.lock:
            self.db.execute(
                """INSERT INTO settings (account_hash, key, value, updated_at) VALUES (?,?,?,?)
                   ON CONFLICT(account_hash, key) DO UPDATE SET value = ?, updated_at = ?""",
                (account_hash, key, val_str, now, val_str, now),
            )
            self.db.commit()


# ----------------------------------------------------------------------------- gateway
class PayGateway:
    def __init__(self, store: Store, meter: meter_mod.Meter, rail: Any,
                 models: Dict[str, Any], config: Dict[str, Any],
                 vertex_rail: Any = None, bedrock_rail: Any = None,
                 openrouter_rail: Any = None, azure_rail: Any = None):
        self.store = store
        self.meter = meter
        self.rail = rail
        self.vertex_rail = vertex_rail
        self.bedrock_rail = bedrock_rail
        self.openrouter_rail = openrouter_rail
        self.azure_rail = azure_rail
        self.models = models
        self.config = config
        self.free_daily = float(config.get("free_tier", {}).get("daily_face_usd", 1.50))
        self.limiter = RateLimiter(key_rpm=60, ip_rpm=120)
        self._models_mtime: Optional[float] = None
        self._models_lock = threading.Lock()
        try:
            self._models_mtime = cfg.MODELS_PATH.stat().st_mtime
        except Exception:
            pass

    def _resolve_rail(self, entry: Dict[str, Any]) -> Any:
        """Named resale rails never fall through to RunPod. Absent rail stays RunPod."""
        rail_type = str(entry.get("rail") or "runpod")
        if rail_type == "vertex":
            return self.vertex_rail
        if rail_type == "bedrock":
            return self.bedrock_rail
        if rail_type == "openrouter":
            return self.openrouter_rail
        if rail_type == "azure":
            return self.azure_rail
        if rail_type == "runpod":
            return self.rail
        return None

    def _no_supply(self, entry: Dict[str, Any]) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
        return 503, {
            "error": {
                "code": "no_supply",
                "message": f"rail {entry.get('rail')!r} is not configured",
            }
        }, {}

    def maybe_reload_models(self) -> bool:
        """Hot-reload models.json when the nightly job rewrites it — the
        Win-Win-Win price recompute must reach a running gateway without a
        restart. Returns True when the registry was refreshed."""
        try:
            mtime = cfg.MODELS_PATH.stat().st_mtime
        except Exception:
            return False
        with self._models_lock:
            if self._models_mtime == mtime:
                return False
            try:
                fresh = cfg.load_models()
            except Exception:
                return False  # keep serving the last good registry
            if fresh:
                self.models = fresh
                self._models_mtime = mtime
                return True
            return False

    # ---- helpers ----
    def _model_entry(self, model: str) -> Optional[Dict[str, Any]]:
        m = self.models.get(model)
        if not m or not m.get("endpoint"):
            return None
        return m

    def _estimate_worst_case(self, openai_req: Dict[str, Any], price_per_m: Any) -> float:
        """Reserve worst case: input estimate at the prompt price + max_tokens at
        the completion price. Accepts a (prompt, completion) tuple or one float
        (legacy). Rough by design — settle is measured; the reserve bounds the deny."""
        if isinstance(price_per_m, (tuple, list)):
            p_in, p_out = float(price_per_m[0]), float(price_per_m[1])
        else:
            p_in = p_out = float(price_per_m)
        raw_max = openai_req.get("max_tokens") or openai_req.get("max_completion_tokens")
        max_tokens = int(raw_max) if raw_max is not None and str(raw_max).isdigit() else 4096
        est_in = _estimate_input_tokens(openai_req)
        return (est_in * p_in + max_tokens * p_out) / 1_000_000.0

    def _meter_headers(self, acct: Dict[str, Any], free_remaining_face: Optional[float]) -> Dict[str, str]:
        reset = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta
        reset += timedelta(days=1)
        h = {
            "x-cosmos-quota-reset": reset.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "x-cosmos-credit-balance": f"{self.store.credits(acct['account_hash']):.8f}",
        }
        if free_remaining_face is not None:
            h["x-cosmos-quota-remaining"] = f"{free_remaining_face:.4f}"
        return h

    def _emit(self, **ev: Any) -> None:
        try:
            self.meter.emit(ev)
        except meter_mod.MeterError:
            pass  # meter never breaks the call path; local buffer keeps the truth

    def has_supply(self, model_id: str) -> bool:
        """True when the model is in the registry AND its rail is configured."""
        entry = self._model_entry(model_id)
        return bool(entry) and _rail_configured(self._resolve_rail(entry))

    # ---- the main lane ----
    def _out_of_credit(self, acct: Dict[str, Any], free_remaining: Optional[float] = None
                       ) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
        return 402, {
            "error": {
                "code": "insufficient_credits",
                "message": OUT_OF_CREDIT_MSG,
                "add_credit_url": ADD_CREDIT_URL,
            }
        }, self._meter_headers(acct, free_remaining)

    def _plan_reserve(self, body: Dict[str, Any], price: Any, entry: Dict[str, Any],
                      balance: float) -> Optional[Tuple[float, Optional[int]]]:
        """Return (reserve_usd, upstream_max_tokens) or None when the balance
        cannot cover the call. An explicit max_tokens is honoured as-is. When it
        is absent the output is capped at min(4096, model max) and clamped down
        to what the balance can pay for; the cap is sent upstream so the call
        can never outrun its reserve."""
        if isinstance(price, (tuple, list)):
            p_in, p_out = float(price[0]), float(price[1])
        else:
            p_in = p_out = float(price)
        explicit = _explicit_max_tokens(body)
        est_in = _estimate_input_tokens(body)
        in_cost = est_in * p_in / 1_000_000.0
        if explicit is not None:
            worst = in_cost + explicit * p_out / 1_000_000.0
            return (worst, None) if balance + 1e-12 >= worst else None
        cap = DEFAULT_MAX_TOKENS
        model_max = entry.get("max_completion_tokens") or entry.get("context_length")
        try:
            if model_max and int(model_max) > 0:
                cap = min(cap, int(model_max))
        except (TypeError, ValueError):
            pass
        full = in_cost + cap * p_out / 1_000_000.0
        if balance + 1e-12 >= full:
            return full, cap
        if p_out <= 0 or balance <= in_cost:
            return None
        allowed = min(cap, int((balance - in_cost) * 1_000_000.0 / p_out))
        if allowed < MIN_CLAMPED_TOKENS:
            return None
        return in_cost + allowed * p_out / 1_000_000.0, allowed

    def chat(self, key: str, body: Dict[str, Any], client_ip: str = "127.0.0.1") -> Tuple[int, Dict[str, Any], Dict[str, str]]:
        # 1. Rate limiting (before auth: burst protection for everyone)
        allowed, reason = self.limiter.check_and_record(key, client_ip)
        if not allowed:
            return 429, {
                "error": {
                    "code": reason,
                    "message": "Rate limit exceeded (60 requests/minute). Please back off.",
                }
            }, {"Retry-After": "60"}

        acct = self.store.account_for_key(key)
        if not acct:
            return 401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}}, {}

        # Registry refresh only matters past auth (model lookup follows).
        self.maybe_reload_models()

        # 2. Key-specific cap check (a limit the owner set: stays 429)
        if acct.get("daily_cap_usd") is not None:
            k_used = self.store.key_usage_today(acct["key_hash"])
            if k_used >= float(acct["daily_cap_usd"]):
                return 429, {
                    "error": {
                        "code": "key_cap_exhausted",
                        "message": f"Key-specific daily cap of ${acct['daily_cap_usd']:.2f} reached.",
                    }
                }, self._meter_headers(acct, None)

        model_id = str(body.get("model") or "")
        entry = self._model_entry(model_id)
        target_rail = self._resolve_rail(entry) if entry else None
        if not entry or not _rail_configured(target_rail):
            return 404, {"error": {
                "code": "model_not_found",
                "message": f"model {model_id!r} is not available. See GET /v1/models for the list.",
            }}, {}

        # Upstream is always called non-streaming; SSE is synthesized by chat_sse.
        body = {k: v for k, v in body.items() if k not in ("stream", "stream_options")}

        price = model_prices(entry)
        plan = acct["plan"]
        account_hash = acct["account_hash"]
        balance = self.store.credits(account_hash)
        is_free = plan == "free" and balance <= 0.0 and self.free_daily > 0
        free_remaining = None
        reserved = 0.0

        if is_free:
            used = self.store.free_today(account_hash)
            free_remaining = max(0.0, self.free_daily - used)
            if free_remaining <= 0:
                self._emit(
                    schema=meter_mod.SCHEMA, event="QUOTA_HIT", account=account_hash,
                    quota="free_daily", lane="A", model=model_id,
                    at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                )
                return self._out_of_credit(acct, 0.0)
            if _explicit_max_tokens(body) is None:
                body["max_tokens"] = DEFAULT_MAX_TOKENS
        else:
            if balance <= 0.0:
                return self._out_of_credit(acct)
            plan_r = self._plan_reserve(body, price, entry, balance)
            if plan_r is None:
                return self._out_of_credit(acct)
            worst, upstream_max = plan_r
            if not self.store.reserve(account_hash, worst):
                return self._out_of_credit(acct)
            reserved = worst
            if upstream_max is not None:
                body["max_tokens"] = upstream_max

        try:
            resp = target_rail.runsync(body)
        except Exception as e:
            if reserved:
                self.store.settle_refund_unused(account_hash, reserved, 0.0)
            if _is_no_supply(e):
                return self._no_supply(entry)
            self._emit(schema=meter_mod.SCHEMA, event="RUN_FAILED", account=account_hash,
                       lane="A", rail=entry.get("endpoint") or entry.get("rail"), model=model_id, wallet="cosmos",
                       at=time.strftime("%Y-%m-%dT%H:%M:%S%z"))
            return 502, {"error": {"code": "rail_error", "message": str(e)}}, self._meter_headers(acct, free_remaining)

        usage = resp.get("usage") if isinstance(resp, dict) else None
        usage = usage if isinstance(usage, dict) else {}
        if usage.get("unpriced") or not usage:
            # UNPRICED is never zero: refund the reserve, hold the worst case as UNPRICED.
            self._emit(schema=meter_mod.SCHEMA, event="RUN_UNPRICED", account=account_hash,
                       lane="A", rail=entry.get("endpoint"), model=model_id, wallet="cosmos",
                       cost={"estimated_usd": round(reserved, 6), "provenance": "estimate"},
                       at=time.strftime("%Y-%m-%dT%H:%M:%S%z"))
            if reserved:
                self.store.settle_refund_unused(account_hash, reserved, 0.0)
            headers = self._meter_headers(acct, free_remaining)
            return 200, resp, headers

        tin = int(usage.get("prompt_tokens") or 0)
        tout = int(usage.get("completion_tokens") or 0)
        measured = billed_usd(price, tin, tout, usage.get("cost"))
        if reserved:
            self.store.settle_refund_unused(account_hash, reserved, measured)
        if is_free:
            self.store.free_add(account_hash, measured)
            used_now = self.store.free_today(account_hash)
            free_remaining = max(0.0, self.free_daily - used_now)

        if acct.get("key_hash"):
            self.store.key_usage_add(acct["key_hash"], measured)

        self._emit(
            schema=meter_mod.SCHEMA, event="RUN_SETTLED", account=account_hash,
            lane="A", rail=entry.get("endpoint"), model=model_id, wallet="cosmos",
            tokens={"in": tin, "out": tout, "cached": int(usage.get("cached_tokens", 0) or 0)},
            cost={"estimated_usd": round(reserved, 6), "measured_usd": round(measured, 10),
                  "provenance": "measured"},
            at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        )
        return 200, resp, self._meter_headers(acct, free_remaining)

    def chat_sse(self, key: str, body: Dict[str, Any], client_ip: str = "127.0.0.1"
                 ) -> Tuple[int, Any, Dict[str, str]]:
        """stream:true. The upstream call is non-streaming (same gating and
        billing as chat). On 200 returns a list of OpenAI-compatible SSE lines;
        on error returns the JSON error object with its real HTTP status."""
        code, obj, headers = self.chat(key, body, client_ip)
        if code != 200:
            return code, obj, headers
        return 200, completion_to_sse(obj, str(body.get("model") or "")), headers

    def chat_stream(self, key: str, body: Dict[str, Any], client_ip: str = "127.0.0.1") -> Iterator[str]:
        """Legacy generator form of chat_sse: errors become one SSE error line."""
        code, obj, _headers = self.chat_sse(key, body, client_ip)
        if code != 200:
            yield f"data: {json.dumps(obj)}\n\n"
            return
        for line in obj:
            yield line


OUT_OF_CREDIT_MSG = "Out of credit. Add credit at https://tokenctr.com/pricing.html"
ADD_CREDIT_URL = "https://tokenctr.com/pricing.html"
DEFAULT_MAX_TOKENS = 4096
MIN_CLAMPED_TOKENS = 16


def _rail_configured(rail: Any) -> bool:
    return rail is not None and getattr(rail, "configured", True) is not False


def _explicit_max_tokens(body: Dict[str, Any]) -> Optional[int]:
    raw = body.get("max_tokens")
    if raw is None:
        raw = body.get("max_completion_tokens")
    if raw is None:
        return None
    try:
        v = int(raw)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def _estimate_input_tokens(body: Dict[str, Any]) -> int:
    est_in = 0
    for m in (body.get("messages") or []):
        est_in += len(json.dumps(m)) // 3  # ~chars/3 ~= tokens
    # Under-counting the prompt would under-reserve; pad the estimate.
    return int(est_in * 1.5) + 16


def completion_to_sse(resp: Dict[str, Any], model: str = "") -> List[str]:
    """Turn a non-streaming chat.completion into OpenAI-style SSE lines:
    role chunk, content chunk(s), finish chunk carrying usage, [DONE]."""
    resp = resp if isinstance(resp, dict) else {}
    cid = str(resp.get("id") or f"chatcmpl-{int(time.time() * 1000)}")
    created = int(resp.get("created") or time.time())
    mdl = str(resp.get("model") or model)
    choices = resp.get("choices") or [{"index": 0, "message": {"role": "assistant", "content": ""}}]

    def chunk(index: int, delta: Dict[str, Any], finish: Any = None, usage: Any = None) -> str:
        c: Dict[str, Any] = {"id": cid, "object": "chat.completion.chunk", "created": created,
                             "model": mdl,
                             "choices": [{"index": index, "delta": delta, "finish_reason": finish}]}
        if usage is not None:
            c["usage"] = usage
        return f"data: {json.dumps(c)}\n\n"

    out: List[str] = []
    for i, ch in enumerate(choices):
        idx = int(ch.get("index", i) or 0)
        msg = ch.get("message") or {}
        out.append(chunk(idx, {"role": msg.get("role") or "assistant", "content": ""}))
        reasoning = msg.get("reasoning")
        if isinstance(reasoning, str) and reasoning:
            out.append(chunk(idx, {"reasoning": reasoning}))
        text = msg.get("content")
        if isinstance(text, str) and text:
            for k in range(0, len(text), 512):
                out.append(chunk(idx, {"content": text[k:k + 512]}))
        tool_calls = msg.get("tool_calls")
        if isinstance(tool_calls, list) and tool_calls:
            tc = [dict(t, index=n) for n, t in enumerate(tool_calls) if isinstance(t, dict)]
            out.append(chunk(idx, {"tool_calls": tc}))
        last = i == len(choices) - 1
        out.append(chunk(idx, {}, ch.get("finish_reason") or "stop",
                         resp.get("usage") if last and resp.get("usage") else None))
    out.append("data: [DONE]\n\n")
    return out


def model_prices(entry: Dict[str, Any]) -> Tuple[float, float]:
    """(prompt, completion) USD per 1M tokens for a registry entry.

    Split prices win: prompt_per_m_usd / completion_per_m_usd. Older entries
    carry one price_per_m_usd, used for both sides (backward compatible).
    Missing or bad values are 0.0 here; registry loaders skip such models."""
    def _num(v: Any) -> Optional[float]:
        try:
            f = float(v)
        except (TypeError, ValueError):
            return None
        return f if f >= 0 and f == f and f != float("inf") else None

    single = _num(entry.get("price_per_m_usd"))
    p_in = _num(entry.get("prompt_per_m_usd"))
    p_out = _num(entry.get("completion_per_m_usd"))
    if p_in is None:
        p_in = single if single is not None else 0.0
    if p_out is None:
        p_out = single if single is not None else 0.0
    return p_in, p_out


def billed_usd(prices: Tuple[float, float], tokens_in: int, tokens_out: int,
               vendor_cost_usd: Any = None) -> float:
    """prompt_tokens*prompt_price + completion_tokens*completion_price (per 1M).

    If the rail reports what the vendor actually charged (OpenRouter
    usage.cost) and that is HIGHER than the token math (images, web search,
    audio, cache writes, a price change since the registry refresh), bill the
    vendor cost instead. Zero markup still holds; the operator never eats it."""
    token_math = (int(tokens_in) * prices[0] + int(tokens_out) * prices[1]) / 1_000_000.0
    try:
        vc = float(vendor_cost_usd) if vendor_cost_usd is not None else None
    except (TypeError, ValueError):
        vc = None
    if vc is not None and vc == vc and vc > token_math and vc < 1e6:
        return vc
    return token_math


# Fixed price table: the server decides what a pack costs; the client only names it.
CREDIT_PACKS: Dict[str, Tuple[float, str]] = {
    "mini": (5.0, "Mini \u2014 $5 credit"),
    "maker": (19.0, "Maker \u2014 $19 credit"),
    "studio": (59.0, "Studio \u2014 $59 credit"),
}
FOUNDING_OFFERS: Dict[str, Tuple[float, str]] = {
    "paid": (10.0, "Founding \u2014 lifetime membership + $20 credit"),
    "verified": (1.0, "Card verification \u2014 $1 credit"),
}


def _client_amount_mismatch(body: Dict[str, Any], price: float) -> Optional[str]:
    """None if the client sent no amount or the exact table price; else an error string."""
    if "amount_usd" not in body or body.get("amount_usd") is None:
        return None
    try:
        sent = float(body.get("amount_usd"))
    except (TypeError, ValueError):
        return "amount_usd is not a number"
    if sent != sent or abs(sent - price) > 1e-9:
        return f"amount_usd {body.get('amount_usd')!r} does not match the pack price {price:.2f}"
    return None


_SITE_ORIGINS = ("https://tokenctr.com/", "https://www.tokenctr.com/")


def _site_url(value: Any, default: str) -> str:
    """Checkout return URLs must stay on the TokenCenter site (no open redirect)."""
    if isinstance(value, str) and value.startswith(_SITE_ORIGINS) and len(value) < 500:
        return value
    return default


# ----------------------------------------------------------------------------- HTTP Handler
def make_handler(gw: PayGateway, api: Any = None) -> type:
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *args):  # no-echo rule: never log keys or sensitive headers
            pass

        def _add_cors_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers",
                "Authorization, Content-Type, CF-Turnstile-Token, Stripe-Signature, PayPal-Webhook-Id, "
                "PayPal-Transmission-Id, PayPal-Transmission-Time, PayPal-Transmission-Sig, PayPal-Cert-Url, PayPal-Auth-Algo, "
                "X-Cosmos-Quota-Remaining, X-Cosmos-Quota-Reset, X-Cosmos-Credit-Balance",
            )
            self.send_header(
                "Access-Control-Expose-Headers",
                "X-Cosmos-Quota-Remaining, X-Cosmos-Quota-Reset, X-Cosmos-Credit-Balance, Retry-After",
            )
            self.send_header("Access-Control-Max-Age", "86400")

        def do_OPTIONS(self):
            self.send_response(204)
            self._add_cors_headers()
            self.end_headers()

        def _send(self, code: int, obj: Any, headers: Optional[Dict[str, str]] = None) -> None:
            payload = json.dumps(obj).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self._add_cors_headers()
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(payload)

        def _client_ip(self) -> str:
            if cf_mod:
                return cf_mod.CloudflareClient.extract_client_ip(dict(self.headers))
            xff = self.headers.get("X-Forwarded-For")
            if xff:
                return xff.split(",")[0].strip()
            return self.client_address[0] if self.client_address else "127.0.0.1"

        def _auth_key(self) -> Optional[str]:
            h = self.headers.get("Authorization", "")
            if h.startswith("Bearer "):
                return h[7:].strip()
            return None

        def do_GET(self):
            from urllib.parse import parse_qs, urlparse
            parsed = urlparse(self.path)
            raw_path = parsed.path
            path = raw_path.rstrip("/") if raw_path != "/" else "/"
            q = parse_qs(parsed.query)

            if path == "/healthz":
                self._send(200, {
                    "ok": True,
                    "service": "cosmos-pay-gateway",
                    "at": datetime.now(UTC).isoformat(),
                    "version": "1.0-canonical",
                })
            elif path == "/v1/models":
                gw.maybe_reload_models()
                key = self._auth_key()
                if not key or not gw.store.account_for_key(key):
                    self._send(401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}})
                    return
                models = [
                    {
                        "id": mid,
                        "object": "model",
                        "price_per_m_usd": m.get("price_per_m_usd"),
                        "prompt_per_m_usd": model_prices(m)[0],
                        "completion_per_m_usd": model_prices(m)[1],
                        "cogs_per_m_usd": m.get("cogs_per_m_usd"),
                        "owned_by": "cosmos",
                        "stocked": m.get("stocked", True),
                    }
                    for mid, m in gw.models.items()
                    if gw.has_supply(mid)
                ]
                self._send(200, {"object": "list", "data": models})
            elif path.startswith("/v1/models/"):
                key = self._auth_key()
                if not key or not gw.store.account_for_key(key):
                    self._send(401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}})
                    return
                mid = path[len("/v1/models/"):].strip("/")
                m = gw.models.get(mid) if gw.has_supply(mid) else None
                if not m:
                    self._send(404, {"error": {"code": "model_not_found", "message": f"model {mid!r} not found"}})
                    return
                self._send(200, {
                    "id": mid,
                    "object": "model",
                    "price_per_m_usd": m.get("price_per_m_usd"),
                    "prompt_per_m_usd": model_prices(m)[0],
                    "completion_per_m_usd": model_prices(m)[1],
                    "cogs_per_m_usd": m.get("cogs_per_m_usd"),
                    "owned_by": "cosmos",
                    "stocked": m.get("stocked", True),
                })
            elif path == "/v1/usage/today":
                key = self._auth_key()
                acct = gw.store.account_for_key(key) if key else None
                if not acct:
                    self._send(401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}})
                    return
                day = datetime.now(UTC).strftime("%Y-%m-%d")
                self._send(200, {
                    "day": day,
                    "free_used_face_usd": gw.store.free_today(acct["account_hash"]),
                    "free_quota_face_usd": gw.free_daily,
                    "credits_face_usd": gw.store.credits(acct["account_hash"]),
                    "rollup": gw.meter.rollup_day(day, account=acct["account_hash"]),
                })
            elif path == "/v1/account" and api:
                key = self._auth_key()
                acct = gw.store.account_for_key(key) if key else None
                if not acct:
                    self._send(401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}})
                    return
                self._send(200, {
                    "account": acct["account_hash"],
                    "plan": acct["plan"],
                    "credits_face_usd": gw.store.credits(acct["account_hash"]),
                    "keys": gw.store.keys_for(acct["account_hash"]),
                    "settings": gw.store.get_settings(acct["account_hash"]),
                    "promises": [
                        "zero markup: usage is billed at the provider's cost",
                        "prepaid credit; no subscription",
                    ],
                })
            elif path.startswith("/v1/logs") and api:
                key = self._auth_key()
                acct = gw.store.account_for_key(key) if key else None
                if not acct:
                    self._send(401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}})
                    return

                # Check if specific event id is requested: /v1/logs/{event_id}
                sub = path[len("/v1/logs"):].strip("/")
                if sub:
                    events = gw.meter.tail(limit=1000, account=acct["account_hash"])
                    found = next((e for e in events if e.get("event_id") == sub), None)
                    if found:
                        self._send(200, {"data": found})
                    else:
                        self._send(404, {"error": {"code": "event_not_found"}})
                    return

                limit = int(q.get("limit", ["100"])[0])
                events = gw.meter.tail(limit=limit, account=acct["account_hash"])
                lane = q.get("lane", [None])[0]
                model = q.get("model", [None])[0]
                if lane:
                    events = [e for e in events if e.get("lane") == lane]
                if model:
                    events = [e for e in events if e.get("model") == model]
                self._send(200, {"object": "list", "data": events})
            elif path == "/v1/statement" and api:
                key = self._auth_key()
                acct = gw.store.account_for_key(key) if key else None
                if not acct:
                    self._send(401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}})
                    return
                period = q.get("period", [datetime.now(UTC).strftime("%Y-%m")])[0]
                events = [
                    e for e in gw.meter.tail(10000, account=acct["account_hash"])
                    if isinstance(e, dict) and str(e.get("at", "")).startswith(period)
                ]
                settled = [e for e in events if e.get("event") == "RUN_SETTLED"]
                spent = sum(float((e.get("cost") or {}).get("measured_usd") or 0.0) for e in settled)
                grants = [e for e in events if e.get("event") in ("CREDIT_GRANTED", "CREDIT_PURCHASED")]
                self._send(200, {
                    "period": period,
                    "usage": {"runs": len(settled), "spent_usd": round(spent, 10),
                              "unpriced_runs": sum(1 for e in events if e.get("event") == "RUN_UNPRICED")},
                    "credit_events": grants,
                })
            elif path == "/v1/statement/export" and api:
                key = self._auth_key()
                acct = gw.store.account_for_key(key) if key else None
                if not acct:
                    self._send(401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}})
                    return
                period = q.get("period", [datetime.now(UTC).strftime("%Y-%m")])[0]
                events = [
                    e for e in gw.meter.tail(10000, account=acct["account_hash"])
                    if e.get("at", "").startswith(period)
                ]
                buf = io.StringIO()
                writer = csv.writer(buf)
                writer.writerow(["at", "event", "lane", "model", "measured_usd", "event_id"])
                for e in events:
                    cost = (e.get("cost") or {}).get("measured_usd", 0.0)
                    writer.writerow([e.get("at"), e.get("event"), e.get("lane"), e.get("model"), cost, e.get("event_id")])
                csv_bytes = buf.getvalue().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", f"attachment; filename=statement-{period}.csv")
                self.send_header("Content-Length", str(len(csv_bytes)))
                self._add_cors_headers()
                self.end_headers()
                self.wfile.write(csv_bytes)
            elif path == "/v1/settings" and api:
                key = self._auth_key()
                acct = gw.store.account_for_key(key) if key else None
                if not acct:
                    self._send(401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}})
                    return
                self._send(200, {"settings": gw.store.get_settings(acct["account_hash"])})
            elif path == "/v1/founding/status" and api:
                self._send(200, api["founding"].status())
            elif path == "/v1/cloudflare/status":
                import hmac as _hmac
                sk = (api or {}).get("setup_key") or ""
                given = self.headers.get("X-Setup-Key") or q.get("setup_key", [""])[0]
                if not sk or not given or not _hmac.compare_digest(str(given), str(sk)):
                    self._send(404, {"error": {"code": "not_found"}})
                    return
                if cf_mod:
                    try:
                        cf_client = cf_mod.CloudflareClient()
                        tok_info = cf_client.verify_token()
                        zone_info = cf_client.get_zone_info()
                        self._send(200, {
                            "cloudflare_active": True,
                            "token_status": tok_info.get("status"),
                            "zone": zone_info.get("name"),
                            "zone_status": zone_info.get("status"),
                        })
                        return
                    except Exception as e:
                        self._send(200, {"cloudflare_active": False, "error": str(e)})
                        return
                self._send(200, {"cloudflare_active": False, "note": "Cloudflare module not loaded"})
            elif path == "/v1/export" and api:
                key = self._auth_key()
                acct = gw.store.account_for_key(key) if key else None
                if not acct:
                    self._send(401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}})
                    return
                self._send(200, {
                    "object": "export",
                    "events": gw.meter.tail(100000, account=acct["account_hash"]),
                })
            elif path == "/v1/export/full" and api:
                key = self._auth_key()
                acct = gw.store.account_for_key(key) if key else None
                if not acct:
                    self._send(401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}})
                    return
                self._send(200, {
                    "account": acct["account_hash"],
                    "plan": acct["plan"],
                    "credits": gw.store.credits(acct["account_hash"]),
                    "keys": gw.store.keys_for(acct["account_hash"]),
                    "settings": gw.store.get_settings(acct["account_hash"]),
                    "events": gw.meter.tail(100000, account=acct["account_hash"]),
                })
            else:
                self._send(404, {"error": {"code": "not_found"}})

        def do_POST(self):
            from urllib.parse import urlparse
            raw_path = urlparse(self.path).path
            path = raw_path.rstrip("/") if raw_path != "/" else "/"
            client_ip = self._client_ip()

            # Read raw bytes first — Stripe and processors sign the raw payload.
            length_str = self.headers.get("Content-Length", "0")
            length = int(length_str) if length_str.isdigit() else 0
            raw = self.rfile.read(length) if length else b""
            try:
                body = json.loads(raw.decode("utf-8")) if raw else {}
            except json.JSONDecodeError:
                self._send(400, {"error": {"code": "bad_json"}})
                return

            # ---- webhooks: processor-agnostic, raw bytes verified first ----
            if path.startswith("/v1/webhooks/") and api:
                processor = path.rsplit("/", 1)[-1]
                try:
                    # Pass raw bytes directly so webhook signature verification is 100% exact
                    out = api["webhooks"].receive(processor, raw, dict(self.headers))
                    self._send(200, out)
                except (hooks_mod.WebhookError, proc_mod.ProcessorError) as e:
                    self._send(400, {"error": {"code": str(e).split(" ")[0], "message": str(e)}})
                return

            # ---- Turnstile verification on sensitive routes ----
            turnstile_token = self.headers.get("CF-Turnstile-Token") or body.get("turnstile_token")
            if path in ("/v1/account/create", "/v1/founding/purchase") and turnstile_token and cf_mod:
                if not cf_mod.CloudflareClient.verify_turnstile(turnstile_token, remote_ip=client_ip):
                    self._send(403, {"error": {"code": "turnstile_verification_failed"}})
                    return

            # ---- anonymous key (no email, no card): $0 credit, per-IP daily limit ----
            if path == "/v1/account/anonymous" and api:
                anon_cfg = (api.get("config") or {}).get("anonymous", {}) if isinstance(api, dict) else {}
                if anon_cfg.get("enabled", True) is False:
                    self._send(403, {"error": {"code": "anonymous_disabled"}})
                    return
                ok, why = gw.store.anon_allow(
                    client_ip,
                    per_ip_daily=int(anon_cfg.get("per_ip_daily", 3)),
                    global_daily=int(anon_cfg.get("global_daily", 300)),
                )
                if not ok:
                    self._send(429, {"error": {"code": why, "message": "anonymous key limit reached; try again tomorrow"}},
                               {"Retry-After": "3600"})
                    return
                ah, raw_key = gw.store.create_account(plan="free", credits_face_usd=0.0)
                self._send(200, {"api_key": raw_key, "key": raw_key, "account": ah,
                                 "credits_face_usd": 0.0, "shown_once": True})
                return

            # ---- account bootstrap (setup key from secrets — v1 pre-OAuth) ----
            if path == "/v1/account/create" and api:
                if body.get("setup_key") != api["setup_key"]:
                    self._send(403, {"error": {"code": "bad_setup_key"}})
                    return
                ah, raw_key = gw.store.create_account(plan="free")
                self._send(200, {"account": ah, "key": raw_key, "shown_once": True})
                return

            key = self._auth_key()
            acct = gw.store.account_for_key(key) if key else None
            if not key or not acct:
                self._send(401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}})
                return

            # ---- meter ingest (batched sync from local buffer) ----
            if path == "/v1/meter/ingest":
                events = body.get("events") if isinstance(body, dict) else None
                if not isinstance(events, list):
                    self._send(400, {"error": {"code": "bad_events", "message": "events array required"}})
                    return
                ingested = 0
                for ev in events:
                    if not isinstance(ev, dict):
                        continue
                    # Tenant isolation: the event is stamped with the
                    # authenticated caller's account. A key can never write
                    # another account's book, even if the payload lies.
                    ev = dict(ev)
                    ev["account"] = acct["account_hash"]
                    try:
                        gw.meter.emit(ev)
                        ingested += 1
                    except meter_mod.MeterError:
                        continue
                self._send(200, {"ok": True, "ingested": ingested, "received": len(events)})
                return

            # ---- keys ----
            if path == "/v1/keys/issue" and api:
                cap = body.get("daily_cap_usd")
                raw_key = gw.store.issue_key(
                    acct["account_hash"],
                    body.get("label", ""),
                    daily_cap_usd=float(cap) if cap is not None else None,
                )
                self._send(200, {"key": raw_key, "shown_once": True})
                return
            if path in ("/v1/keys/revoke", "/v1/keys/rotate", "/v1/keys/cap") and api:
                if not gw.store.resolve_key(body.get("key_hash"), acct["account_hash"]):
                    self._send(400, {"error": {
                        "code": "bad_key_hash",
                        "message": "key_hash must identify exactly one key on this account "
                                   "(at least 8 hex characters of the hash shown in your key list)",
                    }})
                    return
            if path == "/v1/keys/revoke" and api:
                ok = gw.store.revoke_key(body.get("key_hash", ""), acct["account_hash"])
                self._send(200, {"revoked": ok})
                return
            if path == "/v1/keys/rotate" and api:
                target = gw.store.resolve_key(body.get("key_hash"), acct["account_hash"])
                cap = body.get("daily_cap_usd")
                raw_key = gw.store.issue_key(
                    acct["account_hash"],
                    body.get("label", "rotated"),
                    daily_cap_usd=float(cap) if cap is not None else None,
                )
                gw.store.revoke_key(target, acct["account_hash"])  # exact full hash: never the new key
                self._send(200, {"key": raw_key, "shown_once": True, "revoked": target[:12] + "..."})
                return
            if path == "/v1/keys/cap" and api:
                kh = body.get("key_hash", "")
                cap = body.get("daily_cap_usd")
                ok = gw.store.set_key_cap(kh, acct["account_hash"], float(cap) if cap is not None else None)
                self._send(200, {"ok": ok, "key_hash": kh, "daily_cap_usd": cap})
                return

            # ---- settings ----
            if path.startswith("/v1/settings/") and api:
                s_key = path.rsplit("/", 1)[-1]
                val = body.get("value", body)
                gw.store.set_setting(acct["account_hash"], s_key, val)
                self._send(200, {"ok": True, "setting": s_key, "value": val})
                return

            # ---- credit purchase ----
            if path == "/v1/credits/purchase" and api:
                pack_id = str(body.get("pack_id") or body.get("pack") or "").strip().lower()
                if pack_id not in CREDIT_PACKS:
                    self._send(400, {"error": {"code": "bad_pack",
                                               "message": "pack_id must be one of: " + ", ".join(CREDIT_PACKS)}})
                    return
                amount, product_name = CREDIT_PACKS[pack_id]
                why = _client_amount_mismatch(body, amount)
                if why:
                    self._send(400, {"error": {"code": "amount_mismatch", "message": why}})
                    return
                processor = body.get("processor", "stripe")
                success_url = _site_url(body.get("success_url"), "https://tokenctr.com/done.html")
                cancel_url = _site_url(body.get("cancel_url"), "https://tokenctr.com/cancel.html")
                try:
                    if processor == "paypal" and api.get("paypal"):
                        order = api["paypal"].create_order(acct["account_hash"], amount, success_url, cancel_url)
                        self._send(200, {"checkout": order})
                        return
                    if api.get("stripe"):
                        sess = api["stripe"].create_checkout_session(
                            acct["account_hash"],
                            amount,
                            success_url=success_url,
                            cancel_url=cancel_url,
                            metadata={"account_hash": acct["account_hash"], "pack_id": pack_id},
                            product_name=product_name,
                        )
                        self._send(200, {"checkout": sess, "pack_id": pack_id, "amount_usd": amount})
                        return
                    self._send(503, {"error": {"code": "no_processor", "message": "payment processor unavailable"}})
                    return
                except proc_mod.ProcessorError as e:
                    self._send(502, {"error": {"code": "processor_error", "message": str(e)}})
                    return

            # ---- founding ----
            if path == "/v1/founding/purchase" and api:
                tier = str(body.get("tier", "paid") or "").strip().lower()
                if tier not in FOUNDING_OFFERS:
                    self._send(400, {"error": {"code": "bad_tier", "message": "paid | verified"}})
                    return
                f_amount, f_name = FOUNDING_OFFERS[tier]
                why = _client_amount_mismatch(body, f_amount)
                if why:
                    self._send(400, {"error": {"code": "amount_mismatch", "message": why}})
                    return
                plan_now = acct.get("plan") if isinstance(acct, dict) else None
                if plan_now == "founding" or (plan_now == "verified_free" and tier != "paid"):
                    self._send(409, {"error": {"code": "already_founding",
                                               "message": "this account already holds that tier"}})
                    return
                if not api.get("stripe"):
                    self._send(503, {"error": {"code": "no_processor", "message": "payment processor unavailable"}})
                    return
                try:
                    sess = api["stripe"].create_checkout_session(
                        acct["account_hash"], f_amount,
                        success_url=_site_url(body.get("success_url"), "https://tokenctr.com/done.html"),
                        cancel_url=_site_url(body.get("cancel_url"), "https://tokenctr.com/cancel.html"),
                        metadata={"founding": tier, "account_hash": acct["account_hash"]},
                        product_name=f_name,
                    )
                except proc_mod.ProcessorError as e:
                    self._send(502, {"error": {"code": "processor_error", "message": str(e)}})
                    return
                self._send(200, {
                    "checkout": sess, "tier": tier, "amount_usd": f_amount,
                    "note": "the webhook grants the tier — the click only creates the session",
                })
                return

            # ---- chat (the main lane) ----
            if path == "/v1/chat/completions":
                if not body.get("model"):
                    self._send(400, {"error": {"code": "missing_model", "message": "model parameter is required"}})
                    return
                if "messages" not in body or not isinstance(body.get("messages"), list):
                    self._send(400, {"error": {"code": "missing_messages", "message": "messages array is required"}})
                    return

                if body.get("stream") is True:
                    # Upstream is called non-streaming; errors keep their real
                    # HTTP status as JSON, success becomes OpenAI-style SSE.
                    code, obj, headers = gw.chat_sse(key, body, client_ip=client_ip)
                    if code != 200:
                        self._send(code, obj, headers)
                        return
                    payload = "".join(obj).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                    self.send_header("Cache-Control", "no-cache")
                    self.send_header("Content-Length", str(len(payload)))
                    for hk, hv in (headers or {}).items():
                        self.send_header(hk, hv)
                    self._add_cors_headers()
                    self.end_headers()
                    self.wfile.write(payload)
                    self.wfile.flush()
                    return

                code, obj, headers = gw.chat(key, body, client_ip=client_ip)
                self._send(code, obj, headers)
                return

            self._send(404, {"error": {"code": "not_found"}})

    return Handler


def build_app() -> Tuple[Any, Any, Dict[str, Any]]:
    """Construct (gw, api, config) without binding a socket. Used by main() and
    by passenger_wsgi.py (cPanel / CloudLinux Python app)."""
    config = cfg.load_config()
    secrets = cfg.load_secrets(required=["mesh_hmac_key_hex"])
    models = cfg.load_models()
    store = Store(str(cfg.KEYS_DB))
    meter = meter_mod.Meter(str(cfg.METER_DB))

    try:
        rail: Any = RunPodRail(
            endpoint_id=secrets.get("runpod_endpoint_id", ""),
            api_key=secrets.get("runpod_api_key", ""),
        )
    except Exception as e:
        print(f"RunPod rail not configured ({e}) — gateway serves 503 no_supply until endpoint lands")

        class _UnconfiguredRail:
            configured = False

            def runsync(self, body: Dict[str, Any]) -> Dict[str, Any]:
                raise RailError("BAD_CONFIG runpod endpoint/key not configured")

            def stream(self, body: Dict[str, Any]) -> Any:
                raise RailError("BAD_CONFIG runpod endpoint/key not configured")
                yield  # make this a generator

        rail = _UnconfiguredRail()
    gw = PayGateway(store, meter, rail, models, config, **attach_rails(config, secrets))

    # ---- UI-facing API mounts when components are available ----
    api: Any = None
    try:
        founding = founding_mod.Founding(store, meter, cap=int(config.get("founding", {}).get("cap", 500)))
        stripe = proc_mod.StripeAdapter(
            secret_key=secrets.get("stripe_secret_key", ""),
            webhook_secret=secrets.get("stripe_webhook_secret", ""),
        ) if secrets.get("stripe_secret_key") else None
        paypal = proc_mod.PayPalAdapter(
            client_id=secrets.get("paypal_client_id", ""),
            client_secret=secrets.get("paypal_client_secret", ""),
        ) if secrets.get("paypal_client_id") else None
        router = hooks_mod.WebhookRouter(store, meter, founding, stripe=stripe, paypal=paypal)
        router.attach(str(cfg.ROOT / "webhooks.db"))
        api = {
            "founding": founding,
            "webhooks": router,
            "stripe": stripe,
            "paypal": paypal,
            "setup_key": secrets.get("setup_key", ""),
            "config": config,
        }
    except Exception as e:
        print(f"UI API not fully mounted: {e} — core chat lane still serves")

    return gw, api, config


def main() -> None:
    gw, api, config = build_app()
    models = gw.models
    host = config["gateway"]["host"]
    port = int(config["gateway"]["port"])
    httpd = ThreadingHTTPServer((host, port), make_handler(gw, api))
    print(f"cosmos-pay-gateway on http://{host}:{port}  (models: {len(models)})")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
