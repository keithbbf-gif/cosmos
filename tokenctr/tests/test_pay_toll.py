#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_toll â€” bracket boundaries + statement fold. Direct-run, house style."""
import sys
import os
import sys
import os
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cosmos_pay_toll as toll

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


# --- boundaries: the 0% band is the tribe promise ---
check("toll(0) == 0", toll.toll_usd(0) == 0.0)
check("toll(99.99) == 0", toll.toll_usd(99.99) == 0.0)
check("toll(100) == 0 (ceiling exclusive)", toll.toll_usd(100) == 0.0)
check("toll(100.01) == 0.0002 (2% on the slice)", abs(toll.toll_usd(100.01) - 0.0002) < 1e-9)

# --- mid brackets ---
check("toll(150) == 1.00", toll.toll_usd(150) == 1.0)
check("toll(200) == 2.00", toll.toll_usd(200) == 2.0)
check("toll(250) == 2.75", toll.toll_usd(250) == 2.75)
check("toll(999) == 13.985 (1.5% runs to $999)", abs(toll.toll_usd(999) - 13.985) < 1e-9)
check("toll(1000) == 14.00 (1% starts at $1k)", toll.toll_usd(1000) == 14.0)

# --- the whale: charges go DOWN with volume ---
check("toll(5000) == 54.00", toll.toll_usd(5000) == 54.0)
check("effective_rate(5000) ~ 1.08%", abs(toll.effective_rate(5000) - 0.0108) < 1e-6)
marg_150 = toll.toll_usd(151) - toll.toll_usd(150)      # the 150th dollar: 2% slice
marg_5000 = toll.toll_usd(5001) - toll.toll_usd(5000)   # the 5000th dollar: 1% slice
check("MARGINAL rates regressive: 5000th dollar (1%) < 150th dollar (2%)", marg_5000 < marg_150)
check("effective rate declines past mid-volume: 5000 (1.08%) < 1000 (1.40%)",
      toll.effective_rate(5000) < toll.effective_rate(1000))

# --- free allowance ---
check("free_allowance_remaining(50) == 50", toll.free_allowance_remaining(50) == 50.0)
check("free_allowance_remaining(150) == 0", toll.free_allowance_remaining(150) == 0.0)

# --- statement fold: provenance discipline ---
events = [
    {"event": "RUN_SETTLED", "lane": "B", "cost": {"measured_usd": 30.0, "provenance": "measured"}},
    {"event": "RUN_SETTLED", "lane": "B", "cost": {"measured_usd": 20.0, "provenance": "billed"}},
    {"event": "RUN_SETTLED", "lane": "B", "cost": {"estimated_usd": 99.0, "provenance": "estimate"}},  # never bills
    {"event": "RUN_SETTLED", "lane": "A", "cost": {"measured_usd": 500.0, "provenance": "measured"}},  # wrong lane
    {"event": "RUN_UNPRICED", "lane": "B", "cost": {"estimated_usd": 5.0, "provenance": "estimate"}},
]
line = toll.statement_line(events, "2026-10")
check("statement basis == 50.0 (measured+billed only, Lane B only)", line["basis_measured_usd"] == 50.0)
check("statement toll_gross == 0.0 (under the free band)", line["toll_gross_usd"] == 0.0)
check("statement unpriced_held == 1", line["unpriced_held"] == 1)
check("statement runs == 2", line["runs"] == 2)

# --- custom brackets (the stewardship lever) ---
custom = [[0, 50, 0.0], [50, None, 0.03]]
check("custom brackets honored", toll.toll_usd(100, custom) == 0.03 * 50)

print(f"\n{PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)

