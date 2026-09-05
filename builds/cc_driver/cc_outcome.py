#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cc_outcome.py  --  typed outcome classifier for the COSMOS Claude Code driver.

THE DEFECT THIS EXISTS TO CLOSE (F-59, measured 2026-08-31)
-----------------------------------------------------------
`cosmos_cc_driver.run_job` recorded the PROCESS outcome as the WORK outcome:

    except subprocess.TimeoutExpired:
        result.update({"rc": None, "error": "timeout", ...})
        ok = False                     # <- a wall-clock kill became "the job failed"
    ...
    if not ok:
        emit_incident(...); _move(job_path, p.failed)

`070_cdeck_mobile_parity` was filed to `failed/` after 2404s while its deliverables
(`mobile_probe.py`, `test_mobile_layout.py`, a MOBILE column in `PARITY_AUDIT.md`)
were already on disk inside the run window. The subprocess died; the work did not.
Those are two different facts and this module keeps them apart.

WHAT IT DOES
------------
`classify()` returns a typed OUTCOME (never a boolean) plus the evidence it was
derived from. Before anything is filed, it asks the two questions the old code
never asked:

  1. did the agent emit its MANDATORY LAST LINE JSON report?   -> `work.report`
  2. did files land under the job's write-fence inside the run window?
                                                               -> `work.artifacts`

and it checks the report's own `files` claim against disk mtimes -- a claim is not
evidence (CLAUDE.md canon: runtime binding). Every field in the returned record is
derived from something the run actually emitted; nothing is asserted.

ROUTING follows the WORK outcome, not the process outcome:
  done/      COMPLETED, COMPLETED_NO_REPORT
  timed_out/ TIMED_OUT_WITH_OUTPUT, MAX_TURNS_WITH_OUTPUT
                                             (deliverables landed -- requeueing
                                             blindly would redo finished work)
  failed/    TIMED_OUT_NO_OUTPUT, MAX_TURNS_NO_OUTPUT,
             CRASHED, REFUSED, BAD_ORDER

Turn-budget exhaustion (GBW `--max-turns`, measured stderr "Max turns reached")
is the same family as a wall-clock kill: a RESOURCE LIMIT, not a crash and not
a work failure. Job 370_gbw_infra_next16 was the proof -- rc=1, timed_out=False,
15 artifacts, filed CRASHED. F-59 taught the clock; this teaches the turn cap.

No hard-coded paths: every scan is rooted at a fence passed in by the caller.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

# ---------------------------------------------------------------- the type ---
# A typed outcome, not a boolean. Order is severity-ish, not meaningful to code.
OUTCOMES = (
    "COMPLETED",              # process exited 0 AND emitted its last-line report
    "COMPLETED_NO_REPORT",    # process exited 0, no parseable report line
    "TIMED_OUT_WITH_OUTPUT",  # wall-clock kill, but report and/or artifacts landed
    "TIMED_OUT_NO_OUTPUT",    # wall-clock kill, nothing landed
    "MAX_TURNS_WITH_OUTPUT",  # engine hit --max-turns, but report/artifacts landed
    "MAX_TURNS_NO_OUTPUT",    # engine hit --max-turns, nothing landed
    "REFUSED",                # agent ran to completion and declined the work
    "CRASHED",                # non-zero exit, launch failure, or driver exception
    "BAD_ORDER",              # malformed work order (unparseable JSON / no task)
)

# Filing destination per outcome. The KEY POINT: a timeout is not routed by the
# fact that the clock ran out, it is routed by whether work landed.
ROUTE = {
    "COMPLETED":             "done",
    "COMPLETED_NO_REPORT":   "done",
    "TIMED_OUT_WITH_OUTPUT": "timed_out",
    "TIMED_OUT_NO_OUTPUT":   "failed",
    "MAX_TURNS_WITH_OUTPUT": "timed_out",  # same family as the wall clock
    "MAX_TURNS_NO_OUTPUT":   "failed",
    "REFUSED":               "failed",
    "CRASHED":               "failed",
    "BAD_ORDER":             "failed",
}

