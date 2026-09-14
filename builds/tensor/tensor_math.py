#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tensor_math — the pairwise disagreement tensor.

    T[pair, domain, judge, scaffold, provider]

P03 defined T[pair, domain]. Measured drops proved judge, scaffold and
provider move the numbers too, so they are variance axes, not metadata:
the generalization is canon. A slice names a value on each axis it
resolves; every axis it does not resolve is marginalized (ALL = "*").

Estimators on pair (i, j) over a slice, after n scored trials:

    freq         = disagree_n / n
    mean_err     = mean observed hole size 1-10 (critic / judge scored)
    mag          = freq x mean_err                  # pair hole-size |v|
    rescue(j|i)  = P(j right | i wrong)             # needs who_erred
    cofail       = P(both wrong)                    # needs who_erred
    xor_err      = P(exactly one wrong)             # needs who_erred
    style_fight  = P(disagree AND both right)       # NOT orthogonality
    orth_sketch  = (xor_err - cofail) x mean_err    # working sketch, open
    complement C = union coverage - intersection of gaps
    P_i[a]       = per-model porosity vector, a fold of the pair obs

Honesty law (fail-closed, never zero-fill):
  * kind = UNMEASURED until mag exists.
  * complement_kind = UNMEASURED until who_erred is scored.
  * A pair never observed is UNMEASURED and sorts last.
  * Orthogonality is NOT disagreement frequency - a style fight (both
    right, ballots differ) drives freq to 1.0 and discovers no error.
  * Orthogonality is NOT unsigned |v| - that is hole-size.

    python -m builds.tensor.tensor_math --selftest
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field

ALL = "*"
AXES = ("domain", "judge", "scaffold", "provider")
WHO_OK = frozenset({"a", "b", "both", "none", "unknown"})
ERR_LO = 1.0
ERR_HI = 10.0
ROTATING = frozenset({
    "openrouter/free", "openrouter/auto", "openrouter/free:free",
    "openrouter/pareto-code",
})
UNMEASURED = "UNMEASURED"
MEASURED = "MEASURED"


