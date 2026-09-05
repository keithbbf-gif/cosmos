#!/usr/bin/env python3
"""Real tests for cosmos_backup.py — run with: python3 test_cosmos_backup.py -v

Bounded on purpose: a small synthetic tree, plus (when COSMOS_TEST_DOCS points
at a real directory, e.g. the mounted COSMOS docs/) a subset of at most five
real files. Never scans the whole tree; never touches .git.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import cosmos_backup as cb

KEY = b"test-hmac-key-not-a-real-secret"


class BackupTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_backup_test_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)  # test scratch only — never tree files
        self.src = self.tmp / "src"
        (self.src / "nested" / "deep").mkdir(parents=True)
        # The explicit newline is load-bearing on Windows: write_text
        # translates LF to CRLF by default, so the file on disk held CRLF
        # while this test asserted the sha256 of the LF form. The backup
        # module was right -- it hashes real bytes; the fixture was
        # platform-naive, and nothing ran it to notice. (2026-08-30)
        (self.src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        (self.src / "nested" / "b.bin").write_bytes(bytes(range(256)) * 100)
        (self.src / "nested" / "deep" / "c.md").write_text("# gamma\n", encoding="utf-8", newline="\n")
        (self.src / "empty.dat").write_bytes(b"")
        (self.src / ".git").mkdir()
        (self.src / ".git" / "excluded.txt").write_text("must not appear", encoding="utf-8", newline="\n")
        self.dest = self.tmp / "dest"


class TestManifest(BackupTestBase):
    def test_manifest_contents_and_exclusion(self):
        m = cb.build_manifest(self.src)
        self.assertEqual(sorted(m["files"]),
                         ["a.txt", "empty.dat", "nested/b.bin", "nested/deep/c.md"])
        self.assertEqual(m["file_count"], 4)
        self.assertNotIn(".git/excluded.txt", m["files"])
        self.assertEqual(m["files"]["a.txt"]["sha256"],
                         cb.hashlib.sha256(b"alpha\n").hexdigest())

    def test_empty_source_refuses(self):
        empty = self.tmp / "empty_src"
        empty.mkdir()
        with self.assertRaises(cb.BackupRefusal):
            cb.build_manifest(empty)


class TestBackupVerifyRehearse(BackupTestBase):
    def test_full_cycle_proves_restorable(self):
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        # manifest artifact exists and its seal verifies
        manifest = json.loads((set_dir / cb.MANIFEST_NAME).read_text(encoding="utf-8"))
        cb.check_seal(manifest, KEY)  # raises on tamper
        # verify passes
        cb.do_verify(set_dir, KEY)
        # rehearse-restore to scratch, re-hash, sealed proof artifact emitted
        scratch = self.tmp / "scratch"
        proof_path = cb.do_rehearse(set_dir, scratch, KEY)
        self.assertTrue(proof_path.is_file())
        proof = json.loads(proof_path.read_text(encoding="utf-8"))
        cb.check_seal(proof, KEY)
        self.assertEqual(proof["kind"], "REHEARSAL_PASS")
        self.assertEqual(proof["files_restored"], 4)
        self.assertEqual(proof["manifest_seal_sha256"], manifest["seal"]["sha256"])
        # restored bytes really match the originals
        for rel in manifest["files"]:
            self.assertEqual(cb.sha256_file(scratch / Path(*rel.split("/"))),
                             cb.sha256_file(self.src / Path(*rel.split("/"))), rel)

    def test_run_once_heartbeats_ok(self):
        cb.run_once([self.src], self.dest, cb.DEFAULT_EXCLUDES, KEY)
        hb = json.loads((self.dest / cb.HEARTBEAT_NAME).read_text(encoding="utf-8"))
        self.assertEqual(hb["status"], "OK")
        self.assertEqual(len(hb["detail"]["completed"]), 1)


class TestFailClosed(BackupTestBase):
    def test_corrupt_byte_refuses_with_incident(self):
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        victim = set_dir / cb.DATA_DIR / "nested" / "b.bin"
        blob = bytearray(victim.read_bytes())
        blob[100] ^= 0xFF  # flip ONE byte
        victim.write_bytes(blob)
        with self.assertRaises(cb.BackupRefusal):
            cb.do_verify(set_dir, KEY)
        incidents = list(set_dir.glob("INCIDENT-*.json"))
        self.assertEqual(len(incidents), 1)
        inc = json.loads(incidents[0].read_text(encoding="utf-8"))
        cb.check_seal(inc, KEY)
        self.assertEqual(inc["kind"], "VERIFY_HASH_MISMATCH")
        self.assertIn("nested/b.bin", inc["detail"]["mismatches"])
        # rehearse also refuses (verify gates it) and restores nothing
        with self.assertRaises(cb.BackupRefusal):
            cb.do_rehearse(set_dir, self.tmp / "scratch2", KEY)
        self.assertFalse((set_dir / cb.REHEARSAL_NAME).exists())

    def test_missing_file_refuses(self):
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        # simulate loss inside the backup set copy (test scratch, not the tree)
        os.replace(set_dir / cb.DATA_DIR / "a.txt", set_dir / cb.DATA_DIR / "a.txt.lost")
        with self.assertRaises(cb.BackupRefusal):
            cb.do_verify(set_dir, KEY)

    def test_tampered_manifest_seal_refuses(self):
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        mpath = set_dir / cb.MANIFEST_NAME
        m = json.loads(mpath.read_text(encoding="utf-8"))
        m["files"]["a.txt"]["sha256"] = "0" * 64  # forge the expected hash
        mpath.write_text(json.dumps(m), encoding="utf-8")
        with self.assertRaises(cb.BackupRefusal):
            cb.do_verify(set_dir, KEY)

    def test_nonempty_scratch_refuses(self):
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        scratch = self.tmp / "occupied"
        scratch.mkdir()
        (scratch / "precious.txt").write_text("do not clobber", encoding="utf-8")
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_rehearse(set_dir, scratch, KEY)
        self.assertEqual(ctx.exception.kind, "SCRATCH_NOT_EMPTY")
        self.assertTrue(str(ctx.exception).startswith("REFUSE[SCRATCH_NOT_EMPTY]"))
        self.assertEqual((scratch / "precious.txt").read_text(encoding="utf-8"),
                         "do not clobber")
        self.assertFalse((set_dir / cb.REHEARSAL_NAME).exists(),
                         "occupied scratch must not seal REHEARSAL.json")

    def test_existing_set_dir_never_overwritten(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.LocalDirTarget(self.tmp, create=True)  # exists already
        self.assertEqual(ctx.exception.kind, "SET_EXISTS")


class TestRestoreRoundTrip(BackupTestBase):
    """The round trip a backup exists for: corrupt the SOURCE, restore, re-hash."""

    def test_corrupted_source_file_is_restored_byte_for_byte(self):
        victim = self.src / "nested" / "b.bin"
        before = cb.sha256_file(victim)
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)

        blob = bytearray(victim.read_bytes())
        blob[4242] ^= 0xFF                      # corrupt the LIVE source file
        victim.write_bytes(blob)
        corrupted = cb.sha256_file(victim)
        self.assertNotEqual(before, corrupted)

        stage = self.tmp / "displaced"
        receipt = cb.do_restore(set_dir, self.src, KEY, stage)
        cb.check_seal(receipt, KEY)
        self.assertEqual(receipt["kind"], "RESTORE_OK")
        self.assertEqual(receipt["files_restored"], 4)
        self.assertEqual(cb.sha256_file(victim), before)          # the proof
        # every file matches the manifest again, not just the victim
        manifest = json.loads((set_dir / cb.MANIFEST_NAME).read_text(encoding="utf-8"))
        for rel, entry in manifest["files"].items():
            self.assertEqual(cb.sha256_file(self.src / Path(*rel.split("/"))),
                             entry["sha256"], rel)
        # the displaced (corrupt) copy was STAGED, never deleted
        self.assertEqual(cb.sha256_file(stage / "nested" / "b.bin"), corrupted)
        self.assertEqual(sorted(receipt["displaced"]),
                         ["a.txt", "empty.dat", "nested/b.bin", "nested/deep/c.md"])

    def test_restore_brings_back_a_lost_file_without_staging(self):
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        gone = self.src / "nested" / "deep" / "c.md"
        want = cb.sha256_file(gone)
        os.replace(gone, self.tmp / "moved_away.md")   # simulate loss (test scratch)
        self.assertFalse(gone.exists())
        fresh = self.tmp / "restored_tree"
        receipt = cb.do_restore(set_dir, fresh, KEY)   # empty dest needs no stage dir
        self.assertEqual(receipt["displaced"], [])
        self.assertEqual(cb.sha256_file(fresh / "nested" / "deep" / "c.md"), want)

    def test_restore_over_existing_without_stage_refuses(self):
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_restore(set_dir, self.src, KEY)      # occupied, no stage dir
        self.assertEqual(ctx.exception.kind, "RESTORE_DEST_OCCUPIED")

    def test_restore_refuses_from_an_unverified_set(self):
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        victim = set_dir / cb.DATA_DIR / "a.txt"
        victim.write_bytes(b"rot\n")                   # corrupt the BACKUP copy
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_restore(set_dir, self.tmp / "nowhere", KEY, self.tmp / "stage2")
        self.assertEqual(ctx.exception.kind, "VERIFY_HASH_MISMATCH")
        self.assertFalse((self.tmp / "nowhere").exists())  # nothing written


class TestRestoreFailClosed(BackupTestBase):
    """STAGE_OCCUPIED, RESTORE_HASH_MISMATCH, REHEARSAL_HASH_MISMATCH,
    SOURCE_NOT_DIR, NOT_A_BACKUP_SET sit in BackupRefusal.kind and in the
    do_restore / build_manifest docstrings. No test named them — a suite that
    only restores onto an empty stage with a clean retrieve stays green if
    those branches are deleted. Bite: `_bite_stage_restore.json`."""

    BITE = Path(__file__).resolve().parent / "_bite_stage_restore.json"

    def test_bite_artifact_records_pre_fix(self):
        self.assertTrue(self.BITE.is_file(), "bite must be recorded before belief")
        rec = json.loads(self.BITE.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertEqual(rec["stage_occupied_old_kind"], "RESTORE_OK")
        self.assertTrue(rec["stage_occupied_old_clobbered"])
        self.assertTrue(rec["stage_occupied_old_dest_restored"])
        self.assertTrue(rec["restore_hash_old_restore_ok"])
        self.assertTrue(rec["rehearse_hash_old_pass_sealed"])
        self.assertEqual(rec["source_not_dir_old_kind"], "SOURCE_UNREADABLE")
        self.assertEqual(rec["not_a_backup_set_old_crash"], "FileNotFoundError")

    def test_occupied_stage_slot_refuses_STAGE_OCCUPIED(self):
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        live = self.tmp / "live_occ"
        live.mkdir()
        (live / "a.txt").write_text("LIVE\n", encoding="utf-8", newline="\n")
        stage = self.tmp / "stage_occ"
        stage.mkdir()
        (stage / "a.txt").write_text("PRECIOUS\n", encoding="utf-8", newline="\n")
        precious = cb.hashlib.sha256(b"PRECIOUS\n").hexdigest()
        live_hash = cb.hashlib.sha256(b"LIVE\n").hexdigest()
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_restore(set_dir, live, KEY, stage)
        self.assertEqual(ctx.exception.kind, "STAGE_OCCUPIED")
        # dest and occupied stage slot both UNTOUCHED — never overwritten in place
        self.assertEqual(cb.sha256_file(stage / "a.txt"), precious)
        self.assertEqual(cb.sha256_file(live / "a.txt"), live_hash)
        self.assertEqual((live / "a.txt").read_text(encoding="utf-8"), "LIVE\n")

    def test_flipped_retrieve_refuses_RESTORE_HASH_MISMATCH(self):
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        live = self.tmp / "live_flip"
        live.mkdir()
        (live / "a.txt").write_text("LIVE\n", encoding="utf-8", newline="\n")
        stage = self.tmp / "stage_flip"
        orig = cb.LocalDirTarget.retrieve

        def flip(self, rel, dst):
            orig(self, rel, dst)
            p = Path(dst)
            blob = bytearray(p.read_bytes())
            if blob:
                blob[0] ^= 0xFF
                p.write_bytes(bytes(blob))

        cb.LocalDirTarget.retrieve = flip
        try:
            with self.assertRaises(cb.BackupRefusal) as ctx:
                cb.do_restore(set_dir, live, KEY, stage)
            self.assertEqual(ctx.exception.kind, "RESTORE_HASH_MISMATCH")
        finally:
            cb.LocalDirTarget.retrieve = orig
        incidents = list(set_dir.glob("INCIDENT-*.json"))
        self.assertTrue(incidents, "restore re-hash must emit an INCIDENT, not only raise")
        inc = json.loads(incidents[0].read_text(encoding="utf-8"))
        self.assertEqual(inc["kind"], "RESTORE_HASH_MISMATCH")

    def test_flipped_retrieve_refuses_REHEARSAL_HASH_MISMATCH(self):
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        scratch = self.tmp / "scratch_flip"
        orig = cb.LocalDirTarget.retrieve

        def flip(self, rel, dst):
            orig(self, rel, dst)
            p = Path(dst)
            blob = bytearray(p.read_bytes())
            if blob:
                blob[0] ^= 0xFF
                p.write_bytes(bytes(blob))

        cb.LocalDirTarget.retrieve = flip
        try:
            with self.assertRaises(cb.BackupRefusal) as ctx:
                cb.do_rehearse(set_dir, scratch, KEY)
            self.assertEqual(ctx.exception.kind, "REHEARSAL_HASH_MISMATCH")
        finally:
            cb.LocalDirTarget.retrieve = orig
        self.assertFalse((set_dir / cb.REHEARSAL_NAME).exists(),
                         "a failed rehearsal must not seal REHEARSAL.json")
        incidents = list(set_dir.glob("INCIDENT-*.json"))
        self.assertTrue(incidents, "rehearse re-hash must emit an INCIDENT")
        inc = json.loads(incidents[0].read_text(encoding="utf-8"))
        self.assertEqual(inc["kind"], "REHEARSAL_HASH_MISMATCH")

    def test_file_as_source_is_SOURCE_NOT_DIR(self):
        notdir = self.tmp / "not_a_dir.txt"
        notdir.write_text("I am a file\n", encoding="utf-8", newline="\n")
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.build_manifest(notdir)
        self.assertEqual(ctx.exception.kind, "SOURCE_NOT_DIR")
        self.assertTrue(str(ctx.exception).startswith("REFUSE[SOURCE_NOT_DIR]"))

    def test_empty_folder_is_NOT_A_BACKUP_SET(self):
        empty = self.tmp / "emptyset"
        empty.mkdir()
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.LocalDirTarget(empty)
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")


class TestManifestKeyContainment(BackupTestBase):
    """Unkeyed seals are forgeable, so the containment check must live at the writer."""

    def _forge_key(self, set_dir, bad_rel):
        mpath = set_dir / cb.MANIFEST_NAME
        m = json.loads(mpath.read_text(encoding="utf-8"))
        m["files"][bad_rel] = {"sha256": "0" * 64, "size": 0, "mtime": 0}
        mpath.write_text(json.dumps(cb.seal(m)), encoding="utf-8")  # re-sealed, no HMAC

    def test_traversing_key_refused_on_verify(self):
        set_dir = cb.do_backup(self.src, self.dest)     # unkeyed: bare sha256 seal
        self._forge_key(set_dir, "../../escape.txt")
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_verify(set_dir)
        self.assertEqual(ctx.exception.kind, "UNSAFE_MANIFEST_KEY")
        self.assertFalse((self.dest.parent / "escape.txt").exists())

    def test_absolute_key_refused_on_rehearse(self):
        set_dir = cb.do_backup(self.src, self.dest)
        self._forge_key(set_dir, "C:/Windows/Temp/pwned.txt")
        scratch = self.tmp / "scratch_traverse"
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_rehearse(set_dir, scratch)
        self.assertEqual(ctx.exception.kind, "UNSAFE_MANIFEST_KEY")
        self.assertFalse(any(scratch.rglob("*")) if scratch.exists() else False)


class TestCycleObservability(BackupTestBase):
    def test_untyped_crash_leaves_a_crashed_heartbeat(self):
        boom = lambda *a, **k: (_ for _ in ()).throw(ValueError("disk fell over"))
        orig, cb.do_rehearse = cb.do_rehearse, boom
        try:
            with self.assertRaises(ValueError):
                cb.run_once([self.src], self.dest, cb.DEFAULT_EXCLUDES, KEY)
        finally:
            cb.do_rehearse = orig
        hb = json.loads((self.dest / cb.HEARTBEAT_NAME).read_text(encoding="utf-8"))
        self.assertEqual(hb["status"], "CRASHED")
        self.assertIn("ValueError", hb["detail"]["error"])
        incidents = [json.loads(p.read_text(encoding="utf-8"))
                     for p in self.dest.glob("INCIDENT-*.json")]
        self.assertEqual([i["kind"] for i in incidents], ["CYCLE_CRASHED"])

    def test_refusal_carries_machine_readable_kind(self):
        empty = self.tmp / "empty_src2"
        empty.mkdir()
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.build_manifest(empty)
        self.assertEqual(ctx.exception.kind, "SOURCE_EMPTY")
        self.assertTrue(str(ctx.exception).startswith("REFUSE[SOURCE_EMPTY]"))


class TestKeyedSealHmac(unittest.TestCase):
    """HMAC is what makes a seal 'ours'. Asserted in check_seal + BackupRefusal.kind,
    never asked by a test — a suite that only check_seal()s a matching key stays
    green if the HMAC branch is deleted. Bite: `_bite_hmac_copyhash.json`."""

    KEY = b"test-hmac-key-not-a-real-secret"
    BITE = Path(__file__).resolve().parent / "_bite_hmac_copyhash.json"

    def test_bite_artifact_records_pre_fix(self):
        self.assertTrue(self.BITE.is_file(), "bite must be recorded before belief")
        rec = json.loads(self.BITE.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertTrue(rec["hmac_forged_old_passed"])
        self.assertIsNone(rec["hmac_forged_old_kind"])
        self.assertEqual(rec["hmac_null_pre_fix_crash"], "TypeError")
        self.assertIsNone(rec["hmac_null_pre_fix_kind"])

    def test_matching_key_verifies(self):
        sealed = cb.seal({"n": 1}, self.KEY)
        cb.check_seal(sealed, self.KEY)  # raises on mismatch
        self.assertIn("hmac_sha256", sealed["seal"])

    def test_forged_hmac_with_valid_sha256_refuses_SEAL_HMAC_MISMATCH(self):
        sealed = cb.seal({"n": 1}, self.KEY)
        forged = dict(sealed)
        forged["seal"] = dict(sealed["seal"])
        forged["seal"]["hmac_sha256"] = "0" * 64
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.check_seal(forged, self.KEY)
        self.assertEqual(ctx.exception.kind, "SEAL_HMAC_MISMATCH")

    def test_missing_hmac_with_key_is_SEAL_HMAC_MISMATCH(self):
        sealed = cb.seal({"n": 1}, self.KEY)
        missing = dict(sealed)
        missing["seal"] = {"algo": "sha256", "sha256": sealed["seal"]["sha256"]}
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.check_seal(missing, self.KEY)
        self.assertEqual(ctx.exception.kind, "SEAL_HMAC_MISMATCH")

    def test_null_hmac_is_typed_refusal_not_a_crash(self):
        """Prose: REFUSE. Incumbent: TypeError from compare_digest(str, None)."""
        sealed = cb.seal({"n": 1}, self.KEY)
        nul = dict(sealed)
        nul["seal"] = dict(sealed["seal"])
        nul["seal"]["hmac_sha256"] = None
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.check_seal(nul, self.KEY)
        self.assertEqual(ctx.exception.kind, "SEAL_HMAC_MISMATCH")

    def test_wrong_key_is_SEAL_HMAC_MISMATCH(self):
        sealed = cb.seal({"n": 1}, self.KEY)
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.check_seal(sealed, b"some-other-key")
        self.assertEqual(ctx.exception.kind, "SEAL_HMAC_MISMATCH")

    def test_body_tamper_is_SEAL_MISMATCH_even_when_keyed(self):
        sealed = cb.seal({"n": 1}, self.KEY)
        sealed["n"] = 2
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.check_seal(sealed, self.KEY)
        self.assertEqual(ctx.exception.kind, "SEAL_MISMATCH")

    def test_unkeyed_check_still_accepts_a_keyed_seal(self):
        """key=None is sha256-only by design; HMAC is the optional 'ours' half."""
        sealed = cb.seal({"n": 1}, self.KEY)
        cb.check_seal(sealed)  # no key → no HMAC demand

    def test_no_seal_is_NO_SEAL(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.check_seal({"n": 1})
        self.assertEqual(ctx.exception.kind, "NO_SEAL")

    def test_artifact_array_is_NO_SEAL_not_AttributeError(self):
        """A JSON array is not a sealed object. Predecessor: AttributeError."""
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.check_seal([])
        self.assertEqual(ctx.exception.kind, "NO_SEAL")

    def test_seal_string_is_NO_SEAL_not_AttributeError(self):
        sealed = cb.seal({"n": 1}, self.KEY)
        sealed["seal"] = "not-an-object"
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.check_seal(sealed, self.KEY)
        self.assertEqual(ctx.exception.kind, "NO_SEAL")


class TestVerifyOnWrite(BackupTestBase):
    """Copy then RE-HASH the copies. COPY_HASH_MISMATCH is in the kind set and
    was a live refusal (CHANGELOG, cvm_dt_bench.py mid-copy). No test asked."""

    BITE = Path(__file__).resolve().parent / "_bite_hmac_copyhash.json"

    def test_bite_artifact_records_unhashed_copy_succeeding(self):
        rec = json.loads(self.BITE.read_text(encoding="utf-8"))
        self.assertTrue(rec["copy_hash_old_succeeded"], rec)
        self.assertTrue(rec["copy_hash_old_manifest_sealed"])
        self.assertIsNone(rec["copy_hash_old_kind"])

    def test_corrupt_copy_refuses_COPY_HASH_MISMATCH(self):
        orig = cb.LocalDirTarget.store

        def flip(self, rel, src):
            orig(self, rel, src)
            p = self.data_path(rel)
            blob = bytearray(p.read_bytes())
            if blob:
                blob[0] ^= 0xFF
                p.write_bytes(bytes(blob))

        cb.LocalDirTarget.store = flip
        try:
            with self.assertRaises(cb.BackupRefusal) as ctx:
                cb.do_backup(self.src, self.dest, key=KEY)
            self.assertEqual(ctx.exception.kind, "COPY_HASH_MISMATCH")
        finally:
            cb.LocalDirTarget.store = orig
        incidents = list(self.dest.glob("*/INCIDENT-*.json"))
        self.assertTrue(incidents, "verify-on-write must emit an INCIDENT, not only raise")
        inc = json.loads(incidents[0].read_text(encoding="utf-8"))
        self.assertEqual(inc["kind"], "COPY_HASH_MISMATCH")


class TestQuiescence(BackupTestBase):
    """SOURCE_MUTATED: a torn snapshot must not seal MANIFEST.

    Copy-hash only sees the copy. Mutating the source AFTER it is stored
    still leaves copies matching the walk-time hashes, so VERIFY is green
    on the incumbent. Bite: `_bite_f43_mutate_retire.json`.
    """

    BITE = Path(__file__).resolve().parent / "_bite_f43_mutate_retire.json"

    def test_bite_artifact_records_pre_fix(self):
        self.assertTrue(self.BITE.is_file(), "bite must be recorded before belief")
        rec = json.loads(self.BITE.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertTrue(rec["torn_snapshot_sealed"])
        self.assertEqual(rec["torn_snapshot_kind"], "BACKUP_OK")
        self.assertTrue(rec["torn_snapshot_manifest_exists"])
        self.assertFalse(rec["has_do_retire"])
        self.assertFalse(rec["source_has_SOURCE_MUTATED"])

    def test_mutated_source_after_copy_is_SOURCE_MUTATED(self):
        orig = cb.LocalDirTarget.store

        def after_store(self, rel, src_path):
            orig(self, rel, src_path)
            if rel == "a.txt":
                Path(src_path).write_bytes(b"MUTATED-AFTER-COPY\n")

        cb.LocalDirTarget.store = after_store
        try:
            with self.assertRaises(cb.BackupRefusal) as ctx:
                cb.do_backup(self.src, self.dest, key=KEY)
            self.assertEqual(ctx.exception.kind, "SOURCE_MUTATED")
        finally:
            cb.LocalDirTarget.store = orig
        incidents = list(self.dest.glob("*/INCIDENT-*.json"))
        self.assertTrue(incidents, "SOURCE_MUTATED must emit an INCIDENT")
        inc = json.loads(incidents[0].read_text(encoding="utf-8"))
        self.assertEqual(inc["kind"], "SOURCE_MUTATED")
        self.assertIn("a.txt", inc["detail"]["mismatches"])

    def test_SOURCE_MUTATED_does_not_seal_manifest(self):
        orig = cb.LocalDirTarget.store

        def after_store(self, rel, src_path):
            orig(self, rel, src_path)
            if rel == "a.txt":
                Path(src_path).write_bytes(b"MUTATED-AFTER-COPY\n")

        cb.LocalDirTarget.store = after_store
        try:
            with self.assertRaises(cb.BackupRefusal) as ctx:
                cb.do_backup(self.src, self.dest, key=KEY)
            self.assertEqual(ctx.exception.kind, "SOURCE_MUTATED")
        finally:
            cb.LocalDirTarget.store = orig
        manifests = list(self.dest.glob("*/MANIFEST.json"))
        self.assertEqual(manifests, [], "a torn snapshot must not seal MANIFEST")
        sets = [p for p in self.dest.iterdir() if p.is_dir()]
        self.assertTrue(sets, "the incomplete set is left, never deleted")


class TestRetire(BackupTestBase):
    """Gap 5: a keep policy that stages, never deletes.

    keep < 1 is KEEP_TOO_SMALL. Oldest finished sets move to
    dest/_delme/predispose_*. Incomplete dirs (no MANIFEST) stay put.
    Bite: `_bite_f43_mutate_retire.json` (incumbent had no do_retire).
    """

    BITE = Path(__file__).resolve().parent / "_bite_f43_mutate_retire.json"

    def test_bite_artifact_records_no_do_retire(self):
        rec = json.loads(self.BITE.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertFalse(rec["has_do_retire"])
        self.assertFalse(rec["source_has_do_retire_def"])
        self.assertFalse(rec["source_has_add_parser_retire"])

    def _three_sets(self):
        sets = []
        for i in range(3):
            (self.src / "a.txt").write_text(f"gen-{i}\n", encoding="utf-8",
                                            newline="\n")
            sets.append(cb.do_backup(self.src, self.dest, key=KEY))
        return sets

    def test_keep_zero_is_KEEP_TOO_SMALL(self):
        self.dest.mkdir()
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_retire(self.dest, 0, key=KEY)
        self.assertEqual(ctx.exception.kind, "KEEP_TOO_SMALL")

    def test_keep_negative_is_KEEP_TOO_SMALL(self):
        self.dest.mkdir()
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_retire(self.dest, -1, key=KEY)
        self.assertEqual(ctx.exception.kind, "KEEP_TOO_SMALL")

    def test_keep_true_is_KEEP_TOO_SMALL_not_keep_one(self):
        """bool is a subclass of int. True == 1; without the bool guard
        this would keep=1 instead of refusing. Bite: True is int."""
        self.dest.mkdir()
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_retire(self.dest, True, key=KEY)
        self.assertEqual(ctx.exception.kind, "KEEP_TOO_SMALL")

    def test_keep_string_one_is_KEEP_TOO_SMALL(self):
        self.dest.mkdir()
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_retire(self.dest, "1", key=KEY)
        self.assertEqual(ctx.exception.kind, "KEEP_TOO_SMALL")

    def test_do_retire_dest_is_file_is_DEST_NOT_DIR(self):
        dest_file = self.tmp / "retire_dest_is_file"
        dest_file.write_text("not-a-dir", encoding="utf-8")
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_retire(dest_file, 1, key=KEY)
        self.assertEqual(ctx.exception.kind, "DEST_NOT_DIR")
        self.assertEqual(dest_file.read_text(encoding="utf-8"), "not-a-dir")

    def test_retires_oldest_stages_never_deletes(self):
        sets = self._three_sets()
        names = [p.name for p in sets]
        rec = cb.do_retire(self.dest, 2, key=KEY)
        cb.check_seal(rec, KEY)
        self.assertEqual(rec["kind"], "RETIRE_OK")
        self.assertTrue(rec["never_deleted"])
        self.assertEqual(len(rec["retired"]), 1)
        self.assertEqual(len(rec["kept"]), 2)
        oldest = sets[0]
        self.assertFalse(oldest.exists(), "retired path must be gone from dest")
        staged = Path(rec["retired"][0]["to"])
        self.assertTrue((staged / cb.MANIFEST_NAME).is_file())
        self.assertTrue((staged / cb.DATA_DIR).is_dir())
        # the staged set still verifies — it was moved, not shredded
        cb.do_verify(staged, KEY)
        remaining = [p.name for p in cb.list_backup_sets(self.dest)]
        self.assertEqual(remaining, names[1:])
        receipts = list(self.dest.glob("RETIRE-*.json"))
        self.assertEqual(len(receipts), 1)

    def test_keep_all_is_noop(self):
        sets = self._three_sets()
        rec = cb.do_retire(self.dest, 99, key=KEY)
        self.assertEqual(rec["retired"], [])
        self.assertEqual(len(rec["kept"]), 3)
        for s in sets:
            self.assertTrue((s / cb.MANIFEST_NAME).is_file())

    def test_does_not_touch_incomplete_or_rehearse(self):
        sets = self._three_sets()
        incomplete = self.dest / "incomplete-no-manifest"
        (incomplete / cb.DATA_DIR).mkdir(parents=True)
        (incomplete / cb.DATA_DIR / "x.txt").write_text("x\n", encoding="utf-8",
                                                         newline="\n")
        rehearse = self.dest / "_rehearse" / "scratch"
        rehearse.mkdir(parents=True)
        (rehearse / "y.txt").write_text("y\n", encoding="utf-8", newline="\n")
        rec = cb.do_retire(self.dest, 1, key=KEY)
        self.assertEqual(len(rec["retired"]), 2)  # of the 3 finished sets
        self.assertTrue((incomplete / cb.DATA_DIR / "x.txt").is_file())
        self.assertTrue((rehearse / "y.txt").is_file())
        self.assertEqual(len(cb.list_backup_sets(self.dest)), 1)
        self.assertTrue((sets[-1] / cb.MANIFEST_NAME).is_file())

    def test_retire_dest_occupied_refuses(self):
        sets = self._three_sets()
        retire_root = self.tmp / "occupied_retire"
        # pre-create the exact dest _xmove would pick
        stamp_probe = cb.do_retire(self.dest, 3, retire_root=retire_root, key=KEY)
        self.assertEqual(stamp_probe["retired"], [])  # keep=3, 3 sets: noop
        # plant an occupied slot for the oldest set's predisose name by
        # retiring with keep=2 after planting dest
        oldest = sets[0]
        planted = retire_root / f"predispose_{oldest.name}_PLANTED"
        # Force occupied by pointing retire_root at a file? Better: wrap
        # the dest that _xmove will use by pre-creating every possible
        # predisose_<name>_* is unique by utc stamp. Plant by making
        # retire_root a FILE so _xmkdirs/rename fails... that's COPY_IO.
        # Direct: call _xmove onto an existing dir.
        existing = self.tmp / "already"
        existing.mkdir()
        (existing / "precious.txt").write_text("PRECIOUS\n", encoding="utf-8",
                                               newline="\n")
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb._xmove(oldest, existing)
        self.assertEqual(ctx.exception.kind, "RETIRE_DEST_OCCUPIED")
        self.assertEqual((existing / "precious.txt").read_text(encoding="utf-8"),
                         "PRECIOUS\n")
        self.assertTrue((oldest / cb.MANIFEST_NAME).is_file())

    def test_cli_keep_zero_exits_2(self):
        self.dest.mkdir()
        rc = cb.main(["retire", "--dest-root", str(self.dest), "--keep", "0"])
        self.assertEqual(rc, 2)

    def test_missing_dest_is_DEST_NOT_DIR(self):
        missing = self.tmp / "no_such_dest"
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.list_backup_sets(missing)
        self.assertEqual(ctx.exception.kind, "DEST_NOT_DIR")


class TestUnpinnedRefusals(BackupTestBase):
    """Kinds that sat in BackupRefusal.kind / do_rehearse / _copy prose and
    were never named. A suite that only rehearses into an empty scratch and
    never hits a copy OSError stays green if those branches are deleted.
    Bite: `_bite_unpinned_refusals.json`."""

    BITE = Path(__file__).resolve().parent / "_bite_unpinned_refusals.json"

    BITE2 = Path(__file__).resolve().parent / "_bite_unpinned_round2.json"

    def test_bite_artifact_records_pre_fix(self):
        self.assertTrue(self.BITE.is_file(), "bite must be recorded before belief")
        rec = json.loads(self.BITE.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertEqual(rec["scratch_not_empty_old_kind"], "REHEARSAL_PASS")
        self.assertTrue(rec["scratch_not_empty_old_sealed"])
        self.assertEqual(rec["copy_io_old_crash"], "FileNotFoundError")

    def test_round2_bite_records_dest_file_untyped_crash(self):
        self.assertTrue(self.BITE2.is_file(), "round2 bite must be recorded before belief")
        rec = json.loads(self.BITE2.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertEqual(rec["dest_file_old_crash"], "FileNotFoundError")
        self.assertIsNone(rec["dest_file_old_kind"])
        self.assertEqual(rec["copy_onto_dir_old_kind"], "COPY_IO_ERROR")

    def test_copy_missing_src_is_COPY_IO_ERROR(self):
        dst = self.tmp / "out.bin"
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb._copy(self.tmp / "no_such_src.bin", dst)
        self.assertEqual(ctx.exception.kind, "COPY_IO_ERROR")
        self.assertTrue(str(ctx.exception).startswith("REFUSE[COPY_IO_ERROR]"))
        self.assertFalse(dst.exists())

    def test_copy_onto_existing_dir_is_COPY_IO_ERROR_not_a_clobber(self):
        dst_dir = self.tmp / "dst_as_dir"
        dst_dir.mkdir()
        precious = dst_dir / "keep.txt"
        precious.write_text("PRECIOUS", encoding="utf-8")
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb._copy(self.src / "a.txt", dst_dir)
        self.assertEqual(ctx.exception.kind, "COPY_IO_ERROR")
        self.assertEqual(precious.read_text(encoding="utf-8"), "PRECIOUS")

    def test_do_backup_dest_is_file_is_DEST_NOT_DIR(self):
        dest_file = self.tmp / "dest_is_file"
        dest_file.write_text("not-a-dir", encoding="utf-8")
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_backup(self.src, dest_file, key=KEY)
        self.assertEqual(ctx.exception.kind, "DEST_NOT_DIR")
        self.assertEqual(dest_file.read_text(encoding="utf-8"), "not-a-dir")


class TestRemoteSeams(unittest.TestCase):
    def test_adapters_registered(self):
        self.assertEqual(sorted(cb.ADAPTERS), ["es3", "gdx", "local", "odx", "r2"])

    def test_r2_without_credential_refuses_NO_CREDENTIALS(self):
        """The deliverable while F-46 is open: typed refusal, not a stub."""
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.ADAPTERS["r2"]()
        self.assertEqual(ctx.exception.kind, "NO_CREDENTIALS")
        self.assertNotIsInstance(ctx.exception, NotImplementedError)

    def test_r2_missing_credential_path_is_the_same_kind(self):
        missing = Path(tempfile.mkdtemp(prefix="cosmos_r2_miss_")) / "r2_credentials.json"
        self.addCleanup(shutil.rmtree, missing.parent, True)
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.ADAPTERS["r2"](credentials=missing)
        self.assertEqual(ctx.exception.kind, "NO_CREDENTIALS")

    def test_gdx_odx_es3_without_dest_refuse_NO_CONFIG(self):
        for name in ("gdx", "odx", "es3"):
            with self.assertRaises(cb.BackupRefusal) as ctx:
                cb.ADAPTERS[name]()
            self.assertEqual(ctx.exception.kind, "NO_CONFIG", name)

    def test_pycache_is_in_default_excludes_and_is_skipped(self):
        self.assertIn("__pycache__", cb.DEFAULT_EXCLUDES)
        tmp = Path(tempfile.mkdtemp(prefix="cosmos_pycache_"))
        self.addCleanup(shutil.rmtree, tmp, True)
        src = tmp / "src"
        (src / "__pycache__").mkdir(parents=True)
        (src / "keep.txt").write_text("ok\n", encoding="utf-8", newline="\n")
        (src / "__pycache__" / "drop.pyc").write_bytes(b"\x00")
        m = cb.build_manifest(src)
        self.assertEqual(sorted(m["files"]), ["keep.txt"])
        self.assertNotIn("__pycache__/drop.pyc", m["files"])


class TestExcludeMatching(unittest.TestCase):
    """Path-prefix + glob excludes. Basename `.git` still works."""

    def test_basename_git_still_matches(self):
        self.assertTrue(cb.is_excluded(".git/HEAD", [".git"]))
        self.assertTrue(cb.is_excluded("pkg/.git/config", [".git"]))
        self.assertFalse(cb.is_excluded("gitignore", [".git"]))

    def test_star_lock_matches_basename_not_other(self):
        self.assertTrue(cb.is_excluded("live/logs/cdeck_feed.lock", ["*.lock"]))
        self.assertTrue(cb.is_excluded("live/ledger/authority.jsonl.lock", ["*.lock"]))
        self.assertFalse(cb.is_excluded("live/ledger/authority.jsonl", ["*.lock"]))

    def test_path_prefix_slash_boundary(self):
        self.assertTrue(cb.is_excluded("live/logs/cdeck_feed.lock", ["live/logs"]))
        self.assertTrue(cb.is_excluded("live/logs", ["live/logs"]))
        self.assertFalse(cb.is_excluded("live/logstash/a.txt", ["live/logs"]))
        self.assertFalse(cb.is_excluded("live/ledger/authority.jsonl", ["live/logs"]))

    def test_build_manifest_skips_lock_and_keeps_ledger(self):
        tmp = Path(tempfile.mkdtemp(prefix="cosmos_ex_"))
        self.addCleanup(shutil.rmtree, tmp, True)
        src = tmp / "src"
        (src / "live" / "logs").mkdir(parents=True)
        (src / "live" / "ledger").mkdir(parents=True)
        (src / "live" / "logs" / "cdeck_feed.lock").write_text("pid\n", encoding="utf-8")
        (src / "live" / "ledger" / "authority.jsonl").write_text("{}\n", encoding="utf-8")
        m = cb.build_manifest(src, excludes=(".git", "*.lock", "live/logs"))
        self.assertEqual(sorted(m["files"]), ["live/ledger/authority.jsonl"])


class TestSecrets(BackupTestBase):
    """COVERAGE.md gap 4: a set that contains install_key.bin is a typed
    refusal, not a verified copy of the signing key. Bite: predecessor
    sealed BACKUP_OK over a planted install_key.bin.
    """

    def test_planted_install_key_bin_is_SECRETS_IN_SCOPE(self):
        (self.src / "install_key.bin").write_bytes(b"NOT-A-REAL-KEY")
        with self.assertRaises(cb.BackupRefusal) as cm:
            cb.do_backup(self.src, self.dest, key=KEY)
        self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE")
        self.assertIn("install_key.bin", cm.exception.detail)
        self.assertFalse(self.dest.exists(),
                         "refusal must happen before a set is created")

    def test_planted_api_token_txt_is_SECRETS_IN_SCOPE(self):
        (self.src / "config").mkdir()
        (self.src / "config" / "api_token.txt").write_text(
            "not-a-real-token\n", encoding="utf-8", newline="\n")
        with self.assertRaises(cb.BackupRefusal) as cm:
            cb.do_backup(self.src, self.dest, key=KEY)
        self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE")
        self.assertIn("api_token.txt", cm.exception.detail)

    def test_scan_secrets_reads_no_file_bytes(self):
        m = {"files": {"config/install_key.bin": {"sha256": "abc", "size": 32},
                       "a.txt": {"sha256": "def", "size": 1}}}
        hits = cb.scan_secrets(m)
        self.assertEqual(hits, ["config/install_key.bin"])

    def test_ordinary_tree_still_backs_up(self):
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        self.assertTrue((set_dir / cb.MANIFEST_NAME).is_file())


# Synthetic PEM *shapes* only. Bodies are dummy labels, not key material.
# Tests never print, echo, or copy these strings in assertions — only paths
# and BackupRefusal.kind.
_PUBLIC_CA_SHAPE = (
    "-----BEGIN CERTIFICATE-----\n"
    "NOT-A-REAL-CERTIFICATE-PUBLIC-CA-BUNDLE-FIXTURE\n"
    "-----END CERTIFICATE-----\n"
    "-----BEGIN CERTIFICATE-----\n"
    "ALSO-NOT-A-REAL-CERTIFICATE\n"
    "-----END CERTIFICATE-----\n"
)
_PRIVATE_RSA_SHAPE = (
    "-----BEGIN RSA PRIVATE KEY-----\n"
    "NOT-A-REAL-KEY-SYNTHETIC-FIXTURE-ONLY\n"
    "-----END RSA PRIVATE KEY-----\n"
)
_PRIVATE_ENCRYPTED_SHAPE = (
    "-----BEGIN ENCRYPTED PRIVATE KEY-----\n"
    "NOT-A-REAL-KEY-SYNTHETIC-FIXTURE-ONLY\n"
    "-----END ENCRYPTED PRIVATE KEY-----\n"
)
_PRIVATE_OPENSSH_SHAPE = (
    "-----BEGIN OPENSSH PRIVATE KEY-----\n"
    "NOT-A-REAL-KEY-SYNTHETIC-FIXTURE-ONLY\n"
    "-----END OPENSSH PRIVATE KEY-----\n"
)
_PRIVATE_EC_SHAPE = (
    "-----BEGIN EC PRIVATE KEY-----\n"
    "NOT-A-REAL-KEY-SYNTHETIC-FIXTURE-ONLY\n"
    "-----END EC PRIVATE KEY-----\n"
)
_PRIVATE_PGP_SHAPE = (
    "-----BEGIN PGP PRIVATE KEY BLOCK-----\n"
    "NOT-A-REAL-KEY-SYNTHETIC-FIXTURE-ONLY\n"
    "-----END PGP PRIVATE KEY BLOCK-----\n"
)


class TestPemClassification(BackupTestBase):
    """Public CA bundles are not key material; private-key envelopes still are.

    The predecessor treated EVERY `.pem` as a secret (path suffix) and ignored
    `.key` content, so a vendored certifi `cacert.pem` blocked offsite backup of
    `builds/` forever, while a private key stored as `signing.key` would have
    shipped. Classification is by BEGIN label; unknown/empty/unreadable refuses.
    """

    def test_public_ca_bundle_is_not_SECRETS_IN_SCOPE(self):
        pem = self.src / "vendor" / "certifi" / "cacert.pem"
        pem.parent.mkdir(parents=True)
        pem.write_text(_PUBLIC_CA_SHAPE, encoding="utf-8", newline="\n")
        set_dir = cb.do_backup(self.src, self.dest, key=KEY)
        self.assertTrue((set_dir / cb.MANIFEST_NAME).is_file())
        manifest = json.loads((set_dir / cb.MANIFEST_NAME).read_text(encoding="utf-8"))
        self.assertIn("vendor/certifi/cacert.pem", manifest["files"])
        self.assertEqual(cb.scan_secrets(manifest), [])

    def test_private_key_shape_is_SECRETS_IN_SCOPE(self):
        """A private-key envelope whose *path* the predecessor did not catch."""
        key = self.src / "vendor" / "mod" / "signing.key"
        key.parent.mkdir(parents=True)
        key.write_text(_PRIVATE_RSA_SHAPE, encoding="utf-8", newline="\n")
        with self.assertRaises(cb.BackupRefusal) as cm:
            cb.do_backup(self.src, self.dest, key=KEY)
        self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE")
        self.assertIn("signing.key", cm.exception.detail)
        self.assertFalse(self.dest.exists(),
                         "refusal must happen before a set is created")

    def test_private_pem_still_refuses(self):
        pem = self.src / "certs" / "server.pem"
        pem.parent.mkdir(parents=True)
        pem.write_text(_PRIVATE_RSA_SHAPE, encoding="utf-8", newline="\n")
        with self.assertRaises(cb.BackupRefusal) as cm:
            cb.do_backup(self.src, self.dest, key=KEY)
        self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE")
        self.assertIn("server.pem", cm.exception.detail)

    def test_encrypted_openssh_ec_pgp_shapes_refuse(self):
        cases = (
            ("enc.key", _PRIVATE_ENCRYPTED_SHAPE),
            ("ssh.key", _PRIVATE_OPENSSH_SHAPE),
            ("ec.key", _PRIVATE_EC_SHAPE),
            ("pgp.key", _PRIVATE_PGP_SHAPE),
        )
        for name, body in cases:
            dest = self.tmp / f"dest-{name}"
            src = self.tmp / f"src-{name}"
            src.mkdir()
            (src / "ok.txt").write_text("ok\n", encoding="utf-8", newline="\n")
            (src / name).write_text(body, encoding="utf-8", newline="\n")
            with self.assertRaises(cb.BackupRefusal) as cm:
                cb.do_backup(src, dest, key=KEY)
            self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE", name)
            self.assertIn(name, cm.exception.detail)

    def test_mixed_cert_and_private_refuses(self):
        pem = self.src / "bundle.pem"
        pem.write_text(_PUBLIC_CA_SHAPE + _PRIVATE_RSA_SHAPE,
                       encoding="utf-8", newline="\n")
        with self.assertRaises(cb.BackupRefusal) as cm:
            cb.do_backup(self.src, self.dest, key=KEY)
        self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE")
        self.assertIn("bundle.pem", cm.exception.detail)

    def test_empty_pem_is_fail_closed(self):
        (self.src / "empty.pem").write_bytes(b"")
        with self.assertRaises(cb.BackupRefusal) as cm:
            cb.do_backup(self.src, self.dest, key=KEY)
        self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE")
        self.assertIn("empty.pem", cm.exception.detail)

    def test_unknown_begin_label_is_fail_closed(self):
        (self.src / "weird.pem").write_text(
            "-----BEGIN UNKNOWN BLOB-----\nNOT-A-REAL-ANYTHING\n-----END UNKNOWN BLOB-----\n",
            encoding="utf-8", newline="\n")
        with self.assertRaises(cb.BackupRefusal) as cm:
            cb.do_backup(self.src, self.dest, key=KEY)
        self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE")
        self.assertIn("weird.pem", cm.exception.detail)

    def test_pem_without_source_root_is_fail_closed(self):
        hits = cb.scan_secrets({"files": {"vendor/certifi/cacert.pem": {"size": 1}}})
        self.assertEqual(hits, ["vendor/certifi/cacert.pem"])

    def test_pem_label_kind_table(self):
        self.assertEqual(cb.pem_label_kind({"CERTIFICATE"}), "public")
        self.assertEqual(cb.pem_label_kind({"TRUSTED CERTIFICATE", "CERTIFICATE"}),
                         "public")
        self.assertEqual(cb.pem_label_kind({"RSA PRIVATE KEY"}), "private")
        self.assertEqual(cb.pem_label_kind({"ENCRYPTED PRIVATE KEY"}), "private")
        self.assertEqual(cb.pem_label_kind({"OPENSSH PRIVATE KEY"}), "private")
        self.assertEqual(cb.pem_label_kind({"EC PRIVATE KEY"}), "private")
        self.assertEqual(cb.pem_label_kind({"PGP PRIVATE KEY BLOCK"}), "private")
        self.assertEqual(cb.pem_label_kind({"CERTIFICATE", "RSA PRIVATE KEY"}),
                         "private")
        self.assertEqual(cb.pem_label_kind(set()), "ambiguous")
        self.assertEqual(cb.pem_label_kind({"UNKNOWN BLOB"}), "ambiguous")
        self.assertEqual(cb.pem_label_kind({"CERTIFICATE", "UNKNOWN BLOB"}),
                         "ambiguous")

    def test_credential_path_shapes_still_refuse_without_opening_pem(self):
        (self.src / "install_key.bin").write_bytes(b"NOT-A-REAL-KEY")
        with self.assertRaises(cb.BackupRefusal) as cm:
            cb.do_backup(self.src, self.dest, key=KEY)
        self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE")
        self.assertIn("install_key.bin", cm.exception.detail)


class TestUnpinnedRound5(BackupTestBase):
    """Round-5: unreadable / non-object artifacts were untyped crashes.
    Bite `_bite_unpinned_round5.json`. Predecessor 5/5 FAIL."""

    BITE = Path(__file__).resolve().parent / "_bite_unpinned_round5.json"

    def test_round5_bite_records_pre_fix(self):
        self.assertTrue(self.BITE.is_file(), "bite must be recorded before belief")
        rec = json.loads(self.BITE.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertEqual(rec["obj_array_old_crash"], "AttributeError")
        self.assertEqual(rec["seal_str_old_crash"], "AttributeError")
        self.assertEqual(rec["local_garbage_old_crash"], "JSONDecodeError")
        self.assertEqual(rec["local_array_old_returned"], "list")
        self.assertEqual(rec["r2_garbage_old_crash"], "JSONDecodeError")
        self.assertEqual(rec["r2_true_old_returned"], "bool")

    def test_unreadable_manifest_is_NOT_A_BACKUP_SET(self):
        set_dir = self.tmp / "set"
        (set_dir / cb.DATA_DIR).mkdir(parents=True)
        (set_dir / cb.MANIFEST_NAME).write_text("{not json", encoding="utf-8")
        target = cb.LocalDirTarget(set_dir)
        with self.assertRaises(cb.BackupRefusal) as ctx:
            target.get_artifact(cb.MANIFEST_NAME)
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")
        self.assertTrue((set_dir / cb.MANIFEST_NAME).is_file(),
                        "refusal must not clobber the unreadable artifact")

    def test_manifest_array_is_NOT_A_BACKUP_SET(self):
        set_dir = self.tmp / "set2"
        (set_dir / cb.DATA_DIR).mkdir(parents=True)
        (set_dir / cb.MANIFEST_NAME).write_text("[]", encoding="utf-8")
        target = cb.LocalDirTarget(set_dir)
        with self.assertRaises(cb.BackupRefusal) as ctx:
            target.get_artifact(cb.MANIFEST_NAME)
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")


class TestFreeze(BackupTestBase):
    """F-43 gap 3: a frozen read-root survives live-source mutation.

    Default backup still SOURCE_MUTATED (TestQuiescence). freeze=handle
    copies from FrozenTree.capture() so a later write to the live source
    cannot appear in the sealed set. freeze=True is VSS: typed
    VSS_UNAVAILABLE when the shadow cannot be created — never a silent
    live-tree copy. Bite `_bite_f43_freeze.json`. Predecessor 4/4 FAIL.
    Round-6: BAD_FREEZE / FREEZE_DEST_OCCUPIED were documented and
    raised but unnamed in this suite; a handle missing info() was
    AttributeError. Bite `_bite_unpinned_round6.json`.
    """

    BITE = Path(__file__).resolve().parent / "_bite_f43_freeze.json"

    def test_bite_artifact_records_pre_fix(self):
        self.assertTrue(self.BITE.is_file(), "bite must be recorded before belief")
        rec = json.loads(self.BITE.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertFalse(rec["has_freeze_param"])
        self.assertEqual(rec["freeze_kw_crash"], "TypeError")
        self.assertEqual(rec["mutated_kind"], "SOURCE_MUTATED")
        self.assertFalse(rec["mutated_manifest_sealed"])

    def test_do_backup_accepts_freeze_kw(self):
        sig = __import__("inspect").signature(cb.do_backup)
        self.assertIn("freeze", sig.parameters)

    def test_frozen_tree_survives_source_mutation(self):
        import cosmos_backup_freeze as fz
        orig_hash = cb.sha256_file(self.src / "a.txt")
        handle = fz.FrozenTree.capture(self.src, self.tmp / "frozen")
        (self.src / "a.txt").write_bytes(b"MUTATED-LIVE\n")
        self.assertNotEqual(cb.sha256_file(self.src / "a.txt"), orig_hash)
        set_dir = cb.do_backup(self.src, self.dest, key=KEY, freeze=handle)
        manifest = json.loads((set_dir / cb.MANIFEST_NAME).read_text(encoding="utf-8"))
        cb.check_seal(manifest, KEY)
        self.assertEqual(manifest["files"]["a.txt"]["sha256"], orig_hash)
        self.assertEqual(manifest["freeze"]["kind"], "copy")
        stored = set_dir / cb.DATA_DIR / "a.txt"
        self.assertEqual(cb.sha256_file(stored), orig_hash)

    def test_default_backup_still_SOURCE_MUTATED(self):
        orig = cb.LocalDirTarget.store

        def after_store(self, rel, src_path):
            orig(self, rel, src_path)
            if rel == "a.txt":
                Path(src_path).write_bytes(b"MUTATED-AFTER-COPY\n")

        cb.LocalDirTarget.store = after_store
        try:
            with self.assertRaises(cb.BackupRefusal) as ctx:
                cb.do_backup(self.src, self.dest, key=KEY)
            self.assertEqual(ctx.exception.kind, "SOURCE_MUTATED")
        finally:
            cb.LocalDirTarget.store = orig

    def test_vss_create_failure_is_VSS_UNAVAILABLE(self):
        import cosmos_backup_freeze as fz
        planted = cb.BackupRefusal("VSS_UNAVAILABLE", "planted")
        orig = fz._create_shadow
        fz._create_shadow = lambda volume: (_ for _ in ()).throw(planted)
        try:
            with self.assertRaises(cb.BackupRefusal) as ctx:
                fz.acquire(self.src, True)
            self.assertEqual(ctx.exception.kind, "VSS_UNAVAILABLE")
        finally:
            fz._create_shadow = orig

    def test_freeze_true_never_silently_copies_live_tree(self):
        """freeze=True is VSS. Either a typed refusal or a vss-kind seal."""
        try:
            set_dir = cb.do_backup(self.src, self.dest, key=KEY, freeze=True)
        except cb.BackupRefusal as e:
            self.assertEqual(e.kind, "VSS_UNAVAILABLE")
            self.assertFalse(self.dest.exists() and any(self.dest.iterdir()),
                             "VSS_UNAVAILABLE must not leave a sealed set")
            return
        manifest = json.loads((set_dir / cb.MANIFEST_NAME).read_text(encoding="utf-8"))
        self.assertEqual(manifest["freeze"]["kind"], "vss")

    def test_freeze_released_on_secrets_refusal(self):
        class Spy:
            def __init__(self, root):
                self._root = Path(root)
                self.released = False

            def read_root(self):
                return self._root

            def info(self):
                return {"kind": "spy"}

            def release(self):
                self.released = True

        (self.src / "install_key.bin").write_bytes(b"NOT-A-REAL-KEY")
        spy = Spy(self.src)
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_backup(self.src, self.dest, freeze=spy)
        self.assertEqual(ctx.exception.kind, "SECRETS_IN_SCOPE")
        self.assertTrue(spy.released, "release() must run on SECRETS_IN_SCOPE")
        self.assertFalse(self.dest.exists(),
                         "refusal must happen before a set is created")

    def test_cli_backup_has_freeze_flag(self):
        import io
        from contextlib import redirect_stderr, redirect_stdout
        buf = io.StringIO()
        with self.assertRaises(SystemExit):
            with redirect_stdout(buf), redirect_stderr(buf):
                cb.main(["backup", "--help"])
        self.assertIn("--freeze", buf.getvalue())

    BITE6 = Path(__file__).resolve().parent / "_bite_unpinned_round6.json"

    def test_round6_bite_records_untyped_noinfo_crash(self):
        self.assertTrue(self.BITE6.is_file(), "bite must be recorded before belief")
        rec = json.loads(self.BITE6.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertEqual(rec["noinfo_dobackup_crash"], "AttributeError")
        self.assertIsNone(rec["noinfo_dobackup_kind"])
        self.assertEqual(rec["garbage_str_kind"], "BAD_FREEZE")
        self.assertEqual(rec["occupied_kind"], "FREEZE_DEST_OCCUPIED")
        self.assertFalse(rec["tests_name_BAD_FREEZE"])
        self.assertFalse(rec["tests_name_FREEZE_DEST_OCCUPIED"])

    def test_garbage_freeze_is_BAD_FREEZE(self):
        import cosmos_backup_freeze as fz
        with self.assertRaises(cb.BackupRefusal) as ctx:
            fz.acquire(self.src, "nope")
        self.assertEqual(ctx.exception.kind, "BAD_FREEZE")
        with self.assertRaises(cb.BackupRefusal) as ctx:
            fz.acquire(self.src, 1)
        self.assertEqual(ctx.exception.kind, "BAD_FREEZE")
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_backup(self.src, self.dest, freeze="nope")
        self.assertEqual(ctx.exception.kind, "BAD_FREEZE")
        self.assertFalse(self.dest.exists() and any(self.dest.iterdir()),
                         "BAD_FREEZE must not leave a sealed set")

    def test_occupied_freeze_dest_is_FREEZE_DEST_OCCUPIED(self):
        import cosmos_backup_freeze as fz
        frozen = self.tmp / "frozen"
        fz.FrozenTree.capture(self.src, frozen)
        with self.assertRaises(cb.BackupRefusal) as ctx:
            fz.FrozenTree.capture(self.src, frozen)
        self.assertEqual(ctx.exception.kind, "FREEZE_DEST_OCCUPIED")
        filedest = self.tmp / "frozen_file"
        filedest.write_bytes(b"x")
        with self.assertRaises(cb.BackupRefusal) as ctx:
            fz.FrozenTree.capture(self.src, filedest)
        self.assertEqual(ctx.exception.kind, "FREEZE_DEST_OCCUPIED")

    def test_handle_without_info_is_BAD_FREEZE(self):
        """Predecessor accepted read_root+release and AttributeError'd in do_backup."""
        import cosmos_backup_freeze as fz

        class NoInfo:
            def __init__(self, root):
                self._root = root

            def read_root(self):
                return self._root

            def release(self):
                return None

        with self.assertRaises(cb.BackupRefusal) as ctx:
            fz.acquire(self.src, NoInfo(self.src))
        self.assertEqual(ctx.exception.kind, "BAD_FREEZE")
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_backup(self.src, self.dest, freeze=NoInfo(self.src))
        self.assertEqual(ctx.exception.kind, "BAD_FREEZE")
        self.assertFalse(self.dest.exists() and any(self.dest.iterdir()),
                         "BAD_FREEZE must not leave a sealed set")


