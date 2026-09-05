#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_f28_competency_map — F-28 HANDS stems are [nodes.*] rows.

The 15 unmapped stems are filed as possessed=false rating=0 with a
HANDS-cited source. Ratings are not invented. The live six still win
pick(). Bite: staged incumbent had unmapped_count=15.

    py -3.14 builds/probe/test_f28_competency_map.py
"""
from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
# Probe scout FIRST — cosmos/cosmos_newai_scout.py is a different module
# and does not export inventory_from_competency.
sys.path.insert(0, str(HERE))
from cosmos_newai_scout import (  # noqa: E402
    inventory_from_competency, inventory_from_hands, norm,
)
sys.path.insert(0, str(REPO / "cosmos"))
from cosmos_competency import load, pick                              # noqa: E402

TOML = REPO / "docs" / "COMPETENCY.toml"
STAGE = (REPO / "docs" / "_delme" /
         "predispose_competency_f28_20260831T145400Z" / "COMPETENCY.toml")
BITE = HERE / "_bite_f28_unmapped.json"
CENSUS = HERE / "_f28_hands_vs_nodes.json"
REQUIRED_SIX = {"G46", "GEM", "OA", "SGH", "Cursor", "DOM"}
FILED = (
    "Aider", "Anthropic", "BrowserUse", "Firecrawl", "GCloud",
    "GitHub", "GitLab", "GoogleGemini", "Groq", "MCPReferenceServers",
    "MicrosoftCopilot", "Ollama", "OpenAI", "PlaywrightMCP", "XaiGrok",
)
TASK_TYPES = [
    "code-build", "code-review-critique", "web-research", "docs-authoring",
    "DOM-automation", "long-context-reasoning",
    "bulk-structured-extraction", "vendor-plural-critique",
]

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


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
    return {"nodes": nodes, "unmapped": unmapped,
            "unmapped_count": len(unmapped)}


def main() -> int:
    check("staged incumbent exists (never-delete)", STAGE.is_file)
    old_text = STAGE.read_text(encoding="utf-8") if STAGE.is_file() else ""
    old = _census(old_text)
    check("staged incumbent unmapped_count is 15 (the bite)",
          lambda: old["unmapped_count"] == 15)
    check("staged incumbent has exactly the live six",
          lambda: set(old["nodes"]) == REQUIRED_SIX)

    bite = json.loads(BITE.read_text(encoding="utf-8")) if BITE.is_file() else {}
    check("bite artifact records unmapped_count=15 before filing",
          lambda: bite.get("unmapped_count") == 15
          and bite.get("node_count") == 6)

    live_text = TOML.read_text(encoding="utf-8")
    live = _census(live_text)
    check("live unmapped_count is 0 (every HANDS stem has a node)",
          lambda: live["unmapped_count"] == 0)
    check("live node set is a SUPERSET of the required six",
          lambda: REQUIRED_SIX <= set(live["nodes"]))
    check("all 15 filed ids are [nodes.*] rows",
          lambda: set(FILED) <= set(live["nodes"]))
    check("live node_count is 21 (6 + 15)",
          lambda: len(live["nodes"]) == 21)

    data = tomllib.loads(live_text)
    nodes = data.get("nodes") or {}
    skills = data.get("skills") or {}
    order = list((data.get("router") or {}).get("nodes_order") or [])

    def _all_unverified():
        for nid in FILED:
            rec = nodes.get(nid) or {}
            if rec.get("id") != nid:
                return False
            if rec.get("family") == "dom":
                return False  # would steal DOM-automation ties
            for task in TASK_TYPES:
                row = (skills.get(task) or {}).get(nid) or {}
                if row.get("possessed") is True:
                    return False
                try:
                    rating = int(row["rating"])
                except (KeyError, TypeError, ValueError):
                    return False
                if rating != 0:
                    return False
                src = str(row.get("source") or "")
                if "docs/research/" not in src or "_HANDS.md" not in src:
                    return False
                if "possessed=false" not in src:
                    return False
        return True

    check("filed nodes are unverified: possessed=false rating=0 HANDS source",
          _all_unverified)
    check("filed nodes are absent from router.nodes_order (live six stay the set)",
          lambda: not (set(FILED) & set(order))
          and set(order) == {"DOM", "G46", "Cursor", "SGH", "GEM", "OA"})

    matrix = load(TOML)
    live_nodes = set((matrix.get("nodes") or {}).keys())
    check("pick(code-build, all live nodes) is still G46",
          lambda: pick(matrix, "code-build", live_nodes) == "G46")
    check("pick(web-research, all live nodes) is still SGH",
          lambda: pick(matrix, "web-research", live_nodes) == "SGH")
    check("pick(DOM-automation, all live nodes) is still DOM",
          lambda: pick(matrix, "DOM-automation", live_nodes) == "DOM")

    census = json.loads(CENSUS.read_text(encoding="utf-8")) if CENSUS.is_file() else {}
    check("re-measured census artifact unmapped_count=0 node_count=21",
          lambda: census.get("unmapped_count") == 0
          and census.get("node_count") == 21
          and census.get("live_six_nodes_pin_would_break_if_we_add") is False)

    bad = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    evidence = {
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "old_unmapped": old["unmapped_count"],
        "new_unmapped": live["unmapped_count"],
        "new_node_count": len(live["nodes"]),
        "pick": {
            "code-build": "G46",
            "web-research": "SGH",
            "DOM-automation": "DOM",
        },
    }
    print("live_value: " + json.dumps(evidence, sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
