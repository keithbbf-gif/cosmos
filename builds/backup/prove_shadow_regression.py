#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""prove_shadow_regression - watch the sys.path-shadow regression test FAIL.

A regression test nobody has seen fail against the old code is an assumption. This
script reconstructs the PRE-FIX import block of `cosmos_offsite_clock.py` (the one
that put `cosmos/` on sys.path to reach the resolver), writes it to a scratch copy,
and runs the CLI against it in a fresh interpreter - exactly what
`TestModuleResolutionInAFreshProcess` does.

Expected, and measured 2026-08-31 on the live root:

    OLD  rc=1  ImportError: cannot import name 'BackupRefusal' from 'cosmos_backup'
                            (V:\A\Ai\COSMOS\cosmos\cosmos_backup.py)
    NEW  rc=0  {"task": "COSMOS Offsite Push", ...}

The scratch copy is written into a temp dir, never the tree, and the tree's module is
never modified. `--plan-task` only prints an argv, so nothing is scheduled and nothing
is written by either run.

    py -3.14 builds/backup/prove_shadow_regression.py --root V:\A\Ai\COSMOS\live
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLOCK = HERE / "cosmos_offsite_clock.py"

OLD_IMPORT_BLOCK = '''_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_COSMOS = _HERE.parents[1] / "cosmos"
if str(_COSMOS) not in sys.path:
    sys.path.insert(0, str(_COSMOS))

import cosmos_backup as cb
import cosmos_backup_r2 as r2
from cosmos_backup import BackupRefusal
from cosmos_paths import CosmosPaths, CosmosPathError


'''


def build_old_copy(dest_dir: Path) -> Path:
    src = CLOCK.read_text(encoding="utf-8")
    start = src.index("_HERE = Path(__file__)")
    end = src.index('SCHEMA = "cosmos-offsite-clock/1"')
    old = dest_dir / "cosmos_offsite_clock_SHADOWED.py"
    old.write_text(src[:start] + OLD_IMPORT_BLOCK + src[end:], encoding="utf-8")
    return old


def run(path: Path, root: str) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(path), "--root", root, "--plan-task"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120)
    tail = ((p.stderr or "") or (p.stdout or "")).strip().splitlines()
    return p.returncode, (tail[-1] if tail else "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True)
    a = ap.parse_args()

    # The scratch copy must sit in the SAME LAYOUT as the real one, or the shadow
    # cannot happen and the proof is theatre: the old code computes `cosmos/` as
    # _HERE.parents[1]/"cosmos", so both trees are mirrored under a temp root. The
    # repo itself is never written to and never modified.
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_shadow_"))
    repo = HERE.parents[1]
    mirror = tmp / "builds" / "backup"
    mirror.mkdir(parents=True)
    (tmp / "cosmos").mkdir()
    for name in ("cosmos_backup.py", "cosmos_backup_r2.py"):
        (mirror / name).write_text((HERE / name).read_text(encoding="utf-8"), encoding="utf-8")
    # Every cosmos/ module, so the shadowed import fails for the REAL reason
    # (cosmos/cosmos_backup.py has no BackupRefusal) and not for a missing sibling.
    for p in sorted((repo / "cosmos").glob("*.py")):
        (tmp / "cosmos" / p.name).write_bytes(p.read_bytes())
    old = build_old_copy(mirror)

    old_rc, old_tail = run(old, a.root)
    new_rc, new_tail = run(CLOCK, a.root)

    print(f"OLD (cosmos/ on sys.path)  rc={old_rc}  {old_tail[:200]}")
    print(f"NEW (resolver by path)     rc={new_rc}  {new_tail[:200]}")

    ok = old_rc != 0 and new_rc == 0
    print("REGRESSION PROVEN" if ok else "NOT PROVEN — the old copy did not fail")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
