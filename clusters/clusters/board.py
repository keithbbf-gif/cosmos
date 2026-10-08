"""Kanban columns. Complete only from in_testing with verified evidence.

A claim is VERIFIED only with source and observed. Complete from any other
column, or without that evidence, is Refuse REVIEW. in_testing from anywhere
but in_progress, or without that evidence, is Refuse EVIDENCE. auto_tick plans
a seat and does not execute. It never passes execute=True.
"""

from __future__ import annotations

from clusters.harness import plan_seat
from clusters.models import COLUMNS, DOORS, HEROES
from clusters.refuse import Refuse
from clusters.sessions import close_session, open_session
from clusters.store import Store, new_id
from clusters.verify import judge


def add_task(
    store: Store,
    *,
    project_id: str,
    title: str,
    body: str = "",
    column: str = "pending",
    door: str = "",
    hero: str = "",
    model: str = "",
    labels: list | None = None,
    workspace: str = "",
) -> dict:
    """Add a card on a kanban column. Refuse TITLE, COLUMN, PROJECT, or LABEL."""
    if not isinstance(title, str) or not title.strip():
        raise Refuse("TITLE", "blank")
    if column not in COLUMNS:
        raise Refuse("COLUMN", str(column))
    if store.view("project").get(project_id) is None:
        raise Refuse("PROJECT", str(project_id))
    task_id = new_id("tsk")
    store.append(
        "task",
        {
            "id": task_id,
            "op": "add",
            "project_id": project_id,
            "title": title.strip(),
            "body": body,
            "column": column,
            "door": door,
            "hero": hero,
            "model": model,
            "labels": _labels(labels),
            "workspace": workspace,
            "session_id": "",
        },
    )
    return dict(store.view("task")[task_id])


def list_tasks(store: Store, project_id: str = "") -> list[dict]:
    """List kanban cards for one project, or all cards, sorted by id."""
    rows = [dict(row) for row in store.view("task").values()]
    if project_id:
        rows = [row for row in rows if row.get("project_id") == project_id]
    rows.sort(key=lambda row: row["id"])
    return rows


def move_task(
    store: Store,
    task_id: str,
    column: str,
    *,
    evidence: dict | None = None,
) -> dict:
    """Move columns. Complete only from in_testing with VERIFIED evidence, else Refuse REVIEW."""
    if column not in COLUMNS:
        raise Refuse("COLUMN", str(column))
    current = store.view("task").get(task_id)
    if current is None:
        raise Refuse("TASK", task_id)
    claim = ""
    if column == "completed":
        allowed = current.get("column") == "in_testing"
        verified = judge("complete", evidence)["verdict"] == "VERIFIED"
        if not allowed or not verified:
            raise Refuse("REVIEW", task_id)
        claim = "complete"
    elif column == "in_testing":
        allowed = current.get("column") == "in_progress"
        verified = judge("review", evidence)["verdict"] == "VERIFIED"
        if not allowed or not verified:
            raise Refuse("EVIDENCE", task_id)
        claim = "review"
    elif column == "in_progress" and current.get("column") in ("pending", "auto"):
        _require_open_session(store, evidence)
    body = _strip(current)
    body["column"] = column
    body["op"] = "move"
    if isinstance(evidence, dict) and "session_id" in evidence:
        body["session_id"] = evidence["session_id"]
    store.append("task", body, evidence, claim=claim)
    return dict(store.view("task")[task_id])


def set_auto_limit(store: Store, limit: int) -> dict:
    """Set the auto concurrency cap. A limit outside 1..50 is Refuse LIMIT."""
    if limit < 1 or limit > 50:
        raise Refuse("LIMIT", str(limit))
    store.append("auto_limit", {"id": "auto-limit", "op": "set", "limit": limit})
    return {"limit": limit}


