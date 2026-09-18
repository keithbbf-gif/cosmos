#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_womb — DEFINE then pick a pair (high orth, low porosity, GAC).

WOMB seats two named pins on one target axis. Reads Opus T
(`cosmos-porosity-tensor/5`) and the model-rater row. Does not rewrite
the T formula. GET never mkdir. GET never invents. Missing cell =
UNMEASURED (skip that pair). UNMEASURED completion rate = skip, not $0.

GAC: completion USD/1M ≤ budget_out (default $1/M).
Always exclude openai/gpt-5.6-sol and non-flex Luna.
Luna Flex (openai/gpt-5.6-luna) is IN if its measured rate ≤ budget.

    py -3.14 cosmos\\cosmos_womb.py --selftest
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-womb-seat/1"
SOL_SLUG = "openai/gpt-5.6-sol"
LUNA_FLEX_SLUG = "openai/gpt-5.6-luna"
DEFAULT_AXIS = "coding"
DEFAULT_BUDGET_OUT = 1.0


class WombError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _slug(row) -> str:
    if isinstance(row, dict):
        return str(row.get("id") or row.get("model") or row.get("slug") or "").strip()
    return str(row or "").strip()


def _name(slug: str) -> str:
    return slug.split("/", 1)[-1].lower()


def _f(v):
    if v is None or v == "":
        return None
    if isinstance(v, str) and v.strip().upper() == "UNMEASURED":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def is_sol(slug: str) -> bool:
    return _name(slug).startswith("gpt-5.6-sol")


def is_luna(slug: str) -> bool:
    return "luna" in _name(slug)


def is_luna_flex(slug: str, row=None) -> bool:
    """Named Flex pin, :flex variant, or an explicit flex marker on the row."""
    n = _name(slug)
    if n == "gpt-5.6-luna" or n.startswith("gpt-5.6-luna:"):
        return True
    if "luna" in n and "flex" in n:
        return True
    if not isinstance(row, dict):
        return False
    if row.get("flex") is True and is_luna(slug):
        return True
    for key in ("provider", "provider_tag", "via", "endpoint"):
        if "flex" in str(row.get(key) or "").lower() and is_luna(slug):
            return True
    return False


def completion_usd_per_m(row) -> float | None:
    """USD / 1M completion tokens. None = UNMEASURED (never treat as $0)."""
    if not isinstance(row, dict):
        return None
    if str(row.get("completion_kind") or "").upper() == "UNMEASURED":
        return None
    for key in ("completion_per_m", "completion_usd_per_m", "out_usd_per_m"):
        if key not in row:
            continue
        return _f(row.get(key))
    pricing = row.get("pricing")
    if isinstance(pricing, dict) and "completion" in pricing:
        raw = _f(pricing.get("completion"))
        if raw is None:
            return None
        # OpenRouter pricing.completion is per-token (same as model_rater).
        return round(raw * 1_000_000.0, 6)
    return None


def _unmeasured(axis: str, reason: str, *, a=None, b=None, orth=None, mag=None) -> dict:
    return {
        "schema": SCHEMA,
        "ok": True,
        "kind": "UNMEASURED",
        "a": a,
        "b": b,
        "axis": axis,
        "orth": orth,
        "mag": mag,
        "reason": reason,
    }


def _measured(a: str, b: str, axis: str, orth: float, mag: float, reason: str) -> dict:
    lo, hi = (a, b) if a.lower() <= b.lower() else (b, a)
    return {
        "schema": SCHEMA,
        "ok": True,
        "kind": "MEASURED",
        "a": lo,
        "b": hi,
        "axis": axis,
        "orth": orth,
        "mag": mag,
        "reason": reason,
    }


def eligible_rows(rater_rows, budget_out: float) -> dict[str, dict]:
    """Slug → row for pins that pass GAC / SOL / non-flex Luna filters."""
    out: dict[str, dict] = {}
    for row in rater_rows or []:
        if not isinstance(row, dict):
            continue
        slug = _slug(row)
        if not slug:
            continue
        if is_sol(slug):
            continue
        if is_luna(slug) and not is_luna_flex(slug, row):
            continue
        rate = completion_usd_per_m(row)
        if rate is None:
            continue
        if rate > float(budget_out):
            continue
        out[slug] = row
    return out


def _axis_of(cell: dict) -> str:
    return str(cell.get("axis") or "").strip().lower()


