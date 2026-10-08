"""scan + load for cowork and grok_tui. Legal ids refuse. No live pack."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

import session_tools
from adapters import cowork, grok_tui, openwork
from clone import refuse_duplicate
from refusals import SessionToolsRefusal


def test_scan_and_load_cowork(cow_store: Path) -> None:
    row = cowork.scan(cow_store)
    assert row["family"] == "cowork"
    assert row["status"] == "OK"
    assert row["n"] == 2
    assert row["n_legal"] == 1
    assert "cow-s1" in row["sample_ids"]

    head, turns = cowork.load(cow_store, "cow-s1")
    assert head["schema"] == "cosmos-transcript/1"
    assert head["id"] == "cow-s1"
    assert head["legal"] is False
    assert len(turns) == 1
    assert "turn one" in (turns[0]["text"] or "")
    assert "turn three" in (turns[0]["text"] or "")
    src = Path(head["sources"][0]["path"])
    assert src.is_file()
    assert head["sources"][0]["len"] == src.stat().st_size


def test_scan_and_load_grok(grok_store: tuple[Path, str]) -> None:
    store, vid = grok_store
    row = grok_tui.scan(store)
    assert row["family"] == "grok_tui"
    assert row["status"] == "OK"
    assert row["n"] == 1
    assert row["sample_ids"] == [f"grok-{vid}"]

    head, turns = grok_tui.load(store, f"grok-{vid}")
    assert head["schema"] == "cosmos-transcript/1"
    assert head["id"] == f"grok-{vid}"
    assert [t["role"] for t in turns] == ["user", "assistant", "user"]
    assert [t["text"] for t in turns] == ["hello fixture", "hi back", "third turn"]
    assert head["sources"][0]["fidelity"] == "span"


def test_legal_id_refuses(cow_store: Path) -> None:
    before = (cow_store / "ordered_transcripts" / "leg.md").read_bytes()
    with pytest.raises(SessionToolsRefusal) as caught:
        cowork.load(cow_store, "cow-legal-case-1")
    assert caught.value.kind == "LEGAL_OMITTED"
    assert (cow_store / "ordered_transcripts" / "leg.md").read_bytes() == before


def test_cli_scan_and_legal_load(cow_store: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = session_tools.main(["scan", "--family", "cowork", "--store", str(cow_store)])
    assert rc == 0
    rec = json.loads(capsys.readouterr().out)
    assert rec["verb"] == "scan"
    assert rec["kind"] == "OK"
    assert rec["families"][0]["n"] == 2
    assert rec["legal_omitted"] == 1

    rc = session_tools.main([
        "load", "--id", "cow-legal-case-1", "--store", str(cow_store),
    ])
    assert rc == 2
    refused = json.loads(capsys.readouterr().out)
    assert refused["kind"] == "LEGAL_OMITTED"


def test_cowork_missing_catalog_refuses(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(SessionToolsRefusal) as caught:
        cowork.scan(empty)
    assert caught.value.kind == "NO_STORE"


def test_openwork_not_a_workspace_refuses(tmp_path: Path) -> None:
    store = tmp_path / "not-a-workspace"
    store.mkdir()
    (store / "readme.txt").write_text("no engine here\n", encoding="utf-8")
    with pytest.raises(SessionToolsRefusal) as caught:
        openwork.load(store, "ow-ses_not_real")
    assert caught.value.kind in {"NO_STORE", "UNMEASURED"}
    assert "ws_" not in str(caught.value)
    with pytest.raises(SessionToolsRefusal) as scanned:
        openwork.scan(store)
    assert scanned.value.kind in {"NO_STORE", "UNMEASURED"}


def test_openwork_does_not_invent_workspace_id(tmp_path: Path) -> None:
    store = tmp_path / "plain-db"
    store.mkdir()
    db = store / "opencode.db"
    con = sqlite3.connect(db)
    con.execute(
        "CREATE TABLE session (id TEXT, title TEXT, directory TEXT, workspace_id TEXT)")
    con.execute(
        "CREATE TABLE message (id TEXT, session_id TEXT, time_created INTEGER, data TEXT)")
    con.execute(
        "CREATE TABLE part ("
        "id TEXT, message_id TEXT, session_id TEXT, time_created INTEGER, data TEXT)")
    con.execute(
        "INSERT INTO session VALUES ('ses_plain_1', 't', ?, NULL)",
        (str(store),),
    )
    con.execute(
        "INSERT INTO message VALUES ('m1', 'ses_plain_1', 1, ?)",
        (json.dumps({"role": "user"}),),
    )
    con.execute(
        "INSERT INTO part VALUES ('p1', 'm1', 'ses_plain_1', 1, ?)",
        (json.dumps({"type": "text", "text": "hi"}),),
    )
    con.commit()
    con.close()

    head, turns = openwork.load(store, "ow-ses_plain_1")
    assert head["vendor_session_id"] == "ses_plain_1"
    assert head["aliases"].get("workspace_id") is None
    assert len(turns) == 1
    blob = json.dumps(head)
    assert "ws_" not in blob


def test_openwork_cow_prefix_refuses(tmp_path: Path) -> None:
    with pytest.raises(SessionToolsRefusal) as caught:
        openwork.load(tmp_path, "ow-ses_cow_001")
    assert caught.value.kind == "DO_NOT_REINGEST"


def test_identical_tail_refuses() -> None:
    tail = "n" * 800
    with pytest.raises(SessionToolsRefusal) as caught:
        refuse_duplicate("alpha-" + tail, "beta-" + tail)
    assert caught.value.kind == "CLONE"


def test_different_tail_is_not_a_clone() -> None:
    refuse_duplicate("a" * 800, "b" * 800)
