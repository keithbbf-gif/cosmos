#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_dispatch - offload layer: TYPE + task in; the OS does the rest.

Caller gives an agent TYPE (e.g. G46) + a task. This module:
  * infers the invocation from the type
  * default identity is the resolver `queue` role (CosmosPaths) — native
  * BTS file-drop remains an explicit `--queue` compatibility lane (decision 9)
  * AUTO-STAMPS docs/AGENT_BRIEF.md (DHx) from datetime.now().astimezone()
    using the protocol grammar `ISO · agent · assignment · stream/file`
  * drops a collector inbox sidecar and appends the assignment under the
    collector's index lock (one locked writer protocol)
  * FILES the result under the locked returns path: queue/returns/<stream>/
  * job_status()/wait_for() monitor; wait_for is CLI `--wait` only
  * native path submits an immutable manifest through Scheduler (decision 4)

The attempt-private workspace fence (P10) lives in `cosmos_dispatch_workspace`
and is re-exported here (PHASE 4 seam, docs/CORE_RESTRUCTURE.md). The
job-source builders (R4) live in `cosmos_dispatch_jobs` and are re-exported
here the same way. Stage-5 critic inlining lives in
`cosmos_dispatch_critique` and is re-exported here the same way.
BTS lane accounting lives in `cosmos_dispatch_lanes` and is
re-exported here the same way. Stamps / DHx / collector index live in
`cosmos_dispatch_stamps` and are re-exported here the same way.

Does not modify kernel / ledger / sched / service source. Native submit uses
Scheduler as a client so the queue ledger has one writer.

    from cosmos_dispatch import dispatch, job_status
    dispatch("G46", "the task")   # dir + queue defaulted; kind inferred

    py -3.14 cosmos\\cosmos_dispatch.py --agent G46 --task "..."
    py -3.14 cosmos\\cosmos_dispatch.py --status <jobfile>
    py -3.14 cosmos\\cosmos_dispatch.py --gate --root <runtime-root>

Kinds (or auto from agent type):
  grok   -> grok --single <task> -m <model> --output-format plain --always-approve
            --max-turns 60 --cwd <attempt-private workspace>
            (PROVEN flags; do not change the flag set. --cwd is the
            attempt-private clone, NEVER the live repo tree. P10.)
  cursor -> POST https://api.cursor.com/v1/agents  (Cloud Agents API v1;
            key from config/cursor_cosmos_key.txt; recipe in
            docs/research/CURSOR_CLOUD_AGENTS_API_v1.md)  UNPROVEN through this harness
  codex  -> cosmos_codex_rail.run_coding_dispatch  (Codex CLI coder+vetter;
            key from config/openai_api_key.txt; recipe in
            docs/research/GITHUB_CODEX_RAIL.md)  UNPROVEN through this harness
  claude / F5 -> claude -p <task> --model claude-fable-5 --permission-mode dontAsk
            --add-dir <dir>   UNPROVEN through this harness
  sonnet -> ANTHROPIC_OFF (no claude -p)
  SSA / subagent / groq -> groq-api openai/gpt-oss-20b (headless SSA replacement,
            Keith 2026-09-05). Not Vertex Llama. Not GF38. Not claude -p.
  haiku  -> claude -p <task> --model haiku --permission-mode dontAsk
            --add-dir <dir>   UNPROVEN through this harness

Defaults (two, kept distinct -- DHx: coding never Sonnet):
  coding -> G46 / grok-4.6 (Cursor is the other coding lane)
  research / analysis / vetting / subagent -> groq (was SSA/sonnet; Anthropic off)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402
# PHASE 4 seam (docs/CORE_RESTRUCTURE.md): the attempt-private workspace fence
# (P10) moved to cosmos_dispatch_workspace. Re-exported here -- and for
# DispatchError it is the SAME class object, not a copy -- so every importer,
# including the grok job this module generates, works unchanged. Additive.
from cosmos_dispatch_workspace import (  # noqa: E402,F401
    CLONE_IGNORE, GROK_WORK_LANE, PROPOSAL_DIFF_CAP, DispatchError,
    _CREATE_NO_WINDOW, _as_resolved, _safe_attempt_id, _seed_clone,
    assert_not_live_workspace, clone_attempt_workspace,
    collect_workspace_proposal, prepare_grok_workspace,
)
# PHASE 4 seam (docs/CORE_RESTRUCTURE.md): job-source builders live in
# cosmos_dispatch_jobs and are re-exported here -- same objects, not copies
# -- so dispatch() and tests/test_dispatch.py (`render_job` via the job
# file text) keep working unchanged. Additive.
from cosmos_dispatch_jobs import (  # noqa: E402,F401
    _claude_job, _codex_job, _cursor_job, _grok_job, _groq_job,
    _job_helpers_block, _py_path, _worker_job, render_job,
)
# PHASE 4 seam (docs/CORE_RESTRUCTURE.md): stage-5 critic inlining lives in
# cosmos_dispatch_critique. Re-exported here -- SAME objects, not copies --
# so dispatch() of gem/oa stage-5 tasks and tests/test_dispatch.py
# (`compose_critique_prompt`) keep working unchanged. Additive.
from cosmos_dispatch_critique import (  # noqa: E402,F401
    _file_row, _format_inlined, _inline_file, _is_critique_task,
    _locate_artifact, _path_tokens, _posix_rel, _seen_path, _under_root,
    compose_critique_prompt,
)
# PHASE 4 seam (docs/CORE_RESTRUCTURE.md): BTS lane accounting lives in
# cosmos_dispatch_lanes. Re-exported here -- SAME objects, not copies --
# so dispatch() / job_status / cosmos_watchdog2 (`measure_lanes`) keep
# working unchanged. Additive.
from cosmos_dispatch_lanes import (  # noqa: E402,F401
    _find_existing, _is_helper, _is_runnable, _lane_dir, _lane_of_path,
    _write_exclusive, job_filename, lane_load, locate_job, measure_lanes,
    pick_least_loaded, returns_dir,
)
# PHASE 4 seam (docs/CORE_RESTRUCTURE.md): stamps / DHx / collector index
# live in cosmos_dispatch_stamps. Re-exported here -- SAME objects, not
# copies -- so dispatch() / job_status / cosmos_node_worker
# (`append_dhx_marker`) / cosmos_dispatcher_daemon (`compose_agent_prompt`)
# keep working unchanged. Additive.
from cosmos_dispatch_stamps import (  # noqa: E402,F401
    _LockCM, _already_in_index, _iso_now, _iter_index_rows, _latest_for_job,
    _marker_line, _marker_tail, _with_file_lock, append_assignment_row,
    append_dhx_marker, append_index_row, append_session_assignment,
    compose_agent_prompt, load_boundaries_text, repo_docs_dir,
    write_inbox_sidecar,
)

SCHEMA = "cosmos-collector/2"
WORKER = "cosmos-dispatch"
NATIVE_STREAM = "cm"
MARKER_SEP = " · "
INDEX_LOCK_NAME = "index.jsonl.lock"
INDEX_NAME = "index.jsonl"
CURSOR_KEY_NAME = "cursor_cosmos_key.txt"
OPENAI_KEY_NAME = "openai_api_key.txt"
SENTINEL_NAME = ".cosmos-root.json"

LANE_ORDER = ("root", "lg", "pb")
RUNNABLE_SUFFIXES = {".py", ".bat", ".cmd", ".ps1"}
SKIP_COUNT_NAMES = {
    "running", "done", "failed", "logs", "staged", "elevated",
    "_lanes", "_delme", "_hold", "_superseded", "__pycache__",
    "research", "findings", "returns", ".git", ".tmp",
    "manifests", "jobs", "dispatch_jobs",
}

