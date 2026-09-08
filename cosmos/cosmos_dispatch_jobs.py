#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_dispatch_jobs - job-source builders (R4: grok flags locked).

Split out of `cosmos_dispatch.py` (PHASE 4, `docs/CORE_RESTRUCTURE.md`) along a
seam that already existed:

    # ---------------------------------------------------------------------------
    # job source (R4: grok flags locked; cursor/claude provisional)
    # ---------------------------------------------------------------------------

This is the dispatch harness's *pure* job-source layer. Kind + task + paths
in, a Python job script string out -- no runtime root identity, no DHx stamp,
no collector index, no queue drop. `cosmos_dispatch` re-exports every name
below, so every existing importer of these names off cosmos_dispatch keeps
working unchanged.

What lives here, and why it is one piece:
  * `_py_path` / `_job_helpers_block` -- the emitted job's bind/emit prelude
  * `_grok_job` / `_cursor_job` / `_codex_job` / `_claude_job` / `_worker_job`
    -- one builder per kind
  * `render_job` -- the kind switch that callers (dispatch()) already used

What deliberately did NOT move: `dispatch()` / `job_status` / `run_gate`.
Those own the queue drop, the collector index, and the stage-6 live-tree
gate. Pulling them out would mean passing the harness into a free function
-- coupling wearing a module's clothes, not a seam. The seam is exactly
here, at the boundary where a job script is a string.

Closed-over constants (`WORKER`, `DEFAULT_MODEL`, `GROK_MAX_TURNS`,
`CURSOR_*`, `CLAUDE_MODEL`, `CLAUDE_KINDS`, `WORKER_KINDS`) are duplicated
here with the same values dispatch already published. Dispatch re-exports
the FUNCTIONS as the same objects (not copies). Importing the constants
the other way would cycle (dispatch imports this module).

