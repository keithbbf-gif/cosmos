#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dbase — the measurement store for the disagreement tensor.

Layers, in canon order (docs/arch/ORTHOGONAL_POROSITY.md):

    obs.jsonl     append-only JSONL   AUTHORITY for this measurement
    tensor.sqlite rebuildable         PROJECTION, never authority
    read()/query()                    read API over the projection's fold

Ingestion takes JSONL rows of schema `orc-tensor-cell/1` - one row per
(order_id, seat, judge) grading cell:

    {"schema":"orc-tensor-cell/1","t":"2026-09-14T13:00:00-05:00",
     "run_id":"b4","order_id":"b4-007","fn":"renderCoreTelemetry",
     "domain":"core","pair":["ling"],"judge":"gemini-3.8-flash (Kelly)",
     "scaffold":{"seat":"ling","preload":"L1","prefill":true},
     "provider":"Novita","model":"inclusionai/ling-3.0-flash-vl:free",
     "gate":"UNCHANGED","score":7.5,"keep":true,"why":"honest no-op",
     "usd":0.0,"cache_version":"orc-b234-20260914",
     "rubric_version":"orc-charter-v2-anchored-20260913"}

Pair observations are DERIVED, not declared: two seats that answered the
same order under the same judge form one pair trial. Ballot = the gate
token, so a pair that agrees on UNCHANGED does not count as a fight.

Laws: ingest is idempotent (dedupe on order_id + seat + judge); the
projection is always rebuildable from the authority; reads NEVER mkdir and
never invent a host; an empty store reads kind=UNMEASURED, n_obs=0.

    python -m builds.tensor.dbase ingest cells.jsonl --root DIR
    python -m builds.tensor.dbase rebuild --root DIR
    python -m builds.tensor.dbase query --root DIR [--agent A --vs B ...]
    python -m builds.tensor.dbase selftest
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

try:  # package run: python -m builds.tensor.dbase
    from . import tensor_math as tm
except ImportError:  # direct run: python builds/tensor/dbase.py
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import tensor_math as tm  # type: ignore

SCHEMA = "cosmos-porosity-tensor/5"
CELL_SCHEMA = "orc-tensor-cell/1"
OBS_NAME = "obs.jsonl"
DB_NAME = "tensor.sqlite"
MIXED = "MIXED"
TEXT_CAP = 400
UNMEASURED = tm.UNMEASURED
MEASURED = tm.MEASURED


class DbaseError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _txt(v, cap: int = TEXT_CAP) -> str:
    return str(v if v is not None else "").strip()[:cap]


def _num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _bool(v):
    if isinstance(v, bool):
        return v
    if v in (1, "1", "true", "True", "yes"):
        return True
    if v in (0, "0", "false", "False", "no"):
        return False
    return None


# ------------------------------------------------------------------- paths
def store_dir(root) -> Path:
    """The store directory. Resolving is not creating - callers mkdir."""
    r = _txt(root, 4096)
    if not r:
        raise DbaseError("BAD_INPUT", "root is required; no hard-coded paths")
    return Path(r).expanduser()


def obs_path(root) -> Path:
    return store_dir(root) / OBS_NAME


def db_path(root) -> Path:
    return store_dir(root) / DB_NAME


# -------------------------------------------------------------------- cells
def scaffold_key(scaffold) -> str:
    """Canonical, stable scaffold axis value. dict -> sorted k=v join."""
    if isinstance(scaffold, dict):
        parts = []
        for k in sorted(scaffold):
            v = scaffold[k]
            if isinstance(v, bool):
                v = "true" if v else "false"
            parts.append(f"{k}={_txt(v, 60)}")
        return "|".join(parts)[:200] or tm.ALL
    return _txt(scaffold, 200) or tm.ALL


