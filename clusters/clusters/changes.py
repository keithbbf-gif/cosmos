"""Diff hashes, worktree plan, commit proposal, and protected push.

Change evidence is sha256 of before and after. Protected branches refuse.
Worktree and push are intent only and do not run git.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from clusters.refuse import PROTECTED_BRANCHES, Refuse, guard_path, is_protected_push
from clusters.store import Store, new_id


def record_change(
    store: Store,
    *,
    session_id: str,
    path: str,
    before: str,
    after: str,
    diff: str,
) -> dict:
    """Record diff hashes. Evidence is sha256 of before and after. Session, path, or non-text refuses."""
    _need(store, session_id)
    guard_path(path)
    if not isinstance(before, str) or not isinstance(after, str) or not isinstance(diff, str):
        raise Refuse("DIFF", "text")
    before_hash = _digest(before)
    after_hash = _digest(after)
    change_id = new_id("chg")
    body = {
        "id": change_id,
        "op": "record",
        "session_id": session_id,
        "path": path,
        "diff": diff,
        "before_hash": before_hash,
        "after_hash": after_hash,
    }
    evidence = {"source": "worktree", "observed": before_hash + ":" + after_hash}
    store.append("change", body, evidence, claim="change")
    return dict(store.view("change")[change_id])


def list_changes(store: Store, session_id: str = "") -> list[dict]:
    """List diff-hash records for one session, or all sessions when the id is blank."""
    rows = [dict(row) for row in store.view("change").values()]
    if session_id:
        rows = [row for row in rows if row.get("session_id") == session_id]
    rows.sort(key=lambda row: row["id"])
    return rows


def plan_worktree(store: Store, *, session_id: str, repo: str) -> dict:
    """Plan a session worktree. A missing session or bad path refuses. Intent only. Does not run git."""
    _need(store, session_id)
    guard_path(repo)
    planned = str(Path(repo) / ".clusters" / "worktrees" / session_id)
    command = f'git worktree add "{planned}" HEAD'
    worktree_id = new_id("wt")
    body = {
        "id": worktree_id,
        "op": "plan",
        "session_id": session_id,
        "repo": repo,
        "planned": planned,
        "command": command,
        "executed": False,
    }
    store.append("worktree", body, claim="")
    row = dict(store.view("worktree")[worktree_id])
    row["executed"] = False
    return row


def propose_commit(store: Store, *, session_id: str, summary: str) -> dict:
    """Propose a commit from recorded hashes. A blank summary refuses. Does not commit or push."""
    if not isinstance(summary, str) or not summary.strip():
        raise Refuse("SUMMARY", "blank")
    changes = list_changes(store, session_id)
    files = [str(row["path"]) for row in changes]
    hashes = [str(row["after_hash"]) for row in changes]
    body = {
        "id": new_id("cmt"),
        "op": "propose",
        "session_id": session_id,
        "summary": summary,
        "files": files,
        "hashes": hashes,
        "executed": False,
    }
    store.append("commit_proposal", body, claim="")
    return {
        "session_id": session_id,
        "summary": summary,
        "files": files,
        "hashes": hashes,
        "executed": False,
    }


def request_push(
    store: Store,
    *,
    session_id: str,
    branch: str,
    confirmed: bool = False,
) -> dict:
    """Protected or unconfirmed push refuses. Intent only. Does not run git."""
    _need(store, session_id)
    if is_protected_push("git push " + branch, branch) or branch.strip().lower() in PROTECTED_BRANCHES:
        raise Refuse("PROTECTED", branch)
    if not confirmed:
        raise Refuse("CONFIRM", branch)
    body = {
        "id": new_id("psh"),
        "op": "intent",
        "session_id": session_id,
        "branch": branch,
        "executed": False,
        "confirmed": True,
    }
    store.append("push_intent", body, claim="")
    return {"executed": False, "branch": branch, "pushed": False}


def _need(store: Store, session_id: str) -> None:
    if session_id not in store.view("session"):
        raise Refuse("SESSION", session_id)


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
