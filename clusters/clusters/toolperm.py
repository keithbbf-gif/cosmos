"""Per-tool Allow, Ask, or Deny for one MCP server.

The marketplace page says each tool on a server can be Allow, Ask, or Deny.
The category matrix does not store that. This stores the operator's choice
for one tool name. It does not call the tool.

A missing project is Refuse("PROJECT", project_id) on set and
Refuse("PROJECT") on read. A server id that is not one line of 1..80
characters is Refuse("TOOL", "server"). A tool name that is not one line
of 1..80 characters is Refuse("TOOL", "name"). A level outside allow, ask,
and deny is Refuse("TOOL", "level"). A missing row stays ask. It is not
an allow.

Python 3.11.
"""

from __future__ import annotations

from clusters.refuse import Refuse
from clusters.store import Store

LEVELS = ("allow", "ask", "deny")

_LIMIT = 80


def set_tool(
    store: Store,
    *,
    project_id: str,
    server_id: str,
    tool: str,
    level: str,
) -> dict:
    """Append one tool choice. The tool is not called."""
    if store.view("project").get(project_id) is None:
        raise Refuse("PROJECT", project_id)
    server = _line(server_id, "server")
    name = _line(tool, "name")
    if level not in LEVELS:
        raise Refuse("TOOL", "level")
    row_id = f"tool-{project_id}-{server}-{name}"
    # The tool is not called. The choice is stored and not executed.
    store.append(
        "tool_perm",
        {
            "id": row_id,
            "project_id": project_id,
            "server_id": server,
            "tool": name,
            "level": level,
        },
    )
    return dict(store.view("tool_perm")[row_id])


def tool_level(
    store: Store,
    *,
    project_id: str,
    server_id: str,
    tool: str,
) -> dict:
    """Return the stored level. A missing row is ask and is not an allow."""
    if store.view("project").get(project_id) is None:
        raise Refuse("PROJECT")
    row = store.view("tool_perm").get(f"tool-{project_id}-{server_id}-{tool}")
    if row is None:
        # The tool is not called. Do not invent an allow.
        return {
            "project_id": project_id,
            "server_id": server_id,
            "tool": tool,
            "level": "ask",
            "stored": False,
        }
    return {
        "project_id": row["project_id"],
        "server_id": row["server_id"],
        "tool": row["tool"],
        "level": row["level"],
        "stored": True,
    }


def _line(text: object, detail: str) -> str:
    """One line, 1..80 characters. A newline or the wrong length is TOOL."""
    if (
        not isinstance(text, str)
        or "\n" in text
        or "\r" in text
        or not 1 <= len(text) <= _LIMIT
    ):
        raise Refuse("TOOL", detail)
    return text
