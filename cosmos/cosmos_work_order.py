#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_work_order - typed work-order record + DONE/COMPLETED split.

Schema (docs/WORK_ORDER_SPEC.md), exact fields:

    Agent            Family | Clade | Version
    Context source   [read*] inputs the agent READS (never writes)
    Task             the assignment
    Target & scope   what it targets + the boundary of what it may produce
    Timestamp        when the work order was dropped
    Output           folder | filename  — the agent's only write surface

Lifecycle: DROPPED -> PICKED_UP -> DONE (runner, iff Output exists and is
non-empty) -> CHECKED (same runner, stamps checks.* on the DONE record,
does not COMPLETE) -> COMPLETED (COW only, via accept_order). DONE !=
COMPLETED. Reject stays DONE. Missing output is FAILED and cannot be
accepted. FAILED is not checked.

P10 is the cwd: every rail is pointed at an attempt-private workspace under
the work role. Agents never write the live tree. accept_order READS the
output; if the output is a proposal, COW implements it through the fenced
commit gateway.

    from cosmos_work_order import (
        parse_order, parse_agent, parse_context_source, parse_output,
        route_agent, build_argv, file_done, accept_order, reject_order,
        notify_core_picked,
    )
    from cosmos_work_order_checks import apply_done_checks, cow_checks_view

Does not open live/ledger/. Pickup POSTs Core WORK_ORDER_PICKED (http
seam). No bts_* import. Does not edit cosmos_dispatch.py grok/claude/cursor
job templates.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from cosmos_workspace import (  # noqa: E402
    WorkspaceError,
    order_workspace,
    output_exists,
    output_path,
    refuse_tree_cwd,
    stage_context,
)

SCHEMA = "cosmos-work-order/1"
SPEC_FIELDS = (
    "Agent",
    "Context source",
    "Task",
    "Target & scope",
    "Timestamp",
    "Output",
)
STATES = ("DROPPED", "PICKED_UP", "DONE", "COMPLETED", "FAILED")
OUTPUT_HEAD = 4000
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

# MODEL_ACCESS families only. Cursor is a lane, not a family — BAD_INPUT.
# OpenAI coding work-orders go through the Codex CLI (not oa-api).
FAMILY_RAIL = {
    "anthropic": "claude",
    "claude": "claude",
    "xai": "grok",
    "grok": "grok",
    "openai": "codex",
    "gpt": "codex",
    "google": "gemini",
    "gemini": "gemini",
}
REFUSED_FAMILIES = frozenset({
    "cursor", "anysphere", "composer", "windsurf", "copilot",
})
RAIL_BINARY = {
    "claude": "claude",
    "grok": "grok",
    "codex": "codex",
    "gemini": "gemini",
}
# Agent Version that is a ROLE, not a grok CLI model id.
# Live fail: `Couldn't set model 'prepaid-orch': unknown model id`
# (wo-20260902T210700-8a1b4f52, 112 of 126 failed pile).
GROK_MODEL_ALIASES = {
    "prepaid-orch": "grok-4.6",
}
GROK_FLAGS = (
    "--single", "--output-format", "plain", "--always-approve",
    "--max-turns", "60",
)


