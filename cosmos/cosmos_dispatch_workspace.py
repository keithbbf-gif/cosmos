#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_dispatch_workspace - the attempt-private workspace seam of dispatch.

PHASE 4, docs/CORE_RESTRUCTURE.md. `cosmos_dispatch.py` was 2,777 lines. This
module is ONE cut along a seam the file already named for itself:

    # ---------------------------------------------------------------------
    # attempt-private workspace (P10: grok/G46 never writes the live tree)
    # ---------------------------------------------------------------------

Everything between that banner and the `job source` banner is here, byte-for-byte
in behaviour. It is the P10 fence and nothing else: clone the repo into an
attempt-private dir, refuse the live tree as cwd, seed the coder's working files,
and surface what the coder wrote as a PROPOSAL for COW. It knows nothing about
lanes, the queue, the DHx, the collector index, job rendering or `dispatch()`.

Why this seam and not another. The block has exactly ONE inbound coupling to the
rest of dispatch -- `DispatchError` -- and zero outbound ones: no lane table, no
KIND_* map, no stamp, no index lock. The other candidate (the job-source
templates, ~450 lines) reaches back into ten module constants and
`resolve_lane_model`, so cutting there would have created a circular import or
forced the KIND_* tables to move with it. A seam is only clean when the cut
crosses few edges; this one crosses one.

That one edge is closed the way `cosmos_rail_base` closed the same problem for
`RailError` -- by INVERTING the hierarchy rather than duplicating the type.
`DispatchError` is defined HERE, the lower layer, and `cosmos_dispatch` imports
and re-exports it. It is the SAME class object, so every existing
`except DispatchError` -- including the one inside the generated grok job, which
does `from cosmos_dispatch import DispatchError, collect_workspace_proposal,
prepare_grok_workspace` -- catches exactly what it caught before. Pinned by
tests/test_dispatch_workspace.py, not by prose. (PHASE 5, one refusal taxonomy,
is where this type finds its permanent home; this move does not pre-empt it.)

The move is ADDITIVE. `cosmos_dispatch` re-exports every name below, so no
importer changes.

    from cosmos_dispatch_workspace import (
        DispatchError, assert_not_live_workspace, clone_attempt_workspace,
        collect_workspace_proposal, prepare_grok_workspace,
    )

Does not modify kernel / ledger / sched / service. No hard-coded paths: the
destination resolves through CosmosPaths' `work` role under the caller's root.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402
from cosmos_workspace import seed_working_tree  # noqa: E402

PROPOSAL_DIFF_CAP = 120_000
GROK_WORK_LANE = "grok"
CLONE_IGNORE = (
    "__pycache__", ".venv", "live", "tmp", "_delme",
    "node_modules", ".grok",
)
_CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


class DispatchError(RuntimeError):
    """Typed refusal. `kind` is BAD_INPUT, NO_LANE, NO_DIR, NO_KEY, NO_ROOT,
    NO_QUEUE, IO, REFUSED, BROKE.

    Defined in the lower layer so the workspace fence can raise it without
    importing `cosmos_dispatch`; `cosmos_dispatch` re-exports this exact class.
    """

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


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


def _seed_clone(src: Path, dest: Path, rec: dict, *, areas=None) -> dict:
    """Overlay src dirty working files onto dest. Dest only (P10)."""
    seeded = seed_working_tree(src, dest, areas=areas)
    rec["seed"] = seeded
    rec["workspace"] = str(dest)
    if not seeded.get("ok"):
        rec["ok"] = False
        rec["how"] = "seed"
        rec["err"] = seeded.get("err") or "seed failed"
    return rec


def clone_attempt_workspace(src: Path, dest: Path, *, areas=None) -> dict:
    """git clone --local, then copytree fallback. Never deletes dest.

    After a successful clone, seed dest with src's uncommitted + untracked
    working files (job target area; gitignore + deny-list). Fail-closed:
    a clone that cannot be seeded is BROKE, never a silent HEAD snapshot.
    """
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
        return _seed_clone(
            src, dest,
            {"ok": True, "how": "git-clone-local", "rc": 0,
             "elapsed_s": elapsed},
            areas=areas)

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
        return _seed_clone(
            src, copy_dest,
            {"ok": True, "how": "copytree", "rc": rc,
             "clone_err": (err or "")[:200],
             "elapsed_s": elapsed},
            areas=areas)
    except OSError as e:
        return {"ok": False, "how": "copytree",
                "err": f"{type(e).__name__}: {e}",
                "clone_err": (err or "")[:200],
                "rc": rc, "timed_out": timed_out}


