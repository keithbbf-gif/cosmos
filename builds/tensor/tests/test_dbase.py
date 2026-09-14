#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dbase: authority/projection layering, idempotent ingest, CLI, mutations.

The corpus here is a SYNTHETIC fixture shaped like the real one (model
families x judges x scaffolds). It is not the measured 103-cell corpus and
must never be read as one - it exercises the store, it does not report
anybody's occupancy.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import pytest  # noqa: E402

from builds.tensor import dbase, tensor_math as tm  # noqa: E402

SRC = Path(dbase.__file__)
KELLY = "gemini-3.8-flash (Kelly)"
GITUR = "grok-4.6 (Gitur)"
LUNA_J = "ling-3.0-vl (Luna)"
JUDGES = (KELLY, GITUR, LUNA_J)
SEATS = ("ling", "luna", "glm", "opus")
SCAFFOLDS = ({"seat": "", "preload": "L1", "prefill": True},
             {"seat": "", "preload": "L2", "prefill": True},
             {"seat": "", "preload": "L2", "prefill": False})


def _mutated(old: str, new: str, name: str):
    src = SRC.read_text(encoding="utf-8")
    assert src.count(old) >= 1, f"mutation target vanished: {old!r}"
    mod_name = f"builds.tensor._mut_dbase_{name}"
    mod = types.ModuleType(mod_name)
    mod.__file__ = str(SRC)
    mod.__package__ = "builds.tensor"
    sys.modules[mod_name] = mod
    try:
        exec(compile(src.replace(old, new, 1), str(SRC), "exec"), mod.__dict__)
    finally:
        sys.modules.pop(mod_name, None)
    return mod


def cell(order, seat, judge, *, gate, score, keep, domain="core",
         provider="Novita", scaffold=None, usd=0.0, run_id="fx"):
    sc = dict(scaffold or SCAFFOLDS[0])
    sc["seat"] = seat
    return {
        "schema": dbase.CELL_SCHEMA,
        "t": "2026-09-14T13:00:00-05:00",
        "run_id": run_id,
        "order_id": order,
        "fn": "renderCoreTelemetry",
        "domain": domain,
        "pair": [seat],
        "judge": judge,
        "scaffold": sc,
        "provider": provider,
        "model": f"vendor/{seat}-3.0:free",
        "gate": gate,
        "score": score,
        "keep": keep,
        "why": "synthetic fixture",
        "usd": usd,
        "cache_version": "orc-b234-20260914",
        "rubric_version": "orc-charter-v2-anchored-20260913",
    }


def corpus() -> list[dict]:
    """4 seats x 3 judges x 3 scaffolds, deterministic. Synthetic fixture."""
    rows = []
    for si, scaf in enumerate(SCAFFOLDS):
        for ji, judge in enumerate(JUDGES):
            order = f"fx-{si}{ji}"
            for ki, seat in enumerate(SEATS):
                good = (ki + ji + si) % 3 != 0
                rows.append(cell(
                    order, seat, judge,
                    gate="PATCHED" if good else "REEMIT",
                    score=8.0 + 0.5 * ki if good else 5.0,
                    keep=good, scaffold=scaf,
                    provider="Novita" if ki % 2 else "Groq",
                    domain="core" if si < 2 else "ui"))
    return rows


# ------------------------------------------------------------ selftest gate
def test_selftest_is_green():
    assert dbase._selftest(quiet=True) == 0


# -------------------------------------------------------------- empty store
def test_empty_store_is_unmeasured_and_read_never_mkdir(tmp_path):
    root = tmp_path / "store"
    snap = dbase.read(root)
    assert snap["kind"] == tm.UNMEASURED and snap["n_obs"] == 0
    assert snap["authority"] == "NO_HOST" and snap["db"] == "NO_HOST"
    assert dbase.query(root, agent="ling")["n_cells"] == 0
    assert dbase.pair_observations(root) == []
    assert not root.exists(), "a read invented a host directory"


def test_root_is_required():
    with pytest.raises(dbase.DbaseError) as e:
        dbase.read("")
    assert e.value.kind == "BAD_INPUT"


# ------------------------------------------------------------- cell schema
@pytest.mark.parametrize("rec,kind", [
    ({"schema": "orc-tensor-cell/2", "order_id": "a", "judge": "j",
      "pair": ["x"]}, "BAD_SCHEMA"),
    ({"schema": dbase.CELL_SCHEMA, "judge": "j", "pair": ["x"]}, "BAD_INPUT"),
    ({"schema": dbase.CELL_SCHEMA, "order_id": "a", "pair": ["x"]},
     "BAD_INPUT"),
    ({"schema": dbase.CELL_SCHEMA, "order_id": "a", "judge": "j"},
     "BAD_INPUT"),
    ({"schema": dbase.CELL_SCHEMA, "order_id": "a", "judge": "j",
      "pair": ["x"], "score": 11}, "BAD_INPUT"),
    ({"schema": dbase.CELL_SCHEMA, "order_id": "a", "judge": "j",
      "pair": ["x"], "err": 42}, "BAD_INPUT"),
])
def test_bad_cells_are_refused(rec, kind):
    with pytest.raises(dbase.DbaseError) as e:
        dbase.normalize_cell(rec)
    assert e.value.kind == kind


