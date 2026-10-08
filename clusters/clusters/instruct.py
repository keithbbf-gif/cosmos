"""Guides name instruction and MCP paths.

AGENTS.md, mcp.json, and skills directories are stored as paths. A
Gemini-to-Antigravity import is stored as accepted or skipped. This module
stores paths and that one fact. It does not store file contents.

Bodies are not read. The path is not opened and nothing is fetched.
set_import does not write settings.json; written stays false.

Python 3.11.
"""

from __future__ import annotations

import hashlib

from clusters.refuse import Refuse, guard_path
from clusters.store import Store

_KINDS = ("agents", "mcp", "skills")
_IMPORTS = ("accepted", "skipped")


def add_instruction(
    store: Store,
    *,
    project_id: str,
    kind: str,
    path: str,
) -> dict:
    _require_project(store, project_id)
    if kind not in _KINDS:
        raise Refuse("KIND")
    kept = _path(path)
    row_id = f"ins-{project_id}-{_digest(kept)}"
    # Path only. Bodies are not read and the path is not opened.
    store.append(
        "instruction",
        {
            "id": row_id,
            "project_id": project_id,
            "kind": kind,
            "path": kept,
            "imported": "",
        },
    )
    return dict(store.view("instruction")[row_id])


def set_import(store: Store, *, project_id: str, result: str) -> dict:
    _require_project(store, project_id)
    if result not in _IMPORTS:
        raise Refuse("IMPORT")
    row_id = f"import-{project_id}"
    # Fact only. written stays false; settings.json is not written.
    store.append(
        "import_status",
        {
            "id": row_id,
            "project_id": project_id,
            "result": result,
            "written": False,
        },
    )
    return dict(store.view("import_status")[row_id])


def list_instructions(store: Store, project_id: str) -> list[dict]:
    _require_project(store, project_id)
    rows = [
        dict(row)
        for row in store.view("instruction").values()
        if row.get("project_id") == project_id
    ]
    rows.sort(key=lambda row: str(row.get("path") or ""))
    return rows


def _require_project(store: Store, project_id: str) -> None:
    if store.view("project").get(project_id) is None:
        raise Refuse("PROJECT", project_id)


def _path(path: str) -> str:
    if not isinstance(path, str):
        raise Refuse("PATH", "empty")
    if len(path) > 240:
        raise Refuse("PATH", "long")
    if "\n" in path or "\r" in path:
        raise Refuse("PATH", "line")
    return guard_path(path)


def _digest(path: str) -> str:
    return hashlib.sha256(path.encode()).hexdigest()[:12]
