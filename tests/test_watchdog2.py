#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: Watchdog2 markdown route sources (WISHLIST + BACKLOG).

Isolated from the live root and the live queue. Does not register schtasks.
Proves: one checkbox parser; WISHLIST 'Open wishes' only; de-dupe vs
MOTIF_TRACKER + BACKLOG + DHx + inflight; a novel wish enters MOTIF at
stage 1; PAUSE hold drops nothing; resume_gate future stays paused;
runtime-binding fields (source=wishlist, token, wishlist_line, job_file).
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cosmos"))

from cosmos_watchdog2 import (  # noqa: E402
    MD_ROUTE_SOURCES, Watchdog2, _tracked_hit, checkbox_skip_reason,
    motif_token, parse_backlog, parse_md_checkboxes, parse_tracker,
    scan_once, wishlist_task,
)
from cosmos_kernel import install  # noqa: E402

RESULTS = []

TRACKER = """# MOTIF TRACKER

| deliverable | current stage (HONEST) | artifact | next stage |
|---|---|---|---|
| **cDeck** | 4 code — UNVETTED | builds/cdeck | 5 critique |
| **runtime binding — ALL** | 0 | — | nothing has passed stage 6 |
"""

BACKLOG = """# BACKLOG

## Open
- [ ] **AUTO-RESESSION** — continue across the context boundary
- [ ] **Unique backlog only** — not on the wishlist
- [x] **PAUSE protocol** — DONE.

## Owed — LIVE CORE (Keith's call; not fire-and-forget)
- [ ] `cosmos.py serve` not up on real root.
"""

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


def _bind(wd: Watchdog2, repo: Path) -> None:
    wd.repo = repo
    wd.backlog = repo / "docs" / "BACKLOG.md"
    wd.wishlist = repo / "docs" / "WISHLIST.md"
    wd.tracker = repo / "docs" / "MOTIF_TRACKER.md"
    wd.dhx = repo / "docs" / "AGENT_BRIEF.md"
    wd.askmine = wd.paths.state("askmine") / "UNANSWERED.md"
    wd.sources = {"backlog": wd.backlog, "wishlist": wd.wishlist,
                  "askmine": wd.askmine}


def _setup():
    td = Path(tempfile.mkdtemp(prefix="cosmos_wd2_wish_"))
    live = install(td / "live", tree_id="spike-wd2-wishlist")
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
    return td, repo, live, queue


