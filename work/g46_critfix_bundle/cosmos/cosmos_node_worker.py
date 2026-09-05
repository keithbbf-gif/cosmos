#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_node_worker - GROK / GEM / OA Windows-native bucket workers.

Each node polls ITS OWN bucket (live/buckets/<node>/), picks up a prompt
drop, executes it through THAT node's COSMOS rail (spend-gated + ledgered),
and writes the result DIRECTLY to the designated folder.

NO BTS import. Does not modify kernel / ledger / sched / service.

Grok -> sgh-api then gw-api (explicit audited fallback).
GEM  -> gem-api.
OA   -> oa-api.

Critique packets (dispatch handoff) carry `returns`/`result`. When present,
land_critique_return writes the REAL body to that path. Empty text is
FAILED, never fake-DONE rc=0. SSA is a claude-CLI lane, consumed by
cosmos_crit_consumer (not this bucket worker).

    py -3.14 cosmos\\cosmos_node_worker.py --root <live> --node grok --once
    py -3.14 cosmos\\cosmos_grok_worker.py --root <live> --loop
    py -3.14 cosmos\\cosmos_gem_worker.py  --root <live> --standup
    py -3.14 cosmos\\cosmos_oa_worker.py   --root <live> --once
    py -3.14 cosmos\\cosmos_grok_worker.py --root <live> --status

Dispatch gem/oa jobs call execute_handoff (drop onto live/buckets/<node>
AND run the rail). Empty rail text is FAILED, never fake-DONE rc=0.

CLI: --loop / --once / --standup / --status, optional --out V|GDX|ODX
     (V is default and BEST). Per-task `out` field overrides --out.

--loop honors live/state/control/PAUSE.flag: pick up NOTHING; heartbeat
state=PAUSED (paused != dead). --once is a commanded drain (Keith/COW
explicit), even while paused, so a proof tick can land.

Heartbeat: live/logs/<node>_worker_heartbeat.json on EVERY tick.
Lock:      live/logs/<node>_worker.lock
Tasks:     'COSMOS Grok Worker' / 'COSMOS GEM Worker' / 'COSMOS OA Worker'
           (1-min self-heal of --loop + ONLOGON relaunch). Detached
           pythonw fallback.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    acquire_lock, atomic_json, create_task, heartbeat_age_s, pid_alive,
    pythonw_exe, query_task, read_heartbeat, spawn_detached, tr_cmdline,
    wait_fresh, write_heartbeat,
)
from cosmos_dispatch import (  # noqa: E402
    append_dhx_marker, append_index_row, default_dhx, index_lock_for,
    index_path_for, inbox_dir, write_inbox_sidecar,
)
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

SCHEMA = "cosmos-node-worker/1"
DEFAULT_INTERVAL_S = 15.0
FRESH_S = 90.0
DROP_SUFFIXES = {".json", ".txt"}
SKIP_DIR_NAMES = {"processed", "failed", "running", "__pycache__", "_delme"}
DEST_KEYS = ("V", "GDX", "ODX")
CONFIG_NAME = "node_worker.json"

# Designated external destinations. These are named return folders, NOT
# COSMOS roles — the resolver refuses absolute parts. V: is the role path
# live/returns/<node>. Override via live/config/node_worker.json `dest`.
DEFAULT_EXT_DEST = {
    "GDX": Path(r"X:\My Drive\BTS_SGH_Handoff"),
    "ODX": Path(r"C:\Users\Papa\OneDrive"),
}

# link_id / incumbent module / metered_usd / default budget — same specs
# cosmos_node_rails.register_node_rails uses. Worker never imports bts_*.
NODES = {
    "grok": {
        "id": "grok",
        "worker": "cosmos-grok-worker",
        "task_name": "COSMOS Grok Worker",
        "task_logon": "COSMOS Grok Worker Logon",
        "heartbeat": "grok_worker_heartbeat.json",
        "lock": "grok_worker.lock",
        "script": "cosmos_grok_worker.py",
        "agent": "GROK",
        "maker": "Grok",
        "rails": (
            {"link_id": "sgh-api", "module": "bts_sgh",
             "metered_usd": 0.02, "budget": 10.0},
            {"link_id": "gw-api", "module": "bts_gw",
             "metered_usd": 0.001, "budget": 5.0},
        ),
    },
    "gem": {
        "id": "gem",
        "worker": "cosmos-gem-worker",
        "task_name": "COSMOS GEM Worker",
        "task_logon": "COSMOS GEM Worker Logon",
        "heartbeat": "gem_worker_heartbeat.json",
        "lock": "gem_worker.lock",
        "script": "cosmos_gem_worker.py",
        "agent": "GEM",
        "maker": "Gemini",
        "rails": (
            {"link_id": "gem-api", "module": "bts_gem",
             "metered_usd": 0.03, "budget": 300.0},
        ),
    },
    "oa": {
        "id": "oa",
        "worker": "cosmos-oa-worker",
        "task_name": "COSMOS OA Worker",
        "task_logon": "COSMOS OA Worker Logon",
        "heartbeat": "oa_worker_heartbeat.json",
        "lock": "oa_worker.lock",
        "script": "cosmos_oa_worker.py",
        "agent": "OAi",
        "maker": "OpenAI",
        "rails": (
            {"link_id": "oa-api", "module": "bts_oa_api",
             "metered_usd": 0.05, "budget": 5.0},
        ),
    },
}


