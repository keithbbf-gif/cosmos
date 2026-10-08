"""Projection of a provider quota window. This is not a second ledger.

This is a projection. A figure without source and observed is UNMEASURED
and pauses new work. It does not reduce the remaining allowance.
"""

from __future__ import annotations

from clusters.refuse import Refuse
from clusters.store import Store, new_id


def set_window(
    store: Store,
    *,
    provider: str,
    limit_usd: float,
    period_seconds: int,
    resets_at: float,
    source: str,
    observed: str,
) -> dict[str, str | bool]:
    text = _provider(provider)
    limit = _non_negative(limit_usd, "WINDOW")
    period = _period(period_seconds)
    resets = _resets(resets_at)
    body = {
        "id": "quota-" + text.casefold(),
        "op": "set",
        "provider": text,
        "limit_usd": limit,
        "period_seconds": period,
        "resets_at": resets,
    }
    row = store.append(
        "quota",
        body,
        {"source": source, "observed": observed},
        claim="quota",
    )
    verdict = str(row["verdict"])
    return {"provider": text, "verdict": verdict, "counted": verdict == "VERIFIED"}


def mark_used(
    store: Store,
    *,
    provider: str,
    used_usd: float,
    source: str,
    observed: str,
) -> dict[str, str | bool]:
    text = _provider(provider)
    used = _non_negative(used_usd, "QUOTA")
    body = {"id": new_id("qus"), "provider": text, "used_usd": used}
    row = store.append("quota_used", body, _stamps(source, observed), claim="quota-used")
    verdict = str(row["verdict"])
    return {"verdict": verdict, "counted": verdict == "VERIFIED"}


def prorata(store: Store, *, provider: str, now: float) -> dict[str, str | float | None]:
    window = _latest_quota(store, provider)
    provider_name = str(window["body"].get("provider") or "")
    # An unmeasured figure stays in the log and does not change the allowance.
    if window["verdict"] != "VERIFIED" or _usage_blocked(store, provider_name):
        return {"decision": "pause", "code": "UNMEASURED", "ahead": None}
    body = window["body"]
    limit = float(body["limit_usd"])
    period = int(body["period_seconds"])
    resets = float(body["resets_at"])
    used = _latest_used(store, provider_name)
    used_fraction = 0.0 if limit == 0 else used / limit
    time_fraction = _time_fraction(_clock(now), resets, period)
    ahead = used_fraction - time_fraction
    if used < limit:
        decision, code = "allow", "OK"
    else:
        decision, code = "pause", "LIMIT"
    return {
        "decision": decision,
        "code": code,
        "used_fraction": used_fraction,
        "time_fraction": time_fraction,
        "ahead": ahead,
        "resets_at": resets,
    }


def _latest_quota(store: Store, provider: str) -> dict:
    text = _provider(provider)
    folded = text.casefold()
    found: dict | None = None
    for row in store.fold("quota"):
        name = str(row["body"].get("provider") or "").strip().casefold()
        if name == folded:
            found = row
    if found is None:
        raise Refuse("PROVIDER", text)
    return found


def _usage_blocked(store: Store, provider: str) -> bool:
    folded = provider.strip().casefold()
    verified = False
    for row in store.fold("quota_used"):
        name = str(row["body"].get("provider") or "").strip().casefold()
        if name != folded:
            continue
        if row["verdict"] == "UNMEASURED":
            return True
        if row["verdict"] == "VERIFIED":
            verified = True
    return not verified


def _latest_used(store: Store, provider: str) -> float:
    folded = provider.strip().casefold()
    used = 0.0
    for row in store.fold("quota_used"):
        body = row["body"]
        name = str(body.get("provider") or "").strip().casefold()
        if name == folded and row["verdict"] == "VERIFIED":
            used = float(body["used_usd"])
    return used


def _time_fraction(now: float, resets_at: float, period_seconds: int) -> float:
    if period_seconds < 1:
        raise Refuse("WINDOW", "period_seconds")
    start = resets_at - period_seconds
    fraction = (now - start) / period_seconds
    if fraction < 0:
        return 0.0
    if fraction > 1:
        return 1.0
    return fraction


def _provider(provider: str) -> str:
    if not isinstance(provider, str) or not provider.strip():
        raise Refuse("PROVIDER", "empty")
    return provider.strip()


def _period(period_seconds: int) -> int:
    if isinstance(period_seconds, bool) or not isinstance(period_seconds, int) or period_seconds < 1:
        raise Refuse("WINDOW", "period_seconds")
    return period_seconds


def _resets(resets_at: float) -> float:
    if isinstance(resets_at, bool) or not isinstance(resets_at, (int, float)):
        raise Refuse("WINDOW", "resets_at")
    stamp = float(resets_at)
    if not stamp > 0:
        raise Refuse("WINDOW", "resets_at")
    return stamp


def _non_negative(value: float, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Refuse(code, "usd")
    amount = float(value)
    if amount < 0:
        raise Refuse(code, "usd")
    return amount


def _clock(now: float) -> float:
    if isinstance(now, bool) or not isinstance(now, (int, float)):
        raise Refuse("WINDOW", "now")
    return float(now)


def _stamps(source: str, observed: str) -> dict[str, str] | None:
    if isinstance(source, str) and isinstance(observed, str) and source.strip() and observed.strip():
        return {"source": source, "observed": observed}
    return None
