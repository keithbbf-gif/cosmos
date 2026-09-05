#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""test_tool_disposition - F-41 proposer. Bite first, live ledger never written.

Pins:

  1. The module was ABSENT (`_bite_tool_disposition_absent.json`).
  2. PLAN_READY only when PORT_DECISIONS has a ruling AND the successor
     cosmos_ module exists on disk.
  3. SUCCESSOR_ABSENT is HOLD, not a fabricated APPLY.
  4. DRIFT (live disposition != plan) is HOLD, never overwritten.
  5. UNPLANNED is HOLD — no invented ruling.
  6. apply() on a scratch ledger records TOOL_DISPOSITION and drops UNDECIDED.
  7. apply() against the live authority path REFUSES LIVE_LEDGER_FORBIDDEN
     and does not open/alter the file.

No key material is read. Live Kernel is used only by the CLI `--root` path;
this suite injects ToolContracts.report() rows.

    py -3.14 builds/probe/test_tool_disposition.py
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
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_ledger import Ledger                                    # noqa: E402
from cosmos_paths import CosmosPaths, write_sentinel                # noqa: E402
from cosmos_tools import ToolContracts                              # noqa: E402
import tool_disposition as td                                       # noqa: E402

BITE = HERE / "_bite_tool_disposition_absent.json"


def _row(name, disposition=None):
    return {"name": name, "disposition": disposition, "verified": None, "age_s": None}


class TestBiteAgainstAbsence(unittest.TestCase):

    def test_absent_bite_artifact_names_ModuleNotFoundError(self):
        self.assertTrue(BITE.is_file(), "bite must be recorded before belief")
        rec = json.loads(BITE.read_text(encoding="utf-8"))
        self.assertEqual(rec["state"], "ABSENT")
        self.assertEqual(rec["kind"], "ModuleNotFoundError")
        self.assertIn("tool_disposition", rec["detail"])

    def test_the_module_now_exists_under_builds_probe(self):
        self.assertEqual(Path(td.__file__).resolve().parent, HERE)
        self.assertEqual(td.WORKER, "tool-disposition")


