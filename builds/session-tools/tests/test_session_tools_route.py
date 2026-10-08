"""convert, diff, check, anonymize, crash-recover, migrate, rebind."""
from __future__ import annotations

import io
import json
import os
import sqlite3
import sys
from pathlib import Path

import pytest

import session_tools
import verbs
from adapters import cowork, grok_tui
from refusals import SessionToolsRefusal
from schema import encode_jsonl, head, parse_jsonl, sha256_bytes, turn


def _ow_db(path: Path) -> None:
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE session ("
        "id TEXT PRIMARY KEY, project_id TEXT, workspace_id TEXT, slug TEXT, "
        "directory TEXT, title TEXT, version TEXT, cost REAL, "
        "tokens_input INTEGER, tokens_output INTEGER, tokens_reasoning INTEGER, "
        "tokens_cache_read INTEGER, tokens_cache_write INTEGER, "
        "time_created INTEGER, time_updated INTEGER)")
    con.execute(
        "CREATE TABLE message ("
        "id TEXT PRIMARY KEY, session_id TEXT, time_created INTEGER, "
        "time_updated INTEGER, data TEXT)")
    con.execute(
        "CREATE TABLE part ("
        "id TEXT PRIMARY KEY, message_id TEXT, session_id TEXT, "
        "time_created INTEGER, time_updated INTEGER, data TEXT)")
    con.commit()
    con.close()


def test_convert_round_trip_grok(grok_store: tuple[Path, str], tmp_path: Path) -> None:
    store, vid = grok_store
    rec_id = f"grok-{vid}"
    loaded_h, loaded_t = grok_tui.load(store, rec_id)
    expect = encode_jsonl(loaded_h, loaded_t)
    out = tmp_path / "out"
    gate = verbs.convert(grok_tui.load, rec_id, store, out, force=False)
    blob = Path(gate["written"]["jsonl"]).read_bytes()
    assert blob == expect
    assert encode_jsonl(*parse_jsonl(blob)) == blob
    assert sha256_bytes(blob) == gate["out_sha"]
    assert gate["spans_ok"] is True
    assert gate["n_turns"] == 3


def test_convert_round_trip_cowork(cow_store: Path, tmp_path: Path) -> None:
    loaded_h, loaded_t = cowork.load(cow_store, "cow-s1")
    expect = encode_jsonl(loaded_h, loaded_t)
    out = tmp_path / "out"
    gate = verbs.convert(cowork.load, "cow-s1", cow_store, out, force=False)
    blob = Path(gate["written"]["jsonl"]).read_bytes()
    assert blob == expect
    assert encode_jsonl(*parse_jsonl(blob)) == blob
    assert gate["spans_ok"] is True


def test_convert_refuses_bad_span_sum(tmp_path: Path) -> None:
    def load_fn(_store: Path, _rec_id: str):
        rec = head(
            id="grok-badsum", family="grok_tui", vendor_session_id="badsum",
            sources=[{"len": 10, "sha256": "abc", "path": "", "fidelity": "span"}],
        )
        one = turn(
            seq=1, role="user", text="nope",
            src={"source_idx": 0, "off": 0, "len": 3},
        )
        return rec, [one]

    with pytest.raises(SessionToolsRefusal) as caught:
        verbs.convert(load_fn, "grok-badsum", tmp_path, tmp_path / "out", force=False)
    assert caught.value.kind == "FIDELITY_MISMATCH"


def test_convert_refuses_bad_span_bytes(tmp_path: Path) -> None:
    raw = b"abcdefghij"
    src = tmp_path / "source.bin"
    src.write_bytes(raw)

    def load_fn(_store: Path, _rec_id: str):
        rec = head(
            id="grok-badspan", family="grok_tui", vendor_session_id="badspan",
            sources=[{
                "path": str(src), "kind": "jsonl", "len": len(raw),
                "sha256": sha256_bytes(raw), "fidelity": "span",
            }],
        )
        one = turn(
            seq=1, role="user", text="x",
            src={"source_idx": 0, "off": 0, "len": len(raw), "sha256": "0" * 64},
        )
        return rec, [one]

    with pytest.raises(SessionToolsRefusal) as caught:
        verbs.convert(load_fn, "grok-badspan", tmp_path, tmp_path / "out", force=False)
    assert caught.value.kind == "FIDELITY_MISMATCH"


