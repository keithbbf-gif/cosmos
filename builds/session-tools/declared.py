#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local write_declared / read_verified (sha-only).

cosmos_validate.py imports the ledger; Slice-1 must not pull kernel/ledger.
Shape matches cosmos_validate: {path, len, sha}. No HMAC on transcripts.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Optional


class DeclaredError(RuntimeError):
    """kind in {SHORT_READ, HASH_MISMATCH}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _extended(p: Path | str) -> str:
    s = str(p)
    if os.name != "nt":
        return s
    if s.startswith("\\\\?\\"):
        return s
    if s.startswith("\\\\"):
        return "\\\\?\\UNC" + s[1:]
    return "\\\\?\\" + os.path.abspath(s)


def read_verified(path: Path, expect_len: Optional[int] = None,
                  expect_sha: Optional[str] = None) -> bytes:
    with open(_extended(path), "rb") as fh:
        data = fh.read()
        more = fh.read(1)
        while more:
            data += more
            more = fh.read(1 << 16)
    if expect_len is not None and len(data) != expect_len:
        raise DeclaredError(
            "SHORT_READ",
            f"{path}: consumed {len(data)} bytes, declared {expect_len}")
    if expect_sha is not None:
        got = hashlib.sha256(data).hexdigest()
        if got != expect_sha:
            raise DeclaredError(
                "HASH_MISMATCH",
                f"{path}: sha {got[:12]} != declared {expect_sha[:12]}")
    return data


def write_declared(path: Path, content: bytes) -> dict:
    path = Path(path)
    with open(_extended(path), "wb") as fh:
        fh.write(content)
    return {"path": str(path), "len": len(content),
            "sha": hashlib.sha256(content).hexdigest()}


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