class WorkerError(RuntimeError):
    """kind in {BAD_NODE, BAD_OUT, BAD_TASK, NO_DEST, NO_KEY, NO_ROOT}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


# Grok/GEM API-rail nodes. Claude-CLI agents (SSA/sonnet/haiku) are
# dispatch lanes, not node-worker rails -- fail closed with a pointer.
NODE_ALIASES = {
    "grok": "grok", "g46": "grok", "sgh": "grok", "gw": "grok",
    "gem": "gem", "gemini": "gem",
    "oa": "oa", "oai": "oa", "openai": "oa",
}
CLAUDE_CLI_AGENTS = {
    "ssa": "SSA",
    "subagent": "SSA",
    "sonnetsubagent": "SSA",
    "sonnet": "sonnet",
    "sonnet5": "sonnet",
    "haiku": "haiku",
    "haiku45": "haiku",
}


def canon_node(node: str) -> str:
    key = str(node or "").strip().lower()
    if key in CLAUDE_CLI_AGENTS:
        raise WorkerError(
            "BAD_NODE",
            f"{node!r} is a claude-CLI dispatch agent "
            f"(cosmos_dispatch --agent {CLAUDE_CLI_AGENTS[key]} / "
            f"cosmos_crit_consumer ssa rail); "
            f"want grok|gem|oa")
    if key not in NODE_ALIASES:
        raise WorkerError("BAD_NODE",
                          f"unknown node {node!r}; want grok|gem|oa")
    return NODE_ALIASES[key]


def node_spec(node: str) -> dict:
    return NODES[canon_node(node)]


def script_for(spec: dict) -> Path:
    here = Path(__file__).resolve().parent
    p = here / spec["script"]
    return p if p.exists() else Path(__file__).resolve()


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat()


def _oneline(s: str, n: int = 140) -> str:
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def _stamp_file() -> str:
    now = datetime.now().astimezone()
    return now.strftime("%Y%m%dT%H%M%S") + now.strftime("%z").replace(":", "")


def load_config(paths: CosmosPaths) -> dict:
    cfg = {"interval_s": DEFAULT_INTERVAL_S, "dest": {}}
    p = paths.config(CONFIG_NAME)
    if not p.exists():
        return cfg
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cfg["_config_error"] = f"unreadable {p}"
        return cfg
    if isinstance(raw, dict):
        if raw.get("interval_s") is not None:
            try:
                cfg["interval_s"] = float(raw["interval_s"])
            except (TypeError, ValueError):
                pass
        dest = raw.get("dest")
        if isinstance(dest, dict):
            cfg["dest"] = {str(k).upper(): str(v) for k, v in dest.items()}
    return cfg


def pause_flag(paths: CosmosPaths) -> dict | None:
    """Presence of live/state/control/PAUSE.flag is the whole signal."""
    p = paths.state("control", "PAUSE.flag")
    if not p.exists() or not p.is_file():
        return None
    rec: dict = {"path": str(p), "state": "PAUSED"}
    try:
        raw = p.read_text(encoding="utf-8").strip()
    except OSError as e:
        rec["read_error"] = str(e)
        return rec
    if raw.startswith("{"):
        try:
            obj = json.loads(raw)
        except ValueError:
            obj = None
        if isinstance(obj, dict):
            rec.update(obj)
            rec.setdefault("state", "PAUSED")
            rec["path"] = str(p)
            return rec
    rec["reason"] = raw[:240] or "(empty flag file)"
    return rec


def is_paused(paused: dict | None) -> bool:
    if paused is None:
        return False
    return str(paused.get("state") or "PAUSED").upper() != "RUNNING"


def bucket_dir(paths: CosmosPaths, node: str) -> Path:
    """live/buckets/<node> — role('root') so we do not invent a new role."""
    d = paths.role("root", "buckets", canon_node(node))
    d.mkdir(parents=True, exist_ok=True)
    (d / "processed").mkdir(parents=True, exist_ok=True)
    (d / "failed").mkdir(parents=True, exist_ok=True)
    return d


def v_returns(paths: CosmosPaths, node: str) -> Path:
    d = paths.role("root", "returns", canon_node(node))
    d.mkdir(parents=True, exist_ok=True)
    return d


def canon_out(value: str | None, default: str = "V") -> str:
    raw = str(value or default or "V").strip().upper()
    raw = raw.replace(":", "").replace("/", "").replace("\\", "")
    if raw not in DEST_KEYS:
        raise WorkerError("BAD_OUT",
                          f"out {value!r} is not V|GDX|ODX")
    return raw


def dest_dir(paths: CosmosPaths, node: str, dest_key: str,
             cfg: dict | None = None) -> Path:
    """Resolve the designated folder. V is the COSMOS-native returns role."""
    key = canon_out(dest_key)
    node = canon_node(node)
    if key == "V":
        return v_returns(paths, node)
    cfg = cfg or {}
    override = (cfg.get("dest") or {}).get(key)
    base = Path(override) if override else DEFAULT_EXT_DEST[key]
    if not base.exists() or not base.is_dir():
        raise WorkerError(
            "NO_DEST",
            f"{key} dest is missing or not a directory: {base}")
    d = base / "COSMOS" / "returns" / node
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise WorkerError("NO_DEST", f"{key} dest unwritable {d}: {e}") from e
    return d


def list_drop_files(bucket: Path) -> list[Path]:
    files: list[Path] = []
    if not bucket.exists():
        return files
    try:
        kids = list(bucket.iterdir())
    except OSError:
        return files
    for p in sorted(kids, key=lambda x: x.stat().st_mtime if x.exists() else 0):
        if not p.is_file():
            continue
        if p.name.startswith("_") or p.name.startswith("."):
            continue
        if p.suffix.lower() not in DROP_SUFFIXES:
            continue
        files.append(p)
    return files


def parse_task(path: Path, default_out: str = "V") -> dict:
    """One task = a prompt + optional out-destination."""
    suffix = path.suffix.lower()
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise WorkerError("BAD_TASK", f"drop unreadable {path}: {e}") from e
    raw: dict = {}
    prompt = ""
    out = default_out
    task_id = path.stem
    if suffix == ".json":
        try:
            obj = json.loads(text) if text.strip() else {}
        except ValueError as e:
            raise WorkerError("BAD_TASK", f"drop is not JSON: {path}: {e}") from e
        if not isinstance(obj, dict):
            raise WorkerError("BAD_TASK", f"drop is not a JSON object: {path}")
        raw = obj
        prompt = str(obj.get("prompt") or obj.get("task")
                     or obj.get("assignment") or obj.get("text") or "").strip()
        if obj.get("out"):
            out = canon_out(obj.get("out"), default_out)
        if obj.get("id"):
            task_id = str(obj["id"]).strip() or task_id
    else:
        prompt = text.strip()
        raw = {"prompt": prompt, "source": "txt"}
    if not prompt:
        raise WorkerError("BAD_TASK", f"drop missing prompt: {path}")
    returns = None
    if raw.get("returns") or raw.get("result"):
        returns = str(raw.get("returns") or raw.get("result")).strip() or None
    kind = str(raw.get("kind") or "").strip().lower() or None
    agent = str(raw.get("agent") or "").strip() or None
    return {
        "prompt": prompt,
        "out": canon_out(out, default_out),
        "id": task_id,
        "raw": raw,
        "path": str(path),
        "name": path.name,
        "returns": returns,
        "kind": kind,
        "agent": agent,
    }


def stage_drop(bucket: Path, drop_path: Path, stamp: str,
               *, failed: bool = False) -> Path:
    """Move a handled drop into processed/ or failed/. Never delete."""
    dest_dir_ = bucket / ("failed" if failed else "processed")
    dest_dir_.mkdir(parents=True, exist_ok=True)
    dest = dest_dir_ / f"{stamp}_{drop_path.name}"
    n = 1
    while dest.exists():
        n += 1
        dest = dest_dir_ / f"{stamp}_{n}_{drop_path.name}"
    try:
        drop_path.replace(dest)
        return dest
    except OSError:
        shutil.copy2(str(drop_path), str(dest))
        claimed = drop_path.with_name(drop_path.name + ".claimed")
        try:
            drop_path.replace(claimed)
        except OSError:
            pass
        return dest


def _open_spend(paths: CosmosPaths, writer: str):
    """Ledger + spend as THIS worker. Not Kernel() — no BOOT_VERIFIED.

    The ledger's OS lock serializes writers (B1); Core remains the
    authority, this worker is a fenced client of the same chain.
    """
    from cosmos_ledger import Ledger
    from cosmos_spend import SpendGate
    keyfile = paths.config("install_key.bin")
    if not keyfile.exists():
        raise WorkerError(
            "NO_KEY",
            f"no install key at {keyfile} - worker refuses rather than "
            f"inventing authentication material")
    key = keyfile.read_bytes()
    led_path = paths.ledger("authority.jsonl")
    ledger = Ledger(led_path, key, writer)
    return ledger, SpendGate(ledger)


def execute_via_rail(paths: CosmosPaths, spec: dict, prompt: str,
                     *, rail_call=None) -> dict:
    """Spend-gated, ledgered dispatch through the node's COSMOS rails.

    `rail_call` is a test seam (fake incumbent). Live path uses
    cosmos_node_rails.NodeRail + cosmos_spend.SpendGate and appends
    RAIL_DISPATCH / RAIL_RESULT like cosmos_rails.Dispatcher.
    """
    if rail_call is not None:
        r = rail_call(prompt)
        if not isinstance(r, dict):
            r = {"ok": True, "kind": "API", "text": str(r),
                 "model": "injected", "usd": None, "link_id": "injected"}
        r.setdefault("kind", "API")
        r.setdefault("link_id", "injected")
        r.setdefault("model", r.get("node") or "injected")
        return r

    from cosmos_node_rails import NodeRail
    from cosmos_spend import SpendError

    ledger, spend = _open_spend(paths, spec["worker"])
    last: dict | None = None
    for rail in spec["rails"]:
        lid = rail["link_id"]
        if lid not in spend.audit()["rails"]:
            spend.set_budget(lid, rail["budget"])
        adapter = NodeRail(rail["module"], metered_usd=rail["metered_usd"])
        ledger.append("RAIL_DISPATCH", {
            "link_id": lid, "kind": "API",
            "src": spec["worker"], "dst": "models",
            "node": spec["id"],
        })
        try:
            result = spend.guarded_call(
                lid, rail["metered_usd"],
                lambda a=adapter: a.dispatch({"prompt": prompt}),
            )
        except SpendError as e:
            ledger.append("RAIL_RESULT", {
                "link_id": lid, "ok": False,
                "detail": f"spend-gated: {e}",
            })
            last = {"ok": False, "kind": "NOT_PERMITTED",
                    "detail": str(e), "link_id": lid, "model": rail["module"]}
            continue
        model = (result.get("model") or result.get("node")
                 or rail["module"])
        ledger.append("RAIL_RESULT", {
            "link_id": lid, "ok": result.get("ok"),
            "kind": result.get("kind"),
            "model": model, "usd": result.get("usd"),
        })
        bound = dict(result)
        bound["link_id"] = lid
        bound["model"] = model
        if bound.get("ok"):
            return bound
        if bound.get("kind") in ("UNREACHABLE", "SESSION_EXPIRED",
                                 "AUTH_REQUIRED"):
            ledger.append("RAIL_FALLBACK", {
                "from": lid, "reason": bound.get("kind"),
                "detail": "explicit audited fallback to next live link",
            })
            last = bound
            continue
        return bound
    return last or {
        "ok": False, "kind": "NO_LIVE_LINK",
        "detail": "all candidate rails failed or absent",
        "link_id": None, "model": None,
    }


def _result_name(task: dict, spec: dict, stamp: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-"
                   for ch in str(task.get("id") or "task"))[:60] or "task"
    return f"{spec['id']}_{safe}_{stamp}_result.json"


def write_result_files(paths: CosmosPaths, spec: dict, rec: dict,
                       dest_key: str, cfg: dict) -> dict:
    """Write DIRECTLY to the designated folder. V is always landed too
    so a spent rail answer is never stranded on a missing GDX/ODX."""
    name = rec["result_name"]
    v_path = v_returns(paths, spec["id"]) / name
    atomic_json(v_path, rec)
    rec["v_path"] = str(v_path)
    rec["result_path"] = str(v_path)
    rec["out_landed"] = "V"
    if dest_key == "V":
        return rec
    try:
        d = dest_dir(paths, spec["id"], dest_key, cfg)
        p = d / name
        atomic_json(p, rec)
        rec["dest_path"] = str(p)
        rec["result_path"] = str(p)
        rec["out_landed"] = dest_key
        atomic_json(v_path, rec)  # V copy carries dest_path
    except WorkerError as e:
        rec["dest_error"] = str(e)
        rec["out_landed"] = "V"
        atomic_json(v_path, rec)
    except OSError as e:
        rec["dest_error"] = f"{type(e).__name__}: {e}"
        rec["out_landed"] = "V"
        atomic_json(v_path, rec)
    return rec


def register_return(paths: CosmosPaths, spec: dict, rec: dict,
                    dhx_path: Path | None = None) -> dict:
    """DHx-log the pickup and register the return with the collector."""
    stamp = rec.get("pickup_at") or _iso_now()
    filename = rec.get("drop_name") or rec.get("result_name") or "task"
    marker = (f"{stamp} · {spec['agent']} · "
              f"pickup {_oneline(rec.get('prompt') or '')} · "
              f"buckets/{spec['id']}/{filename}")
    dhx = Path(dhx_path) if dhx_path is not None else default_dhx(paths)
    dhx_rec = append_dhx_marker(dhx, marker)
    rec["dhx_marker"] = marker
    rec["dhx"] = dhx_rec

    now = time.time()
    artifact = rec.get("result_path") or rec.get("v_path") or ""
    try:
        st = Path(artifact).stat() if artifact else None
    except OSError:
        st = None
    row = {
        "schema": "cosmos-collector/2",
        "collected_at": datetime.fromtimestamp(now).astimezone().isoformat(
            timespec="seconds"),
        "collected_epoch": int(now),
        "source": "node_worker_return",
        "lane": spec["id"],
        "agent": spec["agent"],
        "maker": spec["maker"],
        "app": spec["maker"],
        "task": rec.get("task_id") or rec.get("result_name") or "",
        "status": "ok" if rec.get("ok") else "failed",
        "rc": 0 if rec.get("ok") else 1,
        "artifact": artifact,
        "mtime": float(st.st_mtime) if st else now,
        "mtime_iso": datetime.fromtimestamp(
            st.st_mtime if st else now).astimezone().isoformat(
            timespec="seconds"),
        "summary": _oneline(
            f"{spec['id']} {rec.get('rail', {}).get('model')} "
            f"usd={rec.get('rail', {}).get('usd')} "
            f"{(rec.get('rail') or {}).get('text') or rec.get('error') or ''}"),
        "bytes": int(st.st_size) if st else 0,
        "kind": spec["id"],
        "link_id": (rec.get("rail") or {}).get("link_id"),
        "model": (rec.get("rail") or {}).get("model"),
        "usd": (rec.get("rail") or {}).get("usd"),
        "out": rec.get("out"),
        "out_landed": rec.get("out_landed"),
        "result_path": rec.get("result_path"),
        "v_path": rec.get("v_path"),
        "stamp": stamp,
        "worker": spec["worker"],
    }
    idx = index_path_for(paths)
    idx_rec = append_index_row(idx, row, lock_path=index_lock_for(paths))
    inbox = inbox_dir(paths) / (Path(rec.get("result_name") or "return").stem
                                + "_return.json")
    write_inbox_sidecar(inbox, row)
    rec["collector"] = {
        "wrote": idx_rec.get("wrote"),
        "path": idx_rec.get("path"),
        "inbox": str(inbox),
    }
    rec["marker"] = marker
    return rec


def land_critique_return(rec: dict, returns_path: Path | None) -> dict:
    """Write the critique body to the dispatch packet's designated returns path.

    done = nonempty rail text. rc is recorded, never the predicate.
    Empty text is FAILED, not a fake-DONE (docs/SCAR_PLACATION.md).
    A handoff JSON with kind_live=handoff and no body is assignment, not
    the agent's return — this function is what makes the handoff terminal.
    """
    if returns_path is None:
        return rec
    dest = Path(str(returns_path).strip())
    if not str(dest):
        return rec
    text = str((rec.get("rail") or {}).get("text") or "")
    nonempty = bool(text.strip())
    rec["done"] = nonempty
    rec["done_why"] = "nonempty_stdout" if nonempty else "empty_stdout"
    if not nonempty:
        rec["ok"] = False
        rec.setdefault("error", rec.get("error") or "EMPTY_OUTPUT")
    rec["rc"] = 0 if rec.get("ok") and nonempty else 2
    rec["stdout_tail"] = text[-4000:]
    rec["model"] = (rec.get("rail") or {}).get("model")
    rec["status"] = "returned" if rec.get("ok") and nonempty else "failed"
    rec["worker_result"] = rec.get("v_path") or rec.get("result_path") or str(dest)
    existing: dict = {}
    if dest.exists():
        try:
            raw = json.loads(dest.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                existing = raw
        except (OSError, ValueError):
            existing = {}
    payload = dict(existing)
    payload.update({
        "ok": rec.get("ok"),
        "done": rec["done"],
        "done_why": rec["done_why"],
        "rc": rec["rc"],
        "status": rec["status"],
        "kind": rec.get("node") or existing.get("kind"),
        "agent": rec.get("agent") or existing.get("agent"),
        "kind_live": existing.get("kind_live") or "handoff",
        "model": rec.get("model"),
        "rail": rec.get("rail"),
        "stdout_tail": rec["stdout_tail"],
        "worker_result": rec["worker_result"],
        "worker": rec.get("worker"),
        "error": rec.get("error"),
        "secs": rec.get("elapsed_s"),
        "consumer": rec.get("worker"),
        "pickup_id": rec.get("pickup_id"),
    })
    stdout_path = Path(str(dest) + ".stdout.txt")
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text(text, encoding="utf-8")
        payload["stdout_full"] = str(stdout_path)
        rec["stdout_full"] = str(stdout_path)
    except OSError as e:
        payload["stdout_full_error"] = f"{type(e).__name__}: {e}"
    atomic_json(dest, payload)
    rec["returns_path"] = str(dest)
    rec["returns_landed"] = True
    return rec


def process_drop(paths: CosmosPaths, spec: dict, drop_path: Path,
                 default_out: str = "V", cfg: dict | None = None,
                 *, rail_call=None, dhx_path: Path | None = None) -> dict:
    """Claim, execute via the node's rail, write dest, register."""
    t0 = time.time()
    cfg = cfg if cfg is not None else load_config(paths)
    stamp = _stamp_file()
    pickup_at = _iso_now()
    bucket = bucket_dir(paths, spec["id"])
    try:
        task = parse_task(drop_path, default_out=default_out)
    except WorkerError as e:
        failed = stage_drop(bucket, drop_path, stamp, failed=True)
        return {"ok": False, "kind": e.kind, "error": str(e),
                "drop_path": str(drop_path), "processed_drop": str(failed),
                "elapsed_s": round(time.time() - t0, 3)}

    # CLAIM FIRST so a crash cannot double-spend on retry.
    claimed = stage_drop(bucket, drop_path, stamp, failed=False)
    dest_key = task["out"]
    result_name = _result_name(task, spec, stamp)
    rec = {
        "schema": SCHEMA,
        "ok": False,
        "node": spec["id"],
        "worker": spec["worker"],
        "agent": spec["agent"],
        "task_id": task["id"],
        "prompt": task["prompt"],
        "out": dest_key,
        "result_name": result_name,
        "drop_path": str(drop_path),
        "drop_name": drop_path.name,
        "processed_drop": str(claimed),
        "pickup_at": pickup_at,
        "pickup_id": uuid.uuid4().hex[:12],
    }
    rail = execute_via_rail(paths, spec, task["prompt"], rail_call=rail_call)
    rec["rail"] = {
        "ok": bool(rail.get("ok")),
        "kind": rail.get("kind"),
        "link_id": rail.get("link_id"),
        "model": rail.get("model") or rail.get("node"),
        "usd": rail.get("usd"),
        "text": rail.get("text") or "",
        "detail": rail.get("detail"),
        "node": rail.get("node"),
    }
    rec["ok"] = bool(rail.get("ok"))
    if not rec["ok"]:
        rec["error"] = rail.get("detail") or rail.get("kind") or "RAIL_FAILED"
    rec["elapsed_s"] = round(time.time() - t0, 3)
    rec = write_result_files(paths, spec, rec, dest_key, cfg)
    rec = register_return(paths, spec, rec, dhx_path=dhx_path)
    if task.get("returns"):
        rec = land_critique_return(rec, Path(task["returns"]))
    atomic_json(Path(rec["v_path"]), rec)
    if rec.get("dest_path") and rec.get("out_landed") != "V":
        try:
            atomic_json(Path(rec["dest_path"]), rec)
        except OSError:
            pass
    return rec


