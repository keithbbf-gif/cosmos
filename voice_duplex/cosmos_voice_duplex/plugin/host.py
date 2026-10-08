"""The seam a later COSMOS Code host implements.

The plugin calls this. It does not open files, does not write ``live/``,
and does not keep a ledger. ``spend_snapshot`` is read-only.
"""

from __future__ import annotations

from typing import Protocol


class CodeHost(Protocol):
    def on_user_text(self, text: str) -> None: ...

    def on_assistant_text(self, text: str) -> None: ...

    def call_tool(self, name: str, arguments: dict[str, object]) -> str: ...

    def spend_snapshot(self) -> dict[str, object]: ...
