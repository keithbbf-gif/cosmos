"""Platform adapter: POSIX is exercised here; Windows natives are behind this seam.

Windows-only surfaces (Job Objects, ReadDirectoryChangesW, drive-letter
authority, msvcrt locking) return NATIVE_DEMO_REQUIRED on this container.
The queue-lane demo on live Windows must run those branches.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import os
import re
import select
import struct
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from cosmos.spikes.cosmos_mail.clock import Clock, SystemClock
from cosmos.spikes.cosmos_mail.types import AbsenceKind, Outcome, epoch_of, format_aware

SPIKE_ADAPTER_WORKER = "cursor.cosmos_mail"

DRIVE_RE = re.compile(r"^([A-Za-z]):[\\/](.*)$")
WIN_EXTENDED_PREFIX = "\\\\?\\"
WIN_UNC_PREFIX = "\\\\?\\UNC\\"

# inotify constants (Linux). Used by the POSIX inbox-wakeup path.
IN_CLOEXEC = 0x80000
IN_CREATE = 0x00000100
IN_MOVED_TO = 0x00000080
IN_CLOSE_WRITE = 0x00000008
INOTIFY_EVENT_FMT = "iIII"
INOTIFY_EVENT_SIZE = struct.calcsize(INOTIFY_EVENT_FMT)


@dataclass(frozen=True)
class DriveInfo:
    letter: str
    tail: str


@dataclass(frozen=True)
class FileChange:
    kind: str
    name: str
    mask: int


@dataclass(frozen=True)
class ExclusiveFile:
    fd: int
    path: str


def _stamp(clock: Clock, worker_id: str) -> tuple[str, float]:
    now = clock.now()
    return format_aware(now), epoch_of(now)


class PlatformAdapter:
    """OS seam. Subclasses must not import around this for native calls."""

    name = "base"

    def __init__(
        self, clock: Clock | None = None, worker_id: str = SPIKE_ADAPTER_WORKER
    ) -> None:
        self.clock = clock or SystemClock()
        self.worker_id = worker_id

    def _outcome(
        self,
        kind: AbsenceKind,
        *,
        value: object = None,
        detail: str = "",
        path: str | None = None,
    ) -> Outcome[object]:
        observed_at, observed_epoch = _stamp(self.clock, self.worker_id)
        return Outcome(
            kind=kind,
            value=value,
            detail=detail,
            observed_at=observed_at,
            observed_epoch=observed_epoch,
            worker_id=self.worker_id,
            path=path,
        )

    def native_fs_path(self, path: Path) -> Outcome[str]:
        raise NotImplementedError

    def interpret_drive(self, raw: str) -> Outcome[DriveInfo]:
        raise NotImplementedError

    def reject_foreign_separators(self, raw: str) -> Outcome[str]:
        raise NotImplementedError

    def exclusive_create(self, path: Path) -> Outcome[ExclusiveFile]:
        raise NotImplementedError

    def write_fsync_close(self, handle: ExclusiveFile, payload: bytes) -> Outcome[None]:
        raise NotImplementedError

    def watch_directory(
        self, path: Path, timeout_s: float
    ) -> Outcome[list[FileChange]]:
        raise NotImplementedError

    def job_object_contain(self, pid: int) -> Outcome[str]:
        raise NotImplementedError

    def msvcrt_locking(self, fd: int, nbytes: int = 1) -> Outcome[None]:
        raise NotImplementedError

    def posix_fcntl_lock(self, fd: int) -> Outcome[None]:
        return self._outcome(
            AbsenceKind.NATIVE_DEMO_REQUIRED,
            detail="posix_fcntl_lock is a POSIX analog; this adapter does not claim it",
        )


class PosixPlatformAdapter(PlatformAdapter):
    """Container-run adapter. Drive letters and backslashes are refused (two-universes)."""

    name = "posix"

    def native_fs_path(self, path: Path) -> Outcome[str]:
        text = os.fspath(path)
        foreign = self.reject_foreign_separators(text)
        if foreign.kind is not AbsenceKind.FOUND:
            return Outcome(
                kind=foreign.kind,
                value=None,
                detail=foreign.detail,
                observed_at=foreign.observed_at,
                observed_epoch=foreign.observed_epoch,
                worker_id=foreign.worker_id,
                path=text,
            )
        return self._outcome(
            AbsenceKind.FOUND, value=text, detail="posix path as-is", path=text
        )

    def interpret_drive(self, raw: str) -> Outcome[DriveInfo]:
        if DRIVE_RE.match(raw) or "\\" in raw:
            return self._outcome(
                AbsenceKind.REFUSED,
                detail=(
                    "Windows drive or backslash path refused on POSIX "
                    "(two-universes incident 2026-08-16: a backslash string "
                    "succeeds as a filename and splits the lock/mailbox)"
                ),
                path=raw,
            )
        return self._outcome(
            AbsenceKind.NOT_IN_RECORD,
            detail="POSIX has no drive-letter namespace",
            path=raw,
        )

    def reject_foreign_separators(self, raw: str) -> Outcome[str]:
        if "\\" in raw or DRIVE_RE.match(raw):
            return self._outcome(
                AbsenceKind.REFUSED,
                detail="literal backslash or drive letter refused on POSIX",
                path=raw,
            )
        return self._outcome(
            AbsenceKind.FOUND, value=raw, detail="separators native", path=raw
        )

    def exclusive_create(self, path: Path) -> Outcome[ExclusiveFile]:
        native = self.native_fs_path(path)
        if native.kind is not AbsenceKind.FOUND or native.value is None:
            return Outcome(
                kind=native.kind,
                value=None,
                detail=native.detail,
                observed_at=native.observed_at,
                observed_epoch=native.observed_epoch,
                worker_id=native.worker_id,
                path=native.path,
            )
        target = native.value
        try:
            fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            return self._outcome(
                AbsenceKind.COLLISION_REFUSED,
                detail="exclusive create collided; message name is not unique",
                path=target,
            )
        except FileNotFoundError:
            return self._outcome(
                AbsenceKind.NOT_FOUND,
                detail="parent directory missing; refuse-not-guess (will not write cwd)",
                path=target,
            )
        except PermissionError:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail="exclusive create permission denied",
                path=target,
            )
        except OSError as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"exclusive create failed: {exc}",
                path=target,
            )
        return self._outcome(
            AbsenceKind.FOUND,
            value=ExclusiveFile(fd=fd, path=target),
            detail="O_EXCL create",
            path=target,
        )

    def write_fsync_close(self, handle: ExclusiveFile, payload: bytes) -> Outcome[None]:
        try:
            written = os.write(handle.fd, payload)
            if written != len(payload):
                os.close(handle.fd)
                return self._outcome(
                    AbsenceKind.UNREADABLE,
                    detail=f"short write {written} of {len(payload)}",
                    path=handle.path,
                )
            os.fsync(handle.fd)
        except OSError as exc:
            try:
                os.close(handle.fd)
            except OSError:
                pass
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"write/fsync failed: {exc}",
                path=handle.path,
            )
        try:
            os.close(handle.fd)
        except OSError as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"close failed: {exc}",
                path=handle.path,
            )
        return self._outcome(AbsenceKind.FOUND, detail="fsync+close", path=handle.path)

    def posix_fcntl_lock(self, fd: int) -> Outcome[None]:
        try:
            import fcntl
        except ImportError:
            return self._outcome(
                AbsenceKind.NOT_IN_RECORD,
                detail="fcntl module not present on this interpreter",
            )
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return self._outcome(
                AbsenceKind.REFUSED,
                detail="fcntl lock held by another claimant",
            )
        except OSError as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"fcntl lock failed: {exc}",
            )
        return self._outcome(AbsenceKind.FOUND, detail="fcntl.LOCK_EX|LOCK_NB")

    def watch_directory(
        self, path: Path, timeout_s: float
    ) -> Outcome[list[FileChange]]:
        """Interrupt-driven inbox wakeup via inotify. Not a 60 s poll."""
        native = self.native_fs_path(path)
        if native.kind is not AbsenceKind.FOUND or native.value is None:
            return Outcome(
                kind=native.kind,
                value=None,
                detail=native.detail,
                observed_at=native.observed_at,
                observed_epoch=native.observed_epoch,
                worker_id=native.worker_id,
                path=native.path,
            )
        target = native.value
        if not os.path.isdir(target):
            if not os.path.exists(target):
                return self._outcome(
                    AbsenceKind.NOT_FOUND,
                    detail="watch path missing",
                    path=target,
                )
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail="watch path exists but is not a directory",
                path=target,
            )
        try:
            events = _inotify_wait(target, timeout_s)
        except _InotifyUnavailable as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=str(exc),
                path=target,
            )
        return self._outcome(
            AbsenceKind.FOUND,
            value=events,
            detail=f"inotify events={len(events)} timeout_s={timeout_s}",
            path=target,
        )

    def job_object_contain(self, pid: int) -> Outcome[str]:
        return self._outcome(
            AbsenceKind.NATIVE_DEMO_REQUIRED,
            detail=(
                "Job Objects are a Windows native. Queue-lane demo must call "
                "CreateJobObjectW + AssignProcessToJobObject + KILL_ON_JOB_CLOSE "
                f"for pid={pid}."
            ),
        )

    def msvcrt_locking(self, fd: int, nbytes: int = 1) -> Outcome[None]:
        return self._outcome(
            AbsenceKind.NATIVE_DEMO_REQUIRED,
            detail=(
                "msvcrt.locking is a Windows native. Container analog is "
                f"posix_fcntl_lock (tested). fd={fd} nbytes={nbytes}."
            ),
        )


class WindowsPlatformAdapter(PlatformAdapter):
    """Windows adapter. Off win32 every native call is NATIVE_DEMO_REQUIRED.

    The string-level drive and MAX_PATH helpers are pure and testable here.
    Live ReadDirectoryChangesW / Job Object / msvcrt execution is
    NATIVE-DEMO-REQUIRED.
    """

    name = "windows"

    def native_fs_path(self, path: Path) -> Outcome[str]:
        text = os.fspath(path)
        if text.startswith(WIN_EXTENDED_PREFIX):
            return self._outcome(
                AbsenceKind.FOUND,
                value=text,
                detail="already extended-length",
                path=text,
            )
        if text.startswith("\\\\"):
            extended = WIN_UNC_PREFIX + text[2:]
        else:
            extended = WIN_EXTENDED_PREFIX + text
        return self._outcome(
            AbsenceKind.FOUND,
            value=extended,
            detail="MAX_PATH prefix applied (C-60)",
            path=text,
        )

    def interpret_drive(self, raw: str) -> Outcome[DriveInfo]:
        matched = DRIVE_RE.match(raw)
        if matched is None:
            return self._outcome(
                AbsenceKind.NOT_IN_RECORD,
                detail="no drive letter in path",
                path=raw,
            )
        info = DriveInfo(letter=matched.group(1).upper(), tail=matched.group(2))
        return self._outcome(
            AbsenceKind.FOUND,
            value=info,
            detail=f"drive {info.letter}: is configuration, not a guess",
            path=raw,
        )

    def reject_foreign_separators(self, raw: str) -> Outcome[str]:
        return self._outcome(
            AbsenceKind.FOUND, value=raw, detail="windows separators accepted"
        )

    def exclusive_create(self, path: Path) -> Outcome[ExclusiveFile]:
        if sys.platform != "win32":
            return self._outcome(
                AbsenceKind.NATIVE_DEMO_REQUIRED,
                detail="Windows exclusive create (CreateFileW CREATE_NEW / msvcrt) not run here",
                path=os.fspath(path),
            )
        native = self.native_fs_path(path)
        if native.kind is not AbsenceKind.FOUND or native.value is None:
            return Outcome(
                kind=native.kind,
                value=None,
                detail=native.detail,
                observed_at=native.observed_at,
                observed_epoch=native.observed_epoch,
                worker_id=native.worker_id,
                path=native.path,
            )
        try:
            fd = os.open(native.value, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return self._outcome(
                AbsenceKind.COLLISION_REFUSED,
                detail="Windows exclusive create collided",
                path=native.value,
            )
        except OSError as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"Windows exclusive create failed: {exc}",
                path=native.value,
            )
        return self._outcome(
            AbsenceKind.FOUND,
            value=ExclusiveFile(fd=fd, path=native.value),
            detail="win32 O_EXCL",
            path=native.value,
        )

    def write_fsync_close(self, handle: ExclusiveFile, payload: bytes) -> Outcome[None]:
        if sys.platform != "win32":
            return self._outcome(
                AbsenceKind.NATIVE_DEMO_REQUIRED,
                detail="Windows write/fsync/close not run here",
                path=handle.path,
            )
        posix = PosixPlatformAdapter(clock=self.clock, worker_id=self.worker_id)
        written = posix.write_fsync_close(handle, payload)
        return written

    def watch_directory(
        self, path: Path, timeout_s: float
    ) -> Outcome[list[FileChange]]:
        if sys.platform != "win32":
            return self._outcome(
                AbsenceKind.NATIVE_DEMO_REQUIRED,
                detail=(
                    "NATIVE-DEMO-REQUIRED: ReadDirectoryChangesW on the inbox. "
                    "Open with FILE_LIST_DIRECTORY | FILE_FLAG_BACKUP_SEMANTICS, "
                    "filter FILE_NOTIFY_CHANGE_FILE_NAME, no 60 s poll. "
                    f"path={path} timeout_s={timeout_s}"
                ),
                path=os.fspath(path),
            )
        return _read_directory_changes_w(self, path, timeout_s)

    def job_object_contain(self, pid: int) -> Outcome[str]:
        if sys.platform != "win32":
            return self._outcome(
                AbsenceKind.NATIVE_DEMO_REQUIRED,
                detail=(
                    "NATIVE-DEMO-REQUIRED: Job Object containment for pid "
                    f"{pid}. CreateJobObjectW, JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE, "
                    "AssignProcessToJobObject."
                ),
            )
        return _job_object_contain_windows(self, pid)

    def msvcrt_locking(self, fd: int, nbytes: int = 1) -> Outcome[None]:
        if sys.platform != "win32":
            return self._outcome(
                AbsenceKind.NATIVE_DEMO_REQUIRED,
                detail=(
                    "NATIVE-DEMO-REQUIRED: msvcrt.locking(fd, LK_NBLCK, nbytes). "
                    f"fd={fd} nbytes={nbytes}."
                ),
            )
        return _msvcrt_lock_windows(self, fd, nbytes)

    def posix_fcntl_lock(self, fd: int) -> Outcome[None]:
        return self._outcome(
            AbsenceKind.NATIVE_DEMO_REQUIRED,
            detail="fcntl is not the Windows lock primitive; use msvcrt_locking",
        )


def detect_platform_adapter(clock: Clock | None = None) -> PlatformAdapter:
    if sys.platform == "win32":
        return WindowsPlatformAdapter(clock=clock)
    return PosixPlatformAdapter(clock=clock)


class _InotifyUnavailable(RuntimeError):
    pass


def _inotify_wait(path: str, timeout_s: float) -> list[FileChange]:
    libc_name = ctypes.util.find_library("c")
    if libc_name is None:
        raise _InotifyUnavailable("libc not found; inotify unavailable")
    libc = ctypes.CDLL(libc_name, use_errno=True)
    libc.inotify_init1.argtypes = [ctypes.c_int]
    libc.inotify_init1.restype = ctypes.c_int
    libc.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
    libc.inotify_add_watch.restype = ctypes.c_int

    fd = libc.inotify_init1(IN_CLOEXEC)
    if fd < 0:
        err = ctypes.get_errno()
        raise _InotifyUnavailable(f"inotify_init1 failed errno={err}")
    try:
        watch = libc.inotify_add_watch(
            fd,
            path.encode("utf-8"),
            IN_CREATE | IN_MOVED_TO | IN_CLOSE_WRITE,
        )
        if watch < 0:
            err = ctypes.get_errno()
            raise _InotifyUnavailable(f"inotify_add_watch failed errno={err}")
        ready, _, _ = select.select([fd], [], [], timeout_s)
        if not ready:
            return []
        raw = os.read(fd, 4096)
        return _parse_inotify_events(raw)
    finally:
        os.close(fd)


def _parse_inotify_events(raw: bytes) -> list[FileChange]:
    events: list[FileChange] = []
    offset = 0
    while offset + INOTIFY_EVENT_SIZE <= len(raw):
        _wd, mask, _cookie, name_len = struct.unpack_from(
            INOTIFY_EVENT_FMT, raw, offset
        )
        offset += INOTIFY_EVENT_SIZE
        name_bytes = raw[offset : offset + name_len]
        offset += name_len
        name = name_bytes.split(b"\x00", 1)[0].decode("utf-8", "surrogateescape")
        kind = "modified"
        if mask & IN_CREATE:
            kind = "created"
        elif mask & IN_MOVED_TO:
            kind = "moved_to"
        events.append(FileChange(kind=kind, name=name, mask=int(mask)))
    return events


def _read_directory_changes_w(
    adapter: WindowsPlatformAdapter,
    path: Path,
    timeout_s: float,
) -> Outcome[list[FileChange]]:
    """Live Windows inbox wakeup. Invoked only on win32."""
    import ctypes.wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    FILE_LIST_DIRECTORY = 0x0001
    FILE_SHARE_READ = 0x00000001
    FILE_SHARE_WRITE = 0x00000002
    FILE_SHARE_DELETE = 0x00000004
    OPEN_EXISTING = 3
    FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
    FILE_NOTIFY_CHANGE_FILE_NAME = 0x00000001
    FILE_NOTIFY_CHANGE_LAST_WRITE = 0x00000010
    INVALID_HANDLE_VALUE = ctypes.wintypes.HANDLE(-1).value

    native = adapter.native_fs_path(path)
    if native.kind is not AbsenceKind.FOUND or native.value is None:
        return Outcome(
            kind=native.kind,
            value=None,
            detail=native.detail,
            observed_at=native.observed_at,
            observed_epoch=native.observed_epoch,
            worker_id=native.worker_id,
            path=native.path,
        )

    handle = kernel32.CreateFileW(
        native.value,
        FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        None,
    )
    if handle == INVALID_HANDLE_VALUE:
        err = ctypes.get_last_error()
        return adapter._outcome(
            AbsenceKind.UNREADABLE,
            detail=f"CreateFileW(inbox) failed last_error={err}",
            path=native.value,
        )
    buf = ctypes.create_string_buffer(4096)
    bytes_returned = ctypes.wintypes.DWORD(0)
    ok = kernel32.ReadDirectoryChangesW(
        handle,
        buf,
        4096,
        False,
        FILE_NOTIFY_CHANGE_FILE_NAME | FILE_NOTIFY_CHANGE_LAST_WRITE,
        ctypes.byref(bytes_returned),
        None,
        None,
    )
    kernel32.CloseHandle(handle)
    if not ok:
        err = ctypes.get_last_error()
        return adapter._outcome(
            AbsenceKind.UNREADABLE,
            detail=f"ReadDirectoryChangesW failed last_error={err} timeout_s={timeout_s}",
            path=native.value,
        )
    return adapter._outcome(
        AbsenceKind.FOUND,
        value=[],
        detail=f"ReadDirectoryChangesW bytes={bytes_returned.value}",
        path=native.value,
    )


def _job_object_contain_windows(
    adapter: WindowsPlatformAdapter, pid: int
) -> Outcome[str]:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        err = ctypes.get_last_error()
        return adapter._outcome(
            AbsenceKind.UNREADABLE,
            detail=f"CreateJobObjectW failed last_error={err}",
        )
    PROCESS_SET_QUOTA = 0x0100
    PROCESS_TERMINATE = 0x0001
    process = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, False, pid)
    if not process:
        err = ctypes.get_last_error()
        kernel32.CloseHandle(job)
        return adapter._outcome(
            AbsenceKind.NOT_FOUND,
            detail=f"OpenProcess({pid}) failed last_error={err}",
        )
    assigned = kernel32.AssignProcessToJobObject(job, process)
    kernel32.CloseHandle(process)
    if not assigned:
        err = ctypes.get_last_error()
        kernel32.CloseHandle(job)
        return adapter._outcome(
            AbsenceKind.REFUSED,
            detail=f"AssignProcessToJobObject failed last_error={err}",
        )
    return adapter._outcome(
        AbsenceKind.FOUND,
        value=f"job_handle={int(job)}",
        detail=f"process {pid} assigned to Job Object",
    )


def _msvcrt_lock_windows(
    adapter: WindowsPlatformAdapter, fd: int, nbytes: int
) -> Outcome[None]:
    try:
        import msvcrt
    except ImportError:
        return adapter._outcome(
            AbsenceKind.NOT_IN_RECORD,
            detail="msvcrt module missing on this interpreter",
        )
    try:
        msvcrt.locking(fd, msvcrt.LK_NBLCK, nbytes)
    except OSError as exc:
        return adapter._outcome(
            AbsenceKind.REFUSED,
            detail=f"msvcrt.locking refused: {exc}",
        )
    return adapter._outcome(AbsenceKind.FOUND, detail="msvcrt.LK_NBLCK")


def aware_now_for_docs() -> datetime:
    return SystemClock().now()
