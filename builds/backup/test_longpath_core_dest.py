#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""test_longpath_core_dest - the DESTINATION half of the MAX_PATH fix, on the LIVE
module `cosmos/cosmos_backup.py` (the one `cosmos_backup_clock` drives on schtasks).

The fix landed there this shift. A source-side fix alone is worthless: the walker can
SEE a 300-char file and the copy can still die writing it, because

    dest_root / <stamp> / <240-char relative key>

is LONGER than the source path that was already past the limit. `docs/LONGPATH_FINDING.md`
§7 lists "the DESTINATION needs it too" as a caveat; this suite is the measurement that
it is honored rather than merely written down, at every destination the module has:

    Backup.run            -> os.makedirs(dest/rel) + shutil.copy2 + _sha(dest/rel)
    Backup.run            -> the _MANIFEST.sha256.json write
    rehearse_restore      -> os.makedirs(scratch/rel) + copy2 + re-hash

This suite imports the LIVE module by path with a stub ledger, so it measures the file
Task Scheduler actually executes - not a copy of it in this fence. It writes NOTHING
into the live tree: the ledger is a list in memory and every path is a temp dir.

    py -3.14 builds/backup/test_longpath_core_dest.py
"""
from __future__ import annotations

import hashlib
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_paths import extended as _x   # noqa: E402  the canonical prefix helper


def _load_core():
    r"""The module under test: the LIVE cosmos/cosmos_backup.py by default.

    `--core <path>` loads a DIFFERENT file instead. That flag is not a convenience -
    it is how this suite is proven to be a real gate: extract the pre-fix module
    (`git show HEAD:cosmos/cosmos_backup.py`) and run this same suite against it. A
    regression test nobody has watched FAIL against the old code is an assumption.

    Measured 2026-08-31 against HEAD (pre-fix): 3 failures - files 1 of 3 with
    BACKUP_VERIFIED still appended, the manifest naming 1 key, and the rehearsal
    restoring 1 file. Against the fixed module: 5 tests, OK.
    """
    if "--core" in sys.argv:
        i = sys.argv.index("--core")
        path = Path(sys.argv[i + 1]).resolve()
        del sys.argv[i:i + 2]
        import importlib.util
        spec = importlib.util.spec_from_file_location("core_under_test", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print(f"# module under test: {path}", flush=True)
        return mod
    import cosmos_backup
    return cosmos_backup


core = _load_core()

MAX_PATH_USABLE = 259


class StubLedger:
    """Records appends. The real Ledger is the single writer of the live chain and
    this suite must never touch it - but the events still have to be asserted on,
    because 'BACKUP_VERIFIED over a hole' is the defect being tested for."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def append(self, kind: str, detail: dict) -> None:
        self.events.append((kind, detail))

    def kinds(self) -> list[str]:
        return [k for k, _ in self.events]


def _write(path: Path, payload: bytes) -> None:
    os.makedirs(_x(path.parent), exist_ok=True)
    with open(_x(path), "wb") as fh:
        fh.write(payload)


def _read(path: Path) -> bytes:
    with open(_x(path), "rb") as fh:
        return fh.read()


class TestLiveModuleDestinationSide(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_lpc_"))
        self.src = self.tmp / "src"
        os.makedirs(_x(self.src), exist_ok=True)
        self.payload: dict[str, bytes] = {}

        _write(self.src / "shallow.txt", b"shallow\n")

        a_dir = self.src / ("a" * 40)
        a_name = ("n" * (300 - len(str(a_dir)) - 1 - len(".txt"))) + ".txt"
        self.class_a = a_dir / a_name
        _write(self.class_a, b"class A - long file name, listable directory\n")

        b_dir = self.src
        while len(str(b_dir)) + 41 < 300:
            b_dir = b_dir / ("b" * 40)
        self.class_b = b_dir / "deep.txt"
        _write(self.class_b, b"class B - directory itself past MAX_PATH\n")

        for p in (self.src / "shallow.txt", self.class_a, self.class_b):
            self.payload[str(p)[len(str(self.src)) + 1:].replace("\\", "/")] = _read(p)

        self.ledger = StubLedger()
        self.backup = core.Backup(self.ledger)

    def tearDown(self) -> None:
        shutil.rmtree(_x(self.tmp), ignore_errors=True)

    def test_fixture_is_really_past_max_path(self):
        for p in (self.class_a, self.class_b):
            self.assertGreater(len(str(p)), MAX_PATH_USABLE)
            self.assertTrue(os.path.exists(_x(p)))

    def test_run_writes_every_long_file_to_the_destination_and_rehashes_it(self):
        """The gate: 3 on disk, 3 in the ledger event, and the DEST bytes re-read."""
        target = self.tmp / "dest"
        os.makedirs(_x(target), exist_ok=True)
        out = self.backup.run(self.src, target)

        self.assertEqual(out["files"], 3, "a count of 1 here is the silent-omission bug")
        self.assertEqual(self.ledger.kinds(), ["BACKUP_VERIFIED"])
        kind, detail = self.ledger.events[0]
        self.assertEqual((detail["files"], detail["verified"]), (3, 3))

        dest = Path(out["dest"])
        for rel, data in self.payload.items():
            written = dest / rel
            self.assertEqual(_read(written), data, f"destination bytes differ for {rel}")
            self.assertEqual(hashlib.sha256(_read(written)).hexdigest(),
                             hashlib.sha256(data).hexdigest())
        # The destination really is longer than the source it came from.
        deepest = max((dest / r for r in self.payload), key=lambda p: len(str(p)))
        self.assertGreater(len(str(deepest)), len(str(self.class_a)))
        self.assertGreater(len(str(deepest)), MAX_PATH_USABLE)

    def test_manifest_artifact_lands_and_names_every_long_key(self):
        import json
        target = self.tmp / "dest_m"
        os.makedirs(_x(target), exist_ok=True)
        out = self.backup.run(self.src, target)
        mf = Path(out["dest"]) / "_MANIFEST.sha256.json"
        manifest = json.loads(_read(mf).decode("utf-8"))
        self.assertEqual(len(manifest), 3)
        for rel, data in self.payload.items():
            key = rel.replace("/", os.sep)
            self.assertIn(key, manifest)
            self.assertEqual(manifest[key], hashlib.sha256(data).hexdigest())

    def test_rehearse_restore_into_scratch_past_max_path(self):
        """The second destination: scratch/<240-char key>. Restored bytes re-hashed."""
        target, scratch = self.tmp / "dest_r", self.tmp / "scratch"
        os.makedirs(_x(target), exist_ok=True)
        out = self.backup.run(self.src, target)
        res = self.backup.rehearse_restore(Path(out["dest"]), scratch)

        self.assertEqual(res["files"], 3)
        self.assertIn("RESTORE_REHEARSAL_PASSED", self.ledger.kinds())
        for rel, data in self.payload.items():
            self.assertEqual(_read(scratch / rel.replace("/", os.sep)), data)

    def test_empty_scope_is_a_refusal_not_a_green_run(self):
        """Fail-closed: an empty backup that reports OK is the defect, not a no-op."""
        empty = self.tmp / "empty"
        os.makedirs(_x(empty), exist_ok=True)
        with self.assertRaises(core.BackupError) as cm:
            self.backup.run(empty, self.tmp / "dest_e")
        self.assertEqual(cm.exception.kind, "EMPTY_SCOPE")
        self.assertEqual(self.ledger.kinds(), [], "no ledger event for a refused run")


if __name__ == "__main__":
    unittest.main(verbosity=2)
