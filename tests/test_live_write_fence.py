#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Selftest: NO SUITE MAY WRITE THE LIVE RUNTIME ROOT.

The defect this gate closes (found by cc-cvm, 2026-08-31): heartbeat age is the
fleet's primary liveness signal. If a TEST RUN can freshen a heartbeat under
<repo>/live/logs/, then the signal is forgeable by something other than the
daemon it claims to measure -- the same defect class as a wedged route
reporting ok:true.

WHY mtime COMPARISON IS NOT A PROOF (and is refused here):
  cdeck_feed, the slot runners and watchdog2 tick every 15-30s against the live
  root. A before/after mtime diff around a test run cannot attribute a change to
  the test rather than to a daemon that ticked during it -- it is confounded by
  construction, in both directions (a false alarm from a daemon tick, a false
  clear from a test write that a daemon then overwrote).

WHAT IS MEASURED INSTEAD -- syscall interception inside the suite's own process:
  Each suite is executed in a child interpreter that installs a sys.addaudithook
  BEFORE any suite code runs. The hook sees the "open"/"os.rename"/"os.mkdir"/
  "os.remove"/... events raised by THAT PROCESS ONLY, so a daemon writing the
  same file at the same instant is invisible to it and cannot confound the
  result. Any write-intent event whose target resolves under the fenced root is
  a typed refusal (LIVE_WRITE_FENCE) raised BEFORE the operation happens, so the
  fence also prevents the write it detects. Fail-closed.

TWO CONTROLS, because a detector that never fires proves nothing:
  POSITIVE: the child reports how many write events the hook observed at all
    (to its own tempdir). Zero observed writes => the hook was not live => this
    gate FAILS as UNMEASURED rather than reporting a green.
  NEGATIVE: the same child, same hook, is pointed at a scratch "forbidden" root
    and told to write into it. The fence must refuse it. This proves the
    detector detects, without ever aiming a probe write at the real live tree.

No hard-coded paths: the repo is this file's parent's parent, the runtime root
is its `live` role, and it is accepted only on sentinel CONTENT (system=COSMOS).
An unidentifiable root is a refusal, never a skip.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The suites a static sweep flagged as referencing the live logs path, each
# fenced here against the real runtime root. (relpath, own_it): own_it=True
# means this gate also asserts rc=0. The builds/ suites are gated for the
# INTEGRITY property only -- they belong to another fence, and double-counting
# their rc would report one broken suite as two.
FENCED_SUITES = (
    ("tests/test_collector_dhx.py", True),
    ("tests/test_node_bucket_worker.py", True),
    ("tests/test_backup_clock.py", True),
    ("builds/cvm-dt/test_cvm_dt_clock.py", False),
    ("builds/health/test_cosmos_health_watchdog.py", False),
)
NO_WINDOW = 0x08000000 if os.name == "nt" else 0
TIMEOUT_S = 60          # measured worst case is ~7s; 8x headroom, still bounded

RESULTS: list[tuple[str, bool, str]] = []
LIVE_VALUE: dict = {}


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


