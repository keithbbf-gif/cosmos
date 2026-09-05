#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cosmos_cc_driver.py  --  COSMOS Claude Code node worker.

Drives the Claude Code CLI (`claude -p`) as a COSMOS execution rail. This is the
bootstrap that lets Claude Code CODE COSMOS unattended: Keith runs `claude` /login
ONCE (the OAuth token then persists on disk under ~/.claude), and this daemon runs
every subsequent work order through `claude -p` with no further login.

Canon:
  - No hard-coded paths: the root is passed with --root; every path resolves under it.
  - Fail-closed: auth failure -> status NEEDS_LOGIN, NO execution (never spins blindly).
    A job that fails -> failed/ + incident; the daemon keeps running (a bad job is not
    a daemon crash).
  - Never-delete: jobs move pending -> done/ or failed/, never unlinked.
  - Windowless on Windows (CREATE_NO_WINDOW); PAUSE-aware; heartbeated.
  - COW disposes: this worker PROPOSES via PR/patch; landing on the live tree stays a
    gateway action. It writes results + the agent's stdout; it does not touch cosmos/ core.

Work order = one JSON file dropped in <root>/live/queue/_lanes/cc/ :
  { "id": "health_watchdog_p0",
    "task": "<the full task prompt for claude -p>",
    "model": "claude-fable-5",          # optional; omitted -> claude default
    "cwd":   "<abs path>",              # optional; default = root
    "timeout": 1800 }                    # optional seconds; default 1800

Launch (Windows, after one-time `claude` /login):
  py -3.14 builds\\cc_driver\\cosmos_cc_driver.py --root V:\\A\\Ai\\COSMOS\\live --once
  py -3.14 builds\\cc_driver\\cosmos_cc_driver.py --root V:\\A\\Ai\\COSMOS\\live --interval 20
