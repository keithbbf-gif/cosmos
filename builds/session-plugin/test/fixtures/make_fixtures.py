#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate the plugin fixtures from the real producer, not by hand.

The two clean transcripts come out of `session_tools load --out`, so the plugin
is tested against bytes the shipped tool actually wrote. The legal and tampered
cases are derived from those bytes (session_tools refuses to emit a legal
transcript, which is the point).

    py -3.14 builds/session-plugin/test/fixtures/make_fixtures.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
# Repo-relative so the emitted sources[].path - and therefore the sha - is the
# same on every machine. An absolute path baked into a fixture is not a fixture.
SRC_FIX = Path("tests") / "fixtures" / "session_tools"
TRANSCRIPTS = HERE / "transcripts"
TAMPERED = HERE / "tampered"
ROLLED = HERE / "rolled" / "cosmos.rolled.jsonl"

sys.path.insert(0, str(REPO / "builds" / "session-tools"))
sys.path.insert(0, str(REPO / "cosmos"))

CLEAN = [
    ("cow-abc", SRC_FIX),
    ("grok-aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee", SRC_FIX / "grok"),
]


def _decl(payload: bytes) -> dict:
    return {
        "schema": "cosmos-transcript-decl/1",
        "len": len(payload),
        "sha": hashlib.sha256(payload).hexdigest(),
        "n_turns": payload.count(b"\n") - 1,
        "fidelity": "span",
        "hmac": False,
    }


def _write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    decl = path.with_name(path.name.replace(".ctr.jsonl", ".ctr.decl.json"))
    decl.write_text(json.dumps(_decl(payload), indent=2) + "\n", encoding="utf-8")


def main() -> int:
    import os

    import session_tools as st

    os.chdir(REPO)
    for rec_id, store in CLEAN:
        st.cmd_load(rec_id, store, TRANSCRIPTS)

    base = (TRANSCRIPTS / "cow-abc.ctr.jsonl").read_bytes()
    lines = base.split(b"\n")
    head = json.loads(lines[0])

    # Legal: load refuses to emit one, so derive it. Proves read/search omit it.
    head_legal = dict(head, id="cow-leg1", legal=True, title="parked", stream="legal")
    legal = b"\n".join(
        [json.dumps(head_legal, separators=(",", ":"), ensure_ascii=False).encode("utf-8")]
        + lines[1:])
    _write(TRANSCRIPTS / "cow-leg1.ctr.jsonl", legal)

    # Tampered: a valid sidecar beside mutated bytes of the SAME length, so only
    # the sha catches it. Must refuse HASH_MISMATCH.
    _write(TAMPERED / "cow-tamper.ctr.jsonl", base.replace(b"cow-abc", b"cow-tamper"))
    bad = (TAMPERED / "cow-tamper.ctr.jsonl").read_bytes().replace(
        b"hello from plumbing", b"hello from tampered")
    (TAMPERED / "cow-tamper.ctr.jsonl").write_bytes(bad)

    # Truncated: bytes short of the declaration. Must refuse LEN_MISMATCH.
    _write(TAMPERED / "cow-short.ctr.jsonl", base.replace(b"cow-abc", b"cow-short"))
    short = (TAMPERED / "cow-short.ctr.jsonl").read_bytes()[:-40]
    (TAMPERED / "cow-short.ctr.jsonl").write_bytes(short)

    # rolled-event/1 is PROPOSED - no COSMOS component emits it yet.
    ROLLED.parent.mkdir(parents=True, exist_ok=True)
    events = [
        {"schema": "rolled-event/1", "id": "cow-abc", "seq": 2, "t": 1757000100.0,
         "kind": "session.turn", "actor": "open-sessions", "detail": {"turn": 1}},
        {"schema": "rolled-event/1", "id": "cow-abc", "seq": 1, "t": 1757000000.0,
         "kind": "session.opened", "actor": "open-sessions", "detail": {}},
        {"schema": "rolled-event/1", "id": "grok-aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee",
         "seq": 1, "t": 1757000050.0, "kind": "session.opened", "actor": "cdeck",
         "detail": {}},
    ]
    ROLLED.write_text(
        "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in events),
        encoding="utf-8")
    print("fixtures written:", TRANSCRIPTS, TAMPERED, ROLLED)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
