#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""grading: the charter bar, dual-judge, model rater, and mutation controls."""
from __future__ import annotations

import sys
import types
from dataclasses import replace
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import pytest  # noqa: E402

from builds.tensor import dbase, grading as g, tensor_math as tm  # noqa: E402

SRC = Path(g.__file__)
KELLY = "gemini-3.8-flash (Kelly)"
GITUR = "grok-4.6 (Gitur)"
SCAFFOLD = {"seat": "ling", "preload": "L1", "prefill": True}
PROV = dict(run_id="b4", fn="renderCoreTelemetry", domain="core",
            judge=KELLY, scaffold=SCAFFOLD, provider="Novita")


def _mutated(old: str, new: str, name: str):
    src = SRC.read_text(encoding="utf-8")
    assert src.count(old) >= 1, f"mutation target vanished: {old!r}"
    mod_name = f"builds.tensor._mut_grading_{name}"
    mod = types.ModuleType(mod_name)
    mod.__file__ = str(SRC)
    mod.__package__ = "builds.tensor"
    sys.modules[mod_name] = mod
    try:
        exec(compile(src.replace(old, new, 1), str(SRC), "exec"), mod.__dict__)
    finally:
        sys.modules.pop(mod_name, None)
    return mod


# ------------------------------------------------------------ selftest gate
def test_selftest_is_green():
    assert g._selftest(quiet=True) == 0


# --------------------------------------------------------------- the bar
@pytest.mark.parametrize("score,keep", [
    (10.0, True), (8.1, True), (8.0, True), (7.999, False), (7.0, False),
    (1.0, False)])
def test_real_fix_bar_is_the_q_setpoint(score, keep):
    assert g.apply_bar("fix", raw_score=score)["keep"] is keep


def test_honest_no_op_needs_the_literal_unchanged_token():
    ballot = g.apply_bar("no_op", gate="UNCHANGED")
    assert (ballot["score"], ballot["keep"]) == (7.5, True)
    assert ballot["gate"] == "UNCHANGED"
    with pytest.raises(g.GradingError) as e:
        g.apply_bar("no_op", gate="nothing needed here")
    assert e.value.kind == "UNPROVEN_NOOP"


def test_reemission_is_five_and_drops():
    ballot = g.apply_bar("reemit")
    assert (ballot["score"], ballot["keep"]) == (5.0, False)
    assert ballot["anchor"] == "no fix"


@pytest.mark.parametrize("raw", [None, 5.0, 9.9])
def test_hallucination_drops_regardless_of_the_score(raw):
    ballot = g.apply_bar("hallucination", raw_score=raw)
    assert ballot["keep"] is False and ballot["tier"] == "hallucination"


def test_malformed_drops_and_is_not_usable():
    ballot = g.apply_bar("malformed")
    assert ballot["keep"] is False and ballot["gate"] == "MALFORMED"


@pytest.mark.parametrize("kwargs", [
    {"outcome": "vibes"},
    {"outcome": "fix"},                        # no score
    {"outcome": "fix", "raw_score": 0.5},      # out of range
    {"outcome": "fix", "raw_score": "n/a"},
])
def test_bad_grades_are_refused(kwargs):
    with pytest.raises(g.GradingError):
        g.apply_bar(**kwargs)


def test_bar_is_config_not_a_constant():
    strict = replace(g.CHARTER, q_setpoint=9.0)
    assert g.apply_bar("fix", raw_score=8.5)["keep"] is True
    assert g.apply_bar("fix", raw_score=8.5, charter=strict)["keep"] is False
    assert g.apply_bar("no_op", gate="UNCHANGED", charter=strict)["keep"] is True


def test_anchors_span_the_range():
    got = [g.anchor_for(s) for s in (10.0, 9.0, 8.5, 7.2, 5.0, 3.4, 1.0)]
    assert got == ["exemplary (rare)", "exemplary (rare)", "solid",
                   "minor nit", "no fix", "charter violations", "garbage"]
    assert g.anchor_for(None) == tm.UNMEASURED


