#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_entitlement â€” mint/verify, tamper refuse, expiry/grace, free core."""
import sys
import os
import sys
import os
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cosmos_pay_entitlement as ent

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


KEY = b"test-key-32-bytes-0000000000000000"

# --- mint/verify round trip ---
claims = {"plan": "founding", "holder": "h:abc", "expires_epoch": time.time() + 86400,
          "grace_days": 30, "caps": {"perks": "lifetime"}}
tok = ent.mint(claims, KEY)
got = ent.verify(tok, KEY)
check("round trip: plan survives", got.get("plan") == "founding")
check("round trip: caps survive", got.get("caps", {}).get("perks") == "lifetime")

# --- tamper â†’ BAD_MAC, refuse loud (never silently downgrade) ---
tampered = tok[:-4] + ("AAAA" if not tok.endswith("AAAA") else "BBBB")
try:
    ent.verify(tampered, KEY)
    check("tampered token refused", False)
except ent.EntitlementError as e:
    check("tampered token refused", "BAD_MAC" in str(e))

# --- wrong key â†’ BAD_MAC ---
try:
    ent.verify(tok, b"another-key-0000000000000000000000")
    check("wrong key refused", False)
except ent.EntitlementError as e:
    check("wrong key refused", "BAD_MAC" in str(e))

# --- bad format ---
try:
    ent.verify("not-a-token", KEY)
    check("bad format refused", False)
except ent.EntitlementError as e:
    check("bad format refused", "BAD_FORMAT" in str(e))

# --- expiry â†’ EXPIRED ---
expired = ent.mint({"plan": "founding", "expires_epoch": time.time() - 86400, "grace_days": 0}, KEY)
try:
    ent.verify(expired, KEY)
    check("expired refused", False)
except ent.EntitlementError as e:
    check("expired refused", "EXPIRED" in str(e))

# --- grace: expired but within grace_days â†’ valid with grace=True ---
grace_tok = ent.mint({"plan": "founding", "expires_epoch": time.time() - 86400, "grace_days": 30}, KEY)
got = ent.verify(grace_tok, KEY)
check("grace: valid within window", isinstance(got, ent.GraceEntitlement) and got.get("grace") is True)
check("grace: grace_ends_epoch set", got.get("grace_ends_epoch", 0) > time.time())

# --- free core: never expires ---
free = ent.mint(ent.free_core_claims("h:keith"), KEY)
got = ent.verify(free, KEY)
check("free core: expires_epoch 0 â†’ never expires", got.get("expires_epoch") == 0)

# --- mint requires plan + expires ---
try:
    ent.mint({"holder": "h:x"}, KEY)
    check("mint requires plan+expires", False)
except ent.EntitlementError as e:
    check("mint requires plan+expires", "BAD_FORMAT" in str(e))

# --- founding claims shape ---
fc = ent.founding_claims("h:abc", 20.0)
check("founding claims: lifetime perks + grant face", fc["caps"]["perks"] == "lifetime"
      and fc["caps"]["token_grant_face_usd"] == 20.0)

print(f"\n{PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)

