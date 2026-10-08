"""Report which seated doors have a binary on PATH. Does not run them."""

from __future__ import annotations

import shutil
from pathlib import Path

from g47.doors import DOORS
from g47.locate import probe


def report() -> list[dict[str, str]]:
    indexed = {row["id"]: row for row in probe()}
    rows: list[dict[str, str]] = []
    for door in DOORS.values():
        exe = door.binary[0] if door.binary else ""
        if not exe:
            state = "no-binary"
        elif shutil.which(exe):
            state = "on-path"
        else:
            state = "missing"
        if not door.seated:
            state = state + "/unseated"
        if door.key_file:
            state = state + ("/key" if Path(door.key_file).is_file() else "/NO_KEY")
        extra = indexed.get(door.id, {})
        rows.append({
            "door": door.id,
            "strength": door.strength,
            "binary": exe,
            "state": state,
            "grade": door.grade,
            "local": extra.get("local", ""),
            "binary_found": extra.get("binary_found", ""),
            "obtain": extra.get("obtain", ""),
        })
    return rows
