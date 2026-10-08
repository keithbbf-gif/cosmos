"""CodeAgentSwarm coordinator messages are marked Follow-up or Correction.
Small work stays on the coordinator and does not open a worker.
A global coordinator may hand a goal to the project's coordinator instead of opening a worker itself.

Closing and planning stay in clusters.coordinators. This module does not replace them.
"""

from __future__ import annotations

from clusters import coordinators, history, sessions
from clusters.refuse import Refuse
from clusters.store import Store

_COORDINATOR_ROLES = ("coordinator", "global_coordinator")
_WORKER_KINDS = ("followup", "correction")


def send_worker(
    store: Store,
    *,
    coordinator_id: str,
    worker_id: str,
    text: str,
    kind: str,
) -> dict:
    if kind not in _WORKER_KINDS:
        raise Refuse("KIND", kind if isinstance(kind, str) else "")
    body = _text(text)
    worker = sessions.get_session(store, worker_id)
    if worker.get("parent_id") != coordinator_id:
        raise Refuse("OWNER", worker_id)
    history.add_message(
        store,
        session_id=worker_id,
        role="coordinator",
        kind=kind,
        body=body,
    )
    sessions.queue_message(store, worker_id, 1)
    return {"kind": kind, "worker_id": worker_id, "queued": True}


def keep_small(store: Store, *, coordinator_id: str, text: str) -> dict:
    _need_role(store, coordinator_id, _COORDINATOR_ROLES)
    body = _text(text)
    history.add_message(
        store,
        session_id=coordinator_id,
        role="coordinator",
        kind="system",
        body=body,
    )
    return {"delegated": False, "opened": 0}


def delegate_project(
    store: Store,
    *,
    global_id: str,
    project_id: str,
    text: str,
    door: str,
    hero: str,
    model: str,
) -> dict:
    _need_role(store, global_id, ("global_coordinator",))
    body = _text(text)
    current = _project_coordinator(store, project_id)
    reused = current is not None
    if current is None:
        current = coordinators.open_coordinator(
            store,
            scope="project",
            project_id=project_id,
            hero=hero,
            door=door,
            model=model,
        )
    coordinator_id = str(current["id"])
    coordinators.submit_goal(store, coordinator_id, body)
    return {"delegated": True, "coordinator_id": coordinator_id, "reused": reused}


def _text(text: object) -> str:
    if not isinstance(text, str) or not text.strip():
        raise Refuse("MESSAGE", "empty")
    return text.strip()


def _need_role(store: Store, session_id: str, roles: tuple[str, ...]) -> dict:
    row = store.view("session").get(session_id) if isinstance(session_id, str) else None
    if row is None or row.get("role") not in roles:
        raise Refuse("ROLE", session_id if isinstance(session_id, str) else "")
    return row


def _project_coordinator(store: Store, project_id: str) -> dict | None:
    for row in store.view("session").values():
        if not row.get("open"):
            continue
        if row.get("role") == "coordinator" and row.get("project_id") == project_id:
            return row
    return None
