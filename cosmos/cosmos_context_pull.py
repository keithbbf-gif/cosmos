#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_context_pull - NATIVE Windows session-transcript tail.

The Cowork/Claude sandbox cannot read C:\\ reliably. This tool runs as a host
Python process, finds the CURRENT session transcript (.jsonl), reads the TAIL
(last N turns / M KB), strips tool noise, and returns a context blob plus
provenance (session id + byte range). No BTS. Does not modify kernel / ledger
/ sched / service.

Default hunt (first existing root wins the walk; CURRENT = newest mtime):

  1. %APPDATA%\\Claude\\local-agent-mode-sessions   (spec path)
  2. %USERPROFILE%\\.claude\\projects                 (Claude Code)
  3. %USERPROFILE%\\.claude\\sessions
  4. %USERPROFILE%\\.grok\\sessions                   (Grok Build)

    py -3.14 cosmos\\cosmos_context_pull.py
    py -3.14 cosmos\\cosmos_context_pull.py --max-turns 12 --max-kb 64
    py -3.14 cosmos\\cosmos_context_pull.py --sessions-root <dir>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone as dt_timezone
from pathlib import Path

SCHEMA = "cosmos-context-pull/1"
WORKER = "cosmos-context-pull"

DEFAULT_TURNS = 12
DEFAULT_MAX_KB = 64
MAX_WALK_DEPTH = 6
PER_TURN_CAP = 12000

# Spec path first. Additional roots exist because Cowork's folder is not
# always present on this host (measured 2026-08-25: spec path missing;
# Claude Code jsonl lives under .claude\\projects; this G46 session under
# .grok\\sessions\\...\\chat_history.jsonl).
SPEC_SESSIONS_REL = ("Claude", "local-agent-mode-sessions")

PREFERRED_NAMES = ("chat_history.jsonl",)
SKIP_NAMES = {
    "events.jsonl", "updates.jsonl", "prompt_history.jsonl",
    "session_search.sqlite",
}
SKIP_DIR_NAMES = {
    "node_modules", ".git", "__pycache__", "Cache", "GPUCache",
    "Code Cache", "blob_storage", "Crashpad", "DawnGraphiteCache",
    "DawnWebGPUCache", "Shared Dictionary", "Local Storage",
    "Session Storage", "Network", "Partitions", "terminal", "memory",
}

NOISE_TYPES = {
    "tool_result", "tool_use", "tool_call", "function_call",
    "function_result", "server_tool_use", "queue-operation",
    "system", "last-prompt", "ai-title", "progress", "reasoning",
    "thinking", "redacted_thinking", "image", "document",
}
NOISE_BLOCK_TYPES = {
    "tool_use", "tool_result", "tool_call", "server_tool_use",
    "function_call", "image", "document", "thinking",
    "redacted_thinking", "reasoning",
}


