#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_dispatch_lanes -- PHASE 4 BTS lane-accounting seam.

Moved out of cosmos_dispatch.py with the module (docs/CORE_RESTRUCTURE.md):
a split does not land without its tests moving with it. cosmos_dispatch
re-exports the SAME objects, not copies, so dispatch() and
cosmos_watchdog2 (`measure_lanes`) keep working unchanged.

F-29 lesson: a location/shape change that keeps boot green can still break
CALLERS. This suite pins:
  * cosmos_dispatch re-exports the SAME objects
  * cosmos_dispatch.py no longer defines the moved lane helpers
  * cosmos_watchdog2 still imports measure_lanes off cosmos_dispatch
  * pick_least_loaded / job_filename / locate_job still behave
  * dispatch() still drops a grok job through the re-export
    (boot-green is not drop-green)

Bite: cosmos/_fail_f39_lanes_against_old.py against
_delme/predispose_dispatch_f39_lanes_*/ (all_new_pins_failed).

    py -3.14 tests/test_dispatch_lanes.py
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

import cosmos_dispatch  # noqa: E402
import cosmos_dispatch_lanes as lanes  # noqa: E402
from cosmos_kernel import install  # noqa: E402
from cosmos_dispatch import (  # noqa: E402
    GROK_MAX_TURNS, dispatch, job_filename, locate_job, measure_lanes,
    pick_least_loaded, returns_dir,
)

RESULTS = []

REEXPORTED = (
    "_lane_dir",
    "_is_runnable",
    "_is_helper",
    "lane_load",
    "measure_lanes",
    "pick_least_loaded",
    "job_filename",
    "_write_exclusive",
    "_find_existing",
    "locate_job",
    "_lane_of_path",
    "returns_dir",
)

