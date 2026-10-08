#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_meter â€” schema validation, privacy rejection, idempotency, rollup."""
import sys
import os
import time
import uuid
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


DB = ":memory:"
m = meter.Meter(DB)

# --- schema validation ---
try:
    meter.validate({"schema": "cosmos-meter/0", "event": "RUN_SETTLED"})
    check("bad schema rejected", False)
except meter.MeterError as e:
    check("bad schema rejected", "BAD_SCHEMA" in str(e))

try:
    meter.validate({"schema": meter.SCHEMA, "event": "NOT_A_THING"})
    check("unknown event rejected", False)
except meter.MeterError as e:
    check("unknown event rejected", "BAD_SCHEMA" in str(e))

# --- privacy structural: content keys rejected at ANY depth ---
try:
    meter.validate({"schema": meter.SCHEMA, "event": "RUN_SETTLED", "lane": "A",
                    "rail": "r", "model": "m", "wallet": "cosmos",
                    "tokens": {"in": 1}, "cost": {"measured_usd": 0.01, "provenance": "measured"},
                    "prompt": "secret code"})
    check("forbidden top-level key rejected", False)
except meter.MeterError as e:
    check("forbidden top-level key rejected", "FORBIDDEN_CONTENT" in str(e))

try:
    meter.validate({"schema": meter.SCHEMA, "event": "RUN_SETTLED", "lane": "A",
                    "rail": "r", "model": "m", "wallet": "cosmos",
                    "tokens": {"in": 1}, "cost": {"measured_usd": 0.01, "provenance": "measured"},
                    "meta": {"nested": {"messages": [{"role": "user"}]}}})
    check("forbidden nested key rejected", False)
except meter.MeterError as e:
    check("forbidden nested key rejected", "FORBIDDEN_CONTENT" in str(e))

# --- required fields per event type ---
try:
    meter.validate({"schema": meter.SCHEMA, "event": "RUN_SETTLED", "lane": "A"})
    check("missing fields rejected", False)
except meter.MeterError as e:
    check("missing fields rejected", "MISSING_FIELD" in str(e))

# --- provenance discipline ---
try:
    meter.validate({"schema": meter.SCHEMA, "event": "RUN_SETTLED", "lane": "A",
                    "rail": "r", "model": "m", "wallet": "cosmos",
                    "tokens": {"in": 1}, "cost": {"provenance": "measured"}})
    check("measured requires measured_usd", False)
except meter.MeterError as e:
    check("measured requires measured_usd", "BAD_VALUE" in str(e))

# --- account hashing: PII never stored raw ---
ev = meter.validate({"schema": meter.SCHEMA, "event": "RUN_SETTLED", "lane": "A",
                     "rail": "r", "model": "m", "wallet": "cosmos", "account": "keith@example.com",
                     "tokens": {"in": 10, "out": 5}, "cost": {"measured_usd": 0.01, "provenance": "measured"}})
check("account hashed (h:â€¦, no PII)", ev["account"].startswith("h:") and "keith" not in ev["account"])
check("event_id assigned", len(ev["event_id"]) == 32)

# --- emit + tail + idempotency ---
eid = m.emit({"schema": meter.SCHEMA, "event": "RUN_SETTLED", "lane": "A",
              "rail": "r", "model": "m", "wallet": "cosmos",
              "tokens": {"in": 10, "out": 5}, "cost": {"measured_usd": 0.01, "provenance": "measured"}})
m.emit({"schema": meter.SCHEMA, "event": "RUN_SETTLED", "event_id": eid, "lane": "A",
        "rail": "r", "model": "m", "wallet": "cosmos",
        "tokens": {"in": 10, "out": 5}, "cost": {"measured_usd": 0.01, "provenance": "measured"}})
check("idempotent: same event_id â†’ one row", len(m.tail(100)) == 1)

# --- rollup ---
m.emit({"schema": meter.SCHEMA, "event": "RUN_SETTLED", "lane": "A",
        "rail": "r", "model": "m2", "wallet": "cosmos",
        "tokens": {"in": 100, "out": 50}, "cost": {"measured_usd": 0.10, "provenance": "measured"}})
roll = m.rollup_day(time.strftime("%Y-%m-%d"))
check("rollup has 2 (lane,model) groups", len(roll) == 2)
check("rollup tokens summed", sum(r["tokens_in"] for r in roll) == 110)

# --- QUOTA_HIT (the Founding-offer trigger) ---
m.emit({"schema": meter.SCHEMA, "event": "QUOTA_HIT", "quota": "free_daily", "lane": "A"})
check("QUOTA_HIT accepted", any(e["event"] == "QUOTA_HIT" for e in m.tail(10)))

print(f"\n{PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)


