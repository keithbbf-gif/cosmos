"""Session status moves its kanban card and emits a note.

The move to in_testing is not a completion. Completion stays a separate review.
"""

from __future__ import annotations

from clusters.board import move_task
from clusters.catalog import emit
from clusters.refuse import Refuse
from clusters.sessions import get_session, set_status
from clusters.store import Store

_NOTE_STATUSES = ("finished", "failed", "needs_input")


def on_status(
    store: Store,
    session_id: str,
    status: str,
    *,
    evidence: dict | None = None,
    detail: str = "",
) -> dict:
    previous = get_session(store, session_id).get("verified_status")
    set_status(store, session_id, status, evidence=evidence)
    verified = get_session(store, session_id).get("verified_status")
    moved: list[str] = []
    held: list[str] = []
    if verified == "finished":
        tasks = [
            row
            for row in store.view("task").values()
            if row.get("session_id") == session_id and row.get("column") == "in_progress"
        ]
        tasks.sort(key=lambda row: str(row.get("id") or ""))
        for task in tasks:
            task_id = str(task["id"])
            try:
                move_task(store, task_id, "in_testing", evidence=evidence)
            except Refuse:
                held.append(task_id)
            else:
                moved.append(task_id)
    noted = False
    if verified in _NOTE_STATUSES and verified != previous:
        emit(
            store,
            session_id=session_id,
            kind=str(verified),
            detail=detail if detail else status,
        )
        noted = True
    return {
        "session_id": session_id,
        "verified_status": verified,
        "moved": moved,
        "held": held,
        "noted": noted,
    }
