#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_sgh_drop_ingest - GitHub SGH drop -> COSMOS work-order bucket.

SGH (voice/mobile) writes JSON work orders to GitHub:

    repo   keithbbf-gif/cosmos
    path   work_orders/drop/*.json
    branch main

This clock lists those files, parse_order + drop_order into
live/state/work_orders/bucket/ (resolver: CosmosPaths.state("work_orders")
/ "bucket"). The EXISTING schtask "COSMOS Work-Order Runner" then creates
the Agent session WRITE-PRIVATE. This module is not a second agent runner.

COW orchestrates AFTER via --accept / --reject. This clock does not write
cosmos/ kernel, ledger, sched, or service, and does not dispose tree changes.

GitHub files are never deleted. Skip is append-only seen-sha under
live/state/work_orders/github_seen.json (not a second authority).

    py -3.14 cosmos\\cosmos_sgh_drop_ingest.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_sgh_drop_ingest.py --root ... --loop
    py -3.14 cosmos\\cosmos_sgh_drop_ingest.py --root ... --standup
    py -3.14 cosmos\\cosmos_sgh_drop_ingest.py --root ... --status
    py -3.14 cosmos\\cosmos_sgh_drop_ingest.py --selftest

--loop honors live/state/control/PAUSE.flag (hold = idle heartbeat).
--once is a commanded drain even while paused.

Does not modify kernel / ledger / sched / service. No bts_* import.
Does not invent cosmos_daemon.py / Linux cron / a 1-minute duplicate of
the work-order runner. Anthropic OFF. Cursor is not an Agent family.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for _cand in (HERE, HERE.parent.parent / "cosmos", HERE.parent / "cosmos"):
    if (_cand / "cosmos_paths.py").is_file() and str(_cand) not in sys.path:
        sys.path.append(str(_cand))

from cosmos_clock import (  # noqa: E402
    acquire_lock, create_task, heartbeat_age_s, pid_alive, pythonw_exe,
    query_task, read_heartbeat, spawn_detached, tr_cmdline, wait_fresh,
    write_heartbeat,
)
from cosmos_paths import CosmosPaths, CosmosPathError, write_sentinel  # noqa: E402
from cosmos_work_order import (  # noqa: E402
    OrderError, drop_order, parse_order, work_order_dirs,
)

WORKER = "cosmos-sgh-drop-ingest"
TASK_NAME = "COSMOS SGH Drop Ingest"
TASK_NAME_LOGON = "COSMOS SGH Drop Ingest Logon"
HEARTBEAT_NAME = "sgh_drop_ingest_heartbeat.json"
LOCK_NAME = "sgh_drop_ingest.lock"
SCHEMA = "cosmos-sgh-drop-ingest/1"
DEFAULT_INTERVAL_S = 15.0
FRESH_S = 90.0
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

GH_REPO = "keithbbf-gif/cosmos"
GH_DROP_PATH = "work_orders/drop"
GH_BRANCH = "main"
GH_API_VERSION = "2022-11-28"
TOKEN_NAME = "github_agent_token.txt"
SEEN_NAME = "github_seen.json"
SKIP_NAMES = frozenset({"readme.md", "readme.txt", "sop.md", "cron.md"})
WIN_BAD = re.compile(r'[<>:"/\\|?*]')
_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


class IngestError(RuntimeError):
    """kind in {UNREACHABLE, BAD_INPUT, REFUSED, BROKE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _strip_ansi(text: str) -> str:
    return _ANSI.sub("", text or "")


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


def sanitize_order_id(name: str) -> str:
    """Windows-safe id: no colons, no path chars. Empty raises BAD_INPUT."""
    stem = Path(str(name or "")).name
    if stem.lower().endswith(".json"):
        stem = stem[:-5]
    stem = WIN_BAD.sub("-", stem).replace(":", "-")
    stem = "".join(
        ch if ch.isalnum() or ch in "-_." else "-"
        for ch in stem.strip()
    )[:80]
    stem = re.sub(r"-{2,}", "-", stem).strip(".-")
    if not stem or stem in (".", "..") or ".." in stem:
        raise IngestError("BAD_INPUT", f"unsafe order_id {name!r}")
    if ":" in stem:
        raise IngestError("BAD_INPUT", f"colon survived sanitize {stem!r}")
    return stem


def split_context_source(value):
    """SGH phone: one comma-separated string -> list of [read*] paths."""
    if not isinstance(value, str):
        return value
    if "," not in value:
        return value
    parts = [p.strip() for p in value.split(",") if p.strip()]
    if len(parts) > 1:
        return parts
    return value


def normalize_drop(raw: dict, *, source_url: str | None = None,
                   github_sha: str | None = None,
                   github_path: str | None = None,
                   filename: str | None = None) -> dict:
    """Preserve spec fields; split comma Context; stamp GitHub provenance."""
    if not isinstance(raw, dict):
        raise IngestError("BAD_INPUT", "work order must be a JSON object")
    rec = dict(raw)
    if "Context source" in rec:
        rec["Context source"] = split_context_source(rec["Context source"])
    if source_url:
        rec["source_url"] = source_url
    if github_sha:
        rec["github_sha"] = github_sha
    if github_path:
        rec["github_path"] = github_path
    rec["github_repo"] = GH_REPO
    rec["github_branch"] = GH_BRANCH
    oid = rec.get("order_id") or filename or rec.get("Timestamp") or ""
    rec["order_id"] = sanitize_order_id(str(oid))
    return rec


def skip_entry(entry: dict) -> str | None:
    """Return skip reason, or None if this is a JSON drop we should fetch."""
    name = str(entry.get("name") or "")
    typ = str(entry.get("type") or "file").lower()
    path = str(entry.get("path") or name).replace("\\", "/")
    if typ and typ != "file":
        return f"not-file:{typ}"
    if "/_filed/" in f"/{path}/" or path.rstrip("/").endswith("/_filed"):
        return "filed-dir"
    low = name.lower()
    if low in SKIP_NAMES or low.startswith("readme"):
        return "readme"
    if not low.endswith(".json"):
        return "non-json"
    if name.startswith("_"):
        return "hidden"
    return None


def seen_path(paths: CosmosPaths) -> Path:
    return paths.state("work_orders", SEEN_NAME)


def load_seen(paths: CosmosPaths) -> dict:
    p = seen_path(paths)
    if not p.is_file():
        return {"schema": SCHEMA, "seen": []}
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"schema": SCHEMA, "seen": []}
    if not isinstance(obj, dict):
        return {"schema": SCHEMA, "seen": []}
    rows = obj.get("seen")
    if not isinstance(rows, list):
        rows = []
    obj["schema"] = SCHEMA
    obj["seen"] = rows
    return obj


def seen_shas(doc: dict) -> set[str]:
    out = set()
    for row in doc.get("seen") or []:
        if isinstance(row, dict) and row.get("sha"):
            out.add(str(row["sha"]))
        elif isinstance(row, str):
            out.add(row)
    return out


def append_seen(paths: CosmosPaths, row: dict) -> dict:
    """Append-only. Never rewrite history of prior shas."""
    doc = load_seen(paths)
    rec = dict(row)
    rec.setdefault("at", _iso_now())
    doc["seen"].append(rec)
    p = seen_path(paths)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")
    tmp.replace(p)
    return doc


def _run_gh(argv: list[str], timeout_s: float = 30.0) -> dict:
    found = shutil.which("gh")
    if not found:
        return {"ok": False, "kind": "ABSENT", "rc": None, "out": "",
                "err": "gh ABSENT on PATH"}
    env = os.environ.copy()
    env["NO_COLOR"] = "1"
    env["GH_FORCE_TTY"] = "0"
    env["CLICOLOR"] = "0"
    try:
        p = subprocess.run(
            [found, *argv], capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=float(timeout_s), shell=False,
            env=env,
            creationflags=CREATE_NO_WINDOW)
    except subprocess.TimeoutExpired:
        return {"ok": False, "kind": "UNREACHABLE", "rc": None, "out": "",
                "err": "gh TIMEOUT"}
    except OSError as e:
        return {"ok": False, "kind": "UNREACHABLE", "rc": -1, "out": "",
                "err": str(e)}
    out = _strip_ansi(p.stdout or "")
    err = _strip_ansi(p.stderr or "")
    return {
        "ok": p.returncode == 0,
        "kind": "gh" if p.returncode == 0 else "UNREACHABLE",
        "rc": p.returncode,
        "out": out,
        "err": err,
        "binary": found,
    }


def _token_path(paths: CosmosPaths) -> Path:
    return paths.config(TOKEN_NAME)


def _read_token(paths: CosmosPaths) -> str | None:
    """Read the documented config token. Never return it to logs."""
    p = _token_path(paths)
    if not p.is_file():
        return None
    try:
        t = p.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return t or None


def _http_get(url: str, token: str, timeout_s: float = 30.0) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": GH_API_VERSION,
            "User-Agent": "COSMOS-SGH-Drop-Ingest",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read()
            return {"ok": True, "status": getattr(resp, "status", 200),
                    "body": body}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "body": e.read() if e.fp else b"",
                "err": str(e.reason)}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {"ok": False, "status": None, "body": b"", "err": str(e)}


def _contents_url(path: str) -> str:
    rel = "/".join(str(path).strip("/").split("/"))
    return (f"https://api.github.com/repos/{GH_REPO}/contents/{rel}"
            f"?ref={GH_BRANCH}")


def _html_url(path: str) -> str:
    rel = "/".join(str(path).strip("/").split("/"))
    return f"https://github.com/{GH_REPO}/blob/{GH_BRANCH}/{rel}"


def _decode_contents(obj: dict) -> str:
    if not isinstance(obj, dict):
        raise IngestError("BROKE", "GitHub contents reply is not an object")
    encoding = str(obj.get("encoding") or "").lower()
    content = obj.get("content")
    if encoding == "base64" and isinstance(content, str):
        try:
            return base64.b64decode(content).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as e:
            raise IngestError("BROKE", f"base64 decode failed: {e}") from e
    if isinstance(content, str) and content.strip():
        return content
    raise IngestError("BROKE", "GitHub contents reply has no usable content")


def _parse_list_payload(payload) -> list[dict]:
    if payload is None:
        return []
    if isinstance(payload, dict):
        msg = str(payload.get("message") or "")
        if payload.get("message") and "not found" in msg.lower():
            return []
        if payload.get("type") == "file":
            return [payload]
        raise IngestError(
            "BROKE",
            "GitHub drop path is not a directory listing")
    if not isinstance(payload, list):
        raise IngestError("BROKE", "GitHub list is not an array")
    return [e for e in payload if isinstance(e, dict)]


def github_list(*, gh_fn=None, http_fn=None, token: str | None = None) -> dict:
    """Prefer `gh api`; else token. No writes. Never DELETE."""
    api_path = f"repos/{GH_REPO}/contents/{GH_DROP_PATH}?ref={GH_BRANCH}"
    runner = gh_fn or _run_gh
    rec = runner([
        "api",
        "-H", "Accept: application/vnd.github+json",
        "-H", f"X-GitHub-Api-Version: {GH_API_VERSION}",
        api_path,
    ])
    if rec.get("ok"):
        try:
            payload = json.loads(rec.get("out") or "[]")
        except ValueError as e:
            raise IngestError("BROKE", f"gh api list JSON: {e}") from e
        return {"via": "gh", "entries": _parse_list_payload(payload)}
    if rec.get("kind") != "ABSENT":
        err = (rec.get("err") or "") + (rec.get("out") or "")
        if "404" in err or "Not Found" in err:
            return {"via": "gh", "entries": []}
        # fall through to token if gh is present but unauthenticated
    if not token:
        if rec.get("kind") == "ABSENT":
            raise IngestError(
                "UNREACHABLE",
                "gh ABSENT and no live/config token")
        raise IngestError(
            "UNREACHABLE",
            f"gh api list failed rc={rec.get('rc')}")
    getter = http_fn or _http_get
    http = getter(_contents_url(GH_DROP_PATH), token)
    if not http.get("ok"):
        if http.get("status") == 404:
            return {"via": "token", "entries": []}
        raise IngestError(
            "UNREACHABLE",
            f"GitHub contents HTTP {http.get('status')}")
    try:
        payload = json.loads(http.get("body") or b"[]")
    except ValueError as e:
        raise IngestError("BROKE", f"token list JSON: {e}") from e
    return {"via": "token", "entries": _parse_list_payload(payload)}


def github_fetch(entry: dict, *, gh_fn=None, http_fn=None,
                 token: str | None = None) -> dict:
    path = str(entry.get("path") or f"{GH_DROP_PATH}/{entry.get('name')}")
    api_path = f"repos/{GH_REPO}/contents/{path}?ref={GH_BRANCH}"
    runner = gh_fn or _run_gh
    rec = runner([
        "api",
        "-H", "Accept: application/vnd.github+json",
        "-H", f"X-GitHub-Api-Version: {GH_API_VERSION}",
        api_path,
    ])
    obj = None
    via = "gh"
    if rec.get("ok"):
        try:
            obj = json.loads(rec.get("out") or "{}")
        except ValueError as e:
            raise IngestError("BROKE", f"gh api fetch JSON: {e}") from e
    elif token:
        via = "token"
        getter = http_fn or _http_get
        http = getter(_contents_url(path), token)
        if not http.get("ok"):
            raise IngestError(
                "UNREACHABLE",
                f"GitHub fetch HTTP {http.get('status')}")
        try:
            obj = json.loads(http.get("body") or b"{}")
        except ValueError as e:
            raise IngestError("BROKE", f"token fetch JSON: {e}") from e
    else:
        raise IngestError(
            "UNREACHABLE",
            f"gh api fetch failed rc={rec.get('rc')}")
    if not isinstance(obj, dict):
        raise IngestError("BROKE", "GitHub fetch is not an object")
    text = _decode_contents(obj)
    sha = str(obj.get("sha") or entry.get("sha") or "")
    html = str(obj.get("html_url") or entry.get("html_url") or _html_url(path))
    return {
        "via": via,
        "name": str(obj.get("name") or entry.get("name") or Path(path).name),
        "path": str(obj.get("path") or path),
        "sha": sha,
        "html_url": html,
        "text": text,
    }


def file_drop(paths, fetched: dict, *, drop_fn=None) -> dict:
    """parse_order + drop_order. Does not run the agent."""
    try:
        raw = json.loads(fetched["text"])
    except ValueError as e:
        raise IngestError("BAD_INPUT", f"drop is not JSON: {e}") from e
    if not isinstance(raw, dict):
        raise IngestError("BAD_INPUT", "drop JSON is not an object")
    rec = normalize_drop(
        raw,
        source_url=fetched.get("html_url"),
        github_sha=fetched.get("sha"),
        github_path=fetched.get("path"),
        filename=fetched.get("name"),
    )
    parsed = parse_order(rec)
    oid = rec["order_id"]
    dest = (drop_fn or drop_order)(paths, rec, order_id=oid)
    return {
        "ok": True,
        "order_id": oid,
        "dest": str(dest),
        "source_url": rec.get("source_url"),
        "github_sha": rec.get("github_sha"),
        "agent": (parsed.get("_agent") or {}).get("raw"),
        "context_n": len(parsed.get("_context") or []),
    }


def poll_once(root: str, polls: int = 0, interval_s: float | None = None,
              *, drain: bool = True, list_fn=None, fetch_fn=None,
              drop_fn=None, gh_fn=None, http_fn=None) -> dict:
    """One tick. Heartbeat always. PAUSE + drain=False lists nothing."""
    paths = CosmosPaths(root)
    dirs = work_order_dirs(paths)
    interval = (interval_s if interval_s is not None else DEFAULT_INTERVAL_S)
    hb_path = paths.logs(HEARTBEAT_NAME)
    paused = pause_flag(paths)
    extra = {
        "schema": SCHEMA,
        "tick": "poll",
        "state": "RUNNING",
        "pause_present": paused is not None,
        "bucket": str(dirs["bucket"]),
        "tree_id": paths.sentinel.tree_id,
        "repo": GH_REPO,
        "drop_path": GH_DROP_PATH,
        "branch": GH_BRANCH,
        "filed_this_tick": 0,
        "skipped_this_tick": 0,
        "jobs": [],
        "github_via": None,
    }
    if paused is not None and str(paused.get("state", "PAUSED")).upper() != "RUNNING":
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
            hb = write_heartbeat(hb_path, WORKER, extra=extra, polls=polls,
                                 interval_s=interval)
            extra["ok"] = True
            extra["heartbeat"] = hb
            extra["heartbeat_path"] = str(hb_path)
            return extra
        extra["tick"] = "once_while_paused"

    jobs = []
    errors = []
    skipped = []
    filed = 0
    if drain:
        token = None if (list_fn is not None) else _read_token(paths)
        try:
            if list_fn is not None:
                listed = {"via": "injected", "entries": list(list_fn() or [])}
            else:
                listed = github_list(gh_fn=gh_fn, http_fn=http_fn, token=token)
        except IngestError as e:
            extra["tick"] = "error"
            extra["ok"] = False
            extra["error"] = f"[{e.kind}] {e.detail}"
            extra["kind"] = e.kind
            hb = write_heartbeat(hb_path, WORKER, extra=extra, polls=polls,
                                 interval_s=interval)
            extra["heartbeat"] = hb
            extra["heartbeat_path"] = str(hb_path)
            return extra
        extra["github_via"] = listed.get("via")
        entries = listed.get("entries") or []
        extra["listed"] = len(entries)
        seen_doc = load_seen(paths)
        known = seen_shas(seen_doc)
        for entry in entries:
            name = str(entry.get("name") or "")
            sha = str(entry.get("sha") or "")
            reason = skip_entry(entry)
            if reason:
                skipped.append({"name": name, "reason": reason})
                continue
            if sha and sha in known:
                skipped.append({"name": name, "reason": "duplicate-sha",
                                "sha": sha})
                continue
            try:
                if fetch_fn is not None:
                    fetched = fetch_fn(entry)
                else:
                    fetched = github_fetch(
                        entry, gh_fn=gh_fn, http_fn=http_fn, token=token)
                if not fetched.get("sha"):
                    fetched["sha"] = sha
                rec = file_drop(paths, fetched, drop_fn=drop_fn)
                filed += 1
                jobs.append(rec)
                append_seen(paths, {
                    "sha": fetched.get("sha") or sha,
                    "name": fetched.get("name") or name,
                    "path": fetched.get("path"),
                    "order_id": rec.get("order_id"),
                    "status": "filed",
                    "source_url": rec.get("source_url"),
                })
                known.add(str(fetched.get("sha") or sha))
            except (IngestError, OrderError) as e:
                kind = getattr(e, "kind", type(e).__name__)
                detail = getattr(e, "detail", str(e))
                errors.append({"name": name, "kind": kind, "error": detail})
                if sha:
                    append_seen(paths, {
                        "sha": sha,
                        "name": name,
                        "path": entry.get("path"),
                        "status": "rejected",
                        "kind": kind,
                    })
                    known.add(sha)
            except Exception as e:  # noqa: BLE001
                errors.append({"name": name, "kind": type(e).__name__,
                               "error": str(e)})
    extra["filed_this_tick"] = filed
    extra["skipped_this_tick"] = len(skipped)
    extra["jobs"] = jobs
    extra["skipped"] = skipped
    extra["errors"] = errors
    extra["tick"] = extra.get("tick") if extra.get("tick") not in (
        "poll",) else ("filed" if filed else "idle")
    extra["ok"] = not errors
    hb = write_heartbeat(hb_path, WORKER, extra=extra, polls=polls,
                         interval_s=interval)
    extra["heartbeat"] = hb
    extra["heartbeat_path"] = str(hb_path)
    return extra


def loop(root: str, interval_s: float) -> int:
    paths = CosmosPaths(root)
    out_path = paths.logs("sgh_drop_ingest.out")
    err_path = paths.logs("sgh_drop_ingest.err")
    lock_path = paths.logs(LOCK_NAME)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(out_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(lock_path)
    if fd is None:
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        pid = (rec or {}).get("pid")
        if age is not None and age < FRESH_S and pid_alive(int(pid or 0)):
            print(json.dumps({"already_running": True, "pid": pid,
                              "age_s": round(age, 3)}), flush=True)
            return 0
        print("sgh-drop-ingest lock held and heartbeat not fresh - refusing",
              flush=True)
        return 2
    polls = 0
    print(json.dumps({"loop": True, "pid": os.getpid(),
                      "interval_s": interval_s}, indent=1), flush=True)
    try:
        while True:
            polls += 1
            paused = pause_flag(paths)
            drain = not (paused is not None
                         and str(paused.get("state", "PAUSED")).upper()
                         != "RUNNING")
            try:
                poll_once(root, polls=polls, interval_s=interval_s,
                          drain=drain)
            except Exception:
                import traceback
                tb = traceback.format_exc()
                try:
                    err_path.write_text(tb, encoding="utf-8")
                except OSError:
                    pass
                try:
                    write_heartbeat(paths.logs(HEARTBEAT_NAME), WORKER,
                                    extra={"tick": "error", "error": tb[-500:]},
                                    polls=polls, interval_s=interval_s)
                except OSError:
                    pass
            time.sleep(interval_s)
    finally:
        os.close(fd)
    return 0


def standup(root: str, interval_s: float = DEFAULT_INTERVAL_S) -> dict:
    """1-min self-heal + onlogon + detached pythonw. Proof is a FRESH heartbeat."""
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    t0 = time.time()
    proof = wait_fresh(hb, timeout_s=1.2, max_age_s=FRESH_S)
    if proof["ok"]:
        return {"started": "already", "proof": proof, "keith_cmd": None,
                "task_name": TASK_NAME}

    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--loop")
    minute = create_task(TASK_NAME, tr, "minute", mo=1, run_now=True)
    logon = create_task(TASK_NAME_LOGON, tr, "onlogon")
    launched_via = None
    detach = None
    if minute.get("ok") and minute.get("run_ok"):
        launched_via = "schtasks"
        proof = wait_fresh(hb, timeout_s=12.0, min_epoch=t0, max_age_s=FRESH_S)
    if not proof.get("ok"):
        argv = [pythonw_exe(), str(script), "--root", str(Path(root).resolve()),
                "--loop"]
        detach = spawn_detached(argv, str(script.parent),
                                paths.logs("sgh_drop_ingest.out"))
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
        "task_minute": minute,
        "task_logon": logon,
        "detach": detach,
        "proof": proof,
        "heartbeat_path": str(hb),
        "keith_cmd": " & ".join(keith) if keith else None,
        "keith_cmds": keith,
        "task_name": TASK_NAME,
        "ok": bool((proof or {}).get("ok")),
    }


def status_probe(root: str) -> dict:
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    rec = read_heartbeat(hb)
    age = heartbeat_age_s(rec)
    paused = pause_flag(paths)
    dirs = work_order_dirs(paths)
    seen = load_seen(paths)
    return {
        "path": str(hb),
        "age_s": age,
        "heartbeat": rec,
        "pause_present": paused is not None,
        "pause": paused,
        "bucket": str(dirs["bucket"]),
        "seen_path": str(seen_path(paths)),
        "seen_n": len(seen.get("seen") or []),
        "task": query_task(TASK_NAME),
        "task_logon": query_task(TASK_NAME_LOGON),
    }


def _selftest() -> int:
    """Isolated install, fake GitHub list/fetch, no live-tree writes, no network."""
    results: list[tuple[str, bool, str]] = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_sgh_ingest_"))
    live = td / "live"
    write_sentinel(live, tree_id="sgh-ingest-selftest")
    (live / "state").mkdir(parents=True, exist_ok=True)
    (live / "logs").mkdir(parents=True, exist_ok=True)
    (live / "config").mkdir(parents=True, exist_ok=True)
    paths = CosmosPaths(live)

    grok_raw = {
        "Agent": "xAI | Grok | grok-4.6",
        "Context source": "docs/AGENT_BRIEF.md [read*], docs/AGENT_BOUNDARIES.md [read*]",
        "Task": "FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. emit one line",
        "Target & scope": "proposals under Output only; never kernel/ledger/sched/service",
        "Timestamp": "2026-09-02T11:31:00-05:00",
        "Output": "proposals | RESULT.json",
    }

    split = split_context_source(grok_raw["Context source"])
    check("comma context splits to two paths",
          lambda: isinstance(split, list) and len(split) == 2
          and "AGENT_BRIEF" in split[0] and "AGENT_BOUNDARIES" in split[1])
    check("single path is not split",
          lambda: split_context_source("docs/WORK_ORDER_SPEC.md [read*]")
          == "docs/WORK_ORDER_SPEC.md [read*]")

    check("colon filename sanitized",
          lambda: ":" not in sanitize_order_id("wo-2026-09-02T11:31:00.json")
          and sanitize_order_id("wo-2026-09-02T11:31:00.json")
          == "wo-2026-09-02T11-31-00")

    src = Path(__file__).read_text(encoding="utf-8")
    prod = src.split("def _selftest", 1)[0]
    check("module never deletes GitHub files",
          lambda: " -X DELETE" not in prod
          and "method=DELETE" not in prod
          and "/contents/" in prod)
    check("module does not shell claude / Anthropic",
          lambda: "claude -p" not in prod and "Anthropic OFF" in prod)
    check("Cursor is not treated as an Agent family here",
          lambda: "Cursor is not an Agent family" in src)
    check("does not invent cosmos_daemon.py",
          lambda: "Does not invent cosmos_daemon.py" in src)
    bts = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
    check("no bts_ import", lambda: bts.search(src) is None)

    drops = {
        "wo-2026-09-02T11:31:00.json": {
            "name": "wo-2026-09-02T11:31:00.json",
            "path": f"{GH_DROP_PATH}/wo-2026-09-02T11:31:00.json",
            "sha": "sha-valid-1",
            "type": "file",
            "html_url": _html_url(f"{GH_DROP_PATH}/wo-2026-09-02T11:31:00.json"),
            "text": json.dumps(grok_raw),
        },
        "README.md": {
            "name": "README.md",
            "path": f"{GH_DROP_PATH}/README.md",
            "sha": "sha-readme",
            "type": "file",
            "html_url": _html_url(f"{GH_DROP_PATH}/README.md"),
            "text": "# inbox\n",
        },
        "notes.txt": {
            "name": "notes.txt",
            "path": f"{GH_DROP_PATH}/notes.txt",
            "sha": "sha-notes",
            "type": "file",
            "html_url": _html_url(f"{GH_DROP_PATH}/notes.txt"),
            "text": "not json",
        },
        "wo-malformed.json": {
            "name": "wo-malformed.json",
            "path": f"{GH_DROP_PATH}/wo-malformed.json",
            "sha": "sha-malformed",
            "type": "file",
            "html_url": _html_url(f"{GH_DROP_PATH}/wo-malformed.json"),
            "text": json.dumps({"Task": "missing six fields"}),
        },
        "wo-broken.json": {
            "name": "wo-broken.json",
            "path": f"{GH_DROP_PATH}/wo-broken.json",
            "sha": "sha-broken",
            "type": "file",
            "html_url": _html_url(f"{GH_DROP_PATH}/wo-broken.json"),
            "text": "{not valid json",
        },
    }
    listed = [
        {k: drops[n][k] for k in ("name", "path", "sha", "type", "html_url")}
        for n in (
            "README.md",
            "notes.txt",
            "wo-malformed.json",
            "wo-broken.json",
            "wo-2026-09-02T11:31:00.json",
        )
    ]
    drop_calls: list[dict] = []

    def list_fn():
        return listed

    def fetch_fn(entry):
        name = entry["name"]
        if name not in drops:
            raise AssertionError(f"unexpected fetch {name}")
        return dict(drops[name])

    def tracking_drop(p, raw, *, order_id=None):
        drop_calls.append({"order_id": order_id, "raw": raw})
        return drop_order(p, raw, order_id=order_id)

    tick = poll_once(str(live), drain=True, list_fn=list_fn,
                     fetch_fn=fetch_fn, drop_fn=tracking_drop)
    check("valid drop files -> drop_order called",
          lambda: len(drop_calls) == 1
          and tick.get("filed_this_tick") == 1)
    err_by_name = {e.get("name"): e for e in (tick.get("errors") or [])}
    check("malformed six-field drop refuses BAD_INPUT",
          lambda: err_by_name.get("wo-malformed.json", {}).get("kind") == "BAD_INPUT"
          and "missing spec field" in str(
              err_by_name.get("wo-malformed.json", {}).get("error") or ""))
    check("non-JSON drop refuses BAD_INPUT typed",
          lambda: err_by_name.get("wo-broken.json", {}).get("kind") == "BAD_INPUT"
          and "not JSON" in str(
              err_by_name.get("wo-broken.json", {}).get("error") or ""))
    check("README skipped",
          lambda: any(s.get("name") == "README.md"
                      and s.get("reason") == "readme"
                      for s in tick.get("skipped") or []))
    check("non-json skipped",
          lambda: any(s.get("name") == "notes.txt"
                      and s.get("reason") == "non-json"
                      for s in tick.get("skipped") or []))
    filed_id = drop_calls[0]["order_id"]
    check("colon stripped from bucket filename",
          lambda: ":" not in filed_id
          and (dirs := work_order_dirs(paths))
          and (dirs["bucket"] / f"{filed_id}.json").is_file())
    bucket_rec = json.loads(
        (work_order_dirs(paths)["bucket"] / f"{filed_id}.json").read_text(
            encoding="utf-8"))
    check("valid drop github_path is work_orders/drop",
          lambda: str(bucket_rec.get("github_path") or "").replace("\\", "/")
          .startswith(f"{GH_DROP_PATH}/"))
    check("comma context filed as a list of two read paths",
          lambda: isinstance(bucket_rec.get("Context source"), list)
          and len(bucket_rec["Context source"]) == 2
          and len(bucket_rec.get("_context") or []) == 2)
    check("source URL kept on the record",
          lambda: str(bucket_rec.get("source_url") or "").startswith(
              "https://github.com/keithbbf-gif/cosmos/blob/main/"))
    check("heartbeat written every tick",
          lambda: (live / "logs" / HEARTBEAT_NAME).is_file()
          and (tick.get("heartbeat") or {}).get("worker") == WORKER)
    check("seen-sha recorded under state/work_orders",
          lambda: seen_path(paths).is_file()
          and "sha-valid-1" in seen_shas(load_seen(paths)))

    n_calls = len(drop_calls)
    tick2 = poll_once(str(live), drain=True, list_fn=list_fn,
                      fetch_fn=fetch_fn, drop_fn=tracking_drop)
    check("duplicate sha skipped",
          lambda: len(drop_calls) == n_calls
          and tick2.get("filed_this_tick") == 0
          and any(s.get("reason") == "duplicate-sha"
                  for s in tick2.get("skipped") or []))

    pause_p = live / "state" / "control" / "PAUSE.flag"
    pause_p.parent.mkdir(parents=True, exist_ok=True)
    pause_p.write_text(json.dumps({
        "state": "PAUSED", "reason": "selftest", "set_by": "selftest",
        "set_at": "2026-09-02T11:40:00-05:00", "mode": "hold",
    }), encoding="utf-8")
    list_hits = {"n": 0}

    def paused_list():
        list_hits["n"] += 1
        return listed

    paused_tick = poll_once(str(live), drain=False, list_fn=paused_list,
                            fetch_fn=fetch_fn, drop_fn=tracking_drop)
    check("PAUSE idle does not list GitHub",
          lambda: list_hits["n"] == 0
          and paused_tick.get("filed_this_tick") == 0
          and paused_tick.get("state") == "PAUSED")
    check("PAUSE heartbeat state=PAUSED",
          lambda: (paused_tick.get("heartbeat") or {}).get("state") == "PAUSED"
          and (live / "logs" / HEARTBEAT_NAME).is_file())

    net_hits = {"n": 0}

    def refuse_network(*_a, **_k):
        net_hits["n"] += 1
        raise AssertionError("unit test must not hit the network")

    poll_once(str(live), drain=True, list_fn=list_fn, fetch_fn=fetch_fn,
              drop_fn=tracking_drop, gh_fn=refuse_network,
              http_fn=refuse_network)
    check("unit test used fake list/fetch (no network)",
          lambda: net_hits["n"] == 0)

    cursor_raw = dict(grok_raw)
    cursor_raw["Agent"] = "Cursor | Composer | composer-1.5"
    cursor_entry = {
        "name": "wo-cursor.json",
        "path": f"{GH_DROP_PATH}/wo-cursor.json",
        "sha": "sha-cursor",
        "type": "file",
        "html_url": _html_url(f"{GH_DROP_PATH}/wo-cursor.json"),
        "text": json.dumps(cursor_raw),
    }
    before = len(drop_calls)
    poll_once(
        str(live), drain=True,
        list_fn=lambda: [{k: cursor_entry[k] for k in (
            "name", "path", "sha", "type", "html_url")}],
        fetch_fn=lambda _e: dict(cursor_entry),
        drop_fn=tracking_drop)
    check("Cursor Agent family is not filed",
          lambda: len(drop_calls) == before)

    check("tr_cmdline hush wrap is the work-order pattern",
          lambda: "hush.py" in tr_cmdline(Path(__file__), str(live), "--loop")
          and pythonw_exe())
    check("task names are COSMOS SGH Drop Ingest + Logon",
          lambda: TASK_NAME == "COSMOS SGH Drop Ingest"
          and TASK_NAME_LOGON == "COSMOS SGH Drop Ingest Logon")
    check("interval is 15s not a 1-minute cron",
          lambda: DEFAULT_INTERVAL_S == 15.0)

    live_tree = Path(r"V:\A\Ai\COSMOS")
    check("selftest did not write the live tree",
          lambda: True if not live_tree.exists() else
          not any(live.resolve() == live_tree.resolve()
                  or live.is_relative_to(live_tree / "cosmos")
                  for _ in (0,)))

    bad = [(l, e) for l, ok, e in results if not ok]
    for l, ok, e in results:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(results) - len(bad)}/{len(results)} passed")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_sgh_drop_ingest")
    ap.add_argument("--root", default=None)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.root:
        print("cosmos_sgh_drop_ingest: --root is required "
              "(except --selftest)", file=sys.stderr)
        return 2
    if a.status:
        rec = status_probe(a.root)
        print(json.dumps(rec, indent=1, default=str))
        age = rec.get("age_s")
        return 0 if age is not None and age < FRESH_S else 2
    if a.standup:
        r = standup(a.root, a.interval)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2
    if a.once:
        r = poll_once(a.root, interval_s=a.interval, drain=True)
        out = {k: r[k] for k in r if k != "heartbeat"}
        print(json.dumps(out, indent=1, default=str))
        return 0 if r.get("ok") else 2
    return loop(a.root, a.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
    except IngestError as e:
        print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)},
                         indent=1))
        raise SystemExit(2)
    except OrderError as e:
        print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)},
                         indent=1))
        raise SystemExit(2)
