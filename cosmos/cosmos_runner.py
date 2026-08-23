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


# Bare interpreter names allowed as argv[0]. Anything else is a PATH and must sit
# inside tools_root - the same boundary py: jobs already honor. A name that is not
# on this list and not under the tools root is the K4 argv: bypass, refused.
_INTERP_WHITELIST = {"py", "python", "python3"}


class Runner:
    def __init__(self, sched: Scheduler, work_root: Path, worker_id: str):
        self.sched = sched
        self.work = Path(work_root)
        self.worker = worker_id

    def _tools_root(self) -> Path:
        return Path(getattr(self, "tools_root", self.work.parent / "cosmos"))

    def _refuse(self, job_id: str, detail: str, **flags) -> dict:
        self.sched.done(job_id, "BROKE", detail)
        return {"job_id": job_id, "outcome": "BROKE", **flags}

    def _confine_path(self, job_id: str, path: Path) -> dict | None:
        """THE K4 boundary, shared by py: and argv:. Helper prefix wins first so the
        reason is precise; then tools_root confinement; then existence. Returns a
        refusal record, or None when the path is allowed."""
        if path.name.startswith("_"):
            return self._refuse(
                job_id,
                "helper-prefixed script refused as a job (the `_` "
                "convention, enforced in the runner)",
                helper_refused=True)
        root = self._tools_root()
        try:
            path.resolve().relative_to(Path(root).resolve())
        except ValueError:
            return self._refuse(
                job_id,
                f"script {path} is outside the tools root {root} - "
                f"refused (traversal is not a job)",
                traversal_refused=True)
        if not path.exists():
            return self._refuse(job_id, f"claimed path missing: {path}")
        return None

    @staticmethod
    def _looks_like_path(token: str) -> bool:
        """A token that names a file (absolute, slash-bearing, or a script suffix)
        is a path - flags like -c / -3.14 are not."""
        if not token or token.startswith("-"):
            return False
        return (Path(token).is_absolute()
                or "/" in token or "\\" in token
                or token.lower().endswith((".py", ".cmd", ".bat", ".exe", ".ps1")))

    def _confine_argv(self, job_id: str, argv) -> dict | None:
        """GUARD REST-1 (K4 argv: bypass): the argv: form used to skip tools_root
        and run any host binary. Same confinement + interpreter whitelist as py:."""
        if (not isinstance(argv, list) or not argv
                or not all(isinstance(x, str) for x in argv)):
            return self._refuse(
                job_id, "argv: form must be a JSON list of strings - refused")
        prog = argv[0]
        bare = Path(prog).name
        if not (bare in _INTERP_WHITELIST and not self._looks_like_path(prog)):
            refused = self._confine_path(job_id, Path(prog))
            if refused:
                return refused
        for tok in argv[1:]:
            if self._looks_like_path(tok):
                refused = self._confine_path(job_id, Path(tok))
                if refused:
                    return refused
        return None

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
            # STAGE-7 K4 FIX (GEM IND-002, MEASURED): `py:<path>` ran ANY script on the
            # host - path-traversal RCE for anyone who can submit a job. Confine scripts
            # to an allowed tools root (self.tools_root, default the runner's work parent
            # / "tools"); a script outside it is REFUSED. A job that needs a new tool
            # registers it there first - the tools dir is the boundary, not the filesystem.
            # the `_`-helper convention wins REGARDLESS of location - a helper is never a
            # job, wherever it sits (checked before confinement so the reason is precise).
            refused = self._confine_path(job_id, script)
            if refused:
                return refused
            argv = ["py", "-3.14", str(script)]
        elif cmd.startswith("argv:"):
            try:
                argv = json.loads(cmd[5:])
            except ValueError:
                return self._refuse(job_id, "argv: payload is not JSON - refused")
            refused = self._confine_argv(job_id, argv)
            if refused:
                return refused
        else:
            argv = ["py", "-3.14", "-c", cmd]

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
