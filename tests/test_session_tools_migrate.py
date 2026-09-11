#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic migrate + openwork_native pins. Never opens live opencode.db."""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIX = REPO / "tests" / "fixtures" / "session_tools"
sys.path.insert(0, str(REPO / "builds" / "session-tools"))
sys.path.insert(0, str(REPO / "cosmos"))

import session_tools as st  # noqa: E402
from refusals import SessionToolsRefusal  # noqa: E402
import verbs  # noqa: E402

GROK_ID = "grok-aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee"
GROK_STORE = FIX / "grok"
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
        CREATE TABLE message (
          id TEXT PRIMARY KEY,
          session_id TEXT NOT NULL,
          time_created INTEGER NOT NULL,
          time_updated INTEGER NOT NULL,
          data TEXT NOT NULL
        );
        CREATE TABLE part (
          id TEXT PRIMARY KEY,
          message_id TEXT NOT NULL,
          session_id TEXT NOT NULL,
          time_created INTEGER NOT NULL,
          time_updated INTEGER NOT NULL,
          data TEXT NOT NULL
        );
        INSERT INTO session (id, project_id, workspace_id, slug, directory,
          title, version, cost, tokens_input, tokens_output, tokens_reasoning,
          tokens_cache_read, tokens_cache_write, time_created, time_updated)
        VALUES ('ses_cow_001', 'global', 'ws-fix', 'cow-one', '.',
          'packed', '1', 0,0,0,0,0,0, 1, 1);
        INSERT INTO session (id, project_id, workspace_id, slug, directory,
          title, version, cost, tokens_input, tokens_output, tokens_reasoning,
          tokens_cache_read, tokens_cache_write, time_created, time_updated)
        VALUES ('ses_leftover_a', 'global', 'ws-fix', 'chat-a', '.',
          'leftover A', '1', 0,0,0,0,0,0, 2, 2);
        INSERT INTO session (id, project_id, workspace_id, slug, directory,
          title, version, cost, tokens_input, tokens_output, tokens_reasoning,
          tokens_cache_read, tokens_cache_write, time_created, time_updated)
        VALUES ('ses_leftover_b', 'global', 'ws-fix', 'chat-b', '.',
          'leftover B', '1', 0,0,0,0,0,0, 3, 3);
        INSERT INTO message VALUES ('m1', 'ses_leftover_a', 2, 2,
          '{"role":"user","time":{"created":2}}');
        INSERT INTO part VALUES ('p1', 'm1', 'ses_leftover_a', 2, 2,
          '{"type":"text","text":"hi"}');
        """
    )
    con.commit()
    con.close()
    return db


def test_workspace_unknown():
    try:
        st.cmd_migrate(GROK_ID, GROK_STORE, None, Path("."), None, True)
    except SessionToolsRefusal as e:
        return e.kind == "WORKSPACE_UNKNOWN"
    return False


def test_cow_refused():
    try:
        st.cmd_migrate("cow-abc", FIX, "ws", Path("."), None, True)
    except SessionToolsRefusal as e:
        return e.kind == "DO_NOT_REINGEST"
    return False


def test_dry_run_no_write():
    td = Path(tempfile.mkdtemp(prefix="st_mg_"))
    db = _ow_db(td)
    before = db.read_bytes()
    rec = st.cmd_migrate(GROK_ID, GROK_STORE, "ws-fix", td, None, True)
    return rec["kind"] == "DRY_RUN" and db.read_bytes() == before and rec["gate"]["n_turns"] == 2


def test_no_bak():
    td = Path(tempfile.mkdtemp(prefix="st_nobak_"))
    try:
        st.cmd_migrate(GROK_ID, GROK_STORE, "ws-fix", td, None, False)
    except SessionToolsRefusal as e:
        return e.kind == "NO_BAK"
    return False


def test_migrate_writes_and_gate():
    td = Path(tempfile.mkdtemp(prefix="st_mgw_"))
    db = _ow_db(td)
    rec = st.cmd_migrate(GROK_ID, GROK_STORE, "ws-fix", td, td / "proof", False)
    gate = rec["gate"]
    con = sqlite3.connect(str(db))
    n = con.execute("SELECT count(*) FROM session WHERE id=?",
                    (gate["ses_id"],)).fetchone()[0]
    nm = con.execute("SELECT count(*) FROM message WHERE session_id=?",
                     (gate["ses_id"],)).fetchone()[0]
    np = con.execute("SELECT count(*) FROM part WHERE session_id=?",
                     (gate["ses_id"],)).fetchone()[0]
    cow = con.execute("SELECT count(*) FROM session WHERE id='ses_cow_001'").fetchone()[0]
    con.close()
    return (
        rec["kind"] == "OK"
        and n == 1 and nm == 2 and np == 2
        and gate["n_turns_written"] == 2
        and cow == 1
        and Path(gate["bak_path"]).is_file()
        and Path(gate["proof"]).is_file()
        and gate["ses_id"].startswith("ses_grok_")
    )


def test_catalog_match_refuses():
    td = Path(tempfile.mkdtemp(prefix="st_cat_"))
    _ow_db(td)
    store = Path(tempfile.mkdtemp(prefix="st_catstore_"))
    # copy grok fixture layout? use loader that returns catalog-matching vid
    cat = [{"seq": 1, "session_id": "aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee"}]
    (store / "COW_SESSION_CATALOG.json").write_text(json.dumps(cat), encoding="utf-8")

    def load(_s, _id):
        return (
            {"id": GROK_ID, "family": "grok_tui", "legal": False,
             "vendor_session_id": "aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee",
             "aliases": {}},
            [{"seq": 1, "role": "user", "text": "x"}],
        )

    try:
        verbs.migrate(load, GROK_ID, store, "ws", td, None, dry_run=True)
    except SessionToolsRefusal as e:
        return e.kind == "DO_NOT_REINGEST"
    return False


def test_openwork_scan_excludes_cow():
    td = Path(tempfile.mkdtemp(prefix="st_ow_"))
    _ow_db(td)
    rec = st.cmd_scan(["openwork_native"], td, None)
    fam = rec["families"][0]
    return fam["n"] == 2 and fam["n_legal"] == 0 and "ow-ses_leftover_a" in fam["sample_ids"]


def test_openwork_load():
    td = Path(tempfile.mkdtemp(prefix="st_owl_"))
    _ow_db(td)
    rec = st.cmd_load("ow-ses_leftover_a", td, None)
    return rec["kind"] == "OK" and rec["gate"]["n_turns"] == 1 and rec["record"]["family"] == "openwork_native"


def test_openwork_cow_refused():
    td = Path(tempfile.mkdtemp(prefix="st_owc_"))
    _ow_db(td)
    try:
        st.cmd_load("ow-ses_cow_001", td, None)
    except SessionToolsRefusal as e:
        return e.kind == "DO_NOT_REINGEST"
    return False


def test_scan_unknown_family_null_n():
    rec = st.cmd_scan(["claude_desktop"], FIX, None)
    fam = rec["families"][0]
    return fam["status"] == "UNMEASURED" and fam["n"] is None


def test_hold_families_null_n():
    rec = st.cmd_scan(["cursor", "codex", "gemini", "sgh_voice"], FIX, None)
    return all(
        f["status"] == "UNMEASURED" and f["n"] is None
        for f in rec["families"]
    ) and len(rec["families"]) == 4


if __name__ == "__main__":
    check("WORKSPACE_UNKNOWN", test_workspace_unknown)
    check("cow DO_NOT_REINGEST", test_cow_refused)
    check("dry-run no write", test_dry_run_no_write)
    check("NO_BAK without db", test_no_bak)
    check("migrate writes gate", test_migrate_writes_and_gate)
    check("catalog DO_NOT_REINGEST", test_catalog_match_refuses)
    check("openwork scan n=2", test_openwork_scan_excludes_cow)
    check("openwork load", test_openwork_load)
    check("openwork cow refuse", test_openwork_cow_refused)
    check("unknown family n is null", test_scan_unknown_family_null_n)
    check("HOLD families n is null", test_hold_families_null_n)
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("PASS" if ok else "FAIL"), l, e)
    print(f"{sum(1 for _, ok, _ in RESULTS if ok)}/{len(RESULTS)}")
    raise SystemExit(1 if bad else 0)
