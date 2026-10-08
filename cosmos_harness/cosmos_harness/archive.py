"""Removal is a move into ``_delme``.

The harness has no delete hand. This module is what ``archive`` calls.
The ledger line is append-only JSONL beside the moved bytes. A failed move
leaves the original in place; this function does not unlink it afterwards.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path

from cosmos_harness.jail import Jail
from cosmos_harness.refuse import Refuse


def stage(jail: Jail, relative: str) -> Path:
    """Move ``relative`` under ``_delme`` and append one ledger line.

    Returns the archive path. Refuses a missing file and a path that is the
    jail root itself.
    """
    target = jail.resolve(relative)
    if target == jail.root:
        raise Refuse("ARCHIVE_ROOT", relative)
    if not target.is_file():
        raise Refuse("ARCHIVE_MISSING", relative)
    payload = target.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    dest_dir = jail.root / "_delme"
    dest_dir.mkdir(exist_ok=True)
    dest = dest_dir / f"{stamp}_{digest[:8]}_{target.name}"
    shutil.move(str(target), str(dest))
    if target.exists():
        raise Refuse("ARCHIVE_STILL_THERE", relative)
    line = {
        "at": stamp,
        "original": relative.replace("\\", "/"),
        "archive": jail.relative(dest),
        "sha256": digest,
        "bytes": len(payload),
    }
    ledger = dest_dir / "ledger.jsonl"
    with ledger.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(line, sort_keys=True) + "\n")
    return dest