def normalize_cell(rec) -> dict:
    """Validate one orc-tensor-cell/1 row. Fail-closed on schema and keys."""
    if not isinstance(rec, dict):
        raise DbaseError("BAD_INPUT", f"cell must be an object: {rec!r}")
    schema = _txt(rec.get("schema"))
    if schema != CELL_SCHEMA:
        raise DbaseError("BAD_SCHEMA",
                         f"expected {CELL_SCHEMA}, got {schema!r}")
    order_id = _txt(rec.get("order_id"), 120)
    if not order_id:
        raise DbaseError("BAD_INPUT", "order_id is required (provenance)")
    judge = _txt(rec.get("judge"), 120)
    if not judge:
        raise DbaseError("BAD_INPUT", "judge is required (judge is an axis)")
    raw_pair = rec.get("pair")
    if isinstance(raw_pair, str):
        raw_pair = [raw_pair]
    seats = [_txt(s, 80) for s in (raw_pair or []) if _txt(s, 80)]
    scaffold = rec.get("scaffold")
    if not seats:
        seat_hint = scaffold.get("seat") if isinstance(scaffold, dict) else ""
        seats = [_txt(seat_hint, 80)] if _txt(seat_hint, 80) else []
    if not seats:
        raise DbaseError("BAD_INPUT", "pair/seat is required (who was graded)")
    seat = "+".join(sorted(seats))
    score = _num(rec.get("score"))
    if score is not None and not (0.0 <= score <= 10.0):
        raise DbaseError("BAD_INPUT", f"score out of 0-10: {score}")
    err = _num(rec.get("err", rec.get("hole")))
    if err is not None and not (tm.ERR_LO <= err <= tm.ERR_HI):
        raise DbaseError("BAD_INPUT", f"err (hole size) out of 1-10: {err}")
    return {
        "schema": CELL_SCHEMA,
        "t": _txt(rec.get("t"), 60),
        "run_id": _txt(rec.get("run_id"), 80),
        "order_id": order_id,
        "fn": _txt(rec.get("fn"), 160),
        "domain": _txt(rec.get("domain"), 80) or tm.ALL,
        "pair": seats,
        "seat": seat,
        "n_seats": len(seats),
        "judge": judge,
        "scaffold": scaffold_key(scaffold),
        "provider": _txt(rec.get("provider"), 80) or tm.ALL,
        "model": _txt(rec.get("model"), 160),
        "gate": _txt(rec.get("gate"), 80),
        "score": score,
        "keep": _bool(rec.get("keep")),
        "why": _txt(rec.get("why"), TEXT_CAP),
        "err": err,
        "usd": _num(rec.get("usd")),
        "format_ok": _bool(rec.get("format_ok")),
        "judge_agreement": _bool(rec.get("judge_agreement")),
        "cache_version": _txt(rec.get("cache_version"), 120),
        "rubric_version": _txt(rec.get("rubric_version"), 120),
        "dedupe_key": f"{order_id}|{seat}|{judge}",
    }


def dedupe_key(rec) -> str:
    """order_id + seat + judge. The same cell twice is the same observation."""
    return normalize_cell(rec)["dedupe_key"]


def load_cells(root) -> list[dict]:
    """Read the authority. Missing file is an empty store, never a mkdir."""
    p = obs_path(root)
    if not p.is_file():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            out.append(normalize_cell(rec))
        except (ValueError, DbaseError):
            continue
    return out


def _read_jsonl(source) -> tuple[list[dict], list[dict]]:
    rows, bad = [], []
    if isinstance(source, (str, Path)):
        p = Path(source).expanduser()
        if not p.is_file():
            raise DbaseError("NO_HOST", f"no such cells file: {p}")
        lines = list(enumerate(p.read_text(encoding="utf-8").splitlines(), 1))
        for lineno, line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError as e:
                bad.append({"line": lineno, "kind": "BAD_JSON", "detail": str(e)})
        return rows, bad
    for i, rec in enumerate(source or [], 1):
        if isinstance(rec, str):
            try:
                rows.append(json.loads(rec))
            except ValueError as e:
                bad.append({"line": i, "kind": "BAD_JSON", "detail": str(e)})
            continue
        rows.append(rec)
    return rows, bad


# -------------------------------------------------------- pair derivation
def _ballot(cell: dict) -> str:
    """What this seat said. Empty means it never balloted."""
    if cell["gate"]:
        return cell["gate"].upper()
    if cell["score"] is not None:
        return "SCORE:%.2f" % cell["score"]
    return ""


def _derived_err(a: dict, b: dict, any_wrong: bool):
    explicit = [c["err"] for c in (a, b) if c["err"] is not None]
    if explicit:
        return sum(explicit) / len(explicit), "cell-err"
    if not any_wrong:
        return None, ""          # nobody was wrong: there is no hole to size
    scores = [c["score"] for c in (a, b) if c["score"] is not None]
    if not scores:
        return None, ""
    hole = 10.0 - min(scores)
    hole = min(max(hole, tm.ERR_LO), tm.ERR_HI)
    return hole, "derived-from-score"


