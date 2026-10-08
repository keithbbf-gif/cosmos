#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_meter — cosmos-meter/1 events, local SQLite buffer, batched sync.

The meter is a TAIL ON THE LEDGER, not a second book: dashboard = meter DB =
statement. The reconciliation invariant (statement.total == Σ rollups == Σ events)
is testable — Keith's 32× export-vs-billing scar is structurally impossible here.

Privacy is STRUCTURAL, not a policy:
  - content keys are rejected at emit (prompt/messages/output/code/text/…)
  - account ids are hashes (h:…)
  - source_sha is a hash; porosity ships as aggregates
  - the research export is the same shape, further aggregated

Sync is idempotent by event_id; offline for weeks is fine (carry-over state
machinery). Provenance discipline inherited from cosmos_spend: estimate never
bills; UNPRICED is never zero. Thread-safe: the gateway serves requests on
worker threads (ThreadingHTTPServer), so the connection is shared with a lock.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
import urllib.request
import uuid
from typing import Any, Dict, Iterable, List, Optional

SCHEMA = "cosmos-meter/1"

EVENTS = {
    "RUN_SETTLED",      # call completed, cost measured — Lane A draws credits, Lane B accrues toll, Lane C data only
    "RUN_FAILED",       # failed vendor-side — no charge (provenance records it)
    "RUN_UNPRICED",     # completed, cost unknown — worst case held, never silently $0
    "CREDIT_PURCHASED", # money-in: user buys credits
    "CREDIT_GRANTED",   # money-in at $0: Founding grant, referral bonus, $1 verification credit
    "TOLL_ACCRUED",     # monthly bracket checkpoint — derived but ledgered so statements reconcile
    "QUOTA_HIT",        # free-proxy 429 — the Founding-offer trigger + abuse telemetry
}

# Privacy structural: these keys may never appear anywhere in an event.
FORBIDDEN_KEYS = {
    "prompt", "messages", "output", "content", "text", "code", "completion",
    "system", "instructions", "response", "body",
}

REQUIRED = {
    "RUN_SETTLED": {"lane", "rail", "model", "wallet", "tokens", "cost"},
    "RUN_FAILED": {"lane", "rail", "model"},
    "RUN_UNPRICED": {"lane", "rail", "model", "cost"},
    "CREDIT_PURCHASED": {"amount_usd"},
    "CREDIT_GRANTED": {"amount_usd", "reason"},
    "TOLL_ACCRUED": {"amount_usd", "period"},
    "QUOTA_HIT": {"quota"},
}

LANES = {"A", "B", "C"}
WALLETS = {"cosmos", "byok", "free"}
PROVENANCE = {"estimate", "measured", "billed"}


class MeterError(RuntimeError):
    """kind in {BAD_SCHEMA, FORBIDDEN_CONTENT, MISSING_FIELD, BAD_VALUE}."""