"""
import argparse
import json
import os
import platform
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cc_outcome  # typed outcome classifier (F-59): process outcome != work outcome

NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def claude_bin() -> list[str]:
    """The CLI to drive. Overridable via COSMOS_CC_CLAUDE_BIN so the driver's own
    timeout/refusal/crash paths can be exercised by a stub agent under test --
    an untestable failure path is how F-59 survived. Value is either a plain
    program name or a JSON list (argv prefix)."""
    raw = os.environ.get("COSMOS_CC_CLAUDE_BIN")
    if not raw:
        return ["claude"]
    raw = raw.strip()
    if raw.startswith("["):
        return [str(x) for x in json.loads(raw)]
    return [raw]


ENGINES = ("claude", "gbw")
GROK_MAX_TURNS = "60"   # matches cosmos_dispatch.GROK_MAX_TURNS, marked PROVEN
                        # there; identical on purpose so the two grok paths
                        # cannot drift apart without someone noticing.


def grok_bin() -> list[str]:
    """GBW = Grok Build Worker (`grok`, Grok Build TUI). Same override shape as
    claude_bin, via COSMOS_CC_GROK_BIN, so this engine's timeout/refusal/crash
    paths are testable with a stub too -- an untestable failure path is how
    F-59 survived."""
    raw = os.environ.get("COSMOS_CC_GROK_BIN")
    if not raw:
        return ["grok"]
    raw = raw.strip()
    if raw.startswith("["):
        return [str(x) for x in json.loads(raw)]
    return [raw]


def engine_bin(engine: str) -> list[str]:
    return grok_bin() if engine == "gbw" else claude_bin()


def engine_argv(engine: str, task: str, model, cwd) -> list[str]:
    """The argv for one work order on the chosen engine.

    Both auto-approve edits (claude: --permission-mode acceptEdits, grok:
    --always-approve). grok needs --cwd explicitly -- it does not inherit the
    parent's directory the way `claude -p` does -- so the lane's cwd is passed
    rather than assumed.
    """
    if engine == "gbw":
        argv = grok_bin() + ["--single", task,
                             "--output-format", "plain",
                             "--always-approve",
                             "--max-turns", GROK_MAX_TURNS,
                             "--cwd", str(cwd)]
        if model:
            argv += ["-m", str(model)]
        return argv
    argv = claude_bin() + ["-p", task, "--permission-mode", "acceptEdits"]
    if model:
        argv += ["--model", str(model)]
    return argv


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def env_descriptor(engine: str = "claude") -> dict:
    """Describe the environment the agent runs IN — bound to a real artifact, not asserted."""
    try:
        cv = subprocess.run(engine_bin(engine) + ["--version"], capture_output=True, text=True,
                            timeout=15, creationflags=NO_WINDOW).stdout.strip()
    except Exception:
        cv = f"{engine}:unavailable"
    return {
        "host": socket.gethostname(),
        "os": platform.platform(),
        "python": platform.python_version(),
        "engine": engine,
        "claude": cv,  # e.g. "2.1.247 (Claude Code)" — the surface, self-reported by the binary
    }


def default_report() -> Path:
    """Resolve the Desktop build-log path (OneDrive-redirected Desktop preferred)."""
    od = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer")
    up = os.environ.get("USERPROFILE") or str(Path.home())
    for base in ([od] if od else []) + [up]:
        d = Path(base) / "Desktop"
        if d.is_dir():
            return d / "COSMOS_selfbuild.txt"
    return Path(up) / "COSMOS_selfbuild.txt"


def append_report(report: Path, kind: str, jid: str, meta: str, body: str) -> None:
    """Append one timestamped INPUT or OUTPUT block. Append-only, never truncate."""
    if report is None:
        return
    bar = "=" * 72
    block = (f"{bar}\n[{_now()}] {kind:<6} job={jid} {meta}\n"
             f"{'-' * 72}\n{body.rstrip()}\n")
    try:
        report.parent.mkdir(parents=True, exist_ok=True)
        with open(report, "a", encoding="utf-8") as fh:
            fh.write(block)
    except Exception:
        pass  # the report is a mirror; its failure must never stop the build


class Paths:
    """Resolve every role under one verified root. No path arithmetic elsewhere."""

    def __init__(self, root: Path, report: Path = None,
                 lane_name: str = "cc", engine: str = "claude"):
        self.root = root
        self.engine = engine   # "claude" or "gbw" (Grok Build Worker)
        self.report = report
        self.env = {}   # environment descriptor, set at startup
        # Parallel lanes (2026-08-30). Throughput needs more than one worker,
        # but parallel agents on ONE tree is the one-writer scar this system has
        # already paid for once. Each lane therefore carries a DISJOINT
        # write-fence, stated in its work orders, so two workers never contend
        # for the same file.
        self.lane_name = lane_name
        self.lane = root / "queue" / "_lanes" / lane_name
        self.done = self.lane / "done"
        self.failed = self.lane / "failed"
        # F-59: a wall-clock kill that still produced deliverables is NOT a
        # failure. It gets its own terminal bucket so the lane counters stop
        # under-reporting completed work, and so nothing requeues finished work.
        self.timed_out = self.lane / "timed_out"
        self.returns = self.lane / "returns"
        self.state = root / "state"
        self.control = self.state / "control" / "PAUSE.flag"
        self.heartbeat = self.state / f"cc_driver_{lane_name}_heartbeat.json"
        for d in (self.lane, self.done, self.failed, self.timed_out,
                  self.returns, self.state):
            d.mkdir(parents=True, exist_ok=True)

    def route_dir(self, route: str) -> Path:
        """Map a cc_outcome route name to this lane's terminal directory."""
        return {"done": self.done, "failed": self.failed,
                "timed_out": self.timed_out}.get(route, self.failed)


def paused(p: Paths) -> bool:
    try:
        flag = json.loads(p.control.read_text(encoding="utf-8"))
        return str(flag.get("state", "RUNNING")).upper() != "RUNNING"
    except FileNotFoundError:
        return False
    except Exception:
        # Unreadable control flag = fail-closed: treat as paused, do not execute.
        return True


