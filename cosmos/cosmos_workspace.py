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
        order_workspace, clone_tree, seed_working_tree,
        stage_context, output_path,
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
# Default job target area: source prefixes + repo-root files. Never live/work.
SEED_AREA_PREFIXES = (
    "cosmos/", "tests/", "builds/", "docs/", "kdash/", "apk/",
)
SEED_DENY_PARTS = {
    ".git", "__pycache__", ".venv", "venv", "live", "tmp", "_delme",
    "trylive", "work", "ledger", "logs", "backups", "node_modules",
    ".grok", ".secrets",
}
SEED_SECRET_SUFFIXES = ("_key.txt", "_token.txt", "_env.json", ".pem")
SEED_SECRET_SUBSTR = ("api_key", "apikey", "credentials")


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


def _posix_rel(rel: str) -> str:
    return str(rel or "").replace("\\", "/").lstrip("/")


def _seed_denied(rel: str) -> bool:
    rel = _posix_rel(rel)
    if not rel or rel == ".":
        return True
    parts = [p for p in rel.split("/") if p]
    if any(p in SEED_DENY_PARTS or p == ".." for p in parts):
        return True
    name = parts[-1].lower()
    if name.endswith(SEED_SECRET_SUFFIXES):
        return True
    if any(s in name for s in SEED_SECRET_SUBSTR):
        return True
    if "ledger" in name and name.endswith((".jsonl", ".json")):
        return True
    return False


def _seed_in_area(rel: str, areas) -> bool:
    rel = _posix_rel(rel)
    if _seed_denied(rel):
        return False
    if areas:
        for raw in areas:
            a = _posix_rel(raw).rstrip("/")
            if not a:
                continue
            if rel == a or rel.startswith(a + "/"):
                return True
        return False
    if "/" not in rel:
        return True
    return any(rel.startswith(p) for p in SEED_AREA_PREFIXES)


def _git_c(cwd: Path, args: list, timeout_s: float = 60.0):
    argv = ["git", "-C", str(cwd), *args]
    kw = {
        "capture_output": True, "text": True, "encoding": "utf-8",
        "errors": "replace", "timeout": timeout_s, "shell": False,
        "creationflags": CREATE_NO_WINDOW,
    }
    try:
        p = subprocess.run(argv, **kw)
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired as e:
        return None, "", str(e)[:300]
    except FileNotFoundError as e:
        return -1, "", str(e)
    except OSError as e:
        return -1, "", f"{type(e).__name__}: {e}"


def _splitz(text: str) -> list:
    return [p for p in (text or "").split("\0") if p]


def list_working_files(src: Path) -> dict:
    """Tracked-dirty + untracked (gitignore-honoring) paths under src."""
    src = Path(src)
    rec = {"ok": False, "modified": [], "untracked": [], "err": ""}
    if not (src / ".git").exists():
        rec["ok"] = True
        rec["how"] = "no-git"
        return rec
    rc_m, out_m, err_m = _git_c(src, ["diff", "--name-only", "-z", "HEAD"])
    if rc_m not in (0,):
        rec["how"] = "git-list"
        rec["err"] = f"git diff --name-only HEAD rc={rc_m} {(err_m or '')[:200]}"
        return rec
    rc_u, out_u, err_u = _git_c(
        src, ["ls-files", "-z", "--others", "--exclude-standard"])
    if rc_u not in (0,):
        rec["how"] = "git-list"
        rec["err"] = (
            f"git ls-files --others rc={rc_u} {(err_u or '')[:200]}")
        return rec
    rec["modified"] = _splitz(out_m)
    rec["untracked"] = _splitz(out_u)
    rec["ok"] = True
    rec["how"] = "git"
    return rec


def _snapshot_seeded_clone(dest: Path) -> dict:
    """Commit dest's seeded tree. Dest only; never the source (P10)."""
    if not (dest / ".git").exists():
        return {"ok": True, "how": "no-git", "committed": False}
    rc_a, _, err_a = _git_c(dest, ["add", "-A"])
    if rc_a not in (0,):
        return {"ok": False, "how": "add", "rc": rc_a,
                "err": (err_a or "")[:300]}
    rc_s, st_out, st_err = _git_c(dest, ["status", "--porcelain", "-uall"])
    if rc_s not in (0,):
        return {"ok": False, "how": "status", "rc": rc_s,
                "err": (st_err or "")[:300]}
    if not (st_out or "").strip():
        return {"ok": True, "how": "clean", "committed": False}
    rc_c, _, err_c = _git_c(dest, [
        "-c", "user.email=cosmos-seed@local",
        "-c", "user.name=cosmos-seed",
        "-c", "commit.gpgsign=false",
        "commit", "--no-verify", "-m", "cosmos: seed source working tree",
    ], timeout_s=120.0)
    if rc_c not in (0,):
        return {"ok": False, "how": "commit", "rc": rc_c,
                "err": (err_c or "")[:300]}
    return {"ok": True, "how": "commit", "committed": True}


