#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_health_watchdog - hourly fleet watchdog (P0).

PROPOSED satellite — lives under builds/health/, touches no cosmos/ core
(kernel / ledger / sched / service). Native Python, windowless, fail-closed.

What one --once tick does:
  1. Resolve every path through CosmosPaths roles under ONE --root.
  2. Poll named daemons (runner, pool, collector, dispatcher, watchdog2,
     motif_driver) plus the COSMOS-own clocks via heartbeat artifacts in
     the logs role AND schtasks query state.
  3. Read goals free from MOTIF_TRACKER + collector dhx snap + WD2
     heartbeat; diff against the last beat.
  4. Post a ROUTINE Slack line (incoming webhook; zero Claude) naming
     goals working-on and completed since the last beat.
  5. PAGE on any exception or dead daemon (heartbeat older than that
     daemon's threshold, missing, or unreadable). Pages are
     create-if-absent (fingerprint file); never append-duplicates.
  6. Emit a board + own heartbeat. rc=0 is not the proof — the board is.

    py -3.14 builds\\health\\cosmos_health_watchdog.py --root <runtime> --once
    py -3.14 builds\\health\\cosmos_health_watchdog.py --root <runtime> --standup
    py -3.14 builds\\health\\cosmos_health_watchdog.py --root <runtime> --status

Scheduling: schtasks HOURLY + onlogon, create-if-absent (never /f
replace of an existing task). pythonw, no console. No bts_* import.
Keith drops the Slack webhook at config/slack_webhook.txt (his door).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
from pathlib import Path
from typing import Any, Callable

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent
_COSMOS = _REPO / "cosmos"
if str(_COSMOS) not in sys.path:
    sys.path.insert(0, str(_COSMOS))

from cosmos_clock import (  # noqa: E402
    atomic_json,
    create_task,
    heartbeat_age_s,
    pythonw_exe,
    query_task,
    read_heartbeat,
    tr_cmdline,
    write_heartbeat,
)
from cosmos_paths import CosmosPathError, CosmosPaths  # noqa: E402

WORKER = "cosmos-health-watchdog"
TASK_NAME = "COSMOS Health Watchdog"
TASK_NAME_LOGON = "COSMOS Health Watchdog Logon"
HEARTBEAT_NAME = "health_watchdog_heartbeat.json"
BOARD_NAME = "watchdog_board.json"
LAST_BEAT_NAME = "last_beat.json"
PAGE_FLAG_NAME = "PAGE.flag"
SCHEMA = "cosmos-health-watchdog/1"
DEFAULT_INTERVAL_S = 3600.0
SLACK_WEBHOOK_FILE = "slack_webhook.txt"
CONFIG_NAME = "health_watchdog.json"
SLACK_PREFIX = "https://hooks.slack.com/"
DISK_WARN_PCT_FREE = 10.0
BACKUP_STALE_S = 8 * 3600
AUDIT_STALE_S = 7 * 24 * 3600

HttpPost = Callable[[str, bytes], dict]
TaskQuery = Callable[[str], dict]
DiskUsage = Callable[[str], Any]


@dataclass(frozen=True)
class DaemonSpec:
    """One fleet member. heartbeat is a filename under the logs role."""
    id: str
    heartbeat: str
    task: str
    stale_s: float
    required: bool = True
    logon: str | None = None


# Named daemons from the work order, then the COSMOS-own clocks.
# stale_s = cadence + slack. COMPARE USING last_run_epoch.
FLEET: tuple[DaemonSpec, ...] = (
    DaemonSpec("runner", "cosmos_runner_heartbeat.json",
               "COSMOS Runner", 90.0, logon="COSMOS Runner Logon"),
    DaemonSpec("pool", "cosmos_pool_heartbeat.json",
               "COSMOS Runner Pool", 90.0, logon="COSMOS Runner Pool Logon"),
    DaemonSpec("collector", "collector_heartbeat.json",
               "COSMOS Collector", 120.0, logon="COSMOS Collector Logon"),
    DaemonSpec("dispatcher", "dispatcher_heartbeat.json",
               "COSMOS Dispatcher", 90.0, logon="COSMOS Dispatcher Logon"),
    DaemonSpec("watchdog2", "watchdog2_heartbeat.json",
               "COSMOS Watchdog2", 90.0, logon="COSMOS Watchdog2 Logon"),
    DaemonSpec("motif_driver", "motif_driver_heartbeat.json",
               "COSMOS Motif Driver", 1200.0),
    DaemonSpec("health_clock", "health_clock_heartbeat.json",
               "COSMOS Health", 30.0, logon="COSMOS Health Logon"),
    DaemonSpec("rails_prober", "rails_prober_heartbeat.json",
               "COSMOS Rails Prober", 180.0),
    DaemonSpec("spend_meter", "spend_meter_heartbeat.json",
               "COSMOS Spend Meter", 180.0),
    DaemonSpec("drive_meter", "drive_meter_heartbeat.json",
               "COSMOS Drive Meter", 180.0),
    DaemonSpec("cdeck_feed", "cdeck_feed_heartbeat.json",
               "COSMOS cDeck Feed", 30.0, logon="COSMOS cDeck Feed Logon"),
    DaemonSpec("backup_clock", "backup_clock_heartbeat.json",
               "COSMOS Backup 07", BACKUP_STALE_S),
    DaemonSpec("ledger_verify", "ledger_verify_heartbeat.json",
               "COSMOS Ledger Verify", 600.0),
    DaemonSpec("cosmos_index", "cosmos_index_heartbeat.json",
               "COSMOS Index", 180.0),
    DaemonSpec("mesh_discovery", "mesh_discovery_heartbeat.json",
               "COSMOS Mesh Discovery", 3900.0),
    DaemonSpec("cvm_clock", "cvm_clock_heartbeat.json",
               "COSMOS CVM Clock", 30.0, logon="COSMOS CVM Clock Logon"),
    DaemonSpec("work_order_runner", "work_order_runner_heartbeat.json",
               "COSMOS Work-Order Runner", 90.0,
               required=False, logon="COSMOS Work-Order Runner Logon"),
)

# Discovery (see discover_unwatched). Deliberately far past every cadence in
# FLEET above (the longest is the 8h backup clock), so a file nobody has
# classified yet cannot produce a false alarm on a merely-slow daemon.
UNWATCHED_STALE_S = 24 * 3600.0
HEARTBEAT_GLOB = "*heartbeat*.json"

TRACKER_ROW_RE = re.compile(
    r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$",
    re.M,
)
WISH_RE = re.compile(r"^- \[([ xX])\] \*\*(.+?)\*\*", re.M)
STAGE6_RE = re.compile(r"(?:^|[^\d])6(?:\s|$)|stage[- ]?6|passed the gate|"
                       r"APPLIED_VERIFIED|runtime-binding", re.I)


class HealthWatchdogRefusal(RuntimeError):
    """Fail-closed: raised when the root cannot be verified or a tick
    cannot emit a board. Never caught to invent GREEN."""


# ----------------------------------------------------------------- io helpers


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _utcnow() -> str:
    return datetime.now(dt_timezone.utc).isoformat(timespec="seconds")


def _read_json(path: Path) -> tuple[str, dict | None]:
    """Return (kind, rec). kind in {OK, MISSING, UNREADABLE, UNPARSEABLE}.
    Absence and torn JSON are different facts; neither is repaired."""
    if not path.exists():
        return "MISSING", None
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return "UNREADABLE", None
    try:
        rec = json.loads(raw)
    except ValueError:
        return "UNPARSEABLE", None
    if not isinstance(rec, dict):
        return "UNPARSEABLE", None
    return "OK", rec


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return s[:80] or "unnamed"


def _fingerprint(*parts: str) -> str:
    blob = "|".join(parts).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


# ----------------------------------------------------------------- config


def load_config(paths: CosmosPaths) -> dict:
    cfg = {
        "schema": SCHEMA,
        "interval_s": DEFAULT_INTERVAL_S,
        "slack_webhook_file": SLACK_WEBHOOK_FILE,
        "disk_warn_pct_free": DISK_WARN_PCT_FREE,
        "page_on_red": True,
    }
    p = paths.config(CONFIG_NAME)
    kind, rec = _read_json(p)
    if kind == "OK" and rec:
        for k in ("interval_s", "slack_webhook_file",
                  "disk_warn_pct_free", "page_on_red", "unwatched_stale_s"):
            if k in rec:
                cfg[k] = rec[k]
    elif kind in ("UNREADABLE", "UNPARSEABLE"):
        cfg["_config_error"] = f"{kind} {p.name}"
    return cfg


def load_slack_webhook(paths: CosmosPaths, filename: str) -> tuple[str | None, str]:
    """Webhook lives under the config role. Missing is a typed refusal,
    not a guessed URL. Only hooks.slack.com is accepted (fail-closed)."""
    name = Path(str(filename)).name  # strip any attempted path
    p = paths.config(name)
    if not p.is_file():
        return None, "MISSING"
    try:
        url = p.read_text(encoding="utf-8").strip().splitlines()[0].strip()
    except OSError:
        return None, "UNREADABLE"
    if not url:
        return None, "EMPTY"
    if not url.startswith(SLACK_PREFIX):
        return None, "REFUSED_NOT_SLACK"
    return url, "OK"


# ----------------------------------------------------------------- fleet poll


def _parse_schtasks_list(out: str) -> dict:
    status = last_result = last_run = None
    for line in (out or "").splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        k = key.strip().lower()
        v = val.strip()
        if k == "status":
            status = v
        elif k == "last result":
            last_result = v
        elif k == "last run time":
            last_run = v
    return {"status": status, "last_result": last_result,
            "last_run_time": last_run}


def query_task_safe(name: str, task_query: TaskQuery | None = None) -> dict:
    fn = task_query or query_task
    try:
        rec = fn(name)
    except Exception as e:  # noqa: BLE001
        return {"name": name, "registered": False, "ok": False,
                "error": f"{type(e).__name__}: {e}"}
    rec = dict(rec or {})
    rec["name"] = name
    rec["registered"] = bool(rec.get("ok"))
    rec.update(_parse_schtasks_list(rec.get("out") or ""))
    return rec


def _heartbeat_kind(path: Path) -> tuple[str, dict | None]:
    kind, rec = _read_json(path)
    if kind != "OK":
        return kind, rec
    if "last_run_epoch" not in rec:
        return "UNPARSEABLE", rec
    return "OK", rec


def poll_daemon(spec: DaemonSpec, logs: Path, now: float,
                task_query: TaskQuery | None = None) -> dict:
    hb_path = logs / spec.heartbeat
    kind, rec = _heartbeat_kind(hb_path)
    task = query_task_safe(spec.task, task_query=task_query)
    age = heartbeat_age_s(rec, now=now) if rec else None
    dead_reason = None
    if kind == "MISSING":
        dead_reason = "MISSING_HEARTBEAT"
    elif kind in ("UNREADABLE", "UNPARSEABLE"):
        dead_reason = kind
    elif age is None:
        dead_reason = "NO_EPOCH"
    elif age > spec.stale_s:
        dead_reason = "STALE"
    ok = dead_reason is None
    if not spec.required and kind == "MISSING":
        # optional daemon never stood up: report ABSENT, do not page
        return {
            "id": spec.id, "ok": True, "required": False,
            "state": "ABSENT", "detail": "optional, no heartbeat yet",
            "heartbeat": spec.heartbeat, "age_s": None,
            "stale_s": spec.stale_s, "task": task,
            "pid": None, "dead_reason": None,
        }
    detail = (
        f"age_s={None if age is None else round(age, 3)} "
        f"threshold_s={spec.stale_s} kind={kind}"
        + (f" dead={dead_reason}" if dead_reason else "")
    )
    return {
        "id": spec.id,
        "ok": ok,
        "required": spec.required,
        "state": "ALIVE" if ok else "DEAD",
        "detail": detail,
        "heartbeat": spec.heartbeat,
        "age_s": None if age is None else round(age, 3),
        "stale_s": spec.stale_s,
        "task": {"name": task.get("name"), "registered": task.get("registered"),
                 "status": task.get("status"), "last_result": task.get("last_result")},
        "pid": (rec or {}).get("pid"),
        "worker": (rec or {}).get("worker"),
        "tick": (rec or {}).get("tick"),
        "dead_reason": dead_reason,
        "last_run_epoch": (rec or {}).get("last_run_epoch"),
    }


def _observed_age_s(path: Path, now: float) -> tuple[float | None, str, str]:
    """(age_s, basis, kind) for ANY heartbeat file, watched or not.

    Prefers the daemon's own last_run_epoch. Falls back to file mtime, because
    an unclassified file whose JSON is torn still tells the truth about WHEN it
    stopped being written. If neither can be read the age is UNMEASURED — never
    guessed, and never reported as fresh.
    """
    kind, rec = _read_json(path)
    if kind == "OK" and rec is not None:
        age = heartbeat_age_s(rec, now=now)
        if age is not None:
            return max(0.0, float(age)), "last_run_epoch", kind
    try:
        return max(0.0, now - path.stat().st_mtime), "mtime", kind
    except OSError:
        return None, "UNMEASURED", kind


def discover_unwatched(logs: Path, now: float,
                       fleet: tuple[DaemonSpec, ...] = FLEET,
                       stale_s: float = UNWATCHED_STALE_S) -> dict:
    """Scan the logs role for heartbeats FLEET does not name.

    THE SCAR THIS EXISTS FOR (measured 2026-08-30): three daemons had been dead
    for 3+ days — cosmos_runner.slot4 (3.3d), cvm_dt_clock (3.6d), cvm_dt_voice
    (3.5d) — and this watchdog reported the fleet healthy the entire time. Not
    because a check failed, but because none existed: FLEET is a hand-maintained
    tuple and none of the three appear in it. A daemon added without a FLEET
    entry is unmonitored FOREVER, silently, and the operator's only clue is a
    board that never mentions it.

    So the list of things being watched must be compared against the things that
    exist. Anything writing a heartbeat into the logs role is announcing itself
    as a daemon; if FLEET has no entry for it, that is a monitoring GAP and it
    is reported as one.

    Deliberately does NOT auto-add anything to FLEET. The correct stale_s for a
    daemon is its cadence, which this scan cannot know — inventing one would
    manufacture false alarms, and a board that cries wolf is how a real 3-day
    stall gets ignored. Discovery reports; a human classifies.

    RED only for the exact state the three corpses were in: unwatched AND
    measurably stale past `stale_s`. Unwatched-but-fresh is listed, not paged.
    Nothing is excluded from the scan — an exclusion list is the same
    hand-maintained blind spot this closes, so this daemon's own heartbeat
    appears here too, and truthfully: nobody watches it either.
    """
    watched = {s.heartbeat for s in fleet}
    try:
        found = sorted(p for p in logs.glob(HEARTBEAT_GLOB) if p.is_file())
    except OSError as e:                                             # noqa: BLE001
        # Fail-closed: a scan that cannot run is not a clean scan.
        return {"ok": False, "state": "SCAN_UNREADABLE",
                "detail": f"UNREADABLE logs role: {type(e).__name__}: {e}",
                "scanned": 0, "watched_present": 0, "unwatched": [],
                "stale_names": [], "threshold_s": stale_s}

    rows, stale_names, unmeasured = [], [], []
    for p in found:
        if p.name in watched:
            continue
        age, basis, kind = _observed_age_s(p, now)
        stale = age is not None and age > stale_s
        rows.append({
            "heartbeat": p.name,
            "age_s": None if age is None else round(age, 1),
            "age_basis": basis,
            "kind": kind,
            "stale": stale,
        })
        if stale:
            stale_names.append(p.name)
        elif age is None:
            unmeasured.append(p.name)

    ok = not stale_names
    detail = (f"scanned={len(found)} unwatched={len(rows)} "
              f"stale={len(stale_names)} threshold_s={stale_s}")
    if stale_names:
        detail = ("UNWATCHED+STALE (no FLEET entry, no signal if it dies): "
                  + ", ".join(f"{n}@{next(r['age_s'] for r in rows if r['heartbeat'] == n)}s"
                              for n in stale_names)
                  + " — classify each and give it a FLEET cadence; " + detail)
    elif unmeasured:
        detail = f"UNMEASURED age for {', '.join(unmeasured)} — " + detail
    return {
        "ok": ok,
        # Fingerprinted so a CHANGED set of offenders opens a NEW page instead
        # of hiding behind the first one's create-if-absent flag.
        "state": ("UNWATCHED_STALE:" + _fingerprint(*stale_names)) if stale_names
                 else "OK",
        "detail": detail,
        "scanned": len(found),
        "watched_present": len(found) - len(rows),
        "unwatched": rows,
        "stale_names": stale_names,
        "threshold_s": stale_s,
    }


# ----------------------------------------------------------------- goals


def _tracker_path(paths: CosmosPaths, motif_hb: dict | None) -> Path | None:
    """MOTIF_TRACKER lives in repo docs/. Prefer the runtime docs role,
    then the path the motif-driver heartbeat already recorded, then the
    module-adjacent repo docs (this file's tree). Report the one used."""
    p = paths.docs("MOTIF_TRACKER.md")
    if p.is_file():
        return p
    if motif_hb and isinstance(motif_hb.get("tracker"), str):
        cand = Path(motif_hb["tracker"])
        if cand.is_file():
            return cand
    cand = _REPO / "docs" / "MOTIF_TRACKER.md"
    if cand.is_file():
        return cand
    return None


def _wishlist_path(paths: CosmosPaths) -> Path | None:
    p = paths.docs("WISHLIST.md")
    if p.is_file():
        return p
    cand = _REPO / "docs" / "WISHLIST.md"
    return cand if cand.is_file() else None


def parse_tracker(text: str) -> list[dict]:
    rows = []
    for m in TRACKER_ROW_RE.finditer(text or ""):
        title, stage, artifact, nxt = (g.strip() for g in m.groups())
        if title.lower() == "deliverable":
            continue
        rows.append({
            "slug": _slug(title),
            "title": title,
            "stage": stage,
            "artifact": artifact,
            "next": nxt,
            "source": "motif_tracker",
            "at_gate": bool(STAGE6_RE.search(stage)),
        })
    return rows


def parse_wishlist(text: str) -> list[dict]:
    rows = []
    for m in WISH_RE.finditer(text or ""):
        mark, title = m.group(1), m.group(2).strip()
        rows.append({
            "slug": _slug(title),
            "title": title,
            "checked": mark.lower() == "x",
            "source": "wishlist",
        })
    return rows


def load_goals(paths: CosmosPaths, now: float,
               last_beat: dict | None,
               wd2_hb: dict | None,
               motif_hb: dict | None) -> dict:
    tracker_p = _tracker_path(paths, motif_hb)
    wish_p = _wishlist_path(paths)
    tracker_rows = parse_tracker(
        tracker_p.read_text(encoding="utf-8", errors="replace")
        if tracker_p else "")
    wish_rows = parse_wishlist(
        wish_p.read_text(encoding="utf-8", errors="replace")
        if wish_p else "")

    dhx_kind, dhx = _read_json(paths.state("collector", "dhx.json"))
    dhx_rows = []
    if dhx_kind == "OK" and isinstance((dhx or {}).get("rows"), list):
        dhx_rows = [r for r in dhx["rows"] if isinstance(r, dict)][-12:]

    working = []
    for j in (wd2_hb or {}).get("jobs") or []:
        if not isinstance(j, dict):
            continue
        working.append({
            "slug": j.get("slug") or _slug(str(j.get("title") or j.get("token") or "")),
            "title": j.get("title") or j.get("wishlist_line") or j.get("slug"),
            "source": "watchdog2",
            "lane": j.get("lane"),
        })
    for r in tracker_rows:
        if r["at_gate"]:
            continue
        if any(w["slug"] == r["slug"] for w in working):
            continue
        # inflight / dispatched rows are "working"
        nxt = r.get("next") or ""
        if "DISPATCHED" in nxt or "inflight" in nxt.lower() or not r["at_gate"]:
            if "DISPATCHED" in nxt or "IN FLIGHT" in (r.get("stage") or "").upper():
                working.append({
                    "slug": r["slug"], "title": r["title"],
                    "source": "motif_tracker", "stage": r["stage"],
                })

    prev_stages = ((last_beat or {}).get("goals") or {}).get("stages") or {}
    stages = {r["slug"]: r["stage"] for r in tracker_rows}
    completed = []
    for r in tracker_rows:
        prev = prev_stages.get(r["slug"])
        if prev and prev != r["stage"] and r["at_gate"] and not (
                prev and STAGE6_RE.search(str(prev))):
            completed.append({
                "slug": r["slug"], "title": r["title"],
                "from_stage": prev, "to_stage": r["stage"],
                "source": "motif_tracker",
            })
    prev_wish = ((last_beat or {}).get("goals") or {}).get("wishlist") or {}
    for r in wish_rows:
        if r["checked"] and not prev_wish.get(r["slug"]):
            if last_beat is not None:
                completed.append({
                    "slug": r["slug"], "title": r["title"],
                    "from_stage": "open", "to_stage": "checked",
                    "source": "wishlist",
                })

    # DHx rows whose result appeared after last beat
    return {
        "working": working,
        "completed": completed,
        "stages": stages,
        "wishlist": {r["slug"]: r["checked"] for r in wish_rows},
        "tracker_rows": len(tracker_rows),
        "wishlist_open": sum(1 for r in wish_rows if not r["checked"]),
        "pr_at_gate": sum(1 for r in tracker_rows if not r["at_gate"]),
        "tracker_path": str(tracker_p) if tracker_p else None,
        "wishlist_path": str(wish_p) if wish_p else None,
        "dhx_kind": dhx_kind,
        "dhx_sample": [
            {"task": r.get("task"), "assignment": r.get("assignment"),
             "status": r.get("status")}
            for r in dhx_rows[-5:]
        ],
        "wd2_assigned": (wd2_hb or {}).get("assigned_this_pass"),
        "wd2_flagged": (wd2_hb or {}).get("open_flagged"),
    }


# ----------------------------------------------------------------- extras (queue, disk, backup, audit)


ROUTE_STALL_S = 4 * 3600.0          # alive but producing nothing for this long = RED


def _paused(paths) -> bool:
    """True when a HOLD is set. A deliberate stop must not read as a stall --
    and an unreadable flag is treated as PAUSED (fail-closed), because the one
    thing worse than a missed alarm is a false one that trains you to ignore
    the board."""
    flag = Path(paths.state()) / 'control' / 'PAUSE.flag'
    try:
        d = json.loads(flag.read_text(encoding='utf-8') or '{}')
    except FileNotFoundError:
        return False
    except Exception:  # noqa: BLE001
        return True
    return str(d.get('state', 'PAUSED')).upper() != 'RUNNING'


def _newest_result_epoch(queue: Path) -> tuple[float | None, str | None]:
    """mtime of the newest job RECEIPT anywhere under the queue, and its name.

    A receipt is the one artifact that cannot be produced by a daemon merely
    ticking: something actually ran and returned. That is why progress is
    measured here and not from any heartbeat field.
    """
    newest_t: float | None = None
    newest_n: str | None = None
    try:
        for p in queue.rglob("*_result.json"):
            try:
                m = p.stat().st_mtime
            except OSError:
                continue
            if newest_t is None or m > newest_t:
                newest_t, newest_n = m, p.name
    except OSError:
        return None, None
    return newest_t, newest_n


def _tls_integrity_row(paths, now: float) -> dict:
    """Is the certificate on the wire the certificate we serve?

    Scar 2026-08-30: Avast Web/Mail Shield was terminating and re-signing TLS on
    this host -- on loopback AND on the LAN address, so the CVM phone client
    talking to this PC "over TLS" was talking through an interceptor. An
    operator-supplied trusted cert (the Tailscale-issued path this code is built
    for) never reached a client as itself, and certificate pinning could not work.

    It was found by a test. That is the wrong place for it to live: a test says
    something about a fixture, and only when someone runs it. Whether the bytes
    on your wire are yours is an OPERATIONAL fact about this machine right now,
    so it belongs on the board beside everything else that can silently stop
    being true.

    Mints a throwaway cert, serves it on an ephemeral loopback port, connects,
    and compares serial numbers. Sub-second, no network egress, nothing
    persisted. Any failure to complete the probe is reported as unknown, never
    as clean -- an interceptor must not be able to hide behind a broken check.
    """
    import socket
    import ssl
    import tempfile
    import threading

    rec = {"ok": True, "detail": "not probed", "intercepted": None}
    try:
        from cosmos_service import _ensure_cert
        from cosmos_kernel import Kernel, install
    except Exception as e:                                           # noqa: BLE001
        rec.update({"ok": True, "detail": f"probe unavailable: {type(e).__name__}"})
        return rec

    td = Path(tempfile.mkdtemp(prefix="tls_probe_"))
    try:
        mint = td / "M"
        install(mint, tree_id="tls-probe")
        pair = _ensure_cert(Kernel(mint, worker="core"), "127.0.0.1")
        if not pair:
            rec.update({"detail": "no cert generator available"})
            return rec
        expect = ssl._ssl._test_decode_cert(str(pair[0]))["serialNumber"]

        srv = socket.socket()
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 0))
        port = srv.getsockname()[1]
        srv.listen(1)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(pair[0], pair[1])
        wrapped = ctx.wrap_socket(srv, server_side=True)

        def _accept():
            try:
                conn, _ = wrapped.accept()
                conn.close()
            except Exception:                                        # noqa: BLE001
                pass

        threading.Thread(target=_accept, daemon=True).start()
        cctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        cctx.check_hostname = False
        cctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection(("127.0.0.1", port), timeout=8) as raw:
            with cctx.wrap_socket(raw, server_hostname="127.0.0.1") as t:
                der = t.getpeercert(binary_form=True)

        served_pem = td / "served.pem"
        served_pem.write_text(ssl.DER_cert_to_PEM_cert(der), encoding="utf-8")
        got = ssl._ssl._test_decode_cert(str(served_pem))
        same = got["serialNumber"] == expect
        issuer = " ".join(v for rdn in (got.get("issuer") or ()) for _, v in rdn)

        if same:
            rec.update({"ok": True, "intercepted": False,
                        "detail": "clean: the served cert is the cert we loaded"})
        else:
            rec.update({
                "ok": False,
                "intercepted": True,
                "detail": ("TLS INTERCEPTED: the cert on the wire was re-signed by "
                           + issuer + " -- COSMOS serves the cert it is given, so "
                           "certificate pinning cannot work and an operator-supplied "
                           "trusted cert never reaches a client as itself. Exclude "
                           "this host from the interceptor to restore end-to-end TLS."),
                "issuer": issuer,
                "expected_serial": expect,
                "served_serial": got["serialNumber"],
            })
    except Exception as e:                                           # noqa: BLE001
        # A probe that cannot complete reports UNKNOWN, never clean.
        rec.update({"ok": True, "intercepted": None,
                    "detail": f"probe inconclusive: {type(e).__name__}: {e}"})
    return rec