class ContextPullError(RuntimeError):
    """Typed refusal. kind in {NO_ROOT, NO_TRANSCRIPT, IO}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso(ts: float | None = None) -> str:
    if ts is None:
        return datetime.now().astimezone().isoformat(timespec="seconds")
    return datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


def default_sessions_roots() -> list[Path]:
    appdata = os.environ.get("APPDATA") or str(
        Path.home() / "AppData" / "Roaming")
    home = Path.home()
    return [
        Path(appdata) / SPEC_SESSIONS_REL[0] / SPEC_SESSIONS_REL[1],
        home / ".claude" / "projects",
        home / ".claude" / "sessions",
        home / ".grok" / "sessions",
    ]


def _is_jsonl(path: Path) -> bool:
    if not path.is_file():
        return False
    name = path.name.lower()
    if name.endswith(".lock") or name in SKIP_NAMES:
        return False
    return name.endswith(".jsonl")


def _walk_jsonl(root: Path, max_depth: int = MAX_WALK_DEPTH) -> list[Path]:
    found: list[Path] = []
    if not root.exists() or not root.is_dir():
        return found
    root_n = len(root.parts)
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            p = Path(dirpath)
            depth = len(p.parts) - root_n
            if depth > max_depth:
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES
                           and not d.startswith(".")]
            for fn in filenames:
                fp = p / fn
                if _is_jsonl(fp):
                    found.append(fp)
    except OSError:
        return found
    return found


def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def find_current_transcript(sessions_roots: list[Path] | None = None) -> dict:
    """Newest .jsonl across configured roots. Prefer chat_history.jsonl
    when mtimes are equal (Grok Build session file)."""
    roots = list(sessions_roots or default_sessions_roots())
    existing = []
    missing = []
    candidates: list[Path] = []
    for r in roots:
        rp = Path(r)
        if rp.exists() and rp.is_dir():
            existing.append(str(rp))
            candidates.extend(_walk_jsonl(rp))
        else:
            missing.append(str(rp))
    if not candidates:
        return {
            "ok": False,
            "kind": "NO_TRANSCRIPT",
            "path": None,
            "session_id": None,
            "roots_existing": existing,
            "roots_missing": missing,
            "detail": "no .jsonl transcript under configured session roots",
        }
    # Prefer preferred names by tiny mtime boost so a same-second
    # chat_history.jsonl wins over updates.jsonl in the same folder.
    def score(p: Path) -> tuple:
        mt = _mtime(p)
        pref = 1 if p.name.lower() in PREFERRED_NAMES else 0
        return (mt, pref)

    chosen = max(candidates, key=score)
    session_id = _session_id_from_path(chosen)
    st = chosen.stat()
    return {
        "ok": True,
        "kind": None,
        "path": str(chosen),
        "session_id": session_id,
        "size": int(st.st_size),
        "mtime": float(st.st_mtime),
        "mtime_iso": _iso(st.st_mtime),
        "roots_existing": existing,
        "roots_missing": missing,
        "n_candidates": len(candidates),
    }


def _session_id_from_path(path: Path) -> str:
    # Claude Code: <projects>/<proj>/<session-uuid>.jsonl
    stem = path.stem
    if len(stem) >= 8 and "-" in stem:
        return stem
    # Grok Build: .../<workspace>/<session-uuid>/chat_history.jsonl
    parent = path.parent.name
    if parent and parent not in ("sessions", "projects"):
        return parent
    return stem


def read_tail_bytes(path: Path, max_kb: int) -> dict:
    size = path.stat().st_size
    max_bytes = max(1024, int(max_kb) * 1024)
    start = 0 if size <= max_bytes else size - max_bytes
    with open(path, "rb") as fh:
        fh.seek(start)
        if start > 0:
            fh.readline()  # drop the partial first line
            start = fh.tell()
        data = fh.read()
    end = start + len(data)
    return {
        "data": data,
        "byte_start": int(start),
        "byte_end": int(end),
        "file_size": int(size),
        "capped": start > 0,
    }


def _blocks_to_text(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return str(content).strip()
    parts: list[str] = []
    for b in content:
        if isinstance(b, str):
            if b.strip():
                parts.append(b.strip())
            continue
        if not isinstance(b, dict):
            continue
        t = str(b.get("type") or "").lower()
        if t in NOISE_BLOCK_TYPES:
            continue
        if t in ("text", "output_text", "summary_text", "input_text"):
            tx = b.get("text") or b.get("content") or ""
            if str(tx).strip():
                parts.append(str(tx).strip())
            continue
        if "text" in b and t not in NOISE_TYPES:
            tx = b.get("text")
            if str(tx).strip():
                parts.append(str(tx).strip())
    return "\n".join(parts).strip()


def record_turn(obj) -> dict | None:
    """Return {role, text} for a user/assistant text turn, else None.

    Tool calls, tool results, queue ops, system, and reasoning are noise.
    """
    if not isinstance(obj, dict):
        return None
    t = str(obj.get("type") or "").lower()
    if t in NOISE_TYPES:
        return None
    msg = obj.get("message") if isinstance(obj.get("message"), dict) else obj
    role = str(msg.get("role") or t or "").lower()
    if role in ("tool", "system"):
        return None
    content = msg.get("content")
    text = _blocks_to_text(content)
    if not text:
        return None
    if role in ("user", "human"):
        role = "user"
    elif role in ("assistant", "ai", "model"):
        role = "assistant"
    elif t in ("user", "assistant"):
        role = t
    else:
        return None
    if len(text) > PER_TURN_CAP:
        text = text[:PER_TURN_CAP - 1] + "…"
    return {"role": role, "text": text}


def parse_turns(data: bytes) -> list[dict]:
    text = data.decode("utf-8", errors="replace")
    turns: list[dict] = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            obj = json.loads(ln)
        except ValueError:
            continue
        turn = record_turn(obj)
        if turn is not None:
            turns.append(turn)
    return turns


def format_blob(turns: list[dict]) -> str:
    if not turns:
        return ""
    parts = []
    for t in turns:
        role = t.get("role") or "user"
        body = (t.get("text") or "").strip()
        if not body:
            continue
        parts.append(f"[{role}]\n{body}")
    return "\n\n".join(parts).strip()


def pull_context(sessions_roots: list[Path] | None = None,
                 max_turns: int = DEFAULT_TURNS,
                 max_kb: int = DEFAULT_MAX_KB,
                 transcript: Path | None = None) -> dict:
    """Find (or use) a transcript, read the tail, strip noise, return blob.

    Always returns a record. ok=False is a visible miss (no fabricate).
    """
    now = datetime.now().astimezone()
    rec = {
        "schema": SCHEMA,
        "worker": WORKER,
        "ok": False,
        "pulled_at": now.isoformat(timespec="seconds"),
        "pulled_at_utc": now.astimezone(dt_timezone.utc).isoformat(
            timespec="seconds"),
        "max_turns": int(max_turns),
        "max_kb": int(max_kb),
        "path": None,
        "session_id": None,
        "byte_start": None,
        "byte_end": None,
        "file_size": None,
        "turns": 0,
        "blob": "",
        "blob_chars": 0,
        "provenance": {},
        "error": None,
    }
    loc = None
    path = Path(transcript) if transcript is not None else None
    if path is None:
        loc = find_current_transcript(sessions_roots)
        rec["roots_existing"] = loc.get("roots_existing")
        rec["roots_missing"] = loc.get("roots_missing")
        rec["n_candidates"] = loc.get("n_candidates")
        if not loc.get("ok"):
            rec["error"] = loc.get("detail") or "no transcript"
            rec["kind"] = loc.get("kind") or "NO_TRANSCRIPT"
            rec["provenance"] = {
                "session_id": None,
                "path": None,
                "byte_start": None,
                "byte_end": None,
                "roots_missing": loc.get("roots_missing"),
            }
            return rec
        path = Path(loc["path"])
        rec["session_id"] = loc.get("session_id")
    else:
        if not path.exists() or not path.is_file():
            rec["error"] = f"transcript missing: {path}"
            rec["kind"] = "NO_TRANSCRIPT"
            rec["provenance"] = {"session_id": None, "path": str(path),
                                 "byte_start": None, "byte_end": None}
            return rec
        rec["session_id"] = _session_id_from_path(path)

    rec["path"] = str(path)
    try:
        tail = read_tail_bytes(path, int(max_kb))
    except OSError as e:
        rec["error"] = f"IO {path}: {e}"
        rec["kind"] = "IO"
        rec["provenance"] = {
            "session_id": rec.get("session_id"),
            "path": str(path),
            "byte_start": None,
            "byte_end": None,
        }
        return rec

    turns = parse_turns(tail["data"])
    n = max(1, int(max_turns))
    kept = turns[-n:] if len(turns) > n else turns
    blob = format_blob(kept)
    rec["ok"] = True
    rec["byte_start"] = tail["byte_start"]
    rec["byte_end"] = tail["byte_end"]
    rec["file_size"] = tail["file_size"]
    rec["capped"] = tail["capped"]
    rec["turns_parsed"] = len(turns)
    rec["turns"] = len(kept)
    rec["blob"] = blob
    rec["blob_chars"] = len(blob)
    rec["kind"] = None
    rec["error"] = None
    rec["mtime_iso"] = _iso(_mtime(path))
    rec["provenance"] = {
        "session_id": rec["session_id"],
        "path": str(path),
        "byte_start": rec["byte_start"],
        "byte_end": rec["byte_end"],
        "file_size": rec["file_size"],
        "capped": rec["capped"],
        "turns": rec["turns"],
        "turns_parsed": rec["turns_parsed"],
        "mtime_iso": rec["mtime_iso"],
    }
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_context_pull")
    ap.add_argument("--sessions-root", action="append", default=None,
                    help="session root to walk (repeatable). Default: spec "
                         "path + Claude Code + Grok sessions.")
    ap.add_argument("--transcript", default=None,
                    help="explicit .jsonl path (skip hunt)")
    ap.add_argument("--max-turns", type=int, default=DEFAULT_TURNS)
    ap.add_argument("--max-kb", type=int, default=DEFAULT_MAX_KB)
    a = ap.parse_args()
    roots = [Path(p) for p in a.sessions_root] if a.sessions_root else None
    rec = pull_context(
        sessions_roots=roots,
        max_turns=a.max_turns,
        max_kb=a.max_kb,
        transcript=Path(a.transcript) if a.transcript else None,
    )
    print(json.dumps(rec, indent=1, default=str))
    return 0 if rec.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
