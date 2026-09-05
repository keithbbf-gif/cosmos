#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_dispatch_workspace -- the P10 attempt-private workspace fence.

PHASE 4 seam (docs/CORE_RESTRUCTURE.md). These rows lived in tests/test_dispatch.py
until the block they cover moved out of cosmos_dispatch.py into its own module;
the rule is that a split does not land without its tests moving with it, so they
are here, unchanged in what they assert.

Proves: the fence REFUSES the live repo tree and the runtime root outside work/,
and ALLOWS live/work/<lane>/<attempt>/clone; the clone lands under live/work/grok
and is never the source dir; the working-tree seed copies dirty + untracked
source files while denying live/, work/, __pycache__ and secrets, and never
writes the source tree; the proposal surfaces edited AND brand-new workspace
files with gateway=fenced_commit, while seeded files are not counted as the
agent's proposal.

Plus the seam rows themselves: cosmos_dispatch re-exports every moved name, and
`DispatchError` is the SAME class object in both modules -- not a copy -- so the
`except DispatchError` inside the generated grok job still catches the fence's
refusals. That import line is EXECUTED here, not asserted about.

Does not invoke grok/claude/cursor. Writes only under a temp dir.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
LIVE_COSMOS = Path(r"V:\A\Ai\COSMOS\cosmos")
# Live helpers (kernel/paths) then THIS bundle's dispatch first.
if LIVE_COSMOS.exists():
    sys.path.insert(0, str(LIVE_COSMOS))
sys.path.insert(0, str(BUNDLE / "cosmos"))
sys.path.insert(0, str(HERE))

import cosmos_dispatch                                              # noqa: E402
import cosmos_dispatch_workspace                                    # noqa: E402
from cosmos_kernel import install                                   # noqa: E402
from cosmos_dispatch_workspace import (                             # noqa: E402
    DispatchError, assert_not_live_workspace, collect_workspace_proposal,
    prepare_grok_workspace,
)

RESULTS = []

# The names cosmos_dispatch promised before the split. Every one must still be
# reachable from cosmos_dispatch, and be the identical object.
REEXPORTED = (
    "DispatchError", "assert_not_live_workspace", "clone_attempt_workspace",
    "collect_workspace_proposal", "prepare_grok_workspace",
    "CLONE_IGNORE", "GROK_WORK_LANE", "PROPOSAL_DIFF_CAP",
    "_CREATE_NO_WINDOW", "_as_resolved", "_safe_attempt_id", "_seed_clone",
)


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _raises_refused(fn) -> bool:
    try:
        fn()
    except DispatchError as e:
        return e.kind == "REFUSED"
    return False


def _seam_rows() -> None:
    """The split is additive, or it is not done."""
    for name in REEXPORTED:
        check(
            f"cosmos_dispatch still exports {name} (same object)",
            (lambda n=name: getattr(cosmos_dispatch, n)
             is getattr(cosmos_dispatch_workspace, n)),
        )
    # The generated grok job does exactly this. Execute it, do not assert about it.
    check("generated grok job's import line still resolves", lambda: (
        __import__(
            "cosmos_dispatch",
            fromlist=["DispatchError", "collect_workspace_proposal",
                      "prepare_grok_workspace"],
        ).DispatchError is DispatchError))
    check("a fence refusal is catchable as cosmos_dispatch.DispatchError",
          lambda: _raises_kind_via_dispatch_error())
    check("cosmos_dispatch no longer defines the moved fence in its own source",
          lambda: "def prepare_grok_workspace" not in
          (BUNDLE / "cosmos" / "cosmos_dispatch.py").read_text(encoding="utf-8"))


