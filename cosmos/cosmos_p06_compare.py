#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P06 — compare box$ vs token$ seating only after real obs.jsonl rows.

Seating/COMPARE does not run pair folds, coverage(N), or a bake-off until
`live/state/porosity/obs.jsonl` has at least one row. `n_obs=0` reuses
`empty_snapshot` and stays UNMEASURED. Same-family double-seat refuses
(Sol = Luna). Rotators refuse. Does not write fake obs rows.

    py -3.14 cosmos\\cosmos_p06_compare.py --selftest
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_model_rater import family_of  # noqa: E402
from cosmos_porosity import (  # noqa: E402
    PorosityError,
    ROTATING,
    _agent_pins,
    coverage,
    empty_snapshot,
    load_obs,
)

SCHEMA = "cosmos-p06-compare/1"


def seating_family(model_id: str) -> str:
    """Family slug for seating. OpenAI gpt-5.6 Luna and Sol share one seat."""
    mid = str(model_id or "").strip().lower()
    if not mid:
        return ""
    name = mid.split("/", 1)[-1]
    if name.startswith("gpt-5.6-luna") or name.startswith("gpt-5.6-sol"):
        return "openai/gpt-5.6-luna-sol"
    return family_of(model_id)


def assert_distinct_seating_families(agents) -> list[str]:
    """Named pins only. REFUSED for rotator or same-family double-seat."""
    for raw in agents or []:
        m = str(raw or "").strip()
        if m and m.lower() in ROTATING:
            raise PorosityError("REFUSED", f"rotator id {m!r} is not assignable")
    pins = _agent_pins(agents)
    seen_fam: dict[str, str] = {}
    for pin in pins:
        fam = seating_family(pin)
        if not fam:
            continue
        prev = seen_fam.get(fam)
        if prev is not None and prev != pin:
            raise PorosityError(
                "REFUSED",
                f"same-family double-seat {prev!r} and {pin!r} "
                f"(family {fam!r})",
            )
        seen_fam[fam] = pin
    return pins


def _unmeasured_compare(*, agents: list[str] | None = None) -> dict:
    base = empty_snapshot()
    out = dict(base)
    out["schema"] = SCHEMA
    out["compare_kind"] = "UNMEASURED"
    out["box"] = None
    out["token"] = None
    out["pair"] = None
    out["coverage_n"] = None
    out["pairs"] = []
    out["n_pairs"] = 0
    out["n_obs"] = 0
    out["kind"] = "UNMEASURED"
    if agents:
        out["agents"] = list(agents)
    return out


def compare_box_token(
    paths,
    *,
    box_agents=None,
    token_agents=None,
    profile: str = "forge",
    token_incumbent: str = "",
    box_cost_usd: float | None = None,
    token_costs=None,
) -> dict:
    """COMPARE box$ (fixed/on-box) vs token$ seating after real observations."""
    raw = list(box_agents or []) + list(token_agents or [])
    assert_distinct_seating_families(raw)
    box_pins = _agent_pins(box_agents or [])
    token_pins = _agent_pins(token_agents or [])
    combined = box_pins + [t for t in token_pins if t not in box_pins]

    rows = load_obs(paths)
    n_obs = len(rows)
    if n_obs == 0:
        return _unmeasured_compare(agents=combined)

    box_costs = {m: 0.0 for m in box_pins}
    if box_cost_usd is not None and box_pins:
        per = float(box_cost_usd) / len(box_pins)
        box_costs = {m: per for m in box_pins}

    token_costs = token_costs if isinstance(token_costs, dict) else {}
    box_pack = (
        coverage(
            paths,
            box_pins,
            profile=profile,
            costs=box_costs,
            incumbent=box_pins[0] if box_pins else "",
        )
        if box_pins
        else None
    )
    token_pack = (
        coverage(
            paths,
            token_pins,
            profile=profile,
            costs=token_costs,
            incumbent=str(token_incumbent or "").strip()
            or (token_pins[0] if token_pins else ""),
        )
        if token_pins
        else None
    )

    last = rows[-1]
    pair = {
        "model_a": last.get("model_a") or "",
        "model_b": last.get("model_b") or "",
        "axis": last.get("axis") or "",
    }
    n_meas = sum(
        x
        for x in (
            (box_pack or {}).get("n_measured") or 0,
            (token_pack or {}).get("n_measured") or 0,
        )
    )
    base = empty_snapshot()
    out = dict(base)
    out.update({
        "schema": SCHEMA,
        "kind": "MEASURED" if n_meas else "UNMEASURED",
        "compare_kind": "MEASURED" if n_meas else "UNMEASURED",
        "n_obs": n_obs,
        "n_pairs": (box_pack or {}).get("n_pairs", 0)
        + (token_pack or {}).get("n_pairs", 0),
        "agents": combined,
        "box": {
            "rail": "box$",
            "order": (box_pack or {}).get("order") or [],
            "n_measured": (box_pack or {}).get("n_measured") or 0,
            "pack": box_pack,
        },
        "token": {
            "rail": "token$",
            "order": (token_pack or {}).get("order") or [],
            "n_measured": (token_pack or {}).get("n_measured") or 0,
            "pack": token_pack,
        },
        "pair": pair,
        "coverage_n": {
            "box": len((box_pack or {}).get("order") or []),
            "token": len((token_pack or {}).get("order") or []),
        },
        "last_obs": {
            "at": last.get("at") or "",
            "model_a": pair["model_a"],
            "model_b": pair["model_b"],
        },
    })
    if box_pack:
        out["pairs"] = box_pack.get("pairs") or []
    elif token_pack:
        out["pairs"] = token_pack.get("pairs") or []
    return out


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_p06_"))
    root = install(td / "live", tree_id="spike-p06")
    paths = CosmosPaths(root)

    luna = "openai/gpt-5.6-luna"
    sol = "openai/gpt-5.6-sol"
    glm = "z-ai/glm-5.3-flash"
    ds = "deepseek/deepseek-v4-flash-0731"

    cmp0 = compare_box_token(
        paths, box_agents=[glm, ds], token_agents=[luna])
    check(
        "n_obs=0 compare is UNMEASURED with no pair and no coverage_n",
        lambda: cmp0["compare_kind"] == "UNMEASURED"
        and cmp0["kind"] == "UNMEASURED"
        and cmp0["n_obs"] == 0
        and cmp0["pair"] is None
        and cmp0["coverage_n"] is None
        and cmp0["pairs"] == []
        and cmp0["n_pairs"] == 0,
    )

    refused_fam = False
    try:
        compare_box_token(paths, box_agents=[luna, sol], token_agents=[])
    except PorosityError as e:
        refused_fam = e.kind == "REFUSED"
    check("same-family luna+sol double-seat REFUSED", lambda: refused_fam)

    refused_rot = False
    try:
        compare_box_token(
            paths,
            box_agents=["openrouter/free"],
            token_agents=[glm],
        )
    except PorosityError as e:
        refused_rot = e.kind == "REFUSED"
    check("rotator in seating REFUSED", lambda: refused_rot)

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print(("PASS" if ok else "FAIL"), label, err)
    print("p06 compare selftest", "%d/%d" % (len(results) - len(failed), len(results)))
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("usage: py -3.14 cosmos\\cosmos_p06_compare.py --selftest")
    raise SystemExit(2)