def _route_progress_row(paths, now: float, motif: dict | None,
                        stall_s: float = ROUTE_STALL_S,
                        paused: bool = False) -> dict:
    """Is the route ADVANCING, or only ALIVE?

    THE SCAR THIS EXISTS FOR (2026-08-26 -> 2026-08-30): the motif route produced
    nothing for three days while every heartbeat stayed green and this board
    reported healthy. Nothing was broken in a way anything looked for:

      * The driver ticked on time, so it was never STALE.
      * Its heartbeat said ok:true, tick:"once" -- with dispatched:0 sitting
        beside it as one field among many.
      * The tracker called all ten rows "inflight", and the goals logic counted
        an inflight row as WORKING. The claim WAS the evidence.

    So the fleet was alive, and being alive was read as being productive.

    This row refuses that inference. Progress is bound to an emitted receipt --
    the system's own canon: rc=0 is not done; bind every claim to a real emitted
    artifact. A self-reported "inflight" is a claim, not a measurement, and is
    explicitly NOT accepted as progress here.

    Fires RED on the exact signature of the 3-day wedge: the driver reporting
    rows it will not dispatch, while no receipt has landed.
    """
    queue = Path(paths.queue())
    newest_t, newest_n = _newest_result_epoch(queue)
    age = None if newest_t is None else max(0.0, now - newest_t)

    dispatched = None
    skipped = None
    rows = None
    if isinstance(motif, dict):
        dispatched = motif.get("dispatched")
        skipped = motif.get("skipped")
        rows = motif.get("rows")

    # The wedge signature: rows exist, none dispatch, all are claimed inflight.
    wedged_claim = (
        isinstance(dispatched, int) and dispatched == 0
        and isinstance(skipped, int) and isinstance(rows, int)
        and rows > 0 and skipped >= rows
    )
    stalled = age is not None and age > stall_s
    no_receipts_ever = newest_t is None

    ok = True
    why = "advancing"
    if paused:
        ok, why = True, "paused (PAUSE.flag set) - stall not counted"
    elif no_receipts_ever and not wedged_claim:
        # A tree that has never run anything is NEW, not stalled. Calling that
        # RED would be a false alarm on every fresh install, and a board that
        # cries wolf is exactly how a real 3-day stall got ignored.
        ok, why = True, "no receipts yet (nothing has run in this tree)"
    elif no_receipts_ever:
        ok = False
        why = (f"WEDGED: driver reports {rows} rows, dispatched 0, skipped "
               f"{skipped} - all claimed inflight, yet this tree has never "
               f"produced a receipt")
    elif wedged_claim and stalled:
        ok = False
        why = (f"WEDGED: driver reports {rows} rows, dispatched 0, skipped "
               f"{skipped} (all claimed inflight) and no receipt in "
               f"{age / 3600.0:.1f}h - a claim is not progress")
    elif stalled:
        ok = False
        why = (f"STALLED: fleet alive but no job receipt in {age / 3600.0:.1f}h "
               f"(threshold {stall_s / 3600.0:.1f}h)")
    elif wedged_claim:
        why = (f"watch: dispatched 0 of {rows} rows this tick, but a receipt "
               f"landed {age / 3600.0:.1f}h ago")

    return {
        "ok": ok,
        "detail": why,
        "last_receipt_age_s": None if age is None else round(age, 1),
        "last_receipt": newest_n,
        "stall_threshold_s": stall_s,
        "motif_dispatched": dispatched,
        "motif_skipped": skipped,
        "motif_rows": rows,
        "wedge_signature": bool(wedged_claim),
    }


