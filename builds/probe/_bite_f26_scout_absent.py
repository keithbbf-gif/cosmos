#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite F-26: the open-ended scout clock must be ABSENT before it is built.

    py -3.14 builds/probe/_bite_f26_scout_absent.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_bite_f26_scout_absent.json"
TARGET = HERE / "cosmos_newai_scout.py"


def main() -> int:
    rec = {
        "schema": "cosmos-bite/1",
        "what": "F-26 scout clock is ABSENT (ModuleNotFoundError / no file)",
        "target": str(TARGET),
        "exists": TARGET.is_file(),
    }
    try:
        sys.path.insert(0, str(HERE))
        import cosmos_newai_scout as m  # noqa: F401
        rec.update(state="PRESENT", kind="imported",
                   detail=getattr(m, "__file__", "?"))
    except ModuleNotFoundError as e:
        rec.update(state="ABSENT", kind="ModuleNotFoundError", detail=str(e))
    except Exception as e:  # noqa: BLE001
        rec.update(state="ERROR", kind=type(e).__name__, detail=str(e))
    rec["all_bite"] = rec.get("state") == "ABSENT" and rec.get("exists") is False
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
