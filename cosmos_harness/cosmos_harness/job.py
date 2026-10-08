"""Process-tree section of L7. Filesystem policy stays in ``jail.py``.

On Windows this opens an unnamed job, sets kill-on-job-close and an active
process limit, and reads the flags back. ``probe`` does not assign the
current process. Assigning this process to a kill-on-close job would take
the harness down with the job.

``run_child`` is the only function that assigns a process, and it assigns
the child it just created. The child is created suspended, placed in the
job with the class-9 extended limits, then resumed. If that assignment
fails, the child is killed and ``UNENCLOSED_CHILD`` is raised. A missing
enclosure is not a red oracle and it is not a retry without the job.

``active_limit`` defaults to 4, the same cap ``probe`` sets. ``None`` keeps
kill-on-close and does not cap the process count. The OpenCode door passes
``None`` because that process tree does not fit in four. Assignment failure
still kills the child. The default stays 4 for the oracle and the one-process
chat child.

``wipe_proof`` is always false. A job object without a restricted token, a
denied network, and a measured child assignment is not a wipe-proof
enclosure. The status reason stays ``policy_only`` until that proof exists.
``refuse_unsandboxed_retry`` always raises. A missing primitive does not
become a retry without the job.

``native/job_object.c`` probes the same class-9 limits in C. It does not
assign a child. The Python loader is what the tests run.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from cosmos_harness.refuse import Refuse

JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JobObjectExtendedLimitInformation = 9
CREATE_SUSPENDED = 0x00000004
CREATE_NO_WINDOW = 0x08000000
THREAD_SUSPEND_RESUME = 0x0002
TH32CS_SNAPTHREAD = 0x00000004
_ACTIVE_LIMIT = 4


@dataclass(frozen=True)
class Enclosure:
    """What this process can honestly say about the sandbox."""

    kind: str
    available: bool
    reason: str
    wipe_proof: bool
    flags: int


class UnsandboxedRetryRefused(Refuse):
    """The Codex hole: sandbox failed, so the run continued without one."""

    def __init__(self, why: str) -> None:
        super().__init__("UNSANDBOXED_RETRY", why)


def refuse_unsandboxed_retry(why: str = "sandbox_unavailable") -> None:
    """Always raises. Policy does not evaporate."""
    raise UnsandboxedRetryRefused(why)


def _text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return value


def _plain(argv: list[str], *, cwd: Path, env: dict[str, str], timeout: float) -> tuple[int, str, str]:
    """A child with no job object. Used where Windows is not the host."""
    try:
        proc = subprocess.run(
            argv,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
            shell=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return 124, _text(exc.stdout), _text(exc.stderr) + "\ntimeout"
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _kernel():
    """kernel32 with the job and thread calls this module uses."""
    import ctypes
    from ctypes import wintypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
    ]
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.QueryInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p,
    ]
    kernel.QueryInformationJobObject.restype = wintypes.BOOL
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Thread32First.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
    kernel.Thread32First.restype = wintypes.BOOL
    kernel.Thread32Next.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
    kernel.Thread32Next.restype = wintypes.BOOL
    kernel.OpenThread.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenThread.restype = wintypes.HANDLE
    kernel.ResumeThread.argtypes = [wintypes.HANDLE]
    kernel.ResumeThread.restype = wintypes.DWORD
    return kernel


def _extended():
    """The class-9 structure ``probe`` already sets and reads back."""
    import ctypes
    from ctypes import wintypes

    class Basic(ctypes.Structure):
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

    class IoCounters(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]

    class Extended(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", Basic),
            ("IoInfo", IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    class ThreadEntry(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ThreadID", wintypes.DWORD),
            ("th32OwnerProcessID", wintypes.DWORD),
            ("tpBasePri", ctypes.c_long),
            ("tpDeltaPri", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
        ]

    return Extended, ThreadEntry


def _arm(kernel, handle, active_limit: int | None = _ACTIVE_LIMIT) -> int | None:
    """Set class-9 limits and return the flags that read back.

    ``active_limit`` None sets kill-on-close only. An int also sets that
    process cap, and the readback must show the same number. Returns
    ``None`` when the set or the readback does not hold. Does not assign
    a process.
    """
    import ctypes

    extended, _entry = _extended()
    info = extended()
    wanted = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if active_limit is not None:
        wanted |= JOB_OBJECT_LIMIT_ACTIVE_PROCESS
        info.BasicLimitInformation.ActiveProcessLimit = active_limit
    info.BasicLimitInformation.LimitFlags = wanted
    ok = kernel.SetInformationJobObject(
        handle,
        JobObjectExtendedLimitInformation,
        ctypes.byref(info),
        ctypes.sizeof(info),
    )
    if not ok:
        return None
    readback = extended()
    queried = kernel.QueryInformationJobObject(
        handle,
        JobObjectExtendedLimitInformation,
        ctypes.byref(readback),
        ctypes.sizeof(readback),
        None,
    )
    flags = int(readback.BasicLimitInformation.LimitFlags) if queried else 0
    if not queried or (flags & wanted) != wanted:
        return None
    if active_limit is not None and int(readback.BasicLimitInformation.ActiveProcessLimit) != active_limit:
        return None
    return flags


def _resume(kernel, pid: int) -> int:
    """Resume threads of a ``CREATE_SUSPENDED`` child. ``Popen`` has no thread handle."""
    import ctypes

    _limits, thread_entry = _extended()
    del _limits
    snapshot = kernel.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if not snapshot or int(snapshot) in {0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF}:
        return 0
    resumed = 0
    try:
        entry = thread_entry()
        entry.dwSize = ctypes.sizeof(thread_entry)
        ok = kernel.Thread32First(snapshot, ctypes.byref(entry))
        while ok:
            if int(entry.th32OwnerProcessID) == pid:
                thread = kernel.OpenThread(THREAD_SUSPEND_RESUME, False, int(entry.th32ThreadID))
                if thread:
                    previous = int(kernel.ResumeThread(thread))
                    kernel.CloseHandle(thread)
                    if previous != 0xFFFFFFFF:
                        resumed += 1
            ok = kernel.Thread32Next(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    return resumed


def _windows_child(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: float,
    active_limit: int | None,
) -> tuple[int, str, str]:
    """One child inside a class-9 job. Assignment failure does not run the child."""
    import ctypes
    from ctypes import wintypes

    kernel = _kernel()
    job = kernel.CreateJobObjectW(None, None)
    if not job:
        raise Refuse("UNENCLOSED_CHILD", str(ctypes.get_last_error()))
    proc: subprocess.Popen[bytes] | None = None
    try:
        if _arm(kernel, job, active_limit) is None:
            raise Refuse("UNENCLOSED_CHILD", str(ctypes.get_last_error()))
        proc = subprocess.Popen(
            argv,
            cwd=str(cwd),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            creationflags=CREATE_SUSPENDED | CREATE_NO_WINDOW,
        )
        raw = int(getattr(proc, "_handle", 0))
        assigned = kernel.AssignProcessToJobObject(job, wintypes.HANDLE(raw))
        if not assigned:
            err = str(ctypes.get_last_error())
            proc.kill()
            proc.wait(timeout=5)
            raise Refuse("UNENCLOSED_CHILD", err)
        if _resume(kernel, proc.pid) < 1:
            proc.kill()
            proc.wait(timeout=5)
            raise Refuse("UNENCLOSED_CHILD", "no thread")
        try:
            out, err_b = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err_b = proc.communicate()
            return 124, _text(out), _text(err_b) + "\ntimeout"
        code = proc.returncode if proc.returncode is not None else 1
        return code, _text(out), _text(err_b)
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        kernel.CloseHandle(job)


def run_child(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: float,
    active_limit: int | None = _ACTIVE_LIMIT,
) -> tuple[int, str, str]:
    """Run ``argv`` and return ``(code, stdout, stderr)``.

    On Windows the child is in a job before it runs. Timeout is exit 124.
    ``active_limit`` defaults to 4. ``None`` does not cap the count.
    A limit below 1 raises ``UNENCLOSED_CHILD`` and does not start the
    process. ``OSError`` propagates when the executable cannot be started.
    This function does not assign the current process.
    """
    if active_limit is not None and active_limit < 1:
        raise Refuse("UNENCLOSED_CHILD", "active_limit")
    if sys.platform != "win32":
        return _plain(argv, cwd=cwd, env=env, timeout=timeout)
    return _windows_child(
        argv, cwd=cwd, env=env, timeout=timeout, active_limit=active_limit,
    )


def probe() -> Enclosure:
    """Open a job and read the flags back. Never marks the enclosure wipe-proof."""
    if sys.platform != "win32":
        return Enclosure("none", False, "policy_only", False, 0)
    kernel = _kernel()
    try:
        handle = kernel.CreateJobObjectW(None, None)
    except OSError:
        return Enclosure("none", False, "policy_only", False, 0)
    if not handle:
        return Enclosure("none", False, "policy_only", False, 0)
    try:
        flags = _arm(kernel, handle)
        if flags is None:
            return Enclosure("none", False, "policy_only", False, 0)
        # Handle exists and the flags read back. The filesystem is still the jail.
        return Enclosure("job_object", True, "policy_only", False, flags)
    finally:
        kernel.CloseHandle(handle)
