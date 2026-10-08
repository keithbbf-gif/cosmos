"""Spend projection: daily cap, smart pace, one 5 percent bump, unmeasured pauses.

This is not a second ledger. Only VERIFIED observations reduce the cap.
UNMEASURED spend stays logged and pauses new work.
"""

from __future__ import annotations

from clusters.models import BUDGET_MODES, ON_LIMIT
from clusters.refuse import Refuse
from clusters.store import Store, new_id

BUMP_FRACTION = 0.05


def set_budget(
    store: Store,
    *,
    provider: str,
    daily_cap_usd: float,
    daily_cap_tokens: int = 0,
    mode: str = "cap",
    on_limit: str = "pause",
    window_days: int = 1,
    day_index: int = 0,
) -> dict:
    """Set the daily cap or smart pace. Refuse MODE, LIMIT, CAP, WINDOW, or PROVIDER. Only VERIFIED observations reduce the cap."""
    text = _provider(provider)
    if mode not in BUDGET_MODES:
        raise Refuse("MODE", mode)
    if on_limit not in ON_LIMIT:
        raise Refuse("LIMIT", on_limit)
    window, day = _window(window_days, day_index)
    cap_usd = _usd(daily_cap_usd)
    cap_tokens = _tokens(daily_cap_tokens)
    if cap_usd < 0 or cap_tokens < 0:
        raise Refuse("CAP", "negative")
    body = {
        "id": "budget-" + text.casefold(),
        "provider": text,
        "daily_cap_usd": cap_usd,
        "daily_cap_tokens": cap_tokens,
        "mode": mode,
        "on_limit": on_limit,
        "window_days": window,
        "day_index": day,
    }
    store.append("budget", body)
    return report_one(store, text)


def observe(
    store: Store,
    *,
    provider: str,
    usd: float,
    tokens: int = 0,
    source: str = "",
    observed: str = "",
    day_index: int = 0,
) -> dict:
    """Log spend. Only VERIFIED observations reduce the cap; otherwise the verdict is UNMEASURED."""
    text = _provider(provider)
    amount = _usd(usd)
    count = _tokens(tokens)
    day = _day(day_index)
    if isinstance(source, str) and isinstance(observed, str) and source.strip() and observed.strip():
        evidence = {"source": source, "observed": observed}
    else:
        evidence = None
    body = {
        "id": new_id("spd"),
        "provider": text,
        "usd": amount,
        "tokens": count,
        "day_index": day,
    }
    row = store.append("spend", body, evidence, claim="spend")
    verdict = row["verdict"]
    return {"verdict": verdict, "counted": verdict == "VERIFIED"}


def bump_today(store: Store, *, provider: str) -> dict:
    """Apply one 5 percent bump. Refuse ALREADY_BUMPED or PROVIDER. Only VERIFIED observations reduce the cap."""
    budget = _budget(store, provider)
    text = str(budget["provider"])
    day = int(budget["day_index"])
    if _has_bump(store, text, day):
        raise Refuse("ALREADY_BUMPED", text)
    body = {
        "id": f"bump-{text}-{day}",
        "provider": text,
        "day_index": day,
        "fraction": BUMP_FRACTION,
    }
    store.append("bump", body)
    return {"bumped": True, "fraction": BUMP_FRACTION}


def check(store: Store, *, provider: str, usd: float = 0, tokens: int = 0) -> dict:
    """Decide OK, LIMIT, or pause/UNMEASURED against the daily cap or smart pace. Only VERIFIED observations reduce the cap."""
    budget = _budget(store, provider)
    provider_name = str(budget["provider"])
    day = int(budget["day_index"])
    measured = _measured(store, provider_name, day)
    allowance_usd, allowance_tokens = _allowance(budget, measured, _has_bump(store, provider_name, day))
    request_usd = _usd(usd)
    request_tokens = _tokens(tokens)
    if measured["unmeasured"]:
        return {
            "decision": "pause",
            "code": "UNMEASURED",
            "spent_usd": measured["spent_usd"],
            "allowance_usd": allowance_usd,
        }
    # Cap is daily. Pace slices the window, then tests today's measured
    # spend plus this not-yet-observed call against that slice.
    used_usd = measured["today_usd"] + request_usd
    used_tokens = measured["today_tokens"] + request_tokens
    over = _over(used_usd, allowance_usd)
    if int(budget["daily_cap_tokens"]) > 0 and _over(used_tokens, allowance_tokens):
        over = True
    if over:
        return {
            "decision": budget["on_limit"],
            "code": "LIMIT",
            "spent_usd": measured["spent_usd"],
            "allowance_usd": allowance_usd,
            "on_limit": budget["on_limit"],
        }
    return {
        "decision": "allow",
        "code": "OK",
        "spent_usd": measured["spent_usd"],
        "allowance_usd": allowance_usd,
        "on_limit": budget["on_limit"],
    }