def derive_pair_obs(cells) -> dict:
    """Two seats, one order, one judge -> one pair trial.

    Multi-seat (joint) cells are a single graded entity, not a pair, and are
    skipped here. A trial where neither side balloted is skipped, not
    recorded as agreement.
    """
    groups: dict[tuple, list[dict]] = {}
    n_joint = 0
    for c in cells:
        if c["n_seats"] != 1:
            n_joint += 1
            continue
        key = (c["run_id"], c["order_id"], c["fn"], c["domain"], c["judge"])
        groups.setdefault(key, []).append(c)
    obs, n_unballoted = [], 0
    for key in sorted(groups):
        members = sorted(groups[key], key=lambda m: m["seat"].lower())
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                a, b = members[i], members[j]
                if a["seat"] == b["seat"]:
                    continue
                ba, bb = _ballot(a), _ballot(b)
                if not ba and not bb:
                    n_unballoted += 1
                    continue
                a_keep, b_keep = a["keep"], b["keep"]
                if a_keep is None or b_keep is None:
                    who = "unknown"
                elif a_keep and b_keep:
                    who = "none"
                elif not a_keep and not b_keep:
                    who = "both"
                else:
                    who = "a" if not a_keep else "b"
                any_wrong = who in ("a", "b", "both")
                err, src = _derived_err(a, b, any_wrong)
                usd = [c["usd"] for c in (a, b) if c["usd"] is not None]
                obs.append(tm.observation(
                    a["seat"], b["seat"],
                    disagree=(ba != bb),
                    domain=a["domain"],
                    judge=a["judge"],
                    scaffold=(a["scaffold"] if a["scaffold"] == b["scaffold"]
                              else MIXED),
                    provider=(a["provider"] if a["provider"] == b["provider"]
                              else MIXED),
                    err=err, err_source=src, who_erred=who,
                    usd=(sum(usd) if usd else None),
                    trial_id=a["order_id"],
                    note=f"{a['fn']}|{ba}vs{bb}",
                ))
    return {"obs": obs, "n_joint": n_joint, "n_unballoted": n_unballoted}


# ------------------------------------------------------------------ ingest
def ingest(root, source, *, rebuild_projection: bool = True) -> dict:
    """Append new cells to the authority, then rebuild the projection.

    Idempotent: a cell already in the authority (order_id + seat + judge) is
    counted as a duplicate and NOT appended. POST may create the store dir.
    """
    rows, bad = _read_jsonl(source)
    seen = {c["dedupe_key"] for c in load_cells(root)}
    fresh, n_dupe = [], 0
    for i, rec in enumerate(rows, 1):
        try:
            cell = normalize_cell(rec)
        except DbaseError as e:
            bad.append({"line": i, "kind": e.kind, "detail": str(e)})
            continue
        if cell["dedupe_key"] in seen:
            n_dupe += 1
            continue
        seen.add(cell["dedupe_key"])
        fresh.append((rec, cell))
    if fresh:
        d = store_dir(root)
        d.mkdir(parents=True, exist_ok=True)
        stamp = _iso()
        with obs_path(root).open("a", encoding="utf-8") as fh:
            for rec, cell in fresh:
                line = dict(rec)
                line["schema"] = CELL_SCHEMA
                line["ingested_at"] = stamp
                line["dedupe_key"] = cell["dedupe_key"]
                fh.write(json.dumps(line, ensure_ascii=False) + "\n")
    report = {
        "schema": SCHEMA,
        "ok": True,
        "n_read": len(rows),
        "n_new": len(fresh),
        "n_dupe": n_dupe,
        "n_bad": len(bad),
        "bad": bad[:10],
        "n_obs": len(seen),
        "authority": str(obs_path(root)),
        "at": _iso(),
    }
    if rebuild_projection:
        report["rebuild"] = rebuild(root)
    return report


