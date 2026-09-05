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
  sonnet / SSA -> claude -p <task> --model sonnet --permission-mode dontAsk
            --add-dir <dir>   UNPROVEN through this harness
            SSA = Sonnet SubAgent; RESEARCH/ANALYSIS/vetting default
  haiku  -> claude -p <task> --model haiku --permission-mode dontAsk
            --add-dir <dir>   UNPROVEN through this harness

Defaults (two, kept distinct -- DHx: coding never Sonnet):
  coding -> G46 / grok-4.6 (Cursor is the other coding lane)
  research / analysis / vetting / subagent -> SSA / sonnet
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

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
    "ssa": "ssa",
    "subagent": "ssa",
    "sonnetsubagent": "ssa",
}

# Agent TYPE -> kind. Longest alnum-folded key wins. Explicit --kind overrides.
# Spec tags: G46/GW/SGH/GEM/OAi/CURSOR/SSA/SONNET/HAIKU.
# SSA = Sonnet SubAgent (first-class); --agent sonnet/haiku are Claude CLI lanes.
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
    "ssa": "ssa",
    "subagent": "ssa",
    "sonnetsubagent": "ssa",
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
    "gem": "Gemini", "oa": "OpenAI", "ssa": "SSA",
}
# grok is live-proven through this harness. cursor/claude-family are
# string-matched only. gem/oa drop onto live/buckets/<node> AND spawn
# that node's rail (execute_handoff). Packet-and-exit rc=0 was the scar
# (docs/SCAR_PLACATION.md: OA fa6c68cc rc=0 secs=0.0, empty critique).
# SSA is a first-class Claude-CLI kind (Sonnet 5), not a bucket handoff.
KIND_LIVE = {
    "grok": "proven", "cursor": "UNPROVEN", "codex": "UNPROVEN",
    "claude": "UNPROVEN", "sonnet": "UNPROVEN", "haiku": "UNPROVEN",
    "ssa": "UNPROVEN",
    "gem": "handoff", "oa": "handoff",
}
WORKER_KINDS = frozenset({"gem", "oa"})
CLAUDE_KINDS = frozenset({"claude", "sonnet", "haiku", "ssa"})
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
SSA_MODEL = SONNET_MODEL          # SSA = Sonnet SubAgent
CURSOR_BASE = "https://api.cursor.com"
CURSOR_REPO = "https://github.com/keithbbf-gif/cosmos"
CURSOR_REF = "main"
DEFAULT_MODEL = "grok-4.6"        # CODING default; never Sonnet
CODING_DEFAULT_AGENT = "G46"
RESEARCH_DEFAULT_AGENT = "SSA"
STALL_RATIO = 0.5
PROPOSAL_DIFF_CAP = 120_000
GROK_WORK_LANE = "grok"
CLONE_IGNORE = (
    "__pycache__", ".venv", "live", "tmp", "_delme",
    "node_modules", ".grok",
)
_CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

