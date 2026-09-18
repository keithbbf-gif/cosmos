#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VERIFY: POST /control/resume does not set day_credit to today's spend.

Resume clears kill/pause + session/rate throttles only
(SpendGuard.clear(..., reset_day=False)). The day lane stays; more
budget is spend-admin BUDGET_SET, not resume.

This fails if resume calls clear() with the default reset_day=True:
in ledger mode that writes day_credit_usd = _ledger_day_usd(), which
zeroes day_used and grants another DAY_CAP_USD.
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service  # noqa: E402
from cosmos_spendguard import SpendGuard  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _http(svc, method, path, obj=None, token=None):
    req = urllib.request.Request(
        f"http://127.0.0.1:{svc.port}{path}",
        data=(json.dumps(obj).encode("utf-8") if obj is not None else None),
        method=method)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    if obj is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def test_resume_does_not_set_day_credit_to_today_spend() -> None:
    td = Path(tempfile.mkdtemp(prefix="resume_day_"))
    root = install(td / "live", tree_id="resume-day-lane")
    k = Kernel(root, worker="core")
    today_spend = 1.50
    k.spend.set_budget("rail-resume", 10.0)
    k.spend.guarded_call("rail-resume", today_spend, lambda: {"usd": today_spend})

    lt = time.localtime()
    day = f"{lt.tm_year:04d}-{lt.tm_mon:02d}-{lt.tm_mday:02d}"
    state = k.paths.config("spendguard_state.json")
    state.write_text(json.dumps({
        "day": day,
        "day_usd": 0.0,
        "day_credit_usd": 0.0,
        "sessions": {"phone-a": 0.40},
        "req_epochs": [time.time()],
    }, indent=1), encoding="utf-8")

    probe = SpendGuard(state, ledger=k.ledger, clock=k._clock)
    ledger_today = probe._ledger_day_usd()
    check("today's ledger spend is the settled amount (test is live)",
          lambda: abs(ledger_today - today_spend) < 1e-9)

    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        code, body = _http(svc, "POST", "/api/v1/control/resume", {},
                           token=svc.token)
        after = json.loads(state.read_text(encoding="utf-8"))
        credit = float(after.get("day_credit_usd") or 0.0)
        check("POST /control/resume is 200 resumed",
              lambda: code == 200 and body.get("resumed") is True)
        check("response day_lane_reset is false",
              lambda: body.get("day_lane_reset") is False)
        check("resume does not set day_credit to today's spend",
              lambda: credit != ledger_today and credit == 0.0)
        check("resume still clears the session throttle",
              lambda: after.get("sessions") == {})
        check("resume still clears the rate window",
              lambda: after.get("req_epochs") == [])
        used = probe.audit()["day_used_usd"]
        check("day_used stays today's ledger spend (no second DAY_CAP)",
              lambda: abs(used - today_spend) < 1e-9)
    finally:
        svc.shutdown()


def main() -> int:
    test_resume_does_not_set_day_credit_to_today_spend()
    bad = 0
    for label, ok, err in RESULTS:
        print(("  [ok] " if ok else "  [FAIL] ") + label
              + ((" " + err) if err else ""))
        if not ok:
            bad += 1
    print(f"{len(RESULTS) - bad}/{len(RESULTS)} passed")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