# --------------------------------------------------------------------------
# The fence itself, shipped as a `sitecustomize` on the child's PYTHONPATH.
#
# Why sitecustomize and not an inline hook: an audit hook only sees its OWN
# process, so a suite that shells out (the health watchdog runs its module as
# `--once` in a child -- measured, not assumed) would carry its writes outside
# the fence's view. `sitecustomize` is imported by `site` at interpreter
# startup, so EVERY Python descendant that inherits PYTHONPATH installs the
# same fence before its first import, and each one appends to a shared audit
# log. That is why coverage is a claim and not a hope.
# --------------------------------------------------------------------------
FENCE_SITE = r'''
import atexit, json, os, sys

_ROOT = os.environ.get("COSMOS_FENCE_ROOT", "")
_LOG = os.environ.get("COSMOS_FENCE_LOG", "")
if _ROOT and _LOG and not getattr(sys, "_cosmos_fence", False):
    sys._cosmos_fence = True
    _FORBID = os.path.normcase(os.path.abspath(_ROOT))
    _WRITE_EVENTS = {
        "open", "os.rename", "os.remove", "os.rmdir", "os.mkdir", "os.link",
        "os.symlink", "os.truncate", "os.chmod", "os.utime", "shutil.copyfile",
        "shutil.copymode", "shutil.copystat", "shutil.move", "shutil.rmtree",
    }
    _SPAWN_EVENTS = ("subprocess.Popen", "os.exec", "os.posix_spawn")
    _S = {"writes": 0, "spawned": 0, "busy": False, "spawn_names": []}

    def _emit(rec):
        rec["pid"] = os.getpid()
        _S["busy"] = True                   # the log write is not a suite write
        try:
            with open(_LOG, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")
        except OSError:
            pass                            # a lost line is a lost line, not a pass
        finally:
            _S["busy"] = False

    def _targets(event, args):
        if event == "open":
            path, mode, flags = args
            want = any(c in mode for c in "wax+") if isinstance(mode, str) else False
            if not want and isinstance(flags, int):
                want = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                                     | os.O_APPEND | os.O_TRUNC))
            return [path] if want else []
        return [a for a in args if isinstance(a, (str, bytes, os.PathLike))]

    def _hook(event, args):
        if event in _SPAWN_EVENTS:
            # Name the program. A Python descendant inherits this fence; a
            # native binary (schtasks) cannot, and must be reported as such
            # rather than folded into the count and forgotten.
            _S["spawned"] += 1
            try:
                # subprocess.Popen: (executable, args, cwd, env). `executable`
                # is None for the ordinary Popen([...]) form, and on Windows
                # `args` arrives as a COMMAND LINE STRING, not a list -- taking
                # its basename yields nonsense ("live --once"), which would
                # silently misclassify a fenced Python child as unfenced.
                exe, cmdline = (args[0] if args else None), False
                if not exe and len(args) > 1:
                    exe, cmdline = args[1], True
                if isinstance(exe, (list, tuple)):
                    exe, cmdline = (exe[0] if exe else None), False
                if isinstance(exe, bytes):
                    exe = os.fsdecode(exe)
                if cmdline and isinstance(exe, str):
                    s = exe.strip()
                    exe = (s[1:s.find('"', 1)] if s.startswith('"')
                           and s.find('"', 1) > 0 else s.split(" ")[0])
                exe = os.path.basename(os.fspath(exe)) if exe else "?"
            except Exception:
                exe = "?"
            if len(_S["spawn_names"]) < 64:
                _S["spawn_names"].append(exe)
            return
        if event not in _WRITE_EVENTS or _S["busy"]:
            return
        _S["busy"] = True                   # no recursion through abspath/open
        try:
            for p in _targets(event, args):
                try:
                    if isinstance(p, bytes):
                        p = os.fsdecode(p)
                    ap = os.path.normcase(os.path.abspath(os.fspath(p)))
                except Exception:
                    continue
                _S["writes"] += 1
                if ap == _FORBID or ap.startswith(_FORBID + os.sep):
                    _S["busy"] = False
                    _emit({"kind": "violation", "event": event, "path": ap})
                    raise RuntimeError(
                        "REFUSED [LIVE_WRITE_FENCE] " + event + " -> " + ap)
        finally:
            _S["busy"] = False

    atexit.register(lambda: _emit({"kind": "summary", "writes": _S["writes"],
                                   "spawned": _S["spawned"],
                                   "spawn_names": _S["spawn_names"]}))
    sys.addaudithook(_hook)
'''

