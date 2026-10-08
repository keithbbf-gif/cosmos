"""Local road queue.

Orders wait in one JSONL file until something else sends them. String values
are redacted before they touch the disk. This module never opens a socket.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from cosmos_voice.errors import VoiceError
from cosmos_voice.redact import redact


def _stamp() -> str:
    """UTC time to the second. The id, not this stamp, identifies a row."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _redact_value(value: object) -> object:
    """Redact every string. Nested objects are walked. Other JSON scalars stay."""
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, dict):
        cleaned: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise VoiceError("BAD_REQUEST", "order key is not a string")
            cleaned[key] = _redact_value(item)
        return cleaned
    if value is None or isinstance(value, (bool, int, float)):
        return value
    raise VoiceError("BAD_REQUEST", "order value is not json")


def _redact_order(order: dict[str, object]) -> dict[str, object]:
    """Return a copy of ``order`` with every string value redacted."""
    cleaned: dict[str, object] = {}
    for key, value in order.items():
        cleaned[key] = _redact_value(value)
    return cleaned


def _dump(row: dict[str, object]) -> str:
    """One JSON object, with no trailing newline."""
    return json.dumps(row, sort_keys=True, separators=(",", ":"))


def _parse_row(line: str) -> dict[str, object]:
    """Parse one queue line. A bad line is refused. It is not dropped."""
    try:
        loaded: object = json.loads(line)
    except json.JSONDecodeError:
        raise VoiceError("BAD_REQUEST", "road row is not json") from None
    if not isinstance(loaded, dict):
        raise VoiceError("BAD_REQUEST", "road row is not an object")
    row: dict[str, object] = {}
    for key, item in loaded.items():
        if not isinstance(key, str):
            raise VoiceError("BAD_REQUEST", "road key is not a string")
        row[key] = item
    return row


class RoadQueue:
    """Append-only orders at ``root / road.jsonl``. Sent rows stay on disk."""

    def __init__(self, root: Path) -> None:
        """Bind the queue file. ``root`` must already be a directory."""
        if not root.is_dir():
            raise VoiceError("BAD_REQUEST", "road root is not a directory")
        self._path = root / "road.jsonl"

    def enqueue(self, order: dict[str, object]) -> str:
        """Append one redacted order and return its id. No socket is opened."""
        row_id = uuid4().hex
        row: dict[str, object] = {
            "id": row_id,
            "at": _stamp(),
            "order": _redact_order(order),
            "sent": False,
        }
        with self._path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(_dump(row) + "\n")
        return row_id

    def list_pending(self) -> list[dict[str, object]]:
        """Return rows whose ``sent`` flag is false."""
        return [row for row in self._read() if row.get("sent") is False]

    def mark_sent(self, id: str) -> None:
        """Rewrite the file with this id marked sent. The line is kept.

        An id that is not in the file raises ``VoiceError`` ``BAD_REQUEST``.
        """
        rows = self._read()
        found = False
        updated: list[dict[str, object]] = []
        for row in rows:
            if row.get("id") == id:
                found = True
                changed = dict(row)
                changed["sent"] = True
                updated.append(changed)
            else:
                updated.append(row)
        if not found:
            raise VoiceError("BAD_REQUEST", "unknown id")
        self._write(updated)

    def _read(self) -> list[dict[str, object]]:
        """Read every row. A missing file is an empty queue."""
        if not self._path.is_file():
            return []
        text = self._path.read_text(encoding="utf-8")
        rows: list[dict[str, object]] = []
        for line in text.splitlines():
            if line.strip() == "":
                continue
            rows.append(_parse_row(line))
        return rows

    def _write(self, rows: list[dict[str, object]]) -> None:
        """Replace the file with ``rows``. A crash mid-write keeps the old file."""
        payload = "".join(_dump(row) + "\n" for row in rows)
        temporary = self._path.with_name(self._path.name + ".tmp")
        temporary.write_text(payload, encoding="utf-8", newline="\n")
        temporary.replace(self._path)
