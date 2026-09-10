#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic Slice-1 pins: scan + load cowork wrap and grok_tui."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIX = REPO / "tests" / "fixtures" / "session_tools"
sys.path.insert(0, str(REPO / "builds" / "session-tools"))
sys.path.insert(0, str(REPO / "cosmos"))

import session_tools as st  # noqa: E402
from refusals import SessionToolsRefusal  # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, str(e)))


def test_scan_cowork_counts():
    rec = st.cmd_scan(["cowork"], FIX, None)
    fam = rec["families"][0]
    return fam["n"] == 2 and fam["n_legal"] == 1 and rec["legal_omitted"] == 1


def test_scan_does_not_use_recents_cap():
    rec = st.cmd_scan(["cowork"], FIX, None)
    return rec["families"][0]["n"] != 200


def test_load_cow_id_stable():
    rec = st.cmd_load("cow-abc", FIX, None)
    return rec["kind"] == "OK" and rec["record"]["id"] == "cow-abc" and rec["gate"]["n_turns"] == 1


def test_load_legal_refuses():
    try:
        st.cmd_load("cow-leg1", FIX, None)
    except SessionToolsRefusal as e:
        return e.kind == "LEGAL_OMITTED"
    return False


def test_scan_grok():
    rec = st.cmd_scan(["grok_tui"], FIX / "grok", None)
    fam = rec["families"][0]
    return fam["n"] == 1 and "grok-aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee" in fam["sample_ids"]


def test_load_grok():
    rec = st.cmd_load("grok-aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee", FIX / "grok", None)
    return rec["kind"] == "OK" and rec["gate"]["n_turns"] == 2 and rec["record"]["family"] == "grok_tui"


def test_load_out_jsonl_sidecar():
    td = Path(tempfile.mkdtemp(prefix="st_out_"))
    rec = st.cmd_load("cow-abc", FIX, td)
    jsonl = td / "cow-abc.ctr.jsonl"
    decl = td / "cow-abc.ctr.decl.json"
    if not jsonl.is_file() or not decl.is_file():
        return False
    d = json.loads(decl.read_text(encoding="utf-8"))
    return d.get("sha") == rec["written"]["sha"] and d.get("hmac") is False


def test_guessed_root_refuses():
    try:
        st.cmd_scan(["cowork"], None, None)
    except SessionToolsRefusal as e:
        return e.kind == "GUESSED_ROOT"
    return False


def test_cli_scan():
    rc = st.main(["scan", "--family", "cowork", "--store", str(FIX)])
    return rc == 0


if __name__ == "__main__":
    check("scan cowork n=2 n_legal=1", test_scan_cowork_counts)
    check("scan n is not recents 200", test_scan_does_not_use_recents_cap)
    check("load cow-abc id-stable", test_load_cow_id_stable)
    check("load cow-leg1 LEGAL_OMITTED", test_load_legal_refuses)
    check("scan grok_tui n=1", test_scan_grok)
    check("load grok two turns", test_load_grok)
    check("load --out jsonl+decl sha-only", test_load_out_jsonl_sidecar)
    check("scan without store GUESSED_ROOT", test_guessed_root_refuses)
    check("cli scan rc=0", test_cli_scan)
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("PASS" if ok else "FAIL"), l, e)
    print(f"{sum(1 for _, ok, _ in RESULTS if ok)}/{len(RESULTS)}")
    raise SystemExit(1 if bad else 0)
