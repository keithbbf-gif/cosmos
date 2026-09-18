#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_spendguard - THE VOICE SPEND CIRCUIT-BREAKER (F5 builder, 2026-08-25).

THE PROBLEM THIS CLOSES: /api/v1/voice reaches paid model rails. The SpendGate
already governs each individual call (reserve -> deny-or-call -> settle), but
nothing bounded the AGGREGATE: a chatty client, a stuck retry loop, or a phone
pocket-dialing the mic could drain a day's budget one legitimately-gated call
at a time. This module is the breaker ABOVE the gate: per-SESSION and per-DAY
USD caps plus a per-minute request rate limit, checked BEFORE any model or
orchestrator work happens. Past any cap the voice handler answers with a canned
LOCAL reply and spends ZERO.

FAIL CLOSED, ALWAYS: check() never raises and never guesses open. A corrupt
state file, an unreadable config, a broken ledger - every error path returns
(False, reason). A breaker that fails open is not a breaker.

TRACKING (two lanes, no double counting):
  * RATE + SESSION totals live in a small local JSON counter file, written by
    check() (request stamps) and record() (USD per session, estimates allowed).
  * DAY totals come from the authority LEDGER when one is injected - the fold
    sums SPEND_SETTLED (measured_usd; an UNPRICED settle counts the estimate,
    failing toward refusal) plus outstanding SPEND_RESERVED since local
    midnight. Without a ledger, the counter file's day_usd (fed by record())
    is the day lane. clear() zeroes the local lanes and, in ledger mode,
    writes a day_credit offset - the ledger itself is never rewritten.
  * The day rolls at LOCAL midnight (the injected clock's localtime).

CONFIG: constructor defaults (session=$0.50, day=$3.00, rate=20/min) are
overridable per instance, and a small optional JSON config file
({"session_usd", "day_usd", "rate_per_min"}) is re-read on every check so the
caps are tunable without a restart. An unreadable config fails CLOSED.

Depends on stdlib ONLY. The ledger is duck-typed (.verify() yielding records);
cosmos_ledger is deliberately not imported.
"""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Optional

SESSION_CAP_USD = 0.50    # default per-session USD cap
DAY_CAP_USD = 3.00        # default per-day USD cap (rolls at local midnight)
RATE_PER_MIN = 20         # default requests per RATE_WINDOW_S across all sessions
RATE_WINDOW_S = 60.0
CALL_EST_USD = 0.02       # the worst-case estimate used when a call is unpriced

# The canned local reply the voice handler speaks when the breaker is open.
PAUSED_REPLY = ("AI budget paused - say 'resume' or clear it on the desktop.")


class SpendGuard:
    """check() -> (allowed, reason), record() -> accumulate, clear() -> reset.
    Thread-safe (one lock around every state read/write - the service handler
    runs in a ThreadingHTTPServer). All errors fail CLOSED in check()."""

    def __init__(self, state_file, config_file=None, ledger=None,
                 session_cap_usd: float = SESSION_CAP_USD,
                 day_cap_usd: float = DAY_CAP_USD,
                 rate_per_min: int = RATE_PER_MIN,
                 clock=time.time):
        self._state_file = Path(state_file)
        self._config_file = Path(config_file) if config_file else None
        self._ledger = ledger
        self._session_cap = float(session_cap_usd)
        self._day_cap = float(day_cap_usd)
        self._rate = int(rate_per_min)
        self._clock = clock
        self._lock = threading.Lock()

    # ---------------- state (counter file) ----------------
    def _today(self) -> str:
        lt = time.localtime(self._clock())
        return f"{lt.tm_year:04d}-{lt.tm_mon:02d}-{lt.tm_mday:02d}"

    def _midnight_epoch(self) -> float:
        lt = time.localtime(self._clock())
        return time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday,
                            0, 0, 0, lt.tm_wday, lt.tm_yday, -1))

    def _fresh(self) -> dict:
        return {"day": self._today(), "day_usd": 0.0, "day_credit_usd": 0.0,
                "sessions": {}, "req_epochs": []}

    def _load(self) -> dict:
        """Missing file = a legitimate fresh state. A file that EXISTS and
        cannot be parsed raises - the caller (check) fails closed on it;
        absent and unreadable are different states (the four-state rule)."""
        if not self._state_file.exists():
            return self._fresh()
        st = json.loads(self._state_file.read_text(encoding="utf-8"))
        if not isinstance(st, dict):
            raise ValueError("spendguard state is not a JSON object")
        base = self._fresh()
        base.update({k: st.get(k, base[k]) for k in base})
        if not isinstance(base["sessions"], dict) \
                or not isinstance(base["req_epochs"], list):
            raise ValueError("spendguard state has wrong shapes")
        # the day rolls HERE, at local midnight: totals and sessions reset.
        if base["day"] != self._today():
            return self._fresh()
        return base

    def _save(self, st: dict) -> None:
        """Atomic where the filesystem allows it; a plain write where it does
        not (the FUSE-mount rename scar: a non-atomic write is strictly
        better than a silently unrecorded counter)."""
        body = json.dumps(st, indent=1)
        tmp = self._state_file.with_suffix(".tmp")
        try:
            tmp.write_text(body, encoding="utf-8")
            os.replace(str(tmp), str(self._state_file))
        except OSError:
            self._state_file.write_text(body, encoding="utf-8")

    def _caps(self) -> tuple:
        """(session_cap, day_cap, rate_per_min) - config file wins when
        present; raises when the file exists and cannot be read (fail closed
        upstream)."""
        s, d, r = self._session_cap, self._day_cap, self._rate
        if self._config_file is not None and self._config_file.exists():
            cfg = json.loads(self._config_file.read_text(encoding="utf-8"))
            if not isinstance(cfg, dict):
                raise ValueError("spendguard config is not a JSON object")
            s = float(cfg.get("session_usd", s))
            d = float(cfg.get("day_usd", d))
            r = int(cfg.get("rate_per_min", r))
        return s, d, r

    # ---------------- ledger day lane ----------------
    def _ledger_day_usd(self) -> float:
        """Settled + outstanding-reserved USD on the authority chain since
        local midnight. An UNPRICED settle counts CALL_EST_USD - failing
        toward refusal, never toward free."""
        midnight = self._midnight_epoch()
        settled = 0.0
        reserved: dict = {}
        for rec in self._ledger.verify():
            ev = rec.get("event")
            p = rec.get("payload") or {}
            if not isinstance(p, dict):
                continue
            if ev == "SPEND_RESERVED":
                if float(rec.get("t") or 0.0) >= midnight:
                    reserved[p.get("rid")] = float(p.get("worst_case_usd") or 0.0)
            elif ev == "SPEND_SETTLED":
                reserved.pop(p.get("rid"), None)
                if float(rec.get("t") or 0.0) >= midnight:
                    m = p.get("measured_usd")
                    settled += CALL_EST_USD if m is None else float(m)
            elif ev == "SPEND_RELEASED":
                reserved.pop(p.get("rid"), None)
        return settled + sum(reserved.values())

    # ---------------- the breaker ----------------
    def check(self, session_id: str) -> tuple:
        """(allowed: bool, reason: str). NEVER raises; every failure is a
        refusal with the failure named - the breaker fails CLOSED."""
        try:
            with self._lock:
                sid = str(session_id or "anon")
                sess_cap, day_cap, rate = self._caps()
                st = self._load()
                now = float(self._clock())
                # 1. rate: requests inside the window, across all sessions.
                st["req_epochs"] = [t for t in st["req_epochs"]
                                    if isinstance(t, (int, float))
                                    and now - float(t) < RATE_WINDOW_S]
                if len(st["req_epochs"]) >= rate:
                    self._save(st)
                    return (False, f"RATE_LIMIT: {len(st['req_epochs'])} "
                                   f"requests in the last {RATE_WINDOW_S:.0f}s "
                                   f"(cap {rate}/min)")
                # 2. day cap: ledger lane when composed, counter lane otherwise.
                day_used = (self._ledger_day_usd() if self._ledger is not None
                            else float(st["day_usd"]))
                day_used = max(0.0, day_used - float(st["day_credit_usd"]))
                if day_used + CALL_EST_USD > day_cap:
                    self._save(st)
                    return (False, f"DAY_CAP: ${day_used:.4f} used of "
                                   f"${day_cap:.2f} today - refused before "
                                   f"the call")
                # 3. session cap.
                sess_used = float(st["sessions"].get(sid, 0.0))
                if sess_used + CALL_EST_USD > sess_cap:
                    self._save(st)
                    return (False, f"SESSION_CAP: ${sess_used:.4f} used of "
                                   f"${sess_cap:.2f} for this session")
                st["req_epochs"].append(now)
                self._save(st)
                return (True, "ok")
        except Exception as e:                                    # noqa: BLE001
            return (False, f"GUARD_ERROR ({type(e).__name__}: {e}) - "
                           f"failing CLOSED")

    def record(self, session_id: str, usd: Optional[float] = None) -> bool:
        """Accumulate spend against a session (and the day, in counter mode).
        usd=None records the worst-case estimate - an unpriced call is never
        free. Returns False instead of raising (a failed record must not
        break the reply that already happened)."""
        try:
            with self._lock:
                sid = str(session_id or "anon")
                amt = CALL_EST_USD if usd is None else max(0.0, float(usd))
                st = self._load()
                st["sessions"][sid] = float(st["sessions"].get(sid, 0.0)) + amt
                if self._ledger is None:
                    st["day_usd"] = float(st["day_usd"]) + amt
                self._save(st)
                return True
        except Exception:                                         # noqa: BLE001
            return False

    def clear(self, session_id: Optional[str] = None,
              reset_day: bool = True) -> bool:
        """Clear kill-adjacent session/rate lanes. One session, or
        everything: session totals and the rate window.
        reset_day=True (default, kept for other callers / explicit
        admin reset) also clears the day lane — in ledger mode via a
        day_credit offset equal to today's ledger spend (the chain is
        never rewritten). POST /control/resume MUST pass
        reset_day=False: unmute is not a second DAY_CAP_USD. More
        budget is spend-admin BUDGET_SET, not clear(). A corrupt
        counter file is RECOVERED here to a fresh state - clear() is
        the explicit human reset, and leaving voice bricked behind
        bad JSON would be friction; check() alone stays strictly
        fail-closed."""
        try:
            with self._lock:
                try:
                    st = self._load()
                except Exception:                                 # noqa: BLE001
                    st = self._fresh()
                if session_id is not None:
                    st["sessions"].pop(str(session_id), None)
                else:
                    st["sessions"] = {}
                    st["req_epochs"] = []
                    if reset_day:
                        st["day_usd"] = 0.0
                        if self._ledger is not None:
                            st["day_credit_usd"] = self._ledger_day_usd()
                        else:
                            st["day_credit_usd"] = 0.0
                self._save(st)
                return True
        except Exception:                                         # noqa: BLE001
            return False

    def audit(self) -> dict:
        """The breaker's own view - every number carries measured_at."""
        try:
            with self._lock:
                sess_cap, day_cap, rate = self._caps()
                st = self._load()
                now = float(self._clock())
                day_used = (self._ledger_day_usd() if self._ledger is not None
                            else float(st["day_usd"]))
                day_used = max(0.0, day_used - float(st["day_credit_usd"]))
                return {"measured_at": now, "day": st["day"],
                        "day_used_usd": round(day_used, 6),
                        "day_cap_usd": day_cap,
                        "session_cap_usd": sess_cap,
                        "rate_per_min": rate,
                        "sessions": {k: round(float(v), 6)
                                     for k, v in st["sessions"].items()},
                        "requests_last_minute": len(
                            [t for t in st["req_epochs"]
                             if now - float(t) < RATE_WINDOW_S])}
        except Exception as e:                                    # noqa: BLE001
            return {"error": "GUARD_ERROR",
                    "detail": f"{type(e).__name__}: {e}"}
