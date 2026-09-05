#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin whole-tree local-backup scope: locks out, unreadables in still refuse.

This file lives under tests/ (assignment fence). It imports the clock from
builds/backup/ — never cosmos/cosmos_backup.py (same module name, different
tree). No key material is read, printed, or copied.

    py -3.14 tests/test_backup_local_excludes.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "builds" / "backup"))

import cosmos_backup as cb  # noqa: E402  — builds/backup, not cosmos/
import cosmos_backup_mounts as mounts  # noqa: E402
import cosmos_local_clock as lc  # noqa: E402

CosmosPaths = lc.CosmosPaths


@contextmanager
def _hold_exclusive(path: Path):
    path = Path(path)
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        generic = 0x80000000 | 0x40000000
        handle = ctypes.windll.kernel32.CreateFileW(
            str(path), generic, 0, None, 3, 0x80, None)
        invalid = wintypes.HANDLE(-1).value
        if handle in (None, 0, -1, invalid):
            raise OSError(f"CreateFileW exclusive failed for {path}")
        try:
            yield handle
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    else:
        prev = path.stat().st_mode
        os.chmod(path, 0)
        try:
            yield prev
        finally:
            os.chmod(path, prev)


class TestBackupLocalExcludes(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_lex_"))
        self.root = self.tmp / "live"
        self.root.mkdir(parents=True)
        (self.root / ".cosmos-root.json").write_text(
            json.dumps({"system": "COSMOS", "tree_id": "KMesh-COSMOS-test",
                        "schema_version": 1}), encoding="utf-8")
        for role in ("logs", "config", "work", "state"):
            (self.root / role).mkdir(parents=True, exist_ok=True)
        self.paths = CosmosPaths(self.root)
        self.src = self.tmp / "src"
        self.src.mkdir()
        (self.src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        self.dest = self.tmp / "dest"
        self.dest.mkdir()
        self.cfg = self.paths.config(lc.CONFIG_NAME)
        self.probe = mounts.FakeProbe(volumes={
            str(self.src): "vol:SRC",
            str(self.src.resolve()): "vol:SRC",
            str(self.dest): "vol:DST",
            str(self.dest.resolve()): "vol:DST",
        })
        self.cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {
                "dest": str(self.dest), "source": str(self.src),
            }},
        }), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _sets(self):
        return [p for p in self.dest.iterdir()
                if p.is_dir() and p.name != "_rehearse"]

    def test_lock_file_does_not_block_verified(self):
        lock = self.src / "live" / "logs" / "cdeck_feed.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text("pid\n", encoding="utf-8", newline="\n")
        (self.src / "live" / "ledger").mkdir(parents=True)
        (self.src / "live" / "ledger" / "authority.jsonl").write_text(
            '{"n":1}\n', encoding="utf-8", newline="\n")
        with _hold_exclusive(lock):
            rec = lc.tick(self.paths, self.cfg, probe=self.probe, force=True)
        self.assertEqual(rec["state"], "VERIFIED", rec)
        self.assertGreater(rec.get("files") or 0, 0)
        manifest = json.loads((self._sets()[0] / cb.MANIFEST_NAME).read_text(
            encoding="utf-8"))
        self.assertNotIn("live/logs/cdeck_feed.lock", manifest["files"])
        self.assertIn("live/ledger/authority.jsonl", manifest["files"])

    def test_unreadable_in_scope_data_still_refuses(self):
        lock = self.src / "live" / "logs" / "cdeck_feed.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text("pid\n", encoding="utf-8", newline="\n")
        data = self.src / "zzz" / "data.txt"
        data.parent.mkdir(parents=True)
        data.write_text("canon\n", encoding="utf-8", newline="\n")
        with _hold_exclusive(lock), _hold_exclusive(data):
            rec = lc.tick(self.paths, self.cfg, probe=self.probe, force=True)
        self.assertEqual(rec["state"], "REFUSED", rec)
        self.assertEqual(rec["kind"], "SOURCE_UNREADABLE", rec)
        detail = rec.get("detail") or ""
        self.assertIn("zzz/data.txt", detail.replace("\\", "/"), rec)
        self.assertNotIn("cdeck_feed.lock", detail, rec)
        self.assertEqual(self._sets(), [])


if __name__ == "__main__":
    tests = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    print("%d/%d" % (result.testsRun - len(result.failures) - len(result.errors),
                     result.testsRun))
    raise SystemExit(0 if result.wasSuccessful() else 1)
