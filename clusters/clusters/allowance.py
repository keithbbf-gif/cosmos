"""One admit check over the spend cap and the quota window.

This reads the two projections. It does not append a spend row or a quota row,
and it is not a ledger. A missing quota window is not a pause. A missing
budget is the spend module's Refuse("PROVIDER"). An UNMEASURED figure on
either projection pauses.
"""

from __future__ import annotations

from clusters import quota, spend
from clusters.refuse import Refuse
from clusters.store import Store


def admit(
    store: Store,
    *,
    provider: str,
    usd: float = 0,
    tokens: int = 0,
    now: float,
) -> dict:
    cap = spend.check(store, provider=provider, usd=usd, tokens=tokens)
    window = _window(store, provider, now)
    if cap.get("decision") != "allow":
        return _held(cap["decision"], cap["code"], "spend", cap["code"], window["code"])
    if window.get("decision") != "allow":
        return _held("pause", window["code"], "quota", cap["code"], window["code"])
    return _held("allow", "OK", "", cap["code"], window["code"])


def _window(store: Store, provider: str, now: float) -> dict:
    try:
        return quota.prorata(store, provider=provider, now=now)
    except Refuse as exc:
        if exc.code != "PROVIDER":
            raise
        return {"decision": "allow", "code": "NO_WINDOW"}


def _held(decision: str, code: str, gate: str, spend_code: str, quota_code: str) -> dict:
    return {
        "decision": decision,
        "code": code,
        "gate": gate,
        "spend": spend_code,
        "quota": quota_code,
    }
