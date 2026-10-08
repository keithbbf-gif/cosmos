#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_entitlement — SEED-MAC-shaped entitlement token.

Borrowed from the COSMOS tree's SEED discipline (hmac.compare_digest, refuse
loud on tamper — never silently downgrade). Shape:

    token = b64url(payload_json) + "." + b64url(hmac_sha256(payload_json, key))

    payload = {plan, seats, caps, expires_epoch, grace_days, issued_at, holder}

Verify is LOCAL (no phone-home): the client verifies the MAC, then the clock.
Kinds:
    BAD_FORMAT   — not two parts, bad b64, bad json
    BAD_MAC      — tampered or wrong key → REFUSE LOUD (never silently downgrade)
    EXPIRED      — past expires_epoch AND past grace_days → refuse
    GRACE        — past expires_epoch but within grace_days → valid, flag set
                   (paid features degrade gracefully; the core never gates)

Free grants mirror OpenWork's shape: production ≤5 users free, 30-day full-
feature eval, dev/test always free — encoded as claims, not code paths.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional


class EntitlementError(RuntimeError):
    """kind in {BAD_FORMAT, BAD_MAC, EXPIRED}."""


class GraceEntitlement(dict):
    """A valid-but-expired-within-grace entitlement. `grace=True` on the dict —
    paid features may degrade; the core never gates."""


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64u_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def mint(claims: Dict[str, Any], key: bytes) -> str:
    """Server-side only. claims must include plan + expires_epoch."""
    if "plan" not in claims or "expires_epoch" not in claims:
        raise EntitlementError("BAD_FORMAT mint requires plan + expires_epoch")
    payload = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode("utf-8")
    mac = hmac.new(key, payload, hashlib.sha256).digest()
    return _b64u(payload) + "." + _b64u(mac)


def verify(token: str, key: bytes, now_epoch: Optional[float] = None) -> Dict[str, Any]:
    """Local verify. Returns claims (GraceEntitlement with grace=True inside the
    grace window). Raises EntitlementError(BAD_FORMAT | BAD_MAC | EXPIRED)."""
    now = float(now_epoch if now_epoch is not None else time.time())
    parts = str(token).split(".")
    if len(parts) != 2:
        raise EntitlementError("BAD_FORMAT expected payload.mac")
    try:
        payload = _b64u_decode(parts[0])
        mac = _b64u_decode(parts[1])
        claims = json.loads(payload.decode("utf-8"))
    except Exception as e:
        raise EntitlementError(f"BAD_FORMAT {e}") from e
    expect = hmac.new(key, payload, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expect):
        raise EntitlementError("BAD_MAC — tampered or wrong key; refuse loud")
    try:
        expires = float(claims.get("expires_epoch", 0))
        grace_days = float(claims.get("grace_days", 0))
    except (TypeError, ValueError) as e:
        raise EntitlementError(f"BAD_FORMAT bad clock fields: {e}") from e
    if expires > 0 and now > expires:  # expires_epoch == 0 → never expires (the free core)
        if now <= expires + grace_days * 86400.0:
            out = GraceEntitlement(claims)
            out["grace"] = True
            out["grace_ends_epoch"] = expires + grace_days * 86400.0
            return out
        raise EntitlementError("EXPIRED")
    return claims


def free_core_claims(holder: str, issued_at: Optional[float] = None) -> Dict[str, Any]:
    """The always-free core claim — the MIT promise as an entitlement: the core
    never gates, so this token exists to be *displayed*, not enforced."""
    return {
        "plan": "core-free",
        "holder": holder,
        "issued_at": issued_at or time.time(),
        "expires_epoch": 0,          # never expires
        "grace_days": 0,
        "caps": {"essentials": "unlimited", "solo_local": "unlimited"},
    }


def founding_claims(holder: str, grant_face_usd: float, days: int = 3650,
                    issued_at: Optional[float] = None) -> Dict[str, Any]:
    """Founding Member: lifetime membership (perks), credits are a separate grant."""
    now = issued_at or time.time()
    return {
        "plan": "founding",
        "holder": holder,
        "issued_at": now,
        "expires_epoch": now + days * 86400.0,
        "grace_days": 30,
        "caps": {"perks": "lifetime", "token_grant_face_usd": grant_face_usd},
    }
