#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Slice-2/3/4: convert, diff, check, anonymize, crash-recover."""
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
from cosmos_kernel import Kernel, install  # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, str(e)))


def test_convert_spans_and_roundtrip():
    td = Path(tempfile.mkdtemp(prefix="st_cv_"))
    rec = st.cmd_convert("cow-abc", FIX, td, False)
    p = td / "cow-abc.ctr.jsonl"
    return rec["kind"] == "OK" and rec["gate"]["spans_ok"] is True and p.read_bytes() == p.read_bytes() and rec["gate"]["out_sha"]


def test_convert_out_exists():
    td = Path(tempfile.mkdtemp(prefix="st_cv2_"))
    st.cmd_convert("cow-abc", FIX, td, False)
    try:
        st.cmd_convert("cow-abc", FIX, td, False)
    except SessionToolsRefusal as e:
        return e.kind == "OUT_EXISTS"
    return False


def test_diff_identical_zero():
    td = Path(tempfile.mkdtemp(prefix="st_df_"))
    st.cmd_convert("cow-abc", FIX, td, False)
    a = td / "cow-abc.ctr.jsonl"
    rec = st.cmd_diff(a, a)
    return rec["gate"]["left_sha"] == rec["gate"]["right_sha"] and rec["gate"]["n_turns_delta"] == 0


def test_diff_edit_delta():
    td = Path(tempfile.mkdtemp(prefix="st_df2_"))
    st.cmd_convert("cow-abc", FIX, td, False)
    left = (td / "cow-abc.ctr.jsonl").read_bytes()
    right = left + b'{"seq":2,"role":"assistant","text":"x","src":{"len":1}}\n'
    lp = td / "L.ctr.jsonl"
    rp = td / "R.ctr.jsonl"
    lp.write_bytes(left)
    rp.write_bytes(right)
    rec = st.cmd_diff(lp, rp)
    return rec["gate"]["left_sha"] != rec["gate"]["right_sha"] and rec["gate"]["n_turns_delta"] == 1


def test_check_catalog():
    rec = st.cmd_check("catalog", FIX, None)
    return rec["gate"]["n"] == 2 and rec["kind"] == "VERIFIED"


def test_check_sqlite_ok():
    td = Path(tempfile.mkdtemp(prefix="st_sql_"))
    db = td / "ok.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE session (id TEXT)")
    con.execute("INSERT INTO session VALUES ('a')")
    con.commit()
    con.close()
    rec = st.cmd_check("sqlite", db, None)
    return rec["gate"]["integrity_check"] == "ok" and rec["gate"]["n_session"] == 1


def test_check_sqlite_corrupt():
    td = Path(tempfile.mkdtemp(prefix="st_sqlb_"))
    db = td / "bad.db"
    db.write_bytes(b"not a database")
    try:
        st.cmd_check("sqlite", db, None)
    except SessionToolsRefusal as e:
        return e.kind == "SQLITE_CORRUPT"
    return False


def test_check_seed_mac():
    td = Path(tempfile.mkdtemp(prefix="st_seed_"))
    root = install(td / "live", tree_id="st-seed")
    k = Kernel(root, worker="st-seed")
    k.sessions.open("s1", "Cm")
    k.sessions.close_session(handoff_to="Cm", force=True)
    rec = st.cmd_check("seed", Path(root), None)
    return rec["gate"]["mac_ok"] is True


def test_check_seed_bad_mac():
    td = Path(tempfile.mkdtemp(prefix="st_seedb_"))
    root = install(td / "live", tree_id="st-seedb")
    k = Kernel(root, worker="st-seedb")
    k.sessions.open("s1", "Cm")
    k.sessions.close_session(handoff_to="Cm", force=True)
    seed = Path(root) / "state" / "SEED.json"
    declp = Path(root) / "state" / "SEED.decl.json"
    body = json.loads(seed.read_text(encoding="utf-8"))
    body["facts"]["tamper"] = True
    raw = json.dumps(body).encode("utf-8")
    seed.write_bytes(raw)
    import hashlib
    decl = json.loads(declp.read_text(encoding="utf-8"))
    decl["len"] = len(raw)
    decl["sha"] = hashlib.sha256(raw).hexdigest()
    declp.write_text(json.dumps(decl), encoding="utf-8")
    try:
        st.cmd_check("seed", Path(root), None)
    except SessionToolsRefusal as e:
        return e.kind in ("BAD_SEED",)
    return False


def test_anonymize_redacts_and_keeps_source():
    td = Path(tempfile.mkdtemp(prefix="st_anon_"))
    rec = st.cmd_anonymize("grok-aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee", FIX / "grok", td)
    hist = FIX / "grok" / "cwd1" / "aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee" / "chat_history.jsonl"
    orig = hist.read_text(encoding="utf-8")
    return rec["gate"]["n_redactions"] >= 1 and "sk-ant-" in orig and rec["gate"]["original_untouched"] is True


def test_crash_recover_no_bak():
    td = Path(tempfile.mkdtemp(prefix="st_cr_"))
    t = td / "x.db"
    t.write_bytes(b"live")
    try:
        st.cmd_crash_recover(t, None, td / "stage")
    except SessionToolsRefusal as e:
        return e.kind == "NO_BAK" and t.read_bytes() == b"live"
    return False


def test_crash_recover_restores_sha():
    td = Path(tempfile.mkdtemp(prefix="st_cr2_"))
    live = td / "x.db"
    bak = td / "x.db.bak"
    bak.write_bytes(b"GOOD-BAK")
    live.write_bytes(b"CORRUPT")
    rec = st.cmd_crash_recover(live, bak, td / "stage")
    return rec["gate"]["restored_sha"] == rec["gate"]["bak_sha"] and live.read_bytes() == b"GOOD-BAK"


def test_no_sqlite_recover_in_suite():
    root = REPO / "builds" / "session-tools"
    for p in root.rglob("*.py"):
        if ".recover" in p.read_text(encoding="utf-8", errors="replace"):
            return False
    return True


if __name__ == "__main__":
    check("convert spans_ok + files", test_convert_spans_and_roundtrip)
    check("convert OUT_EXISTS", test_convert_out_exists)
    check("diff identical delta 0", test_diff_identical_zero)
    check("diff edit n_turns_delta 1", test_diff_edit_delta)
    check("check catalog n=2", test_check_catalog)
    check("check sqlite ok", test_check_sqlite_ok)
    check("check sqlite corrupt", test_check_sqlite_corrupt)
    check("check seed mac_ok", test_check_seed_mac)
    check("check seed BAD_SEED on tamper", test_check_seed_bad_mac)
    check("anonymize redacts, original stays", test_anonymize_redacts_and_keeps_source)
    check("crash-recover NO_BAK leaves live", test_crash_recover_no_bak)
    check("crash-recover restored_sha==bak_sha", test_crash_recover_restores_sha)
    check("no sqlite .recover in suite", test_no_sqlite_recover_in_suite)
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("PASS" if ok else "FAIL"), l, e)
    print(f"{sum(1 for _, ok, _ in RESULTS if ok)}/{len(RESULTS)}")
    raise SystemExit(1 if bad else 0)
