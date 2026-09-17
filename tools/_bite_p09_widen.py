#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P09 confirm-to-widen — cap never moves without allow_widen.

Occupancy is handle_post + POST /api/v1/spend (409 WIDEN_REQUIRES_CONFIRM).
This bite does not duplicate spend Core; it proves the refusal path and that
the live cap projection is unchanged on 409.

    py -3.14 cosmos/_bite_p09_widen.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service  # noqa: E402
from cosmos_spend_admin import handle_post  # noqa: E402
from cosmos_spendguard import SpendGuard  # noqa: E402

OUT = HERE / "_bite_p09_widen.json"
ACTOR = "bearer:p09-bite-actor"
RAIL = "p09-bite-rail"


def cap_of(kernel, rail: str):
    row = kernel.spend.audit()["rails"].get(rail)
    return None if row is None else row["cap_usd"]


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_p09_"))
    root = install(td / "live", tree_id="p09-widen-bite")
    k = Kernel(root, worker="core")
    cfg = k.paths.config("spendguard_config.json")
    guard = SpendGuard(
        k.paths.config("spendguard_state.json"),
        config_file=cfg,
        ledger=k.ledger,
    )

    def config_digest(path: Path) -> str | None:
        if not path.is_file():
            return None
        return hashlib.sha256(path.read_bytes()).hexdigest()

    cap_before_mod = cap_of(k, RAIL)
    cfg_before = config_digest(cfg)
    refused_before = sum(
        1 for r in k.ledger.verify() if r.get("event") == "SPEND_CAP_REFUSED"
    )

    code, body = handle_post(
        k, guard, cfg, {"rail": RAIL, "cap_usd": 2.5}, ACTOR, turn_default=60,
    )
    refused_after_module = sum(
        1 for r in k.ledger.verify() if r.get("event") == "SPEND_CAP_REFUSED"
    )
    module_refusal_ledgered = refused_after_module >= refused_before + 1
    cfg_after = config_digest(cfg)
    module_ok = (
        code == 409
        and body.get("error") == "WIDEN_REQUIRES_CONFIRM"
        and body.get("kind") == "WIDEN_REQUIRES_CONFIRM"
        and cap_before_mod is None
        and cap_of(k, RAIL) is None
        and cfg_before == cfg_after
    )

    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        base = "http://127.0.0.1:%d" % svc.port
        auth = {"Authorization": "Bearer " + svc.token,
                "Content-Type": "application/json"}

        def http(method, path, payload=None):
            data = None if payload is None else json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(base + path, data=data, method=method)
            for hk, hv in auth.items():
                req.add_header(hk, hv)
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return resp.status, json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                raw = e.read().decode("utf-8")
                try:
                    b = json.loads(raw)
                except json.JSONDecodeError:
                    b = {"error": raw[:200]}
                return e.code, b

        g0, spend0 = http("GET", "/api/v1/spend")
        cap_before = spend0.get("rails", {}).get(RAIL)
        code_h, body_h = http(
            "POST", "/api/v1/spend", {"rail": RAIL, "cap_usd": 3.0},
        )
        g1, spend1 = http("GET", "/api/v1/spend")
        cap_after = spend1.get("rails", {}).get(RAIL)
    finally:
        svc.shutdown()

    route_ok = (
        g0 == 200
        and cap_before is None
        and code_h == 409
        and body_h.get("error") == "WIDEN_REQUIRES_CONFIRM"
        and g1 == 200
        and cap_after is None
        and cap_before == cap_after
    )

    refused_final = sum(
        1 for r in k.ledger.verify() if r.get("event") == "SPEND_CAP_REFUSED"
    )

    rec = {
        "module_refused_409": code == 409,
        "module_kind": body.get("error"),
        "module_cap_unchanged": cap_of(k, RAIL) is None,
        "spendguard_config_unchanged": cfg_before == cfg_after,
        "route_refused_409": code_h == 409,
        "route_kind": body_h.get("error"),
        "get_cap_before": cap_before,
        "get_cap_after": cap_after,
        "module_refusal_ledgered": module_refusal_ledgered,
        "refusal_events": refused_final,
    }
    rec["all_bite"] = module_ok and route_ok and module_refusal_ledgered
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
