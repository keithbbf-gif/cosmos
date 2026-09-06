#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Grok TUI adapter — ~/.grok/sessions/<cwd>/<uuid>/ summary.json + chat_history.jsonl."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from refusals import SessionToolsRefusal
from schema import head, legal_id, sha256_path, turn

FAMILY = "grok_tui"
_ROLE = {
    "user": "user", "assistant": "assistant", "system": "system",
    "tool_result": "tool_result", "tool": "tool_result",
    "tool_call": "tool_call", "function_call": "tool_call",
}


def _sessions(store: Path) -> list[Path]:
    if not store.is_dir():
        raise SessionToolsRefusal("NO_STORE", str(store))
    found = []
    for p in store.rglob("summary.json"):
        d = p.parent
        if (d / "chat_history.jsonl").is_file():
            found.append(d)
    return sorted(found)


def _vid(d: Path) -> str:
    try:
        info = json.loads((d / "summary.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        info = {}
    inner = info.get("info") if isinstance(info.get("info"), dict) else info
    return str(inner.get("id") or d.name)


def scan(store: Path) -> dict:
    dirs = _sessions(store)
    ids = [legal_id("grok", _vid(d)) for d in dirs[:5]]
    nbytes = sum((d / "chat_history.jsonl").stat().st_size for d in dirs)
    return {
        "family": FAMILY,
        "status": "OK",
        "path": str(store),
        "n": len(dirs),
        "n_legal": 0,
        "bytes": nbytes,
        "sample_ids": ids,
    }


def load(store: Path, rec_id: str) -> tuple[dict, list]:
    want = rec_id[5:] if rec_id.startswith("grok-") else rec_id
    hit = None
    for d in _sessions(store):
        vid = _vid(d)
        if vid == want or legal_id("grok", vid) == rec_id:
            hit = d
            break
    if hit is None:
        raise SessionToolsRefusal("NOT_FOUND", rec_id)
    hist = hit / "chat_history.jsonl"
    n, sha = sha256_path(hist)
    src = {"idx": 0, "path": str(hist), "kind": "jsonl", "len": n, "sha256": sha, "fidelity": "span"}
    summary = json.loads((hit / "summary.json").read_text(encoding="utf-8"))
    inner = summary.get("info") if isinstance(summary.get("info"), dict) else summary
    vid = str(inner.get("id") or hit.name)
    turns = []
    off = 0
    truncated = False
    raw = hist.read_bytes()
    for line in raw.splitlines(True):
        ln = len(line)
        try:
            obj = json.loads(line.decode("utf-8"))
        except ValueError:
            truncated = True
            break
        typ = str(obj.get("type") or obj.get("role") or "meta")
        role = _ROLE.get(typ, "meta")
        text = obj.get("text") or obj.get("content") or obj.get("message")
        if isinstance(text, list):
            text = json.dumps(text, ensure_ascii=False)
        elif text is not None:
            text = str(text)
        turns.append(turn(
            seq=len(turns) + 1, role=role, text=text,
            src={"source_idx": 0, "off": off, "len": ln,
                 "sha256": hashlib.sha256(line).hexdigest()},
            model=obj.get("model") or inner.get("current_model_id"),
        ))
        off += ln
    h = head(
        id=legal_id("grok", vid), family=FAMILY, vendor_session_id=vid,
        title=str(inner.get("generated_title") or inner.get("title") or ""),
        stream="cm" if "COSMOS" in str(inner.get("cwd") or hit.as_posix()) else "unknown",
        legal=False, cwd=str(inner.get("cwd") or ""),
        n_turns=len(turns), sources=[src],
        models=[inner.get("current_model_id")] if inner.get("current_model_id") else [],
    )
    if truncated:
        h["_truncated"] = True
    return h, turns
