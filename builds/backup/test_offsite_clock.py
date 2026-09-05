#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""test_offsite_clock - the scheduled offsite push, and above all its REFUSAL.

The credential (F-46) is not here and will not be here: this suite must pass on a
machine that holds no R2 key, forever. So the two things it pins hardest are:

  1. With NO credential the tick REFUSES, typed (`NO_CREDENTIALS`), writes a
     heartbeat saying so, exits 2, and touches no network. That refusal is the
     deliverable while F-46 is open - it is what lets the schtasks entry be armed
     today and start working the night the credential lands.
  2. With an INJECTED memory transport the SAME tick() runs the whole push -
     manifest, PUT, GET, re-hash, sealed receipt, heartbeat - so the scheduled code
     path is proven end to end offline rather than a parallel imitation of it.

Plus the two things a refusing clock gets wrong if nobody checks: that a refusal
does not fabricate a success timestamp, and that a real success is remembered
across the refusals that follow it.

No key material is read, written or referenced anywhere in this file. The only
credential object is `R2Credentials("...", "TEST-NOT-A-CREDENTIAL", ...)`.

    py -3.14 builds/backup/test_offsite_clock.py
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

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cosmos_backup as bk               # noqa: E402
import cosmos_backup_r2 as r2            # noqa: E402
import cosmos_offsite_clock as oc        # noqa: E402

# The resolver comes from the clock, deliberately: `cosmos/` must never go on
# sys.path here either, or this suite would recreate the very shadow it pins.
CosmosPaths, CosmosPathError = oc.CosmosPaths, oc.CosmosPathError

FAKE = "TEST-NOT-A-CREDENTIAL"


def _fake_creds() -> r2.R2Credentials:
    return r2.R2Credentials("testaccount", FAKE, FAKE, "test-bucket")


class _Root(unittest.TestCase):
    """A real (temporary) COSMOS runtime root: sentinel CONTENT, not just a dir."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_oc_"))
        self.root = self.tmp / "live"
        (self.root).mkdir(parents=True)
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
        self.creds_path = self.paths.config("r2_credentials.json")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def hb(self) -> dict:
        return json.loads(self.paths.logs(oc.HEARTBEAT_NAME).read_text(encoding="utf-8"))


class TestRefusesWithoutCredential(_Root):
    """The deliverable while F-46 is open."""

    def test_tick_refuses_typed_and_does_not_raise(self):
        self.assertFalse(self.creds_path.exists(), "fixture must have NO credential")
        rec = oc.tick(self.paths, self.scopes, self.creds_path)
        self.assertEqual(rec["state"], "REFUSED")
        self.assertEqual(rec["kind"], "NO_CREDENTIALS")
        self.assertFalse(rec["ok"])

    def test_the_refusal_is_heartbeated_not_swallowed(self):
        oc.tick(self.paths, self.scopes, self.creds_path)
        hb = self.hb()
        self.assertEqual(hb["kind"], "NO_CREDENTIALS")
        self.assertEqual(hb["worker"], oc.WORKER)
        self.assertIn("last_run_epoch", hb, "the watchdog compares on last_run_epoch")

    def test_a_refusal_never_fabricates_an_offsite_copy(self):
        """The whole scar class: a green-looking artifact over nothing."""
        rec = oc.tick(self.paths, self.scopes, self.creds_path)
        self.assertFalse(rec["offsite_copy_exists"])
        self.assertIsNone(rec["success_age_s"])
        self.assertNotIn("last_success_epoch", rec)

    def test_refusal_reaches_the_network_never(self):
        """A transport that would explode if constructed. It must not be."""
        def boom():
            raise AssertionError("a credential-less tick must not build a transport")
        rec = oc.tick(self.paths, self.scopes, self.creds_path, transport_factory=boom)
        self.assertEqual(rec["kind"], "NO_CREDENTIALS")

    def test_cli_exits_2_and_names_the_kind(self):
        rc = oc.main(["--root", str(self.root), "--once", "--source", str(self.src)])
        self.assertEqual(rc, 2, "a typed refusal is rc=2, never rc=0")
        self.assertEqual(self.hb()["kind"], "NO_CREDENTIALS")

    def test_malformed_credential_is_a_different_kind(self):
        """BAD_CREDENTIALS != NO_CREDENTIALS: the operator's next move differs."""
        self.creds_path.write_text(json.dumps({"account_id": "x"}), encoding="utf-8")
        rec = oc.tick(self.paths, self.scopes, self.creds_path)
        self.assertEqual(rec["kind"], "BAD_CREDENTIALS")
        # The detail names the missing FIELDS and no value.
        self.assertIn("missing field", rec["detail"])
        self.assertNotIn("secret", rec["detail"].lower().replace("secret_access_key", ""))