# ------------------------------------------------------------- projection
DDL_OBS = """
CREATE TABLE obs (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  dedupe_key TEXT NOT NULL UNIQUE,
  t TEXT, run_id TEXT, order_id TEXT, fn TEXT, domain TEXT,
  seat TEXT, n_seats INTEGER, judge TEXT, scaffold TEXT, provider TEXT,
  model TEXT, gate TEXT, score REAL, keep INTEGER, err REAL, usd REAL,
  format_ok INTEGER, judge_agreement INTEGER, why TEXT,
  cache_version TEXT, rubric_version TEXT)
"""
DDL_PAIR_FOLD = """
CREATE TABLE pair_fold (
  pair_lo TEXT NOT NULL, pair_hi TEXT NOT NULL,
  domain TEXT NOT NULL, judge TEXT NOT NULL,
  scaffold TEXT NOT NULL, provider TEXT NOT NULL,
  n INTEGER, disagree_n INTEGER, freq REAL, mean_err REAL, mag REAL,
  scored_n INTEGER, rescue_hi_given_lo REAL, rescue_lo_given_hi REAL,
  cofail REAL, xor_err REAL, style_fight REAL, orth_sketch REAL,
  complement REAL, mean_usd REAL, kind TEXT, complement_kind TEXT,
  PRIMARY KEY (pair_lo, pair_hi, domain, judge, scaffold, provider))
"""
DDL_AGENT_TENSOR = """
CREATE TABLE agent_tensor (
  agent TEXT NOT NULL, vs TEXT NOT NULL, axis TEXT NOT NULL,
  n INTEGER, freq REAL, mean_err REAL, mag REAL, xor_err REAL, cofail REAL,
  rescue REAL, orth_sketch REAL, complement REAL, style_fight REAL,
  kind TEXT, complement_kind TEXT,
  PRIMARY KEY (agent, vs, axis))
"""


def _pair_rows(cells: list[dict]) -> dict:
    """Full-resolution 5-axis cells plus the domain-marginal T[pair, domain]."""
    derived = derive_pair_obs(cells)
    obs = derived["obs"]
    full = tm.fold(obs, axes=tm.AXES)
    marginal = tm.fold(obs, axes=("domain",))
    return {"obs": obs, "full": full, "marginal": marginal,
            "n_joint": derived["n_joint"],
            "n_unballoted": derived["n_unballoted"]}


def rebuild(root) -> dict:
    """Drop and rebuild the sqlite projection from the JSONL authority."""
    cells = load_cells(root)
    packed = _pair_rows(cells)
    d = store_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path(root)))
    try:
        for table, ddl in (("obs", DDL_OBS), ("pair_fold", DDL_PAIR_FOLD),
                           ("agent_tensor", DDL_AGENT_TENSOR)):
            con.execute(f"DROP TABLE IF EXISTS {table}")
            con.execute(ddl)
        con.execute("CREATE INDEX idx_obs_seat ON obs(seat, judge, domain)")
        con.execute("CREATE INDEX idx_obs_order ON obs(order_id)")
        for c in cells:
            con.execute(
                "INSERT OR REPLACE INTO obs (dedupe_key, t, run_id, order_id, "
                "fn, domain, seat, n_seats, judge, scaffold, provider, model, "
                "gate, score, keep, err, usd, format_ok, judge_agreement, why, "
                "cache_version, rubric_version) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (c["dedupe_key"], c["t"], c["run_id"], c["order_id"], c["fn"],
                 c["domain"], c["seat"], c["n_seats"], c["judge"],
                 c["scaffold"], c["provider"], c["model"], c["gate"],
                 c["score"],
                 None if c["keep"] is None else int(c["keep"]),
                 c["err"], c["usd"],
                 None if c["format_ok"] is None else int(c["format_ok"]),
                 None if c["judge_agreement"] is None
                 else int(c["judge_agreement"]),
                 c["why"], c["cache_version"], c["rubric_version"]))
        for cell in list(packed["full"].values()) + list(packed["marginal"].values()):
            con.execute(
                "INSERT OR REPLACE INTO pair_fold (pair_lo, pair_hi, domain, "
                "judge, scaffold, provider, n, disagree_n, freq, mean_err, "
                "mag, scored_n, rescue_hi_given_lo, rescue_lo_given_hi, "
                "cofail, xor_err, style_fight, orth_sketch, complement, "
                "mean_usd, kind, complement_kind) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (cell["pair_lo"], cell["pair_hi"], cell["domain"],
                 cell["judge"], cell["scaffold"], cell["provider"], cell["n"],
                 cell["disagree_n"], cell["freq"], cell["mean_err"],
                 cell["mag"], cell["scored_n"], cell["rescue_hi_given_lo"],
                 cell["rescue_lo_given_hi"], cell["cofail"], cell["xor_err"],
                 cell["style_fight"], cell["orth_sketch"], cell["complement"],
                 cell["mean_usd"], cell["kind"], cell["complement_kind"]))
        snap = tm.snapshot(packed["obs"], axes=("domain",))
        for agent, vs_map in snap["tensors"].items():
            for vs, axis_map in vs_map.items():
                for axis, p in axis_map.items():
                    con.execute(
                        "INSERT OR REPLACE INTO agent_tensor (agent, vs, axis, "
                        "n, freq, mean_err, mag, xor_err, cofail, rescue, "
                        "orth_sketch, complement, style_fight, kind, "
                        "complement_kind) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (agent, vs, axis, p["n"], p["freq"], p["mean_err"],
                         p["mag"], p["xor_err"], p["cofail"], p["rescue"],
                         p["orth_sketch"], p["complement"], p["style_fight"],
                         p["kind"], p["complement_kind"]))
        con.commit()
    finally:
        con.close()
    return {
        "schema": SCHEMA,
        "ok": True,
        "db": str(db_path(root)),
        "authority_is": str(obs_path(root)),
        "note": "sqlite is a rebuildable projection, never authority",
        "n_cells": len(cells),
        "n_pair_obs": len(packed["obs"]),
        "n_pair_fold": len(packed["full"]) + len(packed["marginal"]),
        "n_joint_cells": packed["n_joint"],
        "n_unballoted": packed["n_unballoted"],
        "at": _iso(),
    }


