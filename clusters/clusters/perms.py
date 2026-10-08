"""CodeAgentSwarm Turbo permission matrix for file, shell, git, network, and MCP.

Turbo is not YOLO. A category allow never overrides a hard refusal.
"""

from __future__ import annotations

from clusters.policy import check_command
from clusters.refuse import Refuse
from clusters.store import Store

_CATEGORIES = ("file", "shell", "git", "network", "mcp")
_LEVELS = ("allow", "ask", "deny")


def set_matrix(
    store: Store,
    *,
    file: str = "ask",
    shell: str = "ask",
    git: str = "ask",
    network: str = "ask",
    mcp: str = "ask",
) -> dict:
    levels = {
        "file": file,
        "shell": shell,
        "git": git,
        "network": network,
        "mcp": mcp,
    }
    for value in levels.values():
        if value not in _LEVELS:
            raise Refuse("MATRIX")
    body = {"id": "matrix", "op": "set", **levels}
    return store.append("matrix", body)


def decide(
    store: Store,
    *,
    category: str,
    command: str,
    turbo: bool = False,
) -> dict:
    if category not in _CATEGORIES:
        raise Refuse("MATRIX")
    prior = check_command(store, command=command, turbo=turbo)
    if prior["decision"] == "refuse":
        return prior
    # Push, force-push, merge, and branch delete stay deny.
    # A git allow and turbo cannot set these guards to allow.
    if "push" in command and (
        "--force" in command or " -f" in command or command.endswith(" -f")
    ):
        return _answer("refuse", "FORCE_PUSH", "force-push", category)
    if "git branch -d" in command or "git branch -D" in command:
        return _answer("refuse", "BRANCH_DELETE", "branch delete", category)
    if command.startswith("git merge") or " git merge " in command:
        return _answer("refuse", "MERGE", "merge", category)
    if "git push" in command:
        return _answer("refuse", "PUSH_GUARD", "push", category)
    level = _matrix_level(store, category)
    if level == "deny":
        return _answer("refuse", "DENY", "deny", category)
    if level == "ask":
        return _answer("needs_approval", "ASK", "ask", category)
    return _answer("allow", "OK", "", category)


def _answer(decision: str, code: str, detail: str, category: str) -> dict[str, str]:
    return {
        "decision": decision,
        "code": code,
        "detail": detail,
        "category": category,
    }


def _matrix_level(store: Store, category: str) -> str:
    row = store.latest_kind("matrix")
    if not isinstance(row, dict):
        return "ask"
    body = row.get("body")
    if not isinstance(body, dict):
        return "ask"
    value = body.get(category, "ask")
    if value not in _LEVELS:
        return "ask"
    return value
