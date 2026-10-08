#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inventory_hands and discover argv plans. No probe, bind, or scheduler."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[1] / "cosmos" / "cosmos_discover.py"
_FORBIDDEN = (
    "probe_http",
    "bind",
    "poll_once",
    "install_task",
    "standup",
    "write_heartbeat",
    "main",
)


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("cosmos_discover", _MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cosmos_discover is missing")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_discover = _load()
inventory_hands = _discover.inventory_hands
plan_once_argv = _discover.plan_once_argv
plan_task_argv = _discover.plan_task_argv


def _boom(label: str):
    def _inner(*_args, **_kwargs):
        raise AssertionError(label)

    return _inner


@pytest.fixture(autouse=True)
def _no_spawn(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _FORBIDDEN:
        monkeypatch.setattr(_discover, name, _boom(name))
    for fn in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, fn, _boom(f"subprocess.{fn}"))
        monkeypatch.setattr(_discover.subprocess, fn, _boom(f"discover.subprocess.{fn}"))
    clock = sys.modules["cosmos_clock"]
    for fn in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(clock.subprocess, fn, _boom(f"clock.subprocess.{fn}"))
    monkeypatch.setattr(os, "system", _boom("os.system"))


def test_inventory_hands_on_temp_research(tmp_path: Path, pytestconfig: pytest.Config) -> None:
    base = Path(str(pytestconfig.option.basetemp)).resolve()
    research = tmp_path / "research"
    nested = research / "nested" / "deep"
    nested.mkdir(parents=True)
    assert research.resolve().is_relative_to(base)

    ollama = "# OLLAMA HANDS\nprobe\n\u03a9\n"
    (research / "OLLAMA_HANDS.md").write_bytes(ollama.encode("utf-8"))
    (research / "EMPTY_HANDS.md").write_bytes(b"")
    (research / "MiXeD_HANDS.md").write_bytes(b"mixed\n")
    (research / "RESEARCH_1.md").write_bytes(b"not a hands file\n")
    (research / "hands.md").write_bytes(b"no underscore suffix\n")
    (research / "skip_HANDS.txt").write_bytes(b"wrong suffix\n")
    (research / "nested" / "XAI_GROK_HANDS.md").write_bytes(b"# XAI\n")
    (nested / "DEEP_HANDS.md").write_bytes(b"deep\n")

    rows = inventory_hands(research)
    by_name = {Path(row["path"]).name: row for row in rows}
    assert set(by_name) == {
        "OLLAMA_HANDS.md",
        "EMPTY_HANDS.md",
        "MiXeD_HANDS.md",
        "XAI_GROK_HANDS.md",
        "DEEP_HANDS.md",
    }
    assert by_name["OLLAMA_HANDS.md"]["maker"] == "OLLAMA"
    assert by_name["XAI_GROK_HANDS.md"]["maker"] == "XAI_GROK"
    assert by_name["MiXeD_HANDS.md"]["maker"] == "MiXeD"
    assert by_name["EMPTY_HANDS.md"]["maker"] == "EMPTY"
    assert by_name["DEEP_HANDS.md"]["maker"] == "DEEP"
    assert by_name["OLLAMA_HANDS.md"]["bytes"] == len(ollama.encode("utf-8"))
    assert by_name["EMPTY_HANDS.md"]["bytes"] == 0
    assert by_name["OLLAMA_HANDS.md"]["bytes"] != len(ollama)

    paths = [row["path"] for row in rows]
    assert paths == [str(path) for path in sorted(Path(item) for item in paths)]
    for row in rows:
        assert set(row) == {"maker", "path", "bytes", "mtime", "mtime_iso"}
        assert isinstance(row["mtime"], float)
        assert row["mtime"] == Path(row["path"]).stat().st_mtime
        assert isinstance(row["bytes"], int)
        assert Path(row["path"]).resolve().is_relative_to(base)


def test_inventory_hands_not_a_directory(tmp_path: Path) -> None:
    missing = tmp_path / "missing-research"
    assert not missing.exists()
    assert inventory_hands(missing) == []
    as_file = tmp_path / "research-file"
    as_file.write_bytes(b"not a directory\n")
    assert inventory_hands(as_file) == []


def test_plan_argv_lists_do_not_spawn(tmp_path: Path) -> None:
    root = tmp_path / "runtime-root"
    script = str(_MODULE_PATH.resolve())
    root_s = str(root.resolve())

    once = plan_once_argv(str(root))
    assert isinstance(once, list)
    assert once == ["py", "-3.14", script, "--root", root_s, "--once"]
    assert all(isinstance(part, str) for part in once)

    task = plan_task_argv(str(root))
    assert isinstance(task, list)
    assert all(isinstance(part, str) for part in task)
    assert task[:5] == ["schtasks", "/create", "/tn", _discover.TASK_NAME, "/tr"]
    assert task[6:] == ["/sc", "HOURLY", "/mo", "1", "/f"]
    assert "/rl" not in task
    tr = task[5]
    assert isinstance(tr, str)
    assert script in tr
    assert root_s in tr
    assert "--root" in tr
    assert "--once" in tr
    assert "hush.py" in tr
    assert "python" in tr.lower()