def hash_account(account: str) -> str:
    """Account ids are hashes — h:… — never email/PII. IDEMPOTENT: an already-
    hashed id (h:-prefixed) returns as-is, so the store's account_hash and the
    meter's account field are the same value (filtering works)."""
    s = str(account)
    if s.startswith("h:"):
        return s
    return "h:" + hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def _reject_content(obj: Any, path: str = "") -> None:
    """Walk the event; any forbidden key at any depth = FORBIDDEN_CONTENT."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            if str(k).lower() in FORBIDDEN_KEYS:
                raise MeterError(f"FORBIDDEN_CONTENT key {p!r} — privacy is structural")
            _reject_content(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _reject_content(v, f"{path}[{i}]")


def validate(event: Dict[str, Any]) -> Dict[str, Any]:
    """Schema check + privacy walk + required fields. Returns a cleaned copy."""
    if event.get("schema", SCHEMA) != SCHEMA:
        raise MeterError(f"BAD_SCHEMA {event.get('schema')!r} != {SCHEMA!r}")
    kind = event.get("event")
    if kind not in EVENTS:
        raise MeterError(f"BAD_SCHEMA unknown event {kind!r}")
    _reject_content(event)
    missing = REQUIRED[kind] - set(event.keys())
    if missing:
        raise MeterError(f"MISSING_FIELD {kind}: {sorted(missing)}")
    clean = dict(event)
    clean["schema"] = SCHEMA
    clean.setdefault("event_id", uuid.uuid4().hex)
    clean.setdefault("at", time.strftime("%Y-%m-%dT%H:%M:%S%z"))
    if "account" in clean:
        clean["account"] = hash_account(clean["account"])
    cost = clean.get("cost")
    if cost is not None:
        if not isinstance(cost, dict):
            raise MeterError("BAD_VALUE cost must be a dict")
        prov = cost.get("provenance")
        if prov is not None and prov not in PROVENANCE:
            raise MeterError(f"BAD_VALUE provenance {prov!r} not in {sorted(PROVENANCE)}")
        if prov == "measured" and cost.get("measured_usd") is None:
            raise MeterError("BAD_VALUE provenance=measured requires measured_usd")
    if clean.get("lane") is not None and clean["lane"] not in LANES:
        raise MeterError(f"BAD_VALUE lane {clean['lane']!r}")
    if clean.get("wallet") is not None and clean["wallet"] not in WALLETS:
        raise MeterError(f"BAD_VALUE wallet {clean['wallet']!r}")
    return clean


class Meter:
    """SQLite buffer. Local-first: emit is always possible; sync is best-effort.
    Thread-safe: one shared connection (check_same_thread=False) + a write lock —
    the gateway serves on ThreadingHTTPServer worker threads."""

    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = threading.Lock()
        with self.lock:
            self.db.execute(
                """CREATE TABLE IF NOT EXISTS meter_events (
                     event_id TEXT PRIMARY KEY,
                     at TEXT NOT NULL,
                     event TEXT NOT NULL,
                     lane TEXT, model TEXT, rail TEXT, wallet TEXT,
                     account TEXT,
                     measured_usd REAL,
                     payload TEXT NOT NULL,
                     synced INTEGER NOT NULL DEFAULT 0
                   )"""
            )
            self.db.execute("CREATE INDEX IF NOT EXISTS ix_meter_at ON meter_events(at)")
            self.db.execute("CREATE INDEX IF NOT EXISTS ix_meter_sync ON meter_events(synced)")
            self.db.commit()

    def emit(self, event: Dict[str, Any]) -> str:
        """Validate → insert. Returns event_id. Raises MeterError on any violation."""
        clean = validate(event)
        with self.lock:
            self.db.execute(
                "INSERT OR IGNORE INTO meter_events (event_id, at, event, lane, model, rail, wallet, account, measured_usd, payload, synced) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,0)",
                (
                    clean["event_id"], clean["at"], clean["event"], clean.get("lane"),
                    clean.get("model"), clean.get("rail"), clean.get("wallet"),
                    clean.get("account"),
                    (clean.get("cost") or {}).get("measured_usd"),
                    json.dumps(clean, sort_keys=True),
                ),
            )
            self.db.commit()
        return clean["event_id"]

    def tail(self, limit: int = 100, since: Optional[str] = None,
             account: Optional[str] = None) -> List[Dict[str, Any]]:
        """account filter: callers only ever see their own events (privacy)."""
        q = "SELECT payload FROM meter_events"
        args: List[Any] = []
        conds: List[str] = []
        if since:
            conds.append("at > ?")
            args.append(since)
        if account:
            conds.append("account = ?")
            args.append(hash_account(account))
        if conds:
            q += " WHERE " + " AND ".join(conds)
        q += " ORDER BY at DESC LIMIT ?"
        args.append(int(limit))
        with self.lock:
            rows = self.db.execute(q, args).fetchall()
        return [json.loads(r[0]) for r in rows]

    def pending(self, limit: int = 500) -> List[Dict[str, Any]]:
        with self.lock:
            rows = self.db.execute(
                "SELECT payload FROM meter_events WHERE synced = 0 ORDER BY at LIMIT ?",
                (int(limit),),
            ).fetchall()
        return [json.loads(r[0]) for r in rows]

    def mark_synced(self, event_ids: Iterable[str]) -> int:
        ids = list(event_ids)
        if not ids:
            return 0
        q = "?" * len(ids)
        with self.lock:
            cur = self.db.execute(
                f"UPDATE meter_events SET synced = 1 WHERE event_id IN ({','.join(q)})",
                ids,
            )
            self.db.commit()
        return cur.rowcount

    def rollup_day(self, day: str, account: Optional[str] = None) -> List[Dict[str, Any]]:
        """Per lane/model/day: runs, verified, tokens, measured — the dashboard's food.
        account filter: callers only ever see their own rollups."""
        q = "SELECT payload FROM meter_events WHERE at LIKE ? AND event = 'RUN_SETTLED'"
        args: List[Any] = [day + "%"]
        if account:
            q += " AND account = ?"
            args.append(hash_account(account))
        with self.lock:
            rows = self.db.execute(q, args).fetchall()
        agg: Dict[tuple, Dict[str, Any]] = {}
        for (payload,) in rows:
            ev = json.loads(payload)
            key = (ev.get("lane"), ev.get("model"))
            a = agg.setdefault(key, {"lane": ev.get("lane"), "model": ev.get("model"),
                                     "runs": 0, "tokens_in": 0, "tokens_out": 0,
                                     "measured_usd": 0.0})
            a["runs"] += 1
            t = ev.get("tokens") or {}
            a["tokens_in"] += int(t.get("in", 0))
            a["tokens_out"] += int(t.get("out", 0))
            c = ev.get("cost") or {}
            if c.get("provenance") in ("measured", "billed") and c.get("measured_usd") is not None:
                a["measured_usd"] += float(c["measured_usd"])
        return sorted(agg.values(), key=lambda x: (x["lane"], x["model"]))

    def sync(self, base_url: str, token: str, batch: int = 500, timeout: int = 30) -> int:
        """Batched idempotent upload. Server dedupes by event_id; replays are no-ops.
        Best-effort: any transport failure returns what was posted so far."""
        if not base_url:
            return 0
        posted = 0
        while True:
            events = self.pending(batch)
            if not events:
                break
            body = json.dumps({"schema": SCHEMA, "events": events}).encode("utf-8")
            req = urllib.request.Request(
                base_url.rstrip("/") + "/v1/meter/ingest",
                data=body,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    if resp.status != 200:
                        break
            except Exception:
                break
            self.mark_synced(e["event_id"] for e in events)
            posted += len(events)
            if len(events) < batch:
                break
        return posted
