#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: the collector's DHx layer (cosmos_collector_dhx).

Moved out of tests/test_collector.py with the module in the PHASE 4 split
(docs/CORE_RESTRUCTURE.md) -- the rule is that no split lands without its tests
moving with it. test_collector.py keeps the end-to-end poll/index/summary
coverage and one re-export contract check; the grammar and the join are proved
here, against the module that actually owns them.

Pure and offline: text and dicts in, dicts out. The one filesystem touch
(resolve_marker_artifact) runs against a tempdir, and both roots are passed in --
nothing here resolves a path from a literal.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_collector_dhx import (
    KNOWN_LANES, LANE_NAMES, correlate_marker, marker_stems, parse_dhx_markers,
    pick_lane_job, resolve_marker_artifact, task_of,
)

RESULTS = []

DHX = """# DHx
## Assignment log — APPEND-ONLY markers
- 2026-08-25T21:00:00-05:00 · G46 · fanout test · root/g46_fanout12__t600.py
- 2026-08-25T21:01:00-05:00 · G46 · ghost never returned · root/ghost_unmatched__t1800.py
- 2026-08-27T01:50:46.467635-05:00 · G46 · motif_collector_s6 gate · cm/g46_grok_motif_collector_s6_you_are_g46_grok_bd071d24__t1800.py
- 2026-08-25T23:55:24.411180-05:00 · GROK · pickup PONG · buckets/grok/proof_pong_grok.json
- 2026-08-28T09:00:00-05:00 - Cursor - read docs/AGENT_BRIEF.md then run it - cm/cursor_seam_check__t900.py
## Active assignments
- 2026-08-25T21:02:00-05:00 · G46 · not in the log section · root/never_parsed__t600.py
"""


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def run() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_collector_dhx_"))

    # ---- task_of: the job-stem normalizer the grammar and the join share ----
    check("task_of: strips _result.json",
          lambda: task_of(Path("g46_fanout12_result.json")) == "g46_fanout12")
    check("task_of: strips .result.json",
          lambda: task_of(Path("g46_fanout12.result.json")) == "g46_fanout12")
    check("task_of: strips the runner timeout suffix __t1800",
          lambda: task_of(Path("grok_docs__t1800.py")) == "grok_docs")
    check("task_of: strips a trailing log stamp",
          lambda: task_of(Path("g46_review__2026-08-25T21-14-04.log")) == "g46_review")
    check("task_of: __t followed by non-digits is not a timeout suffix",
          lambda: task_of(Path("job__tail.py")) == "job__tail")

    # ---- pick_lane_job: scoring, not first/last match ----
    check("pick_lane_job: a known lane + job beats a docs/ mention in the prose",
          lambda: pick_lane_job("read docs/AGENT_BRIEF.md then cm/g46_x__t900.py")[:2]
          == ("cm", "g46_x__t900.py"))
    check("pick_lane_job: nested buckets/grok/<file> resolves to lane buckets",
          lambda: pick_lane_job("pickup buckets/grok/proof_pong_grok.json")[:2]
          == ("buckets", "proof_pong_grok.json"))
    check("pick_lane_job: no path at all -> empty, cut -1",
          lambda: pick_lane_job("no jobfile in this body") == ("", "", -1))
    check("pick_lane_job: a docs/*.md mention alone scores negative and is refused",
          lambda: pick_lane_job("see docs/CORE_RESTRUCTURE.md") == ("", "", -1))
    check("pick_lane_job: backslashes are normalized to /",
          lambda: pick_lane_job(r"cm\g46_win__t600.py")[:2] == ("cm", "g46_win__t600.py"))

    # ---- parse_dhx_markers ----
    markers = parse_dhx_markers(DHX)
    check("parse_dhx_markers: five assignment-log rows",
          lambda: len(markers) == 5 and markers[0]["agent"] == "G46"
          and markers[1]["jobfile"].startswith("ghost_unmatched"))
    check("parse_dhx_markers: cm/ lane + jobfile extracted",
          lambda: any(m.get("lane") == "cm"
                      and "bd071d24" in str(m.get("jobfile"))
                      for m in markers))
    check("parse_dhx_markers: buckets/grok nested path extracted",
          lambda: any(m.get("lane") == "buckets"
                      and "proof_pong_grok" in str(m.get("jobfile"))
                      for m in markers))
    check("parse_dhx_markers: ' - ' separator (dispatch stamps that form)",
          lambda: any(m.get("agent") == "Cursor"
                      and m.get("jobfile") == "cursor_seam_check__t900.py"
                      for m in markers))
    check("parse_dhx_markers: the jobfile is cut out of the assignment text",
          lambda: markers[0]["assignment"] == "fanout test")
    check("parse_dhx_markers: section ends at the next ## heading",
          lambda: not any("never_parsed" in str(m.get("jobfile")) for m in markers))
    check("parse_dhx_markers: empty / None text is [] , not a crash",
          lambda: parse_dhx_markers("") == [] and parse_dhx_markers(None) == [])

    # ---- marker_stems ----
    stems = marker_stems(markers[2])
    check("marker_stems: longest first (a full stem beats a hash collision)",
          lambda: stems == sorted(stems, key=len, reverse=True))
    check("marker_stems: the 8-hex job id is a stem",
          lambda: "bd071d24" in stems)
    check("marker_stems: the timeout-stripped stem is present",
          lambda: any(s.endswith("bd071d24") for s in stems))
    check("marker_stems: nothing shorter than 4 chars",
          lambda: all(len(s) >= 4 for s in stems))
    check("marker_stems: an empty marker yields no stems",
          lambda: marker_stems({}) == [])

    # ---- correlate_marker: source rank beats stem length beats mtime ----
    rows = [
        {"source": "queue_log", "task": "g46_fanout12",
         "artifact": "/q/logs/g46_fanout12__t600__2026-08-25T21-00-00.log",
         "mtime": 9000.0, "rc": 0},
        {"source": "queue_result", "task": "g46_fanout12",
         "artifact": "/q/g46_fanout12_result.json", "mtime": 1000.0, "rc": 0},
        {"source": "dhx_marker", "task": "g46_fanout12",
         "artifact": "/docs/AGENT_BRIEF.md#g46_fanout12", "mtime": 9999.0},
    ]
    hit = correlate_marker(markers[0], rows)
    check("correlate_marker: a queue_result beats a newer queue_log",
          lambda: hit is not None and hit["source"] == "queue_result")
    check("correlate_marker: never joins a marker to another marker",
          lambda: hit["source"] != "dhx_marker")
    check("correlate_marker: no matching row -> None",
          lambda: correlate_marker(markers[1], rows) is None)
    check("correlate_marker: empty catalog -> None",
          lambda: correlate_marker(markers[0], []) is None)
    check("correlate_marker: an unparseable mtime is 0.0, not an exception",
          lambda: correlate_marker(markers[0], [
              {"source": "queue_result", "task": "g46_fanout12",
               "artifact": "/q/g46_fanout12_result.json", "mtime": "not-a-float"},
          ]) is not None)
    newer = dict(rows[1], artifact="/q/g46_fanout12_result.json", mtime=5000.0)
    check("correlate_marker: within one source the newest mtime wins",
          lambda: correlate_marker(markers[0], [rows[1], newer])["mtime"] == 5000.0)

    # ---- resolve_marker_artifact: ARTIFACT vs MISSING ----
    repo = td / "repo"
    runtime = td / "live"
    _write(repo / "cosmos" / "cosmos_seam.py", "print('landed')\n")
    _write(runtime / "logs" / "proof_pong_grok.json", "{}\n")
    check("resolve_marker_artifact: a landed module under repo/cosmos resolves",
          lambda: str(resolve_marker_artifact({"jobfile": "cosmos_seam.py"},
                                              repo, runtime)).endswith("cosmos_seam.py"))
    check("resolve_marker_artifact: a heartbeat under <runtime>/logs resolves",
          lambda: str(resolve_marker_artifact({"jobfile": "proof_pong_grok.json"},
                                              repo, runtime)).endswith("proof_pong_grok.json"))
    # NB: `repo` and `runtime` are BOTH tempdirs (see main()). No literal below
    # names the live tree; tests/test_live_write_fence.py proves that by syscall.
    check("resolve_marker_artifact: the runtime root is searched before the repo",
          lambda: str(Path(resolve_marker_artifact(
              {"jobfile": "proof_pong_grok.json"}, repo, runtime)).parent)
          == str(runtime / "logs"))
    check("resolve_marker_artifact: .py deliverable found from a .json jobfile stem",
          lambda: str(resolve_marker_artifact({"jobfile": "cosmos_seam.json"},
                                              repo, runtime)).endswith("cosmos_seam.py"))
    check("resolve_marker_artifact: genuinely absent -> None (this is MISSING)",
          lambda: resolve_marker_artifact({"jobfile": "ghost_unmatched__t1800.py"},
                                          repo, runtime) is None)
    check("resolve_marker_artifact: a placeholder jobfile is not a deliverable",
          lambda: resolve_marker_artifact({"jobfile": "--"}, repo, runtime) is None
          and resolve_marker_artifact({"jobfile": ""}, repo, runtime) is None)
    check("resolve_marker_artifact: a None root is skipped, not a TypeError",
          lambda: str(resolve_marker_artifact({"jobfile": "cosmos_seam.py"},
                                              repo, None)).endswith("cosmos_seam.py"))
    check("resolve_marker_artifact: a nonexistent root is skipped, not a crash",
          lambda: resolve_marker_artifact({"jobfile": "cosmos_seam.py"},
                                          td / "no_such_repo", td / "no_such_live") is None)

    # ---- lane vocabulary: a lane is never an agent (H2) ----
    check("LANE_NAMES: cm/buckets are lanes, and KNOWN_LANES is a superset",
          lambda: {"cm", "buckets"} <= LANE_NAMES and LANE_NAMES < KNOWN_LANES)
    check("H2: no marker ever reports a lane as its agent",
          lambda: all(str(m["agent"]).lower() not in LANE_NAMES for m in markers))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    return 1 if bad else 0


def test_collector_dhx():
    assert main() == 0


def main() -> int:
    from cosmos_test_guard import sandbox_heartbeats
    with sandbox_heartbeats():
        return run()


if __name__ == "__main__":
    raise SystemExit(main())
