"""Tests for the pathscan gate. Scratch only. No network. No live tree."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

import pathscan as pathscan_mod
from cosmos_federation import PathJail, Refuse, secret_shape
from pathscan import (
    KIND_DRIVE,
    KIND_KEITH_AI,
    KIND_KEITH_TREE,
    KIND_R2_STORE,
    KIND_TAKEN_ID,
    KIND_UNC,
    SCHEMA,
    Hit,
    scan_root,
    scan_text,
)

FAKE_DRIVE_TEXT = "seed Q:\\peer\\var\\not-here\n"


@pytest.fixture
def fake_drive_text() -> str:
    """Source text that names a drive this machine does not use."""
    return FAKE_DRIVE_TEXT


def _write(jail: PathJail, rel: str, text: str) -> None:
    dest = jail.contain(rel)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")


def _kinds(rel: str, text: str) -> list[str]:
    return [hit.kind for hit in scan_text(rel, text)]


def test_public_surface() -> None:
    assert SCHEMA == "cosmos-federation-pathscan/1"
    assert pathscan_mod.SCHEMA == SCHEMA
    assert tuple(pathscan_mod.__all__) == (
        "KIND_DRIVE",
        "KIND_KEITH_AI",
        "KIND_KEITH_TREE",
        "KIND_R2_STORE",
        "KIND_TAKEN_ID",
        "KIND_UNC",
        "SCHEMA",
        "Hit",
        "scan_root",
        "scan_text",
    )
    for name in pathscan_mod.__all__:
        assert hasattr(pathscan_mod, name)


def test_module_stays_local() -> None:
    src = pathscan_mod.__file__
    assert isinstance(src, str)
    source = Path(src).read_text(encoding="utf-8")
    for banned in ("subprocess", "socket", "urllib", "requests", "http.client", "pickle", "eval(", "exec("):
        assert banned not in source


def test_fixture_drive_path_is_a_hit(fake_drive_text: str) -> None:
    hits = scan_text("cosmos/note.py", fake_drive_text)
    assert hits == (
        Hit(rel="cosmos/note.py", line=1, kind=KIND_DRIVE, excerpt="Q:\\peer\\var\\not-here"),
    )
    assert len(hits[0].excerpt) <= 120
    assert "excerpt" in Hit.__slots__


def test_hit_is_frozen(fake_drive_text: str) -> None:
    hit = scan_text("cosmos/note.py", fake_drive_text)[0]
    try:
        setattr(hit, "line", 9)
    except AttributeError:
        return
    raise AssertionError("frozen")


def test_newline_escape_is_not_a_drive() -> None:
    # Source text keeps the backslash. A normal string reads it as a newline.
    assert scan_text("cosmos/refusals.py", "        '    if n:\\n'\n") == ()
    assert scan_text("cosmos/refusals.py", '"    if n:\\t"\n') == ()
    assert _kinds("cosmos/a.py", 'r"    if n:\\n"') == [KIND_DRIVE]
    assert _kinds("cosmos/a.py", 'fr"C:\\npm\\claude.CMD"') == [KIND_DRIVE]
    assert _kinds("cosmos/a.py", "N:\\notes") == [KIND_DRIVE]


def test_specific_roots_are_not_generic_drives() -> None:
    assert _kinds("cosmos/a.py", "V:\\A\\Ai\\COSMOS\\live") == [KIND_KEITH_TREE]
    assert _kinds("cosmos/a.py", "V:\\\\A\\\\Ai\\\\COSMOS\\\\live") == [KIND_KEITH_TREE]
    assert _kinds("cosmos/a.py", "v:/a/ai/cosmos") == [KIND_KEITH_TREE]
    assert _kinds("cosmos/a.py", "V:\\Ai\\BU.MD") == [KIND_KEITH_AI]
    assert _kinds("cosmos/a.py", "D:\\R2Cloner\\x") == [KIND_R2_STORE]
    assert _kinds("cosmos/a.py", "d:/r2cloner") == [KIND_R2_STORE]
    assert _kinds("docs/federation/g.md", "share `V:\\Ai` and `V:\\A`.") == [KIND_KEITH_AI, KIND_DRIVE]
    assert _kinds("cosmos/a.py", "V:\\Airing") == [KIND_DRIVE]


def test_taken_id_urls_and_unc_shapes() -> None:
    assert _kinds("docs/federation/n.md", "id KMesh-COSMOS-live today") == [KIND_TAKEN_ID]
    assert _kinds("docs/federation/n.md", "kmesh-cosmos-live") == [KIND_TAKEN_ID]
    assert scan_text("docs/federation/n.md", "kmesh-cosmos-liver") == ()
    assert scan_text("cosmos/a.py", "see https://example.com/a/b") == ()
    assert scan_text("kdash/index.html", "http://127.0.0.1:8770") == ()
    assert scan_text("kdash/index.html", "p://localhost:8765/x.html") == ()
    assert scan_text("cosmos/a.py", "file://open/local") == ()
    assert scan_text("cosmos/a.py", "py cosmos\\\\cosmos_backup.py\n") == ()
    assert scan_text("cosmos/a.py", '"\\\\cosmos\\\\file"\n') == ()
    assert scan_text("cosmos/a.py", "[\\\\/]\\.cache[\\\\/]") == ()
    assert _kinds("cosmos/a.py", "C:/Users/name") == [KIND_DRIVE]
    assert _kinds("docs/federation/n.md", "see \\\\files\\share\\room\n") == [KIND_UNC]
    assert _kinds("cosmos/a.py", '"\\\\\\\\server\\\\share\\\\room"') == [KIND_UNC]
    assert _kinds("cosmos/a.py", 'r"\\\\server\\share\\room"') == [KIND_UNC]
    assert _kinds("docs/federation/n.md", "//peer/share/room") == [KIND_UNC]
    assert _kinds("cosmos/a.py", "\\\\?\\C:\\Windows") == [KIND_UNC]
    assert _kinds("cosmos/a.py", "C:\\\\Users\\\\name") == [KIND_DRIVE]
    assert _kinds("serve.bat", "%~dp0live\n") == []


def test_line_order_redaction_and_cap() -> None:
    text = "ok\r\nD:\\R2Cloner\r\n"
    assert scan_text("cosmos/a.py", text)[0].line == 2
    mixed = "\\\\box\\share\\a Q:\\peer KMesh-COSMOS-live"
    assert _kinds("docs/federation/n.md", mixed) == [KIND_UNC, KIND_DRIVE, KIND_TAKEN_ID]
    outside = "Q:\\peer\\data " + ("Bearer " + "c" * 12)
    outside_hits = scan_text("cosmos/a.py", outside)
    assert "Bearer" not in outside_hits[0].excerpt
    assert secret_shape(repr(outside_hits[0])) is False
    inside = "Q:\\peer\\" + ("sk-" + "d" * 12)
    inside_hit = scan_text("cosmos/a.py", inside)[0]
    assert inside_hit.kind == KIND_DRIVE
    assert "[REDACTED]" in inside_hit.excerpt
    assert "sk-" not in inside_hit.excerpt
    assert secret_shape(inside_hit.excerpt) is False
    long_hit = scan_text("cosmos/a.py", "Q:\\" + ("e" * 200))[0]
    assert len(long_hit.excerpt) == 120
    assert scan_text("cosmos/a.py", "") == ()
    assert scan_text("cosmos/a.py", "plain words\n") == ()
    assert scan_text("cosmos\\a.py", "Q:\\peer")[0].rel == "cosmos/a.py"
    assert scan_text("cosmos/a.py", "Q:\\peer") == scan_text("cosmos/a.py", "Q:\\peer")


def test_labels_and_roots_refuse() -> None:
    samples: tuple[tuple[object, str], ...] = (
        ("", "BOUND"),
        ("   ", "BOUND"),
        ("a\x00b", "BOUND"),
        ("a" * 513, "BOUND"),
        ("C:/abs.py", "PATH"),
        ("//server/a.py", "PATH"),
        ("/abs.py", "PATH"),
        ("../x.py", "PATH"),
        ("live/a.py", "PATH"),
        ("cosmos/api_token.py", "PATH"),
        ("cosmos/notes.env.py", "PATH"),
    )
    for rel, code in samples:
        try:
            scan_text(cast(str, rel), "Q:\\peer")
        except Refuse as exc:
            assert exc.code == code
        else:
            raise AssertionError(rel)
    try:
        scan_text("cosmos/a.py", cast(str, None))
    except Refuse as exc:
        assert exc.code == "BOUND"
    else:
        raise AssertionError("text")


def test_scan_root_reads_only_the_dayone_surface(scratch: Path) -> None:
    jail = PathJail(scratch)
    _write(jail, "cosmos/a.py", "V:\\A\\Ai\\COSMOS\\live\nV:\\Ai\\BU.MD\nD:\\R2Cloner\\ok\n")
    _write(jail, "README.md", "Z:\\from-readme\n")
    _write(jail, "serve.bat", "KMesh-COSMOS-live\n")
    _write(jail, "kdash/index.html", "<p>W:\\from-html</p>\n")
    _write(jail, "docs/federation/note.md", "//peer/share/room\n")
    _write(jail, "cosmos/nested/b.py", "Q:\\from-nested\n")
    _write(jail, "cosmos/api_token.py", "Q:\\from-token-name\n")
    _write(jail, "cosmos/notes.env.py", "Q:\\from-env-name\n")
    _write(jail, "cosmos/__pycache__/z.py", "Q:\\from-pyc\n")
    _write(jail, "kdash/_delme/old.html", "Q:\\from-delme\n")
    _write(jail, "docs/OTHER.md", "D:\\R2Cloner\\smuggled\n")
    _write(jail, "live/cosmos/x.py", "Q:\\from-live\n")
    _write(jail, "node_modules/pkg/index.html", "Q:\\from-nm\n")
    _write(jail, ".git/config.py", "Q:\\from-git\n")
    _write(jail, "src-tauri/index.html", "Q:\\from-tauri\n")
    hits = scan_root(jail.root)
    assert [hit.rel for hit in hits] == [
        "README.md",
        "cosmos/a.py",
        "cosmos/a.py",
        "cosmos/a.py",
        "docs/federation/note.md",
        "kdash/index.html",
        "serve.bat",
    ]
    assert [hit.kind for hit in hits] == [
        KIND_DRIVE,
        KIND_KEITH_TREE,
        KIND_KEITH_AI,
        KIND_R2_STORE,
        KIND_UNC,
        KIND_DRIVE,
        KIND_TAKEN_ID,
    ]
    blob = "\n".join(hit.excerpt for hit in hits)
    for hidden in ("from-nested", "from-token", "from-env", "from-pyc", "from-delme", "smuggled", "from-live", "from-nm", "from-git", "from-tauri"):
        assert hidden not in blob
    assert scan_root(jail.root) == hits


def test_scan_root_refuses_missing_file_and_live(scratch: Path) -> None:
    jail = PathJail(scratch)
    assert scan_root(jail.root) == ()
    _write(jail, "solo.txt", "x")
    try:
        scan_root(jail.contain("solo.txt"))
    except Refuse as exc:
        assert exc.code == "ROOT"
    else:
        raise AssertionError("file")
    try:
        scan_root(scratch / "missing")
    except Refuse as exc:
        assert exc.code == "ROOT"
    else:
        raise AssertionError("missing")
    try:
        scan_root(cast(Path, "nope"))
    except Refuse as exc:
        assert exc.code == "ROOT"
    else:
        raise AssertionError("type")
    for name in ("live", ".git", "node_modules", "__pycache__", "src-tauri", "_delme"):
        folder = jail.contain(name)
        folder.mkdir(exist_ok=True)
        _write(jail, f"{name}/cosmos/a.py", "Q:\\from-skipped-root\n")
        try:
            scan_root(folder)
        except Refuse as exc:
            assert exc.code == "ROOT"
        else:
            raise AssertionError(name)
