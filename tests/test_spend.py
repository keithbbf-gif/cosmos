#!/usr/bin/env python3
"""Portfolio Studio PS-06: product/stage tags on spend and scheduler evidence."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_portfolio_attribution import (  # noqa: E402
    UNATTRIBUTED,
    UNMEASURED,
    _selftest as attribution_selftest,
    fold_spend_by_product,
    read_tags,
)
from cosmos_sched import Scheduler, SchedError  # noqa: E402
from cosmos_spend import SpendError, SpendGate  # noqa: E402


def test_attribution_module_selftest():
    assert attribution_selftest() == 0


def test_sched_submit_carries_validated_tags():
    td = Path(tempfile.mkdtemp(prefix="ps06_sched_"))
    root = install(td / "live", tree_id="ps06-sched")
    key = (root / "config" / "install_key.bin").read_bytes()
    sched = Scheduler(root / "queue", key, "w1")
    jid = sched.submit("echo hi", product="forge", stage="build")
    st = sched._state()[jid]["m"]
    assert st["product"] == "forge" and st["stage"] == "build"
    tags = read_tags(st)
    assert tags["attribution"] == "TAGGED"


def test_sched_submit_untagged_stays_unattributed():
    td = Path(tempfile.mkdtemp(prefix="ps06_sched_u_"))
    root = install(td / "live", tree_id="ps06-sched-u")
    key = (root / "config" / "install_key.bin").read_bytes()
    sched = Scheduler(root / "queue", key, "w1")
    jid = sched.submit("echo hi")
    st = sched._state()[jid]["m"]
    assert read_tags(st)["attribution"] == UNATTRIBUTED


def test_sched_rejects_partial_tags():
    td = Path(tempfile.mkdtemp(prefix="ps06_sched_p_"))
    root = install(td / "live", tree_id="ps06-sched-p")
    key = (root / "config" / "install_key.bin").read_bytes()
    sched = Scheduler(root / "queue", key, "w1")
    try:
        sched.submit("x", product="forge")
        assert False, "expected SchedError"
    except SchedError as e:
        assert e.kind == "BAD_INPUT"


def test_spend_guarded_call_stamps_tags_on_settle():
    td = Path(tempfile.mkdtemp(prefix="ps06_spend_"))
    root = install(td / "live", tree_id="ps06-spend")
    key = (root / "config" / "install_key.bin").read_bytes()
    from cosmos_ledger import Ledger
    ledger = Ledger(root / "ledger" / "authority.jsonl", key, "w1")
    gate = SpendGate(ledger)
    gate.set_budget("rail-a", 10.0)
    gate.guarded_call(
        "rail-a", 0.5, lambda: {"usd": 0.25},
        product="docket", stage="research",
    )
    settled = [r for r in ledger.verify() if r["event"] == "SPEND_SETTLED"]
    assert len(settled) == 1
    p = settled[0]["payload"]
    assert p["product"] == "docket" and p["stage"] == "research"
    fold = gate.audit_by_product()
    row = next(x for x in fold["products"] if x["product"] == "docket")
    assert row["kind"] == "MEASURED" and row["settled_usd"] == 0.25
    other = next(x for x in fold["products"] if x["product"] == "forge")
    assert other["kind"] == UNMEASURED and other["settled_usd"] is None


def test_spend_historic_untagged_not_allocated():
    td = Path(tempfile.mkdtemp(prefix="ps06_spend_h_"))
    root = install(td / "live", tree_id="ps06-spend-h")
    key = (root / "config" / "install_key.bin").read_bytes()
    from cosmos_ledger import Ledger
    ledger = Ledger(root / "ledger" / "authority.jsonl", key, "w1")
    gate = SpendGate(ledger)
    gate.set_budget("rail-b", 5.0)
    gate.guarded_call("rail-b", 1.0, lambda: {"usd": 1.0})
    fold = fold_spend_by_product(ledger.verify())
    assert all(r["kind"] == UNMEASURED for r in fold["products"])


def test_spend_rejects_partial_tags():
    td = Path(tempfile.mkdtemp(prefix="ps06_spend_pt_"))
    root = install(td / "live", tree_id="ps06-spend-pt")
    key = (root / "config" / "install_key.bin").read_bytes()
    from cosmos_ledger import Ledger
    ledger = Ledger(root / "ledger" / "authority.jsonl", key, "w1")
    gate = SpendGate(ledger)
    gate.set_budget("rail-c", 5.0)
    try:
        gate.guarded_call("rail-c", 0.1, lambda: {"usd": 0.1}, product="forge")
        assert False
    except SpendError:
        pass


class TestPortfolioSpendAttribution(unittest.TestCase):
    def test_attribution_module_selftest(self):
        test_attribution_module_selftest()

    def test_sched_submit_carries_validated_tags(self):
        test_sched_submit_carries_validated_tags()

    def test_sched_submit_untagged_stays_unattributed(self):
        test_sched_submit_untagged_stays_unattributed()

    def test_sched_rejects_partial_tags(self):
        test_sched_rejects_partial_tags()

    def test_spend_guarded_call_stamps_tags_on_settle(self):
        test_spend_guarded_call_stamps_tags_on_settle()

    def test_spend_historic_untagged_not_allocated(self):
        test_spend_historic_untagged_not_allocated()

    def test_spend_rejects_partial_tags(self):
        test_spend_rejects_partial_tags()


if __name__ == "__main__":
    unittest.main()