KIND_CANON = {
    "grok": "grok",
    "g46": "grok",
    "gw": "grok",
    "sgh": "grok",
    "cursor": "cursor",
    "codex": "codex",
    "claude": "claude",
    "f5": "claude",
    "claude-fable": "claude",
    "claude_fable": "claude",
    "sonnet": "sonnet",
    "sonnet5": "sonnet",
    "haiku": "haiku",
    "haiku45": "haiku",
    "gem": "gem",
    "gemini": "gem",
    "oa": "oa",
    "oai": "oa",
    "openai": "oa",
    "ssa": "groq",
    "subagent": "groq",
    "sonnetsubagent": "groq",
    "groq": "groq",
    "gptoss": "groq",
    "gptoss20b": "groq",
}

# Agent TYPE -> kind. Longest alnum-folded key wins. Explicit --kind overrides.
# Spec tags: G46/GW/SGH/GEM/OAi/CURSOR/SSA/SONNET/HAIKU.
# SSA/subagent remap to groq (Keith 2026-09-05). sonnet/haiku stay Claude CLI = OFF.
AGENT_TYPE_KIND = {
    "g46": "grok",
    "gw": "grok",
    "grokbuild": "grok",
    "grok": "grok",
    "gbw": "grok",
    "gwb": "grok",
    "sgh": "grok",
    "supergrok": "grok",
    "gem": "gem",
    "gemini": "gem",
    "oai": "oa",
    "oa": "oa",
    "openai": "oa",
    "cursor": "cursor",
    "codex": "codex",
    "ssa": "groq",
    "subagent": "groq",
    "sonnetsubagent": "groq",
    "groq": "groq",
    "gptoss": "groq",
    "claude": "claude",
    "fable": "claude",
    "f5": "claude",
    "sonnet": "sonnet",
    "sonnet5": "sonnet",
    "haiku": "haiku",
    "haiku45": "haiku",
}

KIND_MAKER = {
    "grok": "Grok", "cursor": "Cursor", "codex": "Codex", "claude": "Claude",
    "sonnet": "Claude", "haiku": "Claude",
    "gem": "Gemini", "oa": "OpenAI", "ssa": "SSA", "groq": "Groq",
}
# grok is live-proven through this harness. claude-family CLI is live-proven
# 2026-08-31T18:42Z: dispatch F5 job -> claude -p PONG, result_rc=0
# (cosmos/_f69_h6_live.json). cursor Cloud Agents and codex stay UNPROVEN
# (no vendor FINISHED through those builders this fence; no key chase).
# gem/oa drop onto live/buckets/<node> AND spawn that node's rail
# (execute_handoff). Packet-and-exit rc=0 was the scar
# (docs/SCAR_PLACATION.md: OA fa6c68cc rc=0 secs=0.0, empty critique).
# SSA remaps to groq (gpt-oss-20b). Claude CLI kinds stay ANTHROPIC_OFF.
KIND_LIVE = {
    "grok": "proven", "cursor": "UNPROVEN", "codex": "UNPROVEN",
    "claude": "ANTHROPIC_OFF", "sonnet": "ANTHROPIC_OFF",
    "haiku": "ANTHROPIC_OFF", "ssa": "adapter",
    "groq": "adapter",
    "gem": "handoff", "oa": "handoff",
}
WORKER_KINDS = frozenset({"gem", "oa"})
CLAUDE_KINDS = frozenset({"claude", "sonnet", "haiku"})
GROQ_KINDS = frozenset({"groq", "ssa"})
# Node-worker identity is live/buckets/<node> (cosmos_node_worker.bucket_dir).
# oa/ssa use the same layout so a later worker can poll without a remap.
WORKER_BUCKET_NODE = {"gem": "gem", "oa": "oa", "ssa": "ssa"}
TAG_CANON = {
    "g46": "G46",
    "gw": "GW",
    "sgh": "SGH",
    "gem": "GEM",
    "gemini": "GEM",
    "oai": "OAi",
    "oa": "OAi",
    "openai": "OAi",
    "cursor": "CURSOR",
    "codex": "CODEX",
    "ssa": "SSA",
    "subagent": "SSA",
    "sonnetsubagent": "SSA",
    "groq": "GROQ",
    "gptoss": "GROQ",
    "f5": "F5",
    "claude": "F5",
    "fable": "F5",
    "sonnet": "SONNET",
    "sonnet5": "SONNET",
    "haiku": "HAIKU",
    "haiku45": "HAIKU",
    "grok": "G46",
    "grokbuild": "G46",
}
STREAM_FOR_LANE = {"root": "cm", "lg": "lg", "pb": "pb", "cm": "cm"}
STATUS_BUCKETS = ("queued", "running", "done", "failed")

GROK_MAX_TURNS = "60"          # proven; do not change
GROK_TIMEOUT_S = 1800
CURSOR_TIMEOUT_S = 900
CODEX_TIMEOUT_S = 1800
CLAUDE_TIMEOUT_S = 1800
CLAUDE_MODEL = "claude-fable-5"   # F5 coding lane (unchanged)
SONNET_MODEL = "sonnet"           # Sonnet 5 via local claude -p --model sonnet
HAIKU_MODEL = "haiku"             # Haiku 4.5 via local claude -p --model haiku
SSA_MODEL = SONNET_MODEL          # leftover alias; SSA kind remaps to groq
GROQ_MODEL = "openai/gpt-oss-20b"  # SSA replacement (Keith 2026-09-05)
GROQ_TIMEOUT_S = 180
CURSOR_BASE = "https://api.cursor.com"
CURSOR_REPO = "https://github.com/keithbbf-gif/cosmos"
CURSOR_REF = "main"
DEFAULT_MODEL = "grok-4.6"        # CODING default; never Sonnet
CODING_DEFAULT_AGENT = "G46"
RESEARCH_DEFAULT_AGENT = "G46"  # was SSA/sonnet; Anthropic off 2026-09-01
STALL_RATIO = 0.5
# Per-file cap for critic inlining. Truncation is marked; sha256 is of the FULL file.
CRITIQUE_INLINE_CAP = 120_000
# PROPOSAL_DIFF_CAP / GROK_WORK_LANE / CLONE_IGNORE / _CREATE_NO_WINDOW are
# imported from cosmos_dispatch_workspace above -- one definition, re-exported.

# Lane -> CLI model id. Cursor/codex honor an explicit --model.
KIND_MODEL = {
    "grok": DEFAULT_MODEL,
    "cursor": "claude-opus-5",
    "claude": CLAUDE_MODEL,
    "sonnet": SONNET_MODEL,
    "haiku": HAIKU_MODEL,
    "ssa": GROQ_MODEL,
    "groq": GROQ_MODEL,
}

# Explicit --model aliases for the claude-family CLI (not grok).
_CLAUDE_MODEL_ALIAS = {
    "sonnet": SONNET_MODEL,
    "sonnet5": SONNET_MODEL,
    "haiku": HAIKU_MODEL,
    "haiku45": HAIKU_MODEL,
    "fable": CLAUDE_MODEL,
    "fable5": CLAUDE_MODEL,
    "claudefable5": CLAUDE_MODEL,
    "f5": CLAUDE_MODEL,
    "opus": "opus",
}

# Task-class tokens. Coding wins (DHx: never Sonnet for coding).
_CODING_RE = re.compile(
    r"\b(implement|code|coding|coder|patch|fix|wire|build|compile|"
    r"refactor|function|class|module|py_compile|pytest|unittest|"
    r"typeerror|syntaxerror)\b",
    re.I,
)
_RESEARCH_RE = re.compile(
    r"\b(research|analys[ei]s|analy[sz]e|vet(?:ting|ter)?|critique|"
    r"subagent|scout|survey|present-day)\b",
    re.I,
)

