"""The chat body the weak door would send. This module does not send it.

System content is the wrapper only. Style, when present, is on the user
side with the task and the contract line. The tool list is the JSON hand
schemas. The pin is the model field. There is no fallback model and no
``:floor`` suffix. ``allow_fallbacks`` is false.

The API key is not an argument. A caller that posts this body attaches the
key outside this package.
"""

from __future__ import annotations

import json
from pathlib import Path

from cosmos_harness.layers import Stack


def load_tools(schema_path: Path) -> list[dict[str, object]]:
    """Read the hand schemas. The file is the L6 layer."""
    payload = json.loads(schema_path.read_text(encoding="utf-8"))
    tools = payload.get("tools")
    if not isinstance(tools, list):
        raise ValueError("L6 tools")
    return tools


def body(stack: Stack, tools: list[dict[str, object]]) -> dict[str, object]:
    """One request object. Style is not in the system message."""
    user = stack.task
    if stack.style:
        user = stack.style + "\n" + user
    user = user + "\n" + stack.contract_line() + "\n"
    return {
        "model": stack.model,
        "messages": [
            {"role": "system", "content": stack.wrap},
            {"role": "user", "content": user},
        ],
        "tools": tools,
        "provider": {"allow_fallbacks": False},
    }


def system_is_wrap(payload: dict[str, object], stack: Stack) -> bool:
    """True when the system turn is the wrapper and does not carry the style."""
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        return False
    system = messages[0].get("content") if isinstance(messages[0], dict) else ""
    if system != stack.wrap:
        return False
    if stack.style and stack.style in str(system):
        return False
    return True
