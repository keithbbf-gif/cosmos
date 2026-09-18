#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_recall - cross-session recall over the authority ledger (COSMOS_next).

Borrowed from Hermes Agent's SessionDB (SQLite WAL + FTS5 search across past sessions)
and re-shaped for COSMOS canon:

  * PROJECTION, NEVER AUTHORITY. The SQLite file indexes CONVO_OPENED / CONVO_TURN
    records from the signed ledger. Delete it and rebuild() produces the same rows
    (state_sha proves it). Nothing is ever written to the index that the chain does
    not hold.
  * VERIFIED, INCREMENTAL. refresh() reads only the ledger bytes after its checkpoint
    (offset + prev_sha + seq) through the ledger's own chain/MAC walk. A ledger shorter
    than the checkpoint REFUSES (TRUNCATED) - the index never outlives its history.
  * OWNER-SCOPED. search() returns turns only from sessions whose owner equals the
    caller's principal (cosmos_convo's rule; an unknown and a foreign session look the
    same). `captain:*` principals search everything.
  * READS NEVER MKDIR. search() on a missing index is UNMEASURED, not an empty result
    and not a new file.
  * WAL, BEGIN IMMEDIATE, short transactions - the Hermes write pattern.
  * User text never reaches FTS5 syntax: every query term is quoted.

    see tests/test_hermes_features.py
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Optional

SCHEMA = "cosmos-recall/1"


class RecallError(RuntimeError):
    """kind in {TRUNCATED, NO_FTS5, BAD_QUERY}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _quote_terms(query: str) -> str:
    terms = [t for t in re.findall(r"\w+", str(query or ""), re.UNICODE) if t]
    if not terms:
        raise RecallError("BAD_QUERY", "query has no searchable terms")
    return " ".join('"%s"' % t.replace('"', '""') for t in terms[:16])


class Recall:
    def __init__(self, ledger, db_path: str | os.PathLike):
        self.ledger = ledger
        self.db_path = Path(db_path)

    # ---------------- storage ----------------
    def _connect(self, create: bool) -> Optional[sqlite3.Connection]:
        if not create and not self.db_path.exists():
            return None
        if create:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(str(self.db_path), timeout=20, isolation_level=None)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
        if create:
            try:
                con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS turns USING fts5("
                            "text, sid UNINDEXED, role UNINDEXED, seq UNINDEXED, "
                            "t UNINDEXED, tokenize='unicode61')")
            except sqlite3.OperationalError as e:
                con.close()
                raise RecallError("NO_FTS5", f"this sqlite build has no FTS5: {e}") from e
            con.execute("CREATE TABLE IF NOT EXISTS sessions (sid TEXT PRIMARY KEY, "
                        "owner TEXT, title TEXT, opened REAL)")
            con.execute("CREATE TABLE IF NOT EXISTS checkpoint (k INTEGER PRIMARY KEY "
                        "CHECK (k = 1), offset INTEGER, prev_sha TEXT, seq INTEGER)")
        return con

    def _checkpoint(self, con) -> tuple[int, str, int]:
        row = con.execute("SELECT offset, prev_sha, seq FROM checkpoint WHERE k = 1").fetchone()
        return (0, "", 0) if row is None else (int(row[0]), str(row[1]), int(row[2]))

    # ---------------- indexing ----------------
    def refresh(self) -> dict:
        con = self._connect(create=True)
        try:
            off, prev, seq = self._checkpoint(con)
            path = Path(self.ledger._path)
            size = path.stat().st_size if path.exists() else 0
            if size < off:
                raise RecallError("TRUNCATED", f"ledger is {size} bytes, index checkpoint "
                                               f"is {off} - rebuild after the incident")
            n_turns = n_sessions = 0
            if size > off:
                with open(path, "rb") as fh:
                    fh.seek(off)
                    data = fh.read(size - off)
                con.execute("BEGIN IMMEDIATE")
                try:
                    for rec, prev, seq, off, _nl in self.ledger._walk(
                            data, off, prev, seq, strict_tail=False, line_no=None):
                        if rec is None:
                            continue
                        ev, p = rec.get("event"), rec.get("payload") or {}
                        if ev == "CONVO_OPENED" and isinstance(p.get("sid"), str):
                            con.execute("INSERT OR IGNORE INTO sessions VALUES (?,?,?,?)",
                                        (p["sid"], p.get("owner"), p.get("title"),
                                         rec.get("t")))
                            n_sessions += 1
                        elif (ev == "CONVO_TURN" and isinstance(p.get("text"), str)
                              and p["text"].strip()):
                            con.execute("INSERT INTO turns VALUES (?,?,?,?,?)",
                                        (p["text"], p.get("sid"), p.get("role"),
                                         p.get("seq"), rec.get("t")))
                            n_turns += 1
                    con.execute("INSERT INTO checkpoint VALUES (1,?,?,?) ON CONFLICT(k) DO "
                                "UPDATE SET offset=excluded.offset, "
                                "prev_sha=excluded.prev_sha, seq=excluded.seq",
                                (off, prev, seq))
                    con.execute("COMMIT")
                except BaseException:
                    con.execute("ROLLBACK")
                    raise
            return {"schema": SCHEMA, "indexed_turns": n_turns,
                    "indexed_sessions": n_sessions, "ledger_seq": seq, "offset": off}
        finally:
            con.close()

    def rebuild(self) -> dict:
        """Drop the index and refold from genesis. Returns state_sha for drift checks."""
        for suffix in ("", "-wal", "-shm"):
            p = Path(str(self.db_path) + suffix)
            if p.exists():
                p.unlink()          # a projection file, not history: safe to discard
        out = self.refresh()
        out["state_sha"] = self.state_sha()
        return out

    def state_sha(self) -> Optional[str]:
        con = self._connect(create=False)
        if con is None:
            return None
        try:
            h = hashlib.sha256()
            for row in con.execute("SELECT sid, role, seq, t, text FROM turns "
                                   "ORDER BY t, sid, seq"):
                h.update(json.dumps(row, separators=(",", ":")).encode("utf-8"))
            for row in con.execute("SELECT sid, owner, title FROM sessions ORDER BY sid"):
                h.update(json.dumps(row, separators=(",", ":")).encode("utf-8"))
            return h.hexdigest()
        finally:
            con.close()

    # ---------------- search ----------------
    def search(self, query: str, *, principal: Optional[str], limit: int = 10) -> dict:
        match = _quote_terms(query)
        con = self._connect(create=False)
        if con is None:
            return {"schema": SCHEMA, "kind": "UNMEASURED", "results": None,
                    "note": "no recall index yet - refresh() builds it; reads never mkdir"}
        try:
            everything = str(principal or "").startswith("captain:")
            sql = ("SELECT t.sid, s.title, t.role, t.seq, t.t, "
                   "snippet(turns, 0, '[', ']', ' ... ', 12), bm25(turns) "
                   "FROM turns t JOIN sessions s ON s.sid = t.sid "
                   "WHERE turns MATCH ? ")
            args: list = [match]
            if not everything:
                sql += "AND s.owner IS ? "
                args.append(principal)
            sql += "ORDER BY bm25(turns) LIMIT ?"
            args.append(max(1, min(int(limit), 50)))
            rows = con.execute(sql, args).fetchall()
        finally:
            con.close()
        return {"schema": SCHEMA, "kind": "MEASURED", "query": match,
                "results": [{"sid": r[0], "title": r[1], "role": r[2], "seq": r[3],
                             "t": r[4], "snippet": r[5], "rank": r[6]} for r in rows]}
