#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_collector_scan -- PHASE 4 scanning seam.

Moved out of cosmos_collector.py with the module (docs/CORE_RESTRUCTURE.md):
a split does not land without its tests moving with it. cosmos_collector
re-exports the SAME objects, not copies, so Collector._collect_* and
tests/test_collector.py (`iter_queue_files`, `ledger_event_kept`,
`SKIP_DIR_NAMES`) keep working unchanged.

F-29 lesson: a location/shape change that keeps boot green can still break
CALLERS. This suite pins:
  * cosmos_collector re-exports the SAME objects
  * cosmos_collector.py no longer defines the moved walkers
  * the walkers still find queue results / drop BOOT_VERIFIED / skip torn JSONL
  * Collector.poll_once still collects through the re-exported iterators
    (boot-green is not poll-green)

Bite: cosmos/_fail_f39_scan_against_old.py against
_delme/predispose_collector_f39_scan_*/ (all_new_pins_failed).

    py -3.14 tests/test_collector_scan.py
"""
from __future__ import annotations

import ast
import json
import sys
import tempfile
from pathlib import Path


def _imports_module(src: str, name: str) -> bool:
    """True iff `src` has an import of `name` (docstring mentions do not count)."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] == name for a in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] == name:
                return True
    return False


HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

import cosmos_collector  # noqa: E402
import cosmos_collector_scan as scan  # noqa: E402
from cosmos_kernel import install  # noqa: E402
from cosmos_collector import (  # noqa: E402
    Collector, LEDGER_DROP, LEDGER_KEEP, SKIP_DIR_NAMES,
    _is_result_name, _walk_files, iter_jsonl_objs, iter_ledger_events,
    iter_queue_files, iter_research_files, iter_runner_ledger,
    ledger_event_kept,
)

RESULTS = []

REEXPORTED = (
    "SKIP_DIR_NAMES",
    "LEDGER_KEEP",
    "LEDGER_KEEP_SUBSTR",
    "LEDGER_DROP",
    "_walk_files",
    "_is_result_name",
    "iter_queue_files",
    "iter_research_files",
    "iter_ledger_events",
    "ledger_event_kept",
    "iter_runner_ledger",
    "iter_jsonl_objs",
)

TREE_ID = "KMesh-COSMOS-live"
MOVED_DEFS = (
    "def _walk_files",
    "def _is_result_name",
    "def iter_queue_files",
    "def iter_research_files",
    "def iter_ledger_events",
    "def ledger_event_kept",
    "def iter_runner_ledger",
    "def iter_jsonl_objs",
)


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _seam_rows() -> None:
    coll_src = (REPO / "cosmos" / "cosmos_collector.py").read_text(encoding="utf-8")
    scan_path = REPO / "cosmos" / "cosmos_collector_scan.py"
    scan_src = scan_path.read_text(encoding="utf-8") if scan_path.is_file() else ""
    caller_src = (HERE / "test_collector.py").read_text(encoding="utf-8")

    check("scan module exists on disk",
          lambda: scan_path.is_file() and len(scan_src) > 200)
    check("import cosmos_collector_scan", lambda: scan is not None)

    for name in REEXPORTED:
        check(
            f"cosmos_collector still exports {name} (same object)",
            (lambda n=name: getattr(cosmos_collector, n) is getattr(scan, n)),
        )

    for defn in MOVED_DEFS:
        check(f"scan module defines {defn}",
              (lambda d=defn: d in scan_src))
        check(f"collector source no longer defines {defn}",
              (lambda d=defn: d not in coll_src))

    check("collector re-exports via cosmos_collector_scan import",
          lambda: "from cosmos_collector_scan import" in coll_src)
    check("scan banner remains as a pointer, not a second definition",
          lambda: "scanning -- moved to cosmos_collector_scan" in coll_src
          and "from cosmos_collector_scan import" in coll_src)
    check("collector still owns Collector / poll_once (daemon not moved)",
          lambda: "class Collector" in coll_src and "def poll_once" in coll_src)
    check("scan does not import cosmos_collector (no cycle)",
          lambda: not _imports_module(scan_src, "cosmos_collector"))
    check("scan never ledger.append",
          lambda: "ledger.append" not in scan_src)
    check("scan has no drive-literal queue default",
          lambda: r"V:\Ai\_queue" not in scan_src
          and "WELL_KNOWN_BOOTSTRAP" not in scan_src)

    check("iter_queue_files imported from cosmos_collector is the scan fn",
          lambda: iter_queue_files is scan.iter_queue_files)
    check("ledger_event_kept imported from cosmos_collector is the scan fn",
          lambda: ledger_event_kept is scan.ledger_event_kept)
    check("SKIP_DIR_NAMES is the scan set (same object)",
          lambda: SKIP_DIR_NAMES is scan.SKIP_DIR_NAMES)
    check("LEDGER_DROP still names BOOT_VERIFIED (re-export, not invented)",
          lambda: "BOOT_VERIFIED" in LEDGER_DROP
          and "BOOT_VERIFIED" in scan.LEDGER_DROP)
    check("LEDGER_KEEP still names RAIL_RESULT (re-export, not invented)",
          lambda: "RAIL_RESULT" in LEDGER_KEEP)

    # F-29 caller pin: the end-to-end suite still names the collector, not the split.
    check("test_collector still constructs Collector and calls poll_once",
          lambda: "Collector(" in caller_src and "poll_once" in caller_src)
    check("test_collector still imports parse_dhx_markers off cosmos_collector",
          lambda: "parse_dhx_markers" in caller_src)


