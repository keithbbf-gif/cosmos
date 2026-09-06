#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Slice-2/3/4 verbs: convert, diff, check, anonymize, crash-recover."""
from __future__ import annotations

import json
import shutil
import sqlite3
import time
from pathlib import Path

from refusals import SessionToolsRefusal
from schema import encode_jsonl, parse_jsonl, sha256_bytes, sha256_path, spans_ok, write_canonical

REPO = Path(__file__).resolve().parent.parent.parent


def _stage_existing(path: Path, force: bool) -> None:
    if not path.exists():
        return
    if not force:
        raise SessionToolsRefusal("OUT_EXISTS", str(path))
    dest = REPO / "_delme" / "session-tools" / time.strftime("%Y%m%dT%H%M%S") / path.name
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
    _stage_existing(jsonl, force)
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


def check_seed(root: Path) -> dict:
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
    if bak is None or not bak.is_file():
        raise SessionToolsRefusal("NO_BAK", str(target))
    before = target.read_bytes() if target.is_file() else b""
    staged = stage_root / time.strftime("%Y%m%dT%H%M%S") / target.name
    staged.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file():
        shutil.copy2(target, staged)
    staged_sha = sha256_bytes(staged.read_bytes()) if staged.is_file() else sha256_bytes(b"")
    bak_sha = sha256_bytes(bak.read_bytes())
    shutil.copy2(bak, target)
    restored_sha = sha256_bytes(target.read_bytes())
    if restored_sha != bak_sha:
        # put back staged
        if staged.is_file():
            shutil.copy2(staged, target)
        raise SessionToolsRefusal("RESTORE_FAILED", str(target))
    return {
        "kind": "OK",
        "bak_path": str(bak),
        "bak_sha": bak_sha,
        "staged_path": str(staged),
        "staged_sha": staged_sha,
        "restored_sha": restored_sha,
        "before_len": len(before),
    }
