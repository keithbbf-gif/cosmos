"""Platform adapter: container-run POSIX paths plus NATIVE-DEMO-REQUIRED Windows surfaces."""

from __future__ import annotations

from pathlib import Path

from cosmos.spikes.cosmos_mail.clock import SystemClock
from cosmos.spikes.cosmos_mail.platform import (
    PosixPlatformAdapter,
    WindowsPlatformAdapter,
    detect_platform_adapter,
)
from cosmos.spikes.cosmos_mail.types import AbsenceKind


def test_detect_platform_is_posix_in_this_container() -> None:
    adapter = detect_platform_adapter()
    assert adapter.name == "posix"


def test_posix_refuses_windows_drive_and_backslash() -> None:
    adapter = PosixPlatformAdapter(clock=SystemClock())
    drive = adapter.interpret_drive(r"V:\Ai\_queue")
    assert drive.kind is AbsenceKind.REFUSED
    slash = adapter.reject_foreign_separators(r"COW_TO_QA_ENGINEER.md")
    # no backslash — accepted
    assert slash.kind is AbsenceKind.FOUND
    foreign = adapter.reject_foreign_separators("V:\\Research4\\letter.md")
    assert foreign.kind is AbsenceKind.REFUSED
    native = adapter.native_fs_path(Path("V:\\Research4\\letter.md"))
    assert native.kind is AbsenceKind.REFUSED


def test_posix_drive_absence_is_not_in_record() -> None:
    adapter = PosixPlatformAdapter(clock=SystemClock())
    result = adapter.interpret_drive("/workspace/mail")
    assert result.kind is AbsenceKind.NOT_IN_RECORD


def test_windows_extended_prefix_is_pure_and_testable() -> None:
    adapter = WindowsPlatformAdapter(clock=SystemClock())
    result = adapter.native_fs_path(Path(r"V:\A\Ai\COSMOS") / ("n" * 80))
    assert result.kind is AbsenceKind.FOUND
    assert isinstance(result.value, str)
    assert result.value.startswith("\\\\?\\")


def test_windows_drive_letter_is_configuration() -> None:
    adapter = WindowsPlatformAdapter(clock=SystemClock())
    result = adapter.interpret_drive(r"V:\A\Ai\COSMOS")
    assert result.kind is AbsenceKind.FOUND
    assert result.value is not None
    assert result.value.letter == "V"
    missing = adapter.interpret_drive("/no/drive")
    assert missing.kind is AbsenceKind.NOT_IN_RECORD


def test_windows_natives_are_native_demo_required_off_win32() -> None:
    adapter = WindowsPlatformAdapter(clock=SystemClock())
    job = adapter.job_object_contain(1)
    watch = adapter.watch_directory(Path("/tmp"), 0.1)
    lock = adapter.msvcrt_locking(0)
    created = adapter.exclusive_create(
        Path("/tmp/never-created-by-windows-adapter.json")
    )
    assert job.kind is AbsenceKind.NATIVE_DEMO_REQUIRED
    assert watch.kind is AbsenceKind.NATIVE_DEMO_REQUIRED
    assert lock.kind is AbsenceKind.NATIVE_DEMO_REQUIRED
    assert created.kind is AbsenceKind.NATIVE_DEMO_REQUIRED
    assert "ReadDirectoryChangesW" in (watch.detail or "")
    assert "Job Object" in (job.detail or "") or "CreateJobObjectW" in (
        job.detail or ""
    )
    assert "msvcrt" in (lock.detail or "")


def test_posix_job_object_and_msvcrt_are_native_demo_required() -> None:
    adapter = PosixPlatformAdapter(clock=SystemClock())
    assert adapter.job_object_contain(1).kind is AbsenceKind.NATIVE_DEMO_REQUIRED
    assert adapter.msvcrt_locking(0).kind is AbsenceKind.NATIVE_DEMO_REQUIRED


def test_posix_fcntl_lock_round_trip(tmp_path: Path) -> None:
    adapter = PosixPlatformAdapter(clock=SystemClock())
    path = tmp_path / "lockme"
    created = adapter.exclusive_create(path)
    assert created.kind is AbsenceKind.FOUND
    assert created.value is not None
    locked = adapter.posix_fcntl_lock(created.value.fd)
    assert locked.kind is AbsenceKind.FOUND
    adapter.write_fsync_close(created.value, b"ok\n")


def test_watch_missing_path_is_not_found(tmp_path: Path) -> None:
    adapter = PosixPlatformAdapter(clock=SystemClock())
    result = adapter.watch_directory(tmp_path / "missing", 0.05)
    assert result.kind is AbsenceKind.NOT_FOUND


def test_watch_file_is_unreadable(tmp_path: Path) -> None:
    adapter = PosixPlatformAdapter(clock=SystemClock())
    target = tmp_path / "notdir"
    target.write_text("x", encoding="utf-8")
    result = adapter.watch_directory(target, 0.05)
    assert result.kind is AbsenceKind.UNREADABLE
