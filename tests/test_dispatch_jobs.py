#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_dispatch_jobs -- PHASE 4 job-source seam.

Moved out of cosmos_dispatch.py with the module (docs/CORE_RESTRUCTURE.md):
a split does not land without its tests moving with it. cosmos_dispatch
re-exports the SAME objects, not copies, so dispatch() and
tests/test_dispatch.py (job file text for grok/cursor/claude) keep working
unchanged.

F-29 lesson: a location/shape change that keeps boot green can still break
CALLERS. This suite pins:
  * cosmos_dispatch re-exports the SAME objects
  * cosmos_dispatch.py no longer defines the moved builders
  * render_job still emits the proven grok flag set, proven claude-CLI, UNPROVEN cursor
  * dispatch() still writes a grok job through the re-export
    (boot-green is not drop-green)
  * tests/test_work_order.py still asserts the cursor Cloud Agents lane
    (api.cursor.com + autoCreatePR) against the dispatch FAMILY, not
    dispatch.py alone -- the stamps/jobs split went red there while this
    suite stayed green.

Bite: cosmos/_fail_f39_jobs_against_old.py against
_delme/predispose_dispatch_f39_jobs_*/ (all_new_pins_failed).

    py -3.14 tests/test_dispatch_jobs.py
"""
from __future__ import annotations

import ast
import json
import sys
import tempfile
from pathlib import Path


def _imports_module(src: str, name: str) -> bool:
    """True iff `src` has an import of `name` (docstring mentions do not count)."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] == name for a in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] == name:
                return True
    return False


HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

import cosmos_dispatch  # noqa: E402
import cosmos_dispatch_jobs as jobs  # noqa: E402
from cosmos_kernel import install  # noqa: E402
from cosmos_dispatch import (  # noqa: E402
    CLAUDE_MODEL, CURSOR_BASE, DEFAULT_MODEL, DispatchError, GROK_MAX_TURNS,
    dispatch, render_job,
)

RESULTS = []

REEXPORTED = (
    "_py_path",
    "_job_helpers_block",
    "_grok_job",
    "_cursor_job",
    "_codex_job",
    "_claude_job",
    "_worker_job",
    "render_job",
)

TREE_ID = "KMesh-COSMOS-live"
MOVED_DEFS = (
    "def _py_path",
    "def _job_helpers_block",
    "def _grok_job",
    "def _cursor_job",
    "def _codex_job",
    "def _claude_job",
    "def _worker_job",
    "def render_job",
)


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _seam_rows() -> None:
    disp_src = (REPO / "cosmos" / "cosmos_dispatch.py").read_text(encoding="utf-8")
    jobs_path = REPO / "cosmos" / "cosmos_dispatch_jobs.py"
    jobs_src = jobs_path.read_text(encoding="utf-8") if jobs_path.is_file() else ""
    caller_src = (HERE / "test_dispatch.py").read_text(encoding="utf-8")

    check("jobs module exists on disk",
          lambda: jobs_path.is_file() and len(jobs_src) > 200)
    check("import cosmos_dispatch_jobs", lambda: jobs is not None)

    for name in REEXPORTED:
        check(
            f"cosmos_dispatch still exports {name} (same object)",
            (lambda n=name: getattr(cosmos_dispatch, n) is getattr(jobs, n)),
        )

    for defn in MOVED_DEFS:
        check(f"jobs module defines {defn}",
              (lambda d=defn: d in jobs_src))
        check(f"dispatch source no longer defines {defn}",
              (lambda d=defn: d not in disp_src))

    check("dispatch re-exports via cosmos_dispatch_jobs import",
          lambda: "from cosmos_dispatch_jobs import" in disp_src)
    check("job-source banner remains as a pointer, not a second definition",
          lambda: "builders live in cosmos_dispatch_jobs" in disp_src
          and "from cosmos_dispatch_jobs import" in disp_src)
    check("dispatch still owns dispatch / job_status (harness not moved)",
          lambda: "def dispatch" in disp_src and "def job_status" in disp_src)
    check("jobs does not import cosmos_dispatch (no cycle)",
          lambda: not _imports_module(jobs_src, "cosmos_dispatch"))
    check("jobs never ledger.append",
          lambda: "ledger.append" not in jobs_src)
    check("jobs has no drive-literal queue default",
          lambda: r"V:\Ai\_queue" not in jobs_src
          and "WELL_KNOWN_BOOTSTRAP" not in jobs_src)

    check("render_job imported from cosmos_dispatch is the jobs fn",
          lambda: render_job is jobs.render_job)
    check("test_dispatch still calls dispatch() off cosmos_dispatch",
          lambda: "from cosmos_dispatch import" in caller_src
          and "dispatch(" in caller_src)

    # F-29 / F-39: a jobs split that keeps THIS suite green can still break
    # tests/test_work_order.py (source-grep of the cursor Cloud Agents lane).
    # The next cut must keep the work-order assertion AND follow the family.
    wo_run = REPO / "cosmos" / "cosmos_work_order_run.py"
    wo_src = wo_run.read_text(encoding="utf-8") if wo_run.is_file() else ""
    wo_test = HERE / "test_work_order.py"
    wo_test_src = wo_test.read_text(encoding="utf-8") if wo_test.is_file() else ""
    check("work-order caller still exists (F-29: callers, not just own suite)",
          lambda: wo_test.is_file() and "_selftest" in wo_test_src)
    check("work-order still asserts dispatch cursor lane (never delete)",
          lambda: "existing dispatch cursor lane still present" in wo_src
          and "api.cursor.com" in wo_src
          and "autoCreatePR" in wo_src)
    check("work-order cursor-lane grep follows the dispatch family, not dispatch.py alone",
          lambda: "_dispatch_family_text" in wo_src
          and "cosmos_dispatch_jobs.py" in wo_src)
    check("work-order family scan follows from cosmos_dispatch_* import (next F-39 cut)",
          lambda: r"from (cosmos_dispatch_\w+) import" in wo_src
          or "cosmos_dispatch_\\w+" in wo_src)
    check("jobs module still carries the cursor Cloud Agents lane tokens",
          lambda: "api.cursor.com" in jobs_src and "autoCreatePR" in jobs_src)


