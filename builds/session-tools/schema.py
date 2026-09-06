#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos-transcript/1 — canonical JSONL head + turns (CCr dispose D1)."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "cosmos-transcript/1"
KIND = "COSMOS_TRANSCRIPT"

ROLES = ("user", "assistant", "system", "tool_call", "tool_result", "meta")

# Windows-illegal in export ids / filenames. Colon-encoded grok cwd dirs are
# source paths, not export names.
_ILLEGAL = re.compile(r'[:*?"<>|]')


def stable_id(prefix: str, vendor_session_id: str) -> str:
    stable = _ILLEGAL.sub("", str(vendor_session_id))
    stable = stable.replace("/", "-").replace("\\", "-")
    return f"{prefix}-{stable}"


def family_of_id(sid: str) -> str | None:
    s = str(sid)
    if s.startswith("cow-"):
        return "cowork"
    if s.startswith("grok-"):
        return "grok_tui"
    return None


def vendor_of_id(sid: str) -> str:
    s = str(sid)
    if s.startswith("cow-"):
        return s[4:]
    if s.startswith("grok-"):
        return s[5:]
    return s


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def head_record(
    *,
    id: str,
    family: str,
    vendor_session_id: str,
    title: str = "",
    stream: str = "",
    legal: bool = False,
    cwd: str = "",
    n_turns: int = 0,
    sources: list[dict] | None = None,
    frames: list[dict] | None = None,
    models: list[str] | None = None,
    t_first=None,
    t_last=None,
    aliases: dict | None = None,
) -> dict:
    return {
        "schema": SCHEMA,
        "kind": KIND,
        "id": id,
        "family": family,
        "vendor_session_id": vendor_session_id,
        "title": title if title is not None else "",
        "stream": stream if stream is not None else "",
        "legal": bool(legal),
        "cwd": cwd if cwd is not None else "",
        "n_turns": int(n_turns),
        "sources": list(sources or []),
        "frames": list(frames or []),
        "models": list(models or []),
        "t_first": t_first,
        "t_last": t_last,
        "aliases": aliases if aliases is not None else {},
    }


def turn_record(
    *,
    seq: int,
    role: str,
    t=None,
    utc_off=None,
    text: str | None = None,
    model: str | None = None,
    src: dict | None = None,
    parts: list | None = None,
    redactions: int = 0,
) -> dict:
    return {
        "seq": int(seq),
        "role": role,
        "t": t,
        "utc_off": utc_off,
        "text": text,
        "model": model,
        "src": src,
        "parts": list(parts or []),
        "redactions": int(redactions),
    }


def source_record(
    *,
    idx: int,
    path: str,
    kind: str,
    data: bytes,
    fidelity: str = "span",
    blob_sha: str | None = None,
) -> dict:
    rec = {
        "idx": int(idx),
        "path": path,
        "kind": kind,
        "len": len(data),
        "sha256": sha256_bytes(data),
        "fidelity": fidelity,
    }
    if blob_sha:
        rec["blob_sha"] = blob_sha
    return rec


def span_src(source_idx: int, off: int, length: int, data: bytes) -> dict:
    return {
        "source_idx": int(source_idx),
        "off": int(off),
        "len": int(length),
        "sha256": sha256_bytes(data[off:off + length] if length else b""),
    }


def _dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"),
                      sort_keys=True)


def encode_jsonl(head: dict, turns: list[dict]) -> bytes:
    """UTF-8 JSONL, \\n newlines, record 1 = head, then N turns. No HMAC."""
    lines = [_dumps(head)]
    for t in turns:
        lines.append(_dumps(t))
    return ("\n".join(lines) + "\n").encode("utf-8")


def encode_turns_body(turns: list[dict]) -> bytes:
    if not turns:
        return b""
    return ("".join(_dumps(t) + "\n" for t in turns)).encode("utf-8")


def view(head: dict, turns: list[dict]) -> dict:
    """Rebuildable JSON object view of the JSONL. The view is not the file."""
    rec = dict(head)
    rec["turns"] = list(turns)
    return rec


def sidecar_payload(*, jsonl_decl: dict, body_sha: str, source_sha: str | None,
                    n_turns: int, fidelity: str = "span",
                    spans_ok=None, produced_at: str | None = None,
                    produced_by: str = "session-tools/1",
                    tree_id=None, anonymized: bool = False,
                    derived_from=None) -> dict:
    """write_declared shape for {id}.ctr.decl.json — sha-only, no HMAC."""
    rec = {
        "len": jsonl_decl["len"],
        "sha": jsonl_decl["sha"],
        "body_sha": body_sha,
        "source_sha": source_sha,
        "n_turns": int(n_turns),
        "fidelity": fidelity,
        "spans_ok": spans_ok,
        "produced_at": produced_at,
        "produced_by": produced_by,
        "tree_id": tree_id,
        "anonymized": bool(anonymized),
        "derived_from": derived_from,
    }
    return rec


def parse_jsonl(data: bytes) -> tuple[dict, list[dict], bool]:
    """Return (head, turns, truncated). Incomplete last line → truncated."""
    truncated = False
    if data and not data.endswith(b"\n"):
        truncated = True
    text = data.decode("utf-8", errors="replace")
    raw_lines = text.split("\n")
    if raw_lines and raw_lines[-1] == "":
        raw_lines = raw_lines[:-1]
    objs: list[dict] = []
    for i, ln in enumerate(raw_lines):
        if not ln.strip():
            continue
        try:
            o = json.loads(ln)
        except ValueError:
            if i == len(raw_lines) - 1:
                truncated = True
                break
            raise
        if not isinstance(o, dict):
            raise ValueError("jsonl record is not an object")
        objs.append(o)
    if not objs:
        return {}, [], truncated
    head = objs[0]
    turns = objs[1:]
    return head, turns, truncated


def jsonl_paths(out_dir: Path, sid: str) -> tuple[Path, Path]:
    return out_dir / f"{sid}.ctr.jsonl", out_dir / f"{sid}.ctr.decl.json"
