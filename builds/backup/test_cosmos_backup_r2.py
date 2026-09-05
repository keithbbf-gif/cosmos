#!/usr/bin/env python3
"""Real tests for cosmos_backup_r2.py — run with: py -3.14 test_cosmos_backup_r2.py -v

Every expectation here was MEASURED before it was written down:

  * the SigV4 constants are AWS's own published `aws-sig-v4-test-suite` vectors
    (`get-vanilla`, and the documented signing-key derivation), run through this
    signer and observed to match — not recalled. A first draft of this file
    carried a canonical-request hash from memory; it was WRONG, the measurement
    caught it, and only the observed values survive here.
  * every network test runs on `MemoryTransport`. Nothing in this suite can open
    a socket, so a green run never depends on reachability.
  * no credential, real or otherwise, is read from disk. The fixtures are
    obviously-fake literals and the suite asserts the secret cannot escape.
"""
from __future__ import annotations

import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
from pathlib import Path

import cosmos_backup as cb
import cosmos_backup_r2 as r2

# AWS sig-v4-test-suite public example credentials. Not a secret: they are printed
# in AWS's own documentation precisely so signers can be checked against them.
VEC_KEY_ID = "AKIDEXAMPLE"
VEC_SECRET = "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY"
VEC_AMZDATE = "20150830T123600Z"
VEC_GET_VANILLA_SIG = "5fa00fa31553b73ebf1942676e86291e8372ff2a2260956d9b8aae1d763fbf31"
VEC_SIGNING_KEY_IAM = "c4afb1cc5771d871763a393e44b703571b55cc28424d1a5e86da6ed3c154a4b9"

SECRET_SENTINEL = "SECRET-VALUE-THAT-MUST-NEVER-BE-RENDERED"
HMAC_KEY = b"test-hmac-key-not-a-real-secret"


def fake_creds(secret: str = SECRET_SENTINEL) -> r2.R2Credentials:
    return r2.R2Credentials("acct1234", "AKIAFAKE0001", secret, "cosmos-bucket")


