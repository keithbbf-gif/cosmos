#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_dispatch_critique -- PHASE 4 stage-5 critic-visibility seam.

Moved out of cosmos_dispatch.py with the module (docs/CORE_RESTRUCTURE.md):
a split does not land without its tests moving with it. cosmos_dispatch
re-exports the SAME objects, not copies, so dispatch() and
tests/test_dispatch.py (compose_critique_prompt inlines disposed bodies)
keep working unchanged.

F-29 lesson: a location/shape change that keeps boot green can still break
CALLERS. This suite pins:
  * cosmos_dispatch re-exports the SAME objects
  * cosmos_dispatch.py no longer defines the moved inliners
  * compose_critique_prompt still embeds on-disk bodies + full-file sha256
  * dispatch() of an OA stage-5 task still inlines through the re-export
    (boot-green is not drop-green)

Bite: cosmos/_fail_f39_critique_against_old.py against
_delme/predispose_dispatch_f39_critique_*/ (all_new_pins_failed).

    py -3.14 tests/test_dispatch_critique.py
"""
from __future__ import annotations

import ast
import hashlib
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
import cosmos_dispatch_critique as critique  # noqa: E402
from cosmos_kernel import install  # noqa: E402
from cosmos_dispatch import (  # noqa: E402
    DispatchError, compose_critique_prompt, dispatch, _is_critique_task,
)

RESULTS = []

REEXPORTED = (
    "_is_critique_task",
    "_posix_rel",
    "_under_root",
    "_path_tokens",
    "_seen_path",
    "_file_row",
    "_locate_artifact",
    "_inline_file",
    "_format_inlined",
    "compose_critique_prompt",
)

TREE_ID = "KMesh-COSMOS-live"
MOVED_DEFS = (
    "def _is_critique_task",
    "def _posix_rel",
    "def _under_root",
    "def _path_tokens",
    "def _seen_path",
    "def _file_row",
    "def _locate_artifact",
    "def _inline_file",
    "def _format_inlined",
    "def compose_critique_prompt",
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
    crit_path = REPO / "cosmos" / "cosmos_dispatch_critique.py"
    crit_src = crit_path.read_text(encoding="utf-8") if crit_path.is_file() else ""
    caller_src = (HERE / "test_dispatch.py").read_text(encoding="utf-8")

    check("critique module exists on disk",
          lambda: crit_path.is_file() and len(crit_src) > 200)
    check("import cosmos_dispatch_critique", lambda: critique is not None)

    for name in REEXPORTED:
        check(
            f"cosmos_dispatch still exports {name} (same object)",
            (lambda n=name: getattr(cosmos_dispatch, n) is getattr(critique, n)),
        )

    for defn in MOVED_DEFS:
        check(f"critique module defines {defn}",
              (lambda d=defn: d in crit_src))
        check(f"dispatch source no longer defines {defn}",
              (lambda d=defn: d not in disp_src))

    check("dispatch re-exports via cosmos_dispatch_critique import",
          lambda: "from cosmos_dispatch_critique import" in disp_src)
    check("stage-5 banner remains as a pointer, not a second definition",
          lambda: "live in cosmos_dispatch_critique" in disp_src
          and "from cosmos_dispatch_critique import" in disp_src)
    check("dispatch still owns dispatch / job_status (harness not moved)",
          lambda: "def dispatch" in disp_src and "def job_status" in disp_src)
    check("critique does not import cosmos_dispatch (no cycle)",
          lambda: not _imports_module(crit_src, "cosmos_dispatch"))
    check("critique never ledger.append",
          lambda: "ledger.append" not in crit_src)
    check("critique has no drive-literal queue default",
          lambda: r"V:\Ai\_queue" not in crit_src
          and "WELL_KNOWN_BOOTSTRAP" not in crit_src)

    check("compose_critique_prompt imported from cosmos_dispatch is the critique fn",
          lambda: compose_critique_prompt is critique.compose_critique_prompt)
    check("test_dispatch still calls compose_critique_prompt off cosmos_dispatch",
          lambda: "from cosmos_dispatch import" in caller_src
          and "compose_critique_prompt" in caller_src)


def _inliner_behaviour() -> None:
    td = Path(tempfile.mkdtemp(prefix="cosmos_f39_critique_"))
    propose = td / "crit_tree" / "_propose"
    src_a = b"def alpha():\n    return 'A-body-unique-9173'\n"
    src_b = b"beta = 42  # B-body-unique-4801\n"
    _write(propose / "BIND.json", json.dumps({
        "schema": "cosmos-p10-bind/1",
        "files": [
            {"target_path": "mod_a.py",
             "sha256": hashlib.sha256(src_a).hexdigest()},
            {"target_path": "pkg/mod_b.py",
             "sha256": hashlib.sha256(src_b).hexdigest()},
        ],
    }, indent=1))
    (propose / "mod_a.py").write_bytes(src_a)
    (propose / "pkg").mkdir(parents=True, exist_ok=True)
    (propose / "pkg" / "mod_b.py").write_bytes(src_b)
    assignment = (
        "STAGE-5 different-family critique of the disposed _propose artifacts "
        "mod_a.py and pkg/mod_b.py. Verify the bodies.")
    built = compose_critique_prompt(assignment, propose_dir=propose,
                                    tree=td / "crit_tree")
    sha_a = hashlib.sha256(src_a).hexdigest()
    sha_b = hashlib.sha256(src_b).hexdigest()
    text_a, text_b = src_a.decode("utf-8"), src_b.decode("utf-8")
    prompt = built.get("prompt") or ""
    recs = {r["path"]: r for r in (built.get("files") or [])}

    check("compose_critique_prompt inlines both disposed bodies",
          lambda: built.get("inlined") is True
          and text_a in prompt and text_b in prompt)
    check("inlined sha256 of mod_a.py is of the FULL file on disk",
          lambda: (recs.get("mod_a.py") or {}).get("sha256") == sha_a
          and (propose / "mod_a.py").read_bytes() == src_a)
    check("inlined sha256 of pkg/mod_b.py is of the FULL file on disk",
          lambda: (recs.get("pkg/mod_b.py") or {}).get("sha256") == sha_b
          and (propose / "pkg" / "mod_b.py").read_bytes() == src_b)
    check("inlined prompt carries BEGIN FILE marks, not path-only",
          lambda: "===== BEGIN FILE " in prompt
          and "sha256=" in prompt
          and "A path you cannot open is not evidence." in prompt)
    check("_is_critique_task fires on STAGE-5 / critique / vendor-plural",
          lambda: _is_critique_task(assignment) is True
          and _is_critique_task("implement the widget") is False)
    check("already-inlined assignment is not double-wrapped",
          lambda: compose_critique_prompt(prompt).get("already") is True)

    missing = compose_critique_prompt(
        "STAGE-5 critique of no_such_file.py",
        files=["no_such_file.py"], tree=td / "crit_tree")
    check("missing disposed file is marked missing, not invented",
          lambda: missing.get("inlined") is False
          and any(r.get("missing") for r in (missing.get("files") or [])))


def _caller_dispatch() -> None:
    """The harness caller, not just the inliner. F-29 shape pin."""
    td = Path(tempfile.mkdtemp(prefix="cosmos_f39_critique_disp_"))
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
    propose = td / "crit_tree" / "_propose"
    src_a = b"def alpha():\n    return 'A-body-unique-9173'\n"
    _write(propose / "BIND.json", json.dumps({
        "schema": "cosmos-p10-bind/1",
        "files": [
            {"target_path": "mod_a.py",
             "sha256": hashlib.sha256(src_a).hexdigest()},
        ],
    }, indent=1))
    (propose / "mod_a.py").write_bytes(src_a)
    assignment = (
        "STAGE-5 different-family critique of the disposed _propose artifacts "
        "mod_a.py. Verify the bodies.")
    rec = dispatch(
        "OA", assignment, str(td / "crit_tree"), queue=queue,
        runtime_root=root, dhx=dhx)
    src = Path(rec["job_path"]).read_text(encoding="utf-8")
    sha_a = hashlib.sha256(src_a).hexdigest()
    check("dispatch() OA stage-5 still drops a worker job",
          lambda: rec.get("kind") == "oa" and rec.get("created") is True)
    check("dropped OA critique job still carries inlined body + sha256",
          lambda: sha_a in src and "A-body-unique-9173" in src)
    check("dropped OA critique job does not bake a BTS drive-literal queue",
          lambda: r"V:\Ai\_queue" not in src)

    grok = dispatch(
        "G46", "Reply with the single word PONG. Do not edit files.",
        str(td / "crit_tree"), kind="grok", queue=queue,
        runtime_root=root, dhx=dhx)
    grok_src = Path(grok["job_path"]).read_text(encoding="utf-8")
    check("dispatch() grok (not a critic rail) is unchanged by the split",
          lambda: grok.get("kind") == "grok" and grok.get("kind_live") == "proven"
          and '"--single"' in grok_src)


def main() -> int:
    _seam_rows()
    _inliner_behaviour()
    _caller_dispatch()
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    disp_path = REPO / "cosmos" / "cosmos_dispatch.py"
    crit_path = REPO / "cosmos" / "cosmos_dispatch_critique.py"
    live_value = {
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "reexported": len(REEXPORTED),
        "compose_same": (
            hasattr(cosmos_dispatch, "compose_critique_prompt")
            and cosmos_dispatch.compose_critique_prompt
            is critique.compose_critique_prompt
        ),
        "is_critique_same": (
            hasattr(cosmos_dispatch, "_is_critique_task")
            and cosmos_dispatch._is_critique_task is critique._is_critique_task
        ),
        "disp_lines": disp_path.read_text(encoding="utf-8").count("\n") + 1,
        "crit_lines": (
            crit_path.read_text(encoding="utf-8").count("\n") + 1
            if crit_path.is_file() else 0
        ),
        "crit_exists": crit_path.is_file(),
        "tree_id": TREE_ID,
    }
    print("live_value: " + json.dumps(live_value, sort_keys=True))
    print(("PASS" if not bad else "FAIL")
          + f" {len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
