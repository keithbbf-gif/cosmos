"""Done is five hashes. A sentence from the model is not one of them.

``diff_hash`` covers the patches the hands recorded.
``oracle_id`` covers the property and the argument vector.
``oracle_log_hash`` is the post-oracle digest.
``pack_hash`` covers the eight layer files in name order.
``cmd_hash`` covers the oracle argument vector.

Any empty field refuses the bundle. The worker stops here. Publishing the
live tree is a separate pen.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

FIELDS = ("diff_hash", "oracle_id", "oracle_log_hash", "pack_hash", "cmd_hash")


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
    names = sorted(path.name for path in pack_dir.iterdir() if path.is_file()) if pack_dir.is_dir() else []
    pack_body = "\n".join(f"{name}\n{(pack_dir / name).read_text(encoding='utf-8')}" for name in names)
    return DoneBundle(
        diff_hash=_sha(diff),
        oracle_id=_sha("constants\n" + cmd),
        oracle_log_hash=oracle_log_hash,
        pack_hash=_sha(pack_body),
        cmd_hash=_sha(cmd),
    )
