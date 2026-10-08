"""Cold-start pair for the one spend ledger.

The live chain stays Core's. This module does not open it, does not mint a
key, and does not append a second wallet.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from cosmos_federation import (
    DEFAULT_CAP_USD_MICROS,
    PathJail,
    Refuse,
    bound_int,
    check_cap,
    check_tree_id,
    const_eq,
)

SCHEMA = "cosmos-federation-ledgerboot/1"

# `ledger/genesis.jsonl` is this proposal's cold-start chain only.
# Core owns the real ledger filename. CCr picks that name when this lands.
# If this file and the Core chain ever disagree, the Core chain wins.
GENESIS_REL = "ledger/genesis.jsonl"

_ZERO_PREV = "0" * 64
_EPOCH_HI = 2**62
# A peer genesis is two short lines. Anything larger is not this file,
# and this slot must not parse or rewrite a Core chain that landed beside it.
_MAX_COLD_BYTES = 65_536

__all__ = [
    "SCHEMA",
    "Event",
    "GENESIS_REL",
    "apply",
    "genesis",
]


@dataclass(frozen=True, slots=True)
class Event:
    """One proposed chain record. `hash` is not part of the hashed body."""

    seq: int
    event: str
    tree_id: str
    epoch: int
    prev: str
    hash: str
    cap_usd_micros: int | None = None


def genesis(tree_id: str, now: int) -> tuple[Event, ...]:
    """Return INSTALL, then CAP_SET. `now` is the caller epoch, not a clock."""
    ident = check_tree_id(tree_id)
    epoch = bound_int(now, lo=0, hi=_EPOCH_HI, name="epoch")
    cap = check_cap(DEFAULT_CAP_USD_MICROS)
    installed = _event(1, "INSTALL", ident, epoch, _ZERO_PREV, None)
    capped = _event(2, "CAP_SET", ident, epoch, installed.hash, cap)
    return (installed, capped)


def apply(jail: PathJail, tree_id: str, now: int) -> Path:
    """Write the cold-start chain once under the jail.

    The same tree id leaves the existing bytes in place and does not append
    a second copy. A different tree id refuses. This is not Core's ledger.
    """
    if not isinstance(jail, PathJail):
        raise Refuse("JAIL", "apply requires a PathJail")
    events = genesis(tree_id, now)
    payload = _render(events)
    path = jail.contain(GENESIS_REL)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        raise Refuse("TORN", "ledger directory cannot be created") from None
    if path.exists() and not path.is_file():
        raise Refuse("TORN", "cold-start path is not a file")
    if path.is_file():
        raw = path.read_bytes()
        if raw == payload:
            return path
        # Same identity means the chain already started. Do not append and
        # do not rewrite; a later epoch is not a new install.
        if const_eq(_tree_of(raw), events[0].tree_id):
            return path
        raise Refuse("IDENTITY_MISMATCH", "existing chain names a different tree")
    path.write_bytes(payload)
    return path


def _event(
    seq: int,
    name: str,
    tree_id: str,
    epoch: int,
    prev: str,
    cap: int | None,
) -> Event:
    body = _body(seq, name, tree_id, epoch, prev, cap)
    digest = hashlib.sha256(_canonical(body)).hexdigest()
    return Event(
        seq=seq,
        event=name,
        tree_id=tree_id,
        epoch=epoch,
        prev=prev,
        hash=digest,
        cap_usd_micros=cap,
    )


def _body(
    seq: int,
    name: str,
    tree_id: str,
    epoch: int,
    prev: str,
    cap: int | None,
) -> dict[str, object]:
    body: dict[str, object] = {
        "epoch": epoch,
        "event": name,
        "prev": prev,
        "seq": seq,
        "tree_id": tree_id,
    }
    if cap is not None:
        body["cap_usd_micros"] = cap
    return body


def _canonical(body: dict[str, object]) -> bytes:
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _render(events: tuple[Event, ...]) -> bytes:
    lines: list[str] = []
    for item in events:
        stored = _body(
            item.seq,
            item.event,
            item.tree_id,
            item.epoch,
            item.prev,
            item.cap_usd_micros,
        )
        stored["hash"] = item.hash
        lines.append(json.dumps(stored, sort_keys=True, separators=(",", ":")))
    return ("\n".join(lines) + "\n").encode("utf-8")


def _tree_of(raw: bytes) -> str:
    if len(raw) > _MAX_COLD_BYTES:
        raise Refuse("TORN", "cold-start file is larger than this proposal")
    try:
        text = raw.decode("utf-8")
    except UnicodeError:
        raise Refuse("TORN", "cold-start file is not utf-8") from None
    first = ""
    for line in text.splitlines():
        if line != "":
            first = line
            break
    if first == "":
        raise Refuse("TORN", "cold-start file is empty")
    try:
        parsed: object = json.loads(first)
    except json.JSONDecodeError:
        raise Refuse("TORN", "cold-start file is not json") from None
    if not isinstance(parsed, dict):
        raise Refuse("TORN", "cold-start file is not an object")
    tree = parsed.get("tree_id")
    if not isinstance(tree, str) or tree == "":
        raise Refuse("TORN", "cold-start file has no tree id")
    return tree
