#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PS-03 — /jukebox jobs/counts contract around scheduler truth.

    py -3.14 -m unittest tests.test_jukebox
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))
sys.path.insert(0, str(ROOT / "builds" / "cdeck"))

from cosmos_jukebox_panel import (  # noqa: E402
    IN_FLIGHT, LEGAL_STATES, MAX_LEDGER_BYTES, SCHEMA, handle_get,
)
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service  # noqa: E402


LEGAL = set(LEGAL_STATES)


def _http(svc, path, token=None):
    req = urllib.request.Request("http://127.0.0.1:%s%s" % (svc.port, path))
    if token is not None:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def _tag_manifest(kernel, jid, **extra):
    mp = kernel.paths.role("queue") / "manifests" / ("%s.json" % jid)
    obj = json.loads(mp.read_text(encoding="utf-8"))
    obj.update(extra)
    mp.write_text(json.dumps(obj, indent=1), encoding="utf-8")


def _gitur_consumer(body):
    """Gitur-shaped read: queue.jobs + st/stale_flag. No command-text stage."""
    q = (body or {}).get("queue") or {}
    raw = q.get("jobs") if isinstance(q, dict) else None
    out = []
    if not q.get("available"):
        return q.get("kind") or "QUEUE_UNAVAILABLE", out
    for row in raw or []:
        if not isinstance(row, dict):
            continue
        out.append({
            "job_id": row.get("job_id"),
            "st": row.get("st") or row.get("state"),
            "stale_flag": row.get("stale_flag"),
            "product": row.get("product"),
            "stage": row.get("stage"),
            "command": row.get("command"),
        })
    return "jukebox", out


def _review_consumer(body):
    """Review-shaped read: FINDINGS / BROKE / stale_flag. No text stage."""
    q = (body or {}).get("queue") or {}
    rows = []
    for j in (q.get("jobs") if isinstance(q, dict) else None) or []:
        if not isinstance(j, dict):
            continue
        st = str(j.get("st") or "").upper()
        if st in ("FINDINGS", "BROKE") or j.get("stale_flag"):
            rows.append({
                "id": j.get("job_id"),
                "state": st,
                "why": ("FINDINGS — awaiting CCr" if st == "FINDINGS"
                        else ("STALE RUNNING" if j.get("stale_flag") else st)),
            })
    return rows


def _runs_consumer(body):
    counts = (body or {}).get("counts") or {}
    jobs = (body or {}).get("jobs") or []
    return {
        "counts": {w: counts.get(w) for w in LEGAL_STATES},
        "stale_flagged": counts.get("stale_flagged"),
        "in_flight": [r for r in jobs if r.get("st") in IN_FLIGHT],
        "broke_in_flight": [r for r in jobs
                            if r.get("st") == "BROKE" and r.get("st") in IN_FLIGHT],
    }


