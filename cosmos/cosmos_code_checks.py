#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Non-AI checkers on a saved CCrew reply, before WOMBAT.

Runs, in order, and records every result:

    python -m py_compile
    python -m ruff check
    python -m mypy
    python -m pytest

Rows go to state/code_checks.db table code_checks. A missing tool is a
row too (status MISSING), never a silent skip. WOMBAT is not called here.

    py -3.14 cosmos\\cosmos_code_checks.py --selftest
"""
from __future__ import annotations

import hashlib
import os
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

SCHEMA = "cosmos-code-checks/1"
TOOLS = ("py_compile", "ruff", "mypy", "pytest")
OUT_CAP = 16000
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def db_path(paths) -> Path:
    path = paths.state("code_checks.db")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect(paths) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path(paths)))
    con.execute(
        "CREATE TABLE IF NOT EXISTS code_checks ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "at TEXT NOT NULL,"
        "order_id TEXT,"
        "tool TEXT NOT NULL,"
        "status TEXT NOT NULL,"
        "returncode INTEGER,"
        "target TEXT,"
        "source_sha TEXT,"
        "stdout TEXT,"
        "stderr TEXT)"
    )
    con.execute(
        "CREATE INDEX IF NOT EXISTS idx_code_checks_order ON code_checks(order_id)"
    )
    return con


def _clip(text: str) -> str:
    raw = text or ""
    if len(raw) <= OUT_CAP:
        return raw
    return raw[:OUT_CAP] + "\n…[truncated]"


def _status(tool: str, rc: int | None) -> str:
    if rc is None:
        return "MISSING"
    if tool == "pytest" and rc == 5:
        return "NO_TESTS"
    if rc == 0:
        return "PASS"
    return "FAIL"


def _argv(tool: str, target: Path) -> list[str]:
    py = sys.executable
    if tool == "py_compile":
        return [py, "-m", "py_compile", str(target)]
    if tool == "ruff":
        return [py, "-m", "ruff", "check", str(target)]
    if tool == "mypy":
        return [py, "-m", "mypy", str(target), "--follow-imports=skip"]
    if tool == "pytest":
        return [
            py, "-m", "pytest", str(target),
            "--noconftest", "-p", "no:cacheprovider", "-q", "--tb=line",
        ]
    raise ValueError(tool)


def _run_one(tool: str, target: Path, cwd: Path) -> tuple[int | None, str, str]:
    try:
        proc = subprocess.run(
            _argv(tool, target),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            shell=False,
            creationflags=CREATE_NO_WINDOW,
        )
    except FileNotFoundError as e:
        return None, "", f"{type(e).__name__}: {e}"
    except subprocess.TimeoutExpired as e:
        out = e.stdout if isinstance(e.stdout, str) else ""
        err = e.stderr if isinstance(e.stderr, str) else ""
        return 124, out, (err or "timeout 60s")
    return int(proc.returncode), proc.stdout or "", proc.stderr or ""


def materialize(text: str, filename: str, folder: Path) -> Path | None:
    """Write the reply where the four tools can see it. NONE has no file."""
    body = text or ""
    if body.lstrip().startswith("NONE"):
        return None
    name = Path(filename or "reply.py").name
    if not name.endswith(".py"):
        name = "reply.py"
    dest = folder / name
    dest.write_text(body, encoding="utf-8")
    return dest


def run_code_checks(paths, rec: dict, text: str) -> list[dict]:
    """Run all four tools. Insert one row each. Return the rows."""
    rec = rec or {}
    oid = str(rec.get("order_id") or "")
    fname = Path(str(rec.get("_output_path") or "reply.py")).name
    sha = hashlib.sha256((text or "").encode("utf-8")).hexdigest()
    rows: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="cosmos-checks-") as td:
        folder = Path(td)
        target = materialize(text or "", fname, folder)
        for tool in TOOLS:
            if target is None:
                rc, out, err = None, "", "no code (coder NONE)"
                status = "NO_CODE"
            else:
                rc, out, err = _run_one(tool, target, folder)
                status = _status(tool, rc)
            row = {
                "schema": SCHEMA,
                "at": _iso_now(),
                "order_id": oid,
                "tool": tool,
                "status": status,
                "returncode": rc,
                "target": target.name if target else "",
                "source_sha": sha,
                "stdout": _clip(out),
                "stderr": _clip(err),
            }
            rows.append(row)
    con = _connect(paths)
    try:
        for row in rows:
            con.execute(
                "INSERT INTO code_checks "
                "(at, order_id, tool, status, returncode, target, source_sha, stdout, stderr) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    row["at"], row["order_id"], row["tool"], row["status"],
                    row["returncode"], row["target"], row["source_sha"],
                    row["stdout"], row["stderr"],
                ),
            )
        con.commit()
    finally:
        con.close()
    return rows


def fails_of(rows: list[dict]) -> str:
    """Text WOMBAT can use. NO_TESTS and PASS are not failures."""
    parts = []
    for row in rows:
        if row.get("status") not in ("FAIL", "MISSING"):
            continue
        detail = (row.get("stderr") or row.get("stdout") or "").strip().splitlines()
        line = detail[0] if detail else row["status"]
        parts.append(f"{row['tool']}: {line[:240]}")
    return "; ".join(parts)


def rows_for(paths, order_id: str) -> list[dict]:
    con = _connect(paths)
    try:
        cur = con.execute(
            "SELECT tool, status, returncode, stdout, stderr FROM code_checks "
            "WHERE order_id = ? ORDER BY id",
            (order_id,),
        )
        return [
            {
                "tool": r[0], "status": r[1], "returncode": r[2],
                "stdout": r[3], "stderr": r[4],
            }
            for r in cur.fetchall()
        ]
    finally:
        con.close()


def _selftest() -> int:
    import tempfile as _tf

    from cosmos_paths import CosmosPaths, write_sentinel

    ok = True

    def check(label, cond):
        nonlocal ok
        print(("  OK  " if cond else "  FAIL") + " " + label)
        if not cond:
            ok = False

    with _tf.TemporaryDirectory() as td:
        root = Path(td)
        write_sentinel(root, tree_id="code-checks-test")
        (root / "state").mkdir()
        paths = CosmosPaths(root)
        good = run_code_checks(
            paths,
            {"order_id": "wo-good", "_output_path": "ping.py"},
            "def ping():\n    return 1\n",
        )
        names = [r["tool"] for r in good]
        check("all four tools ran on the reply", names == list(TOOLS))
        check("py_compile passed", good[0]["status"] == "PASS" and good[0]["returncode"] == 0)
        stored = rows_for(paths, "wo-good")
        check("database has one row per tool",
              [r["tool"] for r in stored] == list(TOOLS)
              and db_path(paths).is_file())
        bad = run_code_checks(
            paths,
            {"order_id": "wo-bad", "_output_path": "ping.py"},
            "def ping(\n",
        )
        check("py_compile records a syntax failure",
              bad[0]["tool"] == "py_compile" and bad[0]["status"] == "FAIL")
        check("ruff, mypy, and pytest still ran",
              [r["tool"] for r in bad[1:]] == ["ruff", "mypy", "pytest"])
        check("failure text names the tool",
              "py_compile:" in fails_of(bad))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("cosmos_code_checks: --selftest", file=sys.stderr)
    raise SystemExit(2)
