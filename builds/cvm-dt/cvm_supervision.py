#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Supervision audit — derive "who should be watched" from the workers.

CVM_BACKLOG B8 / CLOCK_POSTMORTEM P4, the class behind F-19/F-20/F-31/F-65.

The postmortem's finding was that `cvm-dt-clock` and `cvm-dt-voice` never
crashed — **neither was ever registered**, nobody watched them, and every
local signal stayed green. That is possible because supervision lives in two
HAND-MAINTAINED lists a new worker must be manually added to:

  * `cosmos_own_clocks.CLOCKS`          — the scheduled-task registry
  * `cosmos_health_clock.PEER_HEARTBEATS` — the liveness watch list

and **nothing fails when it is not**. A worker can ship a `--register` that
only emits, be in neither list, and look fine forever.

This module closes the detection half of that: the workers already DECLARE
their own supervision contract as module constants (`TASK_NAME`,
`TASK_NAME_LOGON`, `HEARTBEAT_NAME`), so the required rows are derivable, not
remembered. Every declaring module is measured against the three independent
facts:

  1. `in_clocks`     — is TASK_NAME a row in CLOCKS?
  2. `in_watchlist`  — is HEARTBEAT_NAME in PEER_HEARTBEATS?
  3. `os_registered` — does `schtasks /query` actually find the task NOW?
     plus `heartbeat_age_s` off the runtime root's own logs.

(1) and (2) are declarations; (3) is the machine. They disagree constantly,
and the disagreement is the whole point: `in_clocks=true, os_registered=false`
is "the registry lies", and `in_clocks=false, os_registered=false` is the
postmortem's silent hole.

Modules are read with `ast`, never imported — importing a worker starts COM,
threads and daemons, which an audit must not do.

    py -3.14 builds\\cvm-dt\\cvm_supervision.py --root <RUNTIME>
    py -3.14 builds\\cvm-dt\\cvm_supervision.py --root <RUNTIME> --no-schtasks