def _pair_slugs(cell: dict) -> tuple[str, str] | None:
    a = str(cell.get("model_a") or cell.get("a") or cell.get("agent") or "").strip()
    b = str(cell.get("model_b") or cell.get("b") or cell.get("vs") or "").strip()
    if not a or not b or a.lower() == b.lower():
        return None
    return a, b


def _orth(cell: dict):
    """Read T. Prefer orth_sketch; else xor_err − cofail. Do not invent."""
    sketch = _f(cell.get("orth_sketch"))
    if sketch is not None:
        return sketch
    xor_err = _f(cell.get("xor_err"))
    cofail = _f(cell.get("cofail"))
    if xor_err is not None and cofail is not None:
        return xor_err - cofail
    return None


def _mag(cell: dict):
    return _f(cell.get("mag"))


def _iter_cells(porosity_fold):
    """Yield pair×axis cells from a fold, snapshot, tensors, or list."""
    if porosity_fold is None:
        return
    if isinstance(porosity_fold, list):
        for cell in porosity_fold:
            if isinstance(cell, dict):
                yield cell
        return
    if not isinstance(porosity_fold, dict):
        return
    pairs = porosity_fold.get("pairs")
    if isinstance(pairs, list):
        for cell in pairs:
            if isinstance(cell, dict):
                yield cell
        tensors = porosity_fold.get("tensors")
        if isinstance(tensors, dict) and pairs:
            return
    tensors = porosity_fold.get("tensors")
    if isinstance(tensors, dict):
        for agent, vs_map in tensors.items():
            if not isinstance(vs_map, dict):
                continue
            for vs, axes in vs_map.items():
                if not isinstance(axes, dict):
                    continue
                for ax, params in axes.items():
                    if not isinstance(params, dict):
                        continue
                    cell = dict(params)
                    cell.setdefault("model_a", agent)
                    cell.setdefault("model_b", vs)
                    cell.setdefault("axis", ax)
                    yield cell
        if tensors:
            return
    for key, cell in porosity_fold.items():
        if key in ("pairs", "tensors", "tensor", "complement", "schema",
                   "kind", "ok", "n_obs", "n_pairs", "axes", "note",
                   "tensors_shape", "last_obs", "coverage", "db"):
            continue
        if not isinstance(cell, dict):
            continue
        out = dict(cell)
        if isinstance(key, tuple) and len(key) >= 3:
            out.setdefault("model_a", key[0])
            out.setdefault("model_b", key[1])
            out.setdefault("axis", key[2])
        yield out


def pick_pair(porosity_fold, rater_rows, *, axis: str,
              budget_out: float = DEFAULT_BUDGET_OUT) -> dict:
    """Pick the measured pair with max orth_sketch, then min mag, under GAC.

    Missing pair×axis cell is UNMEASURED (skip). UNMEASURED rate is skip,
    not $0. SOL and non-flex Luna are refused. Never invents a score.
    """
    ax = str(axis or "").strip().lower() or DEFAULT_AXIS
    try:
        cap = float(budget_out)
    except (TypeError, ValueError):
        raise WombError("BAD_INPUT", f"budget_out must be a number, got {budget_out!r}")
    allowed = eligible_rows(rater_rows, cap)
    if not allowed:
        return _unmeasured(
            ax,
            "UNMEASURED: no rater slug under GAC (SOL / non-flex Luna / "
            "UNMEASURED rate skipped)",
        )
    allowed_l = {s.lower(): s for s in allowed}
    best = None
    saw_sol = False
    saw_axis = False
    for cell in _iter_cells(porosity_fold):
        if _axis_of(cell) != ax:
            continue
        saw_axis = True
        slugs = _pair_slugs(cell)
        if slugs is None:
            continue
        a, b = slugs
        if is_sol(a) or is_sol(b):
            saw_sol = True
            continue
        ia = allowed_l.get(a.lower())
        ib = allowed_l.get(b.lower())
        if ia is None or ib is None:
            continue
        orth = _orth(cell)
        mag = _mag(cell)
        if orth is None or mag is None:
            continue
        cand = (ia, ib, float(orth), float(mag))
        if best is None:
            best = cand
            continue
        # Maximize orthogonality; then minimize pair porosity mag.
        _ba, _bb, borth, bmag = best
        if (orth, -mag) > (borth, -bmag):
            best = cand
            continue
        if orth == borth and mag == bmag:
            lo_new, hi_new = (ia, ib) if ia.lower() <= ib.lower() else (ib, ia)
            lo_old, hi_old = (_ba, _bb) if _ba.lower() <= _bb.lower() else (_bb, _ba)
            if (lo_new.lower(), hi_new.lower()) < (lo_old.lower(), hi_old.lower()):
                best = cand
    if best is None:
        if saw_sol and not saw_axis:
            reason = "UNMEASURED: refused openai/gpt-5.6-sol; no other pair"
        elif saw_sol:
            reason = (
                "UNMEASURED: refused openai/gpt-5.6-sol; no remaining "
                "measured pair on axis under GAC"
            )
        elif not saw_axis:
            reason = f"UNMEASURED: no pair cell on axis {ax!r}"
        else:
            reason = (
                f"UNMEASURED: no measured pair on axis {ax!r} after GAC "
                "(missing cell skipped; UNMEASURED rate skipped)"
            )
        return _unmeasured(ax, reason)
    a, b, orth, mag = best
    return _measured(
        a, b, ax, orth, mag,
        "MEASURED: high-orth low-porosity pair under GAC "
        f"(orth={orth}, mag={mag}, budget_out={cap})",
    )


