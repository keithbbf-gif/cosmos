#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-measure live --dry-run AFTER docs/AUTO_RESESSION_PROMPT.md is filed.

Writes nothing to live/. Stamps describes so a later edit cannot hide here.

    py -3.14 builds/probe/_emit_f51_prompt_live.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "_f51_prompt_live.json"
PROMPT = REPO / "docs" / "AUTO_RESESSION_PROMPT.md"
LIVE = REPO / "live"


def main() -> int:
    raw = PROMPT.read_bytes()
    disk_sha = hashlib.sha256(raw).hexdigest()
    cmd = [
        sys.executable,
        str(HERE / "cosmos_resession.py"),
        "--root", str(LIVE),
        "--repo", str(REPO),
        "--dry-run",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    rec = json.loads(p.stdout)
    out = {
        "schema": "cosmos-f51-prompt-live/1",
        "ok": (p.returncode == 0
               and rec.get("prompt_sha") == disk_sha
               and rec.get("tree_id") == "KMesh-COSMOS-live"
               and rec.get("dry_run") is True
               and rec.get("state") == "IDLE"),
        "cli_rc": p.returncode,
        "disk_sha": disk_sha,
        "disk_bytes": len(raw),
        "dry_run_prompt_sha": rec.get("prompt_sha"),
        "dry_run_state": rec.get("state"),
        "dry_run_tree_id": rec.get("tree_id"),
        "dry_run_why": rec.get("why"),
        "dry_run_clock_id": rec.get("clock_id"),
        "prompt_path": rec.get("prompt_path"),
        "writes": 0,
        "heartbeat_written": False,
    }
    sys.path.insert(0, str(HERE))
    import artifact_freshness as af                                    # noqa: WPS433
    af.write_stamped(OUT, out, REPO,
                     ["builds/probe/cosmos_resession.py",
                      "docs/AUTO_RESESSION_PROMPT.md"])
    print(json.dumps(out, indent=1))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