def test_convert_force_false_refuses_existing(
        grok_store: tuple[Path, str], tmp_path: Path) -> None:
    store, vid = grok_store
    out = tmp_path / "out"
    verbs.convert(grok_tui.load, f"grok-{vid}", store, out, force=False)
    with pytest.raises(SessionToolsRefusal) as caught:
        verbs.convert(grok_tui.load, f"grok-{vid}", store, out, force=False)
    assert caught.value.kind == "OUT_EXISTS"


def test_convert_force_stages_under_out_parent(
        grok_store: tuple[Path, str], tmp_path: Path) -> None:
    store, vid = grok_store
    rec_id = f"grok-{vid}"
    out = tmp_path / "out"
    verbs.convert(grok_tui.load, rec_id, store, out, force=False)
    jsonl = out / f"{rec_id}.ctr.jsonl"
    old = jsonl.read_bytes()
    hist = next(store.rglob("chat_history.jsonl"))
    hist.write_bytes(hist.read_bytes() + b'{"type":"user","text":"more"}\n')
    verbs.convert(grok_tui.load, rec_id, store, out, force=True)
    assert jsonl.read_bytes() != old
    asides = [
        p for p in out.parent.rglob(f"{rec_id}.ctr.jsonl")
        if p.resolve() != jsonl.resolve()
    ]
    assert asides
    assert old in [p.read_bytes() for p in asides]
    root = out.parent.resolve()
    for path in asides:
        assert root == path.resolve() or root in path.resolve().parents


def test_diff_sha_and_turn_delta() -> None:
    rec = head(id="grok-d", family="grok_tui", vendor_session_id="d")
    left = encode_jsonl(rec, [turn(seq=1, role="user", text="a", src={})])
    right = encode_jsonl(rec, [
        turn(seq=1, role="user", text="a", src={}),
        turn(seq=2, role="assistant", text="b", src={}),
    ])
    gate = verbs.diff_payloads(left, right)
    assert gate["left_sha"] == sha256_bytes(left)
    assert gate["right_sha"] == sha256_bytes(right)
    assert gate["n_turns_delta"] == 1
    assert gate["left_sha"] != gate["right_sha"]
    same = verbs.diff_payloads(left, left)
    assert same["n_turns_delta"] == 0
    assert same["left_sha"] == same["right_sha"]
    assert same["changed"] == []


def _under_live(path) -> bool:
    if isinstance(path, int):
        return False
    try:
        parts = [part.lower() for part in Path(path).parts]
    except (TypeError, ValueError):
        return False
    for index, part in enumerate(parts):
        if part == "cosmos" and index + 1 < len(parts) and parts[index + 1] == "live":
            return True
    return False


