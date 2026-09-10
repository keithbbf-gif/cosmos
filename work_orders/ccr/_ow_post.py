#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append a text part to the current OpenWork session (COSMOS_2 sit).

    py -3.14 work_orders\\ccr\\_ow_post.py --text \"TICK ...\"
"""
from __future__ import annotations

import argparse
import json
import secrets
import sqlite3
import time
from pathlib import Path

DB = Path(r"C:\Users\Papa\.local\share\opencode\opencode.db")


def _nid(prefix: str) -> str:
    return prefix + format(int(time.time() * 1000), "x") + secrets.token_hex(6)


def current_sid(con: sqlite3.Connection) -> str:
    row = con.execute(
        "SELECT id FROM session WHERE directory LIKE '%OpenWork%COSMOS%' "
        "OR directory LIKE '%COSMOS_2%' OR directory LIKE '%COSMOS 2%' "
        "ORDER BY time_updated DESC LIMIT 1"
    ).fetchone()
    if not row:
        raise SystemExit("NO_OW_SESSION")
    return row[0]


def post(text: str) -> dict:
    now = int(time.time() * 1000)
    mid = _nid("msg_")
    pid = _nid("prt_")
    con = sqlite3.connect(str(DB))
    try:
        sid = current_sid(con)
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
            (mid, sid, now, now, json.dumps(msg, ensure_ascii=False)),
        )
        con.execute(
            "INSERT INTO part (id, message_id, session_id, time_created, time_updated, data) "
            "VALUES (?,?,?,?,?,?)",
            (pid, mid, sid, now, now, json.dumps(part, ensure_ascii=False)),
        )
        con.execute(
            "UPDATE session SET time_updated=? WHERE id=?",
            (now, sid),
        )
        con.commit()
        return {"ok": True, "sid": sid, "msg": mid}
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
