#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tensor_math: estimators, honesty law, seating, and mutation controls.

The mutation controls are the negative control: each one edits ONE line of
the module and asserts the module's own selftest goes red. A selftest that
still passes on mutated code is not measuring anything.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import pytest  # noqa: E402

from builds.tensor import tensor_math as tm  # noqa: E402

SRC = Path(tm.__file__)
A, B, C = "seat/ling", "seat/luna", "seat/glm"


def _mutated(old: str, new: str, name: str):
    """Load tensor_math with one line changed, in its own module namespace."""
    src = SRC.read_text(encoding="utf-8")
    assert src.count(old) >= 1, f"mutation target vanished: {old!r}"
    mod_name = f"builds.tensor._mut_{name}"
    mod = types.ModuleType(mod_name)
    mod.__file__ = str(SRC)
    mod.__package__ = "builds.tensor"
    sys.modules[mod_name] = mod          # dataclasses resolves via sys.modules
    try:
        exec(compile(src.replace(old, new, 1), str(SRC), "exec"), mod.__dict__)
    finally:
        sys.modules.pop(mod_name, None)
    return mod


def _obs(**kw):
    kw.setdefault("disagree", True)
    kw.setdefault("domain", "core")
    return tm.observation(kw.pop("a", A), kw.pop("b", B), **kw)


def _cell(observations, axes=("domain",)):
    cells = tm.fold(observations, axes=axes)
    assert len(cells) == 1
    return list(cells.values())[0]


# ------------------------------------------------------------ selftest gate
def test_selftest_is_green():
    assert tm._selftest(quiet=True) == 0


# ------------------------------------------------------------- honesty law
def test_empty_is_unmeasured_not_zero():
    snap = tm.snapshot([])
    assert snap["kind"] == tm.UNMEASURED
    assert snap["n_obs"] == 0 and snap["n_pairs"] == 0
    assert snap["complement_kind"] == tm.UNMEASURED
    assert snap["tensors"] == {}


def test_freq_measured_but_mag_unmeasured_without_a_hole_score():
    cell = _cell([_obs(), _obs(disagree=False)])
    assert cell["freq"] == 0.5
    assert cell["mean_err"] is None and cell["mag"] is None
    assert cell["kind"] == tm.UNMEASURED
    assert cell["complement_kind"] == tm.UNMEASURED


def test_unseen_pair_is_unmeasured_and_never_zero_filled():
    cell = tm.unmeasured_cell(A, C, domain="core")
    assert cell["kind"] == tm.UNMEASURED
    assert cell["freq"] is None and cell["mag"] is None
    assert cell["cofail"] is None and cell["complement"] is None


@pytest.mark.parametrize("bad", [0, 0.5, 10.5, 11])
def test_hole_size_outside_1_10_is_refused(bad):
    with pytest.raises(tm.TensorError) as e:
        _obs(err=bad)
    assert e.value.kind == "BAD_INPUT"


def test_rotator_and_same_model_pairs_refused():
    for args in ((A, A), ("openrouter/free", A)):
        with pytest.raises(tm.TensorError) as e:
            tm.pair_key(*args)
        assert e.value.kind == "REFUSED"


# -------------------------------------------------------------- estimators
def test_mag_is_freq_times_mean_err():
    cell = _cell([_obs(err=8), _obs(disagree=False, err=4)])
    assert (cell["freq"], cell["mean_err"], cell["mag"]) == (0.5, 6.0, 3.0)
    assert cell["mag"] == tm.mag(cell["freq"], cell["mean_err"])


def test_who_erred_splits_xor_cofail_and_rescue():
    cell = _cell([_obs(err=6, who_erred="a"), _obs(err=6, who_erred="b"),
                  _obs(err=6, who_erred="both"), _obs(err=6, who_erred="none")])
    assert cell["scored_n"] == 4
    assert cell["xor_err"] == 0.5 and cell["cofail"] == 0.25
    assert cell["style_fight"] == 0.25
    # lo=seat/glm? no: lo/hi sort case-insensitively on the full pin.
    assert cell["pair_lo"] == "seat/ling" and cell["pair_hi"] == "seat/luna"
    # each side wrong once alone plus once together -> rescue 1/2 both ways
    assert cell["rescue_hi_given_lo"] == 0.5
    assert cell["rescue_lo_given_hi"] == 0.5
    assert cell["complement"] == 0.5


