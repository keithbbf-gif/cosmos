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
import re
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


def _cdeck_root() -> Path:
    return Path(__file__).resolve().parents[1] / "builds" / "cdeck"


def point_local_tree(folder: Path) -> list[str]:
    """Junction ui and src-tauri at the live tree. Read only. No copy. No :8770."""
    made: list[str] = []
    live_root = _cdeck_root()
    if not live_root.is_dir():
        return made
    try:
        folder.resolve().relative_to(live_root.resolve())
        return made
    except ValueError:
        pass
    for name in ("ui", "src-tauri"):
        live = live_root / name
        link = folder / name
        if link.exists() or not live.is_dir():
            continue
        if os.name == "nt":
            proc = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(live)],
                capture_output=True,
                text=True,
                creationflags=CREATE_NO_WINDOW,
            )
            if proc.returncode != 0:
                raise OSError(proc.stderr.strip() or proc.stdout.strip() or "mklink failed")
        else:
            link.symlink_to(live, target_is_directory=True)
        made.append(name)
    return made


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
        if tool == "pytest":
            point_local_tree(cwd)
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


FAKE_FILE_NAMES = frozenset({
    "python", "file", "code", "output", "reply.py", "a/python", "b/python",
})


def extract_file_blocks(text: str) -> list[dict]:
    """Split a unified diff into FILE blocks. Fake paths are kind=FAKE_PATH."""
    raw = text or ""
    s = raw.lstrip()
    if not s:
        return [{"path": "", "body": "", "kind": "EMPTY"}]
    if s.startswith("NONE"):
        return []
    if not s.startswith("diff --git"):
        return [{"path": "", "body": raw, "kind": "NOT_DIFF"}]
    blocks: list[dict] = []
    parts = re.split(r"(?m)^diff --git ", s)
    for part in parts[1:]:
        plus_path = ""
        m = re.search(r"(?m)^\+\+\+ b/(.+)$", part)
        if m:
            plus_path = m.group(1).strip()
        if plus_path == "/dev/null":
            continue
        plus: list[str] = []
        for line in part.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                plus.append(line[1:])
        body = "\n".join(plus)
        if plus:
            body += "\n"
        kind = "OK"
        norm = plus_path.replace("\\", "/").strip()
        base = Path(norm).name.lower() if norm else ""
        if (not norm or norm.lower() in FAKE_FILE_NAMES or base in FAKE_FILE_NAMES
                or norm.lower() in ("python", "a/python")):
            kind = "FAKE_PATH"
        blocks.append({"path": plus_path or "python", "body": body, "kind": kind})
    if not blocks:
        return [{"path": "", "body": "", "kind": "NO_BLOCKS"}]
    return blocks


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
        stripped = (text or "").lstrip()
        if stripped.startswith("NONE"):
            for tool in TOOLS:
                rows.append({
                    "schema": SCHEMA, "at": _iso_now(), "order_id": oid,
                    "tool": tool, "status": "NO_CODE", "returncode": None,
                    "target": "", "source_sha": sha,
                    "stdout": "", "stderr": "no code (coder NONE)",
                })
        elif stripped.startswith("diff --git"):
            blocks = extract_file_blocks(text or "")
            bad = [b for b in blocks if b.get("kind") != "OK"]
            py_blocks = [
                b for b in blocks
                if b.get("kind") == "OK"
                and str(b.get("path") or "").endswith(".py")
            ]
            if bad or not py_blocks:
                why = (
                    (bad[0]["kind"] + ": " + (bad[0].get("path") or ""))
                    if bad else "NO_PY_FILE_BLOCK"
                )
                for tool in TOOLS:
                    rows.append({
                        "schema": SCHEMA, "at": _iso_now(), "order_id": oid,
                        "tool": tool, "status": "FAIL", "returncode": 2,
                        "target": (bad[0].get("path") if bad else ""),
                        "source_sha": sha, "stdout": "",
                        "stderr": why,
                    })
            else:
                for blk in py_blocks:
                    target = folder / Path(blk["path"]).name
                    target.write_text(blk["body"], encoding="utf-8")
                    for tool in TOOLS:
                        rc, out, err = _run_one(tool, target, folder)
                        rows.append({
                            "schema": SCHEMA, "at": _iso_now(),
                            "order_id": oid, "tool": tool,
                            "status": _status(tool, rc),
                            "returncode": rc, "target": target.name,
                            "source_sha": sha,
                            "stdout": _clip(out), "stderr": _clip(err),
                        })
        else:
            target = materialize(text or "", fname, folder)
            for tool in TOOLS:
                if target is None:
                    rc, out, err = None, "", "no code (coder NONE)"
                    status = "NO_CODE"
                else:
                    rc, out, err = _run_one(tool, target, folder)
                    status = _status(tool, rc)
                rows.append({
                    "schema": SCHEMA, "at": _iso_now(), "order_id": oid,
                    "tool": tool, "status": status, "returncode": rc,
                    "target": target.name if target else "",
                    "source_sha": sha,
                    "stdout": _clip(out), "stderr": _clip(err),
                })
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
        fake = extract_file_blocks(
            "diff --git a/python b/python\n+++ b/python\n+x=1\n")
        check("fake path a/python is FAKE_PATH",
              fake and fake[0]["kind"] == "FAKE_PATH")
        fake_rows = run_code_checks(
            paths, {"order_id": "wo-fake", "_output_path": "x.py"},
            "diff --git a/python b/python\n+++ b/python\n+x=1\n",
        )
        check("fake FILE block fails 4Cs",
              fake_rows[0]["status"] == "FAIL" and "FAKE_PATH" in (fake_rows[0]["stderr"] or ""))
        real_diff = (
            "diff --git a/cosmos/ping.py b/cosmos/ping.py\n"
            "+++ b/cosmos/ping.py\n"
            "+def ping():\n+    return 1\n"
        )
        real_blocks = extract_file_blocks(real_diff)
        check("real cosmos path extracts OK",
              real_blocks and real_blocks[0]["kind"] == "OK"
              and real_blocks[0]["path"] == "cosmos/ping.py")
        scratch = root / "pytest-point"
        scratch.mkdir()
        ui = _cdeck_root() / "ui" / "app.js"
        if not ui.is_file():
            check("pytest pointer skipped, cdeck ui not populated", True)
        else:
            before = ui.stat().st_mtime
            made = point_local_tree(scratch)
            seen = (scratch / "ui" / "app.js").is_file()
            after = ui.stat().st_mtime
            check("pytest pointer sees live ui and does not write it",
                  made == ["ui", "src-tauri"] and seen and before == after)
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("cosmos_code_checks: --selftest", file=sys.stderr)
    raise SystemExit(2)
