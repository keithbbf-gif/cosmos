"""Cold-start chain: hash link, one write, identity refusal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from cosmos_federation import DEFAULT_CAP_USD_MICROS, PathJail, Refuse
from ledgerboot import GENESIS_REL, apply, genesis


def _digest(body: dict[str, object]) -> str:
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def test_cap_set_prev_is_the_install_hash() -> None:
    installed, capped = genesis("Peer-1", 1_700_000_000)
    assert installed.seq == 1
    assert installed.event == "INSTALL"
    assert installed.prev == "0" * 64
    assert installed.cap_usd_micros is None
    assert installed.hash == _digest({
        "epoch": 1_700_000_000,
        "event": "INSTALL",
        "prev": "0" * 64,
        "seq": 1,
        "tree_id": "Peer-1",
    })
    assert capped.seq == 2
    assert capped.event == "CAP_SET"
    assert capped.prev == installed.hash
    assert capped.cap_usd_micros == DEFAULT_CAP_USD_MICROS
    assert capped.hash == _digest({
        "cap_usd_micros": DEFAULT_CAP_USD_MICROS,
        "epoch": 1_700_000_000,
        "event": "CAP_SET",
        "prev": installed.hash,
        "seq": 2,
        "tree_id": "Peer-1",
    })
    assert "sk-" not in repr((installed, capped))
    assert genesis("Peer-1", 1_700_000_000) == (installed, capped)


def test_apply_is_idempotent(scratch: Path) -> None:
    jail = PathJail(scratch)
    path = apply(jail, "Peer-1", 1_700_000_000)
    assert path == jail.contain(GENESIS_REL)
    assert scratch.resolve() in path.parents
    body = path.read_bytes()
    again = apply(jail, "Peer-1", 1_700_000_000)
    assert again.read_bytes() == body
    later = apply(jail, "Peer-1", 1_700_000_001)
    assert later.read_bytes() == body
    lines = body.decode("utf-8").splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    second = json.loads(lines[1])
    assert isinstance(first, dict) and isinstance(second, dict)
    assert second["prev"] == first["hash"]
    assert "cap_usd_micros" not in first
    assert second["cap_usd_micros"] == DEFAULT_CAP_USD_MICROS
    assert b"sk-" not in body
    assert b"api_key" not in body


def test_different_tree_refuses(scratch: Path) -> None:
    jail = PathJail(scratch)
    path = apply(jail, "Peer-1", 1_700_000_000)
    before = path.read_bytes()
    try:
        apply(jail, "Peer-2", 1_700_000_000)
    except Refuse as exc:
        assert exc.code == "IDENTITY_MISMATCH"
    else:
        raise AssertionError("IDENTITY_MISMATCH")
    assert path.read_bytes() == before
    assert before.decode("utf-8").count("INSTALL") == 1


def test_bad_identity_and_epoch_refuse() -> None:
    try:
        genesis("GMesh", 0)
    except Refuse as exc:
        assert exc.code == "TREE_ID"
    else:
        raise AssertionError("TREE_ID")
    try:
        genesis("Peer-1", True)
    except Refuse as exc:
        assert exc.code == "BOUND"
    else:
        raise AssertionError("BOUND")
