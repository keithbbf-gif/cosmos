#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Portfolio Studio — canonical product/stage tags for new evidence (PS-06).

Seven occupancy products and nine MOTIF stage ids are the closed catalogs
(``cosmos_profiles.PROFILE_IDS`` / ``STAGE_IDS``). New job, work-order,
spend, and porosity rows may carry a validated pair; historic rows without
the pair stay explicitly ``UNATTRIBUTED``. Per-product spend totals that
cannot be computed from tagged settles are ``UNMEASURED``, never ``0``.

No command-text classification. Tags are only what the writer stamped.

    py -3.14 cosmos\\\\cosmos_portfolio_attribution.py --selftest
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_profiles import PROFILE_IDS, PROFILES, STAGE_IDS  # noqa: E402

SCHEMA = "cosmos-portfolio-attribution/1"
UNATTRIBUTED = "UNATTRIBUTED"
UNMEASURED = "UNMEASURED"
TAGGED = "TAGGED"


class AttributionError(RuntimeError):
    """kind in {BAD_INPUT, PARTIAL}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def catalog_product_ids() -> tuple[str, ...]:
    return tuple(p["id"] for p in PROFILES)


def normalize_product(value) -> str | None:
    if value is None or value == "":
        return None
    p = str(value).strip().lower()
    if p not in PROFILE_IDS:
        raise AttributionError(
            "BAD_INPUT",
            f"product {value!r} not in canonical catalog "
            f"{sorted(PROFILE_IDS)}",
        )
    return p


def normalize_stage(value) -> str | None:
    if value is None or value == "":
        return None
    s = str(value).strip().lower()
    if s not in STAGE_IDS:
        raise AttributionError(
            "BAD_INPUT",
            f"stage {value!r} not in canonical MOTIF ids "
            f"{sorted(STAGE_IDS)}",
        )
    return s


def optional_tags(*, product=None, stage=None) -> dict:
    """Validated ``{product, stage}`` for a new row, or ``{}`` if both omitted.

    One without the other is PARTIAL — refuse rather than invent the missing
    half or quietly drop the present half.
    """
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
    """Read stamped tags. Never infers from command / task text."""
    empty = {
        "product": None,
        "stage": None,
        "attribution": UNATTRIBUTED,
    }
    if not isinstance(payload, dict):
        return empty
    raw_p = payload.get("product")
    raw_s = payload.get("stage")
    if raw_p is None or raw_s is None or raw_p == "" or raw_s == "":
        return empty
    try:
        p = normalize_product(raw_p)
        s = normalize_stage(raw_s)
    except AttributionError:
        return empty
    if p is None or s is None:
        return empty
    return {"product": p, "stage": s, "attribution": TAGGED}


def porosity_optional_tags(*, profile=None, stage=None, product=None) -> dict:
    """Portfolio tags for a porosity row without breaking free-form profiles.

    Operational ``profile`` / ``stage`` stay as the porosity module writes
    them. Portfolio ``product``+``stage`` are stamped only when both ends
    validate against the closed catalogs (explicit ``product`` wins over
    profile when provided). Partial / non-canon → no portfolio tags
    (``UNATTRIBUTED`` when read later).
    """
    p_src = product if product not in (None, "") else profile
    s_src = stage
    try:
        return optional_tags(product=p_src, stage=s_src)
    except AttributionError:
        return {}


def empty_product_spend_totals() -> list[dict]:
    """Every catalog product with no measured tagged spend (never $0)."""
    return [
        {
            "product": pid,
            "settled_usd": None,
            "n_events": 0,
            "kind": UNMEASURED,
        }
        for pid in catalog_product_ids()
    ]


def fold_spend_by_product(records) -> dict:
    """Fold ``SPEND_SETTLED`` rows that carry a validated product/stage pair.

    Untagged historic settles are not allocated into any product bucket.
    Catalog products with no tagged settles stay ``UNMEASURED`` / ``null``.
    """
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for rec in records or []:
        if not isinstance(rec, dict) or rec.get("event") != "SPEND_SETTLED":
            continue
        payload = rec.get("payload") or {}
        tags = read_tags(payload)
        if tags["attribution"] != TAGGED:
            continue
        measured = payload.get("measured_usd")
        if measured is None:
            continue
        pid = tags["product"]
        sums[pid] = sums.get(pid, 0.0) + float(measured)
        counts[pid] = counts.get(pid, 0) + 1
    products = []
    for pid in catalog_product_ids():
        if pid in sums:
            products.append({
                "product": pid,
                "settled_usd": round(sums[pid], 6),
                "n_events": counts[pid],
                "kind": "MEASURED",
            })
        else:
            products.append({
                "product": pid,
                "settled_usd": None,
                "n_events": 0,
                "kind": UNMEASURED,
            })
    return {
        "schema": SCHEMA,
        "products": products,
        "kind": (
            "MEASURED" if any(p["kind"] == "MEASURED" for p in products)
            else UNMEASURED
        ),
        "note": (
            "Per-product totals from tagged SPEND_SETTLED only. "
            "Untagged historic spend stays UNATTRIBUTED and is not "
            "allocated here. Missing product rows are UNMEASURED, never $0."
        ),
    }


def parse_work_order_tags(raw: dict) -> dict:
    """Optional Product/Stage on a work order (stored beside output ``product``).

    Accepts ``Product``/``Stage`` (preferred) or lowercase ``product``/``stage``
    only when ``product`` is a canonical catalog id — so an output-filename
    ``product`` key is never mistaken for portfolio attribution.
    """
    empty = {
        "portfolio_product": None,
        "portfolio_stage": None,
        "attribution": UNATTRIBUTED,
    }
    if not isinstance(raw, dict):
        return empty
    p = raw.get("Product")
    s = raw.get("Stage")
    if p in (None, "") and s in (None, ""):
        lp = raw.get("product")
        ls = raw.get("stage")
        lp_fold = str(lp).strip().lower() if lp not in (None, "") else ""
        if lp_fold in PROFILE_IDS:
            p, s = lp, ls
        else:
            return empty
    if p in (None, "") and s in (None, ""):
        return empty
    tags = optional_tags(product=p, stage=s)
    return {
        "portfolio_product": tags["product"],
        "portfolio_stage": tags["stage"],
        "attribution": TAGGED,
    }


def _selftest() -> int:
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    check("canonical product forge validates",
          lambda: normalize_product("Forge") == "forge")
    bad = False
    try:
        normalize_product("chatbot")
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
          lambda: read_tags({"rail": "x", "command": "forge build"})
          ["attribution"] == UNATTRIBUTED)
    check("read does not classify command text",
          lambda: read_tags({"command": "crucible:round research"})
          ["attribution"] == UNATTRIBUTED)
    check("read tagged payload is TAGGED",
          lambda: read_tags({"product": "docket", "stage": "research"})
          == {"product": "docket", "stage": "research", "attribution": TAGGED})
    empty = empty_product_spend_totals()
    check("empty catalog totals are UNMEASURED not zero",
          lambda: len(empty) == len(PROFILE_IDS)
          and all(r["settled_usd"] is None and r["kind"] == UNMEASURED
                  for r in empty))
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
    check("untagged spend does not zero-fill other products",
          lambda: crucible_row["kind"] == UNMEASURED
          and crucible_row["settled_usd"] is None)
    check("porosity tags when profile+stage are both canon",
          lambda: porosity_optional_tags(profile="forge", stage="consensus1")
          == {"product": "forge", "stage": "consensus1"})
    check("porosity omits tags when stage empty (UNATTRIBUTED later)",
          lambda: porosity_optional_tags(profile="forge", stage="") == {})

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (portfolio attribution)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
