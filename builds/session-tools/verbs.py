#!/usr/bin/env python3
"""Slice-2/3/4 verbs: convert, diff, check, anonymize, crash-recover, migrate, rebind."""
from __future__ import annotations

import json
import shutil
import sqlite3
import time
from pathlib import Path

from refusals import SessionToolsRefusal
from schema import (
    encode_jsonl,
    parse_jsonl,
    sha256_bytes,
    sha256_path,
    spans_ok,
    write_canonical,
)


def _stage_root(out_dir: Path | None, fallback: Path) -> Path:
    """Aside copies live under the out dir's parent, the stage folder passed in."""
    if out_dir is not None:
        return Path(out_dir).parent
    return Path(fallback).parent


def _stage_existing(path: Path, force: bool, stage_root: Path) -> None:
    if not path.exists():
        return
    if not force:
        raise SessionToolsRefusal("OUT_EXISTS", str(path))
    dest = Path(stage_root) / time.strftime("%Y%m%dT%H%M%S") / path.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)


def convert(load_fn, rec_id: str, store: Path, out_dir: Path, force: bool = False) -> dict:
    h, turns = load_fn(store, rec_id)
    ok, span_sum, src_len = spans_ok(h, turns)
    if not ok:
        raise SessionToolsRefusal(
            "FIDELITY_MISMATCH",
            f"span_sum={span_sum} source.len={src_len}")
    payload = encode_jsonl(h, turns)
    jsonl = out_dir / f"{h['id']}.ctr.jsonl"
    _stage_existing(jsonl, force, _stage_root(out_dir, out_dir))
    written = write_canonical(out_dir, h["id"], payload)
    back = Path(written["jsonl"]).read_bytes()
    if back != payload:
        raise SessionToolsRefusal("FIDELITY_MISMATCH", "jsonl round-trip")
    return {
        "id": h["id"],
        "out_sha": written["sha"],
        "source_sha": (h.get("sources") or [{}])[0].get("sha256"),
        "n_turns": len(turns),
        "spans_ok": True,
        "span_sum": span_sum,
        "source_len": src_len,
        "written": written,
    }


def diff_payloads(left: bytes, right: bytes) -> dict:
    ls, rs = sha256_bytes(left), sha256_bytes(right)
    lh, lt = parse_jsonl(left)
    rh, rt = parse_jsonl(right)
    delta = len(rt) - len(lt)
    return {
        "left_sha": ls,
        "right_sha": rs,
        "n_turns_delta": delta,
        "ids_only_left": [lh.get("id")] if lh.get("id") != rh.get("id") else [],
        "ids_only_right": [rh.get("id")] if lh.get("id") != rh.get("id") else [],
        "changed": [] if ls == rs else [{"id": lh.get("id"), "field": "payload"}],
    }


def check_catalog(store: Path) -> dict:
    cat = store / "COW_SESSION_CATALOG.json"
    if store.is_file():
        cat = store
    if not cat.is_file():
        raise SessionToolsRefusal("NO_STORE", str(store))
    rows = json.loads(cat.read_text(encoding="utf-8"))
    missing = []
    trans = cat.parent / "ordered_transcripts"
    for r in rows:
        fn = r.get("filename")
        if fn and not (trans / fn).is_file() and not (cat.parent / fn).is_file():
            missing.append(fn)
    if missing:
        raise SessionToolsRefusal("MISSING_PART", ",".join(missing))
    return {"kind": "VERIFIED", "n": len(rows), "path": str(cat)}


def check_sqlite(path: Path) -> dict:
    if not path.is_file():
        raise SessionToolsRefusal("NO_STORE", str(path))
    uri = path.resolve().as_uri() + "?mode=ro"
    try:
        con = sqlite3.connect(uri, uri=True)
        integ = con.execute("PRAGMA integrity_check").fetchone()[0]
        fk = con.execute("PRAGMA foreign_key_check").fetchall()
        n = None
        names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "session" in names:
            n = con.execute("SELECT count(*) FROM session").fetchone()[0]
        con.close()
    except sqlite3.DatabaseError as e:
        raise SessionToolsRefusal("SQLITE_CORRUPT", str(e)) from e
    if integ != "ok" or fk:
        raise SessionToolsRefusal("SQLITE_CORRUPT", f"integrity={integ} fk={len(fk)}")
    return {"kind": "VERIFIED", "integrity_check": integ, "foreign_key_check": [], "n_session": n}