# What the orchestrator should do with the order next.
REQUEUE = {
    "COMPLETED":             "none",
    "COMPLETED_NO_REPORT":   "none",
    "TIMED_OUT_WITH_OUTPUT": "review",   # work on disk; re-run only after inspection
    "TIMED_OUT_NO_OUTPUT":   "safe",     # nothing landed; a clean re-run is safe
    "MAX_TURNS_WITH_OUTPUT": "review",   # same as timeout-with-output
    "MAX_TURNS_NO_OUTPUT":   "safe",
    "REFUSED":               "reorder",  # same order will refuse again; change it
    "CRASHED":               "safe",
    "BAD_ORDER":             "reorder",
}

# Directories that are never evidence of agent work.
_SKIP_DIRS = {".git", "node_modules", "__pycache__", "_delme", ".venv",
              "target", "dist", ".pytest_cache", ".mypy_cache"}
_MAX_WALK = 40000        # guard: never walk an unbounded tree looking for evidence
_MAX_ARTIFACTS = 200     # record at most this many paths; the COUNT is still exact
_MTIME_GRACE = 5.0       # seconds of slack on the window edges (clock/flush skew)

_FENCE_RE = re.compile(r"write\s+ONLY\s+under\s+[`'\"]?([^\s,;`'\"]+)", re.IGNORECASE)
_FENCE_TRIM = "/\\.,;:`'\""
_REFUSE_RE = re.compile(r"^\s*REFUSE[:\s]", re.MULTILINE)
_REFUSED_STATUS = {"refused", "refuse", "blocked", "declined", "refusal"}
# GBW (`grok --max-turns 60`) emits this on stderr and exits 1. Measured on
# 370_gbw_infra_next16: "Max turns reached\nError: max turns reached\n".
_MAX_TURNS_RE = re.compile(r"(?i)max\s+turns\s+reached")


# ------------------------------------------------------- evidence gatherers ---
def last_line_json(stdout: str, scan_lines: int = 40) -> tuple[dict | None, str | None]:
    """Recover the MANDATORY LAST LINE JSON object from an agent's stdout.

    The contract is 'one line containing only a JSON object and NOTHING after it',
    but a killed process can leave a partial trailing line, so we scan backwards
    over the last `scan_lines` non-empty lines and take the LAST one that parses
    as an object. Returns (obj, raw_line) or (None, None).
    """
    if not stdout:
        return None, None
    lines = [ln.strip() for ln in stdout.splitlines() if ln.strip()]
    for raw in reversed(lines[-scan_lines:]):
        if not (raw.startswith("{") and raw.endswith("}")):
            continue
        try:
            obj = json.loads(raw)
        except Exception:
            continue
        if isinstance(obj, dict):
            return obj, raw
    return None, None


def fence_from_job(job: dict, default: Path | None = None) -> Path | None:
    """Resolve the job's declared write-fence -- the directory its deliverables
    must land in. Explicit `job['fence']` wins; otherwise we read the canonical
    COSMOS work-order phrase 'write ONLY under <path>' out of the task text.
    That phrase is boilerplate on every dispatched order, so it is a contract,
    not a guess. Returns None if neither is present and no default is given.
    """
    fence = job.get("fence")
    if fence:
        return Path(str(fence))
    m = _FENCE_RE.search(str(job.get("task") or ""))
    if m:
        # Trim the sentence punctuation the phrase is always embedded in
        # ("...write ONLY under builds/cdeck/. Other agents...").
        cleaned = m.group(1).rstrip(_FENCE_TRIM)
        if cleaned:
            return Path(cleaned)
    return default