DHX_ASSIGN_HEADER = "## Assignment log"
ONELINE_CAP = 140
GATE_TASK = (
    "Reply with the single word PONG. Do not edit any files. Do not read any files."
)


# DispatchError is defined in cosmos_dispatch_workspace (the lower layer, so the
# P10 fence can raise it without importing this module) and re-exported at the
# top of this file. `except DispatchError` is unchanged for every caller.


# ---------------------------------------------------------------------------
# resolver identity (R1 / R11) — no drive literal, no parent-walk from __file__
# ---------------------------------------------------------------------------

def bind_paths(runtime_root=None) -> CosmosPaths:
    """CosmosPaths from --root or the machine install record. Typed refusal, no guess."""
    if runtime_root is not None:
        try:
            return CosmosPaths(runtime_root)
        except CosmosPathError as e:
            raise DispatchError("NO_ROOT", str(e)) from e
    try:
        return CosmosPaths.from_install_record()
    except CosmosPathError as e:
        raise DispatchError(
            "NO_ROOT",
            f"no --root and install record unavailable: {e}",
        ) from e


def default_target_dir(paths: CosmosPaths) -> Path:
    """Repo tree of the two-roots layout (runtime parent holding DHx), else the root.

    This is the clone SOURCE for grok/G46 jobs. grok's process --cwd is an
    attempt-private workspace under the runtime `work` role, never this tree.
    """
    parent = paths.root.parent
    if (parent / "docs" / "AGENT_BRIEF.md").exists():
        return parent
    if paths.docs("AGENT_BRIEF.md").exists():
        return paths.root
    return parent


def default_dhx(paths: CosmosPaths) -> Path:
    parent = paths.root.parent
    cand = parent / "docs" / "AGENT_BRIEF.md"
    if cand.exists():
        return cand
    return paths.docs("AGENT_BRIEF.md")


def locked_returns_path(paths: CosmosPaths, stream: str, result_name: str) -> Path:
    """One returns identity: queue/returns/<stream>/<name> (R9)."""
    return paths.queue("returns", stream, result_name)


def index_path_for(paths: CosmosPaths) -> Path:
    return paths.state("collector", INDEX_NAME)


def index_lock_for(paths: CosmosPaths) -> Path:
    return paths.state("collector", INDEX_LOCK_NAME)


def inbox_dir(paths: CosmosPaths) -> Path:
    return paths.state("collector", "inbox")


def worker_bucket_dir(paths: CosmosPaths, kind: str) -> Path:
    """Identity drop zone the node workers poll: live/buckets/<node>."""
    node = WORKER_BUCKET_NODE.get(kind, kind)
    return paths.role("root", "buckets", node)


def worker_compat_dir(paths: CosmosPaths, kind: str) -> Path:
    """Prior drop zone (additive keep). Not identity — workers do not poll it."""
    return paths.state("dispatch", "workers", kind)


def dispatch_map_path(paths: CosmosPaths, filename: str) -> Path:
    return paths.state("dispatch", Path(filename).name + ".json")


def is_native_queue(queue: Path, paths: CosmosPaths) -> bool:
    try:
        return Path(queue).resolve() == paths.role("queue").resolve()
    except OSError:
        return False


# ---------------------------------------------------------------------------
# kind inference (R3 ACCEPT)
# ---------------------------------------------------------------------------

def _fold_agent(agent: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(agent or "").strip().lower())


def _canon_kind(kind: str) -> str:
    key = str(kind or "").strip().lower()
    if key not in KIND_CANON:
        raise DispatchError("BAD_INPUT",
                            f"unknown kind {kind!r}; want grok|cursor|codex|"
                            f"claude|F5|sonnet|haiku|gem|oa|groq|ssa")
    return KIND_CANON[key]


def infer_kind(agent: str) -> str:
    """Map an agent TYPE (G46, GW, SGH, GEM, OAi, CURSOR, SSA, SONNET, HAIKU, F5) to a kind."""
    folded = _fold_agent(agent)
    if not folded:
        raise DispatchError("BAD_INPUT",
                            "agent is required to auto-route kind")
    best = None
    best_n = -1
    for key, kind in AGENT_TYPE_KIND.items():
        if folded == key or folded.startswith(key):
            if len(key) > best_n:
                best, best_n = kind, len(key)
    if best is None:
        raise DispatchError(
            "BAD_INPUT",
            f"cannot infer kind from agent {agent!r}; pass "
            f"kind=grok|cursor|codex|claude|sonnet|haiku|gem|oa|groq|ssa")
    return best


def infer_task_class(task: str) -> str:
    """Classify a task as coding or research. Coding wins (never Sonnet)."""
    text = str(task or "")
    if _CODING_RE.search(text):
        return "coding"
    if _RESEARCH_RE.search(text):
        return "research"
    return "coding"


def infer_default_agent(task: str) -> str:
    """Default dispatch agent from task class. Coding->G46, research->SSA."""
    if infer_task_class(task) == "research":
        return RESEARCH_DEFAULT_AGENT
    return CODING_DEFAULT_AGENT


def resolve_lane_model(kind: str, model: str | None) -> str:
    """Bind the model id the lane actually shells.

    Claude-family kinds ignore the grok DEFAULT_MODEL so an omitted --model
    does not leak grok-4.6 onto `claude -p`. An explicit claude-family
    alias (sonnet/haiku/fable/opus) is honored. Coding default stays grok-4.6.
    """
    raw = str(model or "").strip()
    kind_c = str(kind or "").strip().lower()
    if kind_c in CLAUDE_KINDS:
        if raw and raw != DEFAULT_MODEL:
            folded = re.sub(r"[^a-z0-9]+", "", raw.lower())
            return _CLAUDE_MODEL_ALIAS.get(folded, raw)
        return KIND_MODEL[kind_c]
    if kind_c == "cursor":
        # Pin Opus 5. grok-4.6 / Auto / Composer 2.5 leaked onto this lane
        # and cache-read the GitHub repo (2026-09-02 token burn).
        folded = re.sub(r"[^a-z0-9]+", "", raw.lower())
        if not raw or raw == DEFAULT_MODEL or folded in (
                "auto", "default", "grok46", "composer", "composer25",
                "composer2", "composerlatest"):
            return KIND_MODEL["cursor"]
        if folded in ("opus", "opus5", "claudeopus5"):
            return KIND_MODEL["cursor"]
        return raw
    if kind_c in GROQ_KINDS or kind_c == "groq":
        if not raw or raw == DEFAULT_MODEL:
            return KIND_MODEL["groq"]
        return raw
    if not raw:
        return KIND_MODEL.get(kind_c, DEFAULT_MODEL)
    return raw


def parse_agent_tag(agent: str) -> dict:
    """Parse a drop TAG into {tag, kind, folded}. G46/GW/SGH/GEM/OAi/CURSOR/SSA/SONNET/HAIKU."""
    folded = _fold_agent(agent)
    if not folded:
        raise DispatchError("BAD_INPUT", "agent/tag is required")
    kind = infer_kind(agent)
    tag = None
    best_n = -1
    for key, canon in TAG_CANON.items():
        if folded == key or folded.startswith(key):
            if len(key) > best_n:
                tag, best_n = canon, len(key)
    if tag is None:
        tag = str(agent or "").strip().upper() or "UNK"
    return {"tag": tag, "kind": kind, "folded": folded, "raw": str(agent).strip()}


def resolve_kind(agent: str, kind: str | None) -> str:
    raw = str(kind or "").strip().lower()
    if raw in ("", "auto", "none"):
        return infer_kind(agent)
    return _canon_kind(raw)


