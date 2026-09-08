#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_voice_loop — GET fold for the SGH Voice comm loop.

SGH Voice (Think Fast 2.0) → GitHub drop → ingest daemon → GDX/Drive → SGH.

Status only. GET never mutates. Does not POST /voice. Does not poll grok.com.
Capability on this pane is later.

    py -3.14 cosmos\\\\cosmos_voice_loop.py --selftest
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import heartbeat_age_s, read_heartbeat  # noqa: E402
from cosmos_sgh_drop_ingest import (  # noqa: E402
    GH_BRANCH, GH_DROP_PATH, GH_REPO, HEARTBEAT_NAME, SEEN_NAME,
)

SCHEMA = "cosmos-voice-loop/1"


def _hb(paths) -> dict:
    p = paths.logs(HEARTBEAT_NAME)
    rec = read_heartbeat(p) if p.is_file() else None
    age = heartbeat_age_s(rec)
    return {
        "heartbeat": HEARTBEAT_NAME,
        "kind": "NO_SOURCE" if rec is None else "OK",
        "age_s": None if age is None else round(age, 1),
        "last_run": None if not rec else rec.get("last_run"),
        "pid": None if not rec else rec.get("pid"),
        "worker": None if not rec else rec.get("worker"),
        "filed_this_tick": None if not rec else rec.get("filed_this_tick"),
        "github_via": None if not rec else rec.get("github_via"),
        "state": None if not rec else rec.get("state"),
    }


def _github(paths) -> dict:
    seen_p = paths.state("work_orders", SEEN_NAME)
    seen_n = None
    kind = "NO_SOURCE"
    if seen_p.is_file():
        try:
            rec = json.loads(seen_p.read_text(encoding="utf-8"))
            if isinstance(rec, dict):
                shas = rec.get("seen") or rec.get("shas") or rec
                seen_n = len(shas) if isinstance(shas, (dict, list)) else None
                kind = "OK"
        except (OSError, ValueError):
            kind = "BROKE"
    drop_n = None
    try:
        from cosmos_work_order import work_order_dirs_ro
        dirs = work_order_dirs_ro(paths)
        d = dirs.get("drop")
        if d is not None and d.is_dir():
            drop_n = sum(1 for p in d.iterdir()
                         if p.is_file() and p.suffix.lower() == ".json"
                         and not p.name.startswith("_"))
            if kind == "NO_SOURCE":
                kind = "OK"
    except Exception:  # noqa: BLE001
        pass
    return {
        "kind": kind,
        "repo": GH_REPO,
        "path": GH_DROP_PATH,
        "branch": GH_BRANCH,
        "seen_n": seen_n,
        "local_drop_n": drop_n,
        "note": "SGH writes JSON here. Daemon lists GitHub; does not delete.",
    }


def _gdx(kernel) -> dict:
    sf = getattr(kernel, "surfaces", None)
    if sf is None or not hasattr(sf, "report"):
        return {"kind": "NO_SOURCE", "id": "GDX",
                "note": "Drive/CCr return path. Surface unread."}
    try:
        rows = sf.report() or []
    except Exception as e:  # noqa: BLE001
        return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:160]}
    hit = None
    for r in rows:
        if not isinstance(r, dict):
            continue
        rid = str(r.get("id") or "").upper()
        if "GDX" in rid or "DRIVE" in rid or "GOOGLE" in rid:
            hit = r
            break
    if not hit:
        return {"kind": "UNMEASURED", "id": "GDX",
                "note": "GDX not on GET /surfaces this host."}
    return {
        "kind": "OK" if hit.get("reachable") is True else (
            "UNREACHABLE" if hit.get("reachable") is False else "UNKNOWN"),
        "id": hit.get("id"),
        "reachable": hit.get("reachable"),
        "age_s": hit.get("age_s"),
        "role": hit.get("role"),
        "note": "Drive/CCr leg. SGH reads Drive on the way back.",
    }


def snapshot(kernel) -> dict:
    paths = kernel.paths
    daemon = _hb(paths)
    github = _github(paths)
    gdx = _gdx(kernel)
    legs = [
        {
            "id": "sgh",
            "label": "SGH Voice",
            "kind": "NAMED",
            "detail": "Grok Voice Think Fast 2.0 — operator mouth. Not this TUI.",
        },
        {
            "id": "github",
            "label": "GitHub drop",
            "kind": github.get("kind"),
            "detail": f"{github.get('repo')} {github.get('path')} @{github.get('branch')}",
            "seen_n": github.get("seen_n"),
            "local_drop_n": github.get("local_drop_n"),
        },
        {
            "id": "daemon",
            "label": "ingest daemon",
            "kind": daemon.get("kind"),
            "detail": daemon.get("heartbeat"),
            "age_s": daemon.get("age_s"),
            "pid": daemon.get("pid"),
            "last_run": daemon.get("last_run"),
        },
        {
            "id": "gdx",
            "label": "GDX / Drive",
            "kind": gdx.get("kind"),
            "detail": gdx.get("note"),
            "reachable": gdx.get("reachable"),
        },
        {
            "id": "sgh_read",
            "label": "SGH reads Drive",
            "kind": "NAMED",
            "detail": "Return path. Voice via Drive read. Not a mobile backend.",
        },
    ]
    return {
        "schema": SCHEMA,
        "measured_at": time.time(),
        "tree_id": paths.sentinel.tree_id,
        "loop": "SGH → GitHub → daemon → GDX → SGH",
        "legs": legs,
        "daemon": daemon,
        "github": github,
        "gdx": gdx,
        "note": (
            "SGH Voice loop (Keith 2026-09-05): Think Fast 2 → GitHub → daemon "
            "→ Drive/CCr → Voice via Drive read. Status only. GET never mutates. "
            "Does not POST /voice. Does not poll grok.com. Capability later."
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

    td = Path(tempfile.mkdtemp(prefix="cosmos_voiceloop_"))
    root = install(td / "live", tree_id="spike-voiceloop")
    kernel = SimpleNamespace(paths=CosmosPaths(root), surfaces=None)
    rec = snapshot(kernel)
    ids = [leg["id"] for leg in rec["legs"]]
    check("GET fold names the five-leg SGH GitHub daemon GDX SGH loop",
          lambda: rec.get("schema") == SCHEMA
          and ids == ["sgh", "github", "daemon", "gdx", "sgh_read"]
          and "SGH → GitHub → daemon → GDX → SGH" in rec["loop"])
    check("daemon unread is NO_SOURCE, not invented audio",
          lambda: rec["daemon"]["kind"] == "NO_SOURCE"
          and rec["legs"][0]["kind"] == "NAMED")
    check("GET does not POST /voice and does not poll grok.com",
          lambda: "Does not POST /voice" in rec["note"]
          and "Does not poll grok.com" in rec["note"])

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (SGH Voice loop)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