def test_rescue_is_directed():
    cell = _cell([_obs(err=8, who_erred="a") for _ in range(3)])
    assert cell["rescue_hi_given_lo"] == 1.0
    assert cell["rescue_lo_given_hi"] is None


def test_style_fight_is_not_orthogonality():
    """Every trial disagrees, nobody is wrong: freq 1.0, orthogonality 0."""
    cell = _cell([_obs(who_erred="none") for _ in range(4)])
    assert cell["freq"] == 1.0 and cell["style_fight"] == 1.0
    assert cell["xor_err"] == 0.0 and cell["cofail"] == 0.0
    assert cell["orth_sketch"] == 0.0
    assert cell["mag"] is None


def test_unsigned_mag_is_not_orthogonality():
    """Same |v|, opposite sign of complement."""
    rescued = _cell([_obs(err=8, who_erred="a") for _ in range(4)])
    cofailed = _cell([_obs(err=8, who_erred="both") for _ in range(4)])
    assert rescued["mag"] == cofailed["mag"] == 8.0
    assert rescued["orth_sketch"] == 8.0
    assert cofailed["orth_sketch"] == -8.0
    assert rescued["complement"] == 1.0 and cofailed["complement"] == -1.0


def test_orth_sketch_unmeasured_when_weight_missing_but_signal_exists():
    cell = _cell([_obs(who_erred="a"), _obs(who_erred="none")])
    assert cell["xor_err"] == 0.5 and cell["cofail"] == 0.0
    assert cell["mean_err"] is None
    assert cell["orth_sketch"] is None      # non-zero signal, unknown weight


# --------------------------------------------------------- axes and folds
def test_judge_scaffold_provider_are_axes_not_metadata():
    obs = [_obs(err=9, who_erred="a", judge="kelly", scaffold="L1",
                provider="novita"),
           _obs(err=2, who_erred="none", judge="gitur", scaffold="L2",
                provider="groq")]
    full = tm.fold(obs, axes=tm.AXES)
    marginal = tm.fold(obs, axes=("domain",))
    assert len(full) == 2 and len(marginal) == 1
    assert list(marginal.values())[0]["n"] == 2
    assert list(marginal.values())[0]["judge"] == tm.ALL
    assert {c["provider"] for c in full.values()} == {"novita", "groq"}


def test_unknown_axis_name_is_refused():
    with pytest.raises(tm.TensorError) as e:
        tm.fold([_obs()], axes=("vendor",))
    assert e.value.kind == "BAD_INPUT"


def test_porosity_vector_is_per_model_and_needs_who_erred():
    assert tm.porosity([_obs(err=8)]) == {}
    p = tm.porosity([_obs(err=8, who_erred="a") for _ in range(4)])
    assert p[A]["core"]["wrong_rate"] == 1.0
    assert p[A]["core"]["mean_err"] == 8.0
    assert p[A]["core"]["mass"] == 8.0 and p[A]["core"]["kind"] == tm.MEASURED
    assert p[B]["core"]["wrong_rate"] == 0.0
    assert p[B]["core"]["mass"] == 0.0


def test_pair_matrix_enumerates_without_inventing():
    rows = tm.pair_matrix([_obs(err=8, who_erred="a")], [A, B, C],
                          domains=["core"])
    assert len(rows) == 3
    measured = [r for r in rows if r["kind"] == tm.MEASURED]
    assert len(measured) == 1
    assert all(r["mag"] is None for r in rows if r["kind"] == tm.UNMEASURED)


def test_directed_tensor_shape():
    snap = tm.snapshot([_obs(err=8, who_erred="a")], agents=[A, B])
    assert snap["tensors_shape"] == "tensors[agent][vs][axis]"
    assert snap["tensors"][A][B]["core"]["mag"] == 8.0
    assert snap["tensors"][B][A]["core"]["rescue"] == 1.0
    assert snap["tensors"][A][B]["core"]["rescue"] is None


# ------------------------------------------------------------------ seating
def test_recommend_team_seats_incumbent_then_complement():
    obs = ([_obs(a=A, b=B, err=8, who_erred="a") for _ in range(4)]
           + [_obs(a=A, b=C, err=8, who_erred="both") for _ in range(4)])
    team = tm.recommend_team(obs, [B, C], 3, incumbent=A)
    assert team["team"] == [A, B, C]
    assert team["steps"][0]["kind"] == "INCUMBENT"
    assert team["steps"][1]["value"] > team["steps"][2]["value"]


