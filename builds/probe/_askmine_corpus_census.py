#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Census the transcript corpus: where do OPERATOR turns actually live?

Read-only. Prints counts only -- never transcript text, never key material.
Written to answer one question with a measurement instead of an assumption:
the 963-transcript `.claude\\projects\\V--A-Ai-COSMOS` corpus yields exactly
1 user turn per file, all `dispatch`. That is either a parser blindness or a
true statement that Keith's own turns are in a different root.
"""
from __future__ import annotations

import collections
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cosmos_askmine import parse_transcript  # noqa: E402

SKIP_DIRS = {"node_modules", ".git", "__pycache__", "Cache", "GPUCache",
             "Code Cache", "blob_storage", "Crashpad", "Local Storage",
             "Session Storage", "Network", "Partitions"}


def walk(root: Path, cap: int = 20000) -> list[Path]:
    out: list[Path] = []
    if not root.exists():
        return out
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.lower().endswith(".jsonl"):
                out.append(Path(dirpath) / fn)
                if len(out) >= cap:
                    return out
    return out


def main() -> int:
    home = Path.home()
    appdata = Path(os.environ.get("APPDATA") or (home / "AppData" / "Roaming"))
    roots = [
        appdata / "Claude",
        home / ".claude" / "projects",
        home / ".claude" / "sessions",
        home / ".grok" / "sessions",
        home / ".cowork",
    ]
    for root in roots:
        files = walk(root)
        if not files:
            print(f"{'MISSING' if not root.exists() else 'EMPTY':>8}  {root}")
            continue
        tot = collections.Counter()
        multi = []
        for p in files:
            r = parse_transcript(p)
            if not r["ok"]:
                tot["unparsed"] += 1
                continue
            u = [t for t in r["turns"] if t["role"] == "user"]
            tot["files"] += 1
            tot["user_turns"] += len(u)
            for t in u:
                tot["asker_" + t["asker"]] += 1
            if len(u) > 1:
                multi.append((len(u), p))
        multi.sort(key=lambda kv: -kv[0])
        print(f"\nROOT {root}")
        print(f"  jsonl={len(files)} {dict(tot)}")
        print(f"  transcripts with >1 user turn: {len(multi)}")
        for n, p in multi[:8]:
            print(f"    {n:5d} user turns  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