class JukeboxContract(unittest.TestCase):
    def setUp(self):
        self.td = Path(tempfile.mkdtemp(prefix="cosmos_jukebox_"))
        self.root = install(self.td / "live", tree_id="jukebox-ps03")
        self.kernel = Kernel(self.root, worker="core")

    def _fold(self, kernel=None):
        return handle_get(
            str(self.root),
            expected_tree_id="jukebox-ps03",
            kernel=self.kernel if kernel is None else kernel,
        )

    def test_empty_queue_is_explicit(self):
        code, body = self._fold()
        self.assertEqual(code, 200)
        self.assertTrue(body.get("ok"))
        self.assertEqual(body.get("schema"), SCHEMA)
        self.assertEqual(body.get("tree_id"), "jukebox-ps03")
        self.assertEqual(body.get("jobs"), [])
        self.assertEqual(body.get("jobs_n"), 0)
        counts = body["counts"]
        for w in LEGAL_STATES:
            self.assertEqual(counts[w], 0, w)
        self.assertEqual(counts["stale_flagged"], 0)
        self.assertTrue(body["queue"]["available"])
        self.assertEqual(body["queue"]["jobs"], [])
        self.assertEqual(body["queue"]["counts"], counts)
        self.assertIs(body.get("error"), None)

    def test_five_legal_words_and_aliases(self):
        q = self.kernel.sched.submit("py:queued.py", "low")
        r = self.kernel.sched.submit("py:running.py", "normal")
        c = self.kernel.sched.submit("py:clean.py", "normal")
        f = self.kernel.sched.submit("py:findings.py", "high")
        b = self.kernel.sched.submit("py:broke.py", "critical")
        # claim order: critical, high, normal (submitted asc), low
        claimed_b = self.kernel.sched.claim_next()
        self.assertEqual(claimed_b["job_id"], b)
        self.kernel.sched.done(b, "BROKE", "failed")
        claimed_f = self.kernel.sched.claim_next()
        self.assertEqual(claimed_f["job_id"], f)
        self.kernel.sched.done(f, "FINDINGS", "checker")
        claimed_r = self.kernel.sched.claim_next()
        self.assertEqual(claimed_r["job_id"], r)
        claimed_c = self.kernel.sched.claim_next()
        self.assertEqual(claimed_c["job_id"], c)
        self.kernel.sched.done(c, "CLEAN")
        # r still RUNNING; q still QUEUED
        code, body = self._fold()
        self.assertEqual(code, 200)
        by = {row["job_id"]: row for row in body["jobs"]}
        self.assertEqual(by[q]["st"], "QUEUED")
        self.assertEqual(by[q]["state"], "QUEUED")
        self.assertEqual(by[r]["st"], "RUNNING")
        self.assertEqual(by[c]["st"], "CLEAN")
        self.assertEqual(by[c]["outcome"], "CLEAN")
        self.assertEqual(by[f]["st"], "FINDINGS")
        self.assertEqual(by[b]["st"], "BROKE")
        counts = body["counts"]
        self.assertEqual(counts["QUEUED"], 1)
        self.assertEqual(counts["RUNNING"], 1)
        self.assertEqual(counts["CLEAN"], 1)
        self.assertEqual(counts["FINDINGS"], 1)
        self.assertEqual(counts["BROKE"], 1)
        self.assertEqual(body["done_n"], 1)  # CLEAN only
        self.assertEqual(body["findings_n"], 1)
        self.assertEqual(body["in_flight_n"], 3)  # QUEUED+RUNNING+FINDINGS
        self.assertEqual(body["broke_n"], 1)
        self.assertEqual(body["jobs_n"], 5)
        self.assertEqual(body["queue"]["jobs"], body["jobs"])
        for row in body["jobs"]:
            self.assertIn(row["st"], LEGAL)
            self.assertNotIn(row["st"], ("DONE", "FAILED", "PAUSED", "waiting"))

    def test_stale_is_flag_not_outcome_and_never_retry(self):
        jid = self.kernel.sched.submit("py:stale.py", "normal")
        self.kernel.sched.claim_next()
        reported = self.kernel.sched.report_stale(older_than_s=-1)
        self.assertEqual(reported, [jid])
        again = self.kernel.sched.report_stale(older_than_s=-1)
        self.assertEqual(again, [])  # report-never-retry
        code, body = self._fold()
        row = body["jobs"][0]
        self.assertEqual(row["st"], "RUNNING")
        self.assertTrue(row["stale_flag"])
        self.assertTrue(row["stale"])
        self.assertEqual(body["counts"]["RUNNING"], 1)
        self.assertEqual(body["counts"]["stale_flagged"], 1)
        self.assertEqual(body["stale_flagged"], 1)
        self.assertNotIn("actions", body)
        self.assertNotIn("cancel", body)
        self.assertNotIn("retry", body)
        for row in body["jobs"]:
            self.assertNotIn("cancel", row)
            self.assertNotIn("retry", row)

    def test_untagged_not_guessed_from_command_text(self):
        jid = self.kernel.sched.submit(
            "gitur forge implement sgh — heat from command text", "high")
        code, body = self._fold()
        row = [r for r in body["jobs"] if r["job_id"] == jid][0]
        self.assertEqual(row["product"], "UNATTRIBUTED")
        self.assertEqual(row["stage"], "UNMEASURED")
        kind, jobs = _gitur_consumer(body)
        self.assertEqual(kind, "jukebox")
        self.assertEqual(jobs[0]["product"], "UNATTRIBUTED")
        self.assertEqual(jobs[0]["stage"], "UNMEASURED")
        self.assertEqual(jobs[0]["st"], "QUEUED")

    def test_tagged_manifest_wins_without_text_match(self):
        jid = self.kernel.sched.submit("py:unrelated_name.py", "normal")
        _tag_manifest(self.kernel, jid, product="website", stage="critics")
        code, body = self._fold()
        row = [r for r in body["jobs"] if r["job_id"] == jid][0]
        self.assertEqual(row["product"], "website")
        self.assertEqual(row["stage"], "critics")
        self.assertTrue(row["manifest_present"])
        self.assertEqual(row["command"], "py:unrelated_name.py")

    def test_gitur_review_runs_consumers_use_state_words(self):
        f = self.kernel.sched.submit("py:find.py", "high")
        r = self.kernel.sched.submit("py:run.py", "normal")
        self.kernel.sched.claim_next()
        self.kernel.sched.done(f, "FINDINGS")
        self.kernel.sched.claim_next()
        self.kernel.sched.report_stale(older_than_s=-1)
        code, body = self._fold()
        self.assertEqual(code, 200)
        kind, gj = _gitur_consumer(body)
        self.assertEqual(kind, "jukebox")
        by = {j["job_id"]: j for j in gj}
        self.assertEqual(by[f]["st"], "FINDINGS")
        self.assertEqual(by[r]["st"], "RUNNING")
        self.assertTrue(by[r]["stale_flag"])
        rev = _review_consumer(body)
        why = {x["id"]: x["why"] for x in rev}
        self.assertEqual(why[f], "FINDINGS — awaiting CCr")
        self.assertEqual(why[r], "STALE RUNNING")
        runs = _runs_consumer(body)
        self.assertEqual(runs["counts"]["FINDINGS"], 1)
        self.assertEqual(runs["counts"]["RUNNING"], 1)
        self.assertEqual(runs["broke_in_flight"], [])
        self.assertEqual(len(runs["in_flight"]), 2)

    def test_get_does_not_mutate(self):
        head = self.kernel.ledger.head_seq()
        sched_head = self.kernel.sched.ledger.head_seq()
        self.kernel.sched.submit("py:hold.py", "low")
        sched_after_submit = self.kernel.sched.ledger.head_seq()
        handle_get(str(self.root), expected_tree_id="jukebox-ps03",
                   kernel=self.kernel)
        handle_get(str(self.root), expected_tree_id="jukebox-ps03")
        self.assertEqual(self.kernel.ledger.head_seq(), head)
        self.assertEqual(self.kernel.sched.ledger.head_seq(), sched_after_submit)
        self.assertGreaterEqual(sched_after_submit, sched_head)

    def test_get_without_kernel_does_not_mkdir(self):
        raw = install(self.td / "bare", tree_id="jukebox-bare")
        manifests = raw / "queue" / "manifests"
        self.assertFalse(manifests.exists())
        led = raw / "queue" / "sched_ledger.jsonl"
        self.assertFalse(led.exists())
        code, body = handle_get(str(raw), expected_tree_id="jukebox-bare")
        self.assertEqual(code, 200)
        self.assertEqual(body["jobs"], [])
        self.assertFalse(manifests.exists())
        self.assertFalse(led.exists())

    def test_identity_mismatch_is_409(self):
        code, body = handle_get(str(self.root), expected_tree_id="not-this-tree")
        self.assertEqual(code, 409)
        self.assertEqual(body.get("error"), "IDENTITY_MISMATCH")
        self.assertFalse(body["queue"]["available"])
        self.assertIsNone(body["queue"]["jobs"])
        self.assertNotIn("counts", body)

    def test_torn_ledger_is_refused_without_counts(self):
        p = self.kernel.paths.role("queue") / "sched_ledger.jsonl"
        p.write_text("this is not json\n", encoding="utf-8")
        # Disk fold (no kernel) so we re-read the torn file.
        code, body = handle_get(str(self.root), expected_tree_id="jukebox-ps03")
        self.assertEqual(code, 200)
        self.assertEqual(body.get("error"), "LEDGER_REFUSED")
        self.assertFalse(body["ok"])
        self.assertFalse(body["queue"]["available"])
        self.assertNotIn("counts", body)

    def test_too_large_has_no_counts(self):
        import cosmos_jukebox_panel as panel
        old = panel.MAX_LEDGER_BYTES
        panel.MAX_LEDGER_BYTES = 32
        try:
            p = self.kernel.paths.role("queue") / "sched_ledger.jsonl"
            p.write_text("x" * 65, encoding="utf-8")
            code, body = handle_get(str(self.root), expected_tree_id="jukebox-ps03")
            self.assertEqual(code, 200)
            self.assertEqual(body.get("error"), "TOO_LARGE")
            self.assertNotIn("counts", body)
        finally:
            panel.MAX_LEDGER_BYTES = old
        self.assertGreater(MAX_LEDGER_BYTES, 32)

    def test_unknown_job_done_does_not_invent(self):
        # JOB_DONE for an id that was never submitted is ignored by the fold.
        from cosmos_ledger import Ledger
        key = self.kernel.paths.config("install_key.bin").read_bytes()
        led = Ledger(self.kernel.paths.role("queue") / "sched_ledger.jsonl",
                     key, "ghost")
        led.append("JOB_DONE", {"job_id": "j-ghost", "outcome": "CLEAN",
                                "worker": "ghost"})
        code, body = handle_get(str(self.root), expected_tree_id="jukebox-ps03")
        self.assertEqual(code, 200)
        ids = [r["job_id"] for r in body["jobs"]]
        self.assertNotIn("j-ghost", ids)
        self.assertEqual(body["counts"]["CLEAN"], 0)


