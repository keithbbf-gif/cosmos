"""One project coordinator and one global. A second of either scope refuses.

A greeting is not a goal. A plan opens or reuses workers. A plan without
source and observed stays UNMEASURED. Report does not poll. Close only
own workers. Comms applies to sessions opened after the switch. This
module does not call the harness.
"""

from __future__ import annotations

from clusters import sessions
from clusters.models import DOORS
from clusters.refuse import Refuse
from clusters.store import Store
from clusters.verify import judge

_COORDINATOR_ROLES = ("coordinator", "global_coordinator")
_GREETINGS = frozenset({"hi", "hello", "hey"})


def open_coordinator(
    store: Store,
    *,
    scope: str,
    project_id: str,
    hero: str,
    door: str,
    model: str,
) -> dict:
    """Open one project or one global coordinator. A second of that scope refuses."""
    if scope not in ("project", "global"):
        raise Refuse("SCOPE", scope if isinstance(scope, str) else "")
    if not isinstance(project_id, str) or not project_id.strip():
        raise Refuse("PROJECT", project_id if isinstance(project_id, str) else "")
    if project_id not in store.view("project"):
        raise Refuse("PROJECT", project_id)
    role = "global_coordinator" if scope == "global" else "coordinator"
    for row in store.view("session").values():
        if not row.get("open"):
            continue
        if scope == "global" and row.get("role") == "global_coordinator":
            raise Refuse("SECOND", row["id"])
        same_project = row.get("role") == "coordinator" and row.get("project_id") == project_id
        if scope == "project" and same_project:
            raise Refuse("SECOND", row["id"])
    opened = sessions.open_session(
        store,
        project_id=project_id,
        door=door,
        hero=hero,
        model=model,
        role=role,
        cluster_id="",
        parent_id="",
        title="",
    )
    opened["scope"] = scope
    return opened


def submit_goal(store: Store, coordinator_id: str, text: str) -> dict:
    """Record a goal. A greeting or a question is not a goal."""
    from clusters import history

    current = _need_coordinator(store, coordinator_id, require_open=True)
    if not isinstance(text, str):
        raise Refuse("GOAL", "text")
    text = text.strip()
    if not text:
        raise Refuse("GOAL", "empty")
    if text.casefold() in _GREETINGS or text.endswith("?"):
        history.add_message(
            store,
            session_id=coordinator_id,
            role="user",
            kind="user",
            body=text,
            resume_of="",
        )
        return {"started": False, "goal": text}
    goal_id = f"goal-{coordinator_id}"
    store.append(
        "goal",
        {
            "id": goal_id,
            "coordinator_id": coordinator_id,
            "text": text,
            "project_id": current["project_id"],
            "state": "open",
        },
    )
    history.add_message(
        store,
        session_id=coordinator_id,
        role="user",
        kind="user",
        body=text,
        resume_of="",
    )
    return {"started": True, "goal_id": goal_id, "coordinator_id": coordinator_id}


def accept_plan(
    store: Store,
    coordinator_id: str,
    plan: dict,
    *,
    evidence: dict | None,
) -> dict:
    """Open or reuse workers. A plan without source and observed stays UNMEASURED."""
    from clusters import history

    _need_coordinator(store, coordinator_id, require_open=True)
    if not isinstance(plan, dict) or not isinstance(plan.get("workers"), list):
        raise Refuse("PLAN", "workers")
    workers = [_check_worker(store, item) for item in plan["workers"]]
    stamped = judge("plan", evidence)
    if stamped["verdict"] == "VERIFIED":
        plan_verdict = "VERIFIED"
        source = "harness"
    else:
        plan_verdict = "UNMEASURED"
        source = "operator"
    worker_ids: list[str] = []
    for item in workers:
        worker_id = _open_or_reuse(store, coordinator_id, item)
        history.add_message(
            store,
            session_id=worker_id,
            role="coordinator",
            kind="assignment",
            body=item["task"],
            resume_of="",
        )
        worker_ids.append(worker_id)
    return {
        "plan_verdict": plan_verdict,
        "source": source,
        "worker_ids": worker_ids,
        "coordinator_id": coordinator_id,
    }