rc=0 is NOT the gate. The gate is `SUPERVISION.json`'s `unsupervised[]`: each
entry names the worker, which of the three facts is false, and the exact line
that would make it true. An empty `unsupervised[]` is only meaningful next to
a non-zero `declared` count.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for _p in (str(HERE), str(REPO / "cosmos")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

WIRE = "cvm-dt-supervision/1"
# Module-level string constants that together declare a supervision contract.
DECLARES = ("TASK_NAME", "TASK_NAME_LOGON", "HEARTBEAT_NAME")
# Where workers live. _delme / _disposal / __pycache__ hold staged copies and
# probes; auditing them would report the same worker several times.
SCAN_DIRS = ("cosmos", "builds")
SKIP_PARTS = ("_delme", "_disposal", "__pycache__", "_propose", "live",
              "node_modules", ".git")


def _skip(p: Path) -> bool:
    return any(part in SKIP_PARTS for part in p.parts)


def declared_constants(path: Path) -> dict:
    """Module-level `NAME = "literal"` for DECLARES. Static — never imports."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"),
                         filename=str(path))
    except (OSError, SyntaxError, ValueError):
        return {}
    found: dict[str, str] = {}
    for node in tree.body:                       # module level only
        if not isinstance(node, ast.Assign):
            continue
        value = node.value
        if not (isinstance(value, ast.Constant) and isinstance(value.value, str)):
            continue
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and tgt.id in DECLARES:
                found[tgt.id] = value.value
    return found


def scan(repo: Path = REPO) -> list[dict]:
    """Every module that declares a task name and/or a heartbeat name."""
    out: list[dict] = []
    for sub in SCAN_DIRS:
        base = repo / sub
        if not base.is_dir():
            continue
        for py in sorted(base.rglob("*.py")):
            if _skip(py.relative_to(repo)):
                continue
            d = declared_constants(py)
            if not d:
                continue
            out.append({
                "module": py.stem,
                "path": str(py.relative_to(repo)).replace("\\", "/"),
                "task_name": d.get("TASK_NAME"),
                "task_logon": d.get("TASK_NAME_LOGON"),
                "heartbeat": d.get("HEARTBEAT_NAME"),
            })
    return out


def registries() -> dict:
    """The two hand-maintained lists, read as data. Missing → named, not fatal."""
    rec: dict = {"clocks": [], "watchlist": [], "errors": []}
    try:
        from cosmos_own_clocks import CLOCKS
        rec["clocks"] = [
            {"id": c.get("id"), "task": c.get("task"),
             "logon": c.get("logon"), "heartbeat": c.get("heartbeat"),
             "script": c.get("script")} for c in CLOCKS]
    except Exception as e:                                            # noqa: BLE001
        rec["errors"].append("cosmos_own_clocks: %s: %s" % (type(e).__name__, e))
    try:
        from cosmos_health_clock import PEER_HEARTBEATS
        rec["watchlist"] = list(PEER_HEARTBEATS)
    except Exception as e:                                            # noqa: BLE001
        rec["errors"].append("cosmos_health_clock: %s: %s"
                             % (type(e).__name__, e))
    rec["max_clock_id"] = max([int(c["id"]) for c in rec["clocks"]
                               if c.get("id") is not None] or [0])
    return rec


# A worker whose heartbeat is older than this has not run in a whole day. It
# is a LIVENESS fact, reported separately from the supervision wiring: a
# registered-but-cold worker and an unregistered one fail differently.
COLD_S = 86400.0


def _heartbeat(logs_dir, name: str, now: float) -> dict:
    """(age_s, state). `None` age always carries a REASON, never a bare null."""
    if not name:
        return {"age_s": None, "state": "not_declared"}
    if logs_dir is None:
        return {"age_s": None, "state": "no_runtime_root"}
    p = Path(logs_dir) / name
    if not p.is_file():
        return {"age_s": None, "state": "absent"}
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
        last = float(rec.get("last_run_epoch") or 0.0)
    except (OSError, ValueError, TypeError) as e:
        return {"age_s": None, "state": "unreadable",
                "detail": "%s: %s" % (type(e).__name__, e)}
    if not last:
        return {"age_s": None, "state": "no_last_run_epoch"}
    # Sub-second negatives are the worker writing between our clock read and
    # the file read. Clamp the LABEL, never the measured number.
    age = round(now - last, 1)
    return {"age_s": age, "state": "cold" if age > COLD_S else "fresh"}


def audit(root=None, *, use_schtasks: bool = True, repo: Path = REPO) -> dict:
    now = time.time()
    reg = registries()
    tasks = {c["task"] for c in reg["clocks"] if c.get("task")}
    logons = {c["logon"] for c in reg["clocks"] if c.get("logon")}
    beats = set(reg["watchlist"])

    logs_dir = None
    root_rec = {"root": None, "tree_id": None}
    if root:
        try:
            from cosmos_paths import CosmosPaths
            paths = CosmosPaths(Path(root))
            logs_dir = paths.logs()
            root_rec = {"root": str(Path(root)),
                        "tree_id": paths.sentinel.tree_id}
        except Exception as e:                                        # noqa: BLE001
            root_rec = {"root": str(root), "tree_id": None,
                        "error": "%s: %s" % (type(e).__name__, e)}

    query = None
    if use_schtasks:
        try:
            from cosmos_clock import query_task as query
        except Exception as e:                                        # noqa: BLE001
            reg["errors"].append("cosmos_clock: %s: %s" % (type(e).__name__, e))

    rows: list[dict] = []
    for w in scan(repo):
        task, beat = w.get("task_name"), w.get("heartbeat")
        row = dict(w)
        row["in_clocks"] = bool(task and task in tasks)
        row["logon_in_clocks"] = (bool(w.get("task_logon") in logons)
                                  if w.get("task_logon") else None)
        row["in_watchlist"] = bool(beat and beat in beats)
        row["os_registered"] = None
        if query is not None and task:
            row["os_registered"] = bool(query(task).get("ok"))
        hb = _heartbeat(logs_dir, beat, now)
        row["heartbeat_age_s"] = hb["age_s"]
        row["heartbeat_state"] = hb["state"]
        if hb.get("detail"):
            row["heartbeat_detail"] = hb["detail"]

        missing = []
        if task and not row["in_clocks"]:
            missing.append("cosmos_own_clocks.CLOCKS")
        if beat and not row["in_watchlist"]:
            missing.append("cosmos_health_clock.PEER_HEARTBEATS")
        if task and row["os_registered"] is False:
            missing.append("schtasks")
        row["missing"] = missing
        row["supervised"] = not missing
        rows.append(row)

    unsupervised = [r for r in rows if not r["supervised"]]
    # Distinct failure: the wiring is right and the worker still is not running.
    cold = [r for r in rows if r["heartbeat_state"] in ("cold", "absent")]
    # A registry row a worker no longer declares is the mirror failure.
    declared_beats = {r["heartbeat"] for r in rows if r.get("heartbeat")}
    orphan_watch = [b for b in reg["watchlist"] if b not in declared_beats]

    return {
        "ok": not unsupervised,
        "wire": WIRE,
        "audited_at_epoch": now,
        "python": sys.version.split()[0],
        "repo": str(repo),
        "runtime": root_rec,
        "schtasks_queried": query is not None,
        "declared": len(rows),
        "supervised": len(rows) - len(unsupervised),
        "unsupervised_count": len(unsupervised),
        "registries": {
            "clocks_rows": len(reg["clocks"]),
            "max_clock_id": reg["max_clock_id"],
            "watchlist_len": len(reg["watchlist"]),
            "errors": reg["errors"],
        },
        "workers": rows,
        "cold_count": len(cold),
        "unsupervised": [
            {"module": r["module"], "path": r["path"],
             "task_name": r["task_name"], "heartbeat": r["heartbeat"],
             "missing": r["missing"],
             "heartbeat_age_s": r["heartbeat_age_s"],
             "heartbeat_state": r["heartbeat_state"]}
            for r in unsupervised],
        "cold": [
            {"module": r["module"], "heartbeat": r["heartbeat"],
             "heartbeat_age_s": r["heartbeat_age_s"],
             "heartbeat_state": r["heartbeat_state"],
             "os_registered": r["os_registered"],
             "supervised": r["supervised"]} for r in cold],
        "watchlist_without_declarer": orphan_watch,
        "note": ("rc=0 is not the gate. Read unsupervised[]: each entry names "
                 "which of CLOCKS / PEER_HEARTBEATS / schtasks is missing for "
                 "a worker that declares its own supervision contract."),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="COSMOS supervision audit")
    ap.add_argument("--root", default=None,
                    help="runtime root, for heartbeat ages")
    ap.add_argument("--no-schtasks", action="store_true",
                    help="skip the real schtasks /query (declarations only)")
    ap.add_argument("--out", default=str(HERE / "SUPERVISION.json"))
    a = ap.parse_args(argv)

    rec = audit(a.root, use_schtasks=not a.no_schtasks)
    Path(a.out).write_text(json.dumps(rec, indent=1), encoding="utf-8")
    rec["proof_path"] = a.out
    print(json.dumps(rec, indent=1))
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
