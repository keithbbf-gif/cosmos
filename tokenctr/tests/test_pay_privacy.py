#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_privacy — the audit regression: cross-account isolation + concurrency.

The audit find: on a multi-account server, /v1/logs, /v1/export, /v1/statement,
and /v1/usage/today returned ALL accounts' events. These tests make the leak
class structurally impossible:
    1. tail(account=…) never returns another account's events
    2. rollup_day(account=…) same
    3. hash_account is idempotent (store hash == meter hash)
    4. concurrent emit loses nothing (the lock works under load)
"""
from __future__ import annotations

import os
import sys
import tempfile
import threading

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cosmos_pay_meter as meter

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


tmp = tempfile.mkdtemp()
m = meter.Meter(os.path.join(tmp, "m.db"))

# --- idempotent hashing ---
h1 = meter.hash_account("alice")
check("hash_account idempotent", meter.hash_account(h1) == h1)
check("hash format h:…", h1.startswith("h:"))

# --- seed two accounts' events ---
for who, usd in (("alice", 0.01), ("bob", 0.02)):
    m.emit({"schema": meter.SCHEMA, "event": "RUN_SETTLED", "lane": "A", "rail": "r",
            "model": "m", "wallet": "cosmos", "account": who,
            "tokens": {"in": 10, "out": 5}, "cost": {"measured_usd": usd, "provenance": "measured"}})

# --- 1. tail isolation ---
alice_events = m.tail(100, account="alice")
check("tail(account=alice) → only alice", len(alice_events) == 1
      and all(e.get("account") == h1 for e in alice_events))
bob_events = m.tail(100, account="bob")
check("tail(account=bob) → only bob", len(bob_events) == 1)
check("unfiltered tail still sees both (operator view)", len(m.tail(100)) == 2)

# --- 2. rollup isolation ---
import time as _t
day = _t.strftime("%Y-%m-%d")
alice_roll = m.rollup_day(day, account="alice")
check("rollup(account=alice) → only alice", len(alice_roll) == 1
      and alice_roll[0]["measured_usd"] == 0.01)
both_roll = m.rollup_day(day)
check("unfiltered rollup sees both", sum(r["measured_usd"] for r in both_roll) == 0.03)

# --- 3. the store-hash == meter-hash invariant (the double-hash kill) ---
import cosmos_pay_gateway as gw
store = gw.Store(os.path.join(tmp, "keys.db"))
ah, raw = store.create_account(plan="free")
ev = meter.validate({"schema": meter.SCHEMA, "event": "RUN_SETTLED", "lane": "A",
                     "rail": "r", "model": "m", "wallet": "cosmos", "account": ah,
                     "tokens": {"in": 1}, "cost": {"measured_usd": 0.01, "provenance": "measured"}})
check("store account_hash == meter account field (idempotent hash)", ev["account"] == ah)

# --- 4. concurrency: 8 threads × 25 events, nothing lost ---
N_THREADS, N_EACH = 8, 25
errors = []


def worker(tid: int) -> None:
    try:
        for i in range(N_EACH):
            m.emit({"schema": meter.SCHEMA, "event": "RUN_SETTLED", "lane": "A",
                    "rail": "r", "model": "m", "wallet": "cosmos", "account": f"t{tid}",
                    "tokens": {"in": 1, "out": 1},
                    "cost": {"measured_usd": 0.001, "provenance": "measured"}})
    except Exception as e:  # noqa: BLE001
        errors.append(e)


threads = [threading.Thread(target=worker, args=(t,)) for t in range(N_THREADS)]
for t in threads:
    t.start()
for t in threads:
    t.join()
check(f"concurrent emit: no errors ({N_THREADS}×{N_EACH})", not errors)
check("concurrent emit: nothing lost", len(m.tail(100000)) == 2 + N_THREADS * N_EACH)

print(f"\n{PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)