def execute_handoff(root, node, agent, task, result_path,
                    *, rail_call=None, timeout_s=1800,
                    dhx_path=None, returns_path=None) -> dict:
    """Drop onto live/buckets/<node>, run the node's rail, emit stdout.

    done = non-empty rail text written beside the dispatch result.
    rc is recorded, never the predicate (empty text + rc=0 was the scar).
    timeout_s is accepted for the dispatch-job contract; the rail itself
    is spend-gated, not wall-clocked here.
    """
    spec = node_spec(node)
    try:
        paths = CosmosPaths(root)
    except CosmosPathError as e:
        raise WorkerError("NO_ROOT", str(e)) from e
    t0 = time.time()
    stamp = _iso_now()
    file_stamp = _stamp_file()
    bucket = bucket_dir(paths, spec["id"])
    task_id = f"handoff-{file_stamp}"
    dest = bucket / f"{task_id}.json"
    dest_result = str(result_path) if result_path else None
    dest_returns = str(returns_path) if returns_path else dest_result
    packet = {
        "agent": agent, "kind": spec["id"],
        "assignment": task, "prompt": task,
        "stamp": stamp, "id": task_id, "out": "V",
        "result": dest_result,
        "returns": dest_returns,
    }
    dest.write_text(json.dumps(packet, indent=1), encoding="utf-8")
    rec = process_drop(paths, spec, dest, rail_call=rail_call,
                       dhx_path=dhx_path)
    text = str((rec.get("rail") or {}).get("text") or "")
    nonempty = bool(text.strip())
    stdout_path = rec.get("stdout_full")
    if dest_result:
        if not stdout_path:
            stdout_path = str(dest_result) + ".stdout.txt"
        try:
            Path(dest_result).parent.mkdir(parents=True, exist_ok=True)
            Path(stdout_path).write_text(text, encoding="utf-8")
        except OSError:
            stdout_path = rec.get("stdout_full")
    return {
        "agent": agent,
        "kind": spec["id"],
        "kind_live": "handoff",
        "ok": bool(rec.get("ok") and nonempty),
        "done": nonempty,
        "done_why": ("nonempty_stdout" if nonempty else "empty_stdout"),
        "rc": 0 if nonempty else 2,
        "secs": round(time.time() - t0, 1),
        "stdout_tail": (rec.get("stdout_tail") or text[-4000:]),
        "stdout_full": stdout_path,
        "worker_packet": rec.get("processed_drop") or str(dest),
        "worker_result": rec.get("v_path") or rec.get("result_path"),
        "rail": rec.get("rail"),
        "error": rec.get("error") or (None if nonempty else "empty_stdout"),
        "elapsed_s": rec.get("elapsed_s"),
        "model": (rec.get("rail") or {}).get("model"),
        "link_id": (rec.get("rail") or {}).get("link_id"),
        "status": "returned" if nonempty else "failed",
        "returns_path": rec.get("returns_path") or dest_returns,
        "timeout_s": int(timeout_s),
    }


