#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin PEM classification on the builds/backup secret scanner.

Public CA bundles (BEGIN CERTIFICATE) are not key material. Private-key
envelopes (BEGIN RSA/EC/OPENSSH/PGP PRIVATE KEY, BEGIN ENCRYPTED PRIVATE
KEY) still are. Ambiguous still refuses.

This file lives under tests/ (assignment fence). It imports the scanner from
builds/backup/ — never cosmos/cosmos_backup.py (same module name, different
tree). Synthetic PEM shapes only; bodies are dummy labels, not key material.
Nothing is printed from a fixture body.

    py -3.14 tests/test_backup_pem_classify.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "builds" / "backup"))

import cosmos_backup as cb  # noqa: E402  — builds/backup, not cosmos/

_PUBLIC_CA_SHAPE = (
    "-----BEGIN CERTIFICATE-----\n"
    "NOT-A-REAL-CERTIFICATE-PUBLIC-CA-BUNDLE-FIXTURE\n"
    "-----END CERTIFICATE-----\n"
)
_PRIVATE_RSA_SHAPE = (
    "-----BEGIN RSA PRIVATE KEY-----\n"
    "NOT-A-REAL-KEY-SYNTHETIC-FIXTURE-ONLY\n"
    "-----END RSA PRIVATE KEY-----\n"
)


class TestPemClassify(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_pem_classify_"))
        self.src = self.tmp / "src"
        self.src.mkdir()
        (self.src / "ok.txt").write_text("ok\n", encoding="utf-8", newline="\n")
        self.dest = self.tmp / "dest"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, True)

    def test_public_ca_bundle_is_not_SECRETS_IN_SCOPE(self):
        pem = self.src / "vendor" / "certifi" / "cacert.pem"
        pem.parent.mkdir(parents=True)
        pem.write_text(_PUBLIC_CA_SHAPE, encoding="utf-8", newline="\n")
        set_dir = cb.do_backup(self.src, self.dest)
        self.assertTrue((set_dir / cb.MANIFEST_NAME).is_file())
        self.assertEqual(cb.scan_secrets(cb.build_manifest(self.src)), [])

    def test_private_key_shape_is_SECRETS_IN_SCOPE(self):
        key = self.src / "vendor" / "mod" / "signing.key"
        key.parent.mkdir(parents=True)
        key.write_text(_PRIVATE_RSA_SHAPE, encoding="utf-8", newline="\n")
        with self.assertRaises(cb.BackupRefusal) as cm:
            cb.do_backup(self.src, self.dest)
        self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE")
        self.assertIn("signing.key", cm.exception.detail)
        self.assertFalse(self.dest.exists())

    def test_ambiguous_pem_still_refuses(self):
        (self.src / "empty.pem").write_bytes(b"")
        with self.assertRaises(cb.BackupRefusal) as cm:
            cb.do_backup(self.src, self.dest)
        self.assertEqual(cm.exception.kind, "SECRETS_IN_SCOPE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