class TestCredentialFence(_Root):
    r"""D:\R2Cloner is never touched, and the refusal happens before the filesystem."""

    def test_plaintext_key_store_is_refused_by_path_alone(self):
        rec = oc.tick(self.paths, self.scopes, Path(r"D:\R2Cloner\rclone.conf"))
        self.assertEqual(rec["kind"], "FORBIDDEN_CREDENTIAL_PATH")

    def test_no_secret_value_appears_in_the_heartbeat(self):
        oc.tick(self.paths, self.scopes, self.creds_path,
                credentials_override=_fake_creds(), transport_factory=r2.MemoryTransport)
        raw = self.paths.logs(oc.HEARTBEAT_NAME).read_text(encoding="utf-8")
        self.assertNotIn(FAKE, raw, "only a last-4 fingerprint may be emitted")
        self.assertIn("redacted", raw)


class TestScopeDeclaration(_Root):

    def test_missing_scope_file_refuses_rather_than_guessing_a_tree(self):
        with self.assertRaises(bk.BackupRefusal) as cm:
            oc.load_scopes(self.paths.config(oc.SCOPES_NAME))
        self.assertEqual(cm.exception.kind, "NO_SCOPES")

    def test_scope_file_round_trips(self):
        p = self.paths.config(oc.SCOPES_NAME)
        p.write_text(json.dumps({"scopes": [{"name": "src", "source": str(self.src)}]}),
                     encoding="utf-8")
        got = oc.load_scopes(p)
        self.assertEqual(got[0]["name"], "src")
        self.assertEqual(got[0]["source"], str(self.src))
        self.assertIn("__pycache__", got[0]["excludes"])

    def test_a_scope_name_that_traverses_is_refused(self):
        p = self.paths.config(oc.SCOPES_NAME)
        p.write_text(json.dumps({"scopes": [{"name": "../escape", "source": str(self.src)}]}),
                     encoding="utf-8")
        with self.assertRaises(bk.BackupRefusal) as cm:
            oc.load_scopes(p)
        self.assertEqual(cm.exception.kind, "UNSAFE_MANIFEST_KEY")

    def test_malformed_scopes_json_is_BAD_SCOPES(self):
        p = self.paths.config(oc.SCOPES_NAME)
        p.write_text("{not json", encoding="utf-8")
        with self.assertRaises(bk.BackupRefusal) as cm:
            oc.load_scopes(p)
        self.assertEqual(cm.exception.kind, "BAD_SCOPES")

    def test_empty_scopes_list_is_BAD_SCOPES_not_a_silent_no_op(self):
        """Prose: REFUSES rather than inventing a default source tree.
        An empty list is the same as guessing nothing-to-do = VERIFIED."""
        p = self.paths.config(oc.SCOPES_NAME)
        p.write_text(json.dumps({"scopes": []}), encoding="utf-8")
        with self.assertRaises(bk.BackupRefusal) as cm:
            oc.load_scopes(p)
        self.assertEqual(cm.exception.kind, "BAD_SCOPES")

    def test_scope_missing_source_is_BAD_SCOPES(self):
        p = self.paths.config(oc.SCOPES_NAME)
        p.write_text(json.dumps({"scopes": [{"name": "src"}]}), encoding="utf-8")
        with self.assertRaises(bk.BackupRefusal) as cm:
            oc.load_scopes(p)
        self.assertEqual(cm.exception.kind, "BAD_SCOPES")

    def test_scope_missing_name_is_BAD_SCOPES(self):
        p = self.paths.config(oc.SCOPES_NAME)
        p.write_text(json.dumps({"scopes": [{"source": str(self.src)}]}),
                     encoding="utf-8")
        with self.assertRaises(bk.BackupRefusal) as cm:
            oc.load_scopes(p)
        self.assertEqual(cm.exception.kind, "BAD_SCOPES")

    def test_excludes_string_is_BAD_SCOPES_not_characters(self):
        p = self.paths.config(oc.SCOPES_NAME)
        p.write_text(json.dumps({"scopes": [{"name": "src",
                                             "source": str(self.src),
                                             "excludes": "git"}]}),
                     encoding="utf-8")
        with self.assertRaises(bk.BackupRefusal) as cm:
            oc.load_scopes(p)
        self.assertEqual(cm.exception.kind, "BAD_SCOPES")
        self.assertIn("excludes", cm.exception.detail)


