#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Jukebox fold: scheduler truth, five legal states, consumer contracts."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))
sys.path.insert(0, str(ROOT / "builds" / "cdeck"))

from cosmos_jukebox_panel import (  # noqa: E402
    LEGAL,
    MAX_LEDGER_BYTES,
    SCHEMA,
    _empty_counts,
    handle_get,
)
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402


class JukeboxPanelTests(unittest.TestCase):
    def setUp(self):
        self.td = Path(tempfile.mkdtemp(prefix="cosmos_jukebox_"))
        self.root = install(self.td / "live", tree_id="spike-jukebox")
        self.paths = CosmosPaths(self.root)
        self.kernel = Kernel(self.root, worker="core-test")

    def _get(self):
        return handle_get(str(self.root), expected_tree_id=self.paths.sentinel.tree_id)

    def test_empty_queue_explicit_zero_counts(self):
        code, body = self._get()
        self.assertEqual(code, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(body["schema"], SCHEMA)
        c = body["queue"]["counts"]
        self.assertEqual(c, _empty_counts())
        self.assertEqual(body["counts"], c)
        self.assertTrue(body["queue"]["available"])
        self.assertEqual(body["queue"]["jobs"], [])

    def test_lifecycle_legal_states(self):
        jid = self.kernel.sched.submit("echo hi", "normal")
        code, body = self._get()
        self.assertEqual(body["queue"]["counts"]["QUEUED"], 1)
        job = body["queue"]["jobs"][0]
        self.assertEqual(job["st"], "QUEUED")
        self.assertEqual(job["state"], "QUEUED")
        self.assertEqual(job["job_id"], jid)
        self.assertIn("command", job)

        self.kernel.sched.claim_next()
        _, body2 = self._get()
        self.assertEqual(body2["queue"]["counts"]["RUNNING"], 1)
        self.assertEqual(body2["queue"]["counts"]["QUEUED"], 0)

        self.kernel.sched.done(jid, "FINDINGS", detail="critique")
        _, body3 = self._get()
        self.assertEqual(body3["queue"]["counts"]["FINDINGS"], 1)
        self.assertFalse(body3["queue"]["jobs"][0]["stale_flag"])

    def test_top_level_counts_alias(self):
        self.kernel.sched.submit("a", "high")
        self.kernel.sched.submit("b", "normal")
        _, body = self._get()
        self.assertEqual(body["counts"], body["queue"]["counts"])
        self.assertEqual(body["jobs_n"], 2)

    def test_manifest_file_wins_command(self):
        jid = self.kernel.sched.submit("py:ledger.py", "normal")
        mp = self.paths.role("queue") / "manifests" / f"{jid}.json"
        mp.write_text(
            json.dumps({"job_id": jid, "command": "py:file.py", "priority": "high",
                        "lane": "lg", "submitted": 1.0, "timeout_s": 60}),
            encoding="utf-8",
        )
        _, body = self._get()
        row = body["queue"]["jobs"][0]
        self.assertEqual(row["command"], "py:file.py")
        self.assertEqual(row["priority"], "high")
        self.assertTrue(row["manifest_present"])

    def test_missing_manifest_still_lists_job(self):
        jid = self.kernel.sched.submit("orphan", "low")
        mp = self.paths.role("queue") / "manifests" / f"{jid}.json"
        mp.unlink()
        _, body = self._get()
        row = next(j for j in body["queue"]["jobs"] if j["job_id"] == jid)
        self.assertFalse(row["manifest_present"])
        self.assertEqual(row["command"], "orphan")

    def test_stale_flag_from_job_stale_event(self):
        jid = self.kernel.sched.submit("slow", "normal", timeout_s=1)
        self.kernel.sched.claim_next()
        self.kernel.sched.ledger.append(
            "JOB_STALE",
            {"job_id": jid, "worker": "core-test", "detail": "reported"},
        )
        _, body = self._get()
        row = body["queue"]["jobs"][0]
        self.assertTrue(row["stale_flag"])
        self.assertEqual(body["queue"]["counts"]["stale_flagged"], 1)

    def test_too_large_refusal_no_counts(self):
        ledger = self.paths.role("queue") / "sched_ledger.jsonl"
        ledger.write_bytes(b"x" * (MAX_LEDGER_BYTES + 1))
        _, body = self._get()
        self.assertFalse(body["queue"]["available"])
        self.assertEqual(body["queue"]["kind"], "TOO_LARGE")
        self.assertNotIn("counts", body["queue"])

    def test_malformed_middle_no_counts(self):
        self.kernel.sched.submit("x", "normal")
        ledger = self.paths.role("queue") / "sched_ledger.jsonl"
        text = ledger.read_text(encoding="utf-8")
        lines = text.splitlines()
        broken = lines[0] + "\nNOT JSON\n" + "\n".join(lines[1:])
        ledger.write_text(broken, encoding="utf-8")
        _, body = self._get()
        self.assertEqual(body["queue"]["kind"], "MALFORMED")
        self.assertNotIn("counts", body["queue"])

    def test_gitur_consumer_shape(self):
        self.kernel.sched.submit("py:cosmos_cursor_rail.py --gate", "normal")
        _, body = self._get()
        q = body["queue"]
        self.assertTrue(q["available"])
        self.assertIsInstance(q["jobs"], list)
        self.assertTrue(q["jobs"][0].get("command"))

    def test_review_consumer_finds_findings(self):
        jid = self.kernel.sched.submit("work", "normal")
        self.kernel.sched.claim_next()
        self.kernel.sched.done(jid, "FINDINGS")
        import sys as _sys
        cdeck = str(ROOT / "builds" / "cdeck")
        if cdeck not in _sys.path:
            _sys.path.insert(0, cdeck)
        from cosmos_review import _blockers  # noqa: E402

        kernel = SimpleNamespace(paths=self.paths)
        blk = _blockers(kernel)
        states = {r.get("state") for r in blk.get("rows") or []}
        self.assertIn("FINDINGS", states)

    def test_all_legal_words_in_schema_doc(self):
        for w in ("QUEUED", "RUNNING", "BROKE", "CLEAN", "FINDINGS"):
            self.assertIn(w, LEGAL)


if __name__ == "__main__":
    unittest.main()