def _oneline(text: str, n: int = ONELINE_CAP) -> str:
    s = " ".join(str(text).split())
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def _slug(text: str, n: int = 40) -> str:
    words = re.findall(r"[A-Za-z0-9]+", str(text).lower())
    s = "_".join(words) if words else "task"
    return s[:n].strip("_") or "task"


def _timeout_for(kind: str) -> int:
    if kind == "cursor":
        return CURSOR_TIMEOUT_S
    if kind == "codex":
        return CODEX_TIMEOUT_S
    if kind in CLAUDE_KINDS:
        return CLAUDE_TIMEOUT_S
    if kind == "groq":
        return GROQ_TIMEOUT_S
    if kind in ("gem", "oa"):
        return GROK_TIMEOUT_S
    if kind in WORKER_KINDS:  # unused while WORKER_KINDS == {gem, oa}
        return GROK_TIMEOUT_S
    return GROK_TIMEOUT_S


# ---------------------------------------------------------------------------
# BTS compatibility lane accounting (R13 ACCEPT for the bridge)
# PHASE 4 seam: helpers live in cosmos_dispatch_lanes and are re-exported
# above -- same objects, not copies -- so dispatch() / job_status /
# cosmos_watchdog2 keep working unchanged. Additive.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# attempt-private workspace (P10) -> cosmos_dispatch_workspace (PHASE 4 seam,
# docs/CORE_RESTRUCTURE.md). assert_not_live_workspace / clone_attempt_workspace
# / prepare_grok_workspace / collect_workspace_proposal are re-exported at the
# top of this file, so this module's public surface is unchanged.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# job source (R4: grok flags locked; cursor/claude provisional)
# PHASE 4 seam: builders live in cosmos_dispatch_jobs and are re-exported
# above -- same objects, not copies -- so dispatch() and the grok/cursor/
# claude job files keep working unchanged. Additive.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# stamps, DHx, collector index (R5 ACCEPT, R6 lock ` · `, R7 sidecar+lock)
# PHASE 4 seam: helpers live in cosmos_dispatch_stamps and are re-exported
# above -- same objects, not copies -- so dispatch() / job_status /
# cosmos_node_worker / cosmos_dispatcher_daemon keep working unchanged.
# Additive.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# stage-5 critic visibility: inline disposed bodies, not paths the rail
# cannot open (measured 2026-08-27T15:10).
# PHASE 4 seam: inliners live in cosmos_dispatch_critique and are re-exported
# above -- same objects, not copies -- so dispatch() and the OA/GEM critic
# payload keep working unchanged. Additive.
# ---------------------------------------------------------------------------


def _cursor_key_path(paths: CosmosPaths) -> Path:
    return paths.config(CURSOR_KEY_NAME)


def _codex_key_path(paths: CosmosPaths) -> Path:
    return paths.config(OPENAI_KEY_NAME)


def _native_submit(paths: CosmosPaths, command: str, timeout_s: int,
                   lane: str) -> str:
    """Client of Scheduler — does not modify sched source. One ledger writer."""
    from cosmos_sched import Scheduler
    keyfile = paths.config("install_key.bin")
    if not keyfile.exists():
        raise DispatchError(
            "NO_KEY",
            f"no install key at {keyfile} - native queue submit refuses rather "
            f"than inventing a second writer")
    key = keyfile.read_bytes()
    q = paths.role("queue")
    q.mkdir(parents=True, exist_ok=True)
    (q / "manifests").mkdir(parents=True, exist_ok=True)
    sched = Scheduler(q, key, WORKER)
    return sched.submit(command, priority="normal",
                        timeout_s=int(timeout_s), lane=lane)


def _write_mapping(paths: CosmosPaths, filename: str, rec: dict) -> Path:
    p = dispatch_map_path(paths, filename)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    tmp.replace(p)
    return p


def _read_mapping(paths: CosmosPaths, filename: str) -> dict | None:
    p = dispatch_map_path(paths, filename)
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) else None


def _load_json(path: Path) -> dict | None:
    if path is None or not path.exists():
        return None
    try:
        d = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) else None


def _mtime(path: Path | None) -> float | None:
    if path is None:
        return None
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def _result_is_stale(result_path: Path | None, job_path: Path | None) -> bool:
    """M5: a leftover result older than the job file is not this attempt."""
    rm = _mtime(result_path)
    jm = _mtime(job_path)
    if rm is None or jm is None:
        return False
    return rm + 0.05 < jm


# ---------------------------------------------------------------------------
# monitor (R8 ACCEPT pull; REJECT blocking wait as the default)
# ---------------------------------------------------------------------------

def job_status(filename, *, queue=None, runtime_root=None, paths=None) -> dict:
    """Monitor a dispatched job. Never claims done without a fresh result or
    a done/failed bucket (M5: leftover result json is not terminal)."""
    name = Path(filename).name
    bound = None
    if paths is not None:
        bound = paths
    elif runtime_root is not None:
        try:
            bound = bind_paths(runtime_root)
        except DispatchError:
            bound = None
    else:
        try:
            bound = bind_paths(None)
        except DispatchError:
            bound = None

    q = None
    if queue is not None:
        q = Path(queue)
    elif bound is not None:
        q = bound.role("queue")

    native = bool(bound is not None and q is not None and is_native_queue(q, bound))
    mapping = _read_mapping(bound, name) if bound is not None else None

    loc = locate_job(q, name) if q is not None else {
        "path": None, "lane": None, "state": "missing", "bucket": None,
        "filename": name,
    }
    lane = loc["lane"]
    state = loc["state"]
    job_path = loc["path"]
    if mapping and mapping.get("script_path"):
        sp = Path(mapping["script_path"])
        if sp.exists() and job_path is None:
            job_path = sp
            lane = mapping.get("stream") or NATIVE_STREAM
            state = "queued"

    result_name = name.rsplit("__t", 1)[0] + "_result.json" if "__t" in name else (
        name.rsplit(".", 1)[0] + "_result.json")
    candidates: list[Path] = []
    returns_path = None
    if mapping:
        if mapping.get("returns_path"):
            candidates.append(Path(mapping["returns_path"]))
        if mapping.get("result_path"):
            candidates.append(Path(mapping["result_path"]))
    if bound is not None:
        stream = (mapping or {}).get("stream") or STREAM_FOR_LANE.get(lane or "", NATIVE_STREAM)
        candidates.append(locked_returns_path(bound, stream, result_name))
        work = bound.role("work")
        jid = (mapping or {}).get("job_id")
        if jid:
            wdir = work / jid
            if wdir.exists():
                for child in sorted(wdir.glob("*/result.json"),
                                    key=lambda p: p.stat().st_mtime, reverse=True):
                    candidates.append(child)
    if q is not None and lane:
        dest = _lane_dir(q, lane) if lane in LANE_ORDER else q
        candidates.append(dest / result_name)
        candidates.append(returns_dir(dest) / result_name)

    result_path = None
    result = None
    seen = set()
    for p in candidates:
        rp = str(p)
        if rp in seen:
            continue
        seen.add(rp)
        if not p.exists():
            continue
        if _result_is_stale(p, job_path):
            continue
        if result_path is None:
            result_path = p
            result = _load_json(p)
        if "returns" in p.parts:
            returns_path = p
            if result is None:
                result = _load_json(p)

    stalled = False
    queued_age_s = None
    if mapping and mapping.get("submitted"):
        queued_age_s = time.time() - float(mapping["submitted"])
        timeout_s = float(mapping.get("timeout_s") or GROK_TIMEOUT_S)
        if state in ("queued", "missing") and result is None:
            if queued_age_s > timeout_s * STALL_RATIO:
                stalled = True
                state = "STALLED"

    # native work dir can show running even when locate_job said missing
    if native and mapping and mapping.get("job_id") and bound is not None:
        wdir = bound.role("work") / mapping["job_id"]
        if wdir.exists() and result is None:
            logs = list(wdir.glob("*/attempt.log"))
            if logs and state in ("queued", "missing"):
                state = "running"
        if result is not None and isinstance(result, dict) and result.get("outcome"):
            oc = result.get("outcome")
            if oc == "BROKE":
                state = "failed"
            elif oc in ("CLEAN", "FINDINGS"):
                state = "done"
        elif result is not None and state in ("queued", "missing", "running"):
            # job script wrote returns; runner may still be in the process
            if result.get("rc") is not None or result.get("live_tree_id"):
                if result.get("rc") is not None:
                    state = "done" if result.get("rc") == 0 else "failed"

    kind_of = None
    if isinstance(result, dict):
        kind_of = result.get("kind")
    if not kind_of and mapping:
        kind_of = mapping.get("kind")

    terminal = False
    if state in ("done", "failed"):
        terminal = True
    elif result is not None and not _result_is_stale(result_path, job_path):
        if state not in ("queued", "STALLED"):
            terminal = True
        elif result.get("rc") is not None or result.get("outcome"):
            terminal = True

    # Handoff packet drop is assignment, not the agent's return. A runner
    # CLEAN on the drop script (or a leftover rc=0) is not vendor-plural
    # critique landing (SCAR_PLACATION / MOTIF_TRACKER critique-rail gap).
    if kind_of in WORKER_KINDS and isinstance(result, dict):
        worker_landed = bool(
            result.get("worker_result")
            or result.get("stdout_tail")
            or result.get("kind_live") not in ("handoff", None, "")
        )
        if result.get("kind_live") == "handoff" and not worker_landed:
            terminal = False
            if state in ("done", "failed", "queued", "missing", "running"):
                state = "handoff"

    rec = {
        "ok": True,
        "filename": name,
        "state": state,
        "lane": lane or ((mapping or {}).get("stream")),
        "job_path": str(job_path) if job_path is not None else None,
        "result_path": str(result_path) if result_path is not None else None,
        "returns_path": str(returns_path) if returns_path is not None else (
            (mapping or {}).get("returns_path")),
        "rc": (result.get("rc") if isinstance(result, dict) else None),
        "result": result,
        "terminal": terminal,
        "stalled": stalled,
        "queued_age_s": None if queued_age_s is None else round(queued_age_s, 1),
        "native": native,
        "native_job_id": (mapping or {}).get("job_id"),
        "queue": str(q) if q is not None else None,
    }
    if bound is not None and terminal and result is not None:
        rec["collector"] = reconcile_return(
            rec, paths=bound, index_path=index_path_for(bound))
    return rec


