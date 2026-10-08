"""Session mode, cancel intent, mobile follow, and keyboard bindings.

Door modes come from the catalog. An empty mode list accepts only default.
cancel does not kill anything. follow returns session facts with no secrets.
The GUI listens. This module only stores bindings.
"""

from __future__ import annotations

import hashlib

from clusters.catalog import add_shortcut, list_shortcuts
from clusters.models import DOORS
from clusters.refuse import Refuse
from clusters.sessions import get_session, list_sessions
from clusters.store import Store

_KEY_MAP = (
    ("ctrl+n", "new-session"),
    ("ctrl+k", "search-history"),
    ("ctrl+b", "task-board"),
    ("ctrl+shift+t", "turbo"),
)


def set_mode(store: Store, session_id: str, mode: str) -> dict:
    current = store.view("session").get(session_id)
    if current is None:
        raise Refuse("SESSION", session_id)
    spec = DOORS.get(str(current.get("door") or ""))
    if spec is None:
        raise Refuse("MODE", str(current.get("door") or ""))
    modes = spec["modes"]
    if modes:
        if mode not in modes:
            raise Refuse("MODE", str(mode))
    elif mode != "default":
        raise Refuse("MODE", str(mode))
    body = _plain(current)
    body["op"] = "mode"
    body["mode"] = mode
    store.append("session", body)
    return get_session(store, session_id)


def cancel(store: Store, session_id: str) -> dict:
    if session_id not in store.view("session"):
        raise Refuse("SESSION", session_id)
    store.append(
        "cancel",
        {
            "id": f"cancel-{session_id}",
            "session_id": session_id,
            "executed": False,
            "killed": False,
            "op": "intent",
        },
    )
    return {"session_id": session_id, "executed": False, "killed": False}


def follow(store: Store, *, token: str) -> dict:
    # A dark desktop refuses before the pair hash is considered.
    latest = store.latest_kind("desktop")
    online = latest.get("body", {}).get("online") if latest else None
    if online is not True:
        raise Refuse("OFFLINE", "desktop")
    if not isinstance(token, str):
        raise Refuse("PAIR", "token")
    digest = hashlib.sha256(token.encode()).hexdigest()
    paired = any(row.get("token_hash") == digest for row in store.view("device").values())
    if not paired:
        raise Refuse("PAIR", "token")
    hidden = {"token", "api_key"}
    sessions = [
        {key: value for key, value in row.items() if key not in hidden}
        for row in list_sessions(store)
    ]
    return {"sessions": sessions}


def seed_keys(store: Store) -> dict:
    have = {str(row.get("binding") or "") for row in list_shortcuts(store)}
    seeded = 0
    for binding, target in _KEY_MAP:
        if binding in have:
            continue
        add_shortcut(store, kind="key", binding=binding, target=target)
        have.add(binding)
        seeded += 1
    return {"seeded": seeded}


def _plain(body: dict) -> dict:
    return {key: value for key, value in body.items() if not str(key).startswith("_")}
