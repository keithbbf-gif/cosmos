#!/usr/bin/env python3
"""Ling via OpenCode. Prompt is one argv, not a shell string. No fat preload."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
KEY = ROOT / "live" / "config" / "openrouter_api_key.txt"
HOME = ROOT / "live" / "work" / "opencode-home"
OC = Path(os.environ.get("LOCALAPPDATA", "")) / ".." / "Roaming" / "npm" / "opencode.cmd"
if not OC.is_file():
    OC = Path(r"C:\Users\Papa\AppData\Roaming\npm\opencode.cmd")


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("Usage: call_opencode_ling.py WORKTREE ITEM", file=sys.stderr)
        return 2
    worktree = Path(argv[1])
    item = argv[2]
    worktree.mkdir(parents=True, exist_ok=True)
    key = KEY.read_text(encoding="utf-8-sig").strip()
    env = os.environ.copy()
    env["OPENROUTER_API_KEY"] = key
    env["OPENCODE_CONFIG"] = str(HOME / "opencode.json")
    env["OPENCODE_CONFIG_DIR"] = str(HOME)
    env["OPENCODE_DATA_DIR"] = str(HOME / "data")
    sys.path.insert(0, str(ROOT / "work_orders" / "ccr"))
    from hero_unify import bind_native, mission_for
    bind_native(worktree, "opencode")
    item_text = mission_for(worktree) or item
    cmd = [
        str(OC), "run",
        "--dir", str(worktree),
        "-m", "openrouter/inclusionai/ling-3.0-flash",
        "--", item_text,
    ]
    proc = subprocess.run(
        cmd, cwd=str(worktree), env=env,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=150,
    )
    mouth = (proc.stdout or "").strip() or (proc.stderr or "")
    (worktree / "mouth.txt").write_text(mouth, encoding="utf-8", newline="\n")
    sys.stdout.buffer.write((mouth[:2000] + "\n").encode("utf-8", errors="replace"))
    return int(proc.returncode or 0)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