# -------------------------------------------------------------- read API
def read(root, *, axes=("domain",), agents=None) -> dict:
    """GET the fold. Never mkdir. Never invents a cell or a host."""
    cells = load_cells(root)
    packed = _pair_rows(cells)
    snap = tm.snapshot(packed["obs"], axes=axes, agents=agents)
    seats: dict[str, int] = {}
    judges: dict[str, int] = {}
    for c in cells:
        seats[c["seat"]] = seats.get(c["seat"], 0) + 1
        judges[c["judge"]] = judges.get(c["judge"], 0) + 1
    return {
        "schema": SCHEMA,
        "ok": True,
        "kind": snap["kind"] if cells else UNMEASURED,
        "complement_kind": snap["complement_kind"],
        "n_obs": len(cells),
        "n_pair_obs": len(packed["obs"]),
        "n_pairs": snap["n_pairs"],
        "pairs": snap["pairs"],
        "tensors": snap["tensors"],
        "tensors_shape": snap["tensors_shape"],
        "porosity": snap["porosity"],
        "axes": snap["axes"],
        "axes_all": list(tm.AXES),
        "seats": dict(sorted(seats.items())),
        "judges": dict(sorted(judges.items())),
        "authority": "PRESENT" if obs_path(root).is_file() else "NO_HOST",
        "db": "PRESENT" if db_path(root).is_file() else "NO_HOST",
        "note": ("JSONL is authority; sqlite is a rebuildable projection; "
                 "UNMEASURED until observed"),
    }


def query(root, *, agent="", vs="", axis="", domain="", judge="",
          scaffold="", provider="", seat="", order_id="", limit=0) -> dict:
    """Filtered read of cells and of the pair fold. Never mkdir."""
    cells = load_cells(root)
    packed = _pair_rows(cells)

    def _keep_cell(c):
        return all([
            not seat or c["seat"] == seat,
            not order_id or c["order_id"] == order_id,
            not domain or c["domain"] == domain,
            not judge or c["judge"] == judge,
            not scaffold or c["scaffold"] == scaffold,
            not provider or c["provider"] == provider,
            not agent or agent in c["pair"],
        ])

    want_pair = {x for x in (agent, vs) if x}

    def _keep_fold(f):
        if want_pair and not want_pair <= {f["pair_lo"], f["pair_hi"]}:
            return False
        ax = axis or domain
        return all([
            not ax or f["domain"] == ax,
            not judge or f["judge"] == judge,
            not scaffold or f["scaffold"] == scaffold,
            not provider or f["provider"] == provider,
        ])

    hit_cells = [c for c in cells if _keep_cell(c)]
    folds = [f for f in packed["full"].values() if _keep_fold(f)]
    marg = [f for f in packed["marginal"].values() if _keep_fold(f)]
    if limit and limit > 0:
        hit_cells = hit_cells[:limit]
        folds = folds[:limit]
        marg = marg[:limit]
    return {
        "schema": SCHEMA,
        "ok": True,
        "filters": {"agent": agent, "vs": vs, "axis": axis, "domain": domain,
                    "judge": judge, "scaffold": scaffold, "provider": provider,
                    "seat": seat, "order_id": order_id},
        "n_cells": len(hit_cells),
        "cells": hit_cells,
        "n_pair_cells": len(folds),
        "pair_cells": folds,
        "pair_cells_domain": marg,
        "kind": (MEASURED if any(f["kind"] == MEASURED for f in folds + marg)
                 else UNMEASURED),
        "n_obs": len(cells),
    }


