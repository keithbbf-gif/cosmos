#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


def spans_ok(head_rec: dict, turns: list[dict]) -> tuple[bool, int, int]:
    """sum(span.len) vs first source.len. Frame spans count."""
    sources = head_rec.get("sources") or []
    src_len = int((sources[0] or {}).get("len") or 0) if sources else 0
    total = sum(int((t.get("src") or {}).get("len") or 0) for t in turns)
    total += sum(int(f.get("len") or 0) for f in (head_rec.get("frames") or []))
    return total == src_len, total, src_len


def parse_jsonl(payload: bytes) -> tuple[dict, list[dict]]:
    lines = [ln for ln in payload.splitlines() if ln.strip()]
    if not lines:
        raise ValueError("empty transcript")
    head_rec = json.loads(lines[0].decode("utf-8"))
    turns = [json.loads(ln.decode("utf-8")) for ln in lines[1:]]
    return head_rec, turns


def write_canonical(out_dir: Path, rec_id: str, payload: bytes) -> dict:
    from cosmos_validate import write_declared, read_verified

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
