#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""grading — the grading / judging / model-rating system.

Charter-driven, two-tier bar. The bar is CONFIG (`Charter.q_setpoint`), not
a magic number sprinkled through the code:

    real fix        score >= q_setpoint (8.0)          KEEP
    honest no-op    literal UNCHANGED token -> 7.5     KEEP
    re-emission     no fix, output re-sent   -> 5.0    DROP
    hallucination   DROP regardless of the score       DROP

Anchors - a judge must USE the range, never cluster:

    9-10  exemplary (rare)        5.0  no fix
    8.0   solid                   3.0  charter violations
    7.0   minor nit               1.0  garbage

Dual-judge: a primary plus a second judge from a DIFFERENT model family.
Their disagreement rate is not noise to be hidden - the judge is a tensor
axis, so the rate is published data. Every cell records judge, score, keep,
why and judge_agreement.

Model rater: per-seat format%, usable%, keep%, dollars-per-keep and
Q-per-dollar folded from the cells, blended with a bench value when one is
measured, and turned into a seating recommendation by
tensor_math.recommend_team(k).

Every score writes a tensor cell. Provenance (run_id, order_id, fn, domain,
pair, judge, scaffold, provider) is mandatory: a score with no provenance is
refused, not stored.

No network. The judge model is injected as a scorer callable.

    python -m builds.tensor.grading --selftest
