#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HealthBoard GET fold: measured board, negative control RED, GET never ledgers."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_command import Commander  # noqa: E402
import cosmos_health as health_mod  # noqa: E402
from cosmos_health import HealthBoard, snapshot  # noqa: E402
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _health_board_count(k: Kernel) -> int:
    return sum(1 for r in k.ledger.verify() if r["event"] == "HEALTH_BOARD")


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_health_get_"))
    root = install(td / "live", tree_id="health-get")
    k = Kernel(root, worker="core")

    b = snapshot(k)
    check("snapshot returns measured HealthBoard fold keys",
          lambda: {"verdict", "rows", "reds", "negative_control_red",
                   "measured_at_epoch", "elapsed_s"} <= set(b))
    check("negative control stays RED in GET fold",
          lambda: b["negative_control_red"] is True)
    check("healthy kernel verdict GREEN when rows pass",
          lambda: b["verdict"] == "GREEN")
    check("every row carries ok + detail unchanged",
          lambda: all(isinstance(r, dict) and "ok" in r and r.get("detail")
                      for r in b["rows"].values()))
    check("GET snapshot does not append HEALTH_BOARD",
          lambda: _health_board_count(k) == 0)

    before = _health_board_count(k)
    snapshot(k)
    check("second GET snapshot still does not ledger",
          lambda: _health_board_count(k) == before)

    t_first = snapshot(k)["measured_at_epoch"]
    t_second = snapshot(k)["measured_at_epoch"]
    check("10s cache returns same measured_at_epoch",
          lambda: t_first == t_second)

    # command health still ledgers (contrast with GET)
    c = Commander(k)
    h = c.handle("health")
    check("command health ledgers HEALTH_BOARD",
          lambda: _health_board_count(k) == 1)
    check("command health fold matches board contract",
          lambda: h["ok"] and h["negative_control_red"] is True and "rows" in h)

    # RED row survives to client on GET (drop sentinel so resolver row is RED)
    td2 = Path(tempfile.mkdtemp(prefix="cosmos_health_red_"))
    root2 = install(td2 / "live", tree_id="health-red")
    k2 = Kernel(root2, worker="core")
    sentinel = root2 / ".cosmos-root.json"
    sentinel.unlink()
    with health_mod._SNAP_LOCK:
        health_mod._SNAP_CACHE["payload"] = None
        health_mod._SNAP_CACHE["at"] = 0.0
    svc = Service(k2, host="127.0.0.1", port=0)
    svc.serve_background()
    base = f"http://127.0.0.1:{svc.port}"

    def get_health():
        req = urllib.request.Request(base + "/api/v1/health")
        req.add_header("Authorization", "Bearer " + svc.token)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    body = get_health()
    check("GET /api/v1/health serves negative_control_red",
          lambda: body["negative_control_red"] is True)
    check("GET /api/v1/health preserves RED row detail",
          lambda: body["rows"]["resolver/sentinel"]["ok"] is False
          and "sentinel" in body["rows"]["resolver/sentinel"]["detail"].lower())
    check("GET /api/v1/health verdict counts RED rows",
          lambda: body["verdict"].startswith("RED"))
    check("GET /api/v1/health does not mkdir health state dir",
          lambda: not (root2 / "state" / "health").exists()
          or not any((root2 / "state" / "health").iterdir()))
    led_before = _health_board_count(k2)
    get_health()
    check("GET /api/v1/health over wire does not ledger",
          lambda: _health_board_count(k2) == led_before)
    svc.shutdown()

    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    check("service imports health snapshot (not HealthBoard.run on GET)",
          lambda: "from cosmos_health import snapshot as health_snapshot" in src)
    check("service doc: GET never appends HEALTH_BOARD",
          lambda: "never appends HEALTH_BOARD" in src)

    health_src = (ROOT / "cosmos" / "cosmos_health.py").read_text(encoding="utf-8")
    check("health module exposes snapshot with 10s cache",
          lambda: "def snapshot(kernel)" in health_src and "_SNAP_CACHE_S = 10.0" in health_src)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (health GET fold)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


class TestHealthGetFold(unittest.TestCase):
    def test_measured_board_get_never_ledgers(self):
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    raise SystemExit(main())