def resolve_seed_root(root: Path) -> Path:
    """The root the caller handed in. No install record, no other tree."""
    return Path(root)


def _require_seed_root(root: Path) -> None:
    """NO_ROOT / NO_MAC before Kernel. A stat is not a read of the key or the MAC."""
    root = Path(root)
    sentinel = root / ".cosmos-root.json"
    if not root.is_dir() or not sentinel.is_file():
        raise SessionToolsRefusal("NO_ROOT", f"no COSMOS sentinel at {sentinel}")
    keyfile = root / "config" / "install_key.bin"
    if not keyfile.is_file():
        raise SessionToolsRefusal("NO_MAC", f"no install key at {keyfile}")


def check_seed(root: Path) -> dict:
    root = resolve_seed_root(root)
    _require_seed_root(root)
    import hmac

    from cosmos_kernel import Kernel
    from cosmos_paths import CosmosPaths
    from cosmos_session import SessionError
    from cosmos_validate import read_verified

    paths = CosmosPaths(root)
    seed = paths.role("state", "SEED.json")
    declp = paths.role("state", "SEED.decl.json")
    if not seed.is_file():
        raise SessionToolsRefusal("NO_SEED", str(seed))
    try:
        k = Kernel(root, worker="session-tools-check", read_only=True)
        decl = json.loads(declp.read_text(encoding="utf-8"))
        raw = read_verified(seed, expect_len=int(decl["len"]), expect_sha=str(decl["sha"]))
        body = json.loads(raw.decode("utf-8"))
        mac = str(decl.get("mac") or "")
        want = k.sessions._seed_mac(body.get("tree_id", ""), raw)
        if not mac or not hmac.compare_digest(mac, want):
            raise SessionToolsRefusal("BAD_SEED", "mac mismatch")
        live = str(paths.sentinel.tree_id)
        if str(body.get("tree_id") or "") != live:
            raise SessionToolsRefusal("IDENTITY_MISMATCH", f"{body.get('tree_id')} != {live}")
        return {"kind": "VERIFIED", "mac_ok": True, "tree_id": live, "sha": decl["sha"]}
    except SessionError as e:
        kind = e.kind if getattr(e, "kind", "") in ("BAD_SEED", "NO_SEED", "IDENTITY_MISMATCH") else "BAD_SEED"
        raise SessionToolsRefusal(kind, str(e)) from e


def check_sit(path: Path, chair: str) -> dict:
    p = path
    if not p.is_file():
        raise SessionToolsRefusal("NO_STORE", str(p))
    text = p.read_text(encoding="utf-8")
    if chair == "ccr":
        if 'schema       = "bucm/1"' not in text and 'schema = "bucm/1"' not in text and "bucm/1" not in text:
            raise SessionToolsRefusal("SIT_MIXED", "ccr sit is not bucm/1")
        return {"kind": "VERIFIED", "sit": "ccr", "schema": "bucm/1"}
    if chair == "orc":
        if "burestart/3" not in text:
            raise SessionToolsRefusal("SIT_MIXED", "orc sit is not burestart/3")
        if "bucm/1" in text and "burestart" not in text.split("schema", 1)[-1][:80]:
            raise SessionToolsRefusal("SIT_MIXED", "orc sit looks like BUCm")
        return {"kind": "VERIFIED", "sit": "orc", "schema": "burestart/3"}
    raise SessionToolsRefusal("UNMEASURED", chair)


def anonymize(load_fn, rec_id: str, store: Path, out_dir: Path) -> dict:
    from cosmos_askmine import redact
    h, turns = load_fn(store, rec_id)
    n = 0
    new_turns = []
    for t in turns:
        text, k = redact(t.get("text") or "")
        nt = dict(t)
        nt["text"] = text
        nt["redactions"] = k
        n += k
        new_turns.append(nt)
    src_path = Path((h.get("sources") or [{}])[0].get("path") or "")
    src_sha = (h.get("sources") or [{}])[0].get("sha256")
    if src_path.is_file():
        _, now = sha256_path(src_path)
        if now != src_sha:
            raise SessionToolsRefusal("FIDELITY_MISMATCH", "original mutated")
    payload = encode_jsonl(h, new_turns)
    written = write_canonical(out_dir, h["id"] + ".anon", payload)
    return {
        "n_redactions": n,
        "source_sha": src_sha,
        "out_sha": written["sha"],
        "written": written,
        "original_untouched": True,
    }


