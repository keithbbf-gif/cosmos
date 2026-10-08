"""Session slots. A finished status without evidence does not flip the verified status."""

from __future__ import annotations

from clusters.models import BUSY, DOORS, ROLES, SESSION_CAP, STATUSES, VIEWS
from clusters.refuse import Refuse
from clusters.store import Store, new_id
from clusters.verify import judge


def open_session(
    store: Store,
    *,
    project_id: str,
    door: str,
    hero: str = "",
    model: str = "",
    task: str = "",
    role: str = "worker",
    account_id: str = "",
    cluster_id: str = "",
    parent_id: str = "",
    title: str = "",
) -> dict:
    if role not in ROLES:
        raise Refuse("ROLE", role)
    if door not in DOORS:
        raise Refuse("UNKNOWN_DOOR", door)
    project = store.view("project").get(project_id)
    if project is None:
        raise Refuse("PROJECT", project_id)
    if cluster_id and cluster_id not in store.view("cluster"):
        raise Refuse("CLUSTER", cluster_id)
    if parent_id and parent_id not in store.view("session"):
        raise Refuse("SESSION", parent_id)
    open_count = sum(1 for row in store.view("session").values() if row.get("open"))
    if open_count >= SESSION_CAP:
        raise Refuse("SESSION_CAP", str(SESSION_CAP))
    privacy = store.latest_kind("privacy")
    comms = bool(privacy and privacy["body"].get("enabled"))
    # Claude and Codex are the only managed account providers. A new
    # session with no explicit account takes that provider's default.
    if not account_id and door in ("claude", "codex"):
        for row in store.view("account").values():
            if row.get("provider") == door and row.get("is_default"):
                account_id = str(row["id"])
                break
    session_id = new_id("ses")
    shown = title.strip() or _default_title(door, task)
    body = {
        "id": session_id,
        "op": "open",
        "project_id": project_id,
        "door": door,
        "hero": hero,
        "model": model,
        "task": task,
        "role": role,
        "account_id": account_id,
        "cluster_id": cluster_id,
        "parent_id": parent_id,
        "title": shown,
        "verified_title": shown,
        "status": "idle",
        "verified_status": "idle",
        "open": True,
        "comms": comms,
        "background": role == "worker" and bool(parent_id),
        "view": "tabs",
        "bounds": {},
        "queued": 0,
    }
    store.append("session", body)
    return _public(store, session_id)


def close_session(store: Store, session_id: str, *, confirm: bool = False) -> dict:
    current = _need(store, session_id)
    if not current.get("open"):
        return _public(store, session_id)
    busy = current.get("verified_status") in BUSY or int(current.get("queued") or 0) > 0
    if busy and current.get("parent_id") and not confirm:
        raise Refuse("CONFIRM", "busy worker")
    body = dict(current)
    body["op"] = "close"
    body["open"] = False
    body["role_ended"] = body.get("role") != "worker"
    store.append("session", _strip(body))
    return _public(store, session_id)


def set_status(
    store: Store,
    session_id: str,
    status: str,
    *,
    evidence: dict | None = None,
) -> dict:
    if status not in STATUSES:
        raise Refuse("STATUS", status)
    current = _need(store, session_id)
    stamped = judge(f"status {status}", evidence)
    body = dict(current)
    body["op"] = "status"
    body["reported_status"] = status
    # finished, failed, and needs_input are claims about the agent.
    # Without source and observed, the verified status stays where it was.
    claimed = status in ("finished", "failed", "needs_input")
    if claimed and stamped["verdict"] != "VERIFIED":
        body["pending_report"] = status
        store.append("session", _strip(body), evidence, claim=f"status {status}")
        return _public(store, session_id)
    if claimed:
        body["pending_report"] = ""
    body["status"] = status
    body["verified_status"] = status
    store.append("session", _strip(body), evidence, claim=f"status {status}" if claimed else "")
    return _public(store, session_id)


def set_title(
    store: Store,
    session_id: str,
    title: str,
    *,
    evidence: dict | None = None,
) -> dict:
    current = _need(store, session_id)
    if not title.strip():
        raise Refuse("TITLE", "empty")
    stamped = judge("title", evidence)
    shown = title.strip()
    prior = current.get("title")
    body = dict(current)
    body["op"] = "title"
    body["reported_title"] = shown
    if stamped["verdict"] == "VERIFIED":
        body["title"] = shown
        body["verified_title"] = shown
    store.append("session", _strip(body), evidence, claim="title")
    if stamped["verdict"] == "VERIFIED" and shown != prior:
        store.append(
            "title_history",
            {"id": new_id("ttl"), "session_id": session_id, "title": shown},
            evidence,
            claim="title",
        )
    return _public(store, session_id)


def list_titles(store: Store, session_id: str) -> list[dict]:
    # Dynamic title history.
    # Missing session raises Refuse("SESSION", session_id).
    # A row exists only for a VERIFIED title that differs from the current one.
    _need(store, session_id)
    rows = [
        dict(row)
        for row in store.view("title_history").values()
        if row.get("session_id") == session_id
    ]
    rows.sort(key=lambda row: row["_seq"])
    return rows


def put_layout(store: Store, session_id: str, *, view: str, bounds: dict) -> dict:
    if view not in VIEWS:
        raise Refuse("VIEW", view)
    if not isinstance(bounds, dict):
        raise Refuse("BOUNDS", "object")
    current = _need(store, session_id)
    body = dict(current)
    body["op"] = "layout"
    body["view"] = view
    body["bounds"] = {key: bounds[key] for key in bounds if key in ("x", "y", "w", "h")}
    store.append("session", _strip(body))
    return _public(store, session_id)


def queue_message(store: Store, session_id: str, delta: int) -> dict:
    current = _need(store, session_id)
    body = dict(current)
    body["op"] = "queue"
    body["queued"] = max(0, int(current.get("queued") or 0) + delta)
    store.append("session", _strip(body))
    return _public(store, session_id)


def list_sessions(store: Store, project_id: str = "") -> list[dict]:
    rows = [_public(store, key) for key in store.view("session")]
    if project_id:
        rows = [row for row in rows if row["project_id"] == project_id]
    rows.sort(key=lambda row: (0 if row["role"] != "worker" else 1, row["id"]))
    return rows


def get_session(store: Store, session_id: str) -> dict:
    _need(store, session_id)
    return _public(store, session_id)


def bind_account(store: Store, session_id: str, account_id: str) -> dict:
    current = _need(store, session_id)
    if current.get("verified_status") != "idle":
        raise Refuse("ACCOUNT_SWITCH", "session is not idle")
    body = dict(current)
    body["op"] = "account"
    body["account_id"] = account_id
    store.append("session", _strip(body))
    return _public(store, session_id)


def _need(store: Store, session_id: str) -> dict:
    current = store.view("session").get(session_id)
    if current is None:
        raise Refuse("SESSION", session_id)
    return current


def _public(store: Store, session_id: str) -> dict:
    row = dict(store.view("session")[session_id])
    door = DOORS.get(row.get("door", ""), {})
    row["door_seated"] = bool(door.get("seated"))
    row["door_executable"] = bool(door.get("executable"))
    row["resume"] = bool(door.get("resume"))
    return row


def _strip(body: dict) -> dict:
    return {key: value for key, value in body.items() if not key.startswith("_")}


def _default_title(door: str, task: str) -> str:
    line = task.strip().splitlines()[0] if task.strip() else "New agent"
    return f"{door}: {line[:80]}"