def _walker_behaviour() -> None:
    td = Path(tempfile.mkdtemp(prefix="cosmos_f39_scan_"))
    queue = td / "queue"
    _write(queue / "g46_fanout12_result.json", '{"rc": 0}\n')
    _write(queue / "done" / "g46_review__t600.py", "print(1)\n")
    _write(queue / "failed" / "broke__t600.py", "raise SystemExit(1)\n")
    _write(queue / "logs" / "g46_review.log", "CLEAN rc=0\n")
    _write(queue / "returns" / "g46_fanout12_result.json", '{"rc": 0, "via": "returns"}\n')
    _write(queue / "_lanes" / "lg" / "grok_docs_result.json", '{"rc": 0}\n')
    _write(queue / "waiting_job__t300.py", "print('queued')\n")
    _write(queue / ".hidden_result.json", '{"rc": 0}\n')

    hits = list(iter_queue_files(queue, "root"))
    sources = {src for _p, src in hits}
    names = {p.name for p, _src in hits}

    check("iter_queue_files root finds queue_result",
          lambda: "queue_result" in sources and "g46_fanout12_result.json" in names)
    check("iter_queue_files root finds queue_done / queue_failed / queue_log",
          lambda: {"queue_done", "queue_failed", "queue_log"} <= sources)
    check("iter_queue_files root finds queue_returns (M2, own source)",
          lambda: "queue_returns" in sources)
    check("iter_queue_files root does not walk _lanes (lg is its own source)",
          lambda: "grok_docs_result.json" not in names)
    check("iter_queue_files root does not index a queued (not done) script",
          lambda: "waiting_job__t300.py" not in names)
    check("_is_result_name accepts _result.json and .result.json",
          lambda: _is_result_name("a_result.json")
          and _is_result_name("a.result.json")
          and not _is_result_name("a.py"))

    lg_hits = list(iter_queue_files(queue / "_lanes" / "lg", "lg"))
    check("iter_queue_files lg finds the lane result",
          lambda: any(p.name == "grok_docs_result.json" for p, _s in lg_hits))

    research = td / "research"
    _write(research / "COSMOS" / "RESEARCH_1.md", "# COSMOS\n")
    _write(research / "notes.txt", "not markdown\n")
    r_hits = list(iter_research_files(research))
    check("iter_research_files yields markdown only",
          lambda: len(r_hits) == 1 and r_hits[0][1] == "research"
          and r_hits[0][0].name == "RESEARCH_1.md")

    check("ledger_event_kept drops BOOT_VERIFIED",
          lambda: ledger_event_kept("BOOT_VERIFIED") is False)
    check("ledger_event_kept drops SPEND_RESERVED",
          lambda: ledger_event_kept("SPEND_RESERVED") is False)
    check("ledger_event_kept keeps RAIL_RESULT",
          lambda: ledger_event_kept("RAIL_RESULT") is True)
    check("ledger_event_kept keeps PROBE_RESULT",
          lambda: ledger_event_kept("PROBE_RESULT") is True)
    check("ledger_event_kept empty is false",
          lambda: ledger_event_kept("") is False)

    led = td / "authority.jsonl"
    _write(led, "\n".join([
        json.dumps({"seq": 1, "event": "BOOT_VERIFIED"}),
        json.dumps({"seq": 2, "event": "RAIL_RESULT", "payload": {"ok": True}}),
        "this is not json",
        json.dumps(["not", "a", "dict"]),
        json.dumps({"seq": 3, "event": "PROBE_RESULT"}),
        "",
    ]) + "\n")
    events = list(iter_ledger_events(led))
    check("iter_ledger_events skips torn lines and non-dicts",
          lambda: [e.get("event") for e in events]
          == ["BOOT_VERIFIED", "RAIL_RESULT", "PROBE_RESULT"])
    check("iter_ledger_events stamps _line",
          lambda: events[0].get("_line") == 1 and events[1].get("_line") == 2)

    kept = [e for e in events if ledger_event_kept(str(e.get("event") or ""))]
    check("keep predicate over the same iterator drops infrastructure noise",
          lambda: [e.get("event") for e in kept]
          == ["RAIL_RESULT", "PROBE_RESULT"])

    rl = td / "runner_ledger.jsonl"
    _write(rl, json.dumps({"event": "end", "job": "g46_fanout12__t600.py",
                           "rc": 0}) + "\n")
    rled = list(iter_runner_ledger(rl))
    check("iter_runner_ledger yields the end event and stamps _ledger",
          lambda: len(rled) == 1 and rled[0].get("event") == "end"
          and rled[0].get("_ledger") == str(rl))

    missing = list(iter_queue_files(td / "no_such_queue", "root"))
    check("iter_queue_files missing tree yields nothing (not a crash)",
          lambda: missing == [])

    walked = list(_walk_files(queue, set(SKIP_DIR_NAMES) | {"_lanes", "returns"}))
    check("_walk_files skips named dirs and dotfiles",
          lambda: all(p.name != ".hidden_result.json" for p in walked)
          and any(p.name == "g46_fanout12_result.json" for p in walked))


