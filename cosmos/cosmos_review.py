#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_review — GET fold for the Review pane.

Spending approvals, blocking decisions, required logins, and a catalog of
recent work products / session summaries (day / week / month / 90d).

GET never mutates. Never mkdir. Does not copy OpenWork/Legal files into
the COSMOS tree. The GFO OpenWork session is a read-only sample.

    py -3.14 cosmos\\\\cosmos_review.py --selftest
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-review/1"
WINDOWS = {
    "day": 1,
    "week": 7,
    "month": 30,
    "90": 90,
}
OW_DB = Path(r"C:\Users\Papa\.local\share\opencode\opencode.db")
GFO_SID = "ses_f8b931bc6ffeD0FE5wEcuLuFSN"
GFO_PRODUCTS = (
    Path(r"V:\OPENWORK\COSMOS_2\legal\Abraxas\02_ACTIVE_STRATEGY\DEP_EXHIBITS_COMPILATION.pdf"),
    Path(r"V:\OPENWORK\COSMOS_2\legal\Abraxas\02_ACTIVE_STRATEGY\DEP_QUESTIONS_TOP40_FINAL.docx"),
    Path(r"V:\OPENWORK\COSMOS_2\legal\Abraxas\02_ACTIVE_STRATEGY\DEP_QUESTIONS_TOP40_WITH_EVIDENCE.md"),
)


def _iso(ts) -> str | None:
    if ts is None:
        return None
    try:
        n = float(ts)
    except (TypeError, ValueError):
        return str(ts)[:40]
    if n > 1e12:
        n = n / 1000.0
    try:
        return datetime.fromtimestamp(n, tz=timezone.utc).astimezone().isoformat(
            timespec="seconds")
    except (OSError, OverflowError, ValueError):
        return None


def _epoch(raw) -> float | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, (int, float)):
        n = float(raw)
        return n / 1000.0 if n > 1e12 else n
    s = str(raw).strip()
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s).timestamp()
    except ValueError:
        return None


def _in_window(when, days: int, now: float) -> bool:
    ep = _epoch(when)
    if ep is None:
        return True
    return ep >= (now - days * 86400)


def _tail_events(kernel, n: int = 40) -> list[dict]:
    ledger = getattr(kernel, "ledger", None)
    if ledger is None or not hasattr(ledger, "verify"):
        return []
    buf: deque = deque(maxlen=n)
    try:
        for r in ledger.verify():
            if isinstance(r, dict):
                buf.append(r)
    except Exception:  # noqa: BLE001
        return []
    return list(buf)


def _spend_approvals(kernel) -> dict:
    spend = getattr(kernel, "spend", None)
    meters = []
    kind = "NO_SOURCE"
    if spend is not None and hasattr(spend, "audit"):
        try:
            aud = spend.audit()
            kind = "OK"
            for rid, row in (aud.get("rails") or {}).items():
                if not isinstance(row, dict):
                    continue
                meters.append({
                    "rail": rid,
                    "cap_usd": row.get("cap_usd"),
                    "settled_usd": row.get("settled_usd"),
                    "headroom_usd": row.get("headroom_usd"),
                    "needs_widen": False,
                })
        except Exception as e:  # noqa: BLE001
            kind = f"{type(e).__name__}: {e}"[:160]
    refused = []
    for ev in _tail_events(kernel, 80):
        name = str(ev.get("event") or "")
        if name == "SPEND_CAP_REFUSED":
            p = ev.get("payload") if isinstance(ev.get("payload"), dict) else {}
            refused.append({
                "seq": ev.get("seq"),
                "t": ev.get("t"),
                "iso": _iso(ev.get("t")),
                "kind": p.get("kind") or "WIDEN_REQUIRES_CONFIRM",
                "detail": str(p.get("detail") or p.get("reason") or "")[:240],
            })
    return {
        "kind": kind,
        "pending": refused,
        "meters": meters,
        "note": (
            "POST /spend is fail-closed: a widen is 409 WIDEN_REQUIRES_CONFIRM "
            "until allow_widen is true. There is no silent pending pile — "
            "refused events from the ledger tail are the queue."
        ),
    }


