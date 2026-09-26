#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_porosity — porosity (hole size + distribution) and pair orthogonality.

Porosity (Keith): how big the holes are, and how they are distributed
across named axes. Per-model. Not a pair.

Orthogonality (Keith): of a pair, different × accurate. High = they catch
different errors well. Low = they catch (and miss) the same errors.
Working sketch when who_erred is scored: signed complement
(xor_err − cofail) × error_magnitude. Not disagreement frequency alone.
PRELIMINARY method (Keith 2026-09-10). Math still open. Do not invent scores.
Interaction tensor slot stays UNMEASURED. JUDGE pack on every row so a
different judge can re-score the same prompt+outputs.

Pair mag = disagreement_frequency × error_magnitude is hole-size of the
pair, not orthogonality. Tensor grid T[i,j,a] seats models for token
efficiency and error discovery.

JSONL is the observation log (authority for this measurement). SQLite is
a rebuildable projection, never authority. GET never mkdir. GET never
invents a score. UNMEASURED until observed. Rotators refused.

    py -3.14 cosmos\\cosmos_porosity.py --selftest
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-porosity-tensor/5"
_OBS_LOCK = threading.Lock()
COMPARE_SCHEMA = "cosmos-porosity-compare/1"
# Six surface axes (now). Docs: docs/arch/POROSITY_SURFACE.md
SURFACE_AXES = (
    "coding", "agentic", "intelligence", "math", "instruction", "knowledge",
)
# Extra objective meters (not the six). Docs: POROSITY_SURFACE.md
# brevity = size (tokens_out / +LOC). brittleness/robustness = coding bits.
EXTRA_METERS = ("brevity", "brittleness", "robustness")
# Slots we cannot count yet. Display 1 on 0-1 quality scale until measured.
# 1 = identity (does not change a product). 0 = measured miss. Never write 1 to obs.jsonl.
PENDING_AXES = (
    "stability", "file", "office", "long_context", "multilingual",
    "security", "multimodal", "law",
)
NEUTRAL_UNMEASURED = 1.0


def normalize_quality(raw, *, measured: bool) -> float:
    """Fixed 0-1. Unmeasured → 1. Measured miss → 0. Not catalog min-max."""
    if not measured:
        return NEUTRAL_UNMEASURED
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return NEUTRAL_UNMEASURED
    if v > 1.0:
        v = v / 100.0
    if v < 0.0:
        v = 0.0
    if v > 1.0:
        v = 1.0
    return round(v, 6)
OBS_NAME = "obs.jsonl"
DB_NAME = "porosity.sqlite"
JUDGE_TEXT_CAP = 8000
ROTATING = frozenset({
    "openrouter/free", "openrouter/auto", "openrouter/free:free",
    "openrouter/pareto-code",
})
PROFILE_AXES = {
    "forge": ("coding", "spec", "security", "tests", "tool_use"),
    "crucible": ("law", "facts", "procedure"),
    "diligence": ("bull", "bear", "risk"),
    "differentiator": ("diagnosis", "plan"),
    "docket": ("novelty", "enablement", "prior_art"),
    "website": ("copy", "layout", "a11y"),
}
DEFAULT_AXES = ("task",)
WHO_OK = frozenset({"", "a", "b", "both", "none", "unknown"})
FAIL_OK = frozenset({"", "429", "timeout", "refuse", "empty-text", "fail"})
_TRUE = frozenset({"1", "true", "yes", "y", "on", "t"})
_FALSE = frozenset({"", "0", "false", "no", "n", "off", "f"})


def _full_sha256(value) -> str | None:
    if value is None:
        return None
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _judge_text(value) -> str:
    return str(value or "")[:JUDGE_TEXT_CAP]


def _fail_kind(value) -> str:
    kind = str(value or "").strip().lower()
    if kind not in FAIL_OK:
        raise PorosityError(
            "BAD_INPUT",
            f"fail_kind must be one of {sorted(FAIL_OK)}, got {value!r}",
        )
    return kind
SRC_OK = frozenset({"local", "federation"})


class PorosityError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _f(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _flag(v, name: str) -> bool:
    """Strict parse of a caller flag (write side): "false" is False, not True."""
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)) and v == v and v != float("inf") and v != float("-inf"):
        return v != 0
    s = str(v if v is not None else "").strip().lower()
    if s in _TRUE:
        return True
    if s in _FALSE:
        return False
    raise PorosityError("BAD_INPUT", f"{name} must be a boolean, got {v!r}")


def _axes_list(axes, profile) -> list[str]:
    """Axes as a list. A str is comma-split, never iterated by character."""
    if isinstance(axes, str):
        axes = axes.split(",")
    out = [str(a).strip().lower() for a in (axes or axes_for(profile)) if str(a).strip()]
    return out or list(axes_for(profile))


def store_dir(paths) -> Path:
    return paths.role("state", "porosity")


def obs_path(paths) -> Path:
    return store_dir(paths) / OBS_NAME


def db_path(paths) -> Path:
    return store_dir(paths) / DB_NAME


def axes_for(profile: str) -> tuple[str, ...]:
    p = str(profile or "").strip().lower()
    return PROFILE_AXES.get(p) or DEFAULT_AXES


def _pin(model) -> str:
    m = str(model or "").strip()
    if not m:
        raise PorosityError("BAD_INPUT", "model is required")
    if m.lower() in ROTATING:
        raise PorosityError("REFUSED", f"rotator id {m!r} is not assignable")
    return m


def _pair(a: str, b: str) -> tuple[str, str]:
    if a == b:
        raise PorosityError("REFUSED", "pair requires two distinct models")
    lo, hi = (a, b) if a.lower() <= b.lower() else (b, a)
    return lo, hi


def _who_cell(model_a: str, model_b: str, who: str, lo: str, hi: str):
    """Map who_erred (relative to model_a/b) onto lo/hi. None = unscored."""
    w = str(who or "").strip().lower()
    if w in ("", "unknown"):
        return None
    if w == "none":
        return "none"
    if w == "both":
        return "both"
    if w == "a":
        erred = model_a
    elif w == "b":
        erred = model_b
    else:
        return None
    if erred == lo:
        return "lo"
    if erred == hi:
        return "hi"
    return None


def _axis(axis, profile: str) -> str:
    a = str(axis or "").strip().lower()
    if not a:
        a = axes_for(profile)[0]
    return a[:80]


def empty_snapshot() -> dict:
    return {
        "schema": SCHEMA,
        "ok": True,
        "kind": "UNMEASURED",
        "n_obs": 0,
        "n_pairs": 0,
        "pairs": [],
        "tensor": {},
        "complement": {},
        "complement_kind": "UNMEASURED",
        "axes": list(DEFAULT_AXES),
        "note": (
            "SQLite projection: each agent_tensor row is the parameter set of "
            "one named pin against one other agent on one axis. "
            "Porosity = hole size + distribution. "
            "Orthogonality = different x accurate (signed xor-cofail when scored). "
            "JSONL is authority. GET never mkdir. Does not invent scores."
        ),
        "tensors": {},
        "tensors_shape": "tensors[agent][vs][axis]",
        "last_obs": {},
    }