class R2TestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_r2_test_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)   # test scratch only — never tree files
        self.src = self.tmp / "src"
        (self.src / "nested").mkdir(parents=True)
        (self.src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        (self.src / "nested" / "b.bin").write_bytes(bytes(range(256)) * 8)
        self.scratch = self.tmp / "readback"

    def push_ok(self, prefix="cosmos"):
        tp = r2.MemoryTransport()
        target = r2.R2Target(fake_creds(), prefix, tp)
        receipt = r2.push(self.src, target, key=HMAC_KEY, scratch=self.scratch)
        return tp, target, receipt


# ------------------------------------------------------------------ SigV4

class TestSigV4Vectors(unittest.TestCase):
    """The signer against AWS's published vectors. If these drift, R2 rejects every
    request with 403 and the offsite backup silently is not one."""

    def test_get_vanilla_signature_matches_published_vector(self):
        creds = r2.R2Credentials("acct", VEC_KEY_ID, VEC_SECRET, "b",
                                 region="us-east-1", service="service")
        canonical, signed = r2.canonical_request(
            "GET", "/", {"host": "example.amazonaws.com", "x-amz-date": VEC_AMZDATE},
            r2.EMPTY_SHA256)
        self.assertEqual(signed, "host;x-amz-date")
        self.assertEqual(canonical,
                         "GET\n/\n\nhost:example.amazonaws.com\n"
                         f"x-amz-date:{VEC_AMZDATE}\n\nhost;x-amz-date\n{r2.EMPTY_SHA256}")
        sig, scope = r2.sign_request(creds, canonical, VEC_AMZDATE)
        self.assertEqual(scope, "20150830/us-east-1/service/aws4_request")
        self.assertEqual(sig, VEC_GET_VANILLA_SIG)

    def test_signing_key_derivation_matches_documented_vector(self):
        creds = r2.R2Credentials("acct", VEC_KEY_ID, VEC_SECRET, "b",
                                 region="us-east-1", service="iam")
        # sign("") exposes the derived key through one more HMAC; derive it the
        # documented way and compare the two chains agree end to end.
        import hashlib
        import hmac as _h
        k = ("AWS4" + VEC_SECRET).encode()
        for part in ("20150830", "us-east-1", "iam", "aws4_request"):
            k = _h.new(k, part.encode(), hashlib.sha256).digest()
        self.assertEqual(k.hex(), VEC_SIGNING_KEY_IAM)
        self.assertEqual(creds.sign("x", "20150830"),
                         _h.new(k, b"x", hashlib.sha256).hexdigest())

    def test_r2_defaults_are_auto_region_s3_service(self):
        c = fake_creds()
        self.assertEqual((c.region, c.service), ("auto", "s3"))
        self.assertEqual(c.endpoint, "https://acct1234.r2.cloudflarestorage.com")

    def test_put_payload_hash_is_the_manifest_hash(self):
        """The manifest's per-file sha256 IS x-amz-content-sha256 — one hash, computed
        once, serving both the backup proof and the request signature."""
        m = cb.build_manifest(self.tmp_src())
        tp = r2.MemoryTransport()
        seen = {}

        class Capture(r2.MemoryTransport):
            def request(self, method, url, headers, body=None):
                seen[url.rsplit("/", 1)[-1]] = headers.get("x-amz-content-sha256")
                return super().request(method, url, headers, body)

        tp = Capture()
        target = r2.R2Target(fake_creds(), "p", tp)
        target.store("a.txt", self.tmp_src() / "a.txt")
        self.assertEqual(seen["a.txt"], m["files"]["a.txt"]["sha256"])

    def tmp_src(self):
        d = Path(tempfile.mkdtemp(prefix="cosmos_r2_hash_"))
        self.addCleanup(shutil.rmtree, d, True)
        (d / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        return d


# ------------------------------------------------------------------ key safety

class TestSafeRel(unittest.TestCase):
    GOOD = ("a.txt", "nested/b.bin", "x/y/z.md")
    BAD = ("", "/abs.txt", "../escape.txt", "a/../../b", "C:/win.txt", "\\\\srv\\share")

    def test_agrees_with_cosmos_backup_child(self):
        """Two containment checks that drift are worse than one. This pins them together."""
        root = Path(tempfile.mkdtemp(prefix="cosmos_r2_key_"))
        self.addCleanup(shutil.rmtree, root, True)
        for rel in self.GOOD:
            r2.safe_rel(rel)
            cb._child(root, rel)
        for rel in self.BAD:
            with self.subTest(rel=rel):
                with self.assertRaises(cb.BackupRefusal) as a:
                    r2.safe_rel(rel)
                self.assertEqual(a.exception.kind, "UNSAFE_MANIFEST_KEY")
                with self.assertRaises(cb.BackupRefusal):
                    cb._child(root, rel)

    def test_object_key_is_prefixed_and_posix(self):
        t = r2.R2Target(fake_creds(), "cosmos/tree", r2.MemoryTransport())
        self.assertEqual(t.key_for("nested\\b.bin"), "cosmos/tree/nested/b.bin")


# ------------------------------------------------------------------ credentials

class TestCredentialFence(unittest.TestCase):
    def test_plaintext_key_store_is_refused_without_being_touched(self):
        for p in (r"D:\R2Cloner\rclone.conf", "d:/r2cloner/anything.json",
                  r"D:\r2cloner"):
            with self.subTest(p=p):
                with self.assertRaises(cb.BackupRefusal) as a:
                    r2.load_credentials(Path(p))
                self.assertEqual(a.exception.kind, "FORBIDDEN_CREDENTIAL_PATH")

    def test_missing_file_is_typed_not_a_crash(self):
        d = Path(tempfile.mkdtemp(prefix="cosmos_r2_cred_"))
        self.addCleanup(shutil.rmtree, d, True)
        with self.assertRaises(cb.BackupRefusal) as a:
            r2.load_credentials(d / "r2_credentials.json")
        self.assertEqual(a.exception.kind, "NO_CREDENTIALS")

    def test_malformed_and_incomplete_are_named_by_field_not_by_value(self):
        d = Path(tempfile.mkdtemp(prefix="cosmos_r2_cred_"))
        self.addCleanup(shutil.rmtree, d, True)
        bad = d / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        with self.assertRaises(cb.BackupRefusal) as a:
            r2.load_credentials(bad)
        self.assertEqual(a.exception.kind, "BAD_CREDENTIALS")

        partial = d / "partial.json"
        partial.write_text(json.dumps({"account_id": "a", "secret_access_key": SECRET_SENTINEL}),
                           encoding="utf-8")
        with self.assertRaises(cb.BackupRefusal) as a:
            r2.load_credentials(partial)
        self.assertEqual(a.exception.kind, "BAD_CREDENTIALS")
        self.assertIn("access_key_id", a.exception.detail)
        self.assertNotIn(SECRET_SENTINEL, str(a.exception))

    def test_valid_credential_loads_and_still_hides_the_secret(self):
        d = Path(tempfile.mkdtemp(prefix="cosmos_r2_cred_"))
        self.addCleanup(shutil.rmtree, d, True)
        p = d / "r2_credentials.json"
        p.write_text(json.dumps({"account_id": "acct1234", "access_key_id": "AKIAFAKE0001",
                                 "secret_access_key": SECRET_SENTINEL,
                                 "bucket": "cosmos-bucket"}), encoding="utf-8")
        c = r2.load_credentials(p)
        self.assertEqual(c.bucket, "cosmos-bucket")
        self.assertNotIn(SECRET_SENTINEL, repr(c) + str(c) + json.dumps(c.asdict()))

    def test_empty_field_is_BAD_CREDENTIALS_not_a_blank_secret(self):
        """Missing fields were pinned; a present-but-empty / whitespace
        secret was accepted (the constructor strip() would store ""). Bite:
        stripped empty-field check accepted keep='   '."""
        with self.assertRaises(cb.BackupRefusal) as a:
            r2.R2Credentials("acct1234", "AKIAFAKE0001", "   ", "cosmos-bucket")
        self.assertEqual(a.exception.kind, "BAD_CREDENTIALS")
        self.assertIn("secret_access_key", a.exception.detail)
        self.assertNotIn("   ", a.exception.detail)

    def test_json_true_is_BAD_CREDENTIALS_not_TypeError(self):
        d = Path(tempfile.mkdtemp(prefix="cosmos_r2_true_"))
        self.addCleanup(shutil.rmtree, d, True)
        p = d / "r2_credentials.json"
        p.write_text("true", encoding="utf-8")
        with self.assertRaises(cb.BackupRefusal) as a:
            r2.load_credentials(p)
        self.assertEqual(a.exception.kind, "BAD_CREDENTIALS")
        self.assertIn("not a JSON object", a.exception.detail)

    def test_round4_bite_records_pre_fix(self):
        bite = Path(__file__).resolve().parent / "_bite_unpinned_round4.json"
        self.assertTrue(bite.is_file(), "bite must be recorded before belief")
        rec = json.loads(bite.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertTrue(rec["empty_field_old_accepted"])
        self.assertIsNone(rec["empty_field_old_kind"])
        self.assertEqual(rec["cred_true_old_crash"], "TypeError")
        self.assertIsNone(rec["cred_true_old_kind"])


class TestSecretNeverEscapes(R2TestBase):
    """The one failure this module must never have: a key in an artifact or a log."""

    def test_secret_absent_from_every_emitted_surface(self):
        tp, target, receipt = self.push_ok()
        pf = r2.preflight(self.src, None)
        surfaces = [json.dumps(receipt, sort_keys=True), json.dumps(pf, sort_keys=True),
                    repr(target.creds), str(target.creds),
                    json.dumps(target.get_artifact(r2.RECEIPT_NAME), sort_keys=True)]
        for s in surfaces:
            self.assertNotIn(SECRET_SENTINEL, s)
        # the PUBLIC half survives as a fingerprint, so a receipt still names which
        # key wrote it (json.dumps escapes the ellipsis, hence ensure_ascii=False)
        self.assertIn("…0001", json.dumps(receipt, ensure_ascii=False))

    def test_http_error_body_cannot_carry_a_credential_out(self):
        class Echo(r2.MemoryTransport):
            def request(self, method, url, headers, body=None):
                return 500, {}, json.dumps(headers).encode()

        t = r2.R2Target(fake_creds(), "p", Echo())
        with self.assertRaises(cb.BackupRefusal) as a:
            t.store("a.txt", self.src / "a.txt")
        self.assertEqual(a.exception.kind, "R2_HTTP_ERROR")
        self.assertNotIn(SECRET_SENTINEL, str(a.exception))
        self.assertNotIn("Signature=", str(a.exception))

    def test_urlopen_OSError_is_R2_UNREACHABLE_not_an_untyped_crash(self):
        """UrllibTransport is the only path that can reach the network.
        An OSError (DNS / timeout / RST) must be R2_UNREACHABLE, never a
        raw exception a caller cannot branch on. Injected: urlopen never
        opens a socket."""
        import urllib.request
        real = urllib.request.urlopen

        def boom(*_a, **_k):
            raise OSError("simulated network down")

        urllib.request.urlopen = boom
        try:
            t = r2.UrllibTransport()
            with self.assertRaises(cb.BackupRefusal) as a:
                t.request("GET", "https://example.invalid/no-socket", {}, None)
            self.assertEqual(a.exception.kind, "R2_UNREACHABLE")
            self.assertNotIn(SECRET_SENTINEL, str(a.exception))
        finally:
            urllib.request.urlopen = real


# ------------------------------------------------------------------ secret scan

class TestSecretScan(unittest.TestCase):
    def test_key_material_in_scope_is_detected_by_path_alone(self):
        m = {"files": {k: {} for k in (
            "config/install_key.bin", "config/api_token.txt", "config/r2_credentials.json",
            "config/openai_api_key.txt", ".git/config", "certs/server.pem",
            "docs/README.md", "cosmos/cosmos_kernel.py", "notes/keynotes.txt")}}
        self.assertEqual(r2.scan_secrets(m), [
            ".git/config", "certs/server.pem", "config/api_token.txt",
            "config/install_key.bin", "config/openai_api_key.txt",
            "config/r2_credentials.json"])

    def test_push_refuses_before_a_single_byte_leaves(self):
        d = Path(tempfile.mkdtemp(prefix="cosmos_r2_sec_"))
        self.addCleanup(shutil.rmtree, d, True)
        (d / "config").mkdir()
        (d / "ok.txt").write_text("fine\n", encoding="utf-8", newline="\n")
        (d / "config" / "install_key.bin").write_bytes(b"\x00" * 32)
        tp = r2.MemoryTransport()
        with self.assertRaises(cb.BackupRefusal) as a:
            r2.push(d, r2.R2Target(fake_creds(), "p", tp), scratch=d.parent / "sc")
        self.assertEqual(a.exception.kind, "SECRETS_IN_SCOPE")
        self.assertEqual(tp.calls, [])            # refused BEFORE the first request
        self.assertEqual(tp.objects, {})

    def test_public_ca_bundle_is_not_a_secret_hit(self):
        d = Path(tempfile.mkdtemp(prefix="cosmos_r2_pem_"))
        self.addCleanup(shutil.rmtree, d, True)
        pem = d / "vendor" / "certifi" / "cacert.pem"
        pem.parent.mkdir(parents=True)
        pem.write_text(
            "-----BEGIN CERTIFICATE-----\n"
            "NOT-A-REAL-CERTIFICATE-PUBLIC-CA-BUNDLE-FIXTURE\n"
            "-----END CERTIFICATE-----\n",
            encoding="utf-8", newline="\n")
        (d / "ok.txt").write_text("fine\n", encoding="utf-8", newline="\n")
        m = cb.build_manifest(d)
        self.assertEqual(r2.scan_secrets(m), [])

    def test_private_key_shape_is_a_secret_hit(self):
        d = Path(tempfile.mkdtemp(prefix="cosmos_r2_key_"))
        self.addCleanup(shutil.rmtree, d, True)
        key = d / "vendor" / "mod" / "signing.key"
        key.parent.mkdir(parents=True)
        key.write_text(
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "NOT-A-REAL-KEY-SYNTHETIC-FIXTURE-ONLY\n"
            "-----END RSA PRIVATE KEY-----\n",
            encoding="utf-8", newline="\n")
        (d / "ok.txt").write_text("fine\n", encoding="utf-8", newline="\n")
        m = cb.build_manifest(d)
        self.assertEqual(r2.scan_secrets(m), ["vendor/mod/signing.key"])


# ------------------------------------------------------------------ round trip

class TestPushRoundTrip(R2TestBase):
    def test_push_stores_reads_back_and_seals(self):
        tp, target, receipt = self.push_ok()
        self.assertEqual(receipt["kind"], "R2_PUSH_OK")
        self.assertEqual(receipt["files_pushed"], 2)
        self.assertEqual(receipt["readback_verified"], 2)
        cb.check_seal(receipt, HMAC_KEY)
        # object keys are <bucket>/<prefix>/<rel> — path-style S3, which is what
        # the canonical URI signs, so the key the transport sees IS the signed one
        self.assertIn("cosmos-bucket/cosmos/a.txt", tp.objects)
        self.assertIn("cosmos-bucket/cosmos/nested/b.bin", tp.objects)
        self.assertEqual(tp.objects["cosmos-bucket/cosmos/a.txt"], b"alpha\n")
        # every data file was PUT and then GET back — the round trip, not a claim
        self.assertEqual([k for m, k in tp.calls if m == "GET"],
                         ["cosmos-bucket/cosmos/a.txt", "cosmos-bucket/cosmos/nested/b.bin"])

    def test_readback_files_rehash_to_the_manifest(self):
        _tp, target, receipt = self.push_ok()
        manifest = target.get_artifact(cb.MANIFEST_NAME)
        cb.check_seal(manifest, HMAC_KEY)
        self.assertEqual(receipt["manifest_seal_sha256"], manifest["seal"]["sha256"])
        for rel, entry in manifest["files"].items():
            self.assertEqual(cb.sha256_file(self.scratch / rel), entry["sha256"])

    def test_corrupted_object_is_caught_by_the_read_back(self):
        """A PUT that returns 200 proves nothing. Flip a byte on the way back out."""
        class Flip(r2.MemoryTransport):
            def request(self, method, url, headers, body=None):
                st, h, b = super().request(method, url, headers, body)
                if method == "GET" and url.endswith("a.txt"):
                    b = b + b"corrupt"
                return st, h, b

        with self.assertRaises(cb.BackupRefusal) as a:
            r2.push(self.src, r2.R2Target(fake_creds(), "cosmos", Flip()),
                    scratch=self.scratch)
        self.assertEqual(a.exception.kind, "R2_HASH_MISMATCH")

    def test_missing_object_is_typed(self):
        t = r2.R2Target(fake_creds(), "p", r2.MemoryTransport())
        with self.assertRaises(cb.BackupRefusal) as a:
            t.retrieve("never-stored.txt", self.tmp / "out.txt")
        self.assertEqual(a.exception.kind, "R2_OBJECT_MISSING")

    def test_artifact_json_round_trips(self):
        t = r2.R2Target(fake_creds(), "p", r2.MemoryTransport())
        t.put_artifact("X.json", {"a": 1, "b": [2, 3]})
        self.assertEqual(t.get_artifact("X.json"), {"a": 1, "b": [2, 3]})

    def test_unreadable_artifact_is_NOT_A_BACKUP_SET_not_JSONDecodeError(self):
        tp = r2.MemoryTransport()
        t = r2.R2Target(fake_creds(), "p", tp)
        t.put_artifact("X.json", {"a": 1})
        for k in list(tp.objects):
            tp.objects[k] = b"{not json"
        with self.assertRaises(cb.BackupRefusal) as a:
            t.get_artifact("X.json")
        self.assertEqual(a.exception.kind, "NOT_A_BACKUP_SET")

    def test_artifact_true_is_NOT_A_BACKUP_SET_not_a_bool(self):
        tp = r2.MemoryTransport()
        t = r2.R2Target(fake_creds(), "p", tp)
        t.put_artifact("X.json", {"a": 1})
        for k in list(tp.objects):
            tp.objects[k] = b"true"
        with self.assertRaises(cb.BackupRefusal) as a:
            t.get_artifact("X.json")
        self.assertEqual(a.exception.kind, "NOT_A_BACKUP_SET")

    def test_scan_files_str_is_NOT_A_BACKUP_SET_not_silent_empty(self):
        with self.assertRaises(cb.BackupRefusal) as a:
            r2.scan_secrets({"files": "install_key.bin"})
        self.assertEqual(a.exception.kind, "NOT_A_BACKUP_SET")

    def test_scan_array_manifest_is_NOT_A_BACKUP_SET(self):
        with self.assertRaises(cb.BackupRefusal) as a:
            r2.scan_secrets([])
        self.assertEqual(a.exception.kind, "NOT_A_BACKUP_SET")

    def test_no_transport_is_a_refusal_not_a_silent_default(self):
        with self.assertRaises(cb.BackupRefusal) as a:
            r2.R2Target(fake_creds(), "p", None)
        self.assertEqual(a.exception.kind, "NO_TRANSPORT")

    def test_push_without_scratch_refuses_rather_than_inventing_a_path(self):
        with self.assertRaises(cb.BackupRefusal) as a:
            r2.push(self.src, r2.R2Target(fake_creds(), "p", r2.MemoryTransport()))
        self.assertEqual(a.exception.kind, "NO_SCRATCH")

    def test_occupied_scratch_refuses(self):
        self.scratch.mkdir(parents=True)
        (self.scratch / "leftover").write_text("x", encoding="utf-8")
        with self.assertRaises(cb.BackupRefusal) as a:
            r2.push(self.src, r2.R2Target(fake_creds(), "p", r2.MemoryTransport()),
                    scratch=self.scratch)
        self.assertEqual(a.exception.kind, "SCRATCH_NOT_EMPTY")


# ------------------------------------------------------------------ preflight / selfcheck

class TestPreflight(R2TestBase):
    def test_absent_credential_is_BLOCKED_and_says_what_to_place(self):
        pf = r2.preflight(self.src, None)
        self.assertEqual(pf["status"], "BLOCKED")
        self.assertTrue(pf["adapter_implemented"])
        self.assertIn("r2_credentials.json", " ".join(pf["blockers"]))
        self.assertEqual(pf["scope"]["files"], 2)
        self.assertEqual(pf["scope"]["secrets_in_scope"], [])

    def test_forbidden_credential_path_surfaces_as_the_credential_state(self):
        pf = r2.preflight(None, Path(r"D:\R2Cloner\rclone.conf"))
        self.assertEqual(pf["credential"]["state"], "FORBIDDEN_CREDENTIAL_PATH")
        self.assertEqual(pf["status"], "BLOCKED")

    def test_ready_when_credential_and_scope_are_both_clean(self):
        d = Path(tempfile.mkdtemp(prefix="cosmos_r2_pf_"))
        self.addCleanup(shutil.rmtree, d, True)
        p = d / "r2_credentials.json"
        p.write_text(json.dumps({"account_id": "acct1234", "access_key_id": "AKIAFAKE0001",
                                 "secret_access_key": SECRET_SENTINEL,
                                 "bucket": "cosmos-bucket"}), encoding="utf-8")
        pf = r2.preflight(self.src, p)
        self.assertEqual(pf["status"], "READY")
        self.assertEqual(pf["credential"]["state"], "PRESENT")
        self.assertNotIn(SECRET_SENTINEL, json.dumps(pf))


class TestSelfcheck(R2TestBase):
    def test_selfcheck_runs_the_whole_path_with_no_credential_and_no_network(self):
        out = r2.selfcheck(self.src, self.scratch, HMAC_KEY)
        self.assertEqual(out["kind"], "R2_PUSH_OK")
        self.assertEqual(out["transport"], "MemoryTransport")
        self.assertEqual(out["files_pushed"], 2)
        self.assertEqual(out["readback_verified"], 2)
        cb.check_seal({k: v for k, v in out.items()
                       if k not in ("transport", "objects", "requests")}, HMAC_KEY)


class TestCLI(R2TestBase):
    def _run(self, argv):
        so, se = io.StringIO(), io.StringIO()
        with redirect_stdout(so), redirect_stderr(se):
            rc = r2.main(argv)
        return rc, so.getvalue(), se.getvalue()

    def test_preflight_exits_zero_and_prints_json(self):
        rc, out, _ = self._run(["preflight", "--source", str(self.src)])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["status"], "BLOCKED")

    def test_push_without_credentials_exits_two_with_a_typed_kind(self):
        rc, _out, err = self._run([
            "push", "--source", str(self.src), "--prefix", "p",
            "--credentials", str(self.tmp / "nope.json"), "--scratch", str(self.scratch)])
        self.assertEqual(rc, 2)
        self.assertEqual(json.loads(err)["kind"], "NO_CREDENTIALS")

    def test_selfcheck_cli_exits_zero(self):
        rc, out, _ = self._run(["selfcheck", "--source", str(self.src),
                                "--scratch", str(self.scratch)])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["readback_verified"], 2)


# ------------------------------------------------------------------ F-47 seam: ADAPTERS["r2"] + Gate B rehearsal

HERE = Path(__file__).resolve().parent
OLD_BACKUP = (HERE.parents[1] / "_delme"
              / "predispose_cosmos_backup_f47_r2adapter_20260831T065325Z"
              / "cosmos_backup.py")
BITE_R2_STUB = HERE / "_bite_f47_r2_stub.json"


class TestAdaptersR2TypedRefusal(unittest.TestCase):
    """ADAPTERS['r2']() is NO_CREDENTIALS, not a NotImplementedError stub."""

    def test_no_args_is_typed_NO_CREDENTIALS(self):
        with self.assertRaises(cb.BackupRefusal) as a:
            cb.ADAPTERS["r2"]()
        self.assertEqual(a.exception.kind, "NO_CREDENTIALS")

    def test_factory_with_injected_creds_and_transport_is_the_real_target(self):
        t = cb.ADAPTERS["r2"](credentials=fake_creds(), prefix="wired",
                              transport=r2.MemoryTransport())
        self.assertIsInstance(t, r2.R2Target)
        self.assertEqual(t.prefix, "wired")

    def test_missing_path_is_NO_CREDENTIALS_and_does_not_open_a_socket(self):
        missing = Path(tempfile.mkdtemp(prefix="cosmos_r2_ad_")) / "r2_credentials.json"
        shutil.rmtree(missing.parent, ignore_errors=True)
        with self.assertRaises(cb.BackupRefusal) as a:
            cb.ADAPTERS["r2"](credentials=missing)
        self.assertEqual(a.exception.kind, "NO_CREDENTIALS")


class TestRehearseTargetGateB(R2TestBase):
    """R2_OFFSITE_PLAN Gate B: restore from the bucket into empty scratch, re-hash.
    Offline: MemoryTransport. No credential file is read."""

    def test_rehearse_from_r2_target_restores_and_reseals(self):
        _tp, target, receipt = self.push_ok()
        # push() already used self.scratch; Gate B needs a DIFFERENT empty dir.
        rehearse_scratch = self.tmp / "rehearse"
        proof = cb.do_rehearse_target(target, rehearse_scratch, HMAC_KEY)
        self.assertEqual(proof["kind"], "REHEARSAL_PASS")
        self.assertEqual(proof["files_restored"], 2)
        self.assertEqual(proof["target"], "R2Target")
        self.assertEqual(proof["manifest_seal_sha256"], receipt["manifest_seal_sha256"])
        cb.check_seal(proof, HMAC_KEY)
        stored = target.get_artifact(cb.REHEARSAL_NAME)
        self.assertEqual(stored["kind"], "REHEARSAL_PASS")
        self.assertEqual(cb.sha256_file(rehearse_scratch / "a.txt"),
                         cb.hashlib.sha256(b"alpha\n").hexdigest())

    def test_occupied_rehearse_scratch_refuses(self):
        _tp, target, _receipt = self.push_ok()
        occupied = self.tmp / "occupied"
        occupied.mkdir()
        (occupied / "leftover").write_text("x", encoding="utf-8")
        with self.assertRaises(cb.BackupRefusal) as a:
            cb.do_rehearse_target(target, occupied, HMAC_KEY)
        self.assertEqual(a.exception.kind, "SCRATCH_NOT_EMPTY")

    def test_staged_old_ADAPTERS_r2_raises_NotImplementedError(self):
        """Bite: the new checks FAIL against the pre-change stub. Required
        before belief. The artifact `_bite_f47_r2_stub.json` is the same
        measurement taken before the factory landed."""
        self.assertTrue(OLD_BACKUP.is_file(), f"missing staged predecessor {OLD_BACKUP}")
        spec = importlib.util.spec_from_file_location("cosmos_backup_f47_old", OLD_BACKUP)
        old = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(old)
        with self.assertRaises(NotImplementedError):
            old.ADAPTERS["r2"]()
        self.assertFalse(hasattr(old, "do_rehearse_target"))
        self.assertEqual(old.DEFAULT_EXCLUDES, (".git",))
        self.assertTrue(BITE_R2_STUB.is_file(), "bite artifact must be recorded before belief")
        rec = json.loads(BITE_R2_STUB.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"])
        self.assertEqual(rec["r2_raises"], "NotImplementedError")
        self.assertFalse(rec["has_do_rehearse_target"])
        self.assertNotIn("__pycache__", rec["default_excludes"])


class TestUnpinnedRound7Headers(unittest.TestCase):
    """Round-7: canonical_request of a non-object headers was AttributeError.
    Bite `_bite_unpinned_round7.json`."""

    BITE = Path(__file__).resolve().parent / "_bite_unpinned_round7.json"

    def test_round7_bite_records_untyped_headers(self):
        rec = json.loads(self.BITE.read_text(encoding="utf-8"))
        self.assertTrue(rec["all_bite"], rec)
        self.assertEqual(rec["canon_headers_list"]["crash"], "AttributeError")
        self.assertEqual(rec["canon_headers_none"]["crash"], "AttributeError")
        self.assertEqual(rec["canon_headers_str"]["crash"], "AttributeError")

    def test_headers_list_is_BAD_HEADERS(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            r2.canonical_request("GET", "/b/k", [], "0" * 64)
        self.assertEqual(ctx.exception.kind, "BAD_HEADERS")

    def test_headers_none_is_BAD_HEADERS(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            r2.canonical_request("GET", "/b/k", None, "0" * 64)
        self.assertEqual(ctx.exception.kind, "BAD_HEADERS")

    def test_headers_str_is_BAD_HEADERS(self):
        with self.assertRaises(cb.BackupRefusal) as ctx:
            r2.canonical_request("GET", "/b/k", "host:x", "0" * 64)
        self.assertEqual(ctx.exception.kind, "BAD_HEADERS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