def _queue_counts(queue: Path) -> dict:
    pending = running = failed = done = broke = 0
    skip = {"__pycache__", "logs", "returns", "manifests"}
    if not queue.is_dir():
        return {"ok": False, "detail": "queue role missing",
                "pending": 0, "running": 0, "failed": 0, "done": 0, "broke": 0}
    for dirpath, dirnames, filenames in os.walk(queue):
        base = Path(dirpath).name.lower()
        dirnames[:] = [d for d in dirnames if d not in skip and not d.startswith(".")]
        for name in filenames:
            low = name.lower()
            if base == "failed":
                failed += 1
            elif base == "running":
                running += 1
            elif base == "done":
                done += 1
            elif name.endswith(".py") and base not in skip:
                pending += 1
            if "broke" in low:
                broke += 1
    draining = pending == 0 or running > 0
    # failed/ is an outcome archive; a BROKE loop is the pageable fault
    # (wishlist: "job outcomes (no BROKE loop)"). Historical failed jobs
    # must not page every hour.
    return {
        "ok": broke == 0,
        "detail": (f"pending={pending} running={running} failed={failed} "
                   f"done={done} broke={broke}"),
        "pending": pending, "running": running, "failed": failed,
        "done": done, "broke": broke, "draining": draining,
    }


def _disk_row(root: Path, warn_pct: float,
              disk_usage: DiskUsage | None = None) -> dict:
    fn = disk_usage or shutil.disk_usage
    try:
        u = fn(str(root))
    except OSError as e:
        return {"ok": False, "detail": f"UNREADABLE {type(e).__name__}: {e}",
                "state": "UNREADABLE"}
    total, used, free = int(u.total), int(u.used), int(u.free)
    pct_free = (free / total * 100.0) if total else 0.0
    warn = pct_free < float(warn_pct)
    return {
        "ok": not warn,
        "detail": f"pct_free={pct_free:.2f} warn_below={warn_pct}",
        "total_bytes": total, "used_bytes": used, "free_bytes": free,
        "pct_free": round(pct_free, 2), "warn": warn,
        "state": "LOW" if warn else "OK",
    }


