#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_sandbox - OpenHands-split SANDBOX layer (not session, not harness).

SGH steal-map item 3: isolate a worker so it cannot reach host pens.

Windows Job-Object spawn is the default host backend:
  kill-on-close, 8 procs, no extra drive maps, no CREATE_BREAKAWAY_FROM_JOB.
HOST_PEN refuse is the whole V:\\ volume (not only V:\\Ai / OpenWork / Desktop)
plus Desktop. Attempt dirs live under live/work/attempts via the work role.

Daytona / E2B / Modal are NAMED. Daytona and E2B are composed as opt-in
transports (backend=daytona|e2b). Modal stays named, not composed. Default
backend remains Job-Object on the host (backend=job). Missing credential is
typed NO_CREDENTIALS — never a silent host spawn. --selftest is fake (no
live cloud spend). GET folds never mkdir. kernel_attached is always false.

This is the sandbox only. Session stays cosmos_session. Harness stays
dispatch. Not a scheduler. Not a cron. Not a second Core. Does not
replace spawn_in_job.

    py -3.14 cosmos\\cosmos_sandbox.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SCHEMA = "cosmos-sandbox/1"
WORKER = "cosmos-sandbox"
DEFAULT_BACKEND = "job"
COMPOSED_BACKENDS = ("job", "daytona", "e2b")
NAMED_BACKENDS = ("job", "daytona", "e2b", "modal")
NAMED_NOT_COMPOSED = ("modal",)
ACTIVE_PROCESS_LIMIT = 8
ATTEMPT_REL = "attempts"
FAKE_ENV = "COSMOS_SANDBOX_FAKE"
BACKEND_ENV = "COSMOS_SANDBOX_BACKEND"
CRED_SUFFIX = "_api_key.txt"

# Job-Object limit flags. Kill-on-close + active-process cap. Breakaway is
# NOT set — a child that can leave the job can reach host pens.
JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_LIMIT_BREAKAWAY_OK = 0x00000800
JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK = 0x00001000
JobObjectExtendedLimitInformation = 9
CREATE_NO_WINDOW = 0x08000000
CREATE_BREAKAWAY_FROM_JOB = 0x01000000

# Host pens the worker must not sit on. V:\\ is the whole volume (item 3).
# Desktop stays a pen even when it is not on V:\\.
HOST_PEN_VOLUME = "V:"
HOST_PEN_DESKTOP = "desktop"