def scan_artifacts(fence: Path, t0: float, t1: float,
                   grace: float = _MTIME_GRACE) -> dict:
    """Files under `fence` whose mtime falls inside the run window [t0, t1].

    This is the runtime binding for 'did the agent do anything': the window is
    the process's own start/end, so a file that predates the run or belongs to a
    later job cannot be counted as this job's output.
    """
    out = {"fence": str(fence), "window": [t0, t1], "exists": False,
           "count": 0, "bytes": 0, "files": [], "walked": 0, "truncated": False}
    if fence is None or not Path(fence).is_dir():
        return out
    out["exists"] = True
    lo, hi = t0 - grace, t1 + grace
    walked = 0
    for dirpath, dirnames, filenames in os.walk(fence):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            walked += 1
            if walked > _MAX_WALK:
                out["truncated"] = True
                break
            fp = os.path.join(dirpath, name)
            try:
                st = os.stat(fp)
            except OSError:
                continue
            if lo <= st.st_mtime <= hi:
                out["count"] += 1
                out["bytes"] += st.st_size
                if len(out["files"]) < _MAX_ARTIFACTS:
                    out["files"].append({
                        "path": os.path.relpath(fp, fence).replace("\\", "/"),
                        "bytes": st.st_size,
                        "mtime": round(st.st_mtime, 1),
                        "offset_s": round(st.st_mtime - t0, 1),
                    })
        if out["truncated"]:
            break
    out["walked"] = walked
    out["files"].sort(key=lambda f: f["mtime"])
    return out


def verify_claimed(report: dict | None, base: Path, t0: float, t1: float,
                   grace: float = _MTIME_GRACE) -> list[dict]:
    """Check the report's own `files` claim against disk. A claim is not evidence.

    Each entry gets a state:
      verified -- exists and was written inside the run window
      stale    -- exists but was NOT touched during this run (pre-existing)
      missing  -- claimed and not on disk (fabricated compliance)
    """
    if not report:
        return []
    claimed = report.get("files")
    if not isinstance(claimed, list):
        return []
    lo, hi = t0 - grace, t1 + grace
    rows = []
    for c in claimed[:_MAX_ARTIFACTS]:
        rel = str(c if not isinstance(c, dict) else (c.get("path") or c.get("file") or ""))
        if not rel:
            continue
        p = Path(rel)
        if not p.is_absolute():
            p = Path(base) / rel
        try:
            st = p.stat()
        except OSError:
            rows.append({"claimed": rel, "state": "missing"})
            continue
        rows.append({
            "claimed": rel,
            "state": "verified" if lo <= st.st_mtime <= hi else "stale",
            "bytes": st.st_size,
            "mtime": round(st.st_mtime, 1),
        })
    return rows


def _is_refusal(report: dict | None, stdout: str) -> bool:
    """A typed refusal: the agent completed and explicitly declined the work."""
    if report:
        status = str(report.get("status", "")).strip().lower()
        if status in _REFUSED_STATUS:
            return True
        if status.startswith("refus") or status.startswith("declin"):
            return True
    return bool(stdout) and bool(_REFUSE_RE.search(stdout[-4000:]))


def _is_max_turns(stderr: str) -> bool:
    """True iff the engine reported turn-budget exhaustion on stderr.

    Detected from the engine's own words, not from rc -- rc=1 is also how a
    crash looks, which is exactly why 370 was mis-filed. The phrase is
    GBW's: 'Max turns reached' / 'Error: max turns reached'.
    """
    return bool(stderr) and bool(_MAX_TURNS_RE.search(stderr[-4000:]))


