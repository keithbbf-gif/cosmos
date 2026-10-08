"""Headless intent for one session.

The Grok Build headless guide says `grok -p` is one turn that prints and
exits, with output formats plain, json, and streaming-json, plus
--max-turns and --sandbox. This stores that intent. It does not run it.

grok.exe does not start. No API key is stored. subprocess is not imported.

A missing session on plan is Refuse("SESSION", session_id). A missing
session on read is Refuse("SESSION"). output_format outside FORMATS is
Refuse("FORMAT"). max_turns must be an int, not a bool, from 1 through 50,
else Refuse("TURNS"). sandbox is "" or one line of 1..80 characters, else
Refuse("SANDBOX"). A missing row is Refuse("HEADLESS", "missing").

The row has no api_key, token, or command. It does not include
--dangerously-skip-permissions or --full-auto. started and executed stay
false. A later fold that says otherwise is still false on read.

Python 3.11.
"""

from __future__ import annotations

from clusters.refuse import Refuse
from clusters.store import Store

FORMATS = ("plain", "json", "streaming-json")

_TURN_LIMIT = 50
_SANDBOX_LIMIT = 80
_BANNED = (
    "--dangerously-skip-permissions",
    "--full-auto",
    "grok.exe",
)


def plan_headless(
    store: Store,
    *,
    session_id: str,
    output_format: str = "plain",
    max_turns: int = 1,
    sandbox: str = "",
) -> dict:
    """Append one headless intent and return the view. started is false."""
    _need_session(store, session_id, detail=True)
    if output_format not in FORMATS:
        raise Refuse("FORMAT")
    turns = _turns(max_turns)
    mode = _sandbox(sandbox)
    row_id = f"headless-{session_id}"
    # grok.exe does not start. The row is intent, not a command.
    store.append(
        "headless",
        {
            "id": row_id,
            "session_id": session_id,
            "output_format": output_format,
            "max_turns": turns,
            "sandbox": mode,
            "executed": False,
            "started": False,
        },
    )
    return _public(store.view("headless")[row_id])


def get_headless(store: Store, session_id: str) -> dict:
    """Return the stored intent. started and executed are false on read."""
    _need_session(store, session_id, detail=False)
    row = store.view("headless").get(f"headless-{session_id}")
    if row is None:
        raise Refuse("HEADLESS", "missing")
    return _public(row)


def _need_session(store: Store, session_id: str, *, detail: bool) -> None:
    if store.view("session").get(session_id) is None:
        if detail:
            raise Refuse("SESSION", session_id)
        raise Refuse("SESSION")


def _turns(max_turns: object) -> int:
    """An int from 1 through 50. A bool is not an int here."""
    if isinstance(max_turns, bool) or not isinstance(max_turns, int):
        raise Refuse("TURNS")
    if not 1 <= max_turns <= _TURN_LIMIT:
        raise Refuse("TURNS")
    return max_turns


def _sandbox(text: object) -> str:
    """Empty, or one line of 1..80 characters. A banned flag is not stored."""
    if not isinstance(text, str):
        raise Refuse("SANDBOX")
    if text == "":
        return ""
    if "\n" in text or "\r" in text or not 1 <= len(text) <= _SANDBOX_LIMIT:
        raise Refuse("SANDBOX")
    folded = text.lower()
    for flag in _BANNED:
        if flag in folded:
            raise Refuse("SANDBOX")
    return text


def _public(row: dict) -> dict:
    """Force started and executed false. grok.exe does not start."""
    view = dict(row)
    view["started"] = False
    view["executed"] = False
    view.pop("api_key", None)
    view.pop("token", None)
    view.pop("command", None)
    return view
