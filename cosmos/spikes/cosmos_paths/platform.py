"""Platform adapter: the only place Windows path, drive, Job Object, watch, and msvcrt live.

Business code never prefixes \\\\?\\, never calls msvcrt, never opens a Job Object,
and never treats a backslash string as a POSIX filename.

Container-run parts (POSIX walk, drive-string logic, fcntl advisory lock, typed
refusals for Windows APIs) are tested here.

Windows-run parts are implemented and marked NATIVE-DEMO-REQUIRED for the
queue-lane demo on live Windows:
  - Job Objects (CreateJobObjectW / AssignProcessToJobObject)
  - ReadDirectoryChangesW
  - live drive/volume queries (GetDriveTypeW / GetVolumeInformationW)
  - msvcrt.locking
  - MAX_PATH WinError 3 without the extended-length prefix
"""

from __future__ import annotations

import os
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

from .absence import AbsenceKind, Absent, Found, TypedRefusal, TypedResult
from .stamp import now_stamp

# Incumbent incident: a 275-char path returns WinError 3 without \\\\?\\.
MAX_PATH_WINDOWS = 260
LONG_PATH_DEMO_CHARS = 275

_DRIVE_ABS = re.compile(r"^[A-Za-z]:[\\/]")
_EXTENDED = re.compile(r"^\\\\\?\\", re.IGNORECASE)
_EXTENDED_UNC = re.compile(r"^\\\\\?\\UNC\\", re.IGNORECASE)
_UNC = re.compile(r"^\\\\[^?\\]")


@dataclass(frozen=True)
class DriveParts:
    drive: str
    tail: str
    kind: str  # "drive" | "unc" | "extended-drive" | "extended-unc" | "none"


def host_is_windows() -> bool:
    return sys.platform == "win32"


def looks_like_windows_path(text: str) -> bool:
    if _EXTENDED.match(text) or _UNC.match(text) or _DRIVE_ABS.match(text):
        return True
    return False


def looks_like_posix_absolute(text: str) -> bool:
    return text.startswith("/") and not text.startswith("//")


class DriveSemantics:
    """Windows drive / UNC / extended-length string algebra.

    This layer is host-independent: it does not open files. Live volume
    queries are a separate NATIVE-DEMO-REQUIRED method on the adapter.
    """

    @staticmethod
    def split(text: str) -> DriveParts:
        if _EXTENDED_UNC.match(text):
            rest = text[8:]  # after \\?\UNC\
            return DriveSemantics._unc_parts(rest, kind="extended-unc")
        if _EXTENDED.match(text):
            body = text[4:]
            if _DRIVE_ABS.match(body):
                return DriveParts(drive=body[:2].upper(), tail=body[2:].replace("/", "\\"), kind="extended-drive")
            return DriveParts(drive="", tail=body, kind="extended-drive")
        if _UNC.match(text):
            return DriveSemantics._unc_parts(text[2:], kind="unc")
        if _DRIVE_ABS.match(text):
            return DriveParts(drive=text[:2].upper(), tail=text[2:].replace("/", "\\"), kind="drive")
        return DriveParts(drive="", tail=text, kind="none")

    @staticmethod
    def _unc_parts(rest: str, kind: str) -> DriveParts:
        cleaned = rest.replace("/", "\\").lstrip("\\")
        bits = cleaned.split("\\")
        if len(bits) < 2:
            return DriveParts(drive="\\\\" + cleaned, tail="", kind=kind)
        share = "\\\\" + bits[0] + "\\" + bits[1]
        tail = ("\\" + "\\".join(bits[2:])) if len(bits) > 2 else ""
        return DriveParts(drive=share, tail=tail, kind=kind)

    @staticmethod
    def normalize_drive_letter(text: str) -> str:
        parts = DriveSemantics.split(text)
        if parts.kind in {"drive", "extended-drive"} and parts.drive:
            letter = parts.drive[0].upper() + ":"
            prefix = "\\\\?\\" if parts.kind == "extended-drive" else ""
            tail = parts.tail if parts.tail.startswith("\\") else ("\\" + parts.tail if parts.tail else "\\")
            return prefix + letter + tail
        return text

    @staticmethod
    def is_extended(text: str) -> bool:
        return bool(_EXTENDED.match(text))

    @staticmethod
    def to_extended_length(text: str) -> str:
        """\\\\?\\ for local drives, \\\\?\\UNC\\ for UNC. Never double-prefix."""
        if _EXTENDED.match(text):
            return text
        if _UNC.match(text):
            return "\\\\?\\UNC\\" + text.lstrip("\\")
        if _DRIVE_ABS.match(text):
            norm = DriveSemantics.normalize_drive_letter(text)
            return "\\\\?\\" + norm
        raise TypedRefusal(
            AbsenceKind.REFUSED,
            "extended-length form requires an absolute Windows drive or UNC path",
            path=text,
        )

    @staticmethod
    def from_extended_length(text: str) -> str:
        if _EXTENDED_UNC.match(text):
            return "\\\\" + text[8:]
        if _EXTENDED.match(text):
            return text[4:]
        return text

    @staticmethod
    def same_drive(a: str, b: str) -> bool:
        pa, pb = DriveSemantics.split(a), DriveSemantics.split(b)
        if not pa.drive or not pb.drive:
            return False
        return pa.drive.upper() == pb.drive.upper()

    @staticmethod
    def roots_are_distinct(a: str, b: str) -> bool:
        return DriveSemantics.normalize_for_compare(a) != DriveSemantics.normalize_for_compare(b)

    @staticmethod
    def normalize_for_compare(text: str) -> str:
        if looks_like_windows_path(text):
            ext = DriveSemantics.to_extended_length(text) if not DriveSemantics.is_extended(text) else text
            stripped = DriveSemantics.from_extended_length(ext)
            return stripped.replace("/", "\\").rstrip("\\").upper()
        return str(Path(text))