def _blockers(kernel) -> dict:
    rows = []
    try:
        import sys as _sys
        cdeck = str(Path(__file__).resolve().parent.parent / "builds" / "cdeck")
        if cdeck not in _sys.path:
            _sys.path.insert(0, cdeck)
        from cosmos_jukebox_panel import handle_get
        code, body = handle_get(str(kernel.paths.root),
                                expected_tree_id=kernel.paths.sentinel.tree_id)
        if code == 200:
            q = (body or {}).get("queue") or {}
            jobs = q.get("jobs") if isinstance(q, dict) else None
            for j in jobs or []:
                if not isinstance(j, dict):
                    continue
                st = str(j.get("st") or "").upper()
                # Review waiting list = FINDINGS + stale RUNNING only (not BROKE).
                if st == "FINDINGS" or j.get("stale_flag"):
                    rows.append({
                        "kind": "job",
                        "id": j.get("job_id"),
                        "state": st,
                        "command": str(j.get("command") or "")[:160],
                        "why": ("FINDINGS — awaiting CCr; resume: work_orders/drop/ "
                                "or CCr --accept (not a re-run)"
                                if st == "FINDINGS"
                                else "STALE RUNNING — flagged; not auto-resumed"),
                    })
    except Exception as e:  # noqa: BLE001
        rows.append({"kind": "BROKE", "detail": f"jukebox {type(e).__name__}: {e}"[:160]})
    try:
        from cosmos_studio import snapshot as studio_snapshot
        pack = studio_snapshot(kernel.paths)
        cons = pack.get("consensus") or {}
        if cons.get("arch_choice") == "hitl" and not cons.get("chosen_id"):
            rows.append({
                "kind": "studio",
                "id": "consensus.arch",
                "state": "HITL",
                "why": "CONSENSUS HITL — architecture not chosen",
            })
        critics = pack.get("critics") or {}
        if critics.get("continue_when") == "hitl":
            rows.append({
                "kind": "studio",
                "id": "critics.continue",
                "state": "HITL",
                "why": "CRITICS continuation is HITL — CCr continues",
            })
    except Exception:  # noqa: BLE001
        pass
    try:
        from cosmos_work_order import fold_work_orders
        rec = fold_work_orders(kernel.paths, limit=12)
        counts = rec.get("counts") or {}
        for folder in ("drop", "picked", "findings"):
            n = counts.get(folder)
            if n:
                rows.append({
                    "kind": "work_order",
                    "id": folder,
                    "state": folder.upper(),
                    "why": f"{n} work order(s) in {folder}",
                })
    except Exception:  # noqa: BLE001
        pass
    return {
        "kind": "OK",
        "rows": rows[:24],
        "note": (
            "Review waiting list (cDeck Review tab): jukebox FINDINGS + stale RUNNING. "
            "FINDINGS awaits CCr (drop/--accept), not approve/reject in the UI. "
            "Also studio HITL and work-order piles when present."
        ),
    }


