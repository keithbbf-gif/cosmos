#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GLM Coder-1 via pi.cmd. Fresh PI home (no stub auth.json). Key from env file, never argv."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
KEY = ROOT / "live" / "config" / "openrouter_api_key.txt"
PI_HOME = ROOT / "live" / "work" / "pi-run"
PI_CMD = Path(os.environ.get("LOCALAPPDATA", "")) / ".." / "Roaming" / "npm" / "pi.cmd"
if not PI_CMD.is_file():
    PI_CMD = Path(r"C:\Users\Papa\AppData\Roaming\npm\pi.cmd")
WRAP = ROOT / "work_orders" / "ccr" / "hero_coders" / "_CODER_WRAP.md"
SYS = (
    "CODER. You have read, write, and edit in this directory only. "
    "Write the file the task names. Python only. No markdown fence. No sentence. "
    "No grok.exe. No merge. Do not leave this directory."
)


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("Usage: call_pi_glm.py WORKTREE ITEM", file=sys.stderr)
        return 2
    worktree = Path(argv[1])
    item = argv[2]
    model = argv[3] if len(argv) > 3 else "z-ai/glm-5.3-flash"
    worktree.mkdir(parents=True, exist_ok=True)
    key = KEY.read_text(encoding="utf-8-sig").strip()
    if len(key) < 20:
        print("OPENROUTER key file too short", file=sys.stderr)
        return 3
    PI_HOME.mkdir(parents=True, exist_ok=True)
    (PI_HOME / "sessions").mkdir(parents=True, exist_ok=True)
    stub = PI_HOME / "auth.json"
    if stub.is_file():
        stub.unlink()
    catalog = ROOT / "live" / "work" / "pi-home" / "models-store.json"
    dest_cat = PI_HOME / "models-store.json"
    if catalog.is_file() and not dest_cat.is_file():
        dest_cat.write_bytes(catalog.read_bytes())
    env = os.environ.copy()
    env["OPENROUTER_API_KEY"] = key
    env["PI_CODING_AGENT_DIR"] = str(PI_HOME)
    env["PI_CODING_AGENT_SESSION_DIR"] = str(PI_HOME / "sessions")
    env["PI_OFFLINE"] = "1"
    sys.path.insert(0, str(ROOT / "work_orders" / "ccr"))
    from hero_unify import bind_native, mission_for, system_for
    bind_native(worktree, "pi")
    sys_prompt = system_for(worktree) or SYS
    item_text = mission_for(worktree) or item
    cmd = [
        str(PI_CMD), "-p",
        "--provider", "openrouter",
        "--model", model,
        "--tools", "read,write,edit",
        "--system-prompt", sys_prompt,
        "--no-session",
    ]
    cmd.append(item_text)
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    proc = subprocess.Popen(
        cmd, cwd=str(worktree), env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace",
        creationflags=CREATE_NEW_PROCESS_GROUP,
    )
    try:
        out, err = proc.communicate(timeout=150)
        mouth = (out or "").strip() or (err or "")
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            capture_output=True, creationflags=0x08000000,
        )
        out, err = proc.communicate(timeout=5)
        mouth = ((out or "").strip() if out else "") or "TIMEOUT"
        err = (err or "") + "\npi timeout (process tree killed)"
        rc = 124
    (worktree / "mouth.txt").write_text(mouth, encoding="utf-8", newline="\n")
    (worktree / "pi_stderr.txt").write_text(err, encoding="utf-8")
    sys.stdout.buffer.write((mouth[:4000] + "\n").encode("utf-8", errors="replace"))
    return 0 if rc == 0 else int(rc or 1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
