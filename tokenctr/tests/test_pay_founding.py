#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_founding — cap counter, two-tier grants, already-holds refusal."""
import os
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cosmos_pay_founding as founding
import cosmos_pay_gateway as gw
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


if __name__ == "__main__":
    tmp = tempfile.mkdtemp()
    store = gw.Store(os.path.join(tmp, "keys.db"))
    m = meter.Meter(os.path.join(tmp, "meter.db"))
    f = founding.Founding(store, m, cap=2)  # small cap for the sold-out test

    check("status starts 0/2", f.status() == {"sold": 0, "cap": 2, "remaining": 2})

    # --- account A: paid tier ---
    ah_a, key_a = store.create_account(plan="free")
    out = f.grant(ah_a, "paid")
    check("paid tier grants $20 face", out["granted_face_usd"] == 20.0)
    check("paid tier sets plan=founding", store.db.execute(
        "SELECT plan FROM accounts WHERE account_hash = ?", (ah_a,)).fetchone()[0] == "founding")
    check("credits incremented by grant", store.credits(ah_a) == 20.0)
    check("status 1/2", f.status()["sold"] == 1)
    check("CREDIT_GRANTED emitted", any(e.get("event") == "CREDIT_GRANTED" and e.get("amount_usd") == 20.0
                                        for e in m.tail(10)))

    # --- same account refuses a second founding tier ---
    try:
        f.grant(ah_a, "verified")
        check("already-founding refused", False)
    except founding.FoundingError as e:
        check("already-founding refused", "ALREADY_FOUNDING" in str(e))

    # --- account B: verified tier ($10 + $1 = $11 face) ---
    ah_b, _ = store.create_account(plan="free")
    out = f.grant(ah_b, "verified")
    check("verified tier grants $11 face ($10 + $1 credited auth)", out["granted_face_usd"] == 11.0)
    check("verified tier sets plan=verified_free", store.db.execute(
        "SELECT plan FROM accounts WHERE account_hash = ?", (ah_b,)).fetchone()[0] == "verified_free")
    check("status 2/2", f.status()["sold"] == 2)

    # --- cap: third account → SOLD_OUT ---
    ah_c, _ = store.create_account(plan="free")
    try:
        f.grant(ah_c, "paid")
        check("sold-out refused at cap", False)
    except founding.FoundingError as e:
        check("sold-out refused at cap", "SOLD_OUT" in str(e))

    # --- bad tier ---
    try:
        f.grant(ah_c, "gold")
        check("bad tier refused", False)
    except founding.FoundingError as e:
        check("bad tier refused", "BAD_TIER" in str(e))

    print(f"\n{PASS} pass, {FAIL} fail")
    sys.exit(1 if FAIL else 0)
