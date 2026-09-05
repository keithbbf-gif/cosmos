#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_ledger_verify - 5-minute chain-verify satellite.

Walks Ledger.verify() on the authority JSONL. A break is REFUSED and named
(TORN / BROKEN_CHAIN / FORGED / UNREADABLE) — never repaired in place.
Writes live/state/ledger/verify.json + heartbeat.

    py -3.14 cosmos\\cosmos_ledger_verify.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_ledger_verify.py --root ... --standup

Task: COSMOS Ledger Verify. schtasks every 5 minutes. No bts_*.
Does not append. Does not modify core. Does not honor PAUSE.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    atomic_json, create_task, heartbeat_age_s, query_task, read_heartbeat,
    tr_cmdline, write_heartbeat,
)
from cosmos_ledger import Ledger, LedgerError  # noqa: E402
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

WORKER = "cosmos-ledger-verify"
TASK_NAME = "COSMOS Ledger Verify"
HEARTBEAT_NAME = "ledger_verify_heartbeat.json"
SCHEMA = "cosmos-ledger-verify/1"
FRESH_S = 400.0


def poll_once(root: str) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    dest_dir = paths.state("ledger")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "verify.json"
    t0 = time.time()
    keyfile = paths.config("install_key.bin")
    extra: dict = {"schema": SCHEMA, "tick": "once", "projection": str(dest)}
    records = 0
    head_seq = 0
    head_event = None
    try:
        if not keyfile.exists():
            raise FileNotFoundError("no install_key.bin")
        key = keyfile.read_bytes()
        ledger = Ledger(paths.ledger("authority.jsonl"), key, WORKER)
        # Loading already verified. Walk again so the tick's count is explicit
        # and a mid-tick append cannot be mistaken for this clock "repairing".
        last = None
        for rec in ledger.verify():
            records += 1
            last = rec
        if last:
            head_seq = int(last.get("seq") or 0)
            head_event = last.get("event")
        extra.update({
            "ok": True, "state": "VERIFIED", "records": records,
            "head_seq": head_seq, "head_event": head_event,
        })
    except LedgerError as e:
        extra.update({"ok": False, "state": "REFUSED", "kind": e.kind,
                      "detail": str(e)[:400], "records": records})
    except Exception as e:  # noqa: BLE001
        extra.update({"ok": False, "state": "ERROR",
                      "detail": f"{type(e).__name__}: {e}"[:400]})
    extra["elapsed_s"] = round(time.time() - t0, 3)
    hb = write_heartbeat(logs / HEARTBEAT_NAME, WORKER, extra=extra)
    projection = {
        "schema": SCHEMA,
        "measured_at": hb["last_run"],
        "measured_epoch": hb["last_run_epoch"],
        "worker": WORKER,
        "ok": extra.get("ok"),
        "state": extra.get("state"),
        "kind": extra.get("kind"),
        "records": extra.get("records", records),
        "head_seq": extra.get("head_seq", head_seq),
        "head_event": extra.get("head_event"),
        "detail": extra.get("detail"),
        "elapsed_s": extra["elapsed_s"],
    }
    atomic_json(dest, projection)
    extra["heartbeat"] = hb
    extra["heartbeat_path"] = str(logs / HEARTBEAT_NAME)
    return extra


def standup(root: str) -> dict:
    existing = query_task(TASK_NAME)
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once")
    tick = poll_once(root)
    if existing.get("ok"):
        return {"started": "already", "task": existing,
                "tick": {"ok": tick.get("ok"), "records": tick.get("records"),
                         "state": tick.get("state")},
                "keith_cmd": None, "task_name": TASK_NAME}
    task = create_task(TASK_NAME, tr, "minute", mo=5, run_now=False)
    return {
        "started": "schtasks" if task.get("ok") else "in-process-tick",
        "task": task,
        "tick": {"ok": tick.get("ok"), "records": tick.get("records"),
                 "state": tick.get("state")},
        "proof": {"ok": bool(tick.get("ok")), "heartbeat": tick.get("heartbeat")},
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
        "task_name": TASK_NAME,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_ledger_verify")
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
    print(json.dumps({k: r[k] for k in r if k != "heartbeat"},
                     indent=1, default=str))
    return 0 if r.get("ok") else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