def load_obs(paths) -> list[dict]:
    p = obs_path(paths)
    if not p.is_file():
        return []
    out = []
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict) and rec.get("model_a") and rec.get("model_b"):
            out.append(rec)
    return out


def _fold_rows(rows: list[dict]) -> dict[tuple[str, str, str], dict]:
    acc: dict[tuple[str, str, str], dict] = {}
    for o in rows:
        a = str(o.get("model_a") or "")
        b = str(o.get("model_b") or "")
        if not a or not b or a == b:
            continue
        lo, hi = (a, b) if a.lower() <= b.lower() else (b, a)
        axis = str(o.get("axis") or "task")
        key = (lo, hi, axis)
        slot = acc.get(key)
        if slot is None:
            slot = {"n": 0, "disagree_n": 0, "err_sum": 0.0, "err_n": 0,
                    "tokens_sum": 0.0, "tokens_n": 0,
                    "scored_n": 0, "none_n": 0, "both_n": 0,
                    "xor_n": 0, "style_n": 0,
                    "rescue_lo_hi": 0, "rescue_hi_lo": 0}
            acc[key] = slot
        slot["n"] += 1
        disc = o.get("disagree") in (True, 1, "1", "true", "yes")
        if disc:
            slot["disagree_n"] += 1
        em = _f(o.get("error_mag"))
        if em is not None:
            slot["err_sum"] += em
            slot["err_n"] += 1
        for tok in (_f(o.get("tokens_a")), _f(o.get("tokens_b"))):
            if tok is not None:
                slot["tokens_sum"] += tok
                slot["tokens_n"] += 1
        who = str(o.get("who_erred") or "").strip().lower()
        cell = _who_cell(a, b, who, lo, hi)
        if cell is not None:
            slot["scored_n"] += 1
            if cell == "none":
                slot["none_n"] += 1
                if disc:
                    slot["style_n"] += 1
            elif cell == "both":
                slot["both_n"] += 1
            elif cell == "lo":
                slot["xor_n"] += 1
                slot["rescue_lo_hi"] += 1
            elif cell == "hi":
                slot["xor_n"] += 1
                slot["rescue_hi_lo"] += 1
    out = {}
    for key, s in acc.items():
        n = s["n"]
        freq = None if n == 0 else round(s["disagree_n"] / n, 6)
        mean_err = None if s["err_n"] == 0 else round(s["err_sum"] / s["err_n"], 4)
        mag = None if freq is None or mean_err is None else round(freq * mean_err, 6)
        mean_tok = None if s["tokens_n"] == 0 else round(
            s["tokens_sum"] / s["tokens_n"], 2)
        scored = s["scored_n"]
        lo_wrong = s["rescue_lo_hi"] + s["both_n"]
        hi_wrong = s["rescue_hi_lo"] + s["both_n"]
        rescue_hi_given_lo = (
            None if lo_wrong == 0 else round(s["rescue_lo_hi"] / lo_wrong, 6))
        rescue_lo_given_hi = (
            None if hi_wrong == 0 else round(s["rescue_hi_lo"] / hi_wrong, 6))
        cofail = None if scored == 0 else round(s["both_n"] / scored, 6)
        xor_r = None if scored == 0 else round(s["xor_n"] / scored, 6)
        style_r = None if scored == 0 else round(s["style_n"] / scored, 6)
        signed = None
        if xor_r is not None and cofail is not None:
            w = 1.0 if mean_err is None else mean_err
            signed = round((xor_r - cofail) * w, 6)
        ckind = "UNMEASURED" if scored == 0 else "MEASURED"
        out[key] = {
            "model_a": key[0], "model_b": key[1], "axis": key[2],
            "n": n,
            "disagree_n": s["disagree_n"],
            "freq": freq,
            "mean_err": mean_err,
            "mag": mag,
            "orthogonality": signed,
            "mean_tokens": mean_tok,
            "kind": "UNMEASURED" if mag is None else "MEASURED",
            "scored_n": scored,
            "rescue_hi_given_lo": rescue_hi_given_lo,
            "rescue_lo_given_hi": rescue_lo_given_hi,
            "cofail": cofail,
            "xor_err": xor_r,
            "style_fight": style_r,
            "signed": signed,
            "complement_kind": ckind,
        }
    return out


def _covar(o: dict) -> tuple[str, str, str, str, str, str]:
    """Co-variables. Empty is its own bucket — never pooled with another judge."""
    judge = str(o.get("judge") or o.get("authority") or "")[:80]
    return (
        str(o.get("axis") or "task")[:80],
        judge,
        str(o.get("mistake_type") or "")[:80],
        str(o.get("prompt_size") or "")[:40],
        str(o.get("complexity") or "")[:40],
        str(o.get("difficulty") or "")[:40],
    )


def _fold_compare(rows: list[dict]) -> dict[tuple, dict]:
    """Pair comparison that does not pool judges or other co-variables.

    Shared hit = who_erred none (both right). Cofail = both. Xor = exactly one.
    Coverage = 1 − cofail (pair-OR if a picker exists). Orth = (xor − cofail) × mean_err.
    """
    acc: dict[tuple, dict] = {}
    for o in rows:
        a = str(o.get("model_a") or "")
        b = str(o.get("model_b") or "")
        if not a or not b or a == b:
            continue
        lo, hi = (a, b) if a.lower() <= b.lower() else (b, a)
        key = (lo, hi) + _covar(o)
        slot = acc.get(key)
        if slot is None:
            slot = {"n": 0, "disagree_n": 0, "err_sum": 0.0, "err_n": 0,
                    "scored_n": 0, "none_n": 0, "both_n": 0, "xor_n": 0,
                    "style_n": 0, "rescue_lo_hi": 0, "rescue_hi_lo": 0}
            acc[key] = slot
        slot["n"] += 1
        if o.get("disagree") in (True, 1, "1", "true", "yes"):
            slot["disagree_n"] += 1
        em = _f(o.get("error_mag"))
        if em is not None:
            slot["err_sum"] += em
            slot["err_n"] += 1
        cell = _who_cell(a, b, str(o.get("who_erred") or ""), lo, hi)
        if cell is None:
            continue
        slot["scored_n"] += 1
        if cell == "none":
            slot["none_n"] += 1
            if o.get("disagree") in (True, 1, "1", "true", "yes"):
                slot["style_n"] += 1
        elif cell == "both":
            slot["both_n"] += 1
        elif cell == "lo":
            slot["xor_n"] += 1
            slot["rescue_lo_hi"] += 1
        elif cell == "hi":
            slot["xor_n"] += 1
            slot["rescue_hi_lo"] += 1
    out = {}
    for key, s in acc.items():
        n = s["n"]
        scored = s["scored_n"]
        mean_err = None if s["err_n"] == 0 else round(s["err_sum"] / s["err_n"], 4)
        freq = None if n == 0 else round(s["disagree_n"] / n, 6)
        mag = None if freq is None or mean_err is None else round(freq * mean_err, 6)
        shared = None if scored == 0 else round(s["none_n"] / scored, 6)
        cofail = None if scored == 0 else round(s["both_n"] / scored, 6)
        xor_r = None if scored == 0 else round(s["xor_n"] / scored, 6)
        style_r = None if scored == 0 else round(s["style_n"] / scored, 6)
        coverage = None if cofail is None else round(1.0 - cofail, 6)
        orth = None
        if xor_r is not None and cofail is not None:
            w = 1.0 if mean_err is None else mean_err
            orth = round((xor_r - cofail) * w, 6)
        lo_wrong = s["rescue_lo_hi"] + s["both_n"]
        hi_wrong = s["rescue_hi_lo"] + s["both_n"]
        out[key] = {
            "model_a": key[0], "model_b": key[1],
            "axis": key[2], "judge": key[3],
            "mistake_type": key[4], "prompt_size": key[5],
            "complexity": key[6], "difficulty": key[7],
            "n": n, "scored_n": scored,
            "shared_hit": shared, "xor_err": xor_r, "cofail": cofail,
            "style_fight": style_r, "coverage": coverage,
            "freq": freq, "mean_err": mean_err, "mag": mag,
            "orthogonality": orth,
            "rescue_hi_given_lo": (
                None if lo_wrong == 0 else round(s["rescue_lo_hi"] / lo_wrong, 6)),
            "rescue_lo_given_hi": (
                None if hi_wrong == 0 else round(s["rescue_hi_lo"] / hi_wrong, 6)),
            "kind": "UNMEASURED" if scored == 0 else "MEASURED",
            "complement_kind": "UNMEASURED" if scored == 0 else "MEASURED",
        }
    return out


