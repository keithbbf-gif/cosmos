#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_watchdog2_scan -- PHASE 4 scanners seam.

Moved out of tests/test_watchdog2.py with the module (docs/CORE_RESTRUCTURE.md):
a split does not land without its tests moving with it. test_watchdog2.py keeps
the 15s scan_once / drop / PAUSE coverage and still imports the names off
cosmos_watchdog2 (re-exports must stay identical objects).

F-29 lesson: a location/shape change that keeps boot green can still break
CALLERS. This suite pins:
  * cosmos_watchdog2 re-exports the SAME objects (test_askmine's
    parse_md_checkboxes import; test_competency's pick_agent import)
  * cosmos_watchdog2.py no longer defines the moved functions
  * the derivation-audit site for dhx_haystack followed the move
  * scan_once (the daemon caller) still flags a novel wish through the
    re-exported parser -- not just that the parser exists

Bite: cosmos/_fail_f39_against_old.py against
_delme/predispose_watchdog2_f39_20260831T153706Z/ (all_new_pins_failed).

    py -3.14 tests/test_watchdog2_scan.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

import cosmos_watchdog2  # noqa: E402
import cosmos_watchdog2_scan  # noqa: E402
from cosmos_watchdog2 import (  # noqa: E402
    MD_ROUTE_SOURCES, Watchdog2, parse_md_checkboxes, parse_backlog,
    pick_agent, scan_once, wishlist_task,
)
from cosmos_watchdog2_scan import (  # noqa: E402
    dhx_haystack, parse_md_checkboxes as scan_parse,
    pick_agent as scan_pick, checkbox_skip_reason,
)
from cosmos_kernel import install  # noqa: E402
from cosmos_motif_driver import motif_token  # noqa: E402

RESULTS = []

REEXPORTED = (
    "MD_ROUTE_SOURCES", "CHECK_RE", "SELF_SLUGS",
    "parse_md_checkboxes", "parse_backlog", "dhx_haystack",
    "cursor_key_exists", "pick_agent", "name_hit", "_tracked_hit",
    "checkbox_skip_reason", "backlog_skip_reason",
    "backlog_task", "wishlist_task", "route_drop_spec",
    "annotate_checkbox", "annotate_backlog",
    "update_source_tick", "update_backlog_tick",
    "_fold", "_backlog_slug", "_clip",
    "CURSOR_KEY_NAME", "CURSOR_LOAD_OVERFLOW",
)

WISHLIST = """# WISHLIST

## Open wishes

- [ ] **cDeck** — full KDash parity + beyond
- [ ] **AUTO-RESESSION** — continue across the context boundary
- [ ] **Brand-new wish alpha** — never tracked anywhere
- [x] **Already shipped wish** — checked off
- [ ] **Cursor key probe** — mentions cursor so pick_agent might vary

## Standing direction
- [ ] **Must not parse** — wrong section, not a route item
"""

BACKLOG = """# BACKLOG

## Open
- [ ] **AUTO-RESESSION** — continue across the context boundary
- [ ] **Unique backlog only** — not on the wishlist
- [x] **PAUSE protocol** — DONE.

## Owed — LIVE CORE (Keith's call; not fire-and-forget)
- [ ] `cosmos.py serve` not up on real root.
"""

TRACKER = """# MOTIF TRACKER

| deliverable | current stage (HONEST) | artifact | next stage |
|---|---|---|---|
| **cDeck** | 4 code — UNVETTED | builds/cdeck | 5 critique |
| **runtime binding — ALL** | 0 | — | nothing has passed stage 6 |
"""

DHX = """# DHx

## Assignment log — APPEND-ONLY markers
- 2026-08-25T20:39:00-05:00 · G46 · cDeck build to KDash-parity · root/g46_cdeck_build3

## Active assignments
- live
"""


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _seam_rows() -> None:
    wd2_src = (REPO / "cosmos" / "cosmos_watchdog2.py").read_text(encoding="utf-8")
    scan_src = (REPO / "cosmos" / "cosmos_watchdog2_scan.py").read_text(
        encoding="utf-8")
    audit_src = (REPO / "cosmos" / "cosmos_derivation_audit.py").read_text(
        encoding="utf-8")
    for name in REEXPORTED:
        check(
            f"cosmos_watchdog2 still exports {name} (same object)",
            (lambda n=name: getattr(cosmos_watchdog2, n)
             is getattr(cosmos_watchdog2_scan, n)),
        )
    check("watchdog2 source no longer defines parse_md_checkboxes",
          lambda: "def parse_md_checkboxes" not in wd2_src)
    check("watchdog2 source no longer defines pick_agent",
          lambda: "def pick_agent" not in wd2_src)
    check("watchdog2 source no longer defines dhx_haystack",
          lambda: "def dhx_haystack" not in wd2_src)
    check("scan module defines parse_md_checkboxes",
          lambda: "def parse_md_checkboxes" in scan_src)
    check("watchdog2 re-exports via cosmos_watchdog2_scan import",
          lambda: "from cosmos_watchdog2_scan import" in wd2_src)
    check("derivation-audit haystack site followed the move",
          lambda: '"file": "cosmos_watchdog2_scan.py"' in audit_src
          and "wd2_dhx_haystack" in audit_src
          and "def dhx_haystack" in scan_src)
    # F-29 caller pins: the exact import lines other suites use.
    check("test_askmine import line still resolves (same parse_md_checkboxes)",
          lambda: __import__(
              "cosmos_watchdog2", fromlist=["parse_md_checkboxes"]
          ).parse_md_checkboxes is scan_parse)
    check("test_competency import line still resolves (same pick_agent)",
          lambda: __import__(
              "cosmos_watchdog2", fromlist=["pick_agent"]
          ).pick_agent is scan_pick)
    check("scan_once still lives on the daemon module (not moved)",
          lambda: "def scan_once" in wd2_src
          and "def scan_once" not in scan_src)


def _parser_rows() -> None:
    items = parse_md_checkboxes(WISHLIST, "wishlist", section="Open wishes")
    slugs = [i["slug"] for i in items]
    check("Open wishes parses five checkbox lines", lambda: len(items) == 5)
    check("standing-direction checkbox is excluded",
          lambda: "must_not_parse" not in slugs)
    check("cDeck wish slug", lambda: slugs[0] == "cdeck")
    check("checked wish is marked checked",
          lambda: any(i["checked"] and "shipped" in i["slug"] for i in items))
    bl = parse_backlog(BACKLOG)
    check("parse_backlog still returns all BACKLOG sections",
          lambda: len(bl) == 4
          and any(i["keith_section"] for i in bl)
          and sum(1 for i in bl if i["checked"]) == 1)
    skip_checked = checkbox_skip_reason(
        next(i for i in items if i["checked"]), set(), "", {}, "")
    check("checked wish skip reason is checked",
          lambda: skip_checked == "checked")
    hay = dhx_haystack(DHX)
    check("dhx_haystack folds assignment-log lines, not other headings",
          lambda: "cdeckbuild" in hay and "assignmentlog" not in hay)
    dhx_only = {"slug": "probe_kdashparity", "title": "KDashparity extra work",
                "body": "", "checked": False, "keith_section": False}
    dhx_skip = checkbox_skip_reason(dhx_only, set(), hay, {}, "")
    check("DHx prose cannot decide a skip (name_hit ignores dhx_fold)",
          lambda: dhx_skip is None)
    novel = next(i for i in items if "alpha" in i["slug"])
    task = wishlist_task(novel)
    tok = motif_token(novel["slug"], 1)
    check("wishlist_task is MOTIF stage-1 research",
          lambda: "STAGE-1 research" in task and tok in task
          and "WISHLIST.md" in task
          and "docs/research/" in task)
    names = [s["name"] for s in MD_ROUTE_SOURCES]
    check("MD_ROUTE_SOURCES lists wishlist, backlog, askmine",
          lambda: names == ["wishlist", "backlog", "askmine"])
    agent, kind = pick_agent(
        {"title": "web research", "body": "look it up"}, {}, False)
    check("pick_agent web-research still callable via re-export",
          lambda: isinstance(agent, str) and isinstance(kind, str)
          and len(agent) >= 2)


def _caller_scan_once() -> None:
    """The daemon caller, not just the parser. F-29 shape pin."""
    td = Path(tempfile.mkdtemp(prefix="cosmos_wd2_scan_seam_"))
    live = install(td / "live", tree_id="f39-wd2-scan")
    repo = td / "repo"
    _write(repo / "docs" / "MOTIF_TRACKER.md", TRACKER)
    _write(repo / "docs" / "BACKLOG.md", BACKLOG)
    _write(repo / "docs" / "WISHLIST.md", WISHLIST)
    _write(repo / "docs" / "AGENT_BRIEF.md", DHX)
    _write(repo / "docs" / "ORCHESTRATION.md",
           "# ORCHESTRATION\n\n## Clock cadence rubric\n")
    queue = live / "queue"
    for lane in (queue, queue / "_lanes" / "lg", queue / "_lanes" / "pb"):
        lane.mkdir(parents=True, exist_ok=True)
        (lane / "running").mkdir(parents=True, exist_ok=True)
        (lane / "done").mkdir(parents=True, exist_ok=True)
    wd = Watchdog2(str(live), queue=queue)
    wd.repo = repo
    wd.backlog = repo / "docs" / "BACKLOG.md"
    wd.wishlist = repo / "docs" / "WISHLIST.md"
    wd.tracker = repo / "docs" / "MOTIF_TRACKER.md"
    wd.dhx = repo / "docs" / "AGENT_BRIEF.md"
    wd.askmine = wd.paths.state("askmine") / "UNANSWERED.md"
    wd.sources = {"backlog": wd.backlog, "wishlist": wd.wishlist,
                  "askmine": wd.askmine}
    dry = scan_once(wd, dry_run=True)
    flagged_src = {(f.get("source"), f.get("slug"))
                   for f in dry.get("flagged", [])}
    check("scan_once (daemon caller) still flags a novel wishlist wish",
          lambda: ("wishlist", "brand_new_wish_alpha") in flagged_src)
    check("scan_once heartbeat still lists md_sources from the scan table",
          lambda: dry.get("md_sources") == ["wishlist", "backlog", "askmine"]
          or (dry.get("heartbeat") or {}).get("md_sources")
          == ["wishlist", "backlog", "askmine"])


def main() -> int:
    _seam_rows()
    _parser_rows()
    _caller_scan_once()
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print("live_value: " + json.dumps({
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "reexported": len(REEXPORTED),
        "parse_same": cosmos_watchdog2.parse_md_checkboxes is scan_parse,
        "pick_same": cosmos_watchdog2.pick_agent is scan_pick,
        "wd2_lines": (REPO / "cosmos" / "cosmos_watchdog2.py").read_text(
            encoding="utf-8").count("\n") + 1,
        "scan_lines": (REPO / "cosmos" / "cosmos_watchdog2_scan.py").read_text(
            encoding="utf-8").count("\n") + 1,
    }, sort_keys=True))
    print(("PASS" if not bad else "FAIL") +
          f" {len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
