#!/usr/bin/env python3
"""cosmos-transcript/1 — JSONL head + turns. Sidecar is sha-only (no HMAC)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SCHEMA = "cosmos-transcript/1"
KIND = "COSMOS_TRANSCRIPT"
RESULT_SCHEMA = "cosmos-session-tools-result/1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), sha256_bytes(data)


def legal_id(prefix: str, vendor_id: str) -> str:
    raw = "".join(c for c in str(vendor_id) if c not in ':*?"<>|\\/')
    return f"{prefix}-{raw}"


def head(*, id: str, family: str, vendor_session_id: str, title: str = "",
         stream: str = "unknown", legal: bool = False, cwd: str = "",
         n_turns: int = 0, sources: list | None = None, aliases: dict | None = None,
         models: list | None = None) -> dict:
    return {
        "schema": SCHEMA,
        "kind": KIND,
        "id": id,
        "family": family,
        "vendor_session_id": vendor_session_id,
        "title": title or "",
        "stream": (stream or "unknown").lower(),
        "legal": bool(legal),
        "cwd": cwd or "",
        "n_turns": int(n_turns),
        "sources": sources or [],
        "frames": [],
        "models": models or [],
        "t_first": None,
        "t_last": None,
        "aliases": aliases or {"seq": None, "filename": None, "opencode_id": None},
    }


def turn(*, seq: int, role: str, text: str | None, src: dict,
         t=None, model: str | None = None) -> dict:
    return {
        "seq": int(seq),
        "role": role,
        "t": t,
        "utc_off": None,
        "text": text,
        "model": model,
        "src": src,
        "parts": [],
        "redactions": 0,
    }


def encode_jsonl(head_rec: dict, turns: list[dict]) -> bytes:
    head_rec = dict(head_rec)
    head_rec["n_turns"] = len(turns)
    lines = [json.dumps(head_rec, separators=(",", ":"), ensure_ascii=False)]
    for t in turns:
        lines.append(json.dumps(t, separators=(",", ":"), ensure_ascii=False))
    return ("\n".join(lines) + "\n").encode("utf-8")


def view(head_rec: dict, turns: list[dict]) -> dict:
    """Rebuildable JSON object. Not the canonical file."""
    out = dict(head_rec)
    out["n_turns"] = len(turns)
    out["turns"] = turns
    return out


def _span_pieces(turns: list[dict], frames: list) -> list[tuple[int, int, str | None]]:
    pieces: list[tuple[int, int, str | None]] = []
    for item in list(turns) + list(frames):
        src = item.get("src") if "src" in item else item
        src = src or {}
        if "off" not in src and "len" not in src:
            continue
        sha = src.get("sha256") or None
        pieces.append((int(src.get("off") or 0), int(src.get("len") or 0), sha))
    return pieces


def spans_ok(head_rec: dict, turns: list[dict]) -> tuple[bool, int, int]:
    """sum(span.len) vs first source.len. Span mode must tile that file."""
    sources = head_rec.get("sources") or []
    src = sources[0] if sources else {}
    if not isinstance(src, dict):
        src = {}
    src_len = int(src.get("len") or 0) if sources else 0
    pieces = _span_pieces(turns, head_rec.get("frames") or [])
    total = sum(ln for _, ln, _ in pieces)
    if total != src_len:
        return False, total, src_len
    if str(src.get("fidelity") or "") == "blob" or not src.get("path"):
        return True, total, src_len
    path = Path(str(src.get("path")))
    if not path.is_file():
        return False, total, src_len
    raw = path.read_bytes()
    if len(raw) != src_len:
        return False, total, src_len
    want = src.get("sha256")
    if want and sha256_bytes(raw) != want:
        return False, total, src_len
    cursor = 0
    ordered = sorted(pieces, key=lambda item: (item[0], item[1]))
    for off, ln, span_sha in ordered:
        if ln < 0 or off != cursor or off + ln > len(raw):
            return False, total, src_len
        chunk = raw[off:off + ln]
        if span_sha and sha256_bytes(chunk) != span_sha:
            return False, total, src_len
        cursor += ln
    if cursor != len(raw):
        return False, total, src_len
    return True, total, src_len


def parse_jsonl(payload: bytes) -> tuple[dict, list[dict]]:
    lines = [ln for ln in payload.splitlines() if ln.strip()]
    if not lines:
        raise ValueError("empty transcript")
    head_rec = json.loads(lines[0].decode("utf-8"))
    turns = [json.loads(ln.decode("utf-8")) for ln in lines[1:]]
    return head_rec, turns


def write_canonical(out_dir: Path, rec_id: str, payload: bytes) -> dict:
    from cosmos_validate import read_verified, write_declared

    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / f"{rec_id}.ctr.jsonl"
    decl = write_declared(jsonl, payload)
    sidecar = {
        "schema": "cosmos-transcript-decl/1",
        "len": decl["len"],
        "sha": decl["sha"],
        "n_turns": payload.count(b"\n") - 1,
        "fidelity": "span",
        "hmac": False,
    }
    decl_path = out_dir / f"{rec_id}.ctr.decl.json"
    decl_path.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")
    back = read_verified(jsonl, expect_len=decl["len"], expect_sha=decl["sha"])
    if back != payload:
        raise RuntimeError("HASH_MISMATCH round-trip")
    return {"jsonl": str(jsonl), "decl": str(decl_path), **decl}
