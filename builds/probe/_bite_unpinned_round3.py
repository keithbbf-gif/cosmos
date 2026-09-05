#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: round-3 unpinned probe refusals against CURRENT code.

  * pause mode="resumed" (M10 third value) with a TidyUP-shaped set_by/reason
    is HOLD because unrecognised mode fails closed BEFORE the ARM branch.
    Strip that check and the same flag becomes ARM — a wrong resume.
  * sha256_file of a directory is None (NO_PROMPT input), not a crash.

    py -3.14 builds/probe/_bite_unpinned_round3.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_round3.json"

from cosmos_resession import classify_pause, sha256_file              # noqa: E402


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite3p_"))
    rec = {"schema": "cosmos-bite/1",
           "what": "round3 unpinned probe refusals — current vs claimed"}
    try:
        resumed_tidy = {
            "state": "PAUSED", "mode": "resumed",
            "set_by": "COW", "reason": "TidyUP + resession",
        }
        cls = classify_pause(resumed_tidy)
        rec["resumed_tidy_class"] = cls.get("class")
        rec["resumed_tidy_why"] = cls.get("why")

        hold_keith = {
            "state": "PAUSED", "mode": "hold",
            "set_by": "Keith", "reason": "stop",
        }
        rec["operator_hold_class"] = classify_pause(hold_keith).get("class")

        arm_tidy = {
            "state": "PAUSED", "mode": "hold",
            "set_by": "COW", "reason": "TidyUP + resession (Keith, 2026-08-25)",
        }
        rec["tidyup_hold_class"] = classify_pause(arm_tidy).get("class")

        d = tmp / "as_dir"
        d.mkdir()
        rec["sha256_dir_returns"] = sha256_file(d)
        rec["sha256_dir_crash"] = None
        missing = tmp / "nope.md"
        rec["sha256_missing_returns"] = sha256_file(missing)
    except Exception as e:                                            # noqa: BLE001
        rec["crash"] = f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec["all_bite"] = (
        rec.get("resumed_tidy_class") == "HOLD"
        and rec.get("tidyup_hold_class") == "ARM"
        and rec.get("operator_hold_class") == "HOLD"
        and rec.get("sha256_dir_returns") is None
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
