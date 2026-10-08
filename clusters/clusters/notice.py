"""Attention records.

A seat is waiting because it needs approval, failed, asked a question, or
claimed it finished. The record is that reason and the store's at time.
This does not notify, send a push, or answer the agent.
"""

from __future__ import annotations

from clusters.refuse import SECRET_KEYS, Refuse
from clusters.store import Store, new_id

REASONS = ("approval", "failed", "question", "finished")


def note_attention(store: Store, *, session_id: str, reason: str) -> dict:
    """Append one attention row. The session stays as it is, and nothing is sent."""
    if session_id not in store.view("session"):
        raise Refuse("SESSION", session_id)
    if not isinstance(reason, str) or reason not in REASONS:
        raise Refuse("REASON", str(reason))
    attention_id = new_id("att")
    # The store stamps at. A second clock is not written, and this does not notify.
    store.append(
        "attention",
        {"id": attention_id, "session_id": session_id, "reason": reason},
    )
    return {"session_id": session_id, "reason": reason, "id": attention_id}


def list_attention(store: Store, session_id: str = "") -> list[dict]:
    """Rows for one session, or every session when session_id is empty."""
    clocks = _clocks(store)
    rows: list[dict] = []
    for row in store.view("attention").values():
        if session_id and row.get("session_id") != session_id:
            continue
        public = _without_secrets(dict(row))
        public["at"] = clocks.get(str(row.get("id") or ""))
        rows.append(public)
    rows.sort(key=lambda item: str(item.get("id") or ""))
    return rows


def _clocks(store: Store) -> dict[str, float]:
    found: dict[str, float] = {}
    for event in store.fold("attention"):
        body = event.get("body") or {}
        item_id = str(body.get("id") or "")
        if item_id:
            found[item_id] = event["at"]
    return found


def _without_secrets(row: dict) -> dict:
    """Drop secret keys. Attention stays a reason and the store clock."""
    clean: dict = {}
    for key, value in row.items():
        if str(key).lower() in SECRET_KEYS:
            continue
        clean[key] = _without_secrets(value) if isinstance(value, dict) else value
    return clean
