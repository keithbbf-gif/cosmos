#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_workspace - ONE attempt-private workspace path for every rail.

The Codex coder already cloned into live/work/codex/<attempt>/clone and
refused the live runtime root as cwd. Work orders, Grok, Claude, and Gemini
were still inventing their own cwd. This module is that path, once:

  live/work/<lane>/<attempt>/...

Workers write HERE. The fenced commit gateway is how anything enters the
live tree. Existence under the runtime root is not permission: only the
work role is a legal write root (the empty-dir / live-tree-cwd scar).

    from cosmos_workspace import (
        assert_not_live, refuse_tree_cwd, prepare_workspace,
        order_workspace, clone_tree, stage_context, output_path,
    )

Does not modify kernel / ledger / sched / service. No bts_* import.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
LANE_ORDER = "orders"
CLONE_IGNORE = (".git", "__pycache__", ".venv", "live", "tmp", "_delme")


class WorkspaceError(RuntimeError):
    """kind in {REFUSED, BROKE, NO_CONTEXT}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def _safe_part(part: str) -> str:
    s = "".join(ch if ch.isalnum() or ch in "-_." else "-"
                for ch in str(part or "").strip())[:80]
    if not s or s in (".", "..") or ".." in s:
        raise WorkspaceError("REFUSED", f"unsafe path part {part!r}")
    if s.startswith("."):
        s = "x" + s
    return s


def under_work(live_root: Path | str, *parts: str) -> Path:
    root = Path(live_root)
    out = root / "work"
    for p in parts:
        out = out / _safe_part(p)
    return out


def assert_not_live(workspace: Path | str, live_root=None) -> None:
    """Refuse a cwd inside the runtime root unless it sits under work/.

    Workspace *outside* the runtime root is allowed (isolated tests, given
    attempt dirs). Workspace == live root, or any other live role, is REFUSED.
    Message pinned: CodexRail tests bind to it.
    """
    if live_root is None:
        return
    try:
        ws = Path(workspace).resolve()
        root = Path(live_root).resolve()
        work = (root / "work").resolve()
    except OSError:
        return
    try:
        ws.relative_to(root)
    except ValueError:
        return
    try:
        ws.relative_to(work)
        return
    except ValueError:
        raise WorkspaceError(
            "REFUSED",
            "coder refuses the live runtime root; attempt-private "
            "clone only under work/ (fenced commit gateway opens the PR)")


def refuse_tree_cwd(workspace: Path | str, live_root,
                    repo_tree: Path | str | None = None) -> Path:
    """Work-order cwd: must be under live/work/, never the repo tree.

    Closes `--cwd = live tree` (repo root / cosmos/ / docs/) which
    assert_not_live alone cannot see — those paths sit *outside* the
    runtime root, so they slipped through as 'not live'.
    """
    assert_not_live(workspace, live_root)
    try:
        ws = Path(workspace).resolve()
        root = Path(live_root).resolve()
        work = (root / "work").resolve()
    except OSError as e:
        raise WorkspaceError("BROKE", f"workspace resolve: {e}") from e
    try:
        ws.relative_to(work)
    except ValueError:
        raise WorkspaceError(
            "REFUSED",
            "work-order workspace must be attempt-private under the work role")
    if repo_tree is not None:
        try:
            repo = Path(repo_tree).resolve()
        except OSError:
            repo = None
        if repo is not None:
            if ws == repo:
                raise WorkspaceError(
                    "REFUSED", "refusing --cwd=live-tree (repo root)")
            for name in ("cosmos", "docs", "tests", "kdash", "builds"):
                if ws == (repo / name):
                    raise WorkspaceError(
                        "REFUSED",
                        f"refusing --cwd=live-tree ({name}/)")
    return ws


def clone_tree(src: Path, dest: Path) -> dict:
    """git clone --local, copytree fallback. Same contract as CodexRail."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    argv = ["git", "clone", "--local", str(src), str(dest)]
    kw = {
        "capture_output": True, "text": True, "encoding": "utf-8",
        "errors": "replace", "timeout": 120.0, "shell": False,
        "creationflags": CREATE_NO_WINDOW,
    }
    try:
        p = subprocess.run(argv, **kw)
        rc, err = p.returncode, (p.stderr or "")[:300]
        timed = False
    except subprocess.TimeoutExpired as e:
        rc, err, timed = None, (str(e)[:300]), True
    except FileNotFoundError as e:
        rc, err, timed = -1, str(e), False
    if (timed or rc not in (0,)) and dest.exists():
        return {"ok": False, "how": "clone", "rc": rc, "err": err}
    if timed or rc not in (0,):
        try:
            shutil.copytree(
                src, dest,
                ignore=shutil.ignore_patterns(*CLONE_IGNORE),
            )
            return {"ok": True, "how": "copytree", "rc": rc, "err": err[:200]}
        except OSError as e:
            return {"ok": False, "how": "copytree",
                    "err": f"{type(e).__name__}: {e}"}
    return {"ok": True, "how": "git-clone-local", "rc": 0}


