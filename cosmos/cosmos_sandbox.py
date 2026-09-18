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


def assert_no_host_map(backend: str, drives=None, listing=None) -> None:
    """Remote worker must not map V:\\ or host pens. Stub / recorded refuse."""
    for p in list(drives or []) + list(listing or []):
        if _is_v_volume(p):
            raise SandboxError(
                "BACKEND_ISOLATION",
                f"{backend} worker must not map {p}")
        for pen in HOST_PENS:
            try:
                Path(str(p)).resolve().relative_to(Path(pen).resolve())
            except (OSError, ValueError):
                continue
            raise SandboxError(
                "BACKEND_ISOLATION",
                f"{backend} worker must not map host pen {pen}")


def spawn_remote(name, argv, cwd, *, paths=None, timeout_s: float = 30.0) -> dict:
    """Daytona/E2B transport. Unconfigured → typed refuse, never host spawn."""
    del argv, cwd, timeout_s  # payload is isolation-checked; no live HTTP
    if not credentials_present(paths, name):
        raise SandboxError(
            "UNCONFIGURED",
            f"{name} backend unconfigured (Keith pastes "
            f"config/{KEY_FILES.get(name, name + '_api_key.txt')}; "
            f"never silent host cwd)")
    assert_no_host_map(name, drives=[], listing=("V:\\", r"V:\Ai", r"V:\OPENWORK"))
    raise SandboxError(
        "UNMEASURED",
        f"live {name} vendor call not bound; isolation recorded")


def spawn_backend(name, argv, cwd, *, timeout_s: float = 30.0,
                  paths=None, extra_drives=None) -> dict:
    """Fail-closed backend picker. Explicit remote + no key = UNCONFIGURED."""
    if extra_drives:
        raise SandboxError(
            "BACKEND_ISOLATION",
            "sandbox child must not map extra drives")
    backend = pick_backend(name, paths=paths)
    if backend in ("", COMPOSED_BACKEND, "posix_subprocess"):
        return spawn_in_job(argv, cwd, timeout_s=timeout_s)
    if backend in REMOTE_BACKENDS:
        return spawn_remote(backend, argv, cwd, paths=paths, timeout_s=timeout_s)
    if backend in NAMED_NOT_COMPOSED:
        raise SandboxError("NOT_COMPOSED",
                           f"{backend} is a named backend, not composed")
    raise SandboxError("UNKNOWN_BACKEND", f"sandbox backend {backend!r}")


def attempt_dir(paths, attempt_id: str | None = None) -> Path:
    aid = str(attempt_id or uuid.uuid4().hex[:12])
    d = paths.role("work", "attempts", aid)
    d.mkdir(parents=True, exist_ok=True)
    return d


def assert_sandbox_cwd(workspace, live_root, repo_tree=None) -> Path:
    ws = refuse_tree_cwd(workspace, live_root, repo_tree=repo_tree)
    for pen in HOST_PENS:
        try:
            host = Path(pen).resolve()
            ws.relative_to(host)
        except (OSError, ValueError):
            continue
        raise SandboxError("HOST_PEN", f"worker cwd refuses {pen}")
    return ws


def spawn_in_job(argv, cwd, *, timeout_s: float = 30.0,
                 extra_drives=None) -> dict:
    """Run argv inside a Windows Job Object (kill-on-close, 8 procs).

    POSIX: plain subprocess. Does not map extra drives. Does not become a scheduler.
    Job-Object cwd may sit under live/work (on V:\\) — Daytona/E2B is the
    isolation that Job-Object-on-host cannot give. extra_drives always refuse.
    """
    if extra_drives:
        raise SandboxError(
            "BACKEND_ISOLATION",
            "job-object child must not map extra drives")
    cwd = str(Path(cwd).resolve())
    if os.name != "nt":
        r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout_s)
        return {"ok": r.returncode == 0, "rc": r.returncode,
                "job": False, "stdout": (r.stdout or "")[:400]}
    import ctypes
    from ctypes import wintypes

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateJobObjectW.restype = wintypes.HANDLE
    k32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        ]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    job = k32.CreateJobObjectW(None, None)
    if not job:
        raise SandboxError("JOB_CREATE", f"CreateJobObject failed {ctypes.get_last_error()}")
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = JOB_KILL_ON_CLOSE | JOB_ACTIVE_PROCESS
    info.BasicLimitInformation.ActiveProcessLimit = 8
    JobObjectExtendedLimitInformation = 9
    k32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
    if not k32.SetInformationJobObject(
            job, JobObjectExtendedLimitInformation, ctypes.byref(info),
            ctypes.sizeof(info)):
        k32.CloseHandle(job)
        raise SandboxError("JOB_LIMIT", f"SetInformationJobObject {ctypes.get_last_error()}")
    try:
        proc = subprocess.Popen(
            argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, creationflags=0x08000000)
        if not k32.AssignProcessToJobObject(job, int(proc._handle)):
            proc.kill()
            raise SandboxError("JOB_ASSIGN", f"AssignProcessToJobObject {ctypes.get_last_error()}")
        out, _ = proc.communicate(timeout=timeout_s)
        return {"ok": proc.returncode == 0, "rc": proc.returncode,
                "job": True, "pid": proc.pid, "stdout": (out or "")[:400]}
    finally:
        k32.CloseHandle(job)


