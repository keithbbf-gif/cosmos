#!/usr/bin/env python3
"""cosmos_voice_loop — SGH Voice drop loop, plus the remote Android mouth.

Two stand-alone products. They share the work-order bucket. Neither is the other.

Voice Drop: SGH Voice (Think Fast 2.0) writes a six-field JSON file to GitHub
``work_orders/drop/``. ``cosmos_sgh_drop_ingest`` lists it and calls
``parse_order`` + ``drop_order``. This module does not run that clock and
does not delete the GitHub file.

Remote Android (cDm APK): talks to Core over HTTP. It does not mount ``live/``.
``POST /api/v1/voice_loop`` ``action=drop`` files the same bucket record the
ingest clock files. The dashboard, command bar, and kill switch keep working
when this drop is never used.

``action=new_sop`` files a SOP name the Voice tab already posts. It does not
start an agent.

GET never mutates and never mkdir. Does not POST /voice. Does not poll grok.com.

    py -3.14 cosmos\\\\cosmos_voice_loop.py --selftest
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import heartbeat_age_s, read_heartbeat
from cosmos_sgh_drop_ingest import (
    GH_BRANCH,
    GH_DROP_PATH,
    GH_REPO,
    HEARTBEAT_NAME,
    SEEN_NAME,
)

SCHEMA = "cosmos-voice-loop/1"
SOP_FILE = "voice_drop_sops.json"
SOP_KINDS = ("query", "work_order", "memo", "sop")
MOUTHS = ("android", "voice", "sgh")
MOUTH_AGENT = "xAI | Grok | grok-4.6"
MOUTH_CONTEXT = [
    "docs/AGENT_BRIEF.md [read*]",
    "docs/AGENT_BOUNDARIES.md [read*]",
    "docs/WORK_ORDER_SPEC.md [read*]",
]
TASK_HEAD = (
    "FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. "
    "P10: PROPOSE only. Never write the live tree. "
)
_WIN_BAD = re.compile(r'[<>:"/\\|?*]')
_SOP_CAP = 40

DROP_TYPES = (
    {
        "kind": "query",
        "id": "query",
        "label": "query",
        "sop": "GDX Voice SOP — query",
        "note": "A question in Task. Same six fields. Same inbox.",
    },
    {
        "kind": "work_order",
        "id": "work_order",
        "label": "work order",
        "sop": "docs/WORK_ORDER_SOP.md",
        "note": (
            "Six-field JSON. SGH Voice Think Fast 2.0 drops it on GitHub "
            "work_orders/drop. The Android app may POST the same object. "
            "Neither mouth mounts live/."
        ),
    },
    {
        "kind": "memo",
        "id": "memo",
        "label": "memo",
        "sop": "GDX Voice SOP — memo",
        "note": "A note for CCr. The drop is the memo. Not a live-tree write.",
    },
    {
        "kind": "sop",
        "id": "sop",
        "label": "New SOP",
        "sop": "Creating a SOP is itself a Voice DROP.",
        "note": "action=new_sop files the name. It does not start an agent.",
    },
)


class VoiceLoopError(RuntimeError):
    """kind in {BAD_INPUT, REFUSED, BROKE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _sop_path(paths) -> Path:
    return paths.state("work_orders", SOP_FILE)


def load_sops(paths) -> list:
    """Read the SOP catalog. Missing file is an empty list. Never mkdir."""
    p = _sop_path(paths)
    if not p.is_file():
        return []
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rows = obj.get("sops") if isinstance(obj, dict) else None
    if not isinstance(rows, list):
        return []
    return [r for r in rows if isinstance(r, dict)]


def _write_sops(paths, rows: list) -> None:
    from cosmos_work_order import work_order_dirs

    work_order_dirs(paths)
    dest = _sop_path(paths)
    payload = {"schema": SCHEMA, "sops": rows[-_SOP_CAP:]}
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(dest)


def _clean_name(name: str) -> str:
    s = str(name or "").strip()
    if not s or len(s) > 80 or s in (".", "..") or ".." in s or _WIN_BAD.search(s):
        raise VoiceLoopError(
            "BAD_INPUT",
            "SOP name must be a short Windows-legal token",
        )
    return s


def _clean_kind(kind: str) -> str:
    k = str(kind or "").strip().lower().replace(" ", "_")
    if k in ("newsop", "new_sop"):
        k = "sop"
    if k not in SOP_KINDS:
        raise VoiceLoopError(
            "BAD_INPUT",
            "kind is query, work_order, memo, or sop",
        )
    return k


def order_from_mouth(body: dict) -> dict:
    """Six-field order from a mouth. A complete order is kept.

    A short body ``{mouth, task}`` is filled with the work-order SOP defaults.
    The phone does not grow its own copy of those rules.
    """
    if not isinstance(body, dict):
        raise VoiceLoopError("BAD_INPUT", "body must be a JSON object")
    mouth = str(body.get("mouth") or "android").strip().lower()
    if mouth not in MOUTHS:
        raise VoiceLoopError("BAD_INPUT", "mouth is android, voice, or sgh")
    six = ("Agent", "Context source", "Task", "Target & scope", "Timestamp", "Output")
    if all(k in body for k in six):
        rec = {k: body[k] for k in six}
    else:
        task = str(body.get("task") or body.get("Task") or "").strip()
        if not task:
            raise VoiceLoopError("BAD_INPUT", "task is required")
        if "P10: PROPOSE only" not in task:
            task = TASK_HEAD + task
        rec = {
            "Agent": body.get("Agent") or MOUTH_AGENT,
            "Context source": body.get("Context source") or list(MOUTH_CONTEXT),
            "Task": task,
            "Target & scope": body.get("Target & scope") or body.get("scope") or (
                "proposals under Output only; never kernel/ledger/sched/service"
            ),
            "Timestamp": body.get("Timestamp") or _iso_now(),
            "Output": body.get("Output") or body.get("output") or "proposals | RESULT.json",
        }
    oid = str(body.get("order_id") or "").strip()
    if oid:
        rec["order_id"] = oid
    rec["mouth"] = mouth
    rec["product"] = "voice_drop" if mouth in ("voice", "sgh") else "android"
    return rec


def file_mouth_drop(paths, body: dict) -> dict:
    """parse_order + drop_order. Does not run the agent. Does not touch GitHub."""
    from cosmos_work_order import OrderError, drop_order

    rec = order_from_mouth(body)
    try:
        dest = drop_order(paths, rec)
    except OrderError as e:
        raise VoiceLoopError(e.kind, e.detail) from e
    return {
        "schema": SCHEMA,
        "ok": True,
        "action": "drop",
        "mouth": rec["mouth"],
        "product": rec["product"],
        "order_id": dest.stem,
        "state": "DROPPED",
        "ran_agent": False,
        "note": "Filed into the work-order bucket. The existing runner picks it up.",
    }


def save_sop(paths, body: dict) -> dict:
    """POST /api/v1/voice_loop. new_sop files a name. drop files a work order."""
    if not isinstance(body, dict):
        raise VoiceLoopError("BAD_INPUT", "body must be a JSON object")
    action = str(body.get("action") or "").strip()
    if action == "drop":
        return file_mouth_drop(paths, body)
    if action != "new_sop":
        raise VoiceLoopError("BAD_INPUT", "action is new_sop or drop")
    name = _clean_name(str(body.get("name") or ""))
    kind = _clean_kind(body.get("kind") or "sop")
    rows = load_sops(paths)
    for row in rows:
        if row.get("name") == name and row.get("kind") == kind:
            return {
                "schema": SCHEMA,
                "ok": True,
                "action": "new_sop",
                "already": True,
                "sop": row,
            }
    sop = {
        "name": name,
        "kind": kind,
        "filed_at": _iso_now(),
        "note": "Voice DROP SOP name. Not an agent run.",
    }
    rows.append(sop)
    _write_sops(paths, rows)
    return {"schema": SCHEMA, "ok": True, "action": "new_sop", "sop": sop}


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
    except Exception:  # noqa: BLE001 — status fold must not raise
        if kind == "NO_SOURCE":
            kind = "BROKE"
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
    sops = load_sops(paths)
    return {
        "schema": SCHEMA,
        "measured_at": time.time(),
        "tree_id": paths.sentinel.tree_id,
        "loop": "SGH → GitHub → daemon → GDX → SGH",
        "legs": legs,
        "daemon": daemon,
        "github": github,
        "gdx": gdx,
        "drops": {
            "kind": github.get("kind"),
            "seen_n": github.get("seen_n"),
            "local_drop_n": github.get("local_drop_n"),
            "last_run": daemon.get("last_run"),
        },
        "drop_types": [dict(row) for row in DROP_TYPES],
        "sops": sops,
        "mouths": {
            "voice_drop": "SGH Voice Think Fast 2.0 → GitHub work_orders/drop. Stand-alone.",
            "android": "cDm APK → POST action=drop. Stand-alone. Same bucket when used.",
        },
        "note": (
            "SGH Voice loop (Keith 2026-09-05): Think Fast 2 → GitHub → daemon "
            "→ Drive/CCr → Voice via Drive read. Status only. GET never mutates. "
            "Does not POST /voice. Does not poll grok.com. "
            "Android is a separate app and is not required for this loop."
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
    check("GET names both mouths and does not create the SOP file",
          lambda: rec["mouths"]["voice_drop"].startswith("SGH")
          and rec["mouths"]["android"].startswith("cDm")
          and rec["sops"] == []
          and not (root / "state" / "work_orders" / SOP_FILE).is_file()
          and [t["kind"] for t in rec["drop_types"]] == list(SOP_KINDS))

    try:
        save_sop(kernel.paths, {"action": "new_sop", "name": "bad:name", "kind": "query"})
        filed_bad = False
    except VoiceLoopError as e:
        filed_bad = e.kind == "BAD_INPUT"
    check("new_sop refuses a Windows-illegal name", lambda: filed_bad)

    filed = save_sop(kernel.paths, {
        "action": "new_sop", "name": "query-20260924T120000", "kind": "query",
    })
    again = save_sop(kernel.paths, {
        "action": "new_sop", "name": "query-20260924T120000", "kind": "query",
    })
    seen = snapshot(kernel)
    check("new_sop files a name the GET fold lists, and does not run an agent",
          lambda: filed["sop"]["name"] == "query-20260924T120000"
          and again.get("already") is True
          and seen["sops"][0]["kind"] == "query"
          and "order_id" not in filed)

    dropped = save_sop(kernel.paths, {
        "action": "drop", "mouth": "android", "task": "say the tree id",
    })
    voice = save_sop(kernel.paths, {
        "action": "drop",
        "mouth": "voice",
        "Agent": "xAI | Grok | grok-4.6",
        "Context source": "docs/WORK_ORDER_SPEC.md [read*]",
        "Task": TASK_HEAD + "voice mouth stand-alone",
        "Target & scope": "proposals under Output only",
        "Timestamp": "2026-09-24T12:00:00-05:00",
        "Output": "proposals | VOICE.json",
    })
    bucket = root / "state" / "work_orders" / "bucket"
    check("android drop and voice drop share the bucket and do not run an agent",
          lambda: dropped["mouth"] == "android"
          and dropped["ran_agent"] is False
          and voice["mouth"] == "voice"
          and (bucket / f"{dropped['order_id']}.json").is_file()
          and (bucket / f"{voice['order_id']}.json").is_file())
    try:
        save_sop(kernel.paths, {"action": "drop", "mouth": "android", "task": "  "})
        empty_ok = False
    except VoiceLoopError as e:
        empty_ok = e.kind == "BAD_INPUT"
    check("a drop with no task is refused", lambda: empty_ok)

    partial = order_from_mouth({
        "mouth": "android",
        "task": "FIRST read docs/AGENT_BRIEF.md only the first sentence",
    })
    check("a brief-only task still carries the proposal-only rule",
          lambda: "P10: PROPOSE only" in partial["Task"]
          and "Never write the live tree" in partial["Task"])
    same = "wo-retry-same"
    again_drop = save_sop(kernel.paths, {
        "action": "drop", "mouth": "android", "task": "retry me", "order_id": same,
    })
    check("the same order_id overwrites one bucket file",
          lambda: dropped["order_id"] != same
          and again_drop["order_id"] == same
          and save_sop(kernel.paths, {
              "action": "drop", "mouth": "android", "task": "retry me", "order_id": same,
          })["order_id"] == same
          and (bucket / f"{same}.json").is_file()
          and len(list(bucket.glob(f"{same}.json"))) == 1)

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        flag = "OK  " if ok else "FAIL"
        tail = f"  [{err}]" if err else ""
        print(f"  {flag}  {label}{tail}")
    verdict = "PASS" if not failed else "FAIL"
    print(f"SELFTEST {verdict} - {len(results)} checks (SGH Voice loop)")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