def _builder_behaviour() -> None:
    td = Path(tempfile.mkdtemp(prefix="cosmos_f39_jobs_"))
    result = td / "out" / "g46_result.json"
    returns = td / "returns" / "g46_result.json"
    grok = render_job(
        "grok", "G46", "Reply with the single word PONG.",
        str(td), DEFAULT_MODEL, result, returns, 1800, None,
        runtime_root=td, attempt_id="g46_pong",
    )
    check("grok job uses --single + --always-approve + proven max-turns",
          lambda: '"--single"' in grok and '"--always-approve"' in grok
          and GROK_MAX_TURNS in grok)
    check("grok job takes the attempt-private clone path (P10)",
          lambda: "prepare_grok_workspace" in grok
          and "--cwd" in grok)
    check("grok job does not bake a live-tree cwd fallback",
          lambda: "NEVER fall back to SOURCE as cwd" in grok
          or "never the live tree" in grok.lower()
          or "attempt-private" in grok)

    def _cursor_no_key():
        try:
            render_job(
                "cursor", "Cursor", "stop.",
                str(td), DEFAULT_MODEL, result, returns, 900, None)
        except DispatchError as e:
            return e.kind == "NO_KEY"
        return False

    check("cursor without key_path is typed NO_KEY (H6, no key chase)",
          _cursor_no_key)

    keyp = td / "config" / "cursor_cosmos_key.txt"
    _write(keyp, "crsr_" + ("ab" * 32) + "31ab")
    cursor = render_job(
        "cursor", "Cursor", "Append one line and stop.",
        str(td), DEFAULT_MODEL, result, returns, 900, keyp,
    )
    check("cursor job POSTs /v1/agents against Cloud Agents base",
          lambda: '"/v1/agents"' in cursor and CURSOR_BASE in cursor)
    check("cursor job source still carries autoCreatePR",
          lambda: "autoCreatePR" in cursor)
    check("cursor job reads the key path, does not bake the secret",
          lambda: "cursor_cosmos_key.txt" in cursor and "crsr_" not in cursor)
    check("cursor kind_live in job source is UNPROVEN",
          lambda: '"kind_live": "UNPROVEN"' in cursor
          or "'kind_live': 'UNPROVEN'" in cursor
          or 'kind_live": "UNPROVEN"' in cursor)

    def _claude_off():
        try:
            render_job(
                "claude", "F5", "Reply PONG.",
                str(td), CLAUDE_MODEL, result, returns, 1800, None)
        except DispatchError as e:
            return e.kind == "ANTHROPIC_OFF"
        return False

    check("claude job files are ANTHROPIC_OFF", _claude_off)

    groq = render_job(
        "groq", "SSA", "Vet the alias table.",
        str(td), "openai/gpt-oss-20b", result, returns, 180, None,
        runtime_root=td,
    )
    check("groq SSA job uses GroqRail gpt-oss-20b",
          lambda: "GroqRail" in groq and "gpt-oss-20b" in groq
          and "prepare_grok_workspace" not in groq
          and "gsk_" not in groq)

    def _bad_kind():
        try:
            render_job(
                "nope", "X", "task",
                str(td), DEFAULT_MODEL, result, returns, 60, None)
        except DispatchError as e:
            return e.kind == "BAD_INPUT"
        return False

    check("unhandled kind is typed BAD_INPUT", _bad_kind)


