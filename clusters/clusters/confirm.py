"""Store a git read the operator already performed outside this module.

The record does not run git, and it does not land or push a branch.
"main" may be stored as an observation.
"""

from __future__ import annotations

from clusters.refuse import Refuse
from clusters.store import Store, new_id
from clusters.verify import judge

_BRANCH_LIMIT = 120


def record_confirm(
    store: Store,
    *,
    session_id: str,
    branch: str,
    clean: bool,
    evidence: dict | None = None,
) -> dict[str, str | bool]:
    """Record the branch and whether that outside read showed a clean tree."""
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    text = _branch(branch)
    if not isinstance(clean, bool):
        raise Refuse("CLEAN")
    # Evidence rule: judge("git-read") is VERIFIED only when evidence has both
    # source and observed. Otherwise the verdict is UNMEASURED and confirmed
    # stays false. This record does not run git.
    stamped = judge("git-read", evidence)
    verdict = stamped["verdict"]
    confirmed = verdict == "VERIFIED"
    state = "clean" if clean else "dirty"
    store.append(
        "git_confirm",
        {
            "id": new_id("gcf"),
            "session_id": session_id,
            "branch": text,
            "clean": clean,
            "confirmed": confirmed,
            "executed": False,
        },
        evidence,
        claim="git-read",
    )
    return {
        "summary": f"{text} {state}",
        "confirmed": confirmed,
        "verdict": verdict,
        "executed": False,
    }


def _branch(branch: str) -> str:
    if not isinstance(branch, str) or "\n" in branch or "\r" in branch:
        raise Refuse("BRANCH")
    if not 1 <= len(branch) <= _BRANCH_LIMIT:
        raise Refuse("BRANCH")
    return branch
