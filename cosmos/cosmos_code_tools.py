#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coding-tool parity: Read, Write, Edit, Glob, Grep, Bash.

cosmos_tools.py is the contract registry (ledger dispositions). These six
are the missing invoke bite. Every path must sit under an injected
allowlist. Nothing here opens the ledger, the kernel, or a shell.

Bash is not a shell. argv is a list, shell=False, and the first token
must be on a short allowlist. grok.exe is refused.

    py -3.14 cosmos\\cosmos_code_tools.py --selftest
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

SCHEMA = "cosmos-code-tools/1"
VERBS = ("Read", "Write", "Edit", "Glob", "Grep", "Bash")
READ_MAX_LINES = 2000
READ_MAX_BYTES = 2_000_000
WRITE_MAX_BYTES = 1_000_000
GLOB_CAP = 200
GREP_CAP = 50
BASH_TIMEOUT_S = 30
BASH_TIMEOUT_CAP = 120
BASH_ALLOW = {"py", "python", "python3", "pytest", "git"}
BLOCK_NAMES = {".cosmos-root.json", "api_token.txt", ".env"}
BLOCK_PARTS = {"ledger", ".git"}


class CodeToolError(RuntimeError):
    """kind in {BAD_INPUT, REFUSED, NOT_FOUND, TOO_BIG, AMBIGUOUS}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__("[%s] %s" % (kind, detail))


def declare_on(contracts) -> list:
    """Record the six verbs on a ToolContracts. Skips names already declared.

    Does not open a ledger by itself. The caller owns the ledger.
    """
    state = contracts.state()
    declared = []
    for row in contract_rows():
        if row["name"] in state:
            continue
        contracts.declare(row["name"], row["verbs"], row["behavior"])
        declared.append(row["name"])
    return declared


def contract_rows() -> list[dict]:
    """Declare payloads. Does not open a ledger."""
    behavior = {
        "Read": "read a text window under the allowlist",
        "Write": "replace a file under the allowlist",
        "Edit": "exact one-match string replace under the allowlist",
        "Glob": "list paths matching a pattern under the allowlist",
        "Grep": "search file text under the allowlist",
        "Bash": "run an allowlisted argv with shell=False under the allowlist",
    }
    return [
        {"name": name, "verbs": [name], "behavior": behavior[name],
         "schema": SCHEMA}
        for name in VERBS
    ]


class CodeTools:
    def __init__(self, roots):
        found = []
        for root in list(roots or []):
            path = Path(root).resolve()
            if not path.is_dir():
                raise CodeToolError("BAD_INPUT", "allowlist root is not a directory: %s" % root)
            found.append(path)
        if not found:
            raise CodeToolError("BAD_INPUT", "allowlist is empty")
        self.roots = found

    def _under(self, path) -> Path:
        raw = Path(path)
        if not raw.is_absolute():
            if len(self.roots) != 1:
                raise CodeToolError("BAD_INPUT", "relative path needs exactly one root")
            raw = self.roots[0] / raw
        try:
            resolved = raw.resolve()
        except OSError as e:
            raise CodeToolError("REFUSED", "path did not resolve: %s" % e) from e
        for root in self.roots:
            try:
                resolved.relative_to(root)
                self._refuse_sensitive(resolved)
                return resolved
            except ValueError:
                continue
        raise CodeToolError("REFUSED", "outside allowlist: %s" % resolved)

    def _refuse_sensitive(self, path: Path) -> None:
        if path.name.lower() in BLOCK_NAMES or path.name.lower().endswith(".pem"):
            raise CodeToolError("REFUSED", "sensitive name: %s" % path.name)
        parts = {part.lower() for part in path.parts}
        if parts & BLOCK_PARTS:
            raise CodeToolError("REFUSED", "ledger or git internals")

    def Read(self, path, offset: int = 1, limit: int = READ_MAX_LINES) -> dict:
        target = self._under(path)
        if not target.is_file():
            raise CodeToolError("NOT_FOUND", str(target))
        if target.stat().st_size > READ_MAX_BYTES:
            raise CodeToolError("TOO_BIG", str(target))
        start = max(1, int(offset or 1))
        cap = max(1, min(int(limit or READ_MAX_LINES), READ_MAX_LINES))
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        window = lines[start - 1:start - 1 + cap]
        return {
            "schema": SCHEMA, "verb": "Read", "path": str(target),
            "offset": start, "n": len(window), "text": "\n".join(window),
        }

    def Write(self, path, content: str) -> dict:
        target = self._under(path)
        data = str(content if content is not None else "")
        if len(data.encode("utf-8")) > WRITE_MAX_BYTES:
            raise CodeToolError("TOO_BIG", "write cap")
        target.parent.mkdir(parents=True, exist_ok=True)
        self._under(target.parent)
        tmp = target.with_name(target.name + ".tmp")
        tmp.write_text(data, encoding="utf-8")
        tmp.replace(target)
        return {"schema": SCHEMA, "verb": "Write", "path": str(target), "bytes": target.stat().st_size}

    def Edit(self, path, old: str, new: str) -> dict:
        target = self._under(path)
        if not target.is_file():
            raise CodeToolError("NOT_FOUND", str(target))
        if not old:
            raise CodeToolError("BAD_INPUT", "old string is empty")
        text = target.read_text(encoding="utf-8")
        n = text.count(old)
        if n == 0:
            raise CodeToolError("NOT_FOUND", "old string not in file")
        if n != 1:
            raise CodeToolError("AMBIGUOUS", "old string matched %d times" % n)
        self.Write(target, text.replace(old, new, 1))
        return {"schema": SCHEMA, "verb": "Edit", "path": str(target), "replaced": 1}

    def Glob(self, pattern: str, path=None) -> dict:
        root = self._under(path) if path else self.roots[0]
        if not root.is_dir():
            raise CodeToolError("BAD_INPUT", "glob root is not a directory")
        pat = str(pattern or "").strip()
        if not pat or pat.startswith("/") or ".." in pat.replace("\\", "/").split("/"):
            raise CodeToolError("BAD_INPUT", "bad glob")
        hits = []
        for found in root.glob(pat):
            try:
                self._under(found)
            except CodeToolError:
                continue
            hits.append(str(found))
            if len(hits) >= GLOB_CAP:
                break
        return {"schema": SCHEMA, "verb": "Glob", "n": len(hits), "paths": hits}

    def Grep(self, pattern: str, path=None) -> dict:
        root = self._under(path) if path else self.roots[0]
        if not root.is_dir() and not root.is_file():
            raise CodeToolError("NOT_FOUND", str(root))
        try:
            rx = re.compile(str(pattern))
        except re.error as e:
            raise CodeToolError("BAD_INPUT", "bad regex: %s" % e) from e
        files = [root] if root.is_file() else [
            p for p in root.rglob("*") if p.is_file()
        ]
        hits = []
        for found in files:
            try:
                self._under(found)
            except CodeToolError:
                continue
            if found.stat().st_size > READ_MAX_BYTES:
                continue
            try:
                text = found.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "\x00" in text:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    hits.append({"path": str(found), "line": i, "text": line[:240]})
                    if len(hits) >= GREP_CAP:
                        return {"schema": SCHEMA, "verb": "Grep", "n": len(hits), "hits": hits}
        return {"schema": SCHEMA, "verb": "Grep", "n": len(hits), "hits": hits}

    def Bash(self, argv, *, cwd=None, timeout_s: float = BASH_TIMEOUT_S) -> dict:
        if not isinstance(argv, (list, tuple)) or not argv:
            raise CodeToolError("BAD_INPUT", "argv must be a non-empty list")
        parts = [str(a) for a in argv]
        name = Path(parts[0]).name.lower()
        stem = Path(parts[0]).stem.lower()
        if "grok.exe" in parts[0].lower().replace("\\", "/") or name == "grok":
            raise CodeToolError("REFUSED", "grok.exe is not a coding tool")
        if stem not in BASH_ALLOW and name not in BASH_ALLOW:
            raise CodeToolError("REFUSED", "argv[0] %s is not allowlisted" % name)
        work = self._under(cwd or self.roots[0])
        if not work.is_dir():
            raise CodeToolError("BAD_INPUT", "cwd is not a directory")
        timeout = float(timeout_s or BASH_TIMEOUT_S)
        if timeout <= 0 or timeout > BASH_TIMEOUT_CAP:
            raise CodeToolError("BAD_INPUT", "timeout out of range")
        try:
            proc = subprocess.run(
                parts, cwd=str(work), shell=False, capture_output=True,
                text=True, encoding="utf-8", errors="replace", timeout=timeout)
        except subprocess.TimeoutExpired as e:
            return {
                "schema": SCHEMA, "verb": "Bash", "rc": None, "timed_out": True,
                "out": (e.stdout or "")[-4000:] if isinstance(e.stdout, str) else "",
                "err": "timeout",
            }
        except FileNotFoundError as e:
            raise CodeToolError("NOT_FOUND", str(e)) from e
        return {
            "schema": SCHEMA, "verb": "Bash", "rc": proc.returncode,
            "timed_out": False, "out": (proc.stdout or "")[-4000:],
            "err": (proc.stderr or "")[-1500:],
        }


def _selftest() -> int:
    import tempfile

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, "%s: %s" % (type(e).__name__, e)))

    td = Path(tempfile.mkdtemp(prefix="cosmos_code_tools_"))
    tools = CodeTools([td])
    wrote = tools.Write(td / "note.txt", "alpha beta\n")
    check("Write lands under the allowlist",
          lambda: wrote["bytes"] > 0 and (td / "note.txt").is_file())
    got = tools.Read(td / "note.txt")
    check("Read returns the bytes it wrote", lambda: "alpha beta" in got["text"])
    tools.Edit(td / "note.txt", "beta", "gamma")
    check("Edit replaces one match",
          lambda: "gamma" in (td / "note.txt").read_text(encoding="utf-8")
          and "beta" not in (td / "note.txt").read_text(encoding="utf-8"))
    amb = None
    (td / "note.txt").write_text("x x\n", encoding="utf-8")
    try:
        tools.Edit(td / "note.txt", "x", "y")
    except CodeToolError as e:
        amb = e.kind
    check("Edit refuses an ambiguous match", lambda: amb == "AMBIGUOUS")
    outside = None
    try:
        tools.Read(td.parent / "nope.txt")
    except CodeToolError as e:
        outside = e.kind
    check("Read outside the allowlist is REFUSED", lambda: outside == "REFUSED")
    secret = None
    try:
        tools.Write(td / "api_token.txt", "nope")
    except CodeToolError as e:
        secret = e.kind
    check("sensitive name is REFUSED", lambda: secret == "REFUSED")
    globbed = tools.Glob("*.txt", td)
    check("Glob sees the note", lambda: any(p.endswith("note.txt") for p in globbed["paths"]))
    grepped = tools.Grep("gamma|x x", td)
    check("Grep finds the line", lambda: grepped["n"] >= 1)
    grok = None
    try:
        tools.Bash(["grok.exe", "--single"])
    except CodeToolError as e:
        grok = e.kind
    check("Bash refuses grok.exe", lambda: grok == "REFUSED")
    shell = None
    try:
        tools.Bash(["cmd.exe", "/c", "echo hi"])
    except CodeToolError as e:
        shell = e.kind
    check("Bash refuses a shell", lambda: shell == "REFUSED")
    rows = contract_rows()
    check("six verbs are the contract rows",
          lambda: [r["name"] for r in rows] == list(VERBS))

    class _Contracts:
        def __init__(self):
            self.rows = {}

        def state(self):
            return self.rows

        def declare(self, name, verbs, behavior):
            self.rows[name] = {"verbs": verbs, "behavior": behavior}

    box = _Contracts()
    first = declare_on(box)
    second = declare_on(box)
    check("declare_on records six verbs once",
          lambda: first == list(VERBS) and second == [])

    bad = [(label, err) for label, ok, err in results if not ok]
    for label, ok, err in results:
        print(("  OK  " if ok else "  FAIL") + " " + label + (("  " + err) if err else ""))
    print("%d/%d passed" % (len(results) - len(bad), len(results)))
    return 1 if bad else 0


def main() -> int:
    import sys
    if "--selftest" in sys.argv:
        return _selftest()
    print("usage: py -3.14 cosmos\\cosmos_code_tools.py --selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