def poll_once(root: str, node: str, polls: int = 0,
              interval_s: float | None = None, default_out: str = "V",
              *, drain: bool = True, rail_call=None,
              dhx_path: Path | None = None) -> dict:
    """One tick. Heartbeat always. PAUSE + drain=False => pick up NOTHING."""
    spec = node_spec(node)
    try:
        paths = CosmosPaths(root)
    except CosmosPathError as e:
        raise WorkerError("NO_ROOT", str(e)) from e
    cfg = load_config(paths)
    interval = (interval_s if interval_s is not None
                else float(cfg.get("interval_s") or DEFAULT_INTERVAL_S))
    hb_path = paths.logs(spec["heartbeat"])
    bucket = bucket_dir(paths, spec["id"])
    paused = pause_flag(paths)
    extra = {
        "schema": SCHEMA,
        "tick": "poll",
        "state": "RUNNING",
        "node": spec["id"],
        "pause_present": paused is not None,
        "bucket": str(bucket),
        "out_default": canon_out(default_out),
        "tree_id": paths.sentinel.tree_id,
        "no_bts": True,
    }
    if is_paused(paused):
        extra["state"] = "PAUSED"
        extra["tick"] = "paused"
        extra["mode"] = str(paused.get("mode") or "hold")
        extra["auto_resume_at"] = paused.get("auto_resume_at")
        extra["pause"] = {
            "reason": paused.get("reason"),
            "set_by": paused.get("set_by"),
            "set_at": paused.get("set_at"),
            "path": paused.get("path"),
        }
        if not drain:
            extra["picked_this_tick"] = 0
            extra["jobs"] = []
            hb = write_heartbeat(hb_path, spec["worker"], extra=extra,
                                 polls=polls, interval_s=interval)
            extra["ok"] = True
            extra["heartbeat"] = hb
            extra["heartbeat_path"] = str(hb_path)
            return extra
        extra["tick"] = "once_while_paused"

    jobs = []
    errors = []
    if drain:
        drops = list_drop_files(bucket)
        extra["drops_seen"] = len(drops)
        extra["drop_names"] = [p.name for p in drops]
        # one task per tick — a long rail call must not starve the heartbeat
        for dp in drops[:1]:
            try:
                rec = process_drop(
                    paths, spec, dp, default_out=default_out, cfg=cfg,
                    rail_call=rail_call, dhx_path=dhx_path)
                jobs.append(rec)
            except WorkerError as e:
                errors.append({"drop": str(dp), "kind": e.kind, "error": str(e)})
            except Exception as e:  # noqa: BLE001
                errors.append({"drop": str(dp),
                               "kind": type(e).__name__, "error": str(e)})
    extra["picked_this_tick"] = len(jobs)
    extra["jobs"] = [{
        "ok": j.get("ok"),
        "task_id": j.get("task_id"),
        "result_path": j.get("result_path"),
        "v_path": j.get("v_path"),
        "out": j.get("out"),
        "out_landed": j.get("out_landed"),
        "model": (j.get("rail") or {}).get("model"),
        "link_id": (j.get("rail") or {}).get("link_id"),
        "usd": (j.get("rail") or {}).get("usd"),
        "dhx_marker": j.get("dhx_marker"),
        "error": j.get("error"),
    } for j in jobs]
    extra["errors"] = errors
    extra["tick"] = extra.get("tick") if extra.get("tick") not in (
        "poll",) else ("drained" if jobs else "idle")
    extra["ok"] = not errors and all(j.get("ok") for j in jobs) if jobs else (
        not errors)
    hb = write_heartbeat(hb_path, spec["worker"], extra=extra,
                         polls=polls, interval_s=interval)
    extra["heartbeat"] = hb
    extra["heartbeat_path"] = str(hb_path)
    return extra


