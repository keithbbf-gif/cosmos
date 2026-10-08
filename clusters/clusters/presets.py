"""Navbar project-switcher outfit.

A shortcut has a colour, an icon, an agent door, resume mode, and Turbo.
This stores that outfit. It does not launch a terminal, open a session, or
call the harness. Turbo stored here does not change policy and does not pass
skip-permissions. Resume stored here does not claim a resume.
"""

from __future__ import annotations

from clusters.models import DOORS
from clusters.refuse import Refuse
from clusters.store import Store

_MARK = 32


def set_preset(
    store: Store,
    *,
    project_id: str,
    colour: str,
    icon: str,
    door: str,
    resume: bool = False,
    turbo: bool = False,
) -> dict:
    """Append the outfit. The public view never claims resume or applies turbo."""
    if store.view("project").get(project_id) is None:
        # The shortcut hangs off a project. This does not create one.
        raise Refuse("PROJECT", project_id)
    colour = _mark(colour, "colour")
    icon = _mark(icon, "icon")
    if not isinstance(door, str) or door not in DOORS:
        # The agent is a catalog door. Storing a name does not seat it.
        raise Refuse("UNKNOWN_DOOR", door if isinstance(door, str) else "")
    if not isinstance(resume, bool) or not isinstance(turbo, bool):
        # Real bools only. 1 or "yes" is not coerced into a mode.
        raise Refuse("PRESET", "flag")
    preset_id = f"preset-{project_id}"
    store.append(
        "preset",
        {
            "id": preset_id,
            "op": "set",
            "project_id": project_id,
            "colour": colour,
            "icon": icon,
            "door": door,
            "resume": resume,
            "turbo": turbo,
        },
    )
    return _public(store.view("preset")[preset_id])


def get_preset(store: Store, project_id: str) -> dict:
    """Return the stored outfit. Missing project and missing preset both refuse."""
    if store.view("project").get(project_id) is None:
        raise Refuse("PROJECT")
    row = store.view("preset").get(f"preset-{project_id}")
    if row is None:
        raise Refuse("PRESET", "missing")
    return _public(row)


def _mark(text: object, field: str) -> str:
    """One line, 1..32 characters. A newline or the wrong length is PRESET."""
    if (
        not isinstance(text, str)
        or "\n" in text
        or "\r" in text
        or not 1 <= len(text) <= _MARK
    ):
        raise Refuse("PRESET", field)
    return text


def _public(row: dict) -> dict:
    """Drop projection keys. Claim and apply stay false on every read."""
    view = {key: value for key, value in row.items() if not str(key).startswith("_")}
    view["resume_claimed"] = False
    view["applied"] = False
    return view
