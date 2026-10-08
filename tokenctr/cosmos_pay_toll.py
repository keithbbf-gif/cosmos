#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_toll — Lane B: the declining bracket curve (cosmos-meter/1).

Marginal brackets, no cliffs. Charges go DOWN, not up, with volume — the whales
are the best customers, not churn risks. 0% under $100/mo is the tribe promise.

    $0–100    0%     (free, forever — stewardship-class)
    $100–200  2%
    $201–999  1.5%
    $1k+      1%

Pure function: coordinated measured_usd in, toll out. The monthly statement is
a fold over the meter's Lane B RUN_SETTLED events — never a second book.

Stewardship-class: the bracket table is a promise. Raise later is available;
cut later is a betrayal event.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

# (floor_usd, ceiling_usd_exclusive_or_None, rate) — marginal slices
DEFAULT_BRACKETS: Tuple[Tuple[float, Optional[float], float], ...] = (
    (0.0, 100.0, 0.0),
    (100.0, 200.0, 0.02),
    (200.0, 1000.0, 0.015),
    (1000.0, None, 0.01),
)


def _brackets(config: Optional[List[List]] = None) -> Tuple[Tuple[float, Optional[float], float], ...]:
    if not config:
        return DEFAULT_BRACKETS
    return tuple((float(f), (float(c) if c is not None else None), float(r)) for f, c, r in config)


def toll_usd(coordinated_usd: float, brackets: Optional[List[List]] = None) -> float:
    """Marginal bracket computation. $5,000 → 2 + 12 + 40 = $54.00 (effective 1.08%)."""
    amount = max(0.0, float(coordinated_usd))
    total = 0.0
    for floor, ceiling, rate in _brackets(brackets):
        if amount <= floor:
            break
        top = amount if ceiling is None else min(amount, ceiling)
        total += (top - floor) * rate
    return round(total, 4)


def effective_rate(coordinated_usd: float, brackets: Optional[List[List]] = None) -> float:
    """Total toll ÷ spend. A $5k/mo whale pays ~1.08% — never a cliff."""
    amount = max(0.0, float(coordinated_usd))
    if amount <= 0:
        return 0.0
    return toll_usd(amount, brackets) / amount


def free_allowance_remaining(coordinated_usd: float, brackets: Optional[List[List]] = None) -> float:
    """Dollars of coordinated spend still inside the 0% band this month."""
    first = _brackets(brackets)[0]
    floor, ceiling, rate = first
    if rate != 0.0:
        return 0.0
    return max(0.0, ceiling - max(0.0, float(coordinated_usd)))


def statement_line(
    lane_b_events: Iterable[Dict],
    period: str,
    brackets: Optional[List[List]] = None,
    processing_rate: float = 0.035,
) -> Dict:
    """Fold Lane B RUN_SETTLED events for a period into one statement line.

    Reconciliation invariant: statement.basis_measured_usd == Σ(event.measured_usd).
    Provenance discipline: only `measured`/`billed` events count — estimates never bill.
    """
    total_measured = 0.0
    runs = 0
    unpriced = 0
    for ev in lane_b_events:
        if not isinstance(ev, dict):
            continue
        if ev.get("event") != "RUN_SETTLED" or ev.get("lane") != "B":
            continue
        cost = ev.get("cost") or {}
        if not isinstance(cost, dict):
            unpriced += 1
            continue
        prov = cost.get("provenance")
        measured = cost.get("measured_usd")
        if prov not in ("measured", "billed") or measured is None:
            unpriced += 1
            continue
        try:
            total_measured += float(measured)
        except (TypeError, ValueError):
            unpriced += 1
            continue
        runs += 1
    gross = toll_usd(total_measured, brackets)
    net = round(gross * (1.0 - processing_rate), 4)
    return {
        "period": period,
        "line": "toll",
        "runs": runs,
        "unpriced_held": unpriced,
        "basis_measured_usd": round(total_measured, 4),
        "toll_gross_usd": gross,
        "toll_net_usd": net,
        "effective_rate": round(effective_rate(total_measured, brackets), 6),
        "processing_rate": processing_rate,
    }