"""
from __future__ import annotations

import statistics
import sys
from dataclasses import dataclass, replace
from pathlib import Path

try:  # package run
    from . import dbase, tensor_math as tm
except ImportError:  # direct run
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import dbase  # type: ignore
    import tensor_math as tm  # type: ignore

UNMEASURED = tm.UNMEASURED
MEASURED = tm.MEASURED
CELL_SCHEMA = dbase.CELL_SCHEMA
PROVENANCE = ("run_id", "order_id", "fn", "domain", "pair", "judge",
              "scaffold", "provider")
OUTCOMES = ("fix", "no_op", "reemit", "hallucination", "malformed")
UNCHANGED = "UNCHANGED"
GATE_BY_OUTCOME = {
    "fix": "PATCHED",
    "no_op": UNCHANGED,
    "reemit": "REEMIT",
    "hallucination": "HALLUCINATION",
    "malformed": "MALFORMED",
}
UNUSABLE_GATES = frozenset({"HALLUCINATION", "MALFORMED", "EMPTY", ""})
MALFORMED_GATES = frozenset({"MALFORMED", "EMPTY", ""})
ANCHORS = (
    (9.0, 10.0, "exemplary (rare)"),
    (8.0, 8.999, "solid"),
    (7.0, 7.999, "minor nit"),
    (5.0, 6.999, "no fix"),
    (3.0, 4.999, "charter violations"),
    (1.0, 2.999, "garbage"),
)


class GradingError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


@dataclass(frozen=True)
class Charter:
    """The judging contract. Versioned, so a re-score is comparable."""

    rubric_version: str = "orc-charter-v2-anchored-20260913"
    q_setpoint: float = 8.0          # the KEEP bar for a real fix
    no_op_score: float = 7.5         # honest no-op, literal UNCHANGED token
    no_fix_score: float = 5.0        # re-emission without a fix
    hallucination_score: float = 1.0
    unchanged_token: str = UNCHANGED
    anchors: tuple = ANCHORS
    min_range_n: int = 5             # below this, clustering is not a claim
    min_spread: float = 1.0          # judge must span at least this much
    min_distinct: int = 2


CHARTER = Charter()


def _num(value):
    """Tolerant read: anything unparseable is UNMEASURED, never 0.0."""
    try:
        return tm._num(value)
    except tm.TensorError:
        return None


def anchor_for(score, *, charter: Charter = CHARTER) -> str:
    """The anchor band a score falls in. Unscored stays UNMEASURED."""
    s = _num(score)
    if s is None:
        return UNMEASURED
    for lo, hi, label in charter.anchors:
        if lo <= s <= hi:
            return label
    return "off-scale"


def _score(raw, what: str) -> float:
    s = _num(raw)
    if s is None:
        raise GradingError("BAD_INPUT", f"{what} requires a numeric score")
    if not (1.0 <= s <= 10.0):
        raise GradingError("BAD_INPUT", f"{what} score out of 1-10: {s}")
    return s


def apply_bar(outcome, *, raw_score=None, gate="", why="",
              charter: Charter = CHARTER) -> dict:
    """The two-tier bar. Returns the ballot; never invents an outcome.

    An honest no-op must carry the LITERAL `UNCHANGED` token - a claim of
    "nothing to fix" with no token is refused, not quietly worth 7.5.
    """
    kind = str(outcome or "").strip().lower()
    if kind not in OUTCOMES:
        raise GradingError("BAD_INPUT",
                           f"unknown outcome {outcome!r}; want {OUTCOMES}")
    gate_txt = str(gate or "").strip()
    if kind == "fix":
        s = _score(raw_score, "a real fix")
        keep = s >= charter.q_setpoint
        tier = "fix" if keep else "under-bar"
        out_gate = gate_txt.upper() or GATE_BY_OUTCOME["fix"]
    elif kind == "no_op":
        tokens = {t.strip().upper() for t in gate_txt.replace(":", " ").split()}
        if charter.unchanged_token not in tokens:
            raise GradingError(
                "UNPROVEN_NOOP",
                "honest no-op needs the literal %s token in gate, got %r"
                % (charter.unchanged_token, gate_txt))
        s = charter.no_op_score
        keep, tier = True, "honest no-op"
        out_gate = charter.unchanged_token
    elif kind == "reemit":
        s = charter.no_fix_score
        keep, tier = False, "re-emission without a fix"
        out_gate = GATE_BY_OUTCOME["reemit"]
    elif kind == "hallucination":
        s = _num(raw_score)
        s = charter.hallucination_score if s is None else s
        keep, tier = False, "hallucination"
        out_gate = GATE_BY_OUTCOME["hallucination"]
    else:  # malformed
        s = _num(raw_score)
        s = charter.hallucination_score if s is None else s
        keep, tier = False, "malformed"
        out_gate = GATE_BY_OUTCOME["malformed"]
    return {
        "outcome": kind,
        "gate": out_gate,
        "score": round(float(s), 2),
        "keep": bool(keep),
        "tier": tier,
        "anchor": anchor_for(s, charter=charter),
        "why": str(why or tier)[:dbase.TEXT_CAP],
        "bar": charter.q_setpoint,
        "rubric_version": charter.rubric_version,
    }


def judge_range_report(scores, *, charter: Charter = CHARTER) -> dict:
    """Is this judge using the range, or clustering on one number?"""
    vals = [_num(s) for s in (scores or [])]
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0, "kind": UNMEASURED, "clustered": None,
                "note": "no scores yet"}
    spread = round(max(vals) - min(vals), 4)
    distinct = len({round(v, 2) for v in vals})
    enough = len(vals) >= charter.min_range_n
    clustered = bool(enough and (spread < charter.min_spread
                                 or distinct < charter.min_distinct))
    return {
        "n": len(vals),
        "min": min(vals),
        "max": max(vals),
        "mean": round(statistics.fmean(vals), 4),
        "stdev": round(statistics.pstdev(vals), 4) if len(vals) > 1 else 0.0,
        "spread": spread,
        "distinct": distinct,
        "clustered": clustered if enough else None,
        "kind": MEASURED if enough else UNMEASURED,
        "anchors_used": sorted({anchor_for(v, charter=charter) for v in vals}),
        "note": ("judge clusters - charter says use the range"
                 if clustered else "range in use"),
    }


def model_family(model_id) -> str:
    """Family of a model / judge id. Different family = a real second judge."""
    txt = str(model_id or "").strip()
    if not txt:
        return ""
    txt = txt.split("(")[0].strip()          # "grok-4.6 (Gitur)" -> "grok-4.6"
    txt = txt.split(":")[0]                  # drop ":free"
    txt = txt.split("/")[-1]                 # drop the provider prefix
    head = txt.replace("_", "-").split("-")[0]
    return head.strip().lower()


@dataclass
class Judge:
    """A judge seat. `scorer` is injected - this module makes no calls."""

    id: str
    provider: str = ""
    scorer: object = None
    charter: Charter = CHARTER
    family: str = ""

    def __post_init__(self):
        if not str(self.id or "").strip():
            raise GradingError("BAD_INPUT", "judge id is required")
        self.family = self.family or model_family(self.id)

    def score(self, payload) -> dict:
        """Ask the injected scorer for an outcome, then apply the charter bar."""
        if not callable(self.scorer):
            raise GradingError("NO_SCORER",
                               f"judge {self.id!r} has no scorer callable")
        raw = self.scorer(payload)
        if not isinstance(raw, dict):
            raise GradingError("BAD_JUDGE_OUTPUT",
                               f"judge {self.id!r} returned {type(raw).__name__}")
        ballot = apply_bar(raw.get("outcome"), raw_score=raw.get("score"),
                           gate=raw.get("gate", ""), why=raw.get("why", ""),
                           charter=self.charter)
        ballot["judge"] = self.id
        ballot["judge_family"] = self.family
        ballot["judge_provider"] = self.provider
        return ballot


def dual_judge(primary: dict, second: dict, *,
               refuse_same_family: bool = True) -> dict:
    """Primary + second judge. Same family is refused, not averaged away.

    Disagreement is PUBLISHED DATA: the judge is a tensor axis, so the rate
    is a measurement, not a defect to smooth over.
    """
    for name, b in (("primary", primary), ("second", second)):
        if not isinstance(b, dict) or "keep" not in b:
            raise GradingError("BAD_INPUT", f"{name} ballot is not a ballot")
    fam_a = primary.get("judge_family") or model_family(primary.get("judge"))
    fam_b = second.get("judge_family") or model_family(second.get("judge"))
    if refuse_same_family and fam_a and fam_a == fam_b:
        raise GradingError(
            "SAME_FAMILY",
            f"second judge must be a different model family (both {fam_a!r})")
    agree = bool(primary["keep"]) == bool(second["keep"])
    sa, sb = _num(primary.get("score")), _num(second.get("score"))
    delta = None if sa is None or sb is None else round(abs(sa - sb), 2)
    return {
        "judge_agreement": agree,
        "score_delta": delta,
        "primary": {"judge": primary.get("judge"), "score": sa,
                    "keep": primary.get("keep"), "family": fam_a},
        "second": {"judge": second.get("judge"), "score": sb,
                   "keep": second.get("keep"), "family": fam_b},
        "families": [fam_a, fam_b],
        "kind": MEASURED,
        "note": "judge disagreement is published data, not noise",
    }


def judge_disagreement(cells) -> dict:
    """Judge-vs-judge KEEP disagreement rate over the corpus."""
    rows = [c if c.get("dedupe_key") else dbase.normalize_cell(c)
            for c in (cells or [])]
    groups: dict[tuple, list[dict]] = {}
    for c in rows:
        groups.setdefault((c["order_id"], c["seat"]), []).append(c)
    n_cmp, n_dis = 0, 0
    by_pair: dict[str, dict] = {}
    for key in sorted(groups):
        members = sorted(groups[key], key=lambda m: m["judge"].lower())
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                a, b = members[i], members[j]
                if a["keep"] is None or b["keep"] is None:
                    continue
                pk = "%s|%s" % (a["judge"], b["judge"])
                slot = by_pair.setdefault(pk, {
                    "judges": [a["judge"], b["judge"]],
                    "families": [model_family(a["judge"]),
                                 model_family(b["judge"])],
                    "n": 0, "n_disagree": 0, "rate": None,
                    "same_family": model_family(a["judge"])
                    == model_family(b["judge"])})
                slot["n"] += 1
                n_cmp += 1
                if bool(a["keep"]) != bool(b["keep"]):
                    slot["n_disagree"] += 1
                    n_dis += 1
    for slot in by_pair.values():
        slot["rate"] = round(slot["n_disagree"] / slot["n"], 6) if slot["n"] else None
    return {
        "n_comparisons": n_cmp,
        "n_disagree": n_dis,
        "rate": round(n_dis / n_cmp, 6) if n_cmp else None,
        "by_judge_pair": by_pair,
        "kind": MEASURED if n_cmp else UNMEASURED,
        "note": "judge is a tensor axis; this rate is published, not hidden",
    }


# ---------------------------------------------------------------- rater
def _format_ok(c: dict) -> bool | None:
    if c.get("format_ok") is not None:
        return bool(c["format_ok"])
    gate = (c.get("gate") or "").upper()
    return gate not in MALFORMED_GATES


def _usable(c: dict) -> bool | None:
    if not _format_ok(c):
        return False
    return (c.get("gate") or "").upper() not in UNUSABLE_GATES


def seat_rates(cells, *, charter: Charter = CHARTER) -> dict:
    """Per-seat rates folded from cells. Empty slices stay UNMEASURED."""
    rows = [c if c.get("dedupe_key") else dbase.normalize_cell(c)
            for c in (cells or [])]
    acc: dict[str, dict] = {}
    for c in rows:
        s = acc.setdefault(c["seat"], {
            "seat": c["seat"], "models": set(), "providers": set(),
            "judges": set(), "n": 0, "n_format": 0, "n_format_known": 0,
            "n_usable": 0, "n_keep": 0, "n_keep_known": 0,
            "scores": [], "usd_sum": 0.0, "usd_n": 0})
        s["n"] += 1
        if c["model"]:
            s["models"].add(c["model"])
        if c["provider"]:
            s["providers"].add(c["provider"])
        s["judges"].add(c["judge"])
        fmt = _format_ok(c)
        if fmt is not None:
            s["n_format_known"] += 1
            s["n_format"] += 1 if fmt else 0
            if _usable(c):
                s["n_usable"] += 1
        if c["keep"] is not None:
            s["n_keep_known"] += 1
            s["n_keep"] += 1 if c["keep"] else 0
        if c["score"] is not None:
            s["scores"].append(c["score"])
        if c["usd"] is not None:
            s["usd_sum"] += c["usd"]
            s["usd_n"] += 1

    def _pct(num, den):
        return None if not den else round(100.0 * num / den, 3)

    out: dict[str, dict] = {}
    for seat, s in sorted(acc.items()):
        mean_q = round(statistics.fmean(s["scores"]), 4) if s["scores"] else None
        keep_n = s["n_keep"]
        usd = round(s["usd_sum"], 6) if s["usd_n"] else None
        free = usd is not None and usd == 0.0
        out[seat] = {
            "seat": seat,
            "models": sorted(s["models"]),
            "providers": sorted(s["providers"]),
            "judges": sorted(s["judges"]),
            "n": s["n"],
            "format_pct": _pct(s["n_format"], s["n_format_known"]),
            "usable_pct": _pct(s["n_usable"], s["n_format_known"]),
            "keep_pct": _pct(keep_n, s["n_keep_known"]),
            "keep_n": keep_n,
            "mean_score": mean_q,
            "range": judge_range_report(s["scores"], charter=charter),
            "usd": usd,
            "usd_per_keep": (None if not keep_n or usd is None
                             else round(usd / keep_n, 6)),
            "q_per_usd": (None if mean_q is None or not usd
                          else round(mean_q / usd, 4)),
            "cost_kind": ("FREE" if free else
                          (UNMEASURED if usd is None else MEASURED)),
            "bar": charter.q_setpoint,
            "kind": MEASURED if s["scores"] else UNMEASURED,
            "rubric_version": charter.rubric_version,
        }
    return out


def blend(rate_row: dict, bench=None, *, w_rate=0.75, w_bench=0.25) -> dict:
    """Blend measured keep-quality with a bench value. No component, no Q.

    Weights are renormalized over the components that actually exist, so a
    missing bench does not silently drag Q toward zero.
    """
    comps, weights = {}, {}
    q = None if rate_row is None else _num(rate_row.get("mean_score"))
    if q is not None:
        comps["rate"], weights["rate"] = q, float(w_rate)
    b = _num(bench)
    if b is not None:
        comps["bench"], weights["bench"] = b, float(w_bench)
    total_w = sum(weights.values())
    if not comps or total_w <= 0:
        return {"q_blend": None, "components": comps, "weights": {},
                "kind": UNMEASURED,
                "note": "no measured component; Q stays UNMEASURED"}
    norm = {k: round(v / total_w, 6) for k, v in weights.items()}
    q_blend = round(sum(comps[k] * norm[k] for k in comps), 4)
    return {"q_blend": q_blend, "components": comps, "weights": norm,
            "kind": MEASURED,
            "note": "weights renormalized over measured components only"}


def rate_seats(root, *, benches=None, charter: Charter = CHARTER) -> dict:
    """Read the store and rate every seat in it. Never mkdir."""
    cells = dbase.load_cells(root)
    rates = seat_rates(cells, charter=charter)
    benches = benches if isinstance(benches, dict) else {}
    for seat, row in rates.items():
        row["blend"] = blend(row, benches.get(seat))
    return {
        "schema": dbase.SCHEMA,
        "ok": True,
        "n_obs": len(cells),
        "kind": MEASURED if rates else UNMEASURED,
        "seats": rates,
        "judges": judge_disagreement(cells),
        "bar": charter.q_setpoint,
        "rubric_version": charter.rubric_version,
    }


def recommend_seating(root, candidates, k=3, *, incumbent="", benches=None,
                      costs=None, domains=None, charter: Charter = CHARTER) -> dict:
    """Seating recommendation = tensor_math.recommend_team(k) over the store."""
    rated = rate_seats(root, benches=benches, charter=charter)
    scores = {}
    for seat, row in rated["seats"].items():
        q = row["blend"]["q_blend"]
        if q is not None:
            scores[seat] = q
    obs = dbase.pair_observations(root)
    team = tm.recommend_team(obs, candidates, k, incumbent=incumbent,
                             scores=scores, costs=costs, axes=("domain",),
                             domains=domains)
    team["scores"] = scores
    team["scores_kind"] = MEASURED if scores else UNMEASURED
    team["n_obs"] = rated["n_obs"]
    team["bar"] = charter.q_setpoint
    return team


# --------------------------------------------------- score -> tensor cell
def make_cell(*, run_id, order_id, fn, domain, pair, judge, scaffold,
              provider, ballot: dict, model="", usd=None, cache_version="",
              t="", judge_agreement=None, charter: Charter = CHARTER) -> dict:
    """Build one orc-tensor-cell/1 row. Missing provenance is REFUSED."""
    prov = {"run_id": run_id, "order_id": order_id, "fn": fn,
            "domain": domain, "pair": pair, "judge": judge,
            "scaffold": scaffold, "provider": provider}
    missing = [k for k in PROVENANCE
               if not prov[k] or (isinstance(prov[k], (list, tuple))
                                  and not [x for x in prov[k] if x])]
    if missing:
        raise GradingError("NO_PROVENANCE",
                           "a score with no provenance is not a measurement; "
                           f"missing {missing}")
    if not isinstance(ballot, dict) or "score" not in ballot:
        raise GradingError("BAD_INPUT", "ballot must come from apply_bar()")
    seats = list(pair) if isinstance(pair, (list, tuple)) else [pair]
    cell = {
        "schema": CELL_SCHEMA,
        "t": str(t or dbase._iso()),
        "run_id": run_id,
        "order_id": order_id,
        "fn": fn,
        "domain": domain,
        "pair": seats,
        "judge": judge,
        "scaffold": scaffold,
        "provider": provider,
        "model": model,
        "gate": ballot["gate"],
        "score": ballot["score"],
        "keep": ballot["keep"],
        "why": ballot.get("why", ""),
        "usd": 0.0 if usd is None else float(usd),
        "cache_version": str(cache_version or ""),
        "rubric_version": ballot.get("rubric_version", charter.rubric_version),
    }
    if judge_agreement is not None:
        cell["judge_agreement"] = bool(judge_agreement)
    dbase.normalize_cell(cell)          # fail-closed before it reaches the store
    return cell


def score_and_record(root, *, outcome, run_id, order_id, fn, domain, pair,
                     judge, scaffold, provider, raw_score=None, gate="",
                     why="", model="", usd=None, cache_version="",
                     second=None, charter: Charter = CHARTER,
                     write: bool = True) -> dict:
    """Grade once, then write the tensor cell(s). One path, always provenanced.

    `second` is an optional second-judge ballot dict (with a `judge` id from
    a different model family); when present the pair's agreement is recorded
    on both cells and a second cell is written for the second judge.
    """
    ballot = apply_bar(outcome, raw_score=raw_score, gate=gate, why=why,
                       charter=charter)
    ballot["judge"] = judge
    ballot["judge_family"] = model_family(judge)
    dual = None
    if second is not None:
        dual = dual_judge(ballot, second)
    cells = [make_cell(run_id=run_id, order_id=order_id, fn=fn, domain=domain,
                       pair=pair, judge=judge, scaffold=scaffold,
                       provider=provider, ballot=ballot, model=model, usd=usd,
                       cache_version=cache_version,
                       judge_agreement=None if dual is None
                       else dual["judge_agreement"], charter=charter)]
    if dual is not None:
        cells.append(make_cell(
            run_id=run_id, order_id=order_id, fn=fn, domain=domain, pair=pair,
            judge=second.get("judge"), scaffold=scaffold, provider=provider,
            ballot=second, model=model, usd=second.get("usd"),
            cache_version=cache_version,
            judge_agreement=dual["judge_agreement"], charter=charter))
    out = {"ballot": ballot, "dual": dual, "cells": cells,
           "bar": charter.q_setpoint,
           "rubric_version": charter.rubric_version}
    if write:
        out["ingest"] = dbase.ingest(root, cells)
    return out


# ---------------------------------------------------------------- selftest
def _selftest(quiet: bool = False) -> int:
    import tempfile

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    def _refuses(fn, kind):
        try:
            fn()
        except GradingError as e:
            return e.kind == kind
        return False

    KELLY = "gemini-3.8-flash (Kelly)"
    GITUR = "grok-4.6 (Gitur)"

    # 1. Two-tier bar, exactly at the setpoint.
    at_bar = apply_bar("fix", raw_score=8.0)
    under = apply_bar("fix", raw_score=7.9)
    check("real fix at the bar (8.0) KEEPs; 7.9 DROPs",
          lambda: at_bar["keep"] is True and at_bar["score"] == 8.0
          and under["keep"] is False and under["tier"] == "under-bar"
          and at_bar["bar"] == 8.0)

    # 2. Honest no-op needs the literal token.
    noop = apply_bar("no_op", gate="UNCHANGED")
    check("honest no-op = literal UNCHANGED token -> 7.5 KEEP",
          lambda: noop["score"] == 7.5 and noop["keep"] is True
          and noop["gate"] == UNCHANGED and noop["anchor"] == "minor nit")
    check("NEGATIVE CONTROL: a no-op claim without the literal UNCHANGED "
          "token is REFUSED, not worth 7.5",
          lambda: _refuses(lambda: apply_bar("no_op", gate="nothing to fix"),
                           "UNPROVEN_NOOP"))

    # 3. Re-emission and hallucination.
    reemit = apply_bar("reemit")
    hall = apply_bar("hallucination", raw_score=9.5)
    check("re-emission without a fix -> 5.0 DROP",
          lambda: reemit["score"] == 5.0 and reemit["keep"] is False
          and reemit["anchor"] == "no fix")
    check("NEGATIVE CONTROL: hallucination DROPs regardless of the score "
          "(9.5 still DROP)",
          lambda: hall["keep"] is False and hall["score"] == 9.5
          and hall["tier"] == "hallucination")
    check("unknown outcome refused; fix without a score refused",
          lambda: _refuses(lambda: apply_bar("vibes"), "BAD_INPUT")
          and _refuses(lambda: apply_bar("fix"), "BAD_INPUT"))

    # 4. Anchors span the range.
    check("anchors map 9.5/8.0/7.0/5.0/3.0/1.0 to the charter bands",
          lambda: [anchor_for(s) for s in (9.5, 8.0, 7.0, 5.0, 3.0, 1.0)]
          == ["exemplary (rare)", "solid", "minor nit", "no fix",
              "charter violations", "garbage"]
          and anchor_for(None) == UNMEASURED)

    # 5. NEGATIVE CONTROL: a clustering judge is flagged.
    clustered = judge_range_report([8.0] * 6)
    spread = judge_range_report([9.5, 8.0, 7.0, 5.0, 3.0, 1.0])
    thin = judge_range_report([8.0, 8.0])
    check("NEGATIVE CONTROL: six identical scores flag clustered=True; a "
          "judge using the range does not; n<5 stays UNMEASURED",
          lambda: clustered["clustered"] is True and clustered["spread"] == 0.0
          and spread["clustered"] is False and spread["spread"] == 8.5
          and len(spread["anchors_used"]) == 6
          and thin["clustered"] is None and thin["kind"] == UNMEASURED)

    # 6. Dual-judge across families; same family refused.
    check("model_family splits vendor prefixes and nicknames",
          lambda: model_family(KELLY) == "gemini"
          and model_family("inclusionai/ling-3.0-flash-vl:free") == "ling"
          and model_family(GITUR) == "grok")
    b1 = dict(at_bar, judge=KELLY, judge_family="gemini")
    b2 = dict(reemit, judge=GITUR, judge_family="grok")
    dual = dual_judge(b1, b2)
    check("dual-judge records agreement and the score delta as data",
          lambda: dual["judge_agreement"] is False
          and dual["score_delta"] == 3.0
          and dual["families"] == ["gemini", "grok"])
    check("NEGATIVE CONTROL: a second judge from the same family is REFUSED",
          lambda: _refuses(
              lambda: dual_judge(b1, dict(b2, judge="gemini-3.8-pro",
                                          judge_family="gemini")),
              "SAME_FAMILY"))

    # 7. Judge interface: the scorer is injected, no network.
    judge = Judge(KELLY, provider="Vertex",
                  scorer=lambda payload: {"outcome": "no_op",
                                          "gate": "UNCHANGED",
                                          "why": "honest no-op"})
    ballot = judge.score({"fn": "renderCoreTelemetry"})
    check("Judge applies the charter to an injected scorer's outcome",
          lambda: ballot["score"] == 7.5 and ballot["judge"] == KELLY
          and ballot["judge_family"] == "gemini")
    check("a judge with no scorer refuses instead of inventing a score",
          lambda: _refuses(lambda: Judge("x-1").score({}), "NO_SCORER"))

    # 8. Provenance is mandatory - the negative control on the write path.
    td = Path(tempfile.mkdtemp(prefix="tensor_grading_"))
    root = td / "store"
    scaffold = {"seat": "ling", "preload": "L1", "prefill": True}
    check("NEGATIVE CONTROL: a score with no provenance is REFUSED, not stored",
          lambda: _refuses(lambda: make_cell(
              run_id="b4", order_id="", fn="renderCoreTelemetry",
              domain="core", pair=["ling"], judge=KELLY, scaffold=scaffold,
              provider="Novita", ballot=noop), "NO_PROVENANCE")
          and not root.exists())

    # 9. Every score writes a tensor cell, and the store reads it back.
    rec = score_and_record(
        root, outcome="no_op", gate="UNCHANGED", run_id="b4",
        order_id="b4-007", fn="renderCoreTelemetry", domain="core",
        pair=["ling"], judge=KELLY, scaffold=scaffold, provider="Novita",
        model="inclusionai/ling-3.0-flash-vl:free", usd=0.0,
        cache_version="orc-b234-20260914", why="honest no-op")
    snap = dbase.read(root)
    check("score_and_record writes a provenanced cell the store reads back",
          lambda: rec["ingest"]["n_new"] == 1 and snap["n_obs"] == 1
          and snap["seats"] == {"ling": 1}
          and rec["cells"][0]["rubric_version"]
          == CHARTER.rubric_version)

    # 10. Second judge writes its own cell on the judge axis.
    second = dict(apply_bar("reemit"), judge=GITUR, judge_family="grok")
    rec2 = score_and_record(
        root, outcome="fix", raw_score=8.5, gate="PATCHED", run_id="b4",
        order_id="b4-008", fn="renderCoreTelemetry", domain="core",
        pair=["ling"], judge=KELLY, scaffold=scaffold, provider="Novita",
        second=second, usd=0.0)
    dis = judge_disagreement(dbase.load_cells(root))
    check("dual-judge writes both cells and publishes the disagreement rate",
          lambda: len(rec2["cells"]) == 2 and rec2["dual"]["judge_agreement"]
          is False and dis["n_comparisons"] == 1 and dis["rate"] == 1.0
          and dis["kind"] == MEASURED)

    # 11. Model rater: rates, free-seat cost honesty, blend renormalization.
    rated = rate_seats(root, benches={"ling": 6.0})
    ling = rated["seats"]["ling"]
    check("seat rates: keep%, mean score, dollars-per-keep on a free seat",
          lambda: ling["n"] == 3 and ling["keep_pct"] == round(200.0 / 3, 3)
          and ling["format_pct"] == 100.0
          and ling["usd_per_keep"] == 0.0
          and ling["q_per_usd"] is None and ling["cost_kind"] == "FREE")
    check("blend renormalizes over measured components; no component -> "
          "UNMEASURED",
          lambda: ling["blend"]["kind"] == MEASURED
          and ling["blend"]["weights"] == {"rate": 0.75, "bench": 0.25}
          and blend({"mean_score": None})["kind"] == UNMEASURED
          and blend({"mean_score": 8.0})["weights"] == {"rate": 1.0})

    # 12. Format and usable rates separate "parsed" from "worth keeping".
    fmt_root = td / "format"
    plan = (("fix", 9.0, "PATCHED"), ("no_op", None, "UNCHANGED"),
            ("reemit", None, "REEMIT"),
            ("hallucination", None, "HALLUCINATION"),
            ("malformed", None, "MALFORMED"))
    for i, (outcome, sc, gate) in enumerate(plan, start=1):
        score_and_record(
            fmt_root, outcome=outcome, raw_score=sc, gate=gate, run_id="b7",
            order_id=f"b7-00{i}", fn="renderCoreTelemetry", domain="core",
            pair=["glm"], judge=KELLY,
            scaffold={"seat": "glm", "preload": "L1"}, provider="Novita",
            model="z-ai/glm-5.3-flash", usd=0.0)
    glm = rate_seats(fmt_root)["seats"]["glm"]
    check("format% counts parsed output, usable% drops hallucination and "
          "malformed, keep% is the bar (80 / 60 / 40 on five cells)",
          lambda: glm["n"] == 5 and glm["format_pct"] == 80.0
          and glm["usable_pct"] == 60.0 and glm["keep_pct"] == 40.0
          and glm["keep_n"] == 2)

    # 13. Paid seat: Q-per-dollar is measured, dollars-per-keep is real.
    paid_root = td / "paid"
    for i, (outcome, score) in enumerate(
            (("fix", 9.0), ("reemit", None)), start=1):
        score_and_record(
            paid_root, outcome=outcome, raw_score=score,
            gate="PATCHED" if outcome == "fix" else "REEMIT",
            run_id="b5", order_id=f"b5-00{i}", fn="renderCoreTelemetry",
            domain="core", pair=["opus"], judge=KELLY,
            scaffold={"seat": "opus", "preload": "L1"}, provider="Anthropic",
            model="claude/opus-5", usd=0.5)
    paid = rate_seats(paid_root)["seats"]["opus"]
    check("paid seat: usd_per_keep and q_per_usd are MEASURED numbers",
          lambda: paid["usd"] == 1.0 and paid["keep_n"] == 1
          and paid["usd_per_keep"] == 1.0 and paid["q_per_usd"] == 7.0
          and paid["cost_kind"] == MEASURED)

    # 14. Seating recommendation comes from the tensor, not from the rates.
    team_root = td / "team"
    for i, (ling_out, luna_out, ling_s, luna_s) in enumerate((
            ("reemit", "fix", None, 9.0),
            ("reemit", "fix", None, 8.5),
            ("fix", "fix", 8.0, 8.0)), start=1):
        for seat, outcome, sc, prov in (("ling", ling_out, ling_s, "Novita"),
                                        ("luna", luna_out, luna_s, "Groq")):
            score_and_record(
                team_root, outcome=outcome, raw_score=sc,
                gate="PATCHED" if outcome == "fix" else "REEMIT",
                run_id="b6", order_id=f"b6-00{i}", fn="renderCoreTelemetry",
                domain="core", pair=[seat], judge=KELLY,
                scaffold={"seat": seat, "preload": "L1"}, provider=prov,
                model=f"vendor/{seat}", usd=0.0)
    team = recommend_seating(team_root, ["luna", "glm"], 3, incumbent="ling")
    check("seating: incumbent seated, rescuing seat next, unseen seat last",
          lambda: team["team"] == ["ling", "luna", "glm"]
          and team["steps"][1]["kind"] == MEASURED
          and team["steps"][1]["via"] == "complement"
          and team["steps"][2]["kind"] == UNMEASURED
          and team["scores_kind"] == MEASURED)

    # 15. The bar is config, not a constant baked into the logic.
    strict = replace(CHARTER, q_setpoint=9.0)
    check("q_setpoint config moves the KEEP bar (8.5 KEEPs at 8.0, DROPs at 9.0)",
          lambda: apply_bar("fix", raw_score=8.5)["keep"] is True
          and apply_bar("fix", raw_score=8.5, charter=strict)["keep"] is False
          and apply_bar("no_op", gate="UNCHANGED",
                        charter=strict)["keep"] is True)

    failed = [(l, e) for l, ok, e in results if not ok]
    if not quiet:
        for label, ok, err in results:
            print(("PASS" if ok else "FAIL"), label, err)
        print("grading selftest %d/%d"
              % (len(results) - len(failed), len(results)))
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print(__doc__)
    raise SystemExit(2)
