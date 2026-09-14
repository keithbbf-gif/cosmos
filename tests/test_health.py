#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused health snapshot tests for GET /api/v1/health.

The route already calls cosmos_health.snapshot. This suite pins the fold:
measured HealthBoard rows, planted-failure RED, GET never ledgers / never
mkdir, 10s Core cache, and every error/RED surviving unchanged to the
client contract. Command ``health`` still ledgers via HealthBoard.run.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cosmos"))

import cosmos_health as ch  # noqa: E402
from cosmos_health import HealthBoard, snapshot  # noqa: E402
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service  # noqa: E402

FOLD_KEYS = (
    "measured_at_epoch",
    "elapsed_s",
    "rows",
    "reds",
    "negative_control_red",
    "diagnosis",
    "verdict",
)
PLANTED_RED = "PLANTED-RED-DETAIL-ps02-must-survive"


def _clear_cache() -> None:
    with ch._SNAP_LOCK:
        ch._SNAP_CACHE["key"] = None
        ch._SNAP_CACHE["at"] = 0.0
        ch._SNAP_CACHE["payload"] = None


def _walk_dirs(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_dir()}


def _http_get(svc: Service, path: str):
    req = urllib.request.Request(f"http://127.0.0.1:{svc.port}{path}")
    req.add_header("Authorization", "Bearer " + svc.token)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


class TestHealthSnapshot(unittest.TestCase):
    def setUp(self):
        _clear_cache()
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_health_snap_"))
        self.root = install(self.tmp / "live", tree_id="health-snap")
        self.k = Kernel(self.root, worker="core")

    def tearDown(self):
        _clear_cache()

    def test_cache_ttl_is_ten_seconds(self):
        self.assertEqual(ch._SNAP_CACHE_S, 10.0)

    def test_snapshot_is_healthboard_fold(self):
        board = snapshot(self.k)
        for key in FOLD_KEYS:
            self.assertIn(key, board)
        self.assertIsInstance(board["rows"], dict)
        self.assertTrue(board["rows"], "empty rows must be explicit, not omitted")
        self.assertIn("queue", board["rows"])
        q = board["rows"]["queue"]
        self.assertIn("ok", q)
        self.assertTrue(q["detail"], "empty queue is a measured sentence, not blank")
        self.assertIn("no jobs yet", q["detail"])
        self.assertIsInstance(board["reds"], int)
        self.assertNotEqual(board["elapsed_s"], "UNMEASURED")
        self.assertIsInstance(board["measured_at_epoch"], (int, float))

    def test_negative_control_stays_red(self):
        board = snapshot(self.k)
        self.assertIs(board["negative_control_red"], True)
        self.assertNotIn("negative control (must be RED)", board["rows"])
        self.assertFalse(str(board["verdict"]).startswith("BOARD-BROKEN"))

    def test_snapshot_does_not_ledger(self):
        before = [r["seq"] for r in self.k.ledger.verify()]
        head = self.k.ledger.head_seq()
        snapshot(self.k)
        after = list(self.k.ledger.verify())
        self.assertEqual(self.k.ledger.head_seq(), head)
        self.assertEqual([r["seq"] for r in after], before)
        self.assertFalse(any(r["event"] == "HEALTH_BOARD" for r in after))

    def test_snapshot_does_not_mkdir(self):
        before = _walk_dirs(self.root)
        snapshot(self.k)
        self.assertEqual(_walk_dirs(self.root), before)

    def test_ten_second_cache_returns_same_fold(self):
        a = snapshot(self.k)
        b = snapshot(self.k)
        self.assertIs(a, b)
        ch._SNAP_CACHE["at"] = 0.0
        c = snapshot(self.k)
        self.assertIsNot(a, c)
        self.assertEqual(c["verdict"], a["verdict"])
        self.assertIs(c["negative_control_red"], True)

    def test_planted_red_detail_survives_unchanged(self):
        hb = HealthBoard(self.k)
        hb.add_row("bomb", lambda: (False, PLANTED_RED))
        board = hb.measure()
        self.assertEqual(board["rows"]["bomb"]["ok"], False)
        self.assertEqual(board["rows"]["bomb"]["detail"], PLANTED_RED)
        self.assertGreaterEqual(board["reds"], 1)
        self.assertTrue(board["verdict"].startswith("RED"))
        self.assertIs(board["negative_control_red"], True)

    def test_raising_row_is_red_not_zero(self):
        hb = HealthBoard(self.k)
        hb.add_row("bomb", lambda: (_ for _ in ()).throw(RuntimeError("boom-ps02")))
        board = hb.measure()
        detail = board["rows"]["bomb"]["detail"]
        self.assertFalse(board["rows"]["bomb"]["ok"])
        self.assertIn("RAISED", detail)
        self.assertIn("boom-ps02", detail)
        self.assertNotEqual(board["reds"], 0)
        self.assertNotEqual(board["verdict"], "GREEN")

    def test_run_still_ledgers_command_path(self):
        head = self.k.ledger.head_seq()
        board = HealthBoard(self.k).run()
        self.assertIs(board["negative_control_red"], True)
        events = [r for r in self.k.ledger.verify() if r["event"] == "HEALTH_BOARD"]
        self.assertTrue(events)
        self.assertGreater(self.k.ledger.head_seq(), head)
        self.assertEqual(events[-1]["payload"].get("node"),
                         self.k.paths.sentinel.system)

    def test_service_binds_existing_health_route_to_snapshot(self):
        src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
        self.assertIn('self.path == "/api/v1/health"', src)
        self.assertIn("from cosmos_health import snapshot as health_snapshot", src)
        self.assertIn("health_snapshot(kernel)", src)
        self.assertIn("never appends HEALTH_BOARD", src)
        self.assertNotIn("HealthBoard(kernel).run()", src.split("if self.path == \"/api/v1/health\":", 1)[1][:400])


