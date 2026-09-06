#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Grok TUI family. Store: ~/.grok/sessions/<urlencoded-cwd>/<uuid>/

Required: summary.json + chat_history.jsonl. updates.jsonl is NOT authority.
id = grok-{uuid} from summary.info.id.
legal=true only if cwd is a Legal tree (P:\\Legal or V:\\Ai LEGAL). V:\\A is not.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from refusals import LEGAL_OMITTED, NO_STORE, NOT_FOUND, Refusal
from schema import (
    head_record, source_record, span_src, stable_id, turn_record,
)

FAMILY = "grok_tui"
PREFIX = "grok"
SUMMARY = "summary.json"
HISTORY = "chat_history.jsonl"

# Turn-authority types. Unmappable → SCHEMA_UNKNOWN (never silent fold).
_ROLE_MAP = {
    "user": "user",
    "human": "user",
    "assistant": "assistant",
    "ai": "assistant",
    "system": "system",
    "tool_result": "tool_result",
    "function_result": "tool_result",
    "tool_call": "tool_call",
    "tool_use": "tool_call",
    "function_call": "tool_call",
    "reasoning": "meta",
    "thinking": "meta",
    "redacted_thinking": "meta",
    "meta": "meta",
}

# Not turns. Skipping these is not folding a role into user/assistant.
_SKIP_TYPES = {
    "ai-title", "progress", "queue-operation", "last-prompt",
    "image", "document", "server_tool_use",
}


def default_store() -> Path:
    return Path.home() / ".grok" / "sessions"


def is_legal_cwd(cwd: str) -> bool:
    """Sticky legal only for named Legal trees. Do not guess from V:\\A."""
    if not cwd:
        return False
    n = cwd.replace("/", "\\").lower().rstrip("\\")
    if n.startswith("p:\\legal"):
        return True
    if n.startswith("v:\\ai\\") and ("\\legal\\" in n + "\\" or n.endswith("\\legal")):
        return True
    return False


def grok_stream(cwd: str, legal: bool) -> str:
    if legal:
        return "legal"
    n = (cwd or "").replace("/", "\\").lower()
    if "\\ai\\cosmos" in n or "\\worktrees\\ai-cosmos" in n:
        return "cm"
    return "unknown"


def _iso_to_epoch(s) -> float | None:
    if not s or not isinstance(s, str):
        return None
    try:
        t = s.replace("Z", "+00:00")
        dt = datetime.fromisoformat(t)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return None


def _text_of(obj) -> str | None:
    c = obj.get("content")
    if c is None:
        return None
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        parts = []
        for b in c:
            if isinstance(b, str):
                parts.append(b)
            elif isinstance(b, dict):
                if b.get("type") in ("text", "summary_text") or "text" in b:
                    parts.append(str(b.get("text") or ""))
        return "".join(parts)
    return str(c)


def _read_summary(sess: Path) -> dict:
    p = sess / SUMMARY
    return json.loads(p.read_text(encoding="utf-8"))


def session_vendor_id(sess: Path, summary: dict | None = None) -> str:
    summary = summary or _read_summary(sess)
    info = summary.get("info") if isinstance(summary.get("info"), dict) else {}
    vid = info.get("id") or summary.get("id") or sess.name
    return str(vid)


def is_session_dir(path: Path) -> bool:
    return (path / SUMMARY).is_file() and (path / HISTORY).is_file()


def walk_sessions(store: Path) -> list[Path]:
    """uuid dirs that contain BOTH required files. Missing history → not counted."""
    store = Path(store)
    found: list[Path] = []
    if is_session_dir(store):
        return [store]
    if not store.is_dir():
        return found
    for dirpath, dirnames, filenames in __import__("os").walk(store):
        p = Path(dirpath)
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        if SUMMARY in filenames and HISTORY in filenames:
            found.append(p)
    return found


def discover(store: Path) -> dict:
    store = Path(store)
    if not store.exists():
        raise Refusal(NO_STORE, f"grok store missing: {store}",
                      path=str(store), n=None)
    if not store.is_dir():
        raise Refusal(NO_STORE, f"grok store is not a directory: {store}",
                      path=str(store), n=None)
    sessions = walk_sessions(store)
    hits = []
    n_legal = 0
    total_bytes = 0
    for sess in sessions:
        try:
            summary = _read_summary(sess)
        except (OSError, ValueError):
            continue
        info = summary.get("info") if isinstance(summary.get("info"), dict) else {}
        cwd = str(info.get("cwd") or summary.get("cwd") or "")
        legal = is_legal_cwd(cwd)
        if legal:
            n_legal += 1
        hist = sess / HISTORY
        size = hist.stat().st_size if hist.is_file() else 0
        total_bytes += size
        vid = session_vendor_id(sess, summary)
        hits.append({
            "family": FAMILY,
            "id": stable_id(PREFIX, vid),
            "path": str(sess),
            "vendor_session_id": vid,
            "stream": grok_stream(cwd, legal),
            "legal": legal,
            "bytes": size,
            "sha256": None,
            "title": str(summary.get("generated_title")
                         or summary.get("session_summary") or ""),
            "cwd": cwd,
        })
    sample = [h["id"] for h in hits[:5]]
    return {
        "status": "OK",
        "path": str(store),
        "n": len(hits),
        "n_legal": n_legal,
        "bytes": total_bytes,
        "sample_ids": sample,
        "hits": hits,
    }