def attach_to_kernel(kernel, adapters=None, boot_compose: bool = False, **_kw) -> dict:
    """Fail-open satellite. Missing Daytona/E2B does not abort READY."""
    del adapters, boot_compose, _kw
    try:
        snap = snapshot(getattr(kernel, "paths", None))
        kernel.sandbox = snap
        return {"ok": True, "composed": snap.get("composed"),
                "remote": snap.get("remote")}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def _selftest() -> int:
    from cosmos_paths import CosmosPaths, write_sentinel
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_sbx_"))
    live = td / "live"
    write_sentinel(live, tree_id="sbx-selftest")
    (live / "work").mkdir(parents=True)
    (live / "config").mkdir(parents=True)
    p = CosmosPaths(live)
    ws = attempt_dir(p, "t1")
    check("attempt dir is under work/attempts",
          lambda: "attempts" in str(ws) and ws.is_dir())
    check("sandbox cwd accepts attempt dir",
          lambda: assert_sandbox_cwd(ws, live, repo_tree=td) == ws.resolve())
    try:
        (live / "state").mkdir(exist_ok=True)
        assert_sandbox_cwd(live / "state", live, repo_tree=td)
        results.append(("sandbox cwd refuses live/state", False, "did not refuse"))
    except (SandboxError, WorkspaceError):
        results.append(("sandbox cwd refuses live/state", True, ""))
    rec = spawn_in_job([sys.executable, "-c", "print('sbx-ok')"], ws, timeout_s=10)
    check("job spawn prints sbx-ok",
          lambda: rec.get("ok") and "sbx-ok" in rec.get("stdout", ""))
    snap = snapshot(p)
    check("snapshot names job_object; daytona/e2b UNCONFIGURED; modal named",
          lambda: snap["schema"] == SCHEMA
          and snap["composed"] in (COMPOSED_BACKEND, "posix_subprocess")
          and snap["remote"]["daytona"] == "UNCONFIGURED"
          and snap["remote"]["e2b"] == "UNCONFIGURED"
          and "modal" in snap["named_not_composed"]
          and snap["kind"] == "MEASURED")
    host_calls = []
    real_job = spawn_in_job

    def spy_job(*a, **k):
        host_calls.append(1)
        return real_job(*a, **k)

    try:
        globals()["spawn_in_job"] = spy_job
        spawn_backend("daytona", [sys.executable, "-c", "pass"], ws, paths=p)
        results.append(("daytona unconfigured is UNCONFIGURED", False, "did not"))
    except SandboxError as e:
        results.append(("daytona unconfigured is UNCONFIGURED",
                        e.kind == "UNCONFIGURED" and not host_calls, e.kind))
    finally:
        globals()["spawn_in_job"] = real_job
    try:
        spawn_backend("e2b", [sys.executable, "-c", "pass"], ws, paths=p)
        results.append(("e2b unconfigured is UNCONFIGURED", False, "did not"))
    except SandboxError as e:
        results.append(("e2b unconfigured is UNCONFIGURED",
                        e.kind == "UNCONFIGURED", e.kind))
    try:
        assert_no_host_map("daytona", listing=("V:\\",))
        results.append(("listing V:\\ is BACKEND_ISOLATION", False, "did not"))
    except SandboxError as e:
        results.append(("listing V:\\ is BACKEND_ISOLATION",
                        e.kind == "BACKEND_ISOLATION", e.kind))
    try:
        spawn_in_job([sys.executable, "-c", "pass"], ws, extra_drives=["Z:"])
        results.append(("extra drives refuse", False, "did not"))
    except SandboxError as e:
        results.append(("extra drives refuse",
                        e.kind == "BACKEND_ISOLATION", e.kind))
    try:
        spawn_backend("modal", [sys.executable, "-c", "pass"], ws, paths=p)
        results.append(("modal is NOT_COMPOSED", False, "did not"))
    except SandboxError as e:
        results.append(("modal is NOT_COMPOSED",
                        e.kind == "NOT_COMPOSED", e.kind))
    check("default pick_backend is job_object when remote unconfigured",
          lambda: pick_backend(paths=p) == COMPOSED_BACKEND)
    att = attach_to_kernel(type("K", (), {"paths": p})())
    check("attach_to_kernel fail-open does not abort",
          lambda: att.get("ok") is True
          and att.get("remote", {}).get("daytona") == "UNCONFIGURED")
    failed = [r for r in results if not r[1]]
    for label, ok, err in results:
        print(("PASS" if ok else "FAIL"), label, err)
    print("sandbox selftest", f"{len(results)-len(failed)}/{len(results)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_selftest() if "--selftest" in sys.argv else 2)
