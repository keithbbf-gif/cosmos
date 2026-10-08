#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_gateway — api.cosmos…/v1: the only public surface.

    POST /v1/chat/completions   auth -> rate-limit -> quota/breaker (fail-closed) ->
                                route -> relay (runsync or SSE stream) -> settle ->
                                meter -> headers
    GET  /v1/models             the supply registry (our prices)
    GET  /v1/usage/today        local meter query (real-time, no delayed dashboard)
    GET  /v1/account            account info, plan, credit balance, keys, promises
    GET  /v1/logs               audit logs and verification receipts
    GET  /v1/logs/{id}          single event receipt lookup
    GET  /v1/statement          monthly toll statement and credit purchases
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
    GET  /v1/cloudflare/status  Cloudflare zone and edge status
    GET  /healthz               gateway liveness
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

    def revoke_key(self, key_hash: str, account_hash: str) -> bool:
        target = self.hash_key(key_hash) if key_hash.startswith("ck_") else key_hash.rstrip(".")
        with self.lock:
            cur = self.db.execute(
                "UPDATE keys SET revoked = 1 WHERE (key_hash = ? OR key_hash LIKE ?) AND account_hash = ?",
                (target, target + "%", account_hash),
            )
            self.db.commit()
        return cur.rowcount > 0

    def set_key_cap(self, key_hash: str, account_hash: str, daily_cap_usd: Optional[float]) -> bool:
        target = self.hash_key(key_hash) if key_hash.startswith("ck_") else key_hash.rstrip(".")
        with self.lock:
            cur = self.db.execute(
                "UPDATE keys SET daily_cap_usd = ? WHERE (key_hash = ? OR key_hash LIKE ?) AND account_hash = ?",
                (daily_cap_usd, target, target + "%", account_hash),
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
        diff = round(float(reserved) - float(measured), 8)
        if abs(diff) > 1e-9:
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

    def _estimate_worst_case(self, openai_req: Dict[str, Any], price_per_m: float) -> float:
        """Reserve worst case: input estimate + max_tokens at the model price.
        Rough by design — settle is measured; the reserve only bounds the deny."""
        raw_max = openai_req.get("max_tokens") or openai_req.get("max_completion_tokens")
        max_tokens = int(raw_max) if raw_max is not None and str(raw_max).isdigit() else 4096
        est_in = 0
        for m in (openai_req.get("messages") or []):
            est_in += len(json.dumps(m)) // 3  # ~chars/3 ~= tokens
        return (est_in + max_tokens) * price_per_m / 1_000_000.0

    def _meter_headers(self, acct: Dict[str, Any], free_remaining_face: Optional[float]) -> Dict[str, str]:
        reset = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta
        reset += timedelta(days=1)
        h = {
            "x-cosmos-quota-reset": reset.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "x-cosmos-credit-balance": f"{self.store.credits(acct['account_hash']):.4f}",
        }
        if free_remaining_face is not None:
            h["x-cosmos-quota-remaining"] = f"{free_remaining_face:.4f}"
        return h

    def _emit(self, **ev: Any) -> None:
        try:
            self.meter.emit(ev)
        except meter_mod.MeterError:
            pass  # meter never breaks the call path; local buffer keeps the truth

    # ---- the main lane ----
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

        # 2. Key-specific cap check
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
        if not entry:
            return 503, {"error": {"code": "no_supply", "message": f"model {model_id!r} not in the registry"}}, {}

        target_rail = self._resolve_rail(entry)
        if target_rail is None:
            return self._no_supply(entry)

        price = float(entry.get("price_per_m_usd", 0.0))
        plan = acct["plan"]
        is_free = plan == "free" and self.store.credits(acct["account_hash"]) <= 0.0
        free_remaining = None
        reserved = 0.0

        if is_free:
            used = self.store.free_today(acct["account_hash"])
            free_remaining = max(0.0, self.free_daily - used)
            if free_remaining <= 0:
                self._emit(
                    schema=meter_mod.SCHEMA, event="QUOTA_HIT", account=acct["account_hash"],
                    quota="free_daily", lane="A", model=model_id,
                    at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                )
                reset = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
                from datetime import timedelta
                reset += timedelta(days=1)
                return 429, {
                    "error": {
                        "code": "quota_exhausted",
                        "message": "You've used today's free capacity. $10 keeps you running tonight.",
                        "resets_at": reset.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "founding_offer": "/founding",
                    }
                }, self._meter_headers(acct, 0.0)
        else:
            worst = self._estimate_worst_case(body, price)
            if not self.store.reserve(acct["account_hash"], worst):
                return 402, {
                    "error": {"code": "insufficient_credits",
                              "message": "reserve failed — the breaker denies before it spends"},
                }, self._meter_headers(acct, None)
            reserved = worst

        account_hash = acct["account_hash"]
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

        usage = resp.get("usage") or {}
        if usage.get("unpriced"):
            # UNPRICED is never zero: refund the reserve, hold the worst case as UNPRICED.
            self._emit(schema=meter_mod.SCHEMA, event="RUN_UNPRICED", account=account_hash,
                       lane="A", rail=entry.get("endpoint"), model=model_id, wallet="cosmos",
                       cost={"estimated_usd": reserved, "provenance": "estimate"},
                       at=time.strftime("%Y-%m-%dT%H:%M:%S%z"))
            if reserved:
                self.store.settle_refund_unused(account_hash, reserved, 0.0)
            headers = self._meter_headers(acct, free_remaining)
            return 200, resp, headers

        tin = int(usage.get("prompt_tokens") or 0)
        tout = int(usage.get("completion_tokens") or 0)
        measured = (tin + tout) * price / 1_000_000.0
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
            cost={"estimated_usd": round(reserved, 6), "measured_usd": round(measured, 8),
                  "provenance": "measured"},
            at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        )
        return 200, resp, self._meter_headers(acct, free_remaining)

    def chat_stream(self, key: str, body: Dict[str, Any], client_ip: str = "127.0.0.1") -> Iterator[str]:
        """SSE streaming relay: yields data: <json> lines ending with data: [DONE]."""
        allowed, reason = self.limiter.check_and_record(key, client_ip)
        if not allowed:
            yield f"data: {json.dumps({'error': {'code': reason, 'message': 'Rate limit exceeded'}})}\n\n"
            return

        acct = self.store.account_for_key(key)
        if not acct:
            yield f"data: {json.dumps({'error': {'code': 'bad_key', 'message': 'unknown or revoked key'}})}\n\n"
            return

        # Registry refresh only matters past auth (model lookup follows).
        self.maybe_reload_models()

        model_id = str(body.get("model") or "")
        entry = self._model_entry(model_id)
        if not entry:
            yield f"data: {json.dumps({'error': {'code': 'no_supply', 'message': f'model {model_id!r} not in registry'}})}\n\n"
            return

        target_rail = self._resolve_rail(entry)
        if target_rail is None:
            _code, obj, _headers = self._no_supply(entry)
            yield f"data: {json.dumps(obj)}\n\n"
            return

        price = float(entry.get("price_per_m_usd", 0.0))
        plan = acct["plan"]
        is_free = plan == "free" and self.store.credits(acct["account_hash"]) <= 0.0
        reserved = 0.0

        if is_free:
            used = self.store.free_today(acct["account_hash"])
            if self.free_daily - used <= 0:
                yield f"data: {json.dumps({'error': {'code': 'quota_exhausted', 'founding_offer': '/founding'}})}\n\n"
                return
        else:
            worst = self._estimate_worst_case(body, price)
            if not self.store.reserve(acct["account_hash"], worst):
                yield f"data: {json.dumps({'error': {'code': 'insufficient_credits'}})}\n\n"
                return
            reserved = worst

        account_hash = acct["account_hash"]
        final_usage = {}
        tokens_est = 0
        try:
            for chunk in target_rail.stream(body):
                if isinstance(chunk, dict) and "usage" in chunk:
                    final_usage = chunk["usage"]
                yield f"data: {json.dumps(chunk)}\n\n"
                tokens_est += 1
            yield "data: [DONE]\n\n"
        except Exception as e:
            if reserved:
                self.store.settle_refund_unused(account_hash, reserved, 0.0)
            if _is_no_supply(e):
                _code, obj, _headers = self._no_supply(entry)
                yield f"data: {json.dumps(obj)}\n\n"
                return
            yield f"data: {json.dumps({'error': {'code': 'stream_error', 'message': str(e)}})}\n\n"
            return

        # Settle streaming call. No usage block from the worker means UNPRICED:
        # refund the reserve and hold an estimate — never invent prompt tokens
        # and bill them as measured (provenance discipline).
        if not isinstance(final_usage, dict) or not final_usage:
            self._emit(schema=meter_mod.SCHEMA, event="RUN_UNPRICED", account=account_hash,
                       lane="A", rail=entry.get("endpoint"), model=model_id, wallet="cosmos",
                       cost={"estimated_usd": round(reserved, 6), "provenance": "estimate"},
                       at=time.strftime("%Y-%m-%dT%H:%M:%S%z"))
            if reserved:
                self.store.settle_refund_unused(account_hash, reserved, 0.0)
            return

        tin = int(final_usage.get("prompt_tokens") or 0)
        tout = int(final_usage.get("completion_tokens") or tokens_est)
        measured = (tin + tout) * price / 1_000_000.0
        if reserved:
            self.store.settle_refund_unused(account_hash, reserved, measured)
        if is_free:
            self.store.free_add(account_hash, measured)
        if acct.get("key_hash"):
            self.store.key_usage_add(acct["key_hash"], measured)

        self._emit(
            schema=meter_mod.SCHEMA, event="RUN_SETTLED", account=account_hash,
            lane="A", rail=entry.get("endpoint"), model=model_id, wallet="cosmos",
            tokens={"in": tin, "out": tout, "cached": 0},
            cost={"estimated_usd": round(reserved, 6), "measured_usd": round(measured, 8),
                  "provenance": "measured"},
            at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        )


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
                        "cogs_per_m_usd": m.get("cogs_per_m_usd"),
                        "owned_by": "cosmos",
                        "stocked": m.get("stocked", True),
                    }
                    for mid, m in gw.models.items()
                ]
                self._send(200, {"object": "list", "data": models})
            elif path.startswith("/v1/models/"):
                key = self._auth_key()
                if not key or not gw.store.account_for_key(key):
                    self._send(401, {"error": {"code": "bad_key", "message": "unknown or revoked key"}})
                    return
                mid = path[len("/v1/models/"):].strip("/")
                m = gw.models.get(mid)
                if not m:
                    self._send(404, {"error": {"code": "model_not_found", "message": f"model {mid!r} not found"}})
                    return
                self._send(200, {
                    "id": mid,
                    "object": "model",
                    "price_per_m_usd": m.get("price_per_m_usd"),
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
                        "essentials free forever",
                        "toll-free under $100/mo",
                        "provider discounts pass at full value",
                        "data opt-in, anonymized, never sold",
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
                import cosmos_pay_toll as toll_mod
                events = [
                    e for e in gw.meter.tail(10000, account=acct["account_hash"])
                    if e.get("at", "").startswith(period)
                ]
                line = toll_mod.statement_line(events, period)
                grants = [e for e in events if e.get("event") in ("CREDIT_GRANTED", "CREDIT_PURCHASED")]
                self._send(200, {"period": period, "toll": line, "credit_events": grants})
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
            if path == "/v1/keys/revoke" and api:
                ok = gw.store.revoke_key(body.get("key_hash", ""), acct["account_hash"])
                self._send(200, {"revoked": ok})
                return
            if path == "/v1/keys/rotate" and api:
                cap = body.get("daily_cap_usd")
                raw_key = gw.store.issue_key(
                    acct["account_hash"],
                    body.get("label", "rotated"),
                    daily_cap_usd=float(cap) if cap is not None else None,
                )
                gw.store.revoke_key(body.get("key_hash", ""), acct["account_hash"])
                self._send(200, {"key": raw_key, "shown_once": True})
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
                amount = float(body.get("amount_usd", 10.0))
                processor = body.get("processor", "stripe")
                success_url = body.get("success_url", "https://tokenctr.com/done")
                cancel_url = body.get("cancel_url", "https://tokenctr.com/cancel")
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
                            metadata={"account_hash": acct["account_hash"]},
                        )
                        self._send(200, {"checkout": sess})
                        return
                    self._send(503, {"error": {"code": "no_processor", "message": "payment processor unavailable"}})
                    return
                except proc_mod.ProcessorError as e:
                    self._send(502, {"error": {"code": "processor_error", "message": str(e)}})
                    return

            # ---- founding ----
            if path == "/v1/founding/purchase" and api:
                tier = body.get("tier", "paid")
                amounts = {"paid": 10.0, "verified": 1.0}
                if tier not in amounts:
                    self._send(400, {"error": {"code": "bad_tier", "message": "paid | verified"}})
                    return
                try:
                    sess = api["stripe"].create_checkout_session(
                        acct["account_hash"], amounts[tier],
                        success_url=body.get("success_url", "https://tokenctr.com/done"),
                        cancel_url=body.get("cancel_url", "https://tokenctr.com/cancel"),
                        metadata={"founding": tier, "account_hash": acct["account_hash"]},
                    )
                except proc_mod.ProcessorError as e:
                    self._send(502, {"error": {"code": "processor_error", "message": str(e)}})
                    return
                self._send(200, {
                    "checkout": sess,
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
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache")
                    self.send_header("Connection", "keep-alive")
                    self._add_cors_headers()
                    self.end_headers()
                    for chunk in gw.chat_stream(key, body, client_ip=client_ip):
                        self.wfile.write(chunk.encode("utf-8"))
                        self.wfile.flush()
                    return

                code, obj, headers = gw.chat(key, body, client_ip=client_ip)
                self._send(code, obj, headers)
                return

            self._send(404, {"error": {"code": "not_found"}})

    return Handler


def main() -> None:
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

    host = config["gateway"]["host"]
    port = int(config["gateway"]["port"])
    httpd = ThreadingHTTPServer((host, port), make_handler(gw, api))
    print(f"cosmos-pay-gateway on http://{host}:{port}  (models: {len(models)})")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
