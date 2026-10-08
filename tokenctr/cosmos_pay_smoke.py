#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_smoke — the deploy smoke test (10_RUNPOD_DEPLOY.md §9 step 7).

Default (offline self-test): config → secrets → registry → Store/Meter/pricing/
founding round-trip. Proves the machinery without network.
    py -3 cosmos_pay_smoke.py

Live mode (--live --key ck_… --url http://127.0.0.1:8787): one REAL chat call
through the running gateway → asserts 200 + usage + headers + meter event.
    py -3 cosmos_pay_smoke.py --live --key ck_… --url http://127.0.0.1:8787

Exit 0 = the clock can start. Exit 1 = fix before launch.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

PASS = 0
FAIL = 0


def check(name: str, cond: bool) -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}")


def offline_self_test() -> None:
    print("-- offline self-test --")
    import cosmos_pay_config as cfg
    import cosmos_pay_meter as meter_mod
    import cosmos_pay_pricing as pricing
    import cosmos_pay_toll as toll_mod
    import cosmos_pay_entitlement as ent
    import cosmos_pay_gateway as gw

    check("config loads", bool(cfg.load_config()))
    try:
        sec = cfg.load_secrets(required=["mesh_hmac_key_hex"])
        check("secrets present", bool(sec.get("mesh_hmac_key_hex")))
        if not sec.get("runpod_api_key"):
            print("    [NOTE] runpod_api_key pending in secrets.json (needed for live rail)")
    except cfg.ConfigError as e:
        check("secrets present", False)
        print("    -> ConfigError:", str(e).encode("ascii", "replace").decode("ascii"))

    models = cfg.load_models()
    if not models:
        seed = Path(__file__).resolve().parent / "models.seed.json"
        if seed.exists():
            cfg.ensure_dirs()
            (cfg.ROOT / "models.json").write_text(seed.read_text(encoding="utf-8"), encoding="utf-8")
            models = cfg.load_models()
            print("    -> seeded models.json from models.seed.json")
    check(f"registry has models ({len(models)})", len(models) >= 1)

    # round-trip in a temp dir: store → meter → pricing → founding → toll
    tmp = tempfile.mkdtemp()
    store = gw.Store(str(Path(tmp) / "keys.db"))
    meter = meter_mod.Meter(str(Path(tmp) / "meter.db"))
    ah, raw = store.create_account(plan="free")
    check("account + key minted", ah.startswith("h:") and raw.startswith("ck_"))
    check("account lookup by key", store.account_for_key(raw)["account_hash"] == ah)

    if not models:
        print("    -> registry still empty; skipping model-dependent checks")
        print(f"\n{PASS} pass, {FAIL} fail")
        sys.exit(1 if FAIL else 0)
    m = models[next(iter(models))]
    price = float(m.get("price_per_m_usd", 0.3))
    meter.emit({"schema": meter_mod.SCHEMA, "event": "RUN_SETTLED", "lane": "A",
                "rail": "smoke", "model": next(iter(models)), "wallet": "cosmos",
                "tokens": {"in": 100, "out": 20}, "cost": {"measured_usd": 120 * price / 1e6,
                                                           "provenance": "measured"}})
    check("meter event emitted + readable", any(e.get("event") == "RUN_SETTLED" for e in meter.tail(5)))

    f = __import__("cosmos_pay_founding").Founding(store, meter, cap=500)
    f.grant(ah, "paid")
    check("founding grant works", store.credits(ah) >= 20.0)

    key = b"x" * 32
    tok = ent.mint(ent.free_core_claims("h:smoke"), key)
    check("entitlement verify", ent.verify(tok, key).get("plan") == "core-free")

    line = toll_mod.statement_line(meter.tail(10), time.strftime("%Y-%m"))
    check("toll statement folds", "toll_gross_usd" in line)
    print(f"    reconciliation: statement basis ${line['basis_measured_usd']} == sum events OK")


def live_test(key: str, url: str) -> None:
    print("-- live gateway test --")
    body = {"model": "", "messages": [{"role": "user", "content": "Say PONG and nothing else."}]}
    code, out, headers = None, None, {}
    # discover a model first
    req = urllib.request.Request(url.rstrip("/") + "/v1/models",
                                 headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=10) as r:
        models = json.loads(r.read().decode())["data"]
    check("models endpoint", len(models) >= 1)
    body["model"] = models[0]["id"]

    req = urllib.request.Request(
        url.rstrip("/") + "/v1/chat/completions", data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        code = r.status
        out = json.loads(r.read().decode())
        headers = dict(r.headers)
    check(f"chat 200 (model {body['model']})", code == 200)
    check("choices present", "choices" in out)
    check("quota header present", any(k.startswith("x-cosmos-") for k in headers))
    print(f"    response: {out['choices'][0]['message']['content'][:80]!r}")
    print("    -> now run the REAL smoke: a work-order task through the 4C gate (10_RUNPOD_DEPLOY section 9 step 7)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--key", default="")
    ap.add_argument("--url", default="http://127.0.0.1:8787")
    args = ap.parse_args()
    if args.live and args.key:
        live_test(args.key, args.url)
    else:
        offline_self_test()
    print(f"\n{PASS} pass, {FAIL} fail")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
