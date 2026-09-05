#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-measure LIVE_LEDGER_FORBIDDEN against the CURRENT tool_disposition.py.

Does not open the ledger (the refusal is the evidence). st_size only —
never reads, prints, or copies key material. Stamps describes.

    py -3.14 builds/probe/_emit_f41_live_apply.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "_f41_live_apply_refused.json"
LEDGER = REPO / "live" / "ledger" / "authority.jsonl"
ROOT = REPO / "live"


def main() -> int:
    before = LEDGER.stat() if LEDGER.is_file() else None
    p = subprocess.run(
        [sys.executable, str(HERE / "tool_disposition.py"),
         "--root", str(ROOT),
         "--apply", "--ledger", str(LEDGER)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO),
    )
    after = LEDGER.stat() if LEDGER.is_file() else None
    kind = None
    try:
        body = json.loads(p.stdout or "{}")
        kind = body.get("kind")
    except json.JSONDecodeError:
        body = {}
    rec = {
        "cli_rc": p.returncode,
        "kind": kind,
        "stdout_head": (p.stdout or "")[:800],
        "stderr_head": (p.stderr or "")[:400],
        "ledger_before_bytes": None if before is None else before.st_size,
        "ledger_after_bytes": None if after is None else after.st_size,
        "ledger_untouched": (
            before is not None and after is not None
            and before.st_size == after.st_size
            and before.st_mtime_ns == after.st_mtime_ns
        ),
        "mtime_ns_before": None if before is None else before.st_mtime_ns,
        "mtime_ns_after": None if after is None else after.st_mtime_ns,
    }
    rec["ok"] = rec["kind"] == "LIVE_LEDGER_FORBIDDEN" and rec["ledger_untouched"] is True
    sys.path.insert(0, str(HERE))
    import artifact_freshness as af                                    # noqa: WPS433
    af.write_stamped(OUT, rec, REPO, ["builds/probe/tool_disposition.py"])
    print(json.dumps({k: rec[k] for k in rec if k != "stdout_head"},
                     indent=2, default=str))
    print("stdout_head_chars", len(rec.get("stdout_head") or ""))
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