# The child. The fence is already installed by sitecustomize before this runs;
# the child's only job is to execute the target and report its rc.
CHILD = r'''
import os, runpy, sys

MODE = sys.argv[1]                      # "run" a suite | "probe" the fence
TARGET = sys.argv[2]
ALLOWED = sys.argv[3] if len(sys.argv) > 3 else ""   # probe: a path OUTSIDE the fence

if not getattr(sys, "_cosmos_fence", False):
    print("FENCE_RC 99")                # UNMEASURED: the fence never installed
    sys.exit(99)

rc = 0
if MODE == "probe":
    # NEGATIVE CONTROL: deliberately write inside the fenced root. The hook must
    # refuse it, and the file must not exist afterwards.
    try:
        with open(TARGET, "w", encoding="utf-8") as fh:
            fh.write("this must never land")
        rc = 90                                     # fence did NOT fire
    except RuntimeError as e:
        rc = 0 if "LIVE_WRITE_FENCE" in str(e) else 91
    # a write OUTSIDE the fence, to prove the hook blocks by location and does
    # not simply block everything (a fence that refuses all writes is not a fence)
    try:
        with open(ALLOWED, "w", encoding="utf-8") as fh:
            fh.write("ok")
    except Exception:
        rc = 92
else:
    sys.argv = [TARGET]                             # the suite sees its own argv
    try:
        runpy.run_path(TARGET, run_name="__main__")
    except SystemExit as e:
        rc = int(e.code or 0)
    except RuntimeError as e:
        if "LIVE_WRITE_FENCE" not in str(e):
            raise
        rc = 93                                     # suite tried to write live
sys.stdout.flush()
sys.exit(rc)
'''


def _is_python(name: str) -> bool:
    """A Python interpreter inherits PYTHONPATH, so it inherits the fence."""
    return Path(str(name)).stem.lower().rstrip("w0123456789.-") in ("python", "py")


def run_child(forbid: Path, mode: str, target: Path | str,
              allowed: Path | str = "") -> dict:
    """Run one fenced process tree. Returns the AGGREGATE across every Python
    process in it -- the child and any Python descendant it spawned. An empty
    audit log means the fence never installed, which is UNMEASURED, not a pass."""
    with tempfile.TemporaryDirectory(prefix="cosmos_fence_site_") as site:
        (Path(site) / "sitecustomize.py").write_text(FENCE_SITE, encoding="utf-8")
        log = Path(site) / "fence.jsonl"
        log.write_text("", encoding="utf-8")

        env = dict(os.environ)
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["COSMOS_FENCE_ROOT"] = str(forbid)
        env["COSMOS_FENCE_LOG"] = str(log)
        # F-60: descendant `--once` children inherit this so cosmos_clock
        # never invokes schtasks.exe. Native spawns are otherwise unfenced.
        env["COSMOS_SCHTASKS_SANDBOX"] = "1"
        # appended, not prepended: the fence must not shadow the suite's imports
        env["PYTHONPATH"] = os.pathsep.join(
            [p for p in (os.environ.get("PYTHONPATH", ""), site) if p])

        try:
            p = subprocess.run(
                [sys.executable, "-c", CHILD, mode, str(target), str(allowed)],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                cwd=str(REPO), timeout=TIMEOUT_S, env=env,
                creationflags=NO_WINDOW, stdin=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:
            # A killed child's atexit summary never ran, so the fence measured
            # only part of it. Report UNMEASURED; never let it read as a pass.
            return {"rc": -1, "measured": False, "procs": 0, "violations": [],
                    "writes_observed": 0, "spawned": 0, "python_spawns": 0,
                    "unfenced_spawns": [],
                    "tail": f"TIMEOUT after {TIMEOUT_S}s"}
        rows = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines() if x]

    out = ((p.stdout or "") + (p.stderr or "")).strip()
    summaries = [r for r in rows if r.get("kind") == "summary"]
    names = [n for r in summaries for n in r.get("spawn_names", [])]
    return {
        "rc": p.returncode,
        "measured": bool(summaries),
        "procs": len(summaries),
        "writes_observed": sum(int(r.get("writes", 0)) for r in summaries),
        "spawned": sum(int(r.get("spawned", 0)) for r in summaries),
        # a Python child inherits the fence; anything else is outside it
        "python_spawns": sum(1 for n in names if _is_python(n)),
        "unfenced_spawns": sorted({n for n in names if not _is_python(n)}),
        "violations": [r for r in rows if r.get("kind") == "violation"],
        "tail": out[-400:],
    }


