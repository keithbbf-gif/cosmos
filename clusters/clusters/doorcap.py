"""Door capabilities the permission matrix does not store.

Guides name Pi manual, auto-approve edits, and full-access; Kimi plan, auto,
and yolo; an OpenCode provider; Grok plan mode; no-subagents; a worktree
name; and the resolved command path. Storing them does not enable them.
Hard launch flags stay refused as execution. applied and started stay false.

Nothing launches.
"""

from __future__ import annotations

from clusters.refuse import HARD_FLAGS, Refuse, guard_path
from clusters.store import Store

MODES = (
    "manual",
    "auto-edits",
    "full-access",
    "plan",
    "auto",
    "yolo",
    "suggest",
    "default",
)
PROVIDERS = ("", "anthropic", "openai", "google", "copilot", "local")

_WORKTREE = 80


def set_caps(
    store: Store,
    *,
    session_id: str,
    mode: str,
    provider: str = "",
    subagents: bool = True,
    worktree: str = "",
    command_path: str = "",
) -> dict:
    """Append a door_cap row. Nothing launches."""
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    if mode not in MODES:
        raise Refuse("MODE")
    if provider not in PROVIDERS:
        raise Refuse("PROVIDER")
    if not isinstance(subagents, bool):
        raise Refuse("CAPS", "subagents")
    named = _worktree(worktree)
    path = _command_path(command_path)
    row_id = f"caps-{session_id}"
    # Nothing launches. yolo and full-access are stored names, not applied.
    # A path ending in grok.exe is stored. started stays false.
    store.append(
        "door_cap",
        {
            "id": row_id,
            "session_id": session_id,
            "mode": mode,
            "provider": provider,
            "subagents": subagents,
            "worktree": named,
            "command_path": path,
            "applied": False,
            "started": False,
        },
    )
    return _shown(store, session_id)


def get_caps(store: Store, session_id: str) -> dict:
    """Return the row. applied and started are forced false on read."""
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION")
    if store.view("door_cap").get(f"caps-{session_id}") is None:
        raise Refuse("CAPS", "missing")
    return _shown(store, session_id)


def _shown(store: Store, session_id: str) -> dict:
    view = dict(store.view("door_cap")[f"caps-{session_id}"])
    view["applied"] = False
    view["started"] = False
    return view


def _worktree(text: object) -> str:
    if not isinstance(text, str) or "\n" in text or "\r" in text:
        raise Refuse("CAPS", "worktree")
    if text == "":
        return ""
    if not 1 <= len(text) <= _WORKTREE:
        raise Refuse("CAPS", "worktree")
    _reject_flag(text)
    return text


def _command_path(text: object) -> str:
    """Accept an empty path or a guarded path. Do not execute it."""
    if text == "":
        return ""
    if not isinstance(text, str):
        raise Refuse("PATH", "empty")
    kept = guard_path(text)
    _reject_flag(kept)
    # A folded path ending in grok.exe is stored. started stays false.
    # Nothing launches.
    return kept


def _reject_flag(text: str) -> None:
    """Hard launch flags are refused. They are not written on the row."""
    folded = text.lower()
    for flag in HARD_FLAGS:
        if flag in folded:
            raise Refuse("FLAG", flag)
