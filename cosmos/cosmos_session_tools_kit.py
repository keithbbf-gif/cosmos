#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_session_tools_kit — Open Sessions suite fold for cDeck.

GET returns catalog only (never mutates, never mkdir). POST runs one verb via
the session-tools CLI (builds/session-tools/session_tools.py). Suite verbs are
CLI — not a polling GET surface.

    py -3.14 cosmos\\\\cosmos_session_tools_kit.py --selftest
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

SCHEMA = "cosmos-session-tools-kit/1"
HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CLI = REPO / "builds" / "session-tools" / "session_tools.py"

SUITE_VERBS = (
    "scan", "load", "convert", "diff", "check", "anonymize", "crash-recover",
    "strip", "doi",
)
OPEN_SESSIONS_PANES = (
    ("scan", "Scan families"),
    ("load", "Load one session"),
    ("convert", "Convert to canonical"),
    ("diff", "Diff two payloads"),
    ("check", "Integrity check"),
    ("anonymize", "Anonymize export"),
    ("crash-recover", "Crash recover"),
    ("strip", "Leftover strip"),
    ("doi", "DOI named"),
)


class SessionToolsKitError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def snapshot(paths) -> dict:
    return {
        "schema": SCHEMA,
        "product": "Open Sessions",
        "suite": "Open Sessions suite",
        "verbs": list(SUITE_VERBS),
        "panes": [{"id": i, "label": lab} for i, lab in OPEN_SESSIONS_PANES],
        "cli": str(CLI.relative_to(REPO)).replace("\\", "/"),
        "available": CLI.is_file(),
        "kind": "OK" if CLI.is_file() else "NO_SOURCE",
        "note": (
            "Suite verbs are CLI via session_tools.py. POST runs one verb. "
            "GET never mutates. Legal OMITTED. Original stays."
        ),
        "leftover_strip": {"named": True, "label": "leftover strip"},
        "doi": {"named": True, "label": "DOI named"},
        "measured_at": time.time(),
        "tree_id": paths.sentinel.tree_id,
    }


def _run_cli(argv: list[str]) -> dict:
    if not CLI.is_file():
        raise SessionToolsKitError("NO_SOURCE", f"missing {CLI}")
    cmd = [sys.executable, str(CLI), *argv]
    try:
        cp = subprocess.run(
            cmd,
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise SessionToolsKitError("TIMEOUT", str(e)[:200]) from e
    out = (cp.stdout or "").strip()
    err = (cp.stderr or "").strip()
    if not out:
        raise SessionToolsKitError("CLI_FAILED", err or f"exit {cp.returncode}")
    try:
        rec = json.loads(out)
    except ValueError as e:
        raise SessionToolsKitError("CLI_FAILED", out[:240]) from e
    rec["cli_exit"] = cp.returncode
    if err:
        rec["cli_stderr"] = err[:400]
    return rec


def run(body: dict, paths=None, **_kw) -> dict:
    if paths is None:
        raise SessionToolsKitError("BAD_INPUT", "paths is required")
    if not isinstance(body, dict):
        raise SessionToolsKitError("BAD_INPUT", "body must be an object")
    verb = str(body.get("verb") or body.get("action") or "").strip().lower()
    if not verb:
        raise SessionToolsKitError("BAD_INPUT", "verb is required")
    if verb not in SUITE_VERBS:
        raise SessionToolsKitError("BAD_INPUT", f"unknown verb {verb!r}")

    if verb in ("strip", "doi"):
        return {
            "schema": SCHEMA,
            "verb": verb,
            "kind": "NAMED",
            "gate": {
                "detail": (
                    "leftover strip" if verb == "strip" else "DOI named"
                ),
                "note": "Named suite pane — POST only; no GET poll.",
            },
            "legal_omitted": 0,
        }

    root = str(paths.root)
    store = body.get("store")
    argv: list[str] = []
    if verb == "scan":
        argv = ["scan", "--root", root]
        fams = body.get("families") or body.get("family")
        if fams:
            for f in (fams if isinstance(fams, list) else [fams]):
                argv.extend(["--family", str(f)])
        if store:
            argv.extend(["--store", str(store)])
    elif verb == "load":
        sid = str(body.get("id") or "").strip()
        if not sid or not store:
            raise SessionToolsKitError("BAD_INPUT", "load requires id and store")
        argv = ["load", "--id", sid, "--store", str(store)]
    elif verb == "convert":
        sid = str(body.get("id") or "").strip()
        out_dir = body.get("out_dir") or body.get("out-dir")
        if not sid or not store or not out_dir:
            raise SessionToolsKitError(
                "BAD_INPUT", "convert requires id, store, out_dir")
        argv = ["convert", "--id", sid, "--store", str(store),
                "--out-dir", str(out_dir)]
        if body.get("force"):
            argv.append("--force")
    elif verb == "diff":
        left, right = body.get("left"), body.get("right")
        if not left or not right:
            raise SessionToolsKitError("BAD_INPUT", "diff requires left and right")
        argv = ["diff", "--left", str(left), "--right", str(right)]
    elif verb == "check":
        what = str(body.get("what") or "catalog").strip()
        path = body.get("path") or store
        if not path:
            raise SessionToolsKitError("BAD_INPUT", "check requires path or store")
        argv = ["check", "--what", what, "--path", str(path)]
    elif verb == "anonymize":
        sid = str(body.get("id") or "").strip()
        out_dir = body.get("out_dir") or body.get("out-dir")
        if not sid or not store or not out_dir:
            raise SessionToolsKitError(
                "BAD_INPUT", "anonymize requires id, store, out_dir")
        argv = ["anonymize", "--id", sid, "--store", str(store),
                "--out-dir", str(out_dir)]
    elif verb == "crash-recover":
        target = body.get("target")
        if not target:
            raise SessionToolsKitError("BAD_INPUT", "crash-recover requires target")
        argv = ["crash-recover", "--target", str(target)]
        if body.get("bak"):
            argv.extend(["--bak", str(body["bak"])])
        if body.get("stage"):
            argv.extend(["--stage", str(body["stage"])])
    else:
        raise SessionToolsKitError("BAD_INPUT", f"verb not wired: {verb}")

    rec = _run_cli(argv)
    rec["verb"] = verb
    rec["schema"] = SCHEMA
    return rec


def _selftest() -> int:
    import tempfile

    sys.path.insert(0, str(HERE))
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_stkit_"))
    root = install(td / "live", tree_id="spike-stkit")
    paths = CosmosPaths(root)
    snap = snapshot(paths)
    check("GET snapshot names Open Sessions suite + CLI",
          lambda: snap.get("suite") == "Open Sessions suite"
          and snap.get("cli", "").endswith("session_tools.py")
          and "strip" in snap.get("verbs", [])
          and snap.get("leftover_strip", {}).get("named") is True
          and snap.get("doi", {}).get("named") is True)
    strip = run({"verb": "strip"}, paths=paths)
    check("POST strip is NAMED leftover strip",
          lambda: strip.get("kind") == "NAMED"
          and strip.get("gate", {}).get("detail") == "leftover strip")
    doi = run({"verb": "doi"}, paths=paths)
    check("POST doi is NAMED DOI",
          lambda: doi.get("kind") == "NAMED"
          and doi.get("gate", {}).get("detail") == "DOI named")

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (session tools kit)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
