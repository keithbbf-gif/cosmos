"""Refusals and one staged payload for the updater slot."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path

from cosmos_federation import PathJail, Refuse
from updater import SCHEMA, UpdateOk, stage, verify


def _packet(**overrides: object) -> dict[str, object]:
    payload_obj = overrides.get("payload", b"dayone-update")
    payload = payload_obj if isinstance(payload_obj, bytes) else b"dayone-update"
    packet: dict[str, object] = {
        "tree_id": "Peer-1",
        "version": 2,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "payload": payload,
        "signer_id": "hub-1",
    }
    packet.update(overrides)
    return packet


def _expect(
    code: str,
    packet: Mapping[str, object] | None = None,
    *,
    local_tree_id: str = "Peer-1",
    local_version: int = 1,
    now: int = 1_700_000_000,
) -> None:
    body = _packet() if packet is None else packet
    try:
        verify(body, local_tree_id=local_tree_id, local_version=local_version, now=now)
    except Refuse as exc:
        assert exc.code == code
    else:
        raise AssertionError(code)


def test_schema_name() -> None:
    assert SCHEMA == "cosmos-federation-updater/1"


def test_unsigned_when_signer_is_empty() -> None:
    _expect("UNSIGNED", _packet(signer_id=""))


def test_secret_signer_is_refused_and_not_echoed() -> None:
    raw = "sk-" + ("a" * 12)
    try:
        verify(
            _packet(signer_id=raw),
            local_tree_id="Peer-1",
            local_version=1,
            now=1_700_000_000,
        )
    except Refuse as exc:
        assert exc.code == "SECRET"
        assert raw not in str(exc)
    else:
        raise AssertionError("SECRET")


def test_tree_mismatch() -> None:
    _expect("TREE_MISMATCH", _packet(tree_id="Peer-2"))


def test_forbidden_tree_id_is_not_a_mismatch() -> None:
    _expect("TREE_ID", local_tree_id="GMesh")
    _expect("TREE_ID", _packet(tree_id="KMesh-COSMOS-live"))
    _expect("TREE_ID", _packet(tree_id="live"))


def test_downgrade_includes_equal_version() -> None:
    _expect("DOWNGRADE", _packet(version=2), local_version=2)
    _expect("DOWNGRADE", _packet(version=1), local_version=2)


def test_bad_hash() -> None:
    _expect("BAD_HASH", _packet(sha256="0" * 64))


def test_malformed_fields_are_bound() -> None:
    _expect("BOUND", _packet(version=True))
    _expect("BOUND", _packet(payload="not-bytes"))
    missing = _packet()
    del missing["signer_id"]
    _expect("BOUND", missing)
    _expect("BOUND", now=-1)


def test_verify_accepts_a_newer_matching_packet() -> None:
    payload = b"dayone-update"
    ok = verify(_packet(), local_tree_id="Peer-1", local_version=1, now=1_700_000_000)
    assert ok == UpdateOk(version=2, nbytes=len(payload))
    assert ok.digest == hashlib.sha256(payload).hexdigest()
    assert ok.digest not in repr(ok)
    assert "sk-" not in repr(ok)
    assert "payload" not in repr(ok)


def test_stage_writes_payload_and_leaves_other_files(scratch: Path) -> None:
    payload = b"\x00\xffdayone"
    packet = _packet(payload=payload, version=3)
    jail = PathJail(scratch)
    note = jail.contain("updates/3/note.txt")
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("keep", encoding="utf-8")
    keep = jail.contain("config/install_record.json")
    keep.parent.mkdir(parents=True, exist_ok=True)
    keep.write_bytes(b"record")
    path = stage(jail, packet, local_tree_id="Peer-1", local_version=1, now=1_700_000_000)
    assert path == jail.contain("updates/3/payload.bin")
    assert path.read_bytes() == payload
    assert note.read_text(encoding="utf-8") == "keep"
    assert keep.read_bytes() == b"record"
    names = sorted(item.name for item in (scratch / "updates" / "3").iterdir())
    assert names == ["note.txt", "payload.bin"]


def test_refused_packet_is_not_staged(scratch: Path) -> None:
    jail = PathJail(scratch)
    try:
        stage(
            jail,
            _packet(signer_id=""),
            local_tree_id="Peer-1",
            local_version=1,
            now=1_700_000_000,
        )
    except Refuse as exc:
        assert exc.code == "UNSIGNED"
    else:
        raise AssertionError("UNSIGNED")
    assert not (scratch / "updates").exists()


class _SwapPayload(dict[str, object]):
    """First payload read is the hashed body. The next read keeps the length."""

    reads: int

    def __init__(self, base: Mapping[str, object]) -> None:
        super().__init__(base)
        self.reads = 0

    def __getitem__(self, key: str) -> object:
        if key == "payload":
            self.reads += 1
            if self.reads == 1:
                return b"aaaa"
            return b"bbbb"
        return dict.__getitem__(self, key)


def test_stage_refuses_same_length_payload_swap(scratch: Path) -> None:
    packet = _SwapPayload(_packet(payload=b"aaaa", version=4))
    jail = PathJail(scratch)
    try:
        stage(jail, packet, local_tree_id="Peer-1", local_version=1, now=1_700_000_000)
    except Refuse as exc:
        assert exc.code == "BAD_HASH"
    else:
        raise AssertionError("BAD_HASH")
    assert packet.reads >= 2
    assert not (scratch / "updates").exists()


def test_second_stage_does_not_replace(scratch: Path) -> None:
    payload = b"dayone-update"
    packet = _packet()
    jail = PathJail(scratch)
    first = stage(jail, packet, local_tree_id="Peer-1", local_version=1, now=1_700_000_000)
    try:
        stage(jail, packet, local_tree_id="Peer-1", local_version=1, now=1_700_000_000)
    except Refuse as exc:
        assert exc.code == "PRESENT"
    else:
        raise AssertionError("PRESENT")
    assert first.read_bytes() == payload
