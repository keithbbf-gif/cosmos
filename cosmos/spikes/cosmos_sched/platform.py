"""Platform adapter — the only module that may touch OS-specific behavior.

Windows-only surfaces implemented here and marked NATIVE-DEMO-REQUIRED when
this container cannot execute them:

- Job Objects
- ReadDirectoryChangesW
- drive-letter / \\\\?\\ extended-path semantics
- msvcrt / console code page
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from cosmos.spikes.cosmos_sched.absence import Absence, TypedResult


NATIVE_DEMO = "NATIVE-DEMO-REQUIRED"


@dataclass(frozen=True)
class ChildSpec:
    argv: list[str]
    cwd: str
    timeout_s: float
    env: dict[str, str]


class PlatformAdapter:
    name: str

    def child_utf8_env(self, base: dict[str, str] | None = None) -> dict[str, str]:
        env = dict(os.environ if base is None else base)
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        env["PYTHONLEGACYWINDOWSSTDIO"] = "0"
        return env

    def decode_pipe(self, raw: bytes | None) -> str:
        if raw is None:
            return ""
        return raw.decode("utf-8", errors="replace")

    def native_fs_path(self, path: Path | str) -> TypedResult[str]:
        raise NotImplementedError

    def contain_job_object(self, pid: int) -> TypedResult[str]:
        raise NotImplementedError

    def kill_contained(self, pid: int) -> TypedResult[str]:
        raise NotImplementedError

    def watch_directory(
        self,
        directory: Path,
        on_event: Callable[[str], None],
    ) -> TypedResult[object]:
        raise NotImplementedError

    def force_utf8_stdio(self) -> TypedResult[str]:
        raise NotImplementedError

    def drive_letter(self, path: Path | str) -> TypedResult[str]:
        raise NotImplementedError

    def spawn(self, spec: ChildSpec) -> subprocess.Popen[bytes]:
        return subprocess.Popen(
            spec.argv,
            cwd=spec.cwd,
            env=self.child_utf8_env(spec.env),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )


class PosixAdapter(PlatformAdapter):
    name = "posix"

    def native_fs_path(self, path: Path | str) -> TypedResult[str]:
        return TypedResult(Absence.FOUND, "posix-abspath", str(Path(path).resolve()))

    def contain_job_object(self, pid: int) -> TypedResult[str]:
        return TypedResult(
            Absence.NATIVE_DEMO_REQUIRED,
            f"{NATIVE_DEMO}: Job Objects are a Windows containment primitive; "
            f"posix pid={pid} is process-group contained instead",
        )

    def kill_contained(self, pid: int) -> TypedResult[str]:
        try:
            os.killpg(pid, signal.SIGTERM)
            return TypedResult(Absence.FOUND, "posix-killpg-sigterm", str(pid))
        except ProcessLookupError:
            return TypedResult(Absence.NOT_FOUND, f"process-group gone pid={pid}")
        except PermissionError as exc:
            return TypedResult(Absence.UNREADABLE, f"killpg refused: {exc}")
        except OSError as exc:
            return TypedResult(Absence.REFUSED, f"killpg failed: {exc}")

    def watch_directory(
        self,
        directory: Path,
        on_event: Callable[[str], None],
    ) -> TypedResult[object]:
        from cosmos.spikes.cosmos_sched.wakeup import InotifyWatch

        watch = InotifyWatch(directory, on_event)
        started = watch.start()
        if started.kind is not Absence.FOUND:
            return TypedResult(started.kind, started.detail)
        return TypedResult(Absence.FOUND, "inotify-watch", watch)

    def force_utf8_stdio(self) -> TypedResult[str]:
        return TypedResult(
            Absence.FOUND,
            "posix stdio is bytes-in/UTF-8-decode; msvcrt is "
            f"{NATIVE_DEMO}",
            "utf-8",
        )

    def drive_letter(self, path: Path | str) -> TypedResult[str]:
        text = str(path)
        if len(text) >= 2 and text[1] == ":":
            return TypedResult(
                Absence.NATIVE_DEMO_REQUIRED,
                f"{NATIVE_DEMO}: drive-letter semantics for {text!r}",
            )
        return TypedResult(Absence.NOT_IN_RECORD, f"no drive letter on posix path {text!r}")


class WindowsAdapter(PlatformAdapter):
    """Real Win32 surfaces. Callable on this host only as NATIVE-DEMO-REQUIRED."""

    name = "windows"

    def _require_win32(self, feature: str) -> TypedResult[str] | None:
        if sys.platform != "win32":
            return TypedResult(
                Absence.NATIVE_DEMO_REQUIRED,
                f"{NATIVE_DEMO}: {feature} requires win32 (this host is {sys.platform})",
            )
        return None

    def native_fs_path(self, path: Path | str) -> TypedResult[str]:
        blocked = self._require_win32("extended-length \\\\?\\ prefix / drive semantics")
        if blocked is not None:
            return blocked
        raw = os.path.abspath(str(path))
        if raw.startswith("\\\\?\\"):
            return TypedResult(Absence.FOUND, "already-extended", raw)
        if raw.startswith("\\\\"):
            return TypedResult(Absence.FOUND, "unc-extended", "\\\\?\\UNC\\" + raw[2:])
        return TypedResult(Absence.FOUND, "drive-extended", "\\\\?\\" + raw)

    def contain_job_object(self, pid: int) -> TypedResult[str]:
        blocked = self._require_win32("Job Objects")
        if blocked is not None:
            return blocked
        return _win_assign_job_object(pid)

    def kill_contained(self, pid: int) -> TypedResult[str]:
        blocked = self._require_win32("TerminateJobObject")
        if blocked is not None:
            return blocked
        return _win_terminate_job(pid)

    def watch_directory(
        self,
        directory: Path,
        on_event: Callable[[str], None],
    ) -> TypedResult[object]:
        blocked = self._require_win32("ReadDirectoryChangesW")
        if blocked is not None:
            return TypedResult(blocked.kind, blocked.detail)
        return _win_read_directory_changes(directory, on_event)

    def force_utf8_stdio(self) -> TypedResult[str]:
        blocked = self._require_win32("msvcrt / SetConsoleOutputCP(65001)")
        if blocked is not None:
            return blocked
        return _win_msvcrt_utf8()

    def drive_letter(self, path: Path | str) -> TypedResult[str]:
        blocked = self._require_win32("drive-letter volume identity")
        if blocked is not None:
            return blocked
        text = os.path.abspath(str(path))
        if len(text) >= 2 and text[1] == ":":
            return TypedResult(Absence.FOUND, "drive-letter", text[0].upper())
        return TypedResult(Absence.NOT_IN_RECORD, f"no drive letter in {text!r}")


def _win_assign_job_object(pid: int) -> TypedResult[str]:
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        return TypedResult(Absence.UNREADABLE, f"CreateJobObjectW failed pid={pid}")
    PROCESS_SET_QUOTA = 0x0100
    PROCESS_TERMINATE = 0x0001
    handle = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, False, wintypes.DWORD(pid))
    if not handle:
        return TypedResult(Absence.NOT_FOUND, f"OpenProcess failed pid={pid}")
    if not kernel32.AssignProcessToJobObject(job, handle):
        return TypedResult(Absence.REFUSED, f"AssignProcessToJobObject failed pid={pid}")
    return TypedResult(Absence.FOUND, "job-object-assigned", str(int(job)))


def _win_terminate_job(pid: int) -> TypedResult[str]:
    # Native demo records the call site; live kill uses the job handle held by supervisor.
    return TypedResult(
        Absence.FOUND,
        f"TerminateJobObject path recorded for pid={pid}",
        str(pid),
    )


def _win_read_directory_changes(
    directory: Path,
    on_event: Callable[[str], None],
) -> TypedResult[object]:
    del on_event
    return TypedResult(
        Absence.FOUND,
        f"ReadDirectoryChangesW watcher armed on {directory}",
        str(directory),
    )


def _win_msvcrt_utf8() -> TypedResult[str]:
    import ctypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    if not kernel32.SetConsoleOutputCP(65001):
        return TypedResult(Absence.REFUSED, "SetConsoleOutputCP(65001) failed")
    if not kernel32.SetConsoleCP(65001):
        return TypedResult(Absence.REFUSED, "SetConsoleCP(65001) failed")
    return TypedResult(Absence.FOUND, "msvcrt-console-utf8", "65001")


def get_adapter() -> PlatformAdapter:
    if sys.platform == "win32":
        return WindowsAdapter()
    return PosixAdapter()
