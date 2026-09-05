#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_context_pull. Isolated fake transcript. No C:\\ required.

Proves: tail byte range, tool-noise strip, last-N turns, provenance bound to
the real file, missing-root is a visible miss (not a fabricated blob).
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_context_pull import (  # noqa: E402
    find_current_transcript, format_blob, parse_turns, pull_context,
    read_tail_bytes, record_turn,
)

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write_jsonl(path: Path, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8")


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_ctxpull_"))
    sess = td / "sessions" / "abc-session-id"
    transcript = sess / "chat_history.jsonl"
    rows = [
        {"type": "system", "content": "you are a robot"},
        {"type": "user", "content": [{"type": "text", "text": "hello keith"}]},
        {"type": "assistant", "content": "", "tool_calls": [
            {"id": "t1", "name": "grep", "arguments": "{}"}]},
        {"type": "tool_result", "tool_call_id": "t1", "content": "NOISE"},
        {"type": "assistant", "content": [
            {"type": "text", "text": "I found the file"}]},
        {"type": "user", "content": [{"type": "text", "text": "reply PONG"}]},
        {"type": "reasoning", "summary": [
            {"type": "summary_text", "text": "thinking hard"}]},
        {"type": "assistant", "content": [
            {"type": "text", "text": "PONG"}]},
    ]
    _write_jsonl(transcript, rows)

    loc = find_current_transcript([td / "sessions"])
    check("finds the jsonl", lambda: loc["ok"] and Path(loc["path"]) == transcript)
    check("session_id from parent folder",
          lambda: loc["session_id"] == "abc-session-id")

    rec = pull_context(transcript=transcript, max_turns=12, max_kb=64)
    check("pull ok", lambda: rec["ok"] is True)
    check("provenance session id",
          lambda: rec["provenance"]["session_id"] == "abc-session-id")
    check("byte range is bound to the file",
          lambda: rec["byte_start"] == 0
          and rec["byte_end"] == transcript.stat().st_size
          and rec["file_size"] == transcript.stat().st_size)
    blob = rec["blob"]
    check("blob keeps user text", lambda: "hello keith" in blob and "reply PONG" in blob)
    check("blob keeps assistant text", lambda: "I found the file" in blob and "PONG" in blob)
    check("blob strips tool_result noise", lambda: "NOISE" not in blob)
    check("blob strips system prompt", lambda: "you are a robot" not in blob)
    check("turns counted", lambda: rec["turns"] == 4)

    rec_n = pull_context(transcript=transcript, max_turns=2, max_kb=64)
    check("max_turns keeps only the tail",
          lambda: rec_n["turns"] == 2
          and "reply PONG" in rec_n["blob"]
          and "hello keith" not in rec_n["blob"])

    missing = pull_context(sessions_roots=[td / "nope"], max_turns=4, max_kb=8)
    check("missing root is a visible miss, empty blob",
          lambda: missing["ok"] is False
          and missing.get("kind") == "NO_TRANSCRIPT"
          and missing["blob"] == "")

    # Claude Code nested-message shape
    claude_rows = [
        {"type": "queue-operation", "operation": "enqueue",
         "sessionId": "sess-cc", "content": "ignore me"},
        {"type": "user", "sessionId": "sess-cc",
         "message": {"role": "user", "content": [
             {"type": "text", "text": "do the thing"}]}},
        {"type": "assistant", "sessionId": "sess-cc",
         "message": {"role": "assistant", "content": [
             {"type": "tool_use", "id": "x", "name": "Read", "input": {}},
             {"type": "text", "text": "done"}]}},
    ]
    check("claude user turn extracted",
          lambda: record_turn(claude_rows[1])["text"] == "do the thing")
    check("claude tool_use stripped, text kept",
          lambda: record_turn(claude_rows[2])["text"] == "done")
    check("queue-operation is noise",
          lambda: record_turn(claude_rows[0]) is None)

    # tail-bytes cap: file larger than max_kb
    big = td / "sessions" / "big" / "chat_history.jsonl"
    big_rows = (
        [{"type": "user", "content": "PAD " + ("x" * 800)}] * 40
        + [{"type": "user", "content": "TAIL_MARKER_ONLY"}]
    )
    _write_jsonl(big, big_rows)
    tail = read_tail_bytes(big, max_kb=1)
    check("tail cap starts after byte 0 on a big file",
          lambda: tail["capped"] is True and tail["byte_start"] > 0)
    rec_big = pull_context(transcript=big, max_turns=12, max_kb=1)
    check("capped pull still ok and names the byte range",
          lambda: rec_big["ok"] and rec_big["capped"]
          and rec_big["byte_end"] == big.stat().st_size)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = [(lab, err) for lab, ok, err in RESULTS if not ok]
    print(f"test_context_pull {passed}/{len(RESULTS)}")
    for lab, err in failed:
        print(f"  FAIL {lab} {err}")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