def test_check_seed_refuses_without_root_or_key(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    """check --what seed with no sentinel and no key. Refusal before any live open."""
    bare = tmp_path / "bare-root"
    bare.mkdir()
    monkeypatch.setattr(verbs, "resolve_seed_root", lambda _root: bare)
    blocked = {
        "cosmos_kernel", "cosmos_paths", "cosmos_session", "cosmos_validate",
    }
    real_import = __import__

    def guarded_import(name, *args, **kwargs):
        if name in blocked:
            raise AssertionError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", guarded_import)
    real_stat = os.stat

    def guarded_stat(path, *args, **kwargs):
        if _under_live(path):
            raise AssertionError(str(path))
        return real_stat(path, *args, **kwargs)

    monkeypatch.setattr(os, "stat", guarded_stat)
    real_open = io.open

    def guarded_open(file, *args, **kwargs):
        if _under_live(file) or str(file).lower().endswith("install_key.bin"):
            raise AssertionError(str(file))
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr(io, "open", guarded_open)

    with pytest.raises(SessionToolsRefusal) as caught:
        verbs.check_seed(tmp_path / "not-the-root")
    assert caught.value.kind == "NO_ROOT"
    assert "install_key.bin" not in str(caught.value)
    assert "cosmos_kernel" not in sys.modules

    rc = session_tools.main([
        "check", "--what", "seed", "--path", str(tmp_path / "not-the-root"),
    ])
    assert rc == 2
    rec = json.loads(capsys.readouterr().out)
    assert rec["verb"] == "check"
    assert rec["kind"] == "NO_ROOT"
    assert "install_key.bin" not in rec["gate"]["detail"]
    assert "cosmos_kernel" not in sys.modules


def test_check_missing_catalog_refuses(tmp_path: Path) -> None:
    empty = tmp_path / "no-catalog"
    empty.mkdir()
    with pytest.raises(SessionToolsRefusal) as caught:
        verbs.check_catalog(empty)
    assert caught.value.kind == "NO_STORE"


def test_check_good_catalog_verifies(cow_store: Path) -> None:
    gate = verbs.check_catalog(cow_store)
    assert gate["kind"] == "VERIFIED"
    assert gate["n"] == 2


def test_check_sqlite_and_sit(tmp_path: Path) -> None:
    db = tmp_path / "ok.sqlite"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE session (id TEXT)")
    con.execute("INSERT INTO session (id) VALUES ('s1')")
    con.commit()
    con.close()
    gate = verbs.check_sqlite(db)
    assert gate["kind"] == "VERIFIED"
    assert gate["integrity_check"] == "ok"
    assert gate["n_session"] == 1
    missing = tmp_path / "missing.sqlite"
    with pytest.raises(SessionToolsRefusal) as caught:
        verbs.check_sqlite(missing)
    assert caught.value.kind == "NO_STORE"

    sit = tmp_path / "sit.toml"
    sit.write_text('schema = "bucm/1"\n', encoding="utf-8")
    chair = verbs.check_sit(sit, "ccr")
    assert chair["kind"] == "VERIFIED"
    assert chair["schema"] == "bucm/1"


def test_anonymize_redacts_export_and_keeps_source(
        grok_with_key: tuple[Path, str, str], tmp_path: Path) -> None:
    store, vid, key = grok_with_key
    hist = next(store.rglob("chat_history.jsonl"))
    before = hist.read_bytes()
    assert key.encode("utf-8") in before
    out = tmp_path / "anon-out"
    gate = verbs.anonymize(grok_tui.load, f"grok-{vid}", store, out)
    assert hist.read_bytes() == before
    exported = Path(gate["written"]["jsonl"])
    blob = exported.read_bytes()
    assert exported.parent.resolve() == out.resolve()
    assert exported.resolve() != hist.resolve()
    assert key.encode("utf-8") not in blob
    assert b"[REDACTED:" in blob
    assert gate["n_redactions"] >= 1
    assert gate["original_untouched"] is True


def test_legal_anonymize_refuses(cow_store: Path, tmp_path: Path) -> None:
    src = cow_store / "ordered_transcripts" / "leg.md"
    before = src.read_bytes()
    with pytest.raises(SessionToolsRefusal) as caught:
        verbs.anonymize(cowork.load, "cow-legal-case-1", cow_store, tmp_path / "out")
    assert caught.value.kind == "LEGAL_OMITTED"
    assert src.read_bytes() == before


def test_crash_recover_yields_new_file(tmp_path: Path) -> None:
    target = tmp_path / "chat_history.jsonl"
    truncated = b'{"type":"user","text":"hel'
    full = b'{"type":"user","text":"hello"}\n'
    target.write_bytes(truncated)
    bak = tmp_path / "chat_history.jsonl.bak"
    bak.write_bytes(full)
    gate = verbs.crash_recover(target, bak, tmp_path / "stage")
    assert target.read_bytes() == truncated
    recovered = Path(gate["restored_path"])
    assert recovered.resolve() != target.resolve()
    assert recovered.read_bytes() == full
    assert gate["restored_sha"] == gate["bak_sha"]
    assert gate["staged_sha"] == sha256_bytes(truncated)
    assert tmp_path.resolve() in recovered.resolve().parents


def test_crash_recover_no_bak_leaves_target(tmp_path: Path) -> None:
    target = tmp_path / "chat_history.jsonl"
    target.write_bytes(b"abc")
    with pytest.raises(SessionToolsRefusal) as caught:
        verbs.crash_recover(target, tmp_path / "missing.bak", tmp_path / "stage")
    assert caught.value.kind == "NO_BAK"
    assert target.read_bytes() == b"abc"


def test_cli_crash_recover_keeps_target(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "live.jsonl"
    target.write_bytes(b'{"cut":')
    bak = tmp_path / "live.jsonl.bak"
    bak.write_bytes(b'{"type":"user","text":"whole"}\n')
    before = target.read_bytes()
    rc = session_tools.main([
        "crash-recover",
        "--target", str(target),
        "--bak", str(bak),
        "--stage", str(tmp_path / "stage"),
    ])
    assert rc == 0
    assert target.read_bytes() == before
    rec = json.loads(capsys.readouterr().out)
    recovered = Path(rec["gate"]["restored_path"])
    assert recovered.read_bytes() == bak.read_bytes()
    assert recovered.resolve() != target.resolve()


def test_migrate_cow_refuses(tmp_path: Path) -> None:
    with pytest.raises(SessionToolsRefusal) as caught:
        verbs.migrate(
            cowork.load, "cow-s1", tmp_path, "ws_fixture_only",
            tmp_path, None, dry_run=True)
    assert caught.value.kind == "DO_NOT_REINGEST"


def test_migrate_fixture_db(grok_store: tuple[Path, str], tmp_path: Path) -> None:
    store, vid = grok_store
    rec_id = f"grok-{vid}"
    ws = tmp_path / "ws"
    ws.mkdir()
    dry = verbs.migrate(
        grok_tui.load, rec_id, store, "ws_fixture_only", ws, None, dry_run=True)
    assert dry["dry_run"] is True
    assert dry["workspace_id"] == "ws_fixture_only"
    assert dry["n_turns"] == 3
    assert not (ws / "opencode.db").exists()

    db = ws / "opencode.db"
    _ow_db(db)
    out = tmp_path / "proof"
    gate = verbs.migrate(
        grok_tui.load, rec_id, store, "ws_fixture_only", ws, out, dry_run=False)
    assert gate["workspace_id"] == "ws_fixture_only"
    assert gate["n_turns_written"] == 3
    assert gate["message_count"] == 3
    assert gate["part_count"] == 3
    bak = Path(gate["bak_path"])
    assert bak.is_file()
    assert bak.resolve().is_relative_to(tmp_path.resolve())
    con = sqlite3.connect(db)
    row = con.execute("SELECT id, workspace_id FROM session").fetchone()
    con.close()
    assert row[1] == "ws_fixture_only"
    assert str(row[0]).startswith("ses_grok_")
    assert not str(row[0]).startswith("ses_cow_")


def test_rebind_cow_prefix_refuses(tmp_path: Path) -> None:
    with pytest.raises(SessionToolsRefusal) as caught:
        verbs.rebind("ses_cow_001", tmp_path, "ws_new_fixture")
    assert caught.value.kind == "DO_NOT_REINGEST"


def test_rebind_fixture_db(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    ws.mkdir()
    db = ws / "opencode.db"
    _ow_db(db)
    con = sqlite3.connect(db)
    con.execute(
        "INSERT INTO session (id, workspace_id, directory, time_created, time_updated) "
        "VALUES (?, ?, ?, ?, ?)",
        ("ses_grok_fixture01", "ws_old", str(ws), 1, 1),
    )
    con.commit()
    con.close()
    out = tmp_path / "proof"
    gate = verbs.rebind(
        "ses_grok_fixture01", ws, "ws_new_fixture", dry_run=False, out_dir=out)
    assert gate["workspace_id"] == "ws_new_fixture"
    assert gate["prev_workspace_id"] == "ws_old"
    assert Path(gate["bak_path"]).resolve().is_relative_to(tmp_path.resolve())
    con = sqlite3.connect(db)
    got = con.execute(
        "SELECT workspace_id FROM session WHERE id=?",
        ("ses_grok_fixture01",),
    ).fetchone()
    con.close()
    assert got[0] == "ws_new_fixture"
