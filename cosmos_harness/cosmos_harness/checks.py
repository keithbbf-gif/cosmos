"""The four checkers, in Keith's order for this package: py_compile, ruff, mypy, pytest.

A tool this interpreter cannot import is ``UNAVAILABLE``. That row blocks
done. It is not a pass and it is not a skip. pytest exit 5 is ``NO_TESTS``,
which also blocks a coding seat. ``PROSE`` is reserved for a mission that
never produced a Python file.

The product package still spells a missing tool ``MISSING``. Same fact.
This harness uses the word from the 2026-09-30 standalone record.
"""

from __future__ import annotations

import importlib.util
import os
import py_compile
import subprocess
import sys
from pathlib import Path

from cosmos_harness.layers import scrub_env


def _present(name: str) -> list[str] | None:
    if importlib.util.find_spec(name) is None:
        return None
    return [sys.executable, "-m", name]


def _run(argv: list[str], cwd: Path, *, timeout: float = 120.0) -> tuple[int, str, str]:
    """Run one checker. A hung checker is exit 124, which is not a pass.

    Checkers stay outside the active-process job. That limit is for one
    oracle child, not for pytest collecting a tree.
    """
    env = scrub_env(dict(os.environ))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        proc = subprocess.run(
            argv,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def grade(root: Path) -> list[dict[str, str]]:
    """One row per checker. Status is PASS, FAIL, UNAVAILABLE, NO_TESTS, or PROSE.

    pytest executes the tests. Collection alone is not a pass. Exit 5 is
    ``NO_TESTS``. A checker that exceeds its timeout is ``FAIL``.
    """
    files = [path for path in root.rglob("*.py") if "__pycache__" not in path.parts and "_delme" not in path.parts]
    rows: list[dict[str, str]] = []
    if not files:
        rows.append({"tool": "py_compile", "status": "PROSE"})
        for tool in ("ruff", "mypy", "pytest"):
            rows.append({"tool": tool, "status": "PROSE"})
        return rows
    errors: list[str] = []
    for path in files:
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{path.name}: {exc}")
    rows.append({"tool": "py_compile", "status": "FAIL" if errors else "PASS"})
    for tool, extra in (
        ("ruff", ["check", "--no-cache", str(root)]),
        ("mypy", ["--no-error-summary", str(root)]),
        ("pytest", ["-q", "-p", "no:cacheprovider", "--tb=no", str(root)]),
    ):
        base = _present(tool)
        if base is None:
            rows.append({"tool": tool, "status": "UNAVAILABLE"})
            continue
        code, _out, _err = _run([*base, *extra], root)
        if tool == "pytest" and code == 5:
            status = "NO_TESTS"
        elif code == 0:
            status = "PASS"
        else:
            status = "FAIL"
        rows.append({"tool": tool, "status": status})
    return rows
