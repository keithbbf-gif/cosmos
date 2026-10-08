"""Credential route for one session.

Guides name where a CLI keeps login state. This stores the route and a
path pointer, never the secret bytes. Managed account bytes stay out.
Secrets are not stored. The file is not opened.

Refusals: a missing session is Refuse("SESSION", session_id). A route
that is not one line of 1..80 characters is Refuse("ROUTE"). A route
that contains "=" is Refuse("SECRET", "route"). A path that fails
clusters.refuse.guard_path is refused there, and a live path raises
LIVE_TREE. get_route on a session with no row is Refuse("ROUTE", "missing").
"""

from __future__ import annotations

from clusters.refuse import Refuse, guard_path
from clusters.store import Store

_ROUTE_LIMIT = 80


def set_route(store: Store, *, session_id: str, route: str, path: str) -> dict:
    """Record the login route and a path pointer. Secret bytes stay out."""
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    label = _label(route)
    # guard_path checks the string only. Do not open the file or read a credential.
    kept = guard_path(path)
    row_id = f"route-{session_id}"
    # Pointer only. present means the route is recorded. copied stays false.
    # Body keys are id, session_id, route, path, present, and copied.
    # Secret field names stay off the body. scrub refuses them.
    store.append(
        "cred_route",
        {
            "id": row_id,
            "session_id": session_id,
            "route": label,
            "path": kept,
            "present": True,
            "copied": False,
        },
    )
    return dict(store.view("cred_route")[row_id])


def get_route(store: Store, session_id: str) -> dict:
    """Return the stored route. A missing session or row is a refusal."""
    if store.view("session").get(session_id) is None:
        raise Refuse("SESSION", session_id)
    row = store.view("cred_route").get(f"route-{session_id}")
    if row is None:
        raise Refuse("ROUTE", "missing")
    return dict(row)


def _label(route: str) -> str:
    if not isinstance(route, str):
        raise Refuse("ROUTE")
    # A label such as browser-login, device-auth, or env-key.
    # A space-separated token that looks like key=value is not a route.
    for token in route.split():
        if "=" in token:
            raise Refuse("SECRET", "route")
    if "=" in route:
        raise Refuse("SECRET", "route")
    if "\n" in route or "\r" in route or not 1 <= len(route) <= _ROUTE_LIMIT:
        raise Refuse("ROUTE")
    return route