class TestFullPushOffline(_Root):
    """The same tick(), with the bucket in memory. Nothing here can reach a socket."""

    def run_tick(self):
        return oc.tick(self.paths, self.scopes, self.creds_path,
                       transport_factory=r2.MemoryTransport,
                       credentials_override=_fake_creds())

    def test_push_reads_back_and_rehashes_every_object(self):
        rec = self.run_tick()
        self.assertTrue(rec["ok"], rec)
        row = rec["scopes"][0]
        self.assertEqual(row["state"], "PUSHED")
        self.assertEqual(row["files_pushed"], 2)
        self.assertEqual(row["readback_verified"], row["files_pushed"],
                         "an upload nobody read back is a claim, not a backup")
        self.assertEqual(len(row["manifest_seal_sha256"]), 64)

    def test_receipt_lands_on_this_machine_too(self):
        rec = self.run_tick()
        p = Path(rec["scopes"][0]["receipt"])
        self.assertTrue(p.is_file())
        receipt = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(receipt["kind"], "R2_PUSH_OK")
        bk.check_seal(receipt)          # REFUSES if the artifact was altered
        self.assertEqual(receipt["target"]["secret_access_key"],
                         "<redacted — never emitted>")

    def test_readback_scratch_is_staged_never_deleted(self):
        rec = self.run_tick()
        scratch = Path(rec["scopes"][0]["readback_scratch"])
        self.assertTrue(scratch.is_dir(), "read-back copy must survive for inspection")
        self.assertIn(oc.READBACK_STAGE, scratch.parts,
                      "it is born in the staging dir; Keith deletes at his leisure")
        self.assertTrue((scratch / "a.txt").is_file())

    def test_success_sets_the_protection_clock(self):
        rec = self.run_tick()
        self.assertTrue(rec["offsite_copy_exists"])
        self.assertIsNotNone(rec["success_age_s"])
        self.assertEqual(rec["last_success_scopes"], ["src"])

    def test_a_later_refusal_remembers_the_last_real_success(self):
        """Liveness and protection are different questions; both must survive."""
        first = self.run_tick()
        second = oc.tick(self.paths, self.scopes, self.creds_path)   # no credential now
        self.assertEqual(second["state"], "REFUSED")
        self.assertEqual(second["last_success_epoch"], first["last_success_epoch"])
        self.assertTrue(second["offsite_copy_exists"],
                        "a copy that exists off-machine does not stop existing "
                        "because tonight's tick refused")

    def test_prefix_is_dated_so_a_push_never_overwrites_its_predecessor(self):
        rec = self.run_tick()
        prefix = rec["scopes"][0]["prefix"]
        self.assertTrue(prefix.startswith("src/"))
        self.assertRegex(prefix, r"^src/\d{8}T\d{6}$")

    def test_secrets_in_scope_refuse_the_push_before_a_byte_moves(self):
        """Off-machine storage inherits every exposure in scope."""
        (self.src / "api_token.txt").write_text("not-a-real-token\n", encoding="utf-8")
        rec = self.run_tick()
        self.assertFalse(rec["ok"])
        row = rec["scopes"][0]
        self.assertEqual(row["kind"], "SECRETS_IN_SCOPE")
        self.assertFalse(rec["offsite_copy_exists"])

    def test_one_scope_refusing_does_not_cancel_the_others(self):
        missing = self.tmp / "not_there"
        self.scopes.append({"name": "missing", "source": str(missing), "excludes": ()})
        rec = self.run_tick()
        by = {r["scope"]: r for r in rec["scopes"]}
        self.assertEqual(by["src"]["state"], "PUSHED")
        self.assertEqual(by["missing"]["kind"], "SOURCE_NOT_DIR")
        self.assertEqual(rec["state"], "PARTIAL")
        self.assertFalse(rec["ok"])