def claude_ready(default_cwd: Path) -> tuple[bool, str]:
    """Preflight: is `claude` present and authed? Fail-closed if not."""
    try:
        p = subprocess.run(
            claude_bin() + ["-p", "Reply with exactly: CC-READY"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(default_cwd), timeout=90, creationflags=NO_WINDOW,
            stdin=subprocess.DEVNULL,
        )
        out = (p.stdout or "") + (p.stderr or "")
        if "CC-READY" in out:
            return True, "ok"
        if "Not logged in" in out or "/login" in out:
            return False, "NEEDS_LOGIN"
        return False, f"unexpected: {out.strip()[:200]}"
    except FileNotFoundError:
        return False, "claude CLI not found on PATH"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def heartbeat(p: Paths, status: str, done_count: int, current: str = "") -> None:
    payload = {
        "node": "cc_driver", "ts": _now(), "status": status,
        "jobs_done_session": done_count, "current": current,
    }
    try:
        tmp = p.heartbeat.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=1), encoding="utf-8")
        os.replace(tmp, p.heartbeat)  # atomic
    except Exception:
        pass


def emit_incident(p: Paths, job_id: str, kind: str, detail: str) -> None:
    inc = p.state / f"cc_incident_{job_id}_{int(time.time())}.json"
    try:
        inc.write_text(json.dumps(
            {"node": "cc_driver", "ts": _now(), "job": job_id,
             "kind": kind, "detail": detail[:2000]}, indent=1), encoding="utf-8")
    except Exception:
        pass


def _file_bad_order(p: Paths, job_path: Path, jid: str, kind: str, detail: str) -> str:
    """A malformed work order is its own typed outcome, not a generic failure."""
    now = time.time()
    rec = cc_outcome.classify(
        rc=None, timed_out=False, exception=None, stdout="", stderr=detail,
        t0=now, t1=now, fence=None, base=job_path.parent, bad_order=kind)
    _finish(p, job_path, jid, {"agent": "CC", "kind": "claude-code", "id": jid,
                               "ts_start": _now(), "error": detail}, rec)
    emit_incident(p, jid, kind, detail)
    return rec["outcome"]


def run_job(p: Paths, job_path: Path, root: Path) -> bool:
    try:
        job = json.loads(job_path.read_text(encoding="utf-8"))
    except Exception as e:
        _file_bad_order(p, job_path, job_path.stem, "BAD_JOB_JSON", str(e))
        return False

    jid = str(job.get("id") or job_path.stem)
    task = job.get("task")
    if not task:
        _file_bad_order(p, job_path, jid, "NO_TASK", "work order has no 'task' field")
        return False
    model = job.get("model")
    cwd = job.get("cwd") or str(root.parent)  # repo tree = root's parent (…/COSMOS)
    timeout = int(job.get("timeout", 1800))
    # The write-fence the order declared: where this job's deliverables must land.
    # Explicit `fence`, else the canonical "write ONLY under <path>" contract line.
    fence = cc_outcome.fence_from_job(job)
    if fence is not None and not fence.is_absolute():
        fence = Path(cwd) / fence

    engine = getattr(p, "engine", "claude")
    argv = engine_argv(engine, task, model, cwd)

    # Desktop build-log: record the INPUT verbatim, timestamped, before running.
    agent_label = "GBW/Grok-Build" if engine == "gbw" else "CC/Claude-Code"
    agent_env = (f"agent={agent_label} model={model or 'default'} "
                 f"env=[host={p.env.get('host','?')} claude={p.env.get('claude','?')} cwd={cwd}]")
    append_report(p.report, "INPUT", jid, agent_env, task)

    t0 = time.time()
    full = ""
    err = ""
    rc = None
    timed_out = False
    exception = None
    result = {"agent": ("GBW" if engine == "gbw" else "CC"),
              "kind": ("grok-build" if engine == "gbw" else "claude-code"),
              "engine": engine, "id": jid, "model": model,
              "ts_start": _now(), "cwd": cwd, "fence": str(fence) if fence else None}
    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=cwd, timeout=timeout,
            creationflags=NO_WINDOW, stdin=subprocess.DEVNULL,
        )
        full = proc.stdout or ""
        err = proc.stderr or ""
        rc = proc.returncode
    except subprocess.TimeoutExpired as e:
        # The kill discards nothing: whatever the agent had already written to the
        # pipe is on the exception, and it is the only place the MANDATORY LAST
        # LINE report can still be recovered from. The old code threw it away and
        # then called the job failed on no evidence at all.
        timed_out = True
        full = _as_text(e.stdout)
        err = _as_text(e.stderr)
    except Exception as e:
        exception = f"{type(e).__name__}: {e}"
        err = exception
    t1 = time.time()

    # P5 anti-loss: full stdout to a sidecar ALWAYS, including the timeout path.
    (p.returns / f"{jid}_result.json.stdout.txt").write_text(full, encoding="utf-8")

    # Classify BEFORE filing. The process outcome (rc / killed / crashed) and the
    # work outcome (did the report and the deliverables land) are separate facts.
    verdict = cc_outcome.classify(
        rc=rc, timed_out=timed_out, exception=exception, stdout=full, stderr=err,
        t0=t0, t1=t1, fence=fence, base=Path(cwd))

    result.update({
        "rc": rc, "secs": round(t1 - t0, 1),
        "stdout_tail": full[-4000:], "stderr_tail": err[-1500:],
        "outcome": verdict["outcome"], "route": verdict["route"],
        "requeue": verdict["requeue"], "work_landed": verdict["work_landed"],
        "evidence": verdict["evidence"], "verdict": verdict,
    })
    if timed_out:
        result["error"] = "timeout"
    elif exception:
        result["error"] = exception

    # Desktop build-log: record the OUTPUT verbatim, timestamped, after running.
    out_body = full if full else (result.get("error") or "(no output)")
    append_report(p.report, "OUTPUT", jid,
                  f"agent=CC/Claude-Code outcome={verdict['outcome']} rc={rc} "
                  f"secs={result['secs']} host={p.env.get('host','?')}", out_body)

    _finish(p, job_path, jid, result, verdict)
    return verdict["route"] == "done"


