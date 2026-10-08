"""This extends CodeAgentSwarm git integration.

The existing clusters.changes module already records diffs, plans a worktree,
proposes a commit shell, and refuses a protected push. This module adds the
guards their turbo guide names, and a review bundle. Nothing is executed. A
review bundle is not a created pull request.
"""

from __future__ import annotations

from clusters.changes import list_changes
from clusters.refuse import Refuse
from clusters.store import Store, new_id
from clusters.verify import judge

_READ = ("status", "diff", "log", "rev-parse")
_REFUSED = frozenset({"force_push", "branch_delete", "merge", "push"})


def classify(command: str) -> dict:
    """Name one git guard. A refused op is not run."""
    folded = [token.lower() for token in command.split()]
    # --force and -f count only as whole tokens. --force-with-lease is a push.
    # Lower case folds branch -D onto -d.
    force = any(token in {"--force", "-f"} for token in folded)
    if _seq(folded, "git", "push") and force:
        return _named("force_push")
    if _seq(folded, "git", "branch", "-d"):
        return _named("branch_delete")
    if _seq(folded, "git", "merge"):
        return _named("merge")
    if _seq(folded, "git", "push"):
        return _named("push")
    if any(_seq(folded, "git", name) for name in _READ):
        return _named("read")
    return _named("other")


def propose_message(
    store: Store,
    *,
    session_id: str,
    evidence: dict | None = None,
    style: str = "detailed",
) -> dict:
    """Commit text from recorded diffs, or from observed text when verified.

    Concise is the subject line. Detailed joins each path and after_hash.
    Any other style is refused. No model is called and no git command runs.
    The result is not executed and not committed.
    """
    _need(store, session_id)
    # Concise or detailed commit text only. A third style is refused.
    # Neither style runs a git command.
    if style not in {"concise", "detailed"}:
        raise Refuse("STYLE", style)
    changes = list_changes(store, session_id)
    files: list[str] = []
    parts = [f"Review {len(changes)} file(s)"]
    for row in changes:
        path = str(row["path"])
        files.append(path)
        if style == "detailed":
            parts.append(path)
            parts.append(str(row["after_hash"]))
    built = " ".join(parts)
    stamped = judge("commit-text", evidence)
    if stamped["verdict"] == "VERIFIED" and isinstance(evidence, dict):
        observed = evidence.get("observed")
        summary = observed if isinstance(observed, str) else str(observed)
        source = "model"
        verdict = "VERIFIED"
    else:
        summary = built
        source = "diff"
        verdict = "UNMEASURED"
    store.append(
        "commit_text",
        {
            "id": new_id("ctx"),
            "session_id": session_id,
            "summary": summary,
            "source": source,
            "style": style,
            "files": files,
            "executed": False,
            "committed": False,
        },
        evidence,
        claim="commit-text",
    )
    return {
        "summary": summary,
        "source": source,
        "style": style,
        "files": files,
        "executed": False,
        "committed": False,
        "verdict": verdict,
    }


def propose_review(store: Store, *, session_id: str, summary: str) -> dict:
    """Record the bundle T3 Code would turn into a pull request. We do not."""
    _need(store, session_id)
    if not isinstance(summary, str) or not summary.strip():
        raise Refuse("SUMMARY")
    public = {
        "id": new_id("rev"),
        "session_id": session_id,
        "summary": summary,
        "pushed": False,
        "pr": False,
        "executed": False,
    }
    store.append("review", public)
    return dict(public)


def _named(op: str) -> dict:
    return {"op": op, "refused": op in _REFUSED}


def _seq(folded: list[str], *parts: str) -> bool:
    width = len(parts)
    want = tuple(parts)
    for index in range(len(folded) - width + 1):
        if tuple(folded[index:index + width]) == want:
            return True
    return False


def _need(store: Store, session_id: str) -> None:
    if session_id not in store.view("session"):
        raise Refuse("SESSION")
