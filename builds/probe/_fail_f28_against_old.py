#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the new F-28 pins FAIL against the staged incumbent COMPETENCY.toml.

Required before belief: all_new_pins_failed == true.

    py -3.14 builds/probe/_fail_f28_against_old.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
from cosmos_newai_scout import (  # noqa: E402
    inventory_from_competency, inventory_from_hands, norm,
)

STAGE = (REPO / "docs" / "_delme" /
         "predispose_competency_f28_20260831T145400Z" / "COMPETENCY.toml")
OUT = HERE / "_fail_f28_against_old.json"
FILED = (
    "Aider", "Anthropic", "BrowserUse", "Firecrawl", "GCloud",
    "GitHub", "GitLab", "GoogleGemini", "Groq", "MCPReferenceServers",
    "MicrosoftCopilot", "Ollama", "OpenAI", "PlaywrightMCP", "XaiGrok",
)
REQUIRED_SIX = {"G46", "GEM", "OA", "SGH", "Cursor", "DOM"}


def _census(text: str) -> dict:
    nodes = sorted(inventory_from_competency(text))
    hands = sorted(inventory_from_hands(REPO))
    node_keys = {norm(n) for n in nodes}
    seen = set()
    unmapped = []
    for h in hands:
        k = norm(h)
        if k in seen or k in node_keys:
            continue
        seen.add(k)
        unmapped.append(h)
    return {"nodes": nodes, "unmapped_count": len(unmapped),
            "unmapped": unmapped}


def main() -> int:
    text = STAGE.read_text(encoding="utf-8")
    rec = _census(text)
    pins = {
        "unmapped_is_zero": rec["unmapped_count"] == 0,
        "node_count_is_21": len(rec["nodes"]) == 21,
        "filed_ids_present": set(FILED) <= set(rec["nodes"]),
        "pin_would_not_break": False,  # old census hard-coded True; see below
    }
    # The old census file claimed the exact-set pin would break. The
    # staged toml still has exactly six nodes, so the SUPERSET pin
    # (required_six <= live_nodes) PASSES on old — that pin is not the
    # discriminating one. Discriminating pins are the three above.
    rec["pins"] = pins
    rec["all_new_pins_failed"] = (
        pins["unmapped_is_zero"] is False
        and pins["node_count_is_21"] is False
        and pins["filed_ids_present"] is False
        and rec["unmapped_count"] == 15
        and set(rec["nodes"]) == REQUIRED_SIX
    )
    rec["staged"] = str(STAGE)
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_new_pins_failed": rec["all_new_pins_failed"],
        "unmapped_count": rec["unmapped_count"],
        "node_count": len(rec["nodes"]),
        "pins": pins,
    }, indent=2))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