Does not modify kernel / ledger / sched / service. No hard-coded drive
literals. Cursor/codex keys are READ at job runtime from a path; never
baked. kind_live for cursor/codex stays UNPROVEN (F-69 H6; no Cloud Agents
launch, no key chase). claude-family CLI is proven (harness PONG).
"""
from __future__ import annotations

import json
from pathlib import Path

from cosmos_cursor_rail import CURSOR_MODEL, pin_cursor_model  # noqa: E402
from cosmos_dispatch_workspace import DispatchError  # noqa: E402

# Values MUST match cosmos_dispatch.py. Dispatch re-exports the FUNCTIONS
# (same objects). These names are the builders' closed-over vocabulary, not
# a second identity table.
WORKER = "cosmos-dispatch"
DEFAULT_MODEL = "grok-4.6"
GROK_MAX_TURNS = "60"
CURSOR_BASE = "https://api.cursor.com"
CURSOR_REPO = "https://github.com/keithbbf-gif/cosmos"
CURSOR_REF = "main"
CLAUDE_MODEL = "claude-fable-5"
CLAUDE_KINDS = frozenset({"claude", "sonnet", "haiku"})
WORKER_KINDS = frozenset({"gem", "oa"})
GROQ_MODEL = "openai/gpt-oss-20b"
OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it:free"


# ---------------------------------------------------------------------------
# job source (R4: grok flags locked; cursor/claude provisional)
# ---------------------------------------------------------------------------

def _py_path(p: Path | None) -> str:
    if p is None:
        return "None"
    return f"Path({json.dumps(str(p))})"


def _job_helpers_block(agent: str, result_path: Path, returns_path: Path,
                       inbox_path: Path | None, sentinel_path: Path | None) -> str:
    return f'''import json, time
from pathlib import Path
AGENT = {json.dumps(agent)}
RESULT = {_py_path(result_path)}
RETURNS = {_py_path(returns_path)}
INBOX = {_py_path(inbox_path)}
SENTINEL = {_py_path(sentinel_path)}

def _bind_live(out):
    try:
        if SENTINEL is not None and SENTINEL.exists():
            _s = json.loads(SENTINEL.read_text(encoding="utf-8"))
            out["live_tree_id"] = _s.get("tree_id")
            out["live_system"] = _s.get("system")
            out["live_sentinel"] = str(SENTINEL)
            out["live_sentinel_mtime"] = SENTINEL.stat().st_mtime
    except Exception as _e:
        out["live_bind_error"] = f"{{type(_e).__name__}}: {{_e}}"
    return out

def _emit(out):
    payload = json.dumps(out, indent=1)
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(payload, encoding="utf-8")
    if RETURNS:
        RETURNS.parent.mkdir(parents=True, exist_ok=True)
        RETURNS.write_text(payload, encoding="utf-8")
    if INBOX:
        INBOX.parent.mkdir(parents=True, exist_ok=True)
        INBOX.write_text(payload, encoding="utf-8")
'''


def _grok_job(agent: str, task: str, target_dir: str, model: str,
              result_path: Path, returns_path: Path, timeout_s: int,
              inbox_path: Path | None, sentinel_path: Path | None,
              runtime_root: Path | None = None,
              cosmos_dir: Path | None = None,
              attempt_id: str | None = None) -> str:
    # PROVEN flags - do not change the flag set. --cwd VALUE is the
    # attempt-private clone, never the live repo tree (P10).
    cosmos = Path(cosmos_dir) if cosmos_dir is not None else Path(__file__).resolve().parent
    root_s = json.dumps(str(runtime_root) if runtime_root else "")
    return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# dispatched by cosmos_dispatch ({WORKER}) — grok lane. Do not edit by hand.
# P10: --cwd is an attempt-private clone; never the live tree.
import os, subprocess, sys
{_job_helpers_block(agent, result_path, returns_path, inbox_path, sentinel_path)}
TASK = {json.dumps(task)}
SOURCE = {json.dumps(target_dir)}
ROOT = {root_s}
ATTEMPT = {json.dumps(str(attempt_id or ""))}
MODEL = {json.dumps(model)}
sys.path.insert(0, {json.dumps(str(cosmos))})
from cosmos_dispatch import (
    DispatchError, collect_workspace_proposal, prepare_grok_workspace,
)
t0 = time.time()
out = {{"agent": AGENT, "kind": "grok", "model": MODEL,
        "source_tree": SOURCE, "gateway": "fenced_commit",
        "workspace_policy": "attempt-private"}}
_bind_live(out)
_emit(out)
try:
    ws, clone_rec = prepare_grok_workspace(
        SOURCE, live_root=(ROOT or None), attempt_id=ATTEMPT)
    CWD = str(ws)
    out["workspace"] = CWD
    out["clone"] = clone_rec
    argv = ["grok", "--single", TASK, "-m", MODEL, "--output-format", "plain",
            "--always-approve", "--max-turns", {json.dumps(GROK_MAX_TURNS)},
            "--cwd", CWD]
    out["argv"] = argv
    _emit(out)
    _kw = {{}}
    if os.name == "nt":
        _si = subprocess.STARTUPINFO()
        _si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        _si.wShowWindow = 0
        _kw = {{"creationflags": 0x08000000, "startupinfo": _si}}
    p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=CWD, timeout={int(timeout_s)},
                       **_kw)
    out.update({{"rc": p.returncode, "secs": round(time.time() - t0, 1),
                 "stdout_tail": (p.stdout or "")[-4000:],
                 "stderr_tail": (p.stderr or "")[-1500:]}})
    try:  # P5 anti-loss: persist FULL stdout beside the result (tail alone lost
          # whole propose-only files: pool/CVM_ARCH/COMPETENCY, 2026-08-26).
        with open(str(RESULT) + ".stdout.txt", "w", encoding="utf-8") as _fh:
            _fh.write(p.stdout or "")
        out["stdout_full"] = str(RESULT) + ".stdout.txt"
    except Exception:
        pass
    try:
        prop = collect_workspace_proposal(
            ws, diff_path=str(RESULT) + ".diff.txt")
        out["proposal"] = prop
        if prop.get("diff_path"):
            out["proposal_diff"] = prop["diff_path"]
    except Exception as _pe:
        out["proposal_error"] = f"{{type(_pe).__name__}}: {{_pe}}"
except DispatchError as e:
    # NEVER fall back to SOURCE as cwd — that is the live tree.
    out["error"] = f"{{e.kind}}: {{e}}"
    out["kind_err"] = e.kind
    out["secs"] = round(time.time() - t0, 1)
    out["rc"] = 2
except Exception as e:
    out["error"] = f"{{type(e).__name__}}: {{e}}"
    out["secs"] = round(time.time() - t0, 1)
    out["rc"] = 2
_emit(out)
raise SystemExit(0 if out.get("rc") == 0 else 2)
'''


def _cursor_job(agent: str, task: str, key_path: Path, result_path: Path,
                returns_path: Path, timeout_s: int, model: str | None,
                inbox_path: Path | None, sentinel_path: Path | None) -> str:
    model_id = pin_cursor_model(model)
    body = {
        "prompt": {"text": task},
        "repos": [{"url": CURSOR_REPO, "startingRef": CURSOR_REF}],
        "autoCreatePR": True,
        "model": {"id": model_id},
    }
    return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# dispatched by cosmos_dispatch ({WORKER}) — Cursor Cloud Agents API v1.
# Key is READ at runtime from the path below; never baked in.
import base64, urllib.error, urllib.request
{_job_helpers_block(agent, result_path, returns_path, inbox_path, sentinel_path)}
KEYP = Path({json.dumps(str(key_path))})
BASE = {json.dumps(CURSOR_BASE)}
BODY = {json.dumps(body)}
TIMEOUT_S = {int(timeout_s)}
key = KEYP.read_text(encoding="utf-8").strip()
auth = "Basic " + base64.b64encode((key + ":").encode()).decode()

def call(method, path, body=None):
    req = urllib.request.Request(
        BASE + path, method=method,
        headers={{"Authorization": auth, "Content-Type": "application/json"}},
        data=(json.dumps(body).encode() if body is not None else None))
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{{}}")
    except urllib.error.HTTPError as e:
        return e.code, {{"error": (e.read().decode() or "")[:400]}}
    except Exception as e:
        return -1, {{"error": f"{{type(e).__name__}}: {{e}}"}}

out = {{"agent": AGENT, "kind": "cursor", "kind_live": "UNPROVEN",
        "key_last4": key[-4:] if len(key) >= 4 else ""}}
_bind_live(out)
_emit(out)
t0 = time.time()
try:
    s, me = call("GET", "/v1/me")
    out["me"] = {{"status": s, "apiKeyName": me.get("apiKeyName"),
                  "err": me.get("error")}}
    if s != 200:
        out["rc"] = 2
    else:
        s2, a = call("POST", "/v1/agents", BODY)
        aid = (a.get("agent") or {{}}).get("id") or a.get("id")
        rid = (a.get("run") or {{}}).get("id")
        out["launch"] = {{"status": s2, "agent": aid, "run": rid,
                          "err": a.get("error")}}
        if not (aid and rid):
            out["rc"] = 2
        else:
            deadline = t0 + TIMEOUT_S - 30
            terminal = ("FINISHED", "ERROR", "CANCELLED", "EXPIRED")
            while time.time() < deadline:
                time.sleep(15)
                s3, run = call("GET", f"/v1/agents/{{aid}}/runs/{{rid}}")
                st = run.get("status")
                if st in terminal:
                    out["run"] = {{"http": s3, "status": st,
                                   "result": (run.get("result") or "")[:800],
                                   "durationMs": run.get("durationMs"),
                                   "git": run.get("git")}}
                    out["rc"] = 0 if st == "FINISHED" else 2
                    break
            else:
                out["run"] = {{"status": "TIMEOUT_POLLING"}}
                out["rc"] = 2
except Exception as e:
    out["error"] = f"{{type(e).__name__}}: {{e}}"
    out["rc"] = 2
out["secs"] = round(time.time() - t0, 1)
_emit(out)
raise SystemExit(0 if out.get("rc") == 0 else 2)
'''


def _codex_job(agent: str, task: str, target_dir: str, key_path: Path,
               result_path: Path, returns_path: Path, timeout_s: int,
               model: str | None, inbox_path: Path | None,
               sentinel_path: Path | None, runtime_root: Path,
               cosmos_dir: Path) -> str:
    """Route --agent codex to cosmos_codex_rail. Key is READ at runtime;
    never baked. done binds last_message + real model field, never rc.
    """
    model_id = model if model and model not in (DEFAULT_MODEL, "") else None
    return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# dispatched by cosmos_dispatch ({WORKER}) — Codex CLI coder rail.
# Key is READ at runtime from the path below; never baked in.
# done = --output-last-message + real model field; rc is recorded, not the predicate.
import sys
{_job_helpers_block(agent, result_path, returns_path, inbox_path, sentinel_path)}
sys.path.insert(0, {json.dumps(str(cosmos_dir))})
from cosmos_codex_rail import run_coding_dispatch
ROOT = {json.dumps(str(runtime_root))}
TASK = {json.dumps(task)}
CWD = {json.dumps(target_dir)}
KEYP = Path({json.dumps(str(key_path))})
MODEL = {json.dumps(model_id)}
TIMEOUT_S = {int(timeout_s)}
t0 = time.time()
out = {{"agent": AGENT, "kind": "codex", "kind_live": "UNPROVEN",
        "key_path_name": KEYP.name, "model": MODEL}}
_bind_live(out)
_emit(out)
try:
    extra = {{"repo": CWD, "timeout_s": TIMEOUT_S, "mode": "coder"}}
    if MODEL:
        extra["model"] = MODEL
    rec = run_coding_dispatch(ROOT, TASK, mode="coder", extra=extra)
    last = (rec.get("last_message") or "").strip()
    model = rec.get("model")
    # Runtime-binding: done is the artifact pair, NEVER rec["rc"] / subprocess rc.
    done = bool(last) and bool(model)
    out.update({{
        "ok": done,
        "done": done,
        "done_why": rec.get("done_why"),
        "model": model,
        "model_source": rec.get("model_source"),
        "last_message": last[:4000],
        "last_message_path": rec.get("last_message_path"),
        "workspace": rec.get("workspace"),
        "pr_url": rec.get("pr_url"),
        "pr_ready": rec.get("pr_ready"),
        "gateway": rec.get("gateway") or "fenced_commit",
        "thread_id": rec.get("thread_id"),
        "usage": rec.get("usage"),
        "observed_rc": rec.get("rc"),
        "detail": rec.get("detail"),
        "kind_rail": rec.get("kind"),
        "secs": round(time.time() - t0, 1),
    }})
    out["rc"] = 0 if done else 2
except Exception as e:
    out["error"] = f"{{type(e).__name__}}: {{e}}"
    out["secs"] = round(time.time() - t0, 1)
    out["done"] = False
    out["ok"] = False
    out["rc"] = 2
_emit(out)
raise SystemExit(0 if out.get("done") else 2)
'''


def _claude_job(agent: str, task: str, target_dir: str, result_path: Path,
                returns_path: Path, timeout_s: int,
                inbox_path: Path | None, sentinel_path: Path | None,
                model: str, kind: str) -> str:
    lane_model = str(model or CLAUDE_MODEL)
    lane_kind = str(kind or "claude")
    return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# dispatched by cosmos_dispatch ({WORKER}) — {lane_kind} claude-CLI lane. Do not edit by hand.
import os, subprocess
{_job_helpers_block(agent, result_path, returns_path, inbox_path, sentinel_path)}
TASK = {json.dumps(task)}
CWD = {json.dumps(target_dir)}
t0 = time.time()
argv = ["claude", "-p", TASK, "--model", {json.dumps(lane_model)},
        "--permission-mode", "dontAsk", "--add-dir", CWD]
out = {{"agent": AGENT, "kind": {json.dumps(lane_kind)}, "kind_live": "proven",
        "model": {json.dumps(lane_model)}, "argv": argv}}
_bind_live(out)
_emit(out)
try:
    p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=CWD, timeout={int(timeout_s)},
                       creationflags=(0x08000000 if os.name == "nt" else 0))
    out.update({{"rc": p.returncode, "secs": round(time.time() - t0, 1),
                 "stdout_tail": (p.stdout or "")[-4000:],
                 "stderr_tail": (p.stderr or "")[-1500:]}})
    try:  # P5 anti-loss: persist FULL stdout beside the result (tail alone lost
          # whole propose-only files: pool/CVM_ARCH/COMPETENCY, 2026-08-26).
        with open(str(RESULT) + ".stdout.txt", "w", encoding="utf-8") as _fh:
            _fh.write(p.stdout or "")
        out["stdout_full"] = str(RESULT) + ".stdout.txt"
    except Exception:
        pass
except Exception as e:
    out["error"] = f"{{type(e).__name__}}: {{e}}"
    out["secs"] = round(time.time() - t0, 1)
    out["rc"] = 2
_emit(out)
raise SystemExit(0 if out.get("rc") == 0 else 2)
'''


def _worker_job(kind: str, agent: str, task: str, worker_dir: Path,
                result_path: Path, returns_path: Path, timeout_s: int,
                inbox_path: Path | None, sentinel_path: Path | None,
                out_dir: Path | None = None,
                compat_dir: Path | None = None,
                runtime_root: Path | None = None) -> str:
    """Drop onto live/buckets/<node> and run that node's rail. No BTS import.

    gem/oa: identity is live/buckets/<node> (what cosmos_node_worker polls).
    The job calls cosmos_node_worker.execute_handoff which writes the packet
    there AND actually invokes the rail. done = nonempty stdout; rc is
    recorded, never the predicate (docs/SCAR_PLACATION.md: empty GEM/OA
    critiques with rc=0 secs=0.0 — packet-and-exit SystemExit(0) was the
    scar). SSA is a claude-CLI lane (Sonnet), not a worker-bucket handoff.
    """
    if kind in ("gem", "oa"):
        cosmos_dir = str(Path(__file__).resolve().parent)
        root_s = str(runtime_root) if runtime_root else ""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# dispatched by cosmos_dispatch ({WORKER}) — {kind} node-worker rail.
import sys
{_job_helpers_block(agent, result_path, returns_path, inbox_path, sentinel_path)}
sys.path.insert(0, {json.dumps(cosmos_dir)})
from cosmos_node_worker import execute_handoff
KIND = {json.dumps(kind)}
TASK = {json.dumps(task)}
ROOT = {json.dumps(root_s)}
TIMEOUT_S = {int(timeout_s)}
WORKER_DIR = Path({json.dumps(str(worker_dir))})
t0 = time.time()
out = {{"agent": AGENT, "kind": KIND, "kind_live": "handoff"}}
_bind_live(out)
_emit(out)
try:
    rec = execute_handoff(ROOT, KIND, AGENT, TASK, str(RESULT),
                          timeout_s=TIMEOUT_S)
    out.update(rec)
    out["secs"] = round(time.time() - t0, 1)
except Exception as e:
    out["error"] = f"{{type(e).__name__}}: {{e}}"
    out["secs"] = round(time.time() - t0, 1)
    out["done"] = False
    out["ok"] = False
    out["rc"] = 2
_emit(out)
raise SystemExit(0 if out.get("done") else 2)
'''
    return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# dispatched by cosmos_dispatch ({WORKER}) — {kind} worker-bucket handoff.
import os
from datetime import datetime
{_job_helpers_block(agent, result_path, returns_path, inbox_path, sentinel_path)}
KIND = {json.dumps(kind)}
TASK = {json.dumps(task)}
WORKER_DIR = Path({json.dumps(str(worker_dir))})
COMPAT_DIR = {_py_path(compat_dir)}
OUT_DIR = {_py_path(out_dir)}
t0 = time.time()
stamp = datetime.now().astimezone().isoformat()
WORKER_DIR.mkdir(parents=True, exist_ok=True)
(WORKER_DIR / "processed").mkdir(exist_ok=True)
(WORKER_DIR / "failed").mkdir(exist_ok=True)
name = "handoff_" + stamp.replace(":", "").replace("+", "p") + ".json"
dest = WORKER_DIR / name
packet = {{
    "id": dest.stem, "agent": AGENT, "kind": KIND,
    "prompt": TASK, "task": TASK, "assignment": TASK, "stamp": stamp,
    "out": "V",
    "out_dir": str(OUT_DIR) if OUT_DIR else None,
    "result": str(RESULT), "returns": str(RETURNS),
    "source": {json.dumps(WORKER)},
}}
dest.write_text(json.dumps(packet, indent=1), encoding="utf-8")
compat_path = None
if COMPAT_DIR:
    COMPAT_DIR.mkdir(parents=True, exist_ok=True)
    compat_path = COMPAT_DIR / name
    compat_path.write_text(json.dumps(packet, indent=1), encoding="utf-8")
out = {{"agent": AGENT, "kind": KIND, "kind_live": "handoff",
        "status": "assigned",
        "worker_packet": str(dest),
        "worker_packet_compat": str(compat_path) if compat_path else None,
        "secs": round(time.time() - t0, 1)}}
_bind_live(out)
_emit(out)
raise SystemExit(0)
'''


def _groq_job(agent: str, task: str, model: str,
              result_path: Path, returns_path: Path, timeout_s: int,
              inbox_path: Path | None, sentinel_path: Path | None,
              runtime_root: Path, cosmos_dir: Path) -> str:
    """Headless SSA replacement: groq-api gpt-oss-20b. Key read at runtime."""
    mid = (model or GROQ_MODEL).strip() or GROQ_MODEL
    return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# dispatched by cosmos_dispatch ({WORKER}) — groq SSA replacement.
# Not Claude CLI. Not GF38. Not Vertex Llama.
import sys
{_job_helpers_block(agent, result_path, returns_path, inbox_path, sentinel_path)}
sys.path.insert(0, {json.dumps(str(cosmos_dir))})
from cosmos_paths import CosmosPaths
from cosmos_groq_rail import GroqRail, KEY_NAME, load_spec
KIND = "groq"
TASK = {json.dumps(task)}
MODEL = {json.dumps(mid)}
ROOT = {json.dumps(str(runtime_root))}
TIMEOUT_S = {int(timeout_s)}
t0 = time.time()
out = {{"agent": AGENT, "kind": KIND, "kind_live": "adapter",
        "model_requested": MODEL}}
_bind_live(out)
try:
    paths = CosmosPaths(ROOT)
    spec_p = paths.config("groq_rail.json")
    spec = load_spec(spec_p if spec_p.is_file() else None)
    rail = GroqRail(paths.config(KEY_NAME), spec)
    rec = rail.dispatch({{
        "prompt": TASK,
        "model": MODEL,
        "reasoning_effort": "low",
        "max_completion_tokens": 1024,
    }})
    out["ok"] = bool(rec.get("ok"))
    out["http"] = rec.get("http")
    out["model"] = rec.get("model")
    out["text"] = rec.get("text") or ""
    out["usage"] = rec.get("usage") or {{}}
    out["link_id"] = rec.get("link_id") or "groq-api"
    out["kind_err"] = rec.get("kind")
    out["detail"] = rec.get("detail")
    out["secs"] = round(time.time() - t0, 1)
    if not out["ok"]:
        out["status"] = "failed"
        _emit(out)
        raise SystemExit(2)
    out["status"] = "done"
    _emit(out)
    raise SystemExit(0)
except SystemExit:
    raise
except Exception as e:
    out["ok"] = False
    out["status"] = "failed"
    out["error"] = f"{{type(e).__name__}}: {{e}}"
    out["secs"] = round(time.time() - t0, 1)
    _emit(out)
    raise SystemExit(2)
'''


def _openrouter_job(agent: str, task: str, model: str,
                    result_path: Path, returns_path: Path, timeout_s: int,
                    inbox_path: Path | None, sentinel_path: Path | None,
                    runtime_root: Path, cosmos_dir: Path) -> str:
    """Named Gemma 4 :free via OpenRouter. Not the rotating free router."""
    mid = (model or OPENROUTER_MODEL).strip() or OPENROUTER_MODEL
    return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# dispatched by cosmos_dispatch ({WORKER}) — OpenRouter named Gemma 4.
# Named pin only. Rotator refused. Not Groq. Not Vertex.
import sys
{_job_helpers_block(agent, result_path, returns_path, inbox_path, sentinel_path)}
sys.path.insert(0, {json.dumps(str(cosmos_dir))})
from cosmos_paths import CosmosPaths
from cosmos_openrouter_rail import OpenRouterRail, KEY_NAME, load_spec
KIND = "openrouter"
TASK = {json.dumps(task)}
MODEL = {json.dumps(mid)}
ROOT = {json.dumps(str(runtime_root))}
TIMEOUT_S = {int(timeout_s)}
t0 = time.time()
out = {{"agent": AGENT, "kind": KIND, "kind_live": "adapter",
        "model_requested": MODEL}}
_bind_live(out)
try:
    paths = CosmosPaths(ROOT)
    spec_p = paths.config("openrouter_rail.json")
    spec = load_spec(spec_p if spec_p.is_file() else None)
    rail = OpenRouterRail(paths.config(KEY_NAME), spec)
    rec = rail.dispatch({{
        "prompt": TASK,
        "model": MODEL,
        "max_tokens": 1024,
    }})
    out["ok"] = bool(rec.get("ok"))
    out["http"] = rec.get("http")
    out["model"] = rec.get("model")
    out["text"] = rec.get("text") or ""
    out["usage"] = rec.get("usage") or {{}}
    out["link_id"] = rec.get("link_id") or "openrouter-api"
    out["kind_err"] = rec.get("kind")
    out["detail"] = rec.get("detail")
    out["secs"] = round(time.time() - t0, 1)
    if not out["ok"]:
        out["status"] = "failed"
        _emit(out)
        raise SystemExit(2)
    out["status"] = "done"
    _emit(out)
    raise SystemExit(0)
except SystemExit:
    raise
except Exception as e:
    out["ok"] = False
    out["status"] = "failed"
    out["error"] = f"{{type(e).__name__}}: {{e}}"
    out["secs"] = round(time.time() - t0, 1)
    _emit(out)
    raise SystemExit(2)
'''


def render_job(kind: str, agent: str, task: str, target_dir: str, model: str,
               result_path: Path, returns_path: Path, timeout_s: int,
               key_path: Path | None,
               inbox_path: Path | None = None,
               sentinel_path: Path | None = None,
               worker_dir: Path | None = None,
               out_dir: Path | None = None,
               runtime_root: Path | None = None,
               compat_dir: Path | None = None,
               attempt_id: str | None = None) -> str:
    if kind == "grok":
        return _grok_job(agent, task, target_dir, model, result_path,
                         returns_path, timeout_s, inbox_path, sentinel_path,
                         runtime_root=runtime_root,
                         cosmos_dir=Path(__file__).resolve().parent,
                         attempt_id=attempt_id)
    if kind == "cursor":
        if key_path is None:
            raise DispatchError("NO_KEY", "cursor kind needs the COSMOS Cursor key path")
        return _cursor_job(agent, task, key_path, result_path, returns_path,
                           timeout_s, model, inbox_path, sentinel_path)
    if kind == "codex":
        if key_path is None:
            raise DispatchError("NO_KEY", "codex kind needs the OpenAI key path")
        if runtime_root is None:
            raise DispatchError("NO_ROOT", "codex kind needs the runtime root")
        return _codex_job(
            agent, task, target_dir, key_path, result_path, returns_path,
            timeout_s, model, inbox_path, sentinel_path,
            Path(runtime_root), Path(__file__).resolve().parent)
    if kind in CLAUDE_KINDS:
        raise DispatchError(
            "ANTHROPIC_OFF",
            "Keith 2026-09-01: no claude-family job files. Kind=%s." % kind)
    if kind == "groq":
        if runtime_root is None:
            raise DispatchError("NO_ROOT", "groq kind needs the runtime root")
        return _groq_job(
            agent, task, model, result_path, returns_path, timeout_s,
            inbox_path, sentinel_path, Path(runtime_root),
            Path(__file__).resolve().parent)
    if kind == "openrouter":
        if runtime_root is None:
            raise DispatchError("NO_ROOT", "openrouter kind needs the runtime root")
        return _openrouter_job(
            agent, task, model, result_path, returns_path, timeout_s,
            inbox_path, sentinel_path, Path(runtime_root),
            Path(__file__).resolve().parent)
    if kind in WORKER_KINDS:
        if worker_dir is None:
            raise DispatchError("NO_DIR", f"{kind} kind needs a worker bucket path")
        return _worker_job(kind, agent, task, worker_dir, result_path,
                           returns_path, timeout_s, inbox_path, sentinel_path,
                           out_dir=out_dir, compat_dir=compat_dir,
                           runtime_root=runtime_root)
    raise DispatchError("BAD_INPUT", f"unhandled kind {kind!r}")