def test_seat_falls_back_to_the_scaffold_seat():
    c = dbase.normalize_cell({"schema": dbase.CELL_SCHEMA, "order_id": "a",
                              "judge": "j",
                              "scaffold": {"seat": "ling", "preload": "L1"}})
    assert c["seat"] == "ling" and c["pair"] == ["ling"]
    assert c["dedupe_key"] == "a|ling|j"


def test_scaffold_key_is_stable_and_sorted():
    a = dbase.scaffold_key({"preload": "L1", "seat": "ling", "prefill": True})
    b = dbase.scaffold_key({"seat": "ling", "prefill": True, "preload": "L1"})
    assert a == b == "prefill=true|preload=L1|seat=ling"


# ------------------------------------------------------------------ ingest
def test_ingest_is_idempotent_on_order_seat_judge(tmp_path):
    root = tmp_path / "store"
    rows = corpus()
    first = dbase.ingest(root, rows)
    assert first["n_new"] == len(rows) and first["n_dupe"] == 0
    second = dbase.ingest(root, rows)
    assert second["n_new"] == 0 and second["n_dupe"] == len(rows)
    lines = dbase.obs_path(root).read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == len(rows)
    assert dbase.read(root)["n_obs"] == len(rows)


def test_authority_keeps_the_cell_and_stamps_ingestion(tmp_path):
    root = tmp_path / "store"
    dbase.ingest(root, [cell("fx-1", "ling", KELLY, gate="UNCHANGED",
                             score=7.5, keep=True)])
    line = json.loads(dbase.obs_path(root).read_text(encoding="utf-8").strip())
    assert line["gate"] == "UNCHANGED" and line["score"] == 7.5
    assert line["dedupe_key"] == f"fx-1|ling|{KELLY}"
    assert line["ingested_at"]


def test_bad_rows_are_reported_not_swallowed(tmp_path):
    root = tmp_path / "store"
    src = tmp_path / "cells.jsonl"
    src.write_text(
        "{oops}\n"
        + json.dumps({"schema": "nope", "order_id": "a", "judge": "j",
                      "pair": ["x"]}) + "\n"
        + json.dumps(cell("fx-2", "ling", KELLY, gate="PATCHED", score=8.0,
                          keep=True)) + "\n",
        encoding="utf-8")
    rep = dbase.ingest(root, src)
    assert rep["n_bad"] == 2 and rep["n_new"] == 1
    assert {b["kind"] for b in rep["bad"]} == {"BAD_JSON", "BAD_SCHEMA"}


def test_missing_cells_file_is_no_host(tmp_path):
    with pytest.raises(dbase.DbaseError) as e:
        dbase.ingest(tmp_path / "store", tmp_path / "nope.jsonl")
    assert e.value.kind == "NO_HOST"


# ------------------------------------------------------- pair derivation
def test_two_seats_one_order_one_judge_make_one_pair_trial(tmp_path):
    root = tmp_path / "store"
    dbase.ingest(root, [
        cell("fx-3", "ling", KELLY, gate="REEMIT", score=5.0, keep=False),
        cell("fx-3", "luna", KELLY, gate="PATCHED", score=9.0, keep=True),
    ])
    obs = dbase.pair_observations(root)
    assert len(obs) == 1
    o = obs[0]
    assert o["disagree"] is True and o["who_erred"] in ("a", "b")
    assert o["err"] == 5.0 and o["err_source"] == "derived-from-score"
    assert o["judge"] == KELLY and o["domain"] == "core"


def test_both_keep_with_different_gates_is_a_style_fight(tmp_path):
    root = tmp_path / "store"
    dbase.ingest(root, [
        cell("fx-4", "ling", KELLY, gate="UNCHANGED", score=7.5, keep=True),
        cell("fx-4", "luna", KELLY, gate="PATCHED", score=8.5, keep=True),
    ])
    o = dbase.pair_observations(root)[0]
    assert o["disagree"] is True and o["who_erred"] == "none"
    assert o["err"] is None, "a trial with no hole was given a hole size"
    fold = list(tm.fold([o], axes=("domain",)).values())[0]
    assert fold["style_fight"] == 1.0 and fold["orth_sketch"] == 0.0


