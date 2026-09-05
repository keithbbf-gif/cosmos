#!/usr/bin/env python3
"""Real tests for cosmos_backup_mounts.py (F-48).

  py -3.14 builds/backup/test_backup_mounts.py

Bite first: the new checks FAIL against the staged pre-change cosmos_backup.py
(GDXTarget/ODXTarget raise NotImplementedError with no kind). Then they PASS
against the mounts module. Injected FakeProbe — nothing in this suite can
touch a real DriveFS/OneDrive/ES.3 mount. No key material is read.
"""
from __future__ import annotations

import importlib.util
import inspect
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cosmos_backup as cb
import cosmos_backup_mounts as m
from cosmos_backup import BackupRefusal

KEY = b"test-hmac-key-not-a-real-secret"
OLD = (HERE.parents[1] / "_delme" / "predispose_cosmos_backup_f48_20260831T055254Z"
       / "cosmos_backup.py")
BITE_STUBS = HERE / "_bite_f48_stubs.json"


def _src(tmp: Path) -> Path:
    src = tmp / "src"
    (src / "nested").mkdir(parents=True)
    (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
    (src / "nested" / "b.bin").write_bytes(bytes(range(256)) * 4)
    return src


def _probe(src: Path, dest: Path, src_vol="vol:SRC", dest_vol="vol:GDX") -> m.FakeProbe:
    return m.FakeProbe(volumes={
        str(src): src_vol,
        str(src.resolve()): src_vol,
        str(dest): dest_vol,
        str(dest.resolve()) if dest.exists() else str(dest): dest_vol,
    })


class MountTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_mount_test_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.src = _src(self.tmp)
        self.dest = self.tmp / "gdx"
        self.dest.mkdir()
        self.cfg = self.tmp / "backup_targets.json"

    def write_cfg(self, **targets):
        self.cfg.write_text(json.dumps({"schema": m.SCHEMA, "targets": targets}),
                            encoding="utf-8")


class TestConfigRefusals(MountTestBase):
    def test_missing_config_is_NO_CONFIG(self):
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("gdx", config_path=self.tmp / "nope.json")
        self.assertEqual(ctx.exception.kind, "NO_CONFIG")

    def test_no_dest_no_config_is_NO_CONFIG(self):
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("gdx")
        self.assertEqual(ctx.exception.kind, "NO_CONFIG")

    def test_empty_targets_row_is_NO_DEST(self):
        self.write_cfg(gdx={"dest": ""})
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("gdx", config_path=self.cfg)
        self.assertEqual(ctx.exception.kind, "NO_DEST")

    def test_relative_dest_is_BAD_CONFIG(self):
        self.write_cfg(gdx={"dest": "relative/out"})
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("gdx", config_path=self.cfg)
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")

    def test_unknown_kind_is_BAD_KIND(self):
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("s3")
        self.assertEqual(ctx.exception.kind, "BAD_KIND")

    def test_malformed_json_is_BAD_CONFIG(self):
        self.cfg.write_text("{not json", encoding="utf-8")
        with self.assertRaises(BackupRefusal) as ctx:
            m.load_config(self.cfg)
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")


class TestMountAndIdentity(MountTestBase):
    def test_missing_dir_is_DRIVE_NOT_MOUNTED(self):
        gone = self.tmp / "not-mounted"
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("gdx", dest=gone)
        self.assertEqual(ctx.exception.kind, "DRIVE_NOT_MOUNTED")

    def test_es3_unmounted_names_the_drive(self):
        gone = self.tmp / "no-es3"
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("es3", dest=gone)
        self.assertEqual(ctx.exception.kind, "DRIVE_NOT_MOUNTED")
        self.assertIn("ST3000NM0033", ctx.exception.detail)

    def test_r2cloner_dest_is_FORBIDDEN_DEST(self):
        with self.assertRaises(BackupRefusal) as ctx:
            m.guard_dest(Path(r"D:\R2Cloner\backup"))
        self.assertEqual(ctx.exception.kind, "FORBIDDEN_DEST")

    def test_same_volume_refuses(self):
        probe = _probe(self.src, self.dest, "vol:SAME", "vol:SAME")
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("gdx", dest=self.dest, probe=probe, source=self.src)
        self.assertEqual(ctx.exception.kind, "SAME_VOLUME")

    def test_different_volume_binds(self):
        probe = _probe(self.src, self.dest)
        got = m.bind("gdx", dest=self.dest, probe=probe, source=self.src)
        self.assertEqual(got, self.dest)

    def test_volume_serial_mismatch_is_IDENTITY_MISMATCH(self):
        probe = _probe(self.src, self.dest, dest_vol="vol:AAAA1111")
        self.write_cfg(gdx={"dest": str(self.dest),
                            "identity": {"kind": "volume_serial",
                                         "value": "vol:BBBB2222"}})
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("gdx", config_path=self.cfg, probe=probe)
        self.assertEqual(ctx.exception.kind, "IDENTITY_MISMATCH")

    def test_volume_serial_match_binds(self):
        probe = _probe(self.src, self.dest, dest_vol="vol:AAAA1111")
        self.write_cfg(gdx={"dest": str(self.dest),
                            "identity": {"kind": "volume_serial",
                                         "value": "vol:AAAA1111"}})
        self.assertEqual(m.bind("gdx", config_path=self.cfg, probe=probe),
                         self.dest)

    def test_fakeprobe_unknown_volume_is_DRIVE_NOT_MOUNTED(self):
        probe = m.FakeProbe(volumes={})
        with self.assertRaises(BackupRefusal) as ctx:
            probe.volume_id(self.dest)
        self.assertEqual(ctx.exception.kind, "DRIVE_NOT_MOUNTED")

    def test_label_mismatch(self):
        probe = _probe(self.src, self.dest)
        probe.labels[str(self.dest)] = "Other"
        self.write_cfg(gdx={"dest": str(self.dest),
                            "identity": {"kind": "volume_label", "value": "Google Drive"}})
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("gdx", config_path=self.cfg, probe=probe)
        self.assertEqual(ctx.exception.kind, "IDENTITY_MISMATCH")

    def test_label_match(self):
        probe = _probe(self.src, self.dest)
        probe.labels[str(self.dest)] = "Google Drive"
        self.write_cfg(gdx={"dest": str(self.dest),
                            "identity": {"kind": "volume_label", "value": "Google Drive"}})
        self.assertEqual(m.bind("gdx", config_path=self.cfg, probe=probe), self.dest)

    def test_model_unmeasured_without_probe_value(self):
        probe = _probe(self.src, self.dest)
        self.write_cfg(es3={"dest": str(self.dest),
                            "identity": {"kind": "model", "value": m.ES3_MODEL}})
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("es3", config_path=self.cfg, probe=probe)
        self.assertEqual(ctx.exception.kind, "IDENTITY_UNMEASURED")

    def test_model_match_when_probe_supplies_it(self):
        probe = _probe(self.src, self.dest, dest_vol="vol:ES3")
        probe.models[str(self.dest)] = m.ES3_MODEL
        self.write_cfg(es3={"dest": str(self.dest),
                            "identity": {"kind": "model", "value": m.ES3_MODEL}})
        self.assertEqual(m.bind("es3", config_path=self.cfg, probe=probe), self.dest)

    def test_sentinel_missing_is_IDENTITY_MISSING(self):
        probe = _probe(self.src, self.dest)
        self.write_cfg(odx={"dest": str(self.dest),
                            "identity": {"kind": "sentinel",
                                         "expect": {"kind": "odx"}}})
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("odx", config_path=self.cfg, probe=probe)
        self.assertEqual(ctx.exception.kind, "IDENTITY_MISSING")

    def test_sentinel_content_is_identity(self):
        sent = self.dest / ".cosmos-backup-target.json"
        sent.write_text(json.dumps({"kind": "odx", "model": "OneDrive"}), encoding="utf-8")
        probe = _probe(self.src, self.dest, dest_vol="vol:ODX")
        self.write_cfg(odx={"dest": str(self.dest),
                            "identity": {"kind": "sentinel",
                                         "expect": {"kind": "odx"}}})
        self.assertEqual(m.bind("odx", config_path=self.cfg, probe=probe), self.dest)

    def test_unknown_identity_kind_is_BAD_CONFIG(self):
        """identity.kind must be one of the four; an unknown kind is not
        skipped. Existence of the dest dir is not identity."""
        probe = _probe(self.src, self.dest)
        self.write_cfg(gdx={"dest": str(self.dest),
                            "identity": {"kind": "mac_address", "value": "aa:bb"}})
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("gdx", config_path=self.cfg, probe=probe)
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")
        self.assertIn("mac_address", ctx.exception.detail)

    def test_model_mismatch_when_measured_is_IDENTITY_MISMATCH(self):
        """IDENTITY_UNMEASURED and match were pinned; a probe that DOES
        return a model, the wrong one, was not. Strip the mismatch raise
        and bind succeeds (existence as identity). Bite: round4."""
        probe = _probe(self.src, self.dest, dest_vol="vol:ES3")
        probe.models[str(self.dest)] = "WRONG-MODEL"
        self.write_cfg(es3={"dest": str(self.dest),
                            "identity": {"kind": "model", "value": m.ES3_MODEL}})
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("es3", config_path=self.cfg, probe=probe)
        self.assertEqual(ctx.exception.kind, "IDENTITY_MISMATCH")
        self.assertIn("WRONG-MODEL", ctx.exception.detail)

    def test_sentinel_field_mismatch_is_IDENTITY_MISMATCH(self):
        """A present sentinel with the wrong field is not IDENTITY_MISSING
        and is not a bind. Bite: stripped loop bound the dest."""
        sent = self.dest / ".cosmos-backup-target.json"
        sent.write_text(json.dumps({"kind": "gdx"}), encoding="utf-8")
        probe = _probe(self.src, self.dest, dest_vol="vol:ODX")
        self.write_cfg(odx={"dest": str(self.dest),
                            "identity": {"kind": "sentinel",
                                         "expect": {"kind": "odx"}}})
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("odx", config_path=self.cfg, probe=probe)
        self.assertEqual(ctx.exception.kind, "IDENTITY_MISMATCH")
        self.assertTrue(sent.is_file(), "refusal must not clobber the sentinel")

    def test_identity_not_object_is_BAD_CONFIG(self):
        probe = _probe(self.src, self.dest)
        self.write_cfg(gdx={"dest": str(self.dest),
                            "identity": "volume_serial"})
        with self.assertRaises(BackupRefusal) as ctx:
            m.bind("gdx", config_path=self.cfg, probe=probe)
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")
        self.assertIn("identity is not an object", ctx.exception.detail)

    def test_config_json_array_is_BAD_CONFIG(self):
        self.cfg.write_text("[]", encoding="utf-8")
        with self.assertRaises(BackupRefusal) as ctx:
            m.load_config(self.cfg)
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")
        self.assertIn("not a JSON object", ctx.exception.detail)

    def test_targets_list_is_BAD_CONFIG(self):
        self.cfg.write_text(json.dumps({"schema": m.SCHEMA, "targets": ["gdx"]}),
                            encoding="utf-8")
        with self.assertRaises(BackupRefusal) as ctx:
            m.load_config(self.cfg)
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")
        self.assertIn("targets", ctx.exception.detail)

    def test_spec_for_config_list_is_BAD_CONFIG(self):
        with self.assertRaises(BackupRefusal) as ctx:
            m.spec_for("gdx", [], None)
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")

    def test_spec_for_targets_str_is_BAD_CONFIG(self):
        with self.assertRaises(BackupRefusal) as ctx:
            m.spec_for("gdx", {"targets": "gdx"}, None)
        self.assertEqual(ctx.exception.kind, "BAD_CONFIG")

    def test_round4_bite_records_pre_fix(self):
        bite = HERE / "_bite_unpinned_round4.json"
        self.assertTrue(bite.is_file(), "bite must be recorded before belief")
        rec = json.loads(bite.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertTrue(rec["model_mismatch_old_bound"])
        self.assertIsNone(rec["model_mismatch_old_kind"])
        self.assertTrue(rec["sentinel_mismatch_old_bound"])
        self.assertEqual(rec["ident_not_obj_old_crash"], "AttributeError")
        self.assertEqual(rec["cfg_array_old_crash"], "AttributeError")
        self.assertEqual(rec["targets_list_old_crash"], "AttributeError")


class TestPushAndSecrets(MountTestBase):
    def test_push_roundtrip_rehashes(self):
        probe = _probe(self.src, self.dest)
        receipt = m.push(self.src, "gdx", dest=self.dest, probe=probe, key=KEY)
        self.assertEqual(receipt["kind"], "MOUNT_PUSH_OK")
        self.assertEqual(receipt["files_pushed"], 2)
        self.assertTrue(receipt["cloud"])
        set_dir = Path(receipt["set_dir"])
        cb.check_seal(json.loads((set_dir / m.RECEIPT_NAME).read_text(encoding="utf-8")), KEY)
        proof = json.loads(cb.do_rehearse(set_dir, self.tmp / "scratch", KEY).read_text(encoding="utf-8"))
        self.assertEqual(proof["kind"], "REHEARSAL_PASS")
        self.assertEqual(proof["files_restored"], 2)

    def test_secrets_in_scope_refuse_before_copy(self):
        (self.src / "api_token.txt").write_text("planted-not-a-real-key\n", encoding="utf-8")
        probe = _probe(self.src, self.dest)
        with self.assertRaises(BackupRefusal) as ctx:
            m.push(self.src, "odx", dest=self.dest, probe=probe)
        self.assertEqual(ctx.exception.kind, "SECRETS_IN_SCOPE")
        self.assertFalse(any(self.dest.iterdir()))  # dest still empty — nothing copied

    def test_never_deletes_existing_set(self):
        probe = _probe(self.src, self.dest)
        first = m.push(self.src, "gdx", dest=self.dest, probe=probe, key=KEY)
        second = m.push(self.src, "gdx", dest=self.dest, probe=probe, key=KEY)
        self.assertNotEqual(first["set_dir"], second["set_dir"])
        self.assertTrue(Path(first["set_dir"]).is_dir())
        self.assertTrue(Path(second["set_dir"]).is_dir())


class TestPreflightAndSelfcheck(MountTestBase):
    def test_preflight_without_config_is_BLOCKED(self):
        out = m.preflight(self.tmp / "missing.json", None)
        self.assertEqual(out["status"], "BLOCKED")
        self.assertEqual(out["adapter_implemented"], True)
        self.assertEqual(out["targets"]["gdx"]["state"], "NO_CONFIG")
        self.assertEqual(out["targets"]["es3"]["state"], "NO_CONFIG")

    def test_preflight_ready_when_dest_bound(self):
        self.write_cfg(gdx={"dest": str(self.dest)},
                       odx={"dest": str(self.dest)},
                       es3={"dest": str(self.dest)})
        probe = _probe(self.src, self.dest)
        out = m.preflight(self.cfg, self.src, probe=probe)
        self.assertEqual(out["status"], "READY")
        self.assertEqual(out["targets"]["gdx"]["state"], "READY")

    def test_selfcheck_emits_rehearsal_pass(self):
        scratch = self.tmp / "sc"
        scratch.mkdir()
        out = m.selfcheck(self.src, scratch, KEY)
        self.assertEqual(out["kind"], "MOUNT_PUSH_OK")
        self.assertEqual(out["rehearsal_kind"], "REHEARSAL_PASS")
        self.assertEqual(out["files_pushed"], 2)

    def test_cli_preflight_rc_2_when_blocked(self):
        err = io.StringIO()
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = m.main(["preflight", "--config", str(self.tmp / "nope.json")])
        self.assertEqual(rc, 2)
        body = json.loads(out.getvalue() or err.getvalue())
        self.assertTrue(body.get("refused") or body.get("status") == "BLOCKED")


class TestNoHardcodedDest(unittest.TestCase):
    def test_source_contains_no_drive_literal_dest(self):
        src = inspect.getsource(m)
        # Strip the docstring + the ES.3 constant comment; the CODE after the
        # module docstring must not invent X:\ or OneDrive paths.
        code = src.split('"""', 2)[-1]
        for banned in ("X:\\\\", "X:/", r"C:\\Users\\Papa\\OneDrive",
                       r"D:\\ODX", "My Drive"):
            self.assertNotIn(banned, code, f"code invents dest {banned!r}")
        self.assertIn("ST3000NM0033", src)  # named as identity, not a path

    def test_kinds_are_exactly_the_wishlist_three(self):
        self.assertEqual(m.KINDS, ("gdx", "odx", "es3"))
        self.assertEqual(m.CLOUD_KINDS, frozenset(("gdx", "odx")))


class TestAdaptersWired(unittest.TestCase):
    """The seam in cosmos_backup.py: gdx/odx/es3 no longer NotImplementedError."""

    def test_adapters_include_es3(self):
        self.assertEqual(sorted(cb.ADAPTERS), ["es3", "gdx", "local", "odx", "r2"])

    def test_gdx_odx_es3_without_dest_are_typed_NO_CONFIG(self):
        for name in ("gdx", "odx", "es3"):
            with self.assertRaises(BackupRefusal) as ctx:
                cb.ADAPTERS[name]()
            self.assertEqual(ctx.exception.kind, "NO_CONFIG", name)

    def test_r2_seam_refuses_NO_CREDENTIALS_not_a_stub(self):
        # Same shape as gdx/odx/es3: a missing operator file is a typed
        # refusal, never NotImplementedError. The real adapter is still
        # cosmos_backup_r2.R2Target; this just stops hiding it behind a stub.
        with self.assertRaises(BackupRefusal) as ctx:
            cb.ADAPTERS["r2"]()
        self.assertEqual(ctx.exception.kind, "NO_CREDENTIALS")


class TestBiteOldStubs(unittest.TestCase):
    """Prove the new checks FAIL against the pre-change file. Required before belief."""

    def test_staged_old_gdx_raises_NotImplementedError(self):
        self.assertTrue(OLD.is_file(), f"missing staged predecessor {OLD}")
        spec = importlib.util.spec_from_file_location("cosmos_backup_f48_old", OLD)
        old = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(old)
        with self.assertRaises(NotImplementedError):
            old.ADAPTERS["gdx"]()
        with self.assertRaises(NotImplementedError):
            old.ADAPTERS["odx"]()
        self.assertNotIn("es3", old.ADAPTERS)

    def test_saved_bite_artifact_matches_the_staged_old(self):
        self.assertTrue(BITE_STUBS.is_file())
        doc = json.loads(BITE_STUBS.read_text(encoding="utf-8"))
        kinds = {b["name"]: b for b in doc["bites"]}
        self.assertEqual(kinds["gdx"]["raised"], "NotImplementedError")
        self.assertIsNone(kinds["gdx"]["kind"])
        self.assertEqual(kinds["odx"]["raised"], "NotImplementedError")


if __name__ == "__main__":
    unittest.main(verbosity=2)