def crash_recover(target: Path, bak: Path | None, stage_root: Path) -> dict:
    """Copy bak to a new file. The target bytes stay where they are."""
    if bak is None or not bak.is_file():
        raise SessionToolsRefusal("NO_BAK", str(target))
    before = target.read_bytes() if target.is_file() else b""
    aside = Path(stage_root) / time.strftime("%Y%m%dT%H%M%S")
    aside.mkdir(parents=True, exist_ok=True)
    staged = aside / target.name
    if target.is_file():
        shutil.copy2(target, staged)
    staged_sha = sha256_bytes(staged.read_bytes()) if staged.is_file() else sha256_bytes(b"")
    bak_sha = sha256_bytes(bak.read_bytes())
    recovered = aside / f"{target.name}.restored"
    shutil.copy2(bak, recovered)
    restored_sha = sha256_bytes(recovered.read_bytes())
    if restored_sha != bak_sha:
        raise SessionToolsRefusal("RESTORE_FAILED", str(recovered))
    after = target.read_bytes() if target.is_file() else b""
    if after != before:
        raise SessionToolsRefusal("RESTORE_FAILED", str(target))
    return {
        "kind": "OK",
        "bak_path": str(bak),
        "bak_sha": bak_sha,
        "staged_path": str(staged),
        "staged_sha": staged_sha,
        "restored_sha": restored_sha,
        "restored_path": str(recovered),
        "before_len": len(before),
    }


def _catalog_rows(store: Path) -> list:
    cat = store / "COW_SESSION_CATALOG.json"
    if store.is_file() and store.name.endswith(".json"):
        cat = store
    if not cat.is_file():
        return []
    rows = json.loads(cat.read_text(encoding="utf-8"))
    return rows if isinstance(rows, list) else []


def _in_666(rec_id: str, head_rec: dict, store: Path) -> bool:
    if rec_id.startswith("cow-") or str(head_rec.get("family") or "") == "cowork":
        return True
    vid = str(head_rec.get("vendor_session_id") or "")
    alias = head_rec.get("aliases") or {}
    ow = str(alias.get("opencode_id") or "")
    if ow.startswith("ses_cow_") or rec_id.startswith("ses_cow_"):
        return True
    for r in _catalog_rows(store):
        sid = str(r.get("session_id") or "")
        if sid and (sid == vid or rec_id == f"cow-{sid}" or vid == sid):
            return True
        seq = str(r.get("seq") or "")
        alias_seq = str(alias.get("seq") or "")
        if seq and seq == alias_seq and sid == vid:
            return True
    return False


def _ses_id(vendor_session_id: str) -> str:
    digest = sha256_bytes(str(vendor_session_id).encode("utf-8"))[:16]
    return f"ses_grok_{digest}"


def _now_ms() -> int:
    return int(time.time() * 1000)


