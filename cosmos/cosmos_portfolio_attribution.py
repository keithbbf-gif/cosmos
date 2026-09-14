#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Portfolio Studio — canonical product/stage tags for new evidence.

Seven products and nine MOTIF stage ids come from ``cosmos_profiles``.
Historic ledger rows without tags stay ``UNATTRIBUTED``; absent folds are
``UNMEASURED``, never numeric zero. No command-text classification.

    py -3.14 cosmos\\\\cosmos_portfolio_attribution.py --selftest
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_profiles import PROFILE_IDS, STAGE_IDS  # noqa: E402

SCHEMA = "cosmos-portfolio-attribution/1"
UNATTRIBUTED = "UNATTRIBUTED"
UNMEASURED = "UNMEASURED"


class AttributionError(RuntimeError):
    """kind in {BAD_INPUT, PARTIAL}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def normalize_product(value) -> str | None:
    if value is None or value == "":
        return None
    p = str(value).strip().lower()
    if p not in PROFILE_IDS:
        raise AttributionError(
            "BAD_INPUT",
            f"product {value!r} not in canonical catalog {sorted(PROFILE_IDS)}",
        )
    return p


def normalize_stage(value) -> str | None:
    if value is None or value == "":
        return None
    s = str(value).strip().lower()
    if s not in STAGE_IDS:
        raise AttributionError(
            "BAD_INPUT",
            f"stage {value!r} not in canonical MOTIF ids {sorted(STAGE_IDS)}",
        )
    return s


def optional_tags(*, product=None, stage=None) -> dict:
    """Return validated tag fields for a new ledger row, or {} if both omitted."""
    p = normalize_product(product)
    s = normalize_stage(stage)
    if p is None and s is None:
        return {}
    if p is None or s is None:
        raise AttributionError(
            "PARTIAL",
            "product and stage must both be present or both omitted",
        )
    return {"product": p, "stage": s}


def read_tags(payload: dict | None) -> dict:
    """Read tags from an existing payload without inferring from command text."""
    if not isinstance(payload, dict):
        return {
            "product": None,
            "stage": None,
            "attribution": UNATTRIBUTED,
        }
    p = payload.get("product")
    s = payload.get("stage")
    if p is not None and s is not None:
        try:
            p = normalize_product(p)
            s = normalize_stage(s)
        except AttributionError:
            return {
                "product": None,
                "stage": None,
                "attribution": UNATTRIBUTED,
            }
        return {"product": p, "stage": s, "attribution": "TAGGED"}
    return {
        "product": None,
        "stage": None,
        "attribution": UNATTRIBUTED,
    }


def catalog_product_order() -> tuple[str, ...]:
    return tuple(p["id"] for p in __import__("cosmos_profiles").PROFILES)


def empty_product_spend_totals() -> list[dict]:
    """Every catalog product with no measured spend (UNMEASURED, not 0)."""
    return [
        {
            "product": pid,
            "settled_usd": None,
            "n_events": 0,
            "kind": UNMEASURED,
        }
        for pid in catalog_product_order()
    ]


def fold_spend_by_product(records: list[dict]) -> dict:
    """Fold SPEND_SETTLED rows that carry validated product tags."""
    acc: dict[str, dict] = {
        pid: {"settled_usd": 0.0, "n_events": 0, "kind": UNMEASURED}
        for pid in catalog_product_order()
    }
    for rec in records or []:
        if not isinstance(rec, dict) or rec.get("event") != "SPEND_SETTLED":
            continue
        tags = read_tags(rec.get("payload") or {})
        if tags["attribution"] != "TAGGED":
            continue
        pid = tags["product"]
        slot = acc.get(pid)
        if slot is None:
            continue
        measured = (rec.get("payload") or {}).get("measured_usd")
        if measured is None:
            continue
        slot["settled_usd"] += float(measured)
        slot["n_events"] += 1
        slot["kind"] = "MEASURED"
    out = []
    for pid in catalog_product_order():
        row = acc[pid]
        if row["kind"] == "MEASURED":
            out.append({
                "product": pid,
                "settled_usd": round(row["settled_usd"], 6),
                "n_events": row["n_events"],
                "kind": "MEASURED",
            })
        else:
            out.append({
                "product": pid,
                "settled_usd": None,
                "n_events": 0,
                "kind": UNMEASURED,
            })
    return {
        "schema": SCHEMA,
        "products": out,
        "note": (
            "Per-product totals from tagged SPEND_SETTLED only. "
            "Untagged historic spend is not allocated here. "
            "Missing product rows are UNMEASURED, never $0."
        ),
    }


def parse_work_order_tags(raw: dict) -> dict:
    """Optional Product/Stage on a work order (validated together)."""
    if not isinstance(raw, dict):
        return {
            "portfolio_product": None,
            "portfolio_stage": None,
            "attribution": UNATTRIBUTED,
        }
    p = raw.get("Product")
    if p is None:
        p = raw.get("product")
    s = raw.get("Stage")
    if s is None:
        s = raw.get("stage")
    if p is None and s is None:
        return {
            "portfolio_product": None,
            "portfolio_stage": None,
            "attribution": UNATTRIBUTED,
        }
    tags = optional_tags(product=p, stage=s)
    return {
        "portfolio_product": tags["product"],
        "portfolio_stage": tags["stage"],
        "attribution": "TAGGED",
    }


def _selftest() -> int:
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    check("canonical product forge validates",
          lambda: normalize_product("forge") == "forge")
    bad = False
    try:
        normalize_product("not-a-product")
    except AttributionError as e:
        bad = e.kind == "BAD_INPUT"
    check("unknown product REFUSED", lambda: bad)
    partial = False
    try:
        optional_tags(product="forge")
    except AttributionError as e:
        partial = e.kind == "PARTIAL"
    check("product without stage is PARTIAL", lambda: partial)
    check("paired tags validate",
          lambda: optional_tags(product="forge", stage="build")
          == {"product": "forge", "stage": "build"})
    check("read untagged payload is UNATTRIBUTED",
          lambda: read_tags({"rail": "x"})["attribution"] == UNATTRIBUTED)
    check("read tagged payload is TAGGED",
          lambda: read_tags({"product": "docket", "stage": "research"})
          == {"product": "docket", "stage": "research", "attribution": "TAGGED"})
    empty = empty_product_spend_totals()
    check("empty catalog totals are UNMEASURED not zero",
          lambda: len(empty) == len(PROFILE_IDS)
          and all(r["settled_usd"] is None and r["kind"] == UNMEASURED for r in empty))
    fold = fold_spend_by_product([
        {"event": "SPEND_SETTLED", "payload": {
            "measured_usd": 1.5, "product": "forge", "stage": "build"}},
        {"event": "SPEND_SETTLED", "payload": {"measured_usd": 2.0}},
    ])
    forge_row = next(r for r in fold["products"] if r["product"] == "forge")
    crucible_row = next(r for r in fold["products"] if r["product"] == "crucible")
    check("tagged spend folds to product total",
          lambda: forge_row["kind"] == "MEASURED"
          and forge_row["settled_usd"] == 1.5)
    check("untagged spend does not fill other products",
          lambda: crucible_row["kind"] == UNMEASURED
          and crucible_row["settled_usd"] is None)

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (portfolio attribution)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
