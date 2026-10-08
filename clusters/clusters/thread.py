"""Thread state without deleting the transcript.

A thread is active, snoozed until a time the operator set, or settled.
Settling does not close the session.
"""

from __future__ import annotations

from clusters.refuse import Refuse
from clusters.store import Store

_STATES = ("active", "snoozed", "settled")


def set_thread(store: Store, *, session_id: str, state: str, until: float = 0) -> dict:
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    if state not in _STATES:
        raise Refuse("STATE")
    _check_until(state, until)
    thread_id = f"thread-{session_id}"
    # Settling does not close the session.
    store.append(
        "thread",
        {
            "id": thread_id,
            "op": "set",
            "session_id": session_id,
            "state": state,
            "until": until,
            "closed": False,
        },
    )
    return dict(store.view("thread")[thread_id])


def get_thread(store: Store, session_id: str) -> dict:
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    row = store.view("thread").get(f"thread-{session_id}")
    if row is None:
        raise Refuse("THREAD", "missing")
    return dict(row)


def _check_until(state: str, until: object) -> None:
    if state == "snoozed":
        if isinstance(until, bool) or not isinstance(until, (int, float)) or not until > 0:
            raise Refuse("UNTIL")
        return
    if until != 0:
        raise Refuse("UNTIL")
