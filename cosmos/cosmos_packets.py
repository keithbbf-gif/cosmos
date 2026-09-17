#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_packets - tool-output packets through the EXISTING CAS.

SGH steal: KEEP_PACKETS. A tool output packet is content-addressed
(filename = hash) in cosmos_segments.CAS. The ledger holds the live
pointer. No second store. No LangGraph. No extra grok.exe. Occupancy of
cDeck is out of scope. Kernel/ledger writer stays Core. Not a scheduler.

GET never mkdir. Fail-closed. Replay of a fenced critique packet stays
refused via the existing cosmos_crit_consumer.is_replay pin. Empty is
explicit (empty=true). UNMEASURED never reports n=0 — n is JSON null.

    py -3.14 cosmos\\cosmos_packets.py --selftest
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_ledger import Ledger, LedgerError  # noqa: E402
from cosmos_segments import CAS  # noqa: E402

SCHEMA = "cosmos-packets/1"
EVENT = "TOOL_OUTPUT_PACKET"
KIND = "TOOL_OUTPUT"
# Existing state role; not a new resolver role and not state/cvm/cas.
CAS_PART = "cas"
SRC = Path(__file__).resolve()


class PacketError(RuntimeError):
    """kind in {EMPTY, REPLAY, NOT_FOUND, HASH_MISMATCH, UNREADABLE,
    BROKEN_CHAIN, UNMEASURED, BAD_PACKET}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def cas_root(paths) -> Path:
    """Existing `state` role + cas/. Does not mkdir. Does not invent a role."""
    return paths.state(CAS_PART)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _as_bytes(data) -> bytes:
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    if data is None:
        return b""
    if isinstance(data, str):
        return data.encode("utf-8")
    raise PacketError(
        "BAD_PACKET",
        "tool output packet body must be bytes or str, not %s" % type(data).__name__)


def open_cas(paths, *, mkdir: bool) -> CAS:
    """One store: cosmos_segments.CAS. PUT may mkdir; GET must not."""
    return CAS(cas_root(paths), mkdir=mkdir)


def refuse_replay(inbox: Path | None, name: str | None,
                  returns_path: Path | None = None) -> None:
    """Existing crit_consumer pin. Replay of a fenced packet is refused."""
    if inbox is None or not name:
        return
    from cosmos_crit_consumer import is_replay  # lazy: no scheduler attach
    if is_replay(Path(inbox), str(name), returns_path):
        raise PacketError(
            "REPLAY",
            "fenced packet %s stays refused (crit_consumer pin)" % name)


def put_packet(paths, ledger: Ledger, data, *,
               name: str | None = None,
               inbox: Path | None = None,
               returns_path: Path | None = None,
               extra: Optional[dict] = None) -> dict:
    """Store packet bytes in the existing CAS; ledger holds only the pointer.

    Write path (may mkdir the CAS dir). Replay of a fenced packet REFUSES
    before any write. Empty body is accepted only as explicit empty=true.
    """
    refuse_replay(inbox, name, returns_path)
    raw = _as_bytes(data)
    empty = len(raw) == 0
    cas = open_cas(paths, mkdir=True)
    sha = cas.put(raw)
    payload = {
        "cas": sha,
        "bytes": len(raw),
        "empty": empty,
        "kind": KIND,
        "name": name,
        "schema": SCHEMA,
    }
    if extra:
        # pointer fields stay authoritative; extra cannot rename the store
        for key, val in extra.items():
            if key in ("cas", "bytes", "empty", "kind", "schema"):
                continue
            payload[key] = val
    rec = ledger.append(EVENT, payload)
    return {
        "schema": SCHEMA,
        "ok": True,
        "kind": "EMPTY" if empty else "STORED",
        "empty": empty,
        "cas": sha,
        "bytes": len(raw),
        "name": name,
        "event": EVENT,
        "seq": rec.get("seq"),
        "second_store": False,
        "is_scheduler": False,
        "note": "CAS filename=hash; ledger holds the live pointer.",
    }


def get_packet(paths, sha: str) -> bytes:
    """GET one blob by sha. Never mkdir. Fail-closed on absent/corrupt."""
    if not sha:
        raise PacketError("NOT_FOUND", "no CAS pointer (empty sha is not a blob)")
    try:
        cas = open_cas(paths, mkdir=False)
    except LedgerError as e:
        raise PacketError(e.kind, str(e)) from e
    try:
        return cas.get(sha)
    except LedgerError as e:
        raise PacketError(e.kind, str(e)) from e


def live_pointer(ledger: Ledger) -> Optional[dict]:
    """Last TOOL_OUTPUT_PACKET payload, or None. Does not mkdir. Does not invent."""
    last = None
    for rec in ledger.verify():
        if rec.get("event") == EVENT and isinstance(rec.get("payload"), dict):
            last = rec["payload"]
    return last


def snapshot(paths, ledger: Ledger) -> dict:
    """GET fold. Never mkdir. Never invents a pointer.

    Absent store or no TOOL_OUTPUT_PACKET → kind=UNMEASURED and n=None
    (JSON null), never n=0. Measured empty is kind=EMPTY with empty=true.
    """
    rec = {
        "schema": SCHEMA,
        "ok": True,
        "kind": "UNMEASURED",
        "n": None,
        "empty": None,
        "cas": None,
        "event": EVENT,
        "second_store": False,
        "is_scheduler": False,
        "kernel_writer": "core",
        "note": (
            "GET never mkdir. Ledger holds the live pointer. Existing CAS "
            "only. UNMEASURED n is null, never 0."
        ),
    }
    root = cas_root(paths)
    if not root.exists():
        return rec
    ptr = live_pointer(ledger)
    if not ptr or not ptr.get("cas"):
        return rec
    sha = str(ptr.get("cas") or "")
    rec["cas"] = sha
    rec["empty"] = bool(ptr.get("empty"))
    rec["name"] = ptr.get("name")
    try:
        data = get_packet(paths, sha)
    except PacketError as e:
        rec["ok"] = False
        rec["kind"] = e.kind
        rec["n"] = None
        rec["error"] = str(e)
        return rec
    rec["n"] = len(data)
    rec["bytes"] = len(data)
    rec["kind"] = "EMPTY" if rec["empty"] else "MEASURED"
    rec["ok"] = True
    return rec


def _selftest() -> int:
    import tempfile
    from cosmos_crit_consumer import is_replay, write_fence
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    src = SRC.read_text(encoding="utf-8")
    prod = src.split("def _selftest")[0]
    check("named module uses existing cosmos_segments.CAS",
          lambda: "from cosmos_segments import CAS" in prod)
    check("named module uses existing cosmos_ledger.Ledger",
          lambda: "from cosmos_ledger import Ledger" in prod)
    check("no second store class",
          lambda: "class CAS" not in prod)
    check("LangGraph is refused, not imported",
          lambda: "import langgraph" not in prod.lower()
          and "No LangGraph" in prod)
    check("does not spawn grok.exe",
          lambda: "subprocess" not in prod and "Popen" not in prod
          and "No extra grok.exe" in prod)
    check("does not invent an HTTP route",
          lambda: "/api/v1/" not in prod)

    tree = ast.parse(src)
    get_fns = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in (
                "snapshot", "get_packet", "live_pointer", "cas_root"):
            get_fns[node.name] = node
    check("GET folds are present",
          lambda: set(get_fns) == {"snapshot", "get_packet", "live_pointer", "cas_root"})

    def _calls_mkdir(fn) -> bool:
        for n in ast.walk(fn):
            if isinstance(n, ast.Call):
                name = ""
                if isinstance(n.func, ast.Attribute):
                    name = n.func.attr
                elif isinstance(n.func, ast.Name):
                    name = n.func.id
                if name == "mkdir":
                    return True
        return False

    check("GET snapshot never mkdir", lambda: not _calls_mkdir(get_fns["snapshot"]))
    check("GET get_packet never mkdir", lambda: not _calls_mkdir(get_fns["get_packet"]))
    check("GET live_pointer never mkdir", lambda: not _calls_mkdir(get_fns["live_pointer"]))
    check("GET cas_root never mkdir", lambda: not _calls_mkdir(get_fns["cas_root"]))
    doc = ast.get_docstring(get_fns["snapshot"]) or ""
    check("snapshot docstring pins Never mkdir", lambda: "Never mkdir" in doc)

    td = Path(tempfile.mkdtemp(prefix="cosmos_packets_"))
    root = install(td / "live", tree_id="spike-packets-cas")
    paths = CosmosPaths(root)
    key = paths.config("install_key.bin").read_bytes()
    ledger = Ledger(paths.ledger("authority.jsonl"), key, "packets-selftest")
    store = cas_root(paths)

    snap0 = snapshot(paths, ledger)
    check("absent CAS is UNMEASURED and n is null not 0",
          lambda: snap0["kind"] == "UNMEASURED"
          and snap0["n"] is None
          and snap0["empty"] is None
          and snap0["ok"] is True)
    check("GET snapshot does not mkdir state/cas",
          lambda: not store.exists())

    missing = False
    try:
        get_packet(paths, "f" * 64)
    except PacketError as e:
        missing = e.kind == "NOT_FOUND"
    check("GET missing blob is NOT_FOUND and still no mkdir",
          lambda: missing and not store.exists())

    body = b"tool-output-packet-body " * 20
    put = put_packet(paths, ledger, body, name="tool_out.json")
    check("PUT stores in existing CAS (filename=hash)",
          lambda: put["ok"] is True
          and put["cas"] == _sha(body)
          and put["kind"] == "STORED"
          and put["second_store"] is False
          and (store / (put["cas"] + ".blob")).is_file())
    check("ledger holds only the live pointer",
          lambda: live_pointer(ledger) == {
              "cas": put["cas"],
              "bytes": len(body),
              "empty": False,
              "kind": KIND,
              "name": "tool_out.json",
              "schema": SCHEMA,
          })
    check("GET round-trips the exact bytes",
          lambda: get_packet(paths, put["cas"]) == body)

    snap1 = snapshot(paths, ledger)
    check("GET after PUT is MEASURED with n=byte length",
          lambda: snap1["kind"] == "MEASURED"
          and snap1["n"] == len(body)
          and snap1["cas"] == put["cas"]
          and snap1["empty"] is False)

    empty_put = put_packet(paths, ledger, b"", name="empty.json")
    check("empty packet is explicit empty=true (measured, not UNMEASURED)",
          lambda: empty_put["kind"] == "EMPTY"
          and empty_put["empty"] is True
          and empty_put["bytes"] == 0)
    snap_e = snapshot(paths, ledger)
    check("GET of explicit empty is EMPTY, not UNMEASURED-as-0",
          lambda: snap_e["kind"] == "EMPTY"
          and snap_e["empty"] is True
          and snap_e["n"] == 0)

    # Replay pin: existing crit_consumer fence
    inbox = td / "inbox"
    fence_dir = inbox / "_fence"
    fence_dir.mkdir(parents=True)
    pkt_name = "handoff_gem.json"
    write_fence(inbox, pkt_name, {
        "schema": "cosmos-crit-consumer/1",
        "owner": "cosmos-crit-consumer",
        "packet": pkt_name,
    })
    check("crit_consumer is_replay still true on fenced packet",
          lambda: is_replay(inbox, pkt_name) is True)
    replayed = False
    try:
        put_packet(paths, ledger, b"replay-must-refuse",
                   name=pkt_name, inbox=inbox)
    except PacketError as e:
        replayed = e.kind == "REPLAY"
    check("PUT of a fenced packet is REPLAY (fail-closed)",
          lambda: replayed)
    check("replay refusal did not store a new blob for the replay body",
          lambda: not (store / (_sha(b"replay-must-refuse") + ".blob")).exists())

    # Tamper: HASH_MISMATCH stay fail-closed
    live = live_pointer(ledger)
    bp = store / (put["cas"] + ".blob")
    raw = bp.read_bytes()
    bp.write_bytes(raw[:-1] + bytes([raw[-1] ^ 0xFF]))
    mismatch = False
    try:
        get_packet(paths, put["cas"])
    except PacketError as e:
        mismatch = e.kind == "HASH_MISMATCH"
    check("tampered CAS blob is HASH_MISMATCH (never handed back)",
          lambda: mismatch)
    # restore so later pointer GET of empty (newer) still works
    bp.write_bytes(raw)
    snap_bad = snapshot(paths, ledger)
    check("live pointer still the latest empty packet after restore",
          lambda: snap_bad["kind"] == "EMPTY" and snap_bad["cas"] == live["cas"])

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (CAS pointer, GET never mkdir, "
          "UNMEASURED n=null, empty explicit, fenced replay refused)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="cosmos_packets")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
