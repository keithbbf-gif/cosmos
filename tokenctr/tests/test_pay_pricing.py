#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_pricing â€” the rule, the recompute, the sourcing rule in code."""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cosmos_pay_pricing as pricing

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


if __name__ == "__main__":
    # --- the rule: min(OR âˆ’ Îµ, 5Ã— COGS) ---
    check("price(0.20, 0.80) == 0.792 (ORâˆ’Îµ binds)", pricing.price_per_m(0.20, 0.80) == 0.792)
    check("price(0.20, 0.30) == 0.297 (ORâˆ’Îµ binds)", pricing.price_per_m(0.20, 0.30) == 0.297)
    check("price(0.10, 5.00) == 0.50 (cap binds â€” fat margin, still 10Ã— under OR)",
          pricing.price_per_m(0.10, 5.00) == 0.50)
    check("price never above ORâˆ’Îµ", pricing.price_per_m(0.01, 0.10) <= 0.10 * 0.99)

    # --- margin ---
    m = pricing.margin_per_m(0.792, 0.20)
    check("margin(0.792, 0.20) == 0.5643 (3.5% processing)", abs(m - 0.5643) < 1e-6)
    check("margin_pct(0.792, 0.20) â‰ˆ 71%", abs(pricing.margin_pct(0.792, 0.20) - 0.7124) < 1e-3)

    # --- the sourcing rule in code: unprofitable manufacture â†’ refer to OR ---
    r = pricing.recompute_model({"cogs_per_m_usd": 0.20, "or_retail_per_m_usd": 0.10})
    # price = min(0.099, 1.0) = 0.099 < COGS 0.20 â†’ margin negative â†’ refer_to_or
    check("unprofitable manufacture â†’ refer_to_or", r.get("refer_to_or") is True and r.get("stocked") is False)

    r2 = pricing.recompute_model({"cogs_per_m_usd": 0.20, "or_retail_per_m_usd": 0.80})
    check("profitable manufacture â†’ stocked", r2.get("stocked") is True and r2.get("refer_to_or") is False)
    check("stocked price == 0.792", r2.get("price_per_m_usd") == 0.792)

    # --- nightly recompute: utilization moves COGS, the rule moves the price ---
    models = {"qwen3-coder-30b-fp8": {"cogs_per_m_usd": 0.18, "or_retail_per_m_usd": 0.30}}
    util = {"qwen3-coder-30b-fp8": {"billed_gpu_seconds": 3600.0, "tokens_served": 72_000_000,
                                    "usd_per_gpu_second": 0.0001}}
    out = pricing.recompute_models(models, util)
    m = out["qwen3-coder-30b-fp8"]
    # COGS = 3600 Ã— 0.0001 / 72 = 0.005/M â€” utilization collapsed the cost
    check("recompute COGS measured == 0.005", m["cogs_per_m_usd"] == 0.005)
    check("recompute provenance == measured", m["cogs_provenance"] == "measured")
    check("recompute price == min(0.297, 0.025) = 0.025 â€” the tribe's discount moved",
          m["price_per_m_usd"] == 0.025)
    check("recompute margin â‰ˆ 0.0191 (25% of a much smaller number â€” the split held)",
          abs(m["margin_per_m_usd"] - 0.0191) < 1e-3)

    # --- no utilization data â†’ estimate provenance, price unchanged ---
    out2 = pricing.recompute_models(models, {})
    m2 = out2["qwen3-coder-30b-fp8"]
    check("no utilization â†’ estimate provenance", m2["cogs_provenance"] == "estimate")
    check("no utilization â†’ price from stored COGS", m2["price_per_m_usd"] == pricing.price_per_m(0.18, 0.30))

    # --- no OR reference â†’ cap floor ---
    r3 = pricing.recompute_model({"cogs_per_m_usd": 0.20})
    check("no OR retail â†’ cap floor 5Ã— COGS = 1.00", r3["price_per_m_usd"] == 1.0 and r3["price_rule"] == "cap_floor")

    print(f"\n{PASS} pass, {FAIL} fail")
    sys.exit(1 if FAIL else 0)