def compare_snapshot(paths, *, judge="", axis="", mistake_type="",
                     prompt_size="", complexity="", difficulty="") -> dict:
    """Comparison cells. Does not pool co-variables. GET never mkdir."""
    rows = load_obs(paths)
    folds = _fold_compare(rows)
    cells = []
    for f in folds.values():
        if judge and f["judge"] != judge:
            continue
        if axis and f["axis"] != axis:
            continue
        if mistake_type and f["mistake_type"] != mistake_type:
            continue
        if prompt_size and f["prompt_size"] != prompt_size:
            continue
        if complexity and f["complexity"] != complexity:
            continue
        if difficulty and f["difficulty"] != difficulty:
            continue
        cells.append(f)
    cells.sort(key=lambda c: (
        -(c["coverage"] if c["coverage"] is not None else -1),
        -(c["orthogonality"] if c["orthogonality"] is not None else -999),
        c["model_a"], c["model_b"],
    ))
    measured = [c for c in cells if c["kind"] == "MEASURED"]
    return {
        "schema": COMPARE_SCHEMA,
        "ok": True,
        "kind": "UNMEASURED" if not measured else "MEASURED",
        "n_obs": len(rows),
        "n_cells": len(cells),
        "n_measured": len(measured),
        "cells": cells,
        "tensors_shape": "compare[i][j][axis][judge][mistake][size][complexity][difficulty]",
        "note": (
            "Shared hit / xor / cofail are the vector comparison. "
            "Judge is an axis. Do not pool co-variables. "
            "Opus T[i,j,a] remains GET /porosity default."
        ),
    }


def _pair_cost(a: str, b: str, costs: dict) -> float | None:
    ca, cb = _f(costs.get(a)), _f(costs.get(b))
    if ca is None or cb is None:
        return None
    return round(ca + cb, 6)


def recommend_call(paths, models, costs=None, *, k=2, judge="", axis="",
                   mistake_type="", prompt_size="", complexity="",
                   difficulty="") -> dict:
    """Which pair / three to call. Coverage first, then orth, then cheap.

    UNMEASURED pairs are skipped, never zero-filled. k=2 pair, k=3 greedy.
    """
    pins = []
    seen = set()
    for raw in models or []:
        m = str(raw or "").strip()
        if not m or m.lower() in ROTATING or m.lower() in seen:
            continue
        seen.add(m.lower())
        pins.append(m)
    costs = costs if isinstance(costs, dict) else {}
    snap = compare_snapshot(
        paths, judge=judge, axis=axis, mistake_type=mistake_type,
        prompt_size=prompt_size, complexity=complexity, difficulty=difficulty,
    )
    by = {}
    for c in snap["cells"]:
        if c["kind"] != "MEASURED" or c.get("coverage") is None:
            continue
        by[(c["model_a"], c["model_b"])] = c
        by[(c["model_b"], c["model_a"])] = c

    def cell(a, b):
        return by.get((a, b))

    want = max(2, min(int(k or 2), len(pins)))
    if want < 2 or len(pins) < 2:
        return {
            "schema": COMPARE_SCHEMA, "kind": "UNMEASURED",
            "k": want, "call": [], "why": "need two named pins",
        }
    ranked = []
    for i in range(len(pins)):
        for j in range(i + 1, len(pins)):
            a, b = pins[i], pins[j]
            f = cell(a, b)
            if not f:
                continue
            ranked.append({
                "a": a, "b": b,
                "coverage": f["coverage"],
                "orthogonality": f["orthogonality"],
                "shared_hit": f["shared_hit"],
                "xor_err": f["xor_err"],
                "cofail": f["cofail"],
                "cost": _pair_cost(a, b, costs),
                "judge": f["judge"], "axis": f["axis"],
            })
    def _pair_key(r):
        cov = r["coverage"] or 0
        orth = r["orthogonality"] if r["orthogonality"] is not None else -999
        cost = r["cost"]
        per = (cov / cost) if (cost is not None and cost > 0) else cov
        return (-per, -orth, -cov, r["a"], r["b"])
    ranked.sort(key=_pair_key)
    if not ranked:
        return {
            "schema": COMPARE_SCHEMA, "kind": "UNMEASURED",
            "k": want, "call": [], "why": "no MEASURED compare cells",
        }
    best = ranked[0]
    call = [best["a"], best["b"]]
    why = (
        f"{best['a']}+{best['b']} coverage={best['coverage']} "
        f"orth={best['orthogonality']} shared_hit={best['shared_hit']}"
    )
    if want >= 3:
        seated = list(call)
        rest = [m for m in pins if m not in seated]
        pick = None
        pick_score = None
        for z in rest:
            fx = cell(z, seated[0])
            fy = cell(z, seated[1])
            if not fx or not fy:
                continue
            cov = ((fx["coverage"] or 0) + (fy["coverage"] or 0)) / 2.0
            orth = ((fx["orthogonality"] or 0) + (fy["orthogonality"] or 0)) / 2.0
            cz = _f(costs.get(z))
            # Hits per dollar: A covers more but costs >> B. Don't call A.
            if cz is not None and cz > 0:
                per = cov / cz
            else:
                per = cov
            score = (per, orth, cov)
            if pick_score is None or score > pick_score:
                pick, pick_score = z, score
        if pick:
            call.append(pick)
            why += f"; +{pick} covers leftover cofail cheaply"
    return {
        "schema": COMPARE_SCHEMA,
        "kind": "MEASURED",
        "k": len(call),
        "call": call,
        "pair": best,
        "why": why,
        "ranked_pairs": ranked[:12],
    }


