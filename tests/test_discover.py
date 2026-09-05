#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: COSMOS mesh-hands discovery projection + heartbeat.

Isolated from the live COSMOS root. Does not register schtasks. Proves: bind
uses the resolver; poll_once writes heartbeat + hands.json; *_HANDS.md files
are inventoried; schtasks plan is HOURLY and points at cosmos_discover.py.
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import install
from cosmos_discover import (
    HEARTBEAT_NAME, TASK_NAME, bind, heartbeat_age_s, inventory_hands,
    plan_once_argv, plan_task_argv, poll_once,
)

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_discover_"))
    root = install(td / "live", tree_id="spike-discover")
    research = td / "research"
    research.mkdir(parents=True, exist_ok=True)
    (research / "OLLAMA_HANDS.md").write_text("# OLLAMA HANDS\nprobe\n", encoding="utf-8")
    (research / "nested" / "XAI_GROK_HANDS.md").parent.mkdir(parents=True, exist_ok=True)
    (research / "nested" / "XAI_GROK_HANDS.md").write_text("# XAI\n", encoding="utf-8")
    (research / "RESEARCH_1.md").write_text("not a hands file\n", encoding="utf-8")

    b = bind(str(root), research=research)
    check("bind: heartbeat path is logs/mesh_discovery_heartbeat.json",
          lambda: b["heartbeat"] == root / "logs" / HEARTBEAT_NAME)
    check("bind: projection is under THIS root state/discovery",
          lambda: b["projection"] == root / "state" / "discovery" / "hands.json")

    hands = inventory_hands(research)
    check("inventory: two *_HANDS.md files", lambda: len(hands) == 2)
    check("inventory: maker names from filename",
          lambda: {h["maker"] for h in hands} == {"OLLAMA", "XAI_GROK"})
    check("inventory: ignores RESEARCH_1.md",
          lambda: all("RESEARCH_1" not in h["path"] for h in hands))

    t0 = int(time.time())
    got = poll_once(str(root), research=research)
    rec = json.loads(b["heartbeat"].read_text(encoding="utf-8"))
    proj = json.loads(b["projection"].read_text(encoding="utf-8"))
    check("poll_once: heartbeat file exists", lambda: b["heartbeat"].exists())
    check("poll_once: last_run_epoch is an int near now",
          lambda: isinstance(rec["last_run_epoch"], int)
          and abs(rec["last_run_epoch"] - t0) < 10)
    check("poll_once: worker is cosmos-discover",
          lambda: rec["worker"] == "cosmos-discover")
    check("poll_once: hands_md_count == 2",
          lambda: rec.get("hands_md_count") == 2)
    check("heartbeat_age_s: fresh after poll",
          lambda: heartbeat_age_s(rec) is not None and heartbeat_age_s(rec) < 5)
    check("projection: schema cosmos-discover/1",
          lambda: proj.get("schema") == "cosmos-discover/1")
    check("projection: py probe present (this process)",
          lambda: any(x.get("id") == "py" and x.get("present") for x in proj["probes"]))
    check("got: heartbeat path returned",
          lambda: got["path"] == str(b["heartbeat"]))

    once_argv = plan_once_argv(str(root))
    task_argv = plan_task_argv(str(root))
    check("plan_once_argv: py -3.14 cosmos_discover.py --once + this root",
          lambda: once_argv[0] == "py" and "-3.14" in once_argv
          and "--once" in once_argv
          and str(root.resolve()) in once_argv
          and "cosmos_discover.py" in once_argv[2])
    check("plan_task_argv: schtasks /create /tn COSMOS Mesh Discovery /sc HOURLY",
          lambda: task_argv[0] == "schtasks" and task_argv[1] == "/create"
          and TASK_NAME in task_argv and "HOURLY" in task_argv)
    check("plan_task_argv: /tr points at cosmos_discover.py --once",
          lambda: "cosmos_discover.py" in task_argv[task_argv.index("/tr") + 1]
          and "--once" in task_argv[task_argv.index("/tr") + 1])
    check("plan_task_argv: no /rl highest (current-user registration)",
          lambda: "/rl" not in task_argv)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    return 1 if bad else 0


def test_discover():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
