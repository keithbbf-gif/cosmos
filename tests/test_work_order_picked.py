#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WORK_ORDER_PICKED: Core HTTP is the first durable write after pickup.

Runner POSTs Core. Core appends. Second POST is idempotent on order_id.
Daemon never opens live/ledger/. Isolated install — no live :8770.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service, record_work_order_picked  # noqa: E402
from cosmos_work_order import notify_core_picked  # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _http(svc, method, path, obj=None):
    import urllib.error
    import urllib.request
    req = urllib.request.Request(
        f"http://127.0.0.1:{svc.port}{path}",
        data=(json.dumps(obj).encode("utf-8") if obj is not None else None),
        method=method)
    req.add_header("Authorization", "Bearer " + svc.token)
    if obj is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_wo_picked_"))
    root = td / "live"
    install(root, tree_id="wo-picked")
    k = Kernel(root, worker="core")
    k.paths.config("api_token.txt").write_text("wo-picked-token\n", encoding="utf-8")

    code, rec = record_work_order_picked(k, {})
    check("missing order_id is 400 BAD_REQUEST",
          lambda: code == 400 and rec.get("error") == "BAD_REQUEST")

    code1, rec1 = record_work_order_picked(k, {
        "order_id": "wo-alpha",
        "agent": "xAI | Grok | grok-4.6",
        "output_path": str(td / "out.md"),
        "picked_at": "2026-09-07T16:00:00-05:00",
    })
    check("first pickup is 201 WORK_ORDER_PICKED with seq/hmac",
          lambda: code1 == 201 and rec1.get("ok") is True
          and rec1.get("already") is False
          and rec1.get("event") == "WORK_ORDER_PICKED"
          and int(rec1.get("seq") or 0) >= 1
          and bool(rec1.get("hmac")) and rec1.get("prev_sha") is not None)

    kinds = [r.get("event") for r in k.ledger.verify()]
    check("ledger actually carries WORK_ORDER_PICKED (not a folder claim)",
          lambda: "WORK_ORDER_PICKED" in kinds)

    code2, rec2 = record_work_order_picked(k, {"order_id": "wo-alpha"})
    check("second pickup same order_id is 200 already, same seq",
          lambda: code2 == 200 and rec2.get("already") is True
          and rec2.get("seq") == rec1.get("seq")
          and rec2.get("hmac") == rec1.get("hmac"))

    n_picked = sum(1 for r in k.ledger.verify()
                   if r.get("event") == "WORK_ORDER_PICKED")
    check("idempotent POST does not double-append",
          lambda: n_picked == 1)

    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        http1, body1 = _http(svc, "POST", "/api/v1/work_orders/picked",
                             {"order_id": "wo-http-1",
                              "agent": "xAI | Grok | grok-4.6"})
        check("HTTP POST /work_orders/picked is 201 with seq",
              lambda: http1 == 201 and body1.get("ok") is True
              and body1.get("seq") is not None)
        http2, body2 = _http(svc, "POST", "/api/v1/work_orders/picked",
                             {"order_id": "wo-http-1"})
        check("HTTP second POST is 200 already",
              lambda: http2 == 200 and body2.get("already") is True
              and body2.get("seq") == body1.get("seq"))
        http3, body3 = _http(svc, "POST", "/api/v1/work_orders/picked", {})
        check("HTTP missing order_id is 400",
              lambda: http3 == 400 and body3.get("error") == "BAD_REQUEST")

        posted = []

        def fake_http(method, url, body, headers):
            posted.append(url)
            return _http(svc, method, "/api/v1/work_orders/picked", body)

        note = notify_core_picked(
            k.paths, {"order_id": "wo-via-runner", "Agent": "xAI | Grok | grok-4.6",
                      "picked_at": "2026-09-07T16:01:00-05:00"},
            http=fake_http, base_url=f"http://127.0.0.1:{svc.port}")
        check("runner notify_core_picked returns Core seq and does not open JSONL",
              lambda: note.get("ok") is True and note.get("seq") is not None
              and posted and "work_orders/picked" in posted[0])
        skip = notify_core_picked(k.paths, {"order_id": "wo-skip"})
        check("no core_url and no http= is CORE_NOT_COMPOSED (no live :8770)",
              lambda: skip.get("kind") == "CORE_NOT_COMPOSED")
    finally:
        svc.shutdown()

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (WORK_ORDER_PICKED Core HTTP)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_work_order_picked():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
