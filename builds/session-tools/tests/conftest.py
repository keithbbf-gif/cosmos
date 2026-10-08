"""Hermetic fixtures. A few turns each. No live store."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_PKG = Path(__file__).resolve().parent.parent
_REPO = _PKG.parent.parent
sys.path.insert(0, str(_PKG))
sys.path.insert(0, str(_REPO / "cosmos"))

GROK_VID = "11111111-2222-3333-4444-555555555555"
KEY_TOKEN = "sk-ant-TestKeyValue99"


def build_grok(root: Path, texts: list[str]) -> tuple[Path, str]:
    day = root / "cwd" / GROK_VID
    day.mkdir(parents=True)
    info = {
        "info": {
            "id": GROK_VID,
            "generated_title": "Tiny grok",
            "cwd": "C:/work/fixture",
        }
    }
    (day / "summary.json").write_text(json.dumps(info), encoding="utf-8")
    roles = ("user", "assistant", "user")
    lines = []
    for i, text in enumerate(texts):
        lines.append(json.dumps(
            {"type": roles[i % 3], "text": text},
            separators=(",", ":"),
        ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    (day / "chat_history.jsonl").write_bytes(raw)
    return root, GROK_VID


def build_cow(root: Path) -> Path:
    trans = root / "ordered_transcripts"
    trans.mkdir(parents=True)
    (trans / "s1.md").write_bytes(b"turn one\nturn two\nturn three\n")
    (trans / "leg.md").write_bytes(b"legal body stays unread\n")
    rows = [
        {
            "session_id": "s1",
            "seq": 1,
            "filename": "s1.md",
            "title": "One",
            "stream": "cm",
        },
        {
            "session_id": "legal-case-1",
            "seq": 2,
            "filename": "leg.md",
            "title": "L",
            "stream": "legal",
        },
    ]
    (root / "COW_SESSION_CATALOG.json").write_text(
        json.dumps(rows), encoding="utf-8")
    return root


@pytest.fixture
def cow_store(tmp_path: Path) -> Path:
    return build_cow(tmp_path / "cow")


@pytest.fixture
def grok_store(tmp_path: Path) -> tuple[Path, str]:
    return build_grok(
        tmp_path / "grok",
        ["hello fixture", "hi back", "third turn"],
    )


@pytest.fixture
def grok_with_key(tmp_path: Path) -> tuple[Path, str, str]:
    root, vid = build_grok(
        tmp_path / "grok-key",
        [f"please use {KEY_TOKEN} now", "ack", "done"],
    )
    return root, vid, KEY_TOKEN