def pair_observations(root) -> list[dict]:
    """The derived pair trials - what tensor_math folds. Read-only."""
    return _pair_rows(load_cells(root))["obs"]


# ---------------------------------------------------------------- selftest
def _sample_cells(order: str, seat: str, judge: str, *, gate: str,
                  score: float, keep: bool, domain: str = "core",
                  provider: str = "Novita", preload: str = "L1",
                  usd: float = 0.0) -> dict:
    return {
        "schema": CELL_SCHEMA,
        "t": "2026-09-14T13:00:00-05:00",
        "run_id": order.split("-")[0],
        "order_id": order,
        "fn": "renderCoreTelemetry",
        "domain": domain,
        "pair": [seat],
        "judge": judge,
        "scaffold": {"seat": seat, "preload": preload, "prefill": True},
        "provider": provider,
        "model": f"vendor/{seat}-3.0:free",
        "gate": gate,
        "score": score,
        "keep": keep,
        "why": "selftest fixture",
        "usd": usd,
        "cache_version": "orc-b234-20260914",
        "rubric_version": "orc-charter-v2-anchored-20260913",
    }


def _selftest(quiet: bool = False) -> int:
    import tempfile

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="tensor_dbase_"))
    root = td / "store"

    # 1. Empty store: UNMEASURED, and the GET did not create a host.
    snap0 = read(root)
    check("empty store reads kind=UNMEASURED n_obs=0 and GET never mkdir",
          lambda: snap0["kind"] == UNMEASURED and snap0["n_obs"] == 0
          and snap0["schema"] == SCHEMA
          and snap0["tensors"] == {} and snap0["authority"] == "NO_HOST"
          and snap0["db"] == "NO_HOST" and not root.exists())
    q0 = query(root, agent="ling")
    check("empty store query is empty and still never mkdir",
          lambda: q0["n_cells"] == 0 and q0["kind"] == UNMEASURED
          and not root.exists())

    # 2. Schema and provenance are fail-closed.
    def _refuses(rec, kind):
        try:
            normalize_cell(rec)
        except DbaseError as e:
            return e.kind == kind
        return False

    check("wrong cell schema REFUSED",
          lambda: _refuses({"schema": "orc-tensor-cell/9", "order_id": "x",
                            "judge": "j", "pair": ["a"]}, "BAD_SCHEMA"))
    check("missing order_id REFUSED (provenance)",
          lambda: _refuses({"schema": CELL_SCHEMA, "judge": "j",
                            "pair": ["a"]}, "BAD_INPUT"))
    check("missing judge REFUSED (judge is a tensor axis)",
          lambda: _refuses({"schema": CELL_SCHEMA, "order_id": "x",
                            "pair": ["a"]}, "BAD_INPUT"))
    check("scaffold dict folds to a stable axis key",
          lambda: scaffold_key({"seat": "ling", "preload": "L1",
                                "prefill": True})
          == "prefill=true|preload=L1|seat=ling")

    # 3. Ingest: two seats, one order, one judge -> one derived pair trial.
    kelly = "gemini-3.8-flash (Kelly)"
    grok = "grok-4.6 (Gitur)"
    batch = [
        _sample_cells("b4-007", "ling", kelly, gate="UNCHANGED", score=7.5,
                      keep=True),
        _sample_cells("b4-007", "luna", kelly, gate="PATCHED", score=8.5,
                      keep=True, provider="Groq"),
        _sample_cells("b4-008", "ling", kelly, gate="REEMIT", score=5.0,
                      keep=False),
        _sample_cells("b4-008", "luna", kelly, gate="PATCHED", score=9.0,
                      keep=True, provider="Groq"),
    ]
    rep = ingest(root, batch)
    check("ingest appends the authority and rebuilds the projection",
          lambda: rep["n_read"] == 4 and rep["n_new"] == 4
          and rep["n_bad"] == 0 and rep["n_obs"] == 4
          and rep["rebuild"]["n_pair_obs"] == 2
          and obs_path(root).is_file() and db_path(root).is_file())

    # 4. NEGATIVE CONTROL: idempotency. The same file twice is one corpus.
    rep2 = ingest(root, batch)
    n_lines = len(obs_path(root).read_text(encoding="utf-8").strip().splitlines())
    check("NEGATIVE CONTROL: re-ingest is idempotent on order_id+seat+judge "
          "(4 new, then 4 dupes, authority stays 4 lines)",
          lambda: rep2["n_new"] == 0 and rep2["n_dupe"] == 4
          and n_lines == 4 and read(root)["n_obs"] == 4)

    # 5. The derived pair trial is honest about ballots and who erred.
    obs = pair_observations(root)
    o007 = [o for o in obs if o["trial_id"] == "b4-007"][0]
    o008 = [o for o in obs if o["trial_id"] == "b4-008"][0]
    check("agreeing-keep pair with different gates = style fight, no hole",
          lambda: o007["disagree"] is True and o007["who_erred"] == "none"
          and o007["err"] is None)
    check("DROP vs KEEP scores who erred and sizes the hole from the score",
          lambda: o008["who_erred"] in ("a", "b")
          and o008["err"] == 5.0 and o008["err_source"] == "derived-from-score")
    check("provider mismatch inside a pair folds to MIXED, not a fake value",
          lambda: o007["provider"] == MIXED and o007["judge"] == kelly)

    # 6. The projection carries the tensor, and it is rebuildable.
    snap = read(root)
    check("read exposes tensors[agent][vs][axis] with rescue directed",
          lambda: snap["n_obs"] == 4 and snap["n_pair_obs"] == 2
          and snap["tensors_shape"] == "tensors[agent][vs][axis]"
          and "core" in snap["tensors"]["luna"]["ling"]
          and snap["tensors"]["luna"]["ling"]["core"]["rescue"] == 1.0
          and snap["tensors"]["ling"]["luna"]["core"]["rescue"] is None)

    def _sql(sql):
        con = sqlite3.connect(str(db_path(root)))
        try:
            return list(con.execute(sql))
        finally:
            con.close()

    check("projection has obs, pair_fold and agent_tensor rows",
          lambda: _sql("SELECT COUNT(*) FROM obs")[0][0] == 4
          and _sql("SELECT COUNT(*) FROM pair_fold")[0][0] >= 2
          and _sql("SELECT COUNT(*) FROM agent_tensor")[0][0] == 2)

    db_path(root).unlink()
    reb = rebuild(root)
    check("NEGATIVE CONTROL: projection rebuilds from the authority alone "
          "(deleted db, same rows back)",
          lambda: reb["n_cells"] == 4 and reb["n_pair_obs"] == 2
          and _sql("SELECT COUNT(*) FROM obs")[0][0] == 4
          and _sql("SELECT COUNT(*) FROM agent_tensor")[0][0] == 2)

    # 7. Judge is an axis: the same order judged twice does not collapse.
    ingest(root, [
        _sample_cells("b4-007", "ling", grok, gate="REEMIT", score=5.0,
                      keep=False),
        _sample_cells("b4-007", "luna", grok, gate="PATCHED", score=8.0,
                      keep=True, provider="Groq"),
    ])
    q = query(root, agent="ling", vs="luna", axis="core")
    judges = {f["judge"] for f in q["pair_cells"]}
    marg = [f for f in q["pair_cells_domain"]][0]
    check("two judges on one order are two cells on the judge axis, and the "
          "domain-marginal cell folds all three trials",
          lambda: judges == {kelly, grok} and marg["judge"] == tm.ALL
          and marg["n"] == 3 and read(root)["n_obs"] == 6)

    # 8. Bad rows are counted, not silently swallowed or crash-inducing.
    bad_file = td / "bad.jsonl"
    bad_file.write_text(
        "{not json}\n"
        + json.dumps({"schema": "nope", "order_id": "x", "judge": "j",
                      "pair": ["a"]}) + "\n"
        + json.dumps(_sample_cells("b4-009", "ling", kelly, gate="PATCHED",
                                   score=8.0, keep=True)) + "\n",
        encoding="utf-8")
    repb = ingest(root, bad_file)
    check("bad JSON and bad schema are reported, good row still lands",
          lambda: repb["n_bad"] == 2 and repb["n_new"] == 1
          and {b["kind"] for b in repb["bad"]} == {"BAD_JSON", "BAD_SCHEMA"}
          and read(root)["n_obs"] == 7)

    # 9. A single-seat order never fabricates a pair.
    ingest(root, [_sample_cells("b4-010", "glm", kelly, gate="PATCHED",
                                score=8.0, keep=True, domain="ui")])
    q_ui = query(root, domain="ui")
    check("one seat on an order yields a cell but no pair observation",
          lambda: q_ui["n_cells"] == 1 and q_ui["n_pair_cells"] == 0
          and q_ui["kind"] == UNMEASURED)

    # 10. NEGATIVE CONTROL: two seats that never balloted are not agreement.
    silent = []
    for seat in ("ling", "luna"):
        c = _sample_cells("b4-011", seat, kelly, gate="", score=None,
                          keep=None, domain="silent")
        c["gate"] = ""
        c["score"] = None
        c["keep"] = None
        silent.append(c)
    rep_s = ingest(root, silent)
    q_silent = query(root, domain="silent")
    check("NEGATIVE CONTROL: a pair where neither seat balloted is counted "
          "unballoted, never folded as agreement",
          lambda: rep_s["rebuild"]["n_unballoted"] == 1
          and q_silent["n_cells"] == 2 and q_silent["n_pair_cells"] == 0)

    failed = [(l, e) for l, ok, e in results if not ok]
    if not quiet:
        for label, ok, err in results:
            print(("PASS" if ok else "FAIL"), label, err)
        print("dbase selftest %d/%d"
              % (len(results) - len(failed), len(results)))
    return 1 if failed else 0