def _as_text(blob) -> str:
    """TimeoutExpired.stdout is str under text mode but bytes if the kill raced
    the decoder. Never let the evidence path throw."""
    if blob is None:
        return ""
    if isinstance(blob, bytes):
        return blob.decode("utf-8", "replace")
    return str(blob)


def _finish(p: Paths, job_path: Path, jid: str, result: dict, verdict: dict) -> None:
    """Write the result + the typed outcome sidecar, then file the order by its
    WORK outcome. A TIMED_OUT_WITH_OUTPUT order can never again be mistaken for
    an agent that produced nothing: the outcome file names which it was and cites
    the artifacts."""
    result.setdefault("outcome", verdict["outcome"])
    (p.returns / f"{jid}_result.json").write_text(
        json.dumps(result, indent=1), encoding="utf-8")
    (p.returns / f"{jid}_outcome.json").write_text(
        json.dumps({"id": jid, "ts": _now(), "lane": p.lane_name, **verdict}, indent=1),
        encoding="utf-8")
    if verdict["route"] != "done":
        emit_incident(p, jid, verdict["outcome"], cc_outcome.summarize(verdict))
    _move(job_path, p.route_dir(verdict["route"]))


def _move(src: Path, dst_dir: Path) -> None:
    """Never-delete: move, never unlink. Collision-safe."""
    dst = dst_dir / src.name
    if dst.exists():
        dst = dst_dir / f"{src.stem}_{int(time.time())}{src.suffix}"
    os.replace(src, dst)


