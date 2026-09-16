#!/usr/bin/env py -3.14
"""PS-05: Keith-approved adjacent stage transitions on POST /profiles."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_profiles import (  # noqa: E402
    TRANSITION_EVENT,
    TRANSITION_EVENT_SCHEMA,
    TRANSITION_GATES,
    UNMEASURED,
    ProfileError,
    apply_stage_transition,
    load_engine,
    motif_transition_edges,
    save_engine,
    transition_contract,
)


def _kernel(tree_id: str = "ps05-transitions") -> Kernel:
    td = Path(tempfile.mkdtemp(prefix="ps05_"))
    root = install(td / "live", tree_id=tree_id)
    return Kernel(root)


def _gates(paths: CosmosPaths, *, health=None, spend=None, product=None) -> dict:
    return {
        "health": health or {
            "verdict": "GREEN",
            "reds": 0,
            "negative_control_red": True,
        },
        "tree": {"tree_id": paths.sentinel.tree_id},
        "spend": spend or {"kind": "OK"},
        "product": product or {"id": "website", "kind": "OK"},
    }


def _seed(paths: CosmosPaths, profile: str = "website") -> dict:
    return save_engine(paths, {
        "profile": profile,
        "define": {"text": "WHAT: PS-05. WHY: transition pin."},
        "dest": {"kind": "staged" if profile == "website" else "local"},
    })


class PortfolioTransitions(unittest.TestCase):
    def test_transition_contract_frozen(self):
        c = transition_contract()
        self.assertEqual(c["schema"], "cosmos-profiles-transition/1")
        self.assertEqual(c["event"], TRANSITION_EVENT)
        self.assertEqual(c["event_schema"], TRANSITION_EVENT_SCHEMA)
        self.assertEqual(list(c["gates"]), list(TRANSITION_GATES))
        edges = motif_transition_edges()
        self.assertEqual(len(edges), 9)
        self.assertTrue(all(e.get("requires_keith") is True for e in edges))

    def test_legal_adjacent_requires_keith_and_ledger(self):
        k = _kernel()
        _seed(k.paths)
        eng = load_engine(k.paths, "website")
        head_before = k.ledger.head_seq()
        jobs_before = dict(k.sched._state())
        out = apply_stage_transition(k.paths, {
            "profile": "website",
            "action": "transition",
            "transition": {
                "from_stage": "define",
                "to_stage": "research",
                "expect_version": eng["version"],
            },
            "keith_decision": {
                "approved": True,
                "decided_by": "keith",
                "note": "advance RESEARCH",
            },
            "gates": _gates(k.paths),
        }, kernel=k)
        self.assertEqual(out["engine"]["current_stage"], "research")
        self.assertEqual(out["transition"]["ledger_event"], TRANSITION_EVENT)
        self.assertIsInstance(out["transition"]["ledger_seq"], int)
        self.assertGreater(out["transition"]["ledger_seq"], head_before)
        self.assertFalse(out["transition"]["job_started"])
        self.assertFalse(out["transition"]["starts_motif"])
        self.assertTrue(out["does_not_publish"])
        self.assertEqual(dict(k.sched._state()), jobs_before)
        recs = [r for r in k.ledger.verify() if r["event"] == TRANSITION_EVENT]
        self.assertEqual(len(recs), 1)
        payload = recs[0]["payload"]
        self.assertEqual(payload["schema"], TRANSITION_EVENT_SCHEMA)
        self.assertEqual(payload["from_stage"], "define")
        self.assertEqual(payload["to_stage"], "research")
        self.assertIs(payload["job_started"], False)
        self.assertEqual(payload["keith_decision"]["decided_by"], "keith")

    def test_save_still_does_not_start_motif(self):
        k = _kernel("ps05-save")
        out = _seed(k.paths)
        self.assertTrue(out["does_not_start_motif"])
        self.assertTrue(out["does_not_publish"])
        self.assertEqual(out["engine"]["current_stage"], "define")
        self.assertIsInstance(out["engine"]["version"], int)
        self.assertEqual(
            out["stage_transition"]["current"]["kind"], UNMEASURED)

    def test_refusals_do_not_queue_work(self):
        k = _kernel("ps05-refuse")
        _seed(k.paths)
        eng = load_engine(k.paths, "website")
        jobs_before = dict(k.sched._state())
        head_before = k.ledger.head_seq()

        cases = [
            ("SKIPPED", {
                "profile": "website",
                "transition": {
                    "from_stage": "define",
                    "to_stage": "build",
                    "expect_version": eng["version"],
                },
                "keith_decision": {"approved": True, "decided_by": "keith"},
                "gates": _gates(k.paths),
            }),
            ("STALE", {
                "profile": "website",
                "transition": {
                    "from_stage": "define",
                    "to_stage": "research",
                    "expect_version": eng["version"] + 7,
                },
                "keith_decision": {"approved": True, "decided_by": "keith"},
                "gates": _gates(k.paths),
            }),
            ("RED", {
                "profile": "website",
                "transition": {
                    "from_stage": "define",
                    "to_stage": "research",
                    "expect_version": eng["version"],
                },
                "keith_decision": {"approved": True, "decided_by": "keith"},
                "gates": _gates(k.paths, health={
                    "verdict": "RED x2",
                    "reds": 2,
                    "negative_control_red": True,
                }),
            }),
            ("UNMEASURED", {
                "profile": "website",
                "transition": {
                    "from_stage": "define",
                    "to_stage": "research",
                    "expect_version": eng["version"],
                },
                "keith_decision": {"approved": True, "decided_by": "keith"},
                "gates": _gates(k.paths, product={
                    "id": "website", "kind": UNMEASURED,
                }),
            }),
            ("UNGATED", {
                "profile": "website",
                "transition": {
                    "from_stage": "define",
                    "to_stage": "research",
                    "expect_version": eng["version"],
                },
                "gates": _gates(k.paths),
            }),
        ]
        for kind, body in cases:
            with self.subTest(kind=kind):
                with self.assertRaises(ProfileError) as ctx:
                    apply_stage_transition(k.paths, body, kernel=k)
                self.assertEqual(ctx.exception.kind, kind)
                self.assertEqual(dict(k.sched._state()), jobs_before)
                self.assertEqual(k.ledger.head_seq(), head_before)

    def test_crucible_legal_adjacent_needs_keith(self):
        """Legal profile (crucible) still requires Keith on adjacent advance."""
        k = _kernel("ps05-legal")
        _seed(k.paths, profile="crucible")
        eng = load_engine(k.paths, "crucible")
        with self.assertRaises(ProfileError) as ctx:
            apply_stage_transition(k.paths, {
                "profile": "crucible",
                "transition": {
                    "from_stage": "define",
                    "to_stage": "research",
                    "expect_version": eng["version"],
                },
                "gates": _gates(k.paths, product={
                    "id": "crucible", "kind": "OK",
                }),
            }, kernel=k)
        self.assertEqual(ctx.exception.kind, "UNGATED")

    def test_service_wires_kernel_into_profiles_save(self):
        src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
        self.assertIn("profiles_save(kernel.paths, d, kernel=kernel)", src)
        self.assertIn("action=transition", src)
        self.assertIn("Does not start MOTIF", src)
        self.assertIn("Does not publish", src)

    def test_no_kernel_is_ungated(self):
        k = _kernel("ps05-nok")
        _seed(k.paths)
        eng = load_engine(k.paths, "website")
        with self.assertRaises(ProfileError) as ctx:
            apply_stage_transition(k.paths, {
                "profile": "website",
                "transition": {
                    "from_stage": "define",
                    "to_stage": "research",
                    "expect_version": eng["version"],
                },
                "keith_decision": {"approved": True, "decided_by": "keith"},
                "gates": _gates(k.paths),
            }, kernel=None)
        self.assertEqual(ctx.exception.kind, "UNGATED")


if __name__ == "__main__":
    unittest.main()