# ------------------------------------------------------- judge behaviour
def test_clustering_judge_is_flagged_and_range_use_is_not():
    assert g.judge_range_report([8.0] * 6)["clustered"] is True
    assert g.judge_range_report([8.0, 8.4, 8.2, 8.1, 8.3])["clustered"] is True
    spread = g.judge_range_report([9.5, 8.0, 7.0, 5.0, 3.0])
    assert spread["clustered"] is False and spread["spread"] == 6.5
    assert g.judge_range_report([])["kind"] == tm.UNMEASURED
    assert g.judge_range_report([8.0, 5.0])["clustered"] is None


@pytest.mark.parametrize("model,family", [
    (KELLY, "gemini"),
    ("inclusionai/ling-3.0-flash-vl:free", "ling"),
    (GITUR, "grok"),
    ("claude-opus-5-thinking", "claude"),
    ("", ""),
])
def test_model_family(model, family):
    assert g.model_family(model) == family


def test_judge_uses_an_injected_scorer_and_refuses_without_one():
    judge = g.Judge(KELLY, provider="Vertex", scorer=lambda p: {
        "outcome": "fix", "score": 8.5, "gate": "PATCHED", "why": "real fix"})
    ballot = judge.score({"fn": "renderCoreTelemetry"})
    assert ballot["keep"] is True and ballot["judge_family"] == "gemini"
    with pytest.raises(g.GradingError) as e:
        g.Judge("mystery-1").score({})
    assert e.value.kind == "NO_SCORER"


def test_judge_with_a_broken_scorer_is_refused():
    judge = g.Judge(KELLY, scorer=lambda p: "8/10, looks fine")
    with pytest.raises(g.GradingError) as e:
        judge.score({})
    assert e.value.kind == "BAD_JUDGE_OUTPUT"


def test_dual_judge_requires_a_different_family():
    primary = dict(g.apply_bar("fix", raw_score=8.5), judge=KELLY)
    same = dict(g.apply_bar("reemit"), judge="gemini-3.8-pro")
    with pytest.raises(g.GradingError) as e:
        g.dual_judge(primary, same)
    assert e.value.kind == "SAME_FAMILY"
    other = dict(g.apply_bar("reemit"), judge=GITUR)
    dual = g.dual_judge(primary, other)
    assert dual["judge_agreement"] is False and dual["score_delta"] == 3.5
    assert dual["families"] == ["gemini", "grok"]


def test_judge_disagreement_is_published(tmp_path):
    root = tmp_path / "store"
    for judge, outcome, score in ((KELLY, "fix", 8.5), (GITUR, "reemit", None)):
        g.score_and_record(root, outcome=outcome, raw_score=score,
                           gate="PATCHED" if outcome == "fix" else "REEMIT",
                           order_id="b4-1", pair=["ling"],
                           **dict(PROV, judge=judge))
    dis = g.judge_disagreement(dbase.load_cells(root))
    assert dis["n_comparisons"] == 1 and dis["rate"] == 1.0
    pair = list(dis["by_judge_pair"].values())[0]
    assert pair["same_family"] is False and pair["n_disagree"] == 1
    assert g.judge_disagreement([])["kind"] == tm.UNMEASURED


# ---------------------------------------------------------- model rater
def _record(root, order, seat, outcome, score=None, usd=0.0, judge=KELLY,
            provider="Novita", domain="core"):
    return g.score_and_record(
        root, outcome=outcome, raw_score=score,
        gate={"fix": "PATCHED", "no_op": "UNCHANGED",
              "reemit": "REEMIT", "hallucination": "HALLUCINATION",
              "malformed": "MALFORMED"}[outcome],
        run_id="b4", order_id=order, fn="renderCoreTelemetry", domain=domain,
        pair=[seat], judge=judge, scaffold={"seat": seat, "preload": "L1"},
        provider=provider, model=f"vendor/{seat}", usd=usd)


def test_seat_rates_are_measured_percentages(tmp_path):
    root = tmp_path / "store"
    _record(root, "b4-1", "ling", "fix", 9.0)
    _record(root, "b4-2", "ling", "no_op")
    _record(root, "b4-3", "ling", "reemit")
    _record(root, "b4-4", "ling", "hallucination")
    row = g.rate_seats(root)["seats"]["ling"]
    assert row["n"] == 4 and row["keep_n"] == 2
    assert row["keep_pct"] == 50.0
    assert row["usable_pct"] == 75.0     # hallucination is not usable output
    assert row["format_pct"] == 100.0
    assert row["mean_score"] == pytest.approx((9.0 + 7.5 + 5.0 + 1.0) / 4)
    assert row["cost_kind"] == "FREE" and row["usd_per_keep"] == 0.0
    assert row["q_per_usd"] is None