def _caller_poll() -> None:
    """The daemon caller, not just the walker. F-29 shape pin."""
    td = Path(tempfile.mkdtemp(prefix="cosmos_f39_scan_poll_"))
    root = install(td / "live", tree_id=TREE_ID)
    queue = td / "queue"
    research = td / "research"
    summary = td / "docs" / "COLLECTOR.md"
    dhx = td / "docs" / "AGENT_BRIEF.md"
    _write(queue / "g46_scan_seam_result.json", json.dumps({
        "rc": 0, "ok": True, "agent": "G46", "summary": "scan seam",
    }))
    _write(research / "SEAM.md", "# scan seam research\n")
    _write(dhx, "# DHx\n## Assignment log — APPEND-ONLY markers\n")
    led = root / "ledger" / "authority.jsonl"
    led.parent.mkdir(parents=True, exist_ok=True)
    led.write_text(
        json.dumps({"seq": 1, "event": "BOOT_VERIFIED", "t": 1.0,
                    "writer": "cli", "payload": {}}) + "\n"
        + json.dumps({"seq": 2, "event": "RAIL_RESULT", "t": 2.0,
                      "writer": "cm-dispatch",
                      "payload": {"link_id": "sgh-api", "ok": True}}) + "\n",
        encoding="utf-8",
    )
    coll = Collector(str(root), queue=queue, research=research,
                     summary_md=summary, interval_s=30.0, dhx=dhx)
    rec = coll.poll_once()
    rows = [json.loads(ln) for ln in coll.index_path.read_text(
        encoding="utf-8").splitlines() if ln.strip()]
    sources = {r.get("source") for r in rows}
    check("poll_once through re-exported walkers collects queue_result",
          lambda: rec.get("new_this_tick", 0) > 0
          and "queue_result" in sources
          and any("g46_scan_seam" in str(r.get("artifact")) for r in rows))
    check("poll_once through re-exported walkers collects research",
          lambda: "research" in sources)
    check("poll_once through re-exported walkers keeps RAIL_RESULT not BOOT_VERIFIED",
          lambda: any(r.get("source") == "ledger"
                      and "RAIL_RESULT" in str(r.get("summary") or r.get("task") or r.get("event") or r)
                      or r.get("artifact", "").endswith("#seq=2")
                      for r in rows)
          and not any(str(r.get("artifact") or "").endswith("#seq=1") for r in rows))
    check("poll_once still writes the collector heartbeat (daemon not moved)",
          lambda: coll.heartbeat.is_file()
          and json.loads(coll.heartbeat.read_text(encoding="utf-8")).get("worker")
          == "cosmos-collector")


def main() -> int:
    _seam_rows()
    _walker_behaviour()
    _caller_poll()
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    coll_path = REPO / "cosmos" / "cosmos_collector.py"
    scan_path = REPO / "cosmos" / "cosmos_collector_scan.py"
    live_value = {
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "reexported": len(REEXPORTED),
        "walk_same": (
            hasattr(cosmos_collector, "_walk_files")
            and cosmos_collector._walk_files is scan._walk_files
        ),
        "kept_same": (
            hasattr(cosmos_collector, "ledger_event_kept")
            and cosmos_collector.ledger_event_kept is scan.ledger_event_kept
        ),
        "coll_lines": coll_path.read_text(encoding="utf-8").count("\n") + 1,
        "scan_lines": (
            scan_path.read_text(encoding="utf-8").count("\n") + 1
            if scan_path.is_file() else 0
        ),
        "scan_exists": scan_path.is_file(),
        "tree_id": TREE_ID,
    }
    print("live_value: " + json.dumps(live_value, sort_keys=True))
    print(("PASS" if not bad else "FAIL")
          + f" {len(RESULTS) - len(bad)}/{len(RESULTS)}")
    out = REPO / "cosmos" / "_f39_scan_split.json"
    rec = {
        "schema": "cosmos-f39-scan-split/1",
        "ok": not bad,
        "tree_id": TREE_ID,
        "coll": {
            "bytes": coll_path.stat().st_size,
            "lines": live_value["coll_lines"],
        },
        "scan": {
            "bytes": scan_path.stat().st_size if scan_path.is_file() else 0,
            "lines": live_value["scan_lines"],
        },
        "walk_same": live_value["walk_same"],
        "kept_same": live_value["kept_same"],
        "suite": {
            "checks": live_value["checks"],
            "passed": live_value["passed"],
        },
    }
    out.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
