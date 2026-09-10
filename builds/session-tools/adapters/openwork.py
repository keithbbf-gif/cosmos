#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""openwork_native — leftover Chat ses_* (not ses_cow_*). scan/load only."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from refusals import SessionToolsRefusal
from schema import head, legal_id, sha256_path, turn

FAMILY = "openwork_native"
LEGAL_MARK = ("legal", "p:\\legal", "/legal/")


def _db(store: Path) -> Path:
    if store.is_file() and store.suffix.lower() in (".db", ".sqlite"):
        return store
    p = store / "opencode.db"
    if p.is_file():
        return p
    raise SessionToolsRefusal("NO_STORE", str(store))


def _connect(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + "?mode=ro"
    try:
        return sqlite3.connect(uri, uri=True)
    except sqlite3.Error as e:
        raise SessionToolsRefusal("SQLITE_CORRUPT", str(e)) from e


def _is_cow(sid: str) -> bool:
    return str(sid or "").startswith("ses_cow_")


def _legal(title: str, directory: str) -> bool:
    blob = f"{title} {directory}".lower()
    return any(m in blob for m in LEGAL_MARK)


def scan(store: Path) -> dict:
    db = _db(store)
    n, sha = sha256_path(db)
    con = _connect(db)
    try:
        rows = list(con.execute(
            "SELECT id, title, directory FROM session WHERE id NOT LIKE 'ses_cow_%'"))
    except sqlite3.Error as e:
        con.close()
        raise SessionToolsRefusal("SCHEMA_UNKNOWN", str(e)) from e
    con.close()
    n_legal = sum(1 for r in rows if _legal(r[1] or "", r[2] or ""))
    ids = [legal_id("ow", r[0]) for r in rows[:5]]
    return {
        "family": FAMILY,
        "status": "OK",
        "path": str(db),
        "n": len(rows),
        "n_legal": n_legal,
        "bytes": n,
        "source_sha": sha,
        "sample_ids": ids,
    }


def load(store: Path, rec_id: str) -> tuple[dict, list]:
    want = rec_id[3:] if rec_id.startswith("ow-") else rec_id
    if _is_cow(want):
        raise SessionToolsRefusal("DO_NOT_REINGEST", rec_id)
    db = _db(store)
    _, sha = sha256_path(db)
    con = _connect(db)
    try:
        row = con.execute(
            "SELECT id, title, directory, workspace_id FROM session WHERE id=?",
            (want,),
        ).fetchone()
        if row is None:
            con.close()
            raise SessionToolsRefusal("NOT_FOUND", rec_id)
        sid, title, directory, ws = row
        if _is_cow(sid):
            con.close()
            raise SessionToolsRefusal("DO_NOT_REINGEST", rec_id)
        legal = _legal(title or "", directory or "")
        msgs = list(con.execute(
            "SELECT id, data FROM message WHERE session_id=? ORDER BY time_created, id",
            (sid,),
        ))
        parts = {}
        for mid, data in con.execute(
                "SELECT message_id, data FROM part WHERE session_id=? ORDER BY time_created, id",
                (sid,)):
            parts.setdefault(mid, []).append(data)
    except sqlite3.Error as e:
        con.close()
        raise SessionToolsRefusal("SCHEMA_UNKNOWN", str(e)) from e
    con.close()
    cid = legal_id("ow", sid)
    src = {"path": str(db), "kind": "sqlite", "len": 0, "sha256": sha,
           "fidelity": "blob", "idx": 0}
    if legal:
        raise SessionToolsRefusal("LEGAL_OMITTED", cid)
    turns = []
    for i, (mid, data) in enumerate(msgs, start=1):
        role = "user"
        text = ""
        try:
            obj = json.loads(data) if data else {}
            role = str(obj.get("role") or "user")
        except ValueError:
            obj = {}
        for raw in parts.get(mid, []):
            try:
                p = json.loads(raw) if raw else {}
            except ValueError:
                p = {}
            if p.get("type") == "text":
                text = str(p.get("text") or text)
        turns.append(turn(seq=i, role=role, text=text,
                          src={"source_idx": 0, "blob_sha": sha, "key": mid}))
    h = head(id=cid, family=FAMILY, vendor_session_id=sid, title=title or "",
             stream="openwork", legal=False, cwd=directory or "",
             n_turns=len(turns), sources=[src],
             aliases={"opencode_id": sid, "seq": None, "filename": None})
    if ws:
        h["aliases"]["workspace_id"] = ws
    return h, turns