# --------------------------------------------------------------------- CLI
def _print(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m builds.tensor.dbase",
        description="tensor store: JSONL authority -> sqlite projection")
    ap.add_argument("--selftest", action="store_true",
                    help="run the negative-control selftest and exit")
    sub = ap.add_subparsers(dest="cmd")

    p_in = sub.add_parser("ingest", help="append orc-tensor-cell/1 rows")
    p_in.add_argument("cells", help="path to a JSONL cells file")
    p_in.add_argument("--root", required=True, help="store directory")
    p_in.add_argument("--no-rebuild", action="store_true")

    p_rb = sub.add_parser("rebuild", help="rebuild the sqlite projection")
    p_rb.add_argument("--root", required=True)

    p_q = sub.add_parser("query", help="read cells and the pair fold")
    p_q.add_argument("--root", required=True)
    for flag in ("agent", "vs", "axis", "domain", "judge", "scaffold",
                 "provider", "seat", "order-id"):
        p_q.add_argument(f"--{flag}", default="")
    p_q.add_argument("--limit", type=int, default=0)
    p_q.add_argument("--snapshot", action="store_true",
                     help="full read() snapshot instead of a filtered query")

    sub.add_parser("selftest", help="run the negative-control selftest")

    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return _selftest()
    try:
        if args.cmd == "ingest":
            _print(ingest(args.root, args.cells,
                          rebuild_projection=not args.no_rebuild))
            return 0
        if args.cmd == "rebuild":
            _print(rebuild(args.root))
            return 0
        if args.cmd == "query":
            if args.snapshot:
                _print(read(args.root))
            else:
                _print(query(args.root, agent=args.agent, vs=args.vs,
                             axis=args.axis, domain=args.domain,
                             judge=args.judge, scaffold=args.scaffold,
                             provider=args.provider, seat=args.seat,
                             order_id=getattr(args, "order_id", ""),
                             limit=args.limit))
            return 0
    except (DbaseError, tm.TensorError) as e:
        _print({"ok": False, "kind": getattr(e, "kind", "ERROR"),
                "detail": str(e)})
        return 3
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
