"""Run py_compile, ruff, mypy, and pytest.

A missing checker is MISSING and the process exits 127.
Pytest exit 5 is NO_TESTS and blocks. FAIL blocks.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable


def _python_files() -> list[Path]:
    found: list[Path] = []
    for folder in (ROOT / "cosmos_hermes", ROOT / "tests", ROOT / "proposals"):
        if not folder.exists():
            continue
        found.extend(path for path in folder.rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(found)


def _run(argv: list[str]) -> tuple[str, int, str]:
    try:
        completed = subprocess.run(
            argv,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except FileNotFoundError:
        return "MISSING", 127, argv[0]
    except subprocess.TimeoutExpired:
        return "FAIL", 1, "timeout"
    text = (completed.stdout + completed.stderr).strip()
    if completed.returncode == 0:
        return "PASS", 0, text[-400:]
    return "FAIL", completed.returncode, text[-800:]


def main() -> int:
    files = _python_files()
    if not files:
        print("NONE no python files")
        return 1
    rows: list[tuple[str, str, int, str]] = []

    compile_argv = [PY, "-m", "py_compile", *[str(path) for path in files]]
    rows.append(("py_compile", *_run(compile_argv)))

    ruff = _run([PY, "-m", "ruff", "check", "cosmos_hermes", "tests", "proposals", "conftest.py", "check4.py"])
    if ruff[0] == "FAIL" and "No module named ruff" in ruff[2]:
        ruff = ("MISSING", 127, ruff[2])
    rows.append(("ruff", *ruff))

    mypy_targets = ["cosmos_hermes", "tests/test_kernel.py", "conftest.py", "check4.py"]
    proposals = ROOT / "proposals"
    if proposals.is_dir():
        for child in sorted(proposals.iterdir()):
            if not child.is_dir():
                continue
            module = child / f"{child.name}.py"
            test = child / f"test_{child.name}.py"
            if module.exists():
                mypy_targets.append(str(module.relative_to(ROOT)))
            if test.exists():
                mypy_targets.append(str(test.relative_to(ROOT)))
    mypy = _run([PY, "-m", "mypy", "--strict", *mypy_targets])
    if mypy[0] == "FAIL" and "No module named mypy" in mypy[2]:
        mypy = ("MISSING", 127, mypy[2])
    rows.append(("mypy", *mypy))

    pytest = _run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=line"])
    if pytest[0] == "FAIL" and "No module named pytest" in pytest[2]:
        pytest = ("MISSING", 127, pytest[2])
    elif pytest[1] == 5:
        pytest = ("NO_TESTS", 5, pytest[2])
    rows.append(("pytest", *pytest))

    blocked = False
    for name, status, code, detail in rows:
        print(f"{name} {status} exit={code}")
        if detail and status != "PASS":
            print(detail)
        if status != "PASS":
            blocked = True
    if any(status == "MISSING" for _, status, _, _ in rows):
        return 127
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
