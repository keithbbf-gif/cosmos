#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sandbox isolation pins (SGH steal-map item 3).

These fail if the sandbox:
  * backend=daytona mkdir's on GET
  * claims kernel_attached
  * lets cwd sit on V:\\ (whole volume, not only V:\\Ai / OpenWork / Desktop)
  * silent-spawns the host Job-Object when Daytona/E2B credentials are missing
  * becomes a scheduler / second Core / replaces spawn_in_job
"""
from __future__ import annotations

import ast
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_sandbox import (  # noqa: E402
    ATTEMPT_REL,
    COMPOSED_BACKENDS,
    CRED_SUFFIX,
    DEFAULT_BACKEND,
    NAMED_NOT_COMPOSED,
    SandboxError,
    _selftest,
    attempt_dir,
    is_v_volume,
    refuse_cwd,
    resolve_backend,
    snapshot,
    spawn,
    spawn_in_job,
)


def test_selftest_five_of_five():
    assert _selftest() == 0


def test_daytona_get_never_mkdirs():
    """Behavioral pin: snapshot(backend=daytona) must not create roles."""
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    td = Path(tempfile.mkdtemp(prefix="sandbox_get_mkdir_"))
    root = install(td / "live", tree_id="spike-sandbox-get")
    paths = CosmosPaths(root)
    attempts = paths.role("work") / ATTEMPT_REL
    cred = paths.config(f"daytona{CRED_SUFFIX}")
    assert not attempts.exists(), "install must not pre-create work/attempts"
    assert not cred.exists()
    rec = snapshot(paths, backend="daytona")
    assert rec["kind"] == "NO_CREDENTIALS"
    assert rec["kernel_attached"] is False
    assert rec["get_mkdir"] is False
    assert rec["live_cloud"] is False
    assert not attempts.exists(), "GET snapshot(backend=daytona) mkdir'd work/attempts"
    assert not cred.exists(), "GET invented a Daytona credential file"


def test_get_fold_source_has_no_mkdir():
    """AST pin: snapshot body must not call mkdir."""
    src = (ROOT / "cosmos" / "cosmos_sandbox.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "snapshot":
            fn = node
            break
    assert fn is not None, "snapshot missing"
    calls = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            name = ""
            if isinstance(n.func, ast.Attribute):
                name = n.func.attr
            elif isinstance(n.func, ast.Name):
                name = n.func.id
            calls.append(name)
    assert "mkdir" not in calls, f"GET fold called mkdir: {calls}"
    doc = ast.get_docstring(fn) or ""
    assert "Never mkdir" in doc


def test_default_kernel_attached_is_false():
    rec = snapshot(backend="job")
    assert rec["kernel_attached"] is False
    assert rec["is_scheduler"] is False
    assert rec["is_core"] is False
    assert rec["backend"] == DEFAULT_BACKEND == "job"


def test_cwd_on_v_volume_refused():
    """Workers cannot sit cwd on V:\\ — whole volume, not a short pen list."""
    for raw in (
        "V:\\",
        r"V:\Ai",
        r"V:\OPENWORK",
        r"V:\Research4\scratch",
        r"v:/Streams/openwork",
        "\\\\?\\V:\\A\\Ai\\COSMOS\\live\\work",
    ):
        try:
            refuse_cwd(raw)
            raised = None
        except SandboxError as e:
            raised = e.kind
        assert raised == "HOST_PEN", f"{raw!r} was not HOST_PEN ({raised})"
        assert is_v_volume(raw)
    try:
        refuse_cwd(r"C:\Users\Papa\Desktop\scratch")
        desk = None
    except SandboxError as e:
        desk = e.kind
    assert desk == "HOST_PEN"


def test_spawn_refuses_v_cwd_for_every_backend():
    td = Path(tempfile.mkdtemp(prefix="sandbox_v_cwd_"))
    for backend in COMPOSED_BACKENDS:
        try:
            spawn([sys.executable, "-c", "x"], cwd=r"V:\Ai\tmp",
                  backend=backend, paths=None)
            kind = None
        except SandboxError as e:
            kind = e.kind
        assert kind == "HOST_PEN", f"backend={backend} let cwd sit on V:\\ ({kind})"
    assert not (td / "attempts").exists()


def test_daytona_missing_creds_does_not_host_spawn():
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths
    import cosmos_sandbox as sb

    td = Path(tempfile.mkdtemp(prefix="sandbox_nocred_"))
    root = install(td / "live", tree_id="spike-sandbox-nocred")
    paths = CosmosPaths(root)
    ws = td / "ws"
    ws.mkdir()
    called = []
    real = sb.spawn_in_job

    def spy(*a, **k):
        called.append(1)
        return real(*a, **k)

    sb.spawn_in_job = spy
    try:
        try:
            sb.spawn(
                [sys.executable, "-c", "print(1)"],
                cwd=ws, paths=paths, backend="daytona")
            kind = None
        except SandboxError as e:
            kind = e.kind
    finally:
        sb.spawn_in_job = real
    assert kind == "NO_CREDENTIALS"
    assert called == [], "missing Daytona creds silent-spawned the host Job-Object"


def test_e2b_missing_creds_is_typed():
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    td = Path(tempfile.mkdtemp(prefix="sandbox_e2b_"))
    root = install(td / "live", tree_id="spike-sandbox-e2b")
    paths = CosmosPaths(root)
    ws = td / "ws"
    ws.mkdir()
    try:
        spawn([sys.executable, "-c", "x"], cwd=ws, paths=paths, backend="e2b")
        kind = None
    except SandboxError as e:
        kind = e.kind
    assert kind == "NO_CREDENTIALS"


def test_modal_named_not_composed():
    assert NAMED_NOT_COMPOSED == ("modal",)
    try:
        resolve_backend("modal")
        kind = None
    except SandboxError as e:
        kind = e.kind
    assert kind == "NOT_COMPOSED"


def test_job_child_must_not_map_extra_drives():
    td = Path(tempfile.mkdtemp(prefix="sandbox_drives_"))
    ws = td / "ws"
    ws.mkdir()
    try:
        spawn_in_job(
            [sys.executable, "-c", "print(1)"],
            cwd=ws, extra_drives=["Z:"])
        kind = None
    except SandboxError as e:
        kind = e.kind
    assert kind == "REFUSED"
    rec = spawn_in_job([sys.executable, "-c", "print('ok')"], cwd=ws)
    assert rec["extra_drives_mapped"] is False
    assert rec["kill_on_close"] is True
    assert rec["active_process_limit"] == 8
    assert rec["ok"] is True


def test_not_scheduler_not_second_core_spawn_in_job_stays():
    src = (ROOT / "cosmos" / "cosmos_sandbox.py").read_text(encoding="utf-8")
    assert "def spawn_in_job" in src
    assert "import cosmos_sch" + "ed" not in src
    assert "from cosmos_sch" + "ed" not in src
    kernel_src = (ROOT / "cosmos" / "cosmos_kernel.py").read_text(encoding="utf-8")
    assert "cosmos_sandbox" not in kernel_src
    tree = ast.parse(src)
    names = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert "spawn_in_job" in names
    assert "spawn" in names
    assert names.count("spawn_in_job") == 1
    dest = attempt_dir
    assert dest is not None


if __name__ == "__main__":
    sys.exit(_selftest())