def prepare_workspace(payload: dict, *, live_root=None, lane: str = "codex",
                      clone_fn=None) -> tuple[Path, dict]:
    """CodexRail._prepare_workspace, extracted. payload.workspace wins.

    clone dest defaults to live/work/<lane>/<attempt>/clone so every rail
    shares the same work/<lane>/<attempt> spine.
    """
    payload = payload or {}
    given = payload.get("workspace")
    if given:
        ws = Path(given)
        ws.mkdir(parents=True, exist_ok=True)
        assert_not_live(ws, live_root)
        return ws, {"ok": True, "how": "given", "workspace": str(ws)}
    if payload.get("skip_clone"):
        raise WorkspaceError(
            "BROKE", "skip_clone set without payload.workspace")
    src = payload.get("repo") or payload.get("cwd") or payload.get("target_dir")
    if not src:
        raise WorkspaceError(
            "BROKE",
            "coder needs payload.repo (or cwd/target_dir) to clone")
    src_p = Path(src)
    if not src_p.exists() or not src_p.is_dir():
        raise WorkspaceError(
            "BROKE", f"clone source is not a directory: {src_p}")
    dest_hint = payload.get("clone_dest")
    if dest_hint:
        dest = Path(dest_hint)
    else:
        attempt = str(payload.get("attempt_id") or f"{lane}-{int(time.time())}")
        if live_root is not None:
            dest = under_work(live_root, lane, attempt, "clone")
        else:
            dest = src_p.parent / f"_{lane}_work" / attempt / "clone"
    if dest.exists():
        assert_not_live(dest, live_root)
        return dest, {"ok": True, "how": "reuse", "workspace": str(dest)}
    assert_not_live(dest, live_root)
    cloner = clone_fn if clone_fn is not None else clone_tree
    cloned = cloner(src_p, dest)
    if not cloned.get("ok"):
        raise WorkspaceError(
            "BROKE",
            f"attempt-private clone failed: {cloned.get('err') or cloned}")
    return dest, {**cloned, "workspace": str(dest), "source": str(src_p)}


def order_workspace(live_root: Path | str, order_id: str,
                    repo_tree: Path | str | None = None) -> Path:
    """Attempt-private work-order root: work/orders/<id>/{context,out}."""
    dest = under_work(live_root, LANE_ORDER, order_id)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "context").mkdir(parents=True, exist_ok=True)
    (dest / "out").mkdir(parents=True, exist_ok=True)
    refuse_tree_cwd(dest, live_root, repo_tree=repo_tree)
    return dest


def stage_context(sources: list, dest_dir: Path, *,
                  repo_tree: Path | str | None = None) -> list:
    """Copy context sources into dest_dir. Read-only copies, never the live
    originals. Missing source is NO_CONTEXT (fail-closed)."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    staged = []
    for i, src in enumerate(sources or []):
        raw = src.get("path") if isinstance(src, dict) else src
        p = Path(str(raw or "").strip())
        if not str(p):
            raise WorkspaceError("NO_CONTEXT", f"context source[{i}] empty")
        if not p.is_absolute() and repo_tree is not None:
            p = Path(repo_tree) / p
        if not p.exists():
            raise WorkspaceError(
                "NO_CONTEXT", f"context source missing: {p}")
        name = _safe_part(p.name or f"src{i}")
        target = dest_dir / name
        n = 1
        while target.exists():
            n += 1
            target = dest_dir / f"{name}_{n}"
        try:
            if p.is_dir():
                shutil.copytree(
                    p, target,
                    ignore=shutil.ignore_patterns(*CLONE_IGNORE),
                )
                how = "dir"
            else:
                shutil.copy2(str(p), str(target))
                how = "file"
        except OSError as e:
            raise WorkspaceError(
                "NO_CONTEXT", f"copy {p} failed: {e}") from e
        staged.append({
            "src": str(p), "dest": str(target), "how": how,
            "mode": "read",
        })
    return staged


def output_path(workspace: Path, folder: str | None, filename: str) -> Path:
    """The agent's only write surface: workspace/out[/<folder>]/<filename>."""
    ws = Path(workspace)
    out = ws / "out"
    if folder:
        out = out / _safe_part(folder)
    out.mkdir(parents=True, exist_ok=True)
    name = _safe_part(filename)
    return out / name


def output_exists(path: Path) -> bool:
    try:
        return path.is_file() and path.stat().st_size > 0
    except OSError:
        return False
