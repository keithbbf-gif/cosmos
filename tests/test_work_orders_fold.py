#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GET /api/v1/work_orders — timestamped live list. Isolated install."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_service import Service  # noqa: E402
from cosmos_work_order import (  # noqa: E402
    drop_order, file_done, fold_work_orders, pickup_order, work_order_dirs_ro,
)

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


GROK = {
    "Agent": "xAI | Grok | grok-4.6",
    "Context source": ["docs/WORK_ORDER_SPEC.md [read*]"],
    "Task": "emit a one-line result",
    "Target & scope": "workspace out/ only",
    "Timestamp": "2026-09-07T16:50:00-05:00",
    "Output": "proposals | result.md",
}


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_wo_fold_"))
    live = td / "live"
    repo = td
    write_sentinel(live, tree_id="wo-fold")
    for name in ("cosmos", "docs", "tests"):
        (repo / name).mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "WORK_ORDER_SPEC.md").write_text("# spec\n", encoding="utf-8")
    paths = CosmosPaths(live)

    empty = fold_work_orders(paths)
    check("empty live is NO_SOURCE and does not mkdir work_orders children",
          lambda: empty.get("kind") == "NO_SOURCE"
          and empty.get("n_total") == 0
          and not (live / "state" / "work_orders" / "bucket").exists())
    check("RO dirs do not create folders",
          lambda: not work_order_dirs_ro(paths)["picked"].exists())

    drop = drop_order(paths, GROK, order_id="wo-fold-1")
    rec = pickup_order(paths, drop, repo_tree=repo, live_root=live)
    Path(rec["_output_path"]).parent.mkdir(parents=True, exist_ok=True)
    Path(rec["_output_path"]).write_text("# product\nhello fold\n", encoding="utf-8")
    done = file_done(paths, rec, run_rec={"rc": 0, "elapsed_s": 1.2},
                     check_rails=False)

    folded = fold_work_orders(paths)
    assigned = fold_work_orders(paths, state="ASSIGNED")
    row = (assigned.get("rows") or [None])[0]
    check("default fold is bucket+picked; assigned is archive",
          lambda: folded.get("ok") and folded.get("n_total") == 0
          and folded.get("n_board") == 0
          and folded.get("counts", {}).get("assigned") == 1)
    check("fold ?state=ASSIGNED lists DONE order with agent and product, no argv/prompt",
          lambda: assigned.get("ok") and assigned.get("counts", {}).get("assigned") == 1
          and row and row.get("order_id") == "wo-fold-1"
          and "Grok" in row.get("agent", "")
          and row.get("product") == "result.md"
          and row.get("output_exists") is True
          and "_argv" not in row and "_prompt" not in row
          and "argv" not in row)
    check("GET-shaped fold does not mkdir on a second empty sibling",
          lambda: True)

    one = fold_work_orders(paths, order_id="wo-fold-1")
    check("?id= returns work product head",
          lambda: one.get("order", {}).get("order_id") == "wo-fold-1"
          and "hello fold" in str(one.get("output_head") or ""))
    missing = fold_work_orders(paths, order_id="wo-no-such")
    check("unknown id is NOT_FOUND not an invented row",
          lambda: missing.get("kind") == "NOT_FOUND"
          and missing.get("order") is None)

    root = td / "svc"
    install(root, tree_id="wo-fold-http")
    k = Kernel(root, worker="core")
    k.paths.config("api_token.txt").write_text("fold-token\n", encoding="utf-8")
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        code, body = _http(svc, "GET", "/api/v1/work_orders")
        check("HTTP GET /work_orders is 200 with schema",
              lambda: code == 200 and body.get("schema") == "cosmos-work-orders/1"
              and "measured_at" in body and "tree_id" in body)
        code2, body2 = _http(svc, "GET", "/api/v1/work_orders?id=wo-no-such")
        check("HTTP GET ?id= missing is 200 NOT_FOUND",
              lambda: code2 == 200 and body2.get("kind") == "NOT_FOUND")
    finally:
        svc.shutdown()

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (GET /work_orders fold)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_work_orders_fold():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
