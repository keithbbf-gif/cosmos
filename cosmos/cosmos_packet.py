#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tool-output packets — hash + preview; bytes in existing CAS.

Headroom shape, not the product. Filename = sha256 under state/cas
(no new cosmos_paths role). PUT mkdir only. GET never mkdir.
No second store. No daemon. No Headroom vendor.

    py -3.14 cosmos\\cosmos_packet.py --selftest
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SCHEMA = "cosmos-packet/1"
LARGE_N = 8000
PREVIEW_N = 240
KIND_PACKET = "PACKET"
KIND_UNMEASURED = "UNMEASURED"


def cas_dir(paths) -> Path:
    """state/cas — existing state role, not a new cas role. Does not mkdir."""
    return paths.state("cas")


def packetize(text, *, dest_dir: Path | None = None, preview: int = PREVIEW_N) -> dict:
    """PUT helper. dest_dir None → UNMEASURED, no store invented, no mkdir."""
    raw = "" if text is None else str(text)
    body = raw.encode("utf-8")
    n_prev = max(0, int(preview))
    rec = {
        "kind": KIND_UNMEASURED,
        "sha256": None,
        "n_bytes": len(body),
        "preview": raw[:n_prev],
    }
    if dest_dir is None:
        return rec
    digest = hashlib.sha256(body).hexdigest()
    rec["sha256"] = digest
    try:
        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / digest
        if not path.is_file():
            path.write_bytes(body)
        rec["kind"] = KIND_PACKET
        rec["path"] = str(path)
        return rec
    except OSError:
        rec["kind"] = KIND_UNMEASURED
        return rec


def retrieve(dest_dir, sha256):
    """GET. Never mkdir. None if missing/unreadable."""
    if dest_dir is None:
        return None
    hexd = str(sha256 or "").strip().lower()
    if len(hexd) != 64 or any(c not in "0123456789abcdef" for c in hexd):
        return None
    path = Path(dest_dir) / hexd
    try:
        return path.read_bytes() if path.is_file() else None
    except OSError:
        return None


def _selftest() -> int:
    import tempfile
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    class _Paths:
        def state(self, *parts):
            return Path("state").joinpath(*parts)

    check("cas_dir is state/cas, no new role",
          lambda: cas_dir(_Paths()).as_posix().replace("\\", "/").endswith("state/cas"))

    td = Path(tempfile.mkdtemp(prefix="pkt_"))
    dest = td / "cas"
    sample = "hello-packet"
    pkt = packetize(sample, dest_dir=dest)
    digest = hashlib.sha256(sample.encode("utf-8")).hexdigest()
    check("packetize small string writes hash file and preview",
          lambda: (pkt["kind"] == KIND_PACKET
                   and pkt["sha256"] == digest
                   and pkt["n_bytes"] == len(sample.encode("utf-8"))
                   and pkt["preview"] == sample
                   and (dest / digest).is_file()
                   and (dest / digest).read_bytes() == sample.encode("utf-8")))

    before = set(p.name for p in td.iterdir())
    none_pkt = packetize("unmeasured-body", dest_dir=None)
    after = set(p.name for p in td.iterdir())
    check("dest_dir None → UNMEASURED, no mkdir",
          lambda: (none_pkt["kind"] == KIND_UNMEASURED
                   and none_pkt["sha256"] is None
                   and none_pkt["n_bytes"] == len(b"unmeasured-body")
                   and none_pkt["preview"] == "unmeasured-body"
                   and after == before))

    got = retrieve(dest, pkt["sha256"])
    check("retrieve: read dest_dir/sha equals original",
          lambda: got == sample.encode("utf-8"))

    ghost = td / "ghost_cas"
    ghost_got = retrieve(ghost, digest)
    check("GET-shaped missing dest does not mkdir",
          lambda: ghost_got is None and not ghost.exists())

    blocked = td / "not_a_dir"
    blocked.write_text("x", encoding="utf-8")
    bad = packetize("io-fail", dest_dir=blocked)
    check("IO error is UNMEASURED, never silent truncate-without-pointer",
          lambda: (bad["kind"] == KIND_UNMEASURED
                   and bad["n_bytes"] == len(b"io-fail")
                   and bad["preview"] == "io-fail"
                   and bool(bad.get("sha256"))))

    failed = [r for r in results if not r[1]]
    for label, ok, err in results:
        print(("PASS" if ok else "FAIL"), label, err)
    print("packet selftest", f"{len(results)-len(failed)}/{len(results)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_selftest() if "--selftest" in sys.argv else 2)
