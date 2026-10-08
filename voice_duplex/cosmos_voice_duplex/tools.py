"""Client function tools. Server-side xAI tools (web_search, x_search) are flags.

A tool marked ``confirm=True`` is held until the spoken confirm gate says yes.
Handlers return a JSON string. They do not write the live COSMOS tree.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field

Handler = Callable[[dict[str, object]], str]


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, object]
    handler: Handler
    confirm: bool = False

    def schema(self) -> dict[str, object]:
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


@dataclass
class ToolRegistry:
    tools: dict[str, Tool] = field(default_factory=dict)
    server_tools: list[dict[str, object]] = field(default_factory=list)

    def add(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def schemas(self) -> list[dict[str, object]]:
        return [*self.server_tools, *[tool.schema() for tool in self.tools.values()]]

    def call(self, name: str, arguments: str, *, confirmed: bool = False) -> str:
        tool = self.tools.get(name)
        if tool is None:
            return json.dumps({"ok": False, "error": f"unknown tool {name}"})
        if tool.confirm and not confirmed:
            return json.dumps({"ok": False, "error": "confirm required"})
        try:
            payload = json.loads(arguments) if arguments else {}
        except json.JSONDecodeError as exc:
            return json.dumps({"ok": False, "error": f"bad arguments: {exc}"})
        if not isinstance(payload, dict):
            return json.dumps({"ok": False, "error": "arguments must be an object"})
        return tool.handler(payload)