def seed_working_tree(src: Path, dest: Path, *, areas=None) -> dict:
    """Copy src's dirty working files into dest. Never writes src (P10).

    git clone --local omits uncommitted + untracked files; without this
    overlay the agent reads the live tree via absolute paths and the
    collected proposal is empty. Honors src .gitignore (ls-files
    --exclude-standard) plus a deny-list. Optional `areas` prefixes
    restrict to the job's target area; default is SEED_AREA_PREFIXES
    plus repo-root files. Snapshot-commits dest only so proposal diffs
    are the agent's writes, not the seed itself.
    """
    src = Path(src)
    dest = Path(dest)
    rec = {
        "ok": False, "copied": [], "deleted": [], "skipped": [],
        "errors": [], "committed": False, "how": None,
    }
    try:
        src_r = src.resolve()
        dest_r = dest.resolve()
    except OSError as e:
        rec["err"] = f"unreadable seed paths: {e}"
        rec["how"] = "resolve"
        return rec
    if src_r == dest_r:
        rec["err"] = "seed refuses dest == src (P10)"
        rec["how"] = "p10"
        return rec
    if not src.is_dir():
        rec["err"] = f"seed source is not a directory: {src}"
        rec["how"] = "src"
        return rec
    if not dest.is_dir():
        rec["err"] = f"seed dest is not a directory: {dest}"
        rec["how"] = "dest"
        return rec

    listed = list_working_files(src)
    rec["list"] = {
        "ok": listed.get("ok"), "how": listed.get("how"),
        "n_modified": len(listed.get("modified") or []),
        "n_untracked": len(listed.get("untracked") or []),
    }
    if not listed.get("ok"):
        rec["err"] = listed.get("err") or "working-tree list failed"
        rec["how"] = "git-list"
        return rec
    if listed.get("how") == "no-git":
        rec["ok"] = True
        rec["how"] = "no-git"
        return rec

    seen = set()
    for names in (listed.get("modified") or [],
                  listed.get("untracked") or []):
        for raw in names:
            rel = _posix_rel(raw)
            if not rel or rel in seen:
                continue
            seen.add(rel)
            if not _seed_in_area(rel, areas):
                rec["skipped"].append(rel)
                continue
            try:
                dest_full = (dest / rel).resolve()
                dest_full.relative_to(dest_r)
            except (OSError, ValueError):
                rec["errors"].append(f"outside dest: {rel}")
                continue
            src_p = src / rel
            dest_p = dest / rel
            if not src_p.exists():
                if dest_p.is_file() or dest_p.is_symlink():
                    try:
                        dest_p.unlink()
                        rec["deleted"].append(rel)
                    except OSError as e:
                        rec["errors"].append(f"unlink {rel}: {e}")
                continue
            if src_p.is_dir():
                rec["skipped"].append(rel)
                continue
            try:
                dest_p.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src_p), str(dest_p))
                rec["copied"].append(rel)
            except OSError as e:
                rec["errors"].append(f"copy {rel}: {e}")

    if rec["errors"] and not rec["copied"] and not rec["deleted"]:
        rec["err"] = "; ".join(rec["errors"][:5])
        rec["how"] = "copy"
        return rec

    snap = _snapshot_seeded_clone(dest)
    rec["snapshot"] = {
        "ok": snap.get("ok"), "how": snap.get("how"),
        "committed": bool(snap.get("committed")),
    }
    if not snap.get("ok"):
        rec["err"] = snap.get("err") or "seed snapshot commit failed"
        rec["how"] = "snapshot"
        rec["committed"] = False
        return rec
    rec["committed"] = bool(snap.get("committed"))
    rec["ok"] = True
    rec["how"] = "seed"
    rec["n_copied"] = len(rec["copied"])
    rec["n_deleted"] = len(rec["deleted"])
    rec["n_skipped"] = len(rec["skipped"])
    return rec


def _attach_seed(rec: dict, src: Path, dest: Path, *, areas=None) -> dict:
    """Fail-closed seed overlay after a successful clone. Dest only."""
    seeded = seed_working_tree(src, dest, areas=areas)
    rec["seed"] = seeded
    if not seeded.get("ok"):
        rec["ok"] = False
        rec["how"] = "seed"
        rec["err"] = seeded.get("err") or "seed failed"
    return rec


def clone_tree(src: Path, dest: Path, *, areas=None) -> dict:
    """git clone --local, copytree fallback. Same contract as CodexRail.

    After a successful clone, overlay src's dirty working files (seed)
    so the attempt-private dest equals the tree the agent must edit.
    """
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
            return _attach_seed(
                {"ok": True, "how": "copytree", "rc": rc, "err": err[:200]},
                src, dest, areas=areas)
        except OSError as e:
            return {"ok": False, "how": "copytree",
                    "err": f"{type(e).__name__}: {e}"}
    return _attach_seed(
        {"ok": True, "how": "git-clone-local", "rc": 0},
        src, dest, areas=areas)


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
    areas = payload.get("areas") or payload.get("target_area")
    if clone_fn is None:
        cloned = clone_tree(src_p, dest, areas=areas)
    else:
        cloned = clone_fn(src_p, dest)
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
