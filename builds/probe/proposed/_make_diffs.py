#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_make_diffs - emit the unified diffs for the PROPOSED changes to cosmos/.

The proposals under this directory target modules OUTSIDE this agent's fence
(`cosmos/cosmos_backup.py`, `cosmos/cosmos_backup_clock.py`). COW disposes of them;
nothing here writes those files. This script only prints the delta, so the proposal
is a generated artifact rather than a transcription — and so its size is a number,
not an adjective.

Line endings are read with universal newlines on both sides, because the bash mount
shows a CRLF-vs-LF phantom full-tree diff (CLAUDE.md hazard) and `cosmos_backup.py`
is genuinely CRLF while the proposal is LF. Comparing content, not bytes.

    py -3.14 builds/probe/proposed/_make_diffs.py
"""
from __future__ import annotations

import difflib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]

PAIRS = (
    ("cosmos/cosmos_backup.py", "cosmos_backup.py"),
    ("cosmos/cosmos_backup_clock.py", "cosmos_backup_clock.py"),
    ("cosmos/cosmos_registry.py", "cosmos_registry.py"),      # F-25 freshness
)
OUT = HERE / "_PROPOSED.diff"


def main() -> int:
    """Print the diffs AND write them to `_PROPOSED.diff`.

    Writing the artifact here rather than by shell redirect means the file can
    never be a stale hand-copy of a script that has since changed - the size
    printed and the size on disk come from the same run.
    """
    total_add = total_del = 0
    chunks: list[str] = []
    for target, proposed in PAIRS:
        a = (REPO / target).read_text(encoding="utf-8").splitlines(keepends=True)
        b = (HERE / proposed).read_text(encoding="utf-8").splitlines(keepends=True)
        d = list(difflib.unified_diff(a, b, fromfile=f"a/{target}",
                                      tofile=f"b/{target}", n=3))
        add = sum(1 for ln in d if ln.startswith("+") and not ln.startswith("+++"))
        rem = sum(1 for ln in d if ln.startswith("-") and not ln.startswith("---"))
        total_add += add
        total_del += rem
        header = f"### PROPOSAL: {target}  (+{add} / -{rem})\n"
        chunks.append(header + "".join(d) + "\n")
        print(header, end="")
        sys.stdout.writelines(d)
        print()
    footer = f"### TOTAL +{total_add} / -{total_del}\n"
    chunks.append(footer)
    OUT.write_text("".join(chunks), encoding="utf-8", newline="\n")
    print(footer, end="")
    print(f"### wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