def compare_pack(paths, models=None, costs=None, **slice_kw) -> dict:
    """Model Rater pack: comparison cells + who to call. Never mkdir."""
    snap = compare_snapshot(paths, **slice_kw)
    agents = []
    seen = set()
    for c in snap["cells"]:
        for m in (c["model_a"], c["model_b"]):
            if m.lower() not in seen:
                seen.add(m.lower())
                agents.append(m)
    if models:
        agents = [str(m).strip() for m in models if str(m).strip()]
    rec = {
        "schema": COMPARE_SCHEMA,
        "kind": snap["kind"],
        "n_obs": snap["n_obs"],
        "n_cells": snap["n_cells"],
        "n_measured": snap["n_measured"],
        "tensors_shape": snap["tensors_shape"],
        "surface_axes": list(SURFACE_AXES),
        "pending_axes": list(PENDING_AXES),
        "unmeasured_fill": NEUTRAL_UNMEASURED,
        "recommend_pair": recommend_call(
            paths, agents, costs, k=2, **slice_kw),
        "recommend_three": recommend_call(
            paths, agents, costs, k=3, **slice_kw),
        "top_pairs": snap["cells"][:8],
    }
    return rec


def record_hit_vectors(paths, hits: dict, *, judge="", axis="coding",
                       profile="forge", error_mag=None, trial_id="hits",
                       mistake_type="", prompt_size="", complexity="",
                       difficulty="", source="local") -> dict:
    """Store one hole-string per model. Each coordinate is a scored trial.

    hits = {model: '++--...'}. '+' right, '-' wrong. Expands to pairwise
    who_erred. Does not invent scores.
    """
    names = [str(m).strip() for m in (hits or {}) if str(m).strip()]
    if len(names) < 2:
        raise PorosityError("BAD_INPUT", "hit vectors need two named models")
    n = len(str(hits[names[0]] or ""))
    if n < 1 or any(len(str(hits[m] or "")) != n for m in names):
        raise PorosityError("BAD_INPUT", "hit strings must be the same length")
    written = 0
    for k in range(n):
        bits = {m: str(hits[m])[k] for m in names}
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                ra, rb = bits[a] == "+", bits[b] == "+"
                if ra and rb:
                    who, disc = "none", False
                elif (not ra) and (not rb):
                    who, disc = "both", False
                elif ra and (not rb):
                    who, disc = "b", True
                else:
                    who, disc = "a", True
                record_pair(
                    paths, a, b, axis=axis, disagree=disc,
                    error_mag=error_mag, profile=profile,
                    trial_id=f"{trial_id}:{k}",
                    who_erred=who, source=source,
                    authority=judge, action="hit-vector",
                    note=f"hole {k}",
                    judge=judge, mistake_type=mistake_type,
                    prompt_size=prompt_size, complexity=complexity,
                    difficulty=difficulty,
                )
                written += 1
    pack = compare_pack(paths)
    pack["n_written"] = written
    pack["n_holes"] = n
    pack["models"] = names
    return pack


def _directed_tensors(folds: dict) -> dict:
    """Each agent -> vs -> axis -> parameter set. Does not invent."""
    tensors: dict = {}
    for f in folds.values():
        lo, hi, axis = f["model_a"], f["model_b"], f["axis"]
        cells = (
            (lo, hi, f.get("rescue_hi_given_lo")),
            (hi, lo, f.get("rescue_lo_given_hi")),
        )
        for agent, vs, rescue in cells:
            params = {
                "n": f["n"],
                "freq": f["freq"],
                "mean_err": f["mean_err"],
                "mag": f["mag"],
                "xor_err": f["xor_err"],
                "cofail": f["cofail"],
                "rescue": rescue,
                "orthogonality": f.get("orthogonality"),
                "kind": f["kind"],
                "complement_kind": f["complement_kind"],
            }
            tensors.setdefault(agent, {}).setdefault(vs, {})[axis] = params
    return tensors


def _rebuild_sqlite(paths, rows: list[dict]) -> None:
    d = store_dir(paths)
    d.mkdir(parents=True, exist_ok=True)
    fp = db_path(paths)
    con = sqlite3.connect(str(fp))
    try:
        con.execute("DROP TABLE IF EXISTS obs")
        con.execute(
            "CREATE TABLE obs ("
            "seq INTEGER PRIMARY KEY AUTOINCREMENT,"
            "at TEXT, trial_id TEXT, profile TEXT, stage TEXT, axis TEXT,"
            "model_a TEXT, model_b TEXT, pair_lo TEXT, pair_hi TEXT,"
            "disagree INTEGER, error_mag REAL, tokens_a REAL, tokens_b REAL,"
            "who_erred TEXT, source TEXT, authority TEXT, action TEXT, note TEXT)"
        )
        con.execute(
            "CREATE INDEX idx_pair_axis ON obs(pair_lo, pair_hi, axis)")
        con.execute("DROP TABLE IF EXISTS pair_fold")
        con.execute(
            "CREATE TABLE pair_fold ("
            "pair_lo TEXT NOT NULL, pair_hi TEXT NOT NULL, axis TEXT NOT NULL,"
            "n INTEGER, disagree_n INTEGER, freq REAL, mean_err REAL, mag REAL,"
            "kind TEXT,"
            "scored_n INTEGER, rescue_hi_given_lo REAL, rescue_lo_given_hi REAL,"
            "cofail REAL, xor_err REAL, style_fight REAL, signed REAL,"
            "orthogonality REAL, complement_kind TEXT,"
            "PRIMARY KEY (pair_lo, pair_hi, axis))"
        )
        con.execute("DROP TABLE IF EXISTS agent_tensor")
        con.execute(
            "CREATE TABLE agent_tensor ("
            "agent TEXT NOT NULL, vs TEXT NOT NULL, axis TEXT NOT NULL,"
            "n INTEGER, freq REAL, mean_err REAL, mag REAL,"
            "xor_err REAL, cofail REAL, rescue REAL, orthogonality REAL,"
            "kind TEXT, complement_kind TEXT,"
            "PRIMARY KEY (agent, vs, axis))"
        )
        for o in rows:
            a = str(o.get("model_a") or "")
            b = str(o.get("model_b") or "")
            if not a or not b:
                continue
            lo, hi = (a, b) if a.lower() <= b.lower() else (b, a)
            em = _f(o.get("error_mag"))
            con.execute(
                "INSERT INTO obs (at, trial_id, profile, stage, axis, "
                "model_a, model_b, pair_lo, pair_hi, disagree, error_mag, "
                "tokens_a, tokens_b, who_erred, source, authority, action, "
                "note) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    o.get("at"), o.get("trial_id"), o.get("profile"),
                    o.get("stage"), o.get("axis"), a, b, lo, hi,
                    1 if o.get("disagree") in (True, 1, "1", "true") else 0,
                    em, _f(o.get("tokens_a")), _f(o.get("tokens_b")),
                    o.get("who_erred") or "", o.get("source") or "local",
                    (o.get("authority") or "")[:80],
                    (o.get("action") or "ballot")[:40],
                    (o.get("note") or "")[:240],
                ),
            )
        folds = _fold_rows(rows)
        for f in folds.values():
            con.execute(
                "INSERT INTO pair_fold (pair_lo, pair_hi, axis, n, disagree_n, "
                "freq, mean_err, mag, kind, scored_n, rescue_hi_given_lo, "
                "rescue_lo_given_hi, cofail, xor_err, style_fight, signed, "
                "orthogonality, complement_kind) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    f["model_a"], f["model_b"], f["axis"], f["n"],
                    f["disagree_n"], f["freq"], f["mean_err"], f["mag"],
                    f["kind"], f["scored_n"], f["rescue_hi_given_lo"],
                    f["rescue_lo_given_hi"], f["cofail"], f["xor_err"],
                    f["style_fight"], f["signed"], f.get("orthogonality"),
                    f["complement_kind"],
                ),
            )
        for agent, vs_map in _directed_tensors(folds).items():
            for vs, axes in vs_map.items():
                for axis, p in axes.items():
                    con.execute(
                        "INSERT INTO agent_tensor (agent, vs, axis, n, freq, "
                        "mean_err, mag, xor_err, cofail, rescue, "
                        "orthogonality, kind, complement_kind) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (
                            agent, vs, axis, p["n"], p["freq"], p["mean_err"],
                            p["mag"], p["xor_err"], p["cofail"], p["rescue"],
                            p["orthogonality"], p["kind"], p["complement_kind"],
                        ),
                    )
        con.commit()
    finally:
        con.close()


