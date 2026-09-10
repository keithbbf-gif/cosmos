#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P11 fail-closed SEED write: silent truncation must not seal.

Pin: old write_declared returned the buffer hash after a raw write.
Fix: write_declared fsyncs and re-reads; mismatch is VERIFY_MISMATCH.
close_session maps that to SessionError VERIFY_MISMATCH and does not
claim SESSION_SEED_WRITTEN over a lie.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_session import SessionError  # noqa: E402
from cosmos_validate import ValidateError, write_declared  # noqa: E402


def write_declared_old(path: Path, content: bytes) -> dict:
    with open(path, "wb") as fh:
        fh.write(content)
    return {"path": str(path), "len": len(content),
            "sha": hashlib.sha256(content).hexdigest()}


def test_old_write_declared_seals_truncated_disk():
    td = Path(tempfile.mkdtemp(prefix="p11_old_"))
    path = td / "SEED.json"
    payload = b'{"kind":"COSMOS_SEED"}'
    decl = write_declared_old(path, payload)
    path.write_bytes(payload[:8])
    assert decl["len"] == len(payload)
    assert hashlib.sha256(path.read_bytes()).hexdigest() != decl["sha"]


def test_new_write_declared_round_trips():
    td = Path(tempfile.mkdtemp(prefix="p11_new_"))
    path = td / "SEED.json"
    payload = b'{"kind":"COSMOS_SEED","facts":{}}'
    decl = write_declared(path, payload)
    assert decl["len"] == len(payload)
    assert decl["sha"] == hashlib.sha256(payload).hexdigest()
    assert path.read_bytes() == payload


def test_close_session_round_trips_and_start_refuses_truncate():
    td = Path(tempfile.mkdtemp(prefix="p11_sess_"))
    root = install(td / "live", tree_id="p11-session")
    k = Kernel(root, worker="p11")
    k.sessions.open("s1", "Cm")
    k.sessions.session.record_fact("lane", "p11")
    seed = k.sessions.close_session(handoff_to="s2")
    assert seed.is_file()
    assert any(r["event"] == "SESSION_SEED_WRITTEN" for r in k.ledger.verify())
    body = json.loads(seed.read_text(encoding="utf-8"))
    assert body["facts"]["lane"] == "p11"
    seed.write_bytes(seed.read_bytes()[:24])
    try:
        k.sessions.start_session("Cm")
    except SessionError as e:
        assert e.kind == "BAD_SEED"
    else:
        raise AssertionError("truncated SEED must refuse start")


def test_truncated_write_refuses_verify_mismatch():
    td = Path(tempfile.mkdtemp(prefix="p11_trunc_"))
    path = td / "SEED.json"
    payload = b'{"kind":"COSMOS_SEED","facts":{"x":"y"}}'
    import builtins
    real_open = builtins.open

    def truncating_open(p, mode="r", *a, **kw):
        fh = real_open(p, mode, *a, **kw)
        if "b" in mode and "w" in mode:
            orig = fh.write

            def write(b, _orig=orig):
                if isinstance(b, (bytes, bytearray)) and len(b) > 12:
                    return _orig(b[:12])
                return _orig(b)

            fh.write = write  # type: ignore[method-assign]
        return fh

    builtins.open = truncating_open  # type: ignore[assignment]
    try:
        write_declared(path, payload)
    except ValidateError as e:
        assert e.kind == "VERIFY_MISMATCH"
    else:
        raise AssertionError("truncated write must VERIFY_MISMATCH")
    finally:
        builtins.open = real_open  # type: ignore[assignment]


def test_verify_mismatch_kind_is_typed():
    err = ValidateError("VERIFY_MISMATCH", "disk lie")
    assert err.kind == "VERIFY_MISMATCH"
    serr = SessionError("VERIFY_MISMATCH", "archive copy mutated")
    assert serr.kind == "VERIFY_MISMATCH"


def main() -> int:
    test_old_write_declared_seals_truncated_disk()
    test_new_write_declared_round_trips()
    test_close_session_round_trips_and_start_refuses_truncate()
    test_truncated_write_refuses_verify_mismatch()
    test_verify_mismatch_kind_is_typed()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