def wait_for(filename, *, queue=None, runtime_root=None,
             timeout_s: float = 1800, poll_s: float = 5.0) -> dict:
    """Poll job_status until terminal or timeout. OS-cheap; not a Claude loop."""
    deadline = time.time() + float(timeout_s)
    last = None
    while time.time() < deadline:
        last = job_status(filename, queue=queue, runtime_root=runtime_root)
        if last.get("terminal"):
            last["wait"] = "landed"
            return last
        time.sleep(max(0.2, float(poll_s)))
    last = last or job_status(filename, queue=queue, runtime_root=runtime_root)
    last["wait"] = "timeout"
    last["terminal"] = False
    return last


def reconcile_return(status: dict, *, paths: CosmosPaths,
                     index_path: Path) -> dict:
    """Join a terminal result onto the collector index (H2). Append-only."""
    result = status.get("result") if isinstance(status.get("result"), dict) else {}
    artifact = status.get("job_path") or status.get("returns_path")
    if not artifact:
        return {"wrote": False, "reason": "no artifact"}
    existing = _latest_for_job(index_path, artifact=artifact,
                               job_file=status.get("filename"))
    if existing and existing.get("status") in ("returned", "MISSING"):
        return {"wrote": False, "reason": "already joined", "row": existing}
    now = time.time()
    row = {
        "schema": SCHEMA,
        "collected_at": datetime.fromtimestamp(now).astimezone().isoformat(
            timespec="seconds"),
        "collected_epoch": int(now),
        "source": "dispatch_return",
        "lane": status.get("lane"),
        "agent": result.get("agent") or (existing or {}).get("agent"),
        "maker": (existing or {}).get("maker") or KIND_MAKER.get(
            str(result.get("kind") or ""), ""),
        "app": (existing or {}).get("app"),
        "task": (existing or {}).get("task") or status.get("filename"),
        "status": "returned" if (
            result.get("rc") == 0 or result.get("outcome") in ("CLEAN", "FINDINGS")
            or result.get("live_tree_id")
        ) else "MISSING",
        "rc": result.get("rc"),
        "artifact": artifact,
        "mtime": float(_mtime(Path(status["returns_path"])) or now)
            if status.get("returns_path") else now,
        "mtime_iso": datetime.fromtimestamp(now).astimezone().isoformat(
            timespec="seconds"),
        "summary": _oneline(
            f"return {status.get('filename')} state={status.get('state')} "
            f"tree_id={result.get('live_tree_id')}"),
        "bytes": 0,
        "kind": result.get("kind") or (existing or {}).get("kind"),
        "job_file": status.get("filename"),
        "result_path": status.get("result_path"),
        "returns_path": status.get("returns_path"),
        "stream": status.get("lane"),
        "native_job_id": status.get("native_job_id"),
        "live_tree_id": result.get("live_tree_id"),
        "stdout_tail": (result.get("stdout_tail") or "")[:400],
        "outcome": result.get("outcome"),
    }
    try:
        if status.get("returns_path") and Path(status["returns_path"]).exists():
            row["bytes"] = Path(status["returns_path"]).stat().st_size
    except OSError:
        pass
    rec = append_index_row(index_path, row, lock_path=index_lock_for(paths))
    inbox = inbox_dir(paths) / (
        Path(status.get("filename") or "return").stem + "_return.json")
    write_inbox_sidecar(inbox, row)
    rec["inbox"] = str(inbox)
    return rec


# ---------------------------------------------------------------------------
# dispatch (R10: TYPE+task only; dir/queue defaulted)
# ---------------------------------------------------------------------------

