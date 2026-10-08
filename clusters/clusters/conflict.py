"""Same-file conflict outcomes.

A guide says two Claude Code sessions that save one file can produce a Git
conflict, and Claude Code usually resolves it. This stores the operator's
outcome. It does not check git and it does not change the file. Git is not
run.

Refusals: a missing session is Refuse("SESSION", session_id). A path that
fails clusters.refuse.guard_path is refused there, and a live path raises
LIVE_TREE. An outcome outside OUTCOMES is Refuse("OUTCOME").
"""

from __future__ import annotations

from clusters.refuse import Refuse, guard_path
from clusters.store import Store, new_id

OUTCOMES = ("unresolved", "agent-resolved", "operator")


def record_conflict(
    store: Store,
    *,
    session_id: str,
    path: str,
    outcome: str,
) -> dict:
    """Store the outcome. Git is not run and the path is not written."""
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    kept = guard_path(path)
    if outcome not in OUTCOMES:
        raise Refuse("OUTCOME")
    conflict_id = new_id("cfl")
    # Git is not run. The path is stored and not written.
    store.append(
        "conflict",
        {
            "id": conflict_id,
            "session_id": session_id,
            "path": kept,
            "outcome": outcome,
            "executed": False,
        },
    )
    return dict(store.view("conflict")[conflict_id])


def list_conflicts(store: Store, session_id: str = "") -> list[dict]:
    """List stored outcomes. A session id limits the rows. Paths are not opened."""
    # Do not open the path. Git is not run.
    rows = [dict(row) for row in store.view("conflict").values()]
    if session_id:
        rows = [row for row in rows if row.get("session_id") == session_id]
    rows.sort(key=lambda row: row["id"])
    return rows