class SandboxError(RuntimeError):
    """kind in {BAD_BACKEND, BAD_INPUT, BROKE, HOST_PEN, NO_CREDENTIALS,
    NO_DIR, NO_ROOT, NOT_COMPOSED, REFUSED, SHELL_REFUSED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def _norm_win(path: str | Path) -> str:
    s = str(path or "").replace("/", "\\")
    if s.upper().startswith("\\\\?\\UNC\\"):
        return s[8:]
    if s.upper().startswith("\\\\?\\"):
        return s[4:]
    return s


def is_v_volume(path: str | Path) -> bool:
    """True for any path on the V:\\ volume (V:\\, V:\\Ai, V:\\Research4, …)."""
    s = _norm_win(path).lstrip()
    return len(s) >= 2 and s[0].upper() == "V" and s[1] == ":"


def is_desktop(path: str | Path) -> bool:
    parts = [p for p in str(path or "").replace("\\", "/").split("/") if p]
    return any(p.lower() == HOST_PEN_DESKTOP for p in parts)


def host_pen_kind(path: str | Path) -> str | None:
    """Return the pen name if `path` is a host pen, else None."""
    if is_v_volume(path):
        return HOST_PEN_VOLUME
    if is_desktop(path):
        return HOST_PEN_DESKTOP
    return None


def refuse_cwd(cwd: str | Path) -> Path:
    """Refuse a worker cwd on V:\\ (whole volume) or Desktop.

    Workers cannot reach V:\\. This is the steal-map isolation pin — not
    only V:\\Ai / OpenWork / Desktop.
    """
    if cwd is None or str(cwd).strip() == "":
        raise SandboxError("BAD_INPUT", "cwd is required")
    raw = Path(str(cwd))
    pen = host_pen_kind(raw)
    if pen is not None:
        raise SandboxError(
            "HOST_PEN",
            f"worker cwd {raw} sits on host pen {pen} — sandbox cannot "
            f"reach V:\\ or Desktop")
    return raw


def resolve_backend(name: str | None = None) -> str:
    raw = name if name is not None else os.environ.get(BACKEND_ENV)
    n = str(raw or DEFAULT_BACKEND).strip().lower() or DEFAULT_BACKEND
    if n in NAMED_NOT_COMPOSED:
        raise SandboxError(
            "NOT_COMPOSED",
            f"{n} is NAMED in the sandbox docstring and is not composed")
    if n not in COMPOSED_BACKENDS:
        raise SandboxError(
            "BAD_BACKEND",
            f"backend={n!r} unknown; composed={COMPOSED_BACKENDS} "
            f"named_not_composed={NAMED_NOT_COMPOSED}")
    return n


def attempt_dir(paths, attempt_id: str) -> Path:
    """live/work/attempts/<id> path. Does not mkdir (GET must stay inert)."""
    aid = "".join(
        ch if ch.isalnum() or ch in "-_." else "-"
        for ch in str(attempt_id or "").strip())[:80]
    if not aid or aid in (".", "..") or ".." in aid:
        raise SandboxError("BAD_INPUT", f"unsafe attempt_id {attempt_id!r}")
    return paths.role("work") / ATTEMPT_REL / aid


def prepare_attempt(paths, attempt_id: str) -> Path:
    """POST/spawn may mkdir the attempt dir. GET must not call this."""
    dest = attempt_dir(paths, attempt_id)
    refuse_cwd(dest)
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def credential_path(paths, backend: str) -> Path:
    b = resolve_backend(backend)
    if b == "job":
        raise SandboxError("BAD_BACKEND", "job backend has no cloud credential")
    return paths.config(f"{b}{CRED_SUFFIX}")


def credentials_present(paths, backend: str) -> bool:
    """Read-only presence. is_file() never mkdir's the key."""
    try:
        p = credential_path(paths, backend)
    except SandboxError:
        return False
    try:
        return p.is_file() and p.stat().st_size > 0
    except OSError:
        return False


def require_credentials(paths, backend: str) -> Path:
    if paths is None:
        raise SandboxError("NO_ROOT", f"{backend} requires a verified COSMOS root")
    p = credential_path(paths, backend)
    if not p.is_file() or p.stat().st_size <= 0:
        raise SandboxError(
            "NO_CREDENTIALS",
            f"no {backend} credential at {p.name} (Keith places it; "
            f"sandbox does not silent-spawn the host Job-Object)")
    return p


def fake_on(explicit: bool = False) -> bool:
    if explicit:
        return True
    return str(os.environ.get(FAKE_ENV) or "").strip() in ("1", "true", "yes")


def snapshot(paths=None, backend: str | None = None) -> dict:
    """Read-only backend fold. Never mkdir.

    GET never creates attempt dirs, credential files, or cloud workspaces.
    backend=daytona / e2b report credential presence only. kernel_attached
    stays false — this layer is not Core.
    """
    b = resolve_backend(backend)
    rec = {
        "schema": SCHEMA,
        "backend": b,
        "default_backend": DEFAULT_BACKEND,
        "composed": list(COMPOSED_BACKENDS),
        "named": list(NAMED_BACKENDS),
        "named_not_composed": list(NAMED_NOT_COMPOSED),
        "kernel_attached": False,
        "is_scheduler": False,
        "is_core": False,
        "get_mkdir": False,
        "live_cloud": False,
        "host_pen": HOST_PEN_VOLUME + "\\",
        "attempt_root": f"work/{ATTEMPT_REL}",
        "split": "sandbox",
        "openhands_split": ("session", "harness", "sandbox"),
    }
    if b == "job":
        rec["kind"] = "JOB"
        rec["kill_on_close"] = True
        rec["active_process_limit"] = ACTIVE_PROCESS_LIMIT
        rec["extra_drives_mapped"] = False
        return rec
    present = False if paths is None else credentials_present(paths, b)
    rec["kind"] = "FAKE" if present else "NO_CREDENTIALS"
    rec["credential_present"] = present
    rec["credential_name"] = f"{b}{CRED_SUFFIX}"
    return rec