def record_pair(paths, model_a, model_b, *, axis="", disagree=True,
                error_mag=None, profile="forge", stage="", trial_id="",
                tokens_a=None, tokens_b=None, who_erred="", source="local",
                authority="", action="", note="",
                judge="", mistake_type="", prompt_size="",
                complexity="", difficulty="") -> dict:
    """Append one pair observation. Does not invent a score."""
    a = _pin(model_a)
    b = _pin(model_b)
    lo, hi = _pair(a, b)
    ax = _axis(axis, profile)
    src = str(source or "local").strip().lower()
    if src not in SRC_OK:
        raise PorosityError("BAD_INPUT", f"unknown source {source!r}")
    who = str(who_erred or "").strip().lower()
    if who not in WHO_OK:
        raise PorosityError("BAD_INPUT", f"unknown who_erred {who_erred!r}")
    em = _f(error_mag)
    if em is not None and (em < 1 or em > 10):
        raise PorosityError("BAD_INPUT", "error_mag must be 1–10 or omitted")
    disc = _flag(disagree, "disagree")
    rec = {
        "schema": SCHEMA,
        "at": _iso(),
        "trial_id": str(trial_id or "")[:120],
        "profile": str(profile or "forge").strip().lower()[:40],
        "stage": str(stage or "").strip().lower()[:40],
        "axis": ax,
        "model_a": a,
        "model_b": b,
        "pair_lo": lo,
        "pair_hi": hi,
        "disagree": disc,
        "error_mag": em,
        "tokens_a": _f(tokens_a),
        "tokens_b": _f(tokens_b),
        "who_erred": who,
        "source": src,
        "authority": str(authority or "")[:80],
        "action": str(action or "ballot")[:40],
        "note": str(note or "")[:240],
        "judge": str(judge or authority or "")[:80],
        "mistake_type": str(mistake_type or "")[:80],
        "prompt_size": str(prompt_size or "")[:40],
        "complexity": str(complexity or "")[:40],
        "difficulty": str(difficulty or "")[:40],
    }
    d = store_dir(paths)
    d.mkdir(parents=True, exist_ok=True)
    line = json.dumps(rec, ensure_ascii=False) + "\n"
    with _OBS_LOCK:
        with obs_path(paths).open("a", encoding="utf-8") as fh:
            fh.write(line)
            fh.flush()
            os.fsync(fh.fileno())
    rows = load_obs(paths)
    _rebuild_sqlite(paths, rows)
    snap = snapshot(paths, profile=rec["profile"])
    snap["last"] = rec
    key = (lo, hi, ax)
    snap["fold"] = _fold_rows(rows).get(key)
    return snap


def hook_trial(paths, runs, *, profile="forge", stage="", axis="",
               trial_id="", error_mag=None, source="local",
               authority="", action="") -> dict:
    """Record every distinct named-model pair in one adversarial trial.

    Irbe stamps (authority source:class, action) ride on each pair row.
    Missing authority stays empty — UNMEASURED as an audit event.
    Agreement is NOT a score: two matching ballots can be the same wrong
    answer, so every hook row is who_erred=unknown. Does not invent none.
    """
    rows = []
    for r in runs or []:
        if not isinstance(r, dict):
            continue
        m = str(r.get("model") or "").strip()
        if not m or m.lower() in ROTATING:
            continue
        rows.append({
            "model": m,
            "ballot": str(r.get("ballot") or ""),
            "tokens": _f(r.get("tokens") if r.get("tokens") is not None
                         else r.get("n_chars")),
        })
    written = []
    skipped = 0
    stamp_action = str(action or "trial")[:40]
    stamp_auth = str(authority or "")[:80]
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            if a["model"] == b["model"]:
                skipped += 1
                continue
            disc = a["ballot"] != b["ballot"]
            snap = record_pair(
                paths, a["model"], b["model"],
                axis=axis, disagree=disc, error_mag=error_mag,
                profile=profile, stage=stage, trial_id=trial_id,
                tokens_a=a["tokens"], tokens_b=b["tokens"],
                who_erred="unknown",
                source=source,
                authority=stamp_auth,
                action=stamp_action,
                note="hook_trial",
            )
            written.append(snap.get("last") or {})
    return {
        "schema": SCHEMA,
        "ok": True,
        "n_runs": len(rows),
        "n_written": len(written),
        "n_skipped_same": skipped,
        "kind": "UNMEASURED" if not written else "OK",
        "profile": str(profile or "forge"),
        "stage": str(stage or ""),
        "axis": _axis(axis, profile),
        "authority": stamp_auth,
        "action": stamp_action,
    }


def hook_returns(paths, returned, *, profile="forge", axis="",
                 authority="", action="round", trial_id="",
                 source="local") -> dict:
    """Pair-fold named returns (critic / coder files) into the tensor.

    `returned` is {name: path}. Ballot is file text. Missing path → empty
    ballot. Does not invent who_erred.
    """
    runs = []
    for name, p in (returned or {}).items():
        body = ""
        if p:
            try:
                body = Path(p).read_text(encoding="utf-8")[:4000]
            except OSError:
                body = ""
        runs.append({
            "model": str(name),
            "ballot": body,
            "tokens": float(len(body)),
        })
    return hook_trial(
        paths, runs, profile=profile, axis=axis,
        trial_id=trial_id, source=source,
        authority=authority, action=action or "round",
    )


def _rescue_of(f: dict, candidate: str, seated: str):
    """P(candidate right | seated wrong). None if that conditional is UNMEASURED."""
    lo, hi = (f.get("model_a"), f.get("model_b"))
    if candidate == hi and seated == lo:
        return f.get("rescue_hi_given_lo")
    if candidate == lo and seated == hi:
        return f.get("rescue_lo_given_hi")
    return None


