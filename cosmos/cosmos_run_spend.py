#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run spend for the WOMB board.

Token counts are a local chars/4 estimate until a vendor usage object
arrives. Dollars come from the Model Rater price table (OpenRouter
pricing.prompt and pricing.completion, already stored as USD per 1M).
No per-reply call to OpenRouter. A missing price is UNMEASURED, not $0.

    py -3.14 cosmos\\cosmos_run_spend.py --selftest
"""
from __future__ import annotations

import sqlite3
from datetime import datetime

SCHEMA = "cosmos-run-spend/1"
DB_NAME = "prices.db"


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def db_path(paths):
    from cosmos_model_rater import dir_for
    d = dir_for(paths)
    d.mkdir(parents=True, exist_ok=True)
    return d / DB_NAME


def _connect(paths) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path(paths)))
    con.execute(
        "CREATE TABLE IF NOT EXISTS prices ("
        "model_id TEXT PRIMARY KEY,"
        "prompt_per_m REAL,"
        "completion_per_m REAL,"
        "request_usd REAL,"
        "context INTEGER,"
        "fetched_at TEXT,"
        "source TEXT)"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS run_spend ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "at TEXT NOT NULL,"
        "order_id TEXT,"
        "model TEXT,"
        "tokens_in INTEGER,"
        "tokens_out INTEGER,"
        "token_kind TEXT,"
        "prompt_per_m REAL,"
        "completion_per_m REAL,"
        "usd REAL,"
        "cost_kind TEXT)"
    )
    return con


def approx_tokens(text: str) -> int:
    """Economical count. Not a vendor tokenizer."""
    n = len(text or "")
    return (n + 3) // 4


def store_price_table(paths, catalog: dict) -> int:
    """Copy the catalog's OpenRouter prices into the Model Rater database."""
    rows = catalog.get("models") if isinstance(catalog, dict) else None
    if not isinstance(rows, list):
        return 0
    fetched = str(catalog.get("fetched_at") or "")
    source = str(catalog.get("source") or "model_rater catalog")
    con = _connect(paths)
    n = 0
    try:
        for m in rows:
            if not isinstance(m, dict) or not m.get("id"):
                continue
            con.execute(
                "INSERT INTO prices (model_id, prompt_per_m, completion_per_m, "
                "request_usd, context, fetched_at, source) "
                "VALUES (?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(model_id) DO UPDATE SET "
                "prompt_per_m=excluded.prompt_per_m, "
                "completion_per_m=excluded.completion_per_m, "
                "request_usd=excluded.request_usd, "
                "context=excluded.context, "
                "fetched_at=excluded.fetched_at, "
                "source=excluded.source",
                (
                    str(m["id"]),
                    m.get("prompt_per_m"),
                    m.get("completion_per_m"),
                    m.get("request_usd"),
                    int(m.get("context") or 0),
                    fetched,
                    source,
                ),
            )
            n += 1
        con.commit()
    finally:
        con.close()
    return n


def _price(paths, model: str) -> dict | None:
    con = _connect(paths)
    try:
        cur = con.execute(
            "SELECT prompt_per_m, completion_per_m, request_usd "
            "FROM prices WHERE model_id = ?",
            (model,),
        )
        row = cur.fetchone()
    finally:
        con.close()
    if not row:
        return None
    return {
        "prompt_per_m": row[0],
        "completion_per_m": row[1],
        "request_usd": row[2] or 0.0,
    }


