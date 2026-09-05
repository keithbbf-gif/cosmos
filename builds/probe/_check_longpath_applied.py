#!/usr/bin/env python3
"""Scratch measurement: has the F-44 long-path proposal landed in cosmos/ yet?"""
import json
import pathlib

PREFIX = "\\\\?\\"
FILES = ["cosmos/cosmos_backup.py", "cosmos/cosmos_backup_clock.py",
         "builds/backup/cosmos_backup.py",
         "builds/probe/proposed/cosmos_backup.py",
         "builds/probe/proposed/cosmos_backup_clock.py"]
out = {}
for p in FILES:
    f = pathlib.Path(p)
    if not f.exists():
        out[p] = "ABSENT"
        continue
    s = f.read_text(encoding="utf-8", errors="replace")
    out[p] = {"lines": s.count("\n") + 1, "def _x(": "def _x(" in s,
              "extended_prefix": PREFIX in s, "import json": "import json" in s,
              "SOURCE_UNREADABLE": "SOURCE_UNREADABLE" in s,
              "SNAPSHOT_INCOMPLETE": "SNAPSHOT_INCOMPLETE" in s}
print(json.dumps(out, indent=1))
