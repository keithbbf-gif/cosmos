#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Public tests for cosmos_packet. Scratch only - no live sentinel."""
from __future__ import annotations

import hashlib
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_packet import (  # noqa: E402
    KIND_PACKET,
    KIND_UNMEASURED,
    LARGE_N,
    PREVIEW_N,
    SCHEMA,
    cas_dir,
    packetize,
    retrieve,
)

SCRATCH = Path(r"C:\Users\Papa\AppData\Local\Temp\c4-pkt")


def _scratch(label: str) -> Path:
    path = SCRATCH / "packet" / label / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    resolved = path.resolve()
    assert resolved.is_relative_to(SCRATCH.resolve())
    live = (ROOT / "live").resolve()
    assert not resolved.is_relative_to(live)
    return path


class _Paths:
    """Stand-in resolver. Does not read a sentinel or the live root."""

    def __init__(self, base: Path) -> None:
        self._base = base

    def state(self, *parts: str) -> Path:
        return self._base.joinpath("state", *parts)


def test_cas_dir_uses_state_role_and_does_not_mkdir():
    base = _scratch("cas")
    found = cas_dir(_Paths(base))
    assert found == base / "state" / "cas"
    assert not found.exists()
    assert not (base / "state").exists()
    assert SCHEMA == "cosmos-packet/1"
    assert LARGE_N == 8000
    assert PREVIEW_N == 240
    assert KIND_PACKET == "PACKET"
    assert KIND_UNMEASURED == "UNMEASURED"


def test_packetize_roundtrip():
    dest = _scratch("put") / "cas"
    sample = "hello-packet"
    pkt = packetize(sample, dest_dir=dest)
    digest = hashlib.sha256(sample.encode("utf-8")).hexdigest()
    assert pkt["kind"] == KIND_PACKET
    assert pkt["sha256"] == digest
    assert pkt["n_bytes"] == len(sample.encode("utf-8"))
    assert pkt["preview"] == sample
    assert pkt["path"] == str(dest / digest)
    body = sample.encode("utf-8")
    assert retrieve(dest, digest) == body
    assert retrieve(dest, digest.upper()) == body
    again = packetize(sample, dest_dir=dest)
    assert again["sha256"] == digest
    assert (dest / digest).read_bytes() == body


def test_dest_none_stays_unmeasured():
    root = _scratch("none")
    before = sorted(p.name for p in root.iterdir())
    pkt = packetize("unmeasured-body", dest_dir=None)
    after = sorted(p.name for p in root.iterdir())
    assert pkt["kind"] == KIND_UNMEASURED
    assert pkt["sha256"] is None
    assert "path" not in pkt
    assert pkt["n_bytes"] == len(b"unmeasured-body")
    assert pkt["preview"] == "unmeasured-body"
    assert after == before
    assert retrieve(None, "ab" * 32) is None


def test_bad_path_is_unmeasured_and_does_not_mkdir():
    root = _scratch("bad")
    blocked = root / "not_a_dir"
    blocked.write_text("x", encoding="utf-8")
    bad = packetize("io-fail", dest_dir=blocked)
    assert bad["kind"] == KIND_UNMEASURED
    assert bad["n_bytes"] == len(b"io-fail")
    assert bad["preview"] == "io-fail"
    assert bad["sha256"]
    assert "path" not in bad
    assert blocked.read_text(encoding="utf-8") == "x"
    assert not blocked.is_dir()
    ghost = root / "ghost_cas"
    assert retrieve(ghost, bad["sha256"]) is None
    assert not ghost.exists()
    assert retrieve(blocked, bad["sha256"]) is None


def test_missing_hash_refuses():
    dest = _scratch("miss") / "cas"
    body = "stored"
    pkt = packetize(body, dest_dir=dest)
    digest = pkt["sha256"]
    assert retrieve(dest, None) is None
    assert retrieve(dest, "") is None
    assert retrieve(dest, "abc") is None
    assert retrieve(dest, "g" * 64) is None
    assert retrieve(dest, "ab" * 32) is None
    assert retrieve(dest, "../" + digest[:61]) is None
    assert retrieve(dest, "  " + digest + "\n") == body.encode("utf-8")
    assert {p.name for p in dest.iterdir()} == {digest}


def test_preview_clamp_and_empty_body():
    short = packetize("abcdef", dest_dir=None, preview=3)
    assert short["preview"] == "abc"
    assert short["n_bytes"] == 6
    zero = packetize("abcdef", dest_dir=None, preview=0)
    assert zero["preview"] == ""
    neg = packetize("abcdef", dest_dir=None, preview=-4)
    assert neg["preview"] == ""
    dest = _scratch("empty") / "cas"
    empty = packetize(None, dest_dir=dest)
    assert empty["kind"] == KIND_PACKET
    assert empty["n_bytes"] == 0
    assert empty["preview"] == ""
    assert retrieve(dest, empty["sha256"]) == b""
