#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic pins for session-tools Slice-1 (scan + load).

No live opencode.db write. No live Core bounce. Fixture n/n_legal, not
recents n_shown=200. Legal load refuses with no body.
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
ST_DIR = REPO / "builds" / "session-tools"
FIX = HERE / "fixtures" / "session_tools"
COW_STORE = FIX / "cowork"
GROK_STORE = FIX / "grok_tui"
CLI = ST_DIR / "session_tools.py"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ST_DIR))

import session_tools as st  # noqa: E402
from declared import read_verified  # noqa: E402
from schema import SCHEMA  # noqa: E402

GROK_ID = "grok-01a07461-9a43-74b0-a903-743dfc1a0748"
GROK_LEGAL_ID = "grok-bbbbbbbb-1111-2222-3333-444444444444"
GROK_HIST = (
    GROK_STORE / "C%3A%5Cfake%5Ccosmos"
    / "01a07461-9a43-74b0-a903-743dfc1a0748" / "chat_history.jsonl"
)

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def run_main(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = st.main(list(argv))
    raw = buf.getvalue()
    rec = json.loads(raw)
    return rc, rec


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def t_scan_cowork_fixture_n_legal():
    rc, rec = run_main(["scan", "--family", "cowork", "--store", str(COW_STORE)])
    fam = rec["families"]["cowork"]
    n, n_legal = fam["n"], fam["n_legal"]
    return (
        rc == 0 and rec["kind"] == "OK" and rec["verb"] == "scan"
        and rec["schema"] == "cosmos-session-tools-result/1"
        and n == 3 and n_legal == 1
        and rec["legal_omitted"] == 1
        and rec["gate"]["n"] == 3 and rec["gate"]["n_legal"] == 1
        and n != 200 and rec["gate"]["n"] != 200
        and "cow-abc" in fam["sample_ids"]
    )


def t_scan_not_recents_200():
    rc, rec = run_main(["scan", "--family", "cowork", "--store", str(COW_STORE)])
    return rec["gate"]["n"] == 3 and rec["gate"]["n"] != 200


def t_scan_grok_counts_both_files_only():
    rc, rec = run_main(["scan", "--family", "grok_tui", "--store", str(GROK_STORE)])
    fam = rec["families"]["grok_tui"]
    ids = fam["sample_ids"]
    return (
        rc == 0 and rec["kind"] == "OK"
        and fam["n"] == 2 and fam["n_legal"] == 1
        and GROK_ID in ids and GROK_LEGAL_ID in ids
        and "dead-session-missing-history" not in "".join(ids)
    )


def t_load_cow_abc():
    rc, rec = run_main(["load", "--id", "cow-abc", "--store", str(COW_STORE)])
    src = Path(COW_STORE / "ordered_transcripts" / "001_clocks.md")
    want_sha = sha_file(src)
    roles = [t["role"] for t in rec.get("turns") or []]
    texts = " ".join(t.get("text") or "" for t in rec.get("turns") or [])
    return (
        rc == 0 and rec["kind"] == "OK"
        and rec["schema"] == "cosmos-session-tools-result/1"
        and rec.get("id") == "cow-abc"
        and rec.get("family") == "cowork"
        and rec.get("vendor_session_id") == "abc"
        and rec["gate"]["schema"] == SCHEMA
        and rec["gate"]["n_turns"] == 2
        and rec["gate"]["n_turns"] == len(rec["turns"])
        and rec["n_turns"] == 2
        and rec["gate"]["source_sha"] == want_sha
        and rec["sources"][0]["sha256"] == want_sha
        and rec["aliases"]["opencode_id"] == "ses_cow_001"
        and roles == ["user", "assistant"]
        and "opened clocks" in texts and "clocks are registered" in texts
        and rec["hmac"] is False
        and rec["legal_omitted"] is False
    )


def t_load_cow_legal_omitted():
    rc, rec = run_main(["load", "--id", "cow-law", "--store", str(COW_STORE)])
    blob = json.dumps(rec)
    return (
        rc == 2 and rec["kind"] == "LEGAL_OMITTED"
        and rec["legal_omitted"] is True
        and rec.get("id") == "cow-law"
        and "turns" not in rec
        and "text" not in rec
        and "secret legal" not in blob
        and "legal transcript body" not in blob
    )


def t_load_cow_topic_honors_file():
    """Catalog turns=0; file has no ## headings → one user turn = whole body."""
    rc, rec = run_main(["load", "--id", "cow-TOPIC", "--store", str(COW_STORE)])
    return (
        rc == 0 and rec["id"] == "cow-TOPIC"
        and rec["n_turns"] == 1
        and rec["turns"][0]["role"] == "user"
        and "plain topic body" in rec["turns"][0]["text"]
        and rec["aliases"]["opencode_id"] == "ses_cow_003"
    )


def t_load_grok_sha():
    rc, rec = run_main(["load", "--id", GROK_ID, "--store", str(GROK_STORE)])
    want = sha_file(GROK_HIST)
    roles = [t["role"] for t in rec.get("turns") or []]
    return (
        rc == 0 and rec["kind"] == "OK"
        and rec["id"] == GROK_ID
        and rec["family"] == "grok_tui"
        and rec["gate"]["schema"] == SCHEMA
        and rec["gate"]["source_sha"] == want
        and rec["sources"][0]["sha256"] == want
        and rec["n_turns"] == len(rec["turns"]) == 3
        and roles == ["user", "assistant", "tool_result"]
        and rec["stream"] == "cm"
        and rec["legal"] is False
        and "hello from grok fixture" in rec["turns"][0]["text"]
        and rec["hmac"] is False
    )


def t_load_grok_legal_omitted():
    rc, rec = run_main(["load", "--id", GROK_LEGAL_ID, "--store", str(GROK_STORE)])
    blob = json.dumps(rec)
    return (
        rc == 2 and rec["kind"] == "LEGAL_OMITTED"
        and rec["legal_omitted"] is True
        and "legal body must not" not in blob
        and "turns" not in rec
    )


def t_cli_refuses_guessed_root():
    rc, rec = run_main(["scan", "--family", "cowork"])
    return (
        rc == 2 and rec["kind"] == "GUESSED_ROOT"
        and rec["verb"] == "scan"
        and rec["schema"] == "cosmos-session-tools-result/1"
    )


def t_load_guessed_root():
    rc, rec = run_main(["load", "--id", "cow-abc"])
    return rc == 2 and rec["kind"] == "GUESSED_ROOT"


def t_empty_dir_no_store_not_n0():
    td = Path(tempfile.mkdtemp(prefix="cow_sessions_"))
    rc, rec = run_main(["scan", "--family", "cowork", "--store", str(td)])
    fam = rec["families"]["cowork"]
    return (
        rec["kind"] == "NO_STORE"
        and fam.get("n") is None
        and fam.get("n") != 0
        and rec["gate"].get("n") is None
    )


def t_load_not_found():
    rc, rec = run_main(["load", "--id", "cow-nope", "--store", str(COW_STORE)])
    return rec["kind"] == "NOT_FOUND" and rc == 2


def t_load_out_jsonl_decl_no_hmac():
    td = Path(tempfile.mkdtemp(prefix="st_out_"))
    rc, rec = run_main([
        "load", "--id", "cow-abc", "--store", str(COW_STORE), "--out", str(td),
    ])
    jsonl = td / "cow-abc.ctr.jsonl"
    declp = td / "cow-abc.ctr.decl.json"
    if not jsonl.is_file() or not declp.is_file():
        return False
    meta = json.loads(declp.read_text(encoding="utf-8"))
    data = read_verified(jsonl, expect_len=meta["len"], expect_sha=meta["sha"])
    text = data.decode("utf-8")
    lines = [ln for ln in text.split("\n") if ln]
    head = json.loads(lines[0])
    turns = [json.loads(ln) for ln in lines[1:]]
    return (
        rc == 0 and rec["kind"] == "OK"
        and head["schema"] == SCHEMA
        and head["kind"] == "COSMOS_TRANSCRIPT"
        and head["n_turns"] == len(turns) == 2
        and "mac" not in meta and "hmac" not in meta
        and meta["sha"] == rec["gate"]["sha"]
        and meta["n_turns"] == 2
        and rec["hmac"] is False
        and rec["out"]["sha"] == meta["sha"]
    )


def t_truncated_kind():
    td = Path(tempfile.mkdtemp(prefix="st_trunc_"))
    sess = td / "sess" / "ccccccc1-2222-3333-4444-555555555555"
    sess.mkdir(parents=True)
    (sess / "summary.json").write_text(json.dumps({
        "info": {"id": sess.name, "cwd": "C:\\Users\\Papa\\.grok\\worktrees\\ai-cosmos\\x"},
        "generated_title": "trunc",
        "current_model_id": "grok-4.6",
    }), encoding="utf-8")
    # two complete lines + a truncated last line (no closing brace, no newline)
    good = json.dumps({"type": "user", "content": "one"}) + "\n"
    good += json.dumps({"type": "assistant", "content": "two"}) + "\n"
    (sess / "chat_history.jsonl").write_bytes(
        good.encode("utf-8") + b'{"type":"user","content":"par'
    )
    rc, rec = run_main(["load", "--id", f"grok-{sess.name}", "--store", str(td)])
    texts = " ".join((t.get("text") or "") for t in rec.get("turns") or [])
    return (
        rec["kind"] == "TRUNCATED"
        and rec["gate"]["n_turns"] == 2
        and rec["n_turns"] == 2
        and "par" not in texts
    )


def t_unmeasured_family():
    rc, rec = run_main([
        "scan", "--family", "claude_desktop", "--store", str(COW_STORE),
    ])
    fam = rec["families"]["claude_desktop"]
    return (
        rec["kind"] == "UNMEASURED"
        and fam["n"] is None
        and fam["status"] == "UNMEASURED"
    )


def t_ids_stable_with_open_sessions():
    rc, rec = run_main(["scan", "--family", "cowork", "--store", str(COW_STORE)])
    ids = rec["families"]["cowork"]["sample_ids"]
    return ids[:3] == ["cow-abc", "cow-law", "cow-TOPIC"]


def main() -> int:
    for label, fn in (
        ("scan cowork fixture n=3 n_legal=1 (not recents 200)",
         t_scan_cowork_fixture_n_legal),
        ("scan cowork gate is catalog n not n_shown=200",
         t_scan_not_recents_200),
        ("scan grok n=2; missing chat_history not counted",
         t_scan_grok_counts_both_files_only),
        ("load cow-abc schema + n_turns + source sha + Open Sessions id",
         t_load_cow_abc),
        ("load cow-law LEGAL_OMITTED no body",
         t_load_cow_legal_omitted),
        ("load cow-TOPIC honors file (catalog turns=0)",
         t_load_cow_topic_honors_file),
        ("load grok fixture sha + roles + stream=cm",
         t_load_grok_sha),
        ("load grok legal LEGAL_OMITTED no body",
         t_load_grok_legal_omitted),
        ("CLI scan without --store/--root → GUESSED_ROOT",
         t_cli_refuses_guessed_root),
        ("CLI load without --store/--root → GUESSED_ROOT",
         t_load_guessed_root),
        ("empty cow_sessions dir → NO_STORE not n=0",
         t_empty_dir_no_store_not_n0),
        ("load unknown id → NOT_FOUND",
         t_load_not_found),
        ("load --out writes jsonl+decl; sidecar sha verifies; no HMAC",
         t_load_out_jsonl_decl_no_hmac),
        ("truncated grok jsonl → TRUNCATED with complete n_turns",
         t_truncated_kind),
        ("scan claude_desktop → UNMEASURED n=null",
         t_unmeasured_family),
        ("cowork ids cow-<session_id> catalog order",
         t_ids_stable_with_open_sessions),
    ):
        check(label, fn)
    n = sum(1 for _, ok, _ in RESULTS if ok)
    for label, ok, err in RESULTS:
        print(("PASS" if ok else "FAIL") + "  " + label + (f"  :: {err}" if err else ""))
    print(f"{n}/{len(RESULTS)} passed")
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
