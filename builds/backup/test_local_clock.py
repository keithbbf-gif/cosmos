#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""test_local_clock - F-43 P0 daemon schtasks vehicle, and its REFUSAL.

Dest is not here. This suite must pass on a machine with no
backup_targets.json forever. Pins:

  1. The module was ABSENT (`_bite_f43_plan_task.json`).
  2. With NO dest, tick() REFUSES `NO_CONFIG`, heartbeats the refusal,
     exits 2, and creates no backup set.
  3. A dest on the same volume is `SAME_VOLUME`.
  4. `--plan-task` emits `COSMOS Bulletproof Backup` daily 04:00 and
     registers nothing.
  5. With FakeProbe + a scratch dest the SAME tick() verifies — the
     scheduled path, not an imitation.

No key material is read. Nothing is written onto a real dest.

    py -3.14 builds/backup/test_local_clock.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cosmos_backup as bk               # noqa: E402
import cosmos_backup_mounts as mounts    # noqa: E402
import cosmos_local_clock as lc          # noqa: E402

CosmosPaths = lc.CosmosPaths
BITE = HERE / "_bite_f43_plan_task.json"


class _Root(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_lc_"))
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

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def hb(self) -> dict:
        return json.loads(self.paths.logs(lc.HEARTBEAT_NAME).read_text(encoding="utf-8"))


class TestBiteAgainstAbsence(_Root):

    def test_absent_bite_artifact_all_bite(self):
        self.assertTrue(BITE.is_file(), "bite must be recorded before belief")
        rec = json.loads(BITE.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"])
        self.assertFalse(rec["clock_exists"])
        self.assertEqual(rec["import_state"], "ABSENT")
        self.assertEqual(rec["import_error"], "ModuleNotFoundError")
        self.assertFalse(rec["daemon_has_plan_task_argv"])

    def test_the_module_now_exists_under_builds_backup(self):
        self.assertEqual(Path(lc.__file__).resolve().parent, HERE)
        self.assertEqual(lc.WORKER, "cosmos-local-clock")
        self.assertEqual(lc.TASK_NAME, "COSMOS Bulletproof Backup")


class TestRefusesWithoutConfig(_Root):

    def test_tick_refuses_typed_and_does_not_raise(self):
        self.assertFalse(self.cfg.exists())
        rec = lc.tick(self.paths, self.cfg)
        self.assertEqual(rec["state"], "REFUSED")
        self.assertEqual(rec["kind"], "NO_CONFIG")
        self.assertFalse(rec["ok"])

    def test_the_refusal_is_heartbeated_not_swallowed(self):
        lc.tick(self.paths, self.cfg)
        hb = self.hb()
        self.assertEqual(hb["kind"], "NO_CONFIG")
        self.assertEqual(hb["worker"], lc.WORKER)
        self.assertIn("last_run_epoch", hb)

    def test_a_refusal_never_fabricates_an_off_volume_copy(self):
        rec = lc.tick(self.paths, self.cfg)
        self.assertFalse(rec["off_volume_copy_exists"])
        self.assertIsNone(rec["success_age_s"])

    def test_empty_local_dest_is_NO_DEST(self):
        self.cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {"dest": "", "source": str(self.src)}},
        }), encoding="utf-8")
        rec = lc.tick(self.paths, self.cfg)
        self.assertEqual(rec["kind"], "NO_DEST")
        self.assertEqual(rec["state"], "REFUSED")

    def test_named_dest_without_source_is_NO_SOURCE(self):
        self.cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {"dest": str(self.dest), "source": ""}},
        }), encoding="utf-8")
        rec = lc.tick(self.paths, self.cfg, probe=self.probe)
        self.assertEqual(rec["kind"], "NO_SOURCE")

    def test_same_volume_is_SAME_VOLUME(self):
        same = mounts.FakeProbe(volumes={
            str(self.src): "vol:SAME",
            str(self.src.resolve()): "vol:SAME",
            str(self.dest): "vol:SAME",
            str(self.dest.resolve()): "vol:SAME",
        })
        rec = lc.tick(self.paths, self.cfg, source=self.src, dest=self.dest,
                      probe=same, force=True)
        self.assertEqual(rec["kind"], "SAME_VOLUME")
        self.assertFalse(rec["ok"])
        self.assertEqual(list(self.dest.iterdir()), [],
                         "SAME_VOLUME must not create a set")

    def test_relative_dest_is_BAD_CONFIG(self):
        with self.assertRaises(bk.BackupRefusal) as ctx:
            lc.bind_local(Path("relative/dest"), self.src, probe=self.probe)
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")

    def test_dest_is_file_is_DRIVE_NOT_MOUNTED(self):
        dest_file = self.tmp / "dest_is_file"
        dest_file.write_text("not-a-dir", encoding="utf-8")
        probe = mounts.FakeProbe(volumes={
            str(self.src): "vol:SRC", str(self.src.resolve()): "vol:SRC",
            str(dest_file): "vol:DST", str(dest_file.resolve()): "vol:DST",
        })
        with self.assertRaises(bk.BackupRefusal) as ctx:
            lc.bind_local(dest_file, self.src, probe=probe)
        self.assertEqual(ctx.exception.kind, "DRIVE_NOT_MOUNTED")
        self.assertTrue(dest_file.is_file(), "refusal must not clobber dest")

    def test_targets_local_list_is_NO_DEST(self):
        self.cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": ["not", "a", "row"]},
        }), encoding="utf-8")
        rec = lc.tick(self.paths, self.cfg, force=True)
        self.assertEqual(rec["kind"], "NO_DEST")
        self.assertEqual(rec["state"], "REFUSED")


class TestIdentityIsContentNotExistence(_Root):
    """Drive letter is not identity. A swapped disk at dest must not copy."""

    def _write_local(self, identity):
        self.cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {
                "dest": str(self.dest), "source": str(self.src),
                "identity": identity,
            }},
        }), encoding="utf-8")

    def _sets(self):
        return [p for p in self.dest.iterdir()
                if p.is_dir() and p.name != "_rehearse"]

    def test_volume_serial_mismatch_is_IDENTITY_MISMATCH(self):
        self._write_local({"kind": "volume_serial", "value": "vol:OTHER"})
        rec = lc.tick(self.paths, self.cfg, probe=self.probe, force=True)
        self.assertEqual(rec["kind"], "IDENTITY_MISMATCH")
        self.assertEqual(rec["state"], "REFUSED")
        self.assertFalse(rec["ok"])
        self.assertEqual(self._sets(), [],
                         "IDENTITY_MISMATCH must not create a set")

    def test_volume_serial_match_still_verifies(self):
        self._write_local({"kind": "volume_serial", "value": "vol:DST"})
        rec = lc.tick(self.paths, self.cfg, probe=self.probe, force=True)
        self.assertEqual(rec["state"], "VERIFIED", rec)
        self.assertTrue(self._sets())

    def test_identity_string_is_BAD_CONFIG(self):
        self._write_local("vol:OTHER")
        rec = lc.tick(self.paths, self.cfg, probe=self.probe, force=True)
        self.assertEqual(rec["kind"], "BAD_CONFIG")
        self.assertEqual(rec["state"], "REFUSED")
        self.assertEqual(self._sets(), [])

    def test_unknown_identity_kind_is_BAD_CONFIG(self):
        self._write_local({"kind": "drive_letter", "value": "D:"})
        rec = lc.tick(self.paths, self.cfg, probe=self.probe, force=True)
        self.assertEqual(rec["kind"], "BAD_CONFIG")
        self.assertEqual(self._sets(), [])

    def test_bind_local_mismatch_raises_IDENTITY_MISMATCH(self):
        with self.assertRaises(bk.BackupRefusal) as ctx:
            lc.bind_local(self.dest, self.src, probe=self.probe,
                          identity={"kind": "volume_serial", "value": "vol:OTHER"})
        self.assertEqual(ctx.exception.kind, "IDENTITY_MISMATCH")

    def test_example_template_names_identity(self):
        example = json.loads(
            (HERE / "backup_targets.example.json").read_text(encoding="utf-8"))
        self.assertIn("identity", example["targets"]["local"])

    def test_example_template_names_per_target_excludes(self):
        example = json.loads(
            (HERE / "backup_targets.example.json").read_text(encoding="utf-8"))
        ex = example["targets"]["local"]["excludes"]
        self.assertIn("*.lock", ex)
        self.assertIn("live/config", ex)
        self.assertIn("live/logs", ex)
        self.assertNotIn("live/ledger", ex)


class TestTickVerifiesOnInjectedDest(_Root):

    def test_injected_dest_is_the_scheduled_path(self):
        rec = lc.tick(self.paths, self.cfg, source=self.src, dest=self.dest,
                      probe=self.probe, force=True)
        self.assertEqual(rec["state"], "VERIFIED", rec)
        self.assertTrue(rec["ok"])
        self.assertTrue(rec["off_volume_copy_exists"])
        sets = [p for p in self.dest.iterdir() if p.is_dir() and p.name != "_rehearse"]
        self.assertTrue(sets, "a verified set must land under dest")
        manifest = json.loads((sets[0] / bk.MANIFEST_NAME).read_text(encoding="utf-8"))
        self.assertIn("a.txt", manifest["files"])


class TestScheduling(_Root):

    def test_plan_task_argv_is_daily_windowless_and_points_at_this_file(self):
        argv = lc.plan_task_argv(self.root, "04:00")
        self.assertEqual(argv[:4], ["schtasks", "/create", "/tn", lc.TASK_NAME])
        joined = " ".join(argv)
        self.assertIn("/sc daily", joined)
        self.assertIn("/st 04:00", joined)
        self.assertIn("cosmos_local_clock.py", joined)
        self.assertIn("--once", joined)
        self.assertNotIn("/rl highest", joined)

    @unittest.skipUnless(os.name == "nt", "pythonw is a Windows binary")
    def test_task_runs_pythonw_so_no_console_flashes_nightly(self):
        self.assertIn("pythonw", " ".join(lc.plan_task_argv(self.root)).lower())

    def test_plan_task_registers_nothing(self):
        calls = []
        real = lc.subprocess.run
        lc.subprocess.run = lambda *a, **k: calls.append(a) or real(*a, **k)
        try:
            rc = lc.main(["--root", str(self.root), "--plan-task"])
        finally:
            lc.subprocess.run = real
        self.assertEqual(rc, 0)
        self.assertEqual(calls, [])

    def test_stale_threshold_matches_a_daily_cadence(self):
        self.assertGreater(lc.STALE_S, 24 * 3600)
        self.assertLess(lc.STALE_S, 48 * 3600)

    def test_heartbeat_name_is_discoverable_by_the_health_watchdog(self):
        self.assertIn("heartbeat", lc.HEARTBEAT_NAME)
        self.assertTrue(lc.HEARTBEAT_NAME.endswith(".json"))


class TestPreflight(_Root):

    def test_preflight_without_config_is_BLOCKED_and_writes_no_heartbeat(self):
        rec = lc.preflight(self.paths, self.cfg)
        self.assertEqual(rec["status"], "BLOCKED")
        self.assertEqual(rec["kind"], "NO_CONFIG")
        self.assertTrue(rec["adapter_implemented"])
        self.assertFalse(rec["heartbeat_written"])
        self.assertFalse(self.paths.logs(lc.HEARTBEAT_NAME).is_file())

    def test_cli_preflight_exits_two(self):
        rc = lc.main(["--root", str(self.root), "--preflight"])
        self.assertEqual(rc, 2)
        self.assertFalse(self.paths.logs(lc.HEARTBEAT_NAME).is_file())


class TestSelfcheck(_Root):

    def test_selfcheck_verifies_on_scratch_dest(self):
        rec = lc.selfcheck(self.paths)
        self.assertEqual(rec["state"], "VERIFIED", rec)
        dest = Path(rec["dest"])
        self.assertIn(lc.SELFCHECK_STAGE, dest.parts)
        self.assertTrue(dest.is_dir(), "never-delete: scratch dest survives")

    def test_cli_selfcheck_exits_zero(self):
        rc = lc.main(["--root", str(self.root), "--selfcheck"])
        self.assertEqual(rc, 0)


class TestModuleResolutionInAFreshProcess(_Root):

    def _run(self, *args) -> tuple[int, str, str]:
        p = subprocess.run([sys.executable, str(Path(lc.__file__).resolve()), *args],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=180)
        return p.returncode, p.stdout, p.stderr

    def test_the_clock_binds_the_builds_backup_backup_module(self):
        self.assertEqual(Path(lc.cb.__file__).resolve().parent, HERE)

    def test_cli_plan_task_in_a_fresh_interpreter(self):
        rc, out, err = self._run("--root", str(self.root), "--plan-task")
        self.assertEqual(rc, 0, f"import-time failure: {err[-600:]}")
        body = json.loads(out)
        self.assertEqual(body["task"], lc.TASK_NAME)
        self.assertIs(body["registers"], False)

    def test_cli_selfcheck_completes_in_a_fresh_interpreter(self):
        rc, out, err = self._run("--root", str(self.root), "--selfcheck")
        self.assertEqual(rc, 0, err[-600:])
        rec = json.loads(out)
        self.assertEqual(rec["state"], "VERIFIED")
        self.assertTrue(Path(rec["heartbeat_path"]).is_file())

    def test_cli_refusal_exit_code_in_a_fresh_interpreter(self):
        rc, out, err = self._run("--root", str(self.root), "--once")
        self.assertEqual(rc, 2, err[-600:])
        self.assertEqual(json.loads(out)["kind"], "NO_CONFIG")


@contextmanager
def _hold_exclusive(path: Path):
    """Hold a file so a later open() is PermissionError (the live daemon lock).

    Windows: CreateFileW share-mode 0. POSIX: chmod 0. Same process, new
    open() — that is sha256_file's path. Never skip: if the hold fails the
    test is invalid.
    """
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


class TestLiveLockScope(_Root):
    """A .lock in the tree is out of scope; an unreadable data file is not.

    Both pins FAIL against the pre-fix walker (exact-basename excludes only,
    tick() hard-coded DEFAULT_EXCLUDES). Bite: `_fail_local_excludes_against_old.py`.
    """

    def _arm_local(self):
        self.cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {
                "dest": str(self.dest), "source": str(self.src),
            }},
        }), encoding="utf-8")

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
        self._arm_local()
        with _hold_exclusive(lock):
            rec = lc.tick(self.paths, self.cfg, probe=self.probe, force=True)
        self.assertEqual(rec["state"], "VERIFIED", rec)
        self.assertTrue(rec["ok"], rec)
        self.assertGreater(rec.get("files") or 0, 0)
        sets = self._sets()
        self.assertTrue(sets, "a verified set must land under dest")
        manifest = json.loads((sets[0] / bk.MANIFEST_NAME).read_text(encoding="utf-8"))
        files = manifest["files"]
        self.assertNotIn("live/logs/cdeck_feed.lock", files)
        self.assertIn("live/ledger/authority.jsonl", files)
        self.assertIn("a.txt", files)

    def test_unreadable_in_scope_data_still_refuses(self):
        # Walk order: live/ before zzz/. Pre-fix hits the lock first and
        # never names the data file. New code skips *.lock, then REFUSES
        # on zzz/data.txt — fail-closed on in-scope unreadables.
        lock = self.src / "live" / "logs" / "cdeck_feed.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text("pid\n", encoding="utf-8", newline="\n")
        data = self.src / "zzz" / "data.txt"
        data.parent.mkdir(parents=True)
        data.write_text("canon\n", encoding="utf-8", newline="\n")
        self._arm_local()
        with _hold_exclusive(lock), _hold_exclusive(data):
            rec = lc.tick(self.paths, self.cfg, probe=self.probe, force=True)
        self.assertEqual(rec["state"], "REFUSED", rec)
        self.assertEqual(rec["kind"], "SOURCE_UNREADABLE", rec)
        detail = rec.get("detail") or ""
        self.assertIn("zzz/data.txt", detail.replace("\\", "/"), rec)
        self.assertNotIn("cdeck_feed.lock", detail, rec)
        self.assertEqual(self._sets(), [],
                         "SOURCE_UNREADABLE must not create a finished set")

    def test_live_config_secret_shape_is_out_of_scope(self):
        cfg_dir = self.src / "live" / "config"
        cfg_dir.mkdir(parents=True)
        (cfg_dir / "api_token.txt").write_text(
            "not-a-real-token\n", encoding="utf-8", newline="\n")
        (self.src / "live" / "ledger").mkdir(parents=True)
        (self.src / "live" / "ledger" / "authority.jsonl").write_text(
            '{"n":1}\n', encoding="utf-8", newline="\n")
        self._arm_local()
        rec = lc.tick(self.paths, self.cfg, probe=self.probe, force=True)
        self.assertEqual(rec["state"], "VERIFIED", rec)
        sets = self._sets()
        manifest = json.loads((sets[0] / bk.MANIFEST_NAME).read_text(encoding="utf-8"))
        files = manifest["files"]
        self.assertNotIn("live/config/api_token.txt", files)
        self.assertFalse(any("api_token.txt" in k for k in files))
        self.assertIn("live/ledger/authority.jsonl", files)
        dest_hit = list((sets[0] / bk.DATA_DIR).rglob("api_token.txt"))
        self.assertEqual(dest_hit, [], "credentials must not land on dest")

    def test_trylive_config_secret_shape_is_out_of_scope(self):
        cfg_dir = self.src / "trylive" / "config"
        cfg_dir.mkdir(parents=True)
        (cfg_dir / "api_token.txt").write_text(
            "not-a-real-token\n", encoding="utf-8", newline="\n")
        (cfg_dir / "install_key.bin").write_bytes(b"NOT-A-REAL-KEY")
        self._arm_local()
        rec = lc.tick(self.paths, self.cfg, probe=self.probe, force=True)
        self.assertEqual(rec["state"], "VERIFIED", rec)
        sets = self._sets()
        manifest = json.loads((sets[0] / bk.MANIFEST_NAME).read_text(encoding="utf-8"))
        files = manifest["files"]
        self.assertFalse(any("api_token.txt" in k for k in files))
        self.assertFalse(any("install_key.bin" in k for k in files))
        self.assertEqual(list((sets[0] / bk.DATA_DIR).rglob("api_token.txt")), [])
        self.assertEqual(list((sets[0] / bk.DATA_DIR).rglob("install_key.bin")), [])

    def test_excludes_not_a_list_is_BAD_CONFIG(self):
        self.cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {
                "dest": str(self.dest), "source": str(self.src),
                "excludes": "*.lock",
            }},
        }), encoding="utf-8")
        rec = lc.tick(self.paths, self.cfg, probe=self.probe, force=True)
        self.assertEqual(rec["kind"], "BAD_CONFIG")
        self.assertEqual(rec["state"], "REFUSED")
        self.assertEqual(self._sets(), [])

    def test_operator_extras_union_defaults_cannot_drop_lock(self):
        row = {"dest": str(self.dest), "source": str(self.src),
               "excludes": ["tmp"]}
        got = lc.parse_excludes(row)
        self.assertIn("*.lock", got)
        self.assertIn("live/config", got)
        self.assertIn("tmp", got)
        self.assertEqual(lc.parse_excludes({"excludes": []}),
                         lc.LOCAL_DEFAULT_EXCLUDES)

    def test_local_row_list_is_BAD_CONFIG(self):
        with self.assertRaises(bk.BackupRefusal) as ctx:
            lc.local_row([])
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")

    def test_local_row_none_is_BAD_CONFIG(self):
        with self.assertRaises(bk.BackupRefusal) as ctx:
            lc.local_row(None)
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")

    def test_parse_excludes_list_is_BAD_CONFIG(self):
        with self.assertRaises(bk.BackupRefusal) as ctx:
            lc.parse_excludes([])
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")

    def test_parse_excludes_str_is_BAD_CONFIG(self):
        with self.assertRaises(bk.BackupRefusal) as ctx:
            lc.parse_excludes("*.lock")
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")

    def test_heartbeat_array_is_empty_object_not_a_list(self):
        hb = self.paths.logs(lc.HEARTBEAT_NAME)
        hb.parent.mkdir(parents=True, exist_ok=True)
        hb.write_text("[]", encoding="utf-8")
        self.assertEqual(lc.read_heartbeat(hb), {})

    def test_write_heartbeat_none_is_BAD_HEARTBEAT(self):
        with self.assertRaises(bk.BackupRefusal) as ctx:
            lc.write_heartbeat(self.paths.logs(lc.HEARTBEAT_NAME), None)
        self.assertEqual(ctx.exception.kind, "BAD_HEARTBEAT")


if __name__ == "__main__":
    tests = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    print("%d/%d" % (result.testsRun - len(result.failures) - len(result.errors),
                     result.testsRun))
    raise SystemExit(0 if result.wasSuccessful() else 1)
