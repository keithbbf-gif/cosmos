#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_kb.py — build the general COSMOS knowledge base SQLite projection.

JSON (work_orders/ccr/COSMOS_KB.json) is the source of truth. This script
rebuilds the queryable SQLite projection from it. Same pattern as the rest of
COSMOS: source -> projection.

Usage:
    py -3.14 cosmos_kb.py build [--json work_orders/ccr/COSMOS_KB.json] [--db live/state/cosmos_kb.db]
    py -3.14 cosmos_kb.py query "SELECT model_id FROM scars WHERE kind='PARENT_TREE_WALK'"
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
DEFAULT_JSON = ROOT / "work_orders" / "ccr" / "COSMOS_KB.json"
DEFAULT_DB = ROOT / "live" / "state" / "cosmos_kb.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS models (
  model_id TEXT PRIMARY KEY,
  seat TEXT, role TEXT, via TEXT,
  window_tokens INT, cache_floor INT, budget_out_usd_per_m REAL
);
CREATE TABLE IF NOT EXISTS optim (
  model_id TEXT, key TEXT, value TEXT, note TEXT,
  PRIMARY KEY (model_id, key)
);
CREATE TABLE IF NOT EXISTS scars (
  id TEXT PRIMARY KEY, scope TEXT, model_id TEXT, kind TEXT, date TEXT,
  status TEXT, symptom TEXT, cause TEXT, restricted_tree TEXT,
  corrective TEXT, outcome TEXT, derivation TEXT
);
CREATE TABLE IF NOT EXISTS lessons (
  id TEXT PRIMARY KEY, scope TEXT, model_id TEXT, date TEXT,
  what_worked TEXT, rule TEXT
);
CREATE TABLE IF NOT EXISTS keys (
  account TEXT PRIMARY KEY, lane TEXT, wallet TEXT, key_file TEXT,
  status TEXT, note TEXT
);
"""


def build(json_path: Path, db_path: Path) -> None:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    con.execute("DELETE FROM models")
    con.execute("DELETE FROM optim")
    con.execute("DELETE FROM scars")
    con.execute("DELETE FROM lessons")
    con.execute("DELETE FROM keys")

    for m in data.get("models", []):
        con.execute(
            "INSERT INTO models (model_id, seat, role, via, window_tokens, cache_floor, budget_out_usd_per_m) "
            "VALUES (?,?,?,?,?,?,?)",
            (m["model_id"], m.get("seat"), m.get("role"), m.get("via"),
             m.get("window_tokens"), m.get("cache_floor"), m.get("budget_out_usd_per_m")),
        )
        for k, v in (m.get("optim") or {}).items():
            con.execute("INSERT INTO optim (model_id, key, value, note) VALUES (?,?,?,?)",
                        (m["model_id"], k, str(v), m.get("optim", {}).get("notes")))

    for s in data.get("scars", []):
        con.execute(
            "INSERT INTO scars (id, scope, model_id, kind, date, status, symptom, cause, "
            "restricted_tree, corrective, outcome, derivation) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (s["id"], s.get("scope"), s.get("model_id"), s.get("kind"), s.get("date"),
             s.get("status"), s.get("symptom"), s.get("cause"), s.get("restricted_tree"),
             s.get("corrective"), s.get("outcome"), s.get("derivation")),
        )

    for l in data.get("lessons", []):
        con.execute(
            "INSERT INTO lessons (id, scope, model_id, date, what_worked, rule) VALUES (?,?,?,?,?,?)",
            (l["id"], l.get("scope"), l.get("model_id"), l.get("date"),
             l.get("what_worked"), l.get("rule")),
        )

    for k in data.get("keys", []):
        con.execute(
            "INSERT INTO keys (account, lane, wallet, key_file, status, note) VALUES (?,?,?,?,?,?)",
            (k["account"], k.get("lane"), k.get("wallet"), k.get("key_file"),
             k.get("status"), k.get("note")),
        )

    con.commit()
    n = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
         for t in ("models", "optim", "scars", "lessons", "keys")}
    con.close()
    print(f"Built {db_path}: {n}")


def query(db_path: Path, sql: str) -> None:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"SQL error: {e}", file=sys.stderr)
        sys.exit(1)
    if not rows:
        print("(no rows)")
        return
    cols = rows[0].keys()
    print(" | ".join(cols))
    for r in rows:
        print(" | ".join(str(r[c]) for c in cols))
    con.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="COSMOS knowledge base projection")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_b = sub.add_parser("build")
    p_b.add_argument("--json", default=str(DEFAULT_JSON))
    p_b.add_argument("--db", default=str(DEFAULT_DB))
    p_q = sub.add_parser("query")
    p_q.add_argument("sql")
    p_q.add_argument("--db", default=str(DEFAULT_DB))
    args = ap.parse_args()

    if args.cmd == "build":
        build(Path(args.json), Path(args.db))
    else:
        query(Path(args.db), args.sql)


if __name__ == "__main__":
    main()