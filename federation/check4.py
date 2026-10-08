"""Run py_compile, ruff, mypy, and pytest for one proposal slug or the shared package.

Usage, from V:\\streams\\federation:

    py -3.14 check4.py
    py -3.14 check4.py wizard
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _run(argv: list[str]) -> int:
    print("+", " ".join(argv), flush=True)
    try:
        completed = subprocess.run(argv, cwd=ROOT, check=False)
    except OSError as exc:
        print(f"MISSING {argv[0]}: {exc}")
        return 127
    return int(completed.returncode)


def _py_files(targets: list[str]) -> list[str]:
    files: list[str] = []
    for target in targets:
        path = ROOT / target
        if path.is_dir():
            files.extend(str(item.relative_to(ROOT)) for item in sorted(path.rglob("*.py")))
        elif path.suffix == ".py":
            files.append(target)
    return files


def main(slug: str | None) -> int:
    py = sys.executable
    if slug is None:
        targets = [
            "cosmos_federation",
            "tests/test_product.py",
            "conftest.py",
            "check4.py",
        ]
        pytest_target = "tests/test_product.py"
    else:
        folder = ROOT / "proposals" / slug
        if not folder.is_dir():
            print(f"MISSING proposals/{slug}")
            return 127
        targets = [f"proposals/{slug}"]
        pytest_target = f"proposals/{slug}"
    code = 0
    sources = _py_files(targets)
    if not sources:
        print("NO_TESTS")
        return 1
    code = max(code, _run([py, "-m", "py_compile", *sources]))
    ruff = _run([py, "-m", "ruff", "check", *targets])
    code = 127 if ruff == 127 else max(code, ruff)
    mypy = _run([py, "-m", "mypy", "--strict", *targets])
    code = 127 if mypy == 127 else max(code, mypy)
    pytest = _run([
        py, "-m", "pytest", pytest_target,
        "-q", "-p", "no:cacheprovider", "--tb=short",
    ])
    if pytest == 5:
        print("NO_TESTS")
        return max(code, 1)
    code = 127 if pytest == 127 else max(code, pytest)
    return code


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    raise SystemExit(main(arg))
