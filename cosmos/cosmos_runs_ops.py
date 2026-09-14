#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_runs_ops — GET fold for the Runs ops column.

Watchdog, clocks, work orders, CCR stream, recents, Gitur jobs, spend.
Never mutates. Never mkdir. Never invents token counts.

    py -3.14 cosmos\\\\cosmos_runs_ops.py --selftest
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import heartbeat_age_s, read_heartbeat  # noqa: E402
from cosmos_own_clocks import CLOCKS  # noqa: E402

SCHEMA = "cosmos-runs-ops/1"


def _hb(paths, name: str) -> dict:
    p = paths.logs(name)
    rec = read_heartbeat(p) if p.is_file() else None
    age = heartbeat_age_s(rec)
    out = {
        "heartbeat": name,
        "kind": "NO_SOURCE" if rec is None else "OK",
        "age_s": None if age is None else round(age, 1),
        "last_run": None if not rec else rec.get("last_run"),
        "pid": None if not rec else rec.get("pid"),
        "worker": None if not rec else rec.get("worker"),
    }
    return out


def _clocks(paths) -> list[dict]:
    rows = []
    for c in CLOCKS:
        hb = _hb(paths, c["heartbeat"])
        rows.append({
            "id": c["id"],
            "clock": c["clock"],
            "cadence": c["cadence"],
            "task": c["task"],
            "heartbeat": hb,
        })
    return rows


def _work_orders(paths) -> dict:
    try:
        from cosmos_work_order import fold_work_orders
        rec = fold_work_orders(paths, limit=8)
    except Exception as e:  # noqa: BLE001
        return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}
    products = []
    for row in rec.get("rows") or []:
        if not isinstance(row, dict):
            continue
        products.append({
            "id": row.get("order_id") or row.get("id"),
            "state": row.get("state") or row.get("folder"),
            "agent": row.get("agent"),
            "task": str(row.get("task") or "")[:160],
            "product": row.get("product") or row.get("output_filename"),
            "output_head": str(row.get("output_head") or row.get("output") or "")[:240] or None,
            "mtime": row.get("timestamp") or row.get("dropped_at"),
        })
        if len(products) >= 8:
            break
    return {
        "kind": "OK",
        "n_total": rec.get("n_total"),
        "counts": rec.get("counts"),
        "recent": products,
    }


def _recents(paths) -> dict:
    try:
        import sys as _sys
        cdeck = str(Path(__file__).resolve().parent.parent / "builds" / "cdeck")
        if cdeck not in _sys.path:
            _sys.path.insert(0, cdeck)
        from cosmos_recents_panel import handle_get
        code, body = handle_get(str(paths.root),
                                expected_tree_id=paths.sentinel.tree_id)
    except Exception as e:  # noqa: BLE001
        return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}
    if code != 200:
        return {"kind": (body or {}).get("error") or f"HTTP_{code}"}
    rows = (body or {}).get("sessions") or (body or {}).get("rows") or []
    out = []
    for row in rows[:3]:
        if not isinstance(row, dict):
            continue
        excerpt = row.get("excerpt") or row.get("preview") or row.get("last")
        out.append({
            "id": row.get("id"),
            "title": row.get("title"),
            "stream": row.get("stream"),
            "date": row.get("date"),
            "turns": row.get("turns"),
            "location": row.get("filename") or row.get("path"),
            "last_posts": None if not excerpt else [str(excerpt)[:240]],
            "last_posts_kind": "excerpt" if excerpt else "UNMEASURED",
        })
    return {
        "kind": "OK" if (body or {}).get("n_shown") is not None else "NO_SOURCE",
        "n_shown": (body or {}).get("n_shown"),
        "sessions": out,
        "note": ("Last 2–3 session rows from recents.json. Message bodies are "
                 "UNMEASURED unless the projection sent an excerpt."),
    }


def _voice(kernel) -> dict:
    ctrl = getattr(kernel, "control", None)
    flags = None
    if ctrl is not None:
        try:
            flags = ctrl.effective(None) if hasattr(ctrl, "effective") else None
        except Exception as e:  # noqa: BLE001
            flags = {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:160]}
    phone = None
    try:
        p = kernel.paths.state("cvm", "phone.json")
        if p.is_file():
            rec = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(rec, dict):
                phone = {
                    "present": True,
                    "updated_at": rec.get("updated_at") or rec.get("measured_at"),
                    "client_id": rec.get("client_id"),
                    "kind": rec.get("kind") or rec.get("mode"),
                }
    except Exception:  # noqa: BLE001
        phone = {"present": False, "kind": "BROKE"}
    looping = False
    if isinstance(flags, dict) and not flags.get("mic_off") and not flags.get("pause"):
        looping = bool(phone and phone.get("present"))
    return {
        "control": flags,
        "cvm": phone or {"present": False, "kind": "NO_SOURCE"},
        "sgh_voice_loop": looping,
        "note": "SGH-Voice loop is inferred from control flags + cvm/phone.json. Not invented audio.",
    }