def test_paid_seat_gets_dollars_per_keep_and_q_per_dollar(tmp_path):
    root = tmp_path / "store"
    _record(root, "b5-1", "opus", "fix", 9.0, usd=0.5)
    _record(root, "b5-2", "opus", "reemit", usd=0.5)
    row = g.rate_seats(root)["seats"]["opus"]
    assert row["usd"] == 1.0 and row["usd_per_keep"] == 1.0
    assert row["q_per_usd"] == 7.0 and row["cost_kind"] == tm.MEASURED


def test_empty_store_rates_are_unmeasured(tmp_path):
    rated = g.rate_seats(tmp_path / "store")
    assert rated["kind"] == tm.UNMEASURED and rated["seats"] == {}
    assert rated["n_obs"] == 0
    assert not (tmp_path / "store").exists()


def test_blend_renormalizes_over_measured_components():
    both = g.blend({"mean_score": 8.0}, 6.0)
    assert both["weights"] == {"rate": 0.75, "bench": 0.25}
    assert both["q_blend"] == pytest.approx(8.0 * 0.75 + 6.0 * 0.25)
    rate_only = g.blend({"mean_score": 8.0})
    assert rate_only["weights"] == {"rate": 1.0} and rate_only["q_blend"] == 8.0
    bench_only = g.blend({"mean_score": None}, 6.0)
    assert bench_only["q_blend"] == 6.0
    assert g.blend({"mean_score": None})["kind"] == tm.UNMEASURED
    assert g.blend(None)["q_blend"] is None


# ------------------------------------------------------- write path / cells
def test_every_score_writes_a_provenanced_tensor_cell(tmp_path):
    root = tmp_path / "store"
    rec = g.score_and_record(root, outcome="no_op", gate="UNCHANGED",
                             order_id="b4-7", pair=["ling"],
                             model="inclusionai/ling-3.0-flash-vl:free",
                             cache_version="orc-b234-20260914", **PROV)
    cell = rec["cells"][0]
    for key in g.PROVENANCE:
        assert cell[key], f"provenance key {key} missing from the cell"
    assert cell["schema"] == dbase.CELL_SCHEMA
    assert cell["score"] == 7.5 and cell["keep"] is True
    assert cell["rubric_version"] == g.CHARTER.rubric_version
    assert dbase.read(root)["n_obs"] == 1


@pytest.mark.parametrize("drop", ["order_id", "fn", "domain", "judge",
                                  "provider", "scaffold", "run_id"])
def test_a_score_without_provenance_is_refused(tmp_path, drop):
    root = tmp_path / "store"
    kw = dict(PROV, order_id="b4-7", pair=["ling"])
    kw[drop] = "" if drop != "scaffold" else {}
    with pytest.raises(g.GradingError) as e:
        g.score_and_record(root, outcome="no_op", gate="UNCHANGED", **kw)
    assert e.value.kind == "NO_PROVENANCE"
    assert not root.exists(), "a refused score still touched the store"


def test_empty_pair_is_refused(tmp_path):
    with pytest.raises(g.GradingError) as e:
        g.make_cell(run_id="b4", order_id="b4-7", fn="f", domain="core",
                    pair=[], judge=KELLY, scaffold=SCAFFOLD,
                    provider="Novita", ballot=g.apply_bar("reemit"))
    assert e.value.kind == "NO_PROVENANCE"


def test_dual_judge_writes_a_cell_per_judge(tmp_path):
    root = tmp_path / "store"
    second = dict(g.apply_bar("reemit"), judge=GITUR)
    rec = g.score_and_record(root, outcome="fix", raw_score=8.5,
                             gate="PATCHED", order_id="b4-8", pair=["ling"],
                             second=second, **PROV)
    assert len(rec["cells"]) == 2
    judges = {c["judge"] for c in rec["cells"]}
    assert judges == {KELLY, GITUR}
    assert all(c["judge_agreement"] is False for c in rec["cells"])
    assert dbase.read(root)["n_obs"] == 2


