"""Plan a HERO seat through g47. Do not start grok.exe.

`seat` does not start a process. `live_call` is one observation, and the
public result keeps seated false. A missing harness is UNMEASURED.
"""

from __future__ import annotations

import sys
from pathlib import Path

from clusters.models import DOORS, HEROES
from clusters.refuse import Refuse, guard_path

DEFAULT_HARNESS = Path(r"V:\streams\cosmos_code\harness\G47")


def plan_seat(
    hero: str,
    task: str,
    where: str,
    via: str = "cosmos-code",
    *,
    execute: bool = False,
    harness_root: str | Path | None = None,
) -> dict:
    """Return a plan or an observation. Never a claim that the agent is seated."""
    guard_path(where)
    if via not in ("native", "cosmos-code"):
        raise Refuse("UNKNOWN_VIA", via)
    if hero == "grok" and via == "native":
        raise Refuse("GROK_EXE", "grok.exe is not a worker. Use via=cosmos-code.")
    if not str(task).strip():
        raise Refuse("PACK_INCOMPLETE", "task")
    if hero not in HEROES:
        return {
            "seated": False,
            "executable": False,
            "verdict": "UNMEASURED",
            "why": "UNKNOWN_HERO",
            "hero": hero,
            "via": via,
            "started": False,
        }
    loaded = _load(harness_root)
    if loaded is None:
        return {
            "seated": False,
            "executable": False,
            "verdict": "UNMEASURED",
            "why": "HARNESS_ABSENT",
            "hero": hero,
            "via": via,
            "started": False,
        }
    seat, live_call = loaded
    try:
        built = seat(hero, via=via, task=task, where=where)
    except Exception as exc:  # noqa: BLE001 — a foreign harness error is a refusal, not a seat
        reason = getattr(exc, "reason", "REFUSED")
        detail = getattr(exc, "detail", str(exc))
        return {
            "seated": False,
            "executable": False,
            "verdict": "REFUSED",
            "why": str(reason),
            "detail": str(detail),
            "hero": hero,
            "via": via,
            "started": False,
        }
    public = built.to_public()
    public["seated"] = False
    public["verdict"] = "RECORDED"
    public["why"] = "plan only"
    public["started"] = False
    if not execute:
        return public
    if public.get("door") == "grok" or not public.get("executable"):
        raise Refuse("NOT_EXECUTABLE", str(public.get("door")))
    door = DOORS.get(str(public.get("door")))
    if door is not None and not door.get("executable"):
        raise Refuse("NOT_EXECUTABLE", door["id"])
    observed = live_call(hero, via=via, task=task, where=where)
    observed["seated"] = False
    observed["started"] = True
    observed["verdict"] = "RECORDED"
    observed["why"] = "live_call is an observation"
    return observed


def _load(harness_root: str | Path | None):
    root = Path(harness_root) if harness_root else DEFAULT_HARNESS
    if not root.is_dir():
        return None
    text = str(root)
    if text not in sys.path:
        sys.path.insert(0, text)
    try:
        from g47.seat import live_call, seat  # type: ignore[import-not-found]
    except ImportError:
        return None
    return seat, live_call