def recommend(paths, seated, candidates, *, axes=None, costs=None,
              profile="forge", mode="complement") -> list[dict]:
    """Rank candidates by complement (rescue − co-fail) per token, else |v|.

    mode=complement uses signed C[i,j,a] when who_erred was scored.
    Falls back to unsigned mag. UNMEASURED sorts last. Never zero-fills.
    """
    seated = [str(s).strip() for s in (seated or []) if str(s).strip()]
    candidates = [str(c).strip() for c in (candidates or []) if str(c).strip()]
    costs = costs if isinstance(costs, dict) else {}
    want = _axes_list(axes, profile)
    folds = _fold_rows(load_obs(paths))
    use_c = str(mode or "complement").strip().lower() != "mag"
    ranked = []
    for c in candidates:
        if c.lower() in ROTATING:
            continue
        score = 0.0
        n_term = 0
        unmeasured = True
        used = "none"
        for s in seated:
            if not s or s == c:
                continue
            lo, hi = (c, s) if c.lower() <= s.lower() else (s, c)
            for ax in want:
                f = folds.get((lo, hi, ax))
                if not f:
                    continue
                if use_c and f.get("complement_kind") == "MEASURED":
                    rsc = _rescue_of(f, c, s)
                    cf = f.get("cofail")
                    if rsc is None and cf is None:
                        continue
                    w = f.get("mean_err")
                    if w is None:
                        w = 1.0
                    term = ((0.0 if rsc is None else rsc) - (0.0 if cf is None else cf)) * w
                    unmeasured = False
                    score += term
                    n_term += 1
                    used = "complement"
                    continue
                if f.get("mag") is None:
                    continue
                unmeasured = False
                score += float(f["mag"])
                n_term += 1
                if used == "none":
                    used = "mag"
        cost = _f(costs.get(c))
        if cost is not None and cost > 0 and n_term:
            per = score / cost
        else:
            per = score
        ranked.append({
            "model": c,
            "score": round(per, 6),
            "n_terms": n_term,
            "kind": "UNMEASURED" if unmeasured else "MEASURED",
            "via_tensor": used,
            "cost": cost,
        })
    ranked.sort(key=lambda r: (r["kind"] != "MEASURED", -r["score"], r["model"]))
    return ranked


def _agent_pins(agents) -> list[str]:
    seen = set()
    out = []
    for raw in agents or []:
        m = str(raw or "").strip()
        if not m or m.lower() in ROTATING:
            continue
        key = m.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(m)
    return out


def pair_matrix(paths, agents, *, profile="") -> list[dict]:
    """Every unordered pair of named agents × profile axes.

    Observed folds are copied. Never-seen pairs stay UNMEASURED.
    Does not invent freq, mag, or complement. GET never mkdir.
    """
    pins = _agent_pins(agents)
    axes = list(axes_for(profile))
    folds = _fold_rows(load_obs(paths))
    rows = []
    for i in range(len(pins)):
        for j in range(i + 1, len(pins)):
            lo, hi = _pair(pins[i], pins[j])
            for ax in axes:
                f = folds.get((lo, hi, ax))
                if f:
                    rows.append(dict(f))
                    continue
                rows.append({
                    "model_a": lo, "model_b": hi, "axis": ax,
                    "n": 0, "disagree_n": 0, "freq": None,
                    "mean_err": None, "mag": None, "orthogonality": None,
                    "mean_tokens": None, "kind": "UNMEASURED",
                    "scored_n": 0, "rescue_hi_given_lo": None,
                    "rescue_lo_given_hi": None, "cofail": None,
                    "xor_err": None, "style_fight": None, "signed": None,
                    "complement_kind": "UNMEASURED",
                })
    return rows


def coverage(paths, agents, *, profile="", costs=None, incumbent="") -> dict:
    """Greedy seating for error-discovery coverage per token.

    First seat is the incumbent (or first named pin). Each next seat is
    recommend() vs the already-seated set. UNMEASURED sorts last. Never
    invents a bake-off number. Goal: cover residual holes cheaply.
    """
    pins = _agent_pins(agents)
    inc = str(incumbent or "").strip()
    seated = []
    if inc and inc in pins:
        seated = [inc]
    elif pins:
        seated = [pins[0]]
    rest = [p for p in pins if p not in seated]
    steps = []
    while rest:
        ranked = recommend(
            paths, seated, rest, costs=costs, profile=profile, mode="complement")
        if not ranked:
            break
        pick = ranked[0]
        seated.append(pick["model"])
        rest = [p for p in rest if p != pick["model"]]
        steps.append(pick)
    pairs = pair_matrix(paths, pins, profile=profile)
    n_meas = sum(1 for p in pairs if p.get("kind") == "MEASURED")
    return {
        "schema": SCHEMA,
        "ok": True,
        "kind": "MEASURED" if n_meas else "UNMEASURED",
        "goal": (
            "Maximize error-discovery coverage per token. "
            "Porosity = hole size + distribution. "
            "Orthogonality = different x accurate (xor-cofail when scored). "
            "Low orthogonality = same errors and same blinds. "
            "UNMEASURED pairs sort last. Does not invent scores."
        ),
        "agents": pins,
        "order": seated,
        "steps": steps,
        "n_pairs": len(pairs),
        "n_measured": n_meas,
        "pairs": pairs,
        "profile": str(profile or ""),
        "axes": list(axes_for(profile)),
    }


def _last_obs(rows: list[dict]) -> dict:
    if not rows:
        return {}
    last = rows[-1]
    return {
        "at": last.get("at") or "",
        "authority": last.get("authority") or "",
        "action": last.get("action") or "",
        "model_a": last.get("model_a") or "",
        "model_b": last.get("model_b") or "",
    }