def _find_session(store: Path, vendor: str) -> Path | None:
    store = Path(store)
    if is_session_dir(store):
        vid = session_vendor_id(store)
        if vid == vendor or store.name == vendor:
            return store
        return None
    for sess in walk_sessions(store):
        if sess.name == vendor:
            return sess
        try:
            if session_vendor_id(sess) == vendor:
                return sess
        except (OSError, ValueError):
            continue
    return None


def parse_history(data: bytes) -> tuple[list[dict], list[str], bool, list[str]]:
    """Returns turns, unknown_types, truncated, models."""
    truncated = bool(data) and not data.endswith(b"\n")
    unknown: list[str] = []
    models: list[str] = []
    turns: list[dict] = []
    seq = 0
    # Split keeping offsets on original bytes.
    i = 0
    n = len(data)
    while i < n:
        j = data.find(b"\n", i)
        if j < 0:
            line = data[i:]
            line_end = n
            last = True
        else:
            line = data[i:j]
            line_end = j + 1
            last = False
        raw = line[:-1] if line.endswith(b"\r") else line
        start = i
        i = line_end
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw.decode("utf-8"))
        except ValueError:
            if last or j < 0:
                truncated = True
                break
            raise Refusal("UNPARSEABLE", f"bad jsonl at offset {start}")
        if not isinstance(obj, dict):
            continue
        t = str(obj.get("type") or "").lower()
        if t in _SKIP_TYPES:
            continue
        role = _ROLE_MAP.get(t)
        if role is None:
            unknown.append(t or "<empty>")
            continue
        text = _text_of(obj)
        tool_calls = obj.get("tool_calls")
        if role == "assistant" and not (text or "").strip() and tool_calls:
            role = "tool_call"
            text = json.dumps(tool_calls, ensure_ascii=False) if tool_calls else None
        model = obj.get("model") or obj.get("model_id")
        if isinstance(model, str) and model and model not in models:
            models.append(model)
        ts = obj.get("timestamp") or obj.get("ts") or obj.get("created_at")
        epoch = ts if isinstance(ts, (int, float)) else _iso_to_epoch(ts) if isinstance(ts, str) else None
        seq += 1
        span_len = len(raw)  # line without newline
        turns.append(turn_record(
            seq=seq,
            role=role,
            t=epoch,
            text=text,
            model=model if isinstance(model, str) else None,
            src=span_src(0, start, span_len, data),
        ))
    return turns, unknown, truncated, models


def load(store: Path, sid: str | None = None, path: Path | None = None) -> dict:
    store = Path(store)
    sess = None
    if path is not None:
        p = Path(path)
        if p.is_file() and p.name == HISTORY:
            p = p.parent
        if is_session_dir(p):
            sess = p
    if sess is None:
        if not store.exists():
            raise Refusal(NO_STORE, f"grok store missing: {store}",
                          path=str(store), n=None)
        vendor = None
        if sid:
            vendor = sid[5:] if sid.startswith("grok-") else sid
        sess = _find_session(store, vendor) if vendor else None
    if sess is None:
        raise Refusal(NOT_FOUND, f"no grok session {sid or path}",
                      id=sid, path=str(path) if path else None)

    try:
        summary = _read_summary(sess)
    except (OSError, ValueError) as e:
        raise Refusal(NOT_FOUND, f"summary.json unreadable: {e}", path=str(sess))
    info = summary.get("info") if isinstance(summary.get("info"), dict) else {}
    cwd = str(info.get("cwd") or summary.get("cwd") or "")
    vid = session_vendor_id(sess, summary)
    gid = stable_id(PREFIX, vid)
    legal = is_legal_cwd(cwd)
    title = str(summary.get("generated_title") or summary.get("session_summary") or "")
    if legal:
        raise Refusal(
            LEGAL_OMITTED,
            f"{gid} cwd is a Legal tree — body omitted from this TUI",
            id=gid,
            family=FAMILY,
            vendor_session_id=vid,
            legal=True,
            cwd=cwd,
        )

    hist = sess / HISTORY
    data = hist.read_bytes()
    turns, unknown, truncated, models = parse_history(data)
    cur = summary.get("current_model_id")
    if isinstance(cur, str) and cur and cur not in models:
        models = [cur] + models
    src = source_record(idx=0, path=str(hist), kind="jsonl", data=data,
                        fidelity="span")
    head = head_record(
        id=gid,
        family=FAMILY,
        vendor_session_id=vid,
        title=title,
        stream=grok_stream(cwd, False),
        legal=False,
        cwd=cwd,
        n_turns=len(turns),
        sources=[src],
        models=models,
        t_first=_iso_to_epoch(summary.get("created_at")),
        t_last=_iso_to_epoch(summary.get("updated_at")),
        aliases={"filename": HISTORY},
    )
    rec = {
        "head": head,
        "turns": turns,
        "source_bytes": data,
        "unknown_roles": unknown,
        "truncated": truncated,
    }
    if unknown:
        rec["unmapped"] = unknown
    return rec