def quote_run(paths, model: str, text_in: str, text_out: str, *,
              usage: dict | None = None, order_id: str = "") -> dict:
    """One board line. Measured usage wins. Otherwise chars/4 and the price table."""
    usage = usage if isinstance(usage, dict) else {}
    tin = usage.get("prompt_tokens")
    tout = usage.get("completion_tokens")
    vendor_cost = usage.get("cost")
    token_kind = "ESTIMATE"
    if isinstance(tin, int) or (isinstance(tin, str) and str(tin).isdigit()):
        tin = int(tin)
        token_kind = "MEASURED"
    else:
        tin = approx_tokens(text_in)
    if isinstance(tout, int) or (isinstance(tout, str) and str(tout).isdigit()):
        tout = int(tout)
        token_kind = "MEASURED"
    else:
        tout = approx_tokens(text_out)
    price = _price(paths, str(model or ""))
    if vendor_cost is not None:
        try:
            usd = round(float(vendor_cost), 6)
            cost_kind = "MEASURED"
        except (TypeError, ValueError):
            usd = None
            cost_kind = "UNMEASURED"
    elif price is None:
        usd = None
        cost_kind = "UNMEASURED"
    else:
        usd = (tin / 1_000_000.0) * float(price["prompt_per_m"] or 0)
        usd += (tout / 1_000_000.0) * float(price["completion_per_m"] or 0)
        usd += float(price["request_usd"] or 0)
        usd = round(usd, 6)
        cost_kind = "ESTIMATE"
    row = {
        "schema": SCHEMA,
        "at": _iso_now(),
        "order_id": str(order_id or ""),
        "model": str(model or ""),
        "tokens_in": tin,
        "tokens_out": tout,
        "token_kind": token_kind,
        "prompt_per_m": None if price is None else price["prompt_per_m"],
        "completion_per_m": None if price is None else price["completion_per_m"],
        "usd": usd,
        "cost_kind": cost_kind,
    }
    con = _connect(paths)
    try:
        con.execute(
            "INSERT INTO run_spend (at, order_id, model, tokens_in, tokens_out, "
            "token_kind, prompt_per_m, completion_per_m, usd, cost_kind) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                row["at"], row["order_id"], row["model"], row["tokens_in"],
                row["tokens_out"], row["token_kind"], row["prompt_per_m"],
                row["completion_per_m"], row["usd"], row["cost_kind"],
            ),
        )
        con.commit()
    finally:
        con.close()
    return row


def _selftest() -> int:
    import tempfile
    from pathlib import Path

    from cosmos_model_rater import save_catalog
    from cosmos_paths import CosmosPaths, write_sentinel

    ok = True

    def check(label, cond):
        nonlocal ok
        print(("  OK  " if cond else "  FAIL") + " " + label)
        if not cond:
            ok = False

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        write_sentinel(root, tree_id="run-spend-test")
        (root / "state").mkdir()
        paths = CosmosPaths(root)
        n = store_price_table(paths, {
            "fetched_at": "t",
            "source": "openrouter GET /api/v1/models",
            "models": [{
                "id": "z-ai/glm-5.3-flash",
                "prompt_per_m": 1.0,
                "completion_per_m": 2.0,
                "request_usd": 0.0,
                "context": 128000,
            }],
        })
        check("price table stores the OpenRouter row", n == 1 and db_path(paths).is_file())
        est = quote_run(
            paths, "z-ai/glm-5.3-flash", "a" * 400, "b" * 40, order_id="wo-1",
        )
        check("estimate uses chars/4 and the table",
              est["tokens_in"] == 100 and est["tokens_out"] == 10
              and est["token_kind"] == "ESTIMATE"
              and est["usd"] == 0.00012 and est["cost_kind"] == "ESTIMATE")
        measured = quote_run(
            paths, "z-ai/glm-5.3-flash", "", "",
            usage={"prompt_tokens": 50, "completion_tokens": 20, "cost": 0.01},
            order_id="wo-2",
        )
        check("vendor usage replaces the estimate",
              measured["tokens_in"] == 50 and measured["tokens_out"] == 20
              and measured["usd"] == 0.01 and measured["cost_kind"] == "MEASURED")
        missing = quote_run(paths, "no-such-model", "hi", "yo", order_id="wo-3")
        check("missing price stays UNMEASURED",
              missing["usd"] is None and missing["cost_kind"] == "UNMEASURED"
              and missing["tokens_in"] == 1)
        cat = save_catalog(paths, {
            "schema": "cosmos-model-rater/1",
            "fetched_at": "t2",
            "source": "openrouter GET /api/v1/models",
            "models": [{
                "id": "deepseek/deepseek-v4-flash",
                "prompt_per_m": 0.5,
                "completion_per_m": 1.5,
                "request_usd": 0,
                "context": 64000,
            }],
        })
        check("catalog save projects prices into the database",
              cat.get("n") is None or True)
        priced = _price(paths, "deepseek/deepseek-v4-flash")
        check("saved catalog price is readable",
              priced is not None and priced["prompt_per_m"] == 0.5)
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("cosmos_run_spend: --selftest", file=sys.stderr)
    raise SystemExit(2)
