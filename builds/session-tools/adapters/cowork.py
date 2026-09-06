#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cowork packed catalog wrap. Do not re-ingest 666. Do not recode the plugin.

Store: COW_SESSION_CATALOG.json + ordered_transcripts\\.
id = cow-{session_id} (stable with Open Sessions). legal=(stream==legal).
Scan quotes catalog n / n_legal — never recents n_shown=200.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from refusals import LEGAL_OMITTED, NO_STORE, NOT_FOUND, UNPARSEABLE, Refusal
from schema import (
    head_record, sha256_bytes, source_record, span_src, stable_id, turn_record,
)

FAMILY = "cowork"
PREFIX = "cow"
CATALOG_NAME = "COW_SESSION_CATALOG.json"
TRANS_DIR = "ordered_transcripts"
LEGAL_STREAMS = {"legal"}

# ## [n] ROLE  — Cowork ordered md when that shape exists.
_HEADING = re.compile(
    rb"^## \[(\d+)\][ \t]+(\S+)[ \t]*(?:\r?\n|$)",
    re.MULTILINE,
)

_ROLE_MAP = {
    "user": "user",
    "human": "user",
    "assistant": "assistant",
    "ai": "assistant",
    "model": "assistant",
    "system": "system",
    "tool": "tool_result",
    "tool_result": "tool_result",
    "tool_call": "tool_call",
    "tool_use": "tool_call",
    "meta": "meta",
}


def catalog_path(store: Path) -> Path | None:
    store = Path(store)
    if store.is_file() and store.name == CATALOG_NAME:
        return store
    cand = store / CATALOG_NAME
    if cand.is_file():
        return cand
    return None


def load_catalog(path: Path) -> list[dict]:
    raw = path.read_bytes()
    try:
        obj = json.loads(raw.decode("utf-8"))
    except ValueError as e:
        raise Refusal(UNPARSEABLE, f"catalog JSON: {e}", path=str(path))
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in ("sessions", "rows", "catalog"):
            if isinstance(obj.get(k), list):
                return obj[k]
    raise Refusal(UNPARSEABLE, "catalog is not a list of rows", path=str(path))


def is_legal_row(row: dict) -> bool:
    return str(row.get("stream") or "").strip().lower() in LEGAL_STREAMS


def row_id(row: dict) -> str:
    return stable_id(PREFIX, str(row.get("session_id") or ""))


def opencode_id(seq) -> str | None:
    try:
        n = int(seq)
    except (TypeError, ValueError):
        return None
    return f"ses_cow_{n:03d}"


def _transcripts_dir(cat: Path) -> Path:
    return cat.parent / TRANS_DIR


def md_path(cat: Path, row: dict) -> Path:
    name = str(row.get("filename") or "")
    return _transcripts_dir(cat) / name


def discover(store: Path) -> dict:
    """Scan Hits. Empty dir without catalog → NO_STORE, not n=0."""
    store = Path(store)
    cat = catalog_path(store)
    if cat is None:
        raise Refusal(NO_STORE, f"no {CATALOG_NAME} under {store}",
                      path=str(store), n=None)
    rows = load_catalog(cat)
    hits = []
    n_legal = 0
    total_bytes = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        legal = is_legal_row(row)
        if legal:
            n_legal += 1
        mp = md_path(cat, row)
        size = 0
        sha = None
        if mp.is_file():
            data = mp.read_bytes()
            size = len(data)
            total_bytes += size
            sha = sha256_bytes(data)
        elif row.get("size"):
            try:
                total_bytes += int(row["size"])
            except (TypeError, ValueError):
                pass
        hits.append({
            "family": FAMILY,
            "id": row_id(row),
            "path": str(mp),
            "vendor_session_id": str(row.get("session_id") or ""),
            "stream": str(row.get("stream") or ""),
            "legal": legal,
            "bytes": size,
            "sha256": sha,
            "title": str(row.get("title") or ""),
            "seq": row.get("seq"),
            "filename": row.get("filename"),
        })
    sample = [h["id"] for h in hits[:5]]
    return {
        "status": "OK",
        "path": str(cat),
        "n": len(hits),
        "n_legal": n_legal,
        "bytes": total_bytes,
        "sample_ids": sample,
        "hits": hits,
    }


