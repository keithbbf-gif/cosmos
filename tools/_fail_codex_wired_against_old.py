#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the codex-cli wiring pins FAIL against the staged predecessor.

Loads `_delme/predispose_codex_wired_20260831T171411Z/cosmos_rails_prober.py`
by path. Writes `cosmos/_fail_codex_wired_against_old.json`.
all_new_pins_failed is the bite — required before belief.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_codex_wired_20260831T171411Z"
OLD_PROBER = OLD_DIR / "cosmos_rails_prober.py"
OUT = REPO / "cosmos" / "_fail_codex_wired_against_old.json"


def _wired_ids(src: str) -> list[str]:
    start = src.find("WIRED_NODES = (")
    end = src.find("\nCLI_RAILS = (", start)
    block = src[start:end] if start >= 0 and end > start else ""
    ids = []
    marker = '"link_id": "'
    i = 0
    while True:
        j = block.find(marker, i)
        if j < 0:
            break
        k = block.find('"', j + len(marker))
        ids.append(block[j + len(marker):k])
        i = k + 1
    return ids


def main() -> int:
    src = OLD_PROBER.read_text(encoding="utf-8")
    wired = _wired_ids(src)
    sat_start = src.find("SATELLITES = {")
    sat_end = src.find("\n\ndef probe_module_for", sat_start)
    sat_block = src[sat_start:sat_end] if sat_start >= 0 and sat_end > sat_start else ""
    pins = {
        "codex_cli_in_wired_nodes": "codex-cli" in wired,
        "codex_live_call_defined": "def _codex_live_call(" in src,
        "codex_in_satellites": '"codex":' in sat_block or "'codex':" in sat_block,
        "codex_hands_branch": 'sat == "codex"' in src or "sat == 'codex'" in src,
        "codex_satellite_row": (
            '"link_id": "codex-cli"' in src and '"satellite": "codex"' in src),
    }
    rec = {
        "schema": "cosmos-codex-wired-fail-old/1",
        "old_dir": str(OLD_DIR),
        "old_prober_bytes": OLD_PROBER.stat().st_size,
        "old_wired": wired,
        "old_wired_count": len(wired),
        "pins": pins,
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