class TensorError(RuntimeError):
    """Refusal. kind is the machine-readable reason."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _num(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        raise TensorError("BAD_INPUT", f"not a number: {value!r}") from None


def _pin(model) -> str:
    m = str(model or "").strip()
    if not m:
        raise TensorError("BAD_INPUT", "model is required")
    if m.lower() in ROTATING:
        raise TensorError("REFUSED", f"rotator id {m!r} is not assignable")
    return m


def pair_key(model_a: str, model_b: str) -> tuple[str, str]:
    """Undirected pair key. Same-model pairs are refused."""
    a, b = _pin(model_a), _pin(model_b)
    if a == b:
        raise TensorError("REFUSED", "pair requires two distinct models")
    return (a, b) if a.lower() <= b.lower() else (b, a)


def _axis_value(value) -> str:
    v = str(value if value is not None else "").strip()
    return v[:120] if v else ALL


def axes_tuple(axes) -> tuple[str, ...]:
    """Validate a requested resolution. Unknown axis names are refused."""
    if axes is None:
        return AXES
    if isinstance(axes, str):
        axes = (axes,)
    out = []
    for a in axes:
        name = str(a or "").strip().lower()
        if name not in AXES:
            raise TensorError("BAD_INPUT", f"unknown axis {a!r}; axes={AXES}")
        if name not in out:
            out.append(name)
    return tuple(out)


def observation(model_a, model_b, *, disagree, domain="", judge="",
                scaffold="", provider="", err=None, who_erred="unknown",
                tokens_a=None, tokens_b=None, usd=None, trial_id="",
                err_source="", note="") -> dict:
    """One scored trial on one pair. Validates; never invents a score.

    err is the observed hole size 1-10, or None for UNMEASURED. who_erred
    is relative to model_a / model_b and stays "unknown" until a critic,
    judge or runtime bind scored it.
    """
    lo, hi = pair_key(model_a, model_b)
    who = str(who_erred or "unknown").strip().lower() or "unknown"
    if who not in WHO_OK:
        raise TensorError("BAD_INPUT", f"unknown who_erred {who_erred!r}")
    if disagree is None:
        raise TensorError("BAD_INPUT", "disagree must be stated, not guessed")
    e = _num(err)
    if e is not None and not (ERR_LO <= e <= ERR_HI):
        raise TensorError("BAD_INPUT", "err (hole size) must be 1-10 or None")
    a = _pin(model_a)
    # who_erred is stated against model_a/model_b; carry it on the lo/hi key.
    if who == "a":
        who_lo_hi = "lo" if a == lo else "hi"
    elif who == "b":
        who_lo_hi = "hi" if a == lo else "lo"
    else:
        who_lo_hi = who
    return {
        "_normalized": True,
        "pair_lo": lo,
        "pair_hi": hi,
        "domain": _axis_value(domain),
        "judge": _axis_value(judge),
        "scaffold": _axis_value(scaffold),
        "provider": _axis_value(provider),
        "disagree": bool(disagree),
        "err": e,
        "err_source": str(err_source or "")[:60],
        "who_erred": who,
        "who_lo_hi": who_lo_hi,
        "tokens_lo": _num(tokens_a if a == lo else tokens_b),
        "tokens_hi": _num(tokens_b if a == lo else tokens_a),
        "usd": _num(usd),
        "trial_id": str(trial_id or "")[:120],
        "note": str(note or "")[:240],
    }


def normalize_obs(rec) -> dict:
    """Accept an observation dict from anywhere; validate it exactly once."""
    if not isinstance(rec, dict):
        raise TensorError("BAD_INPUT", f"observation must be a dict: {rec!r}")
    if rec.get("_normalized"):
        return rec
    a = rec.get("model_a") or rec.get("pair_lo")
    b = rec.get("model_b") or rec.get("pair_hi")
    return observation(
        a, b,
        disagree=rec.get("disagree"),
        domain=rec.get("domain"), judge=rec.get("judge"),
        scaffold=rec.get("scaffold"), provider=rec.get("provider"),
        err=rec.get("err", rec.get("error_mag")),
        who_erred=rec.get("who_erred", "unknown"),
        tokens_a=rec.get("tokens_a"), tokens_b=rec.get("tokens_b"),
        usd=rec.get("usd"), trial_id=rec.get("trial_id") or rec.get("order_id"),
        err_source=rec.get("err_source"), note=rec.get("note"),
    )


@dataclass
class Counts:
    """Sufficient statistics for one pair x slice. Counts only, no scores."""

    n: int = 0
    disagree_n: int = 0
    err_sum: float = 0.0
    err_n: int = 0
    scored_n: int = 0
    none_n: int = 0
    both_n: int = 0
    only_lo_n: int = 0          # exactly lo wrong -> hi rescued
    only_hi_n: int = 0          # exactly hi wrong -> lo rescued
    style_n: int = 0            # disagree AND both right
    usd_sum: float = 0.0
    usd_n: int = 0
    tokens_sum: float = 0.0
    tokens_n: int = 0
    err_sources: set = field(default_factory=set)

    def add(self, o: dict) -> None:
        self.n += 1
        if o["disagree"]:
            self.disagree_n += 1
        if o["err"] is not None:
            self.err_sum += o["err"]
            self.err_n += 1
            if o.get("err_source"):
                self.err_sources.add(o["err_source"])
        if o["usd"] is not None:
            self.usd_sum += o["usd"]
            self.usd_n += 1
        for tok in (o["tokens_lo"], o["tokens_hi"]):
            if tok is not None:
                self.tokens_sum += tok
                self.tokens_n += 1
        who = o["who_lo_hi"]
        if who == "unknown":
            return
        self.scored_n += 1
        if who == "none":
            self.none_n += 1
            if o["disagree"]:
                self.style_n += 1
        elif who == "both":
            self.both_n += 1
        elif who == "lo":
            self.only_lo_n += 1
        elif who == "hi":
            self.only_hi_n += 1


def _r(v, nd=6):
    return None if v is None else round(v, nd)


# ---------------------------------------------------------------- estimators
def freq(disagree_n: int, n: int):
    """Disagreement frequency = disagree_n / n. None (UNMEASURED) when n=0."""
    if not n:
        return None
    return _r(disagree_n / n)


def mean_err(err_sum: float, err_n: int):
    """Mean observed hole size 1-10. None until a hole was actually scored."""
    if not err_n:
        return None
    return _r(err_sum / err_n, 4)


def mag(f, e):
    """Pair hole-size |v| = freq x mean_err. UNMEASURED if either is."""
    if f is None or e is None:
        return None
    return _r(f * e)


def rescue(c: Counts, *, of: str):
    """P(of right | other wrong). Directed: rescue(j|i) != rescue(i|j)."""
    side = str(of or "").strip().lower()
    if side not in ("lo", "hi"):
        raise TensorError("BAD_INPUT", "rescue(of=) must be 'lo' or 'hi'")
    other_wrong = (c.only_hi_n if side == "lo" else c.only_lo_n) + c.both_n
    if not other_wrong:
        return None
    rescued = c.only_hi_n if side == "lo" else c.only_lo_n
    return _r(rescued / other_wrong)


def cofail(c: Counts):
    """P(both wrong). Needs who_erred."""
    if not c.scored_n:
        return None
    return _r(c.both_n / c.scored_n)


def xor_err(c: Counts):
    """P(exactly one wrong) - productive disagreement. Needs who_erred."""
    if not c.scored_n:
        return None
    return _r((c.only_lo_n + c.only_hi_n) / c.scored_n)


def style_fight(c: Counts):
    """P(disagree AND both right). Covers no hole. NOT orthogonality."""
    if not c.scored_n:
        return None
    return _r(c.style_n / c.scored_n)


def orth_sketch(x, cof, e):
    """(xor_err - cofail) x mean_err. Working sketch, math still open.

    When xor_err == cofail the product is 0 for ANY non-negative weight, so
    the sketch is 0.0 even while mean_err is UNMEASURED - that is algebra,
    not a zero-fill. Otherwise an unmeasured weight leaves it UNMEASURED.
    """
    if x is None or cof is None:
        return None
    signed = x - cof
    if signed == 0.0:
        return 0.0
    if e is None:
        return None
    return _r(signed * e)


def complement(c: Counts):
    """C = union coverage - intersection of gaps.

    union coverage    = P(at least one of the pair is right) = 1 - cofail
    intersection gaps = P(both wrong)                        = cofail
    """
    if not c.scored_n:
        return None
    union_cov = (c.scored_n - c.both_n) / c.scored_n
    gap_inter = c.both_n / c.scored_n
    return _r(union_cov - gap_inter)


# --------------------------------------------------------------------- folds
def _cell(lo: str, hi: str, slot: dict, c: Counts) -> dict:
    f = freq(c.disagree_n, c.n)
    e = mean_err(c.err_sum, c.err_n)
    m = mag(f, e)
    cof = cofail(c)
    x = xor_err(c)
    return {
        "pair": [lo, hi],
        "pair_lo": lo,
        "pair_hi": hi,
        "axes": dict(slot),
        "domain": slot["domain"],
        "judge": slot["judge"],
        "scaffold": slot["scaffold"],
        "provider": slot["provider"],
        "n": c.n,
        "disagree_n": c.disagree_n,
        "freq": f,
        "mean_err": e,
        "mag": m,
        "scored_n": c.scored_n,
        "rescue_hi_given_lo": rescue(c, of="hi"),
        "rescue_lo_given_hi": rescue(c, of="lo"),
        "cofail": cof,
        "xor_err": x,
        "style_fight": style_fight(c),
        "orth_sketch": orth_sketch(x, cof, e),
        "complement": complement(c),
        "mean_usd": None if not c.usd_n else _r(c.usd_sum / c.usd_n),
        "mean_tokens": None if not c.tokens_n else _r(c.tokens_sum / c.tokens_n, 2),
        "err_sources": sorted(c.err_sources),
        "freq_kind": UNMEASURED if f is None else MEASURED,
        "hole_kind": UNMEASURED if e is None else MEASURED,
        "kind": UNMEASURED if m is None else MEASURED,
        "complement_kind": UNMEASURED if not c.scored_n else MEASURED,
    }


def fold(observations, *, axes=AXES) -> dict:
    """Fold observations into cells keyed (pair_lo, pair_hi, *axis values).

    Axes not in `axes` are marginalized to ALL. Never zero-fills: a cell
    only exists where an observation exists.
    """
    want = axes_tuple(axes)
    acc: dict[tuple, Counts] = {}
    slots: dict[tuple, dict] = {}
    for raw in observations or []:
        o = normalize_obs(raw)
        slot = {a: (o[a] if a in want else ALL) for a in AXES}
        key = (o["pair_lo"], o["pair_hi"]) + tuple(slot[a] for a in AXES)
        if key not in acc:
            acc[key] = Counts()
            slots[key] = slot
        acc[key].add(o)
    return {
        key: _cell(key[0], key[1], slots[key], c) for key, c in acc.items()
    }


def unmeasured_cell(model_a: str, model_b: str, *, domain=ALL, judge=ALL,
                    scaffold=ALL, provider=ALL) -> dict:
    """The honest cell for a pair nobody has observed yet."""
    lo, hi = pair_key(model_a, model_b)
    slot = {"domain": _axis_value(domain) if domain != ALL else ALL,
            "judge": _axis_value(judge) if judge != ALL else ALL,
            "scaffold": _axis_value(scaffold) if scaffold != ALL else ALL,
            "provider": _axis_value(provider) if provider != ALL else ALL}
    return _cell(lo, hi, slot, Counts())


def pair_matrix(observations, agents, *, axes=("domain",), domains=None) -> list[dict]:
    """Every unordered pair of named agents x requested domains.

    Observed cells are copied; never-seen pairs stay UNMEASURED.
    """
    pins = agent_pins(agents)
    cells = fold(observations, axes=axes)
    seen_domains = sorted({c["domain"] for c in cells.values()}) or [ALL]
    want = [str(d) for d in (domains or seen_domains)]
    rows = []
    for i in range(len(pins)):
        for j in range(i + 1, len(pins)):
            lo, hi = pair_key(pins[i], pins[j])
            for d in want:
                hit = [c for c in cells.values()
                       if c["pair_lo"] == lo and c["pair_hi"] == hi
                       and c["domain"] == d]
                rows.append(dict(hit[0]) if hit
                            else unmeasured_cell(lo, hi, domain=d))
    return rows


def agent_pins(agents) -> list[str]:
    """De-duplicated named pins. Rotators dropped, order preserved."""
    seen, out = set(), []
    for raw in agents or []:
        m = str(raw or "").strip()
        if not m or m.lower() in ROTATING:
            continue
        if m.lower() in seen:
            continue
        seen.add(m.lower())
        out.append(m)
    return out


def porosity(observations, *, axis="domain") -> dict:
    """Per-model porosity vector P_i[a] - hole size AND distribution.

    A fold of the pair observations: for each model, on each value of the
    named axis, how often it was the erring side and how big those holes
    were. UNMEASURED until who_erred is scored.
    """
    name = axes_tuple(axis)[0]
    acc: dict[tuple[str, str], dict] = {}
    for raw in observations or []:
        o = normalize_obs(raw)
        who = o["who_lo_hi"]
        if who == "unknown":
            continue
        a_val = o[name]
        for side, model in (("lo", o["pair_lo"]), ("hi", o["pair_hi"])):
            slot = acc.setdefault((model, a_val), {
                "n_scored": 0, "wrong_n": 0, "err_sum": 0.0, "err_n": 0})
            slot["n_scored"] += 1
            wrong = who == "both" or who == side
            if wrong:
                slot["wrong_n"] += 1
                if o["err"] is not None:
                    slot["err_sum"] += o["err"]
                    slot["err_n"] += 1
    out: dict[str, dict] = {}
    for (model, a_val), s in acc.items():
        rate = None if not s["n_scored"] else _r(s["wrong_n"] / s["n_scored"])
        size = mean_err(s["err_sum"], s["err_n"])
        if rate == 0.0:
            mass = 0.0          # never wrong here: 0 x any weight = 0
        elif rate is None or size is None:
            mass = None
        else:
            mass = _r(rate * size)
        out.setdefault(model, {})[a_val] = {
            "axis": name,
            "n_scored": s["n_scored"],
            "wrong_n": s["wrong_n"],
            "wrong_rate": rate,
            "mean_err": size,
            "mass": mass,
            "kind": UNMEASURED if mass is None else MEASURED,
            "rate_kind": UNMEASURED if rate is None else MEASURED,
        }
    return out


# ------------------------------------------------------------------- seating
def _cells_for(cells: dict, a: str, b: str) -> list[dict]:
    lo, hi = pair_key(a, b)
    return [c for c in cells.values()
            if c["pair_lo"] == lo and c["pair_hi"] == hi]


def complementarity(cell: dict, candidate: str, seated: str) -> dict:
    """One term of the seating score: signed complement, else |v|.

    complement path (who_erred scored): (rescue(candidate|seated) - cofail)
    weighted by mean_err when the hole size is measured. mag path: unsigned
    |v| only. Neither measured -> UNMEASURED term, skipped, never zero.
    """
    if cell["complement_kind"] == MEASURED:
        if candidate == cell["pair_lo"]:
            rsc = cell["rescue_lo_given_hi"]
        elif candidate == cell["pair_hi"]:
            rsc = cell["rescue_hi_given_lo"]
        else:
            raise TensorError("BAD_INPUT",
                              f"{candidate!r} is not in cell pair {cell['pair']}")
        cof = cell["cofail"]
        if rsc is not None or cof is not None:
            signed = (0.0 if rsc is None else rsc) - (0.0 if cof is None else cof)
            w = cell["mean_err"]
            return {"value": _r(signed * (1.0 if w is None else w)),
                    "via": "complement",
                    "weighted": w is not None,
                    "kind": MEASURED}
    if cell["mag"] is not None:
        return {"value": cell["mag"], "via": "mag", "weighted": True,
                "kind": MEASURED}
    return {"value": None, "via": "none", "weighted": False, "kind": UNMEASURED}


def recommend_team(observations, candidates, k=3, *, incumbent="", scores=None,
                   costs=None, axes=("domain",), domains=None) -> dict:
    """Greedy seating: incumbent first, then complementarity x score per token.

    Goal: maximize error-discovery coverage per token. A candidate whose
    pairs against the seated set were never observed is UNMEASURED and
    sorts last - it is never zero-filled into the middle of the field.
    """
    pins = agent_pins(candidates)
    if k is None or int(k) < 1:
        raise TensorError("BAD_INPUT", "k must be >= 1")
    k = int(k)
    scores = scores if isinstance(scores, dict) else {}
    costs = costs if isinstance(costs, dict) else {}
    cells = fold(observations, axes=axes)
    if domains:
        keep = {str(d) for d in domains}
        cells = {kk: c for kk, c in cells.items() if c["domain"] in keep}

    inc = str(incumbent or "").strip()
    seated: list[str] = []
    steps: list[dict] = []
    if inc:
        seated.append(inc)
        steps.append({"model": inc, "value": None, "n_terms": 0,
                      "kind": "INCUMBENT", "via": "seat", "score": _num(
                          scores.get(inc)), "cost": _num(costs.get(inc))})
    rest = [p for p in pins if p not in seated]

    while len(seated) < k and rest:
        ranked = []
        for c in rest:
            total, n_terms, vias, weighted_all = 0.0, 0, set(), True
            for s in seated:
                if s == c:
                    continue
                for cell in _cells_for(cells, c, s):
                    term = complementarity(cell, c, s)
                    if term["kind"] != MEASURED:
                        continue
                    total += term["value"]
                    n_terms += 1
                    vias.add(term["via"])
                    weighted_all = weighted_all and term["weighted"]
            sc = _num(scores.get(c))
            cost = _num(costs.get(c))
            if n_terms:
                comp = total / n_terms
                value = comp * (1.0 if sc is None else sc / 10.0)
                if cost is not None and cost > 0:
                    value = value / cost
                kind, via = MEASURED, "+".join(sorted(vias))
            else:
                comp, value, kind, via = None, None, UNMEASURED, "none"
            ranked.append({
                "model": c,
                "value": _r(value),
                "complementarity": _r(comp),
                "n_terms": n_terms,
                "kind": kind,
                "via": via,
                "weighted": weighted_all if n_terms else False,
                "score": sc,
                "score_kind": UNMEASURED if sc is None else MEASURED,
                "cost": cost,
                "per": "usd" if (cost is not None and cost > 0) else "flat",
            })
        ranked.sort(key=lambda r: (r["kind"] != MEASURED,
                                   -(r["value"] if r["value"] is not None else 0.0),
                                   r["model"]))
        if not seated:
            # No incumbent named: open with the best measured score, else
            # the first pin. Never with an invented complementarity.
            ranked.sort(key=lambda r: (r["score"] is None, -(r["score"] or 0.0),
                                       r["model"]))
        pick = ranked[0]
        seated.append(pick["model"])
        steps.append(pick)
        rest = [p for p in rest if p != pick["model"]]

    n_meas = sum(1 for s in steps if s["kind"] == MEASURED)
    return {
        "goal": ("maximize error-discovery coverage per token; "
                 "UNMEASURED pairs sort last; does not invent scores"),
        "k": k,
        "team": seated,
        "steps": steps,
        "bench": [p for p in rest],
        "n_measured_steps": n_meas,
        "kind": MEASURED if n_meas else UNMEASURED,
        "axes": list(axes_tuple(axes)),
    }


def snapshot(observations, *, axes=("domain",), agents=None) -> dict:
    """Read-model fold: cells, directed tensors[agent][vs][axis], porosity."""
    obs = [normalize_obs(o) for o in (observations or [])]
    cells = fold(obs, axes=axes)
    tensors: dict[str, dict] = {}
    for c in cells.values():
        lo, hi, ax = c["pair_lo"], c["pair_hi"], c["domain"]
        for agent, vs, rsc in ((lo, hi, c["rescue_lo_given_hi"]),
                               (hi, lo, c["rescue_hi_given_lo"])):
            tensors.setdefault(agent, {}).setdefault(vs, {})[ax] = {
                "n": c["n"], "freq": c["freq"], "mean_err": c["mean_err"],
                "mag": c["mag"], "xor_err": c["xor_err"],
                "cofail": c["cofail"], "rescue": rsc,
                "orth_sketch": c["orth_sketch"],
                "complement": c["complement"],
                "style_fight": c["style_fight"],
                "kind": c["kind"], "complement_kind": c["complement_kind"],
            }
    pairs = [cells[key] for key in sorted(cells)]
    return {
        "kind": MEASURED if any(p["mag"] is not None for p in pairs)
        else ("FREQ_ONLY" if pairs else UNMEASURED),
        "complement_kind": (MEASURED if any(
            p["complement_kind"] == MEASURED for p in pairs) else UNMEASURED),
        "n_obs": len(obs),
        "n_pairs": len(pairs),
        "pairs": pairs,
        "tensors": tensors,
        "tensors_shape": "tensors[agent][vs][axis]",
        "axes_all": list(AXES),
        "axes": list(axes_tuple(axes)),
        "porosity": porosity(obs, axis=axes_tuple(axes)[0]),
        "agents": agent_pins(agents),
    }


# ------------------------------------------------------------------ selftest
def _selftest(quiet: bool = False) -> int:
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    A, B, C = "seat/ling", "seat/luna", "seat/glm"

    # 1. empty in, empty out. No invented cell.
    snap0 = snapshot([])
    check("empty observations -> UNMEASURED, no zero-filled cell",
          lambda: snap0["kind"] == UNMEASURED and snap0["n_obs"] == 0
          and snap0["n_pairs"] == 0 and snap0["tensors"] == {}
          and snap0["complement_kind"] == UNMEASURED)

    # 2. refusals.
    def _refuses(fn, kind):
        try:
            fn()
        except TensorError as e:
            return e.kind == kind
        return False

    check("same-model pair REFUSED",
          lambda: _refuses(lambda: pair_key(A, A), "REFUSED"))
    check("rotator id REFUSED",
          lambda: _refuses(lambda: pair_key("openrouter/auto", A), "REFUSED"))
    check("err outside 1-10 refused (no clamping into a fake score)",
          lambda: _refuses(
              lambda: observation(A, B, disagree=True, err=11), "BAD_INPUT"))
    check("unknown axis name refused",
          lambda: _refuses(lambda: axes_tuple(("vendor",)), "BAD_INPUT"))

    # 3. The estimators themselves refuse to read empty as zero.
    empty = Counts()
    check("no observation reads UNMEASURED, never 0.0",
          lambda: freq(0, 0) is None and mean_err(0.0, 0) is None
          and mag(None, 5.0) is None and mag(0.5, None) is None
          and cofail(empty) is None and xor_err(empty) is None
          and style_fight(empty) is None and complement(empty) is None
          and rescue(empty, of="lo") is None
          and orth_sketch(None, None, 5.0) is None)

    # 4. freq without a scored hole leaves mag UNMEASURED.
    o1 = [observation(A, B, disagree=True, domain="core")]
    c1 = fold(o1, axes=("domain",))
    cell1 = list(c1.values())[0]
    check("freq MEASURED while mag stays UNMEASURED without a hole score",
          lambda: cell1["freq"] == 1.0 and cell1["mean_err"] is None
          and cell1["mag"] is None and cell1["kind"] == UNMEASURED
          and cell1["complement_kind"] == UNMEASURED)

    # 5. mag = freq x mean_err, exactly.
    o2 = [observation(A, B, disagree=True, domain="core", err=8),
          observation(A, B, disagree=False, domain="core", err=4)]
    cell2 = list(fold(o2, axes=("domain",)).values())[0]
    check("mag = freq x mean_err (0.5 x 6.0 = 3.0)",
          lambda: cell2["freq"] == 0.5 and cell2["mean_err"] == 6.0
          and cell2["mag"] == 3.0 and cell2["kind"] == MEASURED)

    # 6. NEGATIVE CONTROL - style fight. Every trial disagrees, nobody is
    # wrong. freq is 1.0; orthogonality must NOT follow it.
    style = [observation(A, B, disagree=True, domain="core", who_erred="none")
             for _ in range(4)]
    cellS = list(fold(style, axes=("domain",)).values())[0]
    check("NEGATIVE CONTROL: style fight -> freq 1.0 but orth_sketch 0.0 "
          "(orthogonality is not disagreement frequency)",
          lambda: cellS["freq"] == 1.0 and cellS["style_fight"] == 1.0
          and cellS["xor_err"] == 0.0 and cellS["cofail"] == 0.0
          and cellS["orth_sketch"] == 0.0 and cellS["mag"] is None
          and cellS["complement"] == 1.0)

    # 7. NEGATIVE CONTROL - |v| is hole-size, not orthogonality. Same freq
    # and same mean_err, opposite complement.
    good = [observation(A, B, disagree=True, domain="core", err=8,
                        who_erred="a") for _ in range(4)]
    bad = [observation(A, B, disagree=True, domain="core", err=8,
                       who_erred="both") for _ in range(4)]
    cg = list(fold(good, axes=("domain",)).values())[0]
    cb = list(fold(bad, axes=("domain",)).values())[0]
    check("NEGATIVE CONTROL: equal |v|, opposite orthogonality "
          "(xor pair positive, co-fail pair negative)",
          lambda: cg["mag"] == cb["mag"] == 8.0
          and cg["orth_sketch"] == 8.0 and cb["orth_sketch"] == -8.0
          and cg["complement"] == 1.0 and cb["complement"] == -1.0)

    # 8. rescue is directed, and it is a probability on its own denominator.
    check("rescue(hi|lo) is not rescue(lo|hi)",
          lambda: cg["rescue_hi_given_lo"] == 1.0
          and cg["rescue_lo_given_hi"] is None)
    asym = ([observation(A, B, disagree=True, domain="core", err=7,
                         who_erred="a") for _ in range(3)]
            + [observation(A, B, disagree=True, domain="core", err=7,
                           who_erred="b")]
            + [observation(A, B, disagree=True, domain="core", err=7,
                           who_erred="both")])
    ca = list(fold(asym, axes=("domain",)).values())[0]
    check("rescue conditions on the OTHER side being wrong "
          "(3 lo-only, 1 hi-only, 1 both -> 0.75 and 0.5, never >1)",
          lambda: ca["rescue_hi_given_lo"] == 0.75
          and ca["rescue_lo_given_hi"] == 0.5
          and 0.0 <= ca["rescue_hi_given_lo"] <= 1.0
          and 0.0 <= ca["rescue_lo_given_hi"] <= 1.0)

    # 9. axes: judge / scaffold / provider are variance axes, not metadata.
    split = [
        observation(A, B, disagree=True, domain="core", judge="kelly",
                    scaffold="L1", provider="novita", err=9, who_erred="a"),
        observation(A, B, disagree=False, domain="core", judge="grok",
                    scaffold="L2", provider="groq", err=2, who_erred="none"),
    ]
    full = fold(split, axes=AXES)
    marg = fold(split, axes=("domain",))
    check("full resolution splits on judge/scaffold/provider; domain "
          "marginal folds them together",
          lambda: len(full) == 2 and len(marg) == 1
          and list(marg.values())[0]["n"] == 2
          and list(marg.values())[0]["judge"] == ALL
          and {c["judge"] for c in full.values()} == {"kelly", "grok"})

    # 10. porosity vector is UNMEASURED until who_erred exists.
    check("porosity UNMEASURED without who_erred, MEASURED with it",
          lambda: porosity(o1) == {}
          and porosity(good)[A]["core"]["kind"] == MEASURED
          and porosity(good)[A]["core"]["mass"] == 8.0
          and porosity(good)[B]["core"]["wrong_rate"] == 0.0
          and porosity(good)[B]["core"]["mass"] == 0.0)

    # 11. seating: incumbent first, measured beats unseen, unseen sorts last.
    team = recommend_team(good, [B, C], k=3, incumbent=A,
                          scores={B: 8.0, C: 9.9})
    check("recommend_team seats incumbent first",
          lambda: team["team"][0] == A and team["steps"][0]["kind"] == "INCUMBENT")
    check("NEGATIVE CONTROL: unseen pair stays UNMEASURED and sorts last",
          lambda: team["team"][1] == B
          and team["steps"][1]["kind"] == MEASURED
          and team["steps"][2]["model"] == C
          and team["steps"][2]["kind"] == UNMEASURED
          and team["steps"][2]["value"] is None)

    # 12. co-failure must not be preferred over rescue.
    mixed = good + [observation(A, C, disagree=True, domain="core", err=8,
                                who_erred="both") for _ in range(4)]
    team2 = recommend_team(mixed, [B, C], k=3, incumbent=A)
    check("co-failing candidate ranks below the rescuing one",
          lambda: team2["team"][1] == B and team2["team"][2] == C
          and team2["steps"][1]["value"] > team2["steps"][2]["value"])

    # 13. cost divides: coverage per token, not raw coverage.
    cheap = recommend_team(mixed, [B], k=2, incumbent=A, costs={B: 4.0})
    flat = recommend_team(mixed, [B], k=2, incumbent=A)
    check("cost known -> value is coverage per token",
          lambda: cheap["steps"][1]["per"] == "usd"
          and flat["steps"][1]["per"] == "flat"
          and cheap["steps"][1]["value"] < flat["steps"][1]["value"])

    # 14. pair_matrix enumerates and refuses to invent.
    mat = pair_matrix(good, [A, B, C], domains=["core"])
    check("pair_matrix: observed pair MEASURED, unseen pairs UNMEASURED",
          lambda: len(mat) == 3
          and sum(1 for m in mat if m["kind"] == MEASURED) == 1
          and all(m["mag"] is None for m in mat if m["kind"] == UNMEASURED))

    # 15. directed tensor shape survives the fold.
    snap = snapshot(good, agents=[A, B])
    check("tensors[agent][vs][axis] holds the parameter set",
          lambda: snap["tensors_shape"] == "tensors[agent][vs][axis]"
          and snap["tensors"][A][B]["core"]["mag"] == 8.0
          and snap["tensors"][B][A]["core"]["rescue"] == 1.0
          and snap["tensors"][A][B]["core"]["rescue"] is None)

    failed = [(l, e) for l, ok, e in results if not ok]
    if not quiet:
        for label, ok, err in results:
            print(("PASS" if ok else "FAIL"), label, err)
        print("tensor_math selftest %d/%d"
              % (len(results) - len(failed), len(results)))
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print(__doc__)
    raise SystemExit(2)
