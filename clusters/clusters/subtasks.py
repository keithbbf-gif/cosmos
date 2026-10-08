"""Kanban subtasks.

A child hangs one level under a task. A missing parent is Refuse("TASK", parent_id).
A parent that already has parent_id is Refuse("SUBTASK", "nested"). This stores
records only: it does not complete a card, move a column, or open a session.
"""

from __future__ import annotations

from clusters.board import add_task
from clusters.refuse import Refuse
from clusters.store import Store


def add_subtask(
    store: Store,
    *,
    parent_id: str,
    title: str,
    body: str = "",
) -> dict:
    parent = _require_parent(store, parent_id)
    if parent.get("parent_id"):
        raise Refuse("SUBTASK", "nested")
    created = add_task(
        store,
        project_id=str(parent.get("project_id") or ""),
        title=title,
        body=body,
    )
    recorded = _public(created)
    recorded["parent_id"] = parent_id
    recorded["op"] = "subtask"
    store.append("task", recorded)
    return dict(store.view("task")[created["id"]])


def list_subtasks(store: Store, parent_id: str) -> list[dict]:
    _require_parent(store, parent_id)
    rows = [
        dict(row)
        for row in store.view("task").values()
        if row.get("parent_id") == parent_id
    ]
    rows.sort(key=lambda row: row["id"])
    return rows


def _require_parent(store: Store, parent_id: str) -> dict:
    parent = store.view("task").get(parent_id)
    if parent is None:
        raise Refuse("TASK", parent_id)
    return parent


def _public(body: dict) -> dict:
    """Drop fold bookkeeping. Card fields stay so a later view still lists the task."""
    return {key: value for key, value in body.items() if not str(key).startswith("_")}
