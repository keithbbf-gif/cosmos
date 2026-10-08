"""Projection of an operator meter reading. This is not a ledger.

Guides say an empty usage view is not unlimited, a logged-out local
server must not be stored as stopped, and OpenCode can be BYOK or Zen.
Zen with auto-reload off is a hard stop. Cursor has two pools. This
stores the operator's reading. It does not reduce spend and it does
not change quota rows.
"""

from __future__ import annotations

from clusters.refuse import Refuse
from clusters.store import Store
from clusters.verify import judge

READINGS = ("empty", "capped", "credits", "logged-out")
POOLS = ("byok", "zen", "membership", "cursor-models", "other-models", "window")


def set_meter(
    store: Store,
    *,
    provider: str,
    reading: str,
    pool: str,
    auto_reload: bool = False,
    source: str = "",
    observed: str = "",
) -> dict:
    """Store one operator reading. Refuse PROVIDER, READING, POOL, or RELOAD.

    Unlimited is always false. Stopped is always false. Nothing is
    appended to spend or quota.
    """
    text = _provider(provider)
    named = _reading(reading)
    which = _pool(pool)
    reload = _reload(auto_reload)
    evidence = _evidence(source, observed)
    hard_stop = which == "zen" and reload is False
    row = store.append(
        "meter",
        {
            "id": f"meter-{text.casefold()}-{which}",
            "provider": text,
            "reading": named,
            "pool": which,
            "auto_reload": reload,
            "unlimited": False,
            "stopped": False,
            "hard_stop": hard_stop,
        },
        evidence,
        claim="meter",
    )
    verdict = str(row["verdict"])
    counted = verdict == "VERIFIED" and named not in ("empty", "logged-out")
    return {
        "provider": text,
        "reading": named,
        "pool": which,
        "verdict": verdict,
        "counted": counted,
        "unlimited": False,
        "stopped": False,
        "hard_stop": hard_stop,
    }


def meter_gate(store: Store, *, provider: str, pool: str) -> dict:
    """Pause on the last fold row unless it is a verified countable reading.

    A missing row is Refuse("METER", "missing"). Empty and logged-out
    stay UNMEASURED. Zen with auto-reload off is HARD_STOP. Nothing is
    subtracted from spend.
    """
    text = _provider(provider)
    which = _pool(pool)
    wanted = f"meter-{text.casefold()}-{which}"
    found: dict | None = None
    for row in store.fold("meter"):
        if str(row["body"].get("id") or "") == wanted:
            found = row
    if found is None:
        raise Refuse("METER", "missing")
    body = found["body"]
    reading = body.get("reading")
    if found["verdict"] != "VERIFIED" or reading in ("empty", "logged-out"):
        return {"decision": "pause", "code": "UNMEASURED"}
    if body.get("hard_stop") is True:
        return {"decision": "pause", "code": "HARD_STOP"}
    return {"decision": "allow", "code": "OK"}


def _evidence(source: object, observed: object) -> dict[str, str] | None:
    # Evidence rule: judge("meter") runs only when source and observed are
    # both non-empty strings. Otherwise evidence is None. Counted is true
    # only when that verdict is VERIFIED and the reading is not empty or
    # logged-out. An empty reading is not unlimited.
    if isinstance(source, str) and isinstance(observed, str) and source and observed:
        evidence = {"source": source, "observed": observed}
        judge("meter", evidence)
        return evidence
    return None


def _provider(provider: object) -> str:
    if not isinstance(provider, str):
        raise Refuse("PROVIDER", "empty")
    if "\n" in provider or "\r" in provider or not provider.strip():
        raise Refuse("PROVIDER", "empty")
    return provider.strip()


def _reading(reading: object) -> str:
    if not isinstance(reading, str) or reading not in READINGS:
        raise Refuse("READING")
    return reading


def _pool(pool: object) -> str:
    if not isinstance(pool, str) or pool not in POOLS:
        raise Refuse("POOL")
    return pool


def _reload(auto_reload: object) -> bool:
    if not isinstance(auto_reload, bool):
        raise Refuse("RELOAD")
    return auto_reload
