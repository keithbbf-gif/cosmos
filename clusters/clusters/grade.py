"""4C receipt for one Clusters module.

The four checkers are py_compile, ruff, mypy, and pytest. A missing checker
is MISSING, exit 127, and that is not a pass. pytest exit 5 is NO_TESTS.
The receipt is written under V:\\streams\\clusters\\receipts. This module
does not write the live tree.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent
ROOT = PLUGIN.parent
RECEIPTS = Path(r"V:\streams\clusters\receipts")


def _tool(name: str) -> list[str] | None:
    if importlib.util.find_spec(name) is None:
        return None
    return [sys.executable, "-m", name]


def _run(argv: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        argv,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def grade_module(name: str) -> dict:
    """Grade clusters/<name>.py and tests/test_<name>.py when that test exists."""
    source = PLUGIN / f"{name}.py"
    if not source.is_file():
        raise FileNotFoundError(source)
    checks: list[dict] = []
    try:
        py_compile.compile(str(source), doraise=True)
        checks.append({"tool": "py_compile", "status": "PASS", "code": 0})
    except py_compile.PyCompileError as exc:
        checks.append({"tool": "py_compile", "status": "FAIL", "code": 1, "stderr": str(exc)})

    ruff = _tool("ruff")
    if ruff is None:
        checks.append({"tool": "ruff", "status": "MISSING", "code": 127})
    else:
        code, out, err = _run([*ruff, "check", "--no-cache", str(source)])
        checks.append({
            "tool": "ruff",
            "status": "PASS" if code == 0 else "FAIL",
            "code": code,
            "stdout": out[-2000:],
            "stderr": err[-2000:],
        })

    mypy = _tool("mypy")
    if mypy is None:
        checks.append({"tool": "mypy", "status": "MISSING", "code": 127})
    else:
        code, out, err = _run([
            *mypy, "--follow-imports=silent", "--ignore-missing-imports", str(source),
        ])
        checks.append({
            "tool": "mypy",
            "status": "PASS" if code == 0 else "FAIL",
            "code": code,
            "stdout": out[-2000:],
            "stderr": err[-2000:],
        })

    test = ROOT / "tests" / f"test_{name}.py"
    pytest_bin = _tool("pytest")
    if pytest_bin is None:
        checks.append({"tool": "pytest", "status": "MISSING", "code": 127})
    elif not test.is_file():
        checks.append({"tool": "pytest", "status": "NO_TESTS", "code": 5})
    else:
        code, out, err = _run([*pytest_bin, "-q", str(test)])
        if code == 5:
            status = "NO_TESTS"
        elif code == 0:
            status = "PASS"
        else:
            status = "FAIL"
        checks.append({
            "tool": "pytest",
            "status": status,
            "code": code,
            "stdout": out[-2000:],
            "stderr": err[-2000:],
        })

    blocked = [row["tool"] for row in checks if row["status"] in ("FAIL", "MISSING")]
    receipt = {"module": name, "checks": checks, "blocked": blocked, "ok": not blocked}
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    (RECEIPTS / f"{name}.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt


def main(argv: list[str] | None = None) -> int:
    names = argv if argv is not None else sys.argv[1:]
    if not names:
        print("usage: python -m clusters.grade <module> [module...]")
        return 2
    failed = 0
    for name in names:
        receipt = grade_module(name)
        print(f"{name}: {'PASS' if receipt['ok'] else 'BLOCKED ' + ','.join(receipt['blocked'])}")
        if not receipt["ok"]:
            failed = 1
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
