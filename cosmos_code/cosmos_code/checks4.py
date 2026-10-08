"""The 4Cs: py_compile, ruff, mypy, pytest.

A missing tool is MISSING, never a silent skip. pytest exit 5 is NO_TESTS.
NONE is NO_CODE. Prose does not reach a judge. FAIL and MISSING block.
"""

from __future__ import annotations

import hashlib
import importlib.util
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

TOOLS = ("py_compile", "ruff", "mypy", "pytest")
BLOCKING = frozenset({"FAIL", "MISSING"})


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _row(
    rec: dict[str, Any],
    tool: str,
    status: str,
    returncode: int,
    target: str,
    source_sha: str,
    stdout: str = "",
    stderr: str = "",
) -> dict[str, Any]:
    return {
        "schema": "cosmos-code-checks/1",
        "order_id": str(rec.get("order_id") or ""),
        "tool": tool,
        "status": status,
        "returncode": returncode,
        "target": target,
        "source_sha": source_sha,
        "stdout": stdout[-4000:],
        "stderr": stderr[-4000:],
    }


def fails_of(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("status") in BLOCKING]


def reaches_judge(rows: list[dict[str, Any]]) -> bool:
    if any(row.get("status") == "PROSE" for row in rows):
        return False
    return not fails_of(rows)


def split_unified_diff(text: str) -> list[tuple[str, str]]:
    """Split a unified diff into (basename, body). Deletions to /dev/null are skipped."""
    files: list[tuple[str, str]] = []
    name: str | None = None
    body: list[str] = []
    in_hunk = False

    def flush() -> None:
        nonlocal name, body
        if name and name != "/dev/null":
            files.append((Path(name).name, "\n".join(body) + ("\n" if body else "")))
        body = []

    for line in text.replace("\r\n", "\n").splitlines():
        if line.startswith("diff --git "):
            flush()
            name = None
            in_hunk = False
            continue
        if line.startswith("+++ "):
            raw = line[4:].strip()
            name = raw[2:] if raw.startswith("b/") else raw
            continue
        if line.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            body.append(line[1:])
        elif line.startswith(" "):
            body.append(line[1:])
    flush()
    return files


def _first(text: str) -> str:
    for line in text.replace("\r\n", "\n").splitlines():
        if line.strip():
            return line.strip()
    return ""


def _py_open(line: str) -> bool:
    return line.startswith(("def ", "class ", "import ", "from "))


def _module(name: str) -> list[str] | None:
    """A tool counts as present when this interpreter can run it. PATH is not required."""
    if importlib.util.find_spec(name) is None:
        return None
    return [sys.executable, "-m", name]


def _run(argv: list[str], cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        argv,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _tool_rows(work: Path, rec: dict[str, Any], target: Path, body: str) -> list[dict[str, Any]]:
    digest = _sha(body)
    name = target.name
    rows: list[dict[str, Any]] = []
    try:
        py_compile.compile(str(target), doraise=True)
        rows.append(_row(rec, "py_compile", "PASS", 0, name, digest))
    except py_compile.PyCompileError as exc:
        rows.append(_row(rec, "py_compile", "FAIL", 1, name, digest, stderr=str(exc)))

    ruff = _module("ruff")
    if not ruff:
        rows.append(_row(rec, "ruff", "MISSING", 127, name, digest, stderr="ruff not installed"))
    else:
        code, out, err = _run([*ruff, "check", "--no-cache", str(target)], work)
        rows.append(_row(rec, "ruff", "PASS" if code == 0 else "FAIL", code, name, digest, out, err))

    mypy = _module("mypy")
    if not mypy:
        rows.append(_row(rec, "mypy", "MISSING", 127, name, digest, stderr="mypy not installed"))
    else:
        code, out, err = _run(
            [*mypy, "--follow-imports=silent", "--ignore-missing-imports", str(target)],
            work,
        )
        rows.append(_row(rec, "mypy", "PASS" if code == 0 else "FAIL", code, name, digest, out, err))

    pytest_mod = _module("pytest")
    if not pytest_mod:
        rows.append(_row(rec, "pytest", "MISSING", 127, name, digest, stderr="pytest not installed"))
    else:
        code, out, err = _run([*pytest_mod, "-q", "--noconftest", str(target)], work)
        if code == 5:
            status = "NO_TESTS"
        elif code == 0:
            status = "PASS"
        else:
            status = "FAIL"
        rows.append(_row(rec, "pytest", status, code, name, digest, out, err))
    return rows


def run_code_checks(work: Path, rec: dict[str, Any], text: str) -> list[dict[str, Any]]:
    """Check one reply. A unified diff is split; each file is checked on its own."""
    body = text.replace("\r\n", "\n")
    first = _first(body)
    digest = _sha(body)
    if first == "NONE":
        return [_row(rec, "py_compile", "NO_CODE", 0, str(rec.get("_output_path") or "reply.py"), digest)]
    if not first.startswith("diff --git") and not _py_open(first) and not first.startswith("{"):
        return [_row(rec, "form", "PROSE", 0, "reply", digest)]

    pieces: list[tuple[str, str]]
    if first.startswith("diff --git"):
        pieces = split_unified_diff(body)
        if not pieces:
            return [_row(rec, "form", "FAIL", 1, "diff", digest, stderr="diff produced no file body")]
    else:
        name = str(rec.get("_output_path") or "reply.py")
        pieces = [(Path(name).name, body if body.endswith("\n") else body + "\n")]

    rows: list[dict[str, Any]] = []
    work.mkdir(parents=True, exist_ok=True)
    for name, file_body in pieces:
        if not name.endswith(".py"):
            rows.append(_row(rec, "py_compile", "NO_CODE", 0, name, _sha(file_body)))
            continue
        dest = work / name
        dest.write_text(file_body, encoding="utf-8", newline="\n")
        rows.extend(_tool_rows(work, rec, dest, file_body))
    return rows


def check_package(root: Path) -> list[dict[str, Any]]:
    """Run the 4Cs on a package tree. One receipt row per tool."""
    rec = {"order_id": root.name}
    digest = _sha(str(root))
    rows: list[dict[str, Any]] = []
    files = [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]
    errors: list[str] = []
    for path in files:
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{path.name}: {exc}")
    rows.append(_row(
        rec, "py_compile", "FAIL" if errors else "PASS",
        1 if errors else 0, str(root), digest, stderr="\n".join(errors),
    ))
    for tool, extra in (
        ("ruff", ["check", "--no-cache", str(root)]),
        ("mypy", [str(root)]),
        ("pytest", ["-q", str(root)]),
    ):
        base = _module(tool)
        if base is None:
            rows.append(_row(rec, tool, "MISSING", 127, str(root), digest, stderr=f"{tool} not installed"))
            continue
        code, out, err = _run([*base, *extra], root if root.is_dir() else root.parent)
        if tool == "pytest" and code == 5:
            status = "NO_TESTS"
        elif code == 0:
            status = "PASS"
        else:
            status = "FAIL"
        rows.append(_row(rec, tool, status, code, str(root), digest, out, err))
    return rows