def _backup_row(logs: Path, now: float) -> dict:
    kind, rec = _heartbeat_kind(logs / "backup_clock_heartbeat.json")
    age = heartbeat_age_s(rec, now=now) if rec else None
    stale = age is None or age > BACKUP_STALE_S or kind != "OK"
    state = (rec or {}).get("state")
    failed = state in ("FAILED", "REFUSED") or (rec or {}).get("ok") is False
    return {
        "ok": (not stale) and (not failed),
        "detail": f"kind={kind} age_s={None if age is None else round(age, 1)} "
                  f"state={state}",
        "age_s": None if age is None else round(age, 1),
        "state": state, "kind": kind,
    }


def _audit_row(state: Path, now: float) -> dict:
    cands = sorted(state.glob("principles_audit*_result.json"),
                   key=lambda p: p.stat().st_mtime if p.exists() else 0,
                   reverse=True)
    if not cands:
        cands = sorted(state.glob("audit_*_result.json"),
                       key=lambda p: p.stat().st_mtime if p.exists() else 0,
                       reverse=True)
    if not cands:
        return {"ok": False, "detail": "NO_AUDIT_ARTIFACT", "pass_count": None}
    p = cands[0]
    kind, rec = _read_json(p)
    if kind != "OK" or not rec:
        return {"ok": False, "detail": f"{kind} {p.name}", "path": p.name}
    age = now - p.stat().st_mtime
    pass_count = rec.get("pass_count")
    fail_zero = rec.get("fail_zero")
    if fail_zero is None and "FAIL" in rec:
        fail_zero = rec.get("FAIL") == 0
    ok = bool(fail_zero) and int(pass_count or 0) >= 10 and age <= AUDIT_STALE_S
    return {
        "ok": ok,
        "detail": (f"{p.name} pass_count={pass_count} fail_zero={fail_zero} "
                   f"age_s={round(age, 1)}"),
        "path": p.name, "pass_count": pass_count, "fail_zero": fail_zero,
        "age_s": round(age, 1),
    }