class OrderError(RuntimeError):
    """kind in {BAD_INPUT, REFUSED, BROKE, NO_CONTEXT, FAILED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def _fold(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(s or "").strip().lower())


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def new_order_id(raw: dict | None = None) -> str:
    raw = raw or {}
    stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S")
    basis = (str(raw.get("Task") or "") + "|" + str(raw.get("Agent") or "")
             + "|" + str(time.time()))
    h = hashlib.sha1(basis.encode("utf-8", errors="replace")).hexdigest()[:8]
    return f"wo-{stamp}-{h}"


def _safe_id(order_id: str) -> str:
    s = "".join(ch if ch.isalnum() or ch in "-_." else "-"
                for ch in str(order_id or "").strip())[:80]
    if not s or s in (".", "..") or ".." in s:
        raise OrderError("BAD_INPUT", f"unsafe order_id {order_id!r}")
    return s


def parse_agent(value) -> dict:
    """Family | Clade | Version. Exactly three parts. Cursor family refused."""
    if not isinstance(value, str) or not value.strip():
        raise OrderError("BAD_INPUT", "Agent is required (Family | Clade | Version)")
    parts = [p.strip() for p in value.split("|")]
    if len(parts) != 3 or not all(parts):
        raise OrderError(
            "BAD_INPUT",
            "Agent must be exactly Family | Clade | Version "
            f"(got {len(parts)} part(s))")
    family, clade, version = parts
    folded = _fold(family)
    if folded in REFUSED_FAMILIES:
        raise OrderError(
            "BAD_INPUT",
            f"Agent family {family!r} is not a MODEL_ACCESS family")
    if folded not in FAMILY_RAIL:
        raise OrderError(
            "BAD_INPUT",
            f"unknown Agent family {family!r} "
            "(want Anthropic|xAI|OpenAI|Google)")
    return {
        "raw": value.strip(),
        "family": family,
        "clade": clade,
        "version": version,
        "family_fold": folded,
    }


def parse_context_source(value) -> list:
    """[read*] only. Write-mode context is REFUSED. Missing path is BAD_INPUT."""
    if value is None:
        raise OrderError("BAD_INPUT", "Context source is required")
    if isinstance(value, (str, dict)):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        raise OrderError("BAD_INPUT", "Context source must be a path or list")
    out = []
    for i, item in enumerate(items):
        mode = "read"
        path = None
        if isinstance(item, dict):
            path = item.get("path") or item.get("src") or item.get("file")
            mode = str(item.get("mode") or item.get("access") or "read").strip().lower()
            marker = str(item.get("marker") or "")
        elif isinstance(item, str):
            s = item.strip()
            m = re.match(r"^(.*?)(?:\s*\[([^\]]+)\])\s*$", s)
            if m:
                path, marker = m.group(1).strip(), m.group(2).strip().lower()
            else:
                path, marker = s, "read*"
        else:
            raise OrderError("BAD_INPUT", f"Context source[{i}] is not a path")
        marker = str(marker or "read*").strip().lower()
        if mode not in ("read", "read*", "r", "readonly", "read-only"):
            raise OrderError(
                "REFUSED",
                f"Context source[{i}] write-mode refused (got mode={mode!r})")
        if any(tok in marker.replace(" ", "") for tok in (
                "write", "write*", "rw", "w+", "readwrite")):
            raise OrderError(
                "REFUSED",
                f"Context source[{i}] write-mode refused (got [{marker}])")
        if not str(path or "").strip():
            raise OrderError("BAD_INPUT", f"Context source[{i}] empty")
        out.append({"path": str(path).strip(), "mode": "read", "index": i})
    return out


def _is_absolute_spec(s: str) -> bool:
    t = str(s or "").strip()
    if not t:
        return False
    p = Path(t)
    if p.is_absolute():
        return True
    if len(t) > 1 and t[1] == ":":
        return True
    if t.startswith("/") or t.startswith("\\"):
        return True
    return False


def parse_output(value) -> dict:
    """folder | filename. Absolute Output is REFUSED (P10: only the workspace)."""
    if value is None or (isinstance(value, str) and not value.strip()):
        raise OrderError("BAD_INPUT", "Output is required (folder | filename)")
    folder = None
    filename = None
    if isinstance(value, dict):
        folder = value.get("folder") or value.get("dir")
        filename = value.get("filename") or value.get("file") or value.get("name")
        if folder is not None:
            folder = str(folder).strip() or None
        if filename is not None:
            filename = str(filename).strip() or None
    elif isinstance(value, str):
        s = value.strip()
        if "|" in s:
            left, right = s.split("|", 1)
            folder, filename = left.strip() or None, right.strip() or None
        else:
            filename = s
    else:
        raise OrderError("BAD_INPUT", "Output must be 'folder | filename'")
    if not filename:
        raise OrderError("BAD_INPUT", "Output filename is required")
    if _is_absolute_spec(filename) or (folder and _is_absolute_spec(folder)):
        raise OrderError(
            "REFUSED",
            "absolute Output refused — Output is folder | filename "
            "inside the attempt-private workspace")
    if ".." in filename.replace("\\", "/") or (
            folder and ".." in str(folder).replace("\\", "/")):
        raise OrderError("REFUSED", "Output path traversal refused")
    return {"raw": value if isinstance(value, str) else
            f"{folder or ''} | {filename}".strip(" |"),
            "folder": folder, "filename": filename}


def parse_order(raw) -> dict:
    """Validate the six spec fields. Extra keys are preserved (order_id, notes)."""
    if not isinstance(raw, dict):
        raise OrderError("BAD_INPUT", "work order must be a JSON object")
    missing = [f for f in SPEC_FIELDS if f not in raw]
    if missing:
        raise OrderError(
            "BAD_INPUT", f"missing spec field(s): {', '.join(missing)}")
    agent = parse_agent(raw["Agent"])
    context = parse_context_source(raw["Context source"])
    task = raw["Task"]
    if not isinstance(task, str) or not task.strip():
        raise OrderError("BAD_INPUT", "Task is required")
    scope = raw["Target & scope"]
    if not isinstance(scope, str) or not scope.strip():
        raise OrderError("BAD_INPUT", "Target & scope is required")
    ts = raw["Timestamp"]
    if not isinstance(ts, str) or not ts.strip():
        raise OrderError("BAD_INPUT", "Timestamp is required")
    output = parse_output(raw["Output"])
    from cosmos_portfolio_attribution import AttributionError, parse_work_order_tags
    try:
        tags = parse_work_order_tags(raw)
    except AttributionError as e:
        raise OrderError("BAD_INPUT", str(e)) from e
    rec = dict(raw)
    rec.update(tags)
    rec["_schema"] = SCHEMA
    rec["_agent"] = agent
    rec["_context"] = context
    rec["_output"] = output
    rec["Task"] = task.strip()
    rec["Target & scope"] = scope.strip()
    rec["Timestamp"] = ts.strip()
    return rec


def claude_model(version: str, clade: str = "") -> str:
    """sonnet-5 -> claude-sonnet-5. CLI aliases (sonnet/haiku/opus/fable) kept."""
    v = str(version or "").strip()
    if not v:
        c = _fold(clade)
        return {"sonnet": "sonnet", "haiku": "haiku",
                "opus": "opus", "fable": "claude-fable-5"}.get(c, "sonnet")
    if v.startswith("claude-"):
        return v
    if v in ("sonnet", "haiku", "opus", "fable"):
        return v
    return f"claude-{v}"


VERTEX_CONFIG_NAME = "vertex.json"


def vertex_cli_env(live_root, base: dict | None = None) -> dict:
    """Gemini CLI Vertex wallet from live/config/vertex.json. Never prints keys.

    gemini.cmd in vertex-ai auth mode needs GOOGLE_CLOUD_PROJECT +
    GOOGLE_CLOUD_LOCATION (wo-20260901T205646 rc=41). Studio keys in the
    parent env steal the wallet — drop them. The Express API key stays in
    the existing secrets file for bts_vertex; this env is ADC + project.
    """
    env = dict(os.environ if base is None else base)
    if not live_root:
        return env
    cfg = Path(live_root) / "config" / VERTEX_CONFIG_NAME
    obj = {}
    if cfg.is_file():
        try:
            raw = json.loads(cfg.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                obj = raw
        except (OSError, ValueError, UnicodeDecodeError):
            obj = {}
    project = str(obj.get("project") or "").strip()
    location = str(obj.get("location") or "global").strip() or "global"
    if project:
        env["GOOGLE_CLOUD_PROJECT"] = project
        env["GOOGLE_CLOUD_LOCATION"] = location
        env["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
        env.pop("GEMINI_API_KEY", None)
        env.pop("GOOGLE_API_KEY", None)
    return env


def gemini_binary() -> str:
    """Prefer gemini.cmd over gemini.ps1 (execution-policy dead). Never Ruby `gem`."""
    cmd = shutil.which("gemini.cmd")
    if cmd:
        return cmd
    found = shutil.which("gemini")
    if found and found.lower().endswith(".ps1"):
        cmd = shutil.which("gemini.cmd")
        return cmd or "gemini.cmd"
    return found or "gemini"


def route_agent(agent) -> dict:
    """Family|Clade|Version -> {rail, binary, model}."""
    parsed = agent if isinstance(agent, dict) and "family_fold" in agent else (
        parse_agent(agent))
    rail = FAMILY_RAIL[parsed["family_fold"]]
    version = parsed["version"]
    if rail == "claude":
        model = claude_model(version, parsed.get("clade") or "")
        binary = RAIL_BINARY[rail]
    elif rail == "gemini":
        model = version
        binary = gemini_binary()
    elif rail == "grok":
        model = GROK_MODEL_ALIASES.get(version, version)
        binary = RAIL_BINARY[rail]
    else:
        model = version
        binary = RAIL_BINARY[rail]
    return {
        "rail": rail,
        "binary": binary,
        "model": model,
        "family": parsed["family"],
        "clade": parsed["clade"],
        "version": version,
    }


def compose_prompt(order: dict, *, workspace: Path, output: Path) -> str:
    ctx = order.get("_context") or []
    ctx_lines = "\n".join(f"  - {c['path']}" for c in ctx) or "  (none)"
    return (
        f"{order['Task']}\n\n"
        f"Target & scope: {order['Target & scope']}\n"
        f"Context source [read*] (copies under {Path(workspace) / 'context'}):\n"
        f"{ctx_lines}\n\n"
        f"WRITE ONLY this output file (WRITE-PRIVATE): {output}\n"
        "Do not write the live tree. Do not git push. Do not open a PR. "
        "The fenced commit gateway is how anything enters the tree."
    )


def build_argv(order, workspace: Path, *, prompt: str | None = None,
               output: Path | None = None) -> list:
    """WRITE-PRIVATE argv. cwd/add-dir/--cwd is the attempt-private workspace.

    Proven grok flag set is kept and retargeted at the workspace.
    Claude --add-dir is the workspace. Gemini is the `gemini` binary (not `gem`).
    """
    parsed = order if isinstance(order, dict) and "_agent" in order else parse_order(order)
    routed = route_agent(parsed["_agent"])
    ws = str(Path(workspace))
    text = prompt if prompt is not None else parsed["Task"]
    rail = routed["rail"]
    model = routed["model"]
    if rail == "grok":
        return [
            "grok", "--single", text, "-m", model,
            "--output-format", "plain", "--always-approve",
            "--max-turns", "60", "--cwd", ws,
        ]
    if rail == "claude":
        raise ValueError(
            "[ANTHROPIC_OFF] Keith 2026-09-01: work-order will not shell claude")
    if rail == "gemini":
        return [
            routed["binary"], "-p", text, "-m", model,
            "--approval-mode", "auto_edit",
        ]
    # OpenAI / Codex CLI — same shape as CodexRail.coder
    last = str(Path(workspace) / "codex_last_message.txt")
    argv = [
        "codex", "exec",
        "--sandbox", "workspace-write",
        "--skip-git-repo-check",
        "--json",
        "--output-last-message", last,
        "--color", "never",
        "--ignore-user-config",
    ]
    if model:
        argv.extend(["--model", str(model)])
    argv.append(text)
    return argv


def infer_repo_tree(live_root: Path | str) -> Path:
    """Repo tree sits beside the runtime root (V:\\A\\Ai\\COSMOS / live)."""
    parent = Path(live_root).resolve().parent
    if (parent / "cosmos").is_dir() and (parent / "docs").is_dir():
        return parent
    return parent


FOLD_FOLDERS = ("bucket", "picked", "failed", "assigned", "completed")
FOLD_LIMIT = 200
TASK_PREVIEW = 240


def work_order_dirs_ro(paths) -> dict:
    """Same topology as work_order_dirs. GET must not mkdir (a read is a write)."""
    base = paths.state("work_orders")
    return {
        "bucket": base / "bucket",
        "picked": base / "picked",
        "assigned": base / "assigned",
        "completed": base / "completed",
        "failed": base / "failed",
    }


def work_order_dirs(paths) -> dict:
    """Resolver-only topology. paths is a CosmosPaths."""
    dirs = work_order_dirs_ro(paths)
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def _public_checks(checks) -> dict | None:
    if not isinstance(checks, dict):
        return None
    out = {}
    for name in ("github", "cursor", "gitlab"):
        row = checks.get(name)
        if not isinstance(row, dict):
            continue
        out[name] = {
            "status": row.get("status"),
            "url": row.get("url"),
            "detail": str(row.get("detail") or "")[:160],
        }
    return out or None


def _public_core_picked(rec) -> dict | None:
    cp = rec.get("core_picked") if isinstance(rec, dict) else None
    if not isinstance(cp, dict):
        return None
    keep = {}
    for k in ("ok", "already", "seq", "kind", "http", "detail"):
        if cp.get(k) is not None:
            keep[k] = cp.get(k)
    return keep or None


def public_order_row(raw: dict, folder: str) -> dict:
    """List/detail row. No argv, no prompt, no key material."""
    agent = raw.get("_agent") if isinstance(raw.get("_agent"), dict) else {}
    outp = raw.get("_output") if isinstance(raw.get("_output"), dict) else {}
    run = raw.get("run") if isinstance(raw.get("run"), dict) else {}
    task = str(raw.get("Task") or "")
    oid = str(raw.get("order_id") or "")
    exists = bool(raw.get("output_exists"))
    filename = str(outp.get("filename") or "")
    row = {
        "order_id": oid,
        "folder": folder,
        "state": str(raw.get("state") or folder.upper()),
        "agent": str(raw.get("Agent") or agent.get("raw") or ""),
        "family": str(agent.get("family") or ""),
        "clade": str(agent.get("clade") or ""),
        "version": str(agent.get("version") or ""),
        "task": task[:TASK_PREVIEW],
        "task_len": len(task),
        "output": str(raw.get("Output") or outp.get("raw") or ""),
        "output_folder": outp.get("folder"),
        "output_filename": filename,
        "output_exists": exists,
        "product": filename if exists else None,
        "portfolio_product": raw.get("portfolio_product"),
        "portfolio_stage": raw.get("portfolio_stage"),
        "attribution": raw.get("attribution") or "UNATTRIBUTED",
        "timestamp": str(raw.get("Timestamp") or ""),
        "dropped_at": raw.get("dropped_at"),
        "picked_at": raw.get("picked_at"),
        "filed_at": raw.get("filed_at"),
        "accepted_at": raw.get("accepted_at") or raw.get("completed_at"),
        "observed_rc": raw.get("observed_rc"),
        "elapsed_s": run.get("elapsed_s"),
        "timed_out": run.get("timed_out"),
        "fail_kind": raw.get("fail_kind"),
        "fail_detail": str(raw.get("fail_detail") or "")[:200] or None,
        "checks": _public_checks(raw.get("checks")),
        "core_picked": _public_core_picked(raw),
        "github_path": raw.get("github_path"),
        "source_url": raw.get("source_url"),
        "sort": (
            str(raw.get("picked_at") or raw.get("filed_at")
                or raw.get("dropped_at") or raw.get("Timestamp") or "")
            + "|" + oid
        ),
    }
    return row


def fold_work_orders(paths, *, order_id: str = "", state: str = "",
                     limit=FOLD_LIMIT) -> dict:
    """GET projection. Folders are not authority; this is the live list.

    Does not mkdir. Does not append the ledger. ?id= returns one row plus
    output_head (work product). limit caps the list, not the counts.
    """
    try:
        lim = int(limit)
    except (TypeError, ValueError):
        lim = FOLD_LIMIT
    if lim < 1:
        lim = 1
    if lim > 500:
        lim = 500
    dirs = work_order_dirs_ro(paths)
    base = paths.state("work_orders")
    by_id: dict[str, dict] = {}
    counts = {name: 0 for name in FOLD_FOLDERS}
    unreadable = 0
    for folder in FOLD_FOLDERS:
        d = dirs[folder]
        if not d.is_dir():
            continue
        try:
            names = list(d.iterdir())
        except OSError:
            continue
        for p in names:
            if not p.is_file() or p.suffix.lower() != ".json":
                continue
            if p.name.startswith("_") or p.name.endswith(".tmp"):
                continue
            try:
                raw = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError, UnicodeDecodeError):
                unreadable += 1
                continue
            if not isinstance(raw, dict):
                unreadable += 1
                continue
            oid = str(raw.get("order_id") or p.stem)
            raw["order_id"] = oid
            counts[folder] += 1
            by_id[oid] = public_order_row(raw, folder)
            by_id[oid]["_raw_output_path"] = raw.get("_output_path")
            by_id[oid]["_task_full"] = str(raw.get("Task") or "")
    want = str(order_id or "").strip()
    if want:
        row = by_id.get(want)
        if not row:
            return {
                "ok": True, "available": True, "kind": "NOT_FOUND",
                "order_id": want, "order": None, "rows": [],
                "counts": counts, "unreadable": unreadable,
                "schema": "cosmos-work-orders/1",
                "note": "folders are the live list; ledger WORK_ORDER_PICKED is the pickup receipt",
            }
        out = dict(row)
        out.pop("_raw_output_path", None)
        task_full = out.pop("_task_full", "")
        out["task"] = task_full
        head = None
        head_err = None
        op = row.get("_raw_output_path")
        if op and Path(op).is_file():
            try:
                head = _output_head(Path(op))
            except OrderError as e:
                head_err = e.detail
        elif op:
            head_err = "Output file missing or empty"
        return {
            "ok": True, "available": True, "kind": "OK",
            "order_id": want, "order": out,
            "output_head": head, "output_head_error": head_err,
            "counts": counts, "unreadable": unreadable,
            "schema": "cosmos-work-orders/1",
            "note": "GET never mutates; --accept is still the COMPLETED write",
        }

    st = str(state or "").strip().upper()
    rows = list(by_id.values())
    if st and st != "ALL":
        folder_alias = {
            "BUCKET": "bucket", "DROPPED": "bucket",
            "PICKED": "picked", "PICKED_UP": "picked",
            "ASSIGNED": "assigned", "DONE": "assigned",
            "COMPLETED": "completed", "FAILED": "failed",
        }
        want_folder = folder_alias.get(st)
        if want_folder:
            rows = [r for r in rows if r.get("folder") == want_folder]
        else:
            rows = [r for r in rows if str(r.get("state") or "").upper() == st]
    rows.sort(key=lambda r: str(r.get("sort") or ""), reverse=True)
    shown = []
    for r in rows[:lim]:
        item = dict(r)
        item.pop("_raw_output_path", None)
        item.pop("_task_full", None)
        shown.append(item)
    n_all = sum(counts.values())
    return {
        "ok": True,
        "available": base.is_dir(),
        "kind": "OK" if base.is_dir() else "NO_SOURCE",
        "schema": "cosmos-work-orders/1",
        "rows": shown,
        "n_shown": len(shown),
        "n_total": n_all,
        "truncated": len(rows) > lim,
        "counts": counts,
        "unreadable": unreadable,
        "limit": lim,
        "state": st or "ALL",
        "note": (
            "timestamped live list from state/work_orders/{bucket,picked,"
            "assigned,completed,failed}. Folders are not the ledger. "
            "GET ?id= returns work product head. No argv/prompt."
        ),
    }


def _atomic_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")
    tmp.replace(path)


def _read_json(path: Path) -> dict:
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise OrderError("BROKE", f"unreadable order {path}: {e}") from e
    if not isinstance(obj, dict):
        raise OrderError("BAD_INPUT", f"order {path} is not an object")
    return obj


def order_file(folder: Path, order_id: str) -> Path:
    return Path(folder) / f"{_safe_id(order_id)}.json"


def find_order(dirs: dict, order_id: str) -> tuple[str, Path, dict]:
    oid = _safe_id(order_id)
    for name in ("assigned", "picked", "bucket", "failed", "completed"):
        p = order_file(dirs[name], oid)
        if p.is_file():
            return name, p, _read_json(p)
    raise OrderError("BROKE", f"order {oid} not found")


def pickup_order(paths, drop_path: Path, *, repo_tree: Path | str | None = None,
                 live_root=None) -> dict:
    """Move a bucket drop to picked/, stage context, refuse live-tree cwd."""
    dirs = work_order_dirs(paths)
    raw = _read_json(drop_path)
    parsed = parse_order(raw)
    oid = _safe_id(raw.get("order_id") or drop_path.stem or new_order_id(raw))
    parsed["order_id"] = oid
    parsed["state"] = "PICKED_UP"
    parsed["picked_at"] = _iso_now()
    root = live_root if live_root is not None else paths.root
    repo = Path(repo_tree) if repo_tree is not None else infer_repo_tree(root)
    ws = order_workspace(root, oid, repo_tree=repo)
    refuse_tree_cwd(ws, root, repo_tree=repo)
    staged = stage_context(
        parsed["_context"], ws / "context", repo_tree=repo)
    out = output_path(ws, parsed["_output"]["folder"],
                      parsed["_output"]["filename"])
    parsed["_workspace"] = str(ws)
    parsed["_staged"] = staged
    parsed["_output_path"] = str(out)
    parsed["_repo_tree"] = str(repo)
    dest = order_file(dirs["picked"], oid)
    _atomic_json(dest, parsed)
    try:
        Path(drop_path).unlink()
    except OSError:
        pass
    return parsed


CORE_PICKED_PATH = "/api/v1/work_orders/picked"
DEFAULT_CORE_URL = "http://127.0.0.1:8770"
NOTIFY_TIMEOUT_S = 5.0


def _read_api_token(paths) -> str | None:
    try:
        p = paths.config("api_token.txt")
    except Exception:  # noqa: BLE001
        return None
    if not Path(p).is_file():
        return None
    try:
        text = Path(p).read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text or None


def notify_core_picked(paths, order: dict, *, http=None, base_url=None,
                       token=None, timeout_s: float = NOTIFY_TIMEOUT_S) -> dict:
    """POST Core WORK_ORDER_PICKED. Never opens live/ledger/.

    http= is the test seam: (method, url, body, headers) -> (status, parsed).
    No base_url → CORE_NOT_COMPOSED (no network). Daemon CLI passes
    DEFAULT_CORE_URL. Idempotent on order_id (Core).
    """
    oid = str((order or {}).get("order_id") or "").strip()
    if not oid:
        return {"ok": False, "kind": "BAD_INPUT", "detail": "order_id required"}
    url_base = base_url
    if http is None and not url_base:
        return {
            "ok": False, "kind": "CORE_NOT_COMPOSED",
            "detail": "no core_url; skipped (daemon passes DEFAULT_CORE_URL)",
            "order_id": oid,
        }
    url_base = str(url_base or DEFAULT_CORE_URL).rstrip("/")
    url = url_base + CORE_PICKED_PATH
    body = {
        "order_id": oid,
        "agent": (order or {}).get("Agent") or (order or {}).get("agent"),
        "output_path": (order or {}).get("_output_path")
        or (order or {}).get("output_path"),
        "picked_at": (order or {}).get("picked_at"),
    }
    tok = token if token is not None else _read_api_token(paths)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if tok:
        headers["Authorization"] = "Bearer " + tok
    if http is not None:
        try:
            status, parsed = http("POST", url, body, headers)
        except Exception as e:  # noqa: BLE001
            return {
                "ok": False, "kind": "CORE_UNREACHABLE",
                "detail": f"{type(e).__name__}: {e}"[:200],
                "order_id": oid, "url": url,
            }
    else:
        try:
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(url, method="POST", data=data,
                                         headers=headers)
            with urllib.request.urlopen(req, timeout=float(timeout_s)) as r:
                raw = r.read().decode("utf-8") or "{}"
                try:
                    parsed = json.loads(raw)
                except ValueError:
                    parsed = {"raw": raw[:400]}
                status = int(r.status)
        except urllib.error.HTTPError as e:
            raw = (e.read() or b"").decode("utf-8", "replace")
            try:
                parsed = json.loads(raw) if raw else {"error": str(e)}
            except ValueError:
                parsed = {"error": raw[:400]}
            status = int(e.code)
        except Exception as e:  # noqa: BLE001
            return {
                "ok": False, "kind": "CORE_UNREACHABLE",
                "detail": f"{type(e).__name__}: {e}"[:200],
                "order_id": oid, "url": url,
            }
    if not isinstance(parsed, dict):
        parsed = {"detail": str(parsed)[:200]}
    if status in (200, 201) and parsed.get("ok"):
        return {
            "ok": True,
            "already": bool(parsed.get("already")),
            "order_id": oid,
            "seq": parsed.get("seq"),
            "hmac": parsed.get("hmac"),
            "prev_sha": parsed.get("prev_sha"),
            "http": status,
            "url": url,
        }
    kind = parsed.get("error") or (
        "CORE_UNREACHABLE" if status in (-1, 0) else "BROKE")
    return {
        "ok": False, "kind": str(kind),
        "http": status, "order_id": oid, "url": url,
        "detail": str(parsed.get("detail") or parsed.get("error") or "")[:200],
    }


def file_done(paths, order: dict, *, run_rec: dict | None = None,
              check_rails=None, live_probe=None) -> dict:
    """DONE iff the Output file exists and is non-empty. Never writes COMPLETED.

    rc is recorded, not the predicate. Missing output is FAILED and is not
    checked. When order['runtime_bind'] is true, DONE also requires a live
    emit from Core (:8770 /api/v1/status); missing emit is FAILED with
    fail_kind=MISSING_EMIT even if Output exists. Default runtime_bind off.
    On DONE deposit in assigned/, the same runner stamps
    checks.github / checks.cursor / checks.gitlab (one each). check_rails
    is a dict of callables, None (live rails), or False (skip — tests).
    live_probe= is an injectable callable(paths) for tests.
    """
    dirs = work_order_dirs(paths)
    oid = _safe_id(order.get("order_id") or new_order_id(order))
    rec = dict(order)
    rec["order_id"] = oid
    rec["filed_at"] = _iso_now()
    if run_rec:
        rec["run"] = {
            k: run_rec.get(k) for k in (
                "rc", "out", "err", "timed_out", "elapsed_s", "argv", "cwd",
                "via", "pid",
            ) if k in run_rec
        }
        rec["observed_rc"] = run_rec.get("rc")
    outp = rec.get("_output_path")
    exists = bool(outp) and output_exists(Path(outp))
    rec["output_exists"] = exists
    runtime_bind = rec.get("runtime_bind") is True
    emit_ok = True
    emit_err = None
    if exists and runtime_bind:
        from cosmos_live_emit import LiveEmitError, require_live_emit

        probe = live_probe
        if probe is None:
            probe = lambda _paths: require_live_emit(paths=_paths)  # noqa: E731
        try:
            emit = probe(paths)
            rec["live_emit"] = emit if isinstance(emit, dict) else {"ok": True}
        except LiveEmitError as e:
            emit_ok = False
            emit_err = e
        except Exception as e:  # noqa: BLE001
            emit_ok = False
            emit_err = LiveEmitError("MISSING_EMIT", f"{type(e).__name__}: {e}"[:200])
    if not exists:
        rec["state"] = "FAILED"
        rec["fail_kind"] = "FAILED"
        rec["fail_detail"] = "Output file missing or empty (rc is not the predicate)"
        dest = order_file(dirs["failed"], oid)
    elif runtime_bind and not emit_ok:
        rec["state"] = "FAILED"
        rec["fail_kind"] = emit_err.kind if emit_err else "MISSING_EMIT"
        rec["fail_detail"] = (
            emit_err.detail if emit_err else "live emit missing (runtime_bind)"
        )[:240]
        dest = order_file(dirs["failed"], oid)
    else:
        rec["state"] = "DONE"
        dest = order_file(dirs["assigned"], oid)
    _atomic_json(dest, rec)
    for name in ("picked", "bucket"):
        stale = order_file(dirs[name], oid)
        if stale.is_file() and stale.resolve() != dest.resolve():
            try:
                stale.unlink()
            except OSError:
                pass
    if rec.get("state") == "DONE" and check_rails is not False:
        from cosmos_work_order_checks import apply_done_checks
        rec = apply_done_checks(paths, rec, rails=check_rails, persist=True)
    return rec


def _output_head(path: Path) -> str:
    try:
        data = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise OrderError("BROKE", f"COW could not read output {path}: {e}") from e
    return data[:OUTPUT_HEAD]


def accept_order(root, order_id: str, *, note: str | None = None,
                 accepted_by: str = "COW", paths=None) -> dict:
    """The COW step. READS the output and files COMPLETED. Does not write the tree.

    Requires DONE in assigned. Exposes checks.* so COW can refuse a
    fake-green; does not auto-accept and does not require PASS.
    If the accepted output is a proposal, COW implements it through the
    fenced commit gateway — this function does not.
    """
    from cosmos_paths import CosmosPaths  # local: keep import surface small

    paths = paths or CosmosPaths(root)
    dirs = work_order_dirs(paths)
    oid = _safe_id(order_id)
    loc, src, rec = find_order(dirs, oid)
    if loc == "completed":
        rec["already_completed"] = True
        rec["output_head"] = _output_head(Path(rec["_output_path"])) if rec.get(
            "_output_path") else ""
        return rec
    if loc == "failed" or rec.get("state") == "FAILED":
        raise OrderError(
            "FAILED",
            f"order {oid} is FAILED (missing output) and cannot be accepted")
    if rec.get("state") != "DONE" or loc != "assigned":
        raise OrderError(
            "REFUSED",
            f"order {oid} is {rec.get('state')}/{loc}; "
            "accept_order requires DONE in assigned-tasks")
    outp = rec.get("_output_path")
    if not outp or not output_exists(Path(outp)):
        raise OrderError(
            "FAILED",
            f"order {oid} Output missing at accept; cannot COMPLETE")
    head = _output_head(Path(outp))
    from cosmos_work_order_checks import cow_checks_view
    rec["cow_checks"] = cow_checks_view(rec)
    rec["checks"] = rec.get("checks") if isinstance(rec.get("checks"), dict) else {}
    rec["state"] = "COMPLETED"
    rec["completed_at"] = _iso_now()
    rec["accepted_by"] = accepted_by
    rec["accept_note"] = note
    rec["output_head"] = head
    rec["output_bytes"] = Path(outp).stat().st_size
    dest = order_file(dirs["completed"], oid)
    _atomic_json(dest, rec)
    try:
        src.unlink()
    except OSError:
        pass
    return rec


def reject_order(root, order_id: str, *, note: str | None = None,
                 rejected_by: str = "COW", paths=None) -> dict:
    """Reject stays DONE in assigned-tasks. Never COMPLETED."""
    from cosmos_paths import CosmosPaths

    paths = paths or CosmosPaths(root)
    dirs = work_order_dirs(paths)
    oid = _safe_id(order_id)
    loc, src, rec = find_order(dirs, oid)
    if rec.get("state") == "FAILED" or loc == "failed":
        raise OrderError("FAILED", f"order {oid} is FAILED, not DONE")
    if rec.get("state") == "COMPLETED" or loc == "completed":
        raise OrderError("REFUSED", f"order {oid} is already COMPLETED")
    if rec.get("state") != "DONE" or loc != "assigned":
        raise OrderError(
            "REFUSED",
            f"order {oid} is {rec.get('state')}/{loc}; reject requires DONE")
    rec["rejected"] = True
    rec["rejected_at"] = _iso_now()
    rec["rejected_by"] = rejected_by
    rec["reject_note"] = note
    rec["state"] = "DONE"
    _atomic_json(src, rec)
    return rec


def drop_order(paths, raw: dict, *, order_id: str | None = None) -> Path:
    """Write a DROPPED record into the bucket. Does not run it."""
    parsed = parse_order(raw)
    oid = _safe_id(order_id or raw.get("order_id") or new_order_id(raw))
    parsed["order_id"] = oid
    parsed["state"] = "DROPPED"
    parsed["dropped_at"] = _iso_now()
    dirs = work_order_dirs(paths)
    dest = order_file(dirs["bucket"], oid)
    _atomic_json(dest, parsed)
    return dest
