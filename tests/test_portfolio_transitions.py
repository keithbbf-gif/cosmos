#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Portfolio Studio: optimistic POST /profiles stage transitions (PS-05)."""
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

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_profiles import ProfileError, save_engine  # noqa: E402
from cosmos_service import Service  # noqa: E402


def _events(kernel, name: str):
    return [r for r in kernel.ledger.verify() if r.get("event") == name]


class TestPortfolioTransitions(unittest.TestCase):
    def test_adjacent_transition_ledger_bound(self):
        td = Path(tempfile.mkdtemp(prefix="ps05_adj_"))
        root = install(td / "live", tree_id="ps05-adj")
        paths = CosmosPaths(root)
        k = Kernel(root, worker="ps05-test")
        save_engine(paths, {
            "profile": "website",
            "define": {"text": "WHAT: site. WHY: PS-05 adjacent."},
        })
        head = k.ledger.head_seq()
        rec = save_engine(paths, {
            "profile": "website",
            "tree_id": "ps05-adj",
            "transition": {
                "to": "research",
                "expect_engine_version": 0,
                "expect_ledger_seq": head,
            },
        }, kernel=k)
        self.assertEqual(rec["transition"]["ledger_event"], "PROFILE_MOTIF_STAGE_TRANSITION")
        self.assertEqual(rec["engine"]["motif_cursor"]["stage"], "research")
        self.assertEqual(
            rec["engine"]["motif_cursor"]["ledger_seq"],
            rec["transition"]["ledger_seq"],
        )
        self.assertTrue(_events(k, "PROFILE_MOTIF_STAGE_TRANSITION"))

    def test_stale_engine_version_refuses(self):
        td = Path(tempfile.mkdtemp(prefix="ps05_stale_"))
        root = install(td / "live", tree_id="ps05-stale")
        paths = CosmosPaths(root)
        k = Kernel(root, worker="ps05-test")
        save_engine(paths, {
            "profile": "website",
            "define": {"text": "WHAT: stale. WHY: test."},
        })
        head = k.ledger.head_seq()
        with self.assertRaises(ProfileError) as ctx:
            save_engine(paths, {
                "profile": "website",
                "transition": {
                    "to": "research",
                    "expect_engine_version": 99,
                    "expect_ledger_seq": head,
                },
            }, kernel=k)
        self.assertEqual(ctx.exception.kind, "REFUSED")
        self.assertIn("stale", str(ctx.exception).lower())

    def test_skipped_stage_requires_keith(self):
        td = Path(tempfile.mkdtemp(prefix="ps05_skip_"))
        root = install(td / "live", tree_id="ps05-skip")
        paths = CosmosPaths(root)
        k = Kernel(root, worker="ps05-test")
        save_engine(paths, {
            "profile": "website",
            "define": {"text": "WHAT: skip. WHY: test."},
        })
        head = k.ledger.head_seq()
        with self.assertRaises(ProfileError) as ctx:
            save_engine(paths, {
                "profile": "website",
                "transition": {
                    "to": "arch",
                    "expect_engine_version": 0,
                    "expect_ledger_seq": head,
                },
            }, kernel=k)
        self.assertEqual(ctx.exception.kind, "REFUSED")
        self.assertIn("skipped", str(ctx.exception).lower())

    def test_legal_adjacent_requires_keith_decision(self):
        td = Path(tempfile.mkdtemp(prefix="ps05_legal_"))
        root = install(td / "live", tree_id="ps05-legal")
        paths = CosmosPaths(root)
        k = Kernel(root, worker="ps05-test")
        save_engine(paths, {
            "profile": "crucible",
            "define": {"text": "WHAT: case. WHY: legal profile."},
        })
        head = k.ledger.head_seq()
        with self.assertRaises(ProfileError) as ctx:
            save_engine(paths, {
                "profile": "crucible",
                "transition": {
                    "to": "research",
                    "expect_engine_version": 0,
                    "expect_ledger_seq": head,
                },
            }, kernel=k)
        self.assertEqual(ctx.exception.kind, "REFUSED")
        self.assertIn("keith", str(ctx.exception).lower())

    def test_legal_adjacent_with_keith_emits_evidence(self):
        td = Path(tempfile.mkdtemp(prefix="ps05_keith_"))
        root = install(td / "live", tree_id="ps05-keith")
        paths = CosmosPaths(root)
        k = Kernel(root, worker="ps05-test")
        save_engine(paths, {
            "profile": "crucible",
            "define": {"text": "WHAT: case. WHY: Keith approved advance."},
        })
        head = k.ledger.head_seq()
        rec = save_engine(paths, {
            "profile": "crucible",
            "tree_id": "ps05-keith",
            "transition": {
                "to": "research",
                "expect_engine_version": 0,
                "expect_ledger_seq": head,
                "keith_decision": {
                    "approved": True,
                    "text": "Keith: advance Crucible to RESEARCH for PS-05 test.",
                },
            },
        }, kernel=k)
        self.assertTrue(rec["transition"]["keith_decision"]["approved"])
        payload = _events(k, "PROFILE_MOTIF_STAGE_TRANSITION")[-1]["payload"]
        self.assertTrue(payload.get("keith_decision", {}).get("approved"))

    def test_unmeasured_build_refuses(self):
        td = Path(tempfile.mkdtemp(prefix="ps05_unm_"))
        root = install(td / "live", tree_id="ps05-unm")
        paths = CosmosPaths(root)
        k = Kernel(root, worker="ps05-test")
        save_engine(paths, {
            "profile": "website",
            "define": {"text": "WHAT: build gate. WHY: porosity."},
        })
        head = k.ledger.head_seq()
        save_engine(paths, {
            "profile": "website",
            "transition": {
                "to": "research",
                "expect_engine_version": 0,
                "expect_ledger_seq": head,
            },
        }, kernel=k)
        head = k.ledger.head_seq()
        cur = save_engine(paths, {"profile": "website"})
        ver = cur["engine"]["motif_cursor"]["version"]
        with self.assertRaises(ProfileError) as ctx:
            save_engine(paths, {
                "profile": "website",
                "transition": {
                    "to": "build",
                    "expect_engine_version": ver,
                    "expect_ledger_seq": head,
                    "keith_decision": {
                        "approved": True,
                        "text": "Keith: skip to BUILD to exercise porosity gate.",
                    },
                },
            }, kernel=k)
        self.assertEqual(ctx.exception.kind, "REFUSED")
        self.assertIn("UNMEASURED", str(ctx.exception))

    def test_service_post_transition_http(self):
        td = Path(tempfile.mkdtemp(prefix="ps05_http_"))
        root = install(td / "live", tree_id="ps05-http")
        paths = CosmosPaths(root)
        k = Kernel(root, worker="ps05-test")
        save_engine(paths, {
            "profile": "website",
            "define": {"text": "WHAT: HTTP. WHY: service route."},
        })
        head = k.ledger.head_seq()
        svc = Service(k, host="127.0.0.1", port=0)
        svc.serve_background()
        base = f"http://127.0.0.1:{svc.port}"
        body = json.dumps({
            "profile": "website",
            "tree_id": "ps05-http",
            "transition": {
                "to": "research",
                "expect_engine_version": 0,
                "expect_ledger_seq": head,
            },
        }).encode("utf-8")
        req = urllib.request.Request(
            base + "/api/v1/profiles",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                out = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            self.fail(f"HTTP {e.code}: {e.read()}")
        self.assertEqual(out.get("transition", {}).get("to"), "research")
        self.assertEqual(out.get("tree_id"), "ps05-http")

    def test_profile_save_without_transition_unchanged(self):
        td = Path(tempfile.mkdtemp(prefix="ps05_save_"))
        root = install(td / "live", tree_id="ps05-save")
        paths = CosmosPaths(root)
        rec = save_engine(paths, {
            "profile": "website",
            "define": {"text": "WHAT: plain save. WHY: regression."},
            "dest": {"kind": "staged", "path": "preview/"},
        })
        self.assertEqual(rec["engine"]["dest"]["kind"], "staged")
        self.assertTrue(rec["does_not_start_motif"])
        self.assertIn("motif_cursor", rec["engine"])


if __name__ == "__main__":
    raise SystemExit(unittest.main())