# ----------------------------------------------------------------- slack + pages


def default_http_post(url: str, body: bytes, timeout_s: float = 10.0) -> dict:
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read()[:300]
            return {"ok": 200 <= getattr(resp, "status", 200) < 300,
                    "status": getattr(resp, "status", 200),
                    "body": raw.decode("utf-8", "replace")}
    except (urllib.error.URLError, OSError, TimeoutError, ValueError) as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def format_routine(board: dict) -> str:
    daemons = board.get("daemons") or {}
    alive = sum(1 for d in daemons.values() if d.get("ok"))
    total = len(daemons)
    goals = board.get("goals") or {}
    working = [g.get("title") or g.get("slug") for g in goals.get("working") or []]
    done = [g.get("title") or g.get("slug") for g in goals.get("completed") or []]
    work_s = ", ".join(str(x) for x in working[:8]) or "(none named)"
    done_s = ", ".join(str(x) for x in done[:8]) or "(none this beat)"
    q = board.get("queue") or {}
    disk = board.get("disk") or {}
    return (
        f"COSMOS health {board.get('verdict')} · daemons {alive}/{total} fresh · "
        f"working: {work_s} · completed since last: {done_s} · "
        f"queue {q.get('detail', '?')} · disk {disk.get('detail', '?')} · "
        f"prs-at-gate={goals.get('pr_at_gate')}"
    )


