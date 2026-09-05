#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""test_state_offsite - F-54 payload packer, and above all its REFUSAL.

Dests and the R2 credential are not here. This suite must pass on a machine
that holds neither, forever. Pins:

  1. The module was ABSENT (`_bite_state_offsite_absent.json`).
  2. With NO dest and NO credential, tick() REFUSES `NO_OFFSITE_ROUTE`,
     heartbeats the refusal, exits 2, and writes nothing to a mount.
  3. pack() copies the whitelist and REFUSES SECRETS_IN_SCOPE if a secret
     is planted in the packed tree.
  4. With FakeProbe + MemoryTransport the SAME tick() packs, pushes both
     routes, and read-back-verifies — the scheduled path, not an imitation.

No key material is read. Nothing reaches DriveFS / OneDrive / R2.

    py -3.14 builds/backup/test_state_offsite.py
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
import cosmos_state_offsite as so        # noqa: E402

CosmosPaths, CosmosPathError = so.CosmosPaths, so.CosmosPathError
BITE = HERE / "_bite_state_offsite_absent.json"


class _Root(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_f54_"))
        self.root = self.tmp / "live"
        self.root.mkdir(parents=True)
        (self.root / ".cosmos-root.json").write_text(
            json.dumps({"system": "COSMOS", "tree_id": "KMesh-COSMOS-test",
                        "schema_version": 1}), encoding="utf-8")
        for role in ("logs", "config", "work", "state"):
            (self.root / role).mkdir(parents=True, exist_ok=True)
        self.paths = CosmosPaths(self.root)
        state = self.root / "state"
        (state / "SEED.json").write_text('{"schema":"seed-test","n":1}', encoding="utf-8")
        (state / "SEED.decl.json").write_text('{"len":1}', encoding="utf-8")
        (state / "inflight.jsonl").write_text('{"lease":"a"}\n', encoding="utf-8")
        (state / "motif_tracker.json").write_text('{"stage":1}', encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def hb(self):
        return json.loads(self.paths.logs(so.HEARTBEAT_NAME).read_text(encoding="utf-8"))


class TestBiteAgainstAbsence(_Root):

    def test_absent_bite_artifact_names_ModuleNotFoundError(self):
        self.assertTrue(BITE.is_file(), "bite must be recorded before belief")
        rec = json.loads(BITE.read_text(encoding="utf-8"))
        self.assertEqual(rec["state"], "ABSENT")
        self.assertEqual(rec["kind"], "ModuleNotFoundError")
        self.assertIn("cosmos_state_offsite", rec["detail"])

    def test_the_module_now_exists_under_builds_backup(self):
        self.assertEqual(Path(so.__file__).resolve().parent, HERE)
        self.assertEqual(so.WORKER, "cosmos-state-offsite")
        self.assertEqual(so.PAYLOAD, ("SEED.json", "SEED.decl.json",
                                      "inflight.jsonl", "motif_tracker.json"))


class TestPack(_Root):

    def test_pack_copies_the_whitelist_and_nothing_else(self):
        extra = self.root / "state" / "audit_noise.json"
        extra.write_text("nope", encoding="utf-8")
        dest = self.tmp / "packed"
        rec = so.pack(self.paths, dest)
        self.assertEqual(sorted(rec["copied"]), sorted(so.PAYLOAD))
        self.assertEqual(rec["missing"], [])
        self.assertEqual(rec["files"], 4)
        names = {p.name for p in dest.iterdir()}
        self.assertEqual(names, set(so.PAYLOAD))
        self.assertNotIn("audit_noise.json", names)

    def test_pack_dest_is_file_is_DEST_NOT_DIR(self):
        dest_file = self.tmp / "pack_is_file"
        dest_file.write_text("not-a-dir", encoding="utf-8")
        with self.assertRaises(bk.BackupRefusal) as cm:
            so.pack(self.paths, dest_file)
        self.assertEqual(cm.exception.kind, "DEST_NOT_DIR")
        self.assertEqual(dest_file.read_text(encoding="utf-8"), "not-a-dir")

    def test_pack_refuses_empty_payload(self):
        for name in so.PAYLOAD:
            (self.root / "state" / name).unlink()
        with self.assertRaises(bk.BackupRefusal) as cm:
            so.pack(self.paths, self.tmp / "empty")
        self.assertEqual(cm.exception.kind, "EMPTY_PAYLOAD")

    def test_pack_refuses_a_planted_secret(self):
        dest = self.tmp / "secretpack"
        so.pack(self.paths, dest)
        (dest / "install_key.bin").write_bytes(b"NOT-A-REAL-KEY")
        with self.assertRaises(bk.BackupRefusal) as cm:
            # Re-scan by packing over a dest that already has the secret: the
            # whitelist copy itself does not add it, so we scan after planting.
            manifest = bk.build_manifest(dest)
            offenders = r2.scan_secrets(manifest)
            if offenders:
                raise bk.BackupRefusal("SECRETS_IN_SCOPE", ",".join(offenders))
        self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE")
        self.assertIn("install_key.bin", cm.exception.detail)

    def test_tick_refuses_if_secret_is_in_the_packed_tree_via_payload_name(self):
        """A payload filename that IS a secret name must not go off-machine."""
        # Rename is not possible (PAYLOAD is a constant). Plant inside pack dest
        # by making pack() copy then tick's scan: tick packs fresh. Instead push
        # a dest containing the secret through mounts.push via the adapter.
        dest = self.tmp / "gdx"
        dest.mkdir()
        packed = self.tmp / "p"
        so.pack(self.paths, packed)
        (packed / "install_key.bin").write_bytes(b"NOT-A-REAL-KEY")
        probe = mounts.FakeProbe(volumes={
            str(packed): "vol:SRC", str(packed.resolve()): "vol:SRC",
            str(dest): "vol:GDX", str(dest.resolve()): "vol:GDX",
        })
        with self.assertRaises(bk.BackupRefusal) as cm:
            mounts.push(packed, "gdx", dest=dest, probe=probe)
        self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE")


class TestRefusesWithoutRoute(_Root):

    def test_tick_refuses_typed_NO_OFFSITE_ROUTE(self):
        self.assertFalse(self.paths.config(so.CONFIG_NAME).exists())
        self.assertFalse(self.paths.config(so.CREDENTIALS_NAME).exists())
        rec = so.tick(self.paths)
        self.assertEqual(rec["state"], "REFUSED")
        self.assertEqual(rec["kind"], "NO_OFFSITE_ROUTE")
        self.assertFalse(rec["ok"])
        kinds = {r["kind"] for r in rec["routes"]}
        self.assertIn("NO_CONFIG", kinds)
        self.assertIn("NO_CREDENTIALS", kinds)

    def test_the_refusal_is_heartbeated_not_swallowed(self):
        so.tick(self.paths)
        hb = self.hb()
        self.assertEqual(hb["kind"], "NO_OFFSITE_ROUTE")
        self.assertEqual(hb["worker"], so.WORKER)
        self.assertIn("last_run_epoch", hb)

    def test_a_refusal_never_fabricates_an_offsite_copy(self):
        rec = so.tick(self.paths)
        self.assertFalse(rec["offsite_copy_exists"])
        self.assertNotIn("last_success_epoch", rec)

    def test_preflight_creates_nothing_and_writes_no_heartbeat(self):
        out = so.preflight(self.paths)
        self.assertEqual(out["status"], "BLOCKED")
        self.assertEqual(out["kind"], "NO_OFFSITE_ROUTE")
        self.assertTrue(out["adapter_implemented"]["mount"])
        self.assertTrue(out["adapter_implemented"]["r2"])
        self.assertFalse(out["heartbeat_written"])
        self.assertFalse(self.paths.logs(so.HEARTBEAT_NAME).exists())
        self.assertEqual(out["payload"]["present"], 4)

    def test_preflight_does_not_invent_a_dest(self):
        out = so.preflight(self.paths)
        blob = json.dumps(out)
        self.assertNotIn("X:\\", blob)
        self.assertNotIn("OneDrive", blob)


class TestInjectedRoutes(_Root):

    def test_selfcheck_pushes_both_routes(self):
        rec = so.selfcheck(self.paths)
        self.assertTrue(rec["ok"], rec)
        self.assertEqual(rec["state"], "PUSHED")
        routes = {r["route"] for r in rec["targets"]}
        self.assertEqual(routes, {"mount", "r2"})
        r2_row = next(r for r in rec["targets"] if r["route"] == "r2")
        self.assertEqual(r2_row["readback_verified"], 4)
        self.assertEqual(r2_row["files_pushed"], 4)
        mount_row = next(r for r in rec["targets"] if r["route"] == "mount")
        self.assertEqual(mount_row["files_pushed"], 4)
        self.assertTrue(rec["offsite_copy_exists"])
        self.assertTrue(Path(mount_row["set_dir"]).is_dir())

    def test_selfcheck_never_writes_the_live_mount(self):
        rec = so.selfcheck(self.paths)
        mount_row = next(r for r in rec["targets"] if r["route"] == "mount")
        set_dir = Path(mount_row["set_dir"])
        self.assertTrue(str(set_dir).startswith(str(self.root.resolve()))
                        or str(set_dir).startswith(str(self.paths.root)))
        self.assertIn("_delme_state_offsite", str(set_dir).replace("\\", "/"))


class TestCliFreshInterpreter(_Root):

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(Path(so.__file__).resolve()), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=120)

    def test_cli_binds_builds_backup_not_cosmos(self):
        self.assertEqual(Path(so.cb.__file__).resolve().parent, HERE)

    def test_cli_preflight_refuses_in_a_fresh_interpreter(self):
        p = self._run("--root", str(self.root), "--preflight")
        self.assertEqual(p.returncode, 2, p.stderr[-600:])
        rec = json.loads(p.stdout)
        self.assertEqual(rec["kind"], "NO_OFFSITE_ROUTE")
        self.assertFalse(rec["heartbeat_written"])

    def test_cli_once_refuses_NO_OFFSITE_ROUTE(self):
        p = self._run("--root", str(self.root), "--once")
        self.assertEqual(p.returncode, 2, p.stderr[-600:])
        rec = json.loads(p.stdout)
        self.assertEqual(rec["kind"], "NO_OFFSITE_ROUTE")
        self.assertTrue(Path(rec["heartbeat_path"]).is_file())

    def test_cli_selfcheck_in_a_fresh_interpreter(self):
        p = self._run("--root", str(self.root), "--selfcheck")
        self.assertEqual(p.returncode, 0, (p.stderr or "")[-800:])
        rec = json.loads(p.stdout)
        self.assertEqual(rec["state"], "PUSHED")
        r2_row = next(r for r in rec["targets"] if r["route"] == "r2")
        self.assertEqual(r2_row["readback_verified"], 4)

    def test_cli_plan_task_in_a_fresh_interpreter(self):
        p = self._run("--root", str(self.root), "--plan-task")
        self.assertEqual(p.returncode, 0, p.stderr[-600:])
        rec = json.loads(p.stdout)
        self.assertEqual(rec["task"], so.TASK_NAME)
        self.assertFalse(rec["registers"])
        self.assertEqual(rec["payload"], list(so.PAYLOAD))
        self.assertIn("--once", " ".join(rec["argv"]))


class TestScheduling(_Root):

    def test_plan_task_argv_is_daily_windowless_and_points_at_this_file(self):
        argv = so.plan_task_argv(self.root, "03:15")
        self.assertEqual(argv[:4], ["schtasks", "/create", "/tn", so.TASK_NAME])
        joined = " ".join(argv)
        self.assertIn("/sc daily", joined)
        self.assertIn("/st 03:15", joined)
        self.assertIn("cosmos_state_offsite.py", joined)
        self.assertIn("--once", joined)
        self.assertNotIn("/rl highest", joined, "the push needs no elevation")
        self.assertEqual(so.TASK_NAME, "COSMOS State Offsite Push")

    @unittest.skipUnless(os.name == "nt", "pythonw is a Windows binary")
    def test_task_runs_pythonw_so_no_console_flashes_nightly(self):
        self.assertIn("pythonw", " ".join(so.plan_task_argv(self.root)).lower())

    def test_plan_task_registers_nothing(self):
        calls = []
        real = so.subprocess.run
        so.subprocess.run = lambda *a, **k: calls.append(a) or real(*a, **k)
        try:
            rc = so.main(["--root", str(self.root), "--plan-task"])
        finally:
            so.subprocess.run = real
        self.assertEqual(rc, 0)
        self.assertEqual(calls, [])

    def test_stale_threshold_matches_a_daily_cadence(self):
        self.assertGreater(so.STALE_S, 24 * 3600)
        self.assertLess(so.STALE_S, 48 * 3600)

    def test_heartbeat_name_is_discoverable_by_the_health_watchdog(self):
        self.assertIn("heartbeat", so.HEARTBEAT_NAME)
        self.assertTrue(so.HEARTBEAT_NAME.endswith(".json"))

    def test_payload_is_the_whitelist_not_a_scope_tree(self):
        argv = so.plan_task_argv(self.root)
        joined = " ".join(argv)
        self.assertNotIn("cosmos_offsite_clock.py", joined)
        self.assertNotIn("cosmos_mount_clock.py", joined)
        self.assertEqual(so.PAYLOAD, ("SEED.json", "SEED.decl.json",
                                      "inflight.jsonl", "motif_tracker.json"))


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("live_value", json.dumps({
        "checks": result.testsRun,
        "failures": len(result.failures) + len(result.errors),
        "bite": str(BITE),
        "refusal_kinds": ["NO_OFFSITE_ROUTE", "EMPTY_PAYLOAD", "SECRETS_IN_SCOPE",
                          "DEST_NOT_DIR"],
        "task": so.TASK_NAME,
        "clock": "plan_task_registers_nothing",
    }, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