def runtime_root() -> Path:
    """The live runtime root, by sentinel CONTENT. Existence is not identity."""
    root = REPO / "live"
    sent = json.loads((root / ".cosmos-root.json").read_text(encoding="utf-8"))
    if str(sent.get("system")) != "COSMOS":
        raise RuntimeError(f"REFUSED [IDENTITY_MISMATCH] {root}")
    return root.resolve()


def main() -> int:
    try:
        live = runtime_root()
    except Exception as e:                                            # noqa: BLE001
        print(f"test_live_write_fence UNMEASURED: {type(e).__name__}: {e}")
        return 2
    LIVE_VALUE["fenced_root"] = str(live)

    with tempfile.TemporaryDirectory(prefix="cosmos_fence_ctl_") as td:
        # ---- NEGATIVE CONTROL: the detector must detect ----
        fake = Path(td) / "fake_live"
        (fake / "logs").mkdir(parents=True)
        outside = Path(td) / "outside_the_fence.probe"
        ctl = run_child(fake, "probe", fake / "logs" / "forged_heartbeat.json",
                        outside)
        check("control: the fence refuses a write inside the fenced root",
              lambda: ctl["measured"] and ctl["rc"] == 0
              and len(ctl["violations"]) == 1)
        check("control: the refusal is typed and names the event + path",
              lambda: ctl["violations"][0]["event"] == "open"
              and ctl["violations"][0]["path"].endswith("forged_heartbeat.json"))
        check("control: the forged file never landed (refused BEFORE the write)",
              lambda: not (fake / "logs" / "forged_heartbeat.json").exists())
        check("control: writes OUTSIDE the fenced root are still allowed",
              lambda: outside.is_file())
        LIVE_VALUE["control"] = {"rc": ctl["rc"], "violations": ctl["violations"]}

    # ---- THE GATE: each suite, fenced against the real runtime root ----
    per_suite = {}
    for rel, own_it in FENCED_SUITES:
        suite = REPO / rel
        name = suite.name
        if not suite.is_file():                      # absent gate = refusal
            check(f"{name}: suite present to be fenced", lambda: False)
            continue
        rec = run_child(live, "run", suite)
        per_suite[rel] = {k: rec.get(k) for k in
                          ("rc", "measured", "procs", "writes_observed",
                           "spawned", "python_spawns", "unfenced_spawns",
                           "violations")}
        check(f"{name}: the audit hook was live (writes observed > 0)",
              lambda r=rec: r["measured"] and int(r.get("writes_observed", 0)) > 0)
        check(f"{name}: ZERO writes under the live runtime root",
              lambda r=rec: r.get("violations") == [])
        # Every PYTHON process in the tree must have reported. One that did not
        # is an unmeasured writer, which would make the "zero writes" above a
        # partial claim -- so it fails, it never passes. Native binaries cannot
        # inherit a Python audit hook; they are named in unfenced_spawns and are
        # this gate's stated residual, not a silent gap.
        check(f"{name}: every Python process in the tree was fenced "
              f"({rec.get('procs')} reported, {rec.get('python_spawns')} spawned)",
              lambda r=rec: int(r.get("procs", 0)) == 1 + int(r.get("python_spawns", 0)))
        if own_it:
            check(f"{name}: still passes under the fence (rc=0)",
                  lambda r=rec: r["rc"] == 0)
        if rel == "builds/health/test_cosmos_health_watchdog.py":
            check(f"{name}: no native unfenced spawns (F-60)",
                  lambda r=rec: r.get("unfenced_spawns") == [])
    LIVE_VALUE["suites"] = per_suite

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = [(lab, err) for lab, ok, err in RESULTS if not ok]
    for lab, ok, err in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {lab}" + (f"  {err}" if err else ""))
    print(f"test_live_write_fence {passed}/{len(RESULTS)} passed")
    for name, rec in per_suite.items():
        if rec.get("rc") not in (0, None):
            print(f"  tail[{name}] rc={rec['rc']}")
    print("LIVE_VALUE " + json.dumps(LIVE_VALUE, default=str))
    return 0 if not failed else 1


def test_live_write_fence():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
