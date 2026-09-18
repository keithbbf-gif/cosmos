#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sandbox isolation pins (SGH steal-map item 3) vs origin/main.

Job-Object cwd may sit under live/work (on V:\\) — that is the host backend.
Daytona/E2B must not map V:\\. Unconfigured remote never silent-spawns Job-Object.
GET snapshot never mkdir. Modal stays named, not composed.
"""
from __future__ import annotations

import ast
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_sandbox import (  # noqa: E402
    COMPOSED_BACKEND,
    NAMED_NOT_COMPOSED,
    REMOTE_BACKENDS,
    SandboxError,
    _selftest,
    assert_no_host_map,
    assert_sandbox_cwd,
    attempt_dir,
    pick_backend,
    snapshot,
    spawn_backend,
    spawn_in_job,
)


def test_selftest():
    assert _selftest() == 0


def test_snapshot_never_mkdirs():
    from cosmos_paths import CosmosPaths, write_sentinel

    td = Path(tempfile.mkdtemp(prefix="sandbox_get_"))
    live = td / "live"
    write_sentinel(live, tree_id="sbx-get")
    (live / "work").mkdir(parents=True)
    (live / "config").mkdir(parents=True)
    paths = CosmosPaths(live)
    rec = snapshot(paths)
    assert rec["kind"] == "MEASURED"
    assert rec["remote"]["daytona"] == "UNCONFIGURED"
    assert rec["kernel_attached"] is False
    assert rec["is_scheduler"] is False
    assert not (live / "work" / "attempts").exists()
    assert not (live / "config" / "daytona_api_key.txt").exists()
    assert not (live / "config" / "sandbox_backend.json").exists()


def test_snapshot_ast_has_no_mkdir():
    src = (ROOT / "cosmos" / "cosmos_sandbox.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "snapshot")
    calls = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Attribute):
                calls.append(n.func.attr)
            elif isinstance(n.func, ast.Name):
                calls.append(n.func.id)
    assert "mkdir" not in calls
    assert "Never mkdir" in (ast.get_docstring(fn) or "")


def test_daytona_unconfigured_does_not_host_spawn():
    from cosmos_paths import CosmosPaths, write_sentinel
    import cosmos_sandbox as sb

    td = Path(tempfile.mkdtemp(prefix="sandbox_nocred_"))
    live = td / "live"
    write_sentinel(live, tree_id="sbx-nocred")
    (live / "work").mkdir(parents=True)
    (live / "config").mkdir(parents=True)
    paths = CosmosPaths(live)
    ws = attempt_dir(paths, "t")
    called = []
    real = sb.spawn_in_job

    def spy(*a, **k):
        called.append(1)
        return real(*a, **k)

    sb.spawn_in_job = spy
    try:
        try:
            spawn_backend("daytona", [sys.executable, "-c", "print(1)"],
                          ws, paths=paths)
            kind = None
        except SandboxError as e:
            kind = e.kind
    finally:
        sb.spawn_in_job = real
    assert kind == "UNCONFIGURED"
    assert called == []


def test_e2b_unconfigured_is_typed():
    from cosmos_paths import CosmosPaths, write_sentinel

    td = Path(tempfile.mkdtemp(prefix="sandbox_e2b_"))
    live = td / "live"
    write_sentinel(live, tree_id="sbx-e2b")
    (live / "work").mkdir(parents=True)
    (live / "config").mkdir(parents=True)
    paths = CosmosPaths(live)
    ws = attempt_dir(paths, "t")
    try:
        spawn_backend("e2b", [sys.executable, "-c", "x"], ws, paths=paths)
        kind = None
    except SandboxError as e:
        kind = e.kind
    assert kind == "UNCONFIGURED"


def test_host_pen_job_object_does_not_refuse_whole_v():
    """Gitur PR 564 was wrong: Job-Object workers live under live/work on V:\\."""
    from cosmos_paths import CosmosPaths, write_sentinel
    from cosmos_workspace import WorkspaceError

    td = Path(tempfile.mkdtemp(prefix="sandbox_pen_"))
    live = td / "live"
    write_sentinel(live, tree_id="sbx-pen")
    (live / "work").mkdir(parents=True)
    paths = CosmosPaths(live)
    ws = attempt_dir(paths, "t")
    assert assert_sandbox_cwd(ws, live, repo_tree=td) == ws.resolve()
    try:
        assert_sandbox_cwd(live / "state", live, repo_tree=td)
        raised = None
    except (SandboxError, WorkspaceError) as e:
        raised = getattr(e, "kind", type(e).__name__)
    assert raised in ("HOST_PEN", "LIVE_TREE", "REFUSED")


def test_remote_listing_v_is_isolation():
    try:
        assert_no_host_map("daytona", listing=("V:\\",))
        kind = None
    except SandboxError as e:
        kind = e.kind
    assert kind == "BACKEND_ISOLATION"


def test_modal_named_not_composed():
    assert NAMED_NOT_COMPOSED == ("modal",)
    assert REMOTE_BACKENDS == ("daytona", "e2b")
    try:
        spawn_backend("modal", [sys.executable, "-c", "x"], tempfile.gettempdir())
        kind = None
    except SandboxError as e:
        kind = e.kind
    assert kind == "NOT_COMPOSED"


def test_default_pick_is_job_object():
    assert pick_backend() == COMPOSED_BACKEND
    rec = snapshot()
    assert rec["composed"] in (COMPOSED_BACKEND, "posix_subprocess")
    assert rec["is_scheduler"] is False


def test_extra_drives_refuse():
    td = Path(tempfile.mkdtemp(prefix="sandbox_drv_"))
    ws = td / "ws"
    ws.mkdir()
    try:
        spawn_in_job([sys.executable, "-c", "print(1)"], ws, extra_drives=["Z:"])
        kind = None
    except SandboxError as e:
        kind = e.kind
    assert kind == "BACKEND_ISOLATION"


def test_not_scheduler():
    src = (ROOT / "cosmos" / "cosmos_sandbox.py").read_text(encoding="utf-8")
    assert "def spawn_in_job" in src
    assert "from cosmos_sched" not in src
    assert "import cosmos_sched" not in src


if __name__ == "__main__":
    sys.exit(_selftest())
