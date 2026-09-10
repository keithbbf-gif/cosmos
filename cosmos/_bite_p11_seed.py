#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P11 fail-closed SEED write. Old seals a truncated file; new refuses.

    py -3.14 cosmos/_bite_p11_seed.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

from cosmos_validate import ValidateError, write_declared  # noqa: E402
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_session import SessionError  # noqa: E402

OUT = HERE / "_bite_p11_seed.json"


def write_declared_old(path: Path, content: bytes) -> dict:
    with open(path, "wb") as fh:
        fh.write(content)
    return {"path": str(path), "len": len(content),
            "sha": hashlib.sha256(content).hexdigest()}


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_p11_"))
    payload = b'{"schema":"cosmos-session-seed/1","kind":"COSMOS_SEED","facts":{}}'

    old_path = td / "old" / "SEED.json"
    old_path.parent.mkdir(parents=True)
    old_decl = write_declared_old(old_path, payload)
    old_path.write_bytes(payload[:20])
    old_seals = (
        old_decl["len"] == len(payload)
        and hashlib.sha256(old_path.read_bytes()).hexdigest() != old_decl["sha"]
    )

    new_path = td / "new" / "SEED.json"
    new_path.parent.mkdir(parents=True)
    ok_decl = write_declared(new_path, payload)
    round_trip_ok = (
        ok_decl["len"] == len(payload)
        and ok_decl["sha"] == hashlib.sha256(payload).hexdigest()
        and new_path.read_bytes() == payload
    )

    # Mutate-after-write is not the close path; the close path re-reads before
    # returning. Prove a lying declaration cannot be produced: after a good
    # write, truncating the file and calling read_verified with the declaration
    # is HASH_MISMATCH / SHORT_READ — start_session already refuses that as
    # BAD_SEED. The new gate is write-time VERIFY_MISMATCH when disk != buffer.
    # Simulate a truncated write via a too-short intended payload vs a longer
    # claim: write_declared itself is the claim. Force mismatch by writing
    # then replacing with a wrapper that the round-trip sees.
    lie = td / "lie" / "SEED.json"
    lie.parent.mkdir(parents=True)
    refused_kind = None
    import builtins
    real_open = builtins.open

    def truncating_open(path, mode="r", *a, **kw):
        fh = real_open(path, mode, *a, **kw)
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
        write_declared(lie, payload)
    except ValidateError as e:
        refused_kind = e.kind
    finally:
        builtins.open = real_open  # type: ignore[assignment]

    root = install(td / "live", tree_id="p11-seed-bite")
    k = Kernel(root, worker="p11")
    k.sessions.open("s1", "Cm")
    k.sessions.session.record_fact("lane", "p11")
    seed_path = k.sessions.close_session(handoff_to="s2")
    written = any(r["event"] == "SESSION_SEED_WRITTEN" for r in k.ledger.verify())
    body = seed_path.read_bytes()
    close_round_trip = json.loads(body.decode("utf-8"))["facts"]["lane"] == "p11"

    # Mutate the on-disk seed after close; start must still refuse (existing).
    seed_path.write_bytes(body[:30])
    start_kind = None
    try:
        k.sessions.start_session("Cm")
    except SessionError as e:
        start_kind = e.kind

    rec = {
        "old_seals_after_truncate": old_seals,
        "new_round_trip_ok": round_trip_ok,
        "close_wrote_seed": seed_path.is_file() and written and close_round_trip,
        "start_after_truncate_kind": start_kind,
        "truncated_write_kind": refused_kind,
    }
    rec["all_bite"] = (
        rec["old_seals_after_truncate"] is True
        and rec["new_round_trip_ok"] is True
        and rec["close_wrote_seed"] is True
        and rec["start_after_truncate_kind"] == "BAD_SEED"
        and rec["truncated_write_kind"] == "VERIFY_MISMATCH"
    )
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
