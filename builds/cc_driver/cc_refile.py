#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cc_refile.py  --  re-file a job the PRE-FIX driver mis-classified, using the new
classifier. Not a hand-edit: the verdict comes from `cc_outcome.classify()`, the
same code path the live driver now runs, fed from what is still on disk.

WHY THIS EXISTS
---------------
`cosmos_cc_driver` filed jobs by the PROCESS outcome, so every wall-clock kill
landed in `failed/` regardless of whether the work had landed. Those orders are
still sitting in `failed/` misreporting themselves. This re-runs the evidence
questions against the surviving artifacts and moves each order to the bucket its
WORK outcome earns.

It reconstructs the run window from the old result record (`ts_start` + `secs`),
resolves the order's write-fence, reads the stdout sidecar if the old driver
happened to keep one, and classifies. Where the pre-fix driver discarded stdout
(it always did, on the timeout path) the record says so -- `report_recoverable:
false` -- rather than pretending the report was absent because the agent never
wrote one. Two different facts, again.

Never deletes: the job file is MOVED, and the superseded result record is copied
to `_delme/predispose_<name>_<ts>/` first.

    py -3.14 builds/cc_driver/cc_refile.py --root V:/A/Ai/COSMOS/live \
        --lane cc-cdeck --job 070_cdeck_mobile_parity            # dry run
    py -3.14 builds/cc_driver/cc_refile.py ... --apply           # do it
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cc_outcome  # noqa: E402

HERE = Path(__file__).resolve().parent
TERMINALS = ("failed", "done", "timed_out")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _epoch(ts: str) -> float | None:
    """Parse the driver's own `_now()` stamp back to epoch seconds."""
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc).timestamp()
    except Exception:
        return None


def _stage(src: Path, tag: str) -> Path | None:
    """Never-delete: copy anything we are about to supersede into _delme."""
    if not src.exists():
        return None
    d = HERE / "_delme" / f"predispose_{tag}_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
    d.mkdir(parents=True, exist_ok=True)
    dst = d / src.name
    shutil.copy2(src, dst)
    return dst


def _move(src: Path, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    if dst.exists():
        dst = dst_dir / f"{src.stem}_{int(time.time())}{src.suffix}"
    os.replace(src, dst)
    return dst


def locate(lane_dir: Path, jid: str) -> tuple[Path | None, str | None]:
    for name in TERMINALS:
        p = lane_dir / name / f"{jid}.json"
        if p.exists():
            return p, name
    p = lane_dir / f"{jid}.json"
    return (p, "pending") if p.exists() else (None, None)


def refile(root: Path, lane: str, jid: str, apply: bool,
           repo: Path | None = None) -> dict:
    lane_dir = root / "queue" / "_lanes" / lane
    returns = lane_dir / "returns"
    job_path, current = locate(lane_dir, jid)
    if job_path is None:
        return {"ok": False, "error": f"job {jid} not found under {lane_dir}"}

    order = json.loads(job_path.read_text(encoding="utf-8"))
    res_path = returns / f"{jid}_result.json"
    old = json.loads(res_path.read_text(encoding="utf-8")) if res_path.exists() else {}

    t0 = _epoch(str(old.get("ts_start", "")))
    if t0 is None:
        return {"ok": False, "error": f"no parseable ts_start in {res_path}"}
    t1 = t0 + float(old.get("secs") or 0.0)

    cwd = Path(order.get("cwd") or old.get("cwd") or (repo or root.parent))
    fence = cc_outcome.fence_from_job(order)
    if fence is not None and not fence.is_absolute():
        fence = cwd / fence

    sidecar = returns / f"{jid}_result.json.stdout.txt"
    stdout = sidecar.read_text(encoding="utf-8", errors="replace") if sidecar.exists() else ""

    err = str(old.get("error") or "")
    timed_out = err == "timeout" or bool(old.get("timed_out"))
    exception = None if (timed_out or not err) else err

    verdict = cc_outcome.classify(
        rc=old.get("rc"), timed_out=timed_out, exception=exception,
        stdout=stdout, stderr=str(old.get("stderr_tail") or ""),
        t0=t0, t1=t1, fence=fence, base=cwd)

    verdict["refiled"] = {
        "ts": _now(), "lane": lane, "from": current, "to": verdict["route"],
        "prior_record": {"rc": old.get("rc"), "error": old.get("error"),
                         "secs": old.get("secs")},
        # The pre-fix driver never wrote a stdout sidecar on the timeout path, so
        # the agent's MANDATORY LAST LINE report is unrecoverable for this job.
        # That is a gap in the EVIDENCE, not proof the agent stayed silent.
        "report_recoverable": bool(stdout),
        "stdout_sidecar": str(sidecar) if sidecar.exists() else None,
        "classifier": "cc_outcome.classify (same path the live driver runs)",
    }

    plan = {"ok": True, "job": jid, "from": current, "to": verdict["route"],
            "outcome": verdict["outcome"], "evidence": verdict["evidence"],
            "artifacts": [f["path"] for f in verdict["work"]["artifacts"]["files"]],
            "applied": False}

    if not apply:
        plan["dry_run"] = True
        return plan

    staged = _stage(res_path, f"{jid}_result")
    (returns / f"{jid}_outcome.json").write_text(
        json.dumps({"id": jid, "ts": _now(), "lane": lane, **verdict}, indent=1),
        encoding="utf-8")
    old.update({"outcome": verdict["outcome"], "route": verdict["route"],
                "requeue": verdict["requeue"],
                "work_landed": verdict["work_landed"],
                "evidence": verdict["evidence"], "verdict": verdict})
    res_path.write_text(json.dumps(old, indent=1), encoding="utf-8")

    moved = job_path if current == verdict["route"] else _move(
        job_path, lane_dir / verdict["route"])
    plan.update({"applied": True, "job_path": str(moved),
                 "outcome_file": str(returns / f"{jid}_outcome.json"),
                 "staged_prior_result": str(staged) if staged else None})
    return plan


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="re-file a mis-classified cc_driver job")
    ap.add_argument("--root", required=True, help="runtime root (…/COSMOS/live)")
    ap.add_argument("--lane", required=True)
    ap.add_argument("--job", required=True, help="job id (file stem)")
    ap.add_argument("--apply", action="store_true", help="actually move it")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if not root.is_dir():
        print(f"REFUSE: root does not exist: {root}", file=sys.stderr)
        return 2
    out = refile(root, a.lane, a.job, a.apply)
    print(json.dumps(out, indent=1))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