class TestUnpinnedRound6SealScan(BackupTestBase):
    """Round-6b: seal() of a non-object and scan_secrets of a malformed
    manifest were untyped crashes / a silent empty hit-list.
    Bite `_bite_unpinned_round6.json`. Predecessor 8/8 FAIL."""

    BITE = Path(__file__).resolve().parent / "_bite_unpinned_round6.json"

    def test_round6_bite_records_untyped_seal_and_scan(self):
        self.assertTrue(self.BITE.is_file(), "bite must be recorded before belief")
        rec = json.loads(self.BITE.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertEqual(rec["untyped_seal"], "AttributeError")
        self.assertEqual(rec["untyped_scan"], "KeyError")
        self.assertTrue(rec["scan_files_str_silent"])
        self.assertEqual(rec["seal_array"]["crash"], "AttributeError")
        self.assertEqual(rec["scan_files_str"]["returned"], "list")

    def test_seal_array_is_NO_SEAL(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.seal([])
        self.assertEqual(ctx.exception.kind, "NO_SEAL")

    def test_seal_none_is_NO_SEAL(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.seal(None)
        self.assertEqual(ctx.exception.kind, "NO_SEAL")

    def test_seal_str_is_NO_SEAL(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.seal("x")
        self.assertEqual(ctx.exception.kind, "NO_SEAL")

    def test_scan_empty_obj_is_NOT_A_BACKUP_SET(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.scan_secrets({})
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")

    def test_scan_array_is_NOT_A_BACKUP_SET(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.scan_secrets([])
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")

    def test_scan_files_str_is_NOT_A_BACKUP_SET_not_silent_empty(self):
        """A string iterates as characters and returned [] — the green-log."""
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.scan_secrets({"files": "install_key.bin"})
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")

    def test_scan_files_none_is_NOT_A_BACKUP_SET(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.scan_secrets({"files": None})
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")

    def test_scan_files_int_is_NOT_A_BACKUP_SET(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.scan_secrets({"files": 1})
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")

    def test_scan_still_finds_install_key_on_an_object_manifest(self):
        hits = cb.scan_secrets({
            "files": {"config/install_key.bin": {"sha256": "abc", "size": 32},
                      "a.txt": {"sha256": "def", "size": 1}},
        })
        self.assertEqual(hits, ["config/install_key.bin"])


class TestUnpinnedRound7ManifestExcludes(BackupTestBase):
    """Round-7: source_drift/_check of a malformed files field, is_excluded
    of a string/int, pem_label_kind of None/a string. Bite
    `_bite_unpinned_round7.json`. Predecessor 10/10 FAIL."""

    BITE = Path(__file__).resolve().parent / "_bite_unpinned_round7.json"

    def test_round7_bite_records_untyped_drift_and_excludes(self):
        self.assertTrue(self.BITE.is_file(), "bite must be recorded before belief")
        rec = json.loads(self.BITE.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertEqual(rec["drift_missing_files"]["crash"], "KeyError")
        self.assertEqual(rec["drift_files_str"]["crash"], "AttributeError")
        self.assertEqual(rec["check_files_str"]["crash"], "AttributeError")
        self.assertEqual(rec["check_entry_str"]["crash"], "TypeError")
        self.assertEqual(rec["exclude_int"]["crash"], "TypeError")
        self.assertEqual(rec["exclude_str"]["returned"], "bool")
        self.assertEqual(rec["pem_label_none"]["crash"], "TypeError")
        self.assertEqual(rec["verify_files_str"]["crash"], "AttributeError")

    def test_drift_missing_files_is_NOT_A_BACKUP_SET(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.source_drift(self.src, {})
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")

    def test_drift_files_str_is_NOT_A_BACKUP_SET(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.source_drift(self.src, {"files": "a.txt"})
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")

    def test_check_files_str_is_NOT_A_BACKUP_SET(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb._check({"files": "a.txt"}, lambda rel: self.src / rel)
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")

    def test_check_entry_str_is_NOT_A_BACKUP_SET(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb._check({"files": {"a.txt": "not-an-entry"}},
                      lambda rel: self.src / rel)
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")

    def test_exclude_str_is_BAD_EXCLUDES_not_silent_bool(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.is_excluded("live/git/x", "git")
        self.assertEqual(ctx.exception.kind, "BAD_EXCLUDES")

    def test_exclude_int_is_BAD_EXCLUDES(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.is_excluded("a.txt", 1)
        self.assertEqual(ctx.exception.kind, "BAD_EXCLUDES")

    def test_exclude_none_still_means_empty(self):
        self.assertFalse(cb.is_excluded("a.txt", None))

    def test_pem_label_none_is_ambiguous(self):
        self.assertEqual(cb.pem_label_kind(None), "ambiguous")

    def test_pem_label_str_is_one_label_not_characters(self):
        self.assertEqual(cb.pem_label_kind("PRIVATE KEY"), "private")
        self.assertEqual(cb.pem_label_kind("CERTIFICATE"), "public")

    def test_verify_files_str_is_NOT_A_BACKUP_SET(self):
        set_dir = self.tmp / "set_str_files"
        (set_dir / cb.DATA_DIR).mkdir(parents=True)
        sealed = cb.seal({"format": cb.FORMAT, "files": "a.txt", "total_bytes": 0})
        (set_dir / cb.MANIFEST_NAME).write_text(
            json.dumps(sealed, indent=2, sort_keys=True), encoding="utf-8")
        with self.assertRaises(cb.BackupRefusal) as ctx:
            cb.do_verify(set_dir)
        self.assertEqual(ctx.exception.kind, "NOT_A_BACKUP_SET")


class TestRealDocsSubset(unittest.TestCase):
    """Bounded real-tree test: at most 5 files from $COSMOS_TEST_DOCS."""

    def test_real_subset_roundtrip(self):
        root = os.environ.get("COSMOS_TEST_DOCS")
        if not root or not Path(root).is_dir():
            self.skipTest("COSMOS_TEST_DOCS not set to a real directory")
        picks = sorted(p for p in Path(root).iterdir()
                       if p.is_file() and p.suffix == ".md")[:5]
        self.assertTrue(picks, "no .md files found to test with")
        tmp = Path(tempfile.mkdtemp(prefix="cosmos_backup_real_"))
        self.addCleanup(shutil.rmtree, tmp, True)
        src = tmp / "src"
        src.mkdir()
        for p in picks:
            shutil.copyfile(p, src / p.name)  # copy OUT of the tree; tree untouched
        set_dir = cb.do_backup(src, tmp / "dest", key=KEY)
        proof = json.loads(cb.do_rehearse(set_dir, tmp / "scratch", KEY)
                           .read_text(encoding="utf-8"))
        cb.check_seal(proof, KEY)
        self.assertEqual(proof["files_restored"], len(picks))
        for p in picks:  # restored bytes match the LIVE tree originals
            self.assertEqual(cb.sha256_file(tmp / "scratch" / p.name),
                             cb.sha256_file(p), p.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
