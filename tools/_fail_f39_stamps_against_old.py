#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-39 DHx/stamps/index-split pins FAIL against the staged predecessor.

Loads `_delme/predispose_dispatch_f39_stamps_20260831T182020Z/cosmos_dispatch.py`
as source so the new pins are measured against the unsplit module. Writes
`cosmos/_fail_f39_stamps_against_old.json`. all_new_pins_failed is the bite.

Does not import the old module as cosmos_dispatch (would shadow live).
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_dispatch_f39_stamps_20260831T182020Z"
OLD = OLD_DIR / "cosmos_dispatch.py"
OUT = REPO / "cosmos" / "_fail_f39_stamps_against_old.json"


def main() -> int:
    if not OLD.is_file():
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "old": str(OLD)}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    old_src = OLD.read_text(encoding="utf-8")
    live_mod = REPO / "cosmos" / "cosmos_dispatch_stamps.py"
    pins = {
        "stamps_module_imported": "cosmos_dispatch_stamps" in old_src,
        "iso_now_moved_out": "def _iso_now" not in old_src,
        "marker_line_moved_out": "def _marker_line" not in old_src,
        "append_dhx_moved_out": "def append_dhx_marker" not in old_src,
        "append_index_moved_out": "def append_index_row" not in old_src,
        "write_inbox_moved_out": "def write_inbox_sidecar" not in old_src,
        "compose_prompt_moved_out": "def compose_agent_prompt" not in old_src,
        "banner_is_reexport_only": (
            "live in cosmos_dispatch_stamps" in old_src
            and "from cosmos_dispatch_stamps import" in old_src
            and "def append_dhx_marker" not in old_src
        ),
        "stamps_file_was_present": (
            OLD_DIR / "cosmos_dispatch_stamps.py").is_file(),
    }
    rec = {
        "schema": "cosmos-f39-stamps-fail-old/1",
        "old_dispatch": str(OLD),
        "old_bytes": OLD.stat().st_size,
        "old_lines": old_src.count("\n") + 1,
        "old_has_stamps_banner": "# stamps, DHx, collector index" in old_src,
        "old_defines_append_dhx": "def append_dhx_marker" in old_src,
        "live_stamps_exists": live_mod.is_file(),
        "live_stamps_bytes": live_mod.stat().st_size if live_mod.is_file() else 0,
        "pins": pins,
        "failed_pin_count": sum(1 for v in pins.values() if v is False),
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
