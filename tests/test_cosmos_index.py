#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: COSMOS living index (tools / features / implemented).

Isolated from the live root. Proves: tracker rows not past the Motif gate
land in building; stage-6 PASSED rows do not; WISHLIST + BACKLOG land as
features; live lists only heartbeat/gate/pause-bound
items; cosmos/*.py module count is a true scan; dispositions and
state/*_result.json landings are ingested; dest is state/cosmos_index.json
(never authority) plus a KDash panel fragment; collector poll_once with a
non-default summary_md does not rewrite the index.
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
from cosmos_collector import Collector
from cosmos_index import (
    CLOCK_ID, HEARTBEAT_NAME, INDEX_NAME, PANEL_NAME, PROJECTION_NAME,
    SCHEMA, TASK_NAME, gather, parse_backlog, parse_dispositions,
    parse_tracker, parse_wishlist, plan_task_argv, rebuild, scan_landings,
    scan_modules,
)

RESULTS = []

TRACKER = """# MOTIF TRACKER

<!-- cow-disposition 2026-08-27T02:57:00-0500 -->
## Disposition — COW check-in 2026-08-27T02:57
- **Typed WORK-ORDER system** applied.
- **Critique consumer** on tree, not yet running.
<!-- /cow-disposition -->

| deliverable | current stage (HONEST) | artifact | next stage |
|---|---|---|---|
| **cDeck** | 4 code — UNVETTED | builds/cdeck | 5 critique |
| **collector** | 6 runtime-binding gate PASSED | cosmos/cosmos_collector.py | done |
| **runtime binding — ALL** | 0 | — | nothing has passed stage 6 |
"""

BACKLOG = """# BACKLOG

- [ ] **Spend control** — more granularity than KDash (assigned → cDeck)
- [ ] **Watchdog2** — constant no-idle scanner (being built by G46).
- [x] **PAUSE protocol** — DONE. `docs/PAUSE_PROTOCOL.md`
- [ ] **COSMOS_INDEX** — the single living index.
- [~] **Stage-5 critiques** — in flight.
"""

WISHLIST = """# WISHLIST

## Open wishes
- [ ] **cDeck** — full KDash parity
- [ ] **COSMOS_INDEX** — the single living index
- [x] **PAUSE protocol** — already canon
- [ ] **AUTO-RESESSION** — continue across the context boundary
"""

DHX = """# DHx

## Assignment log — APPEND-ONLY markers
- 2026-08-25T20:39:00-05:00 · G46 · cDeck build to KDash-parity+ · root/g46_cdeck_build3
- 2026-08-25T21:00:00-05:00 · G46 · build permanent results-collector daemon · root/cosmos_build_collector

## Active assignments
- live
"""

FEATURES = """# cDeck — feature requirements

## Required features
- **Spend control** — per-rail budgets, caps, thresholds.
- **Jukebox** — the job/queue control surface.
- **Node map** — movable / draggable nodes.
"""


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _setup():
    td = Path(tempfile.mkdtemp(prefix="cosmos_index_"))
    repo = td / "repo"
    root = install(td / "live", tree_id="spike-index")
    _write(repo / "docs" / "MOTIF_TRACKER.md", TRACKER)
    _write(repo / "docs" / "BACKLOG.md", BACKLOG)
    _write(repo / "docs" / "WISHLIST.md", WISHLIST)
    _write(repo / "docs" / "AGENT_BRIEF.md", DHX)
    _write(repo / "builds" / "cdeck" / "FEATURES_KEITH.md", FEATURES)
    (repo / "builds" / "cdeck").mkdir(parents=True, exist_ok=True)
    _write(repo / "builds" / "cdeck" / "README.md", "# cDeck\n")
    _write(repo / "cosmos" / "cosmos_collector.py",
           '#!/usr/bin/env python3\n"""cosmos_collector - results daemon."""\n')
    _write(repo / "cosmos" / "cosmos_alpha.py",
           '#!/usr/bin/env python3\n"""cosmos_alpha - spike module."""\nCLOCK_ID = 13\n')
    _write(repo / "cosmos" / "cosmos_beta.py",
           '"""cosmos_beta - second spike."""\n')
    logs = root / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    now = int(time.time())
    for name, worker in (
        ("cosmos_runner_heartbeat.json", "cosmos-runner"),
        ("collector_heartbeat.json", "cosmos-collector"),
        ("mesh_discovery_heartbeat.json", "cosmos-discover"),
    ):
        _write(logs / name, json.dumps({
            "last_run": "2026-08-25T22:54:00-05:00",
            "last_run_epoch": now,
            "worker": worker,
            "pid": 1000,
            "polls": 3,
            "tick": "idle",
            "interval_s": 30.0,
        }))
    _write(root / "state" / "land_alpha_result.json", json.dumps({
        "job": "land_alpha", "rc": 0, "ok": True, "ts": "2026-08-27T06:00:00-05:00",
        "summary": "py_compile rc=0",
    }))
    _write(root / "state" / "land_beta_result.json", json.dumps({
        "job": "land_beta", "rc": 2, "ok": False, "status": "failed",
    }))
    flag = root / "state" / "control" / "PAUSE.flag"
    _write(flag, json.dumps({
        "state": "PAUSED", "mode": "hold", "reason": "test",
        "set_at": "2026-08-25T22:47-05",
    }))
    return td, repo, root


def main() -> int:
    check("CLOCK_ID is reserved 13", lambda: CLOCK_ID == 13)
    check("schema is cosmos-index/2", lambda: SCHEMA == "cosmos-index/2")
    check("projection name is cosmos_index.json",
          lambda: PROJECTION_NAME == INDEX_NAME == "cosmos_index.json")

    check("parse_tracker: two data rows + runtimeall",
          lambda: len(parse_tracker(TRACKER)) == 3)
    check("parse_tracker: cDeck not past gate",
          lambda: not parse_tracker(TRACKER)[0]["past_gate"])
    check("parse_tracker: collector IS past gate",
          lambda: parse_tracker(TRACKER)[1]["past_gate"])
    check("parse_backlog: five items, one checked, one wip",
          lambda: len(parse_backlog(BACKLOG)) == 5
          and sum(1 for x in parse_backlog(BACKLOG) if x["checked"]) == 1
          and sum(1 for x in parse_backlog(BACKLOG) if x["wip"]) == 1)
    check("parse_wishlist: four items, one checked",
          lambda: len(parse_wishlist(WISHLIST)) == 4
          and sum(1 for x in parse_wishlist(WISHLIST) if x["checked"]) == 1)
    check("parse_dispositions: one COW block",
          lambda: len(parse_dispositions(TRACKER)) == 1
          and parse_dispositions(TRACKER)[0]["stamp"].startswith("2026-08-27"))

    td, repo, root = _setup()
    mods = scan_modules(repo)
    check("scan_modules: three cosmos/*.py",
          lambda: len(mods) == 3
          and {m["file"] for m in mods}
          == {"cosmos_collector.py", "cosmos_alpha.py", "cosmos_beta.py"})
    check("scan_modules: alpha carries CLOCK_ID 13",
          lambda: any(m["file"] == "cosmos_alpha.py" and m["clock_id"] == 13
                      for m in mods))
    lands = scan_landings(root / "state")
    check("scan_landings: two *_result.json",
          lambda: len(lands) == 2
          and {x["file"] for x in lands}
          == {"land_alpha_result.json", "land_beta_result.json"})

    r = rebuild(str(root), repo=repo)
    dest = Path(r["dest"])
    panel = Path(r["panel"])
    md_docs = repo / "docs" / "COSMOS_INDEX.md"
    proj = json.loads(dest.read_text(encoding="utf-8"))
    html = panel.read_text(encoding="utf-8")
    bundle = r["bundle"]

    check("rebuild ok", lambda: r.get("ok") is True)
    check("dest is state/cosmos_index.json",
          lambda: dest == root / "state" / PROJECTION_NAME and dest.exists())
    check("rebuild wrote heartbeat",
          lambda: (root / "logs" / HEARTBEAT_NAME).exists())
    check("rebuild wrote KDash panel fragment",
          lambda: panel == root / "state" / PANEL_NAME and panel.exists()
          and 'id="panel-index"' in html)
    check("does NOT write docs/COSMOS_INDEX.md (git-tracked cache gone)",
          lambda: not md_docs.exists())
    check("projection authority is false",
          lambda: proj.get("authority") is False)
    check("projection clock_id is 13",
          lambda: proj.get("clock_id") == 13)
    check("counts.modules is the true scan (3)",
          lambda: proj["counts"]["modules"] == 3 == r["module_count"])
    check("section A count is 2 (cDeck + runtimeall, not collector)",
          lambda: r["section_a"] == 2)
    check("section A names exclude collector",
          lambda: {x["name"] for x in bundle["building"]}
          == {"cDeck", "runtime binding — ALL"})
    check("section C includes collector as gate",
          lambda: any(x["item"] == "collector" and x["kind"] == "gate"
                      for x in bundle["live"]))
    check("A table has cDeck builder G46",
          lambda: any(x["name"] == "cDeck" and x["builder"] == "G46"
                      for x in bundle["building"]))
    check("B has Spend control from BACKLOG",
          lambda: any(x["feature"] == "Spend control"
                      and x["source"] == "docs/BACKLOG.md"
                      for x in bundle["features"]))
    check("B Spend control is in-build (cDeck still in A)",
          lambda: any(x["feature"] == "Spend control" and x["status"] == "in-build"
                      for x in bundle["features"]))
    check("B open Watchdog2 is not shipped",
          lambda: any(x["feature"] == "Watchdog2" and x["status"] != "shipped"
                      for x in bundle["features"]))
    check("B PAUSE protocol is shipped (flag bound)",
          lambda: any(x["feature"] == "PAUSE protocol" and x["status"] == "shipped"
                      for x in bundle["features"]))
    check("B includes WISHLIST AUTO-RESESSION as requested",
          lambda: any(x["feature"] == "AUTO-RESESSION"
                      and x["source"] == "docs/WISHLIST.md"
                      and x["status"] == "requested"
                      for x in bundle["features"]))
    check("C lists cosmos_runner with heartbeat mtime",
          lambda: any(x["item"] == "cosmos_runner" and x["kind"] == "daemon"
                      and "file_mtime=" in x["proof"]
                      and "last_run=" in x["proof"]
                      for x in bundle["live"]))
    check("C lists collector daemon",
          lambda: any(x["item"] == "collector" and x["kind"] == "daemon"
                      for x in bundle["live"]))
    check("C lists mesh_discovery daemon",
          lambda: any(x["item"] == "mesh_discovery" and x["kind"] == "daemon"
                      for x in bundle["live"]))
    check("C lists PAUSE protocol bound to flag",
          lambda: any(x["item"] == "PAUSE protocol" and x["kind"] == "protocol"
                      and "PAUSE.flag" in x["proof"]
                      for x in bundle["live"]))
    check("C does not list cDeck as implemented",
          lambda: not any(x["item"] == "cDeck" for x in bundle["live"]))
    check("dispositions landed in projection",
          lambda: len(proj.get("dispositions") or []) == 1)
    check("landings landed in projection",
          lambda: {x["file"] for x in proj.get("landings") or []}
          == {"land_alpha_result.json", "land_beta_result.json"})
    check("panel fragment has modules table and clock id",
          lambda: "MODULES cosmos/*.py" in html and "clock_id=13" in html)
    check("plan_task_argv is COSMOS Index every 1 minute --once",
          lambda: (lambda argv: argv[0] == "schtasks" and TASK_NAME in argv
                   and "minute" in argv and "--once" in argv[argv.index("/tr") + 1])
          (plan_task_argv(str(root))))

    r2 = rebuild(str(root), repo=repo)
    check("idempotent: second rebuild same module_count",
          lambda: r2["module_count"] == r["module_count"] == 3)
    check("idempotent: dest replaced not appended",
          lambda: Path(r2["dest"]).is_file() and Path(r2["dest"]).stat().st_size > 200)

    queue = td / "queue"
    queue.mkdir(exist_ok=True)
    summary = td / "docs" / "COLLECTOR.md"
    dest_mtime = dest.stat().st_mtime
    coll = Collector(str(root), queue=queue, research=td / "research",
                     summary_md=summary, interval_s=30.0)
    extra = coll.poll_once()
    check("collector skip: index_refresh skipped on non-default summary",
          lambda: extra.get("index_refresh", {}).get("skipped") is True)
    check("collector skip: dest mtime unchanged",
          lambda: dest.stat().st_mtime == dest_mtime)

    g = gather(str(root), repo=repo)
    check("gather heartbeats includes the three required daemons",
          lambda: {h["name"] for h in g["heartbeats"] if h.get("exists")}
          >= {"cosmos_runner", "collector", "mesh_discovery"})
    check("gather wishlist_open is 3",
          lambda: sum(1 for w in g["wishlist"] if not w["checked"]) == 3)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    return 1 if bad else 0


def test_cosmos_index():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
