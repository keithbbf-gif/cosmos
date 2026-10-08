"""Review column for one session.

Paths on a session's review stay unseen until the operator marks them seen.
The card cannot be treated as accepted until every path is seen. accepted
is always false here. This does not move a kanban card. Accepting the
record does not commit.
"""

from __future__ import annotations

import hashlib

from clusters.refuse import Refuse, guard_path
from clusters.store import Store


def mark_seen(
    store: Store,
    *,
    session_id: str,
    path: str,
    seen: bool = True,
) -> dict:
    """Append one seen row for a path. This does not commit."""
    if session_id not in store.view("session"):
        raise Refuse("SESSION", session_id)
    kept = guard_path(path)
    if not isinstance(seen, bool):
        raise Refuse("SEEN")
    row_id = f"seen-{session_id}-{_digest(kept)}"
    # Last write wins for this path. Marking it seen does not accept or commit.
    store.append(
        "seen",
        {
            "id": row_id,
            "session_id": session_id,
            "path": kept,
            "seen": seen,
            "accepted": False,
        },
    )
    return dict(store.view("seen")[row_id])


def review_paths(store: Store, session_id: str) -> dict:
    """Count paths whose seen is not true. This does not commit."""
    if session_id not in store.view("session"):
        raise Refuse("SESSION", session_id)
    open_count = sum(
        1
        for row in store.view("seen").values()
        if row.get("session_id") == session_id and row.get("seen") is not True
    )
    # accepted stays false. This does not move a kanban card and does not commit.
    return {"session_id": session_id, "open": open_count, "accepted": False}


def _digest(path: str) -> str:
    return hashlib.sha256(path.encode()).hexdigest()[:12]
