#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""test_longpath_r2 - the MAX_PATH fix, checked on the DESTINATION side of a PUSH.

`test_longpath.py` proves the walker and the LOCAL backup set handle paths past
MAX_PATH. That is only half of an offsite push. A push has TWO more filesystem
touchpoints on the far side of the manifest, and neither is the walker:

    R2Target.store(rel, src)      READS the source file by its plain name
    R2Target.retrieve(rel, dst)   WRITES the read-back copy into the scratch dir

The read-back scratch is the destination the push's own proof depends on: push()
retrieves EVERY object back and re-hashes it. `scratch_root + a 240-char relative
key` is longer than the source path that was already past the limit, so the
destination needs the `\\?\` prefix even when the source root is short.

MEASURED BEFORE THE FIX (2026-08-31, this fixture):

    FileNotFoundError: [Errno 2] No such file or directory:
      'C:\\...\\cosmos_lpr_...\\src\\aaaa...\\nnnn....txt'

raised out of `Path(src).read_bytes()` in R2Target.store - an UNTYPED crash, not a
BackupRefusal, from a module whose whole contract is typed refusals. build_manifest
had already hashed the file successfully through the prefix, so the manifest and the
uploader disagreed about which files exist. Any push of V:\Ai (2,125 long paths)
would have died there.

Portable by construction: on POSIX these are simply long paths (legal there), so the
assertions still mean what they say and nothing is skipped.

    py -3.14 builds/backup/test_longpath_r2.py
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

import cosmos_backup as bk        # noqa: E402
import cosmos_backup_r2 as r2     # noqa: E402

MAX_PATH_USABLE = 259
FAKE = "TEST-NOT-A-CREDENTIAL"


def _write(path: Path, payload: bytes) -> None:
    os.makedirs(bk._x(path.parent), exist_ok=True)
    with open(bk._x(path), "wb") as fh:
        fh.write(payload)


def _read(path: Path) -> bytes:
    with open(bk._x(path), "rb") as fh:
        return fh.read()


def _creds() -> r2.R2Credentials:
    """Obviously-fake, never a real key: this suite must never need a credential."""
    return r2.R2Credentials("testaccount", FAKE, FAKE, "test-bucket")


class _DeepTree(unittest.TestCase):
    """shallow + class A (long file path) + class B (long DIRECTORY path)."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_lpr_"))
        self.src = self.tmp / "src"
        os.makedirs(bk._x(self.src), exist_ok=True)

        self.payload: dict[str, bytes] = {}
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

        for p in (self.shallow, self.class_a, self.class_b):
            self.payload[self._rel(p)] = _read(p)

    def tearDown(self) -> None:
        shutil.rmtree(bk._x(self.tmp), ignore_errors=True)

    def _rel(self, p: Path) -> str:
        return str(p)[len(str(self.src)) + 1:].replace("\\", "/")


class TestFixtureIsReal(_DeepTree):
    """If the fixture is not actually past the limit every test below is theatre."""

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


class TestPushSourceSidePastMaxPath(_DeepTree):
    """store() reads the source by name. Before the fix that read crashed untyped."""

    def test_store_reads_a_long_source_file(self):
        tp = r2.MemoryTransport()
        target = r2.R2Target(_creds(), "p", tp)
        rel = self._rel(self.class_a)
        target.store(rel, self.src / rel)
        self.assertEqual(tp.objects[f"test-bucket/p/{rel}"], self.payload[rel])


class TestPushDestinationSidePastMaxPath(_DeepTree):
    """retrieve() writes the read-back copy. THIS is the destination side."""

    def test_retrieve_writes_past_max_path(self):
        tp = r2.MemoryTransport()
        target = r2.R2Target(_creds(), "p", tp)
        rel = self._rel(self.class_b)
        target.store(rel, self.src / rel)
        # A SHORT scratch root plus a long key is still a long destination - which
        # is exactly why the destination needs the prefix independently of the source.
        dst = self.tmp / "scratch_dest" / rel
        target.retrieve(rel, dst)
        self.assertGreater(len(str(dst)), MAX_PATH_USABLE)
        self.assertEqual(_read(dst), self.payload[rel])

    def test_full_push_readback_covers_every_long_path(self):
        """The whole gate: manifest -> PUT -> GET -> re-hash, past MAX_PATH.

        push() re-hashes every object it read back, so a receipt with
        readback_verified == 3 is the artifact - not the exit code.
        """
        tp = r2.MemoryTransport()
        receipt = r2.push(self.src, r2.R2Target(_creds(), "p", tp), excludes=(),
                          scratch=self.tmp / "readback")
        self.assertEqual(receipt["files_pushed"], 3)
        self.assertEqual(receipt["readback_verified"], 3)
        for rel, data in self.payload.items():
            self.assertEqual(tp.objects[f"test-bucket/p/{rel}"], data)
            self.assertEqual(_read(self.tmp / "readback" / rel), data)
        self.assertEqual(
            receipt["bytes_pushed"], sum(len(v) for v in self.payload.values()))

    def test_receipt_hash_equals_the_manifest_hash_for_a_long_path(self):
        """One hash, two jobs: the manifest digest IS the x-amz-content-sha256."""
        m = bk.build_manifest(self.src, excludes=())
        rel = self._rel(self.class_a)
        self.assertEqual(m["files"][rel]["sha256"],
                         hashlib.sha256(self.payload[rel]).hexdigest())


class TestScratchGuardsUsePrefixedChecks(_DeepTree):
    """The emptiness guard must SEE a long-path file, or it guards nothing."""

    def test_non_empty_scratch_is_refused_even_when_only_a_long_file_is_in_it(self):
        scratch = self.tmp / "occupied"
        deep = scratch
        while len(str(deep)) + 41 < 300:
            deep = deep / ("c" * 40)
        _write(deep / "leftover.txt", b"a prior run left this here\n")
        self.assertGreater(len(str(deep / "leftover.txt")), MAX_PATH_USABLE)
        with self.assertRaises(bk.BackupRefusal) as cm:
            r2.push(self.src, r2.R2Target(_creds(), "p", r2.MemoryTransport()),
                    excludes=(), scratch=scratch)
        self.assertEqual(cm.exception.kind, "SCRATCH_NOT_EMPTY")


if __name__ == "__main__":
    unittest.main(verbosity=2)
