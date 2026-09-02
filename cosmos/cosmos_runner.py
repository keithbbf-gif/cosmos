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
import shutil
import sys
import time
import uuid
from pathlib import Path

from cosmos_platform import run_tree_killed, makedirs
from cosmos_sched import Scheduler


# Interpreter names allowed as argv[0] without being confined to tools_root.
# A host binary that is not one of these (e.g. /bin/echo) is the K4 argv: bypass.
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

    @staticmethod
    def _interp_basename(prog: str) -> str:
        name = Path(prog).name.lower()
        return name[:-4] if name.endswith(".exe") else name

    @classmethod
    def _is_whitelisted_interp(cls, prog: str) -> bool:
        """True for a real Python launcher (bare name, this process, or PATH).
        A random file that merely *named* python3 is not an interpreter."""
        name = cls._interp_basename(prog)
        if name not in _INTERP_WHITELIST and not name.startswith("python3"):
            return False
        if not cls._looks_like_path(prog):
            return True
        try:
            resolved = Path(prog).resolve()
        except OSError:
            return False
        allowed = {Path(sys.executable).resolve()}
        for key in (name, "python3", "python", "py"):
            found = shutil.which(key)
            if found:
                allowed.add(Path(found).resolve())
        return resolved in allowed

    def _confine_argv(self, job_id: str, argv) -> dict | None:
        """GUARD REST-1 (K4 argv: bypass). Confine SCRIPT paths only:

        * whitelisted interpreter + -c  → nothing to confine, run
        * script UNDER tools_root       → run
        * script / host binary OUTSIDE  → refuse
        """
        if (not isinstance(argv, list) or not argv
                or not all(isinstance(x, str) for x in argv)):
            return self._refuse(
                job_id, "argv: form must be a JSON list of strings - refused")
        prog = argv[0]
        rest = argv[1:]
        interp = self._is_whitelisted_interp(prog)
        # interpreter -c CODE has no script file - do not treat flags or the
        # payload as paths, and do not demand the launcher sit under tools_root.
        if interp and "-c" in rest:
            return None
        if not interp:
            refused = self._confine_path(job_id, Path(prog))
            if refused:
                return refused
        for tok in rest:
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
        if cmd.startswith("wo:"):
            # WORK-ORDER form: wo:<wo_id> or wo:drain. The desk ALWAYS writes
            # Output.json (typed kind on rail failure) - that is the measured
            # scar (gemini.cmd died rc=41, no Output file). Never routed to
            # gemini.cmd; Google prove/ping is gem-api / bts_gem.ask.
            return self._run_work_order(job_id, attempt, adir, log, cmd[3:].strip())
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

    def _run_work_order(self, job_id: str, attempt: str, adir: Path,
                        log: Path, spec: str) -> dict:
        """Claimed wo: job: run the desk, land Output.json, word the outcome.

        A rail failure is FINDINGS/BROKE WITH an Output file (typed kind), never
        FAILED-with-missing-file. gemini.cmd is not constructible from this path.
        """
        from cosmos_work_order import WorkOrderDesk, WorkOrderError
        log.write_text(f"RUNNING {job_id} attempt {attempt}\n"
                       f"worker {self.worker}\nwo {spec}\n"
                       f"started {time.ctime()}\n\n", encoding="utf-8")
        try:
            desk = getattr(self, "work_orders", None)
            if desk is None:
                paths = getattr(self, "paths", None)
                ledger = getattr(self.sched, "ledger", None)
                if paths is None or ledger is None:
                    raise WorkOrderError(
                        "NO_RAIL",
                        "runner has no WorkOrderDesk and no paths+ledger to "
                        "compose one - a work-order without a desk is not a job")
                desk = WorkOrderDesk(paths, ledger,
                                     gem_rail=getattr(self, "gem_rail", None),
                                     dom_worker=getattr(self, "dom_worker", None))
            if spec in ("", "drain"):
                results = desk.drain()
                payload = {"drained": [r.get("wo_id") for r in results],
                           "outputs": results}
                ok_all = all(r.get("ok") for r in results) if results else True
                kind = "API" if ok_all else (results[0].get("kind") if results else "OK")
            else:
                payload = desk.run(spec)
                ok_all = bool(payload.get("ok"))
                kind = payload.get("kind") or "API"
        except WorkOrderError as e:
            payload = {"ok": False, "kind": e.kind, "detail": str(e)[:300]}
            ok_all, kind = False, e.kind
        except Exception as e:                                        # noqa: BLE001
            payload = {"ok": False, "kind": "BROKE",
                       "detail": f"{type(e).__name__}: {e}"[:300]}
            ok_all, kind = False, "BROKE"
        with open(log, "a", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(payload, indent=1))
            fh.write(f"\n\nok={ok_all} kind={kind}\n")
        if ok_all:
            outcome, detail = "CLEAN", ""
        elif kind in ("UNREACHABLE", "SESSION_EXPIRED", "AUTH_REQUIRED",
                      "NO_RAIL", "NOT_PERMITTED"):
            outcome, detail = "FINDINGS", f"{kind}: rail typed failure (Output written)"
        else:
            outcome, detail = "BROKE", f"{kind}: {payload.get('detail', '')}"[:200]
        self.sched.done(job_id, outcome, detail)
        result = {"job_id": job_id, "attempt": attempt, "outcome": outcome,
                  "ok": ok_all, "kind": kind, "log": str(log),
                  "wo": payload}
        (adir / "result.json").write_text(json.dumps(result, indent=1),
                                          encoding="utf-8")
        return result

    def drain(self, max_jobs: int = 50) -> list[dict]:
        out = []
        for _ in range(max_jobs):
            r = self.run_one()
            if r is None:
                break
            out.append(r)
        return out