def dispatch(agent, task, target_dir=None, lane=None, model=DEFAULT_MODEL,
             kind=None, *, queue=None, runtime_root=None, dhx=None,
             index_path=None, label=None):
    """Create + assign + stamp + register. One call.

    target_dir and queue are optional: default dir is the repo tree of the
    install; default queue is the resolver `queue` role. Explicit `--queue`
    is the BTS compatibility ingress, never identity.

    label: optional short assignment for the DHx marker and job filename
    (the grok/cursor/claude payload is still `task`, which may carry
    context + the AGENT_BOUNDARIES addendum).
    """
    task = str(task or "").strip()
    if not task:
        raise DispatchError("BAD_INPUT", "task is required")
    agent = str(agent or "").strip()
    if not agent:
        agent = infer_default_agent(task)
    label_s = str(label or "").strip() or task
    kind_c = resolve_kind(agent, kind)
    if kind_c in CLAUDE_KINDS:
        raise DispatchError(
            "ANTHROPIC_OFF",
            "Keith 2026-09-01: Anthropic is off the route — no claude -p, "
            "F5, Sonnet, or Haiku. SSA/subagent remaps to groq "
            "(gpt-oss-20b). Drop G46/Cursor/GEM/OA/groq instead.")
    paths = bind_paths(runtime_root)
    oa_pause = paths.role("state", "control", "OA_PAUSE.flag")
    if kind_c in ("oa",) and oa_pause.is_file():
        raise DispatchError(
            "OA_PAUSED",
            "Keith 2026-09-04: oa-api account lane paused after ~$150 "
            "poll-daemon burn. HOLD lift does not re-enable this lane.")
    model = resolve_lane_model(kind_c, model)
    if target_dir in (None, ""):
        target = default_target_dir(paths)
    else:
        target = Path(target_dir)
    try:
        target = target.resolve()
    except OSError as e:
        raise DispatchError("NO_DIR", f"target_dir unreadable: {target}: {e}") from e
    if not target.exists() or not target.is_dir():
        raise DispatchError("NO_DIR", f"target_dir is not a directory: {target}")

    # Remote critic rails (gem/oa) have no filesystem. A path-only stage-5
    # prompt is a blind critique. Inline disposed bodies into the payload.
    if kind_c in WORKER_KINDS and _is_critique_task(task):
        built = compose_critique_prompt(
            task, tree=target, propose_dir=Path(target) / "_propose")
        if built.get("inlined"):
            task = built["prompt"]

    if queue is None:
        q = paths.role("queue")
        q.mkdir(parents=True, exist_ok=True)
        native = True
    else:
        q = Path(queue)
        if not q.exists():
            raise DispatchError("NO_QUEUE", f"queue does not exist: {q}")
        native = is_native_queue(q, paths)

    dhx_path = Path(dhx) if dhx is not None else default_dhx(paths)
    idx = (Path(index_path) if index_path is not None else index_path_for(paths))
    lock_p = idx.with_name(INDEX_LOCK_NAME) if index_path is not None else index_lock_for(paths)

    lane_forced = lane is not None
    if native:
        chosen = NATIVE_STREAM if lane is None else str(lane).strip().lower()
        if chosen in ("", "(root)", "root"):
            chosen = NATIVE_STREAM
        stream = STREAM_FOR_LANE.get(chosen, chosen)
    else:
        if lane is None:
            chosen = pick_least_loaded(q)
        else:
            chosen = str(lane).strip().lower()
            if chosen in ("", "(root)"):
                chosen = "root"
            if chosen not in LANE_ORDER:
                raise DispatchError("NO_LANE",
                                    f"unknown lane {lane!r}; want root|lg|pb")
        stream = STREAM_FOR_LANE.get(chosen, chosen)

    timeout_s = _timeout_for(kind_c)
    filename = job_filename(agent, kind_c, label_s, str(target), timeout_s)
    result_name = filename.rsplit("__t", 1)[0] + "_result.json"
    sentinel_path = paths.root / SENTINEL_NAME
    inbox_path = inbox_dir(paths) / (filename.rsplit(".", 1)[0] + ".json")
    locked_ret = locked_returns_path(paths, stream, result_name)

    existing_map = _read_mapping(paths, filename)
    if existing_map and existing_map.get("job_id"):
        stamp = existing_map.get("stamp") or _iso_now()
        marker = _marker_line(stamp, agent, label_s,
                              existing_map.get("stream") or chosen, filename)
        dhx_rec = append_dhx_marker(dhx_path, marker)
        st = job_status(filename, queue=q, runtime_root=paths.root, paths=paths)
        return {
            "ok": True,
            "created": False,
            "idempotent": True,
            "agent": agent,
            "kind": kind_c,
            "kind_inferred": kind in (None, "", "auto"),
            "kind_live": KIND_LIVE.get(kind_c, "UNPROVEN"),
            "model": model,
            "lane": existing_map.get("stream") or chosen,
            "stream": existing_map.get("stream") or stream,
            "lane_forced": lane_forced,
            "lane_loads": {},
            "job_path": existing_map.get("script_path"),
            "job_file": filename,
            "result_path": existing_map.get("result_path"),
            "returns_path": existing_map.get("returns_path"),
            "target_dir": str(target),
            "workspace_policy": "attempt-private" if kind_c == "grok" else None,
            "timeout_s": timeout_s,
            "stamp": stamp,
            "marker": marker,
            "dhx": dhx_rec,
            "collector": {"wrote": False, "path": str(idx), "reason": "idempotent"},
            "index": str(idx),
            "queue": str(q),
            "queue_identity": "native" if native else "bootstrap",
            "native": native,
            "native_job_id": existing_map.get("job_id"),
            "status": st,
        }

    key_path = None
    if kind_c == "cursor":
        key_path = _cursor_key_path(paths)
        if not key_path.exists():
            raise DispatchError(
                "NO_KEY",
                f"Cursor COSMOS key missing at {key_path} "
                f"(never hard-code; redact to crsr_…last4)")
    if kind_c == "codex":
        key_path = _codex_key_path(paths)
        if not key_path.exists():
            raise DispatchError(
                "NO_KEY",
                f"OpenAI key missing at {key_path} "
                f"(never hard-code; redact to sk-…last4)")

    worker_dir = None
    compat_dir = None
    out_dir = None
    if kind_c in WORKER_KINDS:
        worker_dir = worker_bucket_dir(paths, kind_c)
        worker_dir.mkdir(parents=True, exist_ok=True)
        (worker_dir / "processed").mkdir(exist_ok=True)
        (worker_dir / "failed").mkdir(exist_ok=True)
        compat_dir = worker_compat_dir(paths, kind_c)
        compat_dir.mkdir(parents=True, exist_ok=True)
        try:
            out_dir = paths.role(
                "root", "returns", WORKER_BUCKET_NODE.get(kind_c, kind_c))
        except CosmosPathError:
            out_dir = None

    created = False
    native_job_id = None
    job_path: Path
    result_path: Path
    returns_path: Path

    if native:
        script_dir = paths.role("tools", "dispatch_jobs")
        script_dir.mkdir(parents=True, exist_ok=True)
        job_path = script_dir / filename
        result_path = locked_ret
        returns_path = locked_ret
        source = render_job(kind_c, agent, task, str(target), model,
                            result_path, returns_path, timeout_s, key_path,
                            inbox_path=inbox_path, sentinel_path=sentinel_path,
                            worker_dir=worker_dir, runtime_root=paths.root,
                            out_dir=out_dir, compat_dir=compat_dir,
                            attempt_id=filename.rsplit(".", 1)[0])
        created = _write_exclusive(job_path, source)
        if not created and not job_path.exists():
            job_path.write_text(source, encoding="utf-8")
            created = True
        elif not created:
            # reuse existing script (idempotent name)
            pass
        command = "py:" + str(job_path)
        native_job_id = _native_submit(paths, command, timeout_s, stream)
        rec_map = {
            "job_id": native_job_id,
            "filename": filename,
            "script_path": str(job_path),
            "returns_path": str(returns_path),
            "result_path": str(result_path),
            "stream": stream,
            "timeout_s": timeout_s,
            "submitted": time.time(),
            "stamp": _iso_now(),
            "agent": agent,
            "kind": kind_c,
            "task": task,
            "target_dir": str(target),
            "workspace_policy": "attempt-private" if kind_c == "grok" else None,
        }
        _write_mapping(paths, filename, rec_map)
        landed = stream
    else:
        dest_dir = _lane_dir(q, chosen)
        dest_dir.mkdir(parents=True, exist_ok=True)
        for sub in ("running", "done", "failed", "logs"):
            (dest_dir / sub).mkdir(parents=True, exist_ok=True)
        ret_dir = returns_dir(dest_dir)
        ret_dir.mkdir(parents=True, exist_ok=True)
        existing = _find_existing(q, filename)
        job_path = existing if existing is not None else (dest_dir / filename)
        result_path = dest_dir / result_name
        returns_path = ret_dir / result_name
        if existing is None:
            source = render_job(kind_c, agent, task, str(target), model,
                                result_path, returns_path, timeout_s, key_path,
                                inbox_path=inbox_path, sentinel_path=sentinel_path,
                                worker_dir=worker_dir, runtime_root=paths.root,
                                out_dir=out_dir, compat_dir=compat_dir,
                                attempt_id=filename.rsplit(".", 1)[0])
            created = _write_exclusive(job_path, source)
            if not created:
                existing = job_path if job_path.exists() else _find_existing(q, filename)
                job_path = existing or job_path
        landed = _lane_of_path(job_path, q) if job_path.exists() else chosen
        if landed != chosen:
            dest_dir = _lane_dir(q, landed)
            result_path = dest_dir / result_name
            returns_path = returns_dir(dest_dir) / result_name
            stream = STREAM_FOR_LANE.get(landed, landed)
        rec_map = {
            "job_id": None,
            "filename": filename,
            "script_path": str(job_path),
            "returns_path": str(returns_path),
            "result_path": str(result_path),
            "stream": stream,
            "timeout_s": timeout_s,
            "submitted": time.time(),
            "stamp": _iso_now(),
            "agent": agent,
            "kind": kind_c,
            "task": task,
            "target_dir": str(target),
            "workspace_policy": "attempt-private" if kind_c == "grok" else None,
            "bootstrap": True,
        }
        _write_mapping(paths, filename, rec_map)

    stamp = (rec_map.get("stamp") if native else _iso_now())
    if not native:
        stamp = rec_map["stamp"] = _iso_now()
        _write_mapping(paths, filename, rec_map)
    marker = _marker_line(stamp, agent, label_s, landed, filename)
    dhx_rec = append_dhx_marker(dhx_path, marker)

    try:
        mtime = job_path.stat().st_mtime
        nbytes = job_path.stat().st_size
    except OSError:
        mtime = time.time()
        nbytes = 0
    now = time.time()
    row = {
        "schema": SCHEMA,
        "collected_at": datetime.fromtimestamp(now).astimezone().isoformat(
            timespec="seconds"),
        "collected_epoch": int(now),
        "source": "dispatch_assignment",
        "lane": landed,
        "agent": agent,
        "maker": KIND_MAKER[kind_c],
        "app": KIND_MAKER[kind_c],
        "task": filename.rsplit("__t", 1)[0],
        "status": "assigned",
        "rc": None,
        "artifact": str(job_path),
        "mtime": float(mtime),
        "mtime_iso": datetime.fromtimestamp(mtime).astimezone().isoformat(
            timespec="seconds"),
        "summary": _oneline(
            f"dispatched {kind_c} {agent} -> {landed}/{filename}"),
        "bytes": int(nbytes),
        "kind": kind_c,
        "kind_live": KIND_LIVE.get(kind_c, "UNPROVEN"),
        "model": model,
        "stamp": stamp,
        "result_path": str(result_path),
        "returns_path": str(returns_path),
        "locked_returns": str(locked_ret),
        "stream": stream,
        "target_dir": str(target),
        "workspace_policy": "attempt-private" if kind_c == "grok" else None,
        "timeout_s": timeout_s,
        "job_file": filename,
        "native": native,
        "native_job_id": native_job_id,
        "queue_identity": "native" if native else "bootstrap",
        "inbox_path": str(inbox_path),
        "worker_bucket": str(worker_dir) if worker_dir is not None else None,
        "worker_compat": str(compat_dir) if compat_dir is not None else None,
    }
    idx_rec = append_assignment_row(idx, row, lock_path=lock_p)
    write_inbox_sidecar(inbox_path, row)

    loads = {} if native else measure_lanes(q)
    return {
        "ok": True,
        "created": created,
        "idempotent": not created,
        "agent": agent,
        "kind": kind_c,
        "kind_inferred": kind in (None, "", "auto"),
        "kind_live": KIND_LIVE.get(kind_c, "UNPROVEN"),
        "model": row["model"],
        "lane": landed,
        "stream": stream,
        "lane_forced": lane_forced,
        "lane_loads": {k: {"queued": v["queued"], "running": v["running"],
                           "load": v["load"]} for k, v in loads.items()},
        "job_path": str(job_path),
        "job_file": filename,
        "result_path": str(result_path),
        "returns_path": str(returns_path),
        "locked_returns": str(locked_ret),
        "target_dir": str(target),
        "workspace_policy": "attempt-private" if kind_c == "grok" else None,
        "timeout_s": timeout_s,
        "stamp": stamp,
        "marker": marker,
        "dhx": dhx_rec,
        "collector": {"wrote": idx_rec["wrote"], "path": idx_rec["path"],
                      "inbox": str(inbox_path)},
        "index": str(idx),
        "queue": str(q),
        "queue_identity": "native" if native else "bootstrap",
        "native": native,
        "native_job_id": native_job_id,
        "worker_bucket": str(worker_dir) if worker_dir is not None else None,
        "worker_compat": str(compat_dir) if compat_dir is not None else None,
        "status": job_status(filename, queue=q, runtime_root=paths.root,
                             paths=paths),
    }