def main() -> int:
    names = [s["name"] for s in MD_ROUTE_SOURCES]
    check("MD_ROUTE_SOURCES lists wishlist, backlog, askmine",
          lambda: names == ["wishlist", "backlog", "askmine"])
    check("askmine source is live/state, section Open, enter implement",
          lambda: MD_ROUTE_SOURCES[2]["loc"] == "state"
          and MD_ROUTE_SOURCES[2]["filename"] == "UNANSWERED.md"
          and MD_ROUTE_SOURCES[2]["section"] == "Open"
          and MD_ROUTE_SOURCES[2]["enter"] == "implement")
    planted = ("# Unanswered asks (askmine)\n\n## Open\n"
               "- [ ] **register_crit_consumer** — Register the "
               "crit_consumer task.\n")
    am_items = parse_md_checkboxes(planted, "askmine", section="Open")
    check("askmine Open checkbox round-trips a slug WD2 would flag",
          lambda: am_items and am_items[0]["slug"] == "register_crit_consumer"
          and am_items[0]["checked"] is False
          and am_items[0]["source"] == "askmine")
    check("wishlist enters motif_s1",
          lambda: MD_ROUTE_SOURCES[0]["enter"] == "motif_s1"
          and MD_ROUTE_SOURCES[0]["section"] == "Open wishes")
    check("backlog enter is implement (unchanged drop recipe)",
          lambda: MD_ROUTE_SOURCES[1]["enter"] == "implement")

    items = parse_md_checkboxes(WISHLIST, "wishlist", section="Open wishes")
    slugs = [i["slug"] for i in items]
    check("Open wishes parses five checkbox lines",
          lambda: len(items) == 5)
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

    rows = parse_tracker(TRACKER)
    tracked = {r["slug"] for r in rows} | {r["name"] for r in rows}
    for it in bl:
        tracked.add(it["slug"])
        tracked.add(it["title"])
    cdeck_wish = next(i for i in items if i["slug"] == "cdeck")
    auto_wish = next(i for i in items if "resession" in i["slug"])
    novel = next(i for i in items if "alpha" in i["slug"])
    check("cDeck wish de-dupes against MOTIF_TRACKER",
          lambda: _tracked_hit(cdeck_wish, tracked) is not None)
    check("AUTO-RESESSION wish de-dupes against BACKLOG",
          lambda: _tracked_hit(auto_wish, tracked) is not None)
    check("novel wish is NOT tracked",
          lambda: _tracked_hit(novel, tracked) is None)

    task = wishlist_task(novel)
    tok = motif_token(novel["slug"], 1)
    check("wishlist_task is MOTIF stage-1 research",
          lambda: "STAGE-1 research" in task and tok in task
          and "WISHLIST.md" in task
          and "docs/research/" in task)

    skip_checked = checkbox_skip_reason(
        next(i for i in items if i["checked"]), set(), "", {}, "")
    check("checked wish skip reason is checked",
          lambda: skip_checked == "checked")

    td, repo, live, queue = _setup()
    wd = Watchdog2(str(live), queue=queue)
    _bind(wd, repo)

    dry = scan_once(wd, dry_run=True)
    flagged_src = {(f.get("source"), f.get("slug")) for f in dry.get("flagged", [])}
    skipped_map = {(s.get("source"), s.get("slug")): s.get("reason")
                   for s in dry.get("skipped_full") or dry.get("skipped_sample") or []}
    # skipped_sample may truncate; prefer skipped_full
    skipped_full = {(s.get("source"), s.get("slug")): s.get("reason")
                    for s in dry.get("skipped_full", [])}

    check("dry_run ok", lambda: dry.get("ok") is True and dry.get("dry_run") is True)
    check("novel wish flagged as wishlist",
          lambda: ("wishlist", novel["slug"]) in flagged_src)
    check("novel wish token is motif s1",
          lambda: any(f.get("source") == "wishlist"
                      and f.get("slug") == novel["slug"]
                      and f.get("token") == tok
                      and f.get("enter") == "motif_s1"
                      and f.get("next_stage") == 1
                      for f in dry.get("assigned", [])))
    check("cDeck wish skipped tracked (not re-dropped)",
          lambda: str(skipped_full.get(("wishlist", "cdeck"), "")).startswith("tracked:"))
    check("AUTO-RESESSION wish skipped tracked",
          lambda: "resession" in "".join(k[1] for k in skipped_full
                                         if k[0] == "wishlist" and "tracked:"
                                         in str(skipped_full[k])))
    check("unique backlog item still flagged (shared helper, not a second scanner)",
          lambda: ("backlog", "unique_backlog_only") in flagged_src)
    check("keith owed backlog not flagged",
          lambda: skipped_full.get(("backlog", _backlog_slug_serve(bl))) == "keith_section"
          or any(s.get("reason") == "keith_section" and s.get("source") == "backlog"
                 for s in dry.get("skipped_full", [])))
    check("heartbeat lists md_sources wishlist+backlog+askmine",
          lambda: (dry.get("heartbeat") or {}).get("md_sources")
          == ["wishlist", "backlog", "askmine"]
          or dry.get("md_sources") == ["wishlist", "backlog", "askmine"])
    check("absent askmine file contributes no route items",
          lambda: not any(f.get("source") == "askmine"
                          for f in (dry.get("flagged") or []))
          and not any(s.get("source") == "askmine"
                      for s in (dry.get("skipped_full") or [])))

    # Real drop of the novel wish into the isolated queue (runtime-binding).
    rec = scan_once(wd, dry_run=False)
    jobs = rec.get("jobs") or []
    wish_jobs = [j for j in jobs if j.get("source") == "wishlist"]
    novel_job = next((j for j in wish_jobs if j.get("slug") == novel["slug"]),
                     None)
    check("live drop assigned >= 1", lambda: rec.get("assigned_this_pass", 0) >= 1)
    check("wishlist job in heartbeat jobs[]", lambda: len(wish_jobs) >= 1)
    check("runtime-binding: source=wishlist",
          lambda: novel_job is not None and novel_job["source"] == "wishlist")
    check("runtime-binding: token motif_*_s1",
          lambda: novel_job is not None and novel_job.get("token") == tok)
    check("runtime-binding: job_file non-empty",
          lambda: novel_job is not None and bool(novel_job.get("job_file")))
    check("runtime-binding: wishlist_line is the verbatim Open-wishes row",
          lambda: novel_job is not None
          and novel_job.get("wishlist_line") == novel["line"]
          and novel_job["wishlist_line"].startswith("- [ ]"))
    job_file = (novel_job.get("job_file") or "") if novel_job else ""
    job_path = None
    for d in rec.get("assigned", []):
        if d.get("source") == "wishlist" and d.get("slug") == novel["slug"] and d.get("job_path"):
            job_path = Path(d["job_path"])
            break
    check("job file exists on isolated queue (not an exit code)",
          lambda: job_path is not None and job_path.is_file())
    check("job task traces to WISHLIST.md line",
          lambda: job_path is not None and "WISHLIST.md" in job_path.read_text(
              encoding="utf-8") and novel["title"] in job_path.read_text(
              encoding="utf-8"))
    wl_txt = (repo / "docs" / "WISHLIST.md").read_text(encoding="utf-8")
    check("WISHLIST line annotated WATCHDOG2 ASSIGNED + job_file",
          lambda: "WATCHDOG2 ASSIGNED" in wl_txt and job_file
          and job_file in wl_txt)
    hb_path = Path(rec["heartbeat_path"])
    hb = json.loads(hb_path.read_text(encoding="utf-8"))
    check("heartbeat artifact carries the wishlist job (gate value)",
          lambda: any(j.get("source") == "wishlist"
                      and j.get("job_file") == job_file
                      and j.get("wishlist_line") == novel["line"]
                      for j in hb.get("jobs", [])))
    check("second pass does not re-drop the novel wish",
          lambda: not any(j.get("source") == "wishlist"
                          and j.get("slug") == novel["slug"]
                          for j in scan_once(wd, dry_run=True).get("jobs", [])))

    # PAUSE hold: drop nothing, heartbeat PAUSED (paused != dead).
    td2, repo2, live2, queue2 = _setup()
    wd2 = Watchdog2(str(live2), queue=queue2)
    _bind(wd2, repo2)
    flag = live2 / "state" / "control" / "PAUSE.flag"
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text(json.dumps({
        "state": "PAUSED", "mode": "hold",
        "reason": "test hold", "set_by": "test_watchdog2",
        "set_at": datetime.now().astimezone().isoformat(),
    }), encoding="utf-8")
    paused = scan_once(wd2, dry_run=False)
    check("PAUSE hold: state PAUSED", lambda: paused.get("state") == "PAUSED")
    check("PAUSE hold: mode hold", lambda: paused.get("mode") == "hold")
    check("PAUSE hold: assigned_this_pass 0",
          lambda: paused.get("assigned_this_pass") == 0)
    check("PAUSE hold: jobs empty (wishlist not dropped)",
          lambda: paused.get("jobs") == [])
    check("PAUSE hold: heartbeat still written",
          lambda: Path(paused["heartbeat_path"]).is_file()
          and json.loads(Path(paused["heartbeat_path"]).read_text(
              encoding="utf-8")).get("state") == "PAUSED")

    # resume_gate in the future stays paused (fail-closed).
    flag.write_text(json.dumps({
        "state": "PAUSED", "mode": "resume_gate",
        "reason": "test gate", "set_by": "test_watchdog2",
        "set_at": datetime.now().astimezone().isoformat(),
        "auto_resume_at": (datetime.now().astimezone()
                           + timedelta(hours=2)).isoformat(),
    }), encoding="utf-8")
    gated = scan_once(wd2, dry_run=False)
    check("resume_gate future: stays PAUSED",
          lambda: gated.get("state") == "PAUSED"
          and gated.get("mode") == "resume_gate"
          and gated.get("assigned_this_pass") == 0)
    check("resume_gate future: flag still present",
          lambda: flag.is_file())

    # resume_gate past auto_resume_at self-clears and scans.
    flag.write_text(json.dumps({
        "state": "PAUSED", "mode": "resume_gate",
        "reason": "test gate due", "set_by": "test_watchdog2",
        "set_at": datetime.now().astimezone().isoformat(),
        "auto_resume_at": (datetime.now().astimezone()
                           - timedelta(seconds=5)).isoformat(),
    }), encoding="utf-8")
    resumed = scan_once(wd2, dry_run=True)
    check("resume_gate due: flag unlinked, scan ran",
          lambda: not flag.exists() and resumed.get("state") != "PAUSED"
          and resumed.get("dry_run") is True
          and any(j.get("source") == "wishlist" for j in resumed.get("jobs", [])))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(("PASS" if not bad else "FAIL") + f" {len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 0 if not bad else 1


def _backlog_slug_serve(bl):
    for i in bl:
        if i.get("keith_section"):
            return i["slug"]
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