def migrate(load_fn, rec_id: str, store: Path, workspace_id: str | None,
            directory: Path | None, out_dir: Path | None = None,
            dry_run: bool = False) -> dict:
    """Grok TUI canonical -> NEW OpenWork ses_*. 666 migrate is CLOSED."""
    if rec_id.startswith("cow-"):
        raise SessionToolsRefusal("DO_NOT_REINGEST", rec_id)
    if not rec_id.startswith("grok-"):
        raise SessionToolsRefusal("DO_NOT_REINGEST", rec_id)
    if not workspace_id:
        raise SessionToolsRefusal("WORKSPACE_UNKNOWN", "--workspace-id required")
    if directory is None:
        raise SessionToolsRefusal("WORKSPACE_UNKNOWN", "--directory required")
    ws = Path(directory)
    if not ws.is_dir():
        raise SessionToolsRefusal("WORKSPACE_UNKNOWN", str(ws))
    db = ws / "opencode.db"
    h, turns = load_fn(store, rec_id)
    if h.get("legal"):
        raise SessionToolsRefusal("LEGAL_OMITTED", rec_id)
    if _in_666(rec_id, h, store):
        raise SessionToolsRefusal("DO_NOT_REINGEST", rec_id)
    ses_id = _ses_id(str(h.get("vendor_session_id") or rec_id))
    plan = {
        "ses_id": ses_id,
        "workspace_id": workspace_id,
        "n_turns": len(turns),
        "db": str(db),
        "insert_session": 1,
        "insert_messages": len(turns),
        "insert_parts": len(turns),
    }
    if dry_run:
        return plan | {"kind": "DRY_RUN", "dry_run": True}
    if not db.is_file():
        raise SessionToolsRefusal("NO_BAK", f"no opencode.db in {ws}")
    stage = _stage_root(out_dir, directory) / "migrate" / time.strftime("%Y%m%dT%H%M%S")
    stage.mkdir(parents=True, exist_ok=True)
    bak = stage / "opencode.db"
    try:
        shutil.copy2(db, bak)
    except OSError as e:
        raise SessionToolsRefusal("NO_BAK", str(e)) from e
    rt = ws / "runtime.sqlite"
    if rt.is_file():
        shutil.copy2(rt, stage / "runtime.sqlite")
    now = _now_ms()
    slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in rec_id)[:48]
    title = str(h.get("title") or rec_id)
    con = sqlite3.connect(str(db))
    try:
        names = {r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        need = {"session", "message", "part"}
        if not need.issubset(names):
            raise SessionToolsRefusal("SCHEMA_UNKNOWN", f"tables={sorted(names)}")
        con.execute(
            "INSERT INTO session (id, project_id, workspace_id, slug, directory, "
            "title, version, cost, tokens_input, tokens_output, tokens_reasoning, "
            "tokens_cache_read, tokens_cache_write, time_created, time_updated) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (ses_id, "global", workspace_id, slug, str(ws), title,
             "session-tools/1", 0, 0, 0, 0, 0, 0, now, now),
        )
        for t in turns:
            seq = int(t.get("seq") or 0)
            mid = f"msg_grok_{seq:04d}_{ses_id[-8:]}"
            pid = f"prt_grok_{seq:04d}_{ses_id[-8:]}"
            ts = t.get("t")
            try:
                tms = int(float(ts) * 1000) if ts is not None else now
            except (TypeError, ValueError):
                tms = now
            role = str(t.get("role") or "user")
            text = t.get("text") or ""
            msg_data = json.dumps({
                "role": role,
                "time": {"created": tms},
                "agent": "session-tools",
                "model": {"providerID": "cosmos", "modelID": "migrate"},
            }, separators=(",", ":"))
            part_data = json.dumps({"type": "text", "text": text},
                                   separators=(",", ":"))
            con.execute(
                "INSERT INTO message (id, session_id, time_created, time_updated, data) "
                "VALUES (?,?,?,?,?)",
                (mid, ses_id, tms, tms, msg_data),
            )
            con.execute(
                "INSERT INTO part (id, message_id, session_id, time_created, "
                "time_updated, data) VALUES (?,?,?,?,?,?)",
                (pid, mid, ses_id, tms, tms, part_data),
            )
        con.commit()
    except SessionToolsRefusal:
        con.rollback()
        shutil.copy2(bak, db)
        con.close()
        raise
    except sqlite3.Error as e:
        con.rollback()
        shutil.copy2(bak, db)
        con.close()
        raise SessionToolsRefusal("RESTORE_FAILED", str(e)) from e
    con.close()
    con = sqlite3.connect(str(db))
    n = con.execute("SELECT count(*) FROM session WHERE id=?", (ses_id,)).fetchone()[0]
    n_m = con.execute(
        "SELECT count(*) FROM message WHERE session_id=?", (ses_id,)).fetchone()[0]
    n_p = con.execute(
        "SELECT count(*) FROM part WHERE session_id=?", (ses_id,)).fetchone()[0]
    con.close()
    if n != 1 or n_m != len(turns) or n_p != len(turns):
        shutil.copy2(bak, db)
        raise SessionToolsRefusal(
            "VERIFY_MISMATCH",
            f"session={n} messages={n_m} parts={n_p} turns={len(turns)}")
    gate = {
        "ses_id": ses_id,
        "workspace_id": workspace_id,
        "n_turns_written": len(turns),
        "bak_path": str(bak),
        "session_count": n,
        "message_count": n_m,
        "part_count": n_p,
    }
    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        proof = out_dir / f"migrate_{rec_id}.json"
        proof.write_text(json.dumps({
            "schema": "cosmos-session-tools-result/1",
            "verb": "migrate",
            "kind": "OK",
            "gate": gate,
        }, indent=2) + "\n", encoding="utf-8")
        gate["proof"] = str(proof)
    return gate