@dataclass(frozen=True)
class WalkHit:
    directory: Path
    dirnames: tuple[str, ...]
    filenames: tuple[str, ...]


@dataclass(frozen=True)
class LockHandle:
    path: Path
    fd: int
    mechanism: str

    def release(self) -> None:
        try:
            os.close(self.fd)
        except OSError:
            pass


class PlatformAdapter:
    """Single owner of OS filesystem, containment, watch, and lock primitives."""

    def __init__(self) -> None:
        self.windows = host_is_windows()

    def native_root_text(self, configured_root: str) -> TypedResult[str]:
        """Refuse the two-universes defect: a Windows path is not a POSIX filename."""
        text = configured_root.strip()
        if not text:
            return Absent(AbsenceKind.REFUSED, "configured root is empty", {"path": configured_root})
        if self.windows:
            if looks_like_posix_absolute(text) and not looks_like_windows_path(text):
                return Absent(
                    AbsenceKind.REFUSED,
                    "POSIX absolute root refused on Windows; drive letter is configuration, not a guess",
                    {"path": text, "host": sys.platform},
                )
            if not looks_like_windows_path(text):
                return Absent(
                    AbsenceKind.REFUSED,
                    "Windows host requires an absolute drive or UNC root",
                    {"path": text},
                )
            return Found(DriveSemantics.normalize_drive_letter(text), "windows root accepted", {"path": text})
        if looks_like_windows_path(text):
            return Absent(
                AbsenceKind.REFUSED,
                "Windows drive/UNC root refused on POSIX — a backslash string must not become a filename",
                {"path": text, "host": sys.platform, "scar": "two-universes-2016-08-16"},
            )
        if not looks_like_posix_absolute(text):
            return Absent(
                AbsenceKind.REFUSED,
                "POSIX host requires an absolute root; relative and guessed paths are refused",
                {"path": text},
            )
        return Found(text, "posix root accepted", {"path": text})

    def for_filesystem(self, path: Path | str) -> str:
        text = str(path)
        if self.windows:
            if looks_like_windows_path(text):
                return DriveSemantics.to_extended_length(text)
            resolved = str(Path(text).resolve())
            if looks_like_windows_path(resolved):
                return DriveSemantics.to_extended_length(resolved)
            return resolved
        return text

    def from_filesystem(self, text: str) -> Path:
        if self.windows and DriveSemantics.is_extended(text):
            return Path(DriveSemantics.from_extended_length(text))
        return Path(text)

    def exists(self, path: Path | str) -> bool:
        return os.path.lexists(self.for_filesystem(path))

    def is_dir(self, path: Path | str) -> bool:
        try:
            return stat.S_ISDIR(os.stat(self.for_filesystem(path)).st_mode)
        except OSError:
            return False

    def is_file(self, path: Path | str) -> bool:
        try:
            return stat.S_ISREG(os.stat(self.for_filesystem(path)).st_mode)
        except OSError:
            return False

    def probe(self, path: Path | str) -> TypedResult[Path]:
        fs = self.for_filesystem(path)
        logical = self.from_filesystem(fs) if self.windows else Path(str(path))
        if not os.path.lexists(fs):
            return Absent(AbsenceKind.NOT_FOUND, "path does not exist", {"path": str(path)})
        try:
            mode = os.stat(fs).st_mode
        except OSError as exc:
            return Absent(AbsenceKind.UNREADABLE, f"stat failed: {exc}", {"path": str(path)})
        return Found(logical, "path present", {"path": str(path), "mode": int(mode)})

    def read_bytes(self, path: Path | str) -> TypedResult[bytes]:
        fs = self.for_filesystem(path)
        if not os.path.lexists(fs):
            return Absent(AbsenceKind.NOT_FOUND, "file does not exist", {"path": str(path)})
        try:
            if stat.S_ISDIR(os.stat(fs).st_mode):
                return Absent(
                    AbsenceKind.UNREADABLE,
                    "path exists as a directory; cannot read file bytes",
                    {"path": str(path)},
                )
        except OSError as exc:
            return Absent(AbsenceKind.UNREADABLE, f"stat failed: {exc}", {"path": str(path)})
        try:
            with open(fs, "rb") as handle:
                data = handle.read()
        except OSError as exc:
            return Absent(AbsenceKind.UNREADABLE, f"read failed: {exc}", {"path": str(path)})
        return Found(data, "read ok", {"path": str(path), "bytes": len(data)})

    def write_bytes(self, path: Path | str, data: bytes) -> TypedResult[Path]:
        fs = self.for_filesystem(path)
        parent = os.path.dirname(fs)
        try:
            os.makedirs(parent, exist_ok=True)
            with open(fs, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            return Absent(AbsenceKind.UNREADABLE, f"write failed: {exc}", {"path": str(path)})
        return Found(self.from_filesystem(fs), "write ok", {"path": str(path), "bytes": len(data)})

    def listdir(self, path: Path | str) -> TypedResult[tuple[str, ...]]:
        fs = self.for_filesystem(path)
        if not os.path.lexists(fs):
            return Absent(AbsenceKind.NOT_FOUND, "directory does not exist", {"path": str(path)})
        try:
            names = tuple(sorted(os.listdir(fs)))
        except OSError as exc:
            return Absent(AbsenceKind.UNREADABLE, f"listdir failed: {exc}", {"path": str(path)})
        return Found(names, "listdir ok", {"path": str(path), "count": len(names)})

    def walk(self, root: Path | str) -> TypedResult[tuple[WalkHit, ...]]:
        fs = self.for_filesystem(root)
        if not os.path.lexists(fs):
            return Absent(AbsenceKind.NOT_FOUND, "walk root does not exist", {"path": str(root)})
        hits: list[WalkHit] = []
        try:
            for dirpath, dirnames, filenames in os.walk(fs):
                hits.append(
                    WalkHit(
                        directory=self.from_filesystem(dirpath),
                        dirnames=tuple(dirnames),
                        filenames=tuple(filenames),
                    )
                )
        except OSError as exc:
            return Absent(AbsenceKind.UNREADABLE, f"walk failed: {exc}", {"path": str(root)})
        return Found(tuple(hits), "walk ok", {"path": str(root), "dirs": len(hits)})

    def normalize_under_root(self, root: Path, candidate: Path) -> TypedResult[Path]:
        try:
            resolved_root = Path(self.for_filesystem(root)).resolve()
            resolved_cand = Path(self.for_filesystem(candidate)).resolve()
        except OSError as exc:
            return Absent(AbsenceKind.UNREADABLE, f"resolve failed: {exc}", {"root": str(root), "path": str(candidate)})
        try:
            resolved_cand.relative_to(resolved_root)
        except ValueError:
            return Absent(
                AbsenceKind.REFUSED,
                "path escapes the configured root after normalization",
                {"root": str(resolved_root), "path": str(resolved_cand)},
            )
        return Found(resolved_cand, "normalized under root", {"root": str(resolved_root)})

    def advisory_lock(self, path: Path | str) -> TypedResult[LockHandle]:
        """Portable advisory lock: fcntl on POSIX, msvcrt.locking on Windows."""
        if self.windows:
            return self.msvcrt_locking(path)
        return self._fcntl_lock(path)

    def _fcntl_lock(self, path: Path | str) -> TypedResult[LockHandle]:
        import fcntl

        fs = self.for_filesystem(path)
        try:
            fd = os.open(fs, os.O_RDWR | os.O_CREAT, 0o644)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            return Absent(AbsenceKind.REFUSED, f"fcntl lock failed: {exc}", {"path": str(path)})
        return Found(
            LockHandle(path=Path(str(path)), fd=fd, mechanism="fcntl.flock"),
            "fcntl exclusive lock held",
            {"path": str(path)},
        )

    def msvcrt_locking(self, path: Path | str) -> TypedResult[LockHandle]:
        """msvcrt.locking — Windows CRT byte-range lock.

        NATIVE-DEMO-REQUIRED on live Windows for the queue-lane demo.
        """
        if not self.windows:
            return Absent(
                AbsenceKind.NATIVE_DEMO_REQUIRED,
                "msvcrt.locking is a Windows CRT call; run the queue-lane demo on native Windows",
                {
                    "api": "msvcrt.locking",
                    "modes": ["LK_NBLCK", "LK_UNLCK"],
                    "host": sys.platform,
                    "demo": "NATIVE-DEMO-REQUIRED",
                },
            )
        try:
            import msvcrt
        except ImportError as exc:
            return Absent(AbsenceKind.UNSUPPORTED_PLATFORM, f"msvcrt missing: {exc}", {"path": str(path)})
        fs = self.for_filesystem(path)
        try:
            fd = os.open(fs, os.O_RDWR | os.O_CREAT, 0o644)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            return Absent(AbsenceKind.REFUSED, f"msvcrt.locking failed: {exc}", {"path": str(path)})
        return Found(
            LockHandle(path=Path(str(path)), fd=fd, mechanism="msvcrt.locking"),
            "msvcrt exclusive lock held",
            {"path": str(path), "demo": "native-windows"},
        )

    def create_job_object(self, name: str) -> TypedResult[int]:
        """Windows Job Object containment.

        NATIVE-DEMO-REQUIRED: CreateJobObjectW + JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        for the queue-lane demo (DOM/worker descendant kill).
        """
        if not self.windows:
            return Absent(
                AbsenceKind.NATIVE_DEMO_REQUIRED,
                "CreateJobObjectW requires native Windows; container cannot exercise Job Objects",
                {
                    "api": "CreateJobObjectW",
                    "also": ["AssignProcessToJobObject", "SetInformationJobObject"],
                    "limit": "JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE",
                    "host": sys.platform,
                    "demo": "NATIVE-DEMO-REQUIRED",
                },
            )
        return self._win_create_job_object(name)

    def assign_process_to_job_object(self, job_handle: int, process_id: int) -> TypedResult[int]:
        if not self.windows:
            return Absent(
                AbsenceKind.NATIVE_DEMO_REQUIRED,
                "AssignProcessToJobObject requires native Windows",
                {"api": "AssignProcessToJobObject", "host": sys.platform, "demo": "NATIVE-DEMO-REQUIRED"},
            )
        return self._win_assign_pid(job_handle, process_id)

    def read_directory_changes(self, path: Path | str, timeout_ms: int = 1) -> TypedResult[tuple[str, ...]]:
        """ReadDirectoryChangesW — interrupt-driven wakeup for the queue-lane demo.

        NATIVE-DEMO-REQUIRED on live Windows. Measured latency vs the 60 s poll
        belongs to that native run, not this container.
        """
        if not self.windows:
            return Absent(
                AbsenceKind.NATIVE_DEMO_REQUIRED,
                "ReadDirectoryChangesW requires native Windows; queue-lane demo measures wakeup vs 60s poll",
                {
                    "api": "ReadDirectoryChangesW",
                    "also": ["CreateFileW FILE_FLAG_BACKUP_SEMANTICS"],
                    "timeout_ms": timeout_ms,
                    "host": sys.platform,
                    "demo": "NATIVE-DEMO-REQUIRED",
                    "poll_baseline_s": 60,
                },
            )
        return self._win_read_directory_changes(path, timeout_ms)

    def windows_volume_info(self, root: str) -> TypedResult[dict[str, object]]:
        """GetDriveTypeW / GetVolumeInformationW.

        NATIVE-DEMO-REQUIRED. Drive-letter string algebra is tested here; live
        volume identity is a Windows-run measurement.
        """
        if not self.windows:
            return Absent(
                AbsenceKind.NATIVE_DEMO_REQUIRED,
                "GetDriveTypeW/GetVolumeInformationW require native Windows",
                {"api": "GetDriveTypeW", "also": ["GetVolumeInformationW"], "root": root, "demo": "NATIVE-DEMO-REQUIRED"},
            )
        return self._win_volume_info(root)

    def max_path_winerror3_without_prefix(self, long_path: Path | str) -> TypedResult[str]:
        """Reproduce the incumbent MAX_PATH scar: 275 chars → WinError 3 without \\\\?\\.

        NATIVE-DEMO-REQUIRED. POSIX hosts have no MAX_PATH=260 clamp; the
        container proves the walk and the prefix algebra, not WinError 3.
        """
        if not self.windows:
            return Absent(
                AbsenceKind.NATIVE_DEMO_REQUIRED,
                "WinError 3 on a 275-char path without \\\\?\\ is a Windows MAX_PATH behavior",
                {
                    "chars": LONG_PATH_DEMO_CHARS,
                    "max_path": MAX_PATH_WINDOWS,
                    "host": sys.platform,
                    "demo": "NATIVE-DEMO-REQUIRED",
                    "path_len": len(str(long_path)),
                },
            )
        raw = str(long_path)
        if DriveSemantics.is_extended(raw):
            return Absent(AbsenceKind.REFUSED, "demo requires the unprefixed path", {"path": raw})
        try:
            os.stat(raw)
        except OSError as exc:
            winerr = getattr(exc, "winerror", None)
            if winerr == 3:
                return Found(
                    "WinError 3",
                    "unprefixed long path produced WinError 3 as expected",
                    {"winerror": 3, "chars": len(raw)},
                )
            return Absent(AbsenceKind.REFUSED, f"unexpected OSError: {exc}", {"winerror": winerr})
        return Absent(
            AbsenceKind.REFUSED,
            "unprefixed long path was reachable; host MAX_PATH policy may be disabled",
            {"path": raw, "chars": len(raw)},
        )

    def long_path_demo_target(self, under: Path, filename: str = "payload.txt") -> Path:
        """Build a path whose string length is at least LONG_PATH_DEMO_CHARS."""
        # Segment length stays well under NAME_MAX (255) on POSIX.
        segment = "L" * 40
        current = Path(under)
        while len(str(current / filename)) < LONG_PATH_DEMO_CHARS:
            current = current / segment
        return current / filename

    def native_demo_checklist(self) -> tuple[dict[str, str], ...]:
        stamp = now_stamp()
        items = (
            {
                "item": "Job Objects",
                "api": "CreateJobObjectW/AssignProcessToJobObject",
                "status": "NATIVE-DEMO-REQUIRED",
                "why": "queue-lane worker/DOM descendant containment",
            },
            {
                "item": "ReadDirectoryChangesW",
                "api": "ReadDirectoryChangesW",
                "status": "NATIVE-DEMO-REQUIRED",
                "why": "interrupt-driven queue wakeup vs 60s poll",
            },
            {
                "item": "msvcrt.locking",
                "api": "msvcrt.locking",
                "status": "NATIVE-DEMO-REQUIRED",
                "why": "Windows CRT advisory lock counterpart to fcntl",
            },
            {
                "item": "live drive/volume",
                "api": "GetDriveTypeW/GetVolumeInformationW",
                "status": "NATIVE-DEMO-REQUIRED",
                "why": "second-install letter V: vs D: on real volumes",
            },
            {
                "item": "MAX_PATH WinError 3",
                "api": "stat without \\\\?\\ on 275+ char path",
                "status": "NATIVE-DEMO-REQUIRED",
                "why": "incumbent C-60; prefix algebra is tested in-container",
            },
        )
        for row in items:
            row["worker_id"] = stamp.worker_id
            row["epoch"] = str(stamp.epoch)
        return items

    # --- Windows ctypes implementations (dead on POSIX; live on native demo) ---

    def _win_create_job_object(self, name: str) -> TypedResult[int]:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        handle = kernel32.CreateJobObjectW(None, name)
        if not handle:
            err = ctypes.get_last_error()
            return Absent(AbsenceKind.REFUSED, f"CreateJobObjectW failed winerr={err}", {"name": name})
        # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE so descendants die with the job.
        JobObjectExtendedLimitInformation = 9
        JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000

        class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
                ("PerJobUserTimeLimit", wintypes.LARGE_INTEGER),
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
                ("ReadOperationCount", ctypes.c_ulonglong),
                ("WriteOperationCount", ctypes.c_ulonglong),
                ("OtherOperationCount", ctypes.c_ulonglong),
                ("ReadTransferCount", ctypes.c_ulonglong),
                ("WriteTransferCount", ctypes.c_ulonglong),
                ("OtherTransferCount", ctypes.c_ulonglong),
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

        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        kernel32.SetInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            wintypes.LPVOID,
            wintypes.DWORD,
        ]
        kernel32.SetInformationJobObject.restype = wintypes.BOOL
        ok = kernel32.SetInformationJobObject(
            handle,
            JobObjectExtendedLimitInformation,
            ctypes.byref(info),
            ctypes.sizeof(info),
        )
        if not ok:
            err = ctypes.get_last_error()
            return Absent(AbsenceKind.REFUSED, f"SetInformationJobObject failed winerr={err}", {"name": name})
        return Found(int(handle), "job object created", {"name": name, "handle": int(handle)})

    def _win_assign_pid(self, job_handle: int, process_id: int) -> TypedResult[int]:
        import ctypes
        from ctypes import wintypes

        PROCESS_SET_QUOTA = 0x0100
        PROCESS_TERMINATE = 0x0001
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        proc = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, False, process_id)
        if not proc:
            return Absent(AbsenceKind.REFUSED, f"OpenProcess failed pid={process_id}", {"pid": process_id})
        kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        ok = kernel32.AssignProcessToJobObject(job_handle, proc)
        kernel32.CloseHandle(proc)
        if not ok:
            err = ctypes.get_last_error()
            return Absent(AbsenceKind.REFUSED, f"AssignProcessToJobObject failed winerr={err}", {"pid": process_id})
        return Found(process_id, "process assigned to job", {"pid": process_id, "job": job_handle})

    def _win_read_directory_changes(self, path: Path | str, timeout_ms: int) -> TypedResult[tuple[str, ...]]:
        import ctypes
        from ctypes import wintypes

        FILE_LIST_DIRECTORY = 0x0001
        FILE_SHARE_READ = 0x00000001
        FILE_SHARE_WRITE = 0x00000002
        FILE_SHARE_DELETE = 0x00000004
        OPEN_EXISTING = 3
        FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
        FILE_NOTIFY_CHANGE_FILE_NAME = 0x00000001
        FILE_NOTIFY_CHANGE_DIR_NAME = 0x00000002
        FILE_NOTIFY_CHANGE_LAST_WRITE = 0x00000010
        INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateFileW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        ]
        kernel32.CreateFileW.restype = wintypes.HANDLE
        fs = self.for_filesystem(path)
        handle = kernel32.CreateFileW(
            fs,
            FILE_LIST_DIRECTORY,
            FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
            None,
            OPEN_EXISTING,
            FILE_FLAG_BACKUP_SEMANTICS,
            None,
        )
        if handle == INVALID_HANDLE_VALUE:
            err = ctypes.get_last_error()
            return Absent(AbsenceKind.UNREADABLE, f"CreateFileW on directory failed winerr={err}", {"path": str(path)})

        class FILE_NOTIFY_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("NextEntryOffset", wintypes.DWORD),
                ("Action", wintypes.DWORD),
                ("FileNameLength", wintypes.DWORD),
                ("FileName", wintypes.WCHAR * 1),
            ]

        buf_size = 4096
        buf = ctypes.create_string_buffer(buf_size)
        bytes_returned = wintypes.DWORD(0)
        kernel32.ReadDirectoryChangesW.argtypes = [
            wintypes.HANDLE,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.BOOL,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            wintypes.LPVOID,
            wintypes.LPVOID,
        ]
        kernel32.ReadDirectoryChangesW.restype = wintypes.BOOL
        # Blocking call; native demo should use overlapped I/O + WaitForSingleObject(timeout_ms).
        _ = timeout_ms
        ok = kernel32.ReadDirectoryChangesW(
            handle,
            buf,
            buf_size,
            True,
            FILE_NOTIFY_CHANGE_FILE_NAME | FILE_NOTIFY_CHANGE_DIR_NAME | FILE_NOTIFY_CHANGE_LAST_WRITE,
            ctypes.byref(bytes_returned),
            None,
            None,
        )
        kernel32.CloseHandle(handle)
        if not ok:
            err = ctypes.get_last_error()
            return Absent(AbsenceKind.UNREADABLE, f"ReadDirectoryChangesW failed winerr={err}", {"path": str(path)})
        names: list[str] = []
        offset = 0
        while bytes_returned.value and offset < bytes_returned.value:
            info = FILE_NOTIFY_INFORMATION.from_buffer_copy(buf.raw[offset:])
            nbytes = info.FileNameLength
            raw_name = buf.raw[offset + 12 : offset + 12 + nbytes]
            names.append(raw_name.decode("utf-16le", errors="replace"))
            if info.NextEntryOffset == 0:
                break
            offset += info.NextEntryOffset
        return Found(tuple(names), "directory changes read", {"path": str(path), "count": len(names)})

    def _win_volume_info(self, root: str) -> TypedResult[dict[str, object]]:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetDriveTypeW.argtypes = [wintypes.LPCWSTR]
        kernel32.GetDriveTypeW.restype = wintypes.UINT
        drive = PureWindowsPath(DriveSemantics.from_extended_length(root)).anchor
        if not drive.endswith("\\"):
            drive = drive + "\\"
        dtype = kernel32.GetDriveTypeW(drive)
        vol = ctypes.create_unicode_buffer(261)
        fsname = ctypes.create_unicode_buffer(261)
        serial = wintypes.DWORD(0)
        maxcomp = wintypes.DWORD(0)
        flags = wintypes.DWORD(0)
        kernel32.GetVolumeInformationW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.LPWSTR,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            ctypes.POINTER(wintypes.DWORD),
            ctypes.POINTER(wintypes.DWORD),
            wintypes.LPWSTR,
            wintypes.DWORD,
        ]
        kernel32.GetVolumeInformationW.restype = wintypes.BOOL
        ok = kernel32.GetVolumeInformationW(
            drive, vol, 261, ctypes.byref(serial), ctypes.byref(maxcomp), ctypes.byref(flags), fsname, 261
        )
        if not ok:
            err = ctypes.get_last_error()
            return Absent(AbsenceKind.UNREADABLE, f"GetVolumeInformationW failed winerr={err}", {"drive": drive})
        payload = {
            "drive": drive,
            "drive_type": int(dtype),
            "volume_name": vol.value,
            "serial": int(serial.value),
            "filesystem": fsname.value,
        }
        return Found(payload, "volume info", payload)


def default_adapter() -> PlatformAdapter:
    return PlatformAdapter()