def _spend(kernel) -> dict:
    spend = getattr(kernel, "spend", None)
    rails = {}
    kind = "NO_SOURCE"
    if spend is not None:
        try:
            aud = spend.audit()
            rails = aud.get("rails") or {}
            kind = "OK"
        except Exception as e:  # noqa: BLE001
            kind = f"{type(e).__name__}: {e}"[:160]
    meters = []
    for rid, row in (rails.items() if isinstance(rails, dict) else []):
        if not isinstance(row, dict):
            continue
        cap = row.get("cap_usd")
        settled = row.get("settled_usd")
        free = (cap == 0) or (isinstance(rid, str) and ":free" in rid)
        meters.append({
            "rail": rid,
            "settled_usd": settled,
            "cap_usd": cap,
            "reserved_usd": row.get("reserved_usd"),
            "headroom_usd": row.get("headroom_usd"),
            "tokens": None,
            "tokens_kind": "UNMEASURED",
            "free": bool(free),
        })
    guard = None
    g = getattr(kernel, "spendguard", None) or getattr(kernel, "guard", None)
    if g is not None and hasattr(g, "audit"):
        try:
            guard = g.audit()
        except Exception:  # noqa: BLE001
            guard = None
    return {
        "kind": kind,
        "meters": meters,
        "guard": guard,
        "note": ("Cost is spend.audit() per rail (the key stays on the rail). "
                 "Token counts are UNMEASURED unless a later meter writes them."),
    }


def snapshot(kernel) -> dict:
    paths = kernel.paths
    wd = _hb(paths, "watchdog2_heartbeat.json")
    try:
        from cosmos_gitur import snapshot as gitur_snapshot
        gitur = gitur_snapshot(kernel)
        gitur_pub = {
            "legs": gitur.get("legs"),
            "jobs": (gitur.get("jobs") or [])[:8],
            "jobs_n": gitur.get("jobs_n"),
            "jobs_kind": gitur.get("jobs_kind"),
            "ccr": gitur.get("ccr"),
            "launch": gitur.get("launch"),
            "note": gitur.get("note"),
        }
    except Exception as e:  # noqa: BLE001
        gitur_pub = {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}
    recents = _recents(paths)
    orders = _work_orders(paths)
    try:
        from cosmos_profiles import portfolio_projection
        portfolio = portfolio_projection(paths, ledger=getattr(kernel, "ledger", None))
    except Exception as e:  # noqa: BLE001
        portfolio = {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}
    streams = []
    ccr = gitur_pub.get("ccr") if isinstance(gitur_pub, dict) else None
    if isinstance(ccr, dict) and ccr.get("held"):
        streams.append({
            "profile": "forge",
            "stream": ccr.get("stream") or "Cm",
            "sid": ccr.get("sid"),
            "location": "CCr lease",
            "active": True,
        })
    for s in recents.get("sessions") or []:
        streams.append({
            "profile": s.get("stream") or "session",
            "stream": s.get("stream"),
            "sid": s.get("id"),
            "location": s.get("location"),
            "title": s.get("title"),
            "date": s.get("date"),
            "turns": s.get("turns"),
            "last_posts": s.get("last_posts"),
            "last_posts_kind": s.get("last_posts_kind"),
            "active": False,
        })
    return {
        "schema": SCHEMA,
        "measured_at": time.time(),
        "tree_id": paths.sentinel.tree_id,
        "watchdog": wd,
        "clocks": _clocks(paths),
        "work_orders": orders,
        "streams": streams[:8],
        "voice": _voice(kernel),
        "gitur": gitur_pub,
        "products": (orders.get("recent") if isinstance(orders, dict) else []),
        "portfolio": portfolio,
        "spend": _spend(kernel),
        "mesh": {
            "note": ("Activity feed is GET /events on the Runs EVENTS column — "
                     "the same ledger tail JACK'S MESH paints. Not a second feed."),
        },
        "note": (
            "Fold of heartbeats, recents, work_orders, gitur, spend. "
            "Does not poll vendors. Token counts stay UNMEASURED until a meter writes them."
        ),
    }


def _selftest() -> int:
    import tempfile

    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths
    from types import SimpleNamespace

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_runsops_"))
    root = install(td / "live", tree_id="spike-runsops")
    paths = CosmosPaths(root)
    kernel = SimpleNamespace(paths=paths, spend=None, control=None, registry=None)
    rec = snapshot(kernel)
    check("GET fold names watchdog and clocks without mkdir",
          lambda: rec.get("schema") == SCHEMA
          and rec["watchdog"]["kind"] == "NO_SOURCE"
          and len(rec["clocks"]) >= 6
          and rec["watchdog"]["heartbeat"] == "watchdog2_heartbeat.json")
    check("spend tokens stay UNMEASURED when no meter wrote them",
          lambda: rec["spend"]["kind"] == "NO_SOURCE"
          and "UNMEASURED" in rec["note"])
    check("does not invent GitHub PR lists",
          lambda: "Does not poll vendors" in rec["note"])
    check("fold names watchdog clocks streams voice gitur spend products mesh",
          lambda: all(k in rec for k in (
              "watchdog", "clocks", "work_orders", "streams",
              "voice", "gitur", "products", "portfolio", "spend", "mesh"))
          and rec["voice"].get("sgh_voice_loop") is False
          and rec["spend"]["meters"] == []
          and rec["spend"]["kind"] == "NO_SOURCE")
    pf = rec.get("portfolio") or {}
    check("portfolio names seven products; stages UNMEASURED not 0",
          lambda: pf.get("n_products") == 7
          and len(pf.get("products") or []) == 7
          and all(p.get("stage", {}).get("n") is None
                  and p.get("stage", {}).get("kind") == "UNMEASURED"
                  for p in (pf.get("products") or [])))

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Runs ops fold)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
