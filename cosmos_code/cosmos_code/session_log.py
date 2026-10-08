"""Append-only session log. A failed attempt never becomes model history."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SessionError(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(code if not detail else f"{code}: {detail}")


class SessionLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")

    def append(self, event: dict[str, Any]) -> None:
        if "ev" not in event:
            raise SessionError("NO_EVENT")
        line = json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n"
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)

    def events(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        raw = self.path.read_text(encoding="utf-8")
        for line in raw.splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def has(self, name: str) -> bool:
        return any(row.get("ev") == name for row in self.events())

    def derive_messages(self) -> list[dict[str, str]]:
        """What the model is allowed to see. Attempts stay out."""
        out: list[dict[str, str]] = []
        for row in self.events():
            ev = row.get("ev")
            if ev == "assistant/attempt":
                continue
            if ev in ("system/message", "user/message", "assistant/message"):
                role = str(ev).split("/", 1)[0]
                out.append({"role": role, "bytes": str(row.get("bytes") or "")})
        return out

    def compact(self, summary: str) -> None:
        """Append a summary after the frozen head. Never splice earlier lines."""
        before = self.path.read_text(encoding="utf-8")
        self.append({"ev": "summary", "bytes": summary})
        after = self.path.read_text(encoding="utf-8")
        if not after.startswith(before):
            raise SessionError("SPLICE", "compact rewrote history")
