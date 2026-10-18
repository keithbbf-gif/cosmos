#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_split_pricing — separate prompt/completion prices (2026-10-18).

bill = prompt_tokens*prompt_price + completion_tokens*completion_price (per 1M);
single price_per_m_usd entries still bill both sides at that price; the reserve
uses the split prices; the credit header shows the post-call balance.
"""
from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cosmos_pay_gateway as gw
import cosmos_pay_meter as meter_mod
import cosmos_pay_openrouter_rail as or_mod

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


def close(a: float, b: float) -> bool:
    return abs(a - b) < 1e-12


if __name__ == "__main__":
    print("-- test_pay_split_pricing --")
    # helpers
    check("split prices", gw.model_prices({"prompt_per_m_usd": 0.02, "completion_per_m_usd": 0.06}) == (0.02, 0.06))
    check("legacy single price", gw.model_prices({"price_per_m_usd": 0.1}) == (0.1, 0.1))
    check("split overrides single", gw.model_prices({"price_per_m_usd": 9, "prompt_per_m_usd": 1, "completion_per_m_usd": 2}) == (1.0, 2.0))
    check("one side split, other falls back", gw.model_prices({"price_per_m_usd": 0.5, "completion_per_m_usd": 2}) == (0.5, 2.0))
    check("negative/garbage -> 0", gw.model_prices({"prompt_per_m_usd": -1, "completion_per_m_usd": "x"}) == (0.0, 0.0))
    check("billed_usd", close(gw.billed_usd((0.02, 0.06), 1000, 500), (1000 * 0.02 + 500 * 0.06) / 1e6))

    tmp = tempfile.mkdtemp()
    store = gw.Store(str(Path(tmp) / "keys.db"))
    meter = meter_mod.Meter(str(Path(tmp) / "meter.db"))
    usage = {"prompt_tokens": 100, "completion_tokens": 40}

    def transport(spec):
        return {"id": "x", "model": spec["body"]["model"], "usage": dict(usage),
                "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}]}

    rail = or_mod.OpenRouterRail(api_key="k", endpoint="https://example.invalid/v1/chat/completions", transport=transport)
    models = {
        "split/model": {"rail": "openrouter", "endpoint": "openrouter", "prompt_per_m_usd": 0.5, "completion_per_m_usd": 4.0},
        "tiny/model": {"rail": "openrouter", "endpoint": "openrouter", "prompt_per_m_usd": 0.021, "completion_per_m_usd": 0.063},
        "legacy/model": {"rail": "openrouter", "endpoint": "openrouter", "price_per_m_usd": 1.0},
    }
    config = {"free_tier": {"daily_face_usd": 0.0}}
    g = gw.PayGateway(store, meter, None, models, config, openrouter_rail=rail)
    ah, key = store.create_account(plan="paid", credits_face_usd=1.0)

    worst_split = g._estimate_worst_case({"max_tokens": 20, "messages": [{"role": "user", "content": "hi"}]}, (0.5, 4.0))
    worst_flat = g._estimate_worst_case({"max_tokens": 20, "messages": [{"role": "user", "content": "hi"}]}, 0.5)
    check("reserve uses completion price for max_tokens", worst_split > worst_flat)

    code, resp, headers = g.chat(key, {"model": "split/model", "max_tokens": 20, "messages": [{"role": "user", "content": "hi"}]})
    want = (100 * 0.5 + 40 * 4.0) / 1e6
    check("split chat 200", code == 200)
    check("split debit exact", close(1.0 - store.credits(ah), want))
    check("credit header is post-call", close(float(headers["x-cosmos-credit-balance"]), round(store.credits(ah), 8)))
    row = sqlite3.connect(str(Path(tmp) / "meter.db")).execute(
        "SELECT measured_usd FROM meter_events WHERE event='RUN_SETTLED' AND model='split/model'").fetchone()
    check("RUN_SETTLED measured matches", row is not None and close(float(row[0]), round(want, 8)))

    before = store.credits(ah)
    code, resp, headers = g.chat(key, {"model": "legacy/model", "max_tokens": 20, "messages": [{"role": "user", "content": "hi"}]})
    check("legacy chat 200", code == 200)
    check("legacy debit (in+out)*price", close(before - store.credits(ah), 140 * 1.0 / 1e6))

    # stream path uses the same pricing
    before = store.credits(ah)
    chunks = list(g.chat_stream(key, {"model": "split/model", "max_tokens": 20, "messages": [{"role": "user", "content": "hi"}]}))
    check("stream done", any("[DONE]" in c for c in chunks))
    check("stream debit exact", close(before - store.credits(ah), want))

    # $0 paid-plan account is denied before supply
    ah0, key0 = store.create_account(plan="paid", credits_face_usd=0.0)
    calls = []
    rail.transport = lambda spec: calls.append(1) or transport(spec)
    code, resp, _ = g.chat(key0, {"model": "split/model", "max_tokens": 20, "messages": [{"role": "user", "content": "hi"}]})
    check("$0 paid key 402", code == 402)
    check("no supply call on deny", not calls)

    # vendor-reported cost: bill it only when higher than token math
    check("vendor cost higher wins", close(gw.billed_usd((0.5, 4.0), 100, 40, 0.01), 0.01))
    check("vendor cost lower ignored", close(gw.billed_usd((0.5, 4.0), 100, 40, 1e-9), want))
    check("vendor cost garbage ignored", close(gw.billed_usd((0.5, 4.0), 100, 40, "n/a"), want))
    rail.transport = transport
    usage["cost"] = 0.002
    before = store.credits(ah)
    code, _, _ = g.chat(key, {"model": "split/model", "max_tokens": 20, "messages": [{"role": "user", "content": "hi"}]})
    check("chat bills higher vendor cost", code == 200 and close(before - store.credits(ah), 0.002))
    usage.pop("cost")

    # sub-1e-8 precision: 26 in x 0.021 + 20 out x 0.063 per 1M = 1.806e-06 exactly (no 8-dp settle rounding)
    usage.update({"prompt_tokens": 26, "completion_tokens": 20})
    before = store.credits(ah)
    code, _, _ = g.chat(key, {"model": "tiny/model", "max_tokens": 20, "messages": [{"role": "user", "content": "hi"}]})
    check("tiny debit exact to 1e-12", code == 200 and close(before - store.credits(ah), 1.806e-06))

    print(f"{PASS} pass, {FAIL} fail")
    sys.exit(1 if FAIL else 0)
