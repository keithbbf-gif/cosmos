#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-39 stage-5-critique-split pins FAIL against the staged predecessor.

Loads `_delme/predispose_dispatch_f39_critique_20260831T1802Z/cosmos_dispatch.py`
as source so the new pins are measured against the unsplit module. Writes
`cosmos/_fail_f39_critique_against_old.json`. all_new_pins_failed is the bite.

Does not import the old module as cosmos_dispatch (would shadow live).
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_dispatch_f39_critique_20260831T1802Z"
OLD = OLD_DIR / "cosmos_dispatch.py"
OUT = REPO / "cosmos" / "_fail_f39_critique_against_old.json"


def main() -> int:
    if not OLD.is_file():
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "old": str(OLD)}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    old_src = OLD.read_text(encoding="utf-8")
    live_mod = REPO / "cosmos" / "cosmos_dispatch_critique.py"
    pins = {
        "critique_module_imported": "cosmos_dispatch_critique" in old_src,
        "compose_moved_out": "def compose_critique_prompt" not in old_src,
        "is_critique_moved_out": "def _is_critique_task" not in old_src,
        "inline_file_moved_out": "def _inline_file" not in old_src,
        "format_inlined_moved_out": "def _format_inlined" not in old_src,
        "locate_artifact_moved_out": "def _locate_artifact" not in old_src,
        "path_tokens_moved_out": "def _path_tokens" not in old_src,
        "banner_is_reexport_only": (
            "live in cosmos_dispatch_critique" in old_src
            and "from cosmos_dispatch_critique import" in old_src
            and "def compose_critique_prompt" not in old_src
        ),
        "critique_file_was_present": (
            OLD_DIR / "cosmos_dispatch_critique.py").is_file(),
    }
    rec = {
        "schema": "cosmos-f39-critique-fail-old/1",
        "old_dispatch": str(OLD),
        "old_bytes": OLD.stat().st_size,
        "old_lines": old_src.count("\n") + 1,
        "old_has_critique_banner": "# stage-5 critic visibility" in old_src,
        "old_defines_compose": "def compose_critique_prompt" in old_src,
        "live_critique_exists": live_mod.is_file(),
        "live_critique_bytes": live_mod.stat().st_size if live_mod.is_file() else 0,
        "pins": pins,
        "failed_pin_count": sum(1 for v in pins.values() if v is False),
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