def test_same_gate_is_not_a_fight(tmp_path):
    root = tmp_path / "store"
    dbase.ingest(root, [
        cell("fx-5", "ling", KELLY, gate="UNCHANGED", score=7.5, keep=True),
        cell("fx-5", "luna", KELLY, gate="UNCHANGED", score=7.5, keep=True),
    ])
    assert dbase.pair_observations(root)[0]["disagree"] is False


def test_single_seat_order_never_fabricates_a_pair(tmp_path):
    root = tmp_path / "store"
    dbase.ingest(root, [cell("fx-6", "glm", KELLY, gate="PATCHED", score=8.0,
                             keep=True)])
    q = dbase.query(root)
    assert q["n_cells"] == 1 and q["n_pair_cells"] == 0
    assert q["kind"] == tm.UNMEASURED


def test_unkept_keep_flag_leaves_who_erred_unknown(tmp_path):
    root = tmp_path / "store"
    dbase.ingest(root, [
        dict(cell("fx-7", "ling", KELLY, gate="PATCHED", score=8.0,
                  keep=True), keep=None),
        cell("fx-7", "luna", KELLY, gate="REEMIT", score=5.0, keep=False),
    ])
    o = dbase.pair_observations(root)[0]
    assert o["who_erred"] == "unknown"
    fold = list(tm.fold([o], axes=("domain",)).values())[0]
    assert fold["complement_kind"] == tm.UNMEASURED
    assert fold["cofail"] is None


def test_mixed_scaffold_or_provider_folds_to_mixed(tmp_path):
    root = tmp_path / "store"
    dbase.ingest(root, [
        cell("fx-8", "ling", KELLY, gate="PATCHED", score=8.0, keep=True,
             provider="Novita", scaffold=SCAFFOLDS[0]),
        cell("fx-8", "luna", KELLY, gate="PATCHED", score=8.0, keep=True,
             provider="Groq", scaffold=SCAFFOLDS[1]),
    ])
    o = dbase.pair_observations(root)[0]
    assert o["provider"] == dbase.MIXED and o["scaffold"] == dbase.MIXED


# ---------------------------------------------------------- the projection
def test_projection_tables_and_rebuild_from_authority(tmp_path):
    root = tmp_path / "store"
    rows = corpus()
    dbase.ingest(root, rows)

    def sql(q):
        con = sqlite3.connect(str(dbase.db_path(root)))
        try:
            return list(con.execute(q))
        finally:
            con.close()

    assert sql("SELECT COUNT(*) FROM obs")[0][0] == len(rows)
    assert sql("SELECT COUNT(*) FROM pair_fold")[0][0] > 0
    assert sql("SELECT COUNT(*) FROM agent_tensor")[0][0] > 0
    before = (sql("SELECT COUNT(*) FROM obs"),
              sql("SELECT COUNT(*) FROM pair_fold"),
              sql("SELECT COUNT(*) FROM agent_tensor"))

    dbase.db_path(root).unlink()
    rep = dbase.rebuild(root)
    assert rep["n_cells"] == len(rows)
    after = (sql("SELECT COUNT(*) FROM obs"),
             sql("SELECT COUNT(*) FROM pair_fold"),
             sql("SELECT COUNT(*) FROM agent_tensor"))
    assert before == after, "the projection is not rebuildable from authority"


def test_projection_holds_both_full_and_domain_marginal_cells(tmp_path):
    root = tmp_path / "store"
    dbase.ingest(root, corpus())
    con = sqlite3.connect(str(dbase.db_path(root)))
    try:
        marg = list(con.execute(
            "SELECT COUNT(*) FROM pair_fold WHERE judge = ?", (tm.ALL,)))[0][0]
        full = list(con.execute(
            "SELECT COUNT(*) FROM pair_fold WHERE judge != ?", (tm.ALL,)))[0][0]
    finally:
        con.close()
    assert marg > 0 and full > marg


def test_judge_axis_does_not_collapse(tmp_path):
    root = tmp_path / "store"
    for judge in (KELLY, GITUR):
        dbase.ingest(root, [
            cell("fx-9", "ling", judge, gate="REEMIT", score=5.0, keep=False),
            cell("fx-9", "luna", judge, gate="PATCHED", score=8.0, keep=True),
        ])
    q = dbase.query(root, agent="ling", vs="luna", axis="core")
    assert {f["judge"] for f in q["pair_cells"]} == {KELLY, GITUR}
    marginal = q["pair_cells_domain"]
    assert len(marginal) == 1 and marginal[0]["n"] == 2
    assert marginal[0]["judge"] == tm.ALL


def test_read_exposes_the_directed_tensor(tmp_path):
    root = tmp_path / "store"
    dbase.ingest(root, [
        cell("fx-10", "ling", KELLY, gate="REEMIT", score=5.0, keep=False),
        cell("fx-10", "luna", KELLY, gate="PATCHED", score=9.0, keep=True),
    ])
    snap = dbase.read(root)
    assert snap["schema"] == dbase.SCHEMA
    assert snap["tensors_shape"] == "tensors[agent][vs][axis]"
    assert snap["tensors"]["luna"]["ling"]["core"]["rescue"] == 1.0
    assert snap["tensors"]["ling"]["luna"]["core"]["rescue"] is None
    assert snap["porosity"]["ling"]["core"]["mass"] == 5.0


