"""Host notes for one session.

Guides say some abilities depend on the host, and one terminal can carry
a base URL and model id while another does not. This stores the operator's
note. Values are not stored and nothing is probed.

Refusals: a missing session is Refuse("SESSION", session_id). A host
outside HOSTS is Refuse("HOST"). A fact outside FACTS is Refuse("FACT").
A non-bool enabled flag is Refuse("FACT", "flag"). An env name that is
not one line of 1..80 characters matching ^[A-Z][A-Z0-9_]*$ is
Refuse("ENV"). A secret-shaped name is Refuse("SECRET", name). No value
parameter is accepted.
"""

from __future__ import annotations

import re

from clusters.refuse import Refuse
from clusters.store import Store

HOSTS = ("windows", "linux", "mac")
FACTS = ("voice", "sandbox", "git-bash", "plain-shell")

_ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")
_ENV_LIMIT = 80
_SECRET_NAMES = frozenset(
    {
        "TOKEN",
        "SECRET",
        "PASSWORD",
        "API_KEY",
        "AUTHORIZATION",
        "CREDENTIAL",
        "ACCESS_TOKEN",
        "REFRESH_TOKEN",
    }
)
_SECRET_SUFFIXES = ("_TOKEN", "_SECRET", "_PASSWORD", "_API_KEY")


def set_host(
    store: Store,
    *,
    session_id: str,
    host: str,
    fact: str,
    enabled: bool,
) -> dict:
    """Record one host ability. probed stays false. Nothing is probed."""
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    if host not in HOSTS:
        raise Refuse("HOST")
    if fact not in FACTS:
        raise Refuse("FACT")
    if not isinstance(enabled, bool):
        raise Refuse("FACT", "flag")
    row_id = f"host-{session_id}-{fact}"
    # Values are not stored and nothing is probed. probed stays false.
    store.append(
        "host_note",
        {
            "id": row_id,
            "session_id": session_id,
            "host": host,
            "fact": fact,
            "enabled": enabled,
            "probed": False,
        },
    )
    return dict(store.view("host_note")[row_id])


def set_env_name(store: Store, *, session_id: str, name: str) -> dict:
    """Record that an env name is present. The value is not stored."""
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    kept = _name(name)
    row_id = f"env-{session_id}-{kept}"
    # The row has no value field. Values are not stored and nothing is probed.
    store.append(
        "env_name",
        {
            "id": row_id,
            "session_id": session_id,
            "name": kept,
            "present": True,
        },
    )
    return dict(store.view("env_name")[row_id])


def _name(name: str) -> str:
    if not isinstance(name, str):
        raise Refuse("ENV")
    if "\n" in name or "\r" in name or not 1 <= len(name) <= _ENV_LIMIT:
        raise Refuse("ENV")
    if _ENV_NAME.fullmatch(name) is None:
        raise Refuse("ENV")
    if name in _SECRET_NAMES or name.endswith(_SECRET_SUFFIXES):
        raise Refuse("SECRET", name)
    return name
