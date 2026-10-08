"""CodeAgentSwarm mentions a skills marketplace next to the MCP marketplace.
The COSMOS harness rule is: a skill is a path, not a pasted body.
This module stores enable flags for skill paths.
It does not read the files and does not fetch them.
skill_for_pack is the enabled paths a HERO PACK may carry. Bodies are not included.
"""

from __future__ import annotations

import hashlib

from clusters.refuse import Refuse, guard_path
from clusters.store import Store


def enable_skill(
    store: Store,
    *,
    project_id: str,
    path: str,
    enabled: bool = True,
) -> dict:
    if store.view("project").get(project_id) is None:
        raise Refuse("PROJECT", project_id)
    kept = _path(path)
    row_id = f"skill-{project_id}-{_digest(kept)}"
    store.append(
        "skill",
        {
            "id": row_id,
            "op": "set",
            "project_id": project_id,
            "path": kept,
            "enabled": bool(enabled),
        },
    )
    return dict(store.view("skill")[row_id])


def list_skills(store: Store, project_id: str) -> list[dict]:
    rows = [
        dict(row)
        for row in store.view("skill").values()
        if row.get("project_id") == project_id
    ]
    rows.sort(key=lambda row: (str(row.get("path") or ""), str(row.get("id") or "")))
    return rows


def skill_for_pack(store: Store, project_id: str) -> list[str]:
    paths = [
        str(row["path"])
        for row in list_skills(store, project_id)
        if row.get("enabled") is True
    ]
    return sorted(paths)


def _path(path: str) -> str:
    if not isinstance(path, str) or "\n" in path or "\r" in path or not 1 <= len(path) <= 240:
        raise Refuse("SKILL")
    return guard_path(path)


def _digest(path: str) -> str:
    return hashlib.sha256(path.encode()).hexdigest()[:12]
