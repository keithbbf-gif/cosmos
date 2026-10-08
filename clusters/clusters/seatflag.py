"""Seat flags the mode row does not store.

Guides name facts the mode row does not store: release channel latest or
stable, Kimi role coder explore or plan, Tool Search left false, WebFetch
failing while WebSearch works, Claude hook imports pinned off on a Grok
terminal, and an Antigravity updater lock path with auto-update disabled.
Store them. Do not apply them.

Nothing is fetched or written. written and fetched stay false.

Python 3.11.
"""

from __future__ import annotations

from clusters.refuse import Refuse, guard_path
from clusters.store import Store

CHANNELS = ("latest", "stable")
ROLES = ("", "coder", "explore", "plan")


def set_seat_flags(
    store: Store,
    *,
    session_id: str,
    channel: str = "stable",
    role: str = "",
    tool_search: bool = False,
    web_fetch: bool = False,
    hooks_off: bool = False,
    auto_update: bool = False,
    lock_path: str = "",
) -> dict:
    """Append a seat_flag row. Nothing is fetched or written."""
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    if channel not in CHANNELS:
        raise Refuse("CHANNEL")
    if role not in ROLES:
        raise Refuse("ROLE")
    _bools(tool_search, web_fetch, hooks_off, auto_update)
    path = _lock_path(lock_path)
    row_id = f"flag-{session_id}"
    # Nothing is fetched or written. The lock path is stored and not opened.
    # written and fetched stay false.
    store.append(
        "seat_flag",
        {
            "id": row_id,
            "session_id": session_id,
            "channel": channel,
            "role": role,
            "tool_search": tool_search,
            "web_fetch": web_fetch,
            "hooks_off": hooks_off,
            "auto_update": auto_update,
            "lock_path": path,
            "written": False,
            "fetched": False,
        },
    )
    return _shown(store, session_id)


def get_seat_flags(store: Store, session_id: str) -> dict:
    """Return the row. written and fetched are forced false on read."""
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION")
    if store.view("seat_flag").get(f"flag-{session_id}") is None:
        raise Refuse("FLAG", "missing")
    return _shown(store, session_id)


def _shown(store: Store, session_id: str) -> dict:
    view = dict(store.view("seat_flag")[f"flag-{session_id}"])
    view["written"] = False
    view["fetched"] = False
    return view


def _bools(
    tool_search: object,
    web_fetch: object,
    hooks_off: object,
    auto_update: object,
) -> None:
    if (
        not isinstance(tool_search, bool)
        or not isinstance(web_fetch, bool)
        or not isinstance(hooks_off, bool)
        or not isinstance(auto_update, bool)
    ):
        raise Refuse("FLAG")


def _lock_path(text: object) -> str:
    """Accept an empty path or a guarded path. Do not open it."""
    if text == "":
        return ""
    if not isinstance(text, str):
        raise Refuse("PATH")
    # Do not open the path. A live path raises LIVE_TREE inside guard_path.
    return guard_path(text)
