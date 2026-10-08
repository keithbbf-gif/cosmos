#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_pricing — min(OR_retail − ε, 5 × COGS), recomputed nightly.

THIS IS THE WIN-WIN-WIN JOB. When COGS falls (utilization up, spot tier added,
owned hardware later), price recomputes — the tribe's discount and our spread
both move, automatically. The split is policy, not a per-decision judgment call.

Pricing rule per model:
    price = min(OR_retail × (1 − ε_pct/100), cap_multiple × COGS)

  - never above the incumbent we respect (OR retail minus a hair)
  - never below cap_multiple × our cost (the margin floor)
  - min() means the user always gets the lower price

Pass-through models (premium, bought at list): provider rates incl. batch/cache/
flex discounts pass at FULL value (the OR model); our take is the 5% surcharge
(3.5% bank + 1.5% net). Two margin sources, cleanly separated:
    manufactured  → 25–80% spread
    pass-through  → 1.5% net
"""
from __future__ import annotations

from typing import Any, Dict, Optional

PROCESSING_RATE = 0.035  # direct merchant account (Commercial Bank & Trust)


def price_per_m(
    cogs_per_m: float,
    or_retail_per_m: float,
    eps_pct: float = 1.0,
    cap_multiple: float = 5.0,
) -> float:
    """The rule. Returns the user-facing $/M for a manufactured model."""
    cogs = max(0.0, float(cogs_per_m))
    or_retail = max(0.0, float(or_retail_per_m))
    or_cap = or_retail * (1.0 - float(eps_pct) / 100.0)
    floor_price = float(cap_multiple) * cogs
    return round(min(or_cap, floor_price), 4)


def margin_per_m(price: float, cogs_per_m: float, processing_rate: float = PROCESSING_RATE) -> float:
    """price − COGS − processing. Processing applies to what we collect."""
    return round(max(0.0, float(price)) - max(0.0, float(cogs_per_m)) - float(price) * float(processing_rate), 4)


def margin_pct(price: float, cogs_per_m: float, processing_rate: float = PROCESSING_RATE) -> float:
    p = max(1e-9, float(price))
    return round(margin_per_m(price, cogs_per_m, processing_rate) / p, 4)


def passthrough_price(
    base_rate_per_m: float,
    surcharge_pct: float = 5.0,
    cache_discount_pct: float = 0.0,
    is_batch: bool = False,
    is_offpeak: bool = False,
) -> float:
    """Pass-through pricing rule (02_THE_FORMULA.md §2.2).
    Provider discounts pass through at FULL value (batch 50% off, offpeak 50% off,
    prompt cache up to 90% off cached input). Our take is the 5% surcharge on
    funding (3.5% bank processing + 1.5% net margin)."""
    rate = max(0.0, float(base_rate_per_m))
    if is_batch:
        rate *= 0.50
    if is_offpeak:
        rate *= 0.50
    if cache_discount_pct > 0:
        rate *= max(0.10, 1.0 - float(cache_discount_pct) / 100.0)
    price = rate * (1.0 + float(surcharge_pct) / 100.0)
    return round(price, 4)


def recompute_model(
    model: Dict[str, Any],
    billed_gpu_seconds: Optional[float] = None,
    tokens_served: Optional[float] = None,
    usd_per_gpu_second: Optional[float] = None,
    eps_pct: Optional[float] = None,
    cap_multiple: Optional[float] = None,
) -> Dict[str, Any]:
    """Nightly recompute for ONE model.

    COGS = (billed_gpu_seconds × usd_per_gpu_second) / (tokens_served / 1e6)
    Falls back to the model's stored cogs when utilization data is absent
    (a fresh endpoint with no traffic keeps its seeded estimate — provenance
    stays `estimate` until real data lands).
    """
    m = dict(model)
    eps = float(eps_pct if eps_pct is not None else m.get("eps_pct", 1.0))
    cap = float(cap_multiple if cap_multiple is not None else m.get("cap_multiple", 5.0))
    rule = m.get("price_rule", "")

    # BYOK lane: user's own keys; Lane B toll applies to coordinated fleet work
    if m.get("byok") is True:
        m["price_per_m_usd"] = 0.0
        m["price_rule"] = "byok_toll"
        m["stocked"] = True
        m["refer_to_or"] = False
        m["margin_per_m_usd"] = 0.0
        m["margin_pct"] = 0.0
        return m

    # 1. Pass-through lane: provider rate + 5% surcharge (1.5% net)
    is_passthrough = rule == "passthrough+surcharge" or m.get("rail") in ("vertex", "bedrock", "azure")
    if is_passthrough:
        or_retail = float(m.get("or_retail_per_m_usd") or 0.0)
        surch = float(m.get("surcharge_pct", 5.0))
        m["price_per_m_usd"] = round(or_retail * (1.0 + surch / 100.0), 4)
        m["cogs_per_m_usd"] = or_retail
        m["cogs_provenance"] = "list"
        m["margin_per_m_usd"] = round(
            m["price_per_m_usd"] - or_retail - (m["price_per_m_usd"] * PROCESSING_RATE), 4
        )
        m["margin_pct"] = round(m["margin_per_m_usd"] / m["price_per_m_usd"], 4) if m["price_per_m_usd"] > 0 else 0.0
        m["surcharge_pct"] = surch
        m["stocked"] = True
        m["refer_to_or"] = False
        return m

    # 2. Manufactured lane: compute or preserve COGS
    if billed_gpu_seconds and tokens_served and usd_per_gpu_second:
        tokens_m = float(tokens_served) / 1_000_000.0
        if tokens_m > 0:
            m["cogs_per_m_usd"] = round(
                (float(billed_gpu_seconds) * float(usd_per_gpu_second)) / tokens_m, 4
            )
            m["cogs_provenance"] = "measured"
        else:
            m["cogs_provenance"] = "estimate"
    else:
        m.setdefault("cogs_provenance", "estimate")

    cogs = float(m.get("cogs_per_m_usd") or 0.0)
    or_retail = float(m.get("or_retail_per_m_usd") or 0.0)
    if or_retail <= 0:
        # No OR reference (our own manufactured-only model): price at the cap floor.
        m["price_per_m_usd"] = round(cap * cogs, 4) if cogs > 0 else 0.0
        m["price_rule"] = "cap_floor"
    else:
        m["price_per_m_usd"] = price_per_m(cogs, or_retail, eps, cap)
        m["price_rule"] = "min(or-eps, cap)"
    m["margin_per_m_usd"] = margin_per_m(m["price_per_m_usd"], cogs)
    m["margin_pct"] = margin_pct(m["price_per_m_usd"], cogs)
    m["surcharge_pct"] = 5.0  # customer-facing on funding; 3.5% bank + 1.5% net
    # The sourcing rule in code: sell what you make or buy at a discount — refer the rest.
    # Unprofitable manufacture is never stocked; the model routes to OR via referral
    # (earn ~3% instead of losing the processing spread).
    m["stocked"] = m["margin_per_m_usd"] > 0
    m["refer_to_or"] = not m["stocked"]
    return m


def recompute_models(
    models: Dict[str, Any],
    utilization: Optional[Dict[str, Dict[str, float]]] = None,
    eps_pct: Optional[float] = None,
    cap_multiple: Optional[float] = None,
) -> Dict[str, Any]:
    """Nightly job over the whole registry.

    `utilization`: {model_id: {"billed_gpu_seconds": …, "tokens_served": …,
    "usd_per_gpu_second": …}} — from the meter/RunPod reporting. Absent models
    keep their stored COGS (provenance `estimate`).
    """
    utilization = utilization or {}
    out: Dict[str, Any] = {}
    for model_id, m in models.items():
        u = utilization.get(model_id) or {}
        out[model_id] = recompute_model(
            m,
            billed_gpu_seconds=u.get("billed_gpu_seconds"),
            tokens_served=u.get("tokens_served"),
            usd_per_gpu_second=u.get("usd_per_gpu_second"),
            eps_pct=eps_pct,
            cap_multiple=cap_multiple,
        )
    return out
