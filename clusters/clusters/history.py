"""Searchable history, resume pointer, claimed false.

Unknown session, kind, role, or empty body is Refuse. resume is only the catalog flag.
"""

from __future__ import annotations

from clusters.models import DOORS, MESSAGE_KINDS
from clusters.refuse import Refuse
from clusters.store import Store, new_id

MESSAGE_ROLES = ("user", "agent", "coordinator")


def add_message(
    store: Store,
    *,
    session_id: str,
    role: str,
    kind: str,
    body: str,
    resume_of: str = "",
    sender_id: str = "",
) -> dict:
    """Append one message or Refuse a bad session, kind, role, or empty body."""
    session = store.view("session").get(session_id)
    if session is None:
        raise Refuse("SESSION", session_id)
    if kind not in MESSAGE_KINDS:
        raise Refuse("KIND", kind)
    if role not in MESSAGE_ROLES:
        raise Refuse("ROLE", role)
    if not isinstance(body, str) or not body.strip():
        raise Refuse("MESSAGE", "empty")
    message_id = new_id("msg")
    record = {
        "id": message_id,
        "op": "add",
        "session_id": session_id,
        "project_id": session["project_id"],
        "role": role,
        "kind": kind,
        "body": body,
        "resume_of": resume_of,
        "sender_id": sender_id,
    }
    store.append("message", record)
    return dict(store.view("message")[message_id])


def search(store: Store, query: str, *, project_id: str = "") -> list[dict]:
    """Searchable history over message bodies. A blank query returns nothing."""
    if not isinstance(query, str) or not query.strip():
        return []
    needle = query.lower()
    rows = []
    for row in store.view("message").values():
        text = str(row.get("body") or "")
        if needle not in text.lower():
            continue
        if project_id and row.get("project_id") != project_id:
            continue
        rows.append(dict(row))
    rows.sort(key=lambda row: int(row.get("_seq") or 0), reverse=True)
    return rows


def resume_pointer(store: Store, session_id: str) -> dict:
    """Resume pointer. Missing session is Refuse. resume is only the catalog flag; claimed stays false."""
    session = store.view("session").get(session_id)
    if session is None:
        raise Refuse("SESSION", session_id)
    messages = [
        row for row in store.view("message").values() if row.get("session_id") == session_id
    ]
    messages.sort(key=lambda row: int(row.get("_seq") or 0))
    chain = [session_id] + [row["id"] for row in messages]
    return {
        "session_id": session_id,
        "resume": bool(DOORS[session["door"]]["resume"]),
        "chain": chain,
        "claimed": False,
    }
