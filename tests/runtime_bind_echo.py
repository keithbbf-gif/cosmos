#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""runtime_bind_echo — child identity emitter for the runtime-binding gate.

Stdlib only: the child must not boot Kernel / Ledger / Sched / Service.
Spawned as a FRESH interpreter (`py -3.14 -B`) by tests/test_runtime_binding.py.
rc=0 is not the gate. The JSON object on stdout is. An old snapshot that
does not read the challenge file cannot emit bind_digest.

    py -3.14 -B tests/runtime_bind_echo.py --nonce-file PATH [--root ROOT]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

# Bytes at LOAD, not at emit. Hashing the file again at emit-time would
# false-pass an in-memory stale process after a git pull (the disk moved;
# the running code did not).
_LOADED_PATH = Path(__file__).resolve()
try:
    _LOADED_BYTES = _LOADED_PATH.read_bytes()
except OSError:
    _LOADED_BYTES = b""
LOADED_SHA256 = hashlib.sha256(_LOADED_BYTES).hexdigest()
LOADED_AT_EPOCH = time.time()
SENTINEL_NAME = ".cosmos-root.json"
SCHEMA = "cosmos-runtime-bind-echo/1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bind_digest(nonce: str, loaded: bytes) -> str:
    return sha256_bytes(nonce.encode("utf-8") + b"\n" + loaded)


def read_challenge(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("challenge is not an object")
    nonce = obj.get("nonce")
    if not isinstance(nonce, str) or len(nonce) < 16:
        raise ValueError("challenge.nonce missing or short")
    return obj


def read_sentinel(root: Path) -> dict | None:
    p = root / SENTINEL_NAME
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"error": "UNPARSEABLE", "path": str(p)}
    if not isinstance(data, dict):
        return {"error": "UNPARSEABLE", "path": str(p)}
    return {
        "path": str(p.resolve()),
        "system": data.get("system"),
        "tree_id": data.get("tree_id"),
        "schema_version": data.get("schema_version"),
    }


def emit(nonce_file: Path, root: Path | None) -> dict:
    t_emit = time.time()
    ch = read_challenge(nonce_file)
    nonce = ch["nonce"]
    disk_err = None
    try:
        disk_bytes = _LOADED_PATH.read_bytes()
    except OSError as e:
        disk_bytes = b""
        disk_err = str(e)
    rec = {
        "ok": True,
        "schema": SCHEMA,
        "pid": os.getpid(),
        "ppid": os.getppid() if hasattr(os, "getppid") else None,
        "epoch": t_emit,
        "loaded_at_epoch": LOADED_AT_EPOCH,
        "nonce": nonce,
        "nonce_sha256": sha256_bytes(nonce.encode("utf-8")),
        "bind_digest": bind_digest(nonce, _LOADED_BYTES),
        "file": str(_LOADED_PATH),
        "loaded_sha256": LOADED_SHA256,
        "disk_sha256": sha256_bytes(disk_bytes) if disk_bytes else None,
        "disk_error": disk_err,
        "executable": sys.executable,
        "version": sys.version.split()[0],
        "version_info": list(sys.version_info[:3]),
        "dont_write_bytecode": bool(sys.dont_write_bytecode),
        "argv": list(sys.argv),
        "cwd": os.getcwd(),
        "cached": globals().get("__cached__"),
    }
    if root is not None:
        rec["root"] = str(root.resolve())
        rec["sentinel"] = read_sentinel(root)
    return rec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="runtime-bind-echo")
    ap.add_argument("--nonce-file", required=True)
    ap.add_argument("--root", default=None)
    a = ap.parse_args(argv)
    try:
        rec = emit(Path(a.nonce_file), Path(a.root) if a.root else None)
    except Exception as e:  # noqa: BLE001
        rec = {
            "ok": False,
            "schema": SCHEMA,
            "kind": type(e).__name__,
            "detail": str(e)[:500],
            "pid": os.getpid(),
            "epoch": time.time(),
            "file": str(_LOADED_PATH),
            "loaded_sha256": LOADED_SHA256,
            "executable": sys.executable,
        }
        print(json.dumps(rec, indent=1), flush=True)
        return 2
    print(json.dumps(rec, indent=1), flush=True)
    return 0 if rec.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
