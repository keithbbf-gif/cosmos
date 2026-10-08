"""Provider conversation id, separate from the resume flag.

Antigravity uses a conversation id. Kimi uses a session id under a project
directory. Native Windows and WSL do not share a home. Cursor resume stays
false until loadSession is advertised. This stores the id. It does not resume.
"""

from __future__ import annotations

from clusters.refuse import Refuse
from clusters.store import Store

_HOMES = ("native", "wsl")
_ID_LIMIT = 120


def set_door_id(
    store: Store,
    *,
    session_id: str,
    conversation_id: str,
    home: str,
) -> dict:
    """Append the provider id and return the view. This does not call the harness."""
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    kept = _conversation(conversation_id)
    if home not in _HOMES:
        raise Refuse("HOME")
    row_id = f"doorid-{session_id}"
    # Record only. This does not resume.
    store.append(
        "door_id",
        {
            "id": row_id,
            "session_id": session_id,
            "conversation_id": kept,
            "home": home,
            "resume_claimed": False,
        },
    )
    return _public(store.view("door_id")[row_id])


def get_door_id(store: Store, session_id: str) -> dict:
    """Return the stored id. A folded resume_claimed of true is still false."""
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION")
    row = store.view("door_id").get(f"doorid-{session_id}")
    if row is None:
        raise Refuse("DOOR_ID", "missing")
    return _public(row)


def _conversation(text: object) -> str:
    """One line, 1..120 characters. Anything else is DOOR_ID."""
    if (
        not isinstance(text, str)
        or "\n" in text
        or "\r" in text
        or not 1 <= len(text) <= _ID_LIMIT
    ):
        raise Refuse("DOOR_ID")
    return text


def _public(row: dict) -> dict:
    """Force resume_claimed false on read. This does not resume."""
    view = dict(row)
    view["resume_claimed"] = False
    return view