TREE_ID = "KMesh-COSMOS-live"
MOVED_DEFS = (
    "def _lane_dir",
    "def _is_runnable",
    "def _is_helper",
    "def lane_load",
    "def measure_lanes",
    "def pick_least_loaded",
    "def job_filename",
    "def _write_exclusive",
    "def _find_existing",
    "def locate_job",
    "def _lane_of_path",
    "def returns_dir",
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
    disp_src = (REPO / "cosmos" / "cosmos_dispatch.py").read_text(encoding="utf-8")
    lanes_path = REPO / "cosmos" / "cosmos_dispatch_lanes.py"
    lanes_src = lanes_path.read_text(encoding="utf-8") if lanes_path.is_file() else ""
    wd2_src = (REPO / "cosmos" / "cosmos_watchdog2.py").read_text(encoding="utf-8")
    caller_src = (HERE / "test_dispatch.py").read_text(encoding="utf-8")

    check("lanes module exists on disk",
          lambda: lanes_path.is_file() and len(lanes_src) > 200)
    check("import cosmos_dispatch_lanes", lambda: lanes is not None)

    for name in REEXPORTED:
        check(
            f"cosmos_dispatch still exports {name} (same object)",
            (lambda n=name: getattr(cosmos_dispatch, n) is getattr(lanes, n)),
        )

    for defn in MOVED_DEFS:
        check(f"lanes module defines {defn}",
              (lambda d=defn: d in lanes_src))
        check(f"dispatch source no longer defines {defn}",
              (lambda d=defn: d not in disp_src))

    check("dispatch re-exports via cosmos_dispatch_lanes import",
          lambda: "from cosmos_dispatch_lanes import" in disp_src)
    check("lanes banner remains as a pointer, not a second definition",
          lambda: "live in cosmos_dispatch_lanes" in disp_src
          and "from cosmos_dispatch_lanes import" in disp_src)
    check("dispatch still owns dispatch / job_status (harness not moved)",
          lambda: "def dispatch" in disp_src and "def job_status" in disp_src)
    check("lanes does not import cosmos_dispatch (no cycle)",
          lambda: not _imports_module(lanes_src, "cosmos_dispatch"))
    check("lanes never ledger.append",
          lambda: "ledger.append" not in lanes_src)
    check("lanes has no drive-literal queue default",
          lambda: r"V:\Ai\_queue" not in lanes_src
          and "WELL_KNOWN_BOOTSTRAP" not in lanes_src)
    check("watchdog2 still imports measure_lanes off cosmos_dispatch",
          lambda: "from cosmos_dispatch import" in wd2_src
          and "measure_lanes" in wd2_src)
    check("measure_lanes imported from cosmos_dispatch is the lanes fn",
          lambda: measure_lanes is lanes.measure_lanes)
    check("test_dispatch still calls pick_least_loaded off cosmos_dispatch",
          lambda: "from cosmos_dispatch import" in caller_src
          and "pick_least_loaded" in caller_src)


def _lane_behaviour() -> None:
    td = Path(tempfile.mkdtemp(prefix="cosmos_f39_lanes_"))
    queue = td / "queue"
    for extra in (queue, queue / "_lanes" / "lg", queue / "_lanes" / "pb"):
        extra.mkdir(parents=True, exist_ok=True)
        (extra / "running").mkdir(parents=True, exist_ok=True)
        (extra / "done").mkdir(parents=True, exist_ok=True)
    _write(queue / "a.py", "print(1)\n")
    _write(queue / "b.py", "print(2)\n")
    _write(queue / "_helper.py", "print('no')\n")
    _write(queue / "_lanes" / "lg" / "c.py", "print(3)\n")
    _write(queue / "_lanes" / "lg" / "running" / "r.py", "print(4)\n")
    _write(queue / "_lanes" / "lg" / "running" / "s.py", "print(5)\n")

    loads = measure_lanes(queue)
    check("root load is queued+running (2)",
          lambda: loads["root"]["queued"] == 2 and loads["root"]["load"] == 2)
    check("lg load is 3",
          lambda: loads["lg"]["queued"] == 1 and loads["lg"]["running"] == 2
          and loads["lg"]["load"] == 3)
    check("pb load is 0", lambda: loads["pb"]["load"] == 0)
    check("pick_least_loaded prefers pb (empty)",
          lambda: pick_least_loaded(queue) == "pb")
    check("_-prefixed files are not counted as jobs",
          lambda: measure_lanes(queue)["root"]["queued"] == 2)

    name = job_filename("G46", "grok", "Reply PONG.", str(td), 1800)
    check("job_filename is not helper-prefixed",
          lambda: not name.startswith("_") and name.endswith(".py"))
    check("job_filename is idempotent for same inputs",
          lambda: job_filename("G46", "grok", "Reply PONG.", str(td), 1800)
          == name)
    check("locate_job of a missing file is state=missing",
          lambda: locate_job(queue, "no_such_job.py")["state"] == "missing")
    _write(queue / "_lanes" / "pb" / name, "print('job')\n")
    loc = locate_job(queue, name)
    check("locate_job finds a queued file in the pb lane",
          lambda: loc["state"] == "queued" and loc["lane"] == "pb"
          and loc["path"] is not None)
    check("returns_dir is the lane's returns/",
          lambda: returns_dir(queue / "_lanes" / "pb")
          == queue / "_lanes" / "pb" / "returns")


def _caller_dispatch() -> None:
    """The harness caller, not just the lane helpers. F-29 shape pin."""
    td = Path(tempfile.mkdtemp(prefix="cosmos_f39_lanes_disp_"))
    root = install(td / "live", tree_id=TREE_ID)
    queue = td / "queue"
    for extra in (queue, queue / "_lanes" / "lg", queue / "_lanes" / "pb"):
        extra.mkdir(parents=True, exist_ok=True)
        (extra / "running").mkdir(parents=True, exist_ok=True)
        (extra / "done").mkdir(parents=True, exist_ok=True)
    dhx = td / "docs" / "AGENT_BRIEF.md"
    _write(dhx, (
        "# DHx\n\n"
        "## Assignment log — APPEND-ONLY markers\n\n"
        "## Active assignments\n"
        "- live\n"
    ))
    cwd = td / "workdir"
    cwd.mkdir()
    # Seed root/lg so pick_least_loaded has a real empty-lane winner (pb).
    # Tie-at-zero would pick LANE_ORDER[0] == root, which is not this pin.
    _write(queue / "seed_root.py", "print(1)\n")
    _write(queue / "_lanes" / "lg" / "seed_lg.py", "print(2)\n")
    rec = dispatch(
        "G46", "Reply with the single word PONG. Do not edit files.",
        str(cwd), kind="grok", queue=queue, runtime_root=root, dhx=dhx,
    )
    src = Path(rec["job_path"]).read_text(encoding="utf-8")
    check("dispatch() through re-export still drops a grok job",
          lambda: rec.get("kind") == "grok" and rec.get("created") is True
          and rec.get("kind_live") == "proven")
    check("dropped grok job still carries the proven flag set",
          lambda: '"--single"' in src and '"--always-approve"' in src
          and GROK_MAX_TURNS in src)
    check("least-loaded empty lane is still chosen (pb)",
          lambda: rec.get("lane") == "pb")
    check("dropped grok job does not bake a BTS drive-literal queue",
          lambda: r"V:\Ai\_queue" not in src)


def main() -> int:
    _seam_rows()
    _lane_behaviour()
    _caller_dispatch()
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    disp_path = REPO / "cosmos" / "cosmos_dispatch.py"
    lanes_path = REPO / "cosmos" / "cosmos_dispatch_lanes.py"
    live_value = {
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "reexported": len(REEXPORTED),
        "measure_same": (
            hasattr(cosmos_dispatch, "measure_lanes")
            and cosmos_dispatch.measure_lanes is lanes.measure_lanes
        ),
        "pick_same": (
            hasattr(cosmos_dispatch, "pick_least_loaded")
            and cosmos_dispatch.pick_least_loaded is lanes.pick_least_loaded
        ),
        "disp_lines": disp_path.read_text(encoding="utf-8").count("\n") + 1,
        "lanes_lines": (
            lanes_path.read_text(encoding="utf-8").count("\n") + 1
            if lanes_path.is_file() else 0
        ),
        "lanes_exists": lanes_path.is_file(),
        "tree_id": TREE_ID,
    }
    print("live_value: " + json.dumps(live_value, sort_keys=True))
    print(("PASS" if not bad else "FAIL")
          + f" {len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
