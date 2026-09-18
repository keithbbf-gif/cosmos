#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Attempt sandbox — OpenHands split, COSMOS-shaped.

Session (ledger) / harness (this) / sandbox (Job-Object child).
Workers run under live/work/attempts/<id>, never on host pens.
Job-Object is the default host backend (kill-on-close, 8 procs).
Daytona and E2B are composed transports behind this facade; unconfigured
→ typed UNCONFIGURED, never a silent host cwd. Modal stays named, not
composed. Not a scheduler. Live vendor HTTP is UNMEASURED until Keith
pastes creds (config/sandbox_backend.json + key files).

    py -3.14 cosmos\\cosmos_sandbox.py --selftest
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_workspace import WorkspaceError, refuse_tree_cwd  # noqa: E402

SCHEMA = "cosmos-sandbox/1"
BACKEND_CONFIG = "sandbox_backend.json"
HOST_PENS = (
    r"V:\Ai",
    r"V:\OPENWORK",
    r"C:\Users\Papa\OneDrive",
)
JOB_KILL_ON_CLOSE = 0x2000
JOB_ACTIVE_PROCESS = 0x0008
COMPOSED_BACKEND = "job_object"
REMOTE_BACKENDS = ("daytona", "e2b")
NAMED_NOT_COMPOSED = ("modal",)
KEY_FILES = {
    "daytona": "daytona_api_key.txt",
    "e2b": "e2b_api_key.txt",
}


class SandboxError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _is_v_volume(path) -> bool:
    s = str(path or "").replace("/", "\\")
    if s.upper().startswith("\\\\?\\"):
        s = s[4:]
    return len(s) >= 2 and s[0].upper() == "V" and s[1] == ":"


def load_backend_config(paths=None) -> dict:
    """Read-only. Never mkdir. Missing/empty file = default job_object."""
    rec = {
        "schema": "cosmos-sandbox-backend/1",
        "backend": COMPOSED_BACKEND,
        "kind": "UNCONFIGURED",
    }
    if paths is None:
        return rec
    p = paths.config(BACKEND_CONFIG)
    if not p.is_file():
        return rec
    try:
        raw = p.read_bytes()
        if not raw.strip():
            return rec
        d = json.loads(raw.decode("utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        rec["error"] = "UNPARSEABLE"
        return rec
    if not isinstance(d, dict):
        rec["error"] = "UNPARSEABLE"
        return rec
    chosen = str(d.get("backend") or COMPOSED_BACKEND).strip().lower()
    if chosen in ("job", "job-object"):
        chosen = COMPOSED_BACKEND
    rec["backend"] = chosen or COMPOSED_BACKEND
    rec["kind"] = "MEASURED"
    rec["file"] = BACKEND_CONFIG
    return rec


def credentials_present(paths, name: str) -> bool:
    """Key file presence. is_file never mkdir's the key. Keith pastes."""
    if paths is None:
        return False
    fname = KEY_FILES.get(str(name or "").strip().lower())
    if not fname:
        return False
    try:
        p = paths.config(fname)
        return p.is_file() and p.stat().st_size > 0
    except OSError:
        return False


def pick_backend(name=None, paths=None) -> str:
    """Facade. Explicit name wins. Unconfigured remote defaults to Job-Object."""
    raw = str(name or "").strip().lower()
    if raw in ("job", "job-object"):
        return COMPOSED_BACKEND
    if raw:
        return raw
    cfg = load_backend_config(paths)
    chosen = str(cfg.get("backend") or COMPOSED_BACKEND).strip().lower()
    if chosen in ("job", "job-object", ""):
        return COMPOSED_BACKEND
    if chosen in REMOTE_BACKENDS and not credentials_present(paths, chosen):
        return COMPOSED_BACKEND
    return chosen


def snapshot(paths=None) -> dict:
    """HTTP GET fold. Never mkdir. Never spawns. Never a scheduler."""
    composed = COMPOSED_BACKEND if os.name == "nt" else "posix_subprocess"
    remote = {
        name: ("READY" if credentials_present(paths, name) else "UNCONFIGURED")
        for name in REMOTE_BACKENDS
    }
    return {
        "schema": SCHEMA,
        "kind": "MEASURED",
        "composed": composed,
        "backends": [COMPOSED_BACKEND, *REMOTE_BACKENDS],
        "remote": remote,
        "named_not_composed": list(NAMED_NOT_COMPOSED),
        "host_pens": list(HOST_PENS),
        "kernel_attached": False,
        "is_scheduler": False,
        "note": "Daytona/E2B composed transports; unconfigured = Job-Object. "
                "GET never mkdir. Modal named, not composed.",
    }