# Lane -> CLI model id. Cursor/codex honor an explicit --model.
KIND_MODEL = {
    "grok": DEFAULT_MODEL,
    "claude": CLAUDE_MODEL,
    "sonnet": SONNET_MODEL,
    "haiku": HAIKU_MODEL,
    "ssa": SSA_MODEL,
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


class DispatchError(RuntimeError):
    """Typed refusal. `kind` is BAD_INPUT, NO_LANE, NO_DIR, NO_KEY, NO_ROOT,
    NO_QUEUE, IO, REFUSED, BROKE."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


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
                            f"claude|F5|sonnet|haiku|gem|oa|ssa")
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
            f"kind=grok|cursor|codex|claude|sonnet|haiku|gem|oa|ssa")
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
    if kind in ("gem", "oa"):
        return GROK_TIMEOUT_S
    if kind in WORKER_KINDS:  # unused while WORKER_KINDS == {gem, oa}
        return GROK_TIMEOUT_S
    return GROK_TIMEOUT_S


# ---------------------------------------------------------------------------
# BTS compatibility lane accounting (R13 ACCEPT for the bridge)
# ---------------------------------------------------------------------------

def _lane_dir(queue: Path, lane: str) -> Path:
    if lane in ("root", "cm", ""):
        return Path(queue)
    return Path(queue) / "_lanes" / lane


def _is_runnable(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in RUNNABLE_SUFFIXES


def _is_helper(path: Path) -> bool:
    return path.name.startswith("_")


def lane_load(lane_dir: Path) -> dict:
    """Count running + queued the way bts_runner --lanes does.

    queued = runnable non-helper files sitting in the lane root (not subdirs).
    running = anything in running/.
    """
    queued = 0
    if lane_dir.exists():
        for p in lane_dir.iterdir():
            if p.name in SKIP_COUNT_NAMES or p.name.startswith("."):
                continue
            if _is_runnable(p) and not _is_helper(p):
                queued += 1
    running_dir = lane_dir / "running"
    running = 0
    if running_dir.exists():
        running = sum(1 for p in running_dir.iterdir()
                      if p.is_file() and not p.name.startswith("."))
    return {"queued": queued, "running": running,
            "load": queued + running, "dir": str(lane_dir)}


def measure_lanes(queue: Path) -> dict:
    out = {}
    for name in LANE_ORDER:
        d = _lane_dir(queue, name)
        rec = lane_load(d)
        rec["lane"] = name
        out[name] = rec
    return out


def pick_least_loaded(queue: Path) -> str:
    """Lowest running+queued. Tie -> first in LANE_ORDER (root, lg, pb)."""
    loads = measure_lanes(queue)
    best = None
    best_n = None
    for name in LANE_ORDER:
        n = int(loads[name]["load"])
        if best_n is None or n < best_n:
            best, best_n = name, n
    return best


def job_filename(agent: str, kind: str, task: str, target_dir: str,
                 timeout_s: int) -> str:
    """Deterministic name: same inputs -> same file. Never `_`-prefixed."""
    agent_s = _slug(agent, 16)
    kind_s = _slug(kind, 12)
    task_s = _slug(task, 36)
    digest = hashlib.sha256(
        f"{agent}\0{kind}\0{task}\0{target_dir}".encode("utf-8")
    ).hexdigest()[:8]
    name = f"{agent_s}_{kind_s}_{task_s}_{digest}__t{int(timeout_s)}.py"
    if name.startswith("_"):
        name = "j" + name
    return name


def _write_exclusive(path: Path, text: str) -> bool:
    """True if created. False if the name already existed (idempotent)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    try:
        fd = os.open(str(path), flags, 0o644)
    except FileExistsError:
        return False
    try:
        os.write(fd, text.encode("utf-8"))
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        raise
    else:
        os.close(fd)
    return True


def _find_existing(queue: Path, filename: str) -> Path | None:
    loc = locate_job(queue, filename)
    return loc["path"]


def locate_job(queue: Path, filename: str) -> dict:
    """Find a job file across BTS lanes/buckets. state is queued|running|done|failed|missing."""
    name = Path(filename).name
    searches = (
        ("queued", ""),
        ("running", "running"),
        ("done", "done"),
        ("done", str(Path("done") / "findings")),
        ("failed", "failed"),
    )
    for lane in LANE_ORDER:
        base = _lane_dir(queue, lane)
        for state, rel in searches:
            p = base / name if not rel else base / rel / name
            if p.exists():
                return {"path": p, "lane": lane, "state": state,
                        "bucket": rel or ".", "filename": name}
    # native record copies (queue/jobs, tools/dispatch_jobs) are not BTS buckets
    for rel in ("jobs", Path("jobs") / "running"):
        p = Path(queue) / rel / name if not isinstance(rel, Path) else Path(queue) / rel / name
        # the loop above already covers simple names; extra native dirs:
    native_job = Path(queue) / "jobs" / name
    if native_job.exists():
        return {"path": native_job, "lane": NATIVE_STREAM, "state": "queued",
                "bucket": "jobs", "filename": name}
    return {"path": None, "lane": None, "state": "missing",
            "bucket": None, "filename": name}


def _lane_of_path(job_path: Path, queue: Path) -> str:
    """Identity via Path.parts, not a substring of the Windows path text (L2)."""
    parts = [p.lower() for p in Path(job_path).parts]
    for i, p in enumerate(parts):
        if p == "_lanes" and i + 1 < len(parts):
            return parts[i + 1]
    if "jobs" in parts or "dispatch_jobs" in parts:
        return NATIVE_STREAM
    return "root"


def returns_dir(lane_dir: Path) -> Path:
    """BTS compatibility copy: the lane IS the stream; results land in returns/."""
    return Path(lane_dir) / "returns"


# ---------------------------------------------------------------------------
# attempt-private workspace (P10: grok/G46 never writes the live tree)
# Mirrors cosmos_codex_rail._prepare_workspace: git clone --local, copytree
# fallback, refuse the live runtime root except work/, refuse the source
# repo tree. Clone failure is BROKE — never fall back to the live tree as cwd.
# ---------------------------------------------------------------------------

def _safe_attempt_id(raw) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", str(raw or "").strip())[:80].strip("._-")
    return s or f"grok-{int(time.time())}"


def _as_resolved(path) -> Path:
    return Path(path).resolve()


def assert_not_live_workspace(workspace, *, live_root=None,
                              source_tree=None) -> None:
    """Refuse a workspace that is the live repo tree or the runtime root
    outside work/. Allowed: under <live>/work/, or wholly outside both trees.
    OSError on resolve is fail-closed (REFUSED), not a pass.
    """
    try:
        ws = _as_resolved(workspace)
    except OSError as e:
        raise DispatchError(
            "REFUSED", f"workspace unreadable: {workspace}: {e}") from e

    if source_tree not in (None, ""):
        try:
            src = _as_resolved(source_tree)
        except OSError as e:
            raise DispatchError(
                "REFUSED", f"source_tree unreadable: {source_tree}: {e}") from e
        try:
            ws.relative_to(src)
        except ValueError:
            pass
        else:
            allowed = False
            if live_root not in (None, ""):
                try:
                    work = (_as_resolved(live_root) / "work")
                    ws.relative_to(work)
                    allowed = True
                except (OSError, ValueError):
                    allowed = False
            if not allowed:
                raise DispatchError(
                    "REFUSED",
                    "coder refuses the live repo tree; attempt-private clone "
                    "only (fenced commit gateway; COW writes the tree)")

    if live_root not in (None, ""):
        try:
            root = _as_resolved(live_root)
            work = (root / "work")
        except OSError as e:
            raise DispatchError(
                "REFUSED", f"live_root unreadable: {live_root}: {e}") from e
        try:
            ws.relative_to(root)
        except ValueError:
            return
        try:
            ws.relative_to(work)
            return
        except ValueError:
            raise DispatchError(
                "REFUSED",
                "coder refuses the live runtime root; attempt-private "
                "clone only under work/ (fenced commit gateway)")


def clone_attempt_workspace(src: Path, dest: Path) -> dict:
    """git clone --local, then copytree fallback. Never deletes dest."""
    src = Path(src)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    argv = ["git", "clone", "--local", str(src), str(dest)]
    t0 = time.time()
    try:
        p = subprocess.run(
            argv, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=120, shell=False,
            creationflags=_CREATE_NO_WINDOW)
        timed_out = False
        rc, err = p.returncode, (p.stderr or "")
    except subprocess.TimeoutExpired as e:
        timed_out = True
        rc = None
        err = (e.stderr if isinstance(e.stderr, str) else "") or "TIMEOUT"
    except FileNotFoundError as e:
        timed_out = False
        rc = -1
        err = f"FileNotFoundError: {e}"
    except Exception as e:  # noqa: BLE001
        timed_out = False
        rc = -1
        err = f"{type(e).__name__}: {e}"
    elapsed = round(time.time() - t0, 1)
    if not timed_out and rc == 0:
        return {"ok": True, "how": "git-clone-local", "rc": 0,
                "workspace": str(dest), "elapsed_s": elapsed}

    copy_dest = dest
    if dest.exists():
        # git may have left a partial dest; never unlink. Pick a sibling.
        n = 0
        while True:
            n += 1
            cand = dest.parent / f"{dest.name}-copy{n}"
            if not cand.exists():
                copy_dest = cand
                break
    try:
        shutil.copytree(
            src, copy_dest,
            ignore=shutil.ignore_patterns(*CLONE_IGNORE),
        )
        return {"ok": True, "how": "copytree", "rc": rc,
                "workspace": str(copy_dest),
                "clone_err": (err or "")[:200],
                "elapsed_s": elapsed}
    except OSError as e:
        return {"ok": False, "how": "copytree",
                "err": f"{type(e).__name__}: {e}",
                "clone_err": (err or "")[:200],
                "rc": rc, "timed_out": timed_out}


def prepare_grok_workspace(source, *, live_root=None, attempt_id=None,
                           dest=None) -> tuple:
    """Clone `source` into an attempt-private dir. Fail-closed: REFUSED/BROKE
    rather than returning the live tree as cwd.
    """
    if source in (None, ""):
        raise DispatchError("BROKE", "coder needs a source tree to clone")
    src = Path(source)
    if not src.exists() or not src.is_dir():
        raise DispatchError("BROKE", f"clone source is not a directory: {src}")
    if live_root not in (None, ""):
        try:
            src_r = _as_resolved(src)
            root = _as_resolved(live_root)
        except OSError as e:
            raise DispatchError("BROKE", f"unreadable clone paths: {e}") from e
        try:
            src_r.relative_to(root)
        except ValueError:
            pass
        else:
            try:
                src_r.relative_to(root / "work")
            except ValueError:
                raise DispatchError(
                    "REFUSED",
                    "clone source is the live runtime root; want the repo tree")
    attempt = _safe_attempt_id(attempt_id)
    if dest not in (None, ""):
        dest_p = Path(dest)
    elif live_root not in (None, ""):
        try:
            paths = CosmosPaths(live_root)
            dest_p = paths.role("work", GROK_WORK_LANE, attempt, "clone")
        except CosmosPathError:
            dest_p = Path(live_root) / "work" / GROK_WORK_LANE / attempt / "clone"
    else:
        dest_p = src.parent / "_grok_work" / attempt / "clone"
    if dest_p.exists():
        # never reuse a dirty prior attempt; never delete. Fresh sibling.
        n = 0
        parent, name = dest_p.parent, dest_p.name
        while dest_p.exists():
            n += 1
            dest_p = parent / f"{name}-{n}"
    assert_not_live_workspace(dest_p, live_root=live_root, source_tree=src)
    cloned = clone_attempt_workspace(src, dest_p)
    if not cloned.get("ok"):
        raise DispatchError(
            "BROKE",
            f"attempt-private clone failed: {cloned.get('err') or cloned}")
    ws = Path(cloned.get("workspace") or dest_p)
    assert_not_live_workspace(ws, live_root=live_root, source_tree=src)
    cloned["source"] = str(src)
    cloned["workspace"] = str(ws)
    return ws, cloned


def collect_workspace_proposal(workspace, *, diff_path=None) -> dict:
    """Surface the coder's private-tree writes as a proposal for COW.

    Never commits, never pushes. git add -A is index-only in the clone so
    untracked files land in the cached diff. Missing .git -> path only.
    """
    ws = Path(workspace)
    rec = {
        "workspace": str(ws),
        "status": "",
        "diff": "",
        "diff_truncated": False,
        "untracked": [],
        "changed": [],
        "how": None,
        "gateway": "fenced_commit",
    }
    if not ws.is_dir():
        rec["how"] = "missing"
        return rec
    if not (ws / ".git").exists():
        rec["how"] = "no-git"
        return rec

    def _git(args, timeout_s=60):
        try:
            p = subprocess.run(
                ["git", "-C", str(ws), *args],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=timeout_s, shell=False,
                creationflags=_CREATE_NO_WINDOW)
            return p.returncode, p.stdout or "", p.stderr or ""
        except Exception as e:  # noqa: BLE001
            return -1, "", f"{type(e).__name__}: {e}"

    _git(["add", "-A"])
    rc_st, st_out, st_err = _git(["status", "--porcelain", "-uall"])
    rec["status"] = (st_out or "")[:8000]
    rec["status_err"] = (st_err or "")[:400]
    rec["how"] = "git"
    for line in rec["status"].splitlines():
        path = line[3:].strip() if len(line) >= 4 else line.strip()
        if not path:
            continue
        rec["changed"].append(path)
        if line.startswith("??") or line[:2].strip() == "A":
            rec["untracked"].append(path)
    rc_d, diff_out, diff_err = _git(["diff", "--cached", "--no-color"])
    body = diff_out or ""
    rec["diff_err"] = (diff_err or "")[:400]
    rec["diff_rc"] = rc_d
    rec["status_rc"] = rc_st
    if diff_path is not None:
        try:
            dp = Path(diff_path)
            dp.parent.mkdir(parents=True, exist_ok=True)
            dp.write_text(body, encoding="utf-8")
            rec["diff_path"] = str(dp)
        except OSError as e:
            rec["diff_path_error"] = f"{type(e).__name__}: {e}"
    rec["diff"] = body[:PROPOSAL_DIFF_CAP]
    rec["diff_truncated"] = len(body) > PROPOSAL_DIFF_CAP
    rec["diff_bytes"] = len(body.encode("utf-8", errors="replace"))
    return rec


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
    model_id = None
    if model and model not in (DEFAULT_MODEL, ""):
        model_id = model
    body = {
        "prompt": {"text": task},
        "repos": [{"url": CURSOR_REPO, "startingRef": CURSOR_REF}],
        "autoCreatePR": True,
    }
    if model_id:
        body["model"] = {"id": model_id}
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
out = {{"agent": AGENT, "kind": {json.dumps(lane_kind)}, "kind_live": "UNPROVEN",
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
        return _claude_job(agent, task, target_dir, result_path, returns_path,
                           timeout_s, inbox_path, sentinel_path,
                           resolve_lane_model(kind, model), kind)
    if kind in WORKER_KINDS:
        if worker_dir is None:
            raise DispatchError("NO_DIR", f"{kind} kind needs a worker bucket path")
        return _worker_job(kind, agent, task, worker_dir, result_path,
                           returns_path, timeout_s, inbox_path, sentinel_path,
                           out_dir=out_dir, compat_dir=compat_dir,
                           runtime_root=runtime_root)
    raise DispatchError("BAD_INPUT", f"unhandled kind {kind!r}")


# ---------------------------------------------------------------------------
# stamps, DHx, collector index (R5 ACCEPT, R6 lock ` · `, R7 sidecar+lock)
# ---------------------------------------------------------------------------

def _iso_now() -> str:
    """The stamp. Never hand-typed. Caller must use this, not a literal."""
    return datetime.now().astimezone().isoformat()


def _marker_line(stamp: str, agent: str, task: str, lane: str,
                 filename: str) -> str:
    return (f"{stamp}{MARKER_SEP}{agent}{MARKER_SEP}"
            f"{_oneline(task)}{MARKER_SEP}{lane}/{filename}")


def _marker_tail(marker: str) -> str:
    if MARKER_SEP in marker:
        return marker.rsplit(MARKER_SEP, 1)[-1].strip()
    return marker.rsplit(" - ", 1)[-1].strip()


def _with_file_lock(lock_path: Path, timeout_s: float = 15.0):
    """Blocking exclusive lock. Yields the fd. Always closed."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    fd = os.open(str(lock_path), flags, 0o644)
    deadline = time.time() + float(timeout_s)
    locked = False
    try:
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    os.lseek(fd, 0, os.SEEK_SET)
                    try:
                        os.write(fd, b"\x00")
                    except OSError:
                        pass
                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except OSError:
                if time.time() >= deadline:
                    os.close(fd)
                    raise DispatchError(
                        "IO", f"timeout acquiring lock {lock_path}")
                time.sleep(0.05)
        yield fd
    finally:
        if locked:
            try:
                if os.name == "nt":
                    import msvcrt
                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        try:
            os.close(fd)
        except OSError:
            pass


class _LockCM:
    def __init__(self, lock_path: Path, timeout_s: float = 15.0):
        self.lock_path = lock_path
        self.timeout_s = timeout_s
        self._gen = None

    def __enter__(self):
        self._gen = _with_file_lock(self.lock_path, self.timeout_s)
        return next(self._gen)

    def __exit__(self, *exc):
        try:
            next(self._gen, None)
        except StopIteration:
            pass
        return False


def append_dhx_marker(dhx: Path, marker: str) -> dict:
    """Append `- <marker>` to the Assignment log section. Idempotent on the
    `stream/file` tail so a retry does not double-stamp. Locked RMW (M2)."""
    dhx.parent.mkdir(parents=True, exist_ok=True)
    lock_path = dhx.with_name(dhx.name + ".lock")
    with _LockCM(lock_path):
        body = dhx.read_text(encoding="utf-8") if dhx.exists() else (
            "# DHx — the DHot box (AGENT BRIEF).\n\n"
            f"{DHX_ASSIGN_HEADER} — APPEND-ONLY markers\n\n"
        )
        line = f"- {marker}\n"
        tail = _marker_tail(marker)
        for existing in body.splitlines():
            if existing.startswith("- ") and existing.rstrip().endswith(tail):
                return {"wrote": False, "line": existing, "path": str(dhx)}
        idx = body.find(DHX_ASSIGN_HEADER)
        if idx < 0:
            if not body.endswith("\n"):
                body += "\n"
            new = body + "\n" + line
        else:
            nl = body.find("\n", idx)
            rest = nl + 1 if nl >= 0 else len(body)
            next_h = body.find("\n## ", rest)
            if next_h < 0:
                prefix, suffix = body, ""
            else:
                prefix, suffix = body[:next_h], body[next_h:]
            if not prefix.endswith("\n"):
                prefix += "\n"
            new = prefix + line + suffix
        dhx.write_text(new, encoding="utf-8")
    return {"wrote": True, "line": line.rstrip("\n"), "path": str(dhx)}


def _iter_index_rows(index_path: Path):
    if not index_path.exists():
        return
    try:
        fh = open(index_path, "r", encoding="utf-8", errors="replace")
    except OSError:
        return
    with fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                row = json.loads(ln)
            except ValueError:
                continue
            if isinstance(row, dict):
                yield row


def _already_in_index(index_path: Path, artifact: str, source: str = "dispatch_assignment") -> dict | None:
    found = None
    for row in _iter_index_rows(index_path) or []:
        if row.get("source") == source and row.get("artifact") == artifact:
            found = row
    return found


def _latest_for_job(index_path: Path, *, artifact: str | None = None,
                    job_file: str | None = None) -> dict | None:
    found = None
    for row in _iter_index_rows(index_path) or []:
        if artifact and row.get("artifact") == artifact:
            found = row
            continue
        if job_file and Path(str(row.get("job_file") or row.get("artifact") or "")).name == job_file:
            found = row
            continue
        if job_file and str(row.get("artifact") or "").endswith(job_file):
            found = row
    return found


def append_index_row(index_path: Path, row: dict, lock_path: Path | None = None) -> dict:
    """Append one JSONL row under the collector index lock (H3)."""
    index_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(row, sort_keys=True, separators=(",", ":"),
                         default=str) + "\n"
    lp = lock_path if lock_path is not None else index_path.with_name(INDEX_LOCK_NAME)
    with _LockCM(lp):
        with open(index_path, "a", encoding="utf-8", newline="") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
    return {"wrote": True, "row": row, "path": str(index_path)}


def append_assignment_row(index_path: Path, row: dict, lock_path: Path | None = None) -> dict:
    existing = _already_in_index(index_path, row["artifact"], "dispatch_assignment")
    if existing is not None:
        return {"wrote": False, "row": existing, "path": str(index_path)}
    return append_index_row(index_path, row, lock_path=lock_path)


def append_session_assignment(path: Path, row: dict) -> dict:
    """Append one JSONL row to the per-session agent-assignment file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(row, sort_keys=True, separators=(",", ":"),
                         default=str) + "\n"
    lock_path = path.with_name(path.name + ".lock")
    with _LockCM(lock_path):
        with open(path, "a", encoding="utf-8", newline="") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
    return {"wrote": True, "path": str(path), "row": row}


def repo_docs_dir() -> Path:
    """Repo-tree docs/ beside this module (not the runtime-root docs role)."""
    return Path(__file__).resolve().parent.parent / "docs"


def load_boundaries_text(path: Path | None = None) -> str:
    """Full text of docs/AGENT_BOUNDARIES.md. Empty string if missing
    (the daemon then refuses rather than sending a task without it)."""
    p = Path(path) if path is not None else (repo_docs_dir() / "AGENT_BOUNDARIES.md")
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def compose_agent_prompt(assignment: str, *, context_blob: str = "",
                         context_hint: str = "", boundaries: str = "",
                         provenance: dict | None = None) -> str:
    """Feed {context + assignment + mandatory AGENT_BOUNDARIES addendum}."""
    parts = [str(assignment or "").strip()]
    hint = str(context_hint or "").strip()
    if hint:
        parts.append("## CONTEXT HINT\n" + hint)
    blob = str(context_blob or "").strip()
    if blob or provenance:
        prov = provenance or {}
        header = (
            "## SESSION CONTEXT (native transcript tail)\n"
            f"session_id={prov.get('session_id')} "
            f"bytes={prov.get('byte_start')}-{prov.get('byte_end')} "
            f"path={prov.get('path')}"
        )
        parts.append(header + ("\n" + blob if blob else "\n(no text turns in tail)"))
    bounds = str(boundaries or "").strip()
    if bounds:
        parts.append(
            "============================================================\n"
            "MANDATORY ADDENDUM — docs/AGENT_BOUNDARIES.md\n"
            "Only the Orchestrator (COW) touches the live tree. Agents PROPOSE\n"
            "tree changes in their results (target path + full content or diff)\n"
            "for COW to execute, or not. Agents never write the live tree or\n"
            "the C:\\ Claude tree, and never delete (propose staging to _delme\\).\n"
            "============================================================\n\n"
            + bounds
        )
    return "\n\n".join(parts).strip() + "\n"


def write_inbox_sidecar(inbox: Path, row: dict) -> dict:
    inbox.parent.mkdir(parents=True, exist_ok=True)
    tmp = inbox.with_suffix(inbox.suffix + ".tmp")
    tmp.write_text(json.dumps(row, indent=1, default=str), encoding="utf-8")
    tmp.replace(inbox)
    return {"wrote": True, "path": str(inbox)}


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
    model = resolve_lane_model(kind_c, model)

    paths = bind_paths(runtime_root)
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