def report(store: Store) -> list[dict]:
    """Project each daily cap. Only VERIFIED observations reduce the cap. Unmeasured pauses stay flagged."""
    return [_public(store, budget) for budget in store.view("budget").values()]


def report_one(store: Store, provider: str) -> dict:
    """Project one provider or refuse PROVIDER. Only VERIFIED observations reduce the cap."""
    text = _provider(provider)
    folded = text.casefold()
    for row in report(store):
        if str(row["provider"]).strip().casefold() == folded:
            return row
    raise Refuse("PROVIDER", text)


def _public(store: Store, budget: dict) -> dict:
    provider = str(budget["provider"])
    day = int(budget["day_index"])
    measured = _measured(store, provider, day)
    allowance_usd, _allowance_tokens = _allowance(budget, measured, _has_bump(store, provider, day))
    return {
        "provider": provider,
        "spent_usd": measured["spent_usd"],
        "allowance_usd": allowance_usd,
        "mode": budget["mode"],
        "on_limit": budget["on_limit"],
        "unmeasured": measured["unmeasured"],
    }


def _allowance(budget: dict, measured: dict, bumped: bool) -> tuple[float, float]:
    cap_usd = float(budget["daily_cap_usd"])
    cap_tokens = float(budget["daily_cap_tokens"])
    if budget["mode"] == "smart_pace":
        days_left = max(1, int(budget["window_days"]) - int(budget["day_index"]))
        # Remaining is the window cap minus every verified dollar.
        allowance_usd = (cap_usd - measured["spent_usd"]) / days_left
        allowance_tokens = (cap_tokens - measured["spent_tokens"]) / days_left
    else:
        allowance_usd = cap_usd
        allowance_tokens = cap_tokens
    if bumped:
        allowance_usd += BUMP_FRACTION * cap_usd
        allowance_tokens += BUMP_FRACTION * cap_tokens
    return allowance_usd, allowance_tokens


def _measured(store: Store, provider: str, day_index: int) -> dict:
    folded = provider.strip().casefold()
    spent_usd = 0.0
    spent_tokens = 0
    today_usd = 0.0
    today_tokens = 0
    unmeasured = False
    for row in store.fold("spend"):
        body = row["body"]
        if str(body.get("provider") or "").strip().casefold() != folded:
            continue
        if row["verdict"] == "UNMEASURED":
            unmeasured = True
            continue
        if row["verdict"] != "VERIFIED":
            continue
        amount = float(body.get("usd") or 0)
        count = int(body.get("tokens") or 0)
        spent_usd += amount
        spent_tokens += count
        if int(body.get("day_index") or 0) == int(day_index):
            today_usd += amount
            today_tokens += count
    return {
        "spent_usd": spent_usd,
        "spent_tokens": spent_tokens,
        "today_usd": today_usd,
        "today_tokens": today_tokens,
        "unmeasured": unmeasured,
    }


def _budget(store: Store, provider: str) -> dict:
    text = _provider(provider)
    row = store.view("budget").get("budget-" + text.casefold())
    if row is None:
        raise Refuse("PROVIDER", text)
    return row


def _has_bump(store: Store, provider: str, day_index: int) -> bool:
    folded = provider.strip().casefold()
    for row in store.fold("bump"):
        body = row["body"]
        name = str(body.get("provider") or "").strip().casefold()
        if name == folded and int(body.get("day_index")) == int(day_index):
            return True
    return False


def _provider(provider: str) -> str:
    if not isinstance(provider, str) or not provider.strip():
        raise Refuse("PROVIDER", "empty")
    return provider.strip()


def _window(window_days: int, day_index: int) -> tuple[int, int]:
    if isinstance(window_days, bool) or not isinstance(window_days, int) or window_days < 1:
        raise Refuse("WINDOW", "window_days")
    day = _day(day_index)
    if day >= window_days:
        raise Refuse("WINDOW", "day_index")
    return window_days, day


def _day(day_index: int) -> int:
    if isinstance(day_index, bool) or not isinstance(day_index, int) or day_index < 0:
        raise Refuse("WINDOW", "day_index")
    return day_index


def _usd(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Refuse("CAP", "usd")
    return float(value)


def _tokens(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("CAP", "tokens")
    return value


def _over(used: float, allowance: float) -> bool:
    return used > allowance + 1e-9