def _raises_kind_via_dispatch_error() -> bool:
    try:
        prepare_grok_workspace("", live_root=None, attempt_id="seam")
    except cosmos_dispatch.DispatchError as e:
        return e.kind == "BROKE"
    return False


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_dispatch_ws_"))
    root = install(td / "live", tree_id="spike-dispatch-ws")
    cwd = td / "workdir"
    cwd.mkdir()

    _seam_rows()

    # ---- P10: grok attempt-private workspace (does not invoke grok) ----
    check("assert_not_live refuses the source repo tree",
          lambda: _raises_refused(
              lambda: assert_not_live_workspace(
                  td, live_root=root, source_tree=td)))
    check("assert_not_live refuses live/state (runtime root outside work/)",
          lambda: _raises_refused(
              lambda: assert_not_live_workspace(
                  root / "state", live_root=root, source_tree=td)))
    allowed_ws = root / "work" / "grok" / "unit" / "clone"
    allowed_ws.mkdir(parents=True, exist_ok=True)
    check("assert_not_live allows live/work/grok/<attempt>/clone",
          lambda: assert_not_live_workspace(
              allowed_ws, live_root=root, source_tree=td) is None)

    ws1, crec = prepare_grok_workspace(
        cwd, live_root=root, attempt_id="unit-pong")
    check("prepare_grok_workspace ok", lambda: crec.get("ok") is True)
    check("prepare workspace is under live/work/grok",
          lambda: "work" in Path(ws1).parts and "grok" in Path(ws1).parts
          and str(Path(ws1).resolve()).startswith(str(Path(root).resolve())))
    check("prepare workspace is not the source dir",
          lambda: Path(ws1).resolve() != Path(cwd).resolve())
    check("prepare workspace is not the repo tree",
          lambda: Path(ws1).resolve() != Path(td).resolve())

    check("REFUSED rather than clone the live runtime root as source",
          lambda: _raises_refused(
              lambda: prepare_grok_workspace(
                  root, live_root=root, attempt_id="unit-live-src")))

    # tiny git repo: coder writes a file; proposal surfaces the diff
    grepo = td / "mini_repo"
    grepo.mkdir()
    _write(grepo / "hello.txt", "one\n")
    git_ok = False
    git_err = ""
    try:
        subprocess.run(["git", "init"], cwd=str(grepo), check=True,
                       capture_output=True, timeout=30)
        subprocess.run(["git", "add", "hello.txt"], cwd=str(grepo), check=True,
                       capture_output=True, timeout=30)
        subprocess.run(
            ["git", "-c", "user.email=c@c", "-c", "user.name=c",
             "-c", "commit.gpgsign=false", "commit", "-m", "t"],
            cwd=str(grepo), check=True, capture_output=True, timeout=30)
        git_ok = True
    except Exception as e:  # noqa: BLE001
        git_err = f"{type(e).__name__}: {e}"
    RESULTS.append(("git available for proposal test", git_ok, git_err))
    if git_ok:
        ws2, _crec2 = prepare_grok_workspace(
            grepo, live_root=root, attempt_id="unit-prop")
        _write(Path(ws2) / "hello.txt", "two\n")
        _write(Path(ws2) / "new.py", "x = 1\n")
        prop = collect_workspace_proposal(ws2)
        check("proposal how is git", lambda: prop.get("how") == "git")
        check("proposal lists the edited file",
              lambda: any("hello.txt" in c for c in (prop.get("changed") or [])))
        check("proposal diff is non-empty",
              lambda: bool((prop.get("diff") or "").strip())
              and "hello.txt" in (prop.get("diff") or ""))
        check("proposal lists a NEW workspace file",
              lambda: any("new.py" in c for c in (prop.get("changed") or []))
              and "new.py" in (prop.get("diff") or ""))
        check("proposal gateway is fenced_commit",
              lambda: prop.get("gateway") == "fenced_commit")

        # Seed: source uncommitted + untracked files land in dest; denied
        # paths (live/, work/, secrets, __pycache__) do not. Snapshot
        # commit means seeded files are NOT the agent's proposal.
        grepo2 = td / "mini_repo_seed"
        grepo2.mkdir()
        _write(grepo2 / "hello.txt", "one\n")
        _write(grepo2 / ".gitignore",
               "live/\nwork/\n__pycache__/\n*_key.txt\n")
        seed_git_ok = False
        seed_git_err = ""
        try:
            subprocess.run(["git", "init"], cwd=str(grepo2), check=True,
                           capture_output=True, timeout=30)
            subprocess.run(["git", "add", "hello.txt", ".gitignore"],
                           cwd=str(grepo2), check=True,
                           capture_output=True, timeout=30)
            subprocess.run(
                ["git", "-c", "user.email=c@c", "-c", "user.name=c",
                 "-c", "commit.gpgsign=false", "commit", "-m", "t"],
                cwd=str(grepo2), check=True, capture_output=True, timeout=30)
            seed_git_ok = True
        except Exception as e:  # noqa: BLE001
            seed_git_err = f"{type(e).__name__}: {e}"
        RESULTS.append(("git available for seed test", seed_git_ok, seed_git_err))
        if seed_git_ok:
            _write(grepo2 / "hello.txt", "dirty\n")
            _write(grepo2 / "area.py", "untracked\n")
            _write(grepo2 / "builds" / "cvm-dt" / "cvm_dt.py", "dt\n")
            _write(grepo2 / "live" / "state" / "x.json", "NO\n")
            _write(grepo2 / "work" / "other" / "nope.py", "NO\n")
            _write(grepo2 / "__pycache__" / "x.pyc", "NO\n")
            _write(grepo2 / "secret_key.txt", "NO\n")
            src_hello = (grepo2 / "hello.txt").read_text(encoding="utf-8")
            src_area = (grepo2 / "area.py").read_text(encoding="utf-8")
            ws3, crec3 = prepare_grok_workspace(
                grepo2, live_root=root, attempt_id="unit-seed")
            seed_rec = crec3.get("seed") or {}
            check("seed rec is ok", lambda: seed_rec.get("ok") is True)
            check("seed copied tracked-modified file",
                  lambda: (Path(ws3) / "hello.txt").read_text(
                      encoding="utf-8") == "dirty\n")
            check("seed copied untracked source file",
                  lambda: (Path(ws3) / "area.py").read_text(
                      encoding="utf-8") == "untracked\n")
            check("seed copied untracked target-area file",
                  lambda: (Path(ws3) / "builds" / "cvm-dt" / "cvm_dt.py"
                           ).read_text(encoding="utf-8") == "dt\n")
            check("seed did not copy live/",
                  lambda: not (Path(ws3) / "live" / "state" / "x.json"
                               ).exists())
            check("seed did not copy work/",
                  lambda: not (Path(ws3) / "work" / "other" / "nope.py"
                               ).exists())
            check("seed did not copy __pycache__",
                  lambda: not (Path(ws3) / "__pycache__" / "x.pyc").exists())
            check("seed did not copy secrets",
                  lambda: not (Path(ws3) / "secret_key.txt").exists())
            check("seed did not write the source tree (P10)",
                  lambda: (grepo2 / "hello.txt").read_text(
                      encoding="utf-8") == src_hello
                  and (grepo2 / "area.py").read_text(
                      encoding="utf-8") == src_area)
            _write(Path(ws3) / "brand_new.py", "y = 2\n")
            prop3 = collect_workspace_proposal(ws3)
            check("proposal captures untracked NEW file in workspace",
                  lambda: any("brand_new.py" in c
                              for c in (prop3.get("changed") or []))
                  and "brand_new.py" in (prop3.get("diff") or ""))
            check("seeded untracked file is not the whole proposal",
                  lambda: "area.py" not in (prop3.get("diff") or "")
                  and "cvm_dt.py" not in (prop3.get("diff") or ""))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    return 1 if bad else 0


def test_dispatch_workspace():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