def _job_record(cwd: Path, attempt_id: str | None) -> dict:
    return {
        "schema": SCHEMA,
        "backend": "job",
        "kind": "JOB",
        "ok": False,
        "kill_on_close": True,
        "active_process_limit": ACTIVE_PROCESS_LIMIT,
        "extra_drives_mapped": False,
        "breakaway": False,
        "kernel_attached": False,
        "is_scheduler": False,
        "cwd": str(cwd),
        "attempt_id": attempt_id,
    }


def _create_windows_job():
    """Create a kill-on-close 8-proc Job Object. Caller closes the handle."""
    import ctypes
    from ctypes import wintypes

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

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateJobObjectW.restype = wintypes.HANDLE
    k32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    k32.SetInformationJobObject.restype = wintypes.BOOL
    k32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD,
    ]
    k32.AssignProcessToJobObject.restype = wintypes.BOOL
    k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]

    job = k32.CreateJobObjectW(None, None)
    if not job:
        raise OSError("CreateJobObjectW failed")
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    flags = (
        JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        | JOB_OBJECT_LIMIT_ACTIVE_PROCESS
    )
    # Explicitly clear breakaway so the child cannot leave for a host pen.
    flags &= ~(
        JOB_OBJECT_LIMIT_BREAKAWAY_OK | JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK
    )
    info.BasicLimitInformation.LimitFlags = flags
    info.BasicLimitInformation.ActiveProcessLimit = ACTIVE_PROCESS_LIMIT
    ok = k32.SetInformationJobObject(
        job, JobObjectExtendedLimitInformation,
        ctypes.byref(info), ctypes.sizeof(info))
    if not ok:
        k32.CloseHandle(job)
        raise OSError("SetInformationJobObject failed")
    return job, k32