def rebind(ses_id: str, directory: Path, workspace_id: str, *,
           dry_run: bool = False, out_dir: Path | None = None) -> dict:
    """Point an existing ses_* at a new workspace id/path. Never re-ingest 666."""
    sid = str(ses_id or "").strip()
    if not sid:
        raise SessionToolsRefusal("BAD_INPUT", "ses_id required")
    if sid.startswith(("ses_cow_", "cow-", "ow-ses_cow_")):
        raise SessionToolsRefusal("DO_NOT_REINGEST", sid)
    sid = sid.removeprefix("ow-")
    if not workspace_id:
        raise SessionToolsRefusal("WORKSPACE_UNKNOWN", "--workspace-id required")
    if directory is None:
        raise SessionToolsRefusal("WORKSPACE_UNKNOWN", "--directory required")
    ws = Path(directory)
    if not ws.is_dir():
        raise SessionToolsRefusal("WORKSPACE_UNKNOWN", str(ws))
    db = ws / "opencode.db"
    plan = {
        "ses_id": sid,
        "workspace_id": workspace_id,
        "directory": str(ws),
        "db": str(db),
    }
    if dry_run:
        return plan | {"kind": "DRY_RUN", "dry_run": True}
    if not db.is_file():
        raise SessionToolsRefusal("NO_BAK", f"no opencode.db in {ws}")
    stage = _stage_root(out_dir, directory) / "rebind" / time.strftime("%Y%m%dT%H%M%S")
    stage.mkdir(parents=True, exist_ok=True)
    bak = stage / "opencode.db"
    try:
        shutil.copy2(db, bak)
    except OSError as e:
        raise SessionToolsRefusal("NO_BAK", str(e)) from e
    now = _now_ms()
    con = sqlite3.connect(str(db))
    try:
        row = con.execute(
            "SELECT id, workspace_id, directory FROM session WHERE id=?",
            (sid,)).fetchone()
        if row is None:
            raise SessionToolsRefusal("NOT_FOUND", sid)
        prev_ws, prev_dir = row[1], row[2]
        con.execute(
            "UPDATE session SET workspace_id=?, directory=?, time_updated=? WHERE id=?",
            (workspace_id, str(ws), now, sid),
        )
        con.commit()
    except SessionToolsRefusal:
        con.close()
        raise
    except sqlite3.Error as e:
        con.rollback()
        con.close()
        shutil.copy2(bak, db)
        raise SessionToolsRefusal("RESTORE_FAILED", str(e)) from e
    con.close()
    con = sqlite3.connect(str(db))
    got = con.execute(
        "SELECT workspace_id, directory FROM session WHERE id=?", (sid,)).fetchone()
    con.close()
    if not got or got[0] != workspace_id:
        shutil.copy2(bak, db)
        raise SessionToolsRefusal("VERIFY_MISMATCH", sid)
    gate = {
        "ses_id": sid,
        "workspace_id": workspace_id,
        "prev_workspace_id": prev_ws,
        "prev_directory": prev_dir,
        "directory": str(ws),
        "bak_path": str(bak),
    }
    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        proof = out_dir / f"rebind_{sid}.json"
        proof.write_text(json.dumps({
            "schema": "cosmos-session-tools-result/1",
            "verb": "rebind",
            "kind": "OK",
            "gate": gate,
        }, indent=2) + "\n", encoding="utf-8")
        gate["proof"] = str(proof)
    return gate
