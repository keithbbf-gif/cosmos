"""Operator CLI name and model for a seat.

similar.md item 8. The chosen door and model are data on the seat.
This does not launch. It does not install a CLI and it does not start grok.exe.
"""

from __future__ import annotations

from clusters.models import DOORS
from clusters.refuse import Refuse
from clusters.store import Store


def bind_seat(store: Store, *, session_id: str, door: str, model: str) -> dict:
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    if door not in DOORS:
        raise Refuse("UNKNOWN_DOOR", door)
    kept = _model(model)
    row_id = f"bind-{session_id}"
    store.append(
        "binding",
        {
            "id": row_id,
            "session_id": session_id,
            "door": door,
            "model": kept,
            "started": False,
            "installed": False,
            "executed": False,
        },
    )
    return dict(store.view("binding")[row_id])


def get_binding(store: Store, session_id: str) -> dict:
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION")
    row = store.view("binding").get(f"bind-{session_id}")
    if row is None:
        raise Refuse("BINDING", "missing")
    return dict(row)


def _model(model: object) -> str:
    if not isinstance(model, str) or "\n" in model or "\r" in model or not 1 <= len(model) <= 80:
        raise Refuse("MODEL")
    return model