def seat(paths, *, axis: str = DEFAULT_AXIS,
         budget_out: float = DEFAULT_BUDGET_OUT) -> dict:
    """Fold live porosity + rater. GET never mkdir. Never invents."""
    from cosmos_model_rater import load_catalog
    from cosmos_porosity import snapshot as porosity_snapshot

    fold = porosity_snapshot(paths)
    cat = load_catalog(paths)
    rows = cat.get("models") or []
    rec = pick_pair(fold, rows, axis=axis, budget_out=budget_out)
    rec["n_obs"] = fold.get("n_obs") if isinstance(fold, dict) else 0
    rec["n_catalog"] = cat.get("n") or len(rows)
    rec["gac_budget_out"] = float(budget_out)
    return rec


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths
    from cosmos_porosity import store_dir

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    glm = "z-ai/glm-5.3-flash"
    ds = "deepseek/deepseek-v4-flash"
    luna = LUNA_FLEX_SLUG
    luna_pro = "openai/gpt-5.6-luna-pro"
    sol = SOL_SLUG
    mystery = "vendor/unmeasured-out"
    pricey = "vendor/over-budget"

    rows = [
        {"id": glm, "completion_per_m": 0.14},
        {"id": ds, "completion_per_m": 0.28},
        {"id": luna, "completion_per_m": 0.60},
        {"id": luna_pro, "completion_per_m": 0.50},
        {"id": sol, "completion_per_m": 10.0},
        {"id": mystery},
        {"id": pricey, "completion_per_m": 5.0},
    ]
    fold = {
        "pairs": [
            {"model_a": glm, "model_b": ds, "axis": "coding",
             "orth_sketch": 0.40, "mag": 1.20,
             "xor_err": 0.70, "cofail": 0.30},
            {"model_a": luna, "model_b": ds, "axis": "coding",
             "orth_sketch": 0.80, "mag": 0.90,
             "xor_err": 0.90, "cofail": 0.10},
            {"model_a": luna, "model_b": glm, "axis": "coding",
             "orth_sketch": 0.80, "mag": 0.40,
             "xor_err": 0.85, "cofail": 0.05},
            {"model_a": sol, "model_b": glm, "axis": "coding",
             "orth_sketch": 0.99, "mag": 0.05,
             "xor_err": 1.0, "cofail": 0.0},
            {"model_a": mystery, "model_b": glm, "axis": "coding",
             "orth_sketch": 0.95, "mag": 0.10,
             "xor_err": 0.95, "cofail": 0.0},
            {"model_a": pricey, "model_b": glm, "axis": "coding",
             "orth_sketch": 0.94, "mag": 0.10,
             "xor_err": 0.94, "cofail": 0.0},
            {"model_a": luna_pro, "model_b": glm, "axis": "coding",
             "orth_sketch": 0.93, "mag": 0.10,
             "xor_err": 0.93, "cofail": 0.0},
            {"model_a": luna, "model_b": ds, "axis": "spec",
             "orth_sketch": 0.10, "mag": 0.01,
             "xor_err": 0.10, "cofail": 0.0},
        ]
    }

    empty = pick_pair({}, [], axis="coding")
    check("empty fold+rows is UNMEASURED, no invented pair",
          lambda: empty["kind"] == "UNMEASURED"
          and empty["a"] is None and empty["b"] is None
          and empty["orth"] is None and empty["mag"] is None
          and empty["axis"] == "coding")

    picked = pick_pair(fold, rows, axis="coding", budget_out=1.0)
    check("picks Luna Flex + GLM: max orth then min mag under GAC",
          lambda: picked["kind"] == "MEASURED"
          and {picked["a"], picked["b"]} == {luna, glm}
          and picked["orth"] == 0.80 and picked["mag"] == 0.40
          and picked["axis"] == "coding")

    sol_only = pick_pair(
        {"pairs": [
            {"model_a": sol, "model_b": glm, "axis": "coding",
             "orth_sketch": 0.99, "mag": 0.05,
             "xor_err": 1.0, "cofail": 0.0},
        ]},
        rows,
        axis="coding",
    )
    check("refuses openai/gpt-5.6-sol even when it is the best cell",
          lambda: sol_only["kind"] == "UNMEASURED"
          and sol_only["a"] is None
          and "sol" in sol_only["reason"].lower())

    xor_fold = {
        "pairs": [
            {"model_a": glm, "model_b": ds, "axis": "coding",
             "xor_err": 0.75, "cofail": 0.10, "mag": 2.0},
        ]
    }
    xor_pick = pick_pair(xor_fold, rows, axis="coding")
    check("orth_sketch fallback is xor_err − cofail (T sketch, not rewritten)",
          lambda: xor_pick["kind"] == "MEASURED"
          and abs(xor_pick["orth"] - 0.65) < 1e-9
          and xor_pick["mag"] == 2.0)

    missing = pick_pair(
        {"pairs": [
            {"model_a": glm, "model_b": ds, "axis": "coding",
             "orth_sketch": 0.5},
        ]},
        rows,
        axis="coding",
    )
    check("missing mag cell is UNMEASURED (skip pair, do not invent)",
          lambda: missing["kind"] == "UNMEASURED")

    unmeas_rate = pick_pair(
        {"pairs": [
            {"model_a": mystery, "model_b": glm, "axis": "coding",
             "orth_sketch": 0.9, "mag": 0.1,
             "xor_err": 0.9, "cofail": 0.0},
        ]},
        rows,
        axis="coding",
    )
    check("UNMEASURED completion rate is skip, not $0",
          lambda: unmeas_rate["kind"] == "UNMEASURED")

    no_flex = pick_pair(
        {"pairs": [
            {"model_a": luna_pro, "model_b": glm, "axis": "coding",
             "orth_sketch": 0.9, "mag": 0.1,
             "xor_err": 0.9, "cofail": 0.0},
        ]},
        rows,
        axis="coding",
    )
    check("non-flex Luna (luna-pro) is excluded even under budget",
          lambda: no_flex["kind"] == "UNMEASURED")

    flex_in = pick_pair(
        {"pairs": [
            {"model_a": luna, "model_b": ds, "axis": "coding",
             "orth_sketch": 0.55, "mag": 1.1,
             "xor_err": 0.7, "cofail": 0.15},
        ]},
        rows,
        axis="coding",
        budget_out=1.0,
    )
    check("Luna Flex IN when completion USD/1M ≤ budget",
          lambda: flex_in["kind"] == "MEASURED"
          and luna in {flex_in["a"], flex_in["b"]})

    td = Path(tempfile.mkdtemp(prefix="cosmos_womb_"))
    root = install(td / "live", tree_id="spike-womb")
    paths = CosmosPaths(root)
    before = store_dir(paths).exists()
    live = seat(paths, axis="coding")
    after = store_dir(paths).exists()
    check("seat GET-fold is UNMEASURED on empty store",
          lambda: live["kind"] == "UNMEASURED"
          and live["a"] is None)
    check("seat GET never mkdir",
          lambda: (not before) and (not after))

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print(("PASS" if ok else "FAIL"), label, err)
    print("womb selftest", "%d/%d" % (len(results) - len(failed), len(results)))
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("usage: py -3.14 cosmos\\cosmos_womb.py --selftest")
    raise SystemExit(2)
