#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_runner - THE EXECUTOR (F5 builder). CRITIC M5: "H8 incumbent behaviors are
not in the runner because there is no runner." Now there is one, and it carries every
incumbent scar the architecture ordered preserved:

  * LOG-FIRST: the attempt log opens with RUNNING + the exact argv BEFORE execution,
    so a crash mid-job is distinguishable from a job that never started.
  * CLAIMED-PATH COMMAND: for script jobs the command is built from the path AS CLAIMED
    (verified to exist at claim time) - verifying a path is not verifying the path you
    are about to use.
  * HELPER CONVENTION: an `_`-prefixed script is a SUPPORTING FILE, refused as a job -
    and the refusal is recorded, never silent.
  * UTF-8 BOTH ENDS via cosmos_platform.run (no shell, ever).
  * THREE WORDED OUTCOMES from rc: 0=CLEAN, 2=FINDINGS, else BROKE; timeout is BROKE
    with the kill result RECORDED.
  * Every artifact is attempt-private: work/<job>/<attempt>/ with log + result.json.
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from cosmos_platform import run_tree_killed, makedirs
from cosmos_sched import Scheduler


class Runner:
    def __init__(self, sched: Scheduler, work_root: Path, worker_id: str):
        self.sched = sched
        self.work = Path(work_root)
        self.worker = worker_id

    def run_one(self) -> dict | None:
        """Claim the next job, EXECUTE it, land the worded outcome. Returns the result
        record, or None when the queue is empty."""
        m = self.sched.claim_next()
        if m is None:
            return None
        job_id = m["job_id"]
        attempt = uuid.uuid4().hex[:10]
        adir = self.work / job_id / attempt
        makedirs(adir)
        log = adir / "attempt.log"

        cmd = m["command"]
        # command forms: "py:<script path>" runs a python file; anything else is argv
        # split on spaces ONLY when it is a list already serialized - keep it explicit.
        if cmd.startswith("py:"):
            script = Path(cmd[3:].strip())
            if script.name.startswith("_"):
                self.sched.done(job_id, "BROKE",
                                "helper-prefixed script refused as a job (the `_` "
                                "convention, enforced in the runner)")
                return {"job_id": job_id, "outcome": "BROKE", "helper_refused": True}
            if not script.exists():
                self.sched.done(job_id, "BROKE", f"claimed path missing: {script}")
                return {"job_id": job_id, "outcome": "BROKE"}
            argv = ["py", "-3.14", str(script)]
        else:
            argv = ["py", "-3.14", "-c", cmd] if not cmd.startswith("argv:") \
                else json.loads(cmd[5:])

        # LOG-FIRST: RUNNING + argv on disk BEFORE the child exists.
        log.write_text(f"RUNNING {job_id} attempt {attempt}\n"
                       f"worker {self.worker}\nargv {argv}\n"
                       f"started {time.ctime()}\n\n", encoding="utf-8")

        r = run_tree_killed(argv, timeout_s=float(m.get("timeout_s", 1800)))

        with open(log, "a", encoding="utf-8", newline="") as fh:
            fh.write((r["out"] or "") + (("\n--- stderr ---\n" + r["err"]) if r["err"] else ""))
            fh.write(f"\n\nrc={r['rc']} timed_out={r['timed_out']} "
                     f"elapsed={r['elapsed_s']:.1f}s kill={r['kill_result']}\n")

        if r["timed_out"]:
            outcome, detail = "BROKE", f"TIMED OUT; kill: {r['kill_result']}"
        elif r["rc"] == 0:
            outcome, detail = "CLEAN", ""
        elif r["rc"] == 2:
            outcome, detail = "FINDINGS", "the job RAN and REPORTED something"
        else:
            outcome, detail = "BROKE", f"rc={r['rc']}"
        self.sched.done(job_id, outcome, detail)
        result = {"job_id": job_id, "attempt": attempt, "outcome": outcome,
                  "rc": r["rc"], "timed_out": r["timed_out"],
                  "elapsed_s": round(r["elapsed_s"], 2), "log": str(log)}
        (adir / "result.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
        return result

    def drain(self, max_jobs: int = 50) -> list[dict]:
        out = []
        for _ in range(max_jobs):
            r = self.run_one()
            if r is None:
                break
            out.append(r)
        return out