def spawn_in_job(argv, *, cwd, timeout_s: float = 30,
                 extra_drives=None, attempt_id: str | None = None) -> dict:
    """Windows Job-Object spawn. Default host backend. Do not replace.

    Kill-on-close, 8-proc cap, no extra drive maps, no breakaway. cwd on
    V:\\ is HOST_PEN. On non-Windows the same contract is recorded and the
    child is process-group isolated (CI / --selftest).
    """
    if isinstance(argv, str):
        raise SandboxError(
            "SHELL_REFUSED",
            "spawn_in_job takes an argv LIST — a string implies a shell")
    if not argv:
        raise SandboxError("BAD_INPUT", "argv is empty")
    if extra_drives:
        raise SandboxError(
            "REFUSED",
            "job-object child must not map extra drives")
    cwd_p = refuse_cwd(cwd)
    if not cwd_p.is_dir():
        raise SandboxError("NO_DIR", f"cwd is not a directory: {cwd_p}")

    rec = _job_record(cwd_p, attempt_id)
    env = os.environ.copy()
    env.pop("COSMOS_MAPPED_DRIVES", None)
    env.pop("COSMOS_EXTRA_DRIVES", None)
    # Job child does not inherit a mapped-drive shopping list.
    rec["env_extra_drives"] = False

    t0 = time.time()
    job = None
    k32 = None
    try:
        if os.name == "nt":
            job, k32 = _create_windows_job()
            # CREATE_BREAKAWAY_FROM_JOB is deliberately absent.
            proc = subprocess.Popen(
                list(argv), cwd=str(cwd_p), env=env, shell=False,
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
            handle = int(getattr(proc, "_handle", 0) or 0)
            if handle and not k32.AssignProcessToJobObject(job, handle):
                proc.kill()
                proc.wait()
                raise SandboxError("BROKE", "AssignProcessToJobObject failed")
        else:
            proc = subprocess.Popen(
                list(argv), cwd=str(cwd_p), env=env, shell=False,
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, start_new_session=True)
        try:
            out_b, err_b = proc.communicate(timeout=timeout_s)
            rec["rc"] = proc.returncode
            rec["timed_out"] = False
        except subprocess.TimeoutExpired:
            proc.kill()
            out_b, err_b = proc.communicate()
            rec["rc"] = None
            rec["timed_out"] = True
        rec["out"] = (out_b or b"").decode("utf-8", "replace")
        rec["err"] = (err_b or b"").decode("utf-8", "replace")
        rec["ok"] = rec["rc"] == 0 and not rec["timed_out"]
    except SandboxError:
        raise
    except OSError as e:
        raise SandboxError("BROKE", f"spawn_in_job: {e}") from e
    finally:
        if job and k32 is not None:
            k32.CloseHandle(job)
    rec["elapsed_s"] = time.time() - t0
    rec["job_object"] = os.name == "nt"
    return rec


def _fake_cloud_spawn(backend: str, *, cwd: Path,
                      attempt_id: str | None) -> dict:
    return {
        "schema": SCHEMA,
        "backend": backend,
        "kind": "FAKE",
        "ok": True,
        "live_cloud": False,
        "kernel_attached": False,
        "is_scheduler": False,
        "host_spawn": False,
        "cwd": str(cwd),
        "attempt_id": attempt_id,
        "note": f"{backend} --selftest is fake; no live cloud spend",
    }


def _cloud_spawn(backend: str, argv, *, cwd, paths, timeout_s: float,
                 attempt_id: str | None, fake: bool) -> dict:
    """Opt-in Daytona/E2B transport. Creds first. Never silent host spawn."""
    require_credentials(paths, backend)
    cwd_p = refuse_cwd(cwd)
    if fake_on(fake):
        return _fake_cloud_spawn(backend, cwd=cwd_p, attempt_id=attempt_id)
    raise SandboxError(
        "REFUSED",
        f"live {backend} spend is not composed; --selftest is fake "
        f"(no cloud HTTP)")


def spawn(argv, *, cwd, paths=None, backend: str | None = None,
          timeout_s: float = 30, extra_drives=None,
          attempt_id: str | None = None, fake: bool = False) -> dict:
    """Compose named backends. Default is Job-Object. Not a scheduler.

    backend=job      → spawn_in_job (host).
    backend=daytona  → opt-in; NO_CREDENTIALS if the key is missing.
    backend=e2b      → opt-in; NO_CREDENTIALS if the key is missing.
    Missing cloud credential never falls through to spawn_in_job.
    """
    if extra_drives:
        raise SandboxError(
            "REFUSED",
            "sandbox child must not map extra drives")
    refuse_cwd(cwd)
    b = resolve_backend(backend)
    if b == "job":
        return spawn_in_job(
            argv, cwd=cwd, timeout_s=timeout_s,
            extra_drives=None, attempt_id=attempt_id)
    return _cloud_spawn(
        b, argv, cwd=cwd, paths=paths, timeout_s=timeout_s,
        attempt_id=attempt_id, fake=fake)


def _selftest() -> int:
    import tempfile

    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results: list[tuple[str, bool, str]] = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_sandbox_"))
    root = install(td / "live", tree_id="spike-sandbox")
    paths = CosmosPaths(root)
    ws = td / "ws"
    ws.mkdir()

    rec = snapshot(paths, backend=None)
    job = spawn_in_job(
        [sys.executable, "-c", "print('job-ok')"], cwd=ws, timeout_s=15)
    extra_refused = False
    try:
        spawn_in_job([sys.executable, "-c", "x"], cwd=ws, extra_drives=["Z:"])
    except SandboxError as e:
        extra_refused = e.kind == "REFUSED"
    check(
        "1 default backend is job; Job-Object kill-on-close 8 procs; "
        "no extra drives",
        lambda: rec["backend"] == "job"
        and rec["default_backend"] == DEFAULT_BACKEND
        and rec["kill_on_close"] is True
        and rec["active_process_limit"] == ACTIVE_PROCESS_LIMIT
        and rec["extra_drives_mapped"] is False
        and job["ok"] is True
        and job["kill_on_close"] is True
        and job["active_process_limit"] == 8
        and job["extra_drives_mapped"] is False
        and extra_refused)

    v_refused = False
    try:
        refuse_cwd(r"V:\Research4\not-ai")
    except SandboxError as e:
        v_refused = e.kind == "HOST_PEN"
    desk_refused = False
    try:
        refuse_cwd(r"C:\Users\Papa\Desktop\scratch")
    except SandboxError as e:
        desk_refused = e.kind == "HOST_PEN"
    check(
        "2 cwd on V:\\ (whole volume) and Desktop is HOST_PEN",
        lambda: v_refused and desk_refused
        and is_v_volume(r"V:\Ai")
        and is_v_volume(r"V:\OPENWORK")
        and is_v_volume(r"V:\Research4"))

    host_calls: list = []
    real_job = spawn_in_job

    def spy_job(*a, **k):
        host_calls.append((a, k))
        return real_job(*a, **k)

    globals()["spawn_in_job"] = spy_job
    no_cred = False
    try:
        spawn([sys.executable, "-c", "x"], cwd=ws, paths=paths,
              backend="daytona")
    except SandboxError as e:
        no_cred = e.kind == "NO_CREDENTIALS"
    finally:
        globals()["spawn_in_job"] = real_job
    check(
        "3 backend=daytona missing credential is NO_CREDENTIALS, "
        "not a silent host spawn",
        lambda: no_cred and host_calls == [])

    attempts = paths.role("work") / ATTEMPT_REL
    before = attempts.exists()
    get_d = snapshot(paths, backend="daytona")
    get_e = snapshot(paths, backend="e2b")
    check(
        "4 GET backend=daytona|e2b never mkdir; kernel_attached is false",
        lambda: get_d["kind"] == "NO_CREDENTIALS"
        and get_e["kind"] == "NO_CREDENTIALS"
        and get_d["kernel_attached"] is False
        and get_e["kernel_attached"] is False
        and get_d["get_mkdir"] is False
        and rec["kernel_attached"] is False
        and attempts.exists() is before
        and not (paths.config() / f"daytona{CRED_SUFFIX}").exists())

    e2b_kind = None
    try:
        spawn([sys.executable, "-c", "x"], cwd=ws, paths=paths, backend="e2b")
    except SandboxError as e:
        e2b_kind = e.kind
    modal_kind = None
    try:
        resolve_backend("modal")
    except SandboxError as e:
        modal_kind = e.kind
    src = Path(__file__).read_text(encoding="utf-8")
    check(
        "5 e2b missing creds NO_CREDENTIALS; modal NAMED not composed; "
        "not a scheduler / Core",
        lambda: e2b_kind == "NO_CREDENTIALS"
        and modal_kind == "NOT_COMPOSED"
        and rec["is_scheduler"] is False
        and rec["is_core"] is False
        and "import cosmos_sch" + "ed" not in src
        and "from cosmos_sch" + "ed" not in src)

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d/%d (Job-Object default; Daytona/E2B opt-in fake; "
          "V:\\ HOST_PEN; GET never mkdir; kernel_attached false; "
          "not a scheduler)"
          % ("PASS" if not failed else "FAIL",
             len(results) - len(failed), len(results)))
    return 0 if not failed else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="cosmos_sandbox",
        description="COSMOS sandbox (OpenHands split). Job-Object default. "
                    "Daytona/E2B opt-in fake --selftest. Not a scheduler.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--backend", default=None,
                    help="job (default) | daytona | e2b")
    ap.add_argument("--root", default=None)
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.root:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from cosmos_paths import CosmosPaths
        rec = snapshot(CosmosPaths(a.root), backend=a.backend)
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("kernel_attached") is False else 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