class JukeboxHTTP(unittest.TestCase):
    def setUp(self):
        self.td = Path(tempfile.mkdtemp(prefix="cosmos_jukebox_http_"))
        self.root = install(self.td / "live", tree_id="jukebox-http")
        self.kernel = Kernel(self.root, worker="core")
        self.svc = Service(self.kernel, host="127.0.0.1", port=0)
        self.svc.serve_background()

    def tearDown(self):
        self.svc.shutdown()

    def test_http_jobs_counts_and_jobs_route_unchanged(self):
        jid = self.kernel.sched.submit("py:http.py", "high")
        _tag_manifest(self.kernel, jid, product="forge", stage="research")
        code, body = _http(self.svc, "/api/v1/jukebox")
        self.assertEqual(code, 200)
        self.assertTrue(body.get("ok"))
        self.assertEqual(body["schema"], SCHEMA)
        self.assertEqual(body["counts"]["QUEUED"], 1)
        self.assertEqual(body["jobs"][0]["product"], "forge")
        self.assertEqual(body["jobs"][0]["stage"], "research")
        jc, jb = _http(self.svc, "/api/v1/jobs")
        self.assertEqual(jc, 200)
        self.assertIn("measured_at", jb)
        self.assertIsInstance(jb["jobs"], dict)
        self.assertEqual(jb["jobs"][jid], "QUEUED")
        self.assertNotIn("counts", jb)
        self.assertNotIn("queue", jb)

    def test_uncomposed_stays_503(self):
        import cosmos_service as svcmod
        orig = svcmod._cdeck_panel_get

        def boom(mod):
            raise ImportError("panel missing")

        svcmod._cdeck_panel_get = boom
        try:
            code, body = _http(self.svc, "/api/v1/jukebox")
        finally:
            svcmod._cdeck_panel_get = orig
        self.assertEqual(code, 503)
        self.assertEqual(body.get("error"), "CDECK_PANEL_NOT_COMPOSED")

    def test_http_get_does_not_move_ledger(self):
        head = self.kernel.ledger.head_seq()
        sched_head = self.kernel.sched.ledger.head_seq()
        _http(self.svc, "/api/v1/jukebox")
        _http(self.svc, "/api/v1/jobs")
        self.assertEqual(self.kernel.ledger.head_seq(), head)
        self.assertEqual(self.kernel.sched.ledger.head_seq(), sched_head)


if __name__ == "__main__":
    unittest.main()
