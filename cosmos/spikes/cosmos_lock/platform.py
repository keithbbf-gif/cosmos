"""Platform adapter.

Windows-only behaviors live behind this adapter:

- Job Objects (worker-tree containment; dying-holder descendants)
- ReadDirectoryChangesW (interrupt-driven wakeup; queue-lane demo)
- drive semantics (V:/UNC/\\\\?\\ volume identity)
- msvcrt.locking (advisory lock; never lease authority)

Container-run parts (POSIX fcntl, st_dev same-volume, path-shape
classification, the two-universes backslash trap) are tested here.
Windows-run parts return NATIVE-DEMO-REQUIRED on this host and are
implemented so a native queue-lane demo can call them without a rewrite.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import BinaryIO

from cosmos.spikes.cosmos_lock.absence import AbsenceKind, Outcome, RefusalCode

IS_WINDOWS = sys.platform == "win32"


class PathShape(str, Enum):
    POSIX_ABSOLUTE = "POSIX_ABSOLUTE"
    POSIX_RELATIVE = "POSIX_RELATIVE"
    WIN_DRIVE = "WIN_DRIVE"
    WIN_UNC = "WIN_UNC"
    WIN_EXTENDED = "WIN_EXTENDED"
    WIN_EXTENDED_UNC = "WIN_EXTENDED_UNC"
    MIXED_OR_UNKNOWN = "MIXED_OR_UNKNOWN"


@dataclass
class LockGuard:
    """Holds an advisory OS lock. This is not a COSMOS lease."""

    path: Path
    handle: BinaryIO
    mechanism: str

    def release(self) -> None:
        try:
            if self.mechanism == "fcntl":
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            elif self.mechanism == "msvcrt":
                import msvcrt

                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)  # type: ignore[attr-defined]
        finally:
            self.handle.close()


@dataclass(frozen=True)
class JobObjectHandle:
    name: str
    raw_handle: int
    mechanism: str


@dataclass(frozen=True)
class DirectoryWatchResult:
    path: str
    mechanism: str
    change_count: int
    notes: str


def classify_path_shape(raw: str) -> PathShape:
    """Classify a path *string* with no I/O.

    On Linux a backslash string succeeds as a filename (STAGE2A two-universes
    incident, 2026-08-16). Classification must precede any open().
    """
    if raw.startswith(("\\\\?\\UNC\\", "//?/UNC/")):
        return PathShape.WIN_EXTENDED_UNC
    if raw.startswith(("\\\\?\\", "//?/")):
        return PathShape.WIN_EXTENDED
    if raw.startswith("\\\\") or (raw.startswith("//") and not raw.startswith("//?")):
        return PathShape.WIN_UNC
    if len(raw) >= 3 and raw[0].isalpha() and raw[1] == ":" and raw[2] in "\\/":
        return PathShape.WIN_DRIVE
    if raw.startswith("/"):
        return PathShape.POSIX_ABSOLUTE
    if "\\" in raw and "/" not in raw:
        return PathShape.MIXED_OR_UNKNOWN
    if raw:
        return PathShape.POSIX_RELATIVE
    return PathShape.MIXED_OR_UNKNOWN


def extended_win_path(raw: str) -> str:
    """Compute the \\\\?\\ form. String math only; does not open the path."""
    if raw.startswith("\\\\?\\"):
        return raw
    if raw.startswith("\\\\"):
        return "\\\\?\\UNC\\" + raw[2:]
    return "\\\\?\\" + raw


class PlatformAdapter:
    """One adapter per composition. Importing this module does no I/O."""

    def __init__(self, *, platform: str | None = None) -> None:
        self.platform = platform or sys.platform

    @property
    def is_windows(self) -> bool:
        return self.platform == "win32"

    def classify(self, raw: str) -> PathShape:
        return classify_path_shape(raw)

    def native_authoritative_path(self, raw: str) -> Outcome[Path]:
        """Refuse a Windows-shaped path on POSIX (the two-universes defect)."""
        shape = classify_path_shape(raw)
        if self.is_windows:
            if shape in {
                PathShape.WIN_DRIVE,
                PathShape.WIN_UNC,
                PathShape.WIN_EXTENDED,
                PathShape.WIN_EXTENDED_UNC,
            } or shape is PathShape.POSIX_ABSOLUTE:
                return Outcome.found(Path(raw), reason=f"shape={shape.value}")
            return Outcome.absent(
                AbsenceKind.IDENTITY_MISMATCH,
                code=RefusalCode.WRONG_UNIVERSE,
                reason=f"unusable native path shape {shape.value}: {raw!r}",
            )
        if shape in {
            PathShape.WIN_DRIVE,
            PathShape.WIN_UNC,
            PathShape.WIN_EXTENDED,
            PathShape.WIN_EXTENDED_UNC,
        }:
            return Outcome.absent(
                AbsenceKind.IDENTITY_MISMATCH,
                code=RefusalCode.WRONG_UNIVERSE,
                reason=(
                    "Windows path shape on a POSIX arbiter is the two-universes "
                    f"defect; refusing {raw!r} as {shape.value}"
                ),
                details={"shape": shape.value, "raw": raw},
            )
        if shape is PathShape.POSIX_ABSOLUTE:
            return Outcome.found(Path(raw), reason=f"shape={shape.value}")
        return Outcome.absent(
            AbsenceKind.IDENTITY_MISMATCH,
            code=RefusalCode.WRONG_UNIVERSE,
            reason=f"path is not an absolute native path: {raw!r} ({shape.value})",
        )

    def same_volume(self, first: Path, second: Path) -> Outcome[bool]:
        if self.is_windows:
            return self._win_same_volume(first, second)
        try:
            a = first.resolve()
            b = second.resolve()
            return Outcome.found(a.stat().st_dev == b.stat().st_dev)
        except FileNotFoundError:
            return Outcome.absent(
                AbsenceKind.NOT_FOUND,
                reason="same_volume target missing",
                details={"first": str(first), "second": str(second)},
            )
        except OSError as exc:
            return Outcome.absent(
                AbsenceKind.UNREADABLE,
                reason=str(exc),
                details={"errno": getattr(exc, "errno", None)},
            )

    def try_exclusive_lock(self, path: Path) -> Outcome[LockGuard]:
        """Advisory OS lock. Never consulted for lease grant or fenced commit."""
        if self.is_windows:
            return self.msvcrt_try_lock(path)
        return self._fcntl_try_lock(path)

    def msvcrt_try_lock(self, path: Path) -> Outcome[LockGuard]:
        if not self.is_windows:
            return Outcome.native_demo_required("msvcrt.locking")
        return self._msvcrt_try_lock(path)

    def create_job_object(self, name: str) -> Outcome[JobObjectHandle]:
        if not self.is_windows:
            return Outcome.native_demo_required("Job Objects")
        return self._win_create_job_object(name)

    def assign_current_process_to_job(self, handle: JobObjectHandle) -> Outcome[bool]:
        if not self.is_windows:
            return Outcome.native_demo_required("Job Objects AssignProcessToJobObject")
        return self._win_assign_current_process(handle)

    def terminate_job_object(self, handle: JobObjectHandle, exit_code: int = 1) -> Outcome[bool]:
        if not self.is_windows:
            return Outcome.native_demo_required("Job Objects TerminateJobObject")
        return self._win_terminate_job(handle, exit_code)

    def close_job_object(self, handle: JobObjectHandle) -> Outcome[bool]:
        if not self.is_windows:
            return Outcome.native_demo_required("Job Objects CloseHandle")
        return self._win_close_handle(handle)

    def watch_directory_rdcw(
        self,
        path: Path,
        *,
        timeout_ms: int = 1000,
    ) -> Outcome[DirectoryWatchResult]:
        if not self.is_windows:
            return Outcome.native_demo_required("ReadDirectoryChangesW")
        return self._win_read_directory_changes(path, timeout_ms=timeout_ms)

    def open_extended(self, raw: str) -> Outcome[Path]:
        """Open using Windows extended-path (\\\\?\\) semantics."""
        if not self.is_windows:
            return Outcome.native_demo_required("Windows drive semantics / extended paths")
        extended = extended_win_path(raw)
        p = Path(extended)
        if not p.exists():
            return Outcome.absent(AbsenceKind.NOT_FOUND, reason=extended)
        return Outcome.found(p)

    def windows_volume_name(self, path: Path) -> Outcome[str]:
        if not self.is_windows:
            return Outcome.native_demo_required("GetVolumeNameForVolumeMountPointW")
        return self._win_volume_name(path)

    # --- POSIX (container-run) -------------------------------------------------

    def _fcntl_try_lock(self, path: Path) -> Outcome[LockGuard]:
        import fcntl

        path.parent.mkdir(parents=True, exist_ok=True)
        handle = path.open("a+b")
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            handle.close()
            return Outcome.refused(
                RefusalCode.ADVISORY_LOCK_HELD,
                reason=f"fcntl lock held on {path}",
            )
        except OSError as exc:
            handle.close()
            return Outcome.absent(AbsenceKind.UNREADABLE, reason=str(exc))
        return Outcome.found(LockGuard(path=path, handle=handle, mechanism="fcntl"))

    # --- Windows (NATIVE-DEMO-REQUIRED on this host) ---------------------------

    def _msvcrt_try_lock(self, path: Path) -> Outcome[LockGuard]:
        import msvcrt

        path.parent.mkdir(parents=True, exist_ok=True)
        handle = path.open("a+b")
        try:
            handle.seek(0)
            if handle.read(1) == b"":
                handle.write(b"\x00")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)  # type: ignore[attr-defined]
        except OSError as exc:
            handle.close()
            return Outcome.refused(
                RefusalCode.ADVISORY_LOCK_HELD,
                reason=f"msvcrt.locking refused on {path}: {exc}",
            )
        return Outcome.found(LockGuard(path=path, handle=handle, mechanism="msvcrt"))

    def _kernel32(self):  # pragma: no cover - win32
        import ctypes

        return ctypes.WinDLL("kernel32", use_last_error=True)

    @staticmethod
    def _winerr() -> int:  # pragma: no cover - win32
        import ctypes

        return int(ctypes.get_last_error())  # type: ignore[attr-defined]

    def _win_create_job_object(self, name: str) -> Outcome[JobObjectHandle]:  # pragma: no cover
        import ctypes

        k32 = self._kernel32()
        create = k32.CreateJobObjectW
        create.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        create.restype = ctypes.c_void_p
        handle = create(None, name)
        if not handle:
            err = self._winerr()
            return Outcome.absent(
                AbsenceKind.UNREADABLE,
                reason=f"CreateJobObjectW failed winerr={err}",
            )
        return Outcome.found(
            JobObjectHandle(name=name, raw_handle=int(handle), mechanism="JobObject")
        )

    def _win_assign_current_process(self, handle: JobObjectHandle) -> Outcome[bool]:  # pragma: no cover
        import ctypes

        k32 = self._kernel32()
        assign = k32.AssignProcessToJobObject
        assign.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        assign.restype = ctypes.c_bool
        current = k32.GetCurrentProcess()
        if not assign(handle.raw_handle, current):
            return Outcome.absent(
                AbsenceKind.UNREADABLE,
                reason=f"AssignProcessToJobObject failed winerr={self._winerr()}",
            )
        return Outcome.found(True)

    def _win_terminate_job(self, handle: JobObjectHandle, exit_code: int) -> Outcome[bool]:  # pragma: no cover
        import ctypes

        k32 = self._kernel32()
        term = k32.TerminateJobObject
        term.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        term.restype = ctypes.c_bool
        if not term(handle.raw_handle, exit_code):
            return Outcome.absent(
                AbsenceKind.UNREADABLE,
                reason=f"TerminateJobObject failed winerr={self._winerr()}",
            )
        return Outcome.found(True)

    def _win_close_handle(self, handle: JobObjectHandle) -> Outcome[bool]:  # pragma: no cover
        import ctypes

        k32 = self._kernel32()
        close = k32.CloseHandle
        close.argtypes = [ctypes.c_void_p]
        close.restype = ctypes.c_bool
        if not close(handle.raw_handle):
            return Outcome.absent(
                AbsenceKind.UNREADABLE,
                reason=f"CloseHandle failed winerr={self._winerr()}",
            )
        return Outcome.found(True)

    def _win_read_directory_changes(
        self,
        path: Path,
        *,
        timeout_ms: int,
    ) -> Outcome[DirectoryWatchResult]:  # pragma: no cover
        import ctypes
        from ctypes import wintypes

        k32 = self._kernel32()
        FILE_LIST_DIRECTORY = 0x0001
        FILE_SHARE_READ = 0x00000001
        FILE_SHARE_WRITE = 0x00000002
        FILE_SHARE_DELETE = 0x00000004
        OPEN_EXISTING = 3
        FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
        FILE_FLAG_OVERLAPPED = 0x40000000
        FILE_NOTIFY_CHANGE_FILE_NAME = 0x00000001
        FILE_NOTIFY_CHANGE_DIR_NAME = 0x00000002
        FILE_NOTIFY_CHANGE_LAST_WRITE = 0x00000010
        INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
        WAIT_OBJECT_0 = 0x00000000
        WAIT_TIMEOUT = 0x00000102

        create_file = k32.CreateFileW
        create_file.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.c_void_p,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.c_void_p,
        ]
        create_file.restype = wintypes.HANDLE

        directory = create_file(
            str(path),
            FILE_LIST_DIRECTORY,
            FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
            None,
            OPEN_EXISTING,
            FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OVERLAPPED,
            None,
        )
        if directory == INVALID_HANDLE_VALUE:
            return Outcome.absent(
                AbsenceKind.UNREADABLE,
                reason=f"CreateFileW failed winerr={self._winerr()}",
            )

        class OVERLAPPED(ctypes.Structure):
            _fields_ = [
                ("Internal", ctypes.c_ulonglong),
                ("InternalHigh", ctypes.c_ulonglong),
                ("Offset", wintypes.DWORD),
                ("OffsetHigh", wintypes.DWORD),
                ("hEvent", wintypes.HANDLE),
            ]

        event = k32.CreateEventW(None, True, False, None)
        overlapped = OVERLAPPED()
        overlapped.hEvent = event
        buf = ctypes.create_string_buffer(4096)
        bytes_ret = wintypes.DWORD(0)
        rdcw = k32.ReadDirectoryChangesW
        ok = rdcw(
            directory,
            buf,
            ctypes.sizeof(buf),
            True,
            FILE_NOTIFY_CHANGE_FILE_NAME
            | FILE_NOTIFY_CHANGE_DIR_NAME
            | FILE_NOTIFY_CHANGE_LAST_WRITE,
            ctypes.byref(bytes_ret),
            ctypes.byref(overlapped),
            None,
        )
        if not ok and self._winerr() not in {997, 0}:  # ERROR_IO_PENDING
            k32.CloseHandle(directory)
            k32.CloseHandle(event)
            return Outcome.absent(
                AbsenceKind.UNREADABLE,
                reason=f"ReadDirectoryChangesW failed winerr={self._winerr()}",
            )
        wait = k32.WaitForSingleObject(event, timeout_ms)
        k32.CloseHandle(directory)
        k32.CloseHandle(event)
        if wait == WAIT_TIMEOUT:
            return Outcome.found(
                DirectoryWatchResult(
                    path=str(path),
                    mechanism="ReadDirectoryChangesW",
                    change_count=0,
                    notes=f"timeout_ms={timeout_ms}",
                )
            )
        if wait != WAIT_OBJECT_0:
            return Outcome.absent(
                AbsenceKind.UNREADABLE,
                reason=f"WaitForSingleObject status={wait}",
            )
        return Outcome.found(
            DirectoryWatchResult(
                path=str(path),
                mechanism="ReadDirectoryChangesW",
                change_count=1 if bytes_ret.value else 0,
                notes=f"bytes={bytes_ret.value}",
            )
        )

    def _win_volume_name(self, path: Path) -> Outcome[str]:  # pragma: no cover
        import ctypes
        from ctypes import wintypes

        k32 = self._kernel32()
        get_path = k32.GetVolumePathNameW
        get_path.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        get_path.restype = wintypes.BOOL
        buf = ctypes.create_unicode_buffer(512)
        if not get_path(str(path), buf, 512):
            return Outcome.absent(
                AbsenceKind.UNREADABLE,
                reason=f"GetVolumePathNameW failed winerr={self._winerr()}",
            )
        get_name = k32.GetVolumeNameForVolumeMountPointW
        get_name.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        get_name.restype = wintypes.BOOL
        name_buf = ctypes.create_unicode_buffer(512)
        if not get_name(buf.value, name_buf, 512):
            return Outcome.absent(
                AbsenceKind.UNREADABLE,
                reason=f"GetVolumeNameForVolumeMountPointW failed winerr={self._winerr()}",
            )
        return Outcome.found(name_buf.value)

    def _win_same_volume(self, first: Path, second: Path) -> Outcome[bool]:  # pragma: no cover
        a = self._win_volume_name(first)
        if not a.ok:
            return Outcome(a.kind, value=None, code=a.code, reason=a.reason, details=a.details)
        b = self._win_volume_name(second)
        if not b.ok:
            return Outcome(b.kind, value=None, code=b.code, reason=b.reason, details=b.details)
        return Outcome.found(a.unwrap() == b.unwrap())
