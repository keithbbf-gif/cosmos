#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Portfolio Studio PS-06: product/stage tags on spend and scheduler evidence."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_ledger import Ledger  # noqa: E402
from cosmos_portfolio_attribution import (  # noqa: E402
    UNATTRIBUTED,
    UNMEASURED,
    _selftest as attribution_selftest,
    fold_spend_by_product,
    read_tags,
)
from cosmos_sched import SchedError, Scheduler  # noqa: E402
from cosmos_spend import SpendError, SpendGate  # noqa: E402


class TestPortfolioSpendAttribution(unittest.TestCase):
    def test_attribution_module_selftest(self):
        self.assertEqual(attribution_selftest(), 0)

    def test_sched_submit_carries_validated_tags(self):
        td = Path(tempfile.mkdtemp(prefix="ps06_sched_"))
        root = install(td / "live", tree_id="ps06-sched")
        key = (root / "config" / "install_key.bin").read_bytes()
        sched = Scheduler(root / "queue", key, "w1")
        jid = sched.submit("echo hi", product="forge", stage="build")
        st = sched._state()[jid]["m"]
        self.assertEqual(st["product"], "forge")
        self.assertEqual(st["stage"], "build")
        self.assertEqual(read_tags(st)["attribution"], "TAGGED")

    def test_sched_submit_untagged_stays_unattributed(self):
        td = Path(tempfile.mkdtemp(prefix="ps06_sched_u_"))
        root = install(td / "live", tree_id="ps06-sched-u")
        key = (root / "config" / "install_key.bin").read_bytes()
        sched = Scheduler(root / "queue", key, "w1")
        jid = sched.submit("crucible:round research")
        st = sched._state()[jid]["m"]
        tags = read_tags(st)
        self.assertEqual(tags["attribution"], UNATTRIBUTED)
        self.assertNotIn("product", st)
        self.assertNotIn("stage", st)

    def test_sched_rejects_partial_and_unknown_tags(self):
        td = Path(tempfile.mkdtemp(prefix="ps06_sched_p_"))
        root = install(td / "live", tree_id="ps06-sched-p")
        key = (root / "config" / "install_key.bin").read_bytes()
        sched = Scheduler(root / "queue", key, "w1")
        with self.assertRaises(SchedError) as cm:
            sched.submit("x", product="forge")
        self.assertEqual(cm.exception.kind, "BAD_INPUT")
        with self.assertRaises(SchedError) as cm2:
            sched.submit("x", product="chatbot", stage="build")
        self.assertEqual(cm2.exception.kind, "BAD_INPUT")

    def test_spend_guarded_call_stamps_tags_on_settle(self):
        td = Path(tempfile.mkdtemp(prefix="ps06_spend_"))
        root = install(td / "live", tree_id="ps06-spend")
        key = (root / "config" / "install_key.bin").read_bytes()
        ledger = Ledger(root / "ledger" / "authority.jsonl", key, "w1")
        gate = SpendGate(ledger)
        gate.set_budget("rail-a", 10.0)
        out = gate.guarded_call(
            "rail-a", 0.5, lambda: {"usd": 0.25},
            product="docket", stage="research",
        )
        self.assertEqual(out.get("product"), "docket")
        settled = [r for r in ledger.verify() if r["event"] == "SPEND_SETTLED"]
        self.assertEqual(len(settled), 1)
        p = settled[0]["payload"]
        self.assertEqual(p["product"], "docket")
        self.assertEqual(p["stage"], "research")
        fold = gate.audit_by_product()
        row = next(x for x in fold["products"] if x["product"] == "docket")
        self.assertEqual(row["kind"], "MEASURED")
        self.assertEqual(row["settled_usd"], 0.25)
        other = next(x for x in fold["products"] if x["product"] == "forge")
        self.assertEqual(other["kind"], UNMEASURED)
        self.assertIsNone(other["settled_usd"])

    def test_spend_historic_untagged_not_allocated(self):
        td = Path(tempfile.mkdtemp(prefix="ps06_spend_h_"))
        root = install(td / "live", tree_id="ps06-spend-h")
        key = (root / "config" / "install_key.bin").read_bytes()
        ledger = Ledger(root / "ledger" / "authority.jsonl", key, "w1")
        gate = SpendGate(ledger)
        gate.set_budget("rail-b", 5.0)
        gate.guarded_call("rail-b", 1.0, lambda: {"usd": 1.0})
        fold = fold_spend_by_product(list(ledger.verify()))
        self.assertTrue(all(r["kind"] == UNMEASURED for r in fold["products"]))
        self.assertTrue(all(r["settled_usd"] is None for r in fold["products"]))

    def test_spend_rejects_partial_tags_as_bad_input(self):
        td = Path(tempfile.mkdtemp(prefix="ps06_spend_pt_"))
        root = install(td / "live", tree_id="ps06-spend-pt")
        key = (root / "config" / "install_key.bin").read_bytes()
        ledger = Ledger(root / "ledger" / "authority.jsonl", key, "w1")
        gate = SpendGate(ledger)
        gate.set_budget("rail-c", 5.0)
        with self.assertRaises(SpendError) as cm:
            gate.guarded_call(
                "rail-c", 0.1, lambda: {"usd": 0.1}, product="forge")
        self.assertEqual(cm.exception.kind, "BAD_INPUT")


if __name__ == "__main__":
    unittest.main()