def auto_tick(store: Store, *, limit: int | None = None, project_id: str = "") -> dict:
    """Plan a seat and do not execute. Never passes execute=True."""
    effective = _effective_limit(store, limit)
    rows = list_tasks(store, project_id)
    active = sum(1 for row in rows if row.get("column") == "in_progress")
    slots = effective - active
    if slots <= 0:
        return {"started": [], "limit": effective}
    started: list[str] = []
    queued = [row for row in rows if row.get("column") == "auto"]
    for task in queued[:slots]:
        if _start_auto(store, task):
            started.append(task["id"])
    return {"started": started, "limit": effective, "executed": False}


def _start_auto(store: Store, task: dict) -> bool:
    hero = str(task.get("hero") or "")
    door = str(task.get("door") or "")
    title = str(task.get("title") or "")
    model = str(task.get("model") or "")
    project_id = str(task.get("project_id") or "")
    opened_id = ""
    if hero in HEROES:
        project = store.view("project").get(project_id)
        if project is None:
            raise Refuse("PROJECT", project_id)
        if door:
            opened_id = open_session(
                store,
                project_id=project_id,
                door=door,
                hero=hero,
                model=model,
                task=title,
            )["id"]
        try:
            plan = plan_seat(
                hero,
                title,
                str(project.get("root") or ""),
                via="cosmos-code",
                execute=False,
            )
        except Exception:
            if opened_id:
                close_session(store, opened_id, confirm=True)
            raise
        if plan.get("verdict") == "REFUSED":
            if opened_id:
                close_session(store, opened_id, confirm=True)
            _hold(store, task, plan)
            return False
    else:
        if door in DOORS:
            opened_id = open_session(
                store,
                project_id=project_id,
                door=door,
                hero=hero,
                model=model,
                task=title,
            )["id"]
        plan = {
            "verdict": "UNMEASURED",
            "why": "UNKNOWN_HERO",
            "seated": False,
            "started": False,
        }
    _advance(store, task, opened_id, plan)
    return True


def _advance(store: Store, task: dict, session_id: str, plan: dict) -> None:
    body = _strip(task)
    body.pop("last_error", None)
    body["op"] = "move"
    body["column"] = "in_progress"
    body["session_id"] = session_id
    body["plan"] = dict(plan)
    store.append("task", body, _harness_evidence(plan), claim="")


def _hold(store: Store, task: dict, plan: dict) -> None:
    body = _strip(task)
    body["op"] = "error"
    body["column"] = "auto"
    noted = {
        "verdict": str(plan.get("verdict") or ""),
        "why": str(plan.get("why") or ""),
    }
    detail = plan.get("detail")
    if detail:
        noted["detail"] = str(detail)
    body["last_error"] = noted
    store.append("task", body, _harness_evidence(plan), claim="")


def _effective_limit(store: Store, limit: int | None) -> int:
    if limit is not None:
        return limit
    saved = store.view("auto_limit").get("auto-limit")
    if saved is None or saved.get("limit") is None:
        return 2
    return saved["limit"]


def _require_open_session(store: Store, evidence: dict | None) -> None:
    if not isinstance(evidence, dict) or "session_id" not in evidence:
        raise Refuse("SESSION", "missing")
    session_id = evidence["session_id"]
    session = store.view("session").get(session_id)
    if session is None or not session.get("open"):
        raise Refuse("SESSION", str(session_id))


def _harness_evidence(plan: dict) -> dict[str, str]:
    verdict = str(plan.get("verdict") or "")
    why = str(plan.get("why") or "")
    return {"source": "clusters.harness", "observed": f"{verdict}:{why}"}


def _labels(labels: list | None) -> list[str]:
    if not labels:
        return []
    if not isinstance(labels, list):
        raise Refuse("LABEL", "list")
    clean: list[str] = []
    for item in labels:
        if not isinstance(item, str):
            raise Refuse("LABEL", "string")
        if "\n" in item or "\r" in item:
            raise Refuse("LABEL", "newline")
        if len(item) > 40:
            raise Refuse("LABEL", "length")
        clean.append(item)
    return clean


def _strip(body: dict) -> dict:
    return {key: value for key, value in body.items() if not str(key).startswith("_")}
