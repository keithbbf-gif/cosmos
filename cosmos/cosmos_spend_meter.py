#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_spend_meter - 1-minute spend/quota projection satellite.

Reads the authority ledger through SpendGate.audit() (no append). Writes
live/state/spend/meter.json + heartbeat. 1-min schtasks — this hammers the
ledger walk, not a 0.5s loop.

    py -3.14 cosmos\\cosmos_spend_meter.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_spend_meter.py --root ... --standup

Task: COSMOS Spend Meter. No bts_* import. Does not modify core modules.
Does not honor PAUSE (meters keep moving).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    create_task, heartbeat_age_s, query_task, read_heartbeat, tr_cmdline,
    write_heartbeat, atomic_json,
)
from cosmos_ledger import Ledger, LedgerError  # noqa: E402
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402
from cosmos_spend import SpendGate  # noqa: E402

WORKER = "cosmos-spend-meter"
TASK_NAME = "COSMOS Spend Meter"
HEARTBEAT_NAME = "spend_meter_heartbeat.json"
SCHEMA = "cosmos-spend-meter/1"
FRESH_S = 180.0


def poll_once(root: str) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    dest_dir = paths.state("spend")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "meter.json"
    t0 = time.time()
    keyfile = paths.config("install_key.bin")
    extra: dict = {"schema": SCHEMA, "tick": "once", "projection": str(dest)}
    audit: dict = {"rails": {}}
    try:
        if not keyfile.exists():
            raise FileNotFoundError("no install_key.bin")
        key = keyfile.read_bytes()
        ledger = Ledger(paths.ledger("authority.jsonl"), key, WORKER)
        gate = SpendGate(ledger)
        audit = gate.audit()
        extra["ok"] = True
        extra["rail_count"] = len(audit.get("rails") or {})
        extra["state"] = "OK"
    except LedgerError as e:
        extra.update({"ok": False, "state": "LEDGER_" + e.kind,
                      "kind": e.kind, "detail": str(e)[:400]})
    except Exception as e:  # noqa: BLE001
        extra.update({"ok": False, "state": "ERROR",
                      "detail": f"{type(e).__name__}: {e}"[:400]})
    extra["elapsed_s"] = round(time.time() - t0, 3)
    hb = write_heartbeat(logs / HEARTBEAT_NAME, WORKER, extra=extra)
    rails = audit.get("rails") or {}
    settled = 0.0
    held = 0.0
    for row in rails.values():
        if not isinstance(row, dict):
            continue
        settled += float(row.get("settled_usd") or 0)
        held += float(row.get("unpriced_held_usd") or 0)
    usd_kind = "MEASURED" if extra.get("ok") and rails else "UNMEASURED"
    projection = {
        "schema": SCHEMA,
        "measured_at": hb["last_run"],
        "measured_epoch": hb["last_run_epoch"],
        "worker": WORKER,
        "ok": extra.get("ok"),
        "state": extra.get("state"),
        "audit": audit,
        "elapsed_s": extra["elapsed_s"],
        # cDeck header strip. Tokens are UNMEASURED until a rail reports them.
        # Day/week USD are UNMEASURED (ledger has no day fold here). Do not invent 0.
        "tokens": {"in": None, "out": None, "kind": "UNMEASURED"},
        "usd": {
            "settled": round(settled, 6) if usd_kind == "MEASURED" else None,
            "unpriced_held": round(held, 6) if usd_kind == "MEASURED" else None,
            "day": None,
            "week": None,
            "kind": usd_kind,
        },
    }
    atomic_json(dest, projection)
    return {"ok": bool(extra.get("ok")), "heartbeat": hb,
            "projection": str(dest), "rail_count": extra.get("rail_count", 0)}


def standup(root: str) -> dict:
    existing = query_task(TASK_NAME)
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once")
    tick = poll_once(root)
    if existing.get("ok"):
        return {"started": "already", "task": existing, "tick": tick,
                "keith_cmd": None, "task_name": TASK_NAME}
    task = create_task(TASK_NAME, tr, "minute", mo=1, run_now=False)
    return {
        "started": "schtasks" if task.get("ok") else "in-process-tick",
        "task": task,
        "tick": {"rail_count": tick.get("rail_count"), "ok": tick.get("ok")},
        "proof": {"ok": True, "heartbeat": tick.get("heartbeat")},
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
        "task_name": TASK_NAME,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_spend_meter")
    ap.add_argument("--root", required=True)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.status:
        paths = CosmosPaths(a.root)
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        print(json.dumps({"path": str(paths.logs(HEARTBEAT_NAME)),
                          "age_s": age, "heartbeat": rec}, indent=1,
                         default=str))
        return 0 if age is not None and age < FRESH_S else 2
    if a.standup:
        r = standup(a.root)
        print(json.dumps(r, indent=1, default=str))
        return 0 if r.get("started") else 2
    r = poll_once(a.root)
    print(json.dumps({"ok": r["ok"], "rail_count": r["rail_count"],
                      "projection": r["projection"]}, indent=1, default=str))
    return 0 if r["ok"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
