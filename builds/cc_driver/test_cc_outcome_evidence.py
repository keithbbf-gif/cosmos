#!/usr/bin/env py -3.14
# -*- coding: utf-8 -*-
"""Unit gate on cc_outcome's evidence gatherers -- the three questions the pre-fix
driver never asked before filing a job.

The end-to-end suite (`test_cc_driver_outcome.py`) proves the driver files by the
WORK outcome. This one pins the evidence itself, including the cases a live run
cannot be made to produce on demand: a report whose `files` claim is a fabrication,
an artifact that predates the run, and a report line buried under trailing noise
from a killed process.

Run: py -3.14 builds/cc_driver/test_cc_outcome_evidence.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def _outcome_under_test():
    """$CC_OUTCOME_UNDER_TEST points the suite at another copy of the classifier
    -- how the pre-fix copy in _delme is proven to fail these tests. Default is
    the live module beside this file."""
    raw = os.environ.get("CC_OUTCOME_UNDER_TEST")
    if not raw:
        import cc_outcome as co
        return co
    path = Path(raw)
    spec = importlib.util.spec_from_file_location("cc_outcome_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


co = _outcome_under_test()

# Measured GBW engine stderr when --max-turns 60 is exhausted (job 370).
_MAX_TURNS_STDERR = "Max turns reached\nError: max turns reached\n"


class LastLineJson(unittest.TestCase):
    def test_plain_last_line(self):
        obj, raw = co.last_line_json('chatter\nmore\n{"status":"ok","files":[]}')
        self.assertEqual(obj["status"], "ok")
        self.assertTrue(raw.startswith("{"))

    def test_survives_trailing_noise_from_a_kill(self):
        """A killed agent can leave a partial line after its report. The contract
        says the report is last; reality says recover it anyway."""
        obj, _ = co.last_line_json('{"status":"ok","gate_passed":93}\nTermina')
        self.assertEqual(obj["gate_passed"], 93)

    def test_takes_the_last_object_not_the_first(self):
        obj, _ = co.last_line_json('{"status":"draft"}\nwork\n{"status":"final"}')
        self.assertEqual(obj["status"], "final")

    def test_no_report_is_none_not_an_exception(self):
        self.assertEqual(co.last_line_json(""), (None, None))
        self.assertEqual(co.last_line_json("no json here at all"), (None, None))
        self.assertEqual(co.last_line_json("{not: valid}"), (None, None))

    def test_a_json_array_is_not_a_report(self):
        self.assertEqual(co.last_line_json('[1,2,3]'), (None, None))


class FenceResolution(unittest.TestCase):
    def test_explicit_field_wins(self):
        self.assertEqual(co.fence_from_job({"fence": "builds/x", "task": "write ONLY under builds/y"}),
                         Path("builds/x"))

    def test_reads_the_canonical_work_order_line(self):
        """This is the only fence 070_cdeck_mobile_parity ever declared."""
        task = ("CANON: write ONLY under builds/cdeck/. Other agents work other "
                "fences RIGHT NOW.")
        self.assertEqual(co.fence_from_job({"task": task}), Path("builds/cdeck"))

    def test_case_insensitive_and_quoted(self):
        self.assertEqual(co.fence_from_job({"task": "Write only under `builds/z/`"}),
                         Path("builds/z"))

    def test_absent_fence_is_none(self):
        self.assertIsNone(co.fence_from_job({"task": "do a thing"}))


class ArtifactWindow(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="cc_ev_"))
        self.addCleanup(shutil.rmtree, self.d, True)

    def _touch(self, rel: str, mtime: float, body: str = "x") -> Path:
        p = self.d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
        os.utime(p, (mtime, mtime))
        return p

    def test_only_files_inside_the_window_count(self):
        now = time.time()
        self._touch("in_window.txt", now - 100)
        self._touch("before_the_run.txt", now - 5000)   # pre-existing
        self._touch("after_the_run.txt", now + 5000)    # a LATER job's output
        got = co.scan_artifacts(self.d, now - 200, now - 50)
        self.assertEqual([f["path"] for f in got["files"]], ["in_window.txt"])
        self.assertEqual(got["count"], 1)

    def test_noise_directories_are_not_evidence(self):
        now = time.time()
        self._touch("real.txt", now)
        for junk in ("__pycache__/a.pyc", "node_modules/b.js", ".git/c", "_delme/d.py"):
            self._touch(junk, now)
        got = co.scan_artifacts(self.d, now - 60, now + 60)
        self.assertEqual([f["path"] for f in got["files"]], ["real.txt"])

    def test_missing_fence_is_reported_not_raised(self):
        got = co.scan_artifacts(self.d / "nope", 0, time.time())
        self.assertFalse(got["exists"])
        self.assertEqual(got["count"], 0)

    def test_claim_verification_catches_fabricated_compliance(self):
        """The failure class canon calls the worst of all: a report that claims
        files it never wrote. The claim is checked against disk, not believed."""
        now = time.time()
        self._touch("really_written.txt", now)
        self._touch("stale.txt", now - 9000)
        rows = co.verify_claimed(
            {"files": ["really_written.txt", "stale.txt", "never_existed.txt"]},
            self.d, now - 60, now + 60)
        self.assertEqual([r["state"] for r in rows], ["verified", "stale", "missing"])


class Verdicts(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="cc_v_"))
        self.addCleanup(shutil.rmtree, self.d, True)
        self.t0 = time.time() - 10
        self.t1 = time.time()

    def _c(self, **kw):
        base = dict(rc=0, timed_out=False, exception=None, stdout="", stderr="",
                    t0=self.t0, t1=self.t1, fence=self.d, base=self.d)
        base.update(kw)
        return co.classify(**base)

    def test_every_outcome_has_a_route_and_a_requeue(self):
        self.assertEqual(set(co.OUTCOMES), set(co.ROUTE))
        self.assertEqual(set(co.OUTCOMES), set(co.REQUEUE))

    def test_timeout_splits_on_work_not_on_the_clock(self):
        """The clock is the same in both. Only the work differs."""
        empty = self._c(rc=None, timed_out=True)
        self.assertEqual(empty["outcome"], "TIMED_OUT_NO_OUTPUT")
        self.assertEqual(empty["route"], "failed")

        (self.d / "deliverable.md").write_text("landed", encoding="utf-8")
        productive = self._c(rc=None, timed_out=True)
        self.assertEqual(productive["outcome"], "TIMED_OUT_WITH_OUTPUT")
        self.assertEqual(productive["route"], "timed_out")
        self.assertTrue(productive["work_landed"])

    def test_report_alone_counts_as_output(self):
        """The agent finished and said so; the kill landed after. Artifacts may
        live outside any fence we can see, but the report is proof it ran."""
        v = self._c(rc=None, timed_out=True, stdout='{"status":"ok","files":[]}')
        self.assertEqual(v["outcome"], "TIMED_OUT_WITH_OUTPUT")

    def test_nonzero_rc_is_a_crash_not_a_timeout(self):
        v = self._c(rc=3)
        self.assertEqual(v["outcome"], "CRASHED")
        self.assertFalse(v["process"]["timed_out"])

    def test_max_turns_with_artifacts_is_not_a_failure(self):
        """THE 370 DEFECT. GBW hit --max-turns 60, rc=1, timed_out=False, and
        left 15 artifacts on disk. Filing that CRASHED records a resource limit
        as a work failure -- the same error F-59 closed for the wall clock."""
        (self.d / "deliverable.md").write_text("landed during the run", encoding="utf-8")
        v = self._c(rc=1, stderr=_MAX_TURNS_STDERR)
        self.assertNotEqual(v["outcome"], "CRASHED",
                            "a max-turns exit with artifacts on disk was filed "
                            "CRASHED -- this is the 370_gbw_infra_next16 defect")
        self.assertNotEqual(v["route"], "failed",
                            "a max-turns exit with deliverables must not file to "
                            "failed/ -- that under-reports completed work")
        self.assertEqual(v["outcome"], "MAX_TURNS_WITH_OUTPUT")
        self.assertEqual(v["route"], "timed_out")
        self.assertEqual(v["requeue"], "review")
        self.assertTrue(v["work_landed"])
        self.assertTrue(v["process"]["max_turns"])
        self.assertFalse(v["process"]["timed_out"])
        self.assertEqual(v["process"]["rc"], 1)

    def test_max_turns_without_output_is_still_failed(self):
        """Not a blanket amnesty: exhausting the turn budget with nothing on
        disk is still a non-delivery."""
        v = self._c(rc=1, stderr=_MAX_TURNS_STDERR)
        self.assertEqual(v["outcome"], "MAX_TURNS_NO_OUTPUT")
        self.assertEqual(v["route"], "failed")
        self.assertEqual(v["requeue"], "safe")
        self.assertFalse(v["work_landed"])
        self.assertTrue(v["process"]["max_turns"])

    def test_max_turns_does_not_swallow_a_real_crash(self):
        """A traceback on stderr is still a crash. The detector matches the
        engine's 'max turns reached' phrase, not every rc=1."""
        v = self._c(rc=1, stderr="Traceback (most recent call last):\nStubError\n")
        self.assertEqual(v["outcome"], "CRASHED")
        self.assertFalse(v["process"]["max_turns"])

    def test_refusal_needs_no_work_to_have_landed(self):
        v = self._c(rc=0, stdout='REFUSE: [FENCE] no\n{"status":"REFUSED","files":[]}')
        self.assertEqual(v["outcome"], "REFUSED")
        self.assertEqual(v["requeue"], "reorder")

    def test_a_refusal_that_shipped_work_is_not_a_refusal(self):
        (self.d / "shipped.md").write_text("but it did the work", encoding="utf-8")
        v = self._c(rc=0, stdout='REFUSE: partial\n{"status":"REFUSED","files":[]}')
        self.assertEqual(v["outcome"], "COMPLETED")

    def test_clean_exit_without_a_report_is_still_done(self):
        v = self._c(rc=0, stdout="did stuff, forgot the last line")
        self.assertEqual(v["outcome"], "COMPLETED_NO_REPORT")
        self.assertEqual(v["route"], "done")

    def test_driver_exception_is_a_crash(self):
        v = self._c(rc=None, exception="FileNotFoundError: claude")
        self.assertEqual(v["outcome"], "CRASHED")

    def test_bad_order_is_its_own_outcome(self):
        v = self._c(bad_order="NO_TASK")
        self.assertEqual(v["outcome"], "BAD_ORDER")
        self.assertEqual(v["requeue"], "reorder")

    def test_evidence_line_names_what_it_saw(self):
        (self.d / "a.md").write_text("hi", encoding="utf-8")
        v = self._c(rc=None, timed_out=True, stdout='{"status":"ok","files":["a.md"]}')
        self.assertIn("outcome=TIMED_OUT_WITH_OUTPUT", v["evidence"])
        self.assertIn("report=yes", v["evidence"])
        self.assertIn("claimed_verified=1/1", v["evidence"])
        self.assertIn("a.md", v["evidence"])

    def test_record_is_json_serialisable(self):
        json.dumps(self._c(rc=0))