def snapshot(paths, *, profile: str = "", agents=None) -> dict:
    """GET fold. Never mkdir. Never invents."""
    rows = load_obs(paths)
    rec = empty_snapshot()
    rec["axes"] = list(axes_for(profile)) if profile else list(DEFAULT_AXES)
    rec["last_obs"] = _last_obs(rows)
    pins = _agent_pins(agents)
    if pins:
        pack = coverage(paths, pins, profile=profile)
        rec.update({
            "kind": pack["kind"],
            "agents": pack["agents"],
            "coverage": pack,
            "pairs": pack["pairs"],
            "n_pairs": pack["n_pairs"],
            "n_obs": len(rows),
            "axes": pack["axes"],
        })
        if rows:
            rec["db"] = "PRESENT" if db_path(paths).is_file() else "NO_HOST"
            rec["tensors"] = _directed_tensors(_fold_rows(rows))
        return rec
    if not rows:
        return rec
    folds = _fold_rows(rows)
    pairs = [folds[k] for k in sorted(folds)]
    tensor: dict[str, dict] = {}
    complement: dict[str, dict] = {}
    for f in pairs:
        pk = "%s|%s" % (f["model_a"], f["model_b"])
        tensor.setdefault(pk, {})[f["axis"]] = {
            "n": f["n"], "freq": f["freq"], "mean_err": f["mean_err"],
            "mag": f["mag"], "kind": f["kind"],
        }
        complement.setdefault(pk, {})[f["axis"]] = {
            "scored_n": f["scored_n"],
            "rescue_hi_given_lo": f["rescue_hi_given_lo"],
            "rescue_lo_given_hi": f["rescue_lo_given_hi"],
            "cofail": f["cofail"],
            "xor_err": f["xor_err"],
            "style_fight": f["style_fight"],
            "signed": f["signed"],
            "kind": f["complement_kind"],
        }
    rec.update({
        "kind": "MEASURED" if any(p["mag"] is not None for p in pairs)
        else "FREQ_ONLY" if pairs else "UNMEASURED",
        "complement_kind": (
            "MEASURED" if any(p["complement_kind"] == "MEASURED" for p in pairs)
            else "UNMEASURED"),
        "n_obs": len(rows),
        "n_pairs": len(pairs),
        "pairs": pairs,
        "tensor": tensor,
        "tensors": _directed_tensors(folds),
        "complement": complement,
        "db": "PRESENT" if db_path(paths).is_file() else "NO_HOST",
    })
    return rec


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

    td = Path(tempfile.mkdtemp(prefix="cosmos_porosity_"))
    root = install(td / "live", tree_id="spike-porosity")
    paths = CosmosPaths(root)

    snap0 = snapshot(paths)
    check("empty store is UNMEASURED and GET does not mkdir",
          lambda: snap0["kind"] == "UNMEASURED" and snap0["n_obs"] == 0
          and snap0["complement_kind"] == "UNMEASURED"
          and snap0["complement"] == {}
          and snap0["schema"] == SCHEMA
          and snap0.get("tensors_shape") == "tensors[agent][vs][axis]"
          and snap0.get("tensors") == {}
          and not store_dir(paths).exists())

    refused = False
    try:
        record_pair(paths, "openrouter/free", "google/gemma-4-26b-a4b-it:free")
    except PorosityError as e:
        refused = e.kind == "REFUSED"
    check("rotator pair REFUSED", lambda: refused)

    same = False
    try:
        record_pair(paths, "google/gemma-4-26b-a4b-it:free",
                    "google/gemma-4-26b-a4b-it:free")
    except PorosityError as e:
        same = e.kind == "REFUSED"
    check("same-model pair REFUSED", lambda: same)

    rec = record_pair(
        paths,
        "google/gemma-4-26b-a4b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        axis="coding", disagree=True, profile="forge", stage="consensus1",
    )
    check("disagree without error_mag leaves mag UNMEASURED; freq measured",
          lambda: rec["fold"]["freq"] == 1.0
          and rec["fold"]["mag"] is None
          and rec["fold"]["kind"] == "UNMEASURED"
          and rec["n_obs"] == 1)

    rec2 = record_pair(
        paths,
        "google/gemma-4-26b-a4b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        axis="coding", disagree=True, error_mag=8,
        profile="forge", stage="consensus1",
    )
    check("mag = disagreement_freq × error_magnitude (1.0 × 8)",
          lambda: rec2["fold"]["mag"] == 8.0
          and rec2["fold"]["orthogonality"] is None
          and rec2["kind"] == "MEASURED")
    check("complement stays UNMEASURED until who_erred is scored",
          lambda: rec2["complement_kind"] == "UNMEASURED"
          and rec2["fold"]["complement_kind"] == "UNMEASURED"
          and rec2["fold"]["signed"] is None)

    rec3 = record_pair(
        paths,
        "google/gemma-4-26b-a4b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        axis="coding", disagree=True, error_mag=8, who_erred="a",
        profile="forge", stage="consensus1",
    )
    # lo=gemma, hi=llama; who=a → lo wrong, hi right → rescue of llama.
    check("who_erred=a folds rescue of hi given lo wrong; xor not cofail",
          lambda: rec3["fold"]["complement_kind"] == "MEASURED"
          and rec3["fold"]["rescue_hi_given_lo"] == 1.0
          and rec3["fold"]["cofail"] == 0.0
          and rec3["fold"]["xor_err"] == 1.0
          and rec3["fold"]["orthogonality"] == rec3["fold"]["signed"]
          and rec3["complement_kind"] == "MEASURED")

    rec4 = record_pair(
        paths,
        "google/gemma-4-26b-a4b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        axis="coding", disagree=True, error_mag=9, who_erred="both",
        profile="forge", stage="consensus1",
    )
    check("who_erred=both raises co-failure and cuts signed complement",
          lambda: rec4["fold"]["cofail"] is not None
          and rec4["fold"]["cofail"] > 0
          and rec4["fold"]["signed"] is not None
          and rec4["fold"]["signed"] < rec3["fold"]["signed"])

    check("sqlite projection exists after POST, not after GET-empty",
          lambda: db_path(paths).is_file())

    def _sqlite_holds_c():
        con = sqlite3.connect(str(db_path(paths)))
        try:
            cols = [r[1] for r in con.execute("PRAGMA table_info(pair_fold)")]
            n = list(con.execute("SELECT COUNT(*) FROM pair_fold"))[0][0]
            kinds = [r[0] for r in con.execute(
                "SELECT complement_kind FROM pair_fold")]
            n_t = list(con.execute("SELECT COUNT(*) FROM agent_tensor"))[0][0]
            tcols = [r[1] for r in con.execute("PRAGMA table_info(agent_tensor)")]
            return (
                "signed" in cols and "xor_err" in cols and "cofail" in cols
                and "mag" in cols and n >= 1
                and "MEASURED" in kinds
                and "agent" in tcols and "vs" in tcols and "rescue" in tcols
                and n_t == 2
            )
        finally:
            con.close()

    check("sqlite pair_fold + agent_tensor (each agent vs the other) in one dbase",
          _sqlite_holds_c)

    hook = hook_trial(
        paths,
        [
            {"model": "google/gemma-4-31b-it:free", "ballot": "A"},
            {"model": "qwen/qwen3-32b:free", "ballot": "B"},
            {"model": "openrouter/auto", "ballot": "C"},
        ],
        profile="forge", stage="research", axis="spec", error_mag=5,
        authority="crew:forge", action="facilitate",
    )
    check("hook_trial writes distinct pairs and skips rotator",
          lambda: hook["n_written"] == 1 and hook["n_runs"] == 2)
    check("hook_trial stamps Irbe authority source:class and action onto obs",
          lambda: hook.get("authority") == "crew:forge"
          and hook.get("action") == "facilitate"
          and any(o.get("authority") == "crew:forge"
                  and o.get("action") == "facilitate"
                  for o in load_obs(paths)))

    ranked = recommend(
        paths,
        seated=["google/gemma-4-26b-a4b-it:free"],
        candidates=[
            "meta-llama/llama-3.3-70b-instruct:free",
            "some/unseen-model",
        ],
        axes=["coding"],
        costs={"meta-llama/llama-3.3-70b-instruct:free": 1.0},
        profile="forge",
    )
    check("recommend ranks measured pair first; unseen stays UNMEASURED",
          lambda: ranked[0]["model"].startswith("meta-llama")
          and ranked[0]["kind"] == "MEASURED"
          and ranked[-1]["kind"] == "UNMEASURED")
    ranked_c = recommend(
        paths,
        seated=["google/gemma-4-26b-a4b-it:free"],
        candidates=["meta-llama/llama-3.3-70b-instruct:free"],
        axes=["coding"],
        costs={"meta-llama/llama-3.3-70b-instruct:free": 1.0},
        profile="forge",
        mode="complement",
    )
    check("recommend complement uses signed rescue−cofail, not unsigned mag alone",
          lambda: ranked_c[0]["via_tensor"] == "complement"
          and ranked_c[0]["kind"] == "MEASURED")

    a = "google/gemma-4-26b-a4b-it:free"
    b = "meta-llama/llama-3.3-70b-instruct:free"
    c = "z-ai/glm-5.3-flash"
    mat = pair_matrix(paths, [a, b, c], profile="forge")
    check("pair_matrix enumerates every agent pair × forge axes; unseen UNMEASURED",
          lambda: len(mat) == 3 * len(axes_for("forge"))
          and any(p["model_a"] == a and p["model_b"] == b
                  and p["axis"] == "coding" and p["kind"] == "MEASURED"
                  for p in mat)
          and any(p["model_b"] == c and p["kind"] == "UNMEASURED"
                  and p["mag"] is None for p in mat))
    cov = coverage(paths, [a, b, c], profile="forge", incumbent=a)
    check("coverage seats incumbent first then recommend; does not invent mag",
          lambda: cov["order"][0] == a
          and set(cov["agents"]) == {a, b, c}
          and cov["n_pairs"] == len(mat)
          and "error-discovery" in cov["goal"])
    snap_a = snapshot(paths, profile="forge", agents=[a, b, c])
    check("GET snapshot with agents returns coverage pack, GET never mkdir",
          lambda: snap_a.get("coverage") and snap_a["coverage"]["order"][0] == a
          and snap_a["n_pairs"] == len(mat))
    check("GET snapshot tensors is tensors[agent][vs][axis]",
          lambda: snap_a.get("tensors_shape") == "tensors[agent][vs][axis]"
          and isinstance(snap_a.get("tensors"), dict)
          and a in snap_a["tensors"]
          and b in snap_a["tensors"][a]
          and "coding" in snap_a["tensors"][a][b]
          and snap_a["tensors"][a][b]["coding"].get("mag") is not None)
    check("GET snapshot last_obs carries Irbe stamps",
          lambda: snap_a.get("last_obs", {}).get("action") == "facilitate"
          and snap_a["last_obs"].get("authority") == "crew:forge")

    ranked_s = recommend(
        paths,
        seated=["google/gemma-4-26b-a4b-it:free"],
        candidates=["meta-llama/llama-3.3-70b-instruct:free"],
        axes="coding",
        costs={"meta-llama/llama-3.3-70b-instruct:free": 1.0},
        profile="forge",
    )
    check('recommend(axes="coding") does not iterate characters',
          lambda: ranked_s and ranked_s[0]["kind"] == "MEASURED"
          and ranked_s[0]["model"].startswith("meta-llama"))

    hook_same = hook_trial(
        paths,
        [
            {"model": "vendor/same-a", "ballot": "WRONG"},
            {"model": "vendor/same-b", "ballot": "WRONG"},
        ],
        profile="forge", axis="coding",
    )
    check("hook_trial matching ballots are who_erred=unknown (do not invent none)",
          lambda: hook_same["n_written"] == 1
          and any(o.get("note") == "hook_trial"
                  and o.get("who_erred") == "unknown"
                  and o.get("disagree") is False
                  and {o.get("model_a"), o.get("model_b")}
                  == {"vendor/same-a", "vendor/same-b"}
                  for o in load_obs(paths)))

    rec_f = record_pair(
        paths, "vendor/fa", "vendor/fb",
        axis="coding", disagree="false", who_erred="unknown",
    )
    bad_bool = False
    try:
        record_pair(paths, "vendor/ba", "vendor/bb", disagree="maybe")
    except PorosityError as e:
        bad_bool = e.kind == "BAD_INPUT"
    check('disagree="false" stores False; garbage is BAD_INPUT',
          lambda: rec_f["last"]["disagree"] is False and bad_bool)

    td2 = Path(tempfile.mkdtemp(prefix="cosmos_porosity_cmp_"))
    root2 = install(td2 / "live", tree_id="spike-compare")
    paths2 = CosmosPaths(root2)
    hits = {
        "cmp/A": "++++++++--",
        "cmp/B": "--++-++---",
        "cmp/C": "---++-++--",
        "cmp/D": "+++-----++",
    }
    costs = {"cmp/A": 1000.0, "cmp/B": 10.0, "cmp/C": 2.0, "cmp/D": 1.0}
    hv = record_hit_vectors(
        paths2, hits, judge="luna", axis="coding", error_mag=5,
        prompt_size="house", complexity="mid", difficulty="hard",
    )
    pair = recommend_call(paths2, list(hits), costs, k=2, judge="luna",
                          axis="coding")
    three = recommend_call(paths2, list(hits), costs, k=3, judge="luna",
                           axis="coding")
    cd = None
    for c in compare_snapshot(paths2, judge="luna", axis="coding")["cells"]:
        if set((c["model_a"], c["model_b"])) == {"cmp/C", "cmp/D"}:
            cd = c
            break
    check("compare does not pool judges; C+D is max orth cheap pair",
          lambda: hv["kind"] == "MEASURED"
          and cd is not None
          and cd["shared_hit"] == 0.0
          and abs(cd["cofail"] - 0.1) < 1e-9
          and abs(cd["coverage"] - 0.9) < 1e-9
          and pair["kind"] == "MEASURED"
          and set(pair["call"]) == {"cmp/C", "cmp/D"})
    check("three-call is B+C+D; expensive A stays on the bench",
          lambda: set(three["call"]) == {"cmp/B", "cmp/C", "cmp/D"}
          and "cmp/A" not in three["call"])
    empty_cmp = compare_pack(paths)
    check("compare_pack on empty-of-vectors store still returns schema",
          lambda: empty_cmp.get("schema") == COMPARE_SCHEMA
          and "recommend_pair" in empty_cmp)
    check("normalize: unmeasured=1, measured miss=0, percent/100, no catalog min-max",
          lambda: normalize_quality(None, measured=False) == 1.0
          and normalize_quality(0, measured=True) == 0.0
          and normalize_quality(80, measured=True) == 0.8
          and normalize_quality(0.4, measured=True) == 0.4)

    td3 = Path(tempfile.mkdtemp(prefix="cosmos_porosity_hv_"))
    root3 = install(td3 / "live", tree_id="spike-hitmag")
    paths3 = CosmosPaths(root3)
    record_hit_vectors(
        paths3,
        {"hv/A": "+-", "hv/B": "-+"},
        judge="luna", axis="coding",
    )
    check("record_hit_vectors default error_mag is omitted not 5",
          lambda: all(o.get("error_mag") is None for o in load_obs(paths3))
          and all(f.get("mag") is None for f in _fold_rows(load_obs(paths3)).values()))

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        line = ("%s %s %s" % (("PASS" if ok else "FAIL"), label, err))
        print(line.encode("ascii", "replace").decode("ascii"))
    print("porosity selftest", "%d/%d" % (len(results) - len(failed), len(results)))
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("usage: py -3.14 cosmos\\cosmos_porosity.py --selftest")
    raise SystemExit(2)
