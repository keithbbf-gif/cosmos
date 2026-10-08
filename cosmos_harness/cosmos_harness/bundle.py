"""Done is five hashes. A sentence from the model is not one of them.

``diff_hash`` covers the patches the hands recorded.
``oracle_id`` covers the property and the argument vector.
``oracle_log_hash`` is the post-oracle digest.
``pack_hash`` covers the pack files in name order. ``seat.jsonl`` is the
journal the loop appends beside them and is not part of the hash.
``cmd_hash`` covers the oracle argument vector.

Any empty field refuses the bundle. The worker stops here. Publishing the
live tree is a separate pen.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

FIELDS = ("diff_hash", "oracle_id", "oracle_log_hash", "pack_hash", "cmd_hash")
_JOURNAL = frozenset({"seat.jsonl"})


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DoneBundle:
    """The five fields the done hook requires."""

    diff_hash: str
    oracle_id: str
    oracle_log_hash: str
    pack_hash: str
    cmd_hash: str

    def as_dict(self) -> dict[str, str]:
        return {name: getattr(self, name) for name in FIELDS}


def make(
    *,
    patches: list[str],
    oracle_argv: tuple[str, ...],
    oracle_log_hash: str,
    pack_dir: Path,
) -> DoneBundle:
    """Hash the artifacts the attempt actually wrote."""
    diff = "\n".join(patches)
    cmd = "\n".join(oracle_argv)
    names: list[str] = []
    if pack_dir.is_dir():
        names = sorted(
            path.name
            for path in pack_dir.iterdir()
            if path.is_file() and path.name not in _JOURNAL
        )
    if names:
        pack_body = "\n".join(f"{name}\n{(pack_dir / name).read_text(encoding='utf-8')}" for name in names)
        pack_hash = _sha(pack_body)
    else:
        pack_hash = ""
    return DoneBundle(
        diff_hash=_sha(diff),
        oracle_id=_sha("constants\n" + cmd),
        oracle_log_hash=oracle_log_hash,
        pack_hash=pack_hash,
        cmd_hash=_sha(cmd),
    )
