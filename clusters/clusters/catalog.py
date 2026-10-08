"""Accounts, MCP flags, shortcuts, mobile pair, and notifications.

Account rows are path pointers, never secret bytes. A secret field is Refuse("SECRET").
The pair token is returned once and stored as sha256.
A claim without source and observed is UNMEASURED. Project slots 1..6 stay on mesh.
"""

from __future__ import annotations

import hashlib
import secrets

from clusters.models import MCP, public_doors, public_mcp
from clusters.refuse import Refuse, guard_path, scrub
from clusters.sessions import bind_account as bind_session_account
from clusters.store import Store, new_id

_ACCOUNT_PROVIDERS = ("claude", "codex")
_SHORTCUT_KINDS = ("agent", "key")
_NOTE_KINDS = ("finished", "needs_input", "failed")


def list_doors() -> list[dict]:
    """Doors. Return the catalog. seated false is not a claim the door ran."""
    return public_doors()


def add_account(
    store: Store,
    *,
    provider: str,
    label: str,
    profile_dir: str,
    **extra: object,
) -> dict:
    """Accounts. Store a profile path. Secret bytes are Refuse("SECRET")."""
    if extra:
        probe: dict[str, object] = {
            "provider": provider,
            "label": label,
            "profile_dir": profile_dir,
        }
        probe.update(extra)
        scrub(probe)
    if provider not in _ACCOUNT_PROVIDERS:
        raise Refuse("PROVIDER", str(provider))
    if not isinstance(label, str) or not label.strip():
        raise Refuse("ACCOUNT", "label")
    kept = guard_path(profile_dir)
    same = [
        row
        for row in store.view("account").values()
        if row.get("provider") == provider
    ]
    account_id = new_id("acc")
    body = {
        "id": account_id,
        "op": "add",
        "provider": provider,
        "label": label.strip(),
        "profile_dir": kept,
        "is_default": not same,
    }
    store.append("account", body)
    return dict(store.view("account")[account_id])


def bind_account(store: Store, session_id: str, account_id: str) -> dict:
    """Accounts. Match the door. A non-idle session is Refuse("ACCOUNT_SWITCH")."""
    account = store.view("account").get(account_id)
    if account is None:
        raise Refuse("ACCOUNT", account_id)
    session = store.view("session").get(session_id)
    if session is None:
        raise Refuse("SESSION", session_id)
    if session.get("door") != account.get("provider"):
        raise Refuse("PROVIDER", str(account.get("provider") or ""))
    return bind_session_account(store, session_id, account_id)


def set_mcp(store: Store, *, project_id: str, server_id: str, enabled: bool) -> dict:
    """MCP flags. Store enabled only. An unknown server is Refuse("MCP")."""
    if store.view("project").get(project_id) is None:
        raise Refuse("PROJECT", project_id)
    if server_id not in MCP:
        raise Refuse("MCP", server_id)
    row_id = f"mcp-{project_id}-{server_id}"
    body = {
        "id": row_id,
        "op": "set",
        "project_id": project_id,
        "server_id": server_id,
        "enabled": bool(enabled),
    }
    store.append("mcp", body)
    return dict(store.view("mcp")[row_id])


def enable_all_mcp(store: Store, *, project_id: str) -> dict:
    """MCP flags. Enable the catalog. No download and no token."""
    enabled: list[str] = []
    for server_id in MCP:
        set_mcp(store, project_id=project_id, server_id=server_id, enabled=True)
        enabled.append(server_id)
    return {"enabled": enabled}


def list_mcp(store: Store, project_id: str) -> list[dict]:
    """MCP flags. Catalog rows plus the enable bit. An unset flag stays false."""
    flags: dict[str, bool] = {}
    for row in store.view("mcp").values():
        if row.get("project_id") == project_id:
            flags[str(row.get("server_id"))] = bool(row.get("enabled"))
    listed: list[dict] = []
    for row in public_mcp():
        item = dict(row)
        item["enabled"] = flags.get(item["id"], False)
        listed.append(item)
    return listed