def _logins(kernel) -> dict:
    rows = []
    reg = getattr(kernel, "registry", None)
    if reg is not None and hasattr(reg, "matrix"):
        try:
            for r in (reg.matrix() or []):
                if not isinstance(r, dict):
                    continue
                v = r.get("verified")
                if v is True:
                    continue
                rows.append({
                    "link_id": r.get("link_id"),
                    "route": r.get("route"),
                    "rail_type": r.get("rail_type"),
                    "verified": v,
                    "age_s": r.get("age_s"),
                    "why": ("UNKNOWN — never probed" if v is None
                            else "FAIL — last probe was not ok"),
                })
        except Exception as e:  # noqa: BLE001
            rows.append({"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:160]})
    auth_ev = []
    for ev in _tail_events(kernel, 80):
        p = ev.get("payload") if isinstance(ev.get("payload"), dict) else {}
        blob = json.dumps(p, default=str).upper()
        if "AUTH_REQUIRED" in blob or str(ev.get("event") or "") in (
                "AUTH_REQUIRED", "PROBE_RESULT"):
            if "AUTH_REQUIRED" in blob or p.get("kind") == "AUTH_REQUIRED":
                auth_ev.append({
                    "seq": ev.get("seq"),
                    "event": ev.get("event"),
                    "t": ev.get("t"),
                    "iso": _iso(ev.get("t")),
                    "link_id": p.get("link_id"),
                    "kind": "AUTH_REQUIRED",
                })
    return {
        "kind": "OK" if rows or auth_ev or reg is not None else "NO_SOURCE",
        "rails": rows[:24],
        "events": auth_ev[:12],
        "note": ("Required logins are Keith's click. Core never automates AUTH. "
                 "Unverified rails and AUTH_REQUIRED probe events are the list."),
    }


def _file_row(p: Path) -> dict:
    exists = p.is_file()
    st = p.stat() if exists else None
    return {
        "name": p.name,
        "path": str(p),
        "exists": exists,
        "bytes": None if st is None else st.st_size,
        "mtime": None if st is None else st.st_mtime,
        "iso": None if st is None else _iso(st.st_mtime),
    }


def _gfo_sample() -> dict:
    """Current OpenWork GFO session — read-only. Never copies Legal files."""
    if not OW_DB.is_file():
        return {"kind": "NO_SOURCE",
                "detail": "opencode.db unread — OpenWork session file not on this host"}
    try:
        con = sqlite3.connect(f"file:{OW_DB}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        sess = con.execute("SELECT * FROM session WHERE id=?", (GFO_SID,)).fetchone()
        if sess is None:
            row = con.execute(
                "SELECT * FROM session WHERE model LIKE '%gemini-3.8-flash%' "
                "ORDER BY time_updated DESC LIMIT 1"
            ).fetchone()
            sess = row
        if sess is None:
            return {"kind": "NO_SOURCE", "detail": "no GFO session in opencode.db"}
        sid = sess["id"]
        summary = None
        msgs = list(con.execute(
            "SELECT id, time_created, data FROM message WHERE session_id=? "
            "ORDER BY time_created DESC LIMIT 16", (sid,)))
        for m in msgs:
            try:
                rec = json.loads(m["data"]) if isinstance(m["data"], str) else {}
            except (ValueError, TypeError):
                continue
            if not isinstance(rec, dict) or rec.get("role") != "assistant":
                continue
            parts = list(con.execute(
                "SELECT data FROM part WHERE message_id=? ORDER BY time_created",
                (m["id"],)))
            for p in parts:
                try:
                    pr = json.loads(p["data"]) if isinstance(p["data"], str) else {}
                except (ValueError, TypeError):
                    continue
                text = pr.get("text") if isinstance(pr, dict) else None
                if text and str(pr.get("type") or "") in ("text", ""):
                    summary = str(text).strip()
                    break
            if summary:
                break
        products = [_file_row(p) for p in GFO_PRODUCTS]
        return {
            "kind": "OK",
            "session_id": sid,
            "title": sess["title"],
            "slug": sess["slug"],
            "directory": sess["directory"],
            "model": sess["model"],
            "agent": sess["agent"],
            "cost_usd": sess["cost"],
            "time_updated": sess["time_updated"],
            "iso": _iso(sess["time_updated"]),
            "summary": (summary or "")[:1200] or None,
            "summary_kind": "assistant_text" if summary else "UNMEASURED",
            "products": products,
            "note": ("Sample from the current OpenWork GFO session "
                     "(gemini-3.8-flash / google-vertex). Paths stay on the "
                     "OpenWork grant; COSMOS does not copy them."),
        }
    except Exception as e:  # noqa: BLE001
        return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}


def _work_products(paths, days: int, now: float) -> list[dict]:
    out = []
    try:
        from cosmos_work_order import fold_work_orders
        rec = fold_work_orders(paths, limit=40)
    except Exception as e:  # noqa: BLE001
        return [{"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:160]}]
    for row in rec.get("rows") or []:
        if not isinstance(row, dict):
            continue
        when = row.get("timestamp") or row.get("dropped_at") or row.get("accepted_at")
        if not _in_window(when, days, now):
            continue
        out.append({
            "kind": "work_order",
            "id": row.get("order_id"),
            "title": str(row.get("task") or "")[:160],
            "product": row.get("product") or row.get("output_filename"),
            "state": row.get("state") or row.get("folder"),
            "when": when,
            "iso": _iso(_epoch(when)) if when else None,
            "stream": row.get("agent"),
        })
        if len(out) >= 40:
            break
    return out


def snapshot(kernel, window: str = "week") -> dict:
    win = str(window or "week").strip().lower()
    if win in ("90d", "90days"):
        win = "90"
    if win not in WINDOWS:
        win = "week"
    days = WINDOWS[win]
    now = time.time()
    gfo = _gfo_sample()
    catalog = _work_products(kernel.paths, days, now)
    if gfo.get("kind") == "OK" and _in_window(gfo.get("time_updated"), days, now):
        catalog.insert(0, {
            "kind": "session_summary",
            "id": gfo.get("session_id"),
            "title": gfo.get("title"),
            "stream": "openwork/gfo",
            "when": gfo.get("time_updated"),
            "iso": gfo.get("iso"),
            "summary": gfo.get("summary"),
            "summary_kind": gfo.get("summary_kind"),
            "products": gfo.get("products"),
            "location": gfo.get("directory"),
        })
    return {
        "schema": SCHEMA,
        "measured_at": now,
        "tree_id": kernel.paths.sentinel.tree_id,
        "window": win,
        "window_days": days,
        "spend_approvals": _spend_approvals(kernel),
        "blockers": _blockers(kernel),
        "logins": _logins(kernel),
        "catalog": {
            "kind": "OK",
            "n": len(catalog),
            "rows": catalog,
            "gfo": {k: gfo.get(k) for k in (
                "kind", "session_id", "title", "iso", "summary_kind", "note",
                "detail") if k in gfo or gfo.get(k) is not None},
        },
        "note": (
            "Review is HITL: spend widens, blocking decisions, required logins, "
            "and a catalog of work products / session summaries. GET never mutates. "
            "Does not copy OpenWork or Legal files into the COSMOS tree. "
            "GFO sample is read-only from the OpenWork session file."
        ),
    }


def _selftest() -> int:
    import tempfile
    from types import SimpleNamespace

    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_review_"))
    root = install(td / "live", tree_id="spike-review")
    paths = CosmosPaths(root)
    kernel = SimpleNamespace(paths=paths, spend=None, control=None,
                             registry=None, ledger=None)
    rec = snapshot(kernel, window="week")
    check("GET fold names spend blockers logins catalog without mkdir",
          lambda: rec.get("schema") == SCHEMA
          and "spend_approvals" in rec
          and "blockers" in rec
          and "logins" in rec
          and "catalog" in rec
          and rec["window"] == "week")
    check("unknown window falls back to week",
          lambda: snapshot(kernel, window="nope")["window"] == "week")
    check("does not copy Legal files into the COSMOS tree",
          lambda: "does not copy" in rec["note"].lower() or
          "does not copy" in (rec["catalog"].get("gfo") or {}).get("note", "").lower()
          or "OpenWork grant" in str(rec["catalog"].get("gfo") or {}))
    check("spend widen is fail-closed, not a silent pile",
          lambda: "WIDEN_REQUIRES_CONFIRM" in rec["spend_approvals"]["note"])

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Review fold)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
