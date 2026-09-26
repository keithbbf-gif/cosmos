#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic rebind pins. Never opens live opencode.db."""
from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "builds" / "session-tools"))

import session_tools as st  # noqa: E402
from refusals import SessionToolsRefusal  # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, str(e)))


def _ow_db(ws: Path) -> Path:
    db = ws / "opencode.db"
    con = sqlite3.connect(str(db))
    con.executescript(
        """
        CREATE TABLE session (
          id TEXT PRIMARY KEY,
          project_id TEXT NOT NULL,
          workspace_id TEXT,
          slug TEXT NOT NULL,
          directory TEXT NOT NULL,
          title TEXT NOT NULL,
          version TEXT NOT NULL,
          cost REAL NOT NULL DEFAULT 0,
          tokens_input INTEGER NOT NULL DEFAULT 0,
          tokens_output INTEGER NOT NULL DEFAULT 0,
          tokens_reasoning INTEGER NOT NULL DEFAULT 0,
          tokens_cache_read INTEGER NOT NULL DEFAULT 0,
          tokens_cache_write INTEGER NOT NULL DEFAULT 0,
          time_created INTEGER NOT NULL,
          time_updated INTEGER NOT NULL
        );
        INSERT INTO session (id, project_id, workspace_id, slug, directory,
          title, version, cost, tokens_input, tokens_output, tokens_reasoning,
          tokens_cache_read, tokens_cache_write, time_created, time_updated)
        VALUES ('ses_cow_001', 'global', 'ws-old', 'cow-one', '.',
          'packed', '1', 0,0,0,0,0,0, 1, 1);
        INSERT INTO session (id, project_id, workspace_id, slug, directory,
          title, version, cost, tokens_input, tokens_output, tokens_reasoning,
          tokens_cache_read, tokens_cache_write, time_created, time_updated)
        VALUES ('ses_leftover_a', 'global', 'ws-old', 'chat-a', '.',
          'leftover A', '1', 0,0,0,0,0,0, 2, 2);
        """
    )
    con.commit()
    con.close()
    return db


def test_cow_refused():
    td = Path(tempfile.mkdtemp(prefix="st_rbc_"))
    _ow_db(td)
    try:
        st.cmd_rebind("ses_cow_001", td, "ws-new", None, True)
    except SessionToolsRefusal as e:
        return e.kind == "DO_NOT_REINGEST"
    return False


def test_workspace_unknown():
    td = Path(tempfile.mkdtemp(prefix="st_rbw_"))
    try:
        st.cmd_rebind("ses_leftover_a", td, None, None, True)
    except SessionToolsRefusal as e:
        return e.kind == "WORKSPACE_UNKNOWN"
    return False


def test_dry_run_no_write():
    td = Path(tempfile.mkdtemp(prefix="st_rbd_"))
    db = _ow_db(td)
    before = db.read_bytes()
    rec = st.cmd_rebind("ses_leftover_a", td, "ws-new", None, True)
    return rec["kind"] == "DRY_RUN" and db.read_bytes() == before


def test_no_bak():
    td = Path(tempfile.mkdtemp(prefix="st_rbb_"))
    try:
        st.cmd_rebind("ses_leftover_a", td, "ws-new", None, False)
    except SessionToolsRefusal as e:
        return e.kind == "NO_BAK"
    return False


def test_rebind_writes_and_gate():
    td = Path(tempfile.mkdtemp(prefix="st_rbw2_"))
    db = _ow_db(td)
    rec = st.cmd_rebind("ses_leftover_a", td, "ws-new", td / "proof", False)
    gate = rec["gate"]
    con = sqlite3.connect(str(db))
    row = con.execute(
        "SELECT workspace_id, directory FROM session WHERE id='ses_leftover_a'"
    ).fetchone()
    cow = con.execute(
        "SELECT workspace_id FROM session WHERE id='ses_cow_001'"
    ).fetchone()[0]
    con.close()
    return (
        rec["kind"] == "OK"
        and row[0] == "ws-new"
        and Path(row[1]) == td
        and cow == "ws-old"
        and gate["prev_workspace_id"] == "ws-old"
        and Path(gate["bak_path"]).is_file()
        and Path(gate["proof"]).is_file()
    )


def test_not_found():
    td = Path(tempfile.mkdtemp(prefix="st_rbn_"))
    _ow_db(td)
    try:
        st.cmd_rebind("ses_missing", td, "ws-new", None, False)
    except SessionToolsRefusal as e:
        return e.kind == "NOT_FOUND"
    return False


if __name__ == "__main__":
    check("cow DO_NOT_REINGEST", test_cow_refused)
    check("WORKSPACE_UNKNOWN", test_workspace_unknown)
    check("dry-run no write", test_dry_run_no_write)
    check("NO_BAK without db", test_no_bak)
    check("rebind writes gate", test_rebind_writes_and_gate)
    check("NOT_FOUND", test_not_found)
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("PASS" if ok else "FAIL"), l, e)
    print(f"{sum(1 for _, ok, _ in RESULTS if ok)}/{len(RESULTS)}")
    raise SystemExit(1 if bad else 0)