def format_page(exceptions: list[dict]) -> str:
    bits = []
    for e in exceptions[:8]:
        bits.append(
            f"{e.get('kind')} id={e.get('id')} {e.get('detail') or ''}".strip()
        )
    return "PAGE COSMOS · " + " · ".join(bits) if bits else "PAGE COSMOS · (empty)"


def post_slack(url: str | None, url_kind: str, text: str,
               http_post: HttpPost | None = None) -> dict:
    if not url:
        return {"ok": False, "kind": url_kind or "MISSING",
                "detail": "no incoming webhook under config role — REFUSED"}
    body = json.dumps({"text": text}, separators=(",", ":")).encode("utf-8")
    fn = http_post or default_http_post
    rec = fn(url, body)
    rec.setdefault("kind", "POST")
    rec["chars"] = len(text)
    return rec


def _page_dir(paths: CosmosPaths) -> Path:
    d = paths.state("health", "pages")
    d.mkdir(parents=True, exist_ok=True)
    return d


def emit_pages(paths: CosmosPaths, exceptions: list[dict], now: float) -> list[dict]:
    """Create-if-absent page files keyed by fingerprint. A still-dead
    daemon with the same last_run_epoch (or MISSING) will not write a
    second file. Recovery + re-death changes last_run_epoch → new page."""
    out = []
    pdir = _page_dir(paths)
    for exc in exceptions:
        fp = _fingerprint(
            str(exc.get("kind") or ""),
            str(exc.get("id") or ""),
            str(exc.get("last_run_epoch") or exc.get("dead_reason") or "none"),
        )
        dest = pdir / f"{fp}.json"
        rec = {
            "schema": SCHEMA,
            "kind": "PAGE",
            "fingerprint": fp,
            "measured_at": _iso_now(),
            "measured_epoch": int(now),
            "exception": exc,
        }
        created = False
        if not dest.exists():
            atomic_json(dest, rec)
            created = True
        out.append({
            "fingerprint": fp,
            "path": str(dest),
            "created": created,
            "id": exc.get("id"),
            "kind": exc.get("kind"),
        })
    flag = {
        "schema": SCHEMA,
        "open": bool(exceptions),
        "count": len(exceptions),
        "measured_at": _iso_now(),
        "measured_epoch": int(now),
        "ids": [e.get("id") for e in exceptions],
        "kinds": sorted({e.get("kind") for e in exceptions}),
    }
    atomic_json(paths.state("health", PAGE_FLAG_NAME), flag)
    return out