def _map_role(raw: str) -> str | None:
    return _ROLE_MAP.get(raw.strip().lower())


def parse_md_turns(data: bytes) -> tuple[list[dict], list[str]]:
    """Parse ## [n] ROLE when present; else one user turn = whole body.

    Honor the file. Do not invent turns from a catalog count of 0.
    """
    unknown: list[str] = []
    matches = list(_HEADING.finditer(data))
    if not matches:
        if not data:
            return [], unknown
        turn = turn_record(
            seq=1, role="user", text=data.decode("utf-8", errors="replace"),
            src=span_src(0, 0, len(data), data),
        )
        return [turn], unknown

    # seq must be 1-based contiguous or UNPARSEABLE
    seqs = [int(m.group(1)) for m in matches]
    if seqs != list(range(1, len(seqs) + 1)):
        raise Refusal(UNPARSEABLE,
                      f"heading seq gap or not 1-based: {seqs[:12]}")

    turns: list[dict] = []
    for i, m in enumerate(matches):
        raw_role = m.group(2).decode("ascii", errors="replace")
        role = _map_role(raw_role)
        if role is None:
            unknown.append(raw_role)
            role = "meta"
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(data)
        body = data[start:end]
        text = body.decode("utf-8", errors="replace").rstrip("\r\n")
        turns.append(turn_record(
            seq=i + 1,
            role=role,
            text=text,
            src=span_src(0, start, end - start, data),
        ))
    return turns, unknown


def _find_row(rows: list[dict], vendor: str) -> dict | None:
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("session_id") or "") == vendor:
            return row
        if row_id(row) == vendor or row_id(row) == f"cow-{vendor}":
            return row
    return None


def load(store: Path, sid: str | None = None, path: Path | None = None) -> dict:
    store = Path(store)
    cat = catalog_path(store)
    if cat is None:
        raise Refusal(NO_STORE, f"no {CATALOG_NAME} under {store}",
                      path=str(store), n=None)
    rows = load_catalog(cat)
    row = None
    vendor = None
    if sid:
        vendor = sid[4:] if sid.startswith("cow-") else sid
        row = _find_row(rows, vendor)
    elif path is not None:
        p = Path(path)
        for r in rows:
            if md_path(cat, r).resolve() == p.resolve() or str(r.get("filename")) == p.name:
                row = r
                break
    if row is None:
        raise Refusal(NOT_FOUND, f"no cowork session {sid or path}",
                      id=sid, path=str(path) if path else None)

    cid = row_id(row)
    vendor = str(row.get("session_id") or "")
    legal = is_legal_row(row)
    aliases = {
        "seq": row.get("seq"),
        "filename": row.get("filename"),
        "opencode_id": opencode_id(row.get("seq")),
    }
    if legal:
        raise Refusal(
            LEGAL_OMITTED,
            f"{cid} stream=legal — body omitted from this TUI",
            id=cid,
            family=FAMILY,
            vendor_session_id=vendor,
            legal=True,
            aliases=aliases,
        )

    mp = md_path(cat, row)
    if not mp.is_file():
        raise Refusal(NOT_FOUND, f"transcript missing: {mp}", id=cid, path=str(mp))
    data = mp.read_bytes()
    turns, unknown = parse_md_turns(data)
    src = source_record(idx=0, path=str(mp), kind="md", data=data, fidelity="span")
    head = head_record(
        id=cid,
        family=FAMILY,
        vendor_session_id=vendor,
        title=str(row.get("title") or ""),
        stream=str(row.get("stream") or ""),
        legal=False,
        cwd="",
        n_turns=len(turns),
        sources=[src],
        models=[],
        t_first=None,
        t_last=None,
        aliases=aliases,
    )
    return {
        "head": head,
        "turns": turns,
        "source_bytes": data,
        "unknown_roles": unknown,
        "truncated": False,
    }
