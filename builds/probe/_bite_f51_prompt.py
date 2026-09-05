#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: docs/AUTO_RESESSION_PROMPT.md is ABSENT. A fire is NO_PROMPT.

Required before filing P1.3. A claim that the prompt is unfiled is not
evidence — this script emits the live values.

    py -3.14 builds/probe/_bite_f51_prompt.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "_bite_f51_prompt.json"
PROMPT = REPO / "docs" / "AUTO_RESESSION_PROMPT.md"
LIVE = REPO / "live"


def main() -> int:
    exists = PROMPT.is_file()
    sha = None
    if exists:
        sha = hashlib.sha256(PROMPT.read_bytes()).hexdigest()
    cmd = [
        sys.executable,
        str(HERE / "cosmos_resession.py"),
        "--root", str(LIVE),
        "--repo", str(REPO),
        "--dry-run",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    rec = None
    parse_err = None
    try:
        rec = json.loads(p.stdout)
    except ValueError as e:
        parse_err = f"{type(e).__name__}: {e}"
    prompt_sha = (rec or {}).get("prompt_sha")
    # Fire path with a good seed and no prompt: NO_PROMPT (already in
    # test_resession; re-measured here so the bite names the live module).
    sys.path.insert(0, str(HERE))
    from cosmos_resession import decide, sha256_file  # noqa: E402
    fire = decide(
        pause=None,
        seed={"ok": True, "kind": None, "detail": "", "sha": "s", "sid": "Cm-9",
              "schema": "cosmos-session-seed/2", "thin": False,
              "cursor": {"slug": "auto-resession", "stage": 4}},
        cow_hb=None, pid_alive=False, now=1.0, prompt_sha=None, rail="grok",
        lease_held_by=None,
    )
    hashed = sha256_file(PROMPT)
    bite = {
        "schema": "cosmos-bite/1",
        "what": "F-51 remaining — docs/AUTO_RESESSION_PROMPT.md unfiled",
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "prompt_path": str(PROMPT),
        "prompt_exists": exists,
        "prompt_sha_on_disk": sha,
        "sha256_file_returns": hashed,
        "dry_run_rc": p.returncode,
        "dry_run_prompt_sha": prompt_sha,
        "dry_run_state": (rec or {}).get("state"),
        "dry_run_tree_id": (rec or {}).get("tree_id"),
        "dry_run_why": (rec or {}).get("why"),
        "dry_run_parse_err": parse_err,
        "fire_without_prompt_kind": fire.get("refused_kind"),
        "fire_without_prompt_state": fire.get("state"),
        "all_bite": (not exists) and hashed is None and prompt_sha is None
                    and fire.get("refused_kind") == "NO_PROMPT",
    }
    OUT.write_text(json.dumps(bite, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(bite, indent=1))
    return 0 if bite["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
