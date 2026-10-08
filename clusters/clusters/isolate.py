"""Isolation intent.

One task, the base ref the operator named, whether the next seat has its own
branch and directory or shares one, and the file boundary it may touch. A repo
with no commits falls back to the project folder, and the record says why.
This stores the operator's intent. It does not run git worktree.
"""

from __future__ import annotations

from clusters.refuse import Refuse, guard_path
from clusters.store import Store, new_id

_SHARES = ("own", "share")
_WORKSPACES = ("worktree", "folder")
_REF_LIMIT = 120
_WHY_LIMIT = 240
_PATH_LIMIT = 20


def plan_isolation(
    store: Store,
    *,
    task_id: str,
    base_ref: str,
    share: str,
    workspace: str,
    why: str = "",
    paths: list[str] | None = None,
) -> dict:
    if store.view("task").get(task_id) is None:
        raise Refuse("TASK", task_id)
    named = _ref(base_ref)
    if share not in _SHARES:
        raise Refuse("SHARE")
    if workspace not in _WORKSPACES:
        raise Refuse("WORKSPACE")
    reason = _why(workspace, why)
    bounded = _paths(paths)
    iso_id = new_id("iso")
    # Git is not run. origin/main is a stored name, not a push.
    store.append(
        "isolation",
        {
            "id": iso_id,
            "task_id": task_id,
            "base_ref": named,
            "share": share,
            "workspace": workspace,
            "why": reason,
            "paths": bounded,
            "executed": False,
            "git": False,
        },
    )
    return dict(store.view("isolation")[iso_id])


def _ref(text: str) -> str:
    if (
        not isinstance(text, str)
        or not text.strip()
        or "\n" in text
        or "\r" in text
        or not 1 <= len(text) <= _REF_LIMIT
    ):
        raise Refuse("REF")
    return text


def _why(workspace: str, why: str) -> str:
    if workspace == "worktree":
        if why != "":
            raise Refuse("WHY")
        return ""
    if (
        not isinstance(why, str)
        or not why.strip()
        or "\n" in why
        or "\r" in why
        or not 1 <= len(why) <= _WHY_LIMIT
    ):
        raise Refuse("WHY")
    return why


def _paths(paths: list[str] | None) -> list[str]:
    if paths is None:
        return []
    if not isinstance(paths, list):
        raise Refuse("PATH", "list")
    if len(paths) > _PATH_LIMIT:
        raise Refuse("PATH", "limit")
    return [guard_path(item) for item in paths]
