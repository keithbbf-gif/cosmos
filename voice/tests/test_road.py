"""Road queue tests. The file is local and secrets do not land in it."""

from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from cosmos_voice.errors import VoiceError
from cosmos_voice.road import RoadQueue


@contextmanager
def _root() -> Iterator[Path]:
    """A temp directory this test removes."""
    root = Path(tempfile.mkdtemp(prefix="cosmos-voice-road-"))
    try:
        yield root
    finally:
        shutil.rmtree(root)


def _load(line: str) -> dict[str, object]:
    """Parse one queue line for an assertion."""
    loaded: object = json.loads(line)
    if not isinstance(loaded, dict):
        raise AssertionError("row")
    row: dict[str, object] = {}
    for key, item in loaded.items():
        if not isinstance(key, str):
            raise AssertionError("key")
        row[key] = item
    return row


def test_enqueue_redacts_and_mark_sent_keeps_the_line() -> None:
    """A sk- key is scrubbed, and mark_sent keeps every row."""
    secret = "sk-" + ("Abcd1234" * 2)
    with _root() as root:
        queue = RoadQueue(root)
        first = queue.enqueue({"task": "ping", "note": f"token {secret}"})
        second = queue.enqueue({"task": "later", "note": "plain"})
        text = (root / "road.jsonl").read_text(encoding="utf-8")
        assert secret not in text
        assert "sk-" not in text
        assert len(text.splitlines()) == 2
        pending = queue.list_pending()
        assert [row["id"] for row in pending] == [first, second]
        queue.mark_sent(first)
        lines = (root / "road.jsonl").read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2
        assert secret not in "\n".join(lines)
        assert "sk-" not in "\n".join(lines)
        kept = [_load(line) for line in lines]
        assert kept[0]["id"] == first
        assert kept[0]["sent"] is True
        assert kept[1]["id"] == second
        assert kept[1]["sent"] is False
        order = kept[0]["order"]
        assert isinstance(order, dict)
        assert order.get("task") == "ping"
        note = order.get("note")
        assert isinstance(note, str)
        assert secret not in note
        still = queue.list_pending()
        assert len(still) == 1
        assert still[0]["id"] == second


def test_mark_sent_unknown_is_refused() -> None:
    """An id that was never queued is BAD_REQUEST and writes nothing."""
    with _root() as root:
        queue = RoadQueue(root)
        with pytest.raises(VoiceError) as caught:
            queue.mark_sent("missing")
        assert caught.value.kind == "BAD_REQUEST"
        assert not (root / "road.jsonl").exists()
