#!/usr/bin/env python3
"""Cowork pack adapter — catalog wrap. Do not re-ingest 666."""
from __future__ import annotations

import json
from pathlib import Path

from refusals import SessionToolsRefusal
from schema import head, legal_id, sha256_path, turn

FAMILY = "cowork"
LEGAL_STREAMS = frozenset({"legal"})


def _catalog_path(store: Path) -> Path:
    if store.is_file() and store.name.endswith(".json"):
        return store
    p = store / "COW_SESSION_CATALOG.json"
    if p.is_file():
        return p
    raise SessionToolsRefusal("NO_STORE", f"no COW_SESSION_CATALOG.json under {store}")


def _load_catalog(store: Path) -> tuple[Path, list]:
    cat = _catalog_path(store)
    raw = json.loads(cat.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise SessionToolsRefusal("UNPARSEABLE", f"{cat}: catalog is not a list")
    return cat, raw


def _md_path(store: Path, row: dict) -> Path | None:
    name = row.get("filename")
    if not name:
        return None
    cat = _catalog_path(store)
    for base in (cat.parent / "ordered_transcripts", store / "ordered_transcripts", store):
        p = base / name
        if p.is_file():
            return p
    return None


def scan(store: Path) -> dict:
    cat, rows = _load_catalog(store)
    n_legal = sum(1 for r in rows if str(r.get("stream") or "").lower() in LEGAL_STREAMS)
    ids = [legal_id("cow", r.get("session_id") or r.get("seq")) for r in rows[:5]]
    return {
        "family": FAMILY,
        "status": "OK",
        "path": str(cat),
        "n": len(rows),
        "n_legal": n_legal,
        "bytes": cat.stat().st_size,
        "sample_ids": ids,
    }


def load(store: Path, rec_id: str) -> tuple[dict, list]:
    _cat, rows = _load_catalog(store)
    want = rec_id.removeprefix("cow-")
    row = None
    for r in rows:
        sid = str(r.get("session_id") or "")
        if sid == want or legal_id("cow", sid) == rec_id:
            row = r
            break
    if row is None:
        raise SessionToolsRefusal("NOT_FOUND", rec_id)
    stream = str(row.get("stream") or "unknown").lower()
    legal = stream in LEGAL_STREAMS
    cid = legal_id("cow", row.get("session_id") or row.get("seq"))
    md = _md_path(store, row)
    src = {"path": str(md) if md else "", "kind": "md", "len": 0, "sha256": "", "fidelity": "span"}
    turns: list = []
    if md and md.is_file():
        n, sha = sha256_path(md)
        src.update({"len": n, "sha256": sha, "idx": 0})
        if not legal:
            body = md.read_text(encoding="utf-8", errors="replace")
            turns = [turn(seq=1, role="user", text=body, src={"source_idx": 0, "off": 0, "len": n, "sha256": sha})]
    if legal:
        raise SessionToolsRefusal("LEGAL_OMITTED", cid)
    h = head(
        id=cid, family=FAMILY, vendor_session_id=str(row.get("session_id") or ""),
        title=str(row.get("title") or ""), stream=stream, legal=False,
        n_turns=len(turns), sources=[src],
        aliases={"seq": row.get("seq"), "filename": row.get("filename"),
                 "opencode_id": f"ses_cow_{int(row.get('seq') or 0):03d}" if row.get("seq") else None},
    )
    return h, turns
