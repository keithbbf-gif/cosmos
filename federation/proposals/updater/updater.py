"""Verify an update packet and stage its bytes without applying them.

The hub may push the packet or the peer may pull it. Either way the peer
checks identity, version, and hash, then leaves the bytes under
``updates/<version>/payload.bin``. Applying those bytes onto the running
tree is a later fenced commit by that peer's own writer. UPDATE_SERVICE.md:
a hub does not silently overwrite a peer (two-writer deletion scar).
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from cosmos_federation import (
    PathJail,
    Refuse,
    bound_int,
    bound_text,
    check_tree_id,
    const_eq,
    secret_shape,
)

SCHEMA = "cosmos-federation-updater/1"

# A caller epoch, not a wall clock. Absurd values are a bad caller.
_MAX_EPOCH = 10**18
# Monotonic packet counter. Zero means this peer has applied nothing yet.
_MAX_VERSION = 1_000_000_000
_MAX_SIGNER = 80


@dataclass(frozen=True, slots=True)
class UpdateOk:
    """A packet that passed verify. Payload and digest stay out of repr."""

    version: int
    nbytes: int
    # Pinned at verify. Not part of equality. Stage refuses a later swap.
    digest: str = field(default="", repr=False, compare=False)


def verify(
    packet: Mapping[str, object],
    *,
    local_tree_id: str,
    local_version: int,
    now: int,
) -> UpdateOk:
    """Refuse a packet that is unsigned, foreign, older, or hash-mismatched.

    ``local_version`` is the caller's last applied version. This module does
    not read a sentinel or a ledger to discover it.
    """
    if not isinstance(packet, Mapping):
        raise Refuse("BOUND", "packet")
    _signer(_require(packet, "signer_id"))
    tree_id = _tree(_require(packet, "tree_id"))
    local = check_tree_id(local_tree_id)
    if tree_id != local:
        raise Refuse("TREE_MISMATCH", "tree id")
    version = bound_int(_require(packet, "version"), lo=0, hi=_MAX_VERSION, name="version")
    current = bound_int(local_version, lo=0, hi=_MAX_VERSION, name="local_version")
    # The caller owns the clock so this module stays deterministic.
    bound_int(now, lo=0, hi=_MAX_EPOCH, name="now")
    if version <= current:
        # Not-greater includes equality. Replaying the installed version is
        # not an update, and a lower version would roll the peer back.
        raise Refuse("DOWNGRADE", "version is not newer")
    payload = _payload(_require(packet, "payload"))
    digest = _check_hash(_require(packet, "sha256"), payload)
    return UpdateOk(version=version, nbytes=len(payload), digest=digest)


def stage(
    jail: PathJail,
    packet: Mapping[str, object],
    *,
    local_tree_id: str,
    local_version: int,
    now: int,
) -> Path:
    """Write ``updates/<version>/payload.bin`` only after verify.

    Applying the payload onto the running tree is a later fenced commit by
    that peer's own writer, matching UPDATE_SERVICE.md: a hub does not
    silently overwrite a peer. This function does not delete or replace
    other files, and it does not rewrite the running tree. The bytes about
    to be written must still match the digest verify pinned.
    """
    ok = verify(packet, local_tree_id=local_tree_id, local_version=local_version, now=now)
    if not isinstance(jail, PathJail):
        raise Refuse("JAIL", "not a jail")
    payload = _payload(_require(packet, "payload"))
    # A live mapping can hand back a same-length body after the first hash.
    # Length alone would let those bytes land under the digest we accepted.
    digest = _check_hash(ok.digest, payload)
    if len(payload) != ok.nbytes or not const_eq(digest, ok.digest):
        raise Refuse("BAD_HASH", "payload sha256")
    path = jail.contain(f"updates/{ok.version}/payload.bin")
    path.parent.mkdir(parents=True, exist_ok=True)
    # A second call must not overwrite bytes the peer has not applied yet.
    if path.exists():
        raise Refuse("PRESENT", "staged payload already exists")
    path.write_bytes(payload)
    return path


def _require(packet: Mapping[str, object], name: str) -> object:
    try:
        return packet[name]
    except KeyError:
        raise Refuse("BOUND", name) from None


def _signer(value: object) -> str:
    """An id, not a key. Empty is unsigned. A secret-shaped value is refused."""
    if not isinstance(value, str):
        raise Refuse("BOUND", "signer_id")
    if value == "":
        raise Refuse("UNSIGNED", "signer id")
    if secret_shape(value):
        raise Refuse("SECRET", "signer id")
    return bound_text(value, limit=_MAX_SIGNER, name="signer_id")


def _tree(value: object) -> str:
    if not isinstance(value, str):
        raise Refuse("TREE_ID", "rejected")
    return check_tree_id(value)


def _payload(value: object) -> bytes:
    if not isinstance(value, bytes):
        raise Refuse("BOUND", "payload")
    return value


def _check_hash(claimed: object, payload: bytes) -> str:
    if not isinstance(claimed, str):
        raise Refuse("BOUND", "sha256")
    digest = hashlib.sha256(payload).hexdigest()
    # Exact lowercase hex. const_eq does not return on the first differing nibble.
    if len(claimed) != len(digest) or not const_eq(claimed, digest):
        raise Refuse("BAD_HASH", "payload sha256")
    return digest


__all__ = ["SCHEMA", "UpdateOk", "stage", "verify"]
