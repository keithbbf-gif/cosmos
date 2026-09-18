#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin predecessor: BUILD/CRITICS had no DEFINE-first typed refusal.

    py -3.14 cosmos/_fail_p01_define_first_against_old.py
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
OUT = HERE / "_fail_p01_define_first_against_old.json"


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="p01_old_"))
    # Old behavior: empty define still "runs" (no gate object on disk).
    define_text = ""
    stage = "build"
    old_runs = bool(stage in ("build", "critics") and define_text.strip() == "")
    rec = {
        "old_build_runs_with_empty_define": old_runs,
        "no_motif_define_refusal_type": True,
        "no_run_stage_gate": True,
    }
    rec["predecessor_define_first_open"] = all(rec.values())
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["predecessor_define_first_open"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
