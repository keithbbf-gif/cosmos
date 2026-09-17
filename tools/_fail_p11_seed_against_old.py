#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin predecessor: write_declared sealed intended bytes, not disk.

Old primitive (GitHub main 302850a): write, return len/sha of the buffer.
Truncate or mutate the file after that write and the declaration still
matches the buffer. close_session then appended SESSION_SEED_WRITTEN.

    py -3.14 cosmos/_fail_p11_seed_against_old.py
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
OUT = HERE / "_fail_p11_seed_against_old.json"


def write_declared_old(path: Path, content: bytes) -> dict:
    """Exact pre-fix body: no fsync, no re-read."""
    with open(path, "wb") as fh:
        fh.write(content)
    return {"path": str(path), "len": len(content),
            "sha": hashlib.sha256(content).hexdigest()}


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_fail_p11_"))
    path = td / "SEED.json"
    payload = b'{"schema":"cosmos-session-seed/1","kind":"COSMOS_SEED"}'
    decl = write_declared_old(path, payload)
    path.write_bytes(payload[:20])  # silent truncation after "seal"
    disk = path.read_bytes()
    rec = {
        "old_sealed_intended_len": decl["len"] == len(payload),
        "old_declared_sha_is_buffer": decl["sha"] == hashlib.sha256(payload).hexdigest(),
        "disk_truncated": len(disk) == 20,
        "disk_sha_disagrees": hashlib.sha256(disk).hexdigest() != decl["sha"],
        "old_did_not_refuse": True,
    }
    rec["predecessor_still_seals"] = (
        rec["old_sealed_intended_len"]
        and rec["old_declared_sha_is_buffer"]
        and rec["disk_truncated"]
        and rec["disk_sha_disagrees"]
        and rec["old_did_not_refuse"]
    )
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["predecessor_still_seals"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
