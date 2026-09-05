#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_dispatch_stamps -- PHASE 4 DHx/stamps/index seam.

Moved out of cosmos_dispatch.py with the module (docs/CORE_RESTRUCTURE.md):
a split does not land without its tests moving with it. cosmos_dispatch
re-exports the SAME objects, not copies, so dispatch() and
cosmos_node_worker / cosmos_dispatcher_daemon / cosmos_crit_consumer
keep working unchanged.

F-29 lesson: a location/shape change that keeps boot green can still break
CALLERS. This suite pins:
  * cosmos_dispatch re-exports the SAME objects
  * cosmos_dispatch.py no longer defines the moved stamp/DHx/index helpers
  * callers still import append_dhx_marker / write_inbox_sidecar /
    compose_agent_prompt off cosmos_dispatch
  * append_dhx_marker is idempotent on the stream/file tail
  * dispatch() still stamps DHx + writes the collector index through
    the re-export (boot-green is not drop-green)

Bite: cosmos/_fail_f39_stamps_against_old.py against
_delme/predispose_dispatch_f39_stamps_*/ (all_new_pins_failed).

    py -3.14 tests/test_dispatch_stamps.py
"""
from __future__ import annotations

import ast
import json
import sys
import tempfile
from datetime import datetime
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
import cosmos_dispatch_stamps as stamps  # noqa: E402
from cosmos_kernel import install  # noqa: E402
from cosmos_dispatch import (  # noqa: E402
    GROK_MAX_TURNS, MARKER_SEP, append_dhx_marker, append_index_row,
    append_session_assignment, compose_agent_prompt, dispatch,
    load_boundaries_text, write_inbox_sidecar,
)

RESULTS = []

REEXPORTED = (
    "_iso_now",
    "_marker_line",
    "_marker_tail",
    "_with_file_lock",
    "_LockCM",
    "append_dhx_marker",
    "_iter_index_rows",
    "_already_in_index",
    "_latest_for_job",
    "append_index_row",
    "append_assignment_row",
    "append_session_assignment",
    "repo_docs_dir",
    "load_boundaries_text",
    "compose_agent_prompt",
    "write_inbox_sidecar",
)

TREE_ID = "KMesh-COSMOS-live"
MOVED_DEFS = (
    "def _iso_now",
    "def _marker_line",
    "def _marker_tail",
    "def _with_file_lock",
    "class _LockCM",
    "def append_dhx_marker",
    "def _iter_index_rows",
    "def _already_in_index",
    "def _latest_for_job",
    "def append_index_row",
    "def append_assignment_row",
    "def append_session_assignment",
    "def repo_docs_dir",
    "def load_boundaries_text",
    "def compose_agent_prompt",
    "def write_inbox_sidecar",
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
    stamps_path = REPO / "cosmos" / "cosmos_dispatch_stamps.py"
    stamps_src = stamps_path.read_text(encoding="utf-8") if stamps_path.is_file() else ""
    worker_src = (REPO / "cosmos" / "cosmos_node_worker.py").read_text(encoding="utf-8")
    daemon_src = (REPO / "cosmos" / "cosmos_dispatcher_daemon.py").read_text(
        encoding="utf-8")
    crit_src = (REPO / "cosmos" / "cosmos_crit_consumer.py").read_text(encoding="utf-8")
    caller_src = (HERE / "test_dispatcher.py").read_text(encoding="utf-8")

    check("stamps module exists on disk",
          lambda: stamps_path.is_file() and len(stamps_src) > 200)
    check("import cosmos_dispatch_stamps", lambda: stamps is not None)

    for name in REEXPORTED:
        check(
            f"cosmos_dispatch still exports {name} (same object)",
            (lambda n=name: getattr(cosmos_dispatch, n) is getattr(stamps, n)),
        )

    for defn in MOVED_DEFS:
        check(f"stamps module defines {defn}",
              (lambda d=defn: d in stamps_src))
        check(f"dispatch source no longer defines {defn}",
              (lambda d=defn: d not in disp_src))

    check("dispatch re-exports via cosmos_dispatch_stamps import",
          lambda: "from cosmos_dispatch_stamps import" in disp_src)
    check("stamps banner remains as a pointer, not a second definition",
          lambda: "live in cosmos_dispatch_stamps" in disp_src
          and "from cosmos_dispatch_stamps import" in disp_src)
    check("dispatch still owns dispatch / job_status (harness not moved)",
          lambda: "def dispatch" in disp_src and "def job_status" in disp_src)
    check("stamps does not import cosmos_dispatch (no cycle)",
          lambda: not _imports_module(stamps_src, "cosmos_dispatch"))
    check("stamps never ledger.append",
          lambda: "ledger.append" not in stamps_src)
    check("stamps has no drive-literal queue default",
          lambda: r"V:\Ai\_queue" not in stamps_src
          and "WELL_KNOWN_BOOTSTRAP" not in stamps_src)
    check("node_worker still imports append_dhx_marker off cosmos_dispatch",
          lambda: "from cosmos_dispatch import" in worker_src
          and "append_dhx_marker" in worker_src
          and "write_inbox_sidecar" in worker_src)
    check("dispatcher_daemon still imports compose_agent_prompt off cosmos_dispatch",
          lambda: "from cosmos_dispatch import" in daemon_src
          and "compose_agent_prompt" in daemon_src
          and "append_session_assignment" in daemon_src)
    check("crit_consumer still imports append_dhx_marker off cosmos_dispatch",
          lambda: "from cosmos_dispatch import" in crit_src
          and "append_dhx_marker" in crit_src)
    check("append_dhx_marker imported from cosmos_dispatch is the stamps fn",
          lambda: append_dhx_marker is stamps.append_dhx_marker)
    check("test_dispatcher still calls compose_agent_prompt off cosmos_dispatch",
          lambda: "from cosmos_dispatch import" in caller_src
          and "compose_agent_prompt" in caller_src)


def _stamp_behaviour() -> None:
    td = Path(tempfile.mkdtemp(prefix="cosmos_f39_stamps_"))
    dhx = td / "docs" / "AGENT_BRIEF.md"
    _write(dhx, (
        "# DHx — the DHot box (AGENT BRIEF).\n\n"
        "## Assignment log — APPEND-ONLY markers\n\n"
        "## Active assignments\n"
        "- live\n"
    ))
    stamp = stamps._iso_now()
    marker = stamps._marker_line(
        stamp, "G46", "Reply PONG.", "pb", "job_g46_pong.py")
    rec = append_dhx_marker(dhx, marker)
    body = dhx.read_text(encoding="utf-8")
    check("stamp is ISO with offset (not a hand-typed ~ time)",
          lambda: "T" in stamp and stamp[-6] in "+-" and "~" not in stamp)
    check("stamp parses as aware datetime",
          lambda: datetime.fromisoformat(stamp).tzinfo is not None)
    check("marker uses protocol · grammar",
          lambda: MARKER_SEP in marker
          and marker.startswith(stamp + MARKER_SEP + "G46" + MARKER_SEP)
          and marker.endswith("pb/job_g46_pong.py"))
    check("append_dhx_marker writes the marker once",
          lambda: rec.get("wrote") is True and marker in body)
    check("marker lives in the Assignment log (before Active assignments)",
          lambda: body.find(marker) < body.find("## Active assignments"))
    rec2 = append_dhx_marker(dhx, marker)
    body2 = dhx.read_text(encoding="utf-8")
    check("second append is idempotent on the stream/file tail",
          lambda: rec2.get("wrote") is False
          and body2.count("job_g46_pong.py") == 1)

    idx = td / "state" / "collector" / "index.jsonl"
    row = {"schema": "cosmos-collector/2", "source": "dispatch_assignment",
           "artifact": str(td / "job_g46_pong.py"), "agent": "G46",
           "status": "assigned"}
    irec = append_index_row(idx, row)
    check("append_index_row writes one JSONL row",
          lambda: irec.get("wrote") is True and idx.is_file())
    rows = [json.loads(ln) for ln in idx.read_text(encoding="utf-8").splitlines()
            if ln.strip()]
    check("index has exactly one assignment row", lambda: len(rows) == 1)
    irec2 = stamps.append_assignment_row(idx, row)
    rows2 = [json.loads(ln) for ln in idx.read_text(encoding="utf-8").splitlines()
             if ln.strip()]
    check("append_assignment_row is idempotent on artifact",
          lambda: irec2.get("wrote") is False and len(rows2) == 1)

    inbox = td / "state" / "collector" / "inbox" / "job_g46_pong.json"
    srec = write_inbox_sidecar(inbox, row)
    check("write_inbox_sidecar lands the sidecar",
          lambda: srec.get("wrote") is True and inbox.is_file())
    loaded = json.loads(inbox.read_text(encoding="utf-8"))
    check("sidecar round-trips the assignment row",
          lambda: loaded.get("artifact") == row["artifact"]
          and loaded.get("agent") == "G46")

    sess = td / "state" / "assignments" / "sess.jsonl"
    arec = append_session_assignment(sess, {"agent": "G46", "task": "pong"})
    check("append_session_assignment writes a JSONL row",
          lambda: arec.get("wrote") is True and sess.is_file())

    bounds = load_boundaries_text()
    prompt = compose_agent_prompt(
        "reply PONG", context_blob="[user]\nhello", context_hint="cm",
        boundaries=bounds, provenance={"session_id": "s1",
                                       "byte_start": 0, "byte_end": 10,
                                       "path": "x.jsonl"})
    check("compose_agent_prompt carries assignment",
          lambda: "reply PONG" in prompt)
    check("compose_agent_prompt auto-attaches AGENT_BOUNDARIES",
          lambda: "MANDATORY ADDENDUM" in prompt and "Propose" in prompt)


def _caller_dispatch() -> None:
    """The harness caller, not just the stamp helpers. F-29 shape pin."""
    td = Path(tempfile.mkdtemp(prefix="cosmos_f39_stamps_disp_"))
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
    _write(queue / "seed_root.py", "print(1)\n")
    _write(queue / "_lanes" / "lg" / "seed_lg.py", "print(2)\n")
    rec = dispatch(
        "G46", "Reply with the single word PONG. Do not edit files.",
        str(cwd), kind="grok", queue=queue, runtime_root=root, dhx=dhx,
    )
    src = Path(rec["job_path"]).read_text(encoding="utf-8")
    dhx_text = dhx.read_text(encoding="utf-8")
    check("dispatch() through re-export still drops a grok job",
          lambda: rec.get("kind") == "grok" and rec.get("created") is True
          and rec.get("kind_live") == "proven")
    check("dropped grok job still carries the proven flag set",
          lambda: '"--single"' in src and '"--always-approve"' in src
          and GROK_MAX_TURNS in src)
    check("dispatch still auto-stamps DHx through the re-export",
          lambda: rec.get("marker") in dhx_text
          and rec.get("stamp") in rec.get("marker", ""))
    idx = Path(rec["index"])
    rows = [json.loads(ln) for ln in idx.read_text(encoding="utf-8").splitlines()
            if ln.strip()]
    check("dispatch still writes one collector assignment row",
          lambda: len(rows) == 1
          and rows[0].get("source") == "dispatch_assignment"
          and rows[0].get("artifact") == rec["job_path"])
    rec2 = dispatch(
        "G46", "Reply with the single word PONG. Do not edit files.",
        str(cwd), kind="grok", queue=queue, runtime_root=root, dhx=dhx,
    )
    check("second dispatch through re-export is still idempotent",
          lambda: rec2.get("idempotent") is True and rec2.get("created") is False)
    check("second dispatch does not double-stamp DHx",
          lambda: dhx.read_text(encoding="utf-8").count(rec["job_file"]) == 1)
    check("dropped grok job does not bake a BTS drive-literal queue",
          lambda: r"V:\Ai\_queue" not in src)


def main() -> int:
    _seam_rows()
    _stamp_behaviour()
    _caller_dispatch()
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    disp_path = REPO / "cosmos" / "cosmos_dispatch.py"
    stamps_path = REPO / "cosmos" / "cosmos_dispatch_stamps.py"
    live_value = {
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "reexported": len(REEXPORTED),
        "dhx_same": (
            hasattr(cosmos_dispatch, "append_dhx_marker")
            and cosmos_dispatch.append_dhx_marker is stamps.append_dhx_marker
        ),
        "inbox_same": (
            hasattr(cosmos_dispatch, "write_inbox_sidecar")
            and cosmos_dispatch.write_inbox_sidecar is stamps.write_inbox_sidecar
        ),
        "disp_lines": disp_path.read_text(encoding="utf-8").count("\n") + 1,
        "stamps_lines": (
            stamps_path.read_text(encoding="utf-8").count("\n") + 1
            if stamps_path.is_file() else 0
        ),
        "stamps_exists": stamps_path.is_file(),
        "tree_id": TREE_ID,
    }
    print("live_value: " + json.dumps(live_value, sort_keys=True))
    print(("PASS" if not bad else "FAIL")
          + f" {len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