def grok_ready() -> tuple[bool, str]:
    """Preflight for GBW: is `grok` on PATH? Never spawn a TUI or `claude -p`."""
    try:
        p = subprocess.run(
            grok_bin() + ["--version"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=15, creationflags=NO_WINDOW, stdin=subprocess.DEVNULL,
        )
        out = ((p.stdout or "") + (p.stderr or "")).strip()
        if p.returncode == 0 or "grok" in out.lower():
            return True, "ok"
        return False, f"unexpected: {out[:200]}"
    except FileNotFoundError:
        return False, "grok CLI not found on PATH"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def engine_ready(engine: str, default_cwd: Path) -> tuple[bool, str]:
    if engine == "gbw":
        return grok_ready()
    return claude_ready(default_cwd)


def cycle(p: Paths, root: Path, state: dict) -> None:
    if paused(p):
        heartbeat(p, "PAUSED", state["done"])
        return
    engine = getattr(p, "engine", "claude")
    ready, why = engine_ready(engine, root.parent)
    if not ready:
        status = ("NEEDS_LOGIN" if why == "NEEDS_LOGIN"
                  else ("GROK_UNAVAILABLE" if engine == "gbw" else "CLAUDE_UNAVAILABLE"))
        heartbeat(p, status, state["done"])
        if state["done"] == 0 and not state.get("warned"):
            emit_incident(p, "preflight", "AUTH", why)
            state["warned"] = True
        return
    pending = sorted(p.lane.glob("*.json"))
    if not pending:
        heartbeat(p, "IDLE", state["done"])
        return
    for job_path in pending:
        heartbeat(p, "RUNNING", state["done"], current=job_path.stem)
        if run_job(p, job_path, root):
            state["done"] += 1
    heartbeat(p, "IDLE", state["done"])


def do_login(root: Path) -> int:
    """Open the Claude Code login NATIVELY (runs on the host, where a process persists
    and a browser exists — the one thing a turn-based sandbox cannot do). Inherits the
    real console so `claude` can open the browser and take the pasted code interactively.
    On success the token is saved under ~/.claude and every later `claude -p` is authed
    with no further login."""
    print("[cc_driver] opening Claude Code login — a browser will open; authorize, and")
    print("[cc_driver] paste the code back here if prompted. (one time; token then persists)")
    try:
        rc = subprocess.call(claude_bin() + ["setup-token"])  # interactive; inherits console
    except FileNotFoundError:
        print("REFUSE: `claude` not found on PATH — install Claude Code first.", file=sys.stderr)
        return 2
    if rc != 0:
        print(f"[cc_driver] login command exited rc={rc}", file=sys.stderr)
        return rc
    ok, why = claude_ready(root.parent)
    print("[cc_driver] LOGIN VERIFIED — Claude Code is authed." if ok
          else f"[cc_driver] login not verified: {why}", file=sys.stderr if not ok else sys.stdout)
    return 0 if ok else 3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="COSMOS Claude Code node worker")
    ap.add_argument("--root", required=True, help="runtime root (…\\COSMOS\\live)")
    ap.add_argument("--login", action="store_true",
                    help="open the Claude Code login natively, then continue if --once/--interval given")
    ap.add_argument("--once", action="store_true", help="run one cycle and exit")
    ap.add_argument("--interval", type=int, default=20, help="loop seconds (default 20)")
    ap.add_argument("--engine", default="claude", choices=list(ENGINES),
                    help="which CLI to drive: claude (Claude Code) or gbw "
                         "(Grok Build Worker). Default claude.")
    ap.add_argument("--lane", default="cc",
                    help="lane under queue/_lanes; parallel workers use one "
                         "lane each with disjoint write-fences")
    ap.add_argument("--report", default=None,
                    help="append-only build log (default: Desktop\\COSMOS_selfbuild.txt); "
                         "pass 'off' to disable")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"REFUSE: root does not exist: {root}", file=sys.stderr)
        return 2
    if args.report == "off":
        report = None
    elif args.report:
        report = Path(args.report)
    else:
        report = default_report()
    p = Paths(root, report, lane_name=args.lane, engine=args.engine)
    p.env = env_descriptor(args.engine)
    state = {"done": 0}
    print(f"[cc_driver] build log -> {report if report else '(disabled)'}")
    # Session banner: record the environment this build ran IN, once per launch.
    append_report(
        report, "SESSION", "cc_driver",
        f"agent=CC (Claude Code)",
        f"host={p.env.get('host')}\nos={p.env.get('os')}\n"
        f"python={p.env.get('python')}\nclaude={p.env.get('claude')}\n"
        f"root={root}\nlane={p.lane}",
    )

    if args.login:
        rc = do_login(root)
        if rc != 0:
            return rc
        # bare `--login` (no run mode) = log in and stop.
        if not args.once and "--interval" not in (argv or sys.argv):
            return 0

    print(f"[cc_driver] root={root} lane={p.lane} {'once' if args.once else f'every {args.interval}s'}")
    if args.once:
        cycle(p, root, state)
        print(f"[cc_driver] done={state['done']}")
        return 0
    while True:
        try:
            cycle(p, root, state)
        except KeyboardInterrupt:
            print("[cc_driver] stopped")
            return 0
        except Exception as e:  # a cycle error must never kill the daemon
            emit_incident(p, "cycle", "CYCLE_ERROR", f"{type(e).__name__}: {e}")
        time.sleep(max(3, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