# ------------------------------------------------------------- the verdict ---
def classify(*, rc: int | None, timed_out: bool, exception: str | None,
             stdout: str, stderr: str, t0: float, t1: float,
             fence: Path | None, base: Path,
             bad_order: str | None = None) -> dict:
    """Return a typed outcome record. Never returns a bare bool.

    `rc`         process return code, or None if it never produced one
    `timed_out`  True iff the driver killed it on the wall clock
    `exception`  driver-side launch/IO exception text, if any
    `t0`/`t1`    run window (epoch seconds) -- used to bind artifacts to THIS run
    `fence`      directory the job was told to write in (see fence_from_job)
    `base`       resolution base for relative paths the report claims
    """
    report, report_line = last_line_json(stdout)
    artifacts = scan_artifacts(fence, t0, t1) if fence is not None else \
        {"fence": None, "exists": False, "count": 0, "bytes": 0, "files": [],
         "walked": 0, "truncated": False, "window": [t0, t1]}
    claimed = verify_claimed(report, base, t0, t1)
    verified = sum(1 for c in claimed if c["state"] == "verified")
    missing = sum(1 for c in claimed if c["state"] == "missing")

    # "Work landed" is the whole point: emitted report OR artifacts on disk.
    landed = bool(report) or artifacts["count"] > 0 or verified > 0
    max_turns = _is_max_turns(stderr)

    if bad_order:
        outcome = "BAD_ORDER"
    elif timed_out:
        # THE FIX. A wall-clock kill is a PROCESS fact. Whether work landed is a
        # separate WORK fact, and the two are recorded separately.
        outcome = "TIMED_OUT_WITH_OUTPUT" if landed else "TIMED_OUT_NO_OUTPUT"
    elif max_turns:
        # Same family as the wall clock: a RESOURCE LIMIT, not a crash. GBW
        # exits 1 with "Max turns reached" after producing work; filing that
        # CRASHED is the 370_gbw_infra_next16 defect.
        outcome = "MAX_TURNS_WITH_OUTPUT" if landed else "MAX_TURNS_NO_OUTPUT"
    elif exception:
        outcome = "CRASHED"
    elif _is_refusal(report, stdout) and artifacts["count"] == 0 and verified == 0:
        outcome = "REFUSED"
    elif rc == 0:
        outcome = "COMPLETED" if report else "COMPLETED_NO_REPORT"
    else:
        outcome = "CRASHED"

    rec = {
        "outcome": outcome,
        "route": ROUTE[outcome],
        "requeue": REQUEUE[outcome],
        "work_landed": landed,
        "process": {
            "rc": rc,
            "timed_out": bool(timed_out),
            "max_turns": bool(max_turns),
            "exception": exception,
            "secs": round(t1 - t0, 1),
            "stderr_tail": (stderr or "")[-500:],
        },
        "work": {
            "report": report,
            "report_line": report_line,
            "report_emitted": bool(report),
            "artifacts": artifacts,
            "claimed_files": claimed,
            "claimed_verified": verified,
            "claimed_missing": missing,
        },
        "classifier": {"module": "cc_outcome", "version": 2},
    }
    rec["evidence"] = evidence_line(rec)
    return rec


def evidence_line(rec: dict) -> str:
    """One human-readable line binding the verdict to what was actually emitted."""
    a = rec["work"]["artifacts"]
    bits = [f"outcome={rec['outcome']}",
            f"rc={rec['process']['rc']}",
            f"secs={rec['process']['secs']}",
            f"report={'yes' if rec['work']['report_emitted'] else 'no'}",
            f"artifacts={a['count']}/{a['bytes']}B"]
    if rec["process"].get("max_turns"):
        bits.append("max_turns=yes")
    if a.get("fence"):
        bits.append(f"fence={a['fence']}")
    if rec["work"]["claimed_files"]:
        bits.append(f"claimed_verified={rec['work']['claimed_verified']}"
                    f"/{len(rec['work']['claimed_files'])}")
    if rec["work"]["claimed_missing"]:
        bits.append(f"claimed_MISSING={rec['work']['claimed_missing']}")
    top = [f["path"] for f in a["files"][-3:]]
    if top:
        bits.append("newest=" + ",".join(top))
    return " ".join(bits)


def summarize(rec: dict) -> str:
    """Short incident/log line."""
    return f"{rec['outcome']} route={rec['route']} requeue={rec['requeue']} :: {rec['evidence']}"


if __name__ == "__main__":  # pragma: no cover - manual probe
    import argparse
    ap = argparse.ArgumentParser(description="classify a cc_driver run from disk")
    ap.add_argument("--fence", required=True)
    ap.add_argument("--t0", type=float, required=True)
    ap.add_argument("--secs", type=float, required=True)
    ap.add_argument("--stdout-file", default=None)
    ap.add_argument("--timed-out", action="store_true")
    ap.add_argument("--rc", default=None)
    a = ap.parse_args()
    so = Path(a.stdout_file).read_text(encoding="utf-8", errors="replace") if a.stdout_file else ""
    print(json.dumps(classify(
        rc=None if a.rc in (None, "None") else int(a.rc),
        timed_out=a.timed_out, exception=None, stdout=so, stderr="",
        t0=a.t0, t1=a.t0 + a.secs, fence=Path(a.fence), base=Path(a.fence)), indent=1))
