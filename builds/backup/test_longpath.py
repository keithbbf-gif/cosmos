#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""test_longpath - the MAX_PATH gap, pinned with a real file past 260 characters.

The defect this suite exists for, measured on the live trees 2026-08-31:

    2,143 files under V:\Ai + V:\A + V:\Research4 have absolute paths longer than
    the 259 characters a plain Win32 call accepts (deepest 412). Before the fix,
    `iter_files` selected FIVE of the 2,129 files under V:\Ai\_session_logs\_mcp_logs
    and RAISED NOTHING - a backup reporting success over a 99.8% hole.

Two distinct failures, and a fix for one is not a fix for the other, so both get a
fixture and both get a test:

    class A  directory lists, file path too long -> `Path.is_file()` swallows
             winerror=3 and returns False; the file is filtered out silently.
    class B  directory path itself too long -> scandir cannot descend and
             `os.walk(onerror=None)` swallows that; the subtree is never seen.

Every file here is created THROUGH the `\\?\` prefix, so the fixture is a real
NTFS object the OS refuses to hand over by its plain name - not a mock of one.

Portable by construction: on POSIX these are simply long paths (legal there), so
the coverage assertions still mean what they say and the suite is not skipped.

    py -3.14 builds/backup/test_longpath.py
"""
from __future__ import annotations

import hashlib
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cosmos_backup as bk  # noqa: E402

MAX_PATH_USABLE = 259


def _write(path: Path, payload: bytes) -> None:
    os.makedirs(bk._x(path.parent), exist_ok=True)
    with open(bk._x(path), "wb") as fh:
        fh.write(payload)


def _read(path: Path) -> bytes:
    with open(bk._x(path), "rb") as fh:
        return fh.read()


class _DeepTree(unittest.TestCase):
    """Builds shallow + class A + class B under a fresh temp root."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_lp_"))
        self.src = self.tmp / "src"
        os.makedirs(bk._x(self.src), exist_ok=True)

        self.payload = {}
        self.shallow = self.src / "shallow.txt"
        _write(self.shallow, b"shallow\n")

        a_dir = self.src / ("a" * 40)
        a_name = ("n" * (300 - len(str(a_dir)) - 1 - len(".txt"))) + ".txt"
        self.class_a = a_dir / a_name
        _write(self.class_a, b"class A - long file name, listable directory\n")

        b_dir = self.src
        while len(str(b_dir)) + 41 < 300:
            b_dir = b_dir / ("b" * 40)
        self.class_b = b_dir / "deep.txt"
        _write(self.class_b, b"class B - directory itself past MAX_PATH\n")

        self.all = (self.shallow, self.class_a, self.class_b)
        for p in self.all:
            self.payload[self._rel(p)] = _read(p)

    def tearDown(self) -> None:
        shutil.rmtree(bk._x(self.tmp), ignore_errors=True)

    def _rel(self, p: Path) -> str:
        return str(p)[len(str(self.src)) + 1:].replace("\\", "/")


class TestFixtureIsReal(_DeepTree):
    """The fixture must actually be past the limit, or every test below is theatre."""

    def test_the_deep_files_really_exceed_max_path(self):
        self.assertGreater(len(str(self.class_a)), MAX_PATH_USABLE)
        self.assertGreater(len(str(self.class_b)), MAX_PATH_USABLE)
        for p in (self.class_a, self.class_b):
            self.assertTrue(os.path.exists(bk._x(p)), f"prefixed access must work: {p}")

    @unittest.skipUnless(os.name == "nt", "MAX_PATH is a Windows limit")
    def test_windows_still_refuses_the_plain_name(self):
        """If this ever passes plainly, LongPathsEnabled was turned on - not the fix."""
        for p in (self.class_a, self.class_b):
            with self.assertRaises(OSError):
                os.stat(str(p))
            # THE defect, in one assertion: is_file() converts that error into a
            # False, and a walker filtering on it drops the file without a word.
            self.assertFalse(Path(p).is_file())


class TestWalkerCoversLongPaths(_DeepTree):

    def test_iter_files_yields_every_file_including_both_long_classes(self):
        got = set(bk.iter_files(self.src, frozenset()))
        self.assertEqual(got, set(self.payload), "iter_files must not lose a long path")

    def test_build_manifest_hashes_the_long_files_correctly(self):
        m = bk.build_manifest(self.src, excludes=())
        self.assertEqual(m["file_count"], 3)
        for rel, data in self.payload.items():
            self.assertIn(rel, m["files"])
            self.assertEqual(m["files"][rel]["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(m["files"][rel]["size"], len(data))

    def test_backup_verify_rehearse_roundtrip_past_max_path(self):
        """The destination side too: set_dir + a 240-char rel is longer still."""
        dest, scratch = self.tmp / "dest", self.tmp / "scratch"
        os.makedirs(bk._x(dest), exist_ok=True)
        set_dir = bk.do_backup(self.src, dest, excludes=())
        m = bk.do_verify(set_dir)
        self.assertEqual(m["file_count"], 3)
        bk.do_rehearse(set_dir, scratch)
        for rel, data in self.payload.items():
            self.assertEqual(_read(scratch / rel), data,
                             f"restored bytes differ for {rel}")

    def test_restore_puts_a_long_path_file_back(self):
        """Delete the deep file, restore, and re-read its bytes - the round trip."""
        dest = self.tmp / "dest2"
        os.makedirs(bk._x(dest), exist_ok=True)
        set_dir = bk.do_backup(self.src, dest, excludes=())
        os.remove(bk._x(self.class_b))
        self.assertFalse(os.path.exists(bk._x(self.class_b)))
        bk.do_restore(set_dir, self.src, stage_dir=self.tmp / "stage")
        self.assertEqual(_read(self.class_b), self.payload[self._rel(self.class_b)])


class TestRefusesRatherThanSkipping(_DeepTree):
    """The other half of the fix: a hole must be LOUD, never absent."""

    def test_unenumerable_directory_refuses(self):
        """os.walk's default onerror=None ate scandir failures. It must not."""
        real_walk = bk.os.walk

        def blind(top, *a, onerror=None, **k):
            if onerror is not None:
                onerror(PermissionError(13, "denied", str(top)))
            return iter(())

        bk.os.walk = blind
        try:
            with self.assertRaises(bk.BackupRefusal) as cm:
                list(bk.iter_files(self.src, frozenset()))
            self.assertEqual(cm.exception.kind, "SOURCE_UNREADABLE")
        finally:
            bk.os.walk = real_walk

    def test_unstattable_entry_refuses_instead_of_being_filtered_out(self):
        """_lstat_mode must never return a guess that fails the is-regular test."""
        real_lstat = bk.os.lstat
        target = os.path.basename(str(self.shallow))

        def flaky(p, *a, **k):
            if str(p).endswith(target):
                raise PermissionError(13, "denied", str(p))
            return real_lstat(p, *a, **k)

        bk.os.lstat = flaky
        try:
            with self.assertRaises(bk.BackupRefusal) as cm:
                list(bk.iter_files(self.src, frozenset()))
            self.assertEqual(cm.exception.kind, "SOURCE_UNREADABLE")
        finally:
            bk.os.lstat = real_lstat


class TestPrefixHelper(unittest.TestCase):

    @unittest.skipUnless(os.name == "nt", "prefix is a Windows construct")
    def test_shapes(self):
        self.assertTrue(bk._x(r"V:\Ai\x").startswith("\\\\?\\"))
        # never double-prefixes
        once = bk._x(r"V:\Ai\x")
        self.assertEqual(bk._x(once), once)
        # UNC takes the \\?\UNC\ shape, not \\?\\\server
        self.assertEqual(bk._x(r"\\srv\share\f"), r"\\?\UNC\srv\share\f")
        # `\\?\` disables normalization, so the path must be absolute and clean
        # BEFORE it is prefixed - abspath is what guarantees that.
        self.assertNotIn("/", bk._x("rel/ative"))
        self.assertNotIn("\\..\\", bk._x(r"V:\Ai\sub\..\x"))

    @unittest.skipIf(os.name == "nt", "POSIX identity")
    def test_identity_on_posix(self):
        self.assertEqual(bk._x("/tmp/x"), "/tmp/x")


if __name__ == "__main__":
    unittest.main(verbosity=2)
