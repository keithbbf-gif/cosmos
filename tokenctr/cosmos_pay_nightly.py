#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_nightly — the nightly job: COGS/price recompute + monthly toll.

THIS IS THE WIN-WIN-WIN JOB (see 02_THE_FORMULA.md §2.3):
    COGS falls (utilization up, spot tier, owned HW) → price recomputes →
    the tribe's discount and our spread both move — automatically.

Usage:
    py -3 cosmos_pay_nightly.py                    # recompute prices from utilization.json (if present)
    py -3 cosmos_pay_nightly.py --toll 2026-10     # monthly toll statement from the meter DB

Inputs:
    ~/.cosmos_pay/models.json        — the supply registry (written back)
    ~/.cosmos_pay/utilization.json   — OPTIONAL per-model {billed_gpu_seconds, tokens_served}
                                       (from RunPod reporting or hand-filled; absent = keep stored COGS)
    ~/.cosmos_pay/meter.db           — Lane B events for the toll statement
    ~/.cosmos_pay/config.json        — eps_pct, cap_multiple, toll_brackets
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cosmos_pay_config as cfg
import cosmos_pay_meter as meter_mod
import cosmos_pay_pricing as pricing
import cosmos_pay_toll as toll_mod


def recompute_prices() -> Dict[str, Any]:
    models = cfg.load_models()
    util_path = cfg.ROOT / "utilization.json"
    utilization = {}
    if util_path.exists():
        utilization = json.loads(util_path.read_text(encoding="utf-8"))
        print(f"utilization.json found: {len(utilization)} model(s)")
    else:
        print("no utilization.json -- prices recomputed from stored COGS (provenance: estimate)")
    out = pricing.recompute_models(
        models, utilization,
        eps_pct=cfg.load_config().get("pricing", {}).get("eps_pct"),
        cap_multiple=cfg.load_config().get("pricing", {}).get("cap_multiple"),
    )
    cfg.save_models(out)
    for mid, m in out.items():
        flag = "STOCKED" if m.get("stocked") else "REFER-TO-OR (unprofitable manufacture)"
        print(f"  {mid}: COGS ${m.get('cogs_per_m_usd')}/M ({m.get('cogs_provenance')}) -> "
              f"price ${m.get('price_per_m_usd')}/M -> margin ${m.get('margin_per_m_usd')}/M "
              f"({m.get('margin_pct', 0) * 100:.0f}%) [{flag}]")
    return out


def monthly_toll(period: str) -> Dict[str, Any]:
    meter = meter_mod.Meter(str(cfg.METER_DB))
    brackets = cfg.load_config().get("toll_brackets")
    events = [e for e in meter.tail(100000) if e.get("at", "").startswith(period)]
    line = toll_mod.statement_line(events, period, brackets)
    print(f"toll statement {period}: measured ${line['basis_measured_usd']} -> "
          f"gross ${line['toll_gross_usd']} -> net ${line['toll_net_usd']} "
          f"(effective {line['effective_rate'] * 100:.2f}%, unpriced held: {line['unpriced_held']})")
    return line


def main() -> None:
    ap = argparse.ArgumentParser(description="TokenCenter nightly job")
    ap.add_argument("--toll", metavar="YYYY-MM", help="compute the monthly toll statement")
    args = ap.parse_args()
    if args.toll:
        monthly_toll(args.toll)
    else:
        recompute_prices()
    print(f"nightly job done at {time.strftime('%Y-%m-%dT%H:%M:%S%z')}")


if __name__ == "__main__":
    main()