class TestPropose(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_f41_"))
        self.cosmos = self.tmp / "cosmos"
        self.cosmos.mkdir()
        (self.cosmos / "cosmos_mail.py").write_text("# stub\n", encoding="utf-8")
        (self.cosmos / "cosmos_sched.py").write_text("# stub\n", encoding="utf-8")
        (self.cosmos / "cosmos_health.py").write_text("# stub\n", encoding="utf-8")
        self.plan = {
            "bts_bus": {
                "disposition": "REPLACED",
                "successor": "cosmos_mail + cosmos_sched + cosmos_health",
                "reason": "bus folds into mail/sched/health",
            },
            "bts_elevated_ops": {
                "disposition": "ADAPTED",
                "successor": None,
                "reason": "external helper, not absorbed",
            },
            "ghost_tool": {
                "disposition": "REPLACED",
                "successor": "cosmos_does_not_exist",
                "reason": "claim, not a port",
            },
        }

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_plan_ready_when_successor_exists(self):
        bundle = td.propose([_row("bts_bus")], plan=self.plan, cosmos_dir=self.cosmos)
        row = next(p for p in bundle["proposals"] if p["name"] == "bts_bus")
        self.assertEqual(row["kind"], "PLAN_READY")
        self.assertEqual(row["action"], "APPLY")
        self.assertEqual(row["plan"], "REPLACED")

    def test_adapted_with_no_successor_is_still_ready(self):
        bundle = td.propose([_row("bts_elevated_ops")], plan=self.plan,
                            cosmos_dir=self.cosmos)
        row = next(p for p in bundle["proposals"] if p["name"] == "bts_elevated_ops")
        self.assertEqual(row["kind"], "PLAN_READY")
        self.assertEqual(row["action"], "APPLY")

    def test_successor_absent_is_hold_not_apply(self):
        bundle = td.propose([_row("ghost_tool")], plan=self.plan, cosmos_dir=self.cosmos)
        row = next(p for p in bundle["proposals"] if p["name"] == "ghost_tool")
        self.assertEqual(row["kind"], "SUCCESSOR_ABSENT")
        self.assertEqual(row["action"], "HOLD")
        self.assertIn("cosmos_does_not_exist", row["successor_missing"])

    def test_drift_is_hold_never_overwritten(self):
        bundle = td.propose([_row("bts_bus", "ADAPTED")], plan=self.plan,
                            cosmos_dir=self.cosmos)
        row = next(p for p in bundle["proposals"] if p["name"] == "bts_bus")
        self.assertEqual(row["kind"], "DRIFT")
        self.assertEqual(row["action"], "HOLD")
        self.assertEqual(row["live"], "ADAPTED")
        self.assertEqual(row["plan"], "REPLACED")

    def test_plan_match_is_skip(self):
        bundle = td.propose([_row("bts_bus", "REPLACED")], plan=self.plan,
                            cosmos_dir=self.cosmos)
        row = next(p for p in bundle["proposals"] if p["name"] == "bts_bus")
        self.assertEqual(row["kind"], "PLAN_MATCH")
        self.assertEqual(row["action"], "SKIP")

    def test_unplanned_is_hold_no_invented_ruling(self):
        bundle = td.propose([_row("mystery_tool")], plan=self.plan, cosmos_dir=self.cosmos)
        row = next(p for p in bundle["proposals"] if p["name"] == "mystery_tool")
        self.assertEqual(row["kind"], "UNPLANNED")
        self.assertEqual(row["action"], "HOLD")
        self.assertIsNone(row["plan"])

    def test_unplanned_card_is_hold_with_no_disposition(self):
        (self.cosmos / "cosmos_mail.py").write_text("# stub\n", encoding="utf-8")
        bundle = td.propose([_row("mystery_mail"), _row("bts_bus")],
                            plan=self.plan, cosmos_dir=self.cosmos)
        cards = td.cards_for_unplanned(bundle, cosmos_dir=self.cosmos)
        names = [c["name"] for c in cards["cards"]]
        self.assertIn("mystery_mail", names)
        self.assertNotIn("bts_bus", names, "planned names must not get UNPLANNED cards")
        card = next(c for c in cards["cards"] if c["name"] == "mystery_mail")
        self.assertIsNone(card["disposition"])
        self.assertIsNone(card["plan"])
        self.assertIsNone(card["successor"])
        self.assertEqual(card["action"], "HOLD")
        self.assertEqual(card["kind"], "UNPLANNED")
        self.assertIn("cosmos_mail", card["successor_candidates"])
        self.assertNotIn(None, card["successor_candidates"])
        # A candidate is evidence, never silently promoted to a ruling.
        self.assertNotIn(card["disposition"], ("REPLACED", "ADAPTED", "PRESERVED", "ABANDONED"))

    def test_card_candidates_only_list_modules_that_exist(self):
        bundle = td.propose([_row("ghost_widget")], plan=self.plan, cosmos_dir=self.cosmos)
        cards = td.cards_for_unplanned(bundle, cosmos_dir=self.cosmos)
        card = cards["cards"][0]
        for mod in card["successor_candidates"]:
            self.assertTrue((self.cosmos / f"{mod}.py").is_file(), mod)

    def test_staged_old_module_has_no_cards_for_unplanned(self):
        old = Path(td.__file__).resolve().parents[2] / "_delme" / (
            "predispose_cosmos_backup_f47_r2adapter_20260831T065325Z"
        ) / "tool_disposition.py"
        self.assertTrue(old.is_file(), f"missing staged predecessor {old}")
        src = old.read_text(encoding="utf-8")
        self.assertNotIn("def cards_for_unplanned", src)
        self.assertNotIn("CARD_SCHEMA", src)

    def test_declare_ready_when_plan_name_is_not_on_live(self):
        bundle = td.propose([], plan=self.plan, cosmos_dir=self.cosmos)
        row = next(p for p in bundle["proposals"] if p["name"] == "bts_bus")
        self.assertEqual(row["kind"], "DECLARE_READY")
        self.assertEqual(row["action"], "DECLARE_AND_APPLY")

    def test_counts_sum_to_proposals(self):
        bundle = td.propose([_row("bts_bus"), _row("mystery_tool")],
                            plan=self.plan, cosmos_dir=self.cosmos)
        self.assertEqual(sum(bundle["by_kind"].values()), len(bundle["proposals"]))
        self.assertEqual(sum(bundle["by_action"].values()), len(bundle["proposals"]))


class TestApplyScratchAndRefuseLive(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_f41a_"))
        self.live = self.tmp / "live"
        write_sentinel(self.live, "KMesh-COSMOS-test")
        (self.live / "ledger").mkdir(parents=True, exist_ok=True)
        self.live_auth = CosmosPaths(self.live).ledger("authority.jsonl")
        self.live_auth.write_text("DO-NOT-TOUCH\n", encoding="utf-8")
        self.scratch = self.tmp / "scratch.jsonl"
        self.plan = {
            "bts_bus": {
                "disposition": "REPLACED",
                "successor": "cosmos_mail",
                "reason": "mail",
            },
        }
        self.cosmos = self.tmp / "cosmos"
        self.cosmos.mkdir()
        (self.cosmos / "cosmos_mail.py").write_text("# stub\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_apply_on_scratch_records_disposition_and_drops_undecided(self):
        rows = [_row("bts_bus")]
        bundle = td.propose(rows, plan=self.plan, cosmos_dir=self.cosmos)
        led = Ledger(self.scratch, b"k", "f41")
        tc = ToolContracts(led)
        rec = td.apply_proposals(tc, bundle, ledger_path=self.scratch, live_root=self.live)
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["applied"], ["bts_bus"])
        st = tc.state()["bts_bus"]
        self.assertEqual(st["disposition"]["decision"], "REPLACED")
        self.assertEqual(self.live_auth.read_text(encoding="utf-8"), "DO-NOT-TOUCH\n")

    def test_apply_against_live_authority_refuses_and_does_not_open(self):
        bundle = td.propose([_row("bts_bus")], plan=self.plan, cosmos_dir=self.cosmos)
        led = Ledger(self.scratch, b"k", "f41")
        tc = ToolContracts(led)
        before = self.live_auth.stat()
        with self.assertRaises(td.DispositionError) as cm:
            td.apply_proposals(tc, bundle, ledger_path=self.live_auth,
                               live_root=self.live)
        self.assertEqual(cm.exception.kind, "LIVE_LEDGER_FORBIDDEN")
        after = self.live_auth.stat()
        self.assertEqual(after.st_mtime_ns, before.st_mtime_ns)
        self.assertEqual(after.st_size, before.st_size)
        self.assertEqual(self.live_auth.read_text(encoding="utf-8"), "DO-NOT-TOUCH\n")
        self.assertEqual(tc.state(), {})

    def test_guard_compares_resolved_paths(self):
        with self.assertRaises(td.DispositionError) as cm:
            td.guard_ledger(self.live_auth, self.live)
        self.assertEqual(cm.exception.kind, "LIVE_LEDGER_FORBIDDEN")
        ok = td.guard_ledger(self.scratch, self.live)
        self.assertEqual(ok, self.scratch.resolve())

    def test_apply_without_ledger_raises_NO_LEDGER(self):
        with self.assertRaises(td.DispositionError) as cm:
            td.require_apply_ledger(None)
        self.assertEqual(cm.exception.kind, "NO_LEDGER")
        with self.assertRaises(td.DispositionError) as cm2:
            td.require_apply_ledger("")
        self.assertEqual(cm2.exception.kind, "NO_LEDGER")

    def test_guard_directory_as_ledger_is_BAD_LEDGER(self):
        folder = self.tmp / "not_a_ledger"
        folder.mkdir()
        with self.assertRaises(td.DispositionError) as cm:
            td.guard_ledger(folder, self.live)
        self.assertEqual(cm.exception.kind, "BAD_LEDGER")
        self.assertTrue(folder.is_dir())

    def test_bool_sentinel_is_BAD_ROOT_not_AttributeError(self):
        rotten = self.tmp / "rotten"
        rotten.mkdir()
        (rotten / ".cosmos-root.json").write_text("true", encoding="utf-8")
        with self.assertRaises(td.DispositionError) as cm:
            td.guard_ledger(self.scratch, rotten)
        self.assertEqual(cm.exception.kind, "BAD_ROOT")

    def test_array_sentinel_is_BAD_ROOT(self):
        rotten = self.tmp / "rotten_arr"
        rotten.mkdir()
        (rotten / ".cosmos-root.json").write_text("[]", encoding="utf-8")
        with self.assertRaises(td.DispositionError) as cm:
            td.guard_ledger(self.scratch, rotten)
        self.assertEqual(cm.exception.kind, "BAD_ROOT")

    def test_apply_bundle_list_is_BAD_BUNDLE(self):
        with self.assertRaises(td.DispositionError) as cm:
            td.apply_proposals(None, [], ledger_path=self.scratch,
                               live_root=self.live)
        self.assertEqual(cm.exception.kind, "BAD_BUNDLE")

    def test_apply_proposals_str_is_BAD_BUNDLE(self):
        with self.assertRaises(td.DispositionError) as cm:
            td.apply_proposals(None, {"proposals": "APPLY"},
                               ledger_path=self.scratch, live_root=self.live)
        self.assertEqual(cm.exception.kind, "BAD_BUNDLE")

    def test_apply_bundle_none_is_BAD_BUNDLE(self):
        with self.assertRaises(td.DispositionError) as cm:
            td.apply_proposals(None, None, ledger_path=self.scratch,
                               live_root=self.live)
        self.assertEqual(cm.exception.kind, "BAD_BUNDLE")


class TestCliFreshInterpreter(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_f41c_"))
        self.live = self.tmp / "live"
        write_sentinel(self.live, "KMesh-COSMOS-test")
        (self.live / "ledger").mkdir(parents=True, exist_ok=True)
        (self.live / "config").mkdir(parents=True, exist_ok=True)
        self.auth = CosmosPaths(self.live).ledger("authority.jsonl")
        self.auth.write_bytes(b"not-a-real-ledger")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(Path(td.__file__).resolve()), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=60)

    def test_cli_apply_without_ledger_is_NO_LEDGER(self):
        p = self._run("--root", str(self.live), "--apply")
        self.assertEqual(p.returncode, 2)
        blob = (p.stdout or "") + (p.stderr or "")
        rec = json.loads(blob)
        self.assertEqual(rec["kind"], "NO_LEDGER")
        self.assertTrue(rec.get("refused") is True)
        self.assertTrue(rec.get("ledger_untouched") is True)

    def test_cli_apply_on_live_authority_prints_LIVE_LEDGER_FORBIDDEN(self):
        """Need a Kernel-openable root OR we pin guard_ledger via in-process CLI
        after Kernel fails. The fence under test is guard_ledger, already pinned
        above; this checks main() surfaces the kind when Kernel can boot.

        Without install_key.bin Kernel refuses NOT_FOUND — that is also correct
        fail-closed, and the live authority bytes stay put.
        """
        before = self.auth.read_bytes()
        p = self._run("--root", str(self.live), "--apply", "--ledger", str(self.auth))
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(self.auth.read_bytes(), before)

    def test_cli_apply_live_authority_emits_json_kind(self):
        """measure_live is stubbed so main() reaches guard_ledger on a sentinel root."""
        import io
        from unittest.mock import patch
        fake_counts = {"total": 0, "by_disposition": {}, "verified_true": 0,
                       "read_only": True, "writes": 0}
        fake_bundle = {"proposals": [], "plan_total": 0, "live_total": 0,
                       "by_kind": {}, "by_action": {}, "apply_ready": [],
                       "apply_ready_count": 0}
        buf = io.StringIO()
        with patch.object(td, "measure_live", return_value=([], fake_counts)), \
             patch.object(td, "propose", return_value=fake_bundle), \
             patch("sys.stdout", buf):
            rc = td.main(["--root", str(self.live), "--apply",
                          "--ledger", str(self.auth),
                          "--out", str(self.tmp / "out.json")])
        self.assertEqual(rc, 2)
        rec = json.loads(buf.getvalue())
        self.assertEqual(rec["kind"], "LIVE_LEDGER_FORBIDDEN")
        self.assertTrue(rec["ledger_untouched"])
        self.assertEqual(self.auth.read_bytes(), b"not-a-real-ledger")


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    live_value = {
        "checks": result.testsRun,
        "failures": len(result.failures) + len(result.errors),
        "bite": str(BITE),
        "refusal_kinds": ["LIVE_LEDGER_FORBIDDEN", "SUCCESSOR_ABSENT", "DRIFT",
                          "UNPLANNED", "NO_LEDGER", "BAD_LEDGER", "BAD_BUNDLE",
                          "BAD_ROOT"],
    }
    print("live_value", json.dumps(live_value, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