# ---------------------------------------------------------------------------
# stage-6 gate: a value only this live tree can emit
# ---------------------------------------------------------------------------

def _read_heartbeat(paths: CosmosPaths) -> dict | None:
    p = paths.logs("cosmos_runner_heartbeat.json")
    return _load_json(p)


def run_gate(runtime_root=None, timeout_s: float = 180.0) -> dict:
    """Dispatch TYPE+task with no --dir/--queue, wait for the native runner
    to name the job_id, then quote the locked returns live_tree_id."""
    paths = bind_paths(runtime_root)
    t0 = time.time()
    nonce = _iso_now()
    rec = dispatch(
        "G46", GATE_TASK, runtime_root=paths.root,
        label=f"STAGE6_GATE {nonce}",
    )
    proof = {
        "ok": False,
        "stage": 6,
        "deliverable": "cosmos_dispatch",
        "gate_nonce": nonce,
        "dispatched_at": rec.get("stamp"),
        "agent": rec.get("agent"),
        "kind": rec.get("kind"),
        "kind_live": rec.get("kind_live"),
        "queue": rec.get("queue"),
        "queue_identity": rec.get("queue_identity"),
        "native_job_id": rec.get("native_job_id"),
        "job_file": rec.get("job_file"),
        "job_path": rec.get("job_path"),
        "returns_path": rec.get("returns_path"),
        "locked_returns": rec.get("locked_returns"),
        "marker": rec.get("marker"),
        "dhx": rec.get("dhx"),
        "index": rec.get("index"),
        "manifest": None,
        "heartbeat": None,
        "live_tree_id": None,
        "stdout_tail": None,
        "emitted": None,
    }
    jid = rec.get("native_job_id")
    if jid:
        mp = paths.queue("manifests", jid + ".json")
        proof["manifest"] = str(mp) if mp.exists() else None
        proof["manifest_exists"] = mp.exists()

    def _runner_work():
        if not jid:
            return None
        wdir = paths.role("work") / jid
        if not wdir.exists():
            return None
        attempts = [p for p in wdir.iterdir() if p.is_dir()]
        if not attempts:
            return None
        chosen = max(attempts, key=lambda p: p.stat().st_mtime)
        logp = chosen / "attempt.log"
        log = logp.read_text(encoding="utf-8", errors="replace") if logp.exists() else ""
        wres = _load_json(chosen / "result.json")
        return {
            "dir": str(chosen),
            "log": str(logp) if logp.exists() else None,
            "attempt_head": log[:500],
            "worker_is_runner": "worker cosmos-runner" in log,
            "job_id_in_log": bool(jid and jid in log),
            "result": wres,
        }

    deadline = time.time() + float(timeout_s)
    hb_hit = None
    returns = None
    last_status = None
    while time.time() < deadline:
        hb = _read_heartbeat(paths)
        if hb and jid and jid in (hb.get("job_ids") or []):
            hb_hit = hb
        last_status = job_status(rec["job_file"], queue=rec["queue"],
                                 runtime_root=paths.root, paths=paths)
        rp = last_status.get("returns_path") or rec.get("returns_path")
        if rp and Path(rp).exists():
            returns = _load_json(Path(rp))
            if returns and (returns.get("live_tree_id") or returns.get("rc") is not None
                            or returns.get("stdout_tail")):
                if hb_hit or (returns.get("live_tree_id") and last_status.get("terminal")):
                    break
        if hb_hit and last_status and last_status.get("terminal"):
            break
        # durable runner bind: work/<job_id>/<attempt>/attempt.log (heartbeat
        # job_ids is overwritten to [] on the next idle tick)
        if last_status and last_status.get("terminal") and _runner_work():
            break
        time.sleep(1.0)

    if hb_hit is None:
        hb_hit = _read_heartbeat(paths)
    work_proof = _runner_work()
    proof["runner_work"] = work_proof
    proof["heartbeat"] = {
        "path": str(paths.logs("cosmos_runner_heartbeat.json")),
        "last_run": (hb_hit or {}).get("last_run"),
        "last_run_epoch": (hb_hit or {}).get("last_run_epoch"),
        "pid": (hb_hit or {}).get("pid"),
        "queue_root": (hb_hit or {}).get("queue_root"),
        "tick": (hb_hit or {}).get("tick"),
        "jobs_this_tick": (hb_hit or {}).get("jobs_this_tick"),
        "job_ids": (hb_hit or {}).get("job_ids"),
        "named_this_job": bool(jid and jid in ((hb_hit or {}).get("job_ids") or [])),
    }
    proof["status"] = last_status
    if returns:
        proof["live_tree_id"] = returns.get("live_tree_id")
        proof["stdout_tail"] = returns.get("stdout_tail")
        proof["result_rc"] = returns.get("rc")
        proof["result_secs"] = returns.get("secs")
        proof["returns_exists"] = True
    else:
        proof["returns_exists"] = False

    idx_row = _latest_for_job(Path(rec["index"]), artifact=rec.get("job_path"),
                              job_file=rec.get("job_file"))
    proof["index_status"] = (idx_row or {}).get("status")
    proof["index_source"] = (idx_row or {}).get("source")
    proof["index_live_tree_id"] = (idx_row or {}).get("live_tree_id")

    dhx_text = ""
    dhx_path = rec.get("dhx", {}).get("path")
    if dhx_path and Path(dhx_path).exists():
        dhx_text = Path(dhx_path).read_text(encoding="utf-8")
    proof["dhx_has_marker"] = bool(rec.get("marker") and rec["marker"] in dhx_text)
    proof["dhx_grammar_dot"] = bool(rec.get("marker") and MARKER_SEP in rec["marker"])
    proof["no_dir_passed"] = True
    proof["no_queue_passed"] = True
    proof["secs"] = round(time.time() - t0, 1)

    sentinel = _load_json(paths.root / SENTINEL_NAME) or {}
    emitted = {
        "live_tree_id": proof.get("live_tree_id") or sentinel.get("tree_id"),
        "gate_nonce": nonce,
        "native_job_id": jid,
        "heartbeat_named": proof["heartbeat"]["named_this_job"],
        "heartbeat_last_run_epoch": proof["heartbeat"]["last_run_epoch"],
        "runner_work_dir": (work_proof or {}).get("dir"),
        "runner_outcome": ((work_proof or {}).get("result") or {}).get("outcome"),
        "runner_worker": (work_proof or {}).get("worker_is_runner"),
        "returns_path": rec.get("returns_path"),
        "index_status": proof.get("index_status"),
        "stdout_tail": (proof.get("stdout_tail") or "")[:200],
        "stamp": rec.get("stamp"),
    }
    proof["emitted"] = emitted
    runner_bound = bool(
        proof["heartbeat"]["named_this_job"]
        or ((work_proof or {}).get("worker_is_runner")
            and (work_proof or {}).get("job_id_in_log"))
    )
    proof["ok"] = bool(
        rec.get("queue_identity") == "native"
        and rec.get("native_job_id")
        and proof.get("manifest_exists")
        and proof.get("dhx_has_marker")
        and proof.get("dhx_grammar_dot")
        and proof.get("live_tree_id")
        and runner_bound
    )
    outp = paths.state("dispatch", "STAGE6_GATE.json")
    outp.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(proof, indent=1, default=str)
    outp.write_text(body, encoding="utf-8")
    dated_name = "STAGE6_GATE_" + nonce.replace(":", "").replace("+", "p") + ".json"
    dated = paths.state("dispatch", dated_name)
    dated.write_text(body, encoding="utf-8")
    proof["proof_path"] = str(outp)
    proof["proof_path_dated"] = str(dated)
    return proof


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="cosmos_dispatch",
        description="Create an agent job, stamp DHx, register the assignment. "
                    "Kind is inferred from --agent unless --kind is set. "
                    "Default queue is the resolver queue role; --queue is bootstrap.")
    ap.add_argument("--agent", default=None,
                    help="agent TYPE (G46, Cursor, F5, SSA, sonnet, haiku, ...). "
                         "Omitted: coding->G46, research/analysis/vetting->SSA.")
    ap.add_argument("--task", default=None)
    ap.add_argument("--dir", default=None, dest="target_dir",
                    help="working directory (default: repo tree of the install)")
    ap.add_argument("--kind", default="auto",
                    help="auto | grok | cursor | codex | claude | F5 | sonnet | "
                         "haiku | SSA | gem | oa (default: auto from agent)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--lane", default=None,
                    help="BTS: root|lg|pb (default least-loaded). Native: ignored.")
    ap.add_argument("--root", default=None,
                    help="COSMOS runtime root (default: install record)")
    ap.add_argument("--queue", default=None,
                    help="optional bootstrap queue (BTS). Default: resolver queue role.")
    ap.add_argument("--dhx", default=None,
                    help="DHx path (default <repo>/docs/AGENT_BRIEF.md)")
    ap.add_argument("--index", default=None,
                    help="collector index.jsonl (default <root>/state/collector/index.jsonl)")
    ap.add_argument("--status", default=None, metavar="JOBFILE",
                    help="monitor a previously dispatched job (filename or path)")
    ap.add_argument("--wait", action="store_true",
                    help="after dispatch (or with --status), poll until terminal")
    ap.add_argument("--wait-timeout", type=float, default=None,
                    help="seconds to wait (default: the job's own timeout)")
    ap.add_argument("--gate", action="store_true",
                    help="stage-6 runtime-binding: dispatch TYPE+task onto the "
                         "native queue and quote a live-tree value")
    a = ap.parse_args()
    try:
        if a.gate:
            rec = run_gate(runtime_root=a.root,
                           timeout_s=a.wait_timeout or 180.0)
        elif a.status:
            rec = job_status(a.status, queue=a.queue, runtime_root=a.root)
            if a.wait:
                rec = wait_for(
                    a.status, queue=a.queue, runtime_root=a.root,
                    timeout_s=a.wait_timeout or GROK_TIMEOUT_S)
        else:
            if not a.task:
                ap.error("--task is required to dispatch "
                         "(--agent defaults: coding->G46, research->SSA; "
                         "--dir and --queue default)")
            rec = dispatch(
                a.agent or infer_default_agent(a.task), a.task, a.target_dir,
                lane=a.lane, model=a.model,
                kind=a.kind, queue=a.queue, runtime_root=a.root, dhx=a.dhx,
                index_path=a.index,
            )
            if a.wait:
                rec["wait"] = wait_for(
                    rec["job_file"], queue=rec["queue"], runtime_root=a.root,
                    timeout_s=a.wait_timeout or rec.get("timeout_s") or GROK_TIMEOUT_S)
    except DispatchError as e:
        print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)}, indent=1))
        return 2
    print(json.dumps(rec, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