def test_recommend_team_sorts_unmeasured_last():
    obs = [_obs(a=A, b=B, err=8, who_erred="a") for _ in range(4)]
    team = tm.recommend_team(obs, [C, B], 3, incumbent=A,
                             scores={C: 9.9, B: 8.0})
    assert team["team"] == [A, B, C]
    last = team["steps"][-1]
    assert last["model"] == C and last["kind"] == tm.UNMEASURED
    assert last["value"] is None and last["n_terms"] == 0


def test_recommend_team_divides_by_cost():
    obs = [_obs(a=A, b=B, err=8, who_erred="a") for _ in range(4)]
    flat = tm.recommend_team(obs, [B], 2, incumbent=A)
    paid = tm.recommend_team(obs, [B], 2, incumbent=A, costs={B: 4.0})
    assert flat["steps"][1]["per"] == "flat"
    assert paid["steps"][1]["per"] == "usd"
    assert paid["steps"][1]["value"] == pytest.approx(
        flat["steps"][1]["value"] / 4.0)


def test_free_seat_is_unbounded_coverage_per_dollar():
    obs = ([_obs(a=A, b=B, err=8, who_erred="a") for _ in range(4)]
           + [_obs(a=A, b=C, err=8, who_erred="a") for _ in range(4)])
    team = tm.recommend_team(obs, [B, C], 3, incumbent=A,
                             costs={B: 0.0, C: 0.5})
    assert team["team"] == [A, B, C]
    assert team["steps"][1]["per"] == "free"
    assert team["steps"][2]["per"] == "usd"
    # the paid seat's per-dollar value is larger, yet the free seat seats first
    assert team["steps"][2]["value"] > team["steps"][1]["value"]


def test_free_seat_that_co_fails_does_not_jump_the_queue():
    obs = ([_obs(a=A, b=B, err=8, who_erred="both") for _ in range(4)]
           + [_obs(a=A, b=C, err=8, who_erred="a") for _ in range(4)])
    team = tm.recommend_team(obs, [B, C], 3, incumbent=A,
                             costs={B: 0.0, C: 1.0})
    assert team["team"] == [A, C, B]


def test_recommend_team_k_must_be_positive():
    with pytest.raises(tm.TensorError):
        tm.recommend_team([], [B], 0)


# ------------------------------------------- negative controls (mutations)
MUTATIONS = [
    # |v| aliased to disagreement frequency
    ("mag_is_freq", "    return _r(f * e)", "    return _r(f)"),
    # orthogonality sign flipped: co-failure would read as complement
    ("orth_sign", "    signed = x - cof", "    signed = x + cof"),
    # zero-fill instead of UNMEASURED
    ("freq_zero_fill", "    if not n:\n        return None",
     "    if not n:\n        return 0.0"),
    ("cofail_zero_fill", "    if not c.scored_n:\n        return None\n"
     "    return _r(c.both_n / c.scored_n)",
     "    return _r(c.both_n / c.scored_n) if c.scored_n else 0.0"),
    # unmeasured pairs promoted to the front of the seating field
    ("unmeasured_first", '            r["kind"] != MEASURED,\n',
     '            r["kind"] == MEASURED,\n'),
    # the free-seat limit dropped: a paid seat outranks a free rescuer
    ("free_tier_ignored",
     '            0 if (r["per"] == "free" and (r["value"] or 0.0) > 0) else 1,\n',
     "            0,\n"),
    # rescue no longer directed
    ("rescue_undirected",
     "    rescued = c.only_hi_n if side == \"lo\" else c.only_lo_n",
     "    rescued = c.only_hi_n + c.only_lo_n"),
    # hole size range check dropped
    ("err_range", "    if e is not None and not (ERR_LO <= e <= ERR_HI):",
     "    if False:"),
]


@pytest.mark.parametrize("name,old,new", MUTATIONS,
                         ids=[m[0] for m in MUTATIONS])
def test_selftest_fails_on_mutated_code(name, old, new):
    mod = _mutated(old, new, name)
    assert mod._selftest(quiet=True) == 1, (
        f"mutation {name} survived the selftest - the selftest is decorative")


if __name__ == "__main__":
    raise SystemExit(tm._selftest())
