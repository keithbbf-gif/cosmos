#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append a text part to a PINNED OpenWork sit session — never the pen.

    py -3.14 work_orders\\ccr\\_ow_post.py --text \"TICK ...\"

Rules:
- PAUSE hold → no insert (ticks stay in CREW/OUT/_tick.log).
- No OW_SIT.sid → no insert (do not chase time_updated; that is the worker).
- Never insert into CCR.lease sid (the pen).
- Never insert into a session that is currently the hottest cosmos-2 tab
  unless that id is the pinned sit and is not the lease.
"""
from __future__ import annotations

import argparse
import json
import secrets
import sqlite3
import time
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
DB = Path(r"C:\Users\Papa\.local\share\opencode\opencode.db")
PAUSE = ROOT / "live" / "state" / "control" / "PAUSE.flag"
LEASE = ROOT / "live" / "state" / "control" / "CCR.lease"
SIT = ROOT / "live" / "state" / "control" / "OW_SIT.sid"
POST_OFF = ROOT / "live" / "state" / "control" / "OW_POST.off"


def _nid(prefix: str) -> str:
    return prefix + format(int(time.time() * 1000), "x") + secrets.token_hex(6)


def _paused() -> bool:
    try:
        raw = json.loads(PAUSE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return raw.get("state") == "PAUSED" and raw.get("mode") == "hold"


def _lease_sid() -> str:
    try:
        raw = json.loads(LEASE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    return str(raw.get("sid") or "").strip()


def _sit_sid() -> str:
    try:
        sid = SIT.read_text(encoding="utf-8").strip().splitlines()[0].strip()
    except (OSError, IndexError):
        return ""
    if sid.startswith("#") or not sid.startswith("ses_"):
        return ""
    return sid


def post(text: str) -> dict:
    if POST_OFF.exists():
        return {"ok": True, "skipped": "ow_post_off"}
    if _paused():
        return {"ok": True, "skipped": "pause_hold"}
    sit = _sit_sid()
    if not sit:
        return {"ok": True, "skipped": "no_sit_sid"}
    lease = _lease_sid()
    if sit == lease:
        return {"ok": False, "error": "sit_is_pen", "sid": sit}

    now = int(time.time() * 1000)
    mid = _nid("msg_")
    pid = _nid("prt_")
    con = sqlite3.connect(str(DB))
    try:
        row = con.execute("SELECT id, title FROM session WHERE id=?", (sit,)).fetchone()
        if not row:
            return {"ok": False, "error": "sit_missing", "sid": sit}
        msg = {
            "role": "user",
            "time": {"created": now},
            "agent": "openwork",
            "model": {
                "providerID": "google-vertex",
                "modelID": "gemini-3.8-flash",
            },
        }
        part = {"type": "text", "text": text}
        con.execute(
            "INSERT INTO message (id, session_id, time_created, time_updated, data) "
            "VALUES (?,?,?,?,?)",
            (mid, sit, now, now, json.dumps(msg, ensure_ascii=False)),
        )
        con.execute(
            "INSERT INTO part (id, message_id, session_id, time_created, time_updated, data) "
            "VALUES (?,?,?,?,?,?)",
            (pid, mid, sit, now, now, json.dumps(part, ensure_ascii=False)),
        )
        con.execute(
            "UPDATE session SET time_updated=? WHERE id=?",
            (now, sit),
        )
        con.commit()
        return {"ok": True, "sid": sit, "msg": mid, "title": row[1]}
    finally:
        con.close()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--text", required=True)
    ns = p.parse_args()
    print(json.dumps(post(ns.text[:12000])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
