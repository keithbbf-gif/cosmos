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
import os
import shutil
import sys
import time
import uuid
from pathlib import Path

from cosmos_clock import pythonw_exe
from cosmos_platform import run_tree_killed, makedirs
from cosmos_sched import Scheduler, SchedError


# Interpreter names allowed as argv[0] without being confined to tools_root.
# A host binary that is not one of these (e.g. /bin/echo) is the K4 argv: bypass.
_INTERP_WHITELIST = {"py", "python", "python3", "pythonw"}


class Runner:
    def __init__(self, sched: Scheduler, work_root: Path, worker_id: str):
        self.sched = sched
        self.work = Path(work_root)
        self.worker = worker_id

    def _tools_root(self) -> Path:
        # Default matches CosmosPaths ROLES["tools"] = "cosmos" (sibling of work).
        return Path(getattr(self, "tools_root", self.work.parent / "cosmos"))

    def _in_allowed_root(self, path: Path) -> bool:
        """K4: tools role OR this runner's work root (claimed adapter / attempt copies)."""
        for root in (self._tools_root(), self.work):
            try:
                path.resolve().relative_to(Path(root).resolve())
                return True
            except ValueError:
                continue
        return False

    def _refuse(self, job_id: str, detail: str, **flags) -> dict:
        self.sched.done(job_id, "BROKE", detail)
        rec = {"job_id": job_id, "outcome": "BROKE", **flags}
        adir = getattr(self, "_attempt_dir", None)
        if adir:
            (Path(adir) / "result.json").write_text(
                json.dumps(rec, indent=1), encoding="utf-8")
        return rec

    def _confine_path(self, job_id: str, path: Path) -> dict | None:
        """THE K4 boundary, shared by py: and argv:. Helper prefix wins first so the
        reason is precise; then tools_root / work_root confinement; then existence.
        Returns a refusal record, or None when the path is allowed."""
        if path.name.startswith("_"):
            return self._refuse(
                job_id,
                "helper-prefixed script refused as a job (the `_` "
                "convention, enforced in the runner)",
                helper_refused=True)
        if not self._in_allowed_root(path):
            root = self._tools_root()
            return self._refuse(
                job_id,
                f"script {path} is outside the tools root {root} and work "
                f"root {self.work} - refused (traversal is not a job)",
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
        if name not in _INTERP_WHITELIST:
            # python3.14 etc. — not python3-evil
            rest = name.split(".")[1:] if name.startswith("python3.") else None
            if not (rest and all(p.isdigit() for p in rest)):
                return False
        if not cls._looks_like_path(prog):
            return True
        try:
            resolved = Path(prog).resolve()
        except OSError:
            return False
        allowed = {Path(sys.executable).resolve()}
        pyw = Path(sys.executable).with_name("pythonw.exe")
        if pyw.is_file():
            allowed.add(pyw.resolve())
        for key in (name, "python3", "python", "pythonw", "py"):
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
        # interpreter -c CODE: skip the payload token, still confine other paths.
        skip_idx: set[int] = set()
        if interp:
            for i, tok in enumerate(rest):
                if tok == "-c" and i + 1 < len(rest):
                    skip_idx.add(i + 1)
        if not interp:
            refused = self._confine_path(job_id, Path(prog))
            if refused:
                return refused
        for i, tok in enumerate(rest):
            if i in skip_idx:
                continue
            if self._looks_like_path(tok):
                refused = self._confine_path(job_id, Path(tok))
                if refused:
                    return refused
        return None

    def run_one(self) -> dict | None:
        """Claim the next job, EXECUTE it, land the worded outcome. Returns the result
        record, or None when the queue is empty."""
        m = self.sched.claim_next(
            lanes=getattr(self, "claim_lanes", None),
            exclude_lanes=getattr(self, "claim_exclude", None))
        if m is None:
            return None
        job_id = m["job_id"]
        attempt = uuid.uuid4().hex[:10]
        adir = self.work / job_id / attempt
        makedirs(adir)
        self._attempt_dir = adir
        log = adir / "attempt.log"

        cmd = m["command"]
        # command forms: "py:<script path>" runs a python file; "argv:<json list>"
        # is explicit argv. A bare string is BAD_COMMAND — never silent python -c
        # (H4: unconstrained -c was the default submit form).
        if cmd.startswith("py:"):
            script = Path(cmd[3:].strip())
            # STAGE-7 K4 FIX (GEM IND-002, MEASURED): `py:<path>` ran ANY script on the
            # host - path-traversal RCE for anyone who can submit a job. Confine scripts
            # to tools_root (CosmosPaths role "cosmos") or this runner's work root
            # (claimed adapter copies). A script outside both is REFUSED.
            # the `_`-helper convention wins REGARDLESS of location - a helper is never a
            # job, wherever it sits (checked before confinement so the reason is precise).
            refused = self._confine_path(job_id, script)
            if refused:
                return refused
            # GUI-subsystem pythonw: `py.exe` is console and still births
            # conhost (focus steal every WD2 assign). stdout stays piped.
            argv = [pythonw_exe(), str(script)]
        elif cmd.startswith("argv:"):
            try:
                argv = json.loads(cmd[5:])
            except (ValueError, TypeError):
                return self._refuse(job_id, "argv: payload is not JSON - refused")
            refused = self._confine_argv(job_id, argv)
            if refused:
                return refused
        else:
            return self._refuse(
                job_id,
                "BAD_COMMAND: bare submit is not python -c; use py:<script> "
                "or argv:<json list>",
                bad_command=True)

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

    def write_heartbeat(self, path: Path, extra: dict | None = None) -> dict:
        """Overwrite the heartbeat on EVERY poll, job or idle.

        COMPARE USING last_run_epoch (int seconds). A timezone-naive local
        stamp was twice misread as five hours stale (bts_runner scar)."""
        from datetime import datetime, timezone as dt_timezone
        now = datetime.now().astimezone()
        rec = {
            "last_run": now.isoformat(timespec="seconds"),
            "last_run_epoch": int(now.timestamp()),
            "last_run_utc": now.astimezone(dt_timezone.utc).isoformat(timespec="seconds"),
            "worker": self.worker,
            "pid": os.getpid(),
            "queue_root": str(self.sched.root),
            "work_root": str(self.work),
            "_readme": (
                "Written on EVERY poll, pass or idle. If last_run_epoch is older "
                "than ~60s this COSMOS runner (or its scheduled task) is what "
                "failed. COMPARE USING last_run_epoch."
            ),
        }
        inst = getattr(self, "instance_id", None)
        if inst:
            rec["instance_id"] = inst
        if extra:
            rec.update(extra)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
        tmp.replace(path)
        return rec

    def _queue_snapshot(self) -> dict:
        """pending file-drops vs queued manifests — idle-empty ≠ idle-full."""
        pending: list[Path] = []
        adapter = getattr(self, "adapter", None)
        if adapter is not None:
            try:
                pending = list(adapter.scan())
            except OSError:
                pending = []
        try:
            queued = list(self.sched.queued())
        except Exception:                                             # noqa: BLE001
            queued = []
        return {
            "pending_files": len(pending),
            "pending_file_names": [p.name for p in pending[:20]],
            "manifests_queued": len(queued),
        }

    def _adapt_ingress(self, max_n: int = 1) -> list[dict]:
        adapter = getattr(self, "adapter", None)
        if adapter is None:
            return []
        return adapter.adapt(max_n=max_n)

    def _tick_name(self, results: list, snap: dict) -> str:
        if results:
            return "drained"
        if snap.get("pending_files"):
            return "stranded"
        return "idle"

    def poll_once(self, heartbeat: Path, max_jobs: int = 1) -> list[dict]:
        """One drain tick. Heartbeat lands before and after so idle is visible."""
        adapted = self._adapt_ingress(max_n=max_jobs)
        self.write_heartbeat(heartbeat, extra={"tick": "poll"})
        results = self.drain(max_jobs=max_jobs)
        adapter = getattr(self, "adapter", None)
        if adapter is not None:
            adapter.project_outcomes(results)
        snap = self._queue_snapshot()
        self.write_heartbeat(heartbeat, extra={
            "tick": self._tick_name(results, snap),
            "jobs_this_tick": len(results),
            "job_ids": [r.get("job_id") for r in results],
            "adapted_this_tick": [a.get("job_id") for a in adapted if a.get("job_id")],
            **snap,
        })
        return results

    def drain_loop(self, heartbeat: Path, interval_s: float = 15.0,
                   max_jobs: int = 1, stale_after_s: float = 7200.0,
                   stop=None, pause_gate=None) -> None:
        """Persistent poll of THIS scheduler's queue. Heartbeat every tick.

        stop: optional zero-arg callable; when it returns true the loop exits.
        pause_gate: optional zero-arg callable; when it returns true this tick
        claims nothing (heartbeat tick=paused, state=PAUSED) and does not kill
        in-flight. A Runner with no pause_gate behaves exactly as today.
        max_jobs defaults to 1 so a long job cannot starve the next heartbeat.
        stale_after_s defaults to 2 h (incumbent STAGE2A).
        """
        polls = 0
        while stop is None or not stop():
            polls += 1
            extra = {"polls": polls, "interval_s": interval_s}
            if pause_gate and pause_gate():
                extra["tick"] = "paused"
                extra["state"] = "PAUSED"
                self.write_heartbeat(heartbeat, extra=extra)
                time.sleep(max(0.05, float(interval_s)))
                continue
            adapted = self._adapt_ingress(max_n=max_jobs)
            extra["adapted_this_tick"] = [
                a.get("job_id") for a in adapted if a.get("job_id")]
            self.write_heartbeat(heartbeat, extra={**extra, "tick": "poll"})
            try:
                stale = self.sched.report_stale(stale_after_s)
            except Exception as e:                                    # noqa: BLE001
                stale = []
                extra["stale_error"] = f"{type(e).__name__}: {e}"
            extra["stale_reported"] = stale
            try:
                results = self.drain(max_jobs=max_jobs)
            except SchedError as e:
                if e.kind == "LOST_CLAIM":
                    time.sleep(0.05)
                    continue
                extra["error"] = f"[{e.kind}] {e}"
                extra["tick"] = "error"
                extra.update(self._queue_snapshot())
                self.write_heartbeat(heartbeat, extra=extra)
                raise
            except Exception as e:                                    # noqa: BLE001
                extra["error"] = f"{type(e).__name__}: {e}"
                extra["tick"] = "error"
                extra.update(self._queue_snapshot())
                self.write_heartbeat(heartbeat, extra=extra)
                raise
            adapter = getattr(self, "adapter", None)
            if adapter is not None:
                adapter.project_outcomes(results)
            snap = self._queue_snapshot()
            extra.update(snap)
            extra["jobs_this_tick"] = len(results)
            extra["job_ids"] = [r.get("job_id") for r in results]
            extra["tick"] = self._tick_name(results, snap)
            self.write_heartbeat(heartbeat, extra=extra)
            if results:
                continue
            time.sleep(max(0.05, float(interval_s)))