def test_query_filters(tmp_path):
    root = tmp_path / "store"
    dbase.ingest(root, corpus())
    all_cells = dbase.query(root)["n_cells"]
    ui = dbase.query(root, domain="ui")
    kelly = dbase.query(root, judge=KELLY)
    seat = dbase.query(root, seat="opus")
    assert 0 < ui["n_cells"] < all_cells
    assert all(c["domain"] == "ui" for c in ui["cells"])
    assert all(c["judge"] == KELLY for c in kelly["cells"])
    assert all(c["seat"] == "opus" for c in seat["cells"])
    assert dbase.query(root, limit=3)["n_cells"] == 3


# --------------------------------------------------------------------- CLI
def _cli(*args):
    return subprocess.run([sys.executable, "-m", "builds.tensor.dbase", *args],
                          cwd=str(REPO), capture_output=True, text=True)


def test_cli_ingest_rebuild_query_roundtrip(tmp_path):
    root = tmp_path / "store"
    src = tmp_path / "cells.jsonl"
    src.write_text("\n".join(json.dumps(c) for c in corpus()) + "\n",
                   encoding="utf-8")

    out = _cli("ingest", str(src), "--root", str(root))
    assert out.returncode == 0, out.stderr
    rep = json.loads(out.stdout)
    assert rep["n_new"] == len(corpus()) and rep["n_bad"] == 0

    again = json.loads(_cli("ingest", str(src), "--root", str(root)).stdout)
    assert again["n_new"] == 0 and again["n_dupe"] == len(corpus())

    reb = json.loads(_cli("rebuild", "--root", str(root)).stdout)
    assert reb["ok"] and reb["n_cells"] == len(corpus())

    q = json.loads(_cli("query", "--root", str(root), "--judge", KELLY).stdout)
    assert q["n_cells"] > 0 and all(c["judge"] == KELLY for c in q["cells"])

    snap = json.loads(_cli("query", "--root", str(root), "--snapshot").stdout)
    assert snap["n_obs"] == len(corpus()) and snap["kind"] == tm.MEASURED


def test_cli_selftest_exits_zero():
    out = _cli("selftest")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "FAIL" not in out.stdout


def test_cli_reports_a_refusal_as_json(tmp_path):
    out = _cli("ingest", str(tmp_path / "missing.jsonl"),
               "--root", str(tmp_path / "store"))
    assert out.returncode == 3
    assert json.loads(out.stdout)["kind"] == "NO_HOST"


# ------------------------------------------- negative controls (mutations)
MUTATIONS = [
    # dedupe removed: re-ingest would double the corpus
    ("no_dedupe", '        if cell["dedupe_key"] in seen:',
     "        if False:"),
    # a hole size invented for a trial where nobody was wrong
    ("invent_hole", "    if not any_wrong:\n        return None, \"\"",
     "    if False:\n        return None, \"\""),
    # reads create the store directory
    ("read_mkdir", "def load_cells(root) -> list[dict]:\n    \"\"\"Read the "
     "authority. Missing file is an empty store, never a mkdir.\"\"\"\n"
     "    p = obs_path(root)",
     "def load_cells(root) -> list[dict]:\n    \"\"\"mutated\"\"\"\n"
     "    store_dir(root).mkdir(parents=True, exist_ok=True)\n"
     "    p = obs_path(root)"),
    # schema gate dropped
    ("any_schema", "    if schema != CELL_SCHEMA:", "    if False:"),
    # provenance gate dropped
    ("no_order_id", "    if not order_id:", "    if False:"),
    # the judge axis collapses into one bucket
    ("judge_collapsed",
     '        key = (c["run_id"], c["order_id"], c["fn"], c["domain"], c["judge"])',
     '        key = (c["run_id"], c["order_id"], c["fn"], c["domain"])'),
    # a pair with no ballot at all counted as agreement
    ("unballoted_as_agreement",
     "                if not ba and not bb:\n"
     "                    n_unballoted += 1\n                    continue",
     "                if False:\n"
     "                    n_unballoted += 1\n                    continue"),
]


@pytest.mark.parametrize("name,old,new", MUTATIONS,
                         ids=[m[0] for m in MUTATIONS])
def test_selftest_fails_on_mutated_code(name, old, new):
    mod = _mutated(old, new, name)
    assert mod._selftest(quiet=True) == 1, (
        f"mutation {name} survived the selftest - the selftest is decorative")


if __name__ == "__main__":
    raise SystemExit(dbase._selftest())