def report(store: Store, coordinator_id: str) -> dict:
    """Report this coordinator's workers when asked. This is not a poll."""
    _need_coordinator(store, coordinator_id, require_open=False)
    workers = []
    for row in sessions.list_sessions(store):
        if row.get("parent_id") != coordinator_id:
            continue
        workers.append(
            {
                "id": row["id"],
                "verified_status": row.get("verified_status") or "",
                "pending_report": row.get("pending_report") or "",
                "title": row.get("title") or "",
                "verdict": row.get("_verdict") or "",
            }
        )
    return {"coordinator_id": coordinator_id, "workers": workers, "polled": False}


def close_worker(
    store: Store,
    coordinator_id: str,
    worker_id: str,
    *,
    confirm: bool = False,
) -> dict:
    """Close a worker this coordinator opened. Another owner refuses."""
    worker = sessions.get_session(store, worker_id)
    if worker.get("parent_id") != coordinator_id:
        raise Refuse("OWNER", worker_id)
    return sessions.close_session(store, worker_id, confirm=confirm)


def ask_session(
    store: Store,
    *,
    sender_id: str,
    target_id: str,
    question: str,
) -> dict:
    """Record one question between sessions that have comms. Comms off refuses."""
    from clusters import history

    _need_comms(store, sender_id)
    _need_comms(store, target_id)
    if not isinstance(question, str) or not question.strip():
        raise Refuse("QUESTION", "empty")
    question = question.strip()
    history.add_message(
        store,
        session_id=target_id,
        role="agent",
        kind="request",
        body=question,
        resume_of="",
        sender_id=sender_id,
    )
    sessions.queue_message(store, target_id, +1)
    return {"kind": "request", "sender_id": sender_id, "target_id": target_id}


def set_session_comms(store: Store, enabled: bool) -> dict:
    """Set session comms. It applies only to sessions opened after this event."""
    flag = bool(enabled)
    store.append("privacy", {"id": "privacy", "op": "set", "enabled": flag})
    return {"enabled": flag, "applies": "sessions opened after this event"}


def _need_coordinator(store: Store, coordinator_id: str, *, require_open: bool) -> dict:
    current = sessions.get_session(store, coordinator_id)
    if current.get("role") not in _COORDINATOR_ROLES:
        raise Refuse("COORDINATOR", str(current.get("role") or coordinator_id))
    if require_open and not current.get("open"):
        raise Refuse("COORDINATOR", "closed")
    return current


def _need_comms(store: Store, session_id: str) -> dict:
    try:
        row = sessions.get_session(store, session_id)
    except Refuse as exc:
        raise Refuse("COMMS_OFF", session_id) from exc
    if not row.get("open") or not row.get("comms"):
        raise Refuse("COMMS_OFF", session_id)
    return row


def _check_worker(store: Store, item: object) -> dict:
    if not isinstance(item, dict):
        raise Refuse("PLAN", "worker")
    project_id = item.get("project_id")
    if not isinstance(project_id, str) or project_id not in store.view("project"):
        raise Refuse("PROJECT", project_id if isinstance(project_id, str) else "")
    door = item.get("door")
    if not isinstance(door, str) or door not in DOORS:
        raise Refuse("UNKNOWN_DOOR", door if isinstance(door, str) else "")
    task = item.get("task")
    if not isinstance(task, str) or not task.strip():
        raise Refuse("PLAN", "task")
    return item


def _open_or_reuse(store: Store, coordinator_id: str, item: dict) -> str:
    project_id = item["project_id"]
    door = item["door"]
    reuse_id = item.get("reuse_session_id")
    if isinstance(reuse_id, str) and reuse_id:
        current = store.view("session").get(reuse_id)
        matched = (
            current is not None
            and current.get("open")
            and current.get("project_id") == project_id
            and current.get("door") == door
        )
        if matched:
            sessions.queue_message(store, reuse_id, +1)
            return reuse_id
    hero_raw = item.get("hero")
    model_raw = item.get("model")
    hero = hero_raw if isinstance(hero_raw, str) else ""
    model = model_raw if isinstance(model_raw, str) else ""
    opened = sessions.open_session(
        store,
        project_id=project_id,
        door=door,
        hero=hero,
        model=model,
        task=item["task"],
        role="worker",
        parent_id=coordinator_id,
        cluster_id="",
        title="",
    )
    return opened["id"]
