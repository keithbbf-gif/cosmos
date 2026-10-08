"""Q2 — Archive rewrite + pathjail Sept 2026 shapes."""

from __future__ import annotations

from pathlib import Path

import pytest
from cosmos_code.safety.archive import ArchiveStore, CrashClass
from cosmos_code.safety.hooks import HookBus, install_defaults
from cosmos_code.safety.pathjail import PathJail, PathJailError


@pytest.fixture
def ws(tmp_path: Path):
    attempt = tmp_path / "attempt"
    delme = tmp_path / "_delme"
    attempt.mkdir()
    delme.mkdir()
    precious = attempt / "precious.txt"
    precious.write_text("keep me", encoding="utf-8")
    jail = PathJail(grants=[attempt, delme])
    store = ArchiveStore(jail, delme)
    bus = install_defaults(HookBus())
    return attempt, delme, precious, jail, store, bus


def test_rm_becomes_delme(ws):
    attempt, delme, precious, jail, store, bus = ws
    d = bus.pre("shell", {"command": f"rm -rf {precious}"})
    assert d.deny is True
    assert d.rewrite_tool == "stage_to_delme"
    dest = store.stage_to_delme(precious, reason="rm_rewrite")
    assert not precious.exists()
    assert dest.exists()
    assert dest.is_relative_to(delme) or str(dest).startswith(str(delme))
    rows = store.read_ledger()
    assert any(r.get("op") == "ARCHIVE" for r in rows)
    assert dest.read_text(encoding="utf-8") == "keep me"


def test_delete_tool_rewritten(ws):
    attempt, delme, precious, jail, store, bus = ws
    d = bus.pre("delete", {"path": str(precious)})
    assert d.deny is True
    assert d.rewrite_tool == "stage_to_delme"
    dest = store.stage_to_delme(d.rewrite_args["path"])
    assert not precious.exists()
    assert dest.exists()
    assert any(r.get("op") == "ARCHIVE" for r in store.read_ledger())


def test_raw_unlink_crash_class(ws):
    attempt, delme, precious, jail, store, bus = ws
    # harness API always raises
    with pytest.raises(CrashClass):
        ArchiveStore.raw_unlink(precious)
    # if enclosure bypassed in test double: file unlinked outside archive → CRASH
    existed = precious.exists()
    precious.unlink()  # simulate bypass
    with pytest.raises(CrashClass):
        ArchiveStore.mark_crash_if_unlinked(precious, existed_before=existed)


def test_pathjail_rejects_sept2026_shapes(ws):
    attempt, delme, precious, jail, store, bus = ws
    shapes = [
        ("../escape.txt", "dotdot"),
        ("C:foo", "drive_relative"),
        ("\\\\server\\share", "unc"),
        ("%2e%2e/secret", "encoded_dotdot"),
        ("evil\x00.txt", "null_byte"),
        ("\\Windows\\System32", "current_drive_windows"),
    ]
    for path, expect_reason in shapes:
        with pytest.raises(PathJailError) as ei:
            jail.check_shape(path)
        assert ei.value.reason == expect_reason, (path, ei.value.reason)
