"""History bookmarks.

A bookmark names a session and an optional message id. Refusals are SESSION
(no such session), MESSAGE (named message missing or on another session),
NOTE (not one line of at most 240 characters), and BOOKMARK (hide of an
unknown id). The message body is not copied. Hide sets removed; it does not
delete the jsonl row.
"""

from __future__ import annotations

from clusters.refuse import Refuse
from clusters.store import Store, new_id

_NOTE_LIMIT = 240


def add_bookmark(
    store: Store,
    *,
    session_id: str,
    message_id: str = "",
    note: str = "",
) -> dict:
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    if message_id:
        message = store.view("message").get(message_id)
        if message is None or message.get("session_id") != session_id:
            raise Refuse("MESSAGE", message_id)
    if not isinstance(note, str) or len(note) > _NOTE_LIMIT or "\n" in note or "\r" in note:
        raise Refuse("NOTE")
    bookmark_id = new_id("bmk")
    # Pointer only. The message body stays on the message row.
    record = {
        "id": bookmark_id,
        "session_id": session_id,
        "message_id": message_id,
        "note": note,
        "removed": False,
    }
    store.append("bookmark", record)
    return dict(store.view("bookmark")[bookmark_id])


def hide_bookmark(store: Store, bookmark_id: str) -> dict:
    current = store.view("bookmark").get(bookmark_id)
    if current is None:
        raise Refuse("BOOKMARK", bookmark_id)
    # Flag, not a deletion. The same id is appended; last write wins.
    store.append(
        "bookmark",
        {
            "id": bookmark_id,
            "session_id": current.get("session_id", ""),
            "message_id": current.get("message_id", ""),
            "note": current.get("note", ""),
            "removed": True,
        },
    )
    return dict(store.view("bookmark")[bookmark_id])


def list_bookmarks(store: Store, session_id: str = "") -> list[dict]:
    rows = []
    for row in store.view("bookmark").values():
        if row.get("removed"):
            continue
        if session_id and row.get("session_id") != session_id:
            continue
        rows.append(dict(row))
    rows.sort(key=lambda row: row["id"])
    return rows