class TestPauseIsHonored(_Root):

    def _flag(self, body: str) -> None:
        p = self.paths.role("state", "control", "PAUSE.flag")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")

    def test_paused_tick_does_no_work_but_still_beats(self):
        self._flag(json.dumps({"state": "PAUSED"}))
        rec = oc.tick(self.paths, self.scopes, self.creds_path)
        self.assertEqual(rec["state"], "PAUSED")
        self.assertTrue(rec["ok"])
        self.assertIn("last_run_epoch", self.hb())

    def test_running_flag_lets_the_tick_proceed(self):
        self._flag(json.dumps({"state": "RUNNING"}))
        rec = oc.tick(self.paths, self.scopes, self.creds_path)
        self.assertEqual(rec["state"], "REFUSED")     # proceeds, then refuses on the credential

    def test_unreadable_flag_is_fail_closed(self):
        self._flag("{ this is not json")
        self.assertTrue(oc.paused(self.paths))

    def test_json_array_flag_is_fail_closed_paused(self):
        self._flag("[]")
        self.assertTrue(oc.paused(self.paths))

    def test_json_true_flag_is_fail_closed_paused(self):
        self._flag("true")
        self.assertTrue(oc.paused(self.paths))

    def test_json_null_flag_is_fail_closed_paused(self):
        self._flag("null")
        self.assertTrue(oc.paused(self.paths))

    def test_heartbeat_array_is_empty_object_not_a_list(self):
        hb = self.paths.logs(oc.HEARTBEAT_NAME)
        hb.parent.mkdir(parents=True, exist_ok=True)
        hb.write_text("[]", encoding="utf-8")
        got = oc.read_heartbeat(hb)
        self.assertEqual(got, {})
        rec = oc.tick(self.paths, self.scopes, self.creds_path, force=True)
        self.assertIn(rec["state"], ("REFUSED", "PARTIAL", "VERIFIED"))
        self.assertIsInstance(self.hb(), dict)

    def test_write_heartbeat_none_is_BAD_HEARTBEAT(self):
        with self.assertRaises(bk.BackupRefusal) as cm:
            oc.write_heartbeat(self.paths.logs(oc.HEARTBEAT_NAME), None)
        self.assertEqual(cm.exception.kind, "BAD_HEARTBEAT")


class TestSelfcheckDrivesTheRealPath(_Root):

    def test_selfcheck_pushes_to_a_memory_bucket_with_a_fake_credential(self):
        rec = oc.selfcheck(self.paths, self.scopes)
        self.assertTrue(rec["ok"], rec)
        self.assertEqual(rec["scopes"][0]["readback_verified"], 2)
        raw = self.paths.logs(oc.HEARTBEAT_NAME).read_text(encoding="utf-8")
        self.assertNotIn(r2.SELFCHECK_ID, raw)

    def test_cli_selfcheck_exits_zero(self):
        rc = oc.main(["--root", str(self.root), "--selfcheck", "--source", str(self.src)])
        self.assertEqual(rc, 0)


