"""Voice tools a COSMOS Code host can register.

``status`` reads the spend snapshot. ``check`` asks the host. ``propose``
is marked confirm, so the duplex session will not run it until a spoken yes.
None of these handlers write the live tree or the COSMOS Code product tree.
"""

from __future__ import annotations

import json

from cosmos_voice_duplex.plugin.host import CodeHost
from cosmos_voice_duplex.session import DuplexSession
from cosmos_voice_duplex.tools import Tool, ToolRegistry

_OBJECT: dict[str, object] = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}
_TEXT: dict[str, object] = {
    "type": "object",
    "properties": {"text": {"type": "string"}},
    "required": ["text"],
    "additionalProperties": False,
}


class VoicePlugin:
    def __init__(self, host: CodeHost) -> None:
        self.host = host
        self.registry = ToolRegistry()
        self.registry.add(
            Tool(
                "status",
                "Read the voice spend snapshot. Does not change a balance.",
                _OBJECT,
                self._status,
            )
        )
        self.registry.add(
            Tool(
                "check",
                "Ask the COSMOS Code host to check the current proposal.",
                _OBJECT,
                self._check,
            )
        )
        self.registry.add(
            Tool(
                "propose",
                "Hold a proposed change until the user confirms out loud.",
                _TEXT,
                self._propose,
                confirm=True,
            )
        )

    def attach(self, session: DuplexSession) -> None:
        session.on_user = self.host.on_user_text
        session.on_assistant = self.host.on_assistant_text
        for tool in self.registry.tools.values():
            session.tools.add(tool)

    def _status(self, arguments: dict[str, object]) -> str:
        del arguments
        return json.dumps({"ok": True, "spend": self.host.spend_snapshot()})

    def _check(self, arguments: dict[str, object]) -> str:
        return self.host.call_tool("check", arguments)

    def _propose(self, arguments: dict[str, object]) -> str:
        text = arguments.get("text")
        shown = text if isinstance(text, str) else ""
        return json.dumps({"ok": True, "proposed": True, "text": shown})