# ----------------------------------------------------------------- tick


def _exceptions_from(daemons: dict, extras: dict, tick_error: str | None) -> list[dict]:
    excs = []
    if tick_error:
        excs.append({"kind": "EXCEPTION", "id": "tick", "detail": tick_error[:400],
                     "dead_reason": "RAISED", "last_run_epoch": None})
    for did, row in daemons.items():
        if not row.get("ok"):
            excs.append({
                "kind": "DEAD_DAEMON",
                "id": did,
                "detail": row.get("detail"),
                "dead_reason": row.get("dead_reason"),
                "last_run_epoch": row.get("last_run_epoch"),
                "age_s": row.get("age_s"),
            })
    for name, row in extras.items():
        if isinstance(row, dict) and row.get("ok") is False:
            excs.append({
                "kind": "RED_ROW",
                "id": name,
                "detail": row.get("detail"),
                "dead_reason": row.get("state") or "RED",
                "last_run_epoch": None,
            })
    return excs


def poll_once(root: str, *, polls: int = 0,
              interval_s: float = DEFAULT_INTERVAL_S,
              now: float | None = None,
              slack_post: HttpPost | None = None,
              task_query: TaskQuery | None = None,
              disk_usage: DiskUsage | None = None,
              tls_probe=None,
              skip_slack: bool = False) -> dict:
    paths = CosmosPaths(root)
    now = float(now if now is not None else time.time())
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    health_state = paths.state("health")
    health_state.mkdir(parents=True, exist_ok=True)

    cfg = load_config(paths)
    last_kind, last_beat = _read_json(health_state / LAST_BEAT_NAME)
    if last_kind not in ("OK", "MISSING"):
        last_beat = None  # torn last-beat is not repaired; start a new snapshot

    daemons: dict[str, dict] = {}
    for spec in FLEET:
        daemons[spec.id] = poll_daemon(spec, logs, now, task_query=task_query)

    wd2 = read_heartbeat(logs / "watchdog2_heartbeat.json")
    motif = read_heartbeat(logs / "motif_driver_heartbeat.json")
    goals = load_goals(paths, now, last_beat, wd2, motif)

    extras = {
        "queue": _queue_counts(paths.queue()),
        "disk": _disk_row(paths.root, float(cfg.get("disk_warn_pct_free")
                                            or DISK_WARN_PCT_FREE),
                          disk_usage=disk_usage),
        "backup": _backup_row(logs, now),
        "audit": _audit_row(paths.state(), now),
        # What is FLEET not watching? A hand-maintained tuple must not be the
        # only thing standing between a dead daemon and silence.
        "unwatched": discover_unwatched(
            logs, now, stale_s=float(cfg.get("unwatched_stale_s")
                                     or UNWATCHED_STALE_S)),
        # Bound to emitted receipts, never to a self-reported "inflight".
        # This is the row that would have caught the 2026-08-26 wedge on day
        # one instead of three days later.
        # Injectable like task_query/disk_usage: a fixture cannot control
        # whether the HOST it runs on has a TLS interceptor installed, and
        # a suite that fails because of the machine it runs on teaches you
        # to ignore it. Production passes None and really probes.
        "tls_integrity": (tls_probe(paths, now) if tls_probe
                          else _tls_integrity_row(paths, now)),
        "route_progress": _route_progress_row(
            paths, now, motif,
            stall_s=float(cfg.get("route_stall_s") or ROUTE_STALL_S),
            paused=_paused(paths),
        ),
    }

    reds = {k: v for k, v in daemons.items() if not v.get("ok")}
    extra_reds = {k: v for k, v in extras.items() if not v.get("ok")}
    n_red = len(reds) + len(extra_reds)
    verdict = "GREEN" if n_red == 0 else f"RED x{n_red}"

    exceptions = _exceptions_from(daemons, extras, None)
    pages = emit_pages(paths, exceptions, now) if exceptions else emit_pages(
        paths, [], now)

    board = {
        "schema": SCHEMA,
        "measured_at": _iso_now(),
        "measured_epoch": int(now),
        "verdict": verdict,
        "reds": sorted(list(reds) + list(extra_reds)),
        "daemons": daemons,
        "goals": {
            "working": goals["working"],
            "completed": goals["completed"],
            "pr_at_gate": goals["pr_at_gate"],
            "wishlist_open": goals["wishlist_open"],
            "tracker_path": goals["tracker_path"],
            "dhx_sample": goals.get("dhx_sample") or [],
            "wd2_assigned": goals["wd2_assigned"],
            "wd2_flagged": goals["wd2_flagged"],
        },
        "queue": extras["queue"],
        "disk": extras["disk"],
        "backup": extras["backup"],
        "audit": extras["audit"],
        # On the board, not only in the exception: the operator classifies
        # these by reading them.
        "unwatched": extras["unwatched"],
        "pages": pages,
        "tree_id": paths.sentinel.tree_id,
        "worker": WORKER,
        "pid": os.getpid(),
        "config_error": cfg.get("_config_error"),
    }

    slack = {"ok": False, "kind": "SKIPPED", "detail": "skip_slack"}
    if not skip_slack:
        url, url_kind = load_slack_webhook(
            paths, str(cfg.get("slack_webhook_file") or SLACK_WEBHOOK_FILE))
        routine = format_routine(board)
        text = (format_page(exceptions) + " | " + routine) if exceptions else routine
        slack = post_slack(url, url_kind, text, http_post=slack_post)
        slack["mode"] = "PAGE" if exceptions else "ROUTINE"
        slack["text"] = text

    board["slack"] = {k: slack.get(k) for k in
                      ("ok", "kind", "mode", "detail", "status", "error", "chars")
                      if k in slack or slack.get(k) is not None}

    board_path = health_state / BOARD_NAME
    atomic_json(board_path, board)

    snapshot = {
        "schema": SCHEMA,
        "measured_at": board["measured_at"],
        "measured_epoch": board["measured_epoch"],
        "verdict": verdict,
        "goals": {
            "stages": goals["stages"],
            "wishlist": goals["wishlist"],
            "working": [w.get("slug") for w in goals["working"]],
            "completed": [c.get("slug") for c in goals["completed"]],
        },
        "reds": board["reds"],
    }
    atomic_json(health_state / LAST_BEAT_NAME, snapshot)

    extra_hb = {
        "schema": SCHEMA,
        "tick": "once",
        "state": "RUNNING",
        "verdict": verdict,
        "reds": n_red,
        "alive": sum(1 for d in daemons.values() if d.get("ok")),
        "fleet": len(daemons),
        "page_count": sum(1 for p in pages if p.get("created")),
        "page_open": bool(exceptions),
        "slack_mode": slack.get("mode"),
        "slack_ok": slack.get("ok"),
        "board": str(board_path),
        "tree_id": paths.sentinel.tree_id,
    }
    hb = write_heartbeat(logs / HEARTBEAT_NAME, WORKER, extra=extra_hb,
                         polls=polls, interval_s=interval_s)
    return {
        "ok": n_red == 0,
        "verdict": verdict,
        "board": board,
        "board_path": str(board_path),
        "heartbeat": hb,
        "heartbeat_path": str(logs / HEARTBEAT_NAME),
        "pages": pages,
        "slack": slack,
        "exceptions": exceptions,
        "cfg": {k: cfg[k] for k in cfg if not k.startswith("_")},
    }