def loop(root: str, node: str, interval_s: float,
         default_out: str = "V") -> int:
    spec = node_spec(node)
    paths = CosmosPaths(root)
    out_path = paths.logs(f"{spec['id']}_worker.out")
    err_path = paths.logs(f"{spec['id']}_worker.err")
    lock_path = paths.logs(spec["lock"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(out_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(lock_path)
    if fd is None:
        rec = read_heartbeat(paths.logs(spec["heartbeat"]))
        age = heartbeat_age_s(rec)
        pid = (rec or {}).get("pid")
        if age is not None and age < FRESH_S and pid_alive(int(pid or 0)):
            print(json.dumps({"already_running": True, "pid": pid,
                              "age_s": round(age, 3),
                              "node": spec["id"]}), flush=True)
            return 0
        print(f"{spec['id']} worker lock held and heartbeat not fresh - refusing",
              flush=True)
        return 2
    polls = 0
    print(json.dumps({"loop": True, "pid": os.getpid(), "node": spec["id"],
                      "interval_s": interval_s}, indent=1), flush=True)
    try:
        while True:
            polls += 1
            paused = pause_flag(paths)
            drain = not is_paused(paused)
            try:
                poll_once(root, spec["id"], polls=polls, interval_s=interval_s,
                          default_out=default_out, drain=drain)
            except Exception:
                import traceback
                tb = traceback.format_exc()
                try:
                    err_path.write_text(tb, encoding="utf-8")
                except OSError:
                    pass
                try:
                    write_heartbeat(
                        paths.logs(spec["heartbeat"]), spec["worker"],
                        extra={"tick": "error", "state": "ERROR",
                               "error": tb[-500:], "node": spec["id"]},
                        polls=polls, interval_s=interval_s)
                except OSError:
                    pass
            time.sleep(interval_s)
    finally:
        os.close(fd)
    return 0


def standup(root: str, node: str, interval_s: float = DEFAULT_INTERVAL_S,
            default_out: str = "V") -> dict:
    spec = node_spec(node)
    paths = CosmosPaths(root)
    hb = paths.logs(spec["heartbeat"])
    t0 = time.time()
    proof = wait_fresh(hb, timeout_s=1.2, max_age_s=FRESH_S)
    if proof["ok"]:
        return {"started": "already", "proof": proof, "keith_cmd": None,
                "task_name": spec["task_name"], "node": spec["id"]}

    script = script_for(spec)
    extra = ["--loop"]
    if default_out and default_out.upper() != "V":
        extra.extend(["--out", canon_out(default_out)])
    tr = tr_cmdline(script, root, *extra)
    minute = create_task(spec["task_name"], tr, "minute", mo=1, run_now=True)
    logon = create_task(spec["task_logon"], tr, "onlogon")
    launched_via = None
    detach = None
    if minute.get("ok") and minute.get("run_ok"):
        launched_via = "schtasks"
        proof = wait_fresh(hb, timeout_s=12.0, min_epoch=t0, max_age_s=FRESH_S)
    if not proof.get("ok"):
        argv = [pythonw_exe(), str(script), "--root",
                str(Path(root).resolve()), "--loop"]
        if default_out and default_out.upper() != "V":
            argv.extend(["--out", canon_out(default_out)])
        detach = spawn_detached(argv, str(script.parent),
                                paths.logs(f"{spec['id']}_worker.out"))
        launched_via = detach.get("method") or "detached"
        expect = detach.get("pid") if isinstance(detach.get("pid"), int) else None
        proof = wait_fresh(hb, timeout_s=15.0, min_epoch=t0, max_age_s=FRESH_S,
                           expect_pid=expect)

    keith = []
    for rec in (minute, logon):
        if rec.get("keith_cmd") and (rec.get("needs_elevation") or not rec.get("ok")):
            keith.append(rec["keith_cmd"])
        h = rec.get("harden") or {}
        if h.get("keith_cmd") and not h.get("ok"):
            keith.append(h["keith_cmd"])
    return {
        "started": launched_via,
        "node": spec["id"],
        "task_minute": minute,
        "task_logon": logon,
        "detach": detach,
        "proof": proof,
        "heartbeat_path": str(hb),
        "keith_cmd": " & ".join(keith) if keith else None,
        "keith_cmds": keith,
        "task_name": spec["task_name"],
    }


def status_probe(root: str, node: str) -> dict:
    spec = node_spec(node)
    paths = CosmosPaths(root)
    hb = paths.logs(spec["heartbeat"])
    rec = read_heartbeat(hb)
    age = heartbeat_age_s(rec)
    paused = pause_flag(paths)
    bucket = paths.role("root", "buckets", spec["id"])
    n = 0
    if bucket.exists():
        n = sum(1 for p in bucket.iterdir()
                if p.is_file() and p.suffix.lower() in DROP_SUFFIXES
                and not p.name.startswith("_") and not p.name.startswith("."))
    return {
        "node": spec["id"],
        "path": str(hb),
        "age_s": age,
        "heartbeat": rec,
        "pause_present": paused is not None,
        "pause": paused,
        "bucket": str(bucket),
        "drops_waiting": n,
        "task": query_task(spec["task_name"]),
        "fresh": age is not None and age < FRESH_S,
    }


def build_parser(prog: str | None = None) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog=prog or "cosmos_node_worker")
    ap.add_argument("--root", required=True)
    ap.add_argument("--node", choices=sorted(NODES), default=None)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--out", default="V", help="V (default, BEST) | GDX | ODX")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    return ap


def run_cli(argv: list[str] | None = None, *, node: str | None = None) -> int:
    ap = build_parser("cosmos_grok_worker" if node == "grok"
                      else ("cosmos_gem_worker" if node == "gem"
                            else ("cosmos_oa_worker" if node == "oa"
                                  else "cosmos_node_worker")))
    a = ap.parse_args(argv)
    chosen = node or a.node
    if not chosen:
        ap.error("--node grok|gem|oa is required (or use cosmos_grok_worker / "
                 "cosmos_gem_worker / cosmos_oa_worker)")
    spec = node_spec(chosen)
    default_out = canon_out(a.out)
    if a.status:
        rec = status_probe(a.root, spec["id"])
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("fresh") else 2
    if a.standup:
        r = standup(a.root, spec["id"], a.interval, default_out=default_out)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2
    if a.once:
        # Commanded drain: Keith/COW explicit --once, even while PAUSE is up.
        # The --loop vehicle idles on PAUSE (pick up NOTHING).
        r = poll_once(a.root, spec["id"], interval_s=a.interval,
                      default_out=default_out, drain=True)
        out = {k: r[k] for k in r if k != "heartbeat"}
        print(json.dumps(out, indent=1, default=str))
        return 0 if r.get("ok") else 2
    if a.loop or True:
        return loop(a.root, spec["id"], a.interval, default_out=default_out)


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
    except WorkerError as e:
        print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)},
                         indent=1))
        raise SystemExit(2)