def test_write_false_grades_without_touching_the_store(tmp_path):
    root = tmp_path / "store"
    rec = g.score_and_record(root, outcome="reemit", order_id="b4-9",
                             pair=["ling"], write=False, **PROV)
    assert "ingest" not in rec and not root.exists()


# ------------------------------------------------------------- seating
def _pair_corpus(root):
    """ling keeps failing where luna fixes; then both solid on one order."""
    plan = ((1, "reemit", None, "fix", 9.0),
            (2, "reemit", None, "fix", 8.5),
            (3, "fix", 8.0, "fix", 8.0))
    for i, ling_out, ling_s, luna_out, luna_s in plan:
        _record(root, f"b6-{i}", "ling", ling_out, ling_s)
        _record(root, f"b6-{i}", "luna", luna_out, luna_s, provider="Groq")


def test_recommend_seating_uses_the_tensor(tmp_path):
    root = tmp_path / "store"
    _pair_corpus(root)
    team = g.recommend_seating(root, ["luna", "glm"], 3, incumbent="ling")
    assert team["team"] == ["ling", "luna", "glm"]
    assert team["steps"][1]["kind"] == tm.MEASURED
    assert team["steps"][1]["via"] == "complement"
    assert team["steps"][2]["kind"] == tm.UNMEASURED
    assert team["scores"]["luna"] > 0 and team["scores_kind"] == tm.MEASURED


def test_recommend_seating_on_an_empty_store_is_unmeasured(tmp_path):
    team = g.recommend_seating(tmp_path / "store", ["luna", "glm"], 2)
    assert team["kind"] == tm.UNMEASURED
    assert all(s["kind"] == tm.UNMEASURED for s in team["steps"])
    assert team["scores"] == {}


# ------------------------------------------- negative controls (mutations)
MUTATIONS = [
    # the bar moved off the charter setpoint
    ("bar_lowered", "    q_setpoint: float = 8.0", "    q_setpoint: float = 7.0"),
    # honest no-op no longer needs the literal token
    ("noop_token_dropped",
     "        if charter.unchanged_token not in tokens:", "        if False:"),
    # no-op priced above the bar
    ("noop_score", "    no_op_score: float = 7.5",
     "    no_op_score: float = 8.5"),
    # hallucination KEPT when the score is high
    ("hallucination_kept", '        keep, tier = False, "hallucination"',
     '        keep, tier = s >= charter.q_setpoint, "hallucination"'),
    # re-emission graded as a fix
    ("reemit_kept", '        keep, tier = False, "re-emission without a fix"',
     '        keep, tier = True, "re-emission without a fix"'),
    # clustering detector disabled
    ("clustering_blind", "    clustered = bool(enough and (spread < charter.min_spread",
     "    clustered = bool(False and (spread < charter.min_spread"),
    # second judge from the same family accepted
    ("same_family_ok", "    if refuse_same_family and fam_a and fam_a == fam_b:",
     "    if False:"),
    # provenance gate dropped from the write path
    ("no_provenance_gate", "    if missing:", "    if False:"),
    # unusable output counted as usable
    ("unusable_counted",
     '    return (c.get("gate") or "").upper() not in UNUSABLE_GATES',
     "    return True"),
    # malformed output counted as well-formed
    ("format_blind", "    return gate not in MALFORMED_GATES", "    return True"),
    # free seats given an invented Q-per-dollar
    ("free_seat_infinite",
     '            "q_per_usd": (None if mean_q is None or not usd\n'
     '                          else round(mean_q / usd, 4)),',
     '            "q_per_usd": (None if mean_q is None\n'
     '                          else round(mean_q / (usd or 1e-9), 4)),'),
    # blend stops renormalizing, so a missing bench drags Q down
    ("blend_no_renorm",
     "    norm = {k: round(v / total_w, 6) for k, v in weights.items()}",
     "    norm = dict(weights)"),
]


@pytest.mark.parametrize("name,old,new", MUTATIONS,
                         ids=[m[0] for m in MUTATIONS])
def test_selftest_fails_on_mutated_code(name, old, new):
    mod = _mutated(old, new, name)
    assert mod._selftest(quiet=True) == 1, (
        f"mutation {name} survived the selftest - the selftest is decorative")


if __name__ == "__main__":
    raise SystemExit(g._selftest())