def ensure_task(task_name: str, tr: str, sc: str,
                mo: int | None = None,
                task_query: TaskQuery | None = None,
                task_create: Callable | None = None) -> dict:
    """Idempotent: query first, create only if absent. Never /f-replace
    a live task (create_task uses /f internally — we must not call it
    when the task already exists)."""
    q = query_task_safe(task_name, task_query=task_query)
    if q.get("registered"):
        return {"name": task_name, "created": False, "already": True,
                "ok": True, "query": q}
    fn = task_create or create_task
    rec = fn(task_name, tr, sc, mo=mo)
    rec = dict(rec or {})
    rec.update({"name": task_name, "created": bool(rec.get("ok")),
                "already": False})
    return rec


def standup(root: str, interval_s: float = DEFAULT_INTERVAL_S,
            task_query: TaskQuery | None = None,
            task_create: Callable | None = None) -> dict:
    paths = CosmosPaths(root)
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once")
    hourly = ensure_task(TASK_NAME, tr, "HOURLY",
                         task_query=task_query, task_create=task_create)
    logon = ensure_task(TASK_NAME_LOGON, tr, "ONLOGON",
                        task_query=task_query, task_create=task_create)
    once = poll_once(root, interval_s=interval_s, task_query=task_query,
                     skip_slack=False)
    return {
        "schema": SCHEMA,
        "started": "standup",
        "task_hourly": hourly,
        "task_logon": logon,
        "once": {"verdict": once["verdict"],
                 "heartbeat_path": once["heartbeat_path"],
                 "board_path": once["board_path"]},
        "pythonw": pythonw_exe(),
        "task_name": TASK_NAME,
        "windowless": Path(pythonw_exe()).name.lower().startswith("pythonw")
                      or os.name != "nt",
    }


def status(root: str) -> dict:
    paths = CosmosPaths(root)
    rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
    age = heartbeat_age_s(rec)
    kind, board = _read_json(paths.state("health", BOARD_NAME))
    return {
        "path": str(paths.logs(HEARTBEAT_NAME)),
        "age_s": age,
        "fresh": age is not None and age < DEFAULT_INTERVAL_S * 2,
        "heartbeat": rec,
        "board_kind": kind,
        "verdict": (board or {}).get("verdict") if kind == "OK" else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_health_watchdog")
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (sentinel-verified). No default.")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    a = ap.parse_args()
    if a.status:
        rec = status(a.root)
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("fresh") else 2
    if a.standup:
        r = standup(a.root, a.interval)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("once") or {}).get("verdict") else 2
    if a.once:
        r = poll_once(a.root, interval_s=a.interval)
        slim = {k: r[k] for k in r if k != "board"}
        slim["verdict"] = r["verdict"]
        slim["reds"] = (r.get("board") or {}).get("reds")
        slim["slack_text"] = (r.get("slack") or {}).get("text")
        print(json.dumps(slim, indent=1, default=str))
        # rc=0 is not the proof; still exit 0 on a successful tick (board
        # emitted) even when RED — RED is a finding, not a crash. Exit 2
        # only when we failed to emit.
        return 0 if r.get("heartbeat_path") else 2
    ap.error("one of --once / --standup / --status is required "
             "(hourly schtask fires --once; there is no hidden default root)")
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2)
    except HealthWatchdogRefusal as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2)
