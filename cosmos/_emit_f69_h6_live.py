#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F-69 H6 live-prove: run a claude-CLI job THROUGH the dispatch harness.

Does not read, print, or copy key material. Does not POST Cloud Agents.
Scratch root only (install() tree_id=f69-h6). Writes cosmos/_f69_h6_live.json.

    py -3.14 cosmos/_emit_f69_h6_live.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

from cosmos_kernel import install  # noqa: E402
from cosmos_dispatch import dispatch  # noqa: E402

OUT = HERE / "_f69_h6_live.json"
NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_f69_h6_"))
    root = install(td / "live", tree_id="f69-h6")
    queue = td / "queue"
    for extra in (queue, queue / "_lanes" / "lg", queue / "_lanes" / "pb"):
        extra.mkdir(parents=True, exist_ok=True)
        (extra / "running").mkdir(parents=True, exist_ok=True)
        (extra / "done").mkdir(parents=True, exist_ok=True)
    dhx = td / "docs" / "AGENT_BRIEF.md"
    _write(dhx, "# DHx\n\n## Assignment log\n\n## Active assignments\n")
    cwd = td / "workdir"
    cwd.mkdir()
    sent = json.loads((Path(root) / ".cosmos-root.json").read_text(encoding="utf-8"))
    t0 = time.time()
    rec = dispatch(
        "F5",
        "Reply with the single word PONG. Do not edit any files.",
        str(cwd), kind="F5", queue=queue, runtime_root=root, dhx=dhx,
    )
    job = Path(rec["job_path"])
    src = job.read_text(encoding="utf-8")
    p = subprocess.run(
        [sys.executable, str(job)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(cwd), timeout=90, creationflags=NO_WINDOW,
    )
    result_path = Path(rec["result_path"])
    result = {}
    if result_path.is_file():
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            result = {"unreadable": True}
    stdout = str(result.get("stdout_tail") or p.stdout or "")
    live = json.loads(
        (REPO / "live" / ".cosmos-root.json").read_text(encoding="utf-8"))
    out = {
        "schema": "cosmos-f69-h6-live/1",
        "ok": bool(
            rec.get("ok")
            and rec.get("kind") == "claude"
            and p.returncode == 0
            and "PONG" in stdout.upper()
            and '"-p"' in src
            and "claude" in src
        ),
        "tree_id": live.get("tree_id"),
        "system": live.get("system"),
        "scratch_tree_id": sent.get("tree_id"),
        "dispatch_kind": rec.get("kind"),
        "dispatch_kind_live": rec.get("kind_live"),
        "job_exists": job.is_file(),
        "job_has_claude_p": '"-p"' in src and '"claude"' in src,
        "job_rc": p.returncode,
        "result_rc": result.get("rc"),
        "result_kind": result.get("kind"),
        "result_kind_live": result.get("kind_live"),
        "stdout_pong": "PONG" in stdout.upper(),
        "stdout_tail": stdout[-200:],
        "secs": round(time.time() - t0, 1),
        "through_harness": True,
        "note": "claude -p FINISHED through render_job/_claude_job, not a raw CLI. "
                "No key material. Cursor Cloud Agents not launched.",
    }
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in (
        "ok", "tree_id", "dispatch_kind", "dispatch_kind_live",
        "job_rc", "result_rc", "stdout_pong", "secs")}, indent=1))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
