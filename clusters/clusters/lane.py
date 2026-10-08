"""CodeAgentSwarm Auto Kanban.

This module only queues. It does not open a session and does not call the
harness. board.auto_tick is what starts work.
"""

from __future__ import annotations

from clusters.board import add_task
from clusters.models import DOORS
from clusters.refuse import Refuse
from clusters.store import Store

REASONING = ("low", "medium", "high", "max")
PERMISSION = ("default", "turbo")
WORKSPACE = ("folder", "worktree", "branch")

_QUEUED = ("door", "hero", "model", "reasoning", "permission", "workspace")
_CHOICES = {
    "door": DOORS,
    "reasoning": REASONING,
    "permission": PERMISSION,
    "workspace": WORKSPACE,
}


def set_defaults(
    store: Store,
    *,
    project_id: str,
    door: str,
    hero: str = "",
    model: str = "",
    reasoning: str = "medium",
    permission: str = "default",
    workspace: str = "worktree",
) -> dict:
    if store.view("project").get(project_id) is None:
        raise Refuse("DEFAULTS", "project")
    _accept("door", door)
    _accept("reasoning", reasoning)
    _accept("permission", permission)
    _accept("workspace", workspace)
    defaults_id = f"defaults-{project_id}"
    store.append(
        "auto_defaults",
        {
            "id": defaults_id,
            "op": "set",
            "project_id": project_id,
            "door": door,
            "hero": hero,
            "model": model,
            "reasoning": reasoning,
            "permission": permission,
            "workspace": workspace,
        },
    )
    return dict(store.view("auto_defaults")[defaults_id])


def queue_drag(store: Store, task_id: str) -> dict:
    task = _pending(store, task_id)
    project_id = str(task.get("project_id") or "")
    picked = _apply(_defaults(store, project_id), {})
    return _write(store, task, picked, "queue")


def queue_lightning(
    store: Store,
    task_id: str,
    *,
    door: str = "",
    hero: str = "",
    model: str = "",
    reasoning: str = "",
    permission: str = "",
    workspace: str = "",
) -> dict:
    task = _pending(store, task_id)
    project_id = str(task.get("project_id") or "")
    picked = _apply(
        _defaults(store, project_id),
        {
            "door": door,
            "hero": hero,
            "model": model,
            "reasoning": reasoning,
            "permission": permission,
            "workspace": workspace,
        },
    )
    return _write(store, task, picked, "lightning")


def queue_new(
    store: Store,
    *,
    project_id: str,
    title: str,
    body: str = "",
    door: str = "",
    hero: str = "",
    model: str = "",
    reasoning: str = "",
    permission: str = "",
    workspace: str = "",
    labels: list | None = None,
) -> dict:
    task = add_task(
        store,
        project_id=project_id,
        title=title,
        body=body,
        column="pending",
        labels=labels,
    )
    overrides = (door, hero, model, reasoning, permission, workspace)
    if any(item != "" for item in overrides):
        return queue_lightning(
            store,
            task["id"],
            door=door,
            hero=hero,
            model=model,
            reasoning=reasoning,
            permission=permission,
            workspace=workspace,
        )
    return queue_drag(store, task["id"])


def _accept(kind: str, value: str) -> None:
    if value not in _CHOICES[kind]:
        raise Refuse("DEFAULTS", kind)


def _pending(store: Store, task_id: str) -> dict:
    task = store.view("task").get(task_id)
    if task is None or task.get("column") != "pending":
        raise Refuse("QUEUE", task_id)
    return task


def _defaults(store: Store, project_id: str) -> dict:
    row = store.view("auto_defaults").get(f"defaults-{project_id}")
    if row is None:
        raise Refuse("DEFAULTS", "missing")
    return row


def _apply(defaults: dict, overrides: dict[str, str]) -> dict:
    chosen: dict = {}
    for key in _QUEUED:
        if key not in defaults:
            raise Refuse("DEFAULTS", key)
        chosen[key] = defaults[key]
    for key, value in overrides.items():
        if value == "":
            continue
        if key in _CHOICES:
            _accept(key, value)
        chosen[key] = value
    return chosen


def _write(store: Store, task: dict, picked: dict, op: str) -> dict:
    body = {key: value for key, value in task.items() if not str(key).startswith("_")}
    body["column"] = "auto"
    body["op"] = op
    for key in _QUEUED:
        body[key] = picked[key]
    store.append("task", body)
    return dict(store.view("task")[task["id"]])
