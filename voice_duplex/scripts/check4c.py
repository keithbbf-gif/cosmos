"""Run the four checkers on this package and write a report beside it.

The report is written beside this package. It is not copied to ``live/state``.
A missing tool is MISSING, not a pass. pytest exit 5 is NO_TESTS, not a pass.
"""

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "4c-report.json"


def _python_files() -> list[Path]:
    found: list[Path] = []
    for path in ROOT.rglob("*.py"):
        if "android" in path.parts or "__pycache__" in path.parts:
            continue
        found.append(path)
    return found


def _compile() -> dict[str, object]:
    failed: list[str] = []
    for path in _python_files():
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            failed.append(str(exc))
    if failed:
        return {"status": "FAIL", "detail": "\n".join(failed)}
    return {"status": "PASS", "files": len(_python_files())}


def _tool(module: str, args: list[str]) -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, "-m", module, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    detail = (proc.stdout + "\n" + proc.stderr).strip()
    if "No module named" in detail:
        return {"status": "MISSING", "detail": detail[-1000:]}
    if module == "pytest" and proc.returncode == 5:
        return {"status": "NO_TESTS", "detail": detail[-1000:]}
    if proc.returncode == 0:
        return {"status": "PASS", "detail": detail[-2000:]}
    return {"status": "FAIL", "code": proc.returncode, "detail": detail[-4000:]}


def main() -> int:
    report: dict[str, dict[str, object]] = {
        "py_compile": _compile(),
        "ruff": _tool(
            "ruff",
            ["check", "cosmos_voice_duplex", "tests", "scripts", "--no-cache"],
        ),
        "mypy": _tool("mypy", ["cosmos_voice_duplex", "tests", "scripts"]),
        "pytest": _tool("pytest", ["-q"]),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    bad = [name for name, row in report.items() if row.get("status") != "PASS"]
    for name, row in report.items():
        print(f"{name}: {row.get('status')}")
    if bad:
        print("4C not green: " + ", ".join(bad))
        return 1
    print(f"4C report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
