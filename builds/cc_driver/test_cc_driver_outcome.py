#!/usr/bin/env py -3.14
# -*- coding: utf-8 -*-
"""The F-59 gate: cosmos_cc_driver must record the PROCESS outcome and the WORK
outcome as two different facts.

MEASURED DEFECT (2026-08-31). `live/queue/_lanes/cc-cdeck/failed/070_cdeck_mobile_parity.json`
was filed FAILED after a 2404s wall-clock kill while its deliverables were on
disk. `070_cdeck_mobile_parity_result.json` is 219 bytes and says only
`"error": "timeout"` -- no stdout sidecar, no artifact check, no report. The
driver never asked whether any work had landed, so a finished job and a job that
produced nothing were filed identically.

This suite drives the REAL driver with a REAL subprocess killed by a REAL wall
clock (`_stub_agent.py`), because the whole reason F-59 survived is that the
timeout path had never once been executed by a test.

Run:
    py -3.14 builds/cc_driver/test_cc_driver_outcome.py

Run it against the pre-fix driver staged in _delme to prove these tests FAIL
against the old code (that is the point -- a regression test nobody watched fail
is a decoration):
    CC_DRIVER_UNDER_TEST=builds/cc_driver/_delme/predispose_.../cosmos_cc_driver.py \
        py -3.14 builds/cc_driver/test_cc_driver_outcome.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUB = HERE / "_stub_agent.py"


def _driver_arg() -> str | None:
    """--driver=<path> (or $CC_DRIVER_UNDER_TEST) points the suite at another copy
    of the driver -- how the pre-fix copy in _delme is proven to fail these."""
    for i, a in enumerate(list(sys.argv[1:])):
        if a.startswith("--driver="):
            sys.argv.remove(a)
            return a.split("=", 1)[1]
        if a == "--driver" and i + 2 <= len(sys.argv) - 1:
            val = sys.argv[i + 2]
            sys.argv.remove(a)
            sys.argv.remove(val)
            return val
    return os.environ.get("CC_DRIVER_UNDER_TEST")


DRIVER = Path(_driver_arg() or (HERE / "cosmos_cc_driver.py"))
STUB_ARGV = [sys.executable, str(STUB)]
HANG = "45"      # stub hang, comfortably past the job timeout
JOB_TIMEOUT = 3  # driver wall clock for the timeout scenarios


class _ClaudeShim:
    """Redirect `claude` to the stub for a driver module that has no injection
    seam of its own. Only the PRE-FIX driver needs this; the current driver
    honours COSMOS_CC_CLAUDE_BIN and is exercised completely unpatched."""

    def __init__(self, real, argv0):
        self._real = real
        self._argv0 = list(argv0)

    def __getattr__(self, name):
        return getattr(self._real, name)

    def run(self, argv, **kw):
        if isinstance(argv, (list, tuple)) and argv and argv[0] == "claude":
            argv = self._argv0 + list(argv)[1:]
        return self._real.run(argv, **kw)


def load_driver(path: Path):
    spec = importlib.util.spec_from_file_location(f"cc_driver_under_test_{id(path)}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "claude_bin"):          # pre-fix driver: no seam
        mod.subprocess = _ClaudeShim(subprocess, STUB_ARGV)
    return mod


def run_scenario(mod, mode: str, jid: str, *, use_fence_phrase: bool = False) -> dict:
    """Drive one job end to end through the driver under test; report what is on
    disk afterwards. Nothing here asserts -- it only observes."""
    tmp = Path(tempfile.mkdtemp(prefix=f"cc_{mode}_"))
    root = tmp / "live"
    work = tmp / "work"
    fence_rel = "out"
    (work / fence_rel).mkdir(parents=True, exist_ok=True)
    root.mkdir(parents=True, exist_ok=True)

    p = mod.Paths(root, None, lane_name="t")
    p.env = {}

    task = "do the thing.\nMANDATORY LAST LINE: one JSON object."
    order = {"id": jid, "timeout": JOB_TIMEOUT, "cwd": str(work), "task": task}
    if use_fence_phrase:
        # The canonical work-order contract line -- this is how 070 declared its
        # fence, and the classifier has to read it to find the deliverables.
        order["task"] = f"CANON: write ONLY under {fence_rel}/ .\n" + task
    else:
        order["fence"] = fence_rel

    job_path = p.lane / f"{jid}.json"
    job_path.write_text(json.dumps(order), encoding="utf-8")

    prev = {k: os.environ.get(k) for k in
            ("STUB_MODE", "STUB_FENCE", "STUB_HANG", "COSMOS_CC_CLAUDE_BIN")}
    os.environ["STUB_MODE"] = mode
    os.environ["STUB_FENCE"] = str(work / fence_rel)
    os.environ["STUB_HANG"] = HANG
    os.environ["COSMOS_CC_CLAUDE_BIN"] = json.dumps(STUB_ARGV)
    t0 = time.time()
    try:
        returned = mod.run_job(p, job_path, root)
    finally:
        for k, v in prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def where() -> str:
        for name in ("done", "failed", "timed_out"):
            if (p.lane / name / f"{jid}.json").exists():
                return name
        return "MISSING"

    def load(name: str):
        fp = p.returns / name
        if not fp.exists():
            return None
        try:
            return json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            return None

    sidecar = p.returns / f"{jid}_result.json.stdout.txt"
    return {
        "tmp": tmp, "filed": where(), "returned": returned,
        "wall": round(time.time() - t0, 1),
        "result": load(f"{jid}_result.json"),
        "outcome": load(f"{jid}_outcome.json"),
        "stdout": sidecar.read_text(encoding="utf-8") if sidecar.exists() else None,
        "deliverable": (work / fence_rel / "stub_deliverable.txt").exists(),
    }


class DriverOutcome(unittest.TestCase):
    scenarios: dict = {}

    @classmethod
    def setUpClass(cls):
        if not DRIVER.exists():
            raise unittest.SkipTest(f"driver not found: {DRIVER}")
        cls.mod = load_driver(DRIVER)
        cls.scenarios = {
            "timeout_with_output": run_scenario(cls.mod, "timeout_with_output",
                                                "j_to_out", use_fence_phrase=True),
            "timeout_no_output": run_scenario(cls.mod, "timeout_no_output", "j_to_nil"),
            "complete": run_scenario(cls.mod, "complete", "j_done"),
            "refuse": run_scenario(cls.mod, "refuse", "j_refuse"),
            "crash": run_scenario(cls.mod, "crash", "j_crash"),
        }

    @classmethod
    def tearDownClass(cls):
        for s in cls.scenarios.values():
            shutil.rmtree(s["tmp"], ignore_errors=True)

    def s(self, name):
        return self.scenarios[name]

    # -- the defect itself -------------------------------------------------
    def test_timeout_with_deliverables_is_not_filed_failed(self):
        """THE F-59 DEFECT. The stub wrote its deliverable and emitted its report
        BEFORE the wall clock killed it. Filing that in failed/ records the
        process outcome as the work outcome."""
        s = self.s("timeout_with_output")
        self.assertTrue(s["deliverable"], "stub never wrote its deliverable")
        self.assertNotEqual(s["filed"], "failed",
                            "a timeout with deliverables on disk was filed FAILED "
                            "-- this is the 070_cdeck_mobile_parity defect")
        self.assertEqual(s["filed"], "timed_out")

    def test_timeout_with_output_is_typed(self):
        s = self.s("timeout_with_output")
        self.assertIsNotNone(s["outcome"], "no typed outcome record was written")
        self.assertEqual(s["outcome"]["outcome"], "TIMED_OUT_WITH_OUTPUT")
        self.assertTrue(s["outcome"]["work_landed"])
        self.assertEqual(s["outcome"]["requeue"], "review")

    def test_outcome_is_a_type_not_a_boolean(self):
        """Every terminal state names itself. `ok=False` cannot tell a killed
        agent from a crashed one from one that declined."""
        got = {k: (v["outcome"] or {}).get("outcome") for k, v in self.scenarios.items()}
        self.assertEqual(got, {
            "timeout_with_output": "TIMED_OUT_WITH_OUTPUT",
            "timeout_no_output": "TIMED_OUT_NO_OUTPUT",
            "complete": "COMPLETED",
            "refuse": "REFUSED",
            "crash": "CRASHED",
        })
        self.assertEqual(len(set(got.values())), 5, "outcomes must be distinguishable")

    def test_productive_and_empty_timeouts_are_distinguishable(self):
        """Requirement 4: the two timeouts must not be the same record."""
        a, b = self.s("timeout_with_output"), self.s("timeout_no_output")
        self.assertNotEqual(a["outcome"]["outcome"], b["outcome"]["outcome"])
        self.assertNotEqual(a["filed"], b["filed"])
        self.assertTrue(a["outcome"]["work_landed"])
        self.assertFalse(b["outcome"]["work_landed"])
        self.assertGreater(a["outcome"]["work"]["artifacts"]["count"], 0)
        self.assertEqual(b["outcome"]["work"]["artifacts"]["count"], 0)

    # -- evidence gathered before filing -----------------------------------
    def test_partial_stdout_is_recovered_from_the_kill(self):
        """The killed process's stdout is the only place the MANDATORY LAST LINE
        report survives. The pre-fix driver discarded it and wrote no sidecar."""
        s = self.s("timeout_with_output")
        self.assertIsNotNone(s["stdout"], "no stdout sidecar written for a timeout")
        self.assertIn('"status":"ok"', s["stdout"])

    def test_mandatory_last_line_report_is_parsed_and_recorded(self):
        s = self.s("timeout_with_output")
        rep = s["outcome"]["work"]["report"]
        self.assertIsInstance(rep, dict, "last-line JSON report was not parsed")
        self.assertEqual(rep["gate_passed"], 93)

    def test_claimed_files_are_verified_against_disk(self):
        """A claim is not evidence: the report's own `files` list is checked for
        existence AND for an mtime inside the run window."""
        s = self.s("timeout_with_output")
        claimed = s["outcome"]["work"]["claimed_files"]
        self.assertTrue(claimed, "report claimed files but none were checked")
        self.assertEqual([c["state"] for c in claimed], ["verified"])
        self.assertEqual(s["outcome"]["work"]["claimed_missing"], 0)

    def test_artifacts_bound_to_the_run_window(self):
        s = self.s("timeout_with_output")
        arts = s["outcome"]["work"]["artifacts"]
        self.assertEqual([f["path"] for f in arts["files"]], ["stub_deliverable.txt"])
        self.assertGreater(arts["bytes"], 0)

    def test_fence_read_from_the_work_order_contract_line(self):
        """070 declared its fence only as 'write ONLY under builds/cdeck/'. If the
        classifier cannot read that, it cannot find the deliverables."""
        s = self.s("timeout_with_output")
        self.assertTrue(s["outcome"]["work"]["artifacts"]["fence"].endswith("out"))

    # -- the other outcomes stay correct -----------------------------------
    def test_completed_still_files_done(self):
        s = self.s("complete")
        self.assertEqual(s["filed"], "done")
        self.assertTrue(s["returned"])

    def test_refusal_is_not_a_crash(self):
        s = self.s("refuse")
        self.assertEqual(s["outcome"]["outcome"], "REFUSED")
        self.assertEqual(s["filed"], "failed")
        self.assertEqual(s["outcome"]["requeue"], "reorder",
                         "re-running an order the agent refused will refuse again")

    def test_crash_is_not_a_timeout(self):
        s = self.s("crash")
        self.assertEqual(s["outcome"]["outcome"], "CRASHED")
        self.assertEqual(s["outcome"]["process"]["rc"], 3)
        self.assertFalse(s["outcome"]["process"]["timed_out"])
        self.assertEqual(s["outcome"]["requeue"], "safe")

    def test_result_carries_the_evidence_line(self):
        """No fabricated compliance: the result file states WHY it was classified
        that way, in terms of what the run emitted."""
        s = self.s("timeout_with_output")
        ev = s["result"].get("evidence", "")
        self.assertIn("outcome=TIMED_OUT_WITH_OUTPUT", ev)
        self.assertIn("report=yes", ev)
        self.assertIn("artifacts=1/", ev)


if __name__ == "__main__":
    print(f"[test_cc_driver_outcome] driver under test: {DRIVER}")
    unittest.main(verbosity=2)