def prepare_grok_workspace(source, *, live_root=None, attempt_id=None,
                           dest=None, areas=None) -> tuple:
    """Clone `source` into an attempt-private dir. Fail-closed: REFUSED/BROKE
    rather than returning the live tree as cwd. `areas` optional path
    prefixes restrict the working-tree seed to the job's target area.
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
    cloned = clone_attempt_workspace(src, dest_p, areas=areas)
    if not cloned.get("ok"):
        raise DispatchError(
            "BROKE",
            f"attempt-private clone failed: {cloned.get('err') or cloned}")
    ws = Path(cloned.get("workspace") or dest_p)
    assert_not_live_workspace(ws, live_root=live_root, source_tree=src)
    cloned["source"] = str(src)
    cloned["workspace"] = str(ws)
    # P07 Layer A: folder grant at spawn. Not a cosmos_lock fencing token.
    from cosmos_spawn_grant import SpawnGrant  # local import: seam, not a cycle
    cloned["spawn_grant"] = SpawnGrant(ws, attempt)
    cloned["spawn_grant_kind"] = SpawnGrant.kind
    cloned["ballot_writer"] = False
    return ws, cloned


def prepare_dual_lane_workspaces(source, *, live_root=None, attempt_id=None,
                                 dest=None, areas=None) -> dict:
    """Two private clones. Sibling recorded. No ballot. Peeking is a later check.

    Lane A cannot read Lane B's workspace (assert_no_peek). Compare is not
    a merge in this function.
    """
    attempt = _safe_attempt_id(attempt_id)
    ws_a, rec_a = prepare_grok_workspace(
        source, live_root=live_root, attempt_id=f"{attempt}-A",
        dest=None if dest in (None, "") else Path(dest) / "A", areas=areas)
    ws_b, rec_b = prepare_grok_workspace(
        source, live_root=live_root, attempt_id=f"{attempt}-B",
        dest=None if dest in (None, "") else Path(dest) / "B", areas=areas)
    rec_a["lane"] = "A"
    rec_b["lane"] = "B"
    rec_a["sibling"] = str(ws_b)
    rec_b["sibling"] = str(ws_a)
    rec_a["ballot_writer"] = False
    rec_b["ballot_writer"] = False
    return {"A": (ws_a, rec_a), "B": (ws_b, rec_b)}


def collect_workspace_proposal(workspace, *, diff_path=None) -> dict:
    """Surface the coder's private-tree writes as a proposal for COW.

    Never commits, never pushes. Dest only (P10). `git add -A` then
    `git add -N` (intent-to-add) so untracked NEW files land in
    `git diff HEAD`. Porcelain status is the change list; any porcelain
    path missing from the diff is filled fail-closed. Missing .git ->
    path only.
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

    rc_a, _, err_a = _git(["add", "-A"])
    rec["add_rc"] = rc_a
    rec["add_err"] = (err_a or "")[:400]
    rc_n, _, err_n = _git(["add", "-N", "--", "."])
    rec["intent_add_rc"] = rc_n
    rec["intent_add_err"] = (err_n or "")[:400]
    rc_st, st_out, st_err = _git(["status", "--porcelain", "-uall"])
    rec["status"] = (st_out or "")[:8000]
    rec["status_err"] = (st_err or "")[:400]
    rec["how"] = "git"
    for line in rec["status"].splitlines():
        path = line[3:].strip() if len(line) >= 4 else line.strip()
        if " -> " in path:
            path = path.split(" -> ")[-1].strip()
        if not path:
            continue
        rec["changed"].append(path)
        xy = line[:2] if len(line) >= 2 else ""
        if line.startswith("??") or xy.strip() in ("A", "AM"):
            rec["untracked"].append(path)
    rc_d, diff_out, diff_err = _git(["diff", "HEAD", "--no-color"])
    body = diff_out or ""
    rec["diff_err"] = (diff_err or "")[:400]
    rec["diff_rc"] = rc_d
    rec["status_rc"] = rc_st

    # Fail-closed: a NEW file that did not land in `git diff HEAD` still
    # gets a hunk (intent-to-add miss, or add -A skipped a path).
    missing = []
    body_norm = body.replace("\\", "/")
    for path in rec["changed"]:
        check = path.replace("\\", "/")
        if not check:
            continue
        marker = f"b/{check}"
        if marker in body_norm or check in body_norm:
            continue
        missing.append(path)
    extra = []
    for path in missing:
        _rc_p, d_p, _ = _git(["diff", "HEAD", "--no-color", "--", path])
        if (d_p or "").strip():
            extra.append(d_p)
            continue
        abs_p = ws / path
        if not abs_p.is_file():
            continue
        nul = "NUL" if os.name == "nt" else "/dev/null"
        _rc_u, d_u, _ = _git(
            ["diff", "--no-index", "--no-color", "--", nul, path])
        if (d_u or "").strip():
            extra.append(d_u)
    if extra:
        rec["diff_filled"] = True
        glue = "" if (not body or body.endswith("\n")) else "\n"
        body = body + glue + "".join(extra)

    if rec["changed"] and not (body or "").strip():
        rec["how"] = "git-empty-diff"
        rec["err"] = "porcelain has changes but git diff HEAD is empty"

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