class Refile(unittest.TestCase):
    """cc_refile repairs orders the pre-fix driver mis-filed. It must reach its
    verdict through the classifier -- never a hand-edit -- and must not delete."""

    def setUp(self):
        import cc_refile
        self.cc_refile = cc_refile
        self.tmp = Path(tempfile.mkdtemp(prefix="cc_rf_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.root = self.tmp / "live"
        self.repo = self.tmp / "repo"
        self.fence = self.repo / "builds" / "thing"
        self.fence.mkdir(parents=True)
        self.lane = self.root / "queue" / "_lanes" / "L"
        (self.lane / "failed").mkdir(parents=True)
        (self.lane / "returns").mkdir(parents=True)

    def _plant(self, jid: str, secs: float, produce: bool) -> None:
        """Recreate the exact on-disk shape the pre-fix driver left behind: the
        order in failed/, and a result record carrying only `error: timeout`."""
        t0 = time.time() - secs - 5
        (self.lane / "failed" / f"{jid}.json").write_text(json.dumps({
            "id": jid, "cwd": str(self.repo), "timeout": int(secs),
            "task": "CANON: write ONLY under builds/thing/. do the work.",
        }), encoding="utf-8")
        (self.lane / "returns" / f"{jid}_result.json").write_text(json.dumps({
            "agent": "CC", "id": jid, "cwd": str(self.repo), "rc": None,
            "error": "timeout", "secs": secs,
            "ts_start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
        }), encoding="utf-8")
        if produce:
            p = self.fence / "deliverable.md"
            p.write_text("landed during the run", encoding="utf-8")
            os.utime(p, (t0 + secs / 2, t0 + secs / 2))

    def test_dry_run_changes_nothing(self):
        self._plant("j1", 120, produce=True)
        out = self.cc_refile.refile(self.root, "L", "j1", apply=False)
        self.assertEqual(out["to"], "timed_out")
        self.assertTrue((self.lane / "failed" / "j1.json").exists())
        self.assertFalse((self.lane / "returns" / "j1_outcome.json").exists())

    def test_productive_timeout_moves_out_of_failed(self):
        self._plant("j2", 120, produce=True)
        out = self.cc_refile.refile(self.root, "L", "j2", apply=True)
        self.assertEqual(out["outcome"], "TIMED_OUT_WITH_OUTPUT")
        self.assertFalse((self.lane / "failed" / "j2.json").exists())
        self.assertTrue((self.lane / "timed_out" / "j2.json").exists())
        rec = json.loads((self.lane / "returns" / "j2_outcome.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["work"]["artifacts"]["count"], 1)
        self.assertFalse(rec["refiled"]["report_recoverable"],
                         "the pre-fix driver kept no stdout; that gap must be stated")

    def test_empty_timeout_stays_failed(self):
        """Not a blanket amnesty: a timeout that produced nothing is still a
        non-delivery and must not be laundered into the timed_out bucket."""
        self._plant("j3", 120, produce=False)
        out = self.cc_refile.refile(self.root, "L", "j3", apply=True)
        self.assertEqual(out["outcome"], "TIMED_OUT_NO_OUTPUT")
        self.assertTrue((self.lane / "failed" / "j3.json").exists())
        self.assertFalse((self.lane / "timed_out" / "j3.json").exists())

    def test_missing_job_refuses(self):
        out = self.cc_refile.refile(self.root, "L", "nope", apply=True)
        self.assertFalse(out["ok"])
        self.assertIn("not found", out["error"])

    def _plant_max_turns(self, jid: str, secs: float, produce: bool) -> None:
        """Recreate 370's on-disk shape: rc=1, timed_out=False, engine stderr
        'Max turns reached', order sitting in failed/."""
        t0 = time.time() - secs - 5
        (self.lane / "failed" / f"{jid}.json").write_text(json.dumps({
            "id": jid, "cwd": str(self.repo), "timeout": 2400,
            "task": "CANON: write ONLY under builds/thing/. do the work.",
        }), encoding="utf-8")
        (self.lane / "returns" / f"{jid}_result.json").write_text(json.dumps({
            "agent": "GBW", "kind": "grok-build", "engine": "gbw",
            "id": jid, "cwd": str(self.repo), "rc": 1,
            "secs": secs, "stderr_tail": _MAX_TURNS_STDERR,
            "ts_start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
        }), encoding="utf-8")
        if produce:
            p = self.fence / "deliverable.md"
            p.write_text("landed during the run", encoding="utf-8")
            os.utime(p, (t0 + secs / 2, t0 + secs / 2))

    def test_max_turns_with_artifacts_moves_out_of_failed(self):
        """cc_refile must re-file 370's shape through the classifier, not by
        hand: max-turns + artifacts leaves failed/ for timed_out/."""
        self._plant_max_turns("j370", 1228.8, produce=True)
        out = self.cc_refile.refile(self.root, "L", "j370", apply=True)
        self.assertEqual(out["outcome"], "MAX_TURNS_WITH_OUTPUT")
        self.assertEqual(out["to"], "timed_out")
        self.assertFalse((self.lane / "failed" / "j370.json").exists())
        self.assertTrue((self.lane / "timed_out" / "j370.json").exists())
        rec = json.loads((self.lane / "returns" / "j370_outcome.json").read_text(
            encoding="utf-8"))
        self.assertEqual(rec["outcome"], "MAX_TURNS_WITH_OUTPUT")
        self.assertEqual(rec["route"], "timed_out")
        self.assertTrue(rec["work_landed"])
        self.assertGreaterEqual(rec["work"]["artifacts"]["count"], 1)
        self.assertTrue(rec["process"]["max_turns"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