class TestHealthHttpContract(unittest.TestCase):
    def setUp(self):
        _clear_cache()
        self.tmp = Path(tempfile.mkdtemp(prefix="cosmos_health_http_"))
        self.root = install(self.tmp / "live", tree_id="health-http")
        self.k = Kernel(self.root, worker="core")
        self.svc = Service(self.k, host="127.0.0.1", port=0)
        self.svc.serve_background()

    def tearDown(self):
        _clear_cache()

    def test_get_health_returns_measured_fold(self):
        head = self.k.ledger.head_seq()
        dirs_before = _walk_dirs(self.root)
        code, body = _http_get(self.svc, "/api/v1/health")
        self.assertEqual(code, 200)
        for key in FOLD_KEYS:
            self.assertIn(key, body)
        self.assertIs(body["negative_control_red"], True)
        self.assertIsInstance(body["rows"], dict)
        self.assertTrue(body["rows"])
        self.assertIn("queue", body["rows"])
        self.assertTrue(body["rows"]["queue"]["detail"])
        self.assertNotEqual(body.get("reds"), "UNMEASURED")
        self.assertEqual(self.k.ledger.head_seq(), head)
        self.assertFalse(any(r["event"] == "HEALTH_BOARD"
                             for r in self.k.ledger.verify()))
        self.assertEqual(_walk_dirs(self.root), dirs_before)

    def test_get_passes_red_detail_unchanged(self):
        orig = HealthBoard.measure

        def planted(self):
            board = orig(self)
            rows = dict(board["rows"])
            rows["bomb"] = {"ok": False, "detail": PLANTED_RED}
            out = dict(board)
            out["rows"] = rows
            out["reds"] = sum(1 for r in rows.values() if not r["ok"])
            out["verdict"] = f"RED x{out['reds']}"
            return out

        HealthBoard.measure = planted  # type: ignore[method-assign]
        try:
            _clear_cache()
            code, body = _http_get(self.svc, "/api/v1/health")
        finally:
            HealthBoard.measure = orig  # type: ignore[method-assign]
        self.assertEqual(code, 200)
        self.assertEqual(body["rows"]["bomb"]["detail"], PLANTED_RED)
        self.assertIs(body["rows"]["bomb"]["ok"], False)
        self.assertTrue(body["verdict"].startswith("RED"))
        self.assertIs(body["negative_control_red"], True)
        self.assertGreaterEqual(body["reds"], 1)
        self.assertNotEqual(body["reds"], 0)

    def test_get_does_not_mutate_on_second_read(self):
        head = self.k.ledger.head_seq()
        code1, body1 = _http_get(self.svc, "/api/v1/health")
        code2, body2 = _http_get(self.svc, "/api/v1/health")
        self.assertEqual(code1, 200)
        self.assertEqual(code2, 200)
        self.assertEqual(body1["measured_at_epoch"], body2["measured_at_epoch"])
        self.assertEqual(body1["verdict"], body2["verdict"])
        self.assertEqual(self.k.ledger.head_seq(), head)


if __name__ == "__main__":
    unittest.main(verbosity=2)
