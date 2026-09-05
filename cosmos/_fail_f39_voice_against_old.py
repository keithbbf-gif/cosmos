#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-39 voice-hardening-split pins FAIL against the staged predecessor.

Loads `_delme/predispose_service_f39_voice_20260831T162539Z/cosmos_service.py`
as source so the new pins are measured against the unsplit module. Writes
`cosmos/_fail_f39_voice_against_old.json`. all_new_pins_failed is the bite.

Does not import the old module as cosmos_service (would shadow live).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_service_f39_voice_20260831T162539Z"
OLD = OLD_DIR / "cosmos_service.py"
OUT = REPO / "cosmos" / "_fail_f39_voice_against_old.json"


def main() -> int:
    if not OLD.is_file():
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "old": str(OLD)}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    old_src = OLD.read_text(encoding="utf-8")
    live_hard = REPO / "cosmos" / "cosmos_voice_hardening.py"
    pins = {
        "hardening_module_imported": "cosmos_voice_hardening" in old_src,
        "bootup_moved_out": "def _bootup_summary" not in old_src,
        "flat_trim_moved_out": "def _flat_trim" not in old_src,
        "stream_section_moved_out": "def _stream_section" not in old_src,
        "dedupe_const_moved_out": "DEDUPE_WINDOW_S =" not in old_src,
        "banner_is_reexport_only": (
            "# ---------------- voice hardening constants" in old_src
            and "from cosmos_voice_hardening import" in old_src
            and "def _bootup_summary" not in old_src
        ),
        "hardening_file_was_present": (OLD_DIR / "cosmos_voice_hardening.py").is_file(),
    }
    rec = {
        "schema": "cosmos-f39-voice-fail-old/1",
        "old_service": str(OLD),
        "old_bytes": OLD.stat().st_size,
        "old_has_voice_banner": "# ---------------- voice hardening constants" in old_src,
        "old_defines_bootup": "def _bootup_summary" in old_src,
        "live_hard_exists": live_hard.is_file(),
        "live_hard_bytes": live_hard.stat().st_size if live_hard.is_file() else 0,
        "pins": pins,
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
