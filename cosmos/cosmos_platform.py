#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_platform - THE PLATFORM ADAPTER (F5 builder). One layer owns encoding,
quoting, path length, line endings, and process containment - no tool touches shell
semantics directly (scar R9: ten scars in the Windows quoting/encoding family).

RULES ENFORCED HERE, NOWHERE ELSE:
  * subprocess: UTF-8 on BOTH ends (child env + parent decode) - the monitor-that-
    worked-when-watched scar (S-134): tools died on emoji the moment stdout was
    redirected. Never text=True without encoding=.
  * NO SHELL, EVER: argv lists only. A command that needs cmd's parser is a command
    carrying %, !, ^ hazards (three punctuation traps in one day, 2026-08-02).
  * timeout kills the TREE on Windows (taskkill /T) - a timed-out wrapper that
    orphans descendants reports a kill it did not finish (OA port hazard 7).
  * write_text_lf(): explicit newline discipline - text-mode '\n'->'\r\n' translation
    broke fs_write with IntegrityError (S-59); here the CALLER SAYS which endings.
  * extended(): MAX_PATH for read AND create (the cosmos_paths spike's banked finding).
"""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from cosmos_paths import extended


class PlatformError(RuntimeError):
    """kind in {TIMEOUT, SHELL_REFUSED, KILL_INCOMPLETE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def run(argv: list[str], timeout_s: float = 120, cwd: str | None = None) -> dict:
    """The ONE way COSMOS starts a process. Returns {rc, out, err, elapsed_s,
    timed_out, kill_result}. A string command is REFUSED - argv only."""
    if isinstance(argv, str):
        raise PlatformError("SHELL_REFUSED",
                            "run() takes an argv LIST - a string implies a shell, and "
                            "a shell has opinions about punctuation (%, !, emoji, ^)")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    t0 = time.time()
    kill_result = None
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout_s, cwd=cwd, env=env,
                           shell=False)
        rc, out, err, timed_out = p.returncode, p.stdout or "", p.stderr or "", False
    except subprocess.TimeoutExpired as e:
        timed_out, rc = True, None
        out = e.stdout if isinstance(e.stdout, str) else ""
        err = e.stderr if isinstance(e.stderr, str) else ""
        kill_result = "TimeoutExpired: python killed the direct child; descendants "\
                      "not guaranteed - RECORDED, not assumed clean"
    return {"rc": rc, "out": out, "err": err, "elapsed_s": time.time() - t0,
            "timed_out": timed_out, "kill_result": kill_result}


def run_tree_killed(argv: list[str], timeout_s: float = 120,
                    cwd: str | None = None) -> dict:
    """run() with WHOLE-TREE kill on timeout (Windows: taskkill /T /F on the pid).
    The kill outcome is REPORTED - a kill that half-worked must say so."""
    if isinstance(argv, str):
        raise PlatformError("SHELL_REFUSED", "argv list only")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    t0 = time.time()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            cwd=cwd, env=env, shell=False)
    try:
        out_b, err_b = proc.communicate(timeout=timeout_s)
        return {"rc": proc.returncode,
                "out": out_b.decode("utf-8", "replace"),
                "err": err_b.decode("utf-8", "replace"),
                "elapsed_s": time.time() - t0, "timed_out": False, "kill_result": None}
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            k = subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace")
            kill_result = f"taskkill /T rc={k.returncode}: {(k.stdout or k.stderr).strip()[:150]}"
        else:
            proc.kill()
            kill_result = "SIGKILL (non-Windows; process group not chased)"
        try:
            out_b, err_b = proc.communicate(timeout=10)
        except Exception:                                             # noqa: BLE001
            out_b, err_b = b"", b""
            kill_result += " | KILL_INCOMPLETE: child did not reap in 10s"
        return {"rc": None, "out": out_b.decode("utf-8", "replace"),
                "err": err_b.decode("utf-8", "replace"),
                "elapsed_s": time.time() - t0, "timed_out": True,
                "kill_result": kill_result}


def write_text_lf(path: Path, content: str) -> None:
    """Explicit LF endings, no platform translation (S-59)."""
    with open(extended(path), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


def write_text_crlf(path: Path, content: str) -> None:
    with open(extended(path), "w", encoding="utf-8", newline="\r\n") as fh:
        fh.write(content)


def makedirs(path: Path) -> None:
    """Directory creation through the adapter - the banked spike finding: MAX_PATH
    bites at CREATION."""
    os.makedirs(extended(path), exist_ok=True)