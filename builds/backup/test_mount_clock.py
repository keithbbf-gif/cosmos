#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""test_mount_clock - the scheduled GDX/ODX/ES.3 push, and above all its REFUSAL.

Dests (F-48 leftover) are not named and will not be named here: this suite must
pass on a machine whose `backup_targets.json` is absent, forever. So the two
things it pins hardest are:

  1. With NO config the tick REFUSES, typed (`NO_CONFIG`), writes a heartbeat
     saying so, exits 2, and writes nothing to any mount. That refusal is the
     deliverable while dests are unconfigured — it is what lets the schtasks
     entry be armed today and start working the night the dests land.
  2. With an INJECTED FakeProbe + scratch dest the SAME tick() runs the whole
     push — bind, secret scan, verify-on-write, receipt, heartbeat — so the
     scheduled code path is proven end to end rather than a parallel imitation.

Bite first: `_bite_mount_clock_absent.json` records ModuleNotFoundError while
this module did not exist. A test that cannot fail against the old world is
not a test.

Nothing in this suite can touch a real DriveFS / OneDrive / ES.3 mount.
No key material is read.

    py -3.14 builds/backup/test_mount_clock.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cosmos_backup as bk               # noqa: E402
import cosmos_backup_mounts as mounts    # noqa: E402
import cosmos_backup_r2 as r2            # noqa: E402
import cosmos_mount_clock as mc          # noqa: E402
import cosmos_offsite_clock as oc        # noqa: E402

CosmosPaths, CosmosPathError = mc.CosmosPaths, mc.CosmosPathError
BITE_ABSENT = HERE / "_bite_mount_clock_absent.json"


class _Root(unittest.TestCase):
    """A real (temporary) COSMOS runtime root: sentinel CONTENT, not just a dir."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_mc_"))
        self.root = self.tmp / "live"
        self.root.mkdir(parents=True)
        (self.root / ".cosmos-root.json").write_text(
            json.dumps({"system": "COSMOS", "tree_id": "KMesh-COSMOS-test",
                        "schema_version": 1}), encoding="utf-8")
        for role in ("logs", "config", "work", "state"):
            (self.root / role).mkdir(parents=True, exist_ok=True)
        self.paths = CosmosPaths(self.root)

        self.src = self.tmp / "src"
        (self.src / "sub").mkdir(parents=True)
        (self.src / "a.txt").write_text("alpha\n", encoding="utf-8")
        (self.src / "sub" / "b.txt").write_text("bravo\n", encoding="utf-8")
        self.scopes = [{"name": "src", "source": str(self.src),
                        "excludes": (".git", "__pycache__")}]
        self.cfg = self.paths.config(mc.CONFIG_NAME)

        self.dest = self.tmp / "gdx"
        self.dest.mkdir()
        self.probe = mounts.FakeProbe(volumes={
            str(self.src): "vol:SRC",
            str(self.src.resolve()): "vol:SRC",
            str(self.dest): "vol:GDX",
            str(self.dest.resolve()): "vol:GDX",
        })

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def hb(self) -> dict:
        return json.loads(self.paths.logs(mc.HEARTBEAT_NAME).read_text(encoding="utf-8"))

    def run_tick(self):
        return mc.tick(self.paths, self.scopes, self.cfg,
                       probe=self.probe, dests={"gdx": self.dest})


class TestBiteAgainstAbsence(_Root):
    """Prove the new checks FAIL against the world that lacked this module."""

    def test_absent_bite_artifact_names_ModuleNotFoundError(self):
        self.assertTrue(BITE_ABSENT.is_file(), "bite must be recorded before belief")
        rec = json.loads(BITE_ABSENT.read_text(encoding="utf-8"))
        self.assertEqual(rec["state"], "ABSENT")
        self.assertEqual(rec["kind"], "ModuleNotFoundError")
        self.assertIn("cosmos_mount_clock", rec["detail"])

    def test_the_module_now_exists_under_builds_backup(self):
        self.assertEqual(Path(mc.__file__).resolve().parent, HERE)
        self.assertEqual(mc.WORKER, "cosmos-mount-clock")


class TestRefusesWithoutConfig(_Root):
    """The deliverable while dests are unconfigured."""

    def test_tick_refuses_typed_and_does_not_raise(self):
        self.assertFalse(self.cfg.exists(), "fixture must have NO backup_targets.json")
        rec = mc.tick(self.paths, self.scopes, self.cfg)
        self.assertEqual(rec["state"], "REFUSED")
        self.assertEqual(rec["kind"], "NO_CONFIG")
        self.assertFalse(rec["ok"])

    def test_the_refusal_is_heartbeated_not_swallowed(self):
        mc.tick(self.paths, self.scopes, self.cfg)
        hb = self.hb()
        self.assertEqual(hb["kind"], "NO_CONFIG")
        self.assertEqual(hb["worker"], mc.WORKER)
        self.assertIn("last_run_epoch", hb)

    def test_a_refusal_never_fabricates_an_offsite_copy(self):
        rec = mc.tick(self.paths, self.scopes, self.cfg)
        self.assertFalse(rec["offsite_copy_exists"])
        self.assertIsNone(rec["success_age_s"])
        self.assertNotIn("last_success_epoch", rec)

    def test_refusal_reaches_a_real_mount_never(self):
        """A probe that would explode if bind() ran. It must not."""
        class Boom(mounts.MountProbe):
            def is_dir(self, path):
                raise AssertionError("a config-less tick must not bind a dest")
        rec = mc.tick(self.paths, self.scopes, self.cfg, probe=Boom())
        self.assertEqual(rec["kind"], "NO_CONFIG")

    def test_cli_exits_2_and_names_the_kind(self):
        rc = mc.main(["--root", str(self.root), "--once", "--source", str(self.src)])
        self.assertEqual(rc, 2, "a typed refusal is rc=2, never rc=0")
        self.assertEqual(self.hb()["kind"], "NO_CONFIG")

    def test_empty_dest_row_is_NO_DEST_not_invented(self):
        self.cfg.write_text(json.dumps({
            "schema": mounts.SCHEMA,
            "targets": {"gdx": {"dest": ""}, "odx": {"dest": ""}, "es3": {"dest": ""}},
        }), encoding="utf-8")
        rec = mc.tick(self.paths, self.scopes, self.cfg, probe=self.probe)
        by = {r["target_kind"]: r for r in rec["targets"]}
        self.assertEqual(by["gdx"]["kind"], "NO_DEST")
        self.assertEqual(by["odx"]["kind"], "NO_DEST")
        self.assertEqual(by["es3"]["kind"], "NO_DEST")
        self.assertEqual(by["r2"]["kind"], "NO_CREDENTIALS",
                         "scheduled path must also emit a typed R2 refusal")
        self.assertFalse(rec["ok"])
        self.assertFalse(rec["offsite_copy_exists"])


class TestForbiddenDest(_Root):

    def test_plaintext_key_store_is_refused_by_path_alone(self):
        rec = mc.tick(self.paths, self.scopes, self.cfg,
                      probe=self.probe,
                      dests={"gdx": Path(r"D:\R2Cloner\backups")})
        self.assertEqual(rec["kind"], "FORBIDDEN_DEST")
        self.assertFalse(rec["offsite_copy_exists"])


class TestScopeDeclaration(_Root):

    def test_missing_scope_file_refuses_rather_than_guessing_a_tree(self):
        with self.assertRaises(bk.BackupRefusal) as cm:
            oc.load_scopes(self.paths.config(mc.SCOPES_NAME))
        self.assertEqual(cm.exception.kind, "NO_SCOPES")

    def test_cli_once_without_scopes_heartbeats_NO_SCOPES(self):
        rc = mc.main(["--root", str(self.root), "--once"])
        self.assertEqual(rc, 2)
        self.assertEqual(self.hb()["kind"], "NO_SCOPES")


class TestFullPushOffline(_Root):
    """The same tick(), with FakeProbe. Nothing here can reach a real mount."""

    def test_push_verify_on_write_lands_files_on_the_scratch_dest(self):
        rec = self.run_tick()
        self.assertTrue(rec["ok"], rec)
        row = rec["targets"][0]
        self.assertEqual(row["state"], "PUSHED")
        self.assertEqual(row["files_pushed"], 2)
        self.assertEqual(row["target_kind"], "gdx")
        set_dir = Path(row["set_dir"])
        self.assertTrue(set_dir.is_dir())
        self.assertTrue((set_dir / "data" / "a.txt").is_file())
        self.assertTrue((set_dir / "data" / "sub" / "b.txt").is_file())
        self.assertTrue(str(set_dir).startswith(str(self.dest)),
                        "selfcheck dest must be the scratch dest, never a real mount")

    def test_receipt_lands_on_this_machine_too(self):
        rec = self.run_tick()
        p = Path(rec["targets"][0]["receipt"])
        self.assertTrue(p.is_file())
        receipt = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(receipt["kind"], "MOUNT_PUSH_OK")
        bk.check_seal(receipt)

    def test_success_sets_the_protection_clock(self):
        rec = self.run_tick()
        self.assertTrue(rec["offsite_copy_exists"])
        self.assertIsNotNone(rec["success_age_s"])
        self.assertEqual(rec["last_success_scopes"], ["src"])

    def test_a_later_refusal_remembers_the_last_real_success(self):
        first = self.run_tick()
        second = mc.tick(self.paths, self.scopes, self.cfg)  # no config now
        self.assertEqual(second["state"], "REFUSED")
        self.assertEqual(second["kind"], "NO_CONFIG")
        self.assertEqual(second["last_success_epoch"], first["last_success_epoch"])
        self.assertTrue(second["offsite_copy_exists"])

    def test_secrets_in_scope_refuse_the_push_before_a_byte_moves(self):
        (self.src / "api_token.txt").write_text("not-a-real-token\n", encoding="utf-8")
        rec = self.run_tick()
        self.assertFalse(rec["ok"])
        row = rec["targets"][0]
        self.assertEqual(row["kind"], "SECRETS_IN_SCOPE")
        self.assertFalse((self.dest / "a.txt").is_file(),
                         "a refused push must not have copied the tree")
        self.assertFalse(rec["offsite_copy_exists"])

    def test_same_volume_is_refused(self):
        same = mounts.FakeProbe(volumes={
            str(self.src): "vol:SAME",
            str(self.src.resolve()): "vol:SAME",
            str(self.dest): "vol:SAME",
            str(self.dest.resolve()): "vol:SAME",
        })
        rec = mc.tick(self.paths, self.scopes, self.cfg,
                      probe=same, dests={"gdx": self.dest})
        self.assertEqual(rec["kind"], "SAME_VOLUME")
        self.assertFalse(rec["offsite_copy_exists"])

    def test_one_kind_refusing_does_not_cancel_the_other(self):
        missing = self.tmp / "not_mounted"
        rec = mc.tick(self.paths, self.scopes, self.cfg, probe=self.probe,
                      dests={"gdx": self.dest, "es3": missing})
        by = {r["target_kind"]: r for r in rec["targets"]}
        self.assertEqual(by["gdx"]["state"], "PUSHED")
        self.assertEqual(by["es3"]["kind"], "DRIVE_NOT_MOUNTED")
        self.assertEqual(rec["state"], "PARTIAL")
        self.assertFalse(rec["ok"])
        self.assertTrue(rec["offsite_copy_exists"],
                        "a PUSHED row means data left this volume even if another kind refused")
        self.assertIsNotNone(rec.get("last_success_epoch"))


class TestPauseIsHonored(_Root):

    def _flag(self, body: str) -> None:
        p = self.paths.role("state", "control", "PAUSE.flag")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")

    def test_paused_tick_does_no_work_but_still_beats(self):
        self._flag(json.dumps({"state": "PAUSED"}))
        rec = mc.tick(self.paths, self.scopes, self.cfg)
        self.assertEqual(rec["state"], "PAUSED")
        self.assertTrue(rec["ok"])
        self.assertIn("last_run_epoch", self.hb())

    def test_running_flag_lets_the_tick_proceed(self):
        self._flag(json.dumps({"state": "RUNNING"}))
        rec = mc.tick(self.paths, self.scopes, self.cfg)
        self.assertEqual(rec["state"], "REFUSED")
        self.assertEqual(rec["kind"], "NO_CONFIG")

    def test_unreadable_flag_is_fail_closed(self):
        self._flag("{ this is not json")
        self.assertTrue(oc.paused(self.paths))

    def test_heartbeat_array_is_empty_object_not_a_list(self):
        hb = self.paths.logs(mc.HEARTBEAT_NAME)
        hb.parent.mkdir(parents=True, exist_ok=True)
        hb.write_text("[]", encoding="utf-8")
        self.assertEqual(mc.read_heartbeat(hb), {})


class TestSelfcheckDrivesTheRealPath(_Root):

    def test_selfcheck_pushes_to_a_scratch_dest_with_FakeProbe(self):
        rec = mc.selfcheck(self.paths, self.scopes)
        self.assertTrue(rec["ok"], rec)
        row = rec["targets"][0]
        self.assertEqual(row["files_pushed"], 2)
        dest = Path(row["dest"])
        self.assertIn(mc.SELFCHECK_STAGE, dest.parts)
        self.assertTrue(dest.is_dir(), "never-delete: scratch dest survives")

    def test_cli_selfcheck_exits_zero(self):
        rc = mc.main(["--root", str(self.root), "--selfcheck",
                      "--source", str(self.src)])
        self.assertEqual(rc, 0)


class TestScheduling(_Root):

    def test_plan_task_argv_is_daily_windowless_and_points_at_this_file(self):
        argv = mc.plan_task_argv(self.root, "03:00")
        self.assertEqual(argv[:4], ["schtasks", "/create", "/tn", mc.TASK_NAME])
        joined = " ".join(argv)
        self.assertIn("/sc daily", joined)
        self.assertIn("/st 03:00", joined)
        self.assertIn("cosmos_mount_clock.py", joined)
        self.assertIn("--once", joined)
        self.assertNotIn("/rl highest", joined, "the push needs no elevation")

    @unittest.skipUnless(os.name == "nt", "pythonw is a Windows binary")
    def test_task_runs_pythonw_so_no_console_flashes_nightly(self):
        self.assertIn("pythonw", " ".join(mc.plan_task_argv(self.root)).lower())

    def test_plan_task_registers_nothing(self):
        calls = []
        real = mc.subprocess.run
        mc.subprocess.run = lambda *a, **k: calls.append(a) or real(*a, **k)
        try:
            rc = mc.main(["--root", str(self.root), "--plan-task"])
        finally:
            mc.subprocess.run = real
        self.assertEqual(rc, 0)
        self.assertEqual(calls, [])

    def test_stale_threshold_matches_a_daily_cadence(self):
        self.assertGreater(mc.STALE_S, 24 * 3600)
        self.assertLess(mc.STALE_S, 48 * 3600)

    def test_heartbeat_name_is_discoverable_by_the_health_watchdog(self):
        self.assertIn("heartbeat", mc.HEARTBEAT_NAME)
        self.assertTrue(mc.HEARTBEAT_NAME.endswith(".json"))


class TestModuleResolutionInAFreshProcess(_Root):
    """Same shadow as the R2 clock: in-process imports hide a cosmos/ collision."""

    def _run(self, *args) -> tuple[int, str, str]:
        p = subprocess.run([sys.executable, str(Path(mc.__file__).resolve()), *args],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=180)
        return p.returncode, p.stdout, p.stderr

    def test_the_clock_binds_the_builds_backup_backup_module(self):
        self.assertEqual(Path(mc.cb.__file__).resolve().parent, HERE)

    def test_cli_imports_cleanly_in_a_fresh_interpreter(self):
        rc, out, err = self._run("--root", str(self.root), "--plan-task")
        self.assertEqual(rc, 0, f"import-time failure: {err[-600:]}")
        self.assertEqual(json.loads(out)["task"], mc.TASK_NAME)

    def test_cli_selfcheck_completes_a_real_push_in_a_fresh_interpreter(self):
        rc, out, err = self._run("--root", str(self.root), "--selfcheck",
                                 "--source", str(self.src))
        self.assertEqual(rc, 0, err[-600:])
        rec = json.loads(out)
        self.assertEqual(rec["targets"][0]["files_pushed"], 2)
        self.assertTrue(Path(rec["heartbeat_path"]).is_file())
        dest = Path(rec["targets"][0]["dest"])
        self.assertNotEqual(dest.drive.upper(), "X:",
                            "selfcheck must never land on DriveFS")
        self.assertNotIn("OneDrive", str(dest))

    def test_cli_refusal_exit_code_in_a_fresh_interpreter(self):
        rc, out, err = self._run("--root", str(self.root), "--once",
                                 "--source", str(self.src))
        self.assertEqual(rc, 2, err[-600:])
        self.assertEqual(json.loads(out)["kind"], "NO_CONFIG")


class TestR2LegOnMountClock(_Root):
    """The 03:00 task must also push to R2. Credential absence is typed."""

    def _cfg_gdx(self) -> None:
        self.cfg.write_text(json.dumps({
            "schema": mounts.SCHEMA,
            "targets": {"gdx": {"dest": str(self.dest)},
                        "odx": {"dest": ""},
                        "es3": {"dest": ""}},
        }), encoding="utf-8")

    def test_scheduled_path_emits_r2_NO_CREDENTIALS_when_file_absent(self):
        self._cfg_gdx()
        self.assertFalse(self.paths.config(mc.CREDENTIALS_NAME).exists())
        rec = mc.tick(self.paths, self.scopes, self.cfg, probe=self.probe)
        by = {r["target_kind"]: r for r in rec["targets"]}
        self.assertEqual(by["gdx"]["state"], "PUSHED")
        self.assertEqual(by["r2"]["state"], "REFUSED")
        self.assertEqual(by["r2"]["kind"], "NO_CREDENTIALS")
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["state"], "PARTIAL")

    def test_injected_dests_without_r2_override_do_not_touch_r2(self):
        rec = self.run_tick()
        kinds = [r["target_kind"] for r in rec["targets"]]
        self.assertNotIn("r2", kinds)
        self.assertTrue(rec["ok"])

    def test_memory_transport_pushes_r2_and_readback_verifies(self):
        rec = mc.tick(
            self.paths, self.scopes, self.cfg,
            probe=self.probe, dests={"gdx": self.dest}, force=True,
            r2_transport_factory=r2.MemoryTransport,
            r2_credentials_override=r2.R2Credentials(
                "selfcheckaccount", r2.SELFCHECK_ID, r2.SELFCHECK_ID,
                "selfcheck-bucket"))
        by = {r["target_kind"]: r for r in rec["targets"]}
        self.assertEqual(by["gdx"]["state"], "PUSHED")
        self.assertEqual(by["r2"]["state"], "PUSHED")
        self.assertEqual(by["r2"]["files_pushed"], 2)
        self.assertEqual(by["r2"]["readback_verified"], 2)
        self.assertEqual(by["r2"]["bucket"], "selfcheck-bucket")
        self.assertTrue(rec["ok"])
        receipt = json.loads(Path(by["r2"]["receipt"]).read_text(encoding="utf-8"))
        self.assertEqual(receipt["kind"], "R2_PUSH_OK")
        self.assertEqual(receipt["target"]["secret_access_key"],
                         "<redacted — never emitted>")

    def test_selfcheck_includes_an_r2_row_via_MemoryTransport(self):
        rec = mc.selfcheck(self.paths, self.scopes)
        by = {r["target_kind"]: r for r in rec["targets"]}
        self.assertEqual(by["gdx"]["files_pushed"], 2)
        self.assertEqual(by["r2"]["state"], "PUSHED")
        self.assertEqual(by["r2"]["readback_verified"], 2)
        self.assertTrue(rec["ok"])

    def test_r2_forbidden_credential_path_is_typed(self):
        rec = mc.tick(
            self.paths, self.scopes, self.cfg,
            probe=self.probe, dests={"gdx": self.dest}, force=True,
            r2_credentials=Path(r"D:\R2Cloner\r2_credentials.json"))
        by = {r["target_kind"]: r for r in rec["targets"]}
        self.assertEqual(by["r2"]["kind"], "FORBIDDEN_CREDENTIAL_PATH")
        self.assertEqual(by["gdx"]["state"], "PUSHED")


class TestRootIdentity(_Root):

    def test_a_directory_without_the_sentinel_is_not_a_root(self):
        plain = self.tmp / "plain"
        plain.mkdir()
        with self.assertRaises(CosmosPathError) as cm:
            CosmosPaths(plain)
        self.assertEqual(cm.exception.kind, "IDENTITY_MISMATCH")

    def test_cli_refuses_a_non_root_with_rc_2(self):
        plain = self.tmp / "plain2"
        plain.mkdir()
        self.assertEqual(mc.main(["--root", str(plain), "--once"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