class TestScheduling(_Root):

    def test_plan_task_argv_is_daily_windowless_and_points_at_this_file(self):
        argv = oc.plan_task_argv(self.root, "02:30")
        self.assertEqual(argv[:4], ["schtasks", "/create", "/tn", oc.TASK_NAME])
        joined = " ".join(argv)
        self.assertIn("/sc daily", joined)
        self.assertIn("/st 02:30", joined)
        self.assertIn("cosmos_offsite_clock.py", joined)
        self.assertIn("--once", joined)
        self.assertNotIn("/rl highest", joined, "the push needs no elevation")

    @unittest.skipUnless(os.name == "nt", "pythonw is a Windows binary")
    def test_task_runs_pythonw_so_no_console_flashes_nightly(self):
        self.assertIn("pythonw", " ".join(oc.plan_task_argv(self.root)).lower())

    def test_plan_task_registers_nothing(self):
        """--plan-task must be safe to run: it prints, it does not schedule."""
        calls = []
        real = oc.subprocess.run
        oc.subprocess.run = lambda *a, **k: calls.append(a) or real(*a, **k)
        try:
            rc = oc.main(["--root", str(self.root), "--plan-task"])
        finally:
            oc.subprocess.run = real
        self.assertEqual(rc, 0)
        self.assertEqual(calls, [])

    def test_stale_threshold_matches_a_daily_cadence(self):
        self.assertGreater(oc.STALE_S, 24 * 3600, "daily + slack, or it cries wolf")
        self.assertLess(oc.STALE_S, 48 * 3600, "two silent days is not 'alive'")

    def test_heartbeat_name_is_discoverable_by_the_health_watchdog(self):
        """discover_unwatched globs *heartbeat*.json in the logs role."""
        self.assertIn("heartbeat", oc.HEARTBEAT_NAME)
        self.assertTrue(oc.HEARTBEAT_NAME.endswith(".json"))


class TestModuleResolutionInAFreshProcess(_Root):
    r"""The shadow that only a real run exposes.

    `cosmos/` and `builds/backup/` both hold a module named `cosmos_backup`, and they
    are DIFFERENT modules. An earlier draft of the clock put `cosmos/` on sys.path to
    reach the resolver; every in-process test still passed, because a test imports the
    builds/backup one first and sys.modules then hides the collision. The live command
    died at import:

        ImportError: cannot import name 'BackupRefusal' from 'cosmos_backup'
                     (V:\A\Ai\COSMOS\cosmos\cosmos_backup.py)

    So these run the CLI in a SUBPROCESS. An in-process assertion cannot see an
    import-time failure that in-process imports have already papered over.
    """

    def _run(self, *args) -> tuple[int, str, str]:
        p = subprocess.run([sys.executable, str(Path(oc.__file__).resolve()), *args],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=180)
        return p.returncode, p.stdout, p.stderr

    def test_the_clock_binds_the_builds_backup_backup_module(self):
        self.assertEqual(Path(oc.cb.__file__).resolve().parent,
                         Path(__file__).resolve().parent,
                         "the clock must bind builds/backup/cosmos_backup.py, not cosmos/")

    def test_cli_imports_cleanly_in_a_fresh_interpreter(self):
        rc, out, err = self._run("--root", str(self.root), "--plan-task")
        self.assertEqual(rc, 0, f"import-time failure: {err[-600:]}")
        self.assertEqual(json.loads(out)["task"], oc.TASK_NAME)

    def test_cli_selfcheck_completes_a_real_push_in_a_fresh_interpreter(self):
        """End to end in a clean process: scope -> push -> read-back -> heartbeat."""
        rc, out, err = self._run("--root", str(self.root), "--selfcheck",
                                 "--source", str(self.src))
        self.assertEqual(rc, 0, err[-600:])
        rec = json.loads(out)
        self.assertEqual(rec["scopes"][0]["readback_verified"], 2)
        self.assertTrue(Path(rec["heartbeat_path"]).is_file())

    def test_cli_refusal_exit_code_in_a_fresh_interpreter(self):
        rc, out, err = self._run("--root", str(self.root), "--once",
                                 "--source", str(self.src))
        self.assertEqual(rc, 2, err[-600:])
        self.assertEqual(json.loads(out)["kind"], "NO_CREDENTIALS")


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
        self.assertEqual(oc.main(["--root", str(plain), "--once"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
