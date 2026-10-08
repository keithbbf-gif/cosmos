"""Read-only look at live ``cosmos_voice``, plus an injected confirm handle.

``probe`` parses the live file with ``ast``. It does not import ``cosmos``
and it does not construct a ledger. Production passes an already-built
``VoiceMode.handle`` into ``CosmosVoiceBind``. Consequential lines then use
that object's nonce. This module never opens ``live/``.
"""

from __future__ import annotations

import ast
from pathlib import Path

from cosmos_voice_duplex.confirm import ConfirmGate, GateResult, VoiceHandle
from cosmos_voice_duplex.session import DuplexSession

PROBED = (
    "SPOKEN_MAX",
    "MAX_TRANSCRIPT",
    "CONFIRM_TTL",
    "CONSEQUENTIAL_VERBS",
    "DESTRUCTIVE_VERBS",
)


def probe(path: str | Path) -> dict[str, object]:
    """Return the voice constants and the ``handle`` argument names."""

    source = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    found: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in PROBED:
                    found[target.id] = ast.literal_eval(node.value)
        if isinstance(node, ast.ClassDef) and node.name == "VoiceMode":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "handle":
                    found["handle_args"] = [arg.arg for arg in item.args.args]
    return found


class CosmosVoiceBind:
    """Confirm gate in front of an injected handle. No ledger of its own."""

    def __init__(self, handle: VoiceHandle, session_id: str = "duplex") -> None:
        self.handle = handle
        self.gate = ConfirmGate(handle, session_id=session_id)

    def on_user_text(self, text: str) -> GateResult:
        return self.gate.on_user_text(text)

    def attach(self, session: DuplexSession) -> None:
        session.voice = self.handle
        session.gate = ConfirmGate(self.handle, session_id=self.gate.session_id)