def _caller_dispatch() -> None:
    """The harness caller, not just the builder. F-29 shape pin."""
    td = Path(tempfile.mkdtemp(prefix="cosmos_f39_jobs_disp_"))
    root = install(td / "live", tree_id=TREE_ID)
    queue = td / "queue"
    for extra in (queue, queue / "_lanes" / "lg", queue / "_lanes" / "pb"):
        extra.mkdir(parents=True, exist_ok=True)
        (extra / "running").mkdir(parents=True, exist_ok=True)
        (extra / "done").mkdir(parents=True, exist_ok=True)
    dhx = td / "docs" / "AGENT_BRIEF.md"
    _write(dhx, (
        "# DHx\n\n"
        "## Assignment log — APPEND-ONLY markers\n\n"
        "## Active assignments\n"
        "- live\n"
    ))
    cwd = td / "workdir"
    cwd.mkdir()
    rec = dispatch(
        "G46", "Reply with the single word PONG. Do not edit files.",
        str(cwd), kind="grok", queue=queue, runtime_root=root, dhx=dhx,
    )
    src = Path(rec["job_path"]).read_text(encoding="utf-8")
    check("dispatch() through re-export still drops a grok job",
          lambda: rec.get("kind") == "grok" and rec.get("created") is True
          and rec.get("kind_live") == "proven")
    check("dropped grok job still carries the proven flag set",
          lambda: '"--single"' in src and '"--always-approve"' in src
          and GROK_MAX_TURNS in src
          and "prepare_grok_workspace" in src)
    check("dropped grok job does not bake a BTS drive-literal queue",
          lambda: r"V:\Ai\_queue" not in src)

    def _cursor_dispatch_nokey():
        try:
            dispatch(
                "Cursor", "stop.",
                str(cwd), kind="cursor", queue=queue,
                runtime_root=root, dhx=dhx)
        except DispatchError as e:
            return e.kind == "NO_KEY"
        return False

    check("dispatch() cursor without key is still typed NO_KEY",
          _cursor_dispatch_nokey)


def main() -> int:
    _seam_rows()
    _builder_behaviour()
    _caller_dispatch()
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    disp_path = REPO / "cosmos" / "cosmos_dispatch.py"
    jobs_path = REPO / "cosmos" / "cosmos_dispatch_jobs.py"
    live_value = {
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "reexported": len(REEXPORTED),
        "render_same": (
            hasattr(cosmos_dispatch, "render_job")
            and cosmos_dispatch.render_job is jobs.render_job
        ),
        "grok_same": (
            hasattr(cosmos_dispatch, "_grok_job")
            and cosmos_dispatch._grok_job is jobs._grok_job
        ),
        "disp_lines": disp_path.read_text(encoding="utf-8").count("\n") + 1,
        "jobs_lines": (
            jobs_path.read_text(encoding="utf-8").count("\n") + 1
            if jobs_path.is_file() else 0
        ),
        "jobs_exists": jobs_path.is_file(),
        "tree_id": TREE_ID,
    }
    print("live_value: " + json.dumps(live_value, sort_keys=True))
    print(("PASS" if not bad else "FAIL")
          + f" {len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