def add_shortcut(store: Store, *, kind: str, binding: str, target: str) -> dict:
    """Shortcuts. Accept agent or key. Any other kind is Refuse("SHORTCUT")."""
    if kind not in _SHORTCUT_KINDS:
        raise Refuse("SHORTCUT", str(kind))
    kept_binding = _one_line(binding, "binding")
    kept_target = _one_line(target, "target")
    shortcut_id = new_id("shp")
    body = {
        "id": shortcut_id,
        "op": "add",
        "kind": kind,
        "binding": kept_binding,
        "target": kept_target,
    }
    store.append("shortcut", body)
    return dict(store.view("shortcut")[shortcut_id])


def list_shortcuts(store: Store) -> list[dict]:
    """Shortcuts. Return agent and key rows. Project slots 1..6 are not here."""
    rows = [dict(row) for row in store.view("shortcut").values()]
    rows.sort(key=lambda row: str(row.get("id") or ""))
    return rows


def pair_mobile(store: Store) -> dict:
    """Mobile pair. Return the token once. Store only its sha256."""
    token = secrets.token_hex(16)
    digest = hashlib.sha256(token.encode()).hexdigest()
    # The jsonl is checked for the raw token as a substring. The digest must not contain it.
    while token in digest:
        token = secrets.token_hex(16)
        digest = hashlib.sha256(token.encode()).hexdigest()
    device_id = new_id("dev")
    store.append(
        "device",
        {"id": device_id, "op": "pair", "token_hash": digest},
    )
    return {"device_id": device_id, "token": token}


def set_desktop(store: Store, *, online: bool) -> dict:
    """Mobile pair. Record the desktop online flag. The flag is not a secret."""
    flag = bool(online)
    store.append("desktop", {"id": "desktop", "op": "set", "online": flag})
    return {"online": flag}


def mobile_message(store: Store, *, token: str, session_id: str, body: str) -> dict:
    """Mobile pair. Match sha256 or Refuse("PAIR"). Offline is Refuse("OFFLINE")."""
    if not isinstance(token, str):
        raise Refuse("PAIR", "token")
    digest = hashlib.sha256(token.encode()).hexdigest()
    matched = None
    for row in store.view("device").values():
        if row.get("token_hash") == digest:
            matched = row
            break
    if matched is None:
        raise Refuse("PAIR", "token")
    latest = store.latest_kind("desktop")
    if latest is None or not bool(latest.get("body", {}).get("online")):
        raise Refuse("OFFLINE", "desktop")
    if session_id not in store.view("session"):
        raise Refuse("SESSION", session_id)
    if not isinstance(body, str) or not body.strip():
        raise Refuse("MESSAGE", "empty")
    store.append(
        "mobile_message",
        {
            "id": new_id("mms"),
            "op": "send",
            "session_id": session_id,
            "body": body,
            "device_id": matched["id"],
        },
    )
    return {"accepted": True, "session_id": session_id}


def emit(store: Store, *, session_id: str, kind: str, detail: str) -> dict:
    """Notifications. Record a note. A note is not source and observed."""
    if kind not in _NOTE_KINDS:
        raise Refuse("NOTE", str(kind))
    if session_id not in store.view("session"):
        raise Refuse("SESSION", session_id)
    if not isinstance(detail, str):
        raise Refuse("NOTE", "detail")
    note_id = new_id("ntf")
    body = {
        "id": note_id,
        "op": "emit",
        "session_id": session_id,
        "note": kind,
        "detail": detail,
        "seen": False,
    }
    store.append("notification", body)
    return dict(store.view("notification")[note_id])


def list_notes(store: Store, unseen_only: bool = False) -> list[dict]:
    """Notifications. List notes. unseen_only keeps rows that are not seen."""
    rows = [dict(row) for row in store.view("notification").values()]
    if unseen_only:
        rows = [row for row in rows if not row.get("seen")]
    rows.sort(key=lambda row: int(row.get("_seq") or 0))
    return rows


def see(store: Store, note_id: str) -> dict:
    """Notifications. Mark one note seen. A missing id is Refuse("NOTE")."""
    current = store.view("notification").get(note_id)
    if current is None:
        raise Refuse("NOTE", note_id)
    body = {key: value for key, value in current.items() if not str(key).startswith("_")}
    body["op"] = "see"
    body["seen"] = True
    store.append("notification", body)
    return dict(store.view("notification")[note_id])


def _one_line(text: str, detail: str) -> str:
    if not isinstance(text, str) or not text.strip() or "\n" in text or "\r" in text:
        raise Refuse("SHORTCUT", detail)
    return text.strip